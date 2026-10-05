# Narration-first — size the PICTURE to the SPEECH, never the reverse

> Read this before planning any film with narration. It replaces the
> beats→render-to-fixed-targets→narrate-to-fit order that shipped a 21-minute
> film with 266s of dead air (20.7%) and forced a full narration rewrite.

## THE PRINCIPLE

Speech has a natural rate you cannot control; picture is trivially elastic
(a still holds for any duration; a video shot slows or speeds within reason).
So **speech is the FIXED quantity and picture is the ELASTIC one** — you
measure the speech, then size each scene to it. The old order made picture
fixed (rendered to a hardcoded 30/32/34s target) and speech elastic (written
to fit), which is backwards: every line came in short and the shortfall
dumped as dead air at every shot's tail — 40 separate stalls, not breathing
room.

**Explicit rule: never hardcode a beat-duration table before the narration
exists.** A number like `SCENE_SECONDS = [30, 32, 34, ...]` at the top of a
render script is the bug.

## THE ORDER

1. **Write the script** — one line per beat, as the arc demands (the film is
   still a story; see SKILL.md step 1). Do NOT assign durations yet.

2. **Calibrate the voice.** Generate ONE representative line — it comes back
   with its real `seconds` (every TTS call now returns the measured length, and
   the clip lands with that `sourceDuration` set). The rate varies with the
   voice AND the delivery instructions, so a planning constant is a guess:

   > Measured datum: **onyx** at *"calm, unhurried documentary"* delivers
   > **2.89 words/sec** (2,950 words / 1,019.6s). The old 2.4 estimate is ~20%
   > low. Calibrate per voice; never assume.

   On this surface the calibration is free and automatic: `narrate_script`
   with `estimateOnly: true` returns the measured rate once ≥2 clips exist,
   plus the per-shot fit table (predicted vs shot seconds, total silence).
   Run it before committing the full pass.

3. **Generate all narration.** Each line comes back with its MEASURED seconds
   and lands with `sourceDuration` set — narration is measured the moment it's
   made, no export needed to probe it (`read_timeline compact:true` shows the
   same numbers). These measured lengths — not estimates — are the truth you
   size against. (Only the VIDEO shots still need a length: pass `sourceDuration`
   to `add_clips`, or export once to measure them.)

4. **Set each scene's target** from its line: `target = line_seconds + leadIn
   + tail`, rounded up (leadIn ~0.2s, tail ~0.5s). A still simply holds that
   long. A video shot renders to it (or `sync_narration_to_shots shrink:true`
   speeds/holds it toward the line).

5. **Render scenes to those targets** — picture sized to speech, so there is
   no structural slack to pool into silence.

## WHY THIS IS ALSO CHEAPER

A `self.wait()` with no active updaters is FREE — manim caches the static
frame (see manim-motion-craft.md). So a scene that is a short animated beat
plus a long hold costs only the animated frames, and the hold is sized to the
narration for free. Sizing picture to speech and holding on stills is both
the cheaper render AND the better pedagogy — the hold is when the viewer
actually reads the formula.

## IF YOU ALREADY HAVE A SILENT-GAP FILM

`sync_narration_to_shots` now reports its silence budget and takes
`distribute:"center"` (split each shot's slack around its line — same air,
reads as pacing not stalls) and `shrink:true` (close gaps by retiming stills
down and speeding video ≤1.35× toward the line). Free, no regeneration — the
first move on an existing film. The real fix is still narration-first for the
NEXT one.
