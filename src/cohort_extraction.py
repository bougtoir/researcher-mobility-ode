#!/usr/bin/env python3
"""
Build an AI/ML researcher cohort from OpenAlex and estimate crude transition
rates for the per-civilisation ODE model.

Usage:
    python src/cohort_extraction.py --sample-per-group 200 --max-authors 0
"""

import argparse
import json
import math
import time
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

from openalex_client import OpenAlexBudgetExhausted, OpenAlexClient


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache" / "openalex"
COHORT_DIR = DATA_DIR / "cohort"

SUBFIELD = "subfields/1702"
CAREER_START_MIN = 2000
CAREER_START_MAX = 2016
MIN_WORKS = 2
ABROAD_WINDOW = 6
HIT_WINDOW = 8
DROPOUT_LATEST_YEAR = 2019  # no work in 2020-2023 -> dropout (as of 2023)


def load_group_mapping():
    with open(DATA_DIR / "country_civilization_mapping.json", "r", encoding="utf-8") as f:
        mapping = json.load(f)
    a2g = {}
    group_to_a2 = defaultdict(list)
    for a3, info in mapping.items():
        a2 = info.get("alpha_2")
        g = info.get("group")
        if a2 and g:
            a2g[a2] = g
            group_to_a2[g].append((a2, info.get("ai_ml_works_2022_2023", 0)))
    return a2g, group_to_a2


def load_origin_overrides():
    """Load manually audited origin-group overrides so they are reproducible."""
    override_path = COHORT_DIR / "author_origin_overrides.csv"
    if not override_path.exists():
        return {}
    df = pd.read_csv(override_path, dtype=str)
    df = df.dropna(subset=["author_id", "origin_group"])
    return dict(zip(df["author_id"].astype(str), df["origin_group"]))


def group_country_codes(group_to_a2, group):
    """Return alpha-2 country codes for a group, sorted by AI/ML output."""
    return [a2 for a2, _ in sorted(group_to_a2[group], key=lambda x: -x[1])]


def top_residual_codes(group_to_a2, top_n=50):
    """Return the top alpha-2 codes in Other Civilizations by AI/ML output."""
    return group_country_codes(group_to_a2, "Other Civilizations")[:top_n]


def author_id_key(raw_id):
    if not raw_id:
        return None
    return raw_id.split("/")[-1]


def work_groups_for_author(work, target_aid, a2g):
    """Return list of civilization groups for the target author in this work."""
    for auth in work.get("authorships", []):
        aid = author_id_key((auth.get("author") or {}).get("id"))
        if aid == target_aid:
            codes = set()
            for inst in auth.get("institutions", []):
                cc = inst.get("country_code")
                if cc and cc in a2g:
                    codes.add(a2g[cc])
            return list(codes)
    return []


def author_position(work, target_aid):
    for auth in work.get("authorships", []):
        aid = author_id_key((auth.get("author") or {}).get("id"))
        if aid == target_aid:
            return auth.get("author_position")
    return None


def is_last_author(work, target_aid):
    """Return True if the target author is the last author, treating a single
    authored paper as last author by default."""
    authorships = work.get("authorships", [])
    if len(authorships) == 1:
        aid = author_id_key(((authorships[0].get("author") or {})).get("id"))
        return aid == target_aid
    return author_position(work, target_aid) == "last"


def is_top10(work):
    cn = work.get("citation_normalized_percentile") or {}
    return bool(cn.get("is_in_top_10_percent"))


