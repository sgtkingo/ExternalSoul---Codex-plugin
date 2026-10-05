---
name: training-monitor
description: "ExternalSoul's Training Monitor app (`training_monitor`) — the workspace's TensorBoard. Use it whenever a training or fine-tuning job should be watched, compared or judged from the workspace: a Python loop logs with `esoul.track` (mirroring TensorBoard is one class), agents read curves and verdicts with its tools, and a Forge app that trains on the user's own computer wires the machine to the monitor without ever putting a token in a command. Read this before building or driving anything that trains."
---

# Training Monitor — the workspace's TensorBoard

> **Optimising the person's own training code across many runs is a research study, not a monitor.** "Find the best config for my repo", "run ablations" and "which knobs matter": use the `research-study` skill. It runs the experiments on their machine, grades each one against a matched control, and keeps a runs sheet. Its runs still log curves here.

One app instance is a **monitor**: it holds RUNS (a name, a group, config, status, step/epoch,
per-metric curves, sample images, system stats, notes), draws them as a live instrument
cluster, and lets an agent ask "is it improving?" as arithmetic, not vibes. The producer is
Python on any machine — a laptop, a GPU box, a Forge-driven `my_computer` — and logs through
`esoul.track`; the monitor is the record.

## 1. What you are working with

| Fact | Consequence |
|---|---|
| A monitor is found or **created by name** — `track.init(monitor="Training")` reuses the same app forever | one monitor per project or per model family; runs accumulate; name it like a dashboard, not like a run |
| Curves are stored as **bounded sketches** (fixed bucket count whose width doubles; cold runs compacted to 96 buckets) | a 20k-step run costs the same as a 20M-step one; there is **no zoom to a single raw step** — for "the exact loss at step 84,312" keep TensorBoard beside it |
| One event per **flush** (default every 5 s), producer-monotonic `seq` | replays never double-count; a run that crashes shows `lastFlushAt` and reads **STALLED** after a silence |
| `log()` returns in microseconds and never raises; a daemon flushes through a WAL | telemetry can never take a run down; `finish()` (or the context manager) drains — an unjoined exit loses the last frames |
| DDP: rank 0 only by default (`all_ranks=False`) | N ranks logging one scalar would fold N× the sample count |
| `publicSharing` redacts — a share shows curves, never config secrets | still: config is hyperparameters, never keys |
| The `system` panel kind renders in the header rail, not as a panel | don't promise a system panel in a dashboard spec |

The app's tools (minted `<verb>_<monitor name>`): `list_runs`, `read_run {run?}`,
`read_series {series[], run?, maxPoints?}` (≈ 320 points per series max), `compare_runs
{runs[]}` (overlays them on every chart AND reports differences), `analyze_run {run?,
series?}` (improving / plateaued / worsening / steady, deterministic, with the numbers behind
it; `lr`, `grad_norm`, throughput have no goal and read steady/changing), `add_run_note {text,
run?}`, `set_dashboard {dashboard}`. `getStateDescription` names the focused run, up to six
runs with status/progress/last values, and points at those tools.

State (for `readAppState` / the hosted `read_app_state`): `{ runs: RunRecord[], activeRunId,
compareRunIds, dashboard }`; a `RunRecord` is `{ id, name, group?, status, startedAt, endedAt?,
lastFlushAt?, lastSeq, step, epoch?, totalSteps?, totalEpochs?, config, series: Record<name,
BucketSketch>, stats: Record<name, { last, best, bestStep, count… }>, images, system?, notes,
error? }`. Read `stats` for numbers; read `series` only to draw.

## 2. Logging from Python — `esoul.track`

