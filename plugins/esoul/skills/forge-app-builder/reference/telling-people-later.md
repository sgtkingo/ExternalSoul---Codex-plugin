# Telling people things later — a status change, a cadence, a first visit

The SDK has **no send-mail primitive** and no way to look a person up after the fact. Both are
deliberate, and they decide the shape of everything below:

- Mail leaves through the **email app already on the workspace**, called like any other app
  (`callWorkspaceTool`, `talking-to-other-apps.md` §1), under a `workspaceTools` grant the owner
  reads at install. Your app never holds a mailbox, a credential, or a sending reputation.
- `viewerProfile(ctx.viewer)` answers only for a LIVE viewer. A task that runs later — a
  cadence, a status change hours after checkout — has no viewer and **cannot ask who someone
  was**. So the address is captured at the moment there IS a viewer, into your own table, with
  their consent recorded beside it.

Everything is a **task** (`server-and-tasks.md` §5): durable, retried, replay-safe. A route or an
op that "sends later" has nothing to hold the promise.

## 1. Capture the recipient while you still can

The first time a signed-in person does the thing worth following up on, record who they are and
what they agreed to. This is the ONLY point in the whole flow where `viewerProfile` works.

```json
"db": {
  "Subscription": {
    "scope": "instance", "owner": "creator",
    "fields": { "email": "string", "kind": "string", "frequency": "string?", "active": "boolean=true", "lastSentAt": "datetime?" },
    "sealed": ["email"],
    "indexes": [["kind", "active"], ["active", "lastSentAt"]],
    "rules": { "read": ["creator", "owner"], "create": { "roles": ["customer", "owner"], "requires": "account" },
               "update": ["creator", "owner"], "delete": ["creator", "owner"] }
  }
}
```

```ts
// an op the UI calls when the person opts in — never silently on first visit
"subscribe": {
  access: "public", requires: "account",
  handler: async (ctx) => {
    const me = await viewerProfile(ctx.viewer);                       // the caller's OWN details, now or never
    if (!me?.email) throw new Refusal("no-email", "This account has no email address to reach.");
    const db = await pluginDb<Db>(ctx);                                // narrowed to the caller by the rules
    const mine = await db.subscription.findFirst({ where: { kind: ctx.args.kind } });   // `read: creator` ⇒ only THEIR row can match
    return mine
      ? db.subscription.update({ where: { id: mine.id }, data: { active: true, frequency: ctx.args.frequency, email: me.email } })
      : db.subscription.create({ data: { email: me.email, kind: ctx.args.kind, frequency: ctx.args.frequency } });
  },
}
```

- **One row per person per kind comes from the RULES, not from `unique`.** A declared `unique`
  group is checked among live rows of the whole INSTANCE — it cannot mean "one per person", and
  the second customer to subscribe would be refused. Under `read: creator` the caller's
  `findFirst` can only ever match their own row, so find-then-create-or-update is exactly "one
  per person". `owner: "creator"` keeps it theirs across every id they have acted under.
- **`sealed: ["email"]`** — encrypted at rest, readable by the row's owner and your own server
  code, null to everyone else. Staff see that a subscription exists; they never see the address.
- **`requires: "account"`** — an anonymous visitor cannot subscribe; there is nobody to notify.
  The UI attempts the call and lets the refusal raise the sign-in wall
  (`data-people-files.md` §2 — never gate on `viewer.signedIn`).
- **Consent is a row, not an assumption.** `active: false` on unsubscribe; never delete (a
  deleted row is a person you may re-add by accident). Every mail you send links to the op that
  flips it.

A row your app writes on someone's BEHALF — an import, a machine — carries no viewer either;
capture the address from the source that has it, and say so in the row (`source: "import"`).

## 2. A status change → one message, once

**A task cannot ask who a row belongs to.** Scope is injected, never accepted: `where: { ownerId }`
is refused (`invalid`), and `ownerId` is not a field you may index. So the row a task will act on
later must **carry its own recipient**, written at the one moment a viewer exists:

