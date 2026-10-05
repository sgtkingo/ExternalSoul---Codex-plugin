---
name: forge-app-builder
description: "Turn an idea into a real ExternalSoul app over MCP — a native app with its own events, UI, agent tools, server ops, durable tasks, tables, realtime, files, other apps and the user's own computer, and the person's accounts at other services (Gmail, Outlook, OneNote, Dropbox, GitHub, Notion — any OAuth or API-key login, the secret never in the app) — built and PROVEN in the user's Forge workbench with tools (look, drive, call its tools, run its tests) before anyone installs it. Use whenever the user says \"make me an app\", \"I want an app that…\", \"build this in the Forge\", asks for a research tool, a store, a dashboard, a labeller, a data pipeline on their machine, an app on their Microsoft / Outlook / OneNote / Google account, or asks to change an app still being built. For a marketing site or homepage use build-esoul-website instead."
---

# Build an ExternalSoul app in the Forge

You are writing a **native app** for a person's ExternalSoul workspace — not a widget, not a
page. It sits beside their spreadsheets and mail, holds its state as typed events on the
shared timeline (scrubbable, replayable), exposes tools that chat, voice, agents and MCP call,
can bring its own server (ops, streaming routes, webhooks), durable background tasks, its own
database tables, realtime channels, the workspace's files and Google Drive, other apps' tools,
and the person's own computer. The Forge gives you a cloud BOX — a plain Node project holding
`esoul-sdk` and the app host from npm, nothing of the platform, nothing the person configures —
with your app at `src/plugins/<id>`; you see it running in the person's frame within seconds,
prove every arm with tools, and install it into their esoul with one call. The platform keeps
every version (the board's SAVED row); the person never touches GitHub.

**You are the only model in this loop.** Nothing writes the app but you. Write as if the person
is reading over your shoulder — they are (the board shows every file, diff, checkpoint and tool
call), and the install page shows them every tool you declared, in your words.

Read `reference/what-you-work-with.md` FIRST — the surfaces you have, what a preview can and
cannot do, every cap, and what things cost. Then `reference/idea-to-app.md` for the flow.
The rest is the contract, read as the app needs it:

| Reference | Read it for |
|---|---|
| `what-you-work-with.md` | the hosted tools, the board tools, the box, the preview's powers and LIMITS, caps, costs, personas |
| `idea-to-app.md` | the interview, the shape decision (fold / tables / machine / external / site), the write order, worked shapes |
| `app-anatomy.md` | the code contract: manifest, schema, events, ops declared once, UI, server, tests |
| `tools-chat-and-voice.md` | how defining tools lets chat, voice, agents and MCP drive the app; honest results; **test tools** |
| `talking-to-other-apps.md` | calling other apps (UI + server), reading them, bindings, events other apps and agents can wake on |
| `computers.md` | parts of the app that run on the person's computers: a SERVICE of its own kept running there (a program), declared commands, agents in a folder — and why only the installed app can reach a computer |
| `my-computer.md` | the older path: driving a paired My Computer app with shell strings (`computer()`) |
| `server-and-tasks.md` | ops, routes (SSE, a token door for machines), webhooks, Inngest tasks and the replay model, realtime |
| `accounts.md` | the person's accounts at other services — Google, Microsoft (Outlook, OneNote), any OAuth 2.0 provider, API keys: declare a slot, call through the platform, what the person sets up once, the Forge limit, `fakeCredentials` |
| `data-people-files.md` | your own tables and rules, roles and access levels, files and Drive (transfers), public viewers, model calls |
| `telling-people-later.md` | notifying a person AFTER the request: a status change, a cadence, a first visit — the recipient table, the task, the email app on the workspace |
| `design-rules.md` | what "native" and "responsive" mean here; the pre-ship checklist |
| `test-and-ship.md` | proving every arm with tools, the problem journal, removing test tools, installing (one call) |

## Where the tools are

Over the hosted connection you have a small set of general tools (`list_workspaces`,
`search_workspace`, `read_app_state`, `get_app_tools`, `call_app_tool`, `create_app`, …;
`what-you-work-with.md` §1 lists them). **The Forge is an app** on the person's workspace (type
`forge`, usually named "Forge"); its workbench tools are minted as `<verb>_<board name>` and
reached like any app's:

```
list_workspaces                                          → find the board's app id
get_app_tools(<board id>)                                → open_workbench_Forge, write_app_file_Forge, …
call_app_tool(<board id>, "open_workbench_Forge", {pluginId, name, description, icon})
```

