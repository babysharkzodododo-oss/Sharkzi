// Headless checks for rhyming-synonyms.html, driven through its window.__rhyme seam.
//
//   npm i playwright && node rhyming-synonyms.test.mjs
//
// The API is stubbed via __rhyme.setFetch, so these run offline and never touch
// api.datamuse.com. They cover the set intersection, every filter, ranking, cap
// detection, both failure paths, scan grouping and the exports — not live API
// behaviour, which only a run against the real host can confirm.

import { chromium } from "playwright";
import { fileURLToPath, pathToFileURL } from "node:url";
import { dirname, join } from "node:path";

const PAGE = pathToFileURL(join(dirname(fileURLToPath(import.meta.url)), "rhyming-synonyms.html")).href;

let pass = 0, fail = 0;
function check(name, cond, detail) {
  if (cond) { pass++; console.log("  ok   " + name); }
  else { fail++; console.log("  FAIL " + name + (detail !== undefined ? "  → " + JSON.stringify(detail) : "")); }
}

// Realistic Datamuse entry shapes: tags carry POS, syl:, pron:, f:; defs are "pos\ttext".
const W = (word, score, syl, pos, freq, def) => ({
  word, score, numSyllables: syl,
  tags: [pos, "syl:" + syl, "pron:X", "f:" + freq],
  defs: def ? [pos + "\t" + def] : undefined
});

const browser = await chromium.launch();
const page = await browser.newPage();
page.on("pageerror", e => { fail++; console.log("  FAIL pageerror → " + e.message); });
await page.goto(PAGE);

// Install a stub that answers by constraint param, so the page's real query layer is exercised.
async function stub(spec) {
  await page.evaluate(spec => {
    window.__rhyme.setFetch(async (url) => {
      const u = new URL(url);
      const p = u.searchParams;
      let key;
      if (p.has("rel_syn") && p.has("rel_rhy")) key = "combo";
      else if (p.has("ml") && p.has("rel_rhy")) key = "combo";
      else if (p.has("rel_syn")) key = "syn";
      else if (p.has("ml")) key = "ml";
      else if (p.has("rel_rhy")) key = "rhy";
      else if (p.has("rel_nry")) key = "nry";
      else if (p.has("sp")) key = "source";
      else key = "unknown";
      const word = p.get("rel_syn") || p.get("ml") || p.get("rel_rhy") || p.get("rel_nry") || p.get("sp");
      const table = spec[word] || spec["*"] || {};
      const entry = table[key];
      if (entry === "throw") throw new Error("simulated network failure");
      if (entry === "500") return { ok: false, status: 500, json: async () => [] };
      return { ok: true, status: 200, json: async () => (entry || []) };
    });
  }, spec);
}

async function setFilters(f) {
  await page.evaluate(f => {
    const $ = id => document.getElementById(id);
    if ("dropRoot" in f) $("fRoot").checked = f.dropRoot;
    if ("singleOnly" in f) $("fSingle").checked = f.singleOnly;
    if ("posMatch" in f) $("fPos").checked = f.posMatch;
    if ("meanSrc" in f) $("meansrc").value = f.meanSrc;
    if ("rhymeSrc" in f) $("rhymesrc").value = f.rhymeSrc;
    if ("max" in f) $("maxset").value = String(f.max);
    $("sylMin").value = f.sylMin ?? "";
    $("sylMax").value = f.sylMax ?? "";
    $("minFreq").value = f.minFreq ?? "";
  }, f);
}

const rows = () => page.evaluate(() =>
  [...document.querySelectorAll("#tbody tr")].map(tr => ({
    cls: tr.className,
    cells: [...tr.querySelectorAll("td")].map(td => td.textContent.trim())
  })));
const label = () => page.evaluate(() => ({
  badge: document.querySelector("#labelslot .label-badge")?.textContent || "",
  cls: document.querySelector("#labelslot .label-badge")?.className || "",
  note: document.getElementById("labelnote").textContent,
  status: document.getElementById("status").textContent,
  dot: document.getElementById("dot").className,
  hits: document.getElementById("hitcount").textContent
}));
const words = () => page.evaluate(() =>
  (window.__rhyme.last?.runs || []).flatMap(r => r.hits.map(h => h.word)));

