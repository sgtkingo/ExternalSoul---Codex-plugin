# Using the person's computer from an app — in the Forge and after install

`my_computer` is an app on the workspace paired with a machine the person owns (a laptop, a
lab box, a GPU rig). Its four tools — `computer_status`, `run_on_computer`,
`get_computer_result`, `claude_task` — run commands and Claude Code sessions there and bring the
output back. Your app orchestrates that machine and **remembers** what it did: the machine
computes, the app records, the app reasons.

## 1. What you are working with

| Fact | Consequence for your design |
|---|---|
| Every command is **approval-gated** unless the OWNER set the app to **Auto** — and only a person can; an agent, a tool or a PAT setting Auto is ignored by design | a `pending_approval` is a WAIT, not a failure: show its `message` as it comes and poll; never try to auto-approve |
| One wait ≤ 55 s; one command ≤ 900 s | anything longer runs **detached** (`nohup … > log 2>&1 & echo $!`) and is **polled** by pid |
| **8,000 characters** of output are kept | compute ON the machine, print a small JSON; a cut answer is `truncated` — unknown, never half-parsed |
| Commands are recorded on the workspace **timeline** | **no secret ever rides in a command** — the workspace credential the owner granted rides in the command's ENVIRONMENT (`ESOUL_TOKEN`, §5); anything else goes through a one-time `token` route |
| Several machines may be paired | remember the chosen `machineNodeId` in the fold or a one-row table; never "the first" |
| From a box, `computer()` travels through the board's open tab | headless (MCP with no board tab open) you get "no board is connected to this preview"; unit-test with the machine mocked, drive live with the preview open on the board, or after install |
| A machine that does not answer is named as such | "no app X in this workspace" / "offline since …" — never blame a server it never asked |

Declare the grants or every call is refused, in the Forge exactly as after install:
```json
"workspaceTools": ["my_computer:computer_status", "my_computer:run_on_computer", "my_computer:get_computer_result", "my_computer:claude_task"]
```

## 2. The server API — `computer(ctx, machineNodeId)` from `esoul-sdk/server`

```ts
const box = computer(ctx, machineNodeId);
const st  = await box.status();                    // { ok, paired, online, hostname, os, autonomy: "approve"|"auto", pendingApproval, message }
const r   = await box.run("cd ~/proj && make", { cwd?, timeoutSeconds: 600, waitSeconds?: 8 });
//  r = { ok, status: "done"|"running"|"pending_approval"|"error"|…, commandId, exitCode, stdout, stderr, timedOut, message }
const r2  = await box.result(r.commandId!, 40);    // ask again for a running command
const end = await box.runToEnd("python -m job", { deadlineMs: 300_000, waitForApproval: true, onWait: (o) => log(o.status) });
const j   = await box.runJson<{ rows: number }>("python summarise.py");            // one JSON document out; `truncated` never parses half
const p   = await box.python<{ ok: boolean }>(`import json; print(json.dumps({"ok": True}))`, { python: "/opt/conda/bin/python" });
const f   = await box.readFile("/home/me/brief.md", { maxBytes: 20_000 });          // { ok, text, error }
const api = await box.fetchJson("http://localhost:8600/health");                    // curl runs ON the machine — its localhost
const ai  = await box.claude("Read README.md and list the run steps", { cwd: "~/proj", permissionMode: "no_writes", sessionId? });
const ai2 = await box.claudeToEnd(prompt, { deadlineMs: 600_000 });                 // { answer, sessionId, costUsd, isError }
```

Pass parameters into a script as a JSON literal — `json.loads(${JSON.stringify(JSON.stringify(params))})`
— a JSON string is a valid Python string literal, so nothing a caller sends can break the script.
**Ops answer within one request**: in an op leave `waitForApproval` off and report a pending
approval; long waits belong in a task (`runToEnd` / `claudeToEnd`, one `step.run` per wait).

From the UI, the same four tools are reachable with `useWorkspaceTools(state).call({ appType:
"my_computer", tool: "run_on_computer", args: { command, waitSeconds, timeoutSeconds } })`, but
prefer ops: the server parses the answers and the fold remembers them.

## 3. The pattern that survives real machines — a helper, detached runs, small polls

Install ONE small stdlib script on the machine once (`~/esoul/<app>/helper.py`, sent base64 in a
single command, versioned — bump `HELPER_VERSION` on every change and re-install when the probe's
version differs), then every op is `python3 helper.py <subcommand> --arg …` and the helper:

