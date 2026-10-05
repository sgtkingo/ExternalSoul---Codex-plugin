---
name: setup
description: "Connect or reconnect Codex to ExternalSoul when its tools are missing, unauthorized, or the user asks to sign in."
---

# Connect ExternalSoul in Codex

The account MCP endpoint is `https://externalsoul.com/mcp/me`. The notebook at
`https://externalsoul.com/en/notebook` is the web interface, not the MCP URL.
Authenticate through ExternalSoul's OAuth sign-in; never ask for a token in chat.

1. Inspect `codex mcp list` and the installed ExternalSoul plugin before adding
   another server. The plugin bundles an `esoul` HTTP server.
2. With a standalone registration, run `codex mcp login esoul`. If no server is
   registered, run `codex mcp add esoul --url https://externalsoul.com/mcp/me`,
   then log in. With only the bundled connection, authenticate through Codex's
   MCP settings, or use the installed server name shown by Codex.
3. Have the user sign in and approve ExternalSoul's browser consent screen.
   The connection reaches the projects and workspaces on that account.
   Codex manages OAuth credentials and refresh. Do not promise a particular
   credential storage backend.
4. Verify `list_workspaces` after login. Open the relevant notebook using the
   returned workspace and app IDs; do not create one just to test connectivity.
5. If this conversation still lacks tools, reload Codex or start a new chat
   after installation. Installed files do not prove tools are live.

If OAuth reports a redirect mismatch, confirm the installed plugin uses
`http://localhost:43821/callback` and callback port `43821`. ExternalSoul rejects
127.0.0.1 loopback redirects even when they match the registration. Keep the
callback URL and listener port together.

For unauthorized calls, reauthenticate. For insufficient scope, reconnect with
OAuth and inspect the consent. An empty workspace list may mean the account has
no projects. Never claim sign-in succeeded without checking it.

## Find capabilities

ExternalSoul exposes general tools. Find apps with `list_workspaces` or
`search_workspace`, inspect schemas with `get_app_tools` (names only first for
large apps), then execute the relevant `call_app_tool`. Use returned IDs and tool
names. Create a workspace or app only when the user's task calls for it.
