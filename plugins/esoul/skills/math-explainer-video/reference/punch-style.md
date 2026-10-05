# The punch style — black infographic manim + Gemini image inserts

> Use when the film explains a SYSTEM, product, cost, comparison, architecture or pipeline — the black infographic register: near-black stage, neon-glow pills/cards/stamps/badges/gauges/checklists, mono ALL-CAPS letterspaced labels, huge hero numbers, one or two punchy meaning-coded accents per frame. "punchy", "black background with neon colors", "tech-explainer / infographic style". A STYLE layer like reference/drip-style.md: SKILL.md owns the pipeline; drip owns continuous-maths beauty (surfaces, morphing curves, the character); THIS owns systems/data storytelling — plant diagrams, price cards, request flows, checklists. One theme per film. Includes the Gemini image arm.

**LaTeX note (measured 2026-08-10).** Where this file says LaTeX is
unavailable and `MathTex`/`Tex`/`DecimalNumber`/`get_graph_label` crash, read that as
*until you install it*. The sandbox is Debian 12 with passwordless sudo:
`sudo apt-get install -y --no-install-recommends texlive-latex-base texlive-latex-extra dvisvgm`
takes ~56s and 255MB, after which `MathTex` renders (verified: `manim -ql` exit 0, real mp4).
Every no-LaTeX idiom below remains correct if you skip that install — and remains the right choice
for captions, which want Pango `Text` regardless.

THE LOOK IN ONE SENTENCE
Black is the stage, not a background: sparse glowing components float in it, every word is ALL-CAPS mono with wide letter-spacing, ONE number per beat is huge, and colour appears only where it MEANS something.

PALETTE
  BG="#0D0D0F"   near-black, NOT #000 — the export pad filter is pure black, so a pure-black bg would blind the BARS letterbox check in verify_frames; #0D0D0F is visually identical and keeps the detector alive
  BOX="#14171C"  component fill (cards/pills read as solid panels, never transparent)
  YEL="#FFD34D"  BLU="#35B8F6"  RED="#FF4D4D"  GRN="#3DDC84"
  TXT="#FFFFFF"  GREY="#9AA3AD" (kickers/captions/body)  PAPER="#ECE9E2"
  config.background_color = BG. NO ambient grid — that is drip; punch floats on clean black.
MEANING-CODE film-wide and never reuse: BLU=flow/input, YEL=hero/highlight, RED=cost/warning, GRN=success/done. A frame carries ONE or TWO accents; everything else is TXT/GREY/BOX. Three accents in a frame reads as noise — recolor toward the frame's one claim.

TYPE SCALE — the proportions ARE the style
Font: JetBrains Mono (sandbox: sudo apt-get install -y fonts-jetbrains-mono && fc-cache -f; fallback "DejaVu Sans Mono" ships everywhere). Name it "JetBrains Mono NL" in code: the plain family has LIGATURES, so `<<<`, `->`, `!=` become one glyph each — code on screen changes shape and `text[6:10]` indexes the wrong characters (a CUDA film coloured "96,25" instead of "4096", 2026-09-28). The signature is mono + CAPS + LETTERSPACING:
  def label(s, size=28, color=TXT, ls=7000):
      return MarkupText(f'<span letter_spacing="{ls}">{s.upper()}</span>',
                        font=MONO, font_size=size, color=color)
(Pango letter_spacing is 1024ths of a pt. Measured on a 720p film, 2026-09-28: 2000–2500 at sizes 18–28 reads designed; 6000+ reads as letters drifting apart and pushes labels off frame. Titles ~3000.)
The RATIOS, film-wide — break one and the frame stops looking designed:
  HERO number 150 bold (one per beat, MAX)  ·  headline 46 caps YEL/TXT  ·  label 26-28 letterspaced
  body 30 mono sentence-case GREY with the keyword tinted (t2c={"sofic": YEL})
  kicker 24 GREY letterspaced top-center  ·  caption 22 GREY bottom-left (the hud slot)
Hero ≥ 3× headline ≥ 1.6× label. Body text max ~2 lines × ~46 chars. If a frame needs a paragraph, it needs two beats.

GLOW — same three strokes as drip (halo, corona, core)
  def glow(vmob, color, width=3.5):
      return VGroup(
          vmob.copy().set_stroke(color, width*5.0, opacity=0.10).set_fill(opacity=0),
          vmob.copy().set_stroke(color, width*2.4, opacity=0.25).set_fill(opacity=0),
          vmob.set_stroke(color, width, opacity=1))
Glow OUTLINES (pills, cards, gauge arcs, accent rules) — never body text. A hero number glows via fill-less copies UNDER it (see hero()).