```python
import esoul.track as track
from esoul.track import Dashboard, Line, Tiles, Images, Config, System

run = track.init(
    monitor="Technotron Column Flow",        # the app, by name; created if absent
    workspace="Type 3 columns", project="technotron",   # BY NAME; omit to use the token's own workspace
    name="columns_site_drive_20260921", group="pipeline-columns",
    config={"lr": 1e-4, "seed": 2, "workers": 2}, total_steps=1500,
    dashboard=Dashboard(title="Columns", hero=["val/inst_iou"], panels=[
        Line("Loss", ["loss/*"]), Line("Validation", ["val/*"], y="log"),
        Tiles(["val/inst_iou", "val/count_acc"]), Images("preview/val", per_row=1, span=2), Config("lr", "seed"), System(),
    ]),
    quiet=True,
)
for step, batch in enumerate(loader):
    loss = train_step(batch)
    run.log({"loss/train": loss, "lr": sched.get_last_lr()[0]}, step=step)     # µs; never blocks
    if step % 500 == 0:
        run.log({"val/inst_iou": iou, "val/count_acc": acc}, step=step)
        run.log_images("preview/val", [img_hwc], step=step, captions=["val"])
run.note("plateau after 1k; lr too high?")                                     # pinned to the run
run.finish()                        # status="finished" | "failed"; or `with track.init(...) as run:` marks failure on exception
```

`resume="<run id>"` continues a run from another process (the WAL under `dir` replays first).
`system_metrics=True` (default) reports throughput, ETA and GPU util/memory when torch is
imported. Omit `dashboard` and the monitor infers a layout from the metric names (`inferDashboard`).
`run.set_dashboard(...)` changes it later; the same spec is what `set_dashboard_<base>` takes.

**Credentials** resolve in order: `token=` kwarg → `ESOUL_TOKEN` → `/var/run/esoul/token`
(sandboxes) → `~/.config/esoul/credentials` (INI, mode 0600; `[default]`, or the section named
by `ESOUL_PROFILE`). On a paired computer the agent writes that file itself: `[default]` plus
one `[ws:<workspaceId>]` per granted workspace with its `name`, and `track.init(workspace=
"<name>")` picks the matching profile offline — so two workspaces on one machine never cross.
None → `MissingCredentialsError`; a loop must catch that and run TensorBoard-only, never die.

## 3. Mirroring TensorBoard — the pattern a repo should ship

Do not replace TensorBoard; mirror it. One class the trainer already calls:

```python
class Tracker:                                   # add_scalar / add_image / close → TB AND esoul
    def __init__(self, out_dir, run_name, monitor, group, config=None, total_steps=None, dashboard=None):
        self.tb = SummaryWriter(out_dir); self.run = None; self._pending = {}; self._step = None
        try:
            from esoul._auth import resolve_credentials; resolve_credentials()          # no creds → TB only, say so once
            from esoul import track
            self.run = track.init(monitor=monitor, name=run_name, group=group, config=config or {}, total_steps=total_steps, dashboard=dashboard, quiet=True)
            print(f"[tracking] esoul monitor {monitor!r} group {group!r} run {run_name!r}")
        except Exception as e:
            print(f"[tracking] esoul init failed ({type(e).__name__}: {e}) -> TensorBoard only")
    def add_scalar(self, tag, value, step):
        self.tb.add_scalar(tag, value, step)
        if self.run is None: return
        if self._step is not None and step != self._step: self._flush()      # one log() per step, all tags together
        self._step = step; self._pending[tag] = float(value)
    def add_image(self, tag, img_chw, step):
        self.tb.add_image(tag, img_chw, step)
        if self.run is not None:
            try: self.run.log_images(tag, [hwc_uint8(img_chw)], step=step, captions=[tag])
            except Exception as e: print(f"[tracking] log_images failed: {e}")
    def _flush(self):
        if self.run is not None and self._pending:
            try: self.run.log(self._pending, step=self._step)
            except Exception as e: print(f"[tracking] log failed: {e}")
        self._pending = {}
    def close(self, status="finished"):
        self._flush(); self.tb.close()
        if self.run is not None:
            try: self.run.finish(status=status)
            except Exception: pass
```

