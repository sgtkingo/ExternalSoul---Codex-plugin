Use when a slide deck should wear the FLORAL PAPER theme — warm ivory slides, cream cards, brown-black ink, teal + amber for data, and a low-key floral ornament — exactly as built for the Autoresearch deck (2026-09-02). This is a STYLE layer for the slideshow app: `reference/themes.md` owns the procedure (list / apply / create); THIS owns the tokens, the scaffold and the component recipes. Copy them; do not redesign. Every slide is one TSX source with a top-level `function Component()` on a fixed 1280×720 canvas, inline styles only, no libraries.

TOKENS (use these hex values verbatim, never others)
PAPER "#fbf7ef" (slide ground) · CARD "#fffdf8" (cards) · SOFT "#f1eadc" (soft panels) · RULE "#e4d9c6" (borders, grey bars) · INK "#2a2118" (text) · MUTED "#7a6a58" (captions, eyebrows) · WAIT "#1f7a72" (teal: waiting, prefill, the "good" series) · GEN "#c2571a" (amber: generation, losses, the second series).
FONT "'Helvetica Neue', Helvetica, Arial, sans-serif" · MONO "ui-monospace, 'SF Mono', Menlo, Consolas, monospace" (every number, every eyebrow).

SCAFFOLD — paste this whole block, then fill BODY. The ornaments are literal SVG; keep them exactly.
```tsx
const P = { paper: "#fbf7ef", card: "#fffdf8", soft: "#f1eadc", rule: "#e4d9c6", ink: "#2a2118", muted: "#7a6a58", wait: "#1f7a72", gen: "#c2571a" };
const FONT = "'Helvetica Neue', Helvetica, Arial, sans-serif";
const MONO = "ui-monospace, 'SF Mono', Menlo, Consolas, monospace";
const Corner = () => (
  <svg viewBox="0 0 340 340" style={{ position: "absolute", right: -8, bottom: -16, width: 300, height: 300, pointerEvents: "none" }}><path d="M 250 330 C 236 268 214 228 176 196" stroke="#1f7a72" strokeWidth="2.5" fill="none" opacity="0.28" strokeLinecap="round"/><path d="M 250 330 C 270 262 262 214 296 170" stroke="#1f7a72" strokeWidth="2.5" fill="none" opacity="0.28" strokeLinecap="round"/><ellipse cx="176" cy="159.0" rx="12.6" ry="28.5" transform="rotate(0 176 186)" fill="#c2571a" opacity="0.3"/><ellipse cx="176" cy="159.0" rx="12.6" ry="28.5" transform="rotate(72 176 186)" fill="#c2571a" opacity="0.3"/><ellipse cx="176" cy="159.0" rx="12.6" ry="28.5" transform="rotate(144 176 186)" fill="#c2571a" opacity="0.3"/><ellipse cx="176" cy="159.0" rx="12.6" ry="28.5" transform="rotate(216 176 186)" fill="#c2571a" opacity="0.3"/><ellipse cx="176" cy="159.0" rx="12.6" ry="28.5" transform="rotate(288 176 186)" fill="#c2571a" opacity="0.3"/><circle cx="176" cy="186" r="9.6" fill="#c2571a" opacity="0.48"/><ellipse cx="298" cy="138.4" rx="10.1" ry="22.8" transform="rotate(0 298 160)" fill="#1f7a72" opacity="0.3"/><ellipse cx="298" cy="138.4" rx="10.1" ry="22.8" transform="rotate(72 298 160)" fill="#1f7a72" opacity="0.3"/><ellipse cx="298" cy="138.4" rx="10.1" ry="22.8" transform="rotate(144 298 160)" fill="#1f7a72" opacity="0.3"/><ellipse cx="298" cy="138.4" rx="10.1" ry="22.8" transform="rotate(216 298 160)" fill="#1f7a72" opacity="0.3"/><ellipse cx="298" cy="138.4" rx="10.1" ry="22.8" transform="rotate(288 298 160)" fill="#1f7a72" opacity="0.3"/><circle cx="298" cy="160" r="7.7" fill="#1f7a72" opacity="0.48"/><ellipse cx="244" cy="220.7" rx="7.1" ry="16.1" transform="rotate(0 244 236)" fill="#c2571a" opacity="0.26"/><ellipse cx="244" cy="220.7" rx="7.1" ry="16.1" transform="rotate(72 244 236)" fill="#c2571a" opacity="0.26"/><ellipse cx="244" cy="220.7" rx="7.1" ry="16.1" transform="rotate(144 244 236)" fill="#c2571a" opacity="0.26"/><ellipse cx="244" cy="220.7" rx="7.1" ry="16.1" transform="rotate(216 244 236)" fill="#c2571a" opacity="0.26"/><ellipse cx="244" cy="220.7" rx="7.1" ry="16.1" transform="rotate(288 244 236)" fill="#c2571a" opacity="0.26"/><circle cx="244" cy="236" r="5.4" fill="#c2571a" opacity="0.42"/><path d="M224 282 q 15.4 -19.8 44.0 0 q -28.6 19.8 -44.0 0 z" transform="rotate(-40 224 282)" fill="#1f7a72" opacity="0.26"/><path d="M262 256 q 14.0 -18.0 40.0 0 q -26.0 18.0 -40.0 0 z" transform="rotate(20 262 256)" fill="#1f7a72" opacity="0.22"/><path d="M206 236 q 11.9 -15.3 34.0 0 q -22.1 15.3 -34.0 0 z" transform="rotate(-75 206 236)" fill="#1f7a72" opacity="0.2"/></svg>
);
const Sprig = () => (
  <svg viewBox="0 0 60 30" style={{ width: 60, height: 30, display: "inline-block", verticalAlign: "middle", marginRight: 10 }}><path d="M 4 26 C 20 22 34 16 46 6" stroke="#1f7a72" strokeWidth="2" fill="none" opacity="0.55" strokeLinecap="round"/><path d="M14 23 q 4.9 -6.3 14.0 0 q -9.1 6.3 -14.0 0 z" transform="rotate(-30 14 23)" fill="#1f7a72" opacity="0.5"/><path d="M28 15 q 4.5 -5.9 13.0 0 q -8.5 5.9 -13.0 0 z" transform="rotate(-20 28 15)" fill="#1f7a72" opacity="0.45"/><ellipse cx="48" cy="0.6" rx="2.5" ry="5.7" transform="rotate(0 48 6)" fill="#c2571a" opacity="0.7"/><ellipse cx="48" cy="0.6" rx="2.5" ry="5.7" transform="rotate(72 48 6)" fill="#c2571a" opacity="0.7"/><ellipse cx="48" cy="0.6" rx="2.5" ry="5.7" transform="rotate(144 48 6)" fill="#c2571a" opacity="0.7"/><ellipse cx="48" cy="0.6" rx="2.5" ry="5.7" transform="rotate(216 48 6)" fill="#c2571a" opacity="0.7"/><ellipse cx="48" cy="0.6" rx="2.5" ry="5.7" transform="rotate(288 48 6)" fill="#c2571a" opacity="0.7"/><circle cx="48" cy="6" r="1.9" fill="#c2571a" opacity="1.00"/></svg>
);
function Component(props) {
  return (
    <div style={{ width: "100%", height: "100%", boxSizing: "border-box", display: "flex", flexDirection: "column", background: P.paper, color: P.ink, fontFamily: FONT, padding: "56px 72px 44px", position: "relative", overflow: "hidden" }}>
      <Corner />
      <div style={{ position: "relative", flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>
        <div style={{ fontFamily: MONO, fontSize: 14, letterSpacing: "0.14em", textTransform: "uppercase", color: P.muted, marginBottom: 12, display: "flex", alignItems: "center" }}><Sprig />EYEBROW</div>
        <div style={{ fontSize: 46, fontWeight: 700, lineHeight: 1.12, letterSpacing: "-0.02em", marginBottom: 26 }}>TITLE, one sentence, at most two lines</div>
        BODY
      </div>
    </div>
  );
}
```

