# The 2D set pieces — what to put on screen

> Use when choosing WHAT to put on screen for a 2D maths beat — the classic explainer set pieces: the linear-map grid, graph stories, Riemann refinement, moving points with trails, counters, camera zooms, callouts. Each is a verified no-LaTeX recipe for manim CE in the sandbox. This is the shot vocabulary under SKILL.md; HOW things move is `reference/manim-motion-craft.md`; real 3D is reference/manim-3d-scenes.md. Colors below are placeholders — use your film's theme palette (drip or paper).

**LaTeX note (measured 2026-08-10).** Where this file says LaTeX is
unavailable and `MathTex`/`Tex`/`DecimalNumber`/`get_graph_label` crash, read that as
*until you install it*. The sandbox is Debian 12 with passwordless sudo:
`sudo apt-get install -y --no-install-recommends texlive-latex-base texlive-latex-extra dvisvgm`
takes ~56s and 255MB, after which `MathTex` renders (verified: `manim -ql` exit 0, real mp4).
Every no-LaTeX idiom below remains correct if you skip that install — and remains the right choice
for captions, which want Pango `Text` regardless.

PICK THE SHOT BY THE STORY BEAT
- "this transformation ACTS on space" (matrices, eigenvectors, complex multiplication) → THE LINEAR MAP.
- "this quantity ACCUMULATES or refines" (integrals, sums, limits) → RIEMANN REFINEMENT / AREA REVEAL.
- "this function CHANGES with a parameter" (families, derivatives, fits) → GRAPH STORY on a ValueTracker.
- "this thing MOVES through a space" (trajectories, iteration, gradient descent) → MOVING POINT with a trail.
- "how much / how many" (probability, samples, convergence) → COUNTER + BAR.
- "look closer / step back" (detail vs context) → CAMERA ZOOM.
- "THIS part right here" (naming a piece of a diagram) → CALLOUT.
A mystery opening = zoom into the odd detail FIRST, explain second. The refinement and limit shots ARE the aha — spend run_time there, not on entrances.

THE LINEAR MAP (verified) — matrices act on space
  static = NumberPlane(x_range=[-8,8], y_range=[-5,5],
      background_line_style={"stroke_color": GREY, "stroke_width": 1, "stroke_opacity": 0.3},
      axis_config={"stroke_color": GREY, "stroke_opacity": 0.4})
  live = NumberPlane(x_range=[-8,8], y_range=[-5,5],
      background_line_style={"stroke_color": INK, "stroke_width": 1.4, "stroke_opacity": 0.7})
  bi = Arrow(ORIGIN, RIGHT, buff=0, color=HOT, stroke_width=6)
  bj = Arrow(ORIGIN, UP, buff=0, color=GRN, stroke_width=6)
  self.add(static, live, bi, bj)
  self.play(live.animate.apply_matrix(M), bi.animate.apply_matrix(M),
            bj.animate.apply_matrix(M), run_time=3)
The FAINT STATIC COPY underneath makes the motion legible — the eye needs the before while watching the after. Basis vectors ride the same matrix; their landing spots ARE the matrix columns (say so). Determinant beat: a filled unit Square shears — its area is det. Eigenvector beat: draw the eigen-line first; the map leaves it in place while everything else swings. Ranges wider than the frame ([-8,8]) keep corners covered. NONLINEAR: live.prepare_for_nonlinear_transform() first (lines subdivide so they can bend), then live.animate.apply_function(f).

THE GRAPH STORY (verified)
  ax = Axes(x_range=[-3,3,1], y_range=[-1,4,1], x_length=8, y_length=5,
            axis_config={"color": GREY, "include_tip": True, "tip_width": 0.18, "tip_height": 0.18})
  f = ax.plot(lambda x: 0.5*x*x, color=INK, stroke_width=4)
  self.play(Create(ax, lag_ratio=0.05)); self.play(Create(f))
Labels: ax.get_graph_label(f, label=Text("f"), x_val=2) — the DEFAULT label is MathTex and CRASHES; ALWAYS pass a Text. Free placement: Text(...).next_to(ax.input_to_graph_point(x, f), UR, buff=0.2).
Morph f→g by Transform(f, g2) on the SAME axes — the held frame is what shows "same question, different function". Area: self.play(FadeIn(ax.get_area(f, x_range=[a,b], color=INK, opacity=0.25))). Parameter families: k = ValueTracker(1); curve = always_redraw(lambda: ax.plot(lambda x: k.get_value()*np.sin(x), color=INK)); self.play(k.animate.set_value(3)) — cheap 2D redraw, sanctioned.

RIEMANN REFINEMENT (verified) — the integral aha
  rects = ax.get_riemann_rectangles(f, x_range=[0,2], dx=0.5,
      color=[INK, HOT], fill_opacity=0.5, stroke_width=1)
  fine  = ax.get_riemann_rectangles(f, x_range=[0,2], dx=0.125,
      color=[INK, HOT], fill_opacity=0.5, stroke_width=0.5)
  self.play(LaggedStartMap(FadeIn, rects, lag_ratio=0.1))
  self.play(Transform(rects, fine), run_time=1.5)