console.log("\n1. pure helpers");
{
  const r = await page.evaluate(() => ({
    root: [
      window.__rhyme.sharesRoot("bemoan", "moan"),
      window.__rhyme.sharesRoot("moaning", "moan"),
      window.__rhyme.sharesRoot("groan", "moan"),
      window.__rhyme.sharesRoot("delight", "light"),
      window.__rhyme.sharesRoot("shiver", "quiver")
    ],
    seeds: window.__rhyme.parseSeeds(" moan, groan\ngleam \n moan ;; "),
    meta: window.__rhyme.meta({
      word: "groan", score: 900, numSyllables: 1,
      tags: ["v", "syl:1", "pron:G R OW N", "f:5.25"], defs: ["v\tto utter a groan"]
    })
  }));
  check("bemoan/moan share a root", r.root[0] === true);
  check("moaning/moan share a root", r.root[1] === true);
  check("groan/moan are independent", r.root[2] === false);
  check("delight/light share a root", r.root[3] === true);
  check("shiver/quiver are independent", r.root[4] === false);
  check("seeds dedupe and normalise", JSON.stringify(r.seeds) === '["moan","groan","gleam"]', r.seeds);
  check("meta parses pos/syl/freq/def", r.meta.pos[0] === "v" && r.meta.syl === 1 &&
    r.meta.freq === 5.25 && r.meta.def === "v · to utter a groan", r.meta);
}

console.log("\n2. self mode intersects the two sets");
await stub({
  moan: {
    syn: [W("groan", 900, 1, "v", "5.25", "to utter a deep sound"), W("lament", 700, 2, "v", "2.10", "express grief")],
    ml:  [W("groan", 880, 1, "v", "5.25"), W("bemoan", 600, 2, "v", "0.40", "regret strongly"),
          W("wail", 500, 1, "v", "1.90"), W("lament", 690, 2, "v", "2.10")],
    // rhy deliberately omits "lament" and includes a word absent from the meaning sets
    rhy: [W("groan", 400, 1, "v", "5.25"), W("bemoan", 380, 2, "v", "0.40"),
          W("cone", 360, 1, "n", "3.00"), W("phone", 350, 1, "n", "40.0")],
    // the server's combined query disagrees: it returns only bemoan
    combo: [W("bemoan", 380, 2, "v", "0.40")]
  }
});
await setFilters({ meanSrc: "both", rhymeSrc: "rhy", dropRoot: false, singleOnly: true, posMatch: false, max: 1000 });
await page.evaluate(() => { document.getElementById("meanword").value = "moan"; window.__rhyme.setMode("self"); });
await page.evaluate(() => window.__rhyme.run());
{
  const w = await words(), l = await label(), rs = await rows();
  check("intersection is exactly {groan, bemoan}", JSON.stringify(w) === '["groan","bemoan"]', w);
  check("non-synonym rhymes (cone, phone) excluded", !w.includes("cone") && !w.includes("phone"));
  check("non-rhyming synonyms (lament, wail) excluded", !w.includes("lament") && !w.includes("wail"));
  check("source word itself excluded", !w.includes("moan"));
  check("groan ranks above bemoan (rel_syn evidence)", w[0] === "groan", w);
  check("groan's server-combo column reads no", rs[0].cells[3] === "no", rs[0].cells);
  check("bemoan's server-combo column reads yes", rs[1].cells[3] === "yes", rs[1].cells);
  check("bemoan flagged as a rich rhyme", rs[1].cells[1].includes("root"), rs[1].cells[1]);
  check("groan carries both rel_syn and ml evidence", rs[0].cells[2].includes("rel_syn") && rs[0].cells[2].includes("ml"), rs[0].cells[2]);
  check("perfect-rhyme tag shown", rs[0].cells[1].includes("perfect"), rs[0].cells[1]);
  check("metadata surfaced (pos/syl/freq)", rs[0].cells[4] === "v" && rs[0].cells[5] === "1" && rs[0].cells[6] === "5.25", rs[0].cells);
  check("definition surfaced", rs[0].cells[8].includes("deep sound"), rs[0].cells[8]);
  check("label is a pass", l.cls.includes("pass") && l.badge.includes("2 confirmed"), l);
  check("status dot ok", l.dot.includes("ok"), l.dot);
}

console.log("\n3. rich-rhyme filter drops the shared root");
await setFilters({ meanSrc: "both", rhymeSrc: "rhy", dropRoot: true, singleOnly: true, posMatch: false, max: 1000 });
await page.evaluate(() => window.__rhyme.run());
{
  const w = await words(), l = await label();
  check("only groan survives", JSON.stringify(w) === '["groan"]', w);
  check("count reflects the filter", l.hits === "1 word", l.hits);
  check("summary reports one filtered out", await page.evaluate(() =>
    [...document.querySelectorAll("#summary dd")].some(d => d.textContent === "1")));
}

console.log("\n4. strict rel_syn only shrinks the meaning set");
await setFilters({ meanSrc: "syn", rhymeSrc: "rhy", dropRoot: false, singleOnly: true, posMatch: false, max: 1000 });
await page.evaluate(() => window.__rhyme.run());
{
  const w = await words();
  check("bemoan gone with ml excluded", JSON.stringify(w) === '["groan"]', w);
  const roles = await page.evaluate(() => window.__rhyme.log.map(e => e.role));
  check("no ml request issued", !roles.includes("ml"), roles);
}

