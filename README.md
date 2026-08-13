# AI/ML researcher mobility ODE pilot

This repository builds a reproducible OpenAlex pipeline for an AI/ML (Computer Science subfield `1702`) researcher-cohort, estimates per-civilisation transition rates, and runs a coupled ODE model to identify intervention priorities and point-of-no-return thresholds.

## One-command reproduce

```bash
bash reproduce.sh
```

This installs dependencies from `requirements.txt` (Python 3.10+, `pandas`, `numpy`, `scipy`, `requests`, `matplotlib`, `python-docx`, `python-pptx`) and regenerates all `results/`, figures, and manuscript documents from the included `data/cohort/` files.

The pipeline uses the pre-extracted cohort and sampled works in `data/cohort/` (OpenAlex snapshot extracted on 2026-08-09, subfield 1702) so it can be reproduced without OpenAlex API access. To re-extract the underlying works, run `python src/openalex_client.py` before `reproduce.sh`; this uses the on-disk cache in `data/cache/`.

## Main outputs

- `data/cohort/cohort.csv` — classified cohort with transition-year milestones
- `data/cohort/transition_rates.csv` — per-civilisation transition rates
- `results/endogenous/equilibrium_summary.csv` — endogenous-inflow equilibrium `T` vs `M`
- `results/endogenous/sensitivity.csv` — elasticities of `T` and `P` to each rate
- `results/endogenous/point_of_no_return.csv` — critical multipliers at which `T` reaches `M`
- `results/annual/` — year-by-year transition rates and 2017-2026 projection
- `docs/manuscript_full_article.docx` — Research Policy full-article manuscript (inline figures/tables)
- `docs/manuscript_full_article_figures.pptx` — editable English figure/table slides
- `docs/figures/` — individual PNG files for each inline figure

## Key model assumptions

- Six compartments per civilisation: `D`, `A`, `H_D`, `H_A`, `P_D`, `P_A`; `L` is absorbing dropout.
- Minimum viable coauthor threshold: `M = k × c_bar`.
- Endogenous PI-driven inflow: `I(P_D) = I0 + r · P_D` with `r` capped at a safety factor of 0.50 relative to `r_critical` (the most constrained fitted group realises about 0.40) to keep the linear system stable.
- Annual model: discrete one-year transition matrices with Laplace smoothing and correction pressures (probability clipping, dropout cap, inflow apportionment).

## Sources

- OpenAlex API: <https://api.openalex.org>
- Subfield: `subfields/1702` (Artificial Intelligence) under `fields/17` (Computer Science)
- Civilisation grouping rationale: `docs/mapping_rationale.md`
