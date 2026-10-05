# Design rules — what "native" and "responsive" mean on ExternalSoul

The platform has a style guide with hard-won invariants. These are the ones an app you build in
the workbench must satisfy; `look_at_app` (desktop light, desktop dark, phone light) is how you
check them. Start with the palette — most "doesn't feel native" comes down to it.

## The non-negotiables

1. **The root fills its frame**: `width:100%; height:100%; overflow:hidden`, a flex column. The
   frame handles size and maximize; never fight it, never scroll the whole app.
2. **Chrome rows `flexShrink:0`; content `flex:1; minHeight:0`** with its own scroll container.
3. **A per-app palette object** — `LIGHT` and `DARK`, same keys — chosen by the `.dark` class on
   `<html>`. **Light = warm sepia** (`#faf6f0` / `#efe7d8` / `#e8dfd0` surfaces, brown text).
   **Dark = translucent data surfaces over the frame's gradient**; neutral greys with R≈G≈B.
4. **In dark mode, editors, dialogs, popovers and sticky headers are OPAQUE.** Translucent
   floating UI is unreadable over the gradient; translucent sticky headers leak scrolled content.
5. **Popovers and menus portal to `document.body`** with a solid backing and close on
   scroll/resize — the `overflow:hidden` root and the frame's CSS transform clip an absolute child.
6. **Touch is a first-class input.** Tap to act — never double-tap-to-edit; `touch-action:
   manipulation`; bigger hit targets on `(pointer: coarse)`; drags set `touch-action: none` only
   while dragging.
7. **Custom clickables are real buttons**: `role="button"`, `tabIndex={0}`, Enter AND Space,
   `aria-label` on icon-only controls. Status is never colour-only.
8. **Distinct icons for distinct actions** — two identical glyphs collapse to ambiguity when
   labels hide on a phone. Icons come from lucide-react.
9. **Empty state present and actionable** — a fresh app says what to do first, in the app's own
   voice, not "No data".
10. **Keyboard where it makes sense**: arrows / Enter / Escape / Delete on grids, lists, editors.
11. **A click shows its result at once, and a failure is named, not hidden.** State the person
    changes is an event — the dispatch is the optimistic update. A server op is wrapped in
    `runOptimistic({ key, what, apply, revert, send })`: the screen changes this frame; if the
    request fails it goes back, and the platform's one banner (bottom-centre pill: a dot, "*Cheer*
    failed — no connection", Try again, ×) says so. Name `what` in the person's words; a refusal
    shows its reason without Try again. Drive it: take the network away in `drive_app` and look.

## Responsive, concretely

- Design for 390 px wide first, then let it breathe. The phone shot from `look_at_app` must show
  no horizontal page scroll, no clipped controls, readable text.
- Measure the VISIBLE scroller (a `ref` on the scroll container, `clientWidth`) for layout
  decisions such as column counts — never a large inner canvas. Re-measure on resize
  (`ResizeObserver` or a window `resize` listener).
- Toolbars `flex-wrap: wrap`; labels collapse to icons on narrow widths; overflow goes into one
  menu, not off the edge.
- A canvas larger than the viewport lives INSIDE the scroll container and is sized to what it
  holds (`minWidth:100%`, `minHeight:100%`), so an empty app shows no scrollbars.
- Long text wraps (`whiteSpace: pre-wrap; wordBreak: break-word`). Fixed heights only for chrome.
- Virtualize past a few hundred rows; re-measure on the touch row-height flip.

## The app's character

The platform is made "as artists": craft over speed, specifics over generics. An app should have
a voice — a sticky-notes wall is linen and paper with a gummed strip and a lifted corner, not a
grid of yellow rectangles. Shadows come in two (contact + ambient). Nothing twitches between
renders: derive any randomness from stable ids, never from `Math.random()` in render. Motion is
brief and purposeful; respect reduced-motion.

## Events, time, agents — the philosophy the UI must honour

- **Events are the truth.** What the workspace remembers goes through `dispatch`; what is honestly
  device-local (a drag in flight, text mid-typing) stays local and lands as ONE event when done.
- **Time is structural.** The user can scrub the timeline; the app must render any prefix of its
  events sensibly. Never store derived data that the fold cannot recompute.
- **Agents are first-class.** Whatever a person can do in the UI, an agent can do through a tool
  emitting the same event — and the UI reflects an agent's event exactly as it reflects a tap.
- **Read-only viewers exist** (public shares, invited readers). Gate every write on
  `useAppCanEdit()`; never hide data behind an edit affordance.
- **Apps store knowledge.** `getStateDescription` is how agents perceive the app — write it as a
  compact, truthful brief with ids, never a dump, never a claim about what did not load.

## Pre-install checklist (run it yourself before `install_app`)

- [ ] Root fills the frame, flex column, `overflow:hidden`; chrome `flexShrink:0`; content
      `flex:1 minHeight:0` with its own scroll.
- [ ] `LIGHT`/`DARK` palette, `.dark` observed at runtime; looked at in BOTH themes.
- [ ] Dark-mode editors/dialogs/popovers/sticky headers opaque; popovers portaled.
- [ ] Phone shot clean: no page-level horizontal scroll, controls reachable, text readable.
- [ ] Tap-to-act, `touch-action`, bumped targets; real buttons with `aria-label`; distinct icons.
- [ ] Empty state actionable; keyboard where relevant.
- [ ] Every UI action has a tool twin (`execute` + `onClient`); tools documented for a model.
- [ ] Ids/timestamps minted in `dataCreator`; processors pure, idempotent, bounded, refusing
      bad payloads; bursts collapsed.
- [ ] `getStateDescription` uses `incompleteStateNotice`; `reconstructStateFromEventLog: true`.
- [ ] Tests cover the fold contract; `check_app` green (no `skipped`).
- [ ] `plugin.json` lists every op and every cross-app grant, and nothing more.
