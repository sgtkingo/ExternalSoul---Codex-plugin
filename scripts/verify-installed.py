"""Read Codex's registry and optionally list ExternalSoul workspaces, with no model turn."""
import argparse, json, queue, shutil, subprocess, threading, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--workspaces', action='store_true')
args = parser.parse_args()
process = subprocess.Popen([shutil.which('codex'), 'app-server', '--stdio'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding='utf-8', cwd=ROOT)
messages = queue.Queue()
def read_output():
    for line in process.stdout:
        try: messages.put(json.loads(line))
        except json.JSONDecodeError: pass
threading.Thread(target=read_output, daemon=True).start()
serial = 0
def send(message):
    process.stdin.write(json.dumps(message) + '\n')
    process.stdin.flush()
def request(method, params, timeout=45):
    global serial
    serial += 1
    expected = serial
    send({'id': expected, 'method': method, 'params': params})
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        message = messages.get(timeout=max(0.1, deadline-time.monotonic()))
        if message.get('id') == expected:
            if 'error' in message: raise RuntimeError(message['error'])
            return message.get('result')
        if 'id' in message and 'method' in message:
            send({'id': message['id'], 'error': {'code': -32601, 'message': 'Interactive requests are not supported by this read-only verifier.'}})
    raise TimeoutError(method)
try:
    request('initialize', {'clientInfo': {'name': 'externalsoul_connection_verifier', 'version': '1.0.0'}, 'capabilities': {'experimentalApi': True}})
    send({'method': 'initialized', 'params': {}})
    registry = request('skills/list', {'cwds': [str(ROOT)], 'forceReload': True})
    skills = [skill for row in registry['data'] for skill in row['skills'] if 'externalsoul-local' in str(skill.get('path', ''))]
    enabled = [skill for skill in skills if skill.get('enabled')]
    print(json.dumps({'installedSkills': len(skills), 'enabledSkills': len(enabled), 'names': [s['name'] for s in enabled]}, indent=2))
    if len(enabled) != 20:
        raise RuntimeError('Expected 20 enabled ExternalSoul skills.')
    if args.workspaces:
        thread = request('thread/start', {'cwd': str(ROOT), 'ephemeral': True})['thread']['id']
        status = request('mcpServerStatus/list', {'threadId': thread, 'detail': 'toolsAndAuthOnly'})
        esoul = next((server for server in status['data'] if server['name'] == 'esoul'), None)
        if not esoul: raise RuntimeError('ExternalSoul is not configured.')
        print(json.dumps({'server': 'esoul', 'authStatus': esoul.get('authStatus'), 'toolCount': len(esoul.get('tools', {}))}))
        tools = esoul.get('tools', {})
        tool = next((name for name, info in tools.items() if info.get('name', name) == 'list_workspaces' or name.endswith('__list_workspaces')), None)
        if not tool: raise RuntimeError('list_workspaces unavailable; complete OAuth and reload Codex.')
        result = request('mcpServer/tool/call', {'threadId': thread, 'server': 'esoul', 'tool': tools[tool].get('name', tool), 'arguments': {}}, timeout=45)
        if result.get('isError'): raise RuntimeError('ExternalSoul returned an error.')
        print(json.dumps(result, indent=2, ensure_ascii=False))
except (RuntimeError, TimeoutError, queue.Empty) as error:
    raise SystemExit(f'Connection check: {error}')
finally:
    process.terminate()
    try: process.wait(timeout=5)
    except subprocess.TimeoutExpired: process.kill()
