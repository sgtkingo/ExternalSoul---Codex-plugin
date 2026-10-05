---
name: block-notes
description: "ExternalSoul's Block Notes app (`block_note_editor`) — Notion-style rich-text pages in folders, the workspace's knowledge, memory and documentation surface. Use it whenever an agent should read, write, append, search, illustrate or file notes: a research log, a diary, task documentation with images, a skillpack of procedures, a knowledge graph. Read this before driving a notes app from chat/MCP or before a Forge app writes into one."
---

# Block Notes — pages, folders, knowledge

One app instance is a notebook: **pages** (BlockNote rich-text documents) in **folders**. A
page's ADDRESS is its folder path (`2026 / August / 7`); ids are always offered; two pages
may share a bare name in different folders, so a bare name that collides is an explicit
ambiguity, never a silent first match. Agents read and write **Markdown**; the app stores
blocks; the workspace indexes the text for semantic search.

## 1. What you are working with

| Fact | Consequence |
|---|---|
| Address = folder path; `pageId` = the stable key | prefer `pageId` from `list_pages`/search; pass a full path otherwise; never guess a bare name that exists twice |
| Markdown in / Markdown out | headings, lists, tables, code, images `![](url)` round-trip; the editor's own extras (drawing embeds, voice notes) read back as their block type |
| `write_page` REPLACES the page; `append_to_page` adds at the end | for logs and diaries append; for a rewrite read first, then write — a person may have typed since |
| Images are workspace files by id | `insert_image {fileId}` — the `[fileId: <uuid>]` marker every image-producing tool returns; `read_page` returns embedded images WITH their fileIds for attachments-taking tools |
| Two searches | `find_in_pages` = exact text, live, no index (names, numbers, dates); `search_notes` = by meaning over the Spotlight index (parts of long pages match); both take `folder` |
| The whole-page save is one collapsible event; two devices editing one paragraph merge word by word | you can append while a person edits; never write the same paragraph they are typing in |
| A page is also a **Zettelkasten**: folders + links + a knowledge graph | `integrate_idea` files an idea where it belongs and cross-links; `graph_*` tools walk it |
| Crimson **skillpack** folders are agent-readable procedures | `search_skills` / `read_skill` / `save_skill` (workspace-level tools) index them account-wide; write a procedure as a page in a skillpack and every agent can find it |
| `getStateDescription` lists pages by full path (≤ ~500 chars) | for a big notebook: `list_pages` then `read_page`, don't rely on the prologue |

Tools (minted `<verb>_<notebook name>`): `list_pages` → `{path, pageId, preview, images?}`;
`read_page {pageId | tabName}` → full Markdown + `images[{name,url,fileId?}]`; `create_page
{tabName | folder + tabName, markdown?}`; `write_page {tabName, markdown}`; `append_to_page
{tabName, markdown}`; `rename_page`, `delete_page` (refuses the last), `select_page`;
`insert_image {fileId, tabName?, caption?}` (omit `tabName` → the page the person is viewing);
`find_in_pages {query, folder?}`; `search_notes {query, topK?, folder?}`; `highlight {tabName,
text, color?}` + `unhighlight` / `clear_highlights` (switches to the page and scrolls the
passage into view — the "show me" tool); `integrate_idea {idea, targetPage?, createNew?}` →
`revert_integration` / `move_integration` (lossless undo/move by the added block ids);
`graph_overview`, `graph_search`, `graph_neighbors {node, hops}`, `graph_path {a, b}`,
`graph_subgraph {seeds, radius}` (read-only, compact JSON with `pageId`s).

## 2. Recipes

**Task documentation with pictures** (the headline use): do the work → an image tool returns
`[fileId: …]` → `append_to_page {tabName:"Runs / 2026-09-21", markdown:"## Fine-tune a3\n…"}` →
`insert_image {tabName, fileId, caption}`. One page per run, a folder per project.

**A diary / daily log**: `create_page {folder:"2026 / September", tabName:"22", markdown}`;
"what happened in September" = `list_pages` (paths sort) → `read_page` by `pageId`; never
`read_page("22")` bare when months share day names.

**Research notes → knowledge**: `integrate_idea {idea}` for each captured thought (it appends
to the best dossier or makes one, files it, cross-links); later `graph_search {label}` →
`graph_neighbors` → `read_page`. `search_notes` for "what did I think about X".

**Guide a reader**: `find_in_pages {query:"pin_memory"}` → `highlight {tabName, text}`; the
answer is one line ("On screen now"), not directions.

**A procedure every agent should follow**: a page in a skillpack folder, written as steps with
when-to-use in the first paragraph; then `save_skill` / the pack's index makes it findable by
`search_skills`.

## 3. From a Forge app

Declare grants for the base names you use — `"block_note_editor:append_to_page"`,
`"block_note_editor:read_page"`, `"block_note_editor:insert_image"` — and call
`callWorkspaceTool({ appType: "block_note_editor", tool: "append_to_page", args: { tabName, markdown } })`
from an op or a task (through the board's tab in a box; by grant after install). Name the
notebook instance (`targetNodeId`, remembered in your fold) when the workspace has several.
Read a page back with the same door (`read_page`) rather than `readAppState` — the fold holds
blocks, not Markdown. A Forge app that keeps its own notes should use the notebook, not
reinvent one.

## 4. What goes wrong

- A confident wrong page: a bare `tabName` matched the wrong folder. Use `pageId` or the path.
- Content "vanished": `write_page` replaced a page the person was editing. Append, or read then write.
- An image that never shows: you passed a URL, not a `fileId`; or the file is not in this workspace.
- Search finds nothing: `find_in_pages` is literal (case-insensitive, not regex); `search_notes`
  needs the page indexed (a fresh write indexes on edit — try again in a moment).
- A code block missing from a search snippet: fenced code is not indexed as prose; `read_page`
  has it.
