#!/usr/bin/env node
// Renders a docs-page-chain prompt from a checkout, or applies the chain's finding coercion to a
// findings JSON, outside the workflow runtime. It extracts the pure functions from
// claude/.claude/workflows/docs-page-chain.js between their marker pair, so it can never drift
// from what the chain runs.
//
//   node scripts/docs-chain-render.mjs render --kind drafter|editor --checkout DIR --page PATH \
//        --track TRACK [--register REL] [--vale-rules FILE] [--page-inputs FILE] [--job TEXT]
//   node scripts/docs-chain-render.mjs coerce --read FILE --checkout DIR --track TRACK \
//        [--register REL]
//
// `render` runs each register section command through bash in the checkout, validates the output
// as the chain would, and prints the prompt; a rejected section prints its reason to stderr and
// exits 1. `coerce` reads a read JSON (an object with `verdict` and `findings`, or a bare findings
// array), applies the coercion against the checkout's brief, and prints the coerced read.
import { readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const RUNNER_PATH = join(HERE, "..", "claude", ".claude", "workflows", "docs-page-chain.js");
const START = "// === REGISTER EXTRACTION AND COERCION (docs-page-chain-derivation.test.mjs extracts this block) ===";
const END = "// === END REGISTER EXTRACTION AND COERCION ===";
const NAMES = [
  "baseGuideFor", "sectionSpecsFor", "sectionCommand", "validateSection", "collectSections",
  "coerceRead", "renderDrafterPrompt", "renderEditorPrompt"
];

/**
 * Loads the chain's pure functions from the runner source.
 * @returns {Record<string, Function>}
 * @throws {Error} when the marker pair is missing or out of order
 */
export function loadChainFunctions() {
  const src = readFileSync(RUNNER_PATH, "utf8");
  const from = src.indexOf(START);
  const to = src.indexOf(END);
  if (from === -1 || to === -1 || from > to) throw new Error(`register extraction markers missing from ${RUNNER_PATH}`);
  // eslint-disable-next-line no-new-func -- the runner cannot be imported (it has a top-level return).
  return new Function(`${src.slice(from, to)}\nreturn { ${NAMES.join(", ")} };`)();
}

/**
 * Extracts and validates every register section for a track by running its rendered command.
 * @param {Record<string, Function>} fns
 * @param {string} track
 * @param {string} checkout
 * @param {string} register - the register path, relative to the checkout
 * @returns {Record<string, string>} the section bodies, markers kept
 * @throws {Error} naming the first rejected section
 */
export function extractSections(fns, track, checkout, register) {
  const returned = fns.sectionSpecsFor(track).map((spec) => ({
    key: spec.key,
    output: execFileSync("bash", ["-c", fns.sectionCommand(spec, checkout, register)], { encoding: "utf8" })
  }));
  const collected = fns.collectSections(track, returned);
  if (!collected.ok) throw new Error(`register extraction rejected: ${collected.reason}`);
  return collected.sections;
}

/**
 * Parses `--flag value` pairs after the subcommand.
 * @param {string[]} argv
 * @returns {Record<string, string>}
 */
function parseFlags(argv) {
  const flags = {};
  for (let i = 0; i < argv.length; i += 2) {
    if (!argv[i].startsWith("--") || argv[i + 1] === undefined) throw new Error(`bad argument near "${argv[i]}"`);
    flags[argv[i].slice(2)] = argv[i + 1];
  }
  return flags;
}

/**
 * Runs one subcommand and returns the text to print.
 * @param {string[]} argv - process.argv after the script path
 * @returns {string}
 */
export function run(argv) {
  const [command, ...rest] = argv;
  const f = parseFlags(rest);
  for (const need of ["checkout", "track"]) if (!f[need]) throw new Error(`--${need} is required`);
  const fns = loadChainFunctions();
  const checkout = resolve(f.checkout);
  const register = f.register || "docs/internal/docs-register.md";
  const sections = extractSections(fns, f.track, checkout, register);
  if (command === "coerce") {
    if (!f.read) throw new Error("--read is required");
    const parsed = JSON.parse(readFileSync(f.read, "utf8"));
    const read = Array.isArray(parsed) ? { verdict: "accept", findings: parsed } : parsed;
    return JSON.stringify(fns.coerceRead(read, sections.brief), null, 2);
  }
  if (command === "render") {
    if (!f.page) throw new Error("--page is required");
    const page = { id: f.page, path: f.page, track: f.track, job: f.job || "" };
    const valeRules = f["vale-rules"] ? readFileSync(f["vale-rules"], "utf8").trim() : "";
    if (f.kind === "editor") return fns.renderEditorPrompt({ wt: checkout, valeRules, page, sections });
    if (f.kind === "drafter") {
      const pageInputs = f["page-inputs"]
        ? JSON.parse(readFileSync(f["page-inputs"], "utf8"))
        : { job: f.job || "(the page's job)", pageType: "", exemplarExcerpts: [], factIds: [], claimInventory: [] };
      return fns.renderDrafterPrompt({
        wt: checkout, valeRules, page, pageInputs, sections, exemplarSources: [],
        briefPath: `docs/internal/briefs/${f.track}/brief.json`, round: 1, findings: "",
        gateText: "(the docs gate line)"
      });
    }
    throw new Error("--kind must be drafter or editor");
  }
  throw new Error("the subcommand must be render or coerce");
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    process.stdout.write(`${run(process.argv.slice(2))}\n`);
  } catch (e) {
    process.stderr.write(`docs-chain-render: ${e.message}\n`);
    process.exitCode = 1;
  }
}
