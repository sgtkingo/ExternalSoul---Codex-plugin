---
name: math-explainer-video
description: "Make a narrated animated explainer VIDEO that teaches a technical or mathematical idea — a concept, formula, theorem, proof, distribution or method — with real manim animation of the maths itself, formula cards, a voiceover synced to the shots, and one mp4 delivered. Dark 3blue1brown look by default; handles a requested length (\"a 5 minute video\"). Triggers on \"make a math explainer video about IID datasets\", \"animate the central limit theorem\", \"explain eigenvalues in a 3 minute video with narration\", \"video explaining the Hessian\". Requires an ExternalSoul MCP connection (list_workspaces / get_app_tools / call_app_tool / create_app) to a workspace you own that is exposed with 'tools' access; it creates the sandbox, video editor and canvas it needs. NOT for animating a story or an essay, and NOT for a slide deck."
---

# Explain a technical idea as a narrated animated video

You are driving an ExternalSoul workspace over MCP. Everything you do to an app is
`call_app_tool(workspace_id, app_id, tool_name, arguments)`.

## WHAT THIS COSTS

Manim rendering is FREE and deterministic. Narration is pennies. Do NOT use a video model
(`generate_video`) for maths: it bills ~$0.40/second and cannot draw a defined motion. **If the
motion can be written as a function, write the function.**

## THE COMPANION FILES — read them, they are the craft

Five vocabularies ship next to this file. Read a file when its beat comes up; do not try to
recall its contents.

- `reference/drip-style.md` — the DEFAULT look for maths-in-motion: dark glow, height-coloured
  surfaces, an animated character. Read it at step 1 and follow it instead of step 2.
- `reference/punch-style.md` — the look for SYSTEMS/products/costs/comparisons: black
  infographic, neon pills/stamps/gauges, mono letterspaced caps, hero numbers, Gemini image
  inserts. Read it at step 1 when the subject is a system, and follow it instead of step 2.
- `reference/manim-motion-craft.md` — HOW motion feels: easing, stagger, entrances, emphasis,
  transform choice, updaters, the no-LaTeX counter.
- `reference/manim-2d-set-pieces.md` — the classic 2D shots: linear-map grid, Riemann refinement,
  graph stories, moving points, camera zooms, callouts.
- `reference/manim-3d-scenes.md` — real 3D: surfaces, solids, trajectories, orbiting cameras, ML
  architecture shots.
- `reference/narration-first.md` — **read this at step 1 for any narrated film.** Size the
  picture to the speech, never the reverse — the workflow that prevents pooled dead air.
- `reference/sandbox-mechanics.md` — how the code sandbox actually behaves: the 60-second rule,
  detached rendering, the restart lifecycle, getting files in and out, seeing your own output.

## STEP 0 — find the apps you can actually drive

`list_workspaces` for the workspace id, then read its apps. You need three: a **code sandbox**
(`e2b_sandbox`) for manim, a **video editor** (`video_editor`) for assembly, and — on the LIGHT
theme only — a **drawing canvas** (`tldraw_canvas`) for typeset formula cards.

`get_app_tools` on each to learn its EXACT per-app tool names. They are suffixed with the app's
base name (`run_code_<base>`, `draw_on_page_<base>`, `add_clip_<base>`). Never guess a tool name;
read it.

**If an app type is missing, create it — but offer it in the same call:**

```
create_app({ workspace_id, application_type: "e2b_sandbox", name: "...", offer: true })
```

`offer: true` is load-bearing and easy to miss. Without it the app IS created but stays invisible
over MCP ("Created. It is NOT offered over MCP yet") — `list_workspaces` won't show it and
`call_app_tool` refuses it as `not_visible`. If you already created one without the flag, do NOT
create a second: creation is idempotent on (workspace, type, name), so re-issue the SAME call with
`offer: true`.

Then `get_app_tools` on it and start calling. **The new app's tools are callable immediately, in
this same session** — `call_app_tool` is one static tool that takes `app_id` as an argument, so
nothing in the MCP tool list changes and there is nothing to refresh. (Guidance written for
ExternalSoul's in-app chat tells you to call `resume_session('vercel')` after adding an app. That
hazard does not exist on this surface; ignore it.)

Two refusals mean something you must act on rather than retry:

- *"exposed read-only"* / `no_tools_access` — the workspace is exposed without `tools` access.
  Reads work, tool calls never will. You own this storefront: flip that workspace to `tools`
  access in its settings, or build in one that already has it. Retrying will not help.
- `policy_never` — that app type opts out of public sharing entirely (slideshow, contacts). It is
  unreachable over MCP however it is configured. Pick a different app or do that part in-app.

**You are the owner of this storefront** — `create_app` is owner-only and you have it, so a
missing app is never a reason to stop or to repurpose an unrelated app. Create it and carry on.

