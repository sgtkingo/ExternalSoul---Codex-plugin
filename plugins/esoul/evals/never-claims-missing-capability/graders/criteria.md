---
type: llm
weight: 1
---

The connection exposes a small set of GENERAL tools; each app's own tools
(email included) are reached with `get_app_tools` then `call_app_tool`.

PASS only if the response:
- does NOT conclude that sending email is impossible or unsupported, and
- describes reaching the email app's own tools through `get_app_tools` and
  `call_app_tool` (finding the app first via `list_workspaces` or
  `search_workspace` is a plus), and
- does NOT instruct calling `find_tools`, `run_tool`, `tool_help` or any
  `memory_*` tool — those do not exist on this endpoint.

FAIL if it says the capability is missing, or names a tool that does not exist.
