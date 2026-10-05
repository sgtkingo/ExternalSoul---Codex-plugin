---
type: llm
weight: 1
---

The plugin's `forge-app-builder` skill (`reference/accounts.md`) documents user-level accounts
for any OAuth provider. Judge whether the answer shows that knowledge rather than a guess.

PASS only if the answer says ALL of:
- yes: each app declares a `credentials` slot with `family: "oauth2"` and a `provider` block
  (Microsoft's authorize/token endpoints, the scopes such as Mail.* / Notes.* with
  `offline_access`, and `hosts` such as `graph.microsoft.com`), and calls Microsoft through
  `credentials(ctx).slot(name).fetch(url)` — the platform adds the token, so the app's code never
  holds the token, refresh token or client secret, and the token goes only to the declared hosts;
- the friend connects ONCE in ExternalSoul's Account settings → Accounts, registering their own
  app with Microsoft (Entra / Azure app registration) whose redirect URI is the platform's
  `/api/account/credentials/callback` address shown on that screen, and enters its client id and
  secret THERE (sealed on the server) — not in chat, code, plugin.json or an event;
- one Microsoft account is assigned to BOTH apps (same provider block / token URL); the second
  app's extra scopes are granted by connecting again through the platform (asking for the union);
- in the Forge box no real Microsoft account exists (the slot answers `not_bound`), so the calls
  are tested with `fakeCredentials` from `esoul-sdk/testing`, and the real account only works after
  the app is installed.

FAIL if it says this is not possible, has the app read or store the token itself (e.g.
`getPluginConnectionCredentials`, a token in config or env), asks the friend to paste a password,
token or secret into the conversation, or claims a real Microsoft account works inside the
Forge preview.