If your connection has NO `call_app_tool` at all — only the SDK-style tools (`read_app_state`,
`dispatch_event`, `spreadsheet_*`) — then this pipeline is not reachable from here. Say that
plainly instead of improvising; the sandbox and video editor cannot be driven by raw events.

A video editor that already holds a timeline: clear it clip by clip with `remove_clip` before
building. A leftover clip is nearly invisible and silently ends up in the export.

## STEP 1 — plan the FILM: length, arc, beats, theme

**LENGTH.** If the user named one, plan to it: beats ≈ minutes × 5. No stated length → 2–3
minutes (10–14 beats).

**Ceiling — 40 narrated shots per film.** `narrate_script` takes at most 40 lines, and sync pairs
line i with shot i (one line per shot; the counts must match). So "beats ≈ minutes × 5" holds up to
~8 minutes; past that the shots simply run LONGER — a 20-minute film is ~40 shots at ~30s, which
reads as documentary pacing, not a defect. Plan a long film as fewer, longer beats; do NOT cram two
ideas into one line to beat the cap (that breaks the one-line-per-shot sync). Genuinely needing
100 short beats on a long film is a platform limit to raise, not something to force here.

**NARRATION-FIRST — the load-bearing order (read `reference/narration-first.md`).** Speech has a
rate you cannot control; picture is elastic. So SIZE THE PICTURE TO THE SPEECH, never the reverse:
write the script, CALIBRATE the voice's real rate (generate one line, measure — or
`narrate_script estimateOnly:true`, which returns the measured rate + a per-shot fit table), then
set each scene's length from its line's measured seconds. **Never hardcode a beat-duration table
before the narration exists** — that pooled 266s of dead air into shot tails once. The old
"2.4 words/sec" heuristic was ~20% slow for onyx (measured 2.89); the number depends on the voice
and the delivery, so calibrate, don't assume.

**ARC.** A film is a story, not a list of facts. Open with the question or the tension (what
breaks or surprises without this idea), build the intuition IN MOTION before any formal card, end
with the payoff — the moment the idea pays rent. Write the beat plan as that arc: one sentence
per beat describing what is SEEN.

**MOTION FLOOR.** Animations carry the story; cards carry formulas. Alternate them, keep cards
well under half the runtime, and treat a beat whose animation is "fade in and hold" as a card in
costume — give it real motion (a camera move counts).

**THEME — DARK DRIP is the default for maths-in-motion.** Read `reference/drip-style.md` and
follow it INSTEAD of step 2: glow on near-black, height-coloured surfaces, an animated character.
That is the "beautiful" / "cinematic" / "3blue1brown" look, and it ships unless the maths forbids
it — or the SUBJECT is a system rather than a function.

**PUNCH for systems, products, costs, comparisons, pipelines.** Read `reference/punch-style.md`:
near-black stage with NO grid, neon-glow pills/cards/stamps/badges/gauges/checklists, mono
ALL-CAPS letterspaced labels, huge hero numbers, one or two meaning-coded accents per frame — the
black-infographic register. A plant diagram, a price comparison, a request flow, an architecture
walkthrough all look BETTER in punch than in drip (the MLE plant film's tanks-and-clarifier beats
were this genre). It also carries the **Gemini image arm** — generated photographic inserts
mounted in a card and annotated by manim vector text. One caveat on THIS surface: `generate_image`
is an esoul chat/agent tool, not exposed over the MCP storefront — have an esoul chat or invoked
agent generate the images first, then use their fileIds (workspace images list via `list_files`).

Heavy formulas no longer force the theme. The old rule — "a nested integral or a matrix needs
LaTeX, and LaTeX typesets only on a light tldraw card, so that film must go light" — rested on
LaTeX being unavailable in the sandbox. It is 56 seconds away (step 3), and `MathTex` produces
ordinary mobjects you can `set_color` to your palette and place on a dark background like anything
else. So a dark drip film CAN carry a nested integral natively.

**And when a formula resists Unicode, change the MATHS before you change the theme.** This is the
move, not a consolation prize: a Fourier film looks light-theme because `e^{-2πixξ}` has no honest
Unicode — but writing the same idea as `cₖ = ⟨f, eₖ⟩` over sines and cosines keeps it dark AND is
more intuitive for the audience. Reformulating usually improves the film. `scripts/glyph_check.py`
tells you in ten seconds whether the premise is even true.

Go LIGHT PAPER (step 2: LaTeX cards on white) when you want that aesthetic, or when the film is
mostly formula cards and the canvas's measured-box layout is genuinely easier than composing them
in manim. Not merely because the maths is dense.

Say which theme you picked. **Never mix — a film has ONE theme.**

## STEP 2 — draw the formula cards (LIGHT PAPER theme only)

One PAGE per card via `add_drawing_page`, then `draw_on_page`. Every card starts with a frame
rect as the FIRST shape in the array:

```json
{"kind": "rect", "x": 0, "y": 0, "w": 1232, "h": 672, "color": "white", "fill": "semi"}
```

