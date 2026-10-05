---
type: llm
weight: 1
---

Connecting is an OAuth sign-in: run `/mcp`, pick the ExternalSoul server,
authenticate in the browser. There is no token to paste.

PASS only if the response:
- directs the user to `/mcp` and a browser sign-in, and
- explicitly does NOT ask the user to paste, share or create an access token
  or API key, and says none is needed.

FAIL if it asks for a token or key, tells the user to set an environment
variable, or tells them to install Python, pip, uv or a local server.
