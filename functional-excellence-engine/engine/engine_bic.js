/**
 * engine_bic.js — the 13-section "Board-In-Chief" docx engine.
 *
 * Pure, deterministic rendering: spec object in, a `docx` Document out. No
 * intelligence, no I/O, no network. All judgment lives upstream in the spec;
 * this file only lays type on a page in the proven 13-section format.
 *
 * The one contract the rest of the pipeline depends on: every case study is
 * rendered with a heading of the exact form
 *
 *     Case <n> — <entity>: <name> (<date>)
 *
 * so the case gate (verify_cases.py) can parse a named entity + a 4-digit year
 * out of each case title in the built document.
 */

const {
  Document, Packer, Paragraph, TextRun, HeadingLevel,
  AlignmentType, ExternalHyperlink,
} = require("docx");

const SECTION_TITLES = [
  "1. Control Tower",
  "2. Landscape",
  "3. Economics",
  "4. Axioms",
  "5. Pillars",
  "6. Metrics",
  "7. Best Practices",
  "8. Failure Modes",
  "9. Diagnostics",
  "10. Interventions",
  "11. 90-Day Plan",
  "12. Case Studies",
  "13. CEO Priorities & Maintenance",
];

function h1(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 320, after: 160 } });
}
function h2(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 80 } });
}
function body(text) {
  return new Paragraph({ children: [new TextRun(text)], spacing: { after: 120 } });
}
function bullet(text) {
  return new Paragraph({ children: [new TextRun(text)], bullet: { level: 0 }, spacing: { after: 40 } });
}
function numbered(text, ref) {
  return new Paragraph({ children: [new TextRun(text)], numbering: { reference: ref, level: 0 }, spacing: { after: 40 } });
}

function caseTitle(c, n) {
  // The exact form the case gate parses.
  return `Case ${n} — ${c.entity}: ${c.name} (${c.date})`;
}

