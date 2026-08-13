#!/usr/bin/env python3
"""
Build the full AI/ML researcher cohort from OpenAlex using the list API.

This is an alternative to the sampled cohort in cohort_extraction.py. It streams
all works in the target subfield and year range through the OpenAlex cursor
paginator, writes them to a local SQLite database, and then classifies every
author who appears in at least one work with a mappable country affiliation.

The fetch stage is parallelised by publication year to make full-population
extraction practical (the OpenAlex API allows ~30 concurrent requests per key).

Usage:
    python src/extract_full_cohort.py
    FULL=1 bash reproduce.sh   # after the cohort.csv has been written
"""

import argparse
import json
import math
import os
import random
import sqlite3
import sys
import threading
import time
from collections import defaultdict
from pathlib import Path
from queue import Queue

import pandas as pd

# Make cohort_extraction helpers importable
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cohort_extraction import (
    ABROAD_WINDOW,
    CAREER_START_MAX,
    CAREER_START_MIN,
    DROPOUT_LATEST_YEAR,
    HIT_WINDOW,
    MIN_WORKS,
    classify_author,
    estimate_rates,
    load_group_mapping,
    load_origin_overrides,
)
from openalex_client import OpenAlexBudgetExhausted, OpenAlexClient

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
COHORT_DIR = DATA_DIR / "cohort"


def setup_db(db_path):
    """Create the works and author_works tables."""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-2000000")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS works (
            id TEXT PRIMARY KEY,
            year INTEGER,
            data TEXT
        ) WITHOUT ROWID
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS author_works (
            author_id TEXT,
            work_id TEXT,
            PRIMARY KEY (author_id, work_id)
        ) WITHOUT ROWID
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_aw_author ON author_works(author_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_w_year ON works(year)")
    return conn


def reduce_work(w):
    """Keep only the fields needed by classify_author."""
    reduced = {
        "id": w.get("id"),
        "publication_year": w.get("publication_year"),
        "authorships": [],
        "citation_normalized_percentile": w.get("citation_normalized_percentile"),
    }
    for auth in w.get("authorships", []):
        author = auth.get("author") or {}
        reduced_auth = {
            "author": {
                "id": author.get("id"),
                "display_name": author.get("display_name"),
            },
            "author_position": auth.get("author_position"),
            "institutions": [
                {"country_code": inst.get("country_code")}
                for inst in auth.get("institutions", [])
            ],
        }
        reduced["authorships"].append(reduced_auth)
    return reduced


def author_id_key(raw_id):
    if not raw_id:
        return None
    return raw_id.split("/")[-1]


def has_mappable_country(w, a2g):
    """Return True if at least one authorship institution has a known country."""
    for auth in w.get("authorships", []):
        for inst in auth.get("institutions", []):
            if inst.get("country_code") in a2g:
                return True
    return False


def work_groups(w, a2g):
    """Return the set of civilisation groups present on a work."""
    groups = set()
    for auth in w.get("authorships", []):
        for inst in auth.get("institutions", []):
            cc = inst.get("country_code")
            if cc and cc in a2g:
                groups.add(a2g[cc])
    return groups


class GroupReservoir:
    """Reservoir sample up to n_per_group works for each civilisation group."""
    def __init__(self, n_per_group, seed=0):
        self.n = n_per_group
        self.counts = defaultdict(int)
        self.samples = defaultdict(list)
        self.rng = random.Random(seed)

    def add(self, work, groups):
        for g in groups:
            self.counts[g] += 1
            samples = self.samples[g]
            if len(samples) < self.n:
                samples.append(work)
            else:
                j = self.rng.randint(0, self.counts[g] - 1)
                if j < self.n:
                    samples[j] = work

    def unique_works(self):
        by_id = {}
        for samples in self.samples.values():
            for w in samples:
                by_id[w["id"]] = w
        return list(by_id.values())


def load_state(state_path):
    """Load the saved per-partition state or start fresh."""
    if state_path.exists():
        with open(state_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state_path, state):
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f)


