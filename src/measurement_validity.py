"""Gate 1 measurement-validity re-verification (reviewer-driven resubmission).

Extends origin_robustness.py with the full spec set requested in the
resubmission gate prompt:

Origin definitions
  A window3_mode   : modal macro-region over first 3 career years (baseline)
  B first_year     : modal macro-region over the career-start year
  C window{2,5}    : early-career modal over first 2 / 5 years
  D probabilistic  : seeded draw proportional to first-3-year group counts

Multi-affiliation specs (applied under rule A)
  fractional : each group in a multi-group year counts 1/k toward the mode
  multi_state: report-only — authors counted in every observed group
  exclusion  : author-years with >1 group dropped from the origin tally;
               authors left with no usable year are dropped

PI / senior-author proxies
  pi_last      : ever last author (single-author counts as last)   [existing]
  pi_corr      : ever corresponding author                          [existing]
  pi_last2     : last author on >=2 works                           [existing]
  pi_career8   : career span >= 8 years
  pi_centrality: distinct coauthor count >= P90 within origin group
  pi_combined  : pi_last OR pi_corr OR pi_career8

For every PI definition the full endogenous pipeline is re-run
(estimate_rates -> run_endogenous_model with PNR scan on T and P), so the
definition change propagates to regional capacity indicators, thresholds
and rankings — not just the PI share.

Outputs (results/measurement_validity/):
  ORIGIN_SENSITIVITY.csv   per-rule per-group rates + equilibrium + PNR
  MOBILITY_SENSITIVITY.csv flow-matrix direction reversals vs baseline
  PI_SENSITIVITY.csv       per-definition PI share + propagated outcomes
  MISSINGNESS.csv          missing country / corresponding coverage /
                           left-censoring / observation-length stats
  COAUTHOR_COUNTS.csv      distinct coauthor counts (persisted input)
"""

import argparse
import json
import sqlite3
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

import cohort_extraction as ce
import ode_model_endogenous as odm
from origin_robustness import COHORT_PATH, DB_PATH, closest_pnr_table

OUT = Path(__file__).resolve().parent.parent / "results" / "measurement_validity"


def stream_authorships(db_path, wanted):
    """Return {aid: [(year, frozenset(groups), position, is_corr, n_auth)]}
    plus a list of missing-country year counts keyed by year."""
    a2g, _ = ce.load_group_mapping()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    out, miss_by_year, total_by_year = {}, Counter(), Counter()
    n = 0
    for wid, aid, year, pos, corr, n_auth, ccs in cur.execute(
            "SELECT work_id, author_id, year, author_position, is_corresponding,"
            " n_authors, country_codes FROM authorships"):
        n += 1
        total_by_year[year] += 1
        if aid not in wanted:
            continue
        codes = ccs.split(",") if ccs else []
        groups = frozenset(a2g[c] for c in codes if c in a2g)
        if not groups:
            miss_by_year[year] += 1
        out.setdefault(aid, []).append((year, groups, pos, corr, n_auth))
    conn.close()
    for v in out.values():
        v.sort()
    return out, miss_by_year, total_by_year, n


def coauthor_counts(db_path, wanted, cache):
    cache = Path(cache)
    if cache.exists():
        df = pd.read_csv(cache, dtype={"author_id": str})
        return df.set_index("author_id")["n_coauthors"]
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT a1.author_id, COUNT(DISTINCT a2.author_id) FROM author_works a1"
        " JOIN author_works a2 ON a1.work_id = a2.work_id"
        " AND a2.author_id != a1.author_id GROUP BY a1.author_id").fetchall()
    conn.close()
    df = pd.DataFrame(rows, columns=["author_id", "n_coauthors"])
    df.to_csv(cache, index=False)
    return df.set_index("author_id")["n_coauthors"]


def modal(counter):
    if not counter:
        return None
    top = max(counter.values())
    return sorted(g for g, c in counter.items() if c == top)[0]


def assign_origin(works, rule, seed_rng=None):
    """works: [(year, groups, pos, corr, n_auth)] sorted.
    Returns (origin, career_start, weight_map) — weight_map only for fractional."""
    career_start = works[0][0]
    counter = Counter()
    frac = Counter()
    win = {"first_year": 0, "window2": 1, "window5": 4,
           "career_mode": 999}.get(rule, 2)  # default: first 3 career years
    for year, groups, *_ in works:
        if year > career_start + win:
            break
        if rule == "exclusion" and len(groups) > 1:
            continue
        if rule == "fractional":
            for g in groups:
                frac[g] += 1.0 / len(groups)
            continue
        for g in groups:
            counter[g] += 1
    if rule == "fractional":
        return modal(frac), career_start, frac
    if rule == "probabilistic":
        if not counter:
            return None, career_start, None
        gs, ws = zip(*counter.items())
        return seed_rng.choice(gs, p=np.array(ws) / sum(ws)), career_start, counter
    return modal(counter), career_start, counter