```json
"Order": { "scope": "instance", "owner": "creator",
  "fields": { "status": "string=new", "totalCents": "int", "lines": "json", "notifyEmail": "string?" },
  "sealed": ["notifyEmail"], "indexes": [["status"], ["createdAt"]],
  "rules": { "read": ["creator", "staff", "owner"], "create": { "roles": ["customer", "staff", "owner"], "requires": "account" },
             "update": { "roles": ["staff", "owner"] }, "delete": ["owner"] } }
```
```ts
// place-order: the caller's active subscription decides whether the order is reachable later
const sub = await db.subscription.findFirst({ where: { kind: "orders", active: true } });   // their own row or nothing
const order = await db.order.create({ data: { status: "new", totalCents, lines, notifyEmail: sub?.email ?? null } });
```

The op that changes state does not send mail. It changes state, then **kicks a task** with the
facts the task needs — because the op's request ends and the task's does not.

```ts
// in the op, after the write, inside the same handler
await kickPluginTask({ applicationType: APP_TYPE, taskName: "notify-status", identifier: ctx.identifier,
  data: { orderId, status, dedup: `order:${orderId}:${status}` } });
```
```ts
tasks: [{
  taskName: "notify-status", description: "Tell the order's owner its status moved",
  concurrency: { limit: 2, scope: "per-app" },
  handler: async (ctx) => {
    const { orderId, status, dedup } = ctx.eventData ?? {};
    if (typeof orderId !== "string" || typeof status !== "string") return;          // a bad kick is silence, not a crash loop
    const db = await pluginDb<Db>(ctx);                                             // internal: rules off, scope on, sealed fields readable
    const order = await ctx.step.run("read-order", () => db.order.findUnique({ where: { id: orderId } }));
    if (!order?.notifyEmail) return;                                                // no consent at checkout → no mail, and that is correct
    const state = await ctx.getState();
    const sent = await ctx.step.run("send", () => callWorkspaceTool({
      pluginId: PLUGIN_ID, nodeId: ctx.identifier.nodeId, appType: "email_viewer", tool: "send_email", targetNodeId: state.mailboxNodeId,
      args: { to: [order.notifyEmail], subject: `Order ${order.id}: ${status}`, body: renderStatus(order, status) },
    }));
    if (!sent.ok) throw new Error(`mail refused: ${sent.text}`);                    // let Inngest retry the STEP, not re-run the op
    await ctx.step.run("record", () => ctx.dispatchEvent("plugin_notice_sent", { orderId, status, dedup, at: Date.now() }));
  },
}],
"kickableTasks": { "notify-status": {} },
"workspaceTools": ["email_viewer:send_email", "email_viewer:list_mailboxes"]
```

The rules that make this correct:

- **The recipient is read off the row, never looked up.** `internal` bypasses rules, never scope,
  and a sealed field is readable to your own server code — that is exactly what makes a
  sealed `notifyEmail` on the order both private and usable.
- **`dedup` travels with the kick and lands in the fold.** A retried kick, a replayed step, a
  status set twice — one mail. Check the fold for `dedup` before sending if the send is not
  itself idempotent.
- **A refusal from the email app is a thrown error inside the step**, so Inngest retries the
  send and nothing before it. Swallowing it produces a quiet app that "sent" nothing.
- **The mailbox is named, not guessed.** A workspace may hold several `email_viewer` instances;
  `targetNodeId` comes from your fold (the owner picked it once, `list_mailboxes` on setup) — the
  same rule as every cross-app call (`talking-to-other-apps.md` §1).
- **The event after the send is the audit.** `plugin_notice_sent` is what a scrub shows, what a
  trigger can wake on, and what the UI's "we emailed you" reads — never a local boolean.

## 3. A cadence → a digest, on the pull lane

Scheduled updates are `pollTasks`: five-minute granularity, minimum five, **handlers idempotent
because sweeps overlap**. There is no per-app cron and no per-person timer; a cadence is one
sweep that decides, per row, whether it is due.

