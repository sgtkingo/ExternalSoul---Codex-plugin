# Animate 3D mathematics with manim

> Use when an animation needs REAL 3D — a surface, a solid, a vector field, a trajectory, an orbiting camera: "animate a saddle surface", "show the gradient as an arrow on the surface", "visualize the Lorenz attractor", "rotate around a torus". This is the 3D scene-writing companion to SKILL.md: that skill owns the full film pipeline (cards, narration, assembly); come here for how to write the ThreeDScene itself. Not for 2D plots (Axes + plot in a plain Scene) and not for diagrams (draw on the canvas).

**LaTeX note (measured 2026-08-10).** Where this file says LaTeX is
unavailable and `MathTex`/`Tex`/`DecimalNumber`/`get_graph_label` crash, read that as
*until you install it*. The sandbox is Debian 12 with passwordless sudo:
`sudo apt-get install -y --no-install-recommends texlive-latex-base texlive-latex-extra dvisvgm`
takes ~56s and 255MB, after which `MathTex` renders (verified: `manim -ql` exit 0, real mp4).
Every no-LaTeX idiom below remains correct if you skip that install — and remains the right choice
for captions, which want Pango `Text` regardless.

STYLE: for the dark glow 3b1b-adjacent look and an animated character, read `reference/drip-style.md` after this. Easing, stagger and emphasis verbs: `reference/manim-motion-craft.md`.

WHERE THIS RUNS
In the e2b_sandbox app, with manim Community Edition. Rendering is FREE and deterministic — if the motion can be written as a function, write the function; never reach for a video model to animate mathematics. First check the environment: `import manim, av` and `shutil.which('latex')`. The sandbox often comes up bare — `pip install manim av pillow scipy` if missing. There is NO LaTeX: MathTex and Tex FAIL. Captions are Pango `Text`; every typeset formula belongs on a tldraw card (SKILL.md step 2), which is also better editing.
Set `config.background_color` to YOUR THEME's background — "#F9F9FB" paper on a light film, the drip skill's BG "#0B0E14" on a dark one. Manim defaults to pure black, which matches neither; a shot whose background differs from the cards reads as a mistake.

THE CAMERA IS THE NARRATOR — one beat, one viewpoint
- `set_camera_orientation(phi=..., theta=..., zoom=...)`. phi is the angle DOWN from the z-axis (0 = top-down plan view, 90 = side elevation; 55-75 reads as "3D"). theta orbits AROUND z. Set it before adding objects so nothing pops.
- A camera move IS a beat: `self.move_camera(phi=45*DEGREES, theta=60*DEGREES, run_time=3)` — use it to reveal structure (look down the axis of a helix, then from the side), not as decoration.
- `self.begin_ambient_camera_rotation(rate=0.15)` ... `self.stop_ambient_camera_rotation()` — a slow orbit (rate 0.1-0.3) is the cheapest way to make depth legible on a static object. ALWAYS stop it before the next beat; a rotation left running turns every later caption sync into soup.
- AZIMUTH IS LOAD-BEARING for saddle-like surfaces. Sighting along a principal direction of z = x²−y² collapses it to a pinched bowtie — the surface looks broken when only the viewpoint is. theta ≈ −28° keeps both arms of a standard saddle open; −52° does not. If a surface looks pinched or flat, rotate the camera and look again before touching the geometry.
- 2D zoom/pan lives in MovingCameraScene (`self.camera.frame.animate.scale(0.5).move_to(target)`, `save_state()` + `Restore(self.camera.frame)`) — but that is a different scene class; you cannot mix it with ThreeDScene.

THE 3D VOCABULARY
- Axes: `ThreeDAxes(x_range=[-4,4,1], y_range=[-4,4,1], z_range=[-2,2,1], x_length=8, y_length=8, z_length=4)`. Place EVERYTHING through `axes.c2p(x,y,z)` so data coordinates stay honest. Axis labels: `axes.get_x_axis_label("x")` etc., registered with `add_fixed_orientation_mobjects` — they billboard (always face the camera) while STAYING at their 3D position. That is different from fixed-in-frame (below); mixing the two is how a label ends up floating over the wrong thing.
- Solids: `Sphere(radius, resolution=(20,20))`, `Cube(side_length)`, `Prism(dimensions=[3,1,2])`, `Cylinder(radius, height)`, `Cone(base_radius, height)`, `Torus(major_radius, minor_radius)`. Give them `fill_opacity=0.7-0.9` and `set_shade_in_3d(True)` when they should read as solid bodies.
- Surfaces, two idioms:
  WIREFRAME (matches the hand-drawn card aesthetic, renders fast):
    Surface(lambda u,v: np.array([u, v, f(u,v)]), u_range=[-R,R], v_range=[-R,R],
            resolution=(12,12), fill_opacity=0.0, stroke_width=1.9,
            stroke_color=INK, checkerboard_colors=False)
  `checkerboard_colors=False`, never None — None THROWS.
  SHADED (when height should read as colour): `axes.plot_surface(f, u_range=..., v_range=..., resolution=(24,24), colorscale=[BLUE, GREEN, YELLOW, RED], fill_opacity=0.8)`. Resolution is quadratic in cost — (24,24) shaded is a final-quality decision, not a default.
