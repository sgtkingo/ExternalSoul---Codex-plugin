Use when the user asks what slideshow THEMES exist ("what slideshow themes do you have", "show me the deck styles"), asks to THEME or RESTYLE an existing deck ("apply the floral theme", "make my slides look like the paper one"), or asks for a deck in a named theme ("open the slideshow app and make floral themed slides about X"). This is the index and the procedure; each theme's tokens, scaffold and recipes live in its own skill — read the theme file the one you use, then copy from it. Small model, no taste required: each theme skill is a paste-and-fill contract. Two are built: floral-paper (light) and starry-night (dark).

THE THEMES
- floral-paper — warm ivory paper, cream cards, brown-black ink, teal + amber data colours, a low-key line-drawn sprig by the eyebrow and a faint flower cluster in the corner. The default for talks and demos. `reference/floral-paper.md`.
- starry-night — deep indigo night with a faint starfield and a small constellation by the eyebrow; gold for the signal, sky-blue for the reference; indigo cards. The dark theme for talks, results and "the limits" slides. `reference/starry-night.md`.
- ink — the floral-paper components on a plain deep navy ground (described at the end of the floral-paper skill). Use only when asked for a plain dark look.

LIST — "what themes do you have?"
Answer in prose with the list above: name, one line of look, when it fits. Offer: "say `use floral-paper` and name the deck, or ask me to make a new one". Do not read the theme skill for a listing; it is long.

APPLY — restyle an existing deck
1. Find the slideshow app (list the workspace's apps if the user did not name it) and read its state: every slide has `id`, `name`, `tsxSource`.
2. `reference/<name>.md`.
3. For each slide, in order: keep its WORDS and NUMBERS (title, bullets, figures, chart data), drop its old styling, and rewrite the whole source in the theme scaffold using the recipes. Then `replace_slide_source_<base>` with the new TSX. Never `apply_slide_edits` for a restyle — the scaffold changes every line.
4. A slide whose content does not fit the theme's word budget is split into two (`add_slide_<base>` after it, then `reorder_slides_<base>` with the full ordered id list).
5. `select_slide_<base>` the first slide and tell the user what changed: "7 slides restyled, 1 split".

CREATE — a new themed deck about X
1. If no slideshow app is open or the user says "open the slideshow app": add one with `add_app` (applicationType "slideshow", a real name like "Roadmap — Q4"). Its sample slide is replaced by the first `add_slide`.
2. Read the theme's recipe file (`reference/<name>.md`). Plan 5–7 slides on paper first: one idea each — a result/title slide with 2–3 tiles, a how-it-works rail, one or two chart slides, a why-it-matters card row, a closing panel. Every number must come from the user, the workspace, or a tool result; ask for what is missing rather than inventing.
3. `add_slide_<base>` per slide with `name` (2–3 words) and the TSX. Validate before each call: `function Component` present, tags balanced, no `vw`/`vh`, nothing past 720px.
4. `critique_slide_<base>` once, on the busiest slide; fix what it names with `replace_slide_source_<base>`.
5. `select_slide_<base>` the first one. Report the slide names in one line.

CHARTS FROM DATA
If the user attaches or names data (a spreadsheet, numbers in chat, a research graph), put the numbers into inline SVG per the theme's chart recipe; label every axis with its unit; one caption line. A chart with a number you cannot source is not a chart, it is a drawing — leave it out.

WHAT GOES WRONG
- Text wraps or spills: you exceeded the word budget. Shorten, or split the slide. Never shrink fonts below the recipe sizes.
- The preview shows a compile error: an unclosed tag or a double-quoted string inside a double-quoted attribute. Fix the source; the runtime is the final word.
- The deck came out generic: you wrote your own styles. Everything visual comes from the theme skill's tokens and recipes.