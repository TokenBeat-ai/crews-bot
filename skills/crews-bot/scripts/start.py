#!/usr/bin/env python3
"""Resolve a registered install and start/reuse its loopback dashboard (POSIX)."""
import argparse, fcntl, hashlib, json, re, socket, subprocess, sys, time
from pathlib import Path
from urllib.request import urlopen


def start(skill, root=None, port=None):
    config = json.loads((skill / 'installation.json').read_text())
    root = Path(root or config['root']).expanduser().resolve()
    state = json.loads((root / 'installation.json').read_text())
    current = Path(state['current']).resolve()
    if current.parent != root / 'releases':
        raise ValueError('Current release is outside this installation')
    router = current / 'general/router-method.md'
    if not router.is_file():
        raise ValueError('Missing coordinator method')
    workspace = root / 'workspace'
    identity = hashlib.sha256(str(workspace.resolve()).encode()).hexdigest()[:20]
    def matches(number):
        try:
            with urlopen(f'http://127.0.0.1:{number}/dashboard.html', timeout=1) as r:
                body = r.read().decode()
            data = json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>', body, re.S).group(1))
            return data.get('workspace_id') == identity
        except Exception:
            return False
    with (workspace / '.startup.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        runtime = workspace / 'dashboard-runtime.json'
        prior = json.loads(runtime.read_text()) if runtime.exists() else {}
        preferred = port or config.get('port', 18761)
        candidates = list(dict.fromkeys([prior.get('port', preferred), preferred] + list(range(preferred, min(preferred + 20, 65536)))))
        selected = next((n for n in candidates if matches(n)), None)
        reused = selected is not None
        if selected is None:
            for n in candidates:
                try:
                    with socket.socket() as probe: probe.bind(('127.0.0.1', n))
                except OSError:
                    continue
                with (workspace / 'dashboard-server.log').open('ab') as log:
                    proc = subprocess.Popen([sys.executable, str(current / 'scripts/open_dashboard.py'), '--root', str(root), '--port', str(n)], stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
                for _ in range(50):
                    if proc.poll() is not None: break
                    if matches(n): selected = n; break
                    time.sleep(.1)
                if selected is not None: break
                if proc.poll() is None:
                    proc.terminate(); proc.wait(timeout=5)
            if selected is None: raise RuntimeError('Dashboard failed to start; inspect dashboard-server.log')
        runtime.write_text(json.dumps({'port': selected}) + '\n')
    return {'root': str(root), 'router': str(router), 'getting_started': str(current / 'general/getting-started.md'), 'workflows': str(workspace / 'workflows.json'), 'tasks': str(workspace / 'tasks.json'), 'local_entry': config.get('local_entry') if str(root) == config['root'] else None, 'url': f'http://127.0.0.1:{selected}/dashboard.html', 'reused': reused}

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--root'); p.add_argument('--port', type=int); a = p.parse_args()
    if a.port is not None and not 1 <= a.port <= 65516: p.error('port must be between 1 and 65516')
    print(json.dumps(start(Path(__file__).resolve().parents[1], a.root, a.port), ensure_ascii=False, indent=2))
