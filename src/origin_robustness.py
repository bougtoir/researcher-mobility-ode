#!/usr/bin/env python3
"""
Robustness of the results to the origin-group assignment rule.

Baseline (data/cohort/cohort.csv): ``origin_group`` is the modal macro-region
over an author's works in the first three career years, with ties broken by
the earliest year a group first appears.  The ``abroad`` flag marks any work
affiliated with a non-origin macro-region within the first six career years.

Reviewers asked whether this assignment -- a modal early-career affiliation,
not an early-career first-observed affiliation and not a biographical origin
country -- changes the results, and whether multi-affiliated authors are
identifiable.  This script rebuilds each author's per-year macro-region sets
from the persisted ``authorships`` table of the full OpenAlex snapshot
(``data/cache/full_cohort.db``; no new API calls) and evaluates three rules:

    window3_mode   baseline: modal group over works in career years 0-2
    first_year     modal group over works in the first observed career year
    career_mode    modal group over all works in the career

For every rule it re-derives ``origin_group`` and ``abroad``, re-estimates
the transition rates, reruns the endogenous-inflow equilibrium and the
closest point of no return, and reports rank agreement (Spearman rho) with
the baseline plus the share of authors whose assignment changes.  The
origin-independent columns (hit, pi, active, recent_group) are carried over
from the baseline cohort file so that only the origin-dependent quantities
move.

Outputs (results/origin_robustness/):
    origin_rule_agreement.csv   assignment concordance and multi-affiliation stats
    origin_rule_rates.csv       transition rates per rule
    origin_rule_equilibrium.csv T, M, T/M, closest PNR per rule and region
    origin_rule_rank_agreement.csv  Spearman rho vs baseline per quantity
    origin_rule_flows.csv       observed origin->destination author flows per rule
"""

import argparse
import json
import sqlite3
import time
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

import cohort_extraction as ce
import ode_model_endogenous as odm
from extract_full_cohort import author_id_key  # noqa: F401  (kept for parity)

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "cache" / "full_cohort.db"
COHORT_PATH = BASE_DIR / "data" / "cohort" / "pi_proxy" / "cohort.csv"
RESULTS_DIR = BASE_DIR / "results" / "origin_robustness"


def modal_group(year_group_counts, first_year_by_group):
    """Replicate classify_author's tie-break: most frequent group, then
    earliest first appearance."""
    if not year_group_counts:
        return None
    return max(year_group_counts, key=lambda g: (year_group_counts[g], -first_year_by_group[g]))


def assign_origin(works, rule):
    """works: list of (year, frozenset-of-groups) sorted by year.

    Returns (origin, career_start) or (None, None) when no mappable
    affiliation exists in the origin window of the rule.
    """
    career_start = works[0][0]
    counter = Counter()
    first_year_by_group = {}
    if rule == "window3_mode":
        window_end = career_start + 2
    elif rule == "first_year":
        window_end = career_start
    elif rule == "career_mode":
        window_end = 10**9
    else:
        raise ValueError(rule)
    for year, groups in works:
        if year > window_end:
            break
        for g in groups:
            counter[g] += 1
            if g not in first_year_by_group:
                first_year_by_group[g] = year
    return modal_group(counter, first_year_by_group), career_start


def mark_abroad(works, origin, career_start, window):
    """Any work affiliated with a non-origin group within `window` career
    years after the first."""
    for year, groups in works:
        if year > career_start + window:
            break
        if any(g != origin for g in groups):
            return True
    return False


def load_author_year_groups(db_path, wanted_authors=None):
    """Stream the authorships table into {author_id: [(year, {groups})]}.

    ``wanted_authors`` restricts to authors of interest (the baseline cohort)
    to bound memory.  Rows are one per (work, author); country_codes is a
    JSON list, so multi-country authorships contribute several groups for a
    single work-year.
    """
    a2g, _ = ce.load_group_mapping()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT author_id, year, country_codes FROM authorships ORDER BY author_id, year")
    out = defaultdict(list)
    multi_affil = Counter()
    n_rows = 0
    for aid, year, ccs in cur:
        n_rows += 1
        if wanted_authors is not None and aid not in wanted_authors:
            continue
        codes = ccs.split(",") if ccs else []
        groups = frozenset(a2g[cc] for cc in codes if cc in a2g)
        out[aid].append((year, groups))
        if len(groups) > 1:
            multi_affil[aid] += 1
    conn.close()
    for aid in out:
        out[aid].sort()
    return out, multi_affil, n_rows


def build_rule_cohort(baseline, works_by_author, rule):
    """Re-derive origin_group/abroad under `rule`; carry over the
    origin-independent columns from the baseline cohort."""
    rows = []
    for rec in baseline.itertuples(index=False):
        works = works_by_author.get(rec.author_id)
        if not works:
            continue
        origin, career_start = assign_origin(works, rule)
        if origin is None:
            continue
        abroad = mark_abroad(works, origin, career_start, ce.ABROAD_WINDOW)
        rows.append({
            "author_id": rec.author_id,
            "career_start": career_start,
            "origin_group": origin,
            "abroad": abroad,
            "hit": rec.hit,
            "pi": rec.pi,
            "active": rec.active,
            "recent_group": rec.recent_group,
        })
    return pd.DataFrame(rows)


def closest_pnr_table(pnr_df, target="domestic_active"):
    p = pnr_df[(pnr_df["target"] == target) & (pnr_df["is_within_bounds"] == True)].copy()
    p["proximity"] = (p["critical_factor"] - 1.0).abs()
    return p.loc[p.groupby("group")["proximity"].idxmin()].set_index("group")