Two refinement steps read as a limit; narrate over the Transform, then swap in the smooth get_area as the destination. Thin the stroke_width as dx shrinks or the fine pass reads black.

THE MOVING POINT (verified)
  dot = Dot(color=HOT)
  trail = TracedPath(dot.get_center, stroke_color=HOT, stroke_width=3, dissipating_time=0.6)
  self.add(trail, dot)
  self.play(MoveAlongPath(dot, path), run_time=2.5, rate_func=rate_functions.ease_in_out_sine)
path is any VMobject — a plotted curve's .copy(), a ParametricFunction. dissipating_time = comet tail; omit it for pen ink (the whole trace stays). Iteration/descent beats: precompute the points (numpy/scipy), VMobject().set_points_smoothly([...]), MoveAlongPath — never simulate inside an updater. The dot is the drip character slot: give IT the eyes.

COUNTER + BAR (verified — DecimalNumber and Integer CRASH without LaTeX)
  t = ValueTracker(0)
  num = always_redraw(lambda: Text(f"{t.get_value():.0f}", font_size=64).move_to(UP*1.5))
  bar = always_redraw(lambda: Rectangle(width=max(t.get_value()*0.06, 0.01), height=0.6,
        fill_opacity=0.8, stroke_width=0).move_to(DOWN*0.5 + RIGHT*t.get_value()*0.03))
  self.play(t.animate.set_value(100), run_time=2.5, rate_func=rate_functions.ease_out_expo)
ease_out_expo makes the count LAND. Full idiom + the emphasize-the-final-value handoff: motion-craft skill.

THE CAMERA ZOOM (verified) — the scene class must be MovingCameraScene
  self.camera.frame.save_state()
  self.play(self.camera.frame.animate.scale(0.35).move_to(spot),
            run_time=1.6, rate_func=rate_functions.ease_in_out_cubic)
  ...
  self.play(Restore(self.camera.frame), run_time=1.4)
Follow a moving dot: self.camera.frame.add_updater(lambda m: m.move_to(dot.get_center())) — and clear_updaters() BEFORE the Restore (a live follow fights it). A zoom is a beat: lean in on the odd detail, Restore for reveal-in-context. Never mixed with ThreeDScene — zooms and orbits live in different scene classes.

THE CALLOUT (verified constraint)
  brace = Brace(target, DOWN)
  label = Text("width", font_size=24).next_to(brace, DOWN, buff=0.1)
Brace itself is a pure path and safe; brace.get_text() typesets LaTeX and CRASHES — always place your own Text. Alternatives: SurroundingRectangle(m) for boxing, CurvedArrow(a.get_bottom(), b.get_bottom()) for "this becomes that".

STAGE MANAGEMENT ACROSS BEATS
- Progressive disclosure: build the diagram element by element, in the order the narration names them — never the finished thing at once.
- Color is meaning, film-wide: fix the mapping once (input INK, result HOT, success GRN); never reuse a colour for a second meaning.
- Position is meaning: left→right = cause→effect and time; top→bottom = derivation; center = the current hero, ONE per frame.
- SCALE is meaning too, and it is the one that silently ships wrong. manim's frame is only
  ~14.2 units wide, so the 1:1 data-to-manim default in these recipes (Arrow(ORIGIN, RIGHT),
  NumberPlane(x_range=[-8,8])) yields a diagram at ~30% of frame width — geometrically
  perfect and far too small. Choose an explicit unit scale per scene (SKILL.md step 3's
  Stage helper): live area 45-65% of frame width, a unit basis vector >=10%.
- Between beats: FadeOut(done, shift=DOWN*0.3) but let the axes/plane PERSIST — re-creating the stage each beat reads as a reset; the held stage makes two beats one investigation.
- End card: restate the one earned claim and hold it longer than feels natural — the viewer is writing it down.

FRAME DISCIPLINE — the camera is 14.2 × 8.0 units and it CROPS, it never shrinks (the shipped-defect classes)
- SAFE AREA: every mobject inside |x| ≤ 6.5, |y| ≤ 3.5 (~0.6 margin). The frame clips silently — a label past the edge renders half-missing and errors nowhere.
- Axes leave room for their LABELS: x_length ≤ 11, y_length ≤ 6, labels INTO the frame, never off the tip — x-label next_to(ax.x_axis.get_end(), DOWN, buff=0.2), y likewise RIGHT. get_x_axis_label's default sits AT the tip: on near-full axes that is already outside safe (a half-clipped "x₂" shipped this way).
- Size every composed group before animating:
    def fit_frame(m, w=13.0, h=7.0):
        if m.width > w: m.scale_to_fit_width(w)
        if m.height > h: m.scale_to_fit_height(h)
        return m
