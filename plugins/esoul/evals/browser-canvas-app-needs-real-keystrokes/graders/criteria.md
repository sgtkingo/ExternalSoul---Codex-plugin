---
type: llm
weight: 1
---

Excel for the web paints its grid on a canvas: it only reacts to real typing,
so setting a field's value does nothing, and clicking into the grid is
unreliable. The correct route is keyboard-driven.

Judge the procedure the response RECOMMENDS. A response that mentions a bad
approach in order to warn against it ("no selector anywhere", "put_text does
nothing here") is following the rule, not breaking it.

PASS only if the recommended procedure has ALL four:
1. writes with real keystrokes — `browser_type` and/or `browser_press_key` —
   and does not recommend `browser_put_text` or a script that sets a value;
2. selects the cell by REFERENCE through the keyboard (the Go To dialog via
   `ControlOrMeta+G`, or the Name Box), not by clicking into the grid;
3. clears the reference field before typing into it (`clear: true` or an
   explicit select-all/clear), because the field remembers its last value;
4. verifies by downloading or re-reading the workbook and comparing, not by
   trusting the success result.

FAIL if the RECOMMENDED path uses put_text or value-setting, clicks cells as the
primary method, skips clearing, or treats a success result as proof.
