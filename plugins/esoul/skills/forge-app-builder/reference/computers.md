# Parts of the app that run on the person's computers

When an app needs the person's own machine — a service that keeps running there (a local model
server, a sampler, a bridge to a device on the desk, a trainer's supervisor), a GPU, files that
never leave a laptop, a tool installed there — it ships a **device arm**: commands it may run,
or its own **program** kept running on the computer, and the computer talks to the app through
the app's own ops. The SDK's contract: `docs/18-your-computer.md` (reference) and
`docs/20-a-service-on-your-computer.md` (the walk-through). Read both in the box
(`read_platform_file {path:"node_modules/esoul-sdk/docs/20-a-service-on-your-computer.md"}`) or
at <https://www.npmjs.com/package/esoul-sdk> (`https://unpkg.com/esoul-sdk/docs/<nn>-<chapter>.md`).

The older path — driving a paired **My Computer** app with shell strings through
`computer(ctx, machineNodeId)` — is in `my-computer.md`. Use it only when the person already
runs My Computer and the work is one-off commands; a new app that lives on a computer is a
device arm.

## 1. Pick the shape

| The app needs | Declare | Server code |
|---|---|---|
| **a service of its own, two-way** (keeps running, answers the app, reports to it) | `device.program` + `device/main.ts` | `devices(ctx).program(linkId).send(topic, data)`; the program calls your ops with `p.op(...)` |
| a known tool run with checked parameters (`nvidia-smi`, `train.py --epochs N`) | `device.commands` (argv templates, typed params) | `devices(ctx).run(name, params)` → `wait` / `get` / `cancel`; UI `useDeviceRun` |
| agents that work IN a project folder (read, edit, patch, test, a dev server in a terminal) | nothing extra — the owner grants a folder | `devices(ctx).sh("patch src/x.py", { agent, stdin })`, `sh("term new dev npm run dev", { agent })` |
| a process that is NOT your program pushes data in (a script, a device, CI) | a route with `"access": "token"` | `mintRouteToken(ctx, { route, ttlSeconds })`; the process POSTs with `Authorization: Bearer` |

## 2. The service pattern (the reference app is CPU monitor, `src/plugins/cpu-monitor`)

```
server.ts ─ devices(ctx).program(linkId).send("ask", data, { waitSeconds: 30 }) ─▶ device/main.ts  p.on("ask", h)
ops.ts    ◀──────────────────── p.op("report", data, { key }) ───────────────── p.every / events
                                                                              │ fetch("http://127.0.0.1:PORT")
                                                                              ▼ the service the program started
```

```json
"ops": ["ask", "report", "computers"],
"device": {
  "program": {
    "main": "device/main.ts", "resident": true,
    "setup": [{ "id": "venv", "describe": "Python environment", "run": ["python3", "-m", "venv", ".venv"] },
              { "id": "deps", "describe": "Install the server", "run": [".venv/bin/pip", "install", "-r", "{program}/device/requirements.txt"], "inputs": ["device/requirements.txt"] }],
    "selfTest": { "run": [".venv/bin/python", "{program}/device/self_test.py"] }
  },
  "config": { "MODEL_DIR": { "describe": "Where the weights are on this computer" } },
  "onAppDeleted": "kill"
}
```

- `device/main.ts` exports `{ start(p), stop?() } satisfies Program` (`import type { Program }
  from "esoul-sdk/machine"` — types only). `p` has `on(topic, handler)` (the return value is the
  answer), `op(name, args, { key })`, `every(ms, fn)`, `status(text, { ready, progress })`,
  `log`, `dataDir` (writable, kept across versions), `programDir`, `workspaceRoot` (the granted
  folder; null with the whole computer), `config` (local settings, never sent to the platform),
  `computer` (hostname, platform, arch, cpus, memoryGb).
- The program starts the service itself (`spawn` with argv, never a shell line), waits for its
  health check, then `p.status("… ready", { ready: true })`. A handler `fetch`es its localhost.
- The program may import Node built-ins, files of `device/`, and `esoul-sdk/machine` **types**.
  No packages — install them in a setup step. ≤ 2 MB and ≤ 200 files; weights and datasets are
  downloaded in setup or at start. Node ≥ 22.6 runs `.ts` directly (no enums, no namespaces).
