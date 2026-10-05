#!/usr/bin/env python3
"""
Does every character in your formulas actually have a glyph on this box?

A codepoint no installed font covers renders as an empty tofu box — silently,
in the final film. This is ten seconds and decisive, so run it BEFORE committing
a dark (Unicode-formula) film, not after rendering one.

    pip install fonttools
    python glyph_check.py "⟨u,w⟩=0" "θₜ₊₁=θₜ−η∇L"      # your actual formula strings
    python glyph_check.py --default                      # the common maths set

Reports the FONT FAMILY per codepoint — that is the name Text(font="...") takes.

TWO FINDINGS WORTH KNOWING (measured, and they bite silently):
  • U+27E8/U+27E9 ⟨ ⟩ — the CORRECT angle brackets — commonly live only in the
    BOLD face of DejaVu Sans. If your formula Text is not weight=BOLD, it can
    fall back to a different glyph. Set weight=BOLD on formula text.
  • U+2329/U+232A 〈 〉 look identical in a code editor but are CJK ANGLE
    BRACKETS: they exist only in Noto CJK and render FULL-WIDTH. Wrong glyph,
    no warning. Always use 27E8/27E9.

If a character comes back TOFU, the fix order is:
  1. Reformulate the maths so it does not need that character. This is usually
     the RIGHT answer and often improves the film — writing cₖ = ⟨f, eₖ⟩ over
     sines and cosines beats e^{-2πixξ} for an audience anyway.
  2. Install a font that covers it and pass font="<family>".
  3. Only then consider switching the film to the light LaTeX-card theme.
"""
import glob
import sys

DEFAULT = "⟨⟩∫Σ√≠≈⊥→θ∇·×∞✓ₜ₊₁₀₂ᵢⱼₖ∂∈ℝℂαβγδελμπστφψωΔΩ±∓≤≥∀∃∅∪∩⊂⊆"

SUSPECT = {
    0x2329: "CJK-equivalent angle bracket — full-width, WRONG. Use U+27E8 ⟨.",
    0x232A: "CJK-equivalent angle bracket — full-width, WRONG. Use U+27E9 ⟩.",
    0x3008: "CJK angle bracket — full-width, WRONG. Use U+27E8 ⟨.",
    0x3009: "CJK angle bracket — full-width, WRONG. Use U+27E9 ⟩.",
    0x27E8: "correct angle bracket — often BOLD-face only; set weight=BOLD.",
    0x27E9: "correct angle bracket — often BOLD-face only; set weight=BOLD.",
}


def main():
    args = [a for a in sys.argv[1:] if a != "--default"]
    text = "".join(args) if args else DEFAULT
    chars = sorted(set(c for c in text if not c.isascii() or not c.isalnum()), key=ord)
    chars = [c for c in chars if not c.isspace()]
    if not chars:
        print("nothing non-ASCII to check")
        return

    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        sys.exit("pip install fonttools first")

    have = {c: [] for c in chars}
    scanned = 0
    for path in glob.glob("/usr/share/fonts/**/*.tt[fc]", recursive=True):
        try:
            f = TTFont(path, fontNumber=0, lazy=True)
            fam = f["name"].getDebugName(1) or path
            sub = f["name"].getDebugName(2) or ""      # Regular / Bold / …
            cmap = f.getBestCmap() or {}
            for c in chars:
                if ord(c) in cmap:
                    have[c].append(f"{fam}{' ' + sub if sub and sub != 'Regular' else ''}")
            f.close()
            scanned += 1
        except Exception:
            continue

    missing = 0
    for c in chars:
        fonts = have[c]
        note = SUSPECT.get(ord(c), "")
        if fonts:
            only_bold = fonts and all("Bold" in x for x in fonts)
            flag = "OK  "
            extra = fonts[0] + (" [BOLD-ONLY — set weight=BOLD]" if only_bold else "")
        else:
            missing += 1
            flag, extra = "TOFU", "NO installed font has this glyph"
        print(f"{flag} U+{ord(c):04X} {c}  {extra}{('  ← ' + note) if note else ''}")

    print(f"\nscanned {scanned} font files; {len(chars) - missing}/{len(chars)} covered")
    if missing:
        print("REFORMULATE the maths before you switch the film to the light theme.")


if __name__ == "__main__":
    main()
