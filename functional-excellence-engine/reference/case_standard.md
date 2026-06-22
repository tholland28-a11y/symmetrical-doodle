# The Case-Study Standard

This is the contract that makes the output worth producing. The case gate
(`scripts/verify_cases.py`) enforces it mechanically on every built document;
this file exists so the standard is internalized during research and writing,
not just caught at the end.

## The rule

> Every case study is a **real, named, dated event with a verifiable outcome.**

Four tests, applied to every case:

| Test | Requirement | Gate behavior |
|------|-------------|---------------|
| Named entity | A proper noun: a company, a CVE, an agency | Reject if missing |
| Date | A 4-digit year for the event and its outcome | Reject if missing |
| Source | A real, verifiable URL | Reject if missing |
| Concrete outcome | A number, ruling, settlement, or measurable result | Flag `weak` if missing |

The first three are hard rejections — a record or a case that fails them is not
allowed into a document. The fourth is a quality flag: a case with no concrete
outcome is weak even if it is real, and should be replaced if a stronger one
exists in the bank.

## Tiers

- **Tier 1 — regulatory.** Enforcement actions, settlements, consent orders,
  fines, government directives. The strongest evidence.
- **Tier 2 — named event.** A specific, attributable, reported event with an
  outcome (a breach, an outage, a recall) even without a regulatory action.
- **Tier 3 — structural.** A documented, attributable pattern or program at a
  named entity (e.g. a published reference architecture or a named company's
  disclosed practice). Use sparingly; prefer Tier 1 and 2.

## Case title format

The engine renders each case heading as:

```
Case <n> — <entity>: <name> (<date>)
```

For example: `Case 1 — Wawa: data breach (2019-2024)`. The gate parses this
heading and requires a proper noun **and** a 4-digit year in every title. Keep
`entity` a clean proper noun and `date` containing the year.

## Good vs. bad

**GOOD**

> **Equifax data breach (2017).** Attackers exploited an unpatched Apache Struts
> vulnerability (CVE-2017-5638) for which a fix had been available for months,
> exposing data on ~147 million people. A 2019 settlement of up to USD 700M with
> the FTC, CFPB, and states followed.
> Source: ftc.gov/enforcement/refunds/equifax-data-breach-settlement

- Named entity (Equifax, plus a CVE), a year, a concrete outcome (USD 700M
  settlement), and a real source. Tier 1.

**BAD**

> A large credit bureau was breached after failing to patch a known
> vulnerability, and later reached a significant settlement.

- No named entity, no date, no source, no specific number. This is filler. The
  gate rejects any document built on cases like this, and it should never reach
  a spec.

**BAD (marketing laundered into fact)**

> As an industry leader in security, the company maintained best-in-class
> defenses throughout the period.

- This is a self-description, not an event. If it appears in research it must be
  tagged `verified: false` in the company profile and must never become a case.

## How this connects to the pipeline

- **Stage 3** applies the rule at the source: the vetting gate rejects records
  that fail the first three tests and flags those missing a concrete outcome.
- **Stage 4** maps vetted records to cases one-to-one; no case may cite an event
  not in the bank.
- **Stage 5** runs `verify_cases.py` against the built document as the final
  backstop. A failure regenerates the spec — it does not ship.
