#!/usr/bin/env node
/**
 * film.mjs — record a short, watchable film of a real web page or app, for a website.
 *
 *   node film.mjs login [url]        once: sign in (a real Chrome window, your own profile)
 *   node film.mjs run my-film.mjs    record the film a script describes → out/<name>/
 *
 * What makes it a FILM, not a screen recording:
 *   - sharp frames at real timing (each frame's own timestamp → constant 30 fps);
 *   - a drawn cursor on eased, slightly curved paths, a ring on every click, human typing;
 *   - marks and cuts: a 60 s wait for an agent becomes 3 s of fast-forward.
 *
 * Needs: Node 18+, `npm install` in this folder (puppeteer-core), ffmpeg on PATH, and a Chrome
 * (found automatically; override with CHROME_PATH). The profile lives in ~/.esoul-film/profile
 * — one Chrome per profile: close the login window before recording.
 *
 * A film script:
 *
 *   export const options = { name: "booking", width: 1440, height: 900, dark: false,
 *                            url: "https://externalsoul.com/notebook", webp: 960 };
 *   export default async function film(f) {
 *     await f.rec.start();
 *     await f.clickText("Calendar");                  // move the cursor there and click
 *     await f.hold(800);
 *     await f.click("button[title='New event']");
 *     await f.type("Tasting menu for two");
 *     f.mark("wait");                                   // name a moment…
 *     await f.page.waitForSelector(".event-saved");     // …wait as long as it takes…
 *     f.mark("saved");
 *     await f.hold(1500);
 *     return { cut: [{ to: "wait" }, { from: "wait", to: "saved", speed: 8 }, { from: "saved" }],
 *              posterAt: "saved" };
 *   }
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { pathToFileURL } from "node:url";
import puppeteer from "puppeteer-core";

const PROFILE = process.env.FILM_PROFILE || path.join(os.homedir(), ".esoul-film", "profile");
const OUT = process.env.FILM_OUT || path.resolve("out");
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

export function findChrome() {
  if (process.env.CHROME_PATH && fs.existsSync(process.env.CHROME_PATH)) return process.env.CHROME_PATH;
  const home = os.homedir();
  const candidates = {
    darwin: ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Chromium.app/Contents/MacOS/Chromium", `${home}/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`],
    win32: [`${process.env.PROGRAMFILES}\\Google\\Chrome\\Application\\chrome.exe`, `${process.env["PROGRAMFILES(X86)"]}\\Google\\Chrome\\Application\\chrome.exe`, `${process.env.LOCALAPPDATA}\\Google\\Chrome\\Application\\chrome.exe`],
    linux: ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/usr/bin/chromium", "/usr/bin/chromium-browser", "/snap/bin/chromium"],
  }[process.platform] ?? [];
  const hit = candidates.find((p) => p && fs.existsSync(p));
  if (hit) return hit;
  // Chrome for Testing installed by `npx @puppeteer/browsers install chrome@stable`
  const cft = path.join(home, ".cache", "puppeteer", "chrome");
  if (fs.existsSync(cft)) {
    for (const v of fs.readdirSync(cft).sort().reverse()) {
      for (const bin of ["chrome-linux64/chrome", "chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing", "chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing", "chrome-win64/chrome.exe"]) {
        const p = path.join(cft, v, bin);
        if (fs.existsSync(p)) return p;
      }
    }
  }
  throw new Error("No Chrome found. Install Google Chrome, or run `npx @puppeteer/browsers install chrome@stable`, or set CHROME_PATH.");
}

async function launch({ headed, width, height }) {
  fs.mkdirSync(PROFILE, { recursive: true });
  return puppeteer.launch({
    executablePath: findChrome(),
    headless: !headed,
    userDataDir: PROFILE,
    defaultViewport: headed ? null : { width, height },
    args: ["--no-first-run", "--no-default-browser-check", `--window-size=${width},${height}`],
  });
}

/** The cursor and click ring, drawn into every document before any script runs. */
const CURSOR = `(() => {
  if (window.__filmCursor) return; window.__filmCursor = true;
  const mount = () => {
    if (!document.body) return requestAnimationFrame(mount);
    const c = document.createElement('div');
    c.innerHTML = '<svg width="26" height="26" viewBox="0 0 26 26"><path d="M4 2.5l15.5 11.2-6.9 1.1 4 7.9-3 1.5-4-7.9-5.4 4.5z" fill="#141210" stroke="#FAF6EF" stroke-width="1.4" stroke-linejoin="round"/></svg>';
    Object.assign(c.style, { position: 'fixed', left: '0px', top: '0px', zIndex: 2147483647, pointerEvents: 'none', transform: 'translate(-3px,-2px)', filter: 'drop-shadow(0 2px 3px rgba(0,0,0,.35))', opacity: '0' });
    document.documentElement.appendChild(c);
    window.__filmCursorAt = (x, y) => { c.style.left = x + 'px'; c.style.top = y + 'px'; c.style.opacity = '1'; };
    window.__filmCursorHide = () => { c.style.opacity = '0'; };
    window.__filmRing = (x, y) => {
      const r = document.createElement('div');
      Object.assign(r.style, { position: 'fixed', left: (x - 16) + 'px', top: (y - 16) + 'px', width: '32px', height: '32px', borderRadius: '99px', border: '2px solid ' + (window.__filmAccent || '#D9772A'), zIndex: 2147483646, pointerEvents: 'none', opacity: '0.9', transform: 'scale(.4)', transition: 'transform .45s cubic-bezier(.2,.7,.2,1), opacity .5s ease' });
      document.documentElement.appendChild(r);
      requestAnimationFrame(() => { r.style.transform = 'scale(1.3)'; r.style.opacity = '0'; });
      setTimeout(() => r.remove(), 600);
    };
    document.addEventListener('mousemove', (e) => window.__filmCursorAt(e.clientX, e.clientY), true);
  };
  mount();
})();`;

