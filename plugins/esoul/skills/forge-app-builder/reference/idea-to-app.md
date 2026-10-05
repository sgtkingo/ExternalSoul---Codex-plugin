# From an idea in someone's head to an installed app

The person has a picture; you have the platform. This is the path between them, in the order
that does not waste their box minutes.

## 1. The interview — one message, five questions

Ask all five at once, with your best guess filled in so they can just correct it:

1. **Who uses it?** Only you · people you invite (editing / read-only) · anyone with a link ·
   customers who sign in · agents. → roles, access levels, `publicSharing`.
2. **What must it remember?** The things the workspace should hold and show on any device, and
   what a person could scrub back through. → the fold (events).
3. **What must be true right now?** Counts, stock, orders, a queue — things two people must not
   both read stale. → tables (`db`) behind ops.
4. **What runs while nobody is looking?** A sync, a poll, a wait for a reply, a long job. → a
   task; or their computer.
5. **What does it touch outside the workspace?** Their Drive, their computer, an API with a
   login, another app on the workspace, a machine that phones home. → files, a program or
   commands on their computer (`computers.md`), their account at Google, Microsoft or any
   OAuth / API-key service (a `credentials` slot — `accounts.md`), `workspaceTools`/bindings, a
   `token` route.

Then say the app back in five lines — what it stores, who sees what, what an agent can ask it
to do, what runs in the background, what it needs granted — and start. Do not build an app you
cannot describe in five lines.

## 2. The shape decision — where each thing lives