- BANDS — three horizontal bands: TITLE (top ~1.2), FIELD (middle), CAPTION (bottom ~1.0, the hud slot). ONE occupant per band at a time, film-wide. A mid-beat formula lives in the FIELD or REPLACES the title (swap idiom), never on top of it: titles EXIT before anything enters the top band. Two texts sharing a band is how "MULTIPLICATION IS ROTATION" shipped with z ↦ e^{iθ}z stamped through it.
- LABELS ON DENSE/CONVERGING DATA COLLIDE (shipped): bunched Bohr levels, close spectral lines — a label AT each point fails when points crowd. The fix is LAYOUT, not a nudge: every k-th label, leader lines to a spread column, or a zoom inset; the guard names WHICH collide.
- DARK TEXT ON DARK BG (shipped): a near-background label (INK/DIM on drip black) is invisible — every text must be TXT or another high-contrast hue.
- TEXT STRADDLING A SHAPE'S EDGE + SIBLING SHAPES COLLIDING (both shipped: an SRT label across a tank border; a clarifier overlapping the aerobic box). A label lives fully INSIDE its box or fully clear; sibling shapes never intersect (nesting is fine).
- TWO COMPOSITES IN ONE BEAT (diagram + chart) each get a REGION: fit_frame each, move_to separate halves, then guard_regions(diagram, chart) proves it.
- GUARD AUTOMATICALLY, EVERY BEAT — guard_scene walks the whole scene graph (nothing to remember to pass), and subclassing GuardedScene instead of Scene makes EVERY wait() self-check, so a -ql draft FAILS the instant a held frame is wrong, naming the offender:
    def guard_scene(scene, bg=BG, pad=0.12, xlim=6.7, ylim=3.7, min_c=0.28, min_area=0.35, ignore=()):
        from itertools import combinations
        lum = lambda c: sum(w*x for w, x in zip((.299, .587, .114), ManimColor(c).to_rgb()))
        fam = [m for r in scene.mobjects for m in r.get_family() if m not in ignore]
        txt = [m for m in fam if isinstance(m, (Text, MarkupText, MathTex, Tex))]
        txt = [m for m in txt if not any(m is not o and m in o.get_family() for o in txt)]
        box = [m for m in fam if isinstance(m, (Rectangle, Circle, Ellipse, Polygon)) and m.width*m.height > min_area]
        B = lambda m: (m.get_left()[0], m.get_right()[0], m.get_bottom()[1], m.get_top()[1])
        def hit(a, b, p=0.0):
            al, ar, ab, at = B(a); bl, br, bb, bt = B(b)
            return al-p < br and bl-p < ar and ab-p < bt and bb-p < at
        def inside(a, b, e=0.02):
            al, ar, ab, at = B(a); bl, br, bb, bt = B(b)
            return al >= bl-e and ar <= br+e and ab >= bb-e and at <= bt+e
        part = lambda a, b: hit(a, b) and not inside(a, b) and not inside(b, a)
        zoomed = getattr(getattr(scene.camera, "frame", None), "width", 14.2) < 14.0
        for m in txt + box:
            l, r, b, t = B(m)
            if not zoomed and (max(abs(l), abs(r)) > xlim or max(abs(b), abs(t)) > ylim):
                raise AssertionError(f"OFF-FRAME: {m}")
        for m in txt:
            # Pango text reports its OWN colour as black: read the glyphs' fills, brightest wins
            peak = max((lum(g.get_fill_color()) for g in m.family_members_with_points() if g.get_fill_opacity() > 0.2), default=1.0)
            if abs(peak - lum(bg)) < min_c:
                raise AssertionError(f"LOW CONTRAST: {m} — recolor to TXT")
            for s in box:
                if part(m, s): raise AssertionError(f"TEXT CROSSES EDGE: {m} straddles {s}")
        for a, b in combinations(txt, 2):
            if hit(a, b, pad): raise AssertionError(f"TEXT OVERLAP: {a} vs {b}")
        for a, b in combinations(box, 2):
            if part(a, b): raise AssertionError(f"SHAPES COLLIDE: {a} vs {b}")
    class GuardedScene(Scene):
        def wait(self, *a, **k):
            guard_scene(self); return super().wait(*a, **k)
    def guard_regions(*gs, pad=0.15):
        from itertools import combinations
        for a, b in combinations(gs, 2):
            if (a.get_left()[0]-pad < b.get_right()[0] and b.get_left()[0]-pad < a.get_right()[0]
                and a.get_bottom()[1]-pad < b.get_top()[1] and b.get_bottom()[1]-pad < a.get_top()[1]):
                raise AssertionError(f"REGIONS COLLIDE: {a} vs {b} — fit_frame each, move_to separate halves")
  Fully-inside text and nested shapes PASS (deliberate); tips/dots fall under min_area; off-frame skips while zoomed (a zoom crops by design). Same 2-line wait() hook on any base (3D: only the fixed HUD is meaningful). Deliberate art → ignore=. A bad final costs a render cycle; this costs nothing.
