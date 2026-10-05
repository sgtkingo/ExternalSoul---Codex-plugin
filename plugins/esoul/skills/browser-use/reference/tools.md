# The cloud browser's tools

All 25, grouped by the job they do. Every name is `browser_<verb>_<base>` — `<base>` is the browser
app's instance name with spaces as underscores — and every one is called through
`call_app_tool(workspace_id, app_id, tool_name, arguments)`. `get_app_tools(app_id)` is always the
authority: if this page and that listing ever disagree, the listing is right.

Most tools accept an optional `tabIndex` (0-based, from `browser_status`). A READ on a background
tab does not steal the user's focus. For WRITES, switch once and then stop passing an index — see
"Tabs and waits" in the skill.

## Orient

| Tool | Arguments | Notes |
|---|---|---|
| `browser_status` | — | **Call first, always.** Never wakes a session, so it costs nothing. Awake or parked, open tabs with indices, signed-in sites, recent downloads, saved automations |
| `browser_list_automations` | — | Recorded task sequences replayable by name. Check before doing a multi-step task by hand |

## Navigate

| Tool | Arguments | Notes |
|---|---|---|
| `browser_goto` | `url`, `tabIndex?` | Wakes the browser if parked. **Never a file URL** — those time out; download instead |
| `browser_open_tab` | `url?` | Opens AND switches; returns the new index. Hold a source page open while working in another |
| `browser_switch_tab` | `tabIndex` | Subsequent unaddressed calls act on this tab |
| `browser_close_tab` | `tabIndex` | Refuses the last tab. **Indices above the closed tab shift down** — re-read status |
| `browser_wait_for` | exactly ONE of `selector` \| `gone` \| `text` \| `url` \| `js`; `maxWaitSeconds?` | Default 30, max 120. ALWAYS returns `{met, timedOut, waitedSeconds}` — check `met`. `url` waits FOR a navigation |

## Read

| Tool | Arguments | Notes |
|---|---|---|
| `browser_read_page` | `tabIndex?` | The page as plain text, no AI cost. Read before you act |
| `browser_extract` | `instruction`, `tabIndex?` | Structured data in natural language: "the top 5 results: title, price" |
| `browser_observe` | `instruction?`, `tabIndex?` | The actionable things on the page WITH selectors. FIND before acting |
| `browser_screenshot` | `tabIndex?` | Saves a workspace file and returns its `fileId`. Use when you must SEE the page |
| `browser_read_field` | `selector`, `tabIndex?` | The full text of one field or element. The way to verify a large transfer landed |
| `browser_copy_out` | `selector?`, `selectAll?` (default true) | Copy OUT of the page. A canvas app has nothing to scrape, but its copy yields clean TSV |

## Act

| Tool | Arguments | Notes |
|---|---|---|
| `browser_act` | `instruction`, `irreversible?`, `approved?`, `variables?`, `tabIndex?` | ONE natural-language action, **one verb per call**. `irreversible: true` for anything that submits, posts, buys, sends or signs in. `needs_approval` → ask the user, re-issue with `approved: true`. Secrets ride in `variables` as `%name%` slots |
| `browser_type` | `text`, `selector?`, `enter?`, `clear?`, `tabIndex?` | Real keystrokes into whatever has focus. **The tool for canvas apps** (Excel for the web, Google Sheets). `clear: true` for any field that remembers its last value |
| `browser_press_key` | `key` or `keys[]`, `selector?`, `tabIndex?` | Platform-neutral and **Capitalised**: `Enter`, `Tab`, `Escape`, `ArrowDown`, `ControlOrMeta+A`. Lowercase does nothing and does not error |
| `browser_put_text` | `selector`, `text`, `tabIndex?` | A LARGE amount of text into an ordinary field in one call. Not for canvas apps or rich editors |
| `browser_paste` | `text`, `html?`, `selector?`, `tabIndex?` | Into the focused rich editor, keeping formatting. An HTML `<table>` fills spreadsheet cells |
| `browser_paste_document` | `appName?` or `appId?`, `part?`, `selector?`, `tabIndex?` | A workspace note or sheet into whatever is open, formatting kept. `part` = page name or sheet name. Open the target and click into its body first |
| `browser_upload_file` | `selector` (the file input), `fileId?` or `fileName?`, `tabIndex?` | A workspace file into a site's upload box |
| `browser_run_script` | `expression`, `arg?`, `tabIndex?` | JavaScript in the page, result returned as JSON. **A function BODY**: `1+1` is evaluated and discarded, `return 1+1;` works |

## Download

| Tool | Arguments | Notes |
|---|---|---|
| `browser_download` | `url?` or `selector?`, `saveAs?`, `folderPath?`, `serverFetch?`, `tabIndex?` | Fetches IN the page with the site's cookies, so files behind a login work. Returns `{fileId, name, bytes, contentType}`. **No `fileId`, no file.** Cap 25 MB |
| `browser_download_batch` | `items[]` of `{url, saveAs?}` (1–50), `folderPath?`, `serverFetch?`, `paceMs?`, `tabIndex?` | Paced server-side (default 800 ms, max 5000). One bad URL never aborts the rest; the result lists every item's outcome |

`serverFetch: true` fetches from the server rather than the page — for presigned or public URLs
that need no login cookies, when the in-page fetch is blocked.

Enumerate download links deterministically rather than by eye:

```
browser_run_script({expression:
  "return [...document.querySelectorAll('a[href]')].map(a => a.href)" +
  ".filter(h => /\\.(pdf|csv|xlsx|zip)([?#]|$)/i.test(h))"})
```

## Automations

| Tool | Arguments | Notes |
|---|---|---|
| `browser_record` | `action` (`"start"` \| `"stop"`), `name?`, `description?` | While recording, every navigation and action becomes a replayable step; stopping saves it |
| `browser_run_automation` | `name`, `variables?` | Replays by name. Steps are re-checked against the site's autonomy policy as they run. `browser_list_automations` shows each one's required variables |

When you finish a multi-step task the user is likely to want again, offer to record it.

## Verifying what you did

`read_app_state(<browser app id>)` returns the authoritative fold: the session, the tabs, the
action log — every goto, act and download you performed — and the downloads. Verify from state,
never from a bare success response.