**Two doors, one handler.** The hosted connection (`/mcp/me`, OAuth, the account OWNER) drives
the board's tools through `call_app_tool` as above. The local `esoul-mcp` server (`pip install
esoul[mcp]`, a Personal Access Token) has the same verbs as `forge_*` tools — `forge_open`,
`forge_write`, `forge_edit`, `forge_test`, `forge_check`, `forge_look`, `forge_drive`, `forge_tool`,
`forge_put_asset`, `forge_commit`, `forge_ship`, `forge_merge`, `forge_close`, … — and, because it
runs on the person's machine, it can read their disk: a film on their laptop reaches the app
through `forge_put_asset(file=…)` and a whole local folder through `forge_sync`. Prefer it when
the person has files to bring; either door is complete for everything else.

Below, board tools are written without the suffix. No board? `create_app(application_type=
"forge", name="Forge")` on the person's workspace — that is the whole setup. **No GitHub, no
keys, no settings**: `open_workbench` needs nothing from the person. Only the **workspace owner**
may author on a board; a collaborator's chat is refused and told so.

## Reading the SDK's own docs

These references are the distilled rules. The SDK — **esoul-sdk on npm,
<https://www.npmjs.com/package/esoul-sdk>** — ships its full CONTRACT as text, and when a reference
and the contract disagree, the contract wins — read it, and say which you used. Whenever you need
more than these references say about ANY part of the SDK, go there.

**In a box, read the INSTALLED version** — it is what this app compiles against.
`read_platform_file {path}` opens (the box holds the npm package, so its docs live under
`node_modules/esoul-sdk/`; the SDK's sources are at `packages/esoul-sdk/src/`):
- `node_modules/esoul-sdk/docs/<nn>-<chapter>.md` — 01 getting-started · 02 manifest · 03 events-and-state ·
  04 tools · 05 ui · 06 server · 07 background-tasks · 08 accounts (connections) · 09 files · 10 testing ·
  11 shipping · 12 rules · 13 people-and-access · 14 database · 15 realtime · 16 bindings ·
  17 editing-and-merging · 18 your-computer · 19 model-calls · 20 a-service-on-your-computer;
- `node_modules/esoul-sdk/api-reference.md` — every export with its signature and doc comment; the
  place to look ONE name up (`search_app_files {scope:"sdk", query:"<name>"}` finds it, and greps
  the SDK's source too);
- `node_modules/esoul-sdk/README.md`, `node_modules/esoul-sdk/llms-full.txt` (the whole contract).

**With no box open**, the published package: [npmjs.com/package/esoul-sdk](https://www.npmjs.com/package/esoul-sdk)
(its README is the overview; its `CHANGELOG.md` says what each version added).
Fetch `https://unpkg.com/esoul-sdk/llms.txt` (the index), then
`https://cdn.jsdelivr.net/npm/esoul-sdk/llms-full.txt` (the whole contract in one file) or one
chapter at `https://unpkg.com/esoul-sdk/docs/<nn>-<chapter>.md`. Published and installed can
differ by a version — for an app that is open in a box, the box's copy is the truth.

## What the SDK gives an app (and where it is explained)

Know these exist before designing — each has a chapter, and the box answers for each (§3 of
`what-you-work-with.md` says what a preview can and cannot do):

| Capability | API | Chapter |
|---|---|---|
| server truth, one declaration | `defineOps` → `handleOp` → `opTool`; `ctx.emit` | 04, 06 |
| events only the server may write | `origin: "server"` on an event definition | 03 |
| durable background work | `tasks`, `kickPluginTask`, `pollTasks`, `ctx.step` | 07 |
| its own tables, per-row rules | `db`, `pluginDb(ctx)`, `sealed` | 14 |
| people, roles, the sign-in wall | `roles`, `ctx.viewer`, `requires: "account"` | 13 |
| realtime to an audience | `channel`, `usePluginRealtime` | 15 |
| the person's account at Google, Microsoft, any OAuth 2.0 provider, or an API key — the secret never in your code | `credentials` slot (`family: google \| oauth2 \| apiKey`), `credentials(ctx).slot(n).fetch`, `useCredential`, `<ConnectAccount/>` (`accounts.md`) | 08 |
| billed model calls | `llm` block, `llm(ctx)` / `ctx.llm` (never a model SDK) | 19 |
| files and Drive, lists of files with progress | `filesForOp`, `files.transfer`, `useTransfer`, `ctx.files` | 09 |
| a question in the platform's questions bell | `questions(ctx).ask / settle` | 06 |
| opened at a place inside the app (tasks pane, chips, recall) | `useAppNav` | 05 |
| another app's tools and state | `workspaceTools` grants, `callWorkspaceTool`, `readAppState` (only inside an op, route, task or webhook; another type needs a grant) | 06 |
| a network run waits for mail | `mailWaitDirective` | 04 |
| a service / commands on the person's computers | `device` block, `devices(ctx)`, `<ConnectComputer/>`, `esoul-device` | 18, 20 |
| images, films, fonts | `put_app_asset`, `assetUrl` | `assets.md` |
| testing worlds | `esoul-sdk/testing`: `memoryDb`, `memoryFiles`, `scriptedModel`, `simGmail`, `fakeCredentials`, `startMockOAuth` | 10 |

