---
type: llm
weight: 1
---

The plugin ships a `build-esoul-website` skill for exactly this request. You
can only see the final response, so judge whether its CONTENT shows the skill's
procedure rather than a generic guess. A plan written for a person need not
name internal tool calls.

PASS only if the plan includes ALL of:
- the site is built INSIDE ExternalSoul with its site app (not hand-written
  HTML files, and not deployed to some other host);
- a review pass that LOOKS at the result — a screenshot and/or a critique —
  before publishing;
- publishing is the LAST step;
- it asks for, or says it will not invent, real business facts (name, address,
  phone, prices) rather than making them up.

FAIL if it proposes writing HTML locally, deploying elsewhere, inventing the
business's details, or gives a generic plan with none of the specifics above.