That size is load-bearing. The snapshot pads 24 canvas px per side then supersamples 2×, so
1232×672 renders to exactly 2560×1440 = 16:9. **Any other size gets BLACK BARS** from the
export's pad filter.

Lay out inside it at left margin x=140: a small grey ALLCAPS kicker, the `{"kind":"latex"}`
formula, an optional grey note beneath.

`fill:"semi"` is opaque PAPER white and HIDES what is behind it; `fill:"solid"` is the pale tint.
Backwards makes a shaded region read as empty.

`draw_on_page` returns each equation's MEASURED box and an overlap report. Read it; if two
collide, move one and redraw with `clear:true`.

Then `snapshot_drawing` each page with `saveAs` to get a workspace fileId — the snapshot comes
back to you as an IMAGE: **look at every one**. Schema-valid is not renders-correctly, and looking
is what catches a formula running off the edge. The measured boxes + overlap report are the
confirming half: assert every box sits inside the 1232×672 frame. A saved card can be re-checked
later with `view_image`.

## STEP 3 — the manim scenes

`run_code` in the sandbox. First check the environment: `import manim, av`, and
`shutil.which('latex')`.

- The sandbox comes up BARE — manim is NOT preinstalled. `pip install manim av pillow scipy`; the
  manim wheels land in ~26s.
- **LaTeX is not installed either, but it is 56 seconds away.** The box is Debian 12 with
  passwordless sudo (verified 2026-08-10):

  ```bash
  sudo apt-get install -y --no-install-recommends texlive-latex-base texlive-latex-extra dvisvgm
  ```

  ~56s, 255MB, and `MathTex` then renders — measured end to end, `manim -ql` exit 0 with a real
  mp4 out. Fire it DETACHED alongside the pip install at the very start, before you write a single
  scene; both together are ~82s against a job that will spend 10–30 minutes rendering.

  Older guidance (including parts of the reference files) says LaTeX is simply unavailable. That
  described the cold image, not a limit. If you skip the install the no-LaTeX idioms still hold —
  `Text` (Pango) captions, formulas on cards, and the `DecimalNumber`/`get_graph_label` crashes
  the reference files warn about are all real WITHOUT LaTeX.
- Set `config.background_color` to your theme's background — `"#F9F9FB"` paper, or the drip
  skill's `"#0B0E14"`. Manim defaults to pure black, which matches neither.

**Six rules that each cost a full render cycle to learn:**

1. **NEVER `always_redraw` a Surface.** Rebuilding a 144-quad mesh across ~480 frames outruns the
   sandbox lifetime. Use `Transform(surf, mk(a2,b2))` between two prebuilt meshes of equal
   resolution — same picture, ~10× faster. 2D `Axes` + `axes.plot()` is cheap: there
   `always_redraw` with a `ValueTracker` is fine and is the natural way to animate a parameter.
2. **Captions must be registered with `add_fixed_in_frame_mobjects`, and RE-REGISTERED after any
   `.become()`** — fixed-in-frame belongs to the individual glyph submobjects, so `.become()`
   silently drops it and half a sentence orbits with the camera. Never build a caption inside the
   animation call, and never `always_redraw` one.
3. **`checkerboard_colors=False`, not `None`** (None throws).
4. **Camera azimuth is load-bearing** for saddle-like surfaces: sighting along a principal
   direction of `z = x² − y²` collapses it to a pinched bowtie. About −28° keeps both arms open;
   −52° does not.
5. **THE FRAME CROPS, it never shrinks.** Keep every mobject inside |x| ≤ 6.5, |y| ≤ 3.5. Axes:
   `x_length ≤ 11`, `y_length ≤ 6`, labels placed INTO the frame (`next_to` the tip pointing
   inward) — the default label position at a near-full-frame axis tip is already outside the
   safe area and ships half-clipped.
6. **ONE OCCUPANT PER BAND.** Title band (top ~1.2 units), field (middle), caption band (bottom).
   A formula never enters the top band while a title persists — the title FadeOuts first, or the
   formula lives in the field. Stacked text through a title is a shipped-defect class, not a
   style choice.

START FROM THIS SKELETON (light theme; the drip file has its own). It obeys all four rules;
deviate only with a reason.