console.log("\n5. syllable, frequency and POS filters");
await stub({
  moan: {
    syn: [W("groan", 900, 1, "v", "5.25"), W("bemoan", 600, 2, "v", "0.40"), W("drone", 500, 1, "n", "1.10")],
    ml: [],
    rhy: [W("groan", 400, 1, "v", "5.25"), W("bemoan", 380, 2, "v", "0.40"), W("drone", 370, 1, "n", "1.10")],
    combo: [],
    source: [{ word: "moan", score: 1, tags: ["v"] }]
  }
});
await setFilters({ meanSrc: "syn", rhymeSrc: "rhy", dropRoot: false, singleOnly: true, posMatch: false, sylMax: 1, max: 1000 });
await page.evaluate(() => window.__rhyme.run());
check("syllable max 1 drops bemoan", JSON.stringify(await words()) === '["groan","drone"]', await words());

await setFilters({ meanSrc: "syn", rhymeSrc: "rhy", dropRoot: false, singleOnly: true, posMatch: false, minFreq: 2, max: 1000 });
await page.evaluate(() => window.__rhyme.run());
check("min freq 2 keeps only groan", JSON.stringify(await words()) === '["groan"]', await words());

await setFilters({ meanSrc: "syn", rhymeSrc: "rhy", dropRoot: false, singleOnly: true, posMatch: true, max: 1000 });
await page.evaluate(() => window.__rhyme.run());
{
  const w = await words();
  check("POS filter drops the noun 'drone' against verb source", !w.includes("drone"), w);
  check("POS filter keeps the verbs", w.includes("groan") && w.includes("bemoan"), w);
  const roles = await page.evaluate(() => window.__rhyme.log.map(e => e.role));
  check("source POS lookup issued only when filter on", roles.filter(r => r === "source").length === 1, roles);
}

console.log("\n6. near rhymes are separable and ranked below perfect");
await stub({
  moan: {
    syn: [W("groan", 900, 1, "v", "5.25"), W("mourn", 800, 1, "v", "1.50")],
    ml: [],
    rhy: [W("groan", 400, 1, "v", "5.25")],
    nry: [W("mourn", 300, 1, "v", "1.50")],
    combo: [W("groan", 400, 1, "v", "5.25")]
  }
});
await setFilters({ meanSrc: "syn", rhymeSrc: "rhy", dropRoot: true, singleOnly: true, posMatch: false, max: 1000 });
await page.evaluate(() => window.__rhyme.run());
check("perfect-only excludes the near rhyme", JSON.stringify(await words()) === '["groan"]', await words());

await setFilters({ meanSrc: "syn", rhymeSrc: "both", dropRoot: true, singleOnly: true, posMatch: false, max: 1000 });
await page.evaluate(() => window.__rhyme.run());
{
  const w = await words(), rs = await rows();
  check("near rhyme included when allowed", JSON.stringify(w) === '["groan","mourn"]', w);
  check("perfect sorts above near", rs[0].cells[1].includes("perfect") && rs[1].cells[1].includes("near"), rs.map(r => r.cells[1]));
}

console.log("\n7. multiword filter");
await stub({
  moan: {
    syn: [W("groan", 900, 1, "v", "5.25"), W("cry out", 800, 2, "v", "1.00")],
    ml: [], rhy: [W("groan", 400, 1, "v", "5.25"), W("cry out", 300, 2, "v", "1.00")], combo: []
  }
});
await setFilters({ meanSrc: "syn", rhymeSrc: "rhy", dropRoot: true, singleOnly: true, posMatch: false, max: 1000 });
await page.evaluate(() => window.__rhyme.run());
check("multiword excluded by default", JSON.stringify(await words()) === '["groan"]', await words());
await setFilters({ meanSrc: "syn", rhymeSrc: "rhy", dropRoot: true, singleOnly: false, posMatch: false, max: 1000 });
await page.evaluate(() => window.__rhyme.run());
check("multiword kept when allowed", (await words()).includes("cry out"), await words());

console.log("\n8. cap detection warns that results are a lower bound");
{
  const many = Array.from({ length: 20 }, (_, i) => W("w" + i, 500 - i, 1, "v", "1.00"));
  await stub({ moan: { syn: many, ml: [], rhy: many, combo: [] } });
  await setFilters({ meanSrc: "syn", rhymeSrc: "rhy", dropRoot: true, singleOnly: true, posMatch: false, max: 20 });
  await page.evaluate(() => window.__rhyme.run());
  const l = await label();
  check("capped sets produce the near label", l.cls.includes("near") && l.badge.includes("capped"), l.badge);
  check("cap note explains the lower bound", l.note.includes("lower bound"), l.note);
  check("requests panel marks the capped sets", await page.evaluate(() =>
    document.querySelectorAll("#reqs li.capped").length >= 2));
}

