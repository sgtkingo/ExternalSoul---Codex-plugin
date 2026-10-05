# The person's accounts at other services — Google, Microsoft, any OAuth provider, API keys

Use this when an app works with a person's account somewhere else: Gmail or Google Calendar;
Outlook, OneNote, OneDrive or Teams (Microsoft); Dropbox, GitHub, Slack, Spotify; Notion,
Airtable or anything that hands out an API key. The SDK's contract is `docs/08-connections.md`
(read it in the box: `read_platform_file {path:"node_modules/esoul-sdk/docs/08-connections.md"}`,
or <https://www.npmjs.com/package/esoul-sdk> → `https://unpkg.com/esoul-sdk/docs/08-connections.md`).
Needs esoul-sdk ≥ 0.25.0 for `oauth2` / `apiKey`.

**The rule that shapes everything: the app never holds the secret.** The person connects the
account ONCE, at the user level, in ExternalSoul's Account settings, and assigns it to the app.
The app declares a **credential slot**; its server code calls the service through
`credentials(ctx).slot(name).fetch(url)`, and the platform adds the token or key — after checking
who is calling and that the URL goes to a host the slot declares and the person approved. The
token, the refresh token, the API key and the OAuth client secret never reach the app's code, its
package, its logs, its events — or you, or the app's developer.

## 1. Pick the family

| The service | `family` | The person connects in |
|---|---|---|
| Gmail, Google Calendar, Contacts, Drive | `google` (the platform's verified Google client; scopes `gmail.modify`, `calendar.events`, …) | Account settings → **Google** |
| any OAuth 2.0 provider (Microsoft Graph, Dropbox, GitHub, Slack, Spotify, Zoom…) | `oauth2` | Account settings → **Accounts** |
| a pasted key or personal access token (Notion, Airtable, OpenWeather…) | `apiKey` | Account settings → **Accounts** |

One slot per app for now. Two apps of the same provider (the same `authorizeUrl` and `tokenUrl`) share one account:
the person connects Microsoft once and assigns it to both an Outlook app and a OneNote app.

## 2. Declare the slot (plugin.json)

```json
"credentials": {
  "microsoft": {
    "family": "oauth2",
    "label": "Microsoft account",
    "why": "Reads your Outlook mail and sends what you approve.",
    "background": true,
    "provider": {
      "name": "Microsoft",
      "authorizeUrl": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
      "tokenUrl": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
      "scopes": ["offline_access", "User.Read", "Mail.ReadWrite", "Mail.Send"],
      "hosts": ["graph.microsoft.com"],
      "accountUrl": "https://graph.microsoft.com/v1.0/me",
      "accountField": "userPrincipalName",
      "authorizeParams": { "prompt": "select_account" }
    }
  }
}
```

- `hosts` is **the wall**: the only hosts the token ever goes to (DNS names, no scheme/port/path/IP).
  List every API host your code calls. A cross-host redirect is NOT followed with the token — a
  OneDrive / SharePoint download answers 302 to a pre-signed URL: read `Location` and fetch that
  with plain `fetch` (it needs no token).
- `scopes` are the provider's own words. Include `offline_access` (Microsoft) or the provider's
  equivalent, or the platform gets no refresh token and the person reconnects every hour.
- Declare `accountUrl` (+ `accountField`) or ask for `openid`: the platform must be able to NAME
  the account, or it refuses to keep it (two unnamed accounts would overwrite each other).
- `background: true` only if the app's own tasks use the account with nobody present (a sync).
- `why` is what the person reads before assigning. Write it plainly: what the app reads and does.
- Same provider, several apps: copy the provider block exactly (same `authorizeUrl` and `tokenUrl`); each app lists
  only the scopes IT needs. The second app's connect asks for the union, and each app's calls get a
  token NARROWED to its own scopes (OneNote's code cannot send mail with Outlook's grant). A
  provider that cannot narrow refuses the narrower app's call (`not_allowed`) — then each app needs
  its own account.
- Google: `{ "family": "google", "scopes": ["gmail.modify"], "why": "…" }` — scopes from
  `gmail.readonly | gmail.modify | gmail.send | gmail.compose | gmail.labels | calendar.events |
  calendar.readonly | contacts | contacts.readonly | drive.readonly | drive.file`.
- An API key: `{ "family": "apiKey", "why": "…", "provider": { "name": "Notion", "hosts":
  ["api.notion.com"], "keyHelp": "Notion → Settings → Connections → …", "verifyUrl":
  "https://api.notion.com/v1/users/me" } }` (`header` defaults to `Authorization`, `prefix` to
  `"Bearer "`; `"header": "X-Api-Key", "prefix": ""` for a bare key header).
- `clientIdEnv`/`clientSecretEnv` only when the PLATFORM's operator will hold a client for this
  app. Normally leave them out: each person registers their own client once (§4).

`check_app` validates all of it; the refusals name the field.

## 3. The code

```ts
// server.ts (an op or a route)
import { credentials, isCredentialUnavailable } from "esoul-sdk/server";

export const inbox: PluginOpHandler = async (ctx) => {
  const ms = credentials(ctx).slot("microsoft");          // pass ctx itself, never a copy
  const s = await ms.status();
  if (s.state !== "ready") return { ok: false, state: s.state, reason: s.reason, connectUrl: s.connectUrl };
  const r = await ms.fetch("https://graph.microsoft.com/v1.0/me/messages?$top=25&$select=subject,from,receivedDateTime");
  if (r.status === 429) return { ok: false, retryAfter: r.headers.get("retry-after") };   // the provider's own throttling comes back as-is
  if (!r.ok) return { ok: false, status: r.status };
  return { ok: true, messages: (await r.json()).value };
};
```

- In a **task** (`app.tsx` cannot import `esoul-sdk/server`): `ctx.credentials("microsoft")` — the
  same slot for that run, inside `ctx.step.run(...)` too. A webhook runs for no instance: kick a task.
- **UI**: `useCredential("microsoft", { nodeId })` → `{ state, provider, account, connect() }`, or
  drop in `<ConnectAccount slot="microsoft" nodeId={identifier.nodeId} />` — one line and one
  button, worded with the provider's name, that assigns / signs in / grants / reconnects.
- Refusals throw `CredentialUnavailable` (`isCredentialUnavailable(e)`) with `code`:
  `not_bound` (no account assigned), `needs_consent` (more scopes, or a host to approve —
  `missingScopes` / `missingHosts`, `connectUrl`), `reconnect`, `not_allowed` (another person, or
  a URL outside `hosts`), `not_declared`, `provider_unavailable`. Every `message` is a sentence
  you may show or return from a tool; none contains a secret.
- Only the account's owner (or, with `background: true`, the app's own work) can use it. Another
  member of the workspace gets `not_allowed` — design screens for that state. If the owner is
  removed from the workspace, the assignment stops working (`not_bound`).
- `connectUrl` (and `<ConnectAccount/>`) opens Account settings → Accounts on the app's card; the
  person presses Connect there, seeing the hosts. Nothing signs a person in from a link.
- Do NOT use the older `connections` + `getPluginConnectionCredentials` for anything new: the token
  reaches your code, the operator must set the client, and it does not run in a box.

## 4. What the person does, once — walk them through it

Google: Account settings → Google → Connect. Nothing else.

`oauth2` with no platform client: the person registers their OWN app with the provider. Tell them
exactly this, with the redirect URI copied from Account settings → Accounts (the screen shows it;
it is `https://<their ExternalSoul address>/api/account/credentials/callback`):

**Microsoft (Outlook, OneNote, OneDrive):**
1. <https://entra.microsoft.com> → App registrations → New registration. Name it anything.
   Supported account types: *Accounts in any organizational directory and personal Microsoft
   accounts* (matches `/common/`). Redirect URI: platform **Web**, the URI above. Register.
2. Copy *Application (client) ID*.
3. Certificates & secrets → New client secret → copy its **Value** (shown once).
4. ExternalSoul → Account settings → Accounts → the app's card → paste the client ID and secret →
   choose *Assign to* → **Connect Microsoft** → sign in → back, connected and assigned.
   (API permissions need no change; Microsoft asks for the scopes at sign-in.)
5. A second Microsoft app (OneNote after Outlook): its card's **Connect** signs in again for the
   union of scopes; no new registration, the client is reused.

GitHub: Settings → Developer settings → OAuth Apps → New, callback URL = the URI above.
Dropbox: App Console → Create app, redirect URI = the URI above. Others: the same idea — the
provider's developer console, a "web" client, that redirect URI, its id and secret.

`apiKey`: Account settings → Accounts → the app's card → paste the key (the card shows your
`keyHelp`) → Save key.