```python
from manim import *
import numpy as np
PAPER, INK, HOT, GREY, DARK = "#F9F9FB", "#3A57D8", "#E03131", "#7C8794", "#1D1D1F"
config.background_color = PAPER

def hud(txt, size=32, color=DARK):
    return Text(txt, font_size=size, color=color).to_edge(DOWN, buff=0.5)

def swap(scene, lbl, txt, **kw):
    # Re-word IN PLACE, and RE-REGISTER: .become() swaps the glyph
    # submobjects that carried the fixed-in-frame exemption.
    scene.play(lbl.animate.set_opacity(0.0), run_time=0.25)
    lbl.become(hud(txt, **kw)); lbl.set_opacity(0.0)
    scene.add_fixed_in_frame_mobjects(lbl)
    scene.play(lbl.animate.set_opacity(1.0), run_time=0.25)
    return lbl

def mk(a, b, R=1.9, ZS=0.38, RES=12):        # z = ZS*(a x^2 + b y^2), wireframe
    return Surface(lambda u, v: np.array([u, v, ZS*(a*u*u + b*v*v)]),
                   u_range=[-R, R], v_range=[-R, R], resolution=(RES, RES),
                   fill_opacity=0.0, stroke_width=1.9, stroke_color=INK,
                   checkerboard_colors=False)

class Demo(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=62*DEGREES, theta=-28*DEGREES, zoom=1.25)
        surf = mk(1, 1); self.add(surf, Dot3D(ORIGIN, radius=0.09, color=HOT))
        lbl = hud("both curvatures positive")
        self.add_fixed_in_frame_mobjects(lbl)          # register ONCE, here
        self.wait(1.2)
        lbl = swap(self, lbl, "now one goes negative")  # caption announces
        self.play(Transform(surf, mk(1, -1)), run_time=3)   # NOT always_redraw
        self.wait(1.1)
```

**FILL THE FRAME — the defect no correctness check catches.** A diagram can be geometrically
perfect, unclipped, correctly coloured, and still *wrong*: 31% of frame width, unit vectors at 7%,
two-thirds empty background. Every automated check passes; the viewer sees a postage stamp.

The cause is a default, not carelessness: `Arrow(ORIGIN, RIGHT)` and `NumberPlane(x_range=[-8,8])`
put one data unit on one manim unit, and manim's frame is only ~14.2 units wide. So build a stage
with an EXPLICIT scale instead of inheriting 1:1 —

```python
class Stage:                       # data space -> manim space, scale chosen ONCE
    def __init__(self, unit=2.6, origin=ORIGIN): self.u, self.o = unit, origin
    def p(self, x, y): return self.o + np.array([x*self.u, y*self.u, 0])
    def vec(self, x, y, **kw): return Arrow(self.o, self.p(x, y), buff=0, **kw)

S = Stage(unit=2.6)                # a unit basis vector is now ~18% of frame width
```

Targets, both one-line measurements from a still (`scripts/verify_frames.py` reports them): live
area **≥45% of frame width**, centred within ~5%; a unit basis vector **≥10% of frame width**.
Pick the scale per scene deliberately; never let it default. (LIVE is measured on the CONTENT
hues, not ink-vs-background — the drip grid spans the whole frame by design, so an ink mask read
~99% on every scene and taught nothing; the ambient DIM grid is excluded, and filling the frame
is no longer flagged as "too wide".)

**DEEPEN BY REFERENCE.** HOW the motion feels → `reference/manim-motion-craft.md`. The classic 2D
shots → `reference/manim-2d-set-pieces.md`. Real 3D → `reference/manim-3d-scenes.md`.

**RENDER DETACHED** — a blocking manim cell dies at the client timeout and takes the subprocess
with it:

```python
subprocess.Popen(['bash','-lc','setsid nohup /home/user/r.sh > /home/user/r.log 2>&1 < /dev/null &'],
                 start_new_session=True)
```

Put `set -euo pipefail` at the top of `r.sh` (else a failed render still writes its success
marker — a green light over a red run); append each finished filename to a PROGRESS file; SKIP
anything already on disk so a relaunch RESUMES; poll with `list_files`, which reads the disk and
does not need the blocked kernel. Full long-job discipline: `reference/sandbox-mechanics.md`.

Render `-ql` first for ALL scenes, build one contact sheet, and LOOK at it (step 5) — then run
the frame assertions over the same draft: a FLAT verdict means a scene rendered nothing, and
catching either at 480p15 costs minutes instead of a full final pass. Only then render `-qm`
(720p30) finals.

**THE SANDBOX RESTARTS AND WIPES `/home/user`**, roughly every 15–30 minutes, pip installs
included. Save clips the moment they finish — never defer to the end (the VM can wipe first). But
you don't need one call per clip: `save_files_to_workspace([{filePath, saveAs?}, …])` saves each
poll's newly-finished clips in ONE call and **returns each file's `durationSeconds`** — keep those,
they go straight into `add_clips` as `sourceDuration` (below). On a reset, re-render the missing
ones and re-save with `overwrite:true` so a retry replaces rather than spawning `_1/_2` duplicates.

**Save `film.py` too, every time you change it.** Clips are re-derivable from the source; the
source is not re-derivable from the clips. Running a 30-minute job with the only copy of 25KB of
scene code on a VM that wipes itself is the one unforced way to lose everything. On a reset:
reinstall, re-fetch the source from the workspace, re-render only what is missing.

**Restyle with an overlay module, not a rewrite.** A second file that does `from film import *`
and redefines only the scenes that change is cheap, and it keeps the original renderable for
comparison.

