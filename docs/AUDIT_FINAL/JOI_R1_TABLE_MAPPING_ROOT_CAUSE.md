# JOI R1 Final: Table 2 PPTX column-mapping root cause

## Defect
Editable PPTX Table 2 built display columns by appending T_over_M then applying a
positional .columns=[...] rename; labels shifted right from index 4, so T/M held I0,
I0 held r, etc. (reproduced corrupted values: T/M=1,588.74, I0=0, r fitted=0).

## Why existing QC passed
The DOCX Table 2 uses .rename(dict) name-based mapping and was always correct;
QC compared DOCX/table text, not the PPTX table object, so the PPTX path had no
cell-level reconciliation. Table-existence checks pass on any well-formed table.

## Fix
New _equilibrium_table_pptx(eq): explicit required-column check (raises KeyError
listing missing columns, no zero/empty substitution) + dict-built display frame
by column NAME (Group/T_eq/M/Margin/T_M/I0/r/r_obs/r_crit). Same pattern applied
to pnr_table, merged, boot_tab (all positional renames converted to .rename(dict)).

## Verification
JOI_R1_TABLE_CELL_RECONCILIATION.csv: 81/81 cells (9 regions x 9 cols incl. header)
match canonical equilibrium_summary.csv under _fmt rounding. Table 8 hosted-pool
and field-hit cells match dominant_strategy/summary.csv. All other 14 PPTX tables
generated via name-based columns or .rename(dict) — audited, no stale values.
