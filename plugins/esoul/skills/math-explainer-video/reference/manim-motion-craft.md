# Motion craft — how manim animation should FEEL

> Use when writing ANY manim animation and deciding HOW things move — easing, choreography of simultaneous vs staggered motion, entrances and exits, emphasis, morphing between states, updaters. The craft layer under SKILL.md (film pipeline), reference/manim-3d-scenes.md (3D vocabulary) and reference/drip-style.md (look): this is what makes motion FEEL alive instead of rendered. Every recipe verified on manim CE 0.20.1 with no LaTeX (the sandbox condition).

**LaTeX note (measured 2026-08-10).** Where this file says LaTeX is
unavailable and `MathTex`/`Tex`/`DecimalNumber`/`get_graph_label` crash, read that as
*until you install it*. The sandbox is Debian 12 with passwordless sudo:
`sudo apt-get install -y --no-install-recommends texlive-latex-base texlive-latex-extra dvisvgm`
takes ~56s and 255MB, after which `MathTex` renders (verified: `manim -ql` exit 0, real mp4).
Every no-LaTeX idiom below remains correct if you skip that install — and remains the right choice
for captions, which want Pango `Text` regardless.

WHAT CRASHES OR DOES NOT EXIST (verified — learn before the pretty parts)
- DecimalNumber, Integer, Variable and Brace.get_text ALL typeset through LaTeX → they CRASH in the sandbox. The Text counter idiom is below; Brace itself is a pure path and fine — label it with your own Text.
- FlashAround does not exist in manim CE (it is manimGL-only) — use Circumscribe or Flash.
- always_redraw on a Surface outruns the sandbox (the 3d skill's rule). always_redraw on Text / 2D lines / plots is FINE — a per-frame Pango Text rebuild is cheap (verified: renders at full speed).
- LaggedStartMap(Anim, group, ...) unpacks the group's SUBMOBJECTS as extra POSITIONAL args to Anim. Harmless for FadeIn/FadeOut (they take *mobjects); FATAL for Create, Write, GrowArrow, GrowFromEdge — the submobject arrives where the second positional param sits (broke 7 scenes once, as two unrelated-looking errors). Build the list yourself: `self.play(LaggedStart(*[Create(m) for m in group], lag_ratio=0.08))`.
- ImageMobject is NOT a VMobject — it CANNOT go in a VGroup (silent-ish breakage, another 7 scenes). Use `Group(img, ...)` for anything holding an ImageMobject.
- `ndarray.ptp()` was REMOVED in NumPy ≥2.0 (the sandbox has it) → `np.ptp(arr)`, not `arr.ptp()`.
- COST MODEL, stated plainly: `self.wait()` with NO active updaters is FREE — manim caches the static frame and emits it repeatedly; only ANIMATED frames cost render time. So design every scene as SHORT animated beats + LONG holds: it is both cheaper AND better pedagogy (the hold is when the viewer reads). A 6s film that animates for 2s and holds for 4s renders in ~2s of frames.

EASING — rate_func is the difference between animated and rendered
Every play() takes rate_func=rate_functions.<name>. Default smooth (slow-fast-slow) is right most of the time; reach past it deliberately:
- linear: constant speed — scanning, conveyors, clock hands. Reads mechanical anywhere else.
- smooth / double_smooth: neutral elegance, the default temperament.
- rush_into (slow→fast): departures, being pulled in. rush_from (fast→slow): arrivals that settle.
- ease_in_out_sine: long contemplative glides — camera moves, slow pans.
- ease_out_expo: snap-then-settle — counters, bars, things that "land".
- ease_out_back: a tiny overshoot at arrival — playful pop, good for the drip mascot's world. ease_out_bounce: literal bounces only.
- there_and_back / there_and_back_with_pause: peek and return — emphasis without commitment.
- lingering: holds at the end — a delay inside an AnimationGroup.
Any function t→[0,1] works: rate_func=lambda t: t*t. Match feel to content — smooth for elegance, linear for precision, back/bounce for character beats — and keep ONE temperament per film; bouncy cut against austere reads as a mistake.

CHOREOGRAPHY — what moves together, what moves in sequence
One beat = one idea moving. Things passed to the same play() say "these belong together"; separate plays say "then".
- AnimationGroup(*anims, lag_ratio=r): r=0 together; r=0.25 each starts when the previous is 25% done; r=1 is sequential.
- LaggedStart(*anims, lag_ratio=0.05-0.2): THE polish tool — a staggered group entrance is dynamic where a simultaneous one is flat. A traveling wave (verified) is LaggedStart of per-item there_and_back shifts:
    self.play(LaggedStart(*[s.animate(rate_func=rate_functions.there_and_back).shift(UP*0.5) for s in grid], lag_ratio=0.05))
- LaggedStartMap(FadeIn, group, shift=UP*0.4, lag_ratio=0.06): the same animation over every submobject, staggered.
- Succession(...): distinct steps treated as one unit.
- run_time on a group is the TOTAL and distributes over children.
Keep lag_ratio small (0.05-0.2) — big lags read as waiting. Beats run 0.5-3s; only camera glides earn more. wait() is rhythm, not dead air: hold 0.5-1s after a reveal — that hold is when the viewer actually sees it.

ENTRANCES AND EXITS — pick the verb by what the thing IS
- Create: shapes and curves, drawn along their path. Write: text, paced by its length. DrawBorderThenFill: filled shapes where the outline matters first.
- FadeIn(m, shift=UP*0.4, scale=0.9): the workhorse — a small shift or scale makes a fade directional instead of dead. Exit with FadeOut(m, shift=DOWN*0.3).
- GrowFromCenter / GrowFromPoint(m, pt) / GrowFromEdge(m, LEFT): birth from a cause — grow the result out of the thing that produced it.
- FadeOut beats Uncreate for exits, unless un-drawing IS the point.

EMPHASIS — point at things without cutting
- Indicate(m, color=...): the default "look here" — brief scale + recolor and back. Works on a glow VGroup: all three strokes recolor and restore together (verified).
- Circumscribe(m, color=..., buff=0.15): draws a temporary frame — regions, groups, whole statements.
- Flash(point, color=..., flash_radius=0.5): radial burst when something ARRIVES — also the drip triumph beat.
- FocusOn(point): darkens around a spot. Wiggle / ApplyWave: character reactions — at most one per scene.
Rules: emphasis lands ON the narration word that names it; ONE emphasis verb at a time; if everything is emphasized, nothing is.

MORPHING — the transform taxonomy (the variable semantics bite)
- .animate for property changes, chained in one play: m.animate.shift(RIGHT).rotate(PI/4).set_color(BLUE).
- Transform(A, B): A now LOOKS like B but the scene object is still A — later code must keep animating A. ReplacementTransform(A, B): B replaces A — later code uses B. Pick one convention per scene; mixing them is the classic "my later animation hit nothing" bug.
- TransformFromCopy(A, B): A stays put, a copy becomes B — the derivation move ("this GIVES that"), and the two-perspectives shot.
- TransformMatchingShapes(t1, t2): on Text it matches shared glyphs and morphs only the difference (verified: "energy in"→"energy out" holds "energy" still) — the no-LaTeX stand-in for TransformMatchingTex. Prefer it over FadeOut/FadeIn for any wording change: transform, don't replace — continuity is what shows the relationship.
- MoveToTarget: m.generate_target(); m.target.shift(...).rotate(...).set_color(...); self.play(MoveToTarget(m)) — declare a compound end state, animate to it in one move.
- path_arc=PI/2 on any Transform makes the travel an arc instead of a straight slide — motion with intent; also how a swap of two items reads as a swap.

UPDATERS — relationships that hold while things move
- follower.add_updater(lambda m: m.next_to(leader, UP, buff=0.15)): a label that stays attached during motion. clear_updaters() the moment the relationship ends — a leaked updater silently fights every later animation of that mobject.
- An arrow between moving things: arr.add_updater(lambda m: m.put_start_and_end_on(a.get_center(), b.get_center())).
- Perpetual motion is a dt updater (frame-rate independent): m.add_updater(lambda m, dt: m.rotate(dt*PI)).
- ValueTracker(x0) is the animatable parameter: everything that reads t.get_value() through updaters or always_redraw moves when you self.play(t.animate.set_value(x1), rate_func=...). increment_value for steps.
- TracedPath(dot.get_center, stroke_width=3, dissipating_time=0.6): the trail. dissipating_time makes a comet tail; omit it and the full path stays like pen ink.

THE COUNTER — the verified no-LaTeX idiom (DecimalNumber crashes)
  t = ValueTracker(0)
  num = always_redraw(lambda: Text(f"{t.get_value():.0f}", font_size=64).move_to(UP*1.5))
  self.add(num); self.play(t.animate.set_value(100), run_time=2.5, rate_func=rate_functions.ease_out_expo)
To emphasize the final value, first self.remove(num) and add a static Text("100") in its place — Indicate on an always_redraw target is fought by the per-frame rebuild.

PUTTING A BEAT TOGETHER
A beat is: an entrance verb chosen by what the thing is + easing that matches the film's temperament + ONE emphasis on the narrated word + a hold. A sequence is: LaggedStart entrances, transforms that preserve continuity, updater-bound labels riding the motion, exits that clear the stage for the next idea. The full shots built from these pieces — linear-map grids, Riemann refinement, moving points, camera zooms — are `reference/manim-2d-set-pieces.md`.
