#!/usr/bin/env python3
"""
The measurement battery: what you check when you CANNOT SEE the film.

Every check here answers a question a human would answer by looking, and prints
a text verdict that survives the storefront's 20K text cap. Run it on a draft
(-ql) before finals, and on the final export.

    python verify_frames.py FILM.mp4 --marks 3,12,25,37 --theme dark
    python verify_frames.py CARD.png --card            # one still

Checks, in the order they catch things:
  FLAT     nothing rendered in that beat (uniform frame)
  BARS     pure-black border strips = a card not authored at 1232x672
  LIVE     live-area extent — the "geometrically perfect and too small" defect.
           Live area should be 45-65% of frame width, centred within ~5%.
  BANDS    contiguous horizontal ink bands (y/x extents) — clean gaps prove no
           collision; margins prove no overflow. Per-band cluster counts catch
           a glyph that silently vanished or fell back.
  PALETTE  pixels near each theme hue, per beat — proves colour continuity AND
           tracks the argument (a hue should APPEAR on the beat that earns it).
  CONTRAST per ink band, a dense text cluster whose luminance barely differs
           from bg = near-invisible text (dark-on-dark / pale-on-paper).
  AUDIO    per-beat narration RMS — catches a dead beat, which no visual check
           does.

scipy is optional (cluster counts degrade to "-" without it).
"""
import argparse, sys
import numpy as np

try:
    from scipy import ndimage  # optional: per-band glyph cluster counts
except Exception:
    ndimage = None

THEMES = {
    "dark": {"bg": (0x0B, 0x0E, 0x14), "hues": {
        "BLUE": (0x58, 0xC4, 0xDD), "RED": (0xFC, 0x62, 0x55),
        "YEL": (0xF4, 0xD3, 0x45), "GRN": (0x83, 0xC1, 0x67),
        "TXT": (0xF5, 0xF1, 0xE6), "GREY": (0x8A, 0x93, 0xA6),
        "DIM": (0x1E, 0x3A, 0x5F)}},
    "light": {"bg": (0xF9, 0xF9, 0xFB), "hues": {
        "INK": (0x3A, 0x57, 0xD8), "HOT": (0xE0, 0x31, 0x31),
        "GREY": (0x7C, 0x87, 0x94), "DARK": (0x1D, 0x1D, 0x1F)}},
    # punch (manim-punch-style): near-black infographic. bg is #0D0D0F, NOT
    # #000, so the BARS pad-detector stays alive. BOX is the component fill —
    # ambient-adjacent (panels are furniture, not subject), so it joins the
    # empty set like drip's DIM grid.
    "punch": {"bg": (0x0D, 0x0D, 0x0F), "hues": {
        "YEL": (0xFF, 0xD3, 0x4D), "BLU": (0x35, 0xB8, 0xF6),
        "RED": (0xFF, 0x4D, 0x4D), "GRN": (0x3D, 0xDC, 0x84),
        "TXT": (0xFF, 0xFF, 0xFF), "GREY": (0x9A, 0xA3, 0xAD),
        "PAPER": (0xEC, 0xE9, 0xE2), "BOX": (0x14, 0x17, 0x1C)}},
}


def ink_mask(rgb, bg, tol=30):
    """Pixels that differ from the theme background — i.e. anything drawn.
    Includes the ambient grid. CONTRAST needs this (it hunts text whose colour
    sits NEAR the background); LIVE does not (see content_mask)."""
    return np.linalg.norm(rgb.astype(np.int16) - np.array(bg, np.int16), axis=2) > tol


# Hues that are SCAFFOLD, not subject — the drip theme's ambient grid is drawn
# in DIM and spans the whole frame. A distance-from-background mask therefore
# reads ~99% "live" on every scene and tells you nothing (field report
# 2026-08-12: "the LIVE frame-fill metric is uninformative here"). Classify by
# nearest palette hue instead and count only the foreground. punch's BOX is the
# component panel fill — furniture, not subject — same treatment.
AMBIENT_HUES = ("DIM", "BOX")


