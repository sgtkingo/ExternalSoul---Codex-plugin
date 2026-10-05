---
type: llm
weight: 1
---

The plugin ships a `memory` skill. Facts live in ONE place, written with the
hosted `remember` tool; a correction is a new `remember` (optionally under the
`subject` recall returned for the old fact) and the old value is kept as
superseded history. `recall` returns the current version first.

PASS only if the response:
- uses `remember` to store the correction, as a self-contained sentence that
  names the new value (8,000 EUR) — ideally noting it replaces 6,000;
- optionally recalls first to find the existing fact's subject (a plus, not
  required);
- does NOT create a notes app (block_note_editor or otherwise) called
  "Memory" or similar, and does NOT append the fact to some page via
  `create_app` / `call_app_tool`;
- does NOT try to delete or overwrite the old fact.

FAIL if it stores the fact anywhere other than `remember`, names a tool that
does not exist on the hosted endpoint (`find_tools`, `run_tool`, `tool_help`,
any `memory_*` tool), or only promises to remember it within this chat.