def _flush(conn, batch_works, batch_authors):
    """Insert pending rows and commit."""
    if batch_works:
        conn.executemany(
            "INSERT OR IGNORE INTO works (id, year, data) VALUES (?, ?, ?)",
            batch_works,
        )
    if batch_authors:
        conn.executemany(
            "INSERT OR IGNORE INTO author_works (author_id, work_id) VALUES (?, ?)",
            batch_authors,
        )
    conn.commit()


def _partition_filter(subfield_id, start_year, end_year):
    """Build filter strings for the whole range and for each year."""
    whole = f"publication_year:{start_year}-{end_year},topics.subfield.id:{subfield_id}"
    per_year = {str(y): f"publication_year:{y},topics.subfield.id:{subfield_id}" for y in range(start_year, end_year + 1)}
    return whole, per_year


def _make_partitions(state, subfield_id, start_year, end_year, workers):
    """Create or resume partitions from the saved state."""
    whole_filter, per_year = _partition_filter(subfield_id, start_year, end_year)
    partitions = {}
    if workers == 1:
        partitions["all"] = {
            "filter": whole_filter,
            "cursor": "*",
            "pages": 0,
            "works": 0,
            "author_rows": 0,
        }
    else:
        for y, f in per_year.items():
            partitions[y] = {
                "filter": f,
                "cursor": "*",
                "pages": 0,
                "works": 0,
                "author_rows": 0,
            }

    # Merge any saved per-partition state for resumption.
    saved = state.get("partitions", {})
    if saved:
        for pid, p in saved.items():
            if pid in partitions:
                partitions[pid].update(p)
    elif state.get("cursor"):
        # Legacy single-cursor state: migrate to one partition.
        for p in partitions.values():
            p["cursor"] = state.get("cursor", "*")
            p["pages"] = state.get("pages", 0)
            p["works"] = state.get("works", 0)
            p["author_rows"] = state.get("author_rows", 0)
            break

    return partitions


def _process_page(w, a2g):
    """Return (works_row, author_rows, reduced_work, groups) or None."""
    if not has_mappable_country(w, a2g):
        return None
    reduced = reduce_work(w)
    wid = reduced["id"]
    year = reduced["publication_year"]
    works_row = (wid, year, json.dumps(reduced, ensure_ascii=False))
    author_rows = []
    seen = set()
    for auth in w.get("authorships", []):
        aid = author_id_key((auth.get("author") or {}).get("id"))
        if aid and aid not in seen:
            seen.add(aid)
            author_rows.append((aid, wid))
    groups = work_groups(reduced, a2g)
    return works_row, author_rows, reduced, groups


def _fetch_partition(partition, q, stop_event, api_key, mailto, per_page, max_pages_per_partition, a2g):
    """Fetch all pages for a single partition and push results to the writer queue."""
    client = OpenAlexClient(delay=0.0, cache_dir=None, api_key=api_key, mailto=mailto)
    base_params = {
        "filter": partition["filter"],
        "select": "id,publication_year,authorships,citation_normalized_percentile",
        "per-page": per_page,
    }
    cursor = partition["cursor"]
    if cursor == "DONE":
        q.put((partition["id"], None, None, None, None, None, None, None, None))
        return

    pages_done = partition["pages"]
    works_done = partition["works"]
    author_rows_done = partition["author_rows"]

    try:
        while not stop_event.is_set():
            if max_pages_per_partition and pages_done >= max_pages_per_partition:
                break
            page = client.get("works", {**base_params, "cursor": cursor})
            results = page.get("results", [])
            works_batch = []
            authors_batch = []
            reduced_batch = []
            groups_batch = []
            for w in results:
                out = _process_page(w, a2g)
                if out is None:
                    continue
                works_row, authors, reduced, groups = out
                works_batch.append(works_row)
                authors_batch.extend(authors)
                reduced_batch.append(reduced)
                groups_batch.append(groups)
                works_done += 1
                author_rows_done += len(authors)

            pages_done += 1
            next_cursor = page.get("meta", {}).get("next_cursor")
            q.put((
                partition["id"], works_batch, authors_batch, reduced_batch, groups_batch,
                next_cursor, pages_done, works_done, author_rows_done,
            ))
            if not next_cursor:
                break
            cursor = next_cursor
    except OpenAlexBudgetExhausted as e:
        q.put((partition["id"], "ERROR", str(e), None, None, None, None, None, None))
        stop_event.set()
        return
    except Exception as e:
        q.put((partition["id"], "ERROR", f"Partition {partition['id']}: {e}", None, None, None, None, None, None))
        stop_event.set()
        return

    q.put((partition["id"], None, None, None, None, None, None, None, None))


