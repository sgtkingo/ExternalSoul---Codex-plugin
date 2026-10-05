---
type: llm
weight: 1
---

The plugin's `forge-app-builder` skill (`reference/computers.md`) documents the device arm.
Judge whether the answer shows that knowledge rather than a guess.

PASS only if the answer says ALL of:
- the app ships its own program for the computer: a `device.program` block in `plugin.json`
  with `device/main.ts` (setup steps, optional self-test, a local setting for the model folder),
  and the program starts the server itself and talks to it on localhost;
- the app reaches the program with `devices(ctx).program(linkId).send(topic, data)` answered by a
  handler (`p.on`), and the program reports back by calling the app's own ops (`p.op`) — nothing
  connects INTO the laptop (no tunnel, no open port), a `send` waits at most about 55 s (longer
  work answers "accepted" and reports later), and messages are small (≈1 MB);
- computers connect only to the INSTALLED app: in the Forge box `devices(ctx).list()` is empty
  and other calls refuse, so the program's logic is tested with a fake `p` and the app side with
  mocks, and the real run comes after install, when the person runs the one connect command
  (`esoul-device connect …`) on the laptop and approves the program (by digest, choosing what it
  may reach).

FAIL if it proposes exposing a port, a tunnel or the app calling `localhost` from the platform,
claims the laptop can be connected to the app inside the Forge preview, or answers only with the
older My Computer shell-command path without the app's own program.
