# JOI R1 Final: semantic code delta audit (DELTA only)

git diff on the R1 branch for scientific-computation files: NONE.
Changes confined to scripts/build_full_manuscript.py (docgen/display) and new
scripts/pptx_table_regression.py (tests). Verified:

- estimands/units/signs/numerators/denominators unchanged in src/ and results/.
- γ=0 field hit stock: code untouched; manuscript now matches CSV (US rises,
  Sinic below) — display fix only.
- γ* definition (terminal criterion in src/dominant_strategy.py): unchanged;
  caption/prose now state the terminal-vs-dip distinction.
- Region↔output correspondence: builder now selects focal rows by name
  (_g0[...focal == dom['focal']]), not position.
- Table 2: _equilibrium_table_pptx maps by column name with required-column
  KeyError; DOCX path was already name-based.
- No canonical CSV regenerated: results/ hashes identical to committed state.

Conclusion: scientific computation needed no change; all edits are
display/docgen fixes plus tests — consistent with a prose/mapping defect, not a
computation defect.
