---
type: llm
weight: 1
---

The `forge-app-builder` skill has a "test tools" pattern: temporary probe
tools/ops with a `__test` prefix, owner-gated at the seam, used from the
workbench's tool-calling to set up state, and REMOVED before shipping, with a
search for the prefix and a re-run of the checks proving they are gone; the
assertions survive in the unit tests.

PASS only if the answer:
- proposes temporary, clearly-named test tools/ops (a `__test`-style prefix or
  equivalent unmistakable marker) that the workbench calls to seed and wipe;
- gates them at the seam too (owner/internal only), not just by obscurity;
- REMOVES them before shipping and verifies the removal (a search for the
  marker across the app's files, then re-running the checks);
- keeps the seed/wipe assertions in the app's tests (e.g. calling the ops
  directly in unit tests) rather than in the shipped doors.

FAIL if it ships the seed/wipe tools behind a flag or "admin only" without
removal, relies on obscurity, or suggests testing only after install.