export async function openFilm({ name, width = 1440, height = 900, dsf = 1, dark = null, url = null, quality = 90, accent = null } = {}) {
  if (!name) throw new Error("options.name is required");
  const dir = path.join(OUT, name);
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(path.join(dir, "frames"), { recursive: true });
  const browser = await launch({ headed: false, width, height });
  const page = await browser.newPage();
  await page.setViewport({ width, height, deviceScaleFactor: dsf });
  if (dark !== null) await page.emulateMediaFeatures([{ name: "prefers-color-scheme", value: dark ? "dark" : "light" }]);
  if (accent) await page.evaluateOnNewDocument((a) => { window.__filmAccent = a; }, accent);
  await page.evaluateOnNewDocument(CURSOR);

  let mouse = { x: width * 0.62, y: height * 0.58 };
  const marks = {};
  const index = [];
  let cdp = null, t0 = 0, n = 0, recording = false;
  const now = () => (index.length ? index[index.length - 1].t : 0);

  const rec = {
    async start() {
      cdp = await page.createCDPSession();
      cdp.on("Page.screencastFrame", (ev) => {
        const ts = ev.metadata?.timestamp ?? Date.now() / 1000;
        if (!t0) t0 = ts;
        const file = String(n++).padStart(6, "0") + ".jpg";
        fs.writeFile(path.join(dir, "frames", file), Buffer.from(ev.data, "base64"), () => {});
        index.push({ t: ts - t0, file });
        cdp.send("Page.screencastFrameAck", { sessionId: ev.sessionId }).catch(() => {});
      });
      await cdp.send("Page.startScreencast", { format: "jpeg", quality, maxWidth: Math.round(width * dsf), maxHeight: Math.round(height * dsf), everyNthFrame: 1 });
      recording = true;
      marks.start = 0;
      await page.mouse.move(mouse.x, mouse.y); // a first frame even on a still page
    },
    async stop() {
      if (!recording) return;
      recording = false;
      await cdp.send("Page.stopScreencast").catch(() => {});
      await sleep(400);
    },
  };

  const f = {
    page, browser, dir, rec, marks,
    async goto(u, { wait = "networkidle2", settle = 1500 } = {}) {
      await page.goto(u, { waitUntil: wait, timeout: 120000 });
      await sleep(settle);
    },
    mark(label) { marks[label] = now(); return marks[label]; },
    hold(ms) { return sleep(ms); },
    async moveTo(target, { ms = 700, dx = 0, dy = 0 } = {}) {
      let x, y;
      if (typeof target === "string") {
        const el = await page.waitForSelector(target, { visible: true, timeout: 30000 });
        const b = await el.boundingBox();
        x = b.x + b.width / 2 + dx; y = b.y + b.height / 2 + dy;
      } else ({ x, y } = target);
      const from = { ...mouse };
      const steps = Math.max(8, Math.round(ms / 16));
      const bend = Math.min(80, Math.hypot(x - from.x, y - from.y) * 0.12); // an arc, not a ruler
      for (let i = 1; i <= steps; i++) {
        const t = ease(i / steps);
        await page.mouse.move(from.x + (x - from.x) * t, from.y + (y - from.y) * t - Math.sin(Math.PI * t) * bend);
        await sleep(ms / steps);
      }
      mouse = { x, y };
      return { x, y };
    },
    /** The on-screen point of visible text (the smallest element whose own text matches). */
    async textPoint(text, { exact = true, within = null } = {}) {
      return page.evaluate(({ text, exact, within }) => {
        const root = within ? document.querySelector(within) : document;
        if (!root) return null;
        const els = [...root.querySelectorAll("*")].filter((e) => {
          const t = (e.innerText || "").trim();
          if (!(exact ? t === text : t.includes(text))) return false;
          const r = e.getBoundingClientRect();
          return r.width > 0 && r.height > 0 && r.bottom > 0 && r.top < window.innerHeight;
        });
        const el = els.sort((a, b) => a.getBoundingClientRect().width * a.getBoundingClientRect().height - b.getBoundingClientRect().width * b.getBoundingClientRect().height)[0];
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return { x: r.x + Math.min(r.width / 2, 60), y: r.y + r.height / 2 };
      }, { text, exact, within });
    },
    async clickText(text, opts = {}) {
      const pt = await f.textPoint(text, opts);
      if (!pt) throw new Error(`text not on screen: ${text}`);
      await f.moveTo(pt, opts);
      await f.click();
    },
    async click(target, opts) {
      if (target) await f.moveTo(target, opts);
      await page.evaluate(({ x, y }) => window.__filmRing?.(x, y), mouse);
      await page.mouse.down(); await sleep(70); await page.mouse.up();
      await sleep(250);
    },
    async drag(target, { dx = 0, dy = 0, ms = 900, ...opts } = {}) {
      const from = await f.moveTo(target, opts);
      await page.mouse.down(); await sleep(120);
      await f.moveTo({ x: from.x + dx, y: from.y + dy }, { ms });
      await sleep(120); await page.mouse.up(); await sleep(250);
    },
    /** Type like a person: jittered rhythm, a breath after punctuation. */
    async type(text, { cps = 16 } = {}) {
      for (const ch of text) {
        await page.keyboard.type(ch);
        const base = 1000 / cps;
        const pause = /[.,:;?!]/.test(ch) ? base * 5 : ch === " " ? base * 1.4 : base;
        await sleep(pause * (0.55 + Math.random() * 0.9));
      }
    },
    /** Ease a scroller (default: the page) so `selector` sits `offset` px below its top. */
    async scrollTo(selector, { scroller = null, offset = 120, ms = 1000 } = {}) {
      await page.evaluate(async ({ selector, scroller, offset, ms }) => {
        const el = document.querySelector(selector); if (!el) return;
        const sc = scroller ? document.querySelector(scroller) : document.scrollingElement;
        const prev = sc.style.scrollBehavior; sc.style.scrollBehavior = "auto";
        const from = sc.scrollTop; const to = from + el.getBoundingClientRect().top - sc.getBoundingClientRect().top - offset; const t0 = performance.now();
        await new Promise((res) => { const step = (t) => { const k = Math.min(1, (t - t0) / ms); const e = k < .5 ? 4*k*k*k : 1 - Math.pow(-2*k+2,3)/2; sc.scrollTop = from + (to - from) * e; k < 1 ? requestAnimationFrame(step) : res(); }; requestAnimationFrame(step); });
        sc.style.scrollBehavior = prev;
      }, { selector, scroller, offset, ms });
    },
    hideCursor() { return page.evaluate(() => window.__filmCursorHide?.()); },
    shot(file) { return page.screenshot({ path: file }); },
  };
  if (url) await f.goto(url);
  return { f, finish: async (spec = {}) => { await rec.stop(); await browser.close().catch(() => {}); return encode({ dir, name, index, marks, ...spec }); }, abort: async () => { await rec.stop().catch(() => {}); await browser.close().catch(() => {}); } };
}