COMPONENT RECIPES (JSX fragments for BODY; sizes are px for the 1280×720 canvas)
- Big-number tile: `<div style={{ flex: 1, background: P.card, border: `1px solid ${P.rule}`, borderRadius: 14, padding: "24px 26px", boxShadow: "0 1px 0 rgba(42,33,24,0.05)" }}><div style={{ fontFamily: MONO, fontSize: 54, fontWeight: 600, color: P.gen, lineHeight: 1, letterSpacing: "-0.02em" }}>33 → 50</div><div style={{ fontSize: 20, color: P.muted, marginTop: 12, lineHeight: 1.3 }}>tokens per second, +52 %</div></div>` — put 2–3 in a `display:flex; gap:20` row; the caption is ONE short line (≤ 5 words).
- Titled card (three per row): same box with `borderTop: "5px solid " + P.wait` (or P.gen, P.ink to distinguish siblings), a 28px bold title, then ONE sentence at 20px in P.muted.
- Soft panel (a callout, a closing line): `background: P.soft, borderRadius: 14, padding: "22px 26px", fontSize: 24, lineHeight: 1.4`, bold the first two words.
- Number row inside a panel: `display:flex; gap:12; alignItems:baseline; padding:"7px 0"; borderTop: 1px solid P.rule` with the number in MONO 22px bold at `flex: "0 0 84px"` and the text at 16.5px, `whiteSpace: "nowrap"` — write it to FIT (≤ 55 chars), never let it wrap.
- Step rail (a process): a row of `flex:1` columns, each a 72px circle (`border: 3px solid <accent>`, MONO 26px number), a 30px bold one-word name, one 18px P.muted line (≤ 8 words); a 3px P.rule line behind the circles at `top: 36`.
- Table of specs: rows of `display:flex; justifyContent:space-between; padding:"7px 0"; borderBottom: 1px solid P.rule; fontSize:18`, label in P.muted, value in MONO bold.

