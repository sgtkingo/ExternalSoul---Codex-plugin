---
type: llm
weight: 1
---

The `forge-app-builder` skill prescribes a short interview (who uses it, what it
remembers, what must be true now, what runs unattended, what it touches outside)
and a shape decision (fold vs tables vs task vs route vs other apps). Judge the
CONTENT of the reply.

PASS only if the reply:
- asks (in one batch, not a drip) about WHO uses it — at least distinguishing
  the owner/staff from customers, and whether customers must sign in;
- puts orders, customers and stock in the app's OWN TABLES with rules/roles
  (not in the event fold), because they are per-person / must be true now /
  must not revert when the timeline is scrubbed;
- keeps the fold for the small shared things (settings, catalogue nudges, the
  shop's own state) — or explicitly says the fold is for what is shared and
  scrubbable;
- says the "tell me when an order comes in" is realtime addressed to the
  staff/owner role (or a task/notify), not a browser timer;
- mentions that the manifest is written first and lists what the owner will be
  asked to grant/declare (public ops for customers, sign-in requirement).

FAIL if it proposes storing orders in the event fold, hand-writes access checks,
starts writing code before the interview, or gives a generic app plan with no
ExternalSoul-specific shape.
