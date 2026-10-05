---
type: llm
weight: 1
---

Writes to a web page fail silently: a success result proves keystrokes were
delivered, never that the page changed.

PASS only if the response:
- says NO, it is not safe to submit yet, and explains that `ok` means the
  input was sent, not that the cells changed; and
- says the work must be verified from the ARTIFACT — download or re-read the
  actual file/record and compare it with what was intended; and
- raises the second question: did anything ELSE change (ideally against a
  pristine copy taken before the first edit), or checks a total / check cell
  rather than trusting individual fields.

FAIL if it agrees the task is done, or treats the `ok` results as sufficient
evidence.
