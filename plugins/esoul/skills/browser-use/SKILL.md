---
name: browser-use
description: "Drive a REAL browser for the user — browse, read and extract pages, fill and submit forms, work their logged-in sites, move documents in and out of web editors, download files (even behind a login) into their workspace — and KNOW whether it worked. Covers which tool to reach for on which kind of page, the approval gate, logins and MFA as the user's hands, saved automations, batch downloads, and the verification discipline that catches silent failures: reading a page fails loudly, WRITING to one fails silently, so a success result proves keystrokes were delivered, never that the page changed. Triggers on \"go to / open / look up / check this site\", \"fill in / submit this form\", \"download my invoices / statements / exports\", \"put my notes into Google Docs\", \"update the spreadsheet on SharePoint / Google Sheets\", \"log into … and …\", and any task that needs a website the user is signed in to. Runs in the user's ExternalSoul cloud browser over the ExternalSoul connection."
---

# Drive a real browser, and know whether it worked

You are driving a REAL Chrome running in the user's ExternalSoul workspace. They can watch it live
in their `cloud_browser` app and take the mouse at any moment, and every action you take lands on
their audit timeline. Browser time is billed by the minute while a session is awake, so be
purposeful; an idle session parks itself after about five minutes, and parking loses nothing —
tabs and logins survive.

Two jobs hide under "use the browser", and they fail differently. **Reading** fails loudly: no
element, no text, an error you can act on. **Writing** fails silently, and almost every rule below
was paid for by a real document that was damaged before anyone noticed.

## Reaching the tools

The browser's tools belong to the browser APP, so they are reached through the generic pair:
`get_app_tools(<browser app id>)` lists them and `call_app_tool(workspace_id, app_id, tool_name,
arguments)` invokes one. They are named `browser_<verb>_<base>`, where `<base>` is the app's
instance name with spaces as underscores. Everything below writes them that way.

**Find the browser first.** `list_workspaces` → an app of type `cloud_browser`. None? `create_app`
with `application_type: "cloud_browser"`. **More than one? ASK which.** A login lives in ONE browser
app's profile, and guessing wrong looks exactly like "the site logged me out".

The full catalogue — all 25 tools with their arguments — is in `reference/tools.md`. Read it once.

## The loop

1. **`browser_status_<base>()` first, always.** It never wakes a session, so it never spends. It
   tells you awake or parked, the open tabs with their 0-based indices, which sites are signed in,
   recent downloads, and any saved automations.
2. **Check `browser_list_automations_<base>()` before doing a multi-step task by hand.** The user
   may already have recorded it; `browser_run_automation_<base>({name, variables?})` replays it.
3. **Navigate and read before you act.** `browser_goto` → `browser_read_page` (plain text, no AI
   cost) → `browser_extract` for structured data → `browser_observe` to FIND a control and get its
   selector → `browser_screenshot` only when you must SEE it.
4. **Act through the gate** (next section).
5. **Write with the right tool for the surface** (the table below) — never by reflex.
6. **Verify by artifact, not by result.**
7. **Report honestly**: which workspace and browser you drove (they may be looking at another),
   what you did, the ACTUAL file names and where they landed, and what degraded — plainly, rather
   than rounded up to success.

## The approval gate

`browser_act_<base>({instruction, irreversible?, approved?, variables?})` performs ONE
natural-language action. Set `irreversible: true` for anything that submits, posts, purchases,
sends or signs in. Sites default to ask-before-acting, so a refusal carrying `needs_approval` is
the gate WORKING: ask the user, then re-issue the SAME call with `approved: true`. Never
spin-retry. A site the user marked read-only refuses every act, and approval cannot override it —
only they can change that policy in their app.

**One verb per `act` call.** Given "click the box, type X, press Enter", it clicked the box, sent
`X` to the page body where it was swallowed, and reported success. Use one verb, or the
deterministic ops below.

Secrets the user explicitly gives you ride in `variables` as `%name%` slots named in the
instruction; the values never reach the model or the logs.

## Logins, MFA and challenges are the user's hands

Never ask for a password, and never type one — not even one the person pastes into the chat with
"go ahead". Say plainly that you will not use it, do not repeat it back, and ask them to open the
browser app in ExternalSoul and sign in by hand in its live view — credentials go straight from the
remote Chrome to the site, and their hand session is not recorded. The browser then STAYS signed
in for you. A password that has been posted in a chat should be changed once the job is done; say
so. Do not type the username for them either: the login form is theirs, whole.