Limits to say rather than build around: one credential slot per app; an `oauth2` / `apiKey`
account cannot be connected inside a Forge box (only the installed app reaches a real account —
`accounts.md` §5); a computer connects only to an installed app (`computers.md`).

## Progress from the first minute (the owner's rule, 2026-09-29)

The person must NEVER look at an empty Forge. The moment they ask for an app — before you ask a
question, before `open_workbench` — call **`set_build_plan {pluginId, name, goal, steps}`**: the
goal in their words and 4–10 steps a person understands ("Draw the list screen", "Remember items
after a refresh", "Check it on a phone"), each with an honest `estMin`. The Forge shows it in
place of the preview — a checklist, a progress ring, "about N minutes left" (it learns your pace
from the steps you finish) — and the box's own address shows it too. It is read-only to them;
only you move it:

- `update_build_step {stepId, status:"doing"}` when you start a step (the one in progress
  becomes done), `"done"` the moment it is, `"skipped"` if it proved unnecessary, `detail` for a
  one-line note. Never batch these at the end — the countdown is only honest if it moves.
- Re-plan with `set_build_plan` when the plan changes; finished steps stay at the top.
- `update_build_step {reveal:true}` when the app's first real screen works — then the person
  sees the app. Until then they may "Peek at it now"; a plan that goes quiet for 20 minutes
  steps aside on its own, so never leave one half-moved.
- On later rounds (a change after install), set a short plan again: the person sees what you are
  doing and roughly how long, every time.

## The flow: idea → app (details in `idea-to-app.md`)

1. **Understand** — five questions, one message: who uses it (only them / invited people /
   the public), what it remembers, what must be true *now* (server truth), what runs while
   nobody is looking, what it touches outside (Drive, their computer, an API, another app).
2. **Shape** — decide where each thing lives: shared-and-small → **the fold** (events);
   per-person / unbounded / must-not-scrub → **tables** (`db`); heavy compute → **their
   computer** (a program or commands, `computers.md`); live view → **route**; durable work → **task**. Write the manifest first: it IS
   the design, and the person reads it at install.
3. **Open** the workbench, read the scaffold, then write in this order: `plugin.json` +
   `ops.ts` + `server.ts` in ONE round (a manifest naming ops the server lacks is refused),
   `app.tsx` (events → tools → describer), `ui/`, tests. Every write answers with the
   preview's health and the **⚠ problem paragraph** — fix those before anything else.
4. **Prove with tools** — `look_at_app` (three viewports, as each persona), `drive_app` (a
   flow, reading the page's console), `call_app_tool` on the app's own tools then
   `read_app_state`, `test_app`, `check_app`. Add **test tools** where a probe needs a door
   the product does not have; remove them before shipping (`tools-chat-and-voice.md` §5).
5. **Iterate with the person** — they play with the build in their frame and tell you what is
   wrong; keep rounds small; `look_at_app` after a visual change, a drive after a behaviour
   change. Resolve the journal rows you fixed (`resolve_problem`), honestly.
6. **Install** — `check_app` green (no `skipped`), test tools gone, version bumped, the
   manifest's name / description / icon reading well (the install page shows them and every
   tool's description), then `install_app`. Follow it with `install_app {status:true}` until it
   says **Live** (about seven minutes: checks → tables → the build → registering tasks → theirs).
   Then `create_app(application_type="plugin_<id>", name=…)` puts it on a workspace — its tools
   are live in chat, voice, agents and MCP. No pull request, no review queue, no GitHub.
   **Continuous development**: change the app in the box, then `install_app` again — it UPDATES in
   place (tables grow additively; data stays). The status line says step · time so far · time left.
   An install that stopped half-way is **resumed** (the same Install), a dead one is cleared by
   pressing it again after ~10 min of silence, and someone else's push landing mid-build is waited
   out, never reverted. The app is PRIVATE: it shows in Add an app only for the person who
   installed it; instances in workspaces they share keep working for everyone there. Pick a
   distinctive `pluginId` — an id already used by another person's app is refused.

## The loop, tool by tool

0. `set_build_plan {pluginId, name, goal, steps}` — FIRST, always (above). It works before the
   box exists; the box's opening shows under it as a live line ("Installing the app host…").
1. `open_workbench {pluginId, name, description, icon}` — `pluginId` lower-case with dashes;
   `icon` a lucide name (the tool lists the allowed ones when yours is wrong). The first box
   takes about a minute (npm install); later ones fork a warm base in seconds. Reopening
   resumes; when a newer esoul-sdk is out the answer says so — compatible or breaking — and you
   ASK the person before `update_box` (a breaking one: `update_box` reviews it first; see
   reference/what-you-work-with.md "The box's SDK version"). Answers with what the box can
   do (`tasks, ops, routes, realtime, viewer, db`) — if that line is missing, `close_workbench`
   and open again. Every checkpoint you make is SAVED by
   the platform (the board's Saved row: v12 · 2 min ago); `restore_app` goes back to any of them.
2. `orient_app` (an app you did not write this conversation) or `list_app_files` +
   `read_app_file {pluginId, path, from?, lines?}`. `search_app_files {query, glob?, regex?,
   scope:"app"|"sdk"}` greps the app, or the SDK's source and docs; `read_platform_file` opens
   an allow-listed SDK file when an answer surprises you.
3. `write_app_file {pluginId, path, content}` / `edit_app_file {pluginId, path, edits:[{find,
   replace}]}` (each `find` matches exactly once or nothing is written) / `delete_app_file`.
   Files `.ts .tsx .json .css .md .txt .svg`, ≤ 512 KB each, ≤ 200 per app, paths ≤ 6 deep.
   The answer's `Preview: live (answered 200 in 0.9 s)` means that build is on screen;
   `Preview: DOWN — …` carries the compiler's own lines. Fix it first.
   Images, films, fonts, PDFs are **assets**, not files: `put_app_asset {pluginId, name,
   fileId | contentBase64 | sourceUrl}` (`fileId`: a workspace file, e.g. what `generate_image` /
   `generate_video` made; over esoul-mcp `forge_put_asset(file=…)` for anything on the
   person's disk, up to 64 MB) stores the bytes content-addressed and writes `assets.json` for
   you; the app renders `assetUrl(assets, "hero.mp4")` from `esoul-sdk` — one URL, the same in
   the preview and installed. `assets.md` has the whole contract.
4. `preview_app {pluginId, viewer?}` — starts the dev server (a minute cold, seconds warm) and
   puts the URL on the frame. Every later write hot-reloads.
5. `look_at_app {pluginId, intent, viewer?}` — screenshots desktop-light, desktop-dark,
   phone-light; returns image URLs plus what is on screen, errors, anything clipped. **Open the
   images and judge them.** Leave `critique` off unless you want a second opinion.
6. `drive_app {pluginId, steps, viewer?}` — use it like a person (≤ 40 steps: `{click}`,
   `{type:[selector,text]}`, `{keys:[selector,key,times]}`, `{select:[selector,value]}`,
   `{wait:ms}`, `{say:selector}`) and read what the PAGE said: console errors, throws, failed
   calls, what each `say` read, a final screenshot. A look proves layout; a drive proves health.
   Steps run against the real preview — a click that starts something starts it.
7. `call_app_tool {pluginId, tool, args}` — runs one of the APP's own tools inside the box; the
   events land in the frame. `read_app_state {pluginId}` reads the fold. This is how an agent
   will drive the app after install — drive it that way now. Ops run over the preview's
   in-memory tables (`pluginDb`) with your real rules, and **VIEW AS** (`viewer:` on
   `look_at_app` / `drive_app` / `preview_app`) shows each persona exactly what those rules let
   them see — visitor-b must see nothing of visitor-a's.
8. `test_app` (the app's own jest, seconds) after any change to schema/events/ops;
   `check_app` (registry sync, the import wall, the app's tests + the platform suites, types)
   before "ready". Read every red gate's detail. `skipped` is not a pass.
9. `app_problems` / `resolve_problem {id, note}` — the journal (§ what-you-work-with).
10. `commit_app {message}` at milestones; `app_history`, `diff_app {sha}`, `restore_app {sha}`
    (a restore is itself a checkpoint). `run_in_app {cmd}` runs one shell command in the app's
    directory (≤ 120 s; `npx jest x.test.ts`, `curl` the preview).
11. `install_app {pluginId}` → the install starts (or an UPDATE, when the app is already
    installed); `install_app {pluginId, status:true}` follows it step by step until **Live**, when
    the app is in the person's Add an app. `close_workbench` when done — a running box costs
    money; it idles out after 10 minutes anyway and reopening resumes.

`ship_app` / `merge_app` are the platform owner's, for a box that is a clone of the platform; a
plain box refuses them. `add_forge_task` changes esoul ITSELF and is the platform owner's too —
never the path to an app.

## The non-negotiables (each earned by a real failure — `app-anatomy.md`, `design-rules.md`)

- **Events are the truth.** Processors pure, idempotent, bounded, refusing bad payloads; ids
  and timestamps minted in `dataCreator`; bursts carry a collapse key per entity and field;
  `reconstructStateFromEventLog: true`.
- **Every UI action has a tool twin**, and every tool has a real `onClient` (`= execute`).
  A tool result says what was DONE and refuses what was not.
- **Ops declared once** (`defineOps` → `handleOp` → `opTool`); the op owns the timeline
  (`ctx.emit`); server truth through an op, never a self-fetch of `/api/v1`.
- **The import wall**: server code reaches the platform only through `esoul-sdk/server`;
  `app.tsx` is never `"use client"`; the UI imports only `esoul-sdk/react`.
- **Every task side effect lives in a `step.run`**; never `void` a promise inside a step.
- **Nothing opens by default**: every op, route and task is `write` unless declared; `read`
  means workspace members, `public` means share-link holders; `requires:"account"` is the
  sign-in wall.
- **Different people see different rows** — never one screen for everyone. `roles` are your
  vocabulary, `db.rules` decide per row (`creator`, a role, a scoped role `{role, where}`),
  `sealed` hides a field from everyone but its owner, and a `customer` sees only their own
  rows while `staff` see all and never an address. Proved as five people (`data-people-files.md` §2).
- **Telling someone later is a task plus your own table.** No send primitive exists and a task
  cannot look a person up: capture the address while there IS a viewer, put what the task will
  need on the row it will act on, send through the workspace's email app under a `workspaceTools`
  grant, and record the send as an event (`telling-people-later.md`).
- **A click shows its result at once.** What a person does is an event (`dispatch` — the fold
  shows it now, the platform delivers it durably). Work that needs the server goes through
  `runOptimistic` (`esoul-sdk/react`): apply now, send, and on failure the screen reverts and the
  platform's banner names it with Try again. No spinner-then-result for the person's own action,
  and never a banner of your own (`docs/05-ui.md`).
- **What the assistant changes shows on screen.** Chat, voice, a task or another device can
  change the app while it is open. State re-renders itself; anything read through an op does not.
  Every op-backed view reloads quietly when the fold moves (a `FoldTick` at the root, one effect
  in your op hook — `docs/05-ui.md`). Check it: open the preview, call a write tool from the
  board, and see the view change without a reload.
- **The box's tables are a model of Postgres, not Postgres.** What passes in the box can fail
  installed where the model is kinder: test every list read past one page (> 200 rows) and on
  tied orders, page with `cursor` alone (never `skip` with it), and run every long op (seed,
  import, bulk write) twice in a test — installed it is 10–30× slower and can stop half-way
  (`docs/14-database.md` → Testing).
- **Missing ≠ empty**: `getStateDescription` uses `incompleteStateNotice`.
- **Native and responsive**: root fills the frame, warm-sepia light / translucent dark,
  opaque popovers in dark, tap-to-act, a 390 px phone shot with no horizontal scroll.
- **Never break the box a person is using**: destructive probes on a throwaway app or when the
  board is idle; a reboot is announced first.

## Honest reporting

Never "installing" without `install_app`'s answer, "live" without `install_app {status:true}`
saying so, "installed" without the new app's node id, "works" without the drive that proved it. A red or `skipped` gate is
reported with its name and detail. A preview that will not come up is quoted in the compiler's
words. Say which `workspaceTools` grants, public doors, connections and file sources the app
declares and why — the person reads them at install. When the app needs something the SDK
does not have, say so and ask for it in the SDK; do not reach around the wall.
