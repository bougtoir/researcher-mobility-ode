# JOI R1 Final: QC failure root cause

Three defects reached the R1 package; why QC missed each:

1. §3.9 scenario reversal — first occurrence: the prose drafted from memory of
   the scenario narrative rather than from summary.csv. QC had figure/table
   consistency checks but no region↔direction text-vs-CSV assertion. Root cause:
   narrative written without a generated-value binding. Corrective: paragraph now
   computes all displayed values from canonical rows (f-strings), plus regression
   tests A1–A9 that fail on the reversal.

2. PPTX Table 2 mapping — first occurrence: original PPTX writer appended
   T_over_M then positionally renamed columns. QC compared DOCX tables (which
   used .rename(dict)) — the PPTX path had no cell reconciliation. Root cause:
   positional index mapping after a column append. Corrective: name-based
   mapping + required-column KeyError + B-series cell-level tests.

3. Single-author voice — 'We/our' survived because prior passes audited
   semantic claims, not pronouns; 'the authors' boilerplate inherited from a
   multi-author template. Root cause: no voice rule in QC. Corrective: full-text
   sweep, 26 singularisations, audit doc lists every residual 'the author' with
   verdicts.

All confirmed by code/text inspection; regression tests demonstrably FAIL when
each defect is reintroduced (B3 on dropped column; A-series on swapped outputs;
voice audit is a deterministic text check).
