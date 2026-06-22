#!/usr/bin/env node
/**
 * build_doc.js — load a spec, call the engine, write the .docx. No intelligence.
 *
 * Usage:
 *   node build_doc.js <spec.js|spec.json> <out.docx>
 *
 * The spec module may export the object directly (module.exports = {...}),
 * as `default`, or as `spec`.
 */

const fs = require("fs");
const path = require("path");
const { buildBuffer } = require("./engine_bic");

function loadSpec(specPath) {
  const abs = path.resolve(specPath);
  if (abs.endsWith(".json")) {
    return JSON.parse(fs.readFileSync(abs, "utf8"));
  }
  const mod = require(abs);
  return mod.default || mod.spec || mod;
}

async function main() {
  const [specPath, outPath] = process.argv.slice(2);
  if (!specPath || !outPath) {
    console.error("Usage: node build_doc.js <spec.js|spec.json> <out.docx>");
    process.exit(2);
  }
  const spec = loadSpec(specPath);
  const buffer = await buildBuffer(spec);
  fs.mkdirSync(path.dirname(path.resolve(outPath)), { recursive: true });
  fs.writeFileSync(outPath, buffer);
  console.log(`Wrote ${outPath} (${buffer.length} bytes)`);
}

main().catch((e) => {
  console.error("BUILD FAILED:", e.message);
  process.exit(1);
});
