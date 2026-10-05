---
type: llm
weight: 1
---

The plugin ships a `cad` skill for exactly this request. You can only see the
final response, so judge whether its CONTENT shows the skill's workflow rather
than a generic CAD plan.

PASS only if the plan includes ALL of:
- the enclosure comes into an ExternalSoul CAD app from a workspace file (an
  import of the STEP; exported from Onshape through the person's cloud browser
  if it is not a file yet);
- the enclosure's holes are READ from the kernel (a describe of the part) before
  the lid is designed to them — not guessed from a picture or assumed;
- the lid is its own body; the person's enclosure is never cut, fused or edited;
- the fit is MEASURED (distance / interference between the parts) before it is
  called fitting;
- the lid is exported by name as an STL for printing.

FAIL if it proposes modelling in another tool, editing the person's part,
checking the fit by eye or by a boolean, or gives a generic plan with none of
the specifics above.
