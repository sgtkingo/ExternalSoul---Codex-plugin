# The anatomy of an app — the code contract

An app is a folder `src/plugins/<id>/` on the platform's branch. The workbench scaffolds it;
you fill it in. Everything reaches the platform **only through `esoul-sdk`** (`esoul-sdk`,
`esoul-sdk/react`, `esoul-sdk/server`, `esoul-sdk/testing`), relative files, `server-only`, and
npm packages the platform already has. `@/…`, `node:*`, `prisma`, `next`, `inngest`: refused by
the import wall at check, sync and release.

```
plugin.json        the manifest — the design, read at install
ops.ts             what every op TAKES, declared once (zod) — imported by server.ts AND app.tsx
app.tsx            the SCHEMA: state, events, tools, describer, tasks, channel. NEVER "use client"
ui/<id>-ui.tsx     the React UI — "use client"; props { state }
server.ts          "server-only": ops, routes, webhooks, file providers
<id>.test.ts       the fold contract, the ops, the task — run by test_app
package.json       only for an npm package the platform lacks (a visible line in the PR)
```

## 1. `plugin.json`

| Field | Rule |
|---|---|
| `id` | lower-case, hyphens; equals the folder; **never changes** |
| `applicationType` | `plugin_` + id with underscores; **never changes**; the schema must name it AS A LITERAL (`applicationType: "plugin_x"` in app.tsx — not behind an import; the registry gate and the install check read it by eye) |
| `name`, `version`, `description` | what people see (≤ 80); semver bumped every submission; one honest paragraph (≤ 500) |
| `entry`, `icon` | `app`; a lucide-react name (the tool lists the allowed set) |
| `ops` | `{ "<name>": { "access"?: "write"\|"read"\|"public", "requires"?: "account" } }` — every op `server.ts` exports; default `write` |
| `routes` | same shape; `access: "token"` for a machine's door |
| `webhooks` | `["inbound"]` → `POST /api/plugins/<id>/webhook/inbound` |
| `kickableTasks`, `pollTasks` | tasks the browser/tools may kick; tasks run on a cadence (5-min granularity, min 5) |
| `roles` | your vocabulary + a `default` map from the platform's kinds; typed `attributes` a grant may carry |
| `db` | your tables: `fields`, `scope`, `owner`, `sealed`, `unique`, `indexes` (kinds `btree`/`contains`/`text`), `rules` |
| `channel` | realtime topics with audiences (`all` / `viewer` / `role:<name>`) and `mayAddress` |
| `workspaceTools` | grants to call OTHER apps' tools: `"<applicationType>:<tool base>"`; absent = none |
| `uses` / `provides` | binding slots and contracts (`talking-to-other-apps.md`) |
| `credentials` | the person's account the app uses — one slot: `google` (scopes), `oauth2` (any OAuth provider: endpoints, scopes, `hosts`) or `apiKey` (`hosts`, header); code calls `credentials(ctx).slot(n).fetch`, never holds the secret (`accounts.md`) |
| `connections` | older OAuth2 / apiKey declarations naming ENV VARIABLE names, never values; the token reaches your code — prefer `credentials` |
| `fileSources` | `{ workspace: "read"\|"readwrite", providers: [...], write: [...] }`; absent = no file access |
| `platformApi` | `{ min, max }` of the platform contract |

Secrets never live here. `ops: ["read-notes"]` (a bare array) still validates and means
`write` for each — prefer the object form so the access is visible.

## 2. `ops.ts` — declared once

```ts
import { z } from "zod";
import { defineOps } from "esoul-sdk";
export const PLUGIN_ID = "sticky-notes";
export const ops = defineOps({
  "read-notes": z.object({}),
  "add-note": z.object({
    text: z.string().min(1).max(2000).describe("The note's text"),
    color: z.enum(["butter", "rose", "mint", "sky", "lilac"]).optional().describe("Paper colour; butter when unsure"),
  }),
});
export type OpIn<K extends keyof typeof ops> = z.infer<(typeof ops)[K]>;
```

`.describe()` every field — it is the model's parameter help. `handleOp` parses with this;
`opTool` mints the tool from it; the UI sends the same fields. `z.object` STRIPS unknown
fields, so a hand-written tool that forgets one silently drops it — the night an op accepted
`imageUrl` and its tool did not, the shop "added Earl Grey" with no picture and every test was
green. Derived tools cannot drift; `check_app` scans for an op not wrapped in `handleOp` or a
tool naming an undeclared op.

## 3. `app.tsx` — the schema

