"""PI-proxy propagation, P-pool side (Gate 1.5 completion).

measurement_validity.py records T-side outcomes per PI definition; this driver
records the PI-dependent side: P_D equilibrium, margin_to_threshold_P and the
P-target PNR closest factor — the quantities that actually respond to the
proxy choice.
"""
import pandas as pd

import cohort_extraction as ce
import ode_model_endogenous as odm
from measurement_validity import (OUT, build_cohort, coauthor_counts,
                                  closest_pnr_table, stream_authorships)
from origin_robustness import COHORT_PATH, DB_PATH

import time

a2g = odm.load_group_mapping()
stats = odm.compute_coauthor_stats(a2g)
baseline = pd.read_csv(COHORT_PATH, dtype={"author_id": str})
baseline["author_id"] = baseline["author_id"].str.split("/").str[-1]
wanted = set(baseline["author_id"])
t0 = time.time()
wba, *_ = stream_authorships(DB_PATH, wanted)
print(f"streamed in {time.time()-t0:.0f}s", flush=True)

pi = {}
for rec in baseline.itertuples(index=False):
    works = wba.get(rec.author_id, [])
    n_last = sum(1 for w in works if w[2] == "last" or w[4] == 1)
    pi[rec.author_id] = {
        "pi_last": n_last >= 1,
        "pi_corr": any(bool(w[3]) for w in works),
        "pi_last2": n_last >= 2,
        "pi_career8": (rec.career_end - rec.career_start + 1) >= 8}
nco = coauthor_counts(DB_PATH, wanted, OUT / "COAUTHOR_COUNTS.csv")
base_origin = baseline.set_index("author_id")["origin_group"]
p90 = nco.groupby(base_origin.reindex(nco.index)).quantile(0.9)
for aid, d in pi.items():
    d["pi_centrality"] = nco.get(aid, 0) >= p90.get(base_origin.get(aid), 1e18)
    d["pi_combined"] = d["pi_last"] or d["pi_corr"] or d["pi_career8"]
pidf = pd.DataFrame(pi).T
pidf.index.name = "author_id"

rows = []
for d in ["pi_last", "pi_corr", "pi_last2", "pi_career8",
          "pi_centrality", "pi_combined"]:
    coh = baseline.copy()
    coh["pi"] = coh["author_id"].map(pidf[d]).fillna(False)
    rates = ce.estimate_rates(coh).set_index("group")
    summary, _, pnr = odm.run_endogenous_model(
        save=False, scan_targets=("P",), cohort_df=coh, rates_df=rates,
        a2g=a2g, stats=stats, compute_sensitivity=False, compute_pnr=True)
    eq = summary.set_index("group")
    cp = pnr[pnr["target"] == "domestic_PIs"].copy()
    cp["proximity"] = (cp["critical_factor"] - 1.0).abs()
    cp = cp.loc[cp.groupby("group")["proximity"].idxmin()].set_index("group")
    for g in eq.index:
        rows.append({"pi_definition": d, "group": g,
                     "P_D_equilibrium": eq.loc[g, "P_D_equilibrium"],
                     "M_threshold_P": eq.loc[g, "P_D_equilibrium"]
                     - eq.loc[g, "margin_to_threshold_P"],
                     "margin_to_threshold_P": eq.loc[g, "margin_to_threshold_P"],
                     "P_over_M_P": eq.loc[g, "P_D_equilibrium"]
                     / (eq.loc[g, "P_D_equilibrium"]
                        - eq.loc[g, "margin_to_threshold_P"]),
                     "closest_P_rate": cp.loc[g, "rate_name"]
                     if g in cp.index else None,
                     "closest_P_factor": cp.loc[g, "critical_factor"]
                     if g in cp.index else None})
    print(f"{d} done", flush=True)
pd.DataFrame(rows).to_csv(OUT / "PI_PROPAGATION_P.csv", index=False)
print("wrote PI_PROPAGATION_P.csv")
