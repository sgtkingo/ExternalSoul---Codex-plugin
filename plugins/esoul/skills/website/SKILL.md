---
name: website
description: "Make a website on ExternalSoul that people want to stay on — a homepage, a business site, a product site — from the story to the published domain, with real films and a coherent look. The entry point of the website skills; it runs the sequence and hands each stage to its own skill (website-story, website-look, website-films, website-media, website-publish). Use when someone asks to \"make me a website\", \"a homepage\", \"a landing page\", \"a site for my business / product\", or \"a site like externalsoul.com\"."
---

# Make a website on ExternalSoul

This is how externalsoul.com itself was made: a story first, a look that holds, real films of
the real product, media served fast, and a check on every screen before anyone sees it. Each
stage has its own skill; this one keeps the order and decides the path.

## The sequence

| # | Stage | Skill | You leave the stage with |
|---|---|---|---|
| 1 | Story | `website-story` | who it is for, the chapters, every line of copy |
| 2 | Look | `website-look` | palette, fonts, one accent, the image style string, the stills |
| 3 | Films (optional, strong) | `website-films` | short films of the product or place, with posters |
| 4 | Media | `website-media` | every image and film on the platform, named, sized |
| 5 | Build | the path below | the pages, built from the story and the look |
| 6 | Check + publish | `website-publish` | phone + desktop, light + dark, SEO text, live on the domain |

Do the stages in order. A site built before its story is a template with words poured in;
media made before the look never match each other.

## Choose the path (ask once, then commit)

**Site app — the default.** Blocks the owner edits in place afterwards, forms, bookings, a
store, server-rendered and fast; self-serve, live in minutes. Build it with the block manual
in `build-esoul-website` (tools, block vocabulary, tested palettes, section rhythm). Films go
in as animated WebP images (`website-media`).

**Forge app — full control.** Custom code, any layout, native `<video>`, scroll-driven
motion, several views (a docs page). What externalsoul.com is. It ships as a pull request the
platform owner approves, so it takes longer to go live. Build it with `forge-app-builder`;
media go in as app assets (`website-media`).

Pick the Site app unless the owner asks for something blocks cannot do (native video, custom
interaction, a layout the vocabulary lacks) or already has a Forge board.

## Tools you have (the hosted MCP)

`list_workspaces`, `list_project_tree`, `create_workspace`, `create_app`, `get_app_tools`,
`call_app_tool`, `read_app_state`, `upload_file`, `list_files`, `view_image`,
`media_models`, `generate_image`, `generate_video`, `generation_status`, `publish_homepage`. A site's own tools (`replace_page_<site>`, `screenshot_page_<site>`,
`critique_page_<site>`, …) and a Forge board's (`put_app_asset_<board>`, `look_at_app_<board>`,
…) are reached with `call_app_tool` after `get_app_tools`. Films are recorded on THIS machine
by the recorder bundled in `website-films` (Node + Chrome + ffmpeg).

**Generated images and clips** land in the workspace's files (`website-look` says what to ask
for, `website-media` how to place them). They spend the owner's credits: show the price first
(`dry_run: true` answers it for free) and draft with `model: "cheapest"`.

## Rules that hold across every stage

- The owner's words, the audience's language (a Czech site is Czech everywhere, including
  buttons and empty states). Never invent a phone number, address, price or quote — ask.
- One accent, one font pair, one image style. Consistency reads as quality.
- Every page is looked at on a phone before it is called done (`website-publish`).
- Publishing is the last action and the owner's to approve.