```ts
import { nanoid, EventTypes, incompleteStateNotice, opTool, kickPluginTask,
  type ApplicationIdentifier, type ApplicationSchema, type ApplicationPort, type EventData, type EventDefinition } from "esoul-sdk";
import { z } from "zod";
import { ops, PLUGIN_ID } from "./ops";
import { StickyNotesUi } from "./ui/sticky-notes-ui";

export interface StickyNotesData extends ApplicationIdentifier {
  notes: { id: string; text: string; color: string; x: number; y: number; createdAt: number; updatedAt: number }[];
}

export const noteAddedEvent: EventDefinition<StickyNotesData> = {
  eventName: "plugin_sticky_notes_added",           // globally unique; prefix with your type
  type: EventTypes.Client,                          // the one type an app declares (there is NO EventTypes.Server); a task's dispatchEvent and an op's ctx.emit write Client events too
  dataCreator: (args) => ({                         // MINTS ids and times. Called by the UI and by tools.
    eventName: "plugin_sticky_notes_added",
    eventData: { noteId: args.noteId ?? nanoid(), text: String(args.text ?? "").slice(0, 2000), color: args.color ?? "butter", x: args.x ?? 24, y: args.y ?? 76, at: args.at ?? Date.now() },
    timestamp: Date.now(),
    workspaceId: args.workspaceId,
    applicationId: args.applicationId || args.nodeId,
    instanceName: args.instanceName,
    chatIdSource: args.chatIdSource,
  }) as EventData<any>,
  processor: (state, event) => {                    // PURE, idempotent, bounded, refusing
    const d = event.eventData ?? {};
    if (typeof d.noteId !== "string" || typeof d.text !== "string") return state;
    if (state.notes.some((n) => n.id === d.noteId)) return state;          // replay-safe
    if (state.notes.length >= 300) return state;                            // bounded
    return { ...state, notes: [...state.notes, { id: d.noteId, text: d.text, color: d.color, x: d.x, y: d.y, createdAt: d.at, updatedAt: d.at }] };
  },
  // An event other apps and agents may WAKE on (agent-builder Trigger node, chat waits):
  triggerMeta: { displayName: "Note added", description: "A sticky note was pinned", sampleVariables: ["noteId", "text"] },
};

export const noteTextSetEvent: EventDefinition<StickyNotesData> = {
  /* …dataCreator / processor as above; an unknown id is ignored, never invented… */
  collapseConfig: {                                  // a typing burst is ONE timeline row
    collapseKeyFn: (eventData, ctx) => `${ctx.applicationId}:${(eventData as { noteId?: string }).noteId}:text`,
    collapseWindowMs: 2500,
  },
} as EventDefinition<StickyNotesData>;

export const pluginSchema: ApplicationSchema<StickyNotesData> = {
  applicationType: "plugin_sticky_notes",           // the literal, as the manifest has it (never a constant from another file)
  description: "A wall of sticky notes on the workspace timeline.",
  reactNode: StickyNotesUi,
  reconstructStateFromEventLog: true,                // state IS the fold — replay, snapshots, durability
  events: [noteAddedEvent, noteTextSetEvent],
  getPorts: (): ApplicationPort[] => [],
  stateCreator: (identifier) => ({ ...identifier, notes: [] }),   // ALWAYS spread the identifier
  toolkitCreator: (identifier, forChatId, eventCallback) => {
    const base = identifier.instanceName.replace(/[^a-zA-Z0-9]/g, "_");
    const idArgs = { ...identifier, applicationId: identifier.nodeId, chatIdSource: forChatId };
    const pin = async (a: { text: string; color?: string }) => {           // an event tool: the fold
      const noteId = nanoid();
      await eventCallback(noteAddedEvent.dataCreator({ ...idArgs, noteId, ...a }));
      return `Pinned note ${noteId}.`;
    };
    return {
      [`pin_note_${base}`]: {
        description: `Pin a sticky note on "${identifier.instanceName}". Returns the note's id, which set_note_text takes.`,
        parameters: z.object({ text: z.string().min(1).max(2000), color: z.enum(["butter", "rose", "mint", "sky", "lilac"]).optional() }),
        execute: pin,
        onClient: pin,                                                       // voice + WebMCP: the SAME work
      },
      [`read_notes_${base}`]: opTool(ops, "read-notes", {                    // an op tool: server truth
        pluginId: PLUGIN_ID, nodeId: identifier.nodeId,
        description: `Read every note on "${identifier.instanceName}" with the ids the other tools take.`,
        readOnly: true, publicSafe: true,
        say: (s: Pick<StickyNotesData, "notes">) => describeNotes(s),
      }),
    };
  },
  getStateDescription: (state) => {                  // what an agent reads every turn
    const notLoaded = incompleteStateNotice({ title: "Sticky notes", instanceName: state?.instanceName, shape: { lists: { notes: state?.notes } } });
    if (notLoaded) return notLoaded;                 // MISSING means not loaded; [] is real
    return describeNotes(state);
  },
  // tasks: [...]  channel: ...   → server-and-tasks.md
};
```

The rules the checks enforce and reviewers read for:

- **Processors are pure, idempotent, bounded, and refuse** — return `state`, never throw (a
  throw in a fold takes the whole workspace view down).
- **Ids and timestamps are minted in `dataCreator`**, never in a processor (two folds of one log
  must be deep-equal).
- **Bursts and whole-replace events carry a collapse key** namespaced by instance AND entity AND
  field — never by the app alone.
- **What is local stays local** (a drag in flight, text mid-typing, which tab is open) and lands
  as ONE event when done. Never mirror app state into a second store.
- **`stateCreator` spreads the identifier**; tools and describers read `instanceName` from state.
- **Every UI action has a tool twin**; every tool has a real `onClient` (`= execute`) — an empty
  stub makes the voice runtime report success for nothing. `readOnly` lets a read-scoped token
  call it; `publicSafe` allows a storefront.
- **A tool never dispatches an event an op also records** — the op owns its timeline
  (`ctx.emit`); a double record has an id the reducer cannot dedupe.
- **`getStateDescription` never claims a count or an emptiness it could not read.**

## 4. `ui/<id>-ui.tsx`

```tsx
"use client";
import React, { useCallback, useEffect, useState } from "react";
import { callPluginOp, PluginCallError } from "esoul-sdk";
import { useAppCanEdit, usePluginCurrentChatId, usePluginEventDispatch, useViewer, useSignInWall, useWorkspaceTools, usePluginRealtime } from "esoul-sdk/react";
import { noteAddedEvent, type StickyNotesData } from "../app";
import { PLUGIN_ID } from "../ops";