## STEP 4 — assemble: a budgeted, resumable sequence

**Budget the calls BEFORE you start.** "Four calls" is true only of narration; the real cost is
a handful of `save_files_to_workspace` batches (one per poll) + one `add_clips` + narrate + (maybe)
measure + sync + export. Compute that up front and make every step RESUMABLE and idempotent (name
outputs per iteration, skip-if-exists), so hitting a ceiling at 80% costs a turn, not the work.
`add_clips` batches every add into one call; `save_files_to_workspace` batches the saves.

**Add the clips MEASURED.** `add_clips` accepts `sourceDuration` per video shot — pass it, using
the `durationSeconds` each `save_files_to_workspace` handed back. A clip that arrives measured needs
no probe, which is what lets you skip the whole measuring export below. (Images carry `imageSeconds`
instead; narration lands measured automatically — `narrate_script`/`generate_speech` return real
seconds and stamp them.)

Then the soundtrack and timing is this sequence:

1. **`narrate_script(lines)`** — the WHOLE voiceover in ONE call, one line per beat. Lengths come
   from narration-first calibration (step 1), NOT a hardcoded budget. **Price it first with
   `estimateOnly:true`** (returns the measured rate + per-shot fit table + predicted silence) and
   pass `maxUsd` on the real call — always, on every billed call. Long scripts run in the
   BACKGROUND: the result carries a `jobId` — poll `narration_job` until `status=done`. Each line
   comes back with its real `seconds` (it landed measured — no probe needed for narration).
2. **`export_timeline`** once, to MEASURE (probes every clip, writes real durations back). Runs in
   the background too; poll `read_timeline` for `exportJob.status=done`. **SKIP THIS ENTIRELY** when
   every video shot already carries `sourceDuration` (you passed it above) — narration is already
   measured, so with the video measured too there is nothing left to probe: go straight to sync.
   Skipping it deletes an 11-minute encode on a long film.
3. **`sync_narration_to_shots`** — deterministic and free: HOLDS cards, SLOWS a manim clip its
   line outruns (floor 0.65×), and with `shrink:true` SPEEDS a clip its line underruns (≤1.35×) —
   use `distribute:"center"` so residual slack reads as pacing. It reports its SILENCE budget;
   a line even the floor cannot fit returns a word budget — rewrite THAT line and re-narrate (only
   the reworded line re-bills; reused lines are free).
4. **`export_timeline`** again.

**Done means ALL of:** `warnings` empty; the silence budget acceptable (<~12%); length matches
sync's total; within ~10% of any requested length — short means ADD BEATS, never pad holds.

### Long-job discipline (the tools enforce most of this now)

- **A timeout is not a failure.** Narrate and export return a `jobId` and finish server-side.
  After a timeout, WAIT until the job reports `done` — do not re-call after a single check. A
  concurrent second call reads stale state; the in-flight lock returns the running jobId rather
  than duplicating, but don't lean on it — poll.
- **Keep retry arguments BYTE-IDENTICAL.** The idempotency key hashes (scriptId, index, voice,
  instructions, text) — adding an optional `trackId` on a retry once re-billed 14 lines. It no
  longer does (trackId is out of the key), but the habit is the point: change nothing on a retry.
- **Use the `trackId` that `add_audio_track` RETURNS.** Passing a label string where an id is
  expected used to materialize a SECOND track (writer and reader diverged). Track params now
  accept id-or-exact-label, but the returned id is the unambiguous handle.
- **`dedupe_track(trackId)`** is the one-call guarantee of no duplicate narration — run it after a
  messy narrate session rather than hunting clips by hand.

**Never hand-compute offsets or speeds** — that arithmetic lives in `sync_narration_to_shots`, and
by hand is how narration drifted in every early film. (You never need to estimate a narration
length: `narrate_script`/`generate_speech` return real `seconds` and the clip lands measured.)

## STEP 5 — LOOK at it, then PROVE it

**You can see your own renders (since 2026-08-10).** Any image a sandbox run writes under
`/home/user` comes back to you as an actual image — vision, not text. Two hard limits shape how
you use it:

- **At most 3 images per tool result, downscaled to ≤1280px.** Never dump nine frames as nine
  files — build ONE contact sheet and look at that. This is why the sheet exists.
- **Videos never come back directly**, on any surface. Frames sampled into a sheet are how a film
  is ever seen.

`view_image(workspace_id, file)` shows any image FILE already saved to the workspace — use it to
re-look at cards or an old sheet without re-running code; `list_files(images_only: true)` finds
them.

**If an image fails to arrive** (`imagesDropped` in the result, or no image where one was
expected), say so and fall back to the measurement battery below — never claim you looked at
something you did not see, and never proceed on faith.

**Looking is necessary, not sufficient.** The eye catches what no assertion anticipates (a scarf
crowding a chin, a mood that is wrong); the battery measures what a glance cannot (43% vs 55%
frame fill, a silent beat — no LOOK can hear). A film ships when both pass.

