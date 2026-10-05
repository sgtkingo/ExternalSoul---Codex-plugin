# The app's own server, and its durable tasks

An app brings its own backend in `server.ts` (`"server-only"`; ops, routes, webhooks) and its
own durable work on the schema (`tasks`, run by the platform's Inngest). The preview runs all
of it in-process before install (`what-you-work-with.md` §3), so every arm is driven with tools
first.

| Need | Use | Lives | Latency | Survives |
|---|---|---|---|---|
| one JSON answer / one action with server truth, tables, a credential | **op** | one request, ≤ 300 s | ~60 ms + your work | nothing outlives the request |
| a stream, bytes, headers, a long single request | **route** (`sseStream`) | one request (minutes) | ms; a fold read ≈ 60 ms | nothing |
| a machine phoning home with no session | **route** `access: "token"` | one request | ms | — |
| something pushed at you by a service | **webhook** → ACK → task | one request | — | the task does |
| work that must FINISH: a sync, a wait for a reply, a job, a cadence | **task** | Inngest | seconds per hop (kick → task 2–15 s; a fold read ≈ 3 s) | process death, deploys, retries |

Measured on the stopwatch: kick → first tick 0.2 s (route) vs 2–15 s (task). **Never make a task
keep sub-second time; never make a route keep a promise past its request.** Ship both when it
matters and record which drove each run.

## 1. Ops

```ts
// ops.ts: ops = defineOps({ "find-faults": z.object({ customer: z.number().int().describe("Customer number") }) })
// server.ts
async function findFaults(ctx: PluginOpContext, input: OpIn<"find-faults">) {
  const db = await pluginDb<LabDb>(ctx);                                   // your tables, already scoped to ctx.viewer
  const rows = await db.fault.findMany({ where: { customer: input.customer }, orderBy: { ts: "desc" }, take: 50 });
  await ctx.notify("inspected", { customer: input.customer });            // a nudge to mounted UIs (§5)
  return { rows, since: rows.at(-1)?.ts ?? null };                          // say what you can see back to
}
export const pluginServer: PluginServerModule = { ops: { "find-faults": handleOp(ops, "find-faults", findFaults) } };
```

`POST /api/plugins/<id>/op/<name>` `{ nodeId, args }`. The platform resolves `ctx.viewer`, checks
the op's declared `access` and that `nodeId` is an instance of YOUR type, parses `args` with your
zod (`invalid` names a field the op does not take), then runs you. `ctx = { nodeId, workspaceId,
viewer, args, emit, notify, apps, cloudConnectionId, origin, … }`.

- Idempotent — a tool call is retried. Derive ids from the input (`product:${sku}`), not from time.
- **The op owns the timeline**: a change that belongs on the fold is `ctx.emit("<your event>",
  data)` — your `dataCreator` mints, your processor folds, triggers fire, it lands on THIS
  instance. Catch a failed emit/notify and report it; never let a courtesy undo a committed row.
- An op reads its **bindings or its tables**, not its history: `readAppState(ctx.nodeId)` folds
  the whole app — fine for a small fold, a paged rebuild for a big one.
- An expected refusal is RETURNED (`{ ok:false, code, message }`); a THROW is journalled as a bug
  and answers 502 (`app-anatomy.md` §5, `guarded()`).
- Access: `write` (default) · `read` (workspace members incl. read-only) · `public` (share-link
  holders) · `public` + `requires:"account"` (must sign in → `login-required`, which the UI turns
  into the sign-in wall). Every `public` op is named on the install card.

## 2. Routes

```json
"routes": { "ticks": { "access": "read" }, "ingest": { "access": "token" } }
```
```ts
import { readAppState, sseStream, pluginDb, emitPluginAppEvent, type PluginServerModule } from "esoul-sdk/server";
export const pluginServer: PluginServerModule = {
  routes: {
    ticks: async (ctx) => sseStream(async (send, signal) => {               // a live view: one process, no scheduler hops
      while (!signal.aborted) {
        const app = await readAppState(ctx.nodeId);
        const cur = (app?.state as { current?: { runId: string; kickedAt: number } }).current;
        if (cur) send("tick", { runId: cur.runId, elapsedMs: Date.now() - cur.kickedAt });
        await new Promise((r) => setTimeout(r, 1000));
      }
    }, { signal: ctx.request.signal }),
    ingest: async (ctx) => {                                                  // a machine's door
      const body = await ctx.request.json();                                  // validate it — a machine is not a friend
      const db = await pluginDb<LabDb>(ctx);
      await db.sample.createMany({ data: body.buckets });                     // ctx.viewer.kind === "internal", viewerIds[0] === "token:<label>"
      return Response.json({ ok: true, n: body.buckets.length });
    },
  },
};
```
```tsx
// UI: the session rides along; a public-share viewer may watch, not write
const es = new EventSource(pluginRouteUrl(PLUGIN_ID, "ticks", state.nodeId));
es.addEventListener("tick", (e) => setTick(JSON.parse((e as MessageEvent).data)));
```

Mounted at `GET|POST /api/plugins/<id>/route/<name>?nodeId=<instance>`. READ to reach;
`ctx.canWrite` says whether the caller may mutate — check it before writing. A route context has
no `emit`: use `emitPluginAppEvent` with `targetNodeId: ctx.nodeId` for your own timeline.

## 3. A door for a machine — `mintRouteToken`

```ts
const grant = await mintRouteToken(ctx, { route: "ingest", ttlSeconds: 7 * 86_400, label: "laptop bridge" });
// grant = { token, url, expiresAt }; url is on the origin THIS call arrived on (a box's preview domain in the Forge, the platform after install)
await computer(ctx, machineNodeId).run(`python3 bridge.py --push '${grant.url}' --token '${grant.token}'`);
```
The machine sends `Authorization: Bearer <token>`. Stateless, signed by the platform, bound to
one route of one instance, expires (≤ 30 days; expiry is the only revocation — keep it short).
A session never opens a `token` route, however privileged. Mint it in an op only the owner
reaches. (The one-time credential hand-off is the same door with a 10-minute life —
`my-computer.md` §5.)

## 4. Webhooks

```json
"webhooks": ["inbound"]
```
```ts
webhooks: { inbound: async (ctx: PluginWebhookContext) => {
  if (!ctx.secret) return new Response("no secret configured", { status: 503 });        // fail CLOSED
  if (!timingSafeEqual(sig(ctx.rawBody, ctx.secret), ctx.request.headers.get("x-signature") ?? "")) return new Response("bad signature", { status: 401 });
  const body = schema.parse(JSON.parse(ctx.rawBody));                                       // validate
  await ctx.sendInngestEvent("plugin_my_app/ingest", { pushId: body.id, payload: body });   // hand off to a task
  return Response.json({ ok: true });                                                       // ACK fast
} }
```
`POST /api/plugins/<id>/webhook/<hook>`. **Verify, validate, hand to a task, ACK** — never do the
work here (senders retry; requests time out; tasks are durable). Every push carries an
idempotency key; derive the event id from it (`deterministicReducerId`) so a redelivery folds to
one item. No sender can reach a box: unit-test the verify + hand-off; install to receive.

## 5. Tasks — durable work on Inngest

```ts
// app.tsx, on the schema
tasks: [{
  taskName: "watch-run",
  description: "Poll a training run on the machine until its verdict",     // ≤ 255 chars — it IS the Inngest function name
  concurrency: { limit: 1, scope: "per-app" },
  handler: async (ctx) => {
    const { runId, machineNodeId } = ctx.eventData ?? {};
    if (typeof runId !== "string" || typeof machineNodeId !== "string") return;
    for (let i = 0; i < 120; i++) {                                                          // bounded
      const poll = await ctx.step.run(`poll-${i}`, () => computer(ctx, machineNodeId).runJson<Poll>(`python3 helper.py train-poll --run ${runId}`));
      if (!poll.ok || poll.value.alive) { await ctx.step.sleep(`wait-${i}`, "30s"); continue; }
      await ctx.step.run("record-verdict", () => ctx.dispatchEvent("plugin_lab_run_recorded", { run: { runId, finishedAt: Date.now(), verdict: readVerdict(poll.value) } }));
      await ctx.step.run("tell-the-room", () => ctx.notify("run", { runId, done: true }));
      return;
    }
  },
}],
```
```json
"kickableTasks": { "watch-run": {} },
"pollTasks": [{ "task": "refresh", "everyMinutes": 30 }]
```

**The context**: `ctx.identifier` (workspaceId, nodeId, applicationType, instanceName),
`ctx.eventData` (the kick's payload — exactly what was sent), `ctx.step` (`run`, `sleep`,
`sendEvent`, `waitForEvent`), `ctx.getState()` (the fold, fresh), `ctx.dispatchEvent(eventName,
eventData)` (through the full pipeline with YOUR processors — a task's mutation is identical to a
tap's), `ctx.notify(topic, data, { to? })`, `ctx.kickedBy`, `ctx.logger`; `computer`,
`callWorkspaceTool`, `readAppState`, `pluginDb` all work.

**The replay model — read it twice.** Inngest **re-runs your handler from the top after every
step boundary**, replacing each finished `step.run` with its cached result. Anything outside a
`step.run` runs again on every replay: a dispatch outside a step with three steps after it fires
four times; `nanoid()` / `Date.now()` outside a step differ per replay. So: **every side effect
lives inside a `step.run`** (dispatch, fetch, emit, notify, a machine command), values are minted
inside, step names are unique per logical operation (loops include the index), and **inside a
step you never `void` a promise that must land** — a fire-and-forget notify inside a step is
orphaned when the step returns (on production not one tick reached the channel while the awaited
`stopped` always did). In a box `step.run` is NOT a barrier: an unwrapped side effect fires once
there and N+1 times on the platform — the unit test with a fake ctx is what catches it.

**How a task starts**: a tool or the UI → `kickPluginTask({ applicationType, taskName, identifier:
state, data })` (only names in `kickableTasks`; `data` is exactly `ctx.eventData`); a webhook →
`ctx.sendInngestEvent("<applicationType>/<task>", payload)`; a cadence → `pollTasks` (5-minute
granularity, minimum 5; handlers idempotent — sweeps overlap); another event →
`ctx.step.waitForEvent` (the platform matches name + your node; sandwich it with a state check
before and after — it matches FUTURE events only). No per-app crons.

**Concurrency** `{ limit, scope: "per-app" | "global" }` — keep it small; a parked wait holds no
slot, so hundreds may wait while five compute.

## 6. Realtime — telling mounted UIs

```json
"channel": { "topics": { "run": {}, "your-order": { "audience": "viewer", "mayAddress": ["staff"] }, "new-order": { "audience": "role:staff", "mayAddress": ["customer", "staff"] } } }
```
```ts
export const channel = definePluginChannel({ applicationType: APP_TYPE, topics: { run: { schema: z.object({ runId: z.string(), done: z.boolean() }) }, /*…*/ } });
await ctx.notify("new-order", { orderId }, { to: { role: "staff" } });                 // from an op or a task
await ctx.notify("your-order", { orderId, status }, { to: { viewerIds: [row.ownerId] } });
```
```tsx
const live = usePluginRealtime<{ runId: string; done: boolean }>({ channel, workspaceId: state.workspaceId, nodeId: state.nodeId, topics: channel.topicNames, enabled: !!state.nodeId });
useEffect(() => { if (live.latestData?.topic === "run") reload(); }, [live.latestData, reload]);
```
Audiences: `all` (one channel per instance), `viewer` (one per person), `role:<name>` (one per
role). The browser asks for a KIND of channel; the server fills in whose — nobody can ask for
another's. Aiming (`to`) is a separate permission from hearing (`mayAddress`); your own tasks
always may. **A message is a nudge, never data**: re-read through your op so the rules decide
what comes back; anything durable is ALSO an event or a row. Everyone who may DO a thing must be
allowed to ANNOUNCE it (list every role the `create` rule allows in `mayAddress`). A UI moves
only when a message or a fold arrives — no `Date.now() − startedAt` clocks pretending to be
progress; a stalled task must look stalled.

## 7. Proving the backend in the box

```
call_app_tool  {tool:"start_run"}         → the tool kicked the task; the preview's runtime ran it in-process
read_app_state                              → current.status "running" within a second
call_app_tool  {tool:"read_run"}            → the op answered from the preview's fold / in-memory tables
   (the frame shows notifies arriving — usePluginRealtime over the store's buffer)
call_app_tool  {tool:"stop_run"} → read_app_state → runs[0].verdict
run_in_app     {cmd:"curl -N 'http://localhost:3000/internal/plugin-preview/route/<id>/ticks?nodeId=preview-<type>'"}   → the route streams
```
Unit-test the task handler with a fake ctx (`step.run` calls the function; `dispatchEvent` and
`notify` record; run it twice with the same `eventData` and assert idempotency; assert every
task `description.length <= 255`). Webhooks: the verify and the hand-off. Then install for
durability, cadences, real receipts — and after any deploy that touches a task, the platform's
Inngest sync must have accepted the functions (a task description over 255 characters failed the
whole sync while the deploy said READY).