/** Build the document children for a single spec. */
function renderChildren(spec) {
  const children = [];

  // Cover.
  children.push(new Paragraph({
    text: spec.title,
    heading: HeadingLevel.TITLE,
    alignment: AlignmentType.CENTER,
    spacing: { after: 80 },
  }));
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Functional Excellence Playbook", italics: true })],
    spacing: { after: 320 },
  }));

  // 1. Control Tower
  children.push(h1(SECTION_TITLES[0]));
  children.push(body(spec.control));

  // 2. Landscape
  children.push(h1(SECTION_TITLES[1]));
  children.push(body(spec.landscape));

  // 3. Economics
  children.push(h1(SECTION_TITLES[2]));
  children.push(body(spec.economics));

  // 4. Axioms
  children.push(h1(SECTION_TITLES[3]));
  spec.axioms.forEach((a) => children.push(numbered(a, "axioms")));

  // 5. Pillars
  children.push(h1(SECTION_TITLES[4]));
  spec.pillars.forEach((p) => {
    children.push(h2(p.name));
    children.push(body(p.detail));
  });

  // 6. Metrics
  children.push(h1(SECTION_TITLES[5]));
  children.push(body(spec.metricsIntro));
  spec.metrics.forEach((m) => {
    children.push(new Paragraph({
      children: [
        new TextRun({ text: `${m.name}. `, bold: true }),
        new TextRun(`${m.definition} `),
        new TextRun({ text: `Target: ${m.target}`, italics: true }),
      ],
      bullet: { level: 0 },
      spacing: { after: 40 },
    }));
  });
  children.push(new Paragraph({ children: [new TextRun({ text: spec.metricsNote, italics: true })], spacing: { before: 80, after: 120 } }));

  // 7. Best Practices
  children.push(h1(SECTION_TITLES[6]));
  spec.bestPractices.forEach((b) => children.push(bullet(b)));

  // 8. Failure Modes
  children.push(h1(SECTION_TITLES[7]));
  spec.failureRefs.forEach((f) => children.push(bullet(f)));

  // 9. Diagnostics
  children.push(h1(SECTION_TITLES[8]));
  spec.diagnostics.forEach((d) => children.push(numbered(d, "diagnostics")));

  // 10. Interventions
  children.push(h1(SECTION_TITLES[9]));
  spec.interventions.forEach((i) => {
    children.push(h2(i.name));
    children.push(body(i.detail));
  });

  // 11. 90-Day Plan
  children.push(h1(SECTION_TITLES[10]));
  spec.plan.forEach((phase) => {
    children.push(h2(phase.horizon));
    phase.actions.forEach((a) => children.push(bullet(a)));
  });

  // 12. Case Studies
  children.push(h1(SECTION_TITLES[11]));
  spec.cases.forEach((c, idx) => {
    children.push(h2(caseTitle(c, idx + 1)));
    children.push(new Paragraph({ children: [new TextRun({ text: "Context: ", bold: true }), new TextRun(c.context)], spacing: { after: 40 } }));
    children.push(new Paragraph({ children: [new TextRun({ text: "Situation: ", bold: true }), new TextRun(c.situation)], spacing: { after: 40 } }));
    children.push(new Paragraph({ children: [new TextRun({ text: "Approach: ", bold: true }), new TextRun(c.approach)], spacing: { after: 40 } }));
    children.push(new Paragraph({ children: [new TextRun({ text: "Result: ", bold: true }), new TextRun(c.result)], spacing: { after: 40 } }));
    children.push(new Paragraph({ children: [new TextRun({ text: "Lessons:", bold: true })], spacing: { after: 20 } }));
    c.lesson.forEach((l) => children.push(numbered(l, `lessons-${idx}`)));
    children.push(new Paragraph({
      children: [new TextRun({ text: "Source: ", bold: true }), new ExternalHyperlink({ link: c.source, children: [new TextRun({ text: c.source, style: "Hyperlink" })] })],
      spacing: { after: 160 },
    }));
  });

  // 13. CEO Priorities & Maintenance
  children.push(h1(SECTION_TITLES[12]));
  children.push(h2("CEO Priorities"));
  spec.ceoPriorities.forEach((p) => children.push(bullet(p)));
  children.push(h2("Maintenance"));
  children.push(body(spec.maintenance));

  // Sources appendix.
  children.push(h1("Sources"));
  spec.sources.forEach((s) => {
    children.push(new Paragraph({
      children: [
        new TextRun(`${s.label} — `),
        new ExternalHyperlink({ link: s.url, children: [new TextRun({ text: s.url, style: "Hyperlink" })] }),
      ],
      bullet: { level: 0 },
      spacing: { after: 40 },
    }));
  });

  return children;
}

/** Numbering configs: one per ordered list so each restarts at 1. */
function numberingConfig(spec) {
  const configs = [
    { reference: "axioms", levels: [{ level: 0, format: "decimal", text: "%1.", alignment: AlignmentType.START }] },
    { reference: "diagnostics", levels: [{ level: 0, format: "decimal", text: "%1.", alignment: AlignmentType.START }] },
  ];
  spec.cases.forEach((_, idx) => {
    configs.push({
      reference: `lessons-${idx}`,
      levels: [{ level: 0, format: "decimal", text: "%1.", alignment: AlignmentType.START }],
    });
  });
  return { config: configs };
}

/** Build a `docx` Document from a validated spec. */
function buildDocument(spec) {
  return new Document({
    creator: "Functional Excellence Engine",
    title: `${spec.title} — Functional Excellence Playbook`,
    numbering: numberingConfig(spec),
    sections: [{ children: renderChildren(spec) }],
  });
}

/** Build a spec into a .docx Buffer. */
async function buildBuffer(spec) {
  const doc = buildDocument(spec);
  return Packer.toBuffer(doc);
}

module.exports = { buildDocument, buildBuffer, SECTION_TITLES, caseTitle };
