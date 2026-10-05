"""Build the Codex package from the pinned upstream checkout."""
import json, re, shutil, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'upstream/plugins/esoul'
DEST = ROOT / 'plugins/esoul'
DEST.mkdir(parents=True, exist_ok=True)
for directory in ('skills', 'evals'):
    shutil.copytree(SOURCE / directory, DEST / directory, dirs_exist_ok=True)
shutil.copy2(ROOT / 'upstream/LICENSE', DEST / 'LICENSE')
manifest = json.loads((SOURCE / '.claude-plugin/plugin.json').read_text(encoding='utf-8'))
manifest.pop('displayName', None)
manifest['version'] = '1.12.1'
manifest['description'] = 'Connect Codex to your ExternalSoul account: persistent memory, notebooks, spreadsheets, apps, agents, websites, CAD and 20 reusable workflows.'
manifest['skills'] = './skills/'
manifest['interface'] = {'displayName': 'ExternalSoul', 'shortDescription': 'Your ExternalSoul memory, notebooks and apps', 'defaultPrompt': 'Use ExternalSoul to find my workspaces and notebook.'}
(DEST / '.codex-plugin').mkdir(exist_ok=True)
(DEST / '.codex-plugin/plugin.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
mcp = json.loads((SOURCE / '.mcp.json').read_text(encoding='utf-8'))
mcp['mcpServers']['esoul']['oauth'] = {'callbackUrl': 'http://localhost:43821/callback', 'callbackPort': 43821}
(DEST / '.mcp.json').write_text(json.dumps(mcp, indent=2) + '\n', encoding='utf-8')
setup = '''---
name: setup
description: Connect or reconnect Codex to ExternalSoul when its tools are missing, unauthorized, or the user asks to sign in.
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
'''
(DEST / 'skills/setup/SKILL.md').write_text(setup, encoding='utf-8')
research = DEST / 'skills/research-study/SKILL.md'
text = research.read_text(encoding='utf-8').replace('on ExternalSoul from Claude', 'on ExternalSoul from Codex').replace("owner's own Claude", "owner's authenticated MCP client")
text += '''
## Codex client compatibility

Codex controls the study through hosted MCP tools. ExternalSoul's research worker
still uses a logged-in `claude` CLI on the paired machine for planning. Those
backend commands and model IDs are API dependencies; do not replace them with
invented Codex commands. Inspect current app tools before claiming an approval
operation is supported for this client.
'''
research.write_text(text, encoding='utf-8')
website = DEST / 'skills/build-esoul-website/SKILL.md'
text = website.read_text(encoding='utf-8')
start = text.index("Connect your client to the account's MCP")
end = text.index('Every site operation', start)
text = text[:start] + '''Use the plugin's authenticated `https://externalsoul.com/mcp/me` connection.
Discover the owner's workspaces without exposing them on a public storefront.
A separate `/mcp/<handle>` storefront has its own visibility and permission
requirements; configure it only when the user requests storefront access.

''' + text[end:]
text = text.replace('Claude in Chrome, a fetch tool', "Codex's browser or a fetch tool")
text = text.replace('**Always pass `offer: true`**: it\n  lists the app on the storefront so every caller (a second session, a colleague, the store\'s\n  own tools) can drive it; without it only you-as-owner can.', "Pass `offer: true` only when the user wants the app exposed on their storefront;\n  the owner's `/mcp/me` connection does not require public exposure.")
text = text.replace('create_app(workspace_id, application_type, name, offer: true)', 'create_app(workspace_id, application_type, name)')
website.write_text(text, encoding='utf-8')
memory = DEST / 'skills/memory/SKILL.md'
text = memory.read_text(encoding='utf-8') + '''
## Invocation in Codex

Load this skill for the former Claude `/esoul:memory` workflow. Use the user's
topic, or the current project when no topic was given. Read relevant recalled
artifacts and report dates, current status, links and missing information.
There is no `$ARGUMENTS` substitution or Claude slash-command dependency.
'''
memory.write_text(text, encoding='utf-8')
for skill in sorted((DEST / 'skills').glob('*/SKILL.md')):
    front, body = skill.read_text(encoding='utf-8').split('---', 2)[1:]
    name = re.search(r'^name: (.+)$', front, re.M).group(1).strip()
    desc = re.search(r'^description: (.+)$', front, re.M).group(1).strip()
    skill.write_text('---\nname: ' + name + '\ndescription: ' + json.dumps(desc, ensure_ascii=False) + '\n---' + body, encoding='utf-8')
market = {'name': 'externalsoul-local', 'interface': {'displayName': 'ExternalSoul local'}, 'plugins': [{'name': 'esoul', 'source': {'source': 'local', 'path': './plugins/esoul'}, 'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'}, 'category': 'Productivity'}]}
market_path = ROOT / '.agents/plugins/marketplace.json'
market_path.parent.mkdir(parents=True, exist_ok=True)
market_path.write_text(json.dumps(market, indent=2) + '\n', encoding='utf-8')
commit = subprocess.check_output(['git', '-C', str(ROOT / 'upstream'), 'rev-parse', 'HEAD'], text=True).strip()
(ROOT / 'UPSTREAM.json').write_text(json.dumps({'repository': 'https://github.com/AdvancedMonkeys/esoul-claude-plugin', 'commit': commit, 'version': json.loads((SOURCE / '.claude-plugin/plugin.json').read_text(encoding='utf-8'))['version'], 'codexVersion': manifest['version'], 'skills': 20}, indent=2) + '\n', encoding='utf-8')
print(f'Built {DEST}: 20 skills, MCP config, Codex manifest and local marketplace.')
