Use when a slide deck should wear the STARRY NIGHT theme — deep indigo night, a faint starfield, a small constellation by the eyebrow, gold for the signal and sky-blue for the reference — exactly as built for the Sheet Edge Counter deck (2026-09-03). A STYLE layer for the slideshow app: `reference/themes.md` owns the procedure (list / apply / create); THIS owns the tokens, the scaffold and the recipes. Copy them; do not redesign. Every slide is one TSX source with a top-level `function Component()` on a fixed 1280×720 canvas, inline styles only, no libraries.

TOKENS (verbatim, never others)
NIGHT "#0f1633" (slide ground) · CARD "#161f44" (cards) · SOFT "#1b264f" (soft panels) · RULE "#2b3868" (borders, grid, range bars) · INK "#eef0f7" (text) · MUTED "#9aa3c2" (captions, eyebrows) · STAR "#f2d38a" (gold: the signal, the winning series, the headline number) · SKY "#7cc4d9" (sky-blue: the reference, the second series). A loss or a refutation may use "#d97b6b" once per deck.
FONT "'Helvetica Neue', Helvetica, Arial, sans-serif" · MONO "ui-monospace, 'SF Mono', Menlo, Consolas, monospace" (every number, every eyebrow).

SCAFFOLD — paste whole, fill BODY. The starfield and the constellation are literal SVG; keep them exactly (the stars are a fixed pattern, so every slide of a deck shares one sky).
```tsx
const P = { night: "#0f1633", card: "#161f44", soft: "#1b264f", rule: "#2b3868", ink: "#eef0f7", muted: "#9aa3c2", star: "#f2d38a", sky: "#7cc4d9" };
const FONT = "'Helvetica Neue', Helvetica, Arial, sans-serif";
const MONO = "ui-monospace, 'SF Mono', Menlo, Consolas, monospace";
const Sky = () => (
  <svg viewBox="0 0 1280 720" preserveAspectRatio="none" style={{ position: "absolute", inset: 0, width: "100%", height: "100%", pointerEvents: "none" }}>
    <defs><radialGradient id="glow" cx="0.85" cy="0.1" r="0.5"><stop offset="0" stopColor="#7cc4d9" stopOpacity="0.16"/><stop offset="1" stopColor="#7cc4d9" stopOpacity="0"/></radialGradient></defs>
    <rect x="0" y="0" width="1280" height="720" fill="url(#glow)"/>
    <circle cx="764" cy="215" r="1.1" fill="#eef0f7" opacity="0.67"/><circle cx="131" cy="704" r="2.1" fill="#eef0f7" opacity="0.40"/><circle cx="438" cy="557" r="2.0" fill="#f2d38a" opacity="0.72"/><circle cx="13" cy="312" r="1.7" fill="#f2d38a" opacity="0.60"/><circle cx="10" cy="406" r="0.8" fill="#eef0f7" opacity="0.79"/><circle cx="571" cy="695" r="1.4" fill="#eef0f7" opacity="0.73"/><circle cx="546" cy="284" r="1.8" fill="#eef0f7" opacity="0.33"/><circle cx="940" cy="456" r="0.8" fill="#eef0f7" opacity="0.43"/><circle cx="783" cy="299" r="0.6" fill="#f2d38a" opacity="0.78"/><circle cx="614" cy="295" r="0.9" fill="#f2d38a" opacity="0.35"/><circle cx="351" cy="587" r="1.0" fill="#eef0f7" opacity="0.60"/><circle cx="1122" cy="466" r="1.1" fill="#eef0f7" opacity="0.26"/><circle cx="347" cy="700" r="1.3" fill="#eef0f7" opacity="0.64"/><circle cx="601" cy="387" r="1.2" fill="#f2d38a" opacity="0.69"/><circle cx="333" cy="523" r="1.8" fill="#eef0f7" opacity="0.25"/><circle cx="664" cy="190" r="1.7" fill="#eef0f7" opacity="0.80"/><circle cx="409" cy="160" r="0.7" fill="#eef0f7" opacity="0.62"/><circle cx="1204" cy="646" r="1.1" fill="#eef0f7" opacity="0.48"/><circle cx="982" cy="49" r="1.1" fill="#f2d38a" opacity="0.36"/><circle cx="1053" cy="717" r="1.2" fill="#eef0f7" opacity="0.58"/><circle cx="168" cy="197" r="2.0" fill="#eef0f7" opacity="0.41"/><circle cx="866" cy="483" r="1.1" fill="#f2d38a" opacity="0.35"/><circle cx="842" cy="229" r="0.8" fill="#f2d38a" opacity="0.79"/><circle cx="936" cy="720" r="0.9" fill="#eef0f7" opacity="0.80"/><circle cx="229" cy="544" r="1.4" fill="#eef0f7" opacity="0.54"/><circle cx="727" cy="330" r="1.6" fill="#eef0f7" opacity="0.50"/><circle cx="70" cy="554" r="1.3" fill="#eef0f7" opacity="0.64"/><circle cx="155" cy="640" r="1.3" fill="#f2d38a" opacity="0.39"/><circle cx="749" cy="677" r="1.1" fill="#f2d38a" opacity="0.71"/><circle cx="538" cy="528" r="1.3" fill="#f2d38a" opacity="0.77"/><circle cx="174" cy="107" r="1.9" fill="#eef0f7" opacity="0.49"/><circle cx="356" cy="282" r="1.4" fill="#eef0f7" opacity="0.71"/><circle cx="769" cy="498" r="1.1" fill="#f2d38a" opacity="0.31"/><circle cx="384" cy="500" r="1.5" fill="#eef0f7" opacity="0.50"/><circle cx="226" cy="310" r="0.8" fill="#f2d38a" opacity="0.69"/><circle cx="29" cy="239" r="1.4" fill="#eef0f7" opacity="0.35"/><circle cx="5" cy="611" r="1.5" fill="#eef0f7" opacity="0.34"/><circle cx="668" cy="530" r="0.8" fill="#eef0f7" opacity="0.60"/><circle cx="698" cy="120" r="1.6" fill="#eef0f7" opacity="0.61"/><circle cx="421" cy="640" r="1.0" fill="#eef0f7" opacity="0.81"/><circle cx="1128" cy="72" r="1.4" fill="#f2d38a" opacity="0.30"/><circle cx="1119" cy="180" r="1.6" fill="#eef0f7" opacity="0.80"/><circle cx="1129" cy="143" r="1.7" fill="#f2d38a" opacity="0.39"/><circle cx="1020" cy="447" r="1.1" fill="#f2d38a" opacity="0.40"/><circle cx="962" cy="710" r="2.1" fill="#eef0f7" opacity="0.81"/><circle cx="202" cy="708" r="1.1" fill="#eef0f7" opacity="0.56"/>
  </svg>
);
const Constellation = () => (
  <svg viewBox="0 0 64 28" style={{ width: 64, height: 28, display: "inline-block", verticalAlign: "middle", marginRight: 10 }}><line x1="6" y1="22" x2="18" y2="10" stroke="#7cc4d9" strokeWidth="1" opacity="0.6"/><line x1="18" y1="10" x2="34" y2="14" stroke="#7cc4d9" strokeWidth="1" opacity="0.6"/><line x1="34" y1="14" x2="46" y2="4" stroke="#7cc4d9" strokeWidth="1" opacity="0.6"/><line x1="46" y1="4" x2="58" y2="12" stroke="#7cc4d9" strokeWidth="1" opacity="0.6"/><circle cx="6" cy="22" r="1.8" fill="#eef0f7" opacity="0.95"/><circle cx="18" cy="10" r="2.6" fill="#f2d38a" opacity="0.95"/><circle cx="34" cy="14" r="1.8" fill="#eef0f7" opacity="0.95"/><circle cx="46" cy="4" r="2.6" fill="#f2d38a" opacity="0.95"/><circle cx="58" cy="12" r="1.8" fill="#eef0f7" opacity="0.95"/></svg>
);
function Component(props) {
  return (
    <div style={{ width: "100%", height: "100%", boxSizing: "border-box", display: "flex", flexDirection: "column", background: P.night, color: P.ink, fontFamily: FONT, padding: "56px 72px 44px", position: "relative", overflow: "hidden" }}>
      <Sky />
      <div style={{ position: "relative", flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>
        <div style={{ fontFamily: MONO, fontSize: 14, letterSpacing: "0.14em", textTransform: "uppercase", color: P.muted, marginBottom: 12, display: "flex", alignItems: "center" }}><Constellation />EYEBROW</div>
        <div style={{ fontSize: 46, fontWeight: 700, lineHeight: 1.12, letterSpacing: "-0.02em", marginBottom: 26 }}>TITLE, one sentence, at most two lines</div>
        BODY
      </div>
    </div>
  );
}
```
The title slide uses padding "64px 72px 56px", a 60px title, a 25px P.muted lede (≤ 30 words), then `<div style={{ flex: 1 }} />` and a row of three tiles.