def classify_author(aid, works, a2g, origin_override=None):
    """Return a dict with career descriptors for one author.

    If ``origin_override`` is provided, it is used as the author's origin
    group instead of the automatic majority-vote over the first three career
    years. The override is applied before ``abroad`` is computed so that the
    derived mobility flag is consistent with the chosen origin.
    """
    # Find author display name
    display_name = None
    for w in works:
        for auth in w.get("authorships", []):
            if author_id_key((auth.get("author") or {}).get("id")) == aid:
                display_name = (auth.get("author") or {}).get("display_name")
                break
        if display_name:
            break

    # Sort works by year
    works = [w for w in works if w.get("publication_year")]
    works.sort(key=lambda w: (w["publication_year"], w.get("id", "")))
    if not works:
        return None

    years = [w["publication_year"] for w in works]
    career_start = min(years)
    career_end = max(years)
    n_works = len(works)

    if career_start < CAREER_START_MIN or career_start > CAREER_START_MAX:
        return None
    if n_works < MIN_WORKS:
        return None

    # Determine origin group from first 3 years (always collected so the
    # absence-of-affiliation filter still applies to overridden authors).
    origin_counter = Counter()
    first_year_by_group = {}
    for w in works:
        if w["publication_year"] <= career_start + 2:
            groups = work_groups_for_author(w, aid, a2g)
            for g in groups:
                origin_counter[g] += 1
                if g not in first_year_by_group:
                    first_year_by_group[g] = w["publication_year"]
    if not origin_counter:
        return None
    if origin_override is not None:
        origin = origin_override
    else:
        # Tie-break by earliest first appearance, then most frequent
        origin = max(
            origin_counter.keys(),
            key=lambda g: (origin_counter[g], -first_year_by_group[g]),
        )

    # Abroad within ABROAD_WINDOW years
    abroad = False
    abroad_year = None
    for w in works:
        y = w["publication_year"]
        if y > career_start + ABROAD_WINDOW:
            break
        groups = work_groups_for_author(w, aid, a2g)
        if any(g != origin for g in groups):
            abroad = True
            abroad_year = y
            break

    # Hit within HIT_WINDOW years (top 10% AI/ML citation percentile,
    # regardless of author position)
    hit = False
    hit_year = None
    for w in works:
        y = w["publication_year"]
        if y > career_start + HIT_WINDOW:
            break
        if is_top10(w):
            hit = True
            hit_year = y
            break

    # PI proxy: first last-author paper (single-authored papers count as last)
    pi_year = None
    for w in works:
        if is_last_author(w, aid):
            pi_year = w["publication_year"]
            break

    # Dropout: no AI/ML work in DROPOUT_LATEST_YEAR..2023
    active = any(w["publication_year"] >= 2020 for w in works)

    # Recent (last 3 years of data) main group for final state
    recent_counter = Counter()
    for w in works:
        if w["publication_year"] >= 2021:
            groups = work_groups_for_author(w, aid, a2g)
            for g in groups:
                recent_counter[g] += 1
    recent_group = recent_counter.most_common(1)[0][0] if recent_counter else None

    return {
        "author_id": aid,
        "display_name": display_name,
        "career_start": career_start,
        "career_end": career_end,
        "n_ai_works": n_works,
        "origin_group": origin,
        "abroad": abroad,
        "abroad_year": abroad_year,
        "hit": hit,
        "hit_year": hit_year,
        "pi_year": pi_year,
        "pi": pi_year is not None,
        "active": active,
        "recent_group": recent_group,
    }


def make_country_filter(codes):
    """Build an OR filter for OpenAlex authorships.institutions.country_code."""
    return "|".join(dict.fromkeys(codes))


def sample_works_for_group(client, group, codes, sample_per_group, seed_start):
    """Sample AI/ML works with at least one institution in the given country codes."""
    if not codes:
        return []
    base_filter = (
        f"publication_year:{CAREER_START_MIN}-2023,"
        f"topics.subfield.id:{SUBFIELD},"
        f"authorships.institutions.country_code:{make_country_filter(codes)}"
    )
    return client.sample_works(
        sample_per_group, base_filter,
        "id,publication_year,authorships",
        per_call=200, seed_start=seed_start,
    )