- **probes** the machine: hostname, `uname -r` (WSL2 = `microsoft` in it), GPU (`nvidia-smi`),
  Pythons, disk, whether the repo/venv/torch exist — one JSON.
- **sets up** idempotently (clone or pull, venv, deps) DETACHED, writing a status file the
  `setup-poll` subcommand reads. Do not install a GPU stack silently — show the exact command for
  the detected CUDA and a "Run it" button.
- **downloads** exactly the files the app names, by expiring grant URLs (`files.readGrant` +
  `fileGrantUrl`, `data-people-files.md` §4), in parallel, skipping same-size files, writing
  `done/total` to a status file.
- **starts** a job detached with `nohup`, records `{pid, log, startedAt, args}` in
  `run_<id>.json`, prints the pid.
- **polls**: `alive(pid)`, the exit code from a `== EXIT n` sentinel the wrapper printed, KEY
  lines chosen by regex (stage headers, verdicts, table rows, errors), the newest log's last four
  lines, the last three error lines — **capped under ~6 KB**. The first poll I wrote was 11 KB and
  came back truncated mid-JSON.
- **stops** by pid; **lists what is live** (a registry) as compact JSON.

The app's op parses the poll into a reading (`stage`, `verdict`, `rows`, `warnings`, `words`)
and dispatches a run-record event when a poll finds the process gone. **While a run is alive the
UI says so everywhere** ("● Running… stage · step · 9 min" on the header, not only inside a
drawer) until a poll records the end; a failed poll ends nothing — the dot turns amber with the
computer's own sentence. The probe also reports a run alive that the app never recorded
(started from a chat, another tab, a terminal) so the app adopts it.

## 4. Real-machine facts that cost a run each

- **WSL2 caps page-locked memory**: eight DataLoader workers die on step one with `pin memory
  thread … CUDA error: out of memory` (reported a line later as "too many resources") with the
  GPU nearly empty. Detect WSL and default to 2 workers; expose the setting; when a run fails
  with that text, say the cure in words.
- **A data folder is never clean**: validate every input file before the job (name what is
  excluded and why); a pipeline that raises on one bad label kills the whole run.
- **Errors ride the poll**: carry the trainer's own error lines, not just "failed, see log".
- Sync inputs before a run; never overwrite a person's fixes with a re-download.
- `claude_task` runs Claude Code on THEIR machine and spends THEIR Claude subscription or key —
  say so; prefer `permissionMode: "no_writes"` for reads.

## 5. Credentials on the machine — the SDK grant, and the one-time door

**A paired computer can already hold a workspace credential.** When the owner pairs it with the
"SDK access" box ticked, or sets **SDK: Read / Write** in the My Computer app, the agent keeps a
credential scoped to THAT workspace (30 days, rotated, revocable in the app or under the
workspace's Access Tokens) at `~/.config/esoul/credentials` and exports `ESOUL_TOKEN` +
`ESOUL_BASE_URL` into every command your app runs there. So `esoul.track`, `esoul-mcp` and the
esoul SDK work in your job with nothing passed — and it can never drive the machine's own
command plane (the credential is refused there by construction). Your op's probe should report
whether the file exists; if not, say "turn on SDK access in the My Computer app". Never ask for
a PAT, never put one in a command.

**A machine that is not a paired computer** (a server of the person's, a device) gets a secret
through a door your app opens for one read:

```json
"routes": { "credential": { "access": "token" } }
```
```ts
// the op: the person pasted the secret into the app → it sits SEALED in a `db` table → mint a one-time door
const grant = await mintRouteToken(ctx, { route: "credential", ttlSeconds: 600, label: "helper" });
await computer(ctx, machine).run(`python3 helper.py credentials --url '${grant.url}'`);   // the URL carries a short-lived bearer, not the secret
// the route: answer the sealed value once, then delete the row → 410 for ever after
```
`grant.url` is on the origin the op was called on — a box's preview domain in the Forge, the
platform after install. The same door, with a longer life, is how a machine PUSHES results back
(`server-and-tasks.md` §3).

## 6. Proving it

- Unit: mock `computer()`; assert the COMMANDS the op issues (the helper subcommand, the args)
  and that a `pending_approval` outcome becomes a `waiting` answer, not a throw; py-compile the
  helper in a test (`String(HELPER_PY)`), never ship a helper you did not compile.
- Live: the preview open on the board (or installed), Auto set by the person, `call_app_tool`
  on `machine_status` → a real hostname; then each step through the UI with `drive_app`.
- Never test on their dataset or their live repo; ask for a scratch directory and say every
  command before a destructive one.
