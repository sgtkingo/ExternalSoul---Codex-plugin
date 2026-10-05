---
type: llm
weight: 1
---

The plugin ships a `memory` skill. Its hosted `recall` tool searches past work
sessions, remembered facts and all dated workspace content in ONE call, widens
vague time phrases itself, and returns each artifact's status today plus a
`link` that opens it.

PASS only if the response:
- makes `recall` the FIRST call, with the user's own words as `query` (about
  the ~500 dental leads spreadsheet) and the time phrase passed verbatim as
  `when` (e.g. "last spring") — NOT converted by hand into exact dates;
- does NOT start by listing every workspace or opening apps one by one to hunt
  for it;
- says it would open the actual data only after recall, with `read_app_entry`
  or `read_app_state` using the returned ids, and/or give the user the `link`;
- for the deleted case, says it would tell the user plainly that the sheet
  was deleted (or is in Recently deleted, restorable), rather than pretending
  it is there or recreating it silently.

FAIL if it names a tool that does not exist on the hosted endpoint
(`find_tools`, `run_tool`, `tool_help`, any `memory_*` tool), invents the
leads, or would answer without calling recall.