console.log("\n9. failures are reported, not rendered as zero");
await stub({ moan: { syn: "throw", ml: [], rhy: [W("groan", 400, 1, "v", "5.25")], combo: [] } });
await setFilters({ meanSrc: "syn", rhymeSrc: "rhy", dropRoot: true, singleOnly: true, posMatch: false, max: 1000 });
await page.evaluate(() => window.__rhyme.run());
{
  const l = await label();
  check("network failure yields incomplete label", l.cls.includes("none") && l.badge.includes("Incomplete"), l.badge);
  check("status dot is err", l.dot.includes("err"), l.dot);
  check("failure named in the requests panel", await page.evaluate(() =>
    document.querySelector("#reqs li.failed .count").textContent.includes("network")));
  check("cap note mentions the missing contribution", l.note.includes("not a full answer"), l.note);
}
await stub({ moan: { syn: "500", ml: [], rhy: [], combo: [] } });
await page.evaluate(() => window.__rhyme.run());
check("HTTP 500 surfaced verbatim", await page.evaluate(() =>
  document.querySelector("#reqs li.failed .count").textContent === "HTTP 500"));

console.log("\n10. genuine empty overlap is stated as such");
await stub({ moan: { syn: [W("lament", 700, 2, "v", "2.10")], ml: [], rhy: [W("cone", 300, 1, "n", "3.00")], combo: [] } });
await page.evaluate(() => window.__rhyme.run());
{
  const l = await label(), rs = await rows();
  check("empty overlap labelled distinctly from failure", l.badge === "No rhyming synonyms found", l.badge);
  check("empty table explains itself", rs[0].cells[0].includes("No word satisfied"), rs[0].cells[0]);
  check("note names the widening levers", l.note.includes("ml") && l.note.includes("near rhymes"), l.note);
}

console.log("\n11. scan mode groups by probe word");
await stub({
  moan:   { syn: [W("groan", 900, 1, "v", "5.25")], ml: [], rhy: [W("groan", 400, 1, "v", "5.25")], combo: [W("groan", 400, 1, "v", "5.25")] },
  quiver: { syn: [W("shiver", 850, 2, "v", "3.10")], ml: [], rhy: [W("shiver", 420, 2, "v", "3.10")], combo: [] },
  tidy:   { syn: [W("neat", 800, 1, "adj", "9.00")], ml: [], rhy: [W("untidy", 300, 3, "adj", "0.50")], combo: [] }
});
await page.evaluate(() => {
  window.__rhyme.setMode("scan");
  document.getElementById("seeds").value = "moan\nquiver\ntidy";
  document.getElementById("conc").value = "3";
});
await setFilters({ meanSrc: "syn", rhymeSrc: "rhy", dropRoot: true, singleOnly: true, posMatch: false, max: 1000 });
await page.evaluate(() => window.__rhyme.run());
{
  const rs = await rows(), w = await words();
  check("both hits found across probes", JSON.stringify(w) === '["groan","shiver"]', w);
  check("tidy contributes nothing (no overlap)", !w.includes("neat") && !w.includes("untidy"), w);
  check("group headers present for each hit word", rs.filter(r => r.cls === "grouphead").length === 2, rs.map(r => r.cls));
  check("group header names the probe and count", rs[0].cells[0].includes("moan") && rs[0].cells[0].includes("1 rhyming synonym"), rs[0].cells[0]);
  const l = await label();
  check("summary counts probes with hits", await page.evaluate(() =>
    [...document.querySelectorAll("#summary dd")].some(d => d.textContent === "2 of 3")));
  check("scan label is a pass", l.cls.includes("pass"), l.badge);
  const budget = await page.evaluate(() => document.getElementById("reqbudget").textContent);
  check("request budget shown for the scan", budget.includes("3 per probe × 3"), budget);
  check("request count matches the budget", (await page.evaluate(() => window.__rhyme.log.length)) === 9);
}

console.log("\n12. exports");
{
  const tsv = await page.evaluate(() => window.__rhyme.tableText());
  const wl = await page.evaluate(() => window.__rhyme.wordsText());
  const head = tsv.split("\n")[0].split("\t");
  check("TSV header complete", head.length === 10 && head[0] === "for" && head[9] === "definition", head);
  check("TSV has one row per hit", tsv.trim().split("\n").length === 3, tsv);
  check("word list groups by probe", wl === "moan: groan\nquiver: shiver", wl);
}

await browser.close();
console.log("\n" + pass + " passed, " + fail + " failed\n");
process.exit(fail ? 1 : 0);
