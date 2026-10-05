---
type: llm
weight: 1
---

# Criteria

Pass only if ALL of these hold:

1. The answer comes from the `research-study` skill (it loaded or quoted it), not forge-app-builder or training-monitor, and it does not propose building a new app.
2. It asks before creating anything, and its questions cover: the repository (link, branch, private?), the metric to improve and on which held-out evaluation, the constraints (design limits, metric floors, spend), a definition of success as a threshold on a named metric, and where the results should live (apps).
3. It asks about the machine: which GPU, and whether it is already connected (My Computer).
4. It says it will play the brief back for confirmation before starting, and that nothing that spends GPU or money happens without an explicit yes.
5. It asks in small groups or offers defaults. It does not dump twenty questions at once.

Fail if it calls a tool that creates or changes anything, invents a tool name, or promises results before any run.
