# Functional Excellence Engine

An automated, company-agnostic playbook-library generator for Claude Code.
Point it at any company; it researches what the company does, derives the
functions that make up that business, gathers real-world evidence for each, and
produces a library of board-ready functional-excellence playbooks — one per
function — in the proven 13-section format, where **every case study is a real,
named, dated event with a verifiable outcome.**

The engine is a **skill** (the intelligence) plus a thin set of **deterministic
scripts** (the mechanics). Claude executes the skill; the scripts only build
docx, validate, count, and gate. See [`SKILL.md`](./SKILL.md) for the full
end-to-end workflow Claude follows.

## Quick start

```bash
cd functional-excellence-engine
npm install                  # installs `docx`
pip install jsonschema       # optional: full spec schema validation

# Smoke-test the whole build → validate → gate loop on the gold-standard spec:
npm run smoke
```

To run the engine on a company, ask Claude to use the
`functional-excellence-engine` skill and name the company. Claude runs the
five-stage pipeline, pausing at the two checkpoints for your approval.

## The five-stage pipeline

| Stage | Name | Output |
|-------|------|--------|
| 1 | Company Discovery | `company_profile.json` |
| 2 | Functional Decomposition | `functions.json` — **Checkpoint 1** |
| 3 | Research Harvesting | `research/<slug>.json` — **Checkpoint 2** |
| 4 | Spec Generation | `specs/<slug>.js` |
| 5 | Build, Validate & Package | `out/<Function>_BIC.docx` |

Two human checkpoints (after the functional map and after the research bank)
catch wrong maps and thin banks while they are cheap to fix. The case gate
(`scripts/verify_cases.py`) is the mechanical backstop: a document whose cases
lack a named entity, a date, and a source never ships — it is regenerated.

## The deterministic scripts

| Script | Single responsibility |
|--------|----------------------|
| `engine/build_doc.js` | Load a spec, call the engine, write the `.docx`. No intelligence. |
| `scripts/validate.py` | Structural docx validation (the 13 sections, in order). |
| `scripts/verify_cases.py` | **The case gate**: count + sequential numbering + every title has a named entity & a year. Exit non-zero on failure. |
| `scripts/check_spec.py` | Validate a spec against the schema (fields present, counts in range) before building. |

## Layout

See the repository map in [`SKILL.md`](./SKILL.md#repository-map).
`reference/spec_example.js` is a gold-standard filled spec (Cybersecurity) used
as both the writing reference and the build fixture.
