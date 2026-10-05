#!/usr/bin/env node
/**
 * check.mjs — look at a website the way its visitors will, before anyone else does.
 *
 *   node check.mjs https://example.cz [--out checks]
 *
 * For phone (390×844) and desktop (1440×900), light and dark:
 *   - a full-page screenshot  → <out>/<viewport>-<theme>.png
 *   - text contrast: every visible text element whose colour against its nearest solid
 *     background is under WCAG AA (4.5:1, or 3:1 for large text) — text on images is
 *     skipped and must be judged by eye on the screenshots;
 *   - horizontal overflow (a page wider than the screen);
 * plus, on desktop light:
 *   - first-load weight (everything transferred before the page settled);
 *   - a reduced-motion screenshot (films should show posters, nothing should be mid-animation).
 * Exits 1 when anything fails, with the reasons in <out>/report.json.
 *
 * Needs: Node 18+, `npm install` in this folder (puppeteer-core), a Chrome (CHROME_PATH or found).
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import puppeteer from "puppeteer-core";

function findChrome() {
  if (process.env.CHROME_PATH && fs.existsSync(process.env.CHROME_PATH)) return process.env.CHROME_PATH;
  const home = os.homedir();
  const c = {
    darwin: ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Chromium.app/Contents/MacOS/Chromium"],
    win32: [`${process.env.PROGRAMFILES}\\Google\\Chrome\\Application\\chrome.exe`, `${process.env.LOCALAPPDATA}\\Google\\Chrome\\Application\\chrome.exe`],
    linux: ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/usr/bin/chromium", "/usr/bin/chromium-browser", "/snap/bin/chromium"],
  }[process.platform] ?? [];
  const hit = c.find((p) => p && fs.existsSync(p));
  if (hit) return hit;
  const cft = path.join(home, ".cache", "puppeteer", "chrome");
  if (fs.existsSync(cft)) for (const v of fs.readdirSync(cft).sort().reverse()) for (const b of ["chrome-linux64/chrome", "chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing", "chrome-win64/chrome.exe"]) { const p = path.join(cft, v, b); if (fs.existsSync(p)) return p; }
  throw new Error("No Chrome found. Install Chrome or set CHROME_PATH.");
}

const url = process.argv[2];
if (!url) { console.log("usage: node check.mjs <url> [--out dir]"); process.exit(2); }
const oi = process.argv.indexOf("--out");
const out = path.resolve(oi > 0 ? process.argv[oi + 1] : "checks");
fs.mkdirSync(out, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** In the page: failing text contrast + horizontal overflow. */
function audit() {
  const parse = (c) => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const [r, g, b, a = 1] = m[1].split(/[ ,/]+/).filter(Boolean).map(Number); return { r, g, b, a }; };
  const lum = ({ r, g, b }) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
  const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
  const bgOf = (el) => {
    for (let e = el; e; e = e.parentElement) {
      const s = getComputedStyle(e);
      if (s.backgroundImage && s.backgroundImage !== "none") return null; // text on an image or gradient: judge by eye
      const c = parse(s.backgroundColor);
      if (c && c.a >= 0.9) return c;
    }
    return parse(getComputedStyle(document.body).backgroundColor) ?? { r: 255, g: 255, b: 255, a: 1 };
  };
  const failing = [];
  const seen = new Set();
  for (const el of document.querySelectorAll("body *")) {
    const own = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim().length > 1);
    if (!own) continue;
    const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    if (!r.width || !r.height || s.visibility === "hidden" || Number(s.opacity) < 0.3) continue;
    if (el.closest("video, picture, svg, [aria-hidden=true]")) continue;
    const fg = parse(s.color); const bg = bgOf(el);
    if (!fg || !bg) continue;
    const size = parseFloat(s.fontSize); const bold = Number(s.fontWeight) >= 700;
    const need = size >= 24 || (bold && size >= 18.66) ? 3 : 4.5;
    const got = ratio(fg, bg);
    const text = el.textContent.trim().slice(0, 50);
    if (got < need && !seen.has(text)) { seen.add(text); failing.push({ text, ratio: +got.toFixed(2), need, color: s.color, background: `rgb(${bg.r},${bg.g},${bg.b})` }); }
  }
  const overflow = document.documentElement.scrollWidth > window.innerWidth + 1;
  return { failing: failing.slice(0, 25), overflow, scrollWidth: document.documentElement.scrollWidth, width: window.innerWidth };
}

const browser = await puppeteer.launch({ executablePath: findChrome(), headless: true });
const report = { url, at: new Date().toISOString(), views: [], problems: [] };
try {
  for (const vp of [{ name: "phone", width: 390, height: 844, dsf: 2, mobile: true }, { name: "desktop", width: 1440, height: 900, dsf: 1, mobile: false }]) {
    for (const theme of ["light", "dark"]) {
      const page = await browser.newPage();
      await page.setViewport({ width: vp.width, height: vp.height, deviceScaleFactor: vp.dsf, isMobile: vp.mobile, hasTouch: vp.mobile });
      await page.emulateMediaFeatures([{ name: "prefers-color-scheme", value: theme }]);
      // Bytes ON THE WIRE (compressed), from the network layer — not decoded bodies.
      let bytes = 0;
      const cdp = await page.createCDPSession();
      await cdp.send("Network.enable");
      cdp.on("Network.loadingFinished", (e) => { bytes += e.encodedDataLength || 0; });
      await page.goto(url, { waitUntil: "networkidle2", timeout: 90000 });
      await sleep(1500);
      const file = path.join(out, `${vp.name}-${theme}.png`);
      await page.screenshot({ path: file, fullPage: true });
      const a = await page.evaluate(audit);
      const view = { view: `${vp.name}-${theme}`, screenshot: file, contrastFailures: a.failing, overflow: a.overflow };
      if (vp.name === "desktop" && theme === "light") view.firstLoadMB = +(bytes / 1e6).toFixed(2);
      report.views.push(view);
      if (a.failing.length) report.problems.push(`${view.view}: ${a.failing.length} text(s) under AA contrast — first: "${a.failing[0].text}" ${a.failing[0].ratio}:1`);
      if (a.overflow) report.problems.push(`${view.view}: the page is ${a.scrollWidth}px wide on a ${a.width}px screen (horizontal scroll)`);
      if (view.firstLoadMB > 3) report.problems.push(`desktop: ${view.firstLoadMB} MB transferred on first load (aim for under ~1.5 MB above the fold)`);
      await page.close();
    }
  }
  const rm = await browser.newPage();
  await rm.setViewport({ width: 1440, height: 900 });
  await rm.emulateMediaFeatures([{ name: "prefers-reduced-motion", value: "reduce" }]);
  await rm.goto(url, { waitUntil: "networkidle2", timeout: 90000 });
  await sleep(1500);
  await rm.screenshot({ path: path.join(out, "reduced-motion.png") });
  const playing = await rm.evaluate(() => [...document.querySelectorAll("video")].filter((v) => !v.paused).length);
  if (playing) report.problems.push(`reduced motion: ${playing} video(s) still playing — show the poster instead`);
  report.views.push({ view: "reduced-motion", screenshot: path.join(out, "reduced-motion.png"), videosPlaying: playing });
} finally {
  await browser.close();
}
fs.writeFileSync(path.join(out, "report.json"), JSON.stringify(report, null, 1));
console.log(report.problems.length ? `${report.problems.length} problem(s):\n- ` + report.problems.join("\n- ") : "No problems found by the checks. Now LOOK at every screenshot.");
console.log(`Screenshots and report: ${out}`);
process.exit(report.problems.length ? 1 : 0);
