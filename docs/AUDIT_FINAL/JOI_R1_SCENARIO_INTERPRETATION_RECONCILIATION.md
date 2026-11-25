# JOI R1 Final: Scenario interpretation reconciliation

## Defect
Pre-repair §3.9 prose stated the field's hit stock declines at γ=0 under the US-led
scenario and held under the Sinic-centred one — the reverse of Table 8 / canonical CSVs.

## Canonical truth (results/dominant_strategy/summary.csv, fitted, host_recruits, γ=0)
- US field_hits_terminal_relative: 1.030/1.061/1.117/1.198/1.284 for φ=0.5–8 (rises;
  year_field_hits_below_baseline=NaN — never dips in-horizon).
- Sinic: 0.9989/0.9952/0.9862/0.9703/0.9507 — below baseline at γ=0 at every φ
  (the two weakest display 1.00 after rounding).
- γ* is a TERMINAL-value criterion (src/dominant_strategy.py gamma_threshold, L374-398).
- US γ*field: not reached@0.5, 5.76@1.0, 2.65@2.0, 1.20@4.0, 0.71@8.0 (γ≤6 search).
- US γ*self (hosted hits): only 3.90@8.0. Sinic γ*self: 4.59/3.76/2.79/2.04/1.61.

## Correction (scripts/build_full_manuscript.py, §3.9 paragraph)
Now states: US rises to 1.28x at strongest pull; Sinic below at γ=0 for every pull
(unrounded 0.999/0.995 at the two weakest); US field losses only beyond γ*
(5.76→0.71, not reached at φ=0.5); γ* scored on end-of-horizon values, not dips;
hosted-stock γ* 3.9 (US@8.0) and 1.6–4.6 (Sinic).
Rendered PDF verified: text matches canonical values.

## Propagation check
Abstract, Discussion, Conclusion, Fig 9/10 captions, highlights, cover letter,
response doc, supplement contain no direction claim contradicting the table
(dead code _poaching_paragraph not emitted). Response doc discloses the correction.

## Regression test
scripts/pptx_table_regression.py tests A1–A9: direction at γ=0 per region,
γ* per region and per metric, terminal-vs-horizon distinction, md-level reversal
guard. All PASS; suite FAILS when the reversal is reintroduced (verified via
the md-content check and canonical direction assertions).
