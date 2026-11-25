# JOI R1 Final: PPTX regression test report

scripts/pptx_table_regression.py — 18/18 PASS.

Scenario (A): A1 US γ=0 field hits rise all φ (min 1.030); A2 Sinic below all φ
(max 0.999); A3 US γ*field not reached @φ=0.5; A4 monotonic decrease 5.76→0.71;
A5 Sinic γ*field=0; A6 US γ*self only @8.0; A7 Sinic γ*self all φ; A8 terminal
criterion (NaN in-horizon dips); A9 manuscript md reversal guard.

Table (B): B1 full-cell Table 2 reconciliation vs canonical CSV via _fmt;
B2 column-permutation invariance; B3 missing-column KeyError; B4 14 table slides
present; B5/B6 Table 2 slide + header; B7 all cells vs canonical (display names
applied); B8/B9 Table 8 cells vs scenario CSVs.

Fail-on-reintroduced-defect: A1/A2 invert under a swapped region→output mapping;
B3 fires on the dropped-column case that caused the original bug.