def _writer(q, conn, state, state_path, pages_per_commit, n_partitions, a2g, sample_per_group):
    """Consume the queue and persist works/author rows to the SQLite DB."""
    reservoir = GroupReservoir(sample_per_group)
    batch_works = []
    batch_authors = []
    pages_since_commit = 0
    sentinels = 0
    start_time = time.time()
    partitions = state.setdefault("partitions", {})
    partitions_done = set()

    while sentinels < n_partitions:
        item = q.get()
        pid = item[0]
        # Sentinel: (pid, None, None, ...)
        if item[1] is None:
            sentinels += 1
            partitions_done.add(pid)
            continue
        # Error signal
        if item[1] == "ERROR":
            _flush(conn, batch_works, batch_authors)
            save_state(state_path, state)
            raise OpenAlexBudgetExhausted(item[2])

        _, works_batch, authors_batch, reduced_batch, groups_batch, next_cursor, pages_done, works_done, author_rows_done = item
        batch_works.extend(works_batch)
        batch_authors.extend(authors_batch)
        for reduced, groups in zip(reduced_batch, groups_batch):
            reservoir.add(reduced, groups)

        partition = partitions.setdefault(pid, {})
        partition.update({
            "cursor": next_cursor or "DONE",
            "pages": pages_done,
            "works": works_done,
            "author_rows": author_rows_done,
        })
        pages_since_commit += 1

        if pages_since_commit >= pages_per_commit:
            _flush(conn, batch_works, batch_authors)
            save_state(state_path, state)
            batch_works.clear()
            batch_authors.clear()
            pages_since_commit = 0
            total_pages = sum(p.get("pages", 0) for p in partitions.values())
            total_works = sum(p.get("works", 0) for p in partitions.values())
            total_authors = sum(p.get("author_rows", 0) for p in partitions.values())
            elapsed = time.time() - start_time
            rate = total_pages / elapsed if elapsed else 0
            print(
                f"  pages={total_pages}, works={total_works}, "
                f"author_rows={total_authors}, elapsed={elapsed:.1f}s, "
                f"rate={rate:.2f} pg/s, done={len(partitions_done)}/{n_partitions}"
            )

    if batch_works or batch_authors:
        _flush(conn, batch_works, batch_authors)
        save_state(state_path, state)

    sampled = reservoir.unique_works()
    sampled_path = Path(str(state_path) + ".sampled.json")
    with open(sampled_path, "w", encoding="utf-8") as f:
        json.dump(sampled, f, ensure_ascii=False)
    return sampled