**And when the film asserts a COMPUTED result, verify the computation before you animate it** — a
wrong number rendered cleanly ships 200 OK, and a beautiful lie is worse than an ugly error because
nobody looks again. For any data- or model-driven explainer (a solved system, a fitted curve, a
simulated plant) the claims are a separate artifact to check, harder than the pixels:

- **Prove convergence, don't assume it.** Near a critical point a quantity can move so slowly that a
  fixed integration horizon hasn't settled — a bisection then reads "not yet" as "never" (a washout
  SRT off by 34% until the check became the exact eigenvalue crossing, not a long run).
- **Never tune a tolerance until it passes.** If the residual is real physics (tanks-in-series vs a
  well-mixed model), loosen the bound and SAY WHY; if it's a bug, fix the bug. Delete your own "the
  sign is consistent" assertion the moment the data contradicts it — the assertion was the guess.
- **A silent fallback that zeroes a value you asked to see IS the bug**, the same rule as everywhere
  else in this platform. An ungated decay term drove dissolved oxygen negative and silently zeroed
  the O₂ penalty the user wanted shown — it read as "no penalty" instead of "penalty uncomputed."
- **Let the model surprise you.** The most honest beat is often one you didn't outline — a soft
  oxygen switch putting 17% of denitrification inside the "aerobic" tank — because it is what the
  equations DO, not what you expected. Follow the model, then explain the surprise.

Keep the verification harness (the model + its checks) as a workspace file beside the film, so every
claim is auditable, not merely asserted.

### 0. The battery — shipped, do not reinvent it

`scripts/verify_frames.py` and `scripts/glyph_check.py` are in this skill. They were written from a
real film's post-mortem; every check exists because something shipped broken without it.

Get them into the sandbox by reading the file and writing it there base64-encoded:

```python
import base64
open('/home/user/verify_frames.py','wb').write(base64.b64decode("<paste base64 of the file>"))
```

**Encode it — do not paste the source into a Python string.** A non-raw string turns `\f` into a
formfeed and `\int` into a warning, and you will debug LaTeX or manim for an hour over a file the
shell corrupted in transit. Then:

```bash
python verify_frames.py film.mp4 --marks 3,12,25,37 --theme dark   # mid-beat seconds
python verify_frames.py card01.png --card --theme dark
python glyph_check.py "⟨u,w⟩=0" "θₜ₊₁=θₜ−η∇L"     # BEFORE committing to a dark film
```

What it prints, and why each line exists:

- **FLAT** — a uniform frame: that beat rendered nothing.
- **BARS** — pure-black border strips: a card not authored at 1232×672.
- **LIVE** — live-area extent as a % of frame. **This is the one that catches the defect every
  other check passes**: a diagram that is geometrically perfect and *too small*. Target 45–65% of
  frame width, centred within ~5%. 31% wide with two-thirds empty background is a defect the
  viewer sees and no correctness check flags.
- **BANDS** — contiguous horizontal ink bands with y/x extents, plus glyph-cluster counts. Clean
  gaps prove no collision; margins prove no overflow; a cluster count that moves (`⟨u,w⟩=0` should
  be 7) means a glyph silently vanished or fell back.
- **PALETTE** — pixels near each theme hue per beat. Proves colour continuity across cuts AND
  tracks the argument: a hue should first APPEAR on the beat that earns it (red when the second
  basis vector enters, green when projection first recovers a coordinate).
- **AUDIO** — per-beat narration RMS. A silent beat is invisible to every pixel check.
- **EDGE** — content ink touching a frame border: something got CROPPED (a half-missing axis
  label looks exactly like this). Distinct from BARS, which is pure-black padding.
- **CONTRAST** — the darkest-vs-background check for the dark-text-on-dark-background class. Per
  ink band, the peak luminance of a DENSE (text-like) cluster; a band with substantial ink whose
  peak barely rises above the background is near-invisible text. (Faint grid lines are sparse, so
  they don't trip it — calibrated.) The PRIMARY guard is still in-scene (below); this is the
  backstop for a frame that shipped without one.

**The tight loop lives IN THE SCENE, not in the pixels.** Four failure classes recur — **labels
colliding on dense/converging data** (Bohr levels bunch up, close spectral lines overlap), **dark
text on a dark background**, **text straddling a shape's edge** (an SRT label across a tank
border), and **sibling shapes colliding** (a clarifier overlapping the aerobic box; a chart drawn
over a diagram). All are free to catch BEFORE rendering, because manim knows its own boxes and
colours — and the guard is now AUTOMATIC and CONTINUOUS, not a call you can forget: subclass
**`GuardedScene`** (set-pieces FRAME DISCIPLINE) instead of `Scene`, and EVERY `wait()` walks the
whole scene graph and raises on overlap, edge-straddle, shape collision, off-frame, or
low-contrast — naming the exact offender, so the `-ql` draft FAILS the instant a held frame is
wrong. Nothing to remember to pass; things that MOVE mid-scene are re-checked at every beat. For a
beat holding two composites (diagram + chart), allocate halves first and prove it with
`guard_regions(diagram, chart)`. Fix the layout (thin labels / leader lines / zoom inset;
inside-or-clear, never straddling; respace or nest) or the colour (→ TXT), re-render.
Text-on-text is deliberately NOT pixel-checked (anti-aliasing defeats it); the in-scene guard
prevents it, the contact-sheet LOOK is the catch-all for what geometry can't judge.

