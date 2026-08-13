"""Reconstruct year-by-year compartment membership from the published cohort.

The cohort.csv file records transition-year milestones (career_start,
abroad_year, hit_year, pi_year) and the author's most recent civilisation group
(recent_group). Because the public raw_sampled_works.json contains only a few
sampled works per author, we use a deterministic set of rules:

- Authors are present from career_start to 2023 if active=True, otherwise to
  their last observed publication year.
- Stage follows hit/PI years: early (E), high-impact (H), PI (P).
- Domestic/abroad location is inferred from:
  1. Any sampled work in that year (origin group present -> domestic, only
     non-origin groups -> abroad).
  2. The first abroad year and the final observed group (recent_group) for
     years without a sampled work.
  3. For authors whose recent_group is the origin civilisation but who have an
     abroad flag, we search the sampled works for the first domestic work after
     abroad_year and use that as the return year. If no such work is sampled,
     we fall back to the start of the recent window (2021) for active authors or
     to career_end for inactive authors.

This reconstruction is best-effort and is intended for estimating annual rates
and for comparing projections to observed counts, not as a complete census.
"""

import json
from collections import defaultdict
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
COHORT_DIR = DATA_DIR / "cohort"

COMPARTMENTS = ["D", "A", "H_D", "H_A", "P_D", "P_A"]


def _parse_bool(value):
    return str(value).strip().lower() in ("true", "1", "yes")


def load_group_mapping():
    with open(DATA_DIR / "country_civilization_mapping.json", "r", encoding="utf-8") as f:
        mapping = json.load(f)
    a2g = {}
    for info in mapping.values():
        a2 = info.get("alpha_2")
        g = info.get("group")
        if a2 and g:
            a2g[a2] = g
    return a2g


def _author_id_key(raw_id):
    if not raw_id:
        return None
    return raw_id.split("/")[-1]


def _work_groups(work, target_aid, a2g):
    for auth in work.get("authorships", []):
        aid = _author_id_key((auth.get("author") or {}).get("id"))
        if aid == target_aid:
            groups = set()
            for inst in auth.get("institutions", []):
                cc = inst.get("country_code")
                if cc and cc in a2g:
                    groups.add(a2g[cc])
            return groups
    return set()


def _load_author_works(cohort_author_ids):
    a2g = load_group_mapping()
    author_works = defaultdict(list)
    with open(COHORT_DIR / "raw_sampled_works.json", "r", encoding="utf-8") as f:
        works = json.load(f)
    for w in works:
        for auth in w.get("authorships", []):
            aid = _author_id_key((auth.get("author") or {}).get("id"))
            if aid and aid in cohort_author_ids:
                author_works[aid].append(w)
    return author_works, a2g


def reconstruct_annual_states():
    """Return a DataFrame with columns author_id, origin_group, year, compartment."""
    cohort = pd.read_csv(COHORT_DIR / "cohort.csv", dtype=str)
    numeric_cols = ["career_start", "career_end", "abroad_year", "hit_year", "pi_year"]
    for col in numeric_cols:
        cohort[col] = pd.to_numeric(cohort[col], errors="coerce")
    cohort["active"] = cohort["active"].apply(_parse_bool)

    author_ids = set(cohort["author_id"].astype(str).tolist())
    author_works, a2g = _load_author_works(author_ids)

    rows = []
    for _, row in cohort.iterrows():
        origin = row["origin_group"]
        if pd.isna(origin):
            continue
        start = row["career_start"]
        end = row["career_end"]
        if pd.isna(start) or pd.isna(end):
            continue
        start = int(start)
        end = int(min(end, 2023))
        active = row["active"]
        final_year = 2023 if active else end

        aid = str(row["author_id"])
        works = author_works.get(aid, [])
        works_by_year = {}
        for w in works:
            y = w.get("publication_year")
            if y is None:
                continue
            groups = _work_groups(w, aid, a2g)
            if groups:
                works_by_year[int(y)] = groups

        abroad = _parse_bool(row["abroad"])
        abroad_year = int(row["abroad_year"]) if abroad and pd.notna(row["abroad_year"]) else None
        recent = row["recent_group"]
        final_abroad = False if pd.isna(recent) else (recent.strip() != origin.strip())

        return_year = None
        if abroad and not final_abroad and abroad_year is not None:
            candidates = [y for y, groups in works_by_year.items() if y > abroad_year and origin in groups]
            if candidates:
                return_year = min(candidates)
            else:
                # Fallback: active authors are assumed to have returned by the recent window
                fallback = 2021 if active else end
                return_year = max(abroad_year + 1, fallback)
                return_year = min(return_year, final_year)

        hit_year = int(row["hit_year"]) if pd.notna(row["hit_year"]) else None
        pi_year = int(row["pi_year"]) if pd.notna(row["pi_year"]) else None

        for y in range(start, final_year + 1):
            # Cohort-inferred location from abroad flag / abroad_year / return_year / recent_group
            if not abroad or abroad_year is None or y < abroad_year:
                cohort_loc = "domestic"
            elif final_abroad:
                cohort_loc = "abroad"
            else:
                if return_year is not None and y >= return_year:
                    cohort_loc = "domestic"
                else:
                    cohort_loc = "abroad"

            # Prefer sampled-work location when available; otherwise use cohort-derived location
            if y in works_by_year:
                if origin in works_by_year[y]:
                    loc = "domestic"
                else:
                    loc = "abroad"
            else:
                loc = cohort_loc

            if pi_year is not None and y >= pi_year:
                stage = "P"
            elif hit_year is not None and y >= hit_year:
                stage = "H"
            else:
                stage = "E"

            key = f"{stage}_{loc}"
            comp = {"E_domestic": "D", "E_abroad": "A",
                    "H_domestic": "H_D", "H_abroad": "H_A",
                    "P_domestic": "P_D", "P_abroad": "P_A"}.get(key)
            if comp:
                rows.append({
                    "author_id": aid,
                    "origin_group": origin,
                    "year": y,
                    "compartment": comp,
                })

    return pd.DataFrame(rows)


def annual_stock_table():
    """Return a year x (origin_group, compartment) count table."""
    states = reconstruct_annual_states()
    table = states.groupby(["year", "origin_group", "compartment"]).size().reset_index(name="count")
    return table


if __name__ == "__main__":
    df = annual_stock_table()
    print(df.head())
    print("Years:", df["year"].min(), df["year"].max())
    print("Total author-years:", len(df))
