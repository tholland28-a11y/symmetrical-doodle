---
name: functional-excellence-engine
description: >-
  Point this at any company to generate a library of board-ready
  functional-excellence playbooks — one per business function — in the proven
  13-section format, where every case study is a real, named, dated event with
  a verifiable source. Use when asked to build, generate, or refresh a
  functional-excellence library, playbook set, or "best-in-class" playbooks for
  a named company or industry.
---

# Functional Excellence Engine

You are running an automated, company-agnostic playbook-library generator.
Point the engine at a company; it researches what the company does, derives the
functions that make up that business, gathers real-world evidence for each, and
produces one board-ready playbook per function.

## The core idea (read this first)

The mechanical pieces — building the docx, file orchestration — are the easy
20%. The 80% that determines whether the output is any good is **research
quality** and **enforcement of the case-study standard**. Left alone, an
automated engine regresses toward generic filler. Everything below exists to
engineer hard against that regression.

Three principles govern how you work:

1. **You orchestrate; scripts do only deterministic work.** The intelligence —
   research, judgment, writing — lives in you executing this skill, not in
   Python. The scripts only build docx, validate, count, and gate.
2. **The case-study standard is an enforced contract, not a hope.** A mechanical
   gate (`verify_cases.py`) rejects any document whose cases lack a named
   entity, a date, and a source. A failing doc never ships — you regenerate it.
3. **Human checkpoints between stages.** The pipeline pauses for approval after
   the functional map (Checkpoint 1) and after the research bank (Checkpoint 2)
   — the two points where an error is cheap to fix early and expensive to
   discover late. Do not run all five stages unattended.

## The case-study standard (internalize it; the gate is the backstop)

Every case study is a **real, named, dated event with a verifiable outcome.**

- **Named entity** — a proper noun: a company, a CVE, an agency. Not "a major
  retailer", not "our team".
- **Date** — at least a 4-digit year for the event and its outcome.
- **Source** — a real URL you can verify.
- **Concrete outcome** — a number, a ruling, a settlement, a measurable result.

GOOD: `Wawa data breach (2019-2024) — POS malware exposed ~34M cards; USD 8M
multistate settlement in 2024. Source: pcworld.com/...`

BAD: `A convenience-store chain suffered a breach and improved its security
posture.` (No named entity, no date, no source, no concrete outcome — this is
filler and the gate will reject any document built on it.)

See `reference/case_standard.md` for more good/bad examples.

## The pipeline — five stages

Each stage consumes the previous stage's output and writes a structured
artifact to `workdir/<company>/`. Stages are independently re-runnable, so a
single function can be regenerated without rebuilding the whole library.

### Stage 1 — Company Discovery → `company_profile.json`

Input: a company name (optionally a website or ticker). Run a handful of web
searches and read the company site. The key output is not prose — it is a
**classification** that drives everything downstream. Capture:

- **Identity**: legal name, aliases/former names, founding, HQ, ownership.
- **Business model**: what it sells, to whom, how it makes money.
- **Industry classification** — the single most important field; it selects the
  functional template in Stage 2.
- **Scale & footprint**: size signals that calibrate metrics and benchmarks.

**Honesty flag (build it into the profile).** Tag each material fact as
`verified` (neutral / independent / filings — founding, HQ, regulatory) or
unverified (company self-description / marketing — "leading provider of…").
This flag propagates so the documents never launder marketing into fact.

Conform to `schemas/company_profile.schema.json`.

### Stage 2 — Functional Decomposition → `functions.json`

From the profile's industry classification, generate the list of functions that
make up this business. This is industry-dependent — a bank, a retailer, and a
cybersecurity firm have different function sets.

- Look up the industry in `reference/industry_functions.md` for a starting
  template, then tailor to the specific company.
- **Weight** each function `core` / `standard` / `peripheral` for this company
  so the build can prioritize what matters most.
- Each function entry carries: `name`, `slug`, `scope` (1-2 sentences),
  `researchThemes` (search seeds for Stage 3), and `weighting`.

Conform to `schemas/function.schema.json`.

> ### CHECKPOINT 1 — human approval (mandatory)
> Stop. Present the functional map for approval before any research runs.
> Show the company, the industry, and the table of functions with their
> weighting and scope. Approving or editing the map here costs seconds;
> discovering a wrong map after building 14 documents wastes the whole run.
> Do not proceed to Stage 3 until the human approves or edits the map.

### Stage 3 — Research Harvesting → `research/<slug>.json` (the critical stage)

For each function, run targeted web searches against its `researchThemes` to
collect real, named, dated events with verifiable outcomes. Store each as a
record (see `schemas/research.schema.json`):