COMPONENT RECIPES (JSX for BODY; px sizes for 1280×720)
- Big-number tile: `<div style={{ flex: 1, background: P.card, border: `1px solid ${P.rule}`, borderRadius: 14, padding: "24px 26px" }}><div style={{ fontFamily: MONO, fontSize: 54, fontWeight: 600, color: P.star, lineHeight: 1, letterSpacing: "-0.02em" }}>0.13</div><div style={{ fontSize: 20, color: P.muted, marginTop: 12, lineHeight: 1.3 }}>sheets of count error</div></div>` — 2–3 per row (`display:flex; gap:20`); the first tile gold, the second sky, the third ink; caption ≤ 8 words.
- Titled card (three per row): the same box with `borderTop: "5px solid " + P.star` (then P.sky, P.ink), a 28px bold title, ONE 20px sentence in P.muted.
- Soft panel: `background: P.soft, borderRadius: 14, padding: "20px 24px", fontSize: 22, lineHeight: 1.4`; bold the first few words; two side by side at 19px for a pair of takeaways.
- Spec table: rows `display:flex; justifyContent:space-between; padding:"7px 0"; borderBottom: 1px solid P.rule; fontSize:18`, label P.muted, value MONO bold, inside a card.
- Step rail: five `flex:1` columns, each a 72px circle (`border: 3px solid <accent>`, MONO 26px number), a 30px bold one-word name, one 18px P.muted line (≤ 8 words); a 3px P.rule line behind the circles at `top: 36`.
- Schematic (a data object drawn, not photographed): a narrow `<rect>` in "#070b1c" with an inner panel "#101a3c" and thin P.star lines — say "schematic" in its caption.

