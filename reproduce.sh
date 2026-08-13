#!/usr/bin/env bash
# Reproduce all results and the manuscript from committed cohort data.
# Cohort extraction from OpenAlex is slow and requires API budget.
# Run it first with REEXTRACT=1 to refresh the sampled cohort, or FULL=1 to
# rebuild the cohort from the complete 2000-2023 AI/ML OpenAlex population.
set -e
cd "$(dirname "$0")"

# Unbuffer Python stdout/stderr so long-running background logs are visible immediately.
export PYTHONUNBUFFERED=1

if [ -n "${FULL}" ]; then
    python -u src/extract_full_cohort.py
elif [ -n "${REEXTRACT}" ]; then
    python -u src/cohort_extraction.py
fi

python src/ode_model.py
python src/ode_model_endogenous.py
python src/ode_model_endogenous.py --saturating --results-dir results/endogenous_saturating
python src/time_varying.py --cutoff 2010
python src/bootstrap_ci.py --n-boot 200
python src/policy_counterfactuals.py --packages
python scripts/annual_rates_projection_report.py
python scripts/build_full_manuscript.py