```json
{
  "name": "Wawa data breach",
  "entity": "Wawa",
  "date": "2019-2024",
  "what_happened": "POS/fuel-dispenser malware exposed ~34M cards…",
  "outcome": "$8M multistate settlement (2024); EMV chip cards unaffected",
  "source_url": "https://…",
  "tier": 1,
  "verified": true
}
```

**The vetting gate — reject before a record reaches a document:**
- No named entity (proper noun)? → reject.
- No date (4-digit year minimum)? → reject.
- No source URL? → reject.
- No concrete outcome (number, ruling, settlement, measurable result)? → flag
  `weak`.

**Target volume: 10-12 vetted events per function**, so the spec can select the
best 8-9. Tiers: 1 = regulatory, 2 = named event, 3 = structural.

> ### CHECKPOINT 2 — human approval (mandatory)
> Stop. Present the research bank — per-function counts plus a sample event per
> function — for approval before writing any specs. Thin or low-quality banks
> are caught here, where a targeted re-search is cheap. Do not proceed to
> Stage 4 until the human approves.

### Stage 4 — Spec Generation → `specs/<slug>.js`

For each function, write the spec object — the exact contract the docx engine
consumes — drawing **only** from that function's vetted research bank. **No case
may cite an event not in the bank.**

The fields (see `schemas/spec.schema.json`): `title`, `control`, `landscape`,
`economics`, `axioms`, `pillars`, `metricsIntro`, `metrics`, `metricsNote`,
`bestPractices`, `failureRefs`, `diagnostics`, `interventions`, `plan`,
`cases`, `ceoPriorities`, `maintenance`, `sources`.

Counts are enforced: **6 axioms, 4 pillars, 8 metrics, 10 diagnostics,
6 interventions, 8-9 cases.** Each case carries `name`, `entity`, `date`,
`context`, `situation`, `approach`, `result`, `lesson` (numbered tactical
moves), `source`, `tier` — mapped directly from a research record.

Write the spec as `specs/<slug>.js` exporting the object
(`module.exports = { … }`). Use `reference/spec_example.js` as the gold
standard. Then run `python3 scripts/check_spec.py specs/<slug>.js` and fix any
field/count failures **before** building.

### Stage 5 — Build, Validate & Package (run one function at a time)

For each function, in order:

1. **Build**: `node engine/build_doc.js specs/<slug>.js workdir/<company>/out/<Function>_BIC.docx`
2. **Validate structure**: `python3 scripts/validate.py <…>.docx` — expect
   `All validations PASSED!`
3. **Run the case gate**: `python3 scripts/verify_cases.py <…>.docx` — confirms
   count, sequential numbering, and that every case title has a proper noun +
   a 4-digit year.

**Failure handling.** If `validate.py` or `verify_cases.py` exits non-zero, the
document does **not** ship. Diagnose, fix the spec (usually the cases or their
titles), re-run `check_spec.py`, and rebuild. Repeat until both pass. Only then
move to the next function.

When every function passes, zip the library and present a **build report**:
documents produced, case counts per doc, and any `weak`/unverified flags
carried from research.

## Repository map

```
functional-excellence-engine/
├─ SKILL.md                      # this file — the playbook you follow end-to-end
├─ engine/
│  ├─ engine_bic.js              # the 13-section docx engine
│  └─ build_doc.js               # wraps a spec → .docx
├─ scripts/
│  ├─ validate.py                # docx structural validation
│  ├─ verify_cases.py            # THE CASE GATE (count + named + dated)
│  └─ check_spec.py              # spec field/count validation
├─ schemas/
│  ├─ company_profile.schema.json
│  ├─ function.schema.json
│  ├─ research.schema.json
│  └─ spec.schema.json           # the field contract
├─ reference/
│  ├─ industry_functions.md      # industry → typical function map
│  ├─ case_standard.md           # the rule + good/bad examples
│  └─ spec_example.js            # a gold-standard filled spec
└─ workdir/<company>/            # all per-run artifacts
   ├─ company_profile.json
   ├─ functions.json
   ├─ research/<slug>.json
   ├─ specs/<slug>.js
   └─ out/<Function>_BIC.docx
```

## What the engine does NOT remove

- **Judgment about what is material** to a function — this is what the human
  checkpoints are for.
- **Research depth** — the engine accelerates harvesting; the human steers
  toward the richest veins.
- **The honesty discipline** — separating verified fact from company marketing
  remains a human responsibility, carried by the `verified` flag.

The engine takes a 10-document library from a multi-session hand-build to a
guided afternoon — without sacrificing the case-study standard that makes the
output worth producing.

## Setup

From `functional-excellence-engine/`: `npm install` (installs `docx`). The
Python scripts use only the standard library, except `check_spec.py` which uses
`jsonschema` for full schema validation and degrades gracefully to field/count
checks if it is not installed (`pip install jsonschema` for the full check).