def build_cohort(sample_per_group, max_authors, client, a2g, group_to_a2):
    """Stratified work sampling by civilization, then author fetch/classify."""
    COHORT_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = COHORT_DIR / "raw_sampled_works.json"
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            sampled = json.load(f)
        print(f"Loaded {len(sampled)} sampled works from cache.")
    else:
        sampled = []
        seen = set()
        groups = list(group_to_a2.keys())
        seed_start = 1
        for g in groups:
            if g == "Other Civilizations":
                codes = top_residual_codes(group_to_a2, top_n=50)
            else:
                codes = group_country_codes(group_to_a2, g)
            print(f"Sampling {sample_per_group} works for {g} ({len(codes)} countries) ...")
            group_works = sample_works_for_group(client, g, codes, sample_per_group, seed_start)
            seed_start += 100  # avoid cache collisions and ensure variety
            for w in group_works:
                wid = w.get("id")
                if wid and wid not in seen:
                    seen.add(wid)
                    sampled.append(w)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(sampled, f, ensure_ascii=False)
        print(f"Sampled {len(sampled)} distinct works across {len(groups)} groups.")

    # Collect unique author ids, preserve order of first appearance
    author_order = []
    seen_authors = set()
    for w in sampled:
        for auth in w.get("authorships", []):
            aid = author_id_key((auth.get("author") or {}).get("id"))
            if aid and aid not in seen_authors:
                seen_authors.add(aid)
                author_order.append(aid)
    print(f"{len(author_order)} unique authors from sampled works.")

    if max_authors and len(author_order) > max_authors:
        import random
        rng = random.Random(42)
        author_order = rng.sample(author_order, max_authors)
        print(f"Capped to {len(author_order)} authors for pilot.")

    # Fetch works per author in batches of 50
    works_by_author = defaultdict(list)
    failed_batches = []
    batch_size = 50
    author_batches = [
        author_order[i:i + batch_size] for i in range(0, len(author_order), batch_size)
    ]
    for i, batch in enumerate(author_batches, 1):
        print(f"  Fetching batch {i}/{len(author_batches)} ({len(batch)} authors) ...")
        works = None
        last_err = None
        for attempt in range(3):
            try:
                works = client.fetch_works_by_authors(
                    batch, "id,publication_year,authorships,citation_normalized_percentile",
                    subfield_id=SUBFIELD,
                )
                break
            except OpenAlexBudgetExhausted:
                # Fail fast so an incomplete cohort is never written to disk.
                raise
            except Exception as e:
                last_err = e
                if attempt < 2:
                    wait = 2 ** attempt
                    print(f"    Batch {i} attempt {attempt + 1} failed: {e}. Retrying in {wait}s ...")
                    time.sleep(wait)
                    continue
        if works is None:
            failed_path = COHORT_DIR / "failed_batches.json"
            failed_batches.append({"batch": i, "authors": batch, "error": str(last_err)})
            with open(failed_path, "w", encoding="utf-8") as f:
                json.dump(failed_batches, f, ensure_ascii=False, indent=2)
            raise RuntimeError(
                f"Batch {i}/{len(author_batches)} failed after 3 attempts: {last_err}. "
                f"Failed batch logged to {failed_path}. Fix the API/network issue and rerun; "
                f"incomplete cohort would be written otherwise."
            )
        for w in works:
            for auth in w.get("authorships", []):
                aid = author_id_key((auth.get("author") or {}).get("id"))
                if aid in batch:
                    works_by_author[aid].append(w)

    # Classify, applying origin-group overrides before mobility flags are
    # computed so that ``abroad`` and other derived fields are consistent.
    overrides = load_origin_overrides()
    rows = []
    for aid in author_order:
        works = works_by_author.get(aid, [])
        row = classify_author(aid, works, a2g, origin_override=overrides.get(aid))
        if row:
            rows.append(row)
    cohort = pd.DataFrame(rows)
    if overrides:
        for author_id in overrides:
            if author_id in cohort["author_id"].values:
                print(f"Applied origin-group override: {author_id} -> {overrides[author_id]}")

    print(f"Cohort size after filtering: {len(cohort)}")
    return cohort