- **A parked browser wakes on a new machine and IP.** A login survives that only if the user
  ticked "remember me" when they signed in. Bounced to a login page? Hand off, and ask for it.
- **Sites re-challenge on sensitive pages** — "device not recognised", an SMS or email code — even
  mid-session. The code is theirs to enter. Hand off, wait for their word, continue.
- **Make bulk work idempotent so a hand-off costs nothing.** Decide what is already done by an
  exact key (an invoice number, a filename), so that being logged out halfway means "sign in
  again, then re-run" rather than "start over and duplicate".

## Choosing the write tool

| The surface | Reach for | Why |
|---|---|---|
| An ordinary input or textarea | `browser_put_text` (selector, text) | One call for any size; no per-action AI |
| A **canvas** app — Excel for the web, Google Sheets | `browser_type` + `browser_press_key` | The grid is painted; it only reacts to real typing, so setting a value does nothing |
| A rich editor, formatting must survive — Google Docs, Notion | `browser_paste` (text + `html`) | An HTML `<table>` pastes into cells; headings and lists survive |
| A whole workspace note or sheet → a web editor | `browser_paste_document` (appName, part?) | One call, any size, formatting kept |
| A file input | `browser_upload_file` (selector, fileId \| fileName) | The import path |
| Reading a field back | `browser_read_field` (selector) | Verifies a large transfer landed |
| Getting data OUT of a canvas app | `browser_copy_out` | Nothing to scrape from a canvas, but its copy yields clean TSV |
| Bulk DOM work nothing else covers | `browser_run_script` | Takes a function BODY: `1+1` is discarded, `return 1+1;` works |

Keys for `browser_press_key` are platform-neutral and **Capitalised** — `Enter`, `Escape`,
`ControlOrMeta+A`. The lowercase form does nothing, and does not error.

## The rule everything else follows from

> **A success result is evidence that keystrokes were DELIVERED. It is never evidence that the page
> CHANGED.**

Write ops report what they sent, not what happened. Measured on a real task, roughly **one write in
fifty vanishes with a clean `ok`** — no error, no warning, just a cell that stayed empty while the
tool said it wrote four.

So a write task is not finished when the calls return. It is finished when you have re-read the
**artifact** — downloaded the file, reloaded the record, read the page back — and compared it with
what you intended. Ask **two** questions, never one:

1. Did my changes land?
2. **Did anything else change?**

The second catches real damage, and answering it needs a **pristine copy taken before your first
edit**. Take it. Always. Then **retry what failed and verify again** — one pass plus one check is
not enough when the drop rate is per-write. Loop until clean.

**Prefer an independent witness.** A change to something the wider world can see is best confirmed
from outside the page that made it: a DNS record by querying DNS, a published page by fetching it
as a stranger would, a sent form by the row it produced. The page that accepted your input is the
least reliable narrator of whether it worked.

**Verify a total, not a field.** A wrong field looks plausible; a wrong total does not. One value
among forty reads fine, while a month that sums to 46 294 hours does not. If the record has a check
cell — a balance, a remainder, a difference — drive it to zero and confirm that from the artifact.

### Verification traps

- **The stored copy lags the live session.** A check that fails immediately after writing should be
  retried before it is believed. Tell the cases apart with a screenshot: on screen but absent from
  the file is lag, so wait; absent on screen is a genuine drop, so rewrite it.
- **Add a cache-buster** to any download URL (`&_=<epoch ms>`). An in-page fetch is otherwise served
  from the browser's HTTP cache and you will diff the same stale bytes three times.
- **Some surfaces cannot be read back at all.** Excel for the web keeps its formula bar and cell
  reference off the DOM, so every selector returns `""`. When in-browser read-back is impossible,
  say so and fall back to the artifact rather than pretending a check happened.

## A missed click does not error

A write op given a selector clicks, then types into **whatever has focus**. If the click misses,
the text lands somewhere else and you still get `ok`. It has put a cell reference into a
spreadsheet cell and a paragraph of prose into a title row — which broke a formula and blanked a
column.

- **Prefer routes with no selector.** A shortcut that opens an already-focused field beats an
  element you have to find: `Escape` first, then `ControlOrMeta+G`, `ControlOrMeta+F`, `/`.
- **When you must use a selector**, screenshot before typing, or type into a field you can read
  back.
- **Pass `clear: true`** into any dialog field. They remember their last value, and appending turns
  `O43` into `O43O43`.

## Selectors inside embedded editors