function resolveT(v, marks, end) {
  if (v === undefined || v === null) return end;
  if (typeof v === "number") return v;
  if (v in marks) return marks[v];
  throw new Error(`unknown mark "${v}" (have: ${Object.keys(marks).join(", ")})`);
}

function ffmpeg(args, cwd) {
  const r = spawnSync("ffmpeg", ["-y", "-loglevel", "error", ...args], { cwd, stdio: "inherit" });
  if (r.error) throw new Error("ffmpeg not found on PATH — install it (brew install ffmpeg / apt install ffmpeg / winget install ffmpeg).");
  if (r.status !== 0) throw new Error("ffmpeg failed");
}

/** Frames + timestamps → a constant-rate mp4 (+ poster, + optional animated WebP), with cuts and speed ranges. */
export function encode({ dir, name, index, marks = {}, cut = null, posterAt = null, fps = 30, crf = 22, width = null, webp = null }) {
  if (!index.length) throw new Error("no frames recorded — did the script call f.rec.start()?");
  const end = index[index.length - 1].t + 0.5;
  const ranges = (cut ?? [{ from: 0 }]).map((r) => ({ from: resolveT(r.from ?? 0, marks, end), to: resolveT(r.to, marks, end), speed: r.speed ?? 1 }));
  const out = [];
  let posterFrame = null;
  const posterSrc = posterAt == null ? null : resolveT(posterAt, marks, end);
  for (const r of ranges) {
    for (let t = r.from; t < r.to; t += r.speed / fps) {
      let lo = 0, hi = index.length - 1, k = 0;
      while (lo <= hi) { const m = (lo + hi) >> 1; if (index[m].t <= t) { k = m; lo = m + 1; } else hi = m - 1; }
      out.push(index[k].file);
      if (posterSrc != null && posterFrame == null && t >= posterSrc) posterFrame = index[k].file;
    }
  }
  fs.writeFileSync(path.join(dir, "concat.txt"), out.map((f) => `file 'frames/${f}'\nduration ${(1 / fps).toFixed(5)}`).join("\n") + `\nfile 'frames/${out[out.length - 1]}'\n`);
  const scale = width ? `,scale=${width}:-2:flags=lanczos` : "";
  const mp4 = path.join(dir, `${name}.mp4`);
  ffmpeg(["-f", "concat", "-safe", "0", "-i", "concat.txt", "-vf", `fps=${fps}${scale},format=yuv420p`, "-c:v", "libx264", "-preset", "slow", "-crf", String(crf), "-profile:v", "high", "-movflags", "+faststart", "-an", mp4], dir);
  const poster = path.join(dir, `${name}.jpg`);
  const pf = posterFrame ?? out[Math.min(out.length - 1, Math.floor(out.length * 0.6))];
  ffmpeg(["-i", path.join("frames", pf), ...(width ? ["-vf", `scale=${width}:-2:flags=lanczos`] : []), "-q:v", "3", poster], dir);
  const result = { mp4, poster, seconds: +(out.length / fps).toFixed(1), mb: +(fs.statSync(mp4).size / 1e6).toFixed(2) };
  if (webp) {
    // An animated WebP plays through a plain <img>: autoplay, loop, no controls — the Site app's way to show a film.
    const w = path.join(dir, `${name}.webp`);
    // 12 fps and q 50 keep a 6–8 s film at 800–960 px around 1–2 MB; a web page should not carry more.
    ffmpeg(["-i", mp4, "-vf", `fps=12,scale=${webp}:-2:flags=lanczos`, "-c:v", "libwebp", "-loop", "0", "-q:v", "50", "-compression_level", "6", "-an", w], dir);
    result.webp = w;
    result.webpMb = +(fs.statSync(w).size / 1e6).toFixed(2);
  }
  return result;
}

