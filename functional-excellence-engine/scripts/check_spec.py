#!/usr/bin/env python3
"""Validate a spec against spec.schema.json BEFORE building.

Catches missing fields and out-of-range counts (6 axioms, 4 pillars, 8 metrics,
10 diagnostics, 6 interventions, 8-9 cases) while they are cheap to fix — i.e.
before the spec is rendered to a docx. This is a deterministic pre-flight check;
it does not judge content quality (that is the human checkpoints' job).

Specs are authored as `specs/<slug>.js` (an ES module / CommonJS module that
exports the spec object) so the docx engine can `require`/`import` them
directly. To validate without a JS runtime, this script first tries to load a
sibling `.json` of the same spec; if only the `.js` exists it shells out to node
to dump it to JSON.

Usage:
    python3 check_spec.py path/to/specs/cybersecurity.js
    python3 check_spec.py path/to/specs/cybersecurity.json
"""

import json
import os
import subprocess
import sys
import tempfile

try:
    import jsonschema
    HAVE_JSONSCHEMA = True
except ImportError:
    HAVE_JSONSCHEMA = False

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = os.path.join(HERE, "..", "schemas", "spec.schema.json")

# Hard count requirements, mirrored from the schema for a clear message even
# when jsonschema is not installed.
COUNTS = {
    "axioms": (6, 6),
    "pillars": (4, 4),
    "metrics": (8, 8),
    "diagnostics": (10, 10),
    "interventions": (6, 6),
    "cases": (8, 9),
}
REQUIRED = [
    "title", "control", "landscape", "economics", "axioms", "pillars",
    "metricsIntro", "metrics", "metricsNote", "bestPractices", "failureRefs",
    "diagnostics", "interventions", "plan", "cases", "ceoPriorities",
    "maintenance", "sources",
]


def load_spec(path):
    if path.endswith(".json"):
        with open(path) as f:
            return json.load(f)
    # A .js spec module — dump it to JSON via node.
    script = (
        "const m = require(process.argv[2]);"
        "const s = m.default || m.spec || m;"
        "process.stdout.write(JSON.stringify(s));"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tf:
        tf.write(script)
        runner = tf.name
    try:
        out = subprocess.check_output(["node", runner, os.path.abspath(path)])
    finally:
        os.unlink(runner)
    return json.loads(out)


def basic_checks(spec):
    errors = []
    for field in REQUIRED:
        if field not in spec:
            errors.append(f"missing required field: {field}")
    for field, (lo, hi) in COUNTS.items():
        val = spec.get(field)
        if isinstance(val, list):
            n = len(val)
            if n < lo or n > hi:
                want = f"{lo}" if lo == hi else f"{lo}-{hi}"
                errors.append(f"{field}: expected {want}, got {n}")
    return errors


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    path = sys.argv[1]

    try:
        spec = load_spec(path)
    except Exception as e:
        print(f"SPEC CHECK FAILED: could not load {path}: {e}", file=sys.stderr)
        sys.exit(2)

    errors = basic_checks(spec)

    if HAVE_JSONSCHEMA:
        with open(SCHEMA) as f:
            schema = json.load(f)
        validator = jsonschema.Draft7Validator(schema)
        for err in validator.iter_errors(spec):
            loc = "/".join(str(p) for p in err.absolute_path) or "(root)"
            errors.append(f"{loc}: {err.message}")
    else:
        print("NOTE: jsonschema not installed — running count/field checks only.", file=sys.stderr)

    if errors:
        print(f"SPEC CHECK FAILED for {path}:", file=sys.stderr)
        for e in sorted(set(errors)):
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    print(f"SPEC CHECK PASSED: {path} satisfies the 16-field contract and all counts.")
    sys.exit(0)


if __name__ == "__main__":
    main()
