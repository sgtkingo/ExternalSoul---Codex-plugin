---
name: website-films
description: "Record short, watchable films of a real product, app or page for a website — a drawn cursor, real timing, cuts that turn a long wait into seconds, a poster frame, and an animated WebP for sites that cannot play video. Ships the recorder (scripts/film.mjs). Stage 3 of the website skills (start at `website`). Use when a site should SHOW the thing working, or when asked for a product film, a demo clip or a hero video."
---

# Films of the real thing

A film of the product doing its job sells harder than any illustration: it is proof. This is
the recorder the films on externalsoul.com were made with. Previous stage: `website-look`;
next: `website-media`.

## 1. Set up (once, on this machine)

```bash
cp -r <this skill>/scripts ~/esoul-films && cd ~/esoul-films && npm install
node film.mjs login        # a Chrome window opens: sign in to ExternalSoul, then close it
```

Needs Node 18+, ffmpeg on PATH (`brew install ffmpeg`, `apt install ffmpeg`, `winget install
ffmpeg`), and Chrome (found automatically; `CHROME_PATH` overrides; or
`npx @puppeteer/browsers install chrome@stable`). The sign-in lives in `~/.esoul-film/profile`;
a film of a PUBLIC page needs no login. Close the login window before recording — one Chrome
per profile.

## 2. Plan the film before recording it

Each film answers ONE question from the story (`website-story`): "can I book a table from my
phone?", "does the agent really answer the mail?". Write it as 3–6 beats, then record:

- **6–12 seconds** on the page, 20–40 s for a docs step. One action per beat.
- **Stage the data first.** Real apps with realistic, fictional content — never the owner's
  private mail, names or numbers. Make a dedicated workspace for the film's set.
- **Start and end still**: hold 1 s at the start, 1.5 s at the end (the poster frame lives
  there), so a loop does not jump.
- **Show the result, cut the wait.** Mark before and after anything slow (an agent run, a
  build) and speed that range 6–10×.
- **Size**: 1440×900 for desktop films; 390×844 with `dsf: 2` for a phone film.

## 3. Write the film script

A film is a small module next to `film.mjs` (full example: `scripts/example-film.mjs`):

```js
export const options = { name: "book-a-table", width: 1440, height: 900, dark: false,
                         url: "https://example.cz", webp: 800 };
export default async function film(f) {
  await f.rec.start();
  await f.hold(1000);
  await f.clickText("Reserve");              // the cursor travels there and clicks
  await f.click("input[name=guests]"); await f.type("2");
  f.mark("wait"); await f.page.waitForSelector(".confirmed"); f.mark("done");
  await f.hold(1500);
  return { cut: [{ to: "wait" }, { from: "wait", to: "done", speed: 8 }, { from: "done" }],
           posterAt: "done" };
}
```

The tools on `f`: `goto(url)`, `clickText(text)`, `click(selector | {x,y})`,
`moveTo(selector | {x,y})`, `type(text)`, `drag(target, {dx,dy})`, `scrollTo(selector)`,
`hold(ms)`, `mark(name)`, `hideCursor()`, `shot(file)`, and `f.page` (puppeteer) for anything
else. Prefer `clickText` with the words a visitor sees over brittle selectors.

## 4. Record, look, redo

```bash
node film.mjs run book-a-table.mjs
```

→ `out/book-a-table/book-a-table.mp4` (H.264, faststart, muted), `.jpg` (the poster),
`.webp` (animated, when `webp` is set). Open the poster and scrub the mp4 before accepting
it: a stray loading spinner, the wrong theme, or private data means record again — it is
cheap. A failed run leaves `failed.png`: the screen at the moment it broke.

## 5. Budgets

| Output | Use | Keep under |
|---|---|---|
| mp4 1440 px, crf 22 | Forge sites (`<video>`) | 4 MB for 10 s |
| animated WebP 800 px, 12 fps | Site app (an Image block) | 2 MB — shorten the film first, then narrow it |
| poster jpg | every film; what shows before play and under reduced motion | 250 KB |

Then: `website-media` puts them on the site. `generate_video` makes atmosphere loops (skies,
water — `website-look` §4); films of the product stay recorded, never generated: a generated
"product film" shows a product that does not exist.
