# Talking to other apps on the workspace

An app is an island until it can use the others. Five doors, each with its own consent; all of
them stay inside the app's own workspace.

| Door | Direction | Consent | From |
|---|---|---|---|
| `workspaceTools` grant → call another app's TOOL | you → them | the manifest lists `"<applicationType>:<tool base>"`; the person reads it at install | UI `useWorkspaceTools`, server `callWorkspaceTool`, `computer()` |
| `readAppState(nodeId)` | you read them | your own type freely; another type needs a `workspaceTools` grant for it | server, only inside an op / route / task / webhook |
| `emitPluginAppEvent` | you write their fold | same workspace; their processors decide | server |
| bindings `uses` / `provides` | a SLOT the owner fills | the owner binds one app to another; a contract, not a toolkit | server `ctx.apps.<slot>` |
| `triggerMeta` on your events | they (and agents) wake on you | the event is declared wake-able | agent-builder Trigger node, chat `wait_for_workspace_event` |

## 1. Calling another app's tools

The grant is the tool's BASE name (before the instance suffix): a spreadsheet minted as
`add_row_Leads` is granted as `"spreadsheet:add_row"`. Find base names with `get_app_tools` on an
instance of that type and strip the suffix.

From the UI:
```ts
const { call, listApps, available } = useWorkspaceTools(state);   // state carries workspaceId + nodeId
const apps = await listApps();                                     // [{ nodeId, instanceName, applicationType }]
const r = await call({ appType: "spreadsheet", tool: "add_row", args: { cells: { When: new Date().toISOString(), Note: text } } });
// or name one instance: call({ targetNodeId, tool, args })         → { ok, text }
```
From server code (an op, a task):
```ts
const r = await callWorkspaceTool({ pluginId: PLUGIN_ID, nodeId: ctx.nodeId, appType: "calendar", tool: "add_event", args: { … } });
if (!r.ok) throw new Refusal("calendar", r.text);                  // relay the other app's refusal in its words
```
A workspace may hold several instances of a type — **name the one you mean** (`targetNodeId`,
remembered in your fold or a one-row table), never "the first". In a box these calls travel
through the board's open tab; headless you get "no board is connected to this preview" — unit-test
with the call mocked, drive for real with the preview open on the board or after install.

## 2. Reading another app

`readAppState(nodeId)` → `{ nodeId, workspaceId, applicationType, foldedSeq, state }` or `null`.
It reads for the call the platform is running: your own app type in your workspace; another type
only when the manifest grants one of its tools (`"spreadsheet:add_row"` covers reading a
spreadsheet) — refused, naming the grant to add, otherwise; `null` for an app in another workspace
(the same answer as one that does not exist); a webhook sees only its own type; outside an op,
route, task or webhook it throws. The box applies the same rule. It is the canonical fold at head — never a raw database read (the wall refuses `prisma`; the
state column lags the log). Read what you need and stop: folding a big app is a paged rebuild.
For built-in apps the state shape is that app's; read it once with the hosted `read_app_state`
to learn it before writing code against it.

## 3. Writing into another app

`emitPluginAppEvent({ source: { pluginId, workspaceId, nodeId, applicationType }, targetNodeId,
eventName, eventData })` appends one of THEIR events (their `dataCreator` shape — mint the ids
they expect), actor-stamped as your plugin. Their processors validate; a payload they refuse is a
silent no-op, so read back with `readAppState` when it matters. Prefer their TOOL when one
exists (it validates and answers in words); emit only for mirroring into a native app whose
processors you cannot call.

## 4. Bindings — leaning on another app by contract

When your app needs a capability, not a particular instance ("use MY room list"):