def content_mask(rgb, theme, ambient=AMBIENT_HUES):
    """Pixels belonging to a FOREGROUND CONTENT hue — the subject, not the
    background and not an ambient/scaffold hue. Each pixel is assigned to its
    nearest palette centroid; it counts as content only when a content hue is
    closer than every 'empty' centroid (bg + the ambient hues). This is the
    semantic-hue mask the field report asked for: it ignores the full-frame
    grid, so LIVE measures the subject's real extent.

    Falls back to ink_mask when a theme defines no separable content hues (the
    light/paper theme has no grid, so distance-from-bg is already correct)."""
    th = THEMES[theme]
    px = rgb.astype(np.int16)
    empty = [np.array(th["bg"], np.int16)]
    content = []
    for name, hue in th["hues"].items():
        (empty if name in ambient else content).append(np.array(hue, np.int16))
    if not content:
        return ink_mask(rgb, th["bg"])
    d_empty = np.min([np.linalg.norm(px - c, axis=2) for c in empty], axis=0)
    d_content = np.min([np.linalg.norm(px - c, axis=2) for c in content], axis=0)
    return d_content < d_empty


def report_frame(rgb, theme, label, band_min_frac=0.002):
    th = THEMES[theme]
    h, w, _ = rgb.shape
    grey = rgb.mean(axis=2)
    out = [f"{label}  {w}x{h}"]

    # FLAT — a uniform frame means the scene rendered nothing.
    std = grey.std()
    out.append(f"  FLAT     std={std:6.1f}  {'DEAD BEAT' if std < 3.0 else 'ok'}")

    # BARS — the export's pad filter adds pure black; the theme bg is not pure black.
    strips = {"L": grey[:, :8], "R": grey[:, -8:], "T": grey[:8, :], "B": grey[-8:, :]}
    barred = [k for k, s in strips.items() if s.mean() < 4 and np.mean(th["bg"]) > 6]
    out.append(f"  BARS     {'PILLAR/LETTERBOX on ' + ','.join(barred) if barred else 'none'}")

    # LIVE — the under-filled-frame defect ("geometrically perfect and too
    # small"). Measured on the CONTENT-hue mask, not ink-vs-bg: the ambient
    # drip grid fills the frame, so ink-vs-bg read 0.99 on every scene and the
    # metric had to be eyeballed (field report 2026-08-12). There is no upper
    # "TOO WIDE" verdict any more — a subject that fills the frame is the goal,
    # not a defect; a real crop is EDGE's job.
    m = ink_mask(rgb, th["bg"])   # kept for EDGE / CONTRAST / BANDS below
    if m.sum() < 50:
        out.append("  LIVE     (no ink found)")
        return "\n".join(out), m
    cm = content_mask(rgb, theme)
    if cm.sum() < 50:
        out.append("  LIVE     (only ambient grid — no foreground content this beat)")
    else:
        ys, xs = np.where(cm)
        lw, lh = (xs.max() - xs.min() + 1) / w, (ys.max() - ys.min() + 1) / h
        cx = ((xs.min() + xs.max()) / 2 / w - 0.5) * 100
        cy = ((ys.min() + ys.max()) / 2 / h - 0.5) * 100
        verdict = "ok" if lw >= 0.45 else "TOO SMALL"
        if abs(cx) > 5 or abs(cy) > 5:
            verdict += " OFF-CENTRE"
        out.append(f"  LIVE     w={lw*100:4.1f}% h={lh*100:4.1f}% centre=({cx:+.1f}%,{cy:+.1f}%)  {verdict}  (content-hue)")

    # EDGE — content ink touching a frame border = something got CROPPED.
    # The manim camera crops silently: a label placed off an axis tip renders
    # half-missing with no error anywhere but here. Detection is the longest
    # CONTIGUOUS ink run along each 6px border strip (a whole-strip mean
    # dilutes a small clipped label to nothing — calibration showed a
    # half-cropped axis label at 0.5% strip mean but a 14px run). Distinct
    # from BARS, which is pure-black padding.
    # (Text-on-text collisions are NOT detected here: anti-aliasing makes
    # colour/density statistics unable to separate stacked text from a
    # legitimate kicker+title. That defect is prevented by the one-occupant-
    # per-band rule + the in-scene guard_frame, and caught by LOOKING.)
    def _run(v) -> int:
        best = cur = 0
        for x in v:
            cur = cur + 1 if x else 0
            if cur > best:
                best = cur
        return best

    edge_runs = {
        "T": _run(m[:6, :].any(axis=0)),
        "B": _run(m[-6:, :].any(axis=0)),
        "L": _run(m[:, :6].any(axis=1)),
        "R": _run(m[:, -6:].any(axis=1)),
    }
    clipped = [f"{k}({n}px)" for k, n in edge_runs.items() if n >= 12]
    out.append(f"  EDGE     {'CONTENT CROPPED at ' + ','.join(clipped) if clipped else 'clear'}")

    # CONTRAST — the dark-text-on-dark-background class. For each contiguous
    # ink band, the peak luminance of its DENSE core vs the background: a band
    # with a text-like ink density whose peak barely rises above bg is
    # near-invisible text. Faint grid lines are SPARSE, so density gates them
    # out (calibrated). The primary guard is in-scene (guard_frame); this is
    # the backstop for a frame rendered without one.
    lum = grey  # 0-255 luminance ≈ mean channel; bg luminance:
    bg_l = float(np.mean(th["bg"]))
    rows_ink = m.sum(axis=1)
    lo = []
    start = None
    for i in range(h + 1):
        on = i < h and rows_ink[i] > max(2, 0.002 * w)
        if on and start is None:
            start = i
        elif not on and start is not None:
            sub = m[start:i]
            dens = sub.mean()
            if dens > 0.03:  # text-like density; the grid mesh (~0.02) is sparser
                band_lum = lum[start:i][sub]  # luminance of THIS band's ink px
                if band_lum.size:
                    # The text CORE is the luminance extreme AWAY from bg —
                    # brightest on a dark theme, darkest on a light one (the
                    # anti-aliased edge sits near bg, so the wrong percentile
                    # falsely reads a legit dark-on-LIGHT label as low). Probe
                    # the core, direction-aware.
                    core = float(np.percentile(band_lum, 95 if bg_l < 128 else 5))
                    # Calibrated: DIM-on-black ~46, GREY caption ~135, TXT ~224.
                    if abs(core - bg_l) < 80:
                        lo.append(f"y={start}-{i} core={core:.0f} vs bg={bg_l:.0f}")
            start = None
    out.append(f"  CONTRAST {'LOW (near-invisible text?) ' + '; '.join(lo) if lo else 'ok'}")

    # BANDS — contiguous rows of ink. Gaps prove no collision.
    rows = m.sum(axis=1) > max(2, band_min_frac * w)
    bands, start = [], None
    for i, on in enumerate(rows):
        if on and start is None:
            start = i
        elif not on and start is not None:
            bands.append((start, i - 1)); start = None
    if start is not None:
        bands.append((start, len(rows) - 1))
    out.append(f"  BANDS    {len(bands)}")
    for (y0, y1) in bands[:8]:
        sub = m[y0:y1 + 1]
        bxs = np.where(sub.any(axis=0))[0]
        n = "-"
        if ndimage is not None:
            n = str(int(ndimage.label(sub)[1]))          # glyph clusters in this band
        out.append(f"    y={y0:4d}-{y1:<4d} x={bxs.min():4d}-{bxs.max():<4d} clusters={n}")
    if len(bands) > 8:
        out.append(f"    … {len(bands) - 8} more bands")

    # PALETTE — colour continuity, and does a hue arrive on the beat that earns it.
    hits = []
    for name, hue in th["hues"].items():
        d = np.linalg.norm(rgb.astype(np.int16) - np.array(hue, np.int16), axis=2)
        px = int((d < 40).sum())
        if px > 0.0005 * w * h:
            hits.append(f"{name}={px}")
    out.append(f"  PALETTE  {'  '.join(hits) if hits else '(none near theme hues)'}")
    return "\n".join(out), m


