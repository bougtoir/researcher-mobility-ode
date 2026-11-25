# JOI R1 Final: public reproducibility audit

States distinguished: public main = merged PR #1 (v4, fdf53b5); revision branch
devin/1795505148-joi-r1 = R1 + delta repairs; PR #2 head = resubmission source;
submitted-soon version = FINAL_LOCK files built from PR #2 head.

- PR #2 branch builds docgen deterministically from frozen canonical outputs:
  `python3 scripts/build_full_manuscript.py` regenerates every DOCX/PPTX/MD/zip;
  verified this session (rebuilt 3x, identical structure).
- Full OpenAlex re-extraction is snapshot-dependent (documented limitation:
  author-level data are not redistributed; reproduce.sh re-extracts).
- Public main does NOT yet contain the R1 revision — honest status: merge of
  PR #2 (author action) is required before main reproduces the resubmission.
- Data and Code Availability statement describes the actual public state;
  blinded version keeps the placeholder phrasing (JOI anonymisation).
- Commit SHA of PR head recorded at push time; dep versions unchanged.