**Mask on SEMANTIC colour, not on "ink".** If you write your own check, match the caption's GREY
against the grid's DIM rather than "anything non-background" — a `NumberPlane` spans the full
frame, so its grid lines sit inside the caption band and a generic ink mask cries overflow on
exactly the scenes you care most about.

### 0. VERIFY THE PIXELS, not the path — and never glob the quality dir

Two silent shippers, both caught only by measuring the file itself:

- **A draft copied into finals.** A render that globs `media/videos/<mod>/*/<scene>.mp4` sorts
  `480p15` BEFORE `720p30` and silently copies DRAFTS into `final/`. Every other check passes; a
  soft 480p film nearly ships. **Construct the final path EXPLICITLY from the quality flag, never
  glob the quality directory**, and after assembling assert the dimensions:
  `verify_frames.py FILM.mp4 --marks …` prints a **DIMS** line — `WRONG` if it is not 1280×720.
  Exit codes and file sizes never catch this.
- **A scene built on the wrong data.** Before a scene DISPLAYS model outputs (reconstructions,
  feature maps, exemplars), build a full-RESOLUTION contact sheet of the ARRAYS THEMSELVES and
  look at it, and score exemplars quantitatively (per-index MSE) to pick a representative-GOOD
  one — **never default to index 0** (it was the worst of sixteen once). A thumbnail-sized scene
  contact sheet will not reveal a wrong digit; data panels need native-resolution inspection.

### 1. Read the tools that MEASURE

- `draw_on_page` returns each equation's measured box and an overlap report.
- `export_timeline` returns real probed durations and a `warnings` array.
- `sync_narration_to_shots` returns word budgets AND a silence budget.

A warning you did not read is a defect you shipped. None of these need vision.

### 2. Assert in the sandbox and PRINT the verdict

Decode frames and check numbers, then print a table — the text comes back to you intact:

```python
import av, numpy as np
c = av.open("/home/user/f.mp4"); fps = float(c.streams.video[0].average_rate)
want = {int(t*fps): t for t in MARKS}          # MARKS = mid-point second of each beat
for i, f in enumerate(c.decode(video=0)):
    if i in want:
        a = np.asarray(f.to_image().convert("L"), dtype=np.float32)
        flat = a.std() < 3.0                    # uniform frame = dead scene / black hole
        bars = a[:, :8].mean() < 4 and a[:, -8:].mean() < 4   # pillarbox suspicion
        print(f"t={want[i]:6.1f}s  mean={a.mean():6.1f}  std={a.std():6.1f}  "
              f"{'FLAT ' if flat else 'ok   '}{'BARS' if bars else ''}")
    if i > max(want): break
c.close()
```

`std < 3` on a beat means nothing rendered there. Side columns near zero on a light-theme film
means the pad filter added bars — a card that was not authored at 1232×672.

### 3. Glyph preflight — do this BEFORE rendering any Unicode formula

The drip theme puts formulas on dark cards as Pango `Text`, and a codepoint no installed font
covers renders as an empty tofu box — silently, in the final film. Check coverage first; this is
deterministic and needs no eyes (`pip install fonttools`):

```python
from fontTools.ttLib import TTFont
import glob
CHARS = "⟨⟩∫Σ√≠≈⊥→θ∇·×∞✓ₜ₊₁₀₂ᵢⱼₖ"
have = {c: [] for c in CHARS}
for path in glob.glob("/usr/share/fonts/**/*.tt[fc]", recursive=True):
    try:
        f = TTFont(path, fontNumber=0, lazy=True)
        fam = f["name"].getDebugName(1) or path       # the name Text(font=...) takes
        for c in CHARS:
            if ord(c) in (f.getBestCmap() or {}): have[c].append(fam)
        f.close()
    except Exception:
        continue
for c in CHARS:
    print(f"{'OK  ' if have[c] else 'TOFU'} U+{ord(c):04X} {c}  "
          f"{have[c][0] if have[c] else '— NO installed font has this glyph'}")
```

Any TOFU line means that character will be a blank box on screen. Fix it by choosing notation the
fonts cover, or install a font that does and pass `font="<family>"` to `Text`. Never ship a
formula whose glyphs you have not cleared.

### 4. The contact sheet — build it, look at it, save it

