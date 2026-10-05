# Tools — how defining them lets chat, voice, agents and MCP drive the app

A tool is the app's verb for a model. The platform mints your `toolkitCreator` per instance as
`<verb>_<instance name>` (spaces and punctuation → underscores) and offers those tools, with
your `getStateDescription`, to **every surface at once**:

| Surface | What runs | What the person experiences |
|---|---|---|
| typed chat in the workspace | `execute` on the server | "pin a note saying milk" → the note appears in the frame |
| WebRTC voice / sideband voice | `onClient` in the browser | says it, sees it; the same event |
| agent-builder networks, triggers, chat waits | `execute` | an agent acts on the app while nobody watches |
| MCP (`get_app_tools` → `call_app_tool` on the instance), the SDK, a storefront | `execute` | a Claude elsewhere drives it; `publicSafe` tools also for strangers |
| WebMCP (a browser-side agent in the person's tab) | `onClient` | the tab does the work |
| other apps' server code (`callWorkspaceTool`) | `execute` | apps compose |

Nothing else is needed for this: **defining a tool IS wiring the app into chat and voice.** The
only work is making the tool honest and the describer true.

## 1. The three kinds of tool

- **An event tool** changes the fold: mint the id, `eventCallback(dataCreator(...))`, return what
  happened with the id. `execute` and `onClient` are the same function.
- **An op tool** needs server truth or the app's tables: `opTool(ops, "<op>", { pluginId,
  nodeId, description, readOnly?, publicSafe?, say(result, input), then?(result, input) })`. Its
  parameters ARE the op's declared input; `onClient` is set for you. The op owns the timeline
  (`ctx.emit`); the tool never also dispatches the event.
- **A task tool** starts durable work: `kickPluginTask({ applicationType, taskName, identifier,
  data })` for a task listed in `kickableTasks`; return the run id and where its status will
  appear (a `status_` tool, the fold).

## 2. Naming and describing — for a model, not a person

- Verbs lower-case with underscores, one action each: `pin_note`, `set_note_text`,
  `start_training`, `training_status`. Never the op's hyphenated name; never the board's suffix.
- The description says what it does, **what it returns, and where its ids come from**
  ("Returns the note's id, which `set_note_text` takes"; "ids come from `read_notes`").
- Parameters: `.describe()` each; enums over free strings; sensible defaults named in the text.
- `readOnly: true` on reads (a read-scoped token may call them); `publicSafe: true` only when
  the tool writes nothing and leaks nothing.

## 3. Honest results — the model believes you

A tool result is what the model will tell the person. Return what you **did**; refuse what you
could not: `No note n9 on this wall — nothing changed. Ids come from read_notes.` — not
"updated". When server truth is unavailable, say so ("could not verify here"). Name the next
step. Never return an empty string (voice reports it as success), never base64 (it prints as
text — a picture is a URL), never a whole log (keep answers short; the model reads them every
turn).

**"Show me" means the SCREEN.** When a tool's job is to present something, the APP shows it
(switch page, scroll, highlight briefly) by dispatching a view event, and the answer is one
line: "On screen now." Never numbered instructions on where to click. The person owns focus —
background runs (tasks, triggers, other agents) write state, never navigation; only a tool
called from the foreground chat/voice may bring a view up.

## 4. `getStateDescription` — what the agent sees every turn

Compact, truthful, with ids, in the app's voice: `## Sticky notes — "Kitchen"` then the ten
newest notes with `id:` markers and a line naming the tools. Never a dump of the state. Never a
count or an emptiness you could not read — `incompleteStateNotice({ title, instanceName, shape:
{ lists: { notes: state?.notes } } })` first; a MISSING collection means the state did not load,
`[]` is real. This text is also what voice carries in its small prompt budget: keep it under
~500 characters when the app is idle.

## 5. Test tools — probes you add, prove with, and REMOVE

The workbench drives the app through its tools (`call_app_tool`) and reads the fold
(`read_app_state`). Sometimes a probe needs a door the product should not have: reset the fold,
seed twenty rows, force a task's failure branch, read a table the UI never shows. Give it one —
and take it away before shipping:

- Name them `__test_<what>` (tools) / `"__test-<what>"` (ops). The prefix is the promise.
- Gate them at the seam too: an op `{ "access": "write" }` and a first line
  `if (ctx.viewer.kind !== "owner" && ctx.viewer.kind !== "internal") throw new Refusal("forbidden", "test door")`.
- Use them from `call_app_tool` to set up a state, then drive the REAL tools and the UI against
  it; read the result with the real read tool and `read_app_state`.
- Before `install_app`: `search_app_files {query:"__test"}` must find nothing in `app.tsx`,
  `ops.ts`, `server.ts` or `plugin.json`. Keep the assertions in `<id>.test.ts` (which may call
  the product's ops directly with `runOp`), not the doors. `check_app` after the removal.

What is NOT a test tool: a real `reset_` or `import_` the person asked for — that ships, with
its access declared and a confirm in the UI.

## 6. Making the app reachable from a chat that never saw it

After install the chat sees `getStateDescription` and the tools of the apps in the workspace. In
a large workspace tools load lazily: an agent finds the app with `search_workspace` /
`list_apps`, reads it with `read_app_state`, then `get_tools` — so the describer's first line and
the manifest `description` are your search results. Write them as such.

## 7. Checking it works, before install

```
call_app_tool  {pluginId, tool:"pin_note",  args:{text:"milk"}}     → "Pinned note n1."
read_app_state {pluginId}                                             → notes:[{id:"n1",…}]
call_app_tool  {pluginId, tool:"read_notes", args:{}}                 → the op answered from the preview's fold
call_app_tool  {pluginId, tool:"pin_note",  args:{text:""}}          → a refusal in words, not a throw (check the ⚠ paragraph: no bug row)
```

Then the same as the person would: `drive_app` types the note and presses Enter; `look_at_app`
shows it. Voice cannot be driven from a box — `onClient = execute` and a real return value are
what make it safe there.
