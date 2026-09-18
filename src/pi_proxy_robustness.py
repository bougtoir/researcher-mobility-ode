#!/usr/bin/env python3
"""
Robustness of the steady-state results to the PI proxy definition.

The published cohort (data/cohort/cohort.csv) defines a PI as an author with
at least one last-author paper.  The full OpenAlex cohort re-extracted with
`extract_full_cohort.py --output-dir data/cohort/pi_proxy` stores, for every
author, the first qualifying year under three definitions:

    first_last      first last-author paper (baseline definition)
    corresponding   first paper flagged authorships.is_corresponding
    recurrent_last  second last-author paper (last author on >= 2 papers)

For each definition we re-estimate the transition rates, recompute the
endogenous-inflow equilibrium (T, M, T/M) and the closest point of no return
for the domestic active pool, and compare the nine-region rankings with the
baseline definition (Spearman rho) and with the published results.

Outputs (results/pi_proxy/):
    pi_proxy_rates.csv          transition rates per definition
    pi_proxy_equilibrium.csv    T, M, T/M, closest PNR per definition and region
    pi_proxy_rank_agreement.csv Spearman rho and rank statistics per definition
"""

import argparse
from pathlib import Path

import pandas as pd

import cohort_extraction as ce
import ode_model_endogenous as odm

BASE_DIR = Path(__file__).resolve().parent.parent
PROXY_COHORT_DIR = BASE_DIR / "data" / "cohort" / "pi_proxy"
RESULTS_DIR = BASE_DIR / "results" / "pi_proxy"
ENDO_DIR = BASE_DIR / "results" / "endogenous"


def closest_pnr_table(pnr_df, target="domestic_active"):
    p = pnr_df[(pnr_df["target"] == target) & (pnr_df["is_within_bounds"] == True)].copy()
    p["proximity"] = (p["critical_factor"] - 1.0).abs()
    closest = p.loc[p.groupby("group")["proximity"].idxmin()]
    return closest.set_index("group")[["rate_name", "critical_factor", "proximity"]]


def evaluate_definition(cohort, definition, a2g, stats):
    df = cohort.copy()
    col = f"pi_year_{definition}"
    df["pi_year"] = df[col]
    df["pi"] = df[col].notna()
    rates = ce.estimate_rates(df)
    rates_idx = rates.set_index("group")
    summary, sens, pnr = odm.run_endogenous_model(
        save=False, scan_targets=("T", "P"), cohort_df=df, rates_df=rates_idx,
        a2g=a2g, stats=stats, compute_sensitivity=True, compute_pnr=True,
    )
    closest = closest_pnr_table(pnr)
    closest_p = closest_pnr_table(pnr, target="domestic_PIs")
    eq = summary.set_index("group")
    pi_inflow = eq["r"] * eq["P_D_eq"]
    el = sens[(sens["target"] == "domestic_active") & (sens["rate"].isin(["p_D", "r"]))] if sens is not None else None
    el_pD = el[el["rate"] == "p_D"].set_index("group")["elasticity"] if el is not None else pd.Series(dtype=float)
    el_r = el[el["rate"] == "r"].set_index("group")["elasticity"] if el is not None else pd.Series(dtype=float)
    out = pd.DataFrame({
        "pi_definition": definition,
        "group": eq.index,
        "n_authors": rates_idx.loc[eq.index, "n"].values,
        "p_pi_domestic": rates_idx.loc[eq.index, "p_pi_domestic"].values,
        "p_D": rates_idx.loc[eq.index, "p_D"].values,
        "p_A": rates_idx.loc[eq.index, "p_A"].values,
        "r": eq["r"].values,
        "I0": eq["I0"].values,
        "T_equilibrium": eq["T_equilibrium"].values,
        "M_threshold": eq["M_threshold"].values,
        "T_over_M": (eq["T_equilibrium"] / eq["M_threshold"]).values,
        "closest_rate": closest.reindex(eq.index)["rate_name"].values,
        "critical_factor": closest.reindex(eq.index)["critical_factor"].values,
        "proximity": closest.reindex(eq.index)["proximity"].values,
        # Quantities that depend on the PI proxy (T and the I0 proximity do not,
        # because I0 is calibrated so that total equilibrium inflow equals observed entry).
        "P_D_equilibrium": eq["P_D_eq"].values,
        "P_D_over_k": (eq["P_D_eq"] / eq["k_used"]).values,
        "pi_driven_inflow_share": (pi_inflow / (eq["I0"] + pi_inflow)).values,
        "closest_rate_P": closest_p.reindex(eq.index)["rate_name"].values,
        "proximity_P": closest_p.reindex(eq.index)["proximity"].values,
        "elasticity_T_p_D": el_pD.reindex(eq.index).values,
        "elasticity_T_r": el_r.reindex(eq.index).values,
    })
    rates["pi_definition"] = definition
    return out, rates