- Curves: `ParametricFunction(lambda t: np.array([...]), t_range=[a,b])` + `.set_shade_in_3d(True)` so it occludes correctly. A helix is ten lines; a chaotic trajectory is NOT a simulation loop — precompute with scipy (`solve_ivp`, dense `t_eval`), then `VMobject().set_points_smoothly([axes.c2p(*p) for p in pts])` and `Create(curve, run_time=...)`. The ODE is solved once, offline; manim only draws the answer.
- Vectors and markers: `Arrow3D(start, end)`, `Line3D`, `Dot3D(axes.c2p(...), radius=0.09)`. A gradient arrow that follows a moving point is an updater on ONE Arrow3D — cheap; rebuild-the-mesh updaters are the expensive class below. **Dot3D defaults to `resolution=(8,8)` = 64 quads EACH** — 140 of them under a moving camera is 6 seconds PER FRAME. Pass `resolution=(3,3)`, cut the count, and for a real point CLOUD do not use Dots at all: rasterize the whole cloud to ONE `ImageMobject` via numpy (project points → an H×W uint8 array), which renders in constant time regardless of point count.

MOTION — what is cheap and what outruns the sandbox
- NEVER `always_redraw` a Surface. Rebuilding a 144-quad mesh on each of ~480 frames outruns the sandbox lifetime — a render that crawls at seconds-per-frame is this, not a slow machine. Morph between PREBUILT meshes of equal resolution instead: `Transform(surf, mk(a2,b2), run_time=3)` interpolates point data — identical picture, ~10× faster.
- `ValueTracker` + `always_redraw` is fine for CHEAP objects: a 2D `axes.plot` curve, one arrow, one dot, a short line. The rule is per-frame rebuild cost, not the pattern itself.
- A point tracing a path: move a `Dot3D` along precomputed points with an updater, and `TracedPath(dot.get_center, stroke_color=..., stroke_width=2)` leaves the trail — no per-frame curve rebuild.
- `Create()` on a big shaded Surface is slow twice (draw-on effect + mesh). Prefer `FadeIn(surf)` or `self.add(surf)` then move the camera.

RASTER IMAGES AND FEATURE MAPS — the ML-architecture kit (UNet, CNNs, autoencoders)
- A pixel grid is an IMAGE, not a grid of mobjects. VGroup-of-Squares is fine to ~12×12 (a conv-kernel demo); a 32×32 feature map is 1024 mobjects and the render crawls — the same cost class as always_redraw on a Surface. Build arrays in numpy, then `ImageMobject(arr.astype(np.uint8))` with nearest resampling (`img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])`) so pixels stay square when scaled up. Feature maps, downsampling ladders, blurry-bottleneck-vs-crisp-mask comparisons are all numpy transforms of ONE synthetic source image (draw a disc or blob by array indexing — deterministic, no assets); maxpool is `arr.reshape(h//2,2,w//2,2).max(axis=(1,3))`.
- An ARCHITECTURE is slabs: one `Prism(dimensions=[w, h, c_scaled])` per stage. Encoder steps DOWN (halve w,h, thicken channels), decoder mirrors up — the U reads from the silhouette alone. Label each slab "H×W×C" with a billboarded Text (add_fixed_orientation_mobjects); skip connections are ParametricFunction arcs (or Arrow3D) from each encoder slab to its decoder mirror. The shot that makes the shape legible is a camera glide ALONG the architecture (move_camera theta sweep) — orbit once, then hold side-on for the skip-connection beat.
- A convolution sliding-window demo is 2D and cheap: a small grid, one moving highlight Rectangle, per-cell fills driven by a ValueTracker.