def audio_rms(path, marks, window=1.0):
    """Per-beat narration RMS. A silent beat is invisible to every pixel check."""
    import av
    try:
        c = av.open(path)
        if not c.streams.audio:
            return ["AUDIO    (no audio stream — narration not on this file)"]
        st = c.streams.audio[0]
        sr = st.rate
        buf = np.concatenate([f.to_ndarray().reshape(-1).astype(np.float32)
                              for f in c.decode(audio=0)]) if sr else np.array([])
        c.close()
        if buf.size == 0:
            return ["AUDIO    (empty)"]
        ch = st.channels or 1
        buf = buf.reshape(-1, ch).mean(axis=1) if ch > 1 and buf.size % ch == 0 else buf
        peak = float(np.abs(buf).max()) or 1.0
        lines = []
        for t in marks:
            a, b = int(max(0, (t - window / 2) * sr)), int((t + window / 2) * sr)
            seg = buf[a:b]
            r = float(np.sqrt((seg.astype(np.float64) ** 2).mean())) / peak if seg.size else 0.0
            lines.append(f"  t={t:6.1f}s rms={r:6.3f}  {'SILENT — dead beat' if r < 0.01 else 'ok'}")
        return ["AUDIO"] + lines
    except Exception as e:
        return [f"AUDIO    (unavailable: {type(e).__name__})"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--marks", default="", help="comma-separated mid-beat seconds")
    ap.add_argument("--theme", default="dark", choices=list(THEMES))
    ap.add_argument("--card", action="store_true", help="input is a single image")
    ap.add_argument("--want", default="", help="expected WxH for the DIMS check (default 1280x720)")
    a = ap.parse_args()

    if a.card:
        from PIL import Image
        rgb = np.asarray(Image.open(a.path).convert("RGB"))
        print(report_frame(rgb, a.theme, f"CARD {a.path}")[0])
        return

    marks = [float(x) for x in a.marks.split(",") if x.strip()]
    if not marks:
        sys.exit("--marks is required for a video (mid-point second of each beat)")

    import av
    c = av.open(a.path)
    vs = c.streams.video[0]
    fps = float(vs.average_rate)
    # DIMS — the finals-by-measurement check. A render script that globs the
    # quality directory (media/videos/<mod>/*/<scene>.mp4) sorts "480p15"
    # BEFORE "720p30" and silently copies DRAFTS into final/ — every other
    # check passes and a soft 480p film nearly ships. Exit codes and file
    # sizes never catch it; the pixel dimensions do. (--want overrides.)
    w, h = int(vs.codec_context.width), int(vs.codec_context.height)
    wantw, wanth = (int(x) for x in a.want.split("x")) if a.want else (1280, 720)
    ok = w == wantw and h == wanth
    print(
        f"DIMS     {w}x{h} @ {fps:g}fps  "
        + ("ok" if ok else f"WRONG — expected {wantw}x{wanth} (a DRAFT copied into finals?)")
    )
    print()
    want = {int(t * fps): t for t in marks}
    seen = 0
    # NEVER build a list of decoded frames — 720p frames are ~2.7MB each and
    # the kernel OOMs (it surfaces as "[object Object]" in stderr). Process
    # each frame and drop it.
    for i, f in enumerate(c.decode(video=0)):
        if i in want:
            rgb = np.asarray(f.to_image().convert("RGB"))
            print(report_frame(rgb, a.theme, f"BEAT t={want[i]:.1f}s")[0])
            print()
            seen += 1
        if i > max(want):
            break
    c.close()
    if seen < len(want):
        print(f"WARNING: only {seen}/{len(want)} marks found — film shorter than expected\n")
    for line in audio_rms(a.path, marks):
        print(line)


if __name__ == "__main__":
    main()
