#!/usr/bin/env python3
"""
Sensitivity of the point-of-no-return results to the minimum viable coauthor
scale M.

M = k x c_bar is scaled by a set of multipliers while the fitted transition
rates, inflow parameters and equilibria are held fixed.  For each multiplier
and macro-region we recompute T/M, the closest point-of-no-return lever and
its proximity, and compare the resulting rankings with the baseline (M x 1).
Elasticities of T do not depend on M, so the dropout-versus-outflow
comparison (P2) is reported once and flagged as invariant.
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import ode_model_endogenous as odm


BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results" / "m_sensitivity"
ENDO_DIR = BASE_DIR / "results" / "endogenous"


def closest_pnr(params, I0, M):
    best = None
    for rate_name in list(params.keys()) + ["I0"]:
        if rate_name != "I0" and params[rate_name] <= 0:
            continue
        pnr = odm.point_of_no_return(params, I0, M, rate_name, target="T")
        if not pnr["is_within_bounds"]:
            continue
        prox = abs(pnr["critical_factor"] - 1.0)
        if best is None or prox < best["proximity"]:
            best = {"rate_name": rate_name, "critical_factor": pnr["critical_factor"], "proximity": prox}
    if best is None:
        best = {"rate_name": None, "critical_factor": np.nan, "proximity": np.nan}
    return best


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--multipliers", type=float, nargs="+",
                        default=[0.5, 0.75, 1.0, 1.25, 1.5, 2.0])
    parser.add_argument("--results-dir", default=str(RESULTS_DIR))
    args = parser.parse_args()
    out_dir = Path(args.results_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    eq = pd.read_csv(ENDO_DIR / "equilibrium_summary.csv")
    sens = pd.read_csv(ENDO_DIR / "sensitivity.csv")
    sens = sens[sens["target"] == "domestic_active"]
    rates = pd.read_csv(odm.COHORT_DIR / "transition_rates.csv").set_index("group")

    rows = []
    for _, e in eq.iterrows():
        g = e["group"]
        params = {c: float(rates.loc[g, c]) for c in odm.RATE_NAMES}
        params["r"] = float(e["r"])
        I0 = float(e["I0"])
        M0 = float(e["M_threshold"])
        T = float(e["T_equilibrium"])
        sg = sens[sens["group"] == g].set_index("rate")["elasticity"]
        e_d = float(sg.get("d", np.nan))
        e_alpha = float(sg.get("alpha", np.nan))
        for mult in args.multipliers:
            M = M0 * mult
            best = closest_pnr(params, I0, M)
            rows.append({
                "group": g,
                "M_multiplier": mult,
                "M_threshold": M,
                "T_equilibrium": T,
                "T_over_M": T / M,
                "below_M": T <= M,
                "closest_rate": best["rate_name"],
                "critical_factor": best["critical_factor"],
                "proximity": best["proximity"],
                "elasticity_d": e_d,
                "elasticity_alpha": e_alpha,
                "abs_e_d_gt_abs_e_alpha": abs(e_d) > abs(e_alpha),
            })
    df = pd.DataFrame(rows)
    df["rank_T_over_M"] = df.groupby("M_multiplier")["T_over_M"].rank(ascending=True).astype(int)
    df["rank_proximity"] = df.groupby("M_multiplier")["proximity"].rank(ascending=True, method="min")
    df.to_csv(out_dir / "m_sensitivity.csv", index=False, encoding="utf-8-sig")

    base = df[np.isclose(df["M_multiplier"], 1.0)].set_index("group")
    summ = []
    for mult, d in df.groupby("M_multiplier"):
        d = d.set_index("group").reindex(base.index)
        rho_tm = float(d["T_over_M"].corr(base["T_over_M"], method="spearman"))
        rho_prox = float(d["proximity"].corr(base["proximity"], method="spearman"))
        summ.append({
            "M_multiplier": mult,
            "n_below_M": int(d["below_M"].sum()),
            "min_T_over_M": float(d["T_over_M"].min()),
            "min_T_over_M_group": str(d["T_over_M"].idxmin()),
            "closest_group": str(d["proximity"].idxmin()) if d["proximity"].notna().any() else None,
            "closest_rate_all_I0": bool((d["closest_rate"] == "I0").all()),
            "closest_rate_unchanged_vs_base": int((d["closest_rate"] == base["closest_rate"]).sum()),
            "spearman_T_over_M_vs_base": rho_tm,
            "spearman_proximity_vs_base": rho_prox,
            "n_d_more_elastic_than_alpha": int(d["abs_e_d_gt_abs_e_alpha"].sum()),
            "n_groups": int(len(d)),
        })
    summary = pd.DataFrame(summ)
    summary.to_csv(out_dir / "m_sensitivity_summary.csv", index=False, encoding="utf-8-sig")
    print(df.to_string(index=False))
    print(summary.to_string(index=False))
    print(f"\nSaved to {out_dir}")


if __name__ == "__main__":
    main()
