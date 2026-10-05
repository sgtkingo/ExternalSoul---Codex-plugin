---
name: website-publish
description: "Check a website on every screen and publish it — phone and desktop, light and dark, contrast, overflow, weight, reduced motion (scripts/check.mjs), a vision critique, the text search engines and link previews show, then the homepage and the custom domain. Stage 6 of the website skills (start at `website`). Use before calling any site done, when publishing a homepage, setting its title/description/preview image, or linking a domain."
---

# Check, then publish

Previous stages: `website-story` → `website-look` → `website-films` → `website-media` → the
build. This is the last one; nothing goes public before it passes.

## 1. Look at it the way visitors will

**Every page, on a phone and a desktop, in light and dark.** Screenshots are for YOU to look
at, not for a tool to approve:

- Site app: `call_app_tool(ws, site, "screenshot_page_<site>", {page, viewport: "phone"})`,
  then `"desktop"`; `view_image` each. Then `critique_page_<site>` `{page, viewport, intent}`
  for each viewport: fix every issue it names, re-run until it passes (score ≥ 0.85).
- Forge app: `call_app_tool(board, "look_at_app_<board>", {pluginId, intent})` — desktop
  light, desktop dark, phone; open every image.
- Any published URL (both paths): the bundled checker, on this machine —

```bash
cp -r <this skill>/scripts ~/esoul-check && cd ~/esoul-check && npm install
node check.mjs https://your-site.example
```

It screenshots phone and desktop in both themes, lists text under WCAG AA contrast (4.5:1;
3:1 for large text), catches a page wider than the screen, measures first-load weight on the
wire, and checks that films pause under reduced motion. It cannot judge text on photos and
films — look at those yourself; they need a 0.4–0.6 dark overlay.

## 2. What "done" looks like

- Nothing clipped, overlapping or scrolling sideways on a 390 px phone.
- Every heading on at most two lines on a phone; no orphan word on its own line in a hero.
- Contrast clean in both themes; buttons read as buttons.
- Films start with a real frame (the poster), not a spinner; reduced motion shows posters.
- First load ≲ 1.5 MB; everything below the fold lazy.
- No lorem, no `[brackets]`, no invented facts; the audience's language everywhere.
- Every button goes somewhere real; forms deliver (send one test submission).

## 3. The text the world sees

- **Page title** ≤ 60 characters: the name and what it is ("Linden Café — breakfast in
  Vinohrady").
- **Description** ≤ 155 characters: who it is for and the one action.
- **Preview image** 1200×630, the hero's best frame or plate, with the name legible.

Set them with `publish_homepage(… , seo_title, seo_description, seo_image_url)` (the image can
be an https URL or an app asset path). For a Site app also set the business record
(`set_business_<site>`: name, address, hours, phone) — it becomes structured data on every page.

## 4. Publish — the owner's call

Ask the owner before this step; it is public at once.

- Site app: `set_publish_mode_<site>` `{mode: "site"}`, then
  `publish_homepage(workspace_id, front_app_id: <site>, app_ids: [<site>], publish_mode: "site")`.
- Forge app: it is live on the owner's approval of the pull request and the deploy; then
  `publish_homepage` with the app as `front_app_id`.

The homepage is `externalsoul.com/u/<handle>`. A custom domain is linked in the Explorer:
the workspace's ⋯ → *Make homepage* panel → domain; the DNS record it shows goes to the
domain's registrar. Sign-in on a custom domain bounces through externalsoul.com and back.

## 5. Verify like a visitor

Open the public URL in a clean browser (or re-run `check.mjs` on it): the homepage, the domain,
a phone. Share a link in a chat app to see the preview card. A green tool result is not
publication; the public page is.