CHARTS — inline SVG, drawn to scale, never a library
- Range-and-dots (per-seed or per-item spread): a P.rule-coloured horizontal line from min to max at `strokeWidth="3" opacity="0.55"` in the series colour, one `<circle r="6">` per value; labels `<text fontSize="19" textAnchor="end">` in P.ink; log x when values span decades, ticks `<text fontSize="15" fill={P.muted}>` on P.rule gridlines.
- Bars: `<rect rx="8">` in P.star for the winner, P.sky for others, P.rule for a control; value in MONO bold beside the bar.
- Lines: `stroke={P.sky} strokeWidth="3"`, points `fill={P.card} stroke={P.sky} strokeWidth="3" r="7"`, a dashed fit in P.muted `strokeDasharray="7 6"`.
- One caption under the chart, 15px P.muted, ≤ 70 chars; a chart `viewBox="0 0 1136 300"` full width or `"0 0 560 330"` beside a text column. Inside SVG text never put a double-quoted font name in a double-quoted attribute; the font inherits.

RULES THAT KEEP IT LOOKING LIKE THIS
1. One idea per slide: a title, then one chart + one text column, or three tiles/cards + one panel. Seven slides for a talk: result · data · how it works · rounds/timeline · the finding · the limits · why it matters.
2. Words are scarce: title ≤ 12 words; a card ≤ 1 sentence; a bullet ≤ 12 words; no block over 40 words. Split the slide rather than shrink a font.
3. Gold is the signal, sky-blue the reference — never swap them mid-deck, never a third accent except the one loss colour. No pure black, no pure white.
4. Numbers come from the user's data or the workspace; an uncertain number is left out, not rounded up. Say what the data cannot prove on its own slide — a limits slide is part of this theme.
5. The Sky stays on every slide and the Constellation before every eyebrow. Nothing else twinkles; low key is the point.
6. Before add_slide, check the TSX: `function Component` present, tags balanced, brackets balanced, no vw/vh, nothing past 720px. `critique_slide` once, on the busiest slide only.