def evaluate_rule(cohort, rule, a2g, stats):
    rates = ce.estimate_rates(cohort)
    rates_idx = rates.set_index("group")
    summary, sens, pnr = odm.run_endogenous_model(
        save=False, scan_targets=("T", "P"), cohort_df=cohort, rates_df=rates_idx,
        a2g=a2g, stats=stats, compute_sensitivity=False, compute_pnr=True,
    )
    closest = closest_pnr_table(pnr)
    eq = summary.set_index("group")
    out = pd.DataFrame({
        "origin_rule": rule,
        "group": eq.index,
        "n_authors": rates_idx.loc[eq.index, "n"].values,
        "p_abroad": rates_idx.loc[eq.index, "p_abroad"].values,
        "alpha": rates_idx.loc[eq.index, "alpha"].values,
        "p_return": rates_idx.loc[eq.index, "p_return"].values,
        "T_equilibrium": eq["T_equilibrium"].values,
        "M_threshold": eq["M_threshold"].values,
        "T_over_M": (eq["T_equilibrium"] / eq["M_threshold"]).values,
        "closest_rate": closest.reindex(eq.index)["rate_name"].values,
        "critical_factor": closest.reindex(eq.index)["critical_factor"].values,
        "proximity": closest.reindex(eq.index)["proximity"].values,
    })
    return rates, out


def spearman(a, b):
    from scipy.stats import spearmanr
    return spearmanr(a, b).statistic


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-path", default=str(DB_PATH))
    parser.add_argument("--cohort", default=str(COHORT_PATH))
    parser.add_argument("--output-dir", default=str(RESULTS_DIR))
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    a2g = odm.load_group_mapping()
    stats = odm.compute_coauthor_stats(a2g)

    baseline = pd.read_csv(args.cohort, dtype={"author_id": str})
    baseline["author_id"] = baseline["author_id"].str.split("/").str[-1]
    wanted = set(baseline["author_id"])
    print(f"Baseline cohort: {len(baseline)} authors; streaming authorships ...")
    t0 = time.time()
    works_by_author, multi_affil, n_rows = load_author_year_groups(args.db_path, wanted)
    print(f"  {n_rows} authorship rows -> {len(works_by_author)} authors "
          f"in {time.time() - t0:.0f}s")

    rules = ["window3_mode", "first_year", "career_mode"]
    all_rates, all_eq, agreement_rows, flow_rows = [], [], [], []
    eq_by_rule, rates_by_rule, cohorts = {}, {}, {}
    for rule in rules:
        cohort = build_rule_cohort(baseline, works_by_author, rule)
        cohorts[rule] = cohort
        rates, eq = evaluate_rule(cohort, rule, a2g, stats)
        rates_by_rule[rule] = rates.set_index("group")
        eq_by_rule[rule] = eq.set_index("group")
        all_rates.append(rates.assign(origin_rule=rule))
        all_eq.append(eq)

        merged = cohort.merge(
            baseline[["author_id", "origin_group"]].rename(columns={"origin_group": "baseline_origin"}),
            on="author_id", how="left")
        n_same = int((merged["origin_group"] == merged["baseline_origin"]).sum())
        agreement_rows.append({
            "origin_rule": rule,
            "n_authors": len(cohort),
            "n_same_origin_as_baseline": n_same,
            "share_same_origin": n_same / len(cohort),
            "share_abroad": cohort["abroad"].mean(),
            "share_multi_affiliated_authors": float(
                sum(1 for aid in cohort["author_id"] if multi_affil.get(aid, 0) > 0) / len(cohort)),
        })

        flows = cohort[cohort["abroad"]].groupby(
            ["origin_group", "recent_group"]).size().reset_index(name="n_authors")
        flows = flows[flows["recent_group"].notna() & (flows["recent_group"] != flows["origin_group"])]
        flows["origin_rule"] = rule
        flow_rows.append(flows)

    base_eq = eq_by_rule["window3_mode"]
    base_rates = rates_by_rule["window3_mode"]
    rank_rows = []
    for rule in rules:
        eq = eq_by_rule[rule].reindex(base_eq.index)
        rates = rates_by_rule[rule].reindex(base_rates.index)
        rank_rows.append({
            "origin_rule": rule,
            "spearman_T_over_M": spearman(base_eq["T_over_M"], eq["T_over_M"]),
            "spearman_T": spearman(base_eq["T_equilibrium"], eq["T_equilibrium"]),
            "spearman_proximity": spearman(base_eq["proximity"], eq["proximity"]),
            "spearman_alpha": spearman(base_rates["alpha"], rates["alpha"]),
            "spearman_p_abroad": spearman(base_rates["p_abroad"], rates["p_abroad"]),
            "spearman_p_return": spearman(base_rates["p_return"], rates["p_return"]),
            "same_min_T_over_M_group": bool(
                base_eq["T_over_M"].idxmin() == eq["T_over_M"].idxmin()),
            "same_closest_group": bool(
                base_eq.sort_values("proximity").index[0] == eq.sort_values("proximity").index[0]),
        })

    pd.DataFrame(agreement_rows).to_csv(out_dir / "origin_rule_agreement.csv", index=False)
    pd.concat(all_rates).to_csv(out_dir / "origin_rule_rates.csv", index=False)
    pd.concat(all_eq).to_csv(out_dir / "origin_rule_equilibrium.csv", index=False)
    pd.DataFrame(rank_rows).to_csv(out_dir / "origin_rule_rank_agreement.csv", index=False)
    pd.concat(flow_rows).to_csv(out_dir / "origin_rule_flows.csv", index=False)

    print("\nAgreement vs baseline assignment:")
    print(pd.DataFrame(agreement_rows).to_string(index=False))
    print("\nRank agreement (Spearman rho vs baseline):")
    print(pd.DataFrame(rank_rows).to_string(index=False))
    print(f"\nWrote {out_dir}")


if __name__ == "__main__":
    main()
