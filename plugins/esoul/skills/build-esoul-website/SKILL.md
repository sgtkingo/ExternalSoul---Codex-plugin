---
name: build-esoul-website
description: "Build a great-looking public website (a homepage, a business site, or a store with ordering) in an ExternalSoul workspace using ONLY the esoul MCP and the site app's own tools — from brief to published domain, with a critique loop instead of eyes. Use when asked to \"make a website / homepage / store on esoul\", \"rebuild a given URL on esoul\", or to add pages, products or a form to an existing site app."
---

# Build a website on esoul with the site app tools

> **Part of the website skills.** Start at `website` (the sequence and the path). Before building:
> `website-story` (the copy), `website-look` (palette, fonts, image style), `website-films` (real
> films, recorded on this machine), `website-media` (getting images and films onto the site).
> After: `website-publish` (checks on every screen, SEO text, domain). This file is the BLOCK
> MANUAL for the Site-app path — its tools, vocabulary, palettes and rhythm.

You have the esoul MCP and this file. The site app is a real website builder that is also an
app: pages are blocks (Puck data), the owner edits every text inline afterwards, agents and the
owner use the SAME tools. Everything below was learned building three real sites: a florist's
homepage, a restaurant store (Karma Kitchen, live on its own domain, orders end to end) and a
café pitch site built cold from this file — its author's feedback is folded in.

## 0. Setup (once) and tools (the hosted MCP)

Use the plugin's authenticated `https://externalsoul.com/mcp/me` connection.
Discover the owner's workspaces without exposing them on a public storefront.
A separate `/mcp/<handle>` storefront has its own visibility and permission
requirements; configure it only when the user requests storefront access.

Every site operation is `call_app_tool(workspace_id, app_id, tool_name, arguments)`; the site's
tool names carry the app's name as a suffix (`replace_page_Karma_Kitchen`) — always read them
from `get_app_tools` first, never guess the suffix. Below, `<site>` stands for that suffix.

- **Discover**: `describe_profile`, `list_workspaces` (workspaces + their app ids/types),
  `read_app_state(workspace_id, app_id)`, `search_workspace`, `list_app_entries`, `read_app_entry`.
- **Tools of an app**: `get_app_tools(workspace_id, app_id, names_only: true)` FIRST on any app
  with more than ~10 tools (a site has 45; the full listing truncates in most clients and the
  second half — critique, screenshot, booking, connect_form, add_product — is the half you need),
  then `get_app_tools(…, tools: ["critique_page_X", "set_up_booking_X"])` for the exact schemas
  of the ones you will call. §7.0 quotes the six you always need.
- **Create**: `create_app(workspace_id, application_type, name)` (owner only) — types
  `"site" | "spreadsheet" | "calendar" | "cloud_browser"`. Pass `offer: true` only when the user wants the app exposed on their storefront;
  the owner's `/mcp/me` connection does not require public exposure. **Names are identities for
  creation**: `create_app` is idempotent on (type, name) — a second `"Menu"` returns the SAME
  app, and a source's `instanceName` must match exactly one app — so name every sheet
  distinctly (`Menu`, `Objednávky`, `Poptávky`), never two sheets with one name.
