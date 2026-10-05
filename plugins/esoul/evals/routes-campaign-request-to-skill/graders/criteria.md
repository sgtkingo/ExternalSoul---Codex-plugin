---
type: llm
weight: 1
---

The plugin ships an `email-campaign` skill for exactly this request. You can only
see the final response, so judge whether its CONTENT shows the skill's procedure
rather than a generic guess. A plan written for a person need not name internal
tool calls.

PASS only if the plan includes ALL of:
- the campaign runs from the person's Gmail app INSIDE ExternalSoul (not a
  mail-merge script, not another mailing service);
- the person sees real sample letters (a preview) BEFORE anything is sent, and
  nothing goes out until they say go;
- the logo is uploaded to the workspace and travels IN the letter (not as a
  link to somewhere else);
- later questions — who replied, what they said — are answered by reading the
  campaign's replies/status, not by guessing.

FAIL if it proposes sending without a preview and an explicit go, sending from
another tool or service, or gives a generic plan with none of the specifics above.
