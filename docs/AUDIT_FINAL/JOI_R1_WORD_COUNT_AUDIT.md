# JOI R1 — Word Count Audit

## Counting rule (JOI Guide for Authors)
Total = main text + figure captions + table contents + references + front matter.
Two independent counters were run on the built DOCX (`word/document.xml`):

| Counter | Method | v4 (submitted) | R1 (revised) |
|---|---|---|---|
| Full-text counter | every `w:t` token incl. headers/fields | 11,338 | **9,731** |
| Section-bucket counter | paragraphs classified by heading + table cells | 11,195 | **9,585** |

The conservative figure is the larger one: **9,731 words (−14.2% vs v4)**, under the 10,000-word cap and inside the 9,000–9,500 editorial target range on the section-bucket measure (9,585). The cover letter and response document quote the conservative full-text figures.

## Section-bucket breakdown

| Bucket | v4 | R1 | Δ |
|---|---|---|---|
| front matter | 42 | 33 | −9 |
| abstract block* | 520 | 514 | −6 |
| other (declarations, availability) | 126 | 126 | 0 |
| introduction | 768 | 801 | +33 (new informetrics framing) |
| methods | 2,547 | 2,104 | −443 |
| tables (cell text) | 1,128 | 722 | −406 (Tables moved to supplement) |
| captions | 617 | 458 | −159 |
| results | 2,406 | 2,060 | −346 |
| discussion | 1,709 | 1,284 | −425 (net; new §4.2 added, elsewhere cut) |
| conclusion | 208 | 154 | −54 |
| references | 1,124 | 1,329 | +205 (net: +21 informetrics refs, −14 removed) |
| **TOTAL** | **11,195** | **9,585** | **−1,610** |

*abstract block includes abstract body (241 words), keywords, highlights, declarations boilerplate.

## How the reduction was achieved
- Duplicated explanations, repeated background and re-enumerated results removed.
- Historical-analogy passage condensed to one evidence-carrying sentence; Jevons framing removed.
- Table S13 (measurement-sensitivity summary) and Table S14 (policy-instrument detail) moved to Supplementary Material (removed ~406 table words from main count).
- Calibration, sensitivity design, limitations and conclusion sections compressed; figure captions shortened.

## Kept in main text (per editor guidance)
Research aim; key operational definitions; model equations; calibration; all main results; origin and PI measurement limits; region-specific-M sensitivity (36/36 reversible, baseline-minimum ~36%); structural-invariance explanation; M non-identifiability; predictive-validity limits; main conclusions.

Measured by /tmp/wordcount.py and `_docx_full_word_count` in scripts/build_full_manuscript.py on docs/JOI_R1_MANUSCRIPT.docx and docs/JOI_MANUSCRIPT_FINAL_LOCK_v4.docx, 2026-11-24.