CHARTS — inline SVG, drawn to scale, never a library
- Bars: `<rect rx="8" fill={P.gen}/>` for the series, `fill={P.rule}` for a grey reference, labels `<text fontSize="18">` in P.ink, the value in MONO bold beside the bar. Horizontal bars, label column on the left (textAnchor="end").
- Lines: `<path fill="none" stroke={P.wait} strokeWidth="3"/>`, points `<circle r="7" fill={P.card} stroke={P.wait} strokeWidth="3"/>`, grid `<line stroke={P.rule}/>`, a dashed fit `strokeDasharray="7 6"` in P.muted, axis ticks `<text fontSize="16" fill={P.muted}>`.
- Size: chart `viewBox="0 0 560 330"` on the left, a text column on the right; or `viewBox="0 0 1136 330"` full width. One caption line under the chart at 15px P.muted, ≤ 70 chars.
- Inside SVG text, never put a double-quoted font name in a double-quoted attribute; font inherits from the root div.

RULES THAT KEEP IT LOOKING LIKE THIS
1. One idea per slide: a title, then at most one chart + one text column, or three tiles/cards + one panel. 6–7 slides for a talk.
2. Words are scarce: title ≤ 12 words; a card ≤ 1 sentence; a bullet ≤ 12 words; no paragraphs over 40 words. If it does not fit at these sizes, split the slide — never shrink fonts.
3. Never vw/vh/rem; never exceed 720px of content; never a second accent colour; never white (#fff) — the cards are #fffdf8.
4. Numbers come from the user's data or the workspace; if a number is uncertain, leave it out rather than round it up.
5. The ornaments stay: Corner on every slide (it sits behind content), Sprig before every eyebrow. Do not add more flowers; low key is the theme.
6. Before add_slide, check the TSX: `function Component` present, every tag closed, brackets balanced. Then `critique_slide` once on the most crowded slide only.

VARIANT "ink" (the same scaffold, dark): PAPER "#0e1420", CARD "#151d29", SOFT "#1a2433", RULE "#233040", INK "#e9eef4", MUTED "#8b98a6", WAIT "#3fb5bf", GEN "#e8834a"; drop the Corner, keep the Sprig. Use only when the user asks for dark.