- The op the program calls checks `ctx.viewer.device` (`{ machineId, linkId, hostname }`) and
  refuses everyone else — only the program may report.

## 3. Rules that decide the design

- **Nothing reaches into the computer** — no tunnel, no open port. The computer calls out; the
  app reaches the program only through `send`. Do not design "the app opens localhost:8711".
- **`send` waits ≤ 55 s** (`waitSeconds: 0` returns at once). Longer work: the handler answers
  `{ accepted: true }`, finishes in the background, and `p.op("report", …, { key: requestId })`.
- **≤ 1 MB of JSON each way**; topics match `[a-zA-Z][a-zA-Z0-9_.:-]{0,63}`. Files go by link
  (`(await filesForOp(ctx)).readGrant(...)` + `fileGrantUrl`), results by op or saved file.
- **`p.op` must be fast and idempotent**: a call whose answer has not come in about 4 s is resent
  (up to 3 tries). Store by `requestId`; pass `{ key }`.
- A message for an **offline** computer expires (600 s default); `list()` says who is online and
  where each program stands (`programState.phase`: installing, a setup step, self-test,
  running, failed, with the program's own status words).
- `send`, `run`, `sh`, `cancel` need `ctx.viewer.canWrite`. The program's `p.op` runs as the
  owner who approved that computer (`viewer.kind === "agent"`).
- **Several computers**: `devices(ctx).list()`; remember the `linkId` the person chose (fold or
  a one-row table) — never "the first".

## 4. In the Forge — the honest limit

**Computers connect to INSTALLED apps only.** In a box `devices(ctx).list()` answers `[]`, every
other `devices()` call throws "computers connect to INSTALLED apps", `<ConnectComputer/>` shows a
note, `useDeviceActions` throws. Build it in this order and say so to the person:

1. **The program, tested with a fake `p`** (a test imports `device/main.ts`, calls `start(fakeP)`,
   then calls the captured handlers with `global.fetch` stubbed) — the SDK page 20 §5 has the
   exact fake.
2. **The app side** with `esoul-sdk/server` mocked (`devices().program().send` answering), and the
   `report` op called with a faked `viewer.device` — the fold shows the result.
3. **The service itself** if it can run in the box: `run_in_app` → start it on a port in the
   background, `curl localhost:<port>/health`.
4. `check_app` packs `device/` and refuses a program over the caps or one that imports a package.
5. `install_app` → `create_app(application_type="plugin_<id>")` → the person opens the app,
   presses **Connect a computer**, pastes the one command on their machine
   (`npx -y -p esoul-sdk@<version> esoul-device connect <link>`, or the `curl … /api/device/install
   | sh -s -- <link>` line when the machine has no Node), sees the same code on both screens,
   picks what the app may reach (commands only / its folder / the whole computer) and approves.
   Then the card shows setup, the self-test, your `p.status` words.

Never claim "it runs on your computer" before the person has approved it and `computers` (or
`list()`) says `running`. What a box CAN prove: the program's logic, the app's ops, the
manifest. What only an install proves: the program on a real computer, `send`, `p.op`, approval.

## 5. What the person approves, and what they can change

- The program is approved **by digest** (every file + the spec). A new version that changes it
  waits for **Approve** on the card; the old one keeps running meanwhile. Tell the person when an
  update will ask them.
- **Reach**: with the whole computer the program runs unconfined — needed when it uses the
  person's own logins (Claude Code, git, pip config). Otherwise it is sandboxed (bubblewrap on
  Linux, Seatbelt on macOS): reads the system, writes only `p.dataDir` and the granted folder;
  no sandbox on that computer → refused, never unconfined. The network is not confined.
- **Secrets stay on the computer**: declare them under `device.config` (`"secret": true`); the
  person sets them there with `esoul-device config set "<app name>" KEY`; the program reads
  `p.config`. Never pass a secret through `send`, an op, or an event.
- Linux and macOS (Windows through WSL2); the runtime runs as a user service and survives reboots.

## 6. Reporting

Say which computers are connected and online, which version of the program each runs, what
reach the person gave it, and anything waiting for their Approve. A refused `send` is reported
in its own words (`expired`, `not approved`, the handler's error).
