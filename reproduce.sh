#!/usr/bin/env bash
# Reproduce all results and the manuscript from committed cohort data.
# Cohort extraction from OpenAlex is slow and requires API budget.
# Run it first with REEXTRACT=1 to refresh the sampled cohort, or FULL=1 to
# rebuild the cohort from the complete 2000-2023 AI/ML OpenAlex population.
set -e
cd "$(dirname "$0")"

# Unbuffer Python stdout/stderr so long-running background logs are visible immediately.
export PYTHONUNBUFFERED=1

# The author-level cohort files (data/cohort/cohort.csv, raw_sampled_works.json
# and data/cohort/pi_proxy/*) are derived from OpenAlex records and are not
# redistributed in the public repository. When they are absent they are
# re-extracted from the OpenAlex API here (sampled cohort: minutes; full
# population for the PI-proxy robustness snapshot: about 30 minutes, needs
# OPENALEX_API_KEY). OpenAlex is updated continuously, so a fresh extraction
# reproduces the published rates and rankings up to small snapshot differences.
if [ -n "${FULL}" ] || [ ! -f data/cohort/pi_proxy/cohort.csv ]; then
    # Full 2000-2023 AI/ML population, persisted to SQLite (data/cache/*.db).
    # Writes the PI-proxy robustness snapshot with all three pi_year_* columns.
    python -u src/extract_full_cohort.py --output-dir data/cohort/pi_proxy
fi
if [ -n "${REEXTRACT}" ] || [ ! -f data/cohort/cohort.csv ]; then
    python -u src/cohort_extraction.py
fi

python src/ode_model.py
python src/ode_model_endogenous.py
python src/ode_model_endogenous.py --saturating --results-dir results/endogenous_saturating
python src/time_varying.py --cutoff 2010
python src/bootstrap_ci.py --n-boot 200
python src/policy_counterfactuals.py --packages
python scripts/annual_rates_projection_report.py
python src/dominant_strategy.py
python src/pi_proxy_robustness.py
python src/m_sensitivity.py
python scripts/build_full_manuscript.py