Rules it encodes: every esoul call is guarded (telemetry never takes a run down); tags are
batched per step; the honest held-out numbers are logged **in the same process** as the run
(a later process resuming by id once attached them to the wrong run); `close()` drains. Print
the `[tracking]` line — it is what a poll greps to prove the mirror is live.

## 4. From a Forge app that trains on the user's computer — the "Train model" button

The app (built with `forge-app-builder`) orchestrates a `my_computer`; the machine logs to the
monitor by itself. (This is the My Computer path on purpose: `esoul.track` needs the workspace
credential a paired My Computer holds. An app's own device program — forge-app-builder →
`reference/computers.md` — holds no workspace credential; it reports to its app through `p.op`,
and the app's server code passes results on.) Three seams, each already built:

1. **The credential is on the machine already.** When the person paired the computer with the
   "SDK access" box ticked (or set **SDK: Write** in the My Computer app), the agent keeps a
   workspace-scoped credential at `~/.config/esoul/credentials` and exports `ESOUL_TOKEN` into
   every command the app runs there. Nothing to paste, nothing in a command. Check it in
   `machine-status` (`test -s ~/.config/esoul/credentials`); if it is missing, the honest
   answer is "turn on SDK access in the My Computer app" — never ask for a PAT. (A machine
   that is NOT a paired computer still gets the one-time `token`-route hand-off,
   `my-computer.md` §5.)
2. **First click creates the monitor; every later run lands in it.** `track.init(monitor=NAME)`
   finds-or-creates the monitor app BY NAME, so the job itself does the first-time setup: pass
   the name from the app's settings (`--monitor "Technotron Column Flow"`) and the dashboard
   spec with the first run. The app remembers the monitor's `nodeId` once it exists: after the
   first run, `useWorkspaceTools(state).listApps()` → the `training_monitor` whose
   `instanceName === NAME` → a `settings_changed { monitorNodeId }` event. Open it for the
   person on that first click (a UI action may bring an app up; a background task may not).
   Later runs: `group` = the sweep, `name` = the run; the monitor overlays them.
3. **The app reads the monitor, it does not re-log it.** Grants
   `"training_monitor:list_runs"`, `"training_monitor:analyze_run"`, `"training_monitor:read_run"`;
   `callWorkspaceTool({ appType: "training_monitor", tool: "analyze_run", args: { run } })`
   from an op — or `readAppState(monitorNodeId)` and read `stats`. Show the verdict beside the
   app's own run record; link "open the monitor". The helper's log poll (30 s) is enough; the
   monitor updates itself.

A proof line for the drive: the run's log carries `[tracking] esoul monitor '<name>' … run
'<run>'` AND `list_runs_<monitor>` shows that run within one flush interval. Both, or the mirror
is not live.

## 5. Driving it as an agent (chat, MCP, agent-builder)

- "How is training going?" → the describer already says; `analyze_run` for the verdict per
  metric; `read_series {series:["val/loss"], maxPoints: 60}` only when you must see the shape.
- "Did B beat A?" → `compare_runs {runs:["B","A"]}` (focused first) — it overlays AND reports.
- "Why did it die?" → `read_run` (`error`, `lastFlushAt`, notes) then the machine's log through
  the app that started it.
- Leave a finding on the run: `add_run_note`. Change the layout: `set_dashboard` with the same
  spec shape Python's `Dashboard.to_spec()` makes.
- Never quote a curve from memory; never call a run "converged" without `analyze_run`'s
  numbers; a run with no flush for minutes is STALLED — say so, don't call it running.

## 6. Building a monitor-shaped feature of your own

The general primitives are reusable: `src/lib/series/bucket-sketch.ts` (any live series into
O(1) state), one event per flush with a producer `seq` (`esoul/stream.py`), and the instrument
kit (`BandChart`, `MetricTile`, `ProgressRing`, `StatusDot`, `ImageStrip`). A Forge app cannot
import those directly (the import wall) — ask for them through `esoul-sdk` (`chartSvg` is
already there) and prefer sending the metrics to a real monitor instead of rebuilding one.