```json
"pollTasks": [{ "task": "send-digests", "everyMinutes": 60 }]
```
```ts
{ taskName: "send-digests", description: "Weekly digest to everyone due for one", concurrency: { limit: 1, scope: "per-app" },
  handler: async (ctx) => {
    const db = await pluginDb<Db>(ctx);
    const due = await ctx.step.run("find-due", () => db.subscription.findMany({
      where: { kind: "digest", active: true, lastSentAt: { lt: new Date(Date.now() - 7 * 86_400_000) } }, orderBy: { lastSentAt: "asc" }, take: 50 }));
    for (const [i, sub] of due.entries()) {
      const body = await ctx.step.run(`compose-${i}`, () => composeDigest(db, sub));   // per-person content, from the rules' view of their rows
      if (!body) continue;
      const sent = await ctx.step.run(`send-${i}`, () => callWorkspaceTool({ /* as above */ args: { to: [sub.email], subject: body.subject, body: body.text } }));
      if (!sent.ok) continue;                                                           // one refused address never blocks the rest
      await ctx.step.run(`mark-${i}`, () => db.subscription.update({ where: { id: sub.id }, data: { lastSentAt: new Date() } }));
    }
  } }
```

- **The sweep sees every subscription** — `internal` reads the whole instance, unsealed. That is
  the one context in which reading everyone's address is correct, and it is why this code runs
  in a task and never in an op.
- **`lastSentAt` is the cursor.** The sweep sends to whoever is due and marks them; the next
  sweep, overlapping or not, finds them not due. `take: 50` bounds one tick; the rest are next
  tick's — never one enormous step.
- **Mark AFTER the send succeeds**, in its own step. Mark first and a crash between the two
  skips a person for a week.
- **A per-person step name** (`send-${i}`) so a replay resumes at the right person.
- **`concurrency.limit: 1`** — two sweeps sending the same digest is the failure this whole
  section exists to prevent.

## 4. The first signed-in visit

"Send them something when they first arrive" is two decisions, and only one of them is yours:

1. **Detect** it: an op the UI calls on mount (`"me"`, `access: "public"`) that reads the
   viewer and your table, and returns `{ known: boolean }`. The first `false` with a real
   `userId` is the first visit. Record it as a row (`Visit`, `owner: "creator"`, one per person)
   — the fold is the wrong place for per-person facts (`data-people-files.md` §1).
2. **Ask** before you write to them. Detection is not consent; a welcome mail to a person who
   signed in to look is the mail that gets your owner's mailbox flagged. Show the offer, run
   `subscribe` on yes, and let §2 do the rest. An owner may configure a welcome that sends on
   subscription; the app never sends on arrival.

## 5. Who may do what — the access levels this touches

| Seam | Level | Why |
|---|---|---|
| `subscribe` op | `public` + `requires: "account"` | share-link visitors may opt in, but only with an account to notify |
| `me` op | `public` | must answer for anonymous visitors too — with `known: false` |
| `Subscription` rows | `read: creator, owner` · `sealed: email` | staff see that a subscription exists, never the address |
| `notify-status` task | kicked only by your own op (`kickableTasks`) | a visitor cannot make your app send mail |
| the email app's tools | `workspaceTools` grant, read by the owner at install | the owner decides your app may send from their mailbox at all |

A read-only member sees the subscriptions list and cannot flip one; a customer flips only their
own; the owner sees every row and no address. Prove it as five people
(`data-people-files.md` §2) — the assertion that matters is that a customer's count of another
customer's subscriptions is **0**, and that `email` is `null` in the staff view.

## 6. Proving it

- **Unit**: a fake ctx with `step.run` as a pass-through, `callWorkspaceTool` mocked — assert
  the **arguments** (`to`, the tool base, `targetNodeId`) and that a refused send throws. Assert
  the dedup: two kicks with one `dedup` → one send.
- **Replay**: the same handler with a ctx whose `step.run` throws on the second call — the send
  must not have fired twice. In a box `step.run` is not a barrier; only this test catches it.
- **Live, on a throwaway instance**: subscribe as VIEW-AS `visitor-a`, move an order, read the
  workspace's email app with the hosted `read_app_state` and find the sent message; read your
  fold and find `plugin_notice_sent`. Tell the owner which mailbox it went from.
