---
name: website-media
description: "Put a website's images, films, posters and fonts on ExternalSoul so they load fast everywhere — workspace files for a Site-app site, app assets for a Forge site — with the right formats, sizes and names. Stage 4 of the website skills (start at `website`). Use when uploading media for a site, wiring a film or image into a page, or when a site loads slowly because of its media."
---

# Media on the site

Previous stages: `website-look` (stills), `website-films` (films). Next: build the pages,
then `website-publish`.

## 1. Prepare every file first

| Kind | Format | Size |
|---|---|---|
| Hero photo | WebP or JPEG, ≤ 1920 px wide | 200–300 KB |
| Section photo / plate | WebP, ≤ 1200 px | ≤ 150 KB |
| Drawn illustration | SVG (authored as text) | small |
| Film (Forge) | mp4 H.264 + poster jpg | ≤ 4 MB / 10 s |
| Film (Site app) | animated WebP + poster jpg | ≤ 2 MB |
| Font (Forge) | woff2 | — |

Name files for what they show, lowercase, no spaces: `hero-cafe.webp`, `film-booking.mp4`,
`film-booking.jpg`. A film and its poster share a name. Convert with ffmpeg
(`ffmpeg -i in.png -q:v 80 out.webp`) before uploading — never upload a 5 MB PNG hero.

## 2. Get the bytes onto the platform

The MCP carries text, not megabytes: base64 written by a model drifts above ~20 KB. So:

- **Small files you authored** (an SVG, a tiny PNG): `upload_file(workspace_id, name,
  content_base64, mime_type, sha256)`.
- **Anything already public** (a photo on the owner's old site): `upload_file(workspace_id,
  name, source_url)`.
- **Files on this machine** (films, photos): ask the owner to drop them into the workspace's
  **Files** (the Explorer → Files, drag and drop). Then `list_files(workspace_id)` — each file
  comes back with its name and its public URL.

## 3. Site app: reference by file name

Image props take a workspace file name or its URL: `{"url": "hero-cafe.webp", "alt": "…"}`.
A film is an `Image` block with the animated WebP (it autoplays and loops); put the poster jpg
as the section's `background` behind it if the page shows before the WebP loads. The site app
has no native video; YouTube/Vimeo go in an `Embed` block. Block details: `build-esoul-website`.

## 4. Forge app: app assets

App assets are content-addressed and served immutable at `/pa/<app>/<hash>.<ext>` — the same
URL in the preview, installed, and on a custom domain, cached forever.

- `call_app_tool(board, "put_app_asset_<board>", {pluginId, name, fileId})` with the file's id
  from `list_files` (or a generation's `file.id`); or `sourceUrl` (a public URL, ≤ 64 MB), or
  `contentBase64` for a small file (≤ 3 MB).
- In the app: `import assets from "./assets.json"` and `assetUrl(assets, "film-booking.mp4")`
  from esoul-sdk. The platform writes `assets.json`; never edit it by hand.
- A film: `<video src=… poster=… muted playsInline loop autoPlay preload="metadata">`; play
  it when it scrolls into view, pause when it leaves; show only the poster under
  `prefers-reduced-motion`.
- Build details: `forge-app-builder` (its `reference/assets.md`).

## 5. Check the weight

Open the published page's network panel (or `screenshot_page_<site>` for a Site app and a
look at the files list): the first screen should load under ~1.5 MB. Films below the fold load
lazily; heavier than budget → shorten, narrow, or cut to a poster with a play button.

## 6. Generated media

`generate_image` / `generate_video` write straight to the workspace's files: pass `name` and
`folder` so they land named as §1 asks, `format: "webp"` + `max_width` for stills. A clip comes
with its poster (`<name>.jpg`) and, with `webp: true`, the animated WebP. Then §3 or §4 as for
any file — a Forge app takes each by id: `put_app_asset_<board> {pluginId, name, fileId}`.
