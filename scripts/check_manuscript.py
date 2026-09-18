#!/usr/bin/env python3
"""Mechanical consistency checks on the generated manuscript DOCX files.

Checks: figure/table first-mention order and presence, citation order and
orphan/phantom references, non-ASCII characters outside allowed sets, and
phrases that refer to earlier versions of the manuscript.
"""
import re
import sys
import unicodedata
from pathlib import Path

from docx import Document

M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

OLD_VERSION_PHRASES = [
    "previous version", "earlier version", "previous analysis", "earlier analysis",
    "in the original submission", "revised version", "we previously", "previous draft",
    "old version", "SHIGA",
]


def body_paragraphs(doc):
    """Yield (text, is_heading, is_caption) for body paragraphs and table cells in document order."""
    import docx.table
    import docx.text.paragraph

    for child in doc.element.body.iterchildren():
        tag = child.tag.split("}")[-1]
        if tag == "p":
            p = docx.text.paragraph.Paragraph(child, doc)
            text = "".join(t.text or "" for t in child.iter(f"{{{W_NS}}}t"))
            yield text, p.style.name.startswith("Heading"), False
        elif tag == "tbl":
            tbl = docx.table.Table(child, doc)
            for row in tbl.rows:
                for cell in row.cells:
                    yield cell.text, False, True


def check_order(label, mentions, captions, errors):
    seen = []
    for n in mentions:
        if n not in seen:
            seen.append(n)
    expected = list(range(1, len(captions) + 1))
    if seen != expected:
        errors.append(f"{label} first-mention order {seen} != {expected}")
    if sorted(captions) != expected:
        errors.append(f"{label} captions {sorted(captions)} not sequential")
    print(f"{label}: first mention {seen}; captions {sorted(captions)}")


def main(path):
    doc = Document(path)
    errors = []
    fig_mentions, tab_mentions, fig_caps, tab_caps = [], [], [], []
    cite_mentions, ref_numbers = [], []
    supp_mentions, supp_caps = [], []
    in_refs = False
    has_refs = False
    non_ascii = {}
    old_hits = []
    full_text = []
    for text, is_heading, in_table in body_paragraphs(doc):
        full_text.append(text)
        if is_heading and text.strip() == "References":
            in_refs = True
            has_refs = True
            continue
        if in_refs:
            m = re.match(r"\[?(\d+)[\].]", text.strip())
            if m:
                ref_numbers.append(int(m.group(1)))
            continue
        cap = re.match(r"(Figure|Table) (\d+)\.", text.strip())
        if cap:
            (fig_caps if cap.group(1) == "Figure" else tab_caps).append(int(cap.group(2)))
        for m in re.finditer(r"\bFigure (\d+)", text):
            fig_mentions.append(int(m.group(1)))
        for m in re.finditer(r"\bTable (\d+)", text):
            tab_mentions.append(int(m.group(1)))
        scap = re.match(r"Supplementary Table S(\d+)\.", text.strip())
        if scap and (not supp_caps or supp_caps[-1] != int(scap.group(1))):
            supp_caps.append(int(scap.group(1)))
        for m in re.finditer(r"\bTable S(\d+)", text):
            supp_mentions.append(int(m.group(1)))
        for m in re.finditer(r"\[(\d+(?:[,–-]\s?\d+)*)\]", text):
            for part in re.split(r",\s?", m.group(1)):
                if re.match(r"\d+[–-]\d+", part):
                    a, b = re.split(r"[–-]", part)
                    cite_mentions.extend(range(int(a), int(b) + 1))
                else:
                    cite_mentions.append(int(part))
        for lower in OLD_VERSION_PHRASES:
            if lower.lower() in text.lower():
                old_hits.append((lower, text[:100]))
    for text in full_text:
        for ch in text:
            if ord(ch) > 127:
                non_ascii.setdefault(ch, 0)
                non_ascii[ch] += 1
    # math text (OMML) is checked separately for wide characters
    for t in doc.element.body.iter(f"{{{M_NS}}}t"):
        for ch in t.text or "":
            if ord(ch) > 127:
                non_ascii.setdefault(ch, 0)
                non_ascii[ch] += 1

    check_order("Figure", fig_mentions, fig_caps, errors)
    check_order("Table", tab_mentions, tab_caps, errors)
    if supp_caps:
        check_order("Table S", supp_mentions, supp_caps, errors)

    if has_refs:
        seen = []
        for n in cite_mentions:
            if n not in seen:
                seen.append(n)
        n_refs = len(ref_numbers)
        print(f"Citations: {len(seen)} distinct, first-mention max {max(seen) if seen else 0}; reference list {n_refs}")
        if seen != list(range(1, n_refs + 1)):
            errors.append(f"Citation first-mention order is not 1..{n_refs}: {seen}")
        if ref_numbers != list(range(1, n_refs + 1)):
            errors.append(f"Reference list numbering not sequential: {ref_numbers[:10]}...")
    else:
        print("No References section: bracketed numbers treated as intervals, citation check skipped")

    wide = {ch: c for ch, c in non_ascii.items() if unicodedata.east_asian_width(ch) in ("W", "F")}
    if wide:
        errors.append(f"Full-width/CJK characters present: {wide}")
    print("Non-ASCII characters used:", {f"{ch} U+{ord(ch):04X} {unicodedata.name(ch, '?')}": c for ch, c in sorted(non_ascii.items())})
    if old_hits:
        errors.append(f"Old-version phrases: {old_hits}")

    if errors:
        print("\nERRORS:")
        for e in errors:
            print(" -", e)
        return 1
    print("All mechanical checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1] if len(sys.argv) > 1 else "docs/manuscript_full_article.docx")))
