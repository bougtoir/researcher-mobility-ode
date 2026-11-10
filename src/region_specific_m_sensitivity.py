#!/usr/bin/env python3
"""Region-specific M sensitivity: independent per-region perturbations of the
operational benchmark M_i' = s_i * M_i, s_i in [0.5, 2.0].

Deterministic interval analysis (primary) plus a stochastic exploration with
s_i drawn iid Uniform(0.5, 2.0) as a computational exploration distribution —
NOT a claim about the real uncertainty of M.

Boundary proximity under perturbed M is recomputed with the same solver
(point_of_no_return) on a grid of per-region multipliers; it is a structural
consequence of the model, not independent validation.

Outputs:
  results/region_specific_m/REGION_SPECIFIC_M_SENSITIVITY.csv  (MC + interval)
  results/region_specific_m/REGION_SPECIFIC_M_INTERVAL_PAIRS.csv
  results/region_specific_m/REGION_SPECIFIC_M_SUMMARY.csv
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, spearmanr

import ode_model_endogenous as odm

BASE_DIR = Path(__file__).resolve().parent.parent
ENDO_DIR = BASE_DIR / "results" / "endogenous"
OUT_DIR = BASE_DIR / "results" / "region_specific_m"
S_LO, S_HI = 0.5, 2.0
N_DRAWS = 200_000
RNG_SEED = 20261103


def main():
    eq = pd.read_csv(ENDO_DIR / "equilibrium_summary.csv")
    groups = eq["group"].tolist()
    T = eq["T_equilibrium"].to_numpy(float)
    M = eq["M_threshold"].to_numpy(float)
    tm = T / M
    g = len(groups)

    # ---------- 1. Deterministic interval analysis ----------
    lo, hi = tm * S_LO, tm * S_HI  # T/(2M), T/(0.5M)
    pairs = []
    for i in range(g):
        for j in range(i + 1, g):
            base_lt = tm[i] < tm[j]
            # order preserved always iff intervals don't overlap
            if hi[i] < lo[j]:
                status = "always i<j" if base_lt else "always j<i"
            elif hi[j] < lo[i]:
                status = "always j<i" if not base_lt else "always i<j"
            else:
                status = "reversible"
            pairs.append({"group_i": groups[i], "group_j": groups[j],
                          "baseline_order": "i<j" if base_lt else "j<i",
                          "status": status})
    pairs_df = pd.DataFrame(pairs)
    n_rev = int((pairs_df["status"] == "reversible").sum())

    # candidate min/max: region i can be the unique minimum iff lo[i] < min_j hi[j]... 
    # more precisely iff exists s in range with tm_i*s_i < tm_j*s_j for all j:
    # take s_i=S_LO, s_j=S_HI: possible iff tm_i*S_LO < tm_j*S_HI for all j.
    can_min = [groups[i] for i in range(g)
               if all(tm[i] * S_LO < tm[j] * S_HI for j in range(g) if j != i)]
    can_max = [groups[i] for i in range(g)
               if all(tm[i] * S_HI > tm[j] * S_LO for j in range(g) if j != i)]

    # ---------- 2. Stochastic exploration (uniform, computational) ----------
    rng = np.random.default_rng(RNG_SEED)
    S = rng.uniform(S_LO, S_HI, size=(N_DRAWS, g))
    TM = tm[None, :] / S
    ranks = TM.argsort(axis=1).argsort(axis=1) + 1
    baseline_rank = tm.argsort().argsort() + 1

    rows = []
    spearman_vals = np.empty(N_DRAWS)
    kendall_vals = np.empty(N_DRAWS)
    chunk = 20_000
    for k in range(0, N_DRAWS, chunk):
        idx = slice(k, k + chunk)
        for r_i, row in enumerate(ranks[idx]):
            spearman_vals[k + r_i] = spearmanr(row, baseline_rank).statistic
            kendall_vals[k + r_i] = kendalltau(row, baseline_rank).statistic

    min_count = (ranks == 1).sum(axis=0)
    max_count = (ranks == g).sum(axis=0)
    rev_freq = (ranks != baseline_rank[None, :]).sum(axis=0) / N_DRAWS
    for i, grp in enumerate(groups):
        rows.append({
            "group": grp,
            "T": T[i], "M": M[i], "baseline_T_over_M": tm[i],
            "baseline_rank": int(baseline_rank[i]),
            "interval_min_T_over_M": lo[i], "interval_max_T_over_M": hi[i],
            "mc_rank_min": int(ranks[:, i].min()), "mc_rank_max": int(ranks[:, i].max()),
            "rank_reversal_freq": float(rev_freq[i]),
            "P_is_min_T_over_M": float(min_count[i] / N_DRAWS),
            "P_is_max_T_over_M": float(max_count[i] / N_DRAWS),
        })
    mc_df = pd.DataFrame(rows)

    # ---------- 3. Boundary proximity under perturbed M (structural recompute) ----------
    rates = pd.read_csv(odm.COHORT_DIR / "transition_rates.csv").set_index("group")
    prox_rows = []
    for _, e in eq.iterrows():
        grp = e["group"]
        params = {c: float(rates.loc[grp, c]) for c in odm.RATE_NAMES}
        params["r"] = float(e["r"])
        I0 = float(e["I0"])
        for s in [0.5, 0.75, 1.0, 1.5, 2.0]:
            Mp = float(e["M_threshold"]) * s
            best = None
            for rate_name in list(params.keys()) + ["I0"]:
                if rate_name != "I0" and params[rate_name] <= 0:
                    continue
                pnr = odm.point_of_no_return(params, I0, Mp, rate_name, target="T")
                if not pnr["is_within_bounds"]:
                    continue
                prox = 1.0 - pnr["critical_factor"] if pnr["direction"] > 0 else pnr["critical_factor"] - 1.0
                prox = abs(pnr["critical_factor"] - 1.0)
                if best is None or prox < best["proximity"]:
                    best = {"rate_name": rate_name, "cf": pnr["critical_factor"], "proximity": prox}
            prox_rows.append({"group": grp, "s": s, "M_perturbed": Mp,
                              "T_over_M_perturbed": float(e["T_equilibrium"]) / Mp,
                              "closest_rate": best["rate_name"] if best else None,
                              "critical_factor": best["cf"] if best else np.nan,
                              "proximity": best["proximity"] if best else np.nan})
    prox_df = pd.DataFrame(prox_rows)

    # ---------- 4. Summary ----------
    spearman_q = np.quantile(spearman_vals, [0.01, 0.05, 0.5, 0.95, 0.99])
    kendall_q = np.quantile(kendall_vals, [0.01, 0.05, 0.5, 0.95, 0.99])
    summary = pd.DataFrame([
        {"metric": "n_pairs_reversible", "value": n_rev},
        {"metric": "n_pairs_total", "value": g * (g - 1) // 2},
        {"metric": "candidate_min_regions", "value": "; ".join(can_min)},
        {"metric": "candidate_max_regions", "value": "; ".join(can_max)},
        {"metric": "mc_min_group_probs", "value": "; ".join(
            f"{r.group}={r.P_is_min_T_over_M:.3f}" for r in mc_df.itertuples() if r.P_is_min_T_over_M > 0)},
        {"metric": "spearman_q01_q50_q99", "value": f"{spearman_q[0]:.3f}/{spearman_q[2]:.3f}/{spearman_q[4]:.3f}"},
        {"metric": "kendall_q01_q50_q99", "value": f"{kendall_q[0]:.3f}/{kendall_q[2]:.3f}/{kendall_q[4]:.3f}"},
        {"metric": "japan_rank_range", "value": f"{int(ranks[:, groups.index('Japanese')].min())}-{int(ranks[:, groups.index('Japanese')].max())}" if "Japanese" in groups else "n/a"},
    ])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    mc_df.to_csv(OUT_DIR / "REGION_SPECIFIC_M_SENSITIVITY.csv", index=False, encoding="utf-8-sig")
    pairs_df.to_csv(OUT_DIR / "REGION_SPECIFIC_M_INTERVAL_PAIRS.csv", index=False, encoding="utf-8-sig")
    prox_df.to_csv(OUT_DIR / "REGION_SPECIFIC_M_PROXIMITY.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT_DIR / "REGION_SPECIFIC_M_SUMMARY.csv", index=False, encoding="utf-8-sig")
    print(summary.to_string(index=False))
    print(mc_df[["group", "baseline_rank", "mc_rank_min", "mc_rank_max",
                 "rank_reversal_freq", "P_is_min_T_over_M", "P_is_max_T_over_M"]].to_string(index=False))
    print(prox_df.groupby("s")["closest_rate"].apply(lambda x: set(x.dropna())).to_string())


if __name__ == "__main__":
    main()
