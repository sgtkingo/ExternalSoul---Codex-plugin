"""Validate the package and every bundled skill using the official skill validator."""
import json, os, re, runpy, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.validation'))
validator_path = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'skills/.system/skill-creator/scripts/quick_validate.py'
if not validator_path.is_file():
    raise SystemExit('Install the Codex skill-creator skill to use its validator.')
validate_skill = runpy.run_path(str(validator_path))['validate_skill']
plugin = ROOT / 'plugins/esoul'
manifest = json.loads((plugin / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
for key in ('skills', 'mcpServers'):
    relative = manifest[key]
    assert relative.startswith('./') and '..' not in Path(relative).parts
    assert (plugin / relative).exists(), relative
mcp = json.loads((plugin / manifest['mcpServers']).read_text(encoding='utf-8'))
assert mcp['mcpServers']['esoul']['url'] == 'https://externalsoul.com/mcp/me'
assert mcp['mcpServers']['esoul']['type'] == 'http'
assert mcp['mcpServers']['esoul']['oauth'] == {'callbackUrl': 'http://localhost:43821/callback', 'callbackPort': 43821}
market = json.loads((ROOT / '.agents/plugins/marketplace.json').read_text(encoding='utf-8'))
assert (ROOT / market['plugins'][0]['source']['path']).resolve() == plugin.resolve()
errors = []
for skill in sorted((plugin / 'skills').iterdir()):
    ok, message = validate_skill(skill)
    if not ok: errors.append(f'{skill.name}: {message}')
    for document in skill.rglob('*.md'):
        content = document.read_text(encoding='utf-8')
        content = re.sub(r'(?ms)^```[^\n]*\n.*?^```[^\n]*$', '', content)
        content = re.sub(r'`[^`\n]+`', '', content)
        for link in re.findall(r'\]\(([^\s)]+)', content):
            if '://' in link or link.startswith(('#', '/')) or '<' in link:
                continue
            target = link.split('#')[0]
            if target and not (document.parent / target).exists():
                errors.append(f'{document.relative_to(ROOT)}: missing {target}')
assert len(list((plugin / 'skills').glob('*/SKILL.md'))) == 20
if errors:
    raise SystemExit('\n'.join(errors))
print('PASS: 20 skills, local Markdown links, manifest paths, MCP URL and marketplace.')
