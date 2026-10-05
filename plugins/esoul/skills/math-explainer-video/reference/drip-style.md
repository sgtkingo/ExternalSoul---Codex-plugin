# The drip style — dark glow manim + a living character

> Use when a manim film should LOOK ALIVE — the dark, glowing, 3Blue1Brown-adjacent aesthetic ("make it look like 3blue1brown", "drip", "cinematic", "make it beautiful") and/or an animated CHARACTER with reactions. This is a STYLE layer over reference/manim-3d-scenes.md and the SKILL.md pipeline: read those for what to build; read this for how it should look. It is the DEFAULT look for explainer films (SKILL.md step 1 sends you here); the paper-white card aesthetic is the fallback those skills keep for formula-heavy films whose LaTeX must typeset on light cards.

**LaTeX note (measured 2026-08-10).** Where this file says LaTeX is
unavailable and `MathTex`/`Tex`/`DecimalNumber`/`get_graph_label` crash, read that as
*until you install it*. The sandbox is Debian 12 with passwordless sudo:
`sudo apt-get install -y --no-install-recommends texlive-latex-base texlive-latex-extra dvisvgm`
takes ~56s and 255MB, after which `MathTex` renders (verified: `manim -ql` exit 0, real mp4).
Every no-LaTeX idiom below remains correct if you skip that install — and remains the right choice
for captions, which want Pango `Text` regardless.

THE ONE RULE: A FILM HAS ONE THEME
Cards and scenes share a background or the cuts read as mistakes. Dark film = dark cards AND dark scenes. tldraw cards cannot go dark (no dark fill exists) — in a dark film the cards are MANIM STILLS: write each card as a Scene that only `self.add`s, render with `manim -qm -s` (saves a PNG to media/images/<module>/<SceneName>*.png), and add it to the timeline as an IMAGE clip — stills stretch to their narration exactly like tldraw cards. Formulas on dark cards are Unicode via Pango Text (θₜ₊₁ = θₜ − η∇L works; no LaTeX in the sandbox) — a formula Unicode cannot write honestly still belongs on a light tldraw latex card, which means that FILM should be light.

THE PALETTE (start here, tune later)
  BG="#0B0E14"  blue-black, never pure black
  BLUE="#58C4DD"  RED="#FC6255"  YEL="#F4D345"  GRN="#83C167"   (the 3b1b hues)
  TXT="#F5F1E6"  warm off-white for text — pure white glares
  GREY="#8A93A6" for captions/kickers   DIM="#1E3A5F" for grids
  config.background_color = BG
Semantics stay consistent film-wide: one colour = one meaning (the loss is BLUE, the learner is RED/YEL, success is GRN).

GLOW — the whole trick is three strokes
  def glow(vmob, color, width=4.0):
      return VGroup(
          vmob.copy().set_stroke(color, width*4.5, opacity=0.10).set_fill(opacity=0),
          vmob.copy().set_stroke(color, width*2.2, opacity=0.22).set_fill(opacity=0),
          vmob.set_stroke(color, width, opacity=1.0))
Halo, corona, core. Use it on every hero curve, accent rule, and title (glow a fill-less copy UNDER text). A moving object's trail glows with TWO TracedPaths: one wide at opacity ~0.14 under one normal.

THE FLOOR — a faint grid makes dark feel deliberate, not empty
  NumberPlane(background_line_style={"stroke_color": DIM, "stroke_width": 1, "stroke_opacity": 0.45},
              axis_config={"stroke_color": DIM, "stroke_opacity": 0.6, "stroke_width": 1})
In 2D: add it first, at full frame. In a ThreeDScene it lies flat at z=0 — exactly the glowing floor under a surface. Lift surfaces slightly (+0.2 z) so they float above it.

SURFACES — shaded and height-coloured, never bare wireframe
  surf = Surface(..., resolution=(20,16), fill_opacity=0.72,
                 stroke_width=0.7, stroke_color="#FFFFFF", stroke_opacity=0.22,
                 checkerboard_colors=False)
  surf.set_fill_by_value(axes=axes, colorscale=[(BLUE, low_z), (mid_color, mid_z), (RED, high_z)], axis=2)