def rank_agreement(df, base, label):
    d = df.set_index("group").reindex(base.index)
    return {
        "pi_definition": str(df["pi_definition"].iloc[0]),
        "reference": label,
        "spearman_T_over_M": float(d["T_over_M"].corr(base["T_over_M"], method="spearman")),
        "spearman_proximity": float(d["proximity"].corr(base["proximity"], method="spearman")),
        "spearman_T": float(d["T_equilibrium"].corr(base["T_equilibrium"], method="spearman")),
        "spearman_p_D": float(d["p_D"].corr(base["p_D"], method="spearman")),
        "spearman_P_D": float(d["P_D_equilibrium"].corr(base["P_D_equilibrium"], method="spearman")) if "P_D_equilibrium" in d and "P_D_equilibrium" in base else float("nan"),
        "spearman_pi_inflow_share": float(d["pi_driven_inflow_share"].corr(base["pi_driven_inflow_share"], method="spearman")) if "pi_driven_inflow_share" in d and "pi_driven_inflow_share" in base else float("nan"),
        "spearman_proximity_P": float(d["proximity_P"].corr(base["proximity_P"], method="spearman")) if "proximity_P" in d and "proximity_P" in base else float("nan"),
        "same_min_T_over_M_group": bool(d["T_over_M"].idxmin() == base["T_over_M"].idxmin()),
        "same_closest_group": bool(d["proximity"].idxmin() == base["proximity"].idxmin()),
        "n_closest_rate_same": int((d["closest_rate"] == base["closest_rate"]).sum()),
        "n_groups": int(len(d)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", default=str(PROXY_COHORT_DIR / "cohort.csv"))
    parser.add_argument("--results-dir", default=str(RESULTS_DIR))
    args = parser.parse_args()
    out_dir = Path(args.results_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cohort = pd.read_csv(args.cohort, low_memory=False)
    missing = [c for c in (f"pi_year_{d}" for d in ce.PI_DEFINITIONS) if c not in cohort.columns]
    if missing:
        raise SystemExit(f"Cohort lacks PI proxy columns {missing}; re-extract with extract_full_cohort.py")

    a2g = odm.load_group_mapping()
    stats = odm.compute_coauthor_stats(a2g)

    eq_frames, rate_frames = [], []
    for definition in ce.PI_DEFINITIONS:
        eq, rates = evaluate_definition(cohort, definition, a2g, stats)
        eq_frames.append(eq)
        rate_frames.append(rates)
        print(f"[{definition}]")
        print(eq[["group", "p_pi_domestic", "T_over_M", "closest_rate", "proximity", "P_D_equilibrium", "pi_driven_inflow_share", "closest_rate_P", "proximity_P", "elasticity_T_p_D"]].to_string(index=False))

    eq_all = pd.concat(eq_frames, ignore_index=True)
    eq_all["rank_T_over_M"] = eq_all.groupby("pi_definition")["T_over_M"].rank().astype("Int64")
    eq_all["rank_proximity"] = eq_all.groupby("pi_definition")["proximity"].rank(method="min").astype("Int64")
    eq_all.to_csv(out_dir / "pi_proxy_equilibrium.csv", index=False, encoding="utf-8-sig")
    pd.concat(rate_frames, ignore_index=True).to_csv(out_dir / "pi_proxy_rates.csv", index=False, encoding="utf-8-sig")

    # Reference 1: baseline definition on the same snapshot.
    base = eq_all[eq_all["pi_definition"] == "first_last"].set_index("group")
    rows = [rank_agreement(eq_all[eq_all["pi_definition"] == d], base, "first_last_same_snapshot")
            for d in ce.PI_DEFINITIONS]

    # Reference 2: published results (results/endogenous), if present.
    pub_eq_path = ENDO_DIR / "equilibrium_summary.csv"
    pub_pnr_path = ENDO_DIR / "point_of_no_return.csv"
    if pub_eq_path.exists() and pub_pnr_path.exists():
        pub = pd.read_csv(pub_eq_path).set_index("group")
        pub_closest = closest_pnr_table(pd.read_csv(pub_pnr_path))
        pub_rates = pd.read_csv(odm.COHORT_DIR / "transition_rates.csv").set_index("group")
        published = pd.DataFrame({
            "T_equilibrium": pub["T_equilibrium"],
            "T_over_M": pub["T_equilibrium"] / pub["M_threshold"],
            "p_D": pub_rates.reindex(pub.index)["p_D"],
            "closest_rate": pub_closest.reindex(pub.index)["rate_name"],
            "proximity": pub_closest.reindex(pub.index)["proximity"],
        })
        for d in ce.PI_DEFINITIONS:
            rows.append(rank_agreement(eq_all[eq_all["pi_definition"] == d], published, "published_results"))

    agreement = pd.DataFrame(rows)
    agreement.to_csv(out_dir / "pi_proxy_rank_agreement.csv", index=False, encoding="utf-8-sig")
    print(agreement.to_string(index=False))

    # Snapshot descriptors for the manuscript.
    meta = pd.DataFrame([{
        "n_authors_snapshot": int(len(cohort)),
        "n_authors_published": int(len(pd.read_csv(odm.COHORT_DIR / "cohort.csv", usecols=["author_id"]))),
        **{f"share_pi_{d}": float(cohort[f"pi_year_{d}"].notna().mean()) for d in ce.PI_DEFINITIONS},
    }])
    meta.to_csv(out_dir / "pi_proxy_snapshot.csv", index=False, encoding="utf-8-sig")
    print(f"Saved to {out_dir}")


if __name__ == "__main__":
    main()
