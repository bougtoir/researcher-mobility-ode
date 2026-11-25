# JOI R1 Final: word count reconciliation

Methods (all on JOI_R1_MANUSCRIPT_FINAL.docx):
A. Full-DOCX count: every w:t token in word/document.xml (headers, captions,
   table cells, references, declarations) = **9,603**.
B. Section-bucket count (front 33 / abstract 497 / other 126 / intro 801 /
   methods 2,092 / tables 722 / captions 444 / results 2,122 / discussion 1,150 /
   conclusion 142 / references 1,329) = **9,458**.
C. Conservative figure-inclusive: A + text drawn inside figures = 9,603 + 195
   = **9,798**. Figure text extracted from the generation source (matplotlib
   title/label/text/annotate/legend calls + f-string literals via AST), not OCR;
   includes axis labels, legends, annotations. Caption text already inside A —
   no double counting.
D. Journal-conventional (main text excl. references/front matter) ≈ 8,241;
   JOI/Elsevier do not publish a binding counting rule, so C is reported as the
   compliance figure.

Verdict: 9,798 < 10,000 hard cap (margin ~200). The ≤9,500 stretch target was not
fully reached; further compression would have removed editor-required content
(§4.2 comparison, sensitivity disclosures). Original (v4, same method A):
11,338 → 9,603 = -15.1%; cover letter and response doc report the same method
and figures.