export function StickyNotesUi({ state }: { state: StickyNotesData }) {
  const dispatch = usePluginEventDispatch();        // the ONLY way to change the fold
  const canEdit = useAppCanEdit();                  // readers of a share see it, cannot mutate
  const viewer = useViewer();                       // kind, role, canWrite, signedIn (a guess — never gate a read on it)
  const wall = useSignInWall();                     // login-required → the sign-in wall
  const tools = useWorkspaceTools(state);           // other apps, by manifest grant
  const dark = useIsDark();                         // observe .dark on <html> at runtime
  const op = useCallback(<T,>(name: string, args?: unknown) => callPluginOp<T>(PLUGIN_ID, name, state.nodeId, args), [state.nodeId]);
  // dispatch(noteAddedEvent.dataCreator({ ...state, applicationId: state.nodeId, text })) is a write; disable when !canEdit
  // wall.ask(() => op("my-orders")).then(r => r && setOrders(r))   — let the SERVER decide who is signed in
}
```
`usePluginCurrentChatId()` is the id of the chat the app is mounted beside — for a UI that hands
something to the conversation (a "discuss this" button); `""` when there is none.

- Props are `{ state }`, the folded state, live; you never fetch it.
- Server truth: `callPluginOp` (rides the session; in a box it reaches the preview's op route).
  A `PluginCallError` carries a `code` (`forbidden`, `login-required`, `invalid`, `not-bound`) —
  relay its message; `wall.raise(err)` turns `login-required` into the wall.
- Editors holding a local copy take remote changes through `useRemoteReconcile` (`packages/esoul-sdk/docs/17-editing-and-merging.md`),
  never a hand-rolled `useEffect` compare.
- Theme, layout, touch, popovers, empty state: `design-rules.md`. A `/`-heavy component tree is
  fine; keep files under 512 KB and the app under 200 files.

## 5. `server.ts`

```ts
import "server-only";
import { handleOp } from "esoul-sdk";
import { readAppState, pluginDb, computer, callWorkspaceTool, filesForOp, mintRouteToken, sseStream,
  type PluginOpContext, type PluginServerModule } from "esoul-sdk/server";
import { ops, type OpIn } from "./ops";

