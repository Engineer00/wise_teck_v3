// Daily Google Lighthouse check of the live site (run by .github/workflows/lighthouse.yml).
// Every page in the sitemap, on a phone and on a desktop: scores, timings and the main issues.
// Writes reports/*.html (full reports), reports/summary.json and a table for the GitHub run page, then posts
// the summary to <SITE_URL>/api/lighthouse/ when LIGHTHOUSE_TOKEN is set (shown on the admin dashboard).
import fs from "node:fs";
import lighthouse from "lighthouse";
import desktopConfig from "lighthouse/core/config/desktop-config.js";
import * as chromeLauncher from "chrome-launcher";

const SITE = (process.env.SITE_URL || "https://wiseteck.dev").replace(/\/$/, "");
const MAX_PAGES = Number(process.env.MAX_PAGES || 40);
const METRICS = { fcp: "first-contentful-paint", lcp: "largest-contentful-paint", tbt: "total-blocking-time", si: "speed-index", cls: "cumulative-layout-shift" };
const CATS = { performance: "performance", accessibility: "accessibility", best_practices: "best-practices", seo: "seo" };
const SKIP = new Set(Object.values(METRICS).concat(["interactive", "max-potential-fid", "valid-source-maps"]));

const sitemap = await (await fetch(`${SITE}/sitemap.xml`)).text();
const urls = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map(m => m[1].trim()).slice(0, MAX_PAGES);
if (!urls.length) throw new Error(`no pages in ${SITE}/sitemap.xml`);

fs.mkdirSync("reports", { recursive: true });
const chrome = await chromeLauncher.launch({ chromeFlags: ["--headless=new", "--no-sandbox", "--disable-gpu"] });
const results = [];
let version = "";
for (const url of urls) {
  for (const mode of ["mobile", "desktop"]) {
    let lhr, report;
    for (let attempt = 1; attempt <= 3; attempt++) {   // a page load trace is occasionally lost: try again
      const r = await lighthouse(url, { port: chrome.port, output: "html", logLevel: "error" }, mode === "desktop" ? desktopConfig : undefined);
      ({ lhr, report } = r);
      if (!lhr.runtimeError) break;
      console.log(`retry ${attempt}: ${url} ${mode} (${lhr.runtimeError.code})`);
    }
    version = lhr.lighthouseVersion;
    const path = new URL(url).pathname;
    fs.writeFileSync(`reports/${mode}${path.replace(/\/$/, "").replace(/\//g, "_") || "_home"}.html`, report);
    const a = lhr.audits;
    const issues = Object.values(a)
      .filter(x => x.score !== null && x.score < 0.9 && !SKIP.has(x.id) && ["binary", "numeric", "metricSavings"].includes(x.scoreDisplayMode))
      .sort((x, y) => x.score - y.score)
      .slice(0, 10)
      .map(x => ({ id: x.id, title: x.title.replace(/`/g, ""), value: x.displayValue || "" }));
    results.push({
      url: path, mode,
      scores: Object.fromEntries(Object.entries(CATS).map(([k, c]) => [k, lhr.categories[c].score === null ? null : Math.round(lhr.categories[c].score * 100)])),
      metrics: Object.fromEntries(Object.entries(METRICS).map(([k, id]) => [k, typeof a[id].numericValue === "number" ? a[id].numericValue : null])),
      issues,
    });
    console.log(path, mode, JSON.stringify(results.at(-1).scores));
  }
}
await chrome.kill();

const run = process.env.GITHUB_RUN_ID ? `${process.env.GITHUB_SERVER_URL}/${process.env.GITHUB_REPOSITORY}/actions/runs/${process.env.GITHUB_RUN_ID}` : "";
const summary = { ran_at: new Date().toISOString(), version, report_url: run, results };
fs.writeFileSync("reports/summary.json", JSON.stringify(summary, null, 1));

// table on the GitHub run page
if (process.env.GITHUB_STEP_SUMMARY) {
  const cell = v => (v === null ? "–" : v >= 90 ? `🟢 ${v}` : v >= 50 ? `🟠 ${v}` : `🔴 ${v}`);
  const lines = ["| Page | Device | Performance | Accessibility | Best practices | SEO |", "| --- | --- | --- | --- | --- | --- |"];
  for (const r of results) lines.push(`| ${r.url} | ${r.mode} | ${cell(r.scores.performance)} | ${cell(r.scores.accessibility)} | ${cell(r.scores.best_practices)} | ${cell(r.scores.seo)} |`);
  fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, `## Lighthouse · ${SITE}\n\n${lines.join("\n")}\n`);
}

// send to the admin dashboard
if (process.env.LIGHTHOUSE_TOKEN) {
  const res = await fetch(`${SITE}/api/lighthouse/`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${process.env.LIGHTHOUSE_TOKEN}` },
    body: JSON.stringify(summary),
  });
  console.log("sent to the dashboard:", res.status, await res.text());
  if (!res.ok) process.exit(1);
} else {
  console.log("LIGHTHOUSE_TOKEN is not set: results are on this run page only, not on the dashboard");
}