def fetch_and_store(client, conn, a2g, state, state_path, subfield_id, start_year,
                    end_year, per_page, pages_per_commit, max_pages, delay,
                    sample_per_group=500, workers=1):
    """Stream all works through the OpenAlex API and store in SQLite.

    Uses multiple fetcher threads partitioned by publication year to keep the
    OpenAlex connection pool saturated while a single writer thread persists
    rows to the database.
    """
    partitions = _make_partitions(state, subfield_id, start_year, end_year, workers)
    for pid, p in partitions.items():
        p["id"] = pid

    if all(p.get("cursor") == "DONE" for p in partitions.values()):
        print("API fetch already marked complete; skipping fetch.")
        return (
            sum(p.get("pages", 0) for p in partitions.values()),
            sum(p.get("works", 0) for p in partitions.values()),
            sum(p.get("author_rows", 0) for p in partitions.values()),
            [],
        )

    state["partitions"] = {pid: {k: v for k, v in p.items() if k != "id"} for pid, p in partitions.items()}
    save_state(state_path, state)

    q = Queue(maxsize=max(4, workers * 2))
    stop_event = threading.Event()

    # Use the existing client to source credentials; each worker gets its own.
    api_key = getattr(client, "api_key", None)
    mailto = getattr(client, "mailto", None)

    writer = threading.Thread(
        target=_writer,
        args=(q, conn, state, state_path, pages_per_commit, len(partitions), a2g, sample_per_group),
    )
    writer.start()

    max_per_partition = 0
    if max_pages:
        max_per_partition = max(1, max_pages // len(partitions))

    threads = []
    for pid, p in partitions.items():
        if p.get("cursor") == "DONE":
            q.put((pid, None, None, None, None, None, None, None, None))
            continue
        t = threading.Thread(
            target=_fetch_partition,
            args=(p, q, stop_event, api_key, mailto, per_page, max_per_partition, a2g),
        )
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    writer.join()

    # Reload partitions from state after writer finishes.
    partitions = state.get("partitions", {})
    total_pages = sum(p.get("pages", 0) for p in partitions.values())
    total_works = sum(p.get("works", 0) for p in partitions.values())
    total_authors = sum(p.get("author_rows", 0) for p in partitions.values())
    reservoir = GroupReservoir(sample_per_group)
    # The writer already saved the reservoir in a separate file? No; we return it.
    # We need the reservoir from writer thread. Since threads can't return, we
    # rebuild from the DB works sample? Instead, writer can save to a temp file.
    # Simpler: the writer saves the sampled works to state_path + '.sampled.json'
    # and we load it here.
    sampled_path = Path(str(state_path) + ".sampled.json")
    if sampled_path.exists():
        with open(sampled_path, "r", encoding="utf-8") as f:
            sampled = json.load(f)
    else:
        sampled = []

    print(
        f"Fetch complete: {total_pages} pages, {total_works} works, "
        f"{total_authors} author_works rows, {len(sampled)} sampled works."
    )
    return total_pages, total_works, total_authors, sampled


def classify_all_authors(conn, a2g, min_works, overrides, batch_size=500):
    """Classify every author with at least min_works AI/ML works."""
    # Update module-level constants that classify_author reads at call time.
    import cohort_extraction as ce
    ce.MIN_WORKS = min_works

    cur = conn.cursor()
    cur.execute(
        "SELECT author_id, COUNT(*) as c FROM author_works GROUP BY author_id HAVING c >= ?",
        (min_works,),
    )
    author_ids = [row[0] for row in cur.fetchall()]
    print(f"Classifying {len(author_ids)} authors with at least {min_works} works ...")

    rows = []
    total = len(author_ids)
    start = time.time()
    for i in range(0, total, batch_size):
        batch = author_ids[i:i + batch_size]
        placeholders = ",".join(["?"] * len(batch))
        cur.execute(
            f"""SELECT aw.author_id, w.year, w.data
                FROM author_works aw
                JOIN works w ON aw.work_id = w.id
                WHERE aw.author_id IN ({placeholders})
                ORDER BY aw.author_id, w.year, w.id""",
            batch,
        )
        works_by_author = defaultdict(list)
        for aid, year, data in cur:
            w = json.loads(data)
            w["publication_year"] = year
            works_by_author[aid].append(w)

        for aid in batch:
            works = works_by_author.get(aid, [])
            row = classify_author(aid, works, a2g, origin_override=overrides.get(aid))
            if row:
                rows.append(row)

        if (i // batch_size + 1) % 10 == 0 or i + batch_size >= total:
            elapsed = time.time() - start
            pct = (i + len(batch)) / total * 100
            print(f"  classified {i + len(batch)}/{total} ({pct:.1f}%) "
                  f"-> {len(rows)} cohort rows, elapsed={elapsed:.1f}s")

    print(f"Classification complete: {len(rows)} cohort rows from {total} candidate authors.")
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--subfield-id", default="subfields/1702")
    parser.add_argument("--start-year", type=int, default=2000)
    parser.add_argument("--end-year", type=int, default=2023)
    parser.add_argument("--min-works", type=int, default=2)
    parser.add_argument("--output-dir", default=str(COHORT_DIR))
    parser.add_argument("--db-path", default=str(CACHE_DIR / "full_cohort.db"))
    parser.add_argument("--state-path", default=str(CACHE_DIR / "full_cohort_state.json"))
    parser.add_argument("--per-page", type=int, default=200)
    parser.add_argument("--delay", type=float, default=0.0)
    parser.add_argument("--pages-per-commit", type=int, default=10)
    parser.add_argument("--workers", type=int, default=24,
                        help="Number of parallel fetcher threads (one per year by default).")
    parser.add_argument("--max-pages", type=int, default=0,
                        help="Stop after this many pages (for testing).")
    parser.add_argument("--sample-per-group", type=int, default=500,
                        help="Number of works to keep per group in raw_sampled_works.json.")
    parser.add_argument("--classify-batch-size", type=int, default=500)
    parser.add_argument("--resume", action="store_true",
                        help="Resume from the state stored in --state-path.")
    parser.add_argument("--no-fetch", action="store_true",
                        help="Skip the API fetch and only classify from the existing DB.")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    db_path = Path(args.db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    state_path = Path(args.state_path)

    a2g, _ = load_group_mapping()
    overrides = load_origin_overrides()
    target_codes = set(a2g.keys())
    print(f"Loaded mapping for {len(target_codes)} country codes.")

    conn = setup_db(db_path)

    state = load_state(state_path)
    sampled_works = []
    if not args.no_fetch:
        client = OpenAlexClient(delay=args.delay, cache_dir=None)
        try:
            pages, works, rows, sampled_works = fetch_and_store(
                client, conn, a2g, state, state_path,
                args.subfield_id, args.start_year, args.end_year,
                args.per_page, args.pages_per_commit, args.max_pages, args.delay,
                sample_per_group=args.sample_per_group,
                workers=args.workers,
            )
        except OpenAlexBudgetExhausted as e:
            print(f"ERROR: {e}")
            print("Add credits or wait for the daily reset and rerun with --resume.")
            sys.exit(1)
    else:
        print("Skipping API fetch, classifying from existing DB.")

    if sampled_works:
        sample_path = output_dir / "raw_sampled_works.json"
        with open(sample_path, "w", encoding="utf-8") as f:
            json.dump(sampled_works, f, ensure_ascii=False)
        print(f"Sampled works saved to {sample_path} ({len(sampled_works)} works)")

    cohort = classify_all_authors(
        conn, a2g, args.min_works, overrides, batch_size=args.classify_batch_size
    )
    cohort_path = output_dir / "cohort.csv"
    cohort.to_csv(cohort_path, index=False, encoding="utf-8-sig")
    print(f"Cohort saved to {cohort_path} ({len(cohort)} rows)")

    rates = estimate_rates(cohort)
    rates_path = output_dir / "transition_rates.csv"
    rates.to_csv(rates_path, index=False, encoding="utf-8-sig")
    print(f"Transition rates saved to {rates_path}")
    print(rates.to_string(index=False))

    conn.close()


if __name__ == "__main__":
    main()