CAPTIONS — HUD text in a 3D scene
`add_fixed_in_frame_mobjects(lbl)` pins a caption to the SCREEN (a HUD). Two traps, both of which cost a render cycle to diagnose:
- Fixed-in-frame is a property of the glyph SUBMOBJECTS. `.become()` swaps them, silently lapsing the exemption — half a sentence stays put, the rest orbits with the camera. RE-REGISTER after every `.become()`. Re-word captions in place with this exact shape:
    def swap(scene, lbl, txt, **kw):
        scene.play(lbl.animate.set_opacity(0.0), run_time=0.25)
        lbl.become(hud(txt, **kw)); lbl.set_opacity(0.0)
        scene.add_fixed_in_frame_mobjects(lbl)
        scene.play(lbl.animate.set_opacity(1.0), run_time=0.25)
        return lbl
- NEVER `always_redraw` a caption — it mints a new mobject per frame that nothing registered; it can never be fixed-in-frame. Captions are discrete beats.
Billboard vs HUD, once more: axis labels = `add_fixed_orientation_mobjects` (live IN the scene, face the camera); captions = `add_fixed_in_frame_mobjects` (live ON the glass).

SCENES AND THE RENDER LADDER
One class per beat, named in story order: `Scene1_Intro(ThreeDScene)`, `Scene2_Saddle(ThreeDScene)`. One command renders many: `manim -ql scene.py Scene1_Intro Scene2_Saddle`. Output lands under `media/videos/<script>/<quality>/<SceneName>.mp4`.
- Draft EVERYTHING at `-ql` (480p15), contact-sheet it (below), LOOK, and only then render finals at `-qm` (720p30). A scene that fails: read the error, fix, re-render ONLY that scene — the others are already on disk.
- RENDER DETACHED. A cell that blocks on manim dies at the client timeout and takes the subprocess with it — a stalled render with no process alive is this. Launch:
    subprocess.Popen(['bash','-lc','setsid nohup /home/user/r.sh > /home/user/r.log 2>&1 < /dev/null &'], start_new_session=True)
  with `set -euo pipefail` at the top of r.sh — without it a dead render still writes its success marker (a green light over a red run). Have the script append each finished filename to a PROGRESS file; poll with list_files (it reads the filesystem, not the blocked kernel).
- THE SANDBOX RESTARTS AND WIPES /home/user roughly every 15-30 minutes, pip installs included. `save_to_workspace` EVERY mp4 the moment it exists — never defer saves to the end. After a reset: reinstall, rewrite the scene file, re-render only what is missing from the workspace.

VERIFY BY LOOKING — one contact sheet, not N clips (over MCP results carry at most 3 images: the sheet IS how you stay under it)
Decode mid-beat frames from any mp4 with PyAV into a single grid image saved under /home/user (the sandbox auto-captures new images and returns them to you). SKILL.md step 5 has the exact snippet. You are checking: does each beat SHOW what its narration says; is the palette continuous; did any caption drift or split; is any surface pinched (camera, not geometry).

HANDOFF TO THE FILM
Clips go to workspace files, then onto a video_editor timeline. The assembly is FOUR calls (SKILL.md step 4): narrate_script → export-to-measure → sync_narration_to_shots → export. The one 3D-specific fact: manim clips are FIXED length — sync slows an outrun clip automatically (floor 0.65×; 0.8-0.9 reads as contemplative), and a line even the floor cannot fit comes back with a word budget: rewrite the words, never trim mid-sentence.

THINGS THAT GO WRONG, AND WHAT THEY MEAN
- MathTex/Tex raises: no LaTeX in the sandbox. Text for captions, formulas on cards.
- A surface renders as a pinched bowtie: azimuth, not geometry — rotate the camera.
- A caption orbits, drifts, or half of it moves: `.become()` without re-registering, or an always_redraw caption.
- An axis label reads backwards or edge-on mid-orbit: it was added raw or fixed-in-frame — it wanted add_fixed_orientation_mobjects.
- Rendering crawls at seconds per frame: always_redraw on a Surface, or shaded resolution too high for a draft.
- Renders die ~25% through with nothing alive: client timeout killed a blocking cell — relaunch detached.
- A success marker but no mp4: the script lacked set -euo pipefail.
- /home/user is suddenly empty: sandbox restart. What was saved to workspace files survived.
- Background jumps between scenes and cards: config.background_color was never set to the theme's colour.
- Everything after an orbit is misaligned with its narration: ambient rotation was never stopped.