```json
// consumer                                              // provider
"uses": { "rooms": { "contract": "rooms/v1", "label": "Rooms", "optional": true } }
"provides": { "rooms/v1": { "tools": ["hold_room", "release_room"], "events": ["room_freed"], "models": ["Room"] } }
```
```ts
export const bindingSetEvent = defineBindingEvent<BookingData>({ applicationType: APP_TYPE, slots: ["rooms"] }); // in `events` — the owner's choice is on YOUR timeline
const rooms = ctx.apps?.rooms;                    // absent when nothing is bound
if (rooms) { const held = await rooms.call("hold_room", { roomId, from, to }); if (!held.ok) throw new Refusal("rooms", held.text); }
```
Checked at BIND time, loudly: contract name, version (a `v2` provider fills a `v1` slot, never
the reverse), and that the provider really mints those tools / declares those events / generates
those tables. A slot reaches the CONTRACT's tools only. The caller travels (a visitor through
your app is a visitor in theirs). Writes never cross directly — the provider's own ops are the
only writers of its tables, which is how a stock ledger keeps refusing to oversell whoever asks.
Hold → write → **release on failure** yourself; a transaction cannot hold another app's write.

## 5. Letting agents and other apps wake on YOUR events

```ts
triggerMeta: { displayName: "Run finished", description: "A training run reached a verdict", sampleVariables: ["runId", "verdict"] }
```
An event with `triggerMeta` becomes a wake-able event: an agent-builder **Trigger node** can start
a network on it, a chat can park on it with `wait_for_workspace_event` (`list_waitable_events`
shows it — an event without `triggerMeta` is undiscoverable). Declare it on the events that mean
something happened (`order_placed`, `run_finished`), not on bursts. Your own tasks may also wake
on events (`ctx.step.waitForEvent`, `server-and-tasks.md`).

## 6. Asking the person, and being opened at the right place

- **A question the person must answer** (an agent waiting on a decision) goes to the platform's
  questions bell, on every workspace: `questions(ctx).ask({ key, question, options?, open?,
  answer: { op, args } })` from server code. Answering in the bell calls YOUR `answer.op` with
  `{ ...args, answer }` as the person who answered, through the op's own access rules; reply
  `{ ok: false, error }` when the question is gone and the bell closes it with your words. When
  your own screen took the answer, `questions(ctx).settle(key, { answer })`. One question per
  `key` — a replayed ask is the same one. In a box there is no bell (`{created:false}`).
- **Opened from outside**: the tasks pane, a chip in a spreadsheet, a recall hit or the bell's
  Open button name a place in your app (`{ thread: id }`, `{ campaign: id }`); hear it with
  `useAppNav(nodeId, (target) => …)` from `esoul-sdk/react` and go there (`docs/05`).
- **A network waiting for mail** in your inbox-like app: a tool that, inside an agent network run
  (`runCtx` present), emits `mailWaitDirective(runCtx, {...})` parks the run on the platform's wait
  kernel (`docs/04`); your app must announce arrivals as `workspace/email.message_arrived` for it
  to wake (the platform does it for the Gmail app).

## 7. The apps with their own skill

Before calling a built-in app, read its skill: it names the real tool base names, the state
shape, and what goes wrong. `computers.md` (this skillset) for an app's own part on the
person's computers, `my-computer.md` for driving a paired `my_computer`; the plugin's
`training-monitor` (the workspace's TensorBoard — a training app logs to it from the machine
with `esoul.track`), `block-notes` (pages, folders, images, knowledge), `slideshow` (slides as
TSX, judged by a critic). For any other app: `get_app_tools` on an instance and read the
descriptions; `read_app_state` once to learn its shape.

## 8. Proving it

- Unit: mock `callWorkspaceTool`/`useWorkspaceTools` and assert the ARGUMENTS (the tool base,
  the target, the payload) — a mock that repeats your mistake proves nothing; read the other
  app's tool signature with `get_app_tools` first.
- Live in the box: the preview open on the board, then `call_app_tool` on YOUR tool and the
  hosted `read_app_state` on THEIR instance to see the row land.
- Say in the report which grants the manifest now carries and why each is needed.
