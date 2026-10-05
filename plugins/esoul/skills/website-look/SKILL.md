---
name: website-look
description: "The look of a website — palette, fonts, one accent, a house style for every image (photos, drawn plates, generated stills), and motion that feels alive without hurting. Stage 2 of the website skills (start at `website`). Use when choosing a site's colours and type, making or choosing its images, or deciding how it moves."
---

# One look, held everywhere

Previous stage: `website-story`. Next: `website-films` (optional) → `website-media`.

## 1. Decide four things, write them down, then never improvise

1. **Background, text, accent** — three colours. Use a tested row from the palette table in
   `build-esoul-website` §3, or derive your own and check contrast (text ≥ 4.5:1 on its
   background; the accent is for buttons and small marks only, never body text).
2. **One font pair** — a display face for headings, a text face for body. Warm/crafts:
   editorial serif + clean sans; product/tech: a grotesk + mono for labels.
3. **One image style** — all photos, OR all drawn plates, OR all generated stills in one
   style. Mixing styles is the fastest way to look cheap.
4. **Dark mode or not** — if yes, design it (a night sky, not an inverted page), and check
   both.

## 2. The style string (the trick behind a coherent set)

Write ONE paragraph that describes the style, and append it to every image prompt. The
externalsoul.com plates used:

> Fine-line copperplate etching, engraved technical illustration, sepia-brown ink on warm cream
> paper (#FAF6EF), confident thin linework with delicate crosshatched shading, generous negative
> space, no text, no lettering, exactly one small element tinted muted burnt orange (#B4540A),
> everything else ink on paper, calm and precise.

Photographs get their own string ("Editorial food photography, natural window light, 35mm,
true colours, no text, no logos, no faces"). The subject changes per image; the string never
does. Make 3 variants per image, pick one, and discard the rest honestly — a weak image hurts
more than no image.

## 3. Where images come from

- **The owner's photos** — best, always. Ask for them. Hero ≤ 1920 px wide, 200–300 KB.
- **Drawn plates / SVG** — authored as text, crisp at any size, themable: the no-photo recipe
  and drawn blocks in `build-esoul-website`.
- **Generated stills** — `generate_image {workspace_id, prompt: "<subject>. <style string>",
  aspect_ratio, name, folder: "Site/Images", format: "webp", max_width: 1920}`. Draft with
  `model: "cheapest"`, then the final with the default (best at legible text and at editing a
  `references` photo of the owner's). `media_models` lists what each model is for and costs;
  `dry_run: true` answers the price for free — show it to the owner before a batch.

## 4. Motion

- **Films of the real thing** beat any animation: `website-films`.
- **Moving backgrounds** (a sea, clouds, leaves behind the hero): `generate_video {prompt:
  "<scene>. <style string>. Static camera, slow natural motion, no people, no text",
  duration_seconds: 6–8, loop: true, webp: true, folder: "Site/Films"}` — a durable job: poll
  `generation_status {generation_id, wait_seconds: 50}` until done (1–5 min). `loop` crossfades
  the end into the start; the poster JPEG is always made. Try `model: "cheapest"` first; one
  default clip is about $1 — price it with `dry_run` and ask. Or a calm clip the owner owns.
- **CSS motion** (Forge sites): reveal on scroll, a slow Ken Burns on a still — 400–700 ms,
  eased, never bouncing.
- **Always** honour `prefers-reduced-motion`: films show their poster, reveals appear at once.
  Text never sits on moving pixels without a dark overlay (0.4–0.6).

## 5. Hand-off

A one-screen "look card" in the workspace notes: the three colours with hex, the fonts, the
style string, the list of images with their chosen file names. `website-media` uploads them;
the build reads the card.