class Refusal extends Error { constructor(public code: string, message: string) { super(message); } }
/** An op that THROWS is journalled as a bug and answers 502. An expected refusal is RETURNED. */
const guarded = <A, R>(run: (ctx: PluginOpContext, a: A) => Promise<R>) => async (ctx: PluginOpContext, a: A) => {
  try { return await run(ctx, a); }
  catch (e) { if (e instanceof Refusal) return { ok: false as const, code: e.code, message: e.message }; throw e; }
};

async function readNotes(ctx: PluginOpContext) {
  const app = await readAppState(ctx.nodeId);                  // the fold at head; null = no such app
  if (!app) throw new Error(`no app ${ctx.nodeId}`);
  const s = app.state as Partial<StickyNotesData>;
  if (!Array.isArray(s.notes)) throw new Error("the wall did not fold (notes missing)");   // MISSING ≠ empty
  return { notes: s.notes };
}
async function addNote(ctx: PluginOpContext, input: OpIn<"add-note">) {
  if (!ctx.viewer.canWrite) throw new Refusal("read_only", "You can look, not pin — ask the owner for edit access.");
  await ctx.emit("plugin_sticky_notes_added", { noteId: `op-${ctx.viewer.viewerIds[0]}-${Date.now()}`, ...input });  // the op owns the timeline
  return { ok: true as const };
}

export const pluginServer: PluginServerModule = {
  ops: { "read-notes": handleOp(ops, "read-notes", readNotes), "add-note": handleOp(ops, "add-note", guarded(addNote)) },
  // routes: { … }, webhooks: { … }   → server-and-tasks.md
};
```

`ctx` on an op: `{ nodeId, workspaceId, viewer, args, emit, notify, apps, cloudConnectionId,
origin, … }`. Ops must be idempotent (a tool call can be retried) and answer within one request.
An op reads its BINDINGS or its tables — folding the app to read one field is a paged rebuild
paid by a stranger pressing "browse".

## 6. Tests — `<id>.test.ts`

```ts
import { fakeApps, fakeViewer, memoryDb, memoryFiles, roleForKind, runOp } from "esoul-sdk/testing";
import { noteAddedEvent, pluginSchema, type StickyNotesData } from "./app";

const IDENT = { workspaceId: "ws1", nodeId: "node1", applicationType: "plugin_sticky_notes", instanceName: "My wall" };
const fresh = (): StickyNotesData => pluginSchema.stateCreator(IDENT as any, {} as any);

it("starts empty; an event adds exactly what it says; a replay is a no-op", () => {
  const ev = noteAddedEvent.dataCreator({ ...IDENT, noteId: "n1", text: "milk" });
  const once = noteAddedEvent.processor(fresh(), ev);
  expect(once.notes.map((n) => n.id)).toEqual(["n1"]);
  expect(noteAddedEvent.processor(once, ev)).toEqual(once);
});
it("refuses a payload it cannot trust", () => expect(noteAddedEvent.processor(fresh(), { eventData: { noteId: 42 } } as any)).toEqual(fresh()));
it("two folds of one log are identical (no processor mints)", () => { /* fold twice, deep-equal */ });
it("the describer never claims an emptiness it could not read", () => {
  expect(pluginSchema.getStateDescription({ ...IDENT } as any)).toMatch(/not loaded|incomplete/i);
  expect(pluginSchema.getStateDescription(fresh())).toMatch(/No notes yet/);
});
it("visitor-b cannot read visitor-a's row", async () => { /* memoryDb(manifest) + fakeViewer + runOp — data-people-files.md */ });
```
`fakeApps({ slot: { nodeId?, tools } })` stands in for `ctx.apps.<slot>` (a bound app) and
records every `call` so a test asserts the ARGUMENTS your op sent; `roleForKind(manifest,
kind)` answers the word your `roles.default` gives a platform kind, so a test names the role the
platform would — not a guess (its `member` is an EDIT member; pass `role` to `fakeViewer` for
read-only).

Tests must not import `node:*` (the wall runs over tests too). Local jest is `isolatedModules`:
types are inert — `check_app` on the box is the bar. Keep tests fast; they run beside the preview.

## 7. `assets.json` — the app's media, by hash

Written by the platform, never by hand, when you `put_app_asset` / `forge_put_asset`:

```json
{ "pluginId": "cafe-site", "files": { "hero.mp4": { "sha256": "…64 hex…", "bytes": 4120334, "type": "video/mp4" } } }
```

The bytes are not in the package — they sit in the platform's content-addressed store and are
served immutable at `/pa/<pluginId>/<sha256>.<ext>`. In the app: `import assets from
"./assets.json"` and `assetUrl(assets, "hero.mp4")` from `esoul-sdk`. See `assets.md`.