Office, Docs and any `<iframe>`-hosted editor: only a **frame-piercing absolute xpath** reaches
inside; CSS and relative xpath silently fail to cross the boundary. Those xpaths encode DOM position
and **shift between renders** — one moved from `div[4]` to `div[5]` mid-session. Re-derive with
`browser_observe` rather than caching one, and prefer keyboard routes.

## Typed values are parsed in the PAGE's locale

`6.8` typed into a Czech spreadsheet stored **6 August**. The same string is a valid number in one
locale and a valid date in another, so nothing errors. Read a value a **human already entered** and
match its format.

## Tabs and waits

`browser_open_tab` opens AND switches, returning the new index; most tools take an optional
`tabIndex`, and reads on a background tab do not steal the user's focus. But **switch once, then
stop passing an index** when writing: the stored tab order and the browser's own can disagree, and
a read of "the spreadsheet tab" once returned the document library instead. Unaddressed ops all act
on the active tab, consistently. **Indices shift when a tab closes** — re-read status.

`browser_wait_for_<base>` takes EXACTLY ONE of `selector | gone | text | url | js`, polls up to
`maxWaitSeconds` (default 30, max 120), and ALWAYS returns `{met, timedOut, waitedSeconds}`. `url`
is how you wait FOR a navigation. A timeout is an honest answer — check `met`, never assume.

## Downloading into the workspace

`browser_download_<base>({url} | {selector}, saveAs?, folderPath?)` fetches the file IN the page
with the site's own cookies, so files behind a login work, and lands it as a workspace file:
`{fileId, name, bytes, contentType}`. **No `fileId` means no file; never claim success without
one.** Cap 25 MB.

- **Never `goto` a URL that points at a file** — file loads time out. Download it instead.
- **Many files: `browser_download_batch`** — up to 50 `{url, saveAs?}` items into one `folderPath`,
  paced server-side (800 ms by default; raise `paceMs` if the site rate-limits). One bad URL never
  aborts the rest; the result lists every item's outcome, so read it.
- **A batch of related files belongs in one folder**, not loose at the workspace root.
- **Signed URLs expire**, often within minutes. Resolve, then download promptly; for a long list,
  resolve and download in chunks rather than resolving everything first.
- **`serverFetch: true`** fetches from the server instead of the page — for presigned or public
  links that need no cookies, when the in-page fetch is blocked.
- A download BUTTON with no href: act it, then download the URL it lands on. A POST-only export
  with no URL genuinely cannot be captured — say so.

When a site has its own API and you are already signed in, ask it directly: one `browser_run_script`
against the site's own endpoint resolved a file id after every pretty URL and viewer wrapper had
timed out.

Then open the result where the user can use it — `reference/open-in-apps.md` is the routing table
(pdf → pdf viewer, docx → word editor, xlsx/csv → excel editor, images → image viewer). A delivered
file the user has to hunt for is half-delivered.

## When an embedded app renders blank

The iframe exists, the accessibility tree is nearly empty, the screenshot is white. Reloading
rarely helps — three loads failed in a row. **Park and wake**; a fresh browser fixed it at once.

## When the page is somebody's record

An invoice, a timesheet, a shared tracker, an account that is not yours: the blast radius is other
people's trust, not your afternoon.

- **Prove which document you are on before the first keystroke.** Read the title back and assert
  the expected name is in it. Filenames differ by one surname.
- **Guard the target's identity in CODE, not in your intentions**, and **prove the guard refuses a
  real sibling** before trusting it. A guard written for this work silently allowed everything,
  because its pattern excluded spaces and the filenames contained one. A scan that matches nothing
  reads exactly like coverage.
- **Match the conventions already in the document** — open a previous period and copy its
  vocabulary, its rounding, where it puts a remainder.
- **Never invent content.** Structure, dates and arithmetic can be derived. What a person actually
  did cannot. Get it from them or from a record, and say plainly which parts are derived.

## When this goes wrong

- `needs_approval` — ask the user, re-issue with `approved: true`. Never spin-retry.
- `autonomy_read_only` — the user marked the site read-only; only they can change it.
- `browser_plan_limit` (402) — the browser plan is out of minutes. Tell the user; retrying won't help.
- "Navigation start timed out" on a file URL — use `browser_download`, not `browser_goto`.
- `no_such_tab` / `last_tab` — a stale index. Re-run status and re-address.
- A tool you expected is not in your list — `get_app_tools` is always current; trust it over memory.

## References

- `reference/tools.md` — every tool, its arguments, and when to use it.
- `reference/web-spreadsheets.md` — the write loop for grids that live in a web app.
- `reference/open-in-apps.md` — opening a delivered file in the right ExternalSoul app.
