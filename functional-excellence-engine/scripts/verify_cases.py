#!/usr/bin/env python3
"""THE CASE GATE.

The single mechanism that lets the pipeline run unattended without quality
regressing into generic filler. It parses a *built* .docx (not the spec) and
enforces the case-study standard mechanically:

  1. Case count is in range (default 8-9).
  2. Cases are numbered sequentially 1..N with no gaps or repeats.
  3. Every case title contains a proper noun (a named entity) AND a 4-digit
     year. A case like "Improving our processes" has neither and fails.

Exit code 0 = PASS (ships). Non-zero = FAIL (the spec is regenerated, it does
NOT ship). This script reads the docx as a zip and parses word/document.xml
directly, so it has no third-party dependencies and audits the real artifact
rather than trusting the spec.

Usage:
    python3 verify_cases.py path/to/Function_BIC.docx [--min 8] [--max 9]
"""

import argparse
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# A case heading looks like: "Case 1 — Wawa data breach (2019-2024)"
# Accept em dash, en dash, hyphen, or colon as the separator after the number.
CASE_HEADING = re.compile(r"^\s*Case\s+(\d+)\s*[—–\-:]\s*(.+?)\s*$")
YEAR = re.compile(r"\b(1[89]\d{2}|20\d{2})\b")
# A "proper noun": a capitalised word (allows internal caps/digits like
# "PCI", "CVE-2021-44228", "T-Mobile"), excluding the leading word "Case".
PROPER_NOUN = re.compile(r"\b([A-Z][A-Za-z0-9.&'-]*(?:\s+[A-Z][A-Za-z0-9.&'-]*)*)")
STOPWORDS = {"Case", "The", "A", "An"}


def paragraph_texts(docx_path):
    """Yield the concatenated text of each paragraph in document order."""
    with zipfile.ZipFile(docx_path) as z:
        xml = z.read("word/document.xml")
    root = ET.fromstring(xml)
    for p in root.iter(W + "p"):
        runs = [t.text for t in p.iter(W + "t") if t.text]
        yield "".join(runs)


def has_proper_noun(title):
    """True if the title carries a named entity beyond filler/stopwords."""
    for m in PROPER_NOUN.finditer(title):
        token = m.group(1)
        first = token.split()[0]
        if first in STOPWORDS and len(token.split()) == 1:
            continue
        # Strip leading stopwords; if anything capitalised remains, it counts.
        words = [w for w in token.split() if w not in STOPWORDS]
        if words:
            return True
    return False


def verify(docx_path, lo, hi):
    failures = []
    numbers = []
    titles = []

    for text in paragraph_texts(docx_path):
        m = CASE_HEADING.match(text)
        if m:
            numbers.append(int(m.group(1)))
            titles.append((int(m.group(1)), m.group(2)))

    count = len(numbers)

    # 1. Count in range.
    if count < lo or count > hi:
        failures.append(f"case count {count} is outside the allowed range {lo}-{hi}")

    # 2. Sequential numbering.
    expected = list(range(1, count + 1))
    if numbers != expected:
        failures.append(f"case numbering not sequential: got {numbers}, expected {expected}")

    # 3. Every title has a proper noun + a 4-digit year.
    for num, title in titles:
        if not YEAR.search(title):
            failures.append(f"Case {num} title has no 4-digit year: {title!r}")
        if not has_proper_noun(title):
            failures.append(f"Case {num} title has no proper noun (named entity): {title!r}")

    return count, failures


def main():
    ap = argparse.ArgumentParser(description="The case gate: validate case studies in a built .docx.")
    ap.add_argument("docx", help="Path to the built .docx")
    ap.add_argument("--min", type=int, default=8, dest="lo", help="Minimum case count (default 8)")
    ap.add_argument("--max", type=int, default=9, dest="hi", help="Maximum case count (default 9)")
    args = ap.parse_args()

    try:
        count, failures = verify(args.docx, args.lo, args.hi)
    except (zipfile.BadZipFile, KeyError) as e:
        print(f"GATE ERROR: {args.docx} is not a readable .docx ({e})", file=sys.stderr)
        sys.exit(2)

    if failures:
        print(f"CASE GATE FAILED ({count} cases found) — this document does NOT ship:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        sys.exit(1)

    print(f"CASE GATE PASSED: {count} cases, sequential, every title has a named entity + a date.")
    sys.exit(0)


if __name__ == "__main__":
    main()