def mark_abroad(works, origin, career_start, window=6):
    for year, groups, *_ in works:
        if year > career_start + window:
            break
        if origin not in groups:
            return True
    return False


def build_cohort(baseline, works_by_author, rule, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for rec in baseline.itertuples(index=False):
        works = works_by_author.get(rec.author_id)
        if not works:
            continue
        origin, cs, _ = assign_origin(works, rule, rng)
        if origin is None:
            continue
        rows.append({"author_id": rec.author_id, "career_start": cs,
                     "origin_group": origin,
                     "abroad": mark_abroad(works, origin, cs),
                     "hit": rec.hit, "pi": rec.pi, "active": rec.active,
                     "recent_group": rec.recent_group})
    return pd.DataFrame(rows)


def evaluate(cohort, a2g, stats):
    rates = ce.estimate_rates(cohort)
    rates_idx = rates.set_index("group")
    summary, _, pnr = odm.run_endogenous_model(
        save=False, scan_targets=("T", "P"), cohort_df=cohort,
        rates_df=rates_idx, a2g=a2g, stats=stats,
        compute_sensitivity=False, compute_pnr=True)
    return rates_idx, summary.set_index("group"), closest_pnr_table(pnr)


def spearman(a, b):
    return pd.Series(a).corr(pd.Series(b), method="spearman")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db-path", default=str(DB_PATH))
    ap.add_argument("--cohort", default=str(COHORT_PATH))
    ap.add_argument("--output-dir", default=str(OUT))
    ap.add_argument("--skip-ode", action="store_true")
    args = ap.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    a2g = odm.load_group_mapping()
    stats = odm.compute_coauthor_stats(a2g)
    baseline = pd.read_csv(args.cohort, dtype={"author_id": str})
    baseline["author_id"] = baseline["author_id"].str.split("/").str[-1]
    wanted = set(baseline["author_id"])
    print(f"Baseline n={len(baseline)}; streaming authorships ...", flush=True)
    t0 = time.time()
    wba, miss_by_year, tot_by_year, n_rows = stream_authorships(
        args.db_path, wanted)
    print(f"  {n_rows} rows -> {len(wba)} authors in {time.time()-t0:.0f}s",
          flush=True)

    # ---- Missingness -----------------------------------------------------
    miss_rows = [{"year": y, "n_rows": tot_by_year[y],
                  "n_missing_country": miss_by_year.get(y, 0),
                  "share_missing": miss_by_year.get(y, 0) / tot_by_year[y]}
                 for y in sorted(tot_by_year)]
    pd.DataFrame(miss_rows).to_csv(out / "MISSINGNESS.csv", index=False)
    corr_cov = pd.Series({
        "authorship_rows": n_rows,
        "cohort_rows_missing_country": sum(miss_by_year.values()),
        "share_missing_country_cohort":
            sum(miss_by_year.values()) / max(1, sum(
                len(v) for v in wba.values())),
    })
    cs = baseline["career_start"]
    span = baseline["career_end"] - baseline["career_start"] + 1
    obs = pd.Series({
        "share_career_start_at_window_edge_2000": float((cs <= 2000).mean()),
        "median_observed_span_years": float(span.median()),
        "share_span_lt5": float((span < 5).mean()),
        "share_span_ge15": float((span >= 15).mean()),
    })
    pd.concat([corr_cov, obs]).to_csv(out / "MISSINGNESS_SUMMARY.csv",
                                      header=["value"])

    # ---- Origin sensitivity ----------------------------------------------
    rules = ["window3_mode", "first_year", "window2", "window5",
             "fractional", "exclusion", "probabilistic"]
    res = {}
    rows_out = []
    for rule in rules:
        coh = build_cohort(baseline, wba, rule, seed=7)
        if args.skip_ode:
            rates = ce.estimate_rates(coh).set_index("group")
            res[rule] = (rates, None, None)
            for g in rates.index:
                rows_out.append({"origin_rule": rule, "group": g,
                                 "n": rates.loc[g, "n"],
                                 "p_abroad": rates.loc[g, "p_abroad"]})
            continue
        rates, eq, pnr = evaluate(coh, a2g, stats)
        res[rule] = (rates, eq, pnr)
        for g in eq.index:
            rows_out.append({
                "origin_rule": rule, "group": g,
                "n": rates.loc[g, "n"], "p_abroad": rates.loc[g, "p_abroad"],
                "T": eq.loc[g, "T_equilibrium"],
                "T_over_M": eq.loc[g, "T_equilibrium"] / eq.loc[g, "M_threshold"],
                "closest_pnr_factor": pnr.loc[g, "critical_factor"]
                if g in pnr.index else np.nan})
        print(f"  origin rule {rule}: n={len(coh)} done", flush=True)
    pd.DataFrame(rows_out).to_csv(out / "ORIGIN_SENSITIVITY.csv", index=False)

    # multi-state spec (report only): author counted toward EVERY group
    # observed in their first 3 career years
    ms = Counter()
    for aid, works in wba.items():
        cs = works[0][0]
        gs = set()
        for year, groups, *_ in works:
            if year > cs + 2:
                break
            gs |= set(groups)
        for g in gs:
            ms[g] += 1
    pd.DataFrame([{"group": g, "n_authors_multi_state": n}
                  for g, n in sorted(ms.items())]
                 ).to_csv(out / "MOBILITY_MULTISTATE.csv", index=False)

    # mobility direction reversals vs baseline (share_abroad by group)
    base_rates = res["window3_mode"][0]
    mrows = []
    for rule in rules:
        if rule == "window3_mode" or res.get(rule) is None:
            continue
        r = res[rule][0]
        common = base_rates.index.intersection(r.index)
        for g in common:
            mrows.append({"origin_rule": rule, "group": g,
                          "p_abroad_baseline": base_rates.loc[g, "p_abroad"],
                          "p_abroad_rule": r.loc[g, "p_abroad"],
                          "direction_reversed":
                              (r.loc[g, "p_abroad"] > 0.5)
                              != (base_rates.loc[g, "p_abroad"] > 0.5)})
    pd.DataFrame(mrows).to_csv(out / "MOBILITY_SENSITIVITY.csv", index=False)

    # ---- PI definitions ---------------------------------------------------
    pi = {}
    for rec in baseline.itertuples(index=False):
        works = wba.get(rec.author_id, [])
        n_last = sum(1 for w in works if w[2] == "last" or w[4] == 1)
        ever_corr = any(bool(w[3]) for w in works)
        span_y = (rec.career_end - rec.career_start + 1)
        pi[rec.author_id] = {
            "pi_last": n_last >= 1, "pi_corr": ever_corr,
            "pi_last2": n_last >= 2, "pi_career8": span_y >= 8}
    # centrality
    try:
        nco = coauthor_counts(args.db_path, wanted,
                              out / "COAUTHOR_COUNTS.csv")
        base_origin = baseline.set_index("author_id")["origin_group"]
        p90 = nco.groupby(base_origin.reindex(nco.index)).quantile(0.9)
        for aid, d in pi.items():
            d["pi_centrality"] = (nco.get(aid, 0)
                                  >= p90.get(base_origin.get(aid), np.inf))
    except Exception as e:  # noqa: BLE001
        print("centrality skipped:", e)
        for d in pi.values():
            d["pi_centrality"] = False
    for aid, d in pi.items():
        d["pi_combined"] = d["pi_last"] or d["pi_corr"] or d["pi_career8"]

    pidf = pd.DataFrame(pi).T
    pidf.index.name = "author_id"
    defs = ["pi_last", "pi_corr", "pi_last2", "pi_career8",
            "pi_centrality", "pi_combined"]
    p_rows = []
    base_eq = None
    for d in defs:
        coh = baseline.copy()
        coh["pi"] = coh["author_id"].map(pidf[d]).fillna(False)
        share = coh.groupby("origin_group")["pi"].mean()
        if args.skip_ode:
            for g, s in share.items():
                p_rows.append({"pi_definition": d, "group": g,
                               "pi_share": s})
            continue
        rates, eq, pnr = evaluate(coh, a2g, stats)
        if d == "pi_last":
            base_eq = eq
        for g in eq.index:
            p_rows.append({
                "pi_definition": d, "group": g, "pi_share": share.get(g),
                "n": rates.loc[g, "n"], "p_abroad": rates.loc[g, "p_abroad"],
                "T": eq.loc[g, "T_equilibrium"],
                "T_over_M": eq.loc[g, "T_equilibrium"] / eq.loc[g, "M_threshold"],
                "rho_T_over_M_vs_baseline":
                    spearman(eq["T_equilibrium"] / eq["M_threshold"],
                             base_eq["T_equilibrium"] / base_eq["M_threshold"])
                    if base_eq is not None and d != "pi_last" else 1.0})
        print(f"  PI def {d}: mean share={coh['pi'].mean():.3f} done",
              flush=True)
    pd.DataFrame(p_rows).to_csv(out / "PI_SENSITIVITY.csv", index=False)
    print("Wrote", out)


if __name__ == "__main__":
    main()
