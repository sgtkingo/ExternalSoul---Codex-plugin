---
type: llm
weight: 1
---

The plugin's `forge-app-builder` skill documents what a Forge preview can and
cannot do. Judge whether the answer shows that knowledge rather than a
confident guess.

PASS only if the answer says ALL of:
- another app's tools (My Computer / `computer()`) are reached from the box
  only through the Forge board's OPEN tab — headless over MCP the call answers
  that no board is connected, so that arm is unit-tested with the machine mocked
  and driven for real with the preview open on the board or after install;
- a long job on the machine runs DETACHED and is POLLED (it is not one blocking
  command), and commands are approval-gated unless the OWNER sets Auto — a
  pending approval is a wait, not a failure, and the agent cannot set Auto;
- a durable task in the preview runs in-process and does NOT prove durability —
  surviving a closed tab / process death is only proven after install (the
  installed task runs on the platform's executor);
- the other arms (events, tools, ops, UI) CAN be proven in the preview with the
  board tools (calling the app's tools, reading its state, looking, driving).

FAIL if it claims the computer can be fully driven headless from the box,
proposes auto-approving commands, claims the preview proves durability, or
answers generically without naming what the preview cannot prove.
