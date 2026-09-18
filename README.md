# AI/ML researcher mobility ODE pilot

This repository builds a reproducible OpenAlex pipeline for an AI/ML (Computer Science subfield `1702`) researcher-cohort, estimates transition rates per research macro-region, and runs a coupled ODE model to identify intervention priorities and point-of-no-return thresholds.

## One-command reproduce

```bash
bash reproduce.sh
```

This installs dependencies from `requirements.txt` (Python 3.10+, `pandas`, `numpy`, `scipy`, `requests`, `matplotlib`, `python-docx`, `python-pptx`, `Pillow`) and regenerates all `results/`, figures, and manuscript documents.

### Data redistribution

The author-level cohort files derived from OpenAlex records (`data/cohort/cohort.csv`, `data/cohort/raw_sampled_works.json`, `data/cohort/pi_proxy/cohort.csv`, `data/cohort/pi_proxy/raw_sampled_works.json` and the SQLite cache under `data/cache/`) are **not redistributed** in this repository. `reproduce.sh` detects that they are missing and re-extracts them from the OpenAlex API (subfield 1702, publication years 2000-2023) with `src/cohort_extraction.py` (stratified sample, minutes) and `src/extract_full_cohort.py` (full population, about 30 minutes; set `OPENALEX_API_KEY` for the polite pool) before running the models. The country-to-macro-region mapping, the estimated transition rates (`data/cohort/transition_rates.csv`, `data/cohort/pi_proxy/transition_rates.csv`), all aggregate result tables in `results/` and the manuscript documents are included. OpenAlex is updated continuously, so a fresh extraction reproduces the published rates, rankings and figures up to small snapshot differences (the manuscript reports the extraction dates of the snapshots it uses).

Running `python src/openalex_client.py` before `reproduce.sh` warms the on-disk cache in `data/cache/`.

`FULL=1 bash reproduce.sh` (or `python src/extract_full_cohort.py`) re-extracts the complete 2000-2023 AI/ML author population from OpenAlex (about 2.9 million works; requires `OPENALEX_API_KEY`). Every extracted work and every authorship (author position, `is_corresponding`, country codes, year) is persisted in a SQLite database under `data/cache/` (tables `works`, `author_works`, `authorships`) so that PI definitions and other classifications can be changed later without re-downloading; the extraction is resumable via a state file that records the extraction schema version, and a cache written by an older schema (without `is_corresponding`/`authorships`) is refused with an explicit error rather than silently reused. `--pi-definition {first_last,corresponding,recurrent_last}` selects the PI proxy used for `pi`/`pi_year` and the transition rates; all three candidate PI years are written to the cohort file regardless. `python src/pi_proxy_robustness.py` compares the three definitions (results/pi_proxy/); `python src/m_sensitivity.py` varies the minimum viable scale M (results/m_sensitivity/).

### Reusing the code for another field

The PI and hit proxies are calibrated to AI/ML authorship conventions: a PI is identified by last-author (or corresponding-author) position and a hit is a paper in the top 10% of the citation-normalised percentile within the AI/ML subfield. In fields with alphabetical author order (mathematics, economics, high-energy physics), first-author-PI conventions or consortium authorship, these proxies are not valid as written. Before applying the pipeline to another OpenAlex subfield, edit `is_last_author`, `pi_years_by_definition` and `is_top10` in `src/cohort_extraction.py` to the field's convention, change `--subfield-id`, and re-check `MIN_WORKS`, `ABROAD_WINDOW` and `HIT_WINDOW` against the field's career timing; the SQLite `authorships` table retains author position and corresponding flags so that alternative definitions can be evaluated without re-extraction.

## Main outputs

- `data/cohort/cohort.csv` — classified cohort with transition-year milestones (regenerated locally from OpenAlex; not redistributed, see above)
- `data/cohort/transition_rates.csv` — per-macro-region transition rates
- `data/country_civilization_mapping.json` — country to macro-region mapping
- `data/ne_110m_countries_slim.geojson` — Natural Earth 1:110m country outlines (public domain), used for Figure 1
- `results/endogenous/equilibrium_summary.csv` — endogenous-inflow equilibrium `T` vs `M`
- `results/endogenous/sensitivity.csv` — elasticities of `T` and `P` to each rate
- `results/endogenous/point_of_no_return.csv` — critical multipliers at which `T` reaches `M`
- `results/annual/` — year-by-year transition rates and 2017-2026 projection (exploratory extension, Supplementary Material S2)
- `results/pi_proxy/` — PI-proxy robustness (first last-author vs corresponding vs recurrent last-author; Supplementary Material S3)
- `results/m_sensitivity/` — sensitivity of T/M, rankings and PNR levers to the level of M (Supplementary Material S4)
- `docs/manuscript_full_article.docx` — Technology in Society manuscript (inline figures/tables, native Word equations); `_blinded.docx` is the double-anonymised version
- `docs/supplementary_material.docx`, `docs/highlights.docx`, `docs/cover_letter_technology_in_society.docx`
- `docs/manuscript_full_article_figures.pptx` — editable English figure/table slides
- `docs/figures/` — individual PNG files for each inline figure; `docs/figures/submission/` — numbered PNG and TIFF copies (Figure_01 ... Figure_10 and Supplementary_Figure_S1 ... S3)
- `docs/manuscript_full_article_submission.zip` — complete submission package

`python src/dominant_strategy.py` runs the coupled nine-region talent-concentration scenario (results/dominant_strategy/, Figures 9–10, Table 8); its pull intensity φ and variety elasticity γ are stylised, listed in `results/dominant_strategy/scenario_assumptions.csv`. Model time is reported in units of the characteristic time τ = 1/mean(d) (mean career duration at the fitted dropout rates; `tau_years` in summary.csv and scenario_assumptions.csv); the `year` column and the upper axes of the figures give the calendar-year equivalent at the fitted rates only as an annotation, not as a forecast.

Run `python scripts/check_manuscript.py docs/manuscript_full_article.docx` to verify figure/table/citation ordering and character set.

## Key model assumptions

- Six compartments per macro-region: `D`, `A`, `H_D`, `H_A`, `P_D`, `P_A`; `L` is absorbing dropout.
- Minimum viable coauthor threshold: `M = k × c_bar`.
- Endogenous PI-driven inflow: `I(P_D) = I0 + r · P_D` with `r` capped at a safety factor of 0.50 relative to `r_critical` (the most constrained fitted group realises about 0.40) to keep the linear system stable.
- Annual model: discrete one-year transition matrices with Laplace smoothing and correction pressures (probability clipping, dropout cap, inflow apportionment).

## Sources

- OpenAlex API: <https://api.openalex.org>
- Subfield: `subfields/1702` (Artificial Intelligence) under `fields/17` (Computer Science)
- Macro-region grouping rationale: `docs/mapping_rationale.md`
- Natural Earth 1:110m Admin 0 countries (public domain): <https://www.naturalearthdata.com>
