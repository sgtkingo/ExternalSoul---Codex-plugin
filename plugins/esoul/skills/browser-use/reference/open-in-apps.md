# Open a workspace file in the right ExternalSoul app

> The routing table: which app type renders which file kind, and the exact per-instance opener
> tool. Everything here is driven with `get_app_tools(app_id)` + `call_app_tool(app_id,
> tool_name, arguments)` — tool names carry the app's instance name (`<verb>_<base>`, spaces as
> underscores).

## The rule

End file-producing work by loading the file into its viewer/editor app and telling the user
where it is — by workspace, app instance name, and the file's ACTUAL name. Load CONTENT into
apps; never try to force the user's screen to it — they tap the app themselves.

## Getting the app

Reuse an existing app of the right type FIRST — opening a document REPLACES what the app shows,
which is what you want: one viewer that always holds the current version, not a new app per
file. Only if none exists: `create_app` / `app_create` with the application_type below, then
`get_app_tools` on the new app id.

## Prefer ids over names

Every opener takes a `workspaceFileId` (from a download result or a sandbox save's
`[fileId: …]` marker). Pass the id — ids are exact; names collide and get auto-suffixed.

## The table

**PDF (.pdf)** → application_type `pdf_viewer`
`call_app_tool(viewer, "open_document_pdf_reader_<base>", {workspaceFileId})`
Navigation/highlights within it: `open_reference_pdf_reader_<base>`.

**Word documents (.docx family)** → application_type `word_editor`
`call_app_tool(editor, "open_document_<base>", {workspaceFileId | fileName})`
The editor starts EMPTY and its other tools refuse until a document is open; afterwards
`read_document_<base>` / `replace_text_<base>` / `append_text_<base>` act on it.

**Spreadsheets (.xlsx/.xls/.csv)** → application_type `excel_editor`
`call_app_tool(editor, "open_workbook_<base>", {workspaceFileId | fileName})`
CAUTION: this REPLACES whatever the editor currently holds — if the user is mid-work in it,
create a second editor instead of clobbering theirs.

**Images (.png/.jpg/.webp…)** → application_type `image_viewer`
Workspace images appear in the viewer's gallery as soon as they exist — nothing to call for
delivery. `call_app_tool(viewer, "show_image_<base>", {imageName?})` additionally returns the
image so YOU can look at it — use that to verify pixels, not just deliver them.

**Video / audio (.mp4/.mp3/.wav…)** → application_type `video_editor`, ONLY when the user wants
to edit or assemble. `add_clips_<base>` places workspace media on the timeline by fileId. For a
plain "here's your video", the workspace files panel is the delivery surface — name the file.

**Everything else (.zip, code, unknown)** → the workspace files panel is the home. Say the exact
file name. If its CONTENT matters, the code sandbox can read or convert it.

## When this goes wrong

- The opener refuses / "nothing opened": wrong id, or the file kind doesn't match the app (a CSV
  won't open in the pdf_viewer) — re-check against the table.
- Two files share a name: you passed `fileName` — pass the `workspaceFileId`.
- The user doesn't see it: name the workspace AND the app instance; never force-focus.
