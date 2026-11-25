#!/usr/bin/env python3
"""Semantic-claim regression on the generated manuscript DOCX.

Extracts all visible text (paragraphs, table cells, captions, OMML math text)
from the DOCX and checks for prohibited assertions: claims that crossing the
operational M benchmark changes the fitted ODE dynamics, is a sufficient/
necessary condition for empirical collapse, or makes loss irreversible.

Negative assertions ("crossing M does not establish ...") are allowed; the
checks look for the affirmative form. This is a tripwire, not a proof of
semantic consistency — combine with manual hostile review.

Usage: python3 scripts/semantic_claim_regression.py <manuscript.docx>
"""
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"


def iter_text_nodes(root):
    for el in root.iter():
        if el.tag in (W + "t", M + "t") and el.text:
            yield el.text


def extract_paragraphs(docx_path):
    with zipfile.ZipFile(docx_path) as z:
        names = ["word/document.xml"]
        names += [n for n in z.namelist()
                  if re.match(r"word/(header|footer)\d*\.xml", n)]
        paras = []
        for name in names:
            root = ET.fromstring(z.read(name))
            for p in root.iter(W + "p"):
                text = "".join(iter_text_nodes(p)).strip()
                if text:
                    paras.append(text)
            for tc in root.iter(W + "tc"):
                text = "".join(iter_text_nodes(tc)).strip()
                if text:
                    paras.append("[cell] " + text)
    return paras


def sentences(paras):
    out = []
    for p in paras:
        for s in re.split(r"(?<=[.!?])\s+", p):
            s = s.strip()
            if s:
                out.append(s)
    return out


# Each rule: (name, pattern asserting the claim, pattern that would exonerate
# the sentence when it merely denies or qualifies the claim).
RULES = [
    (
        "M-crossing stops fitted feedback",
        r"(viability boundary|crossing (of )?M|below M|falls? below M)[^.]*"
        r"(stops? (the )?(fitted )?(feedback|recruitment)|switches? off|"
        r"ceases? to operate|no longer reproduc|self-reinforcing rather than recoverable)",
        r"(does not|do not|not a|never|would|were|no run|scenario's collapse rule|"
        r"stylised|assumption|classification|operational|model event)",
    ),
    (
        "M sufficient/necessary for empirical collapse",
        r"(sufficient|necessary) (rather than necessary )?condition for "
        r"(real-world |empirical )?(community )?collapse",
        r"(neither|only for classification|not an? (established|empirically validated))",
    ),
    (
        "M-crossing irreversible/unrecoverable",
        r"(crossing|below M|falls? below M)[^.]*(irreversib|unrecoverable|"
        r"cannot (rebuild|recover)|point of no return)",
        r"(does not|do not|not|could in principle|scenario|assumption|we do not claim)",
    ),
    (
        "Collapse claimed as empirical finding",
        r"collapse[^.]*(observed|empirical finding|demonstrated|will occur|predicted)",
        r"(no |not |never|0 |zero |model|scenario|rule|assumption|boundary)",
    ),
    (
        "Point of no return language",
        r"point of no return",
        r"(never of|formerly|closest_point|proximity)",
    ),
    (
        "Early-warning predictive claim",
        r"early[- ]warning",
        r"(not|downgraded|monitoring|no validated|diagnostic)",
    ),
]


def main():
    docx = sys.argv[1]
    paras = extract_paragraphs(docx)
    sents = sentences(paras)
    print(f"DOCX: {docx}")
    print(f"Extracted {len(paras)} paragraph/cell blocks, {len(sents)} sentences.")
    failures = []
    flags = []
    for s in sents:
        for name, claim_pat, excuse_pat in RULES:
            if re.search(claim_pat, s, re.I):
                if re.search(excuse_pat, s, re.I):
                    flags.append(f"REVIEW ({name}): {s[:220]}")
                else:
                    failures.append(f"FAIL ({name}): {s[:220]}")
    for f in failures:
        print(f)
    print(f"---\n{len(failures)} hard failures, {len(flags)} flagged for manual review.")
    for f in flags:
        print(f)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
