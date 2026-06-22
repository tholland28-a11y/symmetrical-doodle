#!/usr/bin/env python3
"""Structural docx validation.

Confirms the built .docx is well-formed and contains the proven 13-section
structure (one heading per section, in order). This is the mechanical
"does the document have the right skeleton" check; the case gate
(verify_cases.py) handles the case-study standard separately.

Reads the docx as a zip and parses word/document.xml directly — no third-party
dependencies.

Usage:
    python3 validate.py path/to/Function_BIC.docx
"""

import re
import sys
import zipfile
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# The 13 sections of the proven format, in order. Matching is case-insensitive
# and ignores a leading number / punctuation so "1. Control Tower" matches.
SECTIONS = [
    "Control Tower",
    "Landscape",
    "Economics",
    "Axioms",
    "Pillars",
    "Metrics",
    "Best Practices",
    "Failure",
    "Diagnostics",
    "Interventions",
    "Plan",
    "Case Studies",
    "CEO Priorities",
]


def headings(docx_path):
    """Return (text, style) for every paragraph that uses a Heading style."""
    with zipfile.ZipFile(docx_path) as z:
        xml = z.read("word/document.xml")
    root = ET.fromstring(xml)
    out = []
    for p in root.iter(W + "p"):
        ppr = p.find(W + "pPr")
        style = None
        if ppr is not None:
            pstyle = ppr.find(W + "pStyle")
            if pstyle is not None:
                style = pstyle.get(W + "val")
        text = "".join(t.text for t in p.iter(W + "t") if t.text)
        out.append((text, style))
    return out


def norm(s):
    return re.sub(r"^[\d.\)\s]+", "", s).strip().lower()


def validate(docx_path):
    errors = []
    try:
        with zipfile.ZipFile(docx_path) as z:
            bad = z.testzip()
            if bad:
                errors.append(f"corrupt entry in archive: {bad}")
            names = z.namelist()
        for required in ("word/document.xml", "[Content_Types].xml"):
            if required not in names:
                errors.append(f"missing archive member: {required}")
    except zipfile.BadZipFile as e:
        return [f"not a valid .docx (zip): {e}"]

    # Only consider heading-styled paragraphs, so body text that happens to
    # contain a section keyword cannot satisfy the in-order check.
    all_text = [norm(t) for t, style in headings(docx_path)
                if style and "heading" in style.lower()]

    # Each section heading must be present, in order.
    cursor = 0
    for section in SECTIONS:
        key = section.lower()
        found_at = None
        for i in range(cursor, len(all_text)):
            if key in all_text[i]:
                found_at = i
                break
        if found_at is None:
            errors.append(f"missing or out-of-order section heading: {section!r}")
        else:
            cursor = found_at + 1

    return errors


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    path = sys.argv[1]
    errors = validate(path)
    if errors:
        print(f"VALIDATION FAILED for {path}:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    print("All validations PASSED!")
    sys.exit(0)


if __name__ == "__main__":
    main()