| The thing | Lives in | Because |
|---|---|---|
| shared, small, worth scrubbing (a board's cards, a folder choice, settings, run records) | **the fold** — events with pure processors | any device, any agent, any moment in time sees the same state |
| per-person, unbounded, must never revert on a scrub (orders, tickets, readings, customer profiles) | **tables** (`db`) with rules, behind ops | scoped and rule-checked by the platform; a scrub of the timeline leaves records alone |
| must be true now for a decision (stock, availability) | an **op** over tables, one refusal in one place | two folds can be read in the same instant; one op cannot oversell |
| a live view (a clock, a stream) | a **route** (SSE) | milliseconds; dies with the request |
| durable work (a sync, a wait for a reply, a job that must finish) | a **task** on Inngest | survives everything; seconds per hop |
| a service that keeps running on their machine, heavy compute, GPUs, local data, a repo | **their computer**: the app's own **program** (`device.program`) or declared **commands** (`computers.md`) | it is their hardware; the app orchestrates and remembers; only the installed app reaches a computer |
| pictures, datasets | **files** (workspace + Drive) | one consented surface; grants for machines |
| the person's account at a service — Google, Microsoft (Outlook, OneNote), Dropbox, GitHub, Notion… | a **credential slot** (`credentials`, family `google`, `oauth2` or `apiKey` — `accounts.md`) | the platform holds the token or key, refreshes it, and sends it only to the hosts the person approved; the app never sees it; a real account only in the installed app |
| another app's capability | `workspaceTools` (a grant) or a **binding** (`uses`/`provides`) | the person consents; the other app keeps its own refusals |
| a marketing site / homepage | the **site app** (skill `build-esoul-website`), not a Forge app | already built, published to their handle |

Two rules that decide most arguments: **if two people can read it in the same instant and both
act on it, it is a table with an op, not the fold**; **if a person should be able to scrub back
and see it as it was, it is the fold**.

## 3. Manifest first — the design is a JSON file

Write `plugin.json` before any code; it is what the person reads at install and what the
platform mounts. Name every door it opens:

```json
{
  "manifestVersion": 1, "id": "field-lab", "name": "Field lab", "version": "0.1.0",
  "description": "…one honest paragraph…", "applicationType": "plugin_field_lab", "entry": "app", "icon": "FlaskConical",
  "roles":  { "vocabulary": ["operator", "observer"], "default": { "owner": "operator", "member-edit": "operator", "member-readonly": "observer", "visitor": "observer", "anonymous": "none", "agent": "inherit" } },
  "ops":    { "read-plan": { "access": "read" }, "start-run": {}, "poll-run": { "access": "read" } },
  "routes": { "ingest": { "access": "token" } },
  "kickableTasks": { "watch-run": {} },
  "db":     { "Run": { "fields": { "status": "string=queued", "verdict": "string?" }, "indexes": [["status"], ["createdAt"]] } },
  "workspaceTools": ["my_computer:computer_status", "my_computer:run_on_computer", "my_computer:get_computer_result", "my_computer:claude_task"],
  "fileSources": { "workspace": "read", "providers": ["google-drive"], "write": ["google-drive"] }
}
```

Field-by-field rules: `app-anatomy.md` §1 and `data-people-files.md`. Nothing undeclared runs;
nothing declared is free — say why each line is there.

## 4. The write order (one box, no wasted probes)

Every `write_app_file` is a checkpoint and a health probe (~25 s). Group the files of one
concern into one round and write them in this order:

1. **`plugin.json` + `ops.ts` + `server.ts`** — together (the box re-registers on either the
   manifest or the server; a manifest naming an op the server lacks is refused).
2. **`app.tsx`** — the schema: state, events (`dataCreator` mints; processors fold), tools
   (`opTool` for anything an op answers; event tools for the fold), `getStateDescription`.
3. **`ui/<id>-ui.tsx`** and its parts — `"use client"`; props are `{ state }`; writes through
   `usePluginEventDispatch`; reads of server truth through `callPluginOp`.
4. **`<id>.test.ts`** — the fold contract, the ops with `memoryDb`/`fakeViewer`/`runOp`, the
   task with a fake ctx, the machine mocked.
5. `preview_app` → `look_at_app` → `drive_app` → `call_app_tool` → `test_app` → `check_app`.

Read the ⚠ paragraph on every answer. A `Preview: DOWN` is the compiler talking — fix that before
writing the next file.

## 5. Worked shapes

**A research app** (a brief → a pipeline on the person's machine → results in the workspace). *If what the person wants is to optimise their own training or benchmark code — the best config, ablations, "which knob matters" — do not build an app: that is the built-in research study, and the `research-study` skill drives it.* For a genuinely new research tool:
fold = the brief, chosen folders, the machine, run records (queued/running/verdict); tables =
none until results are per-person; server = ops `plan` (validates inputs, names what is
excluded and why) / `start` (installs a small stdlib helper on the machine, starts the job
DETACHED, returns a run id) / `poll` (the helper composes a ≤ 6 KB summary on the machine —
never a raw log); a task `watch-run` polls every 30 s with `step.run` and dispatches the verdict
event; UI = a drawer with the steps as buttons with state and a header that says "● Running…
stage · step · min" until a poll finds the process gone; tools = `plan_`, `start_`, `status_`.
Machine facts are in `my-computer.md`. A NEW research tool that lives on a computer is better as
a device program (next shape) than a helper driven through My Computer.

**A service on their computer** (a local model server, a sampler, a bridge to a device). fold =
the chosen computer (`linkId`), settings, run/answer records; server = ops `ask` (→
`devices(ctx).program(linkId).send("ask", …)`, ≤ 55 s, ≤ 1 MB), `report` (only the program —
checks `ctx.viewer.device`; idempotent by `requestId`), `computers` (`devices(ctx).list()` → who is
online, the program's phase and words); `device.program` with setup steps (venv, deps), a
self-test and `"resident": true`; `device/main.ts` starts the service, `p.on("ask")` fetches its
localhost, long work answers `accepted` then `p.op("report")`; UI = `<ConnectComputer/>` + a
computer picker. Build the program and the ops with fakes in the box (a box cannot reach a
computer), install, then the person connects. The whole contract: `computers.md`, SDK `docs/20`.

**A shop / e-store**: tables = `Product` (indexes `contains` on tags, `text` on title), `Order` +
`OrderLine` (price at the time), `Customer` (sealed contact fields, `owner: "creator"`); roles
`guest / customer / staff`; public ops `browse` (`access: "public"`), `place-order` (`public` +
`requires: "account"`), staff ops for stock; `db.$transaction` for order + basket; a stock ledger
in ANOTHER app reached by a binding, with hold → write → release-on-failure; realtime
`role:staff` "new order", `viewer` "your order shipped"; `generateAppImage` behind an owner-only
op; the fold holds only the shop's settings and the catalogue-changed nudge (`ctx.emit`).

**A dashboard over a machine's data**: a `token` route the machine pushes buckets to (a bridge
script the app installs with `computer()`), a `Sample` table, rules in `detectors.ts` judged per
bucket, `chartSvg` on screen + `renderChartImage` in the tool's answer, a `viewer`-audience
channel for "your device alerted", `scope: "user"` tables for per-person cursors.

**A labeller over Drive images**: fold = remembered folders (`{sourceId, ref, path}` — the REF,
so a rename does not lose the place), last image per folder, settings; ops = `folder-index`
(ONE `listAll` + `pairImagesWithLabels`), `load-labels`, `save-labels` (a stale check against
the label's `modifiedAt`); UI = `useFolderAutocomplete` + `useFileUrls` (Drive thumbnails at
320 px) + `ImageLabeler`; every write proven on a scratch folder only.

**A website**: not a Forge app — `build-esoul-website`. A Forge app CAN appear on a public share
(`publicSharing` with a `redactState` that is the only wall) and its `publicSafe` tools on a
storefront; design for the reader who is not the owner.

## 6. When to stop and ask

- The person's five answers contradict the shape (they want customers AND no sign-in AND
  private orders) — say what cannot hold and offer the two honest versions.
- The app needs something the SDK does not expose (a platform internal, a raw database, a
  cron finer than 5 minutes) — name it, propose the SDK addition, do not reach around the wall.
- A write would touch their real data (Drive, a machine, credits) — name the scratch target
  and get the nod first.