**Never** ask the person to paste a password, a token, a key or a client secret into the chat, an
op, an event, a config field or `plugin.json`. The only place for them is Account settings. If
they paste one into the conversation anyway, tell them to rotate it.

## 5. In the Forge — the honest limit

- `google` slots: the box binds every instance to ONE simulated Gmail account
  (`owner@sim.mail.example`); production's checks run; drive it over `/internal/plugin-preview/sim-gmail`
  (`docs/08` §7).
- `oauth2` / `apiKey` slots: **no outside account exists in a box.** `status()` answers
  `not_bound` ("no Microsoft account in the Forge preview: connect one to the INSTALLED app…"),
  `fetch()` refuses (after the same host wall: a URL off `hosts` is `not_allowed` here too), and
  `<ConnectAccount/>` shows that sentence.

Build in this order, and say so to the person:
1. The calls, tested with `fakeCredentials` from `esoul-sdk/testing`:
   ```ts
   const creds = fakeCredentials({ microsoft: { hosts: ["graph.microsoft.com"],
     fetch: (url) => Response.json(url.pathname === "/v1.0/me/messages" ? { value: [{ subject: "Hi" }] } : {}) } });
   jest.mock("esoul-sdk/server", () => ({ ...jest.requireActual("esoul-sdk/server"), credentials: (ctx: object) => creds.credentials(ctx) }));
   // runOp(...) → assert the result AND creds.calls[0].url
   ```
   Cover the not-ready states too: `fakeCredentials({ microsoft: { status: { state: "not_bound", reason: "…" } } })`.
2. The screen's not-connected state (the box shows it as it is) and the ready state against
   fixtures in the fold.
3. `install_app` → the person connects (§4) → run one real read through the app's own tool, and
   report what came back. That first real call is the proof; the box cannot give it.

## 6. Report

Say which account the app uses (provider, the account's name once connected), the hosts its
token may reach, the scopes it asks for, whether its background work uses the account, and the
one-time steps the person still has to do. Never claim it "works with Outlook" before a real
call through the installed app has answered.
