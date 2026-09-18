"""
Coupled nine-region simulation of a talent-concentration ("dominant")
strategy.

The single-region six-compartment model of ode_model_endogenous.py is
coupled across research macro-regions through the observed distribution of
each region's abroad researchers over host regions.  One focal region then
pursues an aggressive talent-concentration strategy: it pulls additional early-career researchers
out of every other region and retains the researchers it hosts.  The
simulation compares (i) the focal region's hosted active pool and share of
the field against the baseline and (ii) the number of macro-regions whose
domestic active pool stays above the minimum viable coauthor scale M.

Provenance of inputs
--------------------
Fitted from data (data/cohort, results/endogenous, results/annual):
    transition rates alpha, beta, h_D, h_A, p_D, p_A, d per region;
    baseline recruitment I0 and PI feedback r per region;
    threshold M per region;
    host-region shares of abroad researchers (annual_interciv_stock.csv).
Stylised scenario assumptions (not fitted):
    pull intensity phi (grid);
    retention of researchers pulled to the focal region (beta / (1 + phi));
    irreversible loss of PI-driven recruitment once T falls below M
    (r -> 0 for that region for the rest of the run);
    horizon and initial state (baseline equilibrium).
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
COHORT_DIR = Path(os.environ.get("RESEARCHER_MOBILITY_COHORT_DIR", str(DATA_DIR / "cohort")))
RESULTS_DIR = BASE_DIR / "results"
ENDOGENOUS_DIR = RESULTS_DIR / "endogenous"
ANNUAL_DIR = RESULTS_DIR / "annual"
OUT_DIR = RESULTS_DIR / "dominant_strategy"

RATE_NAMES = ["alpha", "beta", "h_D", "h_A", "p_D", "p_A", "d"]
STATE_NAMES = ["D", "A", "H_D", "H_A", "P_D", "P_A"]
NS = len(STATE_NAMES)

DEFAULT_PHI_GRID = [0.0, 0.5, 1.0, 2.0, 4.0, 8.0]
DEFAULT_GAMMA_GRID = [0.0, 1.0, 2.0]
DEFAULT_HORIZON = 100.0


def load_inputs():
    rates = pd.read_csv(COHORT_DIR / "transition_rates.csv").set_index("group")
    eq = pd.read_csv(ENDOGENOUS_DIR / "equilibrium_summary.csv").set_index("group")
    groups = [g for g in eq.index if g in rates.index]
    rates = rates.loc[groups, RATE_NAMES]
    eq = eq.loc[groups]
    flows = pd.read_csv(ANNUAL_DIR / "annual_interciv_stock.csv")
    flows = flows[(flows["origin_group"] != flows["destination_group"])
                  & flows["origin_group"].isin(groups)
                  & flows["destination_group"].isin(groups)]
    W = (flows.groupby(["origin_group", "destination_group"])["count"].sum()
         .unstack(fill_value=0.0).reindex(index=groups, columns=groups, fill_value=0.0))
    W = W.div(W.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    return groups, rates, eq, W


def region_matrix(alpha, beta, h_D, h_A, p_D, p_A, d, r):
    M = np.zeros((NS, NS))
    M[0, 0] = -(alpha + h_D + d)
    M[0, 1] = beta
    M[0, 4] = r
    M[1, 0] = alpha
    M[1, 1] = -(h_A + beta + d)
    M[2, 0] = h_D
    M[2, 2] = -(p_D + d)
    M[2, 3] = beta
    M[3, 1] = h_A
    M[3, 3] = -(p_A + beta + d)
    M[4, 2] = p_D
    M[4, 4] = -d
    M[4, 5] = beta
    M[5, 3] = p_A
    M[5, 5] = -(beta + d)
    return M


PULLED_NAMES = ["A_f", "H_A_f", "P_A_f"]
NX = NS + len(PULLED_NAMES)


def scenario_parameters(groups, rates, focal, phi):
    """
    Per-region pull rate and retained return rate under a talent-concentration strategy of
    intensity phi by `focal`.  phi = 0 reproduces the baseline.

    For every non-focal region i an additional early-career outflow alpha_i phi
    is directed to the focal region.  Researchers who leave through this channel
    are tracked in separate compartments (A_f, H_A_f, P_A_f) hosted by the focal
    region and return at beta_i / (1 + phi).  The stock that was already abroad
    at the start keeps the observed host distribution W, so every scenario
    starts from the same state as the baseline.
    """
    pull = pd.Series(0.0, index=groups)
    beta_p = rates["beta"].astype(float).copy()
    for g in groups:
        if g == focal or phi == 0.0:
            continue
        pull[g] = rates.loc[g, "alpha"] * phi
        beta_p[g] = rates.loc[g, "beta"] / (1.0 + phi)
    return pull, beta_p


def region_matrix_pulled(alpha, beta, h_D, h_A, p_D, p_A, d, r, pull, beta_p):
    """Nine-state matrix: the six baseline compartments plus the pulled abroad
    compartments A_f, H_A_f, P_A_f that are hosted by the focal region."""
    M = np.zeros((NX, NX))
    M[:NS, :NS] = region_matrix(alpha, beta, h_D, h_A, p_D, p_A, d, r)
    M[0, 0] -= pull
    M[6, 0] = pull
    M[6, 6] = -(h_A + beta_p + d)
    M[7, 6] = h_A
    M[7, 7] = -(p_A + beta_p + d)
    M[8, 7] = p_A
    M[8, 8] = -(beta_p + d)
    M[0, 6] = beta_p
    M[2, 7] = beta_p
    M[4, 8] = beta_p
    return M


def recruitment_split(eq, exogenous_share=None):
    """
    Return (I0, r) per region.  With exogenous_share=None the fitted split
    from equilibrium_summary.csv is used (r capped at half the critical
    feedback, so roughly half of equilibrium recruitment is exogenous).
    Otherwise the same equilibrium recruitment I0 + r P_D_eq is re-split so
    that the exogenous part is `exogenous_share` of the total; the
    equilibrium itself is unchanged, only the response to a falling PI stock.
    """
    I0_fit = eq["I0"].values.astype(float)
    r_fit = eq["r"].values.astype(float)
    P_eq = eq["P_D_eq"].values.astype(float)
    if exogenous_share is None:
        return I0_fit, r_fit
    I_total = I0_fit + r_fit * P_eq
    I0 = exogenous_share * I_total
    r = (I_total - I0) / P_eq
    r_crit = eq["r_critical"].values.astype(float)
    if np.any(r >= r_crit):
        raise ValueError("exogenous_share too small: feedback would exceed r_critical")
    return I0, r


def characteristic_time(rates):
    """Characteristic time tau (years) = 1 / mean fitted dropout rate across regions,
    i.e. the mean career duration. Model time is reported in units of tau because the
    clock is set by the fitted transition rates; calendar years are an annotation."""
    return float(1.0 / rates["d"].astype(float).mean())


def _time_axes(ax, tau, xlabel=True):
    """Primary axis in units of tau; secondary (top) axis in years at fitted rates."""
    if xlabel:
        ax.set_xlabel("Time (units of \u03c4 = mean career duration 1/d\u0304)")
    sec = ax.secondary_xaxis("top", functions=(lambda x: x * tau, lambda y: y / tau))
    sec.set_xlabel("years at fitted rates", fontsize=7, color="grey")
    sec.tick_params(labelsize=7, colors="grey")
    return sec


def effective_regions(T):
    s = T / T.sum()
    return 1.0 / np.sum(s ** 2)


def simulate(groups, rates, eq, W, focal, phi, horizon=DEFAULT_HORIZON, n_out=201,
             exogenous_share=None, host_recruits=True, gamma=0.0):
    """
    host_recruits=True lets every region recruit with its own feedback rate
    from the abroad PIs it hosts (r_j * sum_i w_ij P_A_i, plus the pulled PIs
    for the focal region) in addition to its domestic PIs; I0_j is reduced by
    the baseline value of that term so the fitted equilibrium remains the
    baseline steady state.  Without it the researchers a host attracts would
    never reproduce for anyone.

    gamma > 0 adds a stylised variety dependence of hit generation: every
    region's h_D and h_A are multiplied by (N_eff(t) / N_eff(0))^gamma, where
    N_eff is the inverse-Simpson effective number of macro-regions computed
    on domestic active pools.  gamma = 0 recovers the fitted model.

    The collapse rule (r -> 0 once T < M) is applied with terminal events of
    the integrator: integration stops at the exact crossing, the region is
    marked collapsed, and integration restarts from that state.
    """
    pull, beta_p = scenario_parameters(groups, rates, focal, phi)
    n = len(groups)
    fi = groups.index(focal)
    I0, r_fit = recruitment_split(eq, exogenous_share)
    Mthr = eq["M_threshold"].values.astype(float)
    y0 = np.zeros((n, NX))
    y0[:, :NS] = eq[[f"{s}_eq" for s in STATE_NAMES]].values.astype(float)
    y0 = y0.ravel()
    P_A_eq = eq["P_A_eq"].values.astype(float)
    if host_recruits:
        hosted_PA_base = P_A_eq @ W.values
        I0 = I0 - r_fit * hosted_PA_base
        if np.any(I0 <= 0):
            raise ValueError("host recruitment exceeds exogenous recruitment; lower exogenous_share is not admissible")
    collapsed = np.zeros(n, dtype=bool)
    collapse_year = np.full(n, np.nan)
    N_eff0 = effective_regions(y0.reshape(n, NX)[:, [0, 2, 4]].sum(axis=1))
    base_params = [dict(zip(RATE_NAMES, rates.loc[g, RATE_NAMES].values.astype(float))) for g in groups]
    Wv = W.values

    def matrices(v, dead_mask):
        mats = []
        for i in range(n):
            p = dict(base_params[i])
            p["h_D"] *= v
            p["h_A"] *= v
            mats.append(region_matrix_pulled(**p, r=0.0 if dead_mask[i] else r_fit[i],
                                             pull=pull.iloc[i], beta_p=beta_p.iloc[i]))
        return mats

    def make_rhs(dead_mask):
        fixed = matrices(1.0, dead_mask)

        def rhs(t, y):
            Y = y.reshape(n, NX)
            T = Y[:, 0] + Y[:, 2] + Y[:, 4]
            mats = matrices((effective_regions(T) / N_eff0) ** gamma, dead_mask) if gamma > 0.0 else fixed
            dY = np.empty_like(Y)
            if host_recruits:
                hosted_PA = Y[:, 5] @ Wv
                hosted_PA[fi] += Y[:, 8].sum()
            for i in range(n):
                dY[i] = mats[i] @ Y[i]
                dY[i, 0] += I0[i]
                if host_recruits and not dead_mask[i]:
                    dY[i, 0] += r_fit[i] * hosted_PA[i]
            return dY.ravel()
        return rhs

    def make_events(dead_mask):
        evs = []
        for i in range(n):
            if dead_mask[i]:
                continue

            def ev(t, y, i=i):
                return y[i * NX] + y[i * NX + 2] + y[i * NX + 4] - Mthr[i]
            ev.terminal = True
            ev.direction = -1
            evs.append((i, ev))
        return evs

    t_eval = np.linspace(0.0, horizon, n_out)
    ts, ys = [], []
    t0, y = 0.0, y0.copy()
    while t0 < horizon:
        events = make_events(collapsed)
        seg_eval = t_eval[(t_eval >= t0) & (t_eval <= horizon)]
        sol = solve_ivp(make_rhs(collapsed.copy()), (t0, horizon), y, t_eval=seg_eval,
                        events=[e for _, e in events], method="LSODA",
                        rtol=1e-8, atol=1e-6, max_step=0.25)
        ts.extend(sol.t.tolist())
        ys.extend(sol.y.T.tolist())
        if sol.status == 1:
            hit = [k for k, te in enumerate(sol.t_events) if len(te)]
            t_hit = min(float(sol.t_events[k][0]) for k in hit)
            for k in hit:
                if abs(float(sol.t_events[k][0]) - t_hit) < 1e-9:
                    i = events[k][0]
                    collapsed[i] = True
                    collapse_year[i] = t_hit
            y = sol.y_events[hit[0]][0]
            t0 = t_hit
            t_eval = t_eval[t_eval > t_hit]
        else:
            break
    order = np.argsort(ts)
    t_out = np.array(ts)[order]
    Y = np.array(ys)[order].reshape(len(t_out), n, NX)
    T = Y[:, :, 0] + Y[:, :, 2] + Y[:, :, 4]
    abroad = Y[:, :, 1] + Y[:, :, 3] + Y[:, :, 5]
    pulled = Y[:, :, 6] + Y[:, :, 7] + Y[:, :, 8]
    hosted_from_abroad = abroad @ Wv
    hosted_from_abroad[:, fi] += pulled.sum(axis=1)
    hosted = T + hosted_from_abroad
    P_D = Y[:, :, 4]
    hosted_PI = P_D + Y[:, :, 5] @ Wv
    hosted_PI[:, fi] += Y[:, :, 8].sum(axis=1)
    hosted_hits = Y[:, :, 2] + Y[:, :, 3] @ Wv
    hosted_hits[:, fi] += Y[:, :, 7].sum(axis=1)
    rows = []
    for k, t in enumerate(t_out):
        share = hosted[k] / hosted[k].sum()
        viable = T[k] >= Mthr
        rows.append({
            "focal": focal, "phi": phi, "exogenous_share": exogenous_share if exogenous_share is not None else "fitted",
            "host_recruits": host_recruits, "gamma": gamma, "year": t,
            "focal_hosted_pool": hosted[k, fi],
            "focal_hosted_PI": hosted_PI[k, fi],
            "focal_hosted_hits": hosted_hits[k, fi],
            "focal_share_of_hosted": share[fi],
            "focal_inflow_from_abroad": hosted_from_abroad[k, fi],
            "field_domestic_active_total": T[k].sum(),
            "field_domestic_PI_total": P_D[k].sum(),
            "field_PI_total": P_D[k].sum() + Y[k, :, 5].sum() + Y[k, :, 8].sum(),
            "field_researchers_total": Y[k].sum(),
            "field_hits_total": Y[k, :, 2].sum() + Y[k, :, 3].sum() + Y[k, :, 7].sum(),
            "n_viable_regions": int(viable.sum()),
            "effective_number_of_regions": effective_regions(T[k]),
            **{f"T_over_M__{g}": T[k, i] / Mthr[i] for i, g in enumerate(groups)},
        })
    traj = pd.DataFrame(rows)
    collapse = pd.DataFrame({"focal": focal, "phi": phi,
                             "exogenous_share": exogenous_share if exogenous_share is not None else "fitted",
                             "host_recruits": host_recruits, "gamma": gamma, "group": groups,
                             "collapse_year": collapse_year})
    return traj, collapse


def summarise(traj_all, collapse_all):
    keys = ["focal", "exogenous_share", "host_recruits", "gamma", "phi"]
    out = []
    for key, df in traj_all.groupby(keys, sort=False):
        focal, exo, hr, gamma, phi = key
        base = traj_all[(traj_all["focal"] == focal) & (traj_all["exogenous_share"] == exo)
                        & (traj_all["host_recruits"] == hr) & (traj_all["gamma"] == gamma)
                        & (traj_all["phi"] == 0.0)]
        rel = df["focal_hosted_pool"].values / base["focal_hosted_pool"].values
        rel_hits = df["focal_hosted_hits"].values / base["focal_hosted_hits"].values
        rel_field = df["field_hits_total"].values / base["field_hits_total"].values
        k = int(np.argmax(rel))
        kh = int(np.argmax(rel_hits))
        kf = int(np.argmax(rel_field))
        after = np.where(rel_field[kf:] < 1.0)[0]
        below_year = float(df["year"].values[kf + after[0]]) if len(after) else np.nan
        coll = collapse_all[(collapse_all["focal"] == focal) & (collapse_all["exogenous_share"] == exo)
                            & (collapse_all["host_recruits"] == hr) & (collapse_all["gamma"] == gamma)
                            & (collapse_all["phi"] == phi)]
        out.append({
            "focal": focal, "exogenous_share": exo, "host_recruits": hr, "gamma": gamma, "phi": phi,
            "peak_relative_hosted_pool": rel[k],
            "peak_year": df["year"].values[k],
            "terminal_relative_hosted_pool": rel[-1],
            "peak_relative_focal_hits": rel_hits[kh],
            "peak_year_focal_hits": df["year"].values[kh],
            "terminal_relative_focal_hits": rel_hits[-1],
            "share_start": df["focal_share_of_hosted"].values[0],
            "share_terminal": df["focal_share_of_hosted"].values[-1],
            "n_viable_start": df["n_viable_regions"].values[0],
            "n_viable_terminal": df["n_viable_regions"].values[-1],
            "n_collapsed": int(coll["collapse_year"].notna().sum()),
            "first_collapse_year": coll["collapse_year"].min(),
            "effective_regions_start": df["effective_number_of_regions"].values[0],
            "effective_regions_terminal": df["effective_number_of_regions"].values[-1],
            "min_T_over_M_terminal": df[[c for c in df.columns if c.startswith("T_over_M__")]].iloc[-1].min(),
            "field_PI_terminal_relative": df["field_PI_total"].values[-1] / base["field_PI_total"].values[-1],
            "field_hits_terminal_relative": df["field_hits_total"].values[-1] / base["field_hits_total"].values[-1],
            "field_researchers_terminal_relative": df["field_researchers_total"].values[-1] / base["field_researchers_total"].values[-1],
            "peak_relative_field_hits": rel_field[kf],
            "peak_year_field_hits": df["year"].values[kf],
            "year_field_hits_below_baseline": below_year,
        })
    return pd.DataFrame(out)


def gamma_threshold(groups, rates, eq, W, focal, phi, metric, horizon, host_recruits=True,
                    gamma_max=6.0, n_iter=30):
    """
    Smallest gamma at which the terminal value of `metric` under the dominant
    strategy falls below its baseline value.  Returns NaN if not reached
    within [0, gamma_max].
    """
    def rel(gamma):
        base, _ = simulate(groups, rates, eq, W, focal, 0.0, horizon=horizon, n_out=41,
                           host_recruits=host_recruits, gamma=gamma)
        tr, _ = simulate(groups, rates, eq, W, focal, phi, horizon=horizon, n_out=41,
                         host_recruits=host_recruits, gamma=gamma)
        return tr[metric].values[-1] / base[metric].values[-1]
    if rel(0.0) < 1.0:
        return 0.0
    if rel(gamma_max) >= 1.0:
        return np.nan
    lo, hi = 0.0, gamma_max
    for _ in range(n_iter):
        mid = 0.5 * (lo + hi)
        if rel(mid) < 1.0:
            hi = mid
        else:
            lo = mid
    return hi


def plot_dominant_strategy(traj_all, thresholds, focal, fig_dir, display=None, tau=1.0,
                           out_name="dominant_strategy_scenarios.png"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker

    display = display or (lambda g: g)
    fig_dir = Path(fig_dir)
    fig_dir.mkdir(parents=True, exist_ok=True)
    sel = traj_all[(traj_all["focal"] == focal) & (traj_all["exogenous_share"] == "fitted")
                   & (traj_all["host_recruits"] == True)]  # noqa: E712
    phis = sorted(p for p in sel["phi"].unique() if p > 0)
    gammas = sorted(sel["gamma"].unique())
    cmap = plt.get_cmap("viridis")
    colors = {p: cmap(i / max(1, len(phis) - 1)) for i, p in enumerate(phis)}

    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    ax = axes[0, 0]
    base = sel[(sel["phi"] == 0.0) & (sel["gamma"] == 0.0)]
    for p in phis:
        d = sel[(sel["phi"] == p) & (sel["gamma"] == 0.0)]
        ax.plot(d["year"] / tau, d["focal_hosted_pool"].values / base["focal_hosted_pool"].values,
                color=colors[p], label=f"pull intensity = {p:g}")
    ax.axhline(1.0, color="grey", lw=0.8, ls="--")
    _time_axes(ax, tau)
    ax.set_ylabel("Hosted active pool relative to baseline")
    ax.set_title(f"(a) {display(focal)}: hosted pool (fitted rates)", pad=26)
    ax.legend(fontsize=8)

    ax = axes[0, 1]
    for p in phis:
        d = sel[(sel["phi"] == p) & (sel["gamma"] == 0.0)]
        ax.plot(d["year"] / tau, d["effective_number_of_regions"], color=colors[p])
    ax.plot(base["year"] / tau, base["effective_number_of_regions"], color="black", ls=":", label="baseline")
    _time_axes(ax, tau)
    ax.set_ylabel("Effective number of macro-regions")
    ax.set_title("(b) Field concentration (inverse Simpson on T)", pad=26)
    ax.legend(fontsize=8)

    ax = axes[1, 0]
    p_show = phis[len(phis) // 2] if len(phis) > 1 else phis[0]
    gcmap = plt.get_cmap("plasma")
    for i, g in enumerate(gammas):
        b = sel[(sel["phi"] == 0.0) & (sel["gamma"] == g)]
        d = sel[(sel["phi"] == p_show) & (sel["gamma"] == g)]
        ax.plot(d["year"] / tau, d["field_hits_total"].values / b["field_hits_total"].values,
                color=gcmap(i / max(1, len(gammas) - 1)), label=f"variety elasticity = {g:g}")
    ax.axhline(1.0, color="grey", lw=0.8, ls="--")
    _time_axes(ax, tau)
    ax.set_ylabel("Field hit stock relative to baseline")
    ax.set_title(f"(c) Field output, pull intensity = {p_show:g}", pad=26)
    ax.legend(fontsize=8)

    ax = axes[1, 1]
    th = thresholds[thresholds["host_recruits"] == True]  # noqa: E712
    gmax = float(th["gamma_max"].iloc[0]) if "gamma_max" in th.columns and len(th) else 6.0
    focals = list(dict.fromkeys(th["focal"]))
    styles = ["-", "--", "-.", ":"]
    for fi_, foc in enumerate(focals):
        for metric, lab, mk in [("field_hits_total", "whole field", "o"),
                                ("focal_hosted_hits", "dominant region itself", "s")]:
            t = th[(th["focal"] == foc) & (th["metric"] == metric)].sort_values("phi")
            y = t["gamma_threshold"].values.astype(float)
            reached = ~np.isnan(y)
            yplot = np.where(reached, y, gmax)
            ax.plot(t["phi"], yplot, ls=styles[fi_ % len(styles)], color="C0" if mk == "o" else "C1",
                    marker=mk, markerfacecolor="none" if not reached.all() else None,
                    label=f"{display(foc)} dominant: {lab}")
    ax.axhline(gmax, color="grey", lw=0.6, ls=":")
    ax.text(0.99, gmax + 0.12, f"points on this line: not reached within search range (\u03b3 \u2264 {gmax:g})",
            transform=ax.get_yaxis_transform(), ha="right", va="bottom", fontsize=7, color="grey")
    ax.set_xscale("log", base=2)
    ax.set_xticks(sorted(th["phi"].unique()))
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.set_ylim(-0.2, gmax + 0.8)
    ax.set_xlabel("Pull intensity (log scale)")
    ax.set_ylabel("Variety elasticity at which hit stock\nfalls below baseline within horizon")
    ax.set_title("(d) Elasticity needed for a net loss")
    ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2, frameon=False)
    fig.tight_layout()
    out = fig_dir / out_name
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def plot_regional_trajectories(traj_all, coll_all, focal, fig_dir, phi=None, display=None, tau=1.0,
                               out_name="dominant_strategy_regional_trajectories.png"):
    """Time paths of every macro-region's domestic active pool (as a multiple of its
    minimum viable scale M) under the talent-concentration strategy, one panel per variety
    elasticity gamma. Crosses mark when a region falls below M, after which its
    PI-driven recruitment is switched off permanently."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    display = display or (lambda g: g)
    fig_dir = Path(fig_dir)
    fig_dir.mkdir(parents=True, exist_ok=True)
    sel = traj_all[(traj_all["focal"] == focal) & (traj_all["exogenous_share"] == "fitted")
                   & (traj_all["host_recruits"] == True)]  # noqa: E712
    if phi is None:
        phi = max(sel["phi"].unique())
    gammas = sorted(sel["gamma"].unique())
    tm_cols = [c for c in sel.columns if c.startswith("T_over_M__")]
    groups = [c.replace("T_over_M__", "") for c in tm_cols]
    cmap = plt.get_cmap("tab10")
    colors = {g: cmap(i % 10) for i, g in enumerate(groups)}

    fig, axes = plt.subplots(1, len(gammas), figsize=(4.2 * len(gammas), 4.4), sharey=True)
    axes = np.atleast_1d(axes)
    for ax, gm in zip(axes, gammas):
        d = sel[(sel["phi"] == phi) & (sel["gamma"] == gm)].sort_values("year")
        cy = coll_all[(coll_all["focal"] == focal) & (coll_all["phi"] == phi)
                      & (coll_all["gamma"] == gm) & (coll_all["exogenous_share"] == "fitted")
                      & (coll_all["host_recruits"] == True)]  # noqa: E712
        for g, c in zip(groups, tm_cols):
            lw = 2.4 if g == focal else 1.2
            ax.plot(d["year"] / tau, d[c].astype(float), color=colors[g], lw=lw,
                    label=display(g) + (" (dominant)" if g == focal else ""))
            yr = cy.loc[cy["group"] == g, "collapse_year"]
            if len(yr) and np.isfinite(float(yr.iloc[0])):
                y0 = float(yr.iloc[0]) / tau
                ax.plot([y0], [1.0], marker="x", color=colors[g], ms=9, mew=2)
                ax.axvline(y0, color=colors[g], lw=0.6, ls=":")
        ax.axhline(1.0, color="black", lw=0.8, ls="--")
        ax.set_yscale("log")
        _time_axes(ax, tau)
        ax.set_title(f"variety elasticity = {gm:g}", pad=30)
        ax.grid(alpha=0.25, which="both")
    axes[0].set_ylabel("Domestic active pool / minimum viable scale (log)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=8, loc="lower center", ncol=5, frameon=False,
               bbox_to_anchor=(0.5, -0.02))
    fig.suptitle(f"Talent-concentration strategy by {display(focal)}, pull intensity = {phi:g}: "
                 "regional active pools; x marks when a region falls below M", fontsize=10)
    fig.tight_layout(rect=(0, 0.1, 1, 0.96))
    out = fig_dir / out_name
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--focal", nargs="*", default=None,
                        help="Focal region(s); default = the two largest observed host regions")
    parser.add_argument("--phi", nargs="*", type=float, default=DEFAULT_PHI_GRID)
    parser.add_argument("--gamma", nargs="*", type=float, default=DEFAULT_GAMMA_GRID)
    parser.add_argument("--horizon", type=float, default=DEFAULT_HORIZON)
    parser.add_argument("--out-dir", type=str, default=str(OUT_DIR))
    parser.add_argument("--fig-dir", type=str, default=str(BASE_DIR / "docs" / "figures"))
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    groups, rates, eq, W = load_inputs()
    tau = characteristic_time(rates)
    flows = pd.read_csv(ANNUAL_DIR / "annual_interciv_stock.csv")
    flows = flows[(flows["origin_group"] != flows["destination_group"]) & flows["destination_group"].isin(groups)]
    host_rank = flows.groupby("destination_group")["count"].sum().sort_values(ascending=False)
    focals = args.focal or list(host_rank.index[:2])
    phis = sorted(set([0.0] + list(args.phi)))
    gammas = sorted(set([0.0] + list(args.gamma)))

    trajs, colls = [], []
    for focal in focals:
        for hr in (True, False):
            for gamma in gammas:
                for phi in phis:
                    tr, co = simulate(groups, rates, eq, W, focal, phi, horizon=args.horizon,
                                      host_recruits=hr, gamma=gamma)
                    trajs.append(tr)
                    colls.append(co)
        for exo in (0.25,):
            for phi in phis:
                tr, co = simulate(groups, rates, eq, W, focal, phi, horizon=args.horizon,
                                  exogenous_share=exo, host_recruits=False)
                trajs.append(tr)
                colls.append(co)
    traj_all = pd.concat(trajs, ignore_index=True)
    coll_all = pd.concat(colls, ignore_index=True)
    summ = summarise(traj_all, coll_all)
    summ["tau_years"] = tau

    th_rows = []
    for focal in focals:
        for phi in [p for p in phis if p > 0]:
            for metric in ("field_hits_total", "focal_hosted_hits", "field_PI_total"):
                th_rows.append({"focal": focal, "phi": phi, "host_recruits": True, "metric": metric, "gamma_max": 6.0,
                                "gamma_threshold": gamma_threshold(groups, rates, eq, W, focal, phi, metric,
                                                                   args.horizon, host_recruits=True)})
    thresholds = pd.DataFrame(th_rows)

    traj_all.to_csv(out_dir / "trajectories.csv", index=False, encoding="utf-8-sig")
    coll_all.to_csv(out_dir / "collapse_years.csv", index=False, encoding="utf-8-sig")
    summ.to_csv(out_dir / "summary.csv", index=False, encoding="utf-8-sig")
    thresholds.to_csv(out_dir / "gamma_thresholds.csv", index=False, encoding="utf-8-sig")
    W.reset_index().rename(columns={"origin_group": "group"}).to_csv(
        out_dir / "host_share_matrix.csv", index=False, encoding="utf-8-sig")
    host_rank.rename("hosted_author_years").reset_index().to_csv(
        out_dir / "host_ranking.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame({
        "parameter": ["phi_grid", "gamma_grid", "horizon_years", "tau_years", "horizon_in_tau", "pull_rule", "retention_rule",
                      "host_recruitment_rule", "collapse_rule", "variety_rule", "initial_state",
                      "transition_rates", "recruitment_split", "host_shares"],
        "value": [",".join(str(p) for p in phis), ",".join(str(g) for g in gammas), args.horizon,
                  tau, args.horizon / tau,
                  "additional outflow alpha_i phi from D_i to separate compartments hosted by the focal region (i != focal); pre-existing abroad stock keeps observed host shares W",
                  "beta_i/(1+phi) for researchers pulled to the focal region",
                  "each host recruits r_j x hosted abroad PIs; I0_j reduced so the fitted equilibrium is unchanged",
                  "r_i -> 0 permanently once T_i < M_i (integrator terminal event at the crossing)",
                  "h_D, h_A scaled by (N_eff/N_eff0)^gamma; gamma = 0 is the fitted model",
                  "baseline equilibrium from results/endogenous/equilibrium_summary.csv",
                  "data/cohort/transition_rates.csv",
                  "I0, r from results/endogenous/equilibrium_summary.csv (exogenous_share=fitted); 0.25 as sensitivity",
                  "results/annual/annual_interciv_stock.csv, all years, off-diagonal"],
        "status": ["stylised", "stylised", "stylised", "fitted (1 / mean d)", "derived", "stylised", "stylised", "stylised", "stylised",
                   "stylised", "fitted", "fitted", "fitted / stylised", "fitted"]}).to_csv(
        out_dir / "scenario_assumptions.csv", index=False, encoding="utf-8-sig")
    plot_dominant_strategy(traj_all, thresholds, focals[0], args.fig_dir, tau=tau)
    plot_regional_trajectories(traj_all, coll_all, focals[0], args.fig_dir, tau=tau)
    print(summ[(summ["exogenous_share"] == "fitted") & (summ["host_recruits"] == True)]  # noqa: E712
          .to_string(index=False))
    print(thresholds.to_string(index=False))


if __name__ == "__main__":
    main()