async function login(url = "https://externalsoul.com/notebook") {
  const browser = await launch({ headed: true, width: 1280, height: 860 });
  const [page] = await browser.pages();
  await page.goto(url).catch(() => {});
  console.log("Sign in in the Chrome window, then close it. The session stays in", PROFILE);
  await new Promise((resolve) => browser.on("disconnected", resolve));
  console.log("Saved. Films now record as you.");
}

async function run(scriptPath) {
  const mod = await import(pathToFileURL(path.resolve(scriptPath)).href);
  if (typeof mod.default !== "function") throw new Error("the film script must `export default async function film(f) { … }`");
  const { f, finish, abort } = await openFilm(mod.options ?? {});
  try {
    const spec = (await mod.default(f)) ?? {};
    const r = await finish({ webp: mod.options?.webp ?? null, width: mod.options?.outWidth ?? null, ...spec });
    console.log(JSON.stringify(r, null, 1));
  } catch (e) {
    await f.shot(path.join(f.dir, "failed.png")).catch(() => {});
    await abort();
    console.error("FAILED:", e.message, "— the last screen is in", path.join(f.dir, "failed.png"));
    process.exit(1);
  }
}

const [cmd, arg] = process.argv.slice(2);
if (import.meta.url === pathToFileURL(process.argv[1] ?? "").href) {
  if (cmd === "login") await login(arg);
  else if (cmd === "run" && arg) await run(arg);
  else console.log("usage: node film.mjs login [url] | node film.mjs run <film-script.mjs>");
}
