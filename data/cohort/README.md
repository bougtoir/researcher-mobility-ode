# Cohort data provenance

The files in this directory are derived from the OpenAlex snapshot (subfield `1702`, Artificial Intelligence, career-start years 2000–2023, extracted on 2026-08-09) using `src/cohort_extraction.py`.

- `raw_sampled_works.json` – a stratified random sample of works used to seed the author cohort.
- `cohort.csv` – author-level cohort (career dates, civilisation grouping, `origin_group`, and state flags used for rate estimation).
- `transition_rates.csv` – transition-rate point estimates computed from `cohort.csv`.

## Manual correction in `cohort.csv`

One author (row 239, `Ignazio Stanganelli`, OpenAlex `A5061353810`) was assigned to `United States` by the automatic `classify_author` majority-vote rule. Inspection of the sampled works and the country-to-civilisation mapping showed that the author's earliest affiliation was in Italy (`IT`), which maps to `Continental Europe`. The `origin_group` cell was therefore corrected to `Continental Europe`.

The correction is also stored in `author_origin_overrides.csv` and applied automatically by `src/cohort_extraction.py`, so the same corrected cohort is produced when the extraction script is re-run.