Build the contact sheet anyway, `save_to_workspace` it, and TELL the user its file name — they can
look in seconds, and one human look is worth ten blind re-renders. If something matters and you
cannot verify it, ASK rather than assert.

```python
import urllib.request, av
from PIL import Image
urllib.request.urlretrieve(URL, "/home/user/f.mp4")
c = av.open("/home/user/f.mp4"); fps = float(c.streams.video[0].average_rate)
want = sorted(int(t*fps) for t in MARKS)     # MARKS = mid-point second of each beat
grab = {}
for i, f in enumerate(c.decode(video=0)):
    if i in want: grab[i] = f.to_image()
    if len(grab) == len(want): break
c.close()
ims = [grab[i] for i in want if i in grab]
tw = 300; th = int(ims[0].size[1]*tw/ims[0].size[0]); cols = 4
sheet = Image.new("RGB", (tw*cols, th*((len(ims)+cols-1)//cols)), "white")
for n, im in enumerate(ims):
    sheet.paste(im.resize((tw, th), Image.LANCZOS), ((n % cols)*tw, (n//cols)*th))
sheet.save("/home/user/sheet.png")
```

Then `save_to_workspace` it and name it in your reply.

### 5. Does the film BUILD?

Vision is not what tells you whether the story works; your own beat plan is. Re-read it as a
stranger would: does each beat earn the next, or is it a list of facts? A beat that only restates
its card is dead weight — cut it or re-animate it. That judgement needs no pixels.

**DELIVER, don't describe:** report the file name, the duration, the theme, what you verified and
HOW (measured / asserted / not verified), and what you would change. Never claim you looked at
something you could not see. Over ~45MB, re-encode in the sandbox first (`ffmpeg -crf 28`).

## IF YOU DO USE A VIDEO MODEL ANYWAY

Only for atmosphere, never for defined motion.

- The result line must report anchor frames **greater than zero**. "0 anchor frames" means your
  keyframes never reached the model, it silently became text-to-video, and you were billed for a
  guess. Stop and fix the anchors rather than paying again.
- Durations are 4, 6 or 8 seconds only.
- Write POSITIVELY. Name the subject and state what PERSISTS ("the paper stays warm-white edge to
  edge"), never "no dark background". A negation-heavy prompt scored 0.25 on the built-in
  critique; the positive rewrite of the same shot passed. Read that critique in the tool result —
  it is your only eyes on a clip you cannot open.

## THINGS THAT GO WRONG, AND WHAT THEY MEAN

- **A tool name is not found** — you guessed it instead of reading `get_app_tools`. Names are
  per-app suffixed.
- **Export refuses with `unmeasurable_clips`** — a media URL was unreachable, or an image was
  filed as video because its name lacked ".png".
- **The film has black bars** — a card was not authored at 1232×672.
- **A caption drifts, rotates or splits mid-sentence** — not re-registered as fixed-in-frame after
  `.become()`, or built by `always_redraw`.
- **Rendering stalls with no manim process alive** — the cell was killed by the client timeout.
  Relaunch detached.
- **A success marker but no mp4** — the script lacked `set -euo pipefail`.
- **`/home/user` is empty** — the sandbox restarted. Whatever you already saved to workspace files
  survived; that is why you save as you go.
- **Narration drifts out of sync over the film** — durations were set from estimates instead of
  the measuring pass.
- **A 3D surface looks pinched or flat** — bad camera azimuth, not bad geometry. Rotate the camera
  (and since you cannot check by eye here, say so when you report it).
- **A tool result ends in `… [truncated N chars]`** — the storefront's 20,000-char TEXT cap
  (images ride separately and are never part of it). Print less; do not retry hoping for more.
- **You verified an export and it looked unchanged — you were looking at the PREVIOUS one.** This
  is the mirror of the re-download trap, and worse, because it silently confirms a stale cut.
  Auto-sync only fetches workspace files NOT YET copied to this sandbox, so a same-named
  replacement (`<name>-export.mp4`) never re-downloads. After re-exporting, read `lastExport.fileId`
  from the timeline and `copy_file_to_sandbox` it to a VERSIONED path (`export_v3.mp4`) before
  checking anything.
- **A narrate or export call errored** — do not retry. `read_timeline` first; it probably
  succeeded, and narration bills per character. See step 4.
- **A formula shows empty boxes in the film** — a Unicode codepoint no installed font covers.
  Preflight with the glyph check (step 5) BEFORE rendering, not after. If you installed LaTeX,
  `MathTex` sidesteps the whole class.
- **`MathTex` raises "latex error converting to dvi"** — read `media/Tex/*.log`. `! Missing $
  inserted` (or similar syntax noise) usually means the .py file on disk is CORRUPT, not that a
  package is missing: writing a scene through a non-raw Python string turns `\frac` into a
  formfeed. Print the line back from the file before blaming LaTeX. A genuinely missing package
  says `not found` in the log.
