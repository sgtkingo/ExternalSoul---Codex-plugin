---
name: slideshow
description: "ExternalSoul's Slideshow app (`slideshow`) — a deck where every slide is a live React/TSX component on a fixed 1280×720 canvas, authored by agents, edited by find/replace, and SEEN by a vision critic before it is called done. Use it whenever the user wants slides, a deck, a presentation, a report deck from data or images, or a themed restyle. Read this before adding or editing any slide from chat/MCP or from a Forge app."
---

# Slideshow — slides as code, judged by eye

A slide is TSX declaring `function Component(props) { … }`, compiled server-side when you
add it (an error comes back at once; nothing is created until it compiles), rendered in the
person's frame on a **1280×720 design canvas scaled uniformly** to any container (windowed,
maximised, phone, presentation mode). A deck is a list of named slides; the selected slide's
full source is in the app's state description (2 KB cap), the others as 120-char previews.

## 1. What you are working with

| Fact | Consequence |
|---|---|
| Fixed 1280×720 canvas, uniform scale-to-fit; taller-than-720 shrinks (nothing is clipped, everything gets smaller) | size EVERYTHING in px for that canvas (title 56–80, body 26–36, padding 48–64); never `vw`/`vh`; fit 720 — title in a top block, body in `{flex:1, minHeight:0}`; split rather than cram |
| Bindings inside a slide: `React, useState, useEffect, useRef, useMemo, useCallback, useReducer, useWorkspaceImages(), useWorkspaceFiles()` | no `import`/`export` (not a module); no fetch of the platform, no dispatch; images come from `useWorkspaceImages()` → `[{id,name,url}]` — pick by name |
| Compile check ≠ look check | `critique_slide` renders the slide to an image and a vision model judges overflow, clipping, squished pills, overlap, contrast — call it after every add/edit until it passes (≤ ~3 rounds) |
| `apply_slide_edits` is `{find, replace}` pairs: each `find` exactly once, all-or-nothing, CRLF-normalised | quote a unique chunk; on `find-ambiguous` widen it; a full rewrite is `replace_slide_source` |
| Slide code runs in-page (no sandbox) under the viewer's session | a deck on a public share is trusted code — never put secrets or other people's data in a slide; `publicSharing.policy: "never"` by default |
| Presentation mode is a tool too (`set_presentation_mode`) | "present it" = select the first slide, turn it on |
| Python: `client.slideshow.create/open`, `deck.add_slide(name, tsx)`, `add_slide_until_good`, `critique_slide`, `export_html` | the same loop from the SDK; `critique_source(tsx)` judges TSX before it is on any deck |

Tools (minted `<verb>_<deck name>`): `add_slide {slideName, tsxSource?}` (omitted source =
the sample slide, then edit), `apply_slide_edits {slide, edits:[{find,replace}]}`,
`replace_slide_source {slide, tsxSource}`, `critique_slide {slide, intent?}` → `{pass, score,
issues, suggestions}`, `rename_slide`, `delete_slide` (never the last), `select_slide`,
`reorder_slides {orderedSlides: names|ids}`, `set_presentation_mode {enabled}`.

## 2. The authoring loop

1. **Plan on paper**: 5–7 slides, one idea each — a title/result slide with 2–3 tiles, a
   how-it-works rail, one or two chart slides, a why-it-matters row, a closing line. Word
   budget per slide: a title + 2–3 short sections. Real numbers only; ask for what you lack.
2. **Pick a theme** — `reference/themes.md` lists them; `reference/floral-paper.md` / `reference/starry-night.md` are the recipes: `floral-paper` (warm ivory, the
   default for talks), `starry-night` (indigo, gold signal), `ink` (plain navy). Everything
   visual comes from the theme's tokens and recipes; a deck that "came out generic" is one
   where you wrote your own styles.
3. `add_slide` per slide with a 2–3-word name and the TSX. Validate before the call:
   `function Component` present, tags balanced, no `vw/vh`, no `import`, nothing past 720 px,
   a double-quoted string never inside a double-quoted attribute.
4. `critique_slide` on the busiest slide (then the rest); fix with `apply_slide_edits`;
   critique again until `pass`.
5. `select_slide` the first; report the slide names in one line.

**Charts from data**: inline SVG per the theme's recipe; label every axis with its unit; one
caption line. Data comes from a spreadsheet (`read_app_state` / its tools), a training monitor
(`read_series` — thin to ≤ 60 points), or the chat; never invent a number.

**Images**: the person's workspace images via `useWorkspaceImages()` — filter by `name`; upload
first (`upload_file`) if it is not there. A slide is not a picture: prefer `add_slide` over
`generate_image` when asked for "a slide of X".

## 3. From a Forge app

Declare `"slideshow:add_slide"`, `"slideshow:apply_slide_edits"`, `"slideshow:critique_slide"`
(and `select_slide`, `set_presentation_mode` as needed); `callWorkspaceTool({ appType:
"slideshow", tool: "add_slide", args: { slideName, tsxSource } })` from an op or a task. Read
the compile error in `r.text` and fix before the next call; run `critique_slide` and put its
issues in your own journal. A report deck a task writes (a run's results, a week's stats) is a
natural output — one slide per finding, numbers from your own tables, the theme's recipe for
the look. Name the deck instance in your fold; the workspace may hold several.

## 4. What goes wrong

- Text wraps or spills → over the word budget: shorten or split; never shrink below the recipe sizes.
- A compile error → an unclosed tag, a stray `import`, quotes inside quotes; the runtime is the final word.
- `find-not-found` / `find-ambiguous` → re-read the source from the state description (the
  selected slide) and quote a unique chunk; the batch was rejected whole, nothing changed.
- The images are blank → `useWorkspaceImages()` is async on first paint; guard `images.length`.
- Everything looks the same across decks → no theme; read `reference/themes.md` and use a theme's tokens.