def estimate_rates(cohort, prior=1.0, rate_cap=2.0, min_cohort=10):
    """Compute smoothed constant-hazard transition rates per origin group.

    Laplace smoothing (prior=1) avoids 0/1 probabilities in small samples; the
    resulting per-year hazard is capped at `rate_cap` to keep the ODE numerics
    stable.  The raw sample proportions are also reported.
    """

    def smooth_prop(successes, n):
        if n == 0:
            return 0.0
        return (successes + prior) / (n + 2 * prior)

    def hazard(p, horizon):
        if p <= 0.0:
            return 0.0
        if p >= 1.0:
            return rate_cap
        return min(-math.log(1 - p) / horizon, rate_cap)

    rates = []
    for g, df in cohort.groupby("origin_group"):
        n = len(df)
        if n < min_cohort:
            continue

        p_abroad_raw = df["abroad"].mean()
        alpha = hazard(smooth_prop(df["abroad"].sum(), n), ABROAD_WINDOW)

        domestic = df[~df["abroad"]]
        abroad_df = df[df["abroad"]]

        p_hit_dom_raw = domestic["hit"].mean() if len(domestic) else 0.0
        p_hit_abr_raw = abroad_df["hit"].mean() if len(abroad_df) else 0.0
        h_D = hazard(smooth_prop(domestic["hit"].sum(), len(domestic)), HIT_WINDOW)
        h_A = hazard(smooth_prop(abroad_df["hit"].sum(), len(abroad_df)), HIT_WINDOW)

        returned = abroad_df[abroad_df["recent_group"] == g]
        p_return_raw = len(returned) / len(abroad_df) if len(abroad_df) else 0.0
        beta = hazard(smooth_prop(len(returned), len(abroad_df)), 10.0)

        hit_dom = domestic[domestic["hit"]]
        hit_abr = abroad_df[abroad_df["hit"]]
        p_pi_dom_raw = hit_dom["pi"].mean() if len(hit_dom) else 0.0
        p_pi_abr_raw = hit_abr["pi"].mean() if len(hit_abr) else 0.0
        p_D = hazard(smooth_prop(hit_dom["pi"].sum(), len(hit_dom)), 15.0)
        p_A = hazard(smooth_prop(hit_abr["pi"].sum(), len(hit_abr)), 15.0)

        p_dropout_raw = 1 - df["active"].mean()
        d = hazard(smooth_prop((~df["active"]).sum(), n), 18.0)

        rates.append({
            "group": g,
            "n": n,
            "p_abroad": p_abroad_raw,
            "alpha": alpha,
            "p_return": p_return_raw,
            "beta": beta,
            "p_hit_domestic": p_hit_dom_raw,
            "p_hit_abroad": p_hit_abr_raw,
            "h_D": h_D,
            "h_A": h_A,
            "p_pi_domestic": p_pi_dom_raw,
            "p_pi_abroad": p_pi_abr_raw,
            "p_D": p_D,
            "p_A": p_A,
            "p_dropout": p_dropout_raw,
            "d": d,
        })
    return pd.DataFrame(rates)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-per-group", type=int, default=200,
                        help="Number of works to sample per civilization group.")
    parser.add_argument("--max-authors", type=int, default=0,
                        help="Cap on unique authors to fetch works for (0 = no cap).")
    parser.add_argument("--subfield-id", type=str, default="subfields/1702",
                        help="OpenAlex subfield ID to build the cohort for.")
    parser.add_argument("--output-dir", type=str, default=str(COHORT_DIR),
                        help="Directory to write cohort.csv, transition_rates.csv and raw_sampled_works.json.")
    parser.add_argument("--min-works", type=int, default=2,
                        help="Minimum number of works in the target subfield for an author to be included.")
    parser.add_argument("--cache-dir", type=str, default=str(CACHE_DIR))
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--force-resample", action="store_true",
                        help="Delete cached sampled works and fetch a new sample from OpenAlex.")
    parser.add_argument("--delay", type=float, default=0.2,
                        help="Seconds to sleep between OpenAlex API calls (default 0.2).")
    args = parser.parse_args()

    globals()["SUBFIELD"] = args.subfield_id
    globals()["COHORT_DIR"] = Path(args.output_dir)
    globals()["MIN_WORKS"] = args.min_works

    client = OpenAlexClient(
        cache_dir=None if args.no_cache else args.cache_dir,
        delay=args.delay,
    )
    a2g, group_to_a2 = load_group_mapping()
    print("Loaded group mapping for", len(a2g), "alpha-2 codes covering", len(group_to_a2), "groups.")

    if args.force_resample:
        (COHORT_DIR / "raw_sampled_works.json").unlink(missing_ok=True)

    cohort = build_cohort(args.sample_per_group, args.max_authors, client, a2g, group_to_a2)
    cohort_path = COHORT_DIR / "cohort.csv"
    cohort.to_csv(cohort_path, index=False, encoding="utf-8-sig")
    print(f"Cohort saved to {cohort_path}")

    rates = estimate_rates(cohort)
    rates_path = COHORT_DIR / "transition_rates.csv"
    rates.to_csv(rates_path, index=False, encoding="utf-8-sig")
    print(f"Transition rates saved to {rates_path}")
    print(rates.to_string(index=False))


if __name__ == "__main__":
    main()