- **Site tools** (via `call_app_tool`): `read_site_<site>` (outline with block ids AND a
  `Publication:` block — read it before and after publishing; `vocabulary: true` lists every
  block's props — read it once), `replace_page_<site>` (whole page in one call — how you BUILD),
  `insert_block_ / set_block_props_ / set_blocks_ / move_block_ / remove_block_ /
  duplicate_block_ / find_blocks_` (how you EDIT), `add_page_ / set_page_ / delete_page_`,
  `set_theme_`, `set_business_`, `set_sources_`, `define_fields_`, `apply_data_ops_`,
  `connect_form_`, `set_up_booking_`, `design_block_`, `set_publish_mode_`, `read_site_stats_`,
  `undo_last_edit_`, `add_product_ / update_product_ / browse_menu_ / find_dishes_` (stores),
  `screenshot_page_` (the PNG comes back as a file; `view_image` it) and `critique_page_`
  (a vision judge: pass/score/issues — run it even when you looked yourself).
- **Sheets** (via `call_app_tool` on a spreadsheet app): `add_sheet_` (a tab), `insert_markdown_table_`
  (a whole tab in one call — header row + rows), `add_column_ / add_rows_ / set_cell_ /
  rename_sheet_ / read_sheet_` — read `get_app_tools` for the exact names.
- **Files**: `upload_file(workspace_id, name, …)` with EITHER `content_base64 + mime_type` (small
  files you author: an SVG, a text file, a tiny PNG — add `sha256` of the decoded bytes) OR
  `source_url` (a public https URL the server fetches — photos and anything over ~20 KB; base64
  emitted by a model drifts silently above that and the hash check rightly refuses it);
  `list_files(workspace_id)`; `view_image(url)` to look at a file or a rendered screenshot.
- **Publish**: `publish_homepage(workspace_id, front_app_id, app_ids?, publish_mode: "site")` (owner
  only) — the account's homepage and its linked custom domain now show this site. **Last step.**
- **Reference study**: if your client can browse (Codex's browser or a fetch tool), use it; otherwise
  `create_app(…, "cloud_browser", …, offer: true)` once and drive it through its own tools (`goto`,
  `screenshot`, `read`, `extract`) via `call_app_tool`.

Never edit platform code. Every write is an event the owner can scrub; `undo_last_edit_<site>`
reverts your last batch.

## 1. The sequence (in this order, no skipping)

1. **Brief in one breath**: who it is for, what a visitor must be able to DO (order, book, write,
   read), the tone, the place, the language of the audience (Czech site → Czech copy, Czech
   labels, `Kč`). One accent, one font pair, one background. Commit before touching a block.
2. **Study the reference if there is one.** Screenshots at desktop (1440) AND phone (390); read
   the palette (accent, surface, text), the type (serif/sans, weight, case), the geometry
   (full-bleed hero or boxed; header floating over the hero or above it; section rhythm), what
   the phone composition is (it is usually DIFFERENT from desktop — a menu list, tiles, a sticky
   bar). Write those down as numbers before building. Match geometry, not pixels.
3. **Theme**: `set_theme_<site>` with `{accent, background, foreground, font, radius, density}` —
   pick a row from the palette table in §3 unless the brand dictates otherwise. Font pairs:
   `editorial` (Fraunces+Inter — crafts, food, warm), `serif` (Playfair+Lora — classic,
   hospitality), `sans` (clean product), `display` (bold brand), `familjen` (the restaurant
   store: Familjen Grotesk, dark), `grotesk` (tech), `mono` (dev). `frame` (a colour around the
   page) exists — leave it `""`; it reads as a solid band. Never leave the default blue on a
   warm subject.
4. **Business record**: `set_business_<site>` with `{name, type, telephone, email, street, city,
   postalCode, country, openingHours:["Mo-Th 10:00-21:30", …], sameAs:[…]}` — JSON-LD on every
   page and the tab title. Never invent a phone number or address — ask.
5. **Images, then pages.** Photos: `upload_file` with `source_url` (the reference site's own
   photos while the owner supplies theirs; hero ≤ 1920 px wide, JPEG/WebP 200–300 KB — a 1 MB
   PNG hero is the difference between "fast" and "taking forever"); or the owner uploads through
   the workspace UI and you `list_files`. No photos at all? Use the **no-photo recipe** (§3): a
   typographic hero and one SVG illustration per section, authored as text and uploaded as
   `image/svg+xml` — the image props accept `.svg` by file name and they look excellent.
   Reference images in blocks by FILE NAME (`{"url": "hero-1.jpg"}`) or by the URL the upload
   returns. Product photos live in folders `Menu/<category>/<dish>/`.
6. **Data before pages, for a store**: §4 — sources → tabs → products, in that order, or
   `add_product_` refuses.
7. **Build each page with ONE `replace_page_<site>`** (content = `[{type, props:{id?, …, body:[…]}}]`;
   slots are `body` on Section, `col1..col4` on Columns, `row` on List). Home first, then the
   rest. Give blocks stable ids (`hero`, `about`) so later edits can address them. Default
   section rhythm: §3.
8. **Look, then critique**: `screenshot_page_<site>` `{page, viewport:"phone"}` and `view_image`
   it; then `critique_page_<site>` with `{page, viewport: "phone", intent}` then `"desktop"` for
   EVERY page. Fix every issue it names, re-run until it passes with score ≥ 0.85. If the
   critique is unavailable (it is a paid model call on the owner's AI credit — "positive credit
   balance required" means the OWNER must top up, nothing you did), its reply hands you the
   manual checklist; apply it yourself against the screenshots (§8).
9. **Set the mode**: `set_publish_mode_<site>` with `{mode: "site"}` for a public site (server-
   rendered, fast, hidden data sources still resolve); `"frame"` only when the point is the
   workspace itself.
10. **Publish — the LAST action.** `publish_homepage(workspace_id, front_app_id: <site>,
    app_ids: [<site>], publish_mode: "site")` as the owner (or the owner's Explorer menu). Sheets
    the site reads stay hidden. **Pages, blocks, theme and sheet rows are read per request — an
    edit after publishing is live at once, no republish. What publishing FREEZES is the set of
    public apps and which is in front: an app you `create_app` AFTER publishing (a calendar for
    a booking page, a second site) is not public until you call `publish_homepage` again with
    it in `app_ids`.** `read_site_<site>`'s `Publication:` block tells you exactly this: not
    published / live since when / which hidden apps it reads (fine in site mode) / which apps
    were added after the publish and need a republish / whether visitors land on this site.
11. **Verify like a visitor**: `publish_homepage` answers with `visitor_view` — the mode, every page's address,
    title and image count, and every block a visitor would find empty (an image not found, a Booking with no
    free times or a calendar visitors cannot read). `check_live_site` answers the same at any time. Fix every
    problem it names. Then fetch the public URL with your browser or the cloud browser app,
    check the phone layout, the menu/products count, a form submission or an order if the site
    takes them. A green tool result is not a verification; the public page is.

## 2. Block vocabulary (props you will actually set)

Layout: `Section{tone:plain|tint|accent|dark, width:narrow|normal|wide|full, padding:sm|md|lg,
background:{url,overlay,position}, showOn:all|phone|desktop, bleed:bool, body:[…]}` ·
`Columns{count:2|3|4, gap, col1..col4}` · `Spacer{size}` · `Divider`.
Content: `Hero{eyebrow,title,subtitle,align,primary:{label,href},secondary,image:{url,alt},tone,
background,height:auto|tall|screen}` · `Heading{text,level:1-4,align}` · `RichText{body:html,
align,size}` · `Quote{text,attribution}` · `Card{title,body,image,link}` · `Stats{items:[{value,
label}]}` · `Button{label,href,variant:primary|secondary|link,align,actions,visitorEnabled}` ·
`Footer{text,links:[{label,href}]}` · `LinkList{title,items:[{label,sub,href,icon:clock|calendar|
map|chat|info}]}` (big tappable rows — phone menus, links).
Media: `Image{image,caption,width,rounded}` · `Gallery{images:[{url,alt,caption,detail}],columns:2|3|4,fit:square|portrait|natural}` (a portfolio: `fit:"natural"` keeps each work's shape, caption = title, detail = medium · size · price) ·
`Svg{svg,width,maxHeight,align,color}` (an inline mark; one style per site) · `Embed{url:
YouTube|Vimeo|google.com/maps?q=…}` · `Carousel{images,height:sm|md|lg|screen,scrollHint,
showArrows,showDots,showCount}`.
Store: `Header{logo,title,subtitle,links,showCart,cartHref,showAccount,accountHref,langLabel,
currency,overlay:bool,menuLabel}` (overlay floats it over a screen-height Carousel; on phones the
links fold into a drawer. `overlay` changes only the bar's own styling, never the drawer's
markup: both modes render the same panel, so a drawer bug is never an `overlay` misconfiguration) · `InfoBar{address,mapHref,phone,cta}` · `Hours{title,lines:[{day,hours,
weekday}]}` (**weekday 1 = Monday … 7 = Sunday**; the visitor's day is highlighted) ·
`ModeTiles{modes:[{id:here|pickup|delivery,label,hours,icon}],layout:tiles|bar,links}` ·
`Catalog{categories:[{source,title,emoji,tag,limit}],layout:auto|grid|list,chips,placeholder:{url},
variant:cards|showcase,cardDetails:auto|compact|full,addLabel,currency}` · `CartBar{checkoutHref,
modes}` · `Checkout{deliver:"order",modes,submitLabel,signInText,thanksText,menuHref}` · `Orders{}` ·
`Account{}`.
Data: `Input{label,bind:"visitor.<key>",kind}` · `Select{label,bind,options}` (**options: one per
line, `Label|value`**) · `Toggle` · `List{source,where,sortBy,limit,columns,row:[…]}` ·
`Booking{source,deliver,slotMinutes,daysAhead}` (placed by `set_up_booking_`, never by hand).
A custom look: `design_block_<site>` with `{name, html, css}` registers your own sanitised
HTML+CSS block type; use it for a hero illustration or a signature section, never for layout the
vocabulary already has.

## 3. Design rules, with numbers

**Tested palettes** (surface / foreground / accent; WCAG contrast ratios, all AA or better):

| Mood | background | foreground | accent | fg/bg | accent/bg | text ON accent |
|---|---|---|---|---|---|---|
| Dark warm (restaurant, bar) | `#111111` | `#f8f8f8` | `#e8912d` | 17.8 | 7.7 | dark `#111111` (7.7) |
| Editorial cream (café, crafts, food) | `#faf6ef` | `#1f1a17` | `#b5432a` | 16.0 | 5.1 | white (5.5) |
| Clean product | `#ffffff` | `#14161a` | `#1f5eff` | 18.1 | 5.1 | white (5.1) |
| Forest (garden, wellness) | `#f3f6f1` | `#17211a` | `#2f6b3f` | 15.2 | 5.8 | white (6.4) |
| Ink & brass (studio, law, wine) | `#0f1115` | `#ece7dc` | `#c9a24d` | 15.3 | 7.9 | dark `#111111` (7.9) |
| Slate blue (services, tech) | `#f5f7fa` | `#111827` | `#1e40af` | 16.5 | 8.1 | white (8.7) |

Buttons and prices use the accent; body text never does. A light accent (orange, brass) takes
DARK text on the button; a deep accent takes white. Check any text on a photo has
`background.overlay` 0.4–0.6.

**Heading lengths that survive 390 px** (rule of thumb from the three sites, at the default
type scale): eyebrow ≤ 24 characters; level-1 title ≤ 30 characters (two lines); level-2 section
heading ≤ 44 characters; hero subtitle ≤ 120 characters; a Card title ≤ 28; a button label ≤ 18.
Longer → the critique reports "heading wraps to three lines"; cut words, do not shrink type.

**Default section rhythm** (the composition that produced the pages we were proud of — start
here, deviate for a reason):

1. `Section{tone:plain, padding:sm}` — a utility bar (Header, or logo + one phone link)
2. `Hero{height:tall}` — one statement, one eyebrow, one primary action (+ one secondary)
3. `Section{tone:tint, padding:md}` — `Stats` or three short proof points
4. `Section{tone:plain, padding:lg}` — the offer: `Columns{3}` of `Card`
5. `Section{tone:dark, padding:lg, width:narrow}` — the story: `Heading` + `RichText` (+ `Quote`)
6. `Section{tone:plain, padding:sm}` — utility: `Hours` / `InfoBar` / a form
7. `Section{tone:tint, padding:md}` — footer: `Columns{3}` (address · hours · map) + `Footer`

Never two `lg` plain-text sections in a row — alternate tone (`tint`, a photo `background`,
`dark`). `padding:lg` for story sections, `md` for lists, `sm` for utility bars.

**Hierarchy over decoration**: one hero statement, one eyebrow, one action. Level 2 for sections,
uppercase only where the brand does it (a menu's category titles). **Phone first**: a
screen-height Carousel with an overlay Header; title + address as text under it; `ModeTiles` +
`LinkList` for the phone home (`showOn:"phone"`), an `InfoBar` for desktop (`showOn:"desktop"`).
One page carries both compositions. **Copy**: real sentences in the brief's voice, no lorem, no
"[bracketed]" leftovers, the audience's language throughout including button labels and empty
states.

**The no-photo recipe** (a pitch site rarely has client photography): a typographic `Hero`
(`tone:tint`, no image, a long eyebrow and a short title), one SVG illustration per section
authored as text — flat shapes, two colours (the accent and the foreground at 20 % opacity),
`viewBox="0 0 640 400"`, no text inside the SVG — uploaded once as `image/svg+xml` with a
`sha256`, referenced by file name in `Card.image` / `Image` / `Section.background`; one palette
row from the table; the `Svg` block for a small mark in the header. It reads as designed, not
as "awaiting photos".

## 4. A store in particular — the order is sources → tabs → products

Data = ONE spreadsheet with a TAB per category. **`add_product_` refuses until the site has a
`products` source for the category AND the sheet has that tab**, so:

1. `create_app(ws, "spreadsheet", "Menu", offer: true)` and `create_app(ws, "spreadsheet",
   "Objednávky", offer: true)` (orders; stays hidden from visitors).
2. `set_sources_<site>` with one entry per category: `[{key:"predkrmy", appType:"spreadsheet",
   instanceName:"Menu", view:"products", path:"Předkrmy"}, …]` (`path` = the tab title, exactly).
3. Tabs: `add_sheet_Menu {name:"Předkrmy"}` per category (rename the default first tab with
   `rename_sheet_Menu {sheetId, name}`), then ONE `insert_markdown_table_Menu {sheetId, markdown}` per tab with the
   header row `Název | Popis | Cena | Obrázek | Dostupné | Alergeny | Volby | Štítky | Pořadí`
   and the dishes as rows — three calls per category instead of one per dish. English headers
   work too (name, description, price, image, available, allergens, options, tags, order).
   Gotchas: a `|` inside `Volby` must be escaped as `\|` in the markdown; `Alergeny` is a
   comma-separated list in a cell (the `add_product_` argument is an ARRAY); `Dostupné` empty
   means available, `ne` hides the dish; `Obrázek` = file name or `Menu/<cat>/<dish>/<file>`.
4. Later dishes: `add_product_<site>` `{category, name, price, description, allergens:[…],
   options, tags, photos:[file names or ids]}` / `update_product_<site>` — never hand-edit cells
   when an agent does it. `browse_menu_` / `find_dishes_` are the proof that the wiring works.

Options syntax in `Volby`: `Kde to sním?*: Sním to tady | S sebou (Box) +15 ; Přílohy: Rýže +69`
(`*` required, `+` multiple, `+N` surcharge). Orders: `connect_form_<site>` with
`{key:"order", kind:"order", target:"Objednávky", catalog:[source keys], requireLogin:true,
notify:{email:true}, reply:{toField:"email", subject:"Objednávka {{orderId}}", body:"…{{items}}…{{total}}…"}}`.
Pages: Home (Header overlay, Carousel screen, phone/desktop bands, showcase, about, gallery,
footer with Hours + map Embed + CartBar), Menu (Header, ModeTiles bar, Catalog cards with chips,
CartBar), Košík (Checkout + Orders), Účet (Account), Rezervace, Oblasti doručení.

## 5. What "delivers" means without a mailbox

`connect_form_` / `set_up_booking_` always land the ROW (a sheet row, a calendar request, an
order) — that part needs nothing. `notify:{email:true}` and `reply:{…}` send MAIL, and mail needs
a mailbox in the workspace: a connected Google account or a provisioned address bound to an
email app. Without one the tool result says so (`notifications … won't send`) and the form
still works; say it to the owner up front: "the enquiry lands in the sheet; to be emailed,
connect Google in the workspace or ask for a mailbox". Do not promise "you'll get an email"
until the tool result stops warning.

## 6. Mistakes already made once — do not repeat

- `create_app` without `offer: true`; two sheets with the same name; a source whose
  `instanceName` is ambiguous.
- `add_product_` before the sources and tabs exist (it refuses — read §4's order).
- Publishing mid-build to "check the menu", then forgetting that apps created afterwards are
  not public. Check with a screenshot and `browse_menu_` instead; publish LAST; after any
  `create_app` post-publish, `publish_homepage` again. Read `read_site_`'s `Publication:` block.
- A `frame` colour around the page; a Header AND the reader's nav (the reader nav yields to a
  Header now, but do not add two navigations yourself).
- Publishing in `frame` mode for a public store: the frame resolves sources on the client and
  cannot see hidden sheets → empty categories; and it is slow. Use `site` mode.
- Hero PNGs of 1 MB, or a photo carried as model-emitted base64 (corrupt above ~20 KB — the
  hash check refuses it; use `source_url`).
- A type-only source (`{appType:"gmail"}`) hoping to reach a hidden app — sources that must read
  a hidden app NAME it (`instanceName`).
- Reading a screenshot with empty catalog headers as "the sheet is broken". Since 2026-09-07
  `screenshot_page_` and `critique_page_` resolve sources on the server exactly like the public
  page; an empty Catalog in a screenshot now means the source/tab wiring IS wrong — check
  `browse_menu_` and `set_sources_` (`path` = tab title). The EDITOR preview (`preview:true` on
  an edit) is the owner's browser and only shows dishes for sheets loaded in that workspace —
  do not judge data from it.
- Trusting a green tool result instead of the public URL. Fetch the page; count the dishes.

## 7. Worked examples (copy the shapes, not the words)

### 7.0 The six schemas you always need (arguments of `call_app_tool`)

```
screenshot_page_<site>  {page?: id|slug (default: selected), viewport?: "phone"|"tablet"|"desktop"}
                        → {fileId, fileName, url} — view_image(url)
critique_page_<site>    {page?, viewport?, intent?: "a café pitch site read on a phone"}
                        → PASS/NEEDS WORK, score, issues[], suggestions[] — or the manual checklist when the judge is unavailable
set_sources_<site>      {sources: [{key, appType:"spreadsheet"|"calendar"|…, instanceName, view?: "products"|"free", path?: "<tab title>"}]}  (≤12; replaces the whole list)
connect_form_<site>     {key, kind: "spreadsheet_row"|"order"|"calendar_request"|"todo_item"|"note_line", target: "<app name or id>",
                         mapping?: {visitorKey: "Column"}, catalog?: [sourceKeys] (order), requireLogin?: bool (order),
                         notify?: {email: true}, reply?: {toField: "email", subject, body: "text with {{key}} tokens"}}
set_up_booking_<site>   {calendar: "<name or id>", page?, afterItemId?, key?: "booking", slotMinutes?: 15|30|45|60|90|120,
                         daysAhead?: 7|14|30, title?, hint?, askMessage?: bool, timezone?: "Europe/Prague", locale?: "cs-CZ",
                         notify?: {email: true}, reply?: {toField: "email", subject, body}}
add_product_<site>      {category: "<tab title>", name, price: number, description?, allergens?: string[], options?: "<Volby syntax>",
                         tags?: string[], available?: bool, photos?: [file names | file ids | URLs], order?: number}
set_theme_<site>        {accent?, background?, foreground?: hex, font?: editorial|serif|sans|display|familjen|grotesk|mono,
                         radius?: none|sm|md|lg|pill, density?: compact|comfortable|airy, frame?: hex | ""}
```

### 7.1 A business home page in one `replace_page_<site>` (`arguments: {page: "home", content: [...]}`)

```json
[
  {"type": "Hero", "props": {"id": "hero", "eyebrow": "Květinářství · Vinohrady", "title": "Kytice, které vydrží déle než oslava.",
    "subtitle": "Sezónní květiny z okolí Prahy, vázané ráno, doručené odpoledne.", "align": "left",
    "primary": {"label": "Objednat kytici", "href": "/objednavka"}, "secondary": {"label": "Svatby", "href": "/svatby"},
    "image": {"url": "hero.jpg", "alt": "Pivoňky v dílně"}, "tone": "tint", "height": "tall"}},
  {"type": "Section", "props": {"id": "proof", "tone": "tint", "width": "normal", "padding": "md", "body": [
    {"type": "Stats", "props": {"items": [{"value": "12 let", "label": "vázání kytic"}, {"value": "do 3 h", "label": "doručení po Praze"}, {"value": "4,9 ★", "label": "z 312 hodnocení"}]}}
  ]}},
  {"type": "Section", "props": {"id": "offer", "tone": "plain", "width": "wide", "padding": "lg", "body": [
    {"type": "Columns", "props": {"count": 3, "gap": "lg",
      "col1": [{"type": "Card", "props": {"title": "Kytice na přání", "body": "Řekněte nám příležitost a rozpočet.", "image": {"url": "kytice.jpg", "alt": ""}, "link": {"label": "Objednat", "href": "/objednavka"}}}],
      "col2": [{"type": "Card", "props": {"title": "Svatby", "body": "Od kytice nevěsty po výzdobu stolů.", "image": {"url": "svatba.jpg", "alt": ""}, "link": {"label": "Svatební nabídka", "href": "/svatby"}}}],
      "col3": [{"type": "Card", "props": {"title": "Předplatné", "body": "Každý pátek čerstvá kytice do kanceláře.", "image": {"url": "predplatne.jpg", "alt": ""}, "link": {"label": "Jak to funguje", "href": "/predplatne"}}}],
      "col4": []}}
  ]}},
  {"type": "Section", "props": {"id": "story", "tone": "dark", "width": "narrow", "padding": "lg", "body": [
    {"type": "Heading", "props": {"text": "Malá dílna, velké kytice", "level": 2, "align": "center"}},
    {"type": "RichText", "props": {"body": "<p>Jsme dvě sestry a jedna dodávka. …</p>", "align": "center", "size": "lg"}}
  ]}},
  {"type": "Section", "props": {"id": "book", "tone": "plain", "width": "normal", "padding": "sm", "body": [
    {"type": "Heading", "props": {"id": "book-title", "text": "Domluvte si konzultaci", "level": 2, "align": "center"}}
  ]}},
  {"type": "Section", "props": {"id": "foot", "tone": "tint", "width": "wide", "padding": "md", "body": [
    {"type": "Columns", "props": {"count": 3, "gap": "lg",
      "col1": [{"type": "RichText", "props": {"body": "<strong>Kde nás najdete</strong><br/>Korunní 12, Praha 2"}}],
      "col2": [{"type": "Hours", "props": {"title": "Otevírací doba", "lines": [{"day": "Po–Pá", "hours": "9:00–18:00", "weekday": 1}, {"day": "So", "hours": "9:00–13:00", "weekday": 6}, {"day": "Ne", "hours": "zavřeno", "weekday": 7}]}}],
      "col3": [{"type": "Embed", "props": {"url": "https://www.google.com/maps?q=Korunn%C3%AD+12+Praha", "title": "Mapa", "aspect": "4/3"}}], "col4": []}},
    {"type": "Footer", "props": {"text": "© 2026 Sestry Květ", "links": [{"label": "Instagram", "href": "https://instagram.com/…"}]}}
  ]}}
]
```

Bookings are ONE call, after the page exists: `set_up_booking_<site>` with `{"calendar":
"Rezervace", "page": "home", "afterItemId": "book-title", "slotMinutes": 30, "daysAhead": 21,
"title": "Vyberte čas", "askMessage": true, "locale": "cs-CZ"}` — it declares the calendar
source and the `booking` delivery AND inserts the Booking block; do not hand-place a Booking
block. The calendar app must exist (`create_app(ws, "calendar", "Rezervace", offer: true)`) and
have availability windows — the owner sets them in the calendar; with none, the block shows no
slots, which is not a page bug.

### 7.2 A form that lands in a sheet, with the owner notified and the visitor answered

1. Sheet: `create_app(workspace_id, "spreadsheet", "Poptávky", offer: true)`.
2. Delivery: `connect_form_<site>` with `{key:"enquiry", kind:"spreadsheet_row", target:"Poptávky",
   mapping:{"name":"Jméno","email":"E-mail","message":"Zpráva"}, notify:{email:true},
   reply:{"toField":"email","subject":"Díky, {{name}}","body":"Ozveme se do 24 hodin. {{site}}"}}`
   — missing columns are created; on a fresh sheet the empty A/B/C columns are renamed. Read the
   result: a mailbox warning means the row lands but no mail goes out (§5).
3. Blocks on the page: `Input{label:"Jméno", bind:"visitor.name"}`, `Input{label:"E-mail",
   bind:"visitor.email"}`, `Select{label:"Zájem", bind:"visitor.topic", options:"Svatba|wedding\nPředplatné|subscription"}`,
   `Input{label:"Zpráva", bind:"visitor.message", kind:"multiline"}`,
   `Button{label:"Odeslat", actions:[{"op":"deliver","to":"enquiry"}], visitorEnabled:true}`.
4. Verify: open the public page in a browser, submit once, read the sheet
   (`read_app_state` on the spreadsheet) — the row is the proof, not the tool's "ok". Delete the test row.

### 7.3 The store menu page

```json
[
  {"type": "Header", "props": {"id": "hdr", "logo": {"url": "logo.png", "alt": ""}, "title": "Karma Kitchen - Objednej!", "subtitle": "Restaurace · Ostrava",
    "links": [{"label": "Hlavní stránka", "href": "/"}, {"label": "Menu", "href": "/menu"}, {"label": "Rezervace", "href": "/rezervace"}],
    "showCart": true, "cartHref": "/kosik", "showAccount": true, "accountHref": "/ucet", "langLabel": "cz", "currency": "Kč", "overlay": false}},
  {"type": "Section", "props": {"tone": "plain", "width": "wide", "padding": "sm", "bleed": true, "body": [
    {"type": "ModeTiles", "props": {"layout": "bar", "links": [{"label": "Menu", "href": "/menu"}],
      "modes": [{"id": "here", "label": "Zde", "hours": "11:00 - 22:00", "icon": "here"}, {"id": "pickup", "label": "Vyzvednutí", "hours": "11:00 - 22:00", "icon": "pickup"}, {"id": "delivery", "label": "Rozvoz", "hours": "11:00 - 22:00", "icon": "delivery"}]}}]}},
  {"type": "Section", "props": {"tone": "plain", "width": "wide", "padding": "sm", "body": [
    {"type": "Catalog", "props": {"layout": "auto", "chips": true, "variant": "cards", "cardDetails": "auto", "placeholder": {"url": "logo.png"}, "addLabel": "Přidat", "currency": "Kč",
      "categories": [{"source": "predkrmy", "title": "Předkrmy", "emoji": "🍽️", "tag": "", "limit": 0}, {"source": "kureci", "title": "Kuřecí chody", "emoji": "🍗", "tag": "", "limit": 0}]}}]}},
  {"type": "CartBar", "props": {"checkoutHref": "/kosik", "label": "Košík", "continueLabel": "Pokračovat k objednávce", "currency": "Kč",
    "modes": [{"id": "here", "label": "Zde", "hours": ""}, {"id": "pickup", "label": "Vyzvednutí", "hours": ""}, {"id": "delivery", "label": "Rozvoz", "hours": ""}]}}
]
```

The home's "Doporučujeme" is the same Catalog with `"variant":"showcase"`, `"layout":"grid"`,
`"chips":false` and every category carrying `"tag":"doporučujeme","limit":3`. The phone home
adds, inside a `Section{showOn:"phone"}`: `Heading` (name) + `RichText` (address), then
`ModeTiles{layout:"tiles"}`, `LinkList{title:"Digitální menu", items:[{label:"Menu", href:"/menu"}]}`,
`LinkList{title:"Odkazy:", items:[{label:"Rezervace",href:"/rezervace",icon:"calendar"},…]}`;
the desktop home keeps an `InfoBar` inside `Section{showOn:"desktop"}`.

### 7.4 A signature section as a designed block

`design_block_<site>` with `{"name": "Ribbon", "label": "Ribbon", "html": "<section class=\"rb\"><span data-prop=\"text\">Denní menu 11–14 h</span></section>", "css": ".rb{background:var(--site-accent);color:var(--site-on-accent);padding:24px;text-align:center;font-weight:700;letter-spacing:.08em;text-transform:uppercase}"})`
— `data-prop="text"` makes that element's text an editable prop, `data-prop-image="photo"` on an
`<img>` a picker, `data-prop-href="cta"` on an `<a>` a link; `defaultProps` overrides the values
read from the template. Then insert `{"type": "Ribbon", "props": {"text": "…"}}` like any block.
Scripts, iframes and external `url()` are stripped; use the theme variables (`--site-accent`,
`--site-bg`, `--site-fg`, `--site-muted`, `--site-line`, `--site-font-heading`) so the block
follows a later `set_theme_<site>`.

## 8. The critique loop, precisely

`critique_page_<site>` with `{page, viewport, intent}` renders the page headlessly WITH its data
(sheet rows, bookings) and returns `{pass, score, issues[], suggestions[], summary}`. Run it per
page and per viewport (`phone` first — most visitors — then `desktop`); pass `intent` ("a
restaurant menu people order from on the phone") so the judge knows what good means. Treat every
issue as a defect: fix with `set_block_props_<site>` / `set_blocks_<site>` (several edits in one
call), re-run, stop at `pass` with `score ≥ 0.85` or after four rounds — then say what still
fails instead of looping. Typical verdicts and their fixes: "text unreadable over the photo" →
raise `background.overlay`; "too much empty space" → `padding:"md"` or merge sections; "hero has
no call to action" → `primary`; "looks generic" → a `design_block` mark, real photos, the
brand's own words in the eyebrow.

**When the judge is unavailable** ("positive credit balance required" = the owner's AI credit,
a rate limit, or Chromium down), the tool reply carries this manual checklist — apply it to the
`screenshot_page_` PNGs yourself and say in your summary that the critique was manual:
- text over a photo has `background.overlay` ≥ 0.4, or sits on a plain tone;
- no heading wraps to a third line at 390 px (§3's lengths);
- one accent, one font pair; level 2 for sections, one level 1 per page;
- the phone composition differs from desktop where the reference's does;
- every link and button resolves; every image resolves; alt texts set;
- section rhythm alternates tone; the audience's language everywhere.

## 9. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `add_product_` refuses | no `products` source for that category, or the tab does not exist | §4 order: `set_sources_` (path = tab title) → `add_sheet_` → then products |
| Empty categories on the public site | the site's source names a tab that does not exist, or the source is type-only | `set_sources_<site>` with `path` = the tab title and `instanceName` = the sheet; read the sheet's tab names first |
| Empty categories in a screenshot / critique | same wiring problem (screenshots resolve sources server-side since 2026-09-07) | as above; confirm with `browse_menu_` |
| Empty categories inside the workspace frame only | frame mode resolves sources on the client | `set_publish_mode site` for the public site |
| A page you built after publishing is empty for visitors | the block reads an app created after the publish (a calendar, a second sheet) that is not public | `publish_homepage` again with it in `app_ids`; `read_site_` → `Publication:` names it |
| `upload_file` refuses "sha256 mismatch" | model-emitted base64 drifted (anything over ~20 KB) | `source_url`, an SVG authored as text, or the owner uploads in the UI |
| `critique_page_` "positive credit balance required" | the OWNER's AI credit is empty | tell the owner; use the manual checklist (§8) meanwhile |
| `get_app_tools` result is cut off | 45 schemas exceed the client's result size | `names_only: true`, then `tools: [names]` |
| A tool result says ok but the page did not change | you edited the wrong page (`page` defaults to the SELECTED page) | pass `page` explicitly (id or slug) |
| `create_app` "returned" an existing app | (type, name) already exists — creation is idempotent on the name | pick a distinct name |
| Booking page shows no slots | the calendar has no availability windows | the owner sets availability in the calendar app; not a page bug |
| `connect_form_` warns about notifications | no mailbox in the workspace | §5 — the row still lands; connect Google or provision an address for mail |
| Page "takes forever" | 1 MB PNG hero, or frame mode | re-encode photos ≤ 300 KB; site mode |
| Photo not showing | name mismatch or file not in the workspace | `list_files`; reference the exact file name or the blob URL |
| Two headers | a Header block plus an automatic nav | keep the Header; the reader nav yields to it |
| A dish never appears | `Dostupné` = `ne`, or the row is in the wrong tab | `update_product` / check the tab |
| Order refused "unknown product" | the dish is sold out or in a category the order's `catalog` does not list | `find_dishes` first; check `Dostupné` and the `catalog` keys |
| `publish_homepage` refused | you are not the storefront's owner, or the workspace is not exposed | sign in as the owner; expose the workspace; or the owner's Explorer menu |
| `get_app_tools` lists 0 tools ("withheld") | you are a visitor, not the owner, and the app's tools are opt-in | ask the owner for "All on" on that app (or `storefront_all_tools` in their chat) |

## 10. Checklist before you say "done"

- [ ] `critique_page_<site>` passes on every page, phone and desktop (or the manual checklist was applied and you said so); you looked at `screenshot_page_<site>` yourself
- [ ] business record set; tab title shows the business, not "Site"
- [ ] every link resolves (no `#`, no `/todo`); every photo resolves; alt texts set
- [ ] the audience's language everywhere, including button labels and empty states
- [ ] forms deliver a row (tested, then the test row removed); a store takes one test order; the owner knows whether mail goes out (§5)
- [ ] **`publish_homepage` was the LAST call**: nothing was created after it, or it was called again afterwards — `read_site_`'s `Publication:` block shows nothing "added after the publish"
- [ ] published in `site` mode; only the site app visible; sheets hidden
- [ ] the public URL fetched and read once more as a stranger would
