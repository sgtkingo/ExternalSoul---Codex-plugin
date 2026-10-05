# ExternalSoul for Codex

A Codex adaptation of [AdvancedMonkeys/esoul-claude-plugin](https://github.com/AdvancedMonkeys/esoul-claude-plugin), upstream version 1.12.0 (Codex adaptation 1.12.1), preserving all 20 skills and their resources. The exact upstream revision is in `UPSTREAM.json`. Upstream content remains MIT licensed.

## Install and connect

From PowerShell in this folder:

```powershell
./scripts/install.ps1 -Login
```

This registers the local marketplace, installs `esoul@externalsoul-local`, and starts browser OAuth. Sign in to ExternalSoul and approve its consent screen. Codex manages the credentials. Never paste a token into chat.

The plugin's server is `https://externalsoul.com/mcp/me`. Your [notebook](https://externalsoul.com/en/notebook) is the web interface to the same account, rather than the server URL. The connection discovers your existing projects, workspaces and apps.

Installed skills become available on a subsequent turn or after reloading Codex. Use the skills picker to find ExternalSoul. Start with `setup`, `memory`, or `block-notes`. If this chat still lacks tools, start a new chat. Verify the live connection by calling `list_workspaces`, then identify and read the existing notebook with the returned IDs.

```powershell
codex plugin list --marketplace externalsoul-local --json
codex mcp list
codex mcp login esoul
```

Installation and authentication are separate: an enabled plugin can still be awaiting sign-in. `codex mcp list` reports OAuth once signed in.

## Bundled skills

Memory, setup, block-notes, browser-use, slideshow, CAD, math-explainer-video, forge-app-builder, agent-builder, agent-recipes, email-campaign, research-study, training-monitor, website, website-story, website-look, website-films, website-media, website-publish and build-esoul-website.

The old `/esoul:memory` command is covered by the memory skill. Setup uses Codex OAuth commands. Website setup uses the authenticated account endpoint without requiring a public storefront. Research control works through MCP, but ExternalSoul's paired-machine research worker and `claude_task` API still depend on Claude Code; converting the client does not replace that backend. Helper scripts retain their own upstream dependencies.

## Rebuild and validate

Keep the pinned checkout in `upstream/`, then run:

```powershell
python scripts/adapt.py
python -m pip install --target .validation PyYAML
$env:PYTHONUTF8 = '1'
python scripts/validate.py
python scripts/verify-installed.py
```

The validation checks every skill with Codex's Skill Creator validator, relative Markdown references, manifest paths, the server endpoint, and marketplace resolution. Updating a package requires reinstalling it with `scripts/install.ps1`, then reloading Codex.

Packaging follows [OpenAI's plugin documentation](https://developers.openai.com/plugins/build/plugins); the `.codex-plugin/plugin.json` manifest declares `skills/` and `.mcp.json`. OAuth setup follows [OpenAI's MCP documentation](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).

To verify live account access after OAuth, run `python scripts/verify-installed.py --workspaces`. It uses Codex's app-server MCP transport to list workspaces without starting a model turn. This verification does not edit the notebook.

## OAuth callback compatibility

ExternalSoul currently rejects OAuth callbacks with the `127.0.0.1` host, including exact registered matches. The Codex package uses `http://localhost:43821/callback` and a listener on port `43821`; Codex appends its server-specific callback ID consistently for registration and authorization. Keep this port available during sign-in. Use the installed 1.12.1 package and a fresh `codex mcp login esoul`; previously generated links will not use this fix.