The faint white mesh over a translucent height-gradient IS the reference look. The axes can be an invisible ThreeDAxes (set_opacity(0)) — set_fill_by_value only needs its coordinate mapping.

A CHARACTER WITH LIFE — the protagonist is the maths object
Do not decorate: find the object the maths is ABOUT and give IT eyes. In gradient descent the descending ball is the character; in a sorting explainer, an element; in a limit, the point. Build an ORIGINAL mascot from primitives (never copy the pi creature — it is Grant Sanderson's signature):
  def buddy(radius=0.3, color=BLUE, look=RIGHT):   # halo + body + googly eyes
      halo = Circle(radius=radius*1.55, stroke_width=0).set_fill(color, opacity=0.16)
      body = Circle(radius=radius, stroke_color=color, stroke_width=3).set_fill(color, opacity=0.55)
      eyes = VGroup()
      for dx in (-0.38, 0.38):
          white = Ellipse(width=radius*0.62, height=radius*0.78, stroke_width=1.5,
                          stroke_color=BG).set_fill("#FFFFFF", 1).move_to(
                          body.get_center()+np.array([dx*radius, radius*0.42, 0]))
          pupil = Dot(radius=radius*0.115, color=BG).move_to(
                          white.get_center()+normalize(np.array([*look[:2],0]))*radius*0.12)
          glint = Dot(radius=radius*0.035, color="#FFFFFF").move_to(pupil.get_center()+np.array([radius*0.04, radius*0.05, 0]))
          eyes.add(VGroup(white, pupil, glint))
      return VGroup(halo, body, eyes)
Three verbs make it alive, used SPARINGLY (once or twice per scene):
- look_at: move each pupil toward a direction before the action — the character anticipates ("looks down the slope, THEN steps").
- blink: stretch each eye to 0.08 in y and back, ~0.2s total. One blink on entry beats ten anywhere else.
- react: wide eyes (scale the whites 1.3) + Wiggle for dizzy/alarm; a Flash for triumph; an ArcBetweenPoints mouth on the end card — left→right with POSITIVE angle sags into a smile, negative bulges into a frown (the sign trap shipped a frowning mascot once; check the still). Reactions land ON story beats (the overshoot explodes → dizzy; the minimum is reached → flash + blink).
The character rides MoveAlongPath like any mobject; in 3D keep glowing Dot3Ds instead — a face is mush at orbit distance.

COMPOSITION NOTES
- Titles: bold Text in TXT with a coloured glow copy underneath; a glowing accent rule (Line) under the title block; kicker top-left in GREY BOLD caps.
- Pango happily typesets WIDER than the camera — guard every long card line: `if t.width > 12.2: t.scale_to_fit_width(12.2)` (a clipped formula shipped once; the still is the check).
- One hero per frame. The grid is texture, not content; captions stay GREY and small so the glow carries the eye.
- One occupant per BAND: kicker/title owns the top, captions the bottom, formulas the field between. A second element entering an occupied band means the first FadeOuts FIRST (the swap idiom) — stacked text in the title band is a shipped-defect class, not a style choice. And keep everything inside |x| ≤ 6.5, |y| ≤ 3.5: the camera crops silently.
- Flash(obj, color, flash_radius≈0.5) is the cheapest satisfying beat — use it when something ARRIVES. The full emphasis/easing/stagger grammar (Indicate works on glow groups; one temperament per film) is `reference/manim-motion-craft.md`.
- Cameo the character on the title and end cards (a still pose with look_at toward the title) — it stitches the film's identity together.

PIPELINE DELTAS (everything else is SKILL.md step 4 unchanged)
- Render stills: `manim -qm -s file.py Card01 …` then cp media/images/<module>/Card01*.png out/. Cards land as image clips; scenes as video clips; narrate_script → export-to-measure → sync_narration_to_shots → export exactly as usual.
- Restyling an EXISTING synced film costs no narration: remove the old video-lane clips, add the restyled ones in the same order, then export-measure → sync → export. The narration track re-syncs to the new durations.
- Budget: the drip surfaces render ~2× slower than wireframes (shaded fill + higher resolution). Same detached-render + save-as-you-go rules as always.