THE COMPONENT KIT (verified shapes — compose beats from these, don't redraw)
  def pill(s, color, size=28):
      t = label(s, size, color)
      r = RoundedRectangle(corner_radius=0.32, width=t.width+0.9, height=t.height+0.55,
                           fill_color=BOX, fill_opacity=1).move_to(t)
      return VGroup(glow(r, color), t)
  def card(color, w=3.4, h=1.9, title=None):
      r = RoundedRectangle(corner_radius=0.16, width=w, height=h, fill_color=BOX, fill_opacity=1)
      g = VGroup(glow(r, color, 4.5))
      if title: g.add(label(title, 24, color).move_to(r.get_top() + DOWN*0.42))
      return g
  def stamp(s, color, angle=-6*DEGREES):        # the slammed verdict: NO FREE LUNCH / IMMUTABLE
      t = label(s, 26, color, ls=3000)
      r = Rectangle(width=t.width+0.5, height=t.height+0.3).set_stroke(color, 5).set_fill(BG, 1)
      return VGroup(r, t).rotate(angle)
  def badge(s, color):                          # solid chip, dark text: COINED: SOFICITY
      t = label(s, 24, BG, ls=3000)
      return VGroup(Rectangle(width=t.width+0.44, height=t.height+0.28,
                    fill_color=color, fill_opacity=1, stroke_width=0), t)
  def check(s, color=BLU):                      # one checklist row
      box = Square(0.34).set_stroke(color, 3).set_fill(color, 1)
      return VGroup(box, Text("✓", font_size=24, color=BG).move_to(box),
                    label(s, 24, TXT, ls=4000).next_to(box, RIGHT, 0.25))
  def hero(n, unit="", color=YEL):              # the huge number, glow under the fill
      t = Text(str(n), font=MONO, weight=BOLD, font_size=150, color=color)
      halo = VGroup(*[t.copy().set_fill(opacity=0).set_stroke(color, w, opacity=o)
                      for w, o in ((16, 0.10), (7, 0.22))])
      g = VGroup(halo, t)
      return VGroup(g, label(unit, 30, TXT).next_to(t, DOWN, 0.15)) if unit else g
  def paper(*rows, w=6.8, tilt=2*DEGREES):      # the off-white card insert (dark text on it!)
      r = RoundedRectangle(corner_radius=0.1, width=w, height=len(rows)*0.9 + 1.2,
                           fill_color=PAPER, fill_opacity=1, stroke_width=0)
      sh = r.copy().set_fill("#000000", 0.55).set_stroke(width=0).shift(DOWN*0.07 + RIGHT*0.07)
      g = VGroup(*rows).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to(r)
      return VGroup(sh, r, g).rotate(tilt)
Composites of the kit (no new primitives): GAUGE = dim GREY track Arc + glow(value Arc, BLU) + tick label()s + hero() centered, counted up on a ValueTracker (set-pieces COUNTER idiom). FLOW = pills/cards joined by Arrow(color=TXT, stroke_width=5), revealed left→right as narration names each. PROGRESS = track Rectangle + glow(fill Rectangle, accent). COMPARISON = two card()s flanking a diamond/divider, a stamp() slammed between them.

MOTION — few, decisive moves (punchy = restraint)
- Components ARRIVE: FadeIn(m, scale=0.92), run_time 0.3, in narration order — never all at once.
- Stamps SLAM: FadeIn(st, scale=1.8), run_time 0.25, rate_func=rate_functions.rush_from, AFTER the thing they judge is on screen.
- Heroes COUNT UP (ease_out_expo lands the number); gauges sweep while counting.
- Emphasis = glow pulse (animate the core stroke width 1.3× and back), not movement.
- Everything not moving is STILL. One thing moves at a time. Camera stays fixed — punch has no zooms; a detail beat is a new frame.

STAGE MANAGEMENT
≤5 components per frame — black space IS the layout. Bands + guard rules from set-pieces FRAME DISCIPLINE apply unchanged, and this style is guard_scene's best case (everything is rects + text): subclass GuardedScene and every wait() checks straddle/collision/off-frame/contrast free. Cards are manim stills exactly like drip (render -qm -s → PNG → image clip); a formula Unicode can't write still means a light-paper film, not a punch one (no LaTeX in the sandbox by default).

GEMINI IMAGES — when the subject is photographic, generate it, then annotate it
Manim can't draw a GPU, a brain, a clarifier tank's steel, a person. For those beats: generate the image, put it ON the black stage, and let manim do all the talking on top.
- WHEN: photographic/organic/textured subject as a cutaway or an annotated hero. Never for anything manim draws honestly (charts, boxes, flows — drawing is free and editable; an image is neither).
- HOW (esoul chat/agent): generate_image → the result carries [fileId]. Two mounts:
  (a) timeline still: add_clips {fileId, imageSeconds} between manim beats — a full-frame cutaway;
  (b) in-scene: copy_file_to_sandbox(fileId) → ImageMobject(path).scale_to_fit_height(4.2), mounted INSIDE a card() frame, then pills/arrows/labels composed around it. The card mount also hides any imperfect edges.
- PROMPT RULES (each earned): "isolated on a pure black background, 16:9, no text, no watermark" — the black ground makes the composite seamless. NEVER let the image model render words: AI text is mush, and the whole typography discipline above exists so every word is crisp vector manim. Reuse ONE style clause across the film ("dark studio product photo, single amber key light") — per-image improvisation reads as stock-photo soup.
- SURFACES: generate_image is a chat/agent workspace tool — over the MCP storefront it is NOT exposed; generate from esoul chat or an invoked agent first, then use the fileId (workspace images list via list_files / the sandbox sync).
- Generated stills ride the same verification: they go on the contact sheet, DIMS applies, and the LOOK judges whether the style clause held.

VERIFY
verify_frames.py has a "punch" THEMES entry (bg #0D0D0F + these hues). No ambient hue — unlike drip there is no grid, so LIVE's content mask and plain ink agree. The BARS check works BECAUSE bg ≠ #000 (see PALETTE). Everything else — DIMS, EDGE, CONTRAST, the contact sheet, and the set-pieces in-scene guard — applies unchanged.
