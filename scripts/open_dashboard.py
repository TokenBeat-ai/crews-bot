#!/usr/bin/env python3
"""Serve the dashboard for an installation created by install_manager.py."""
import argparse, json, os, sys
from pathlib import Path

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path('~/crews-bot'))
    p.add_argument('--port', type=int, default=18761)
    a = p.parse_args()
    root = a.root.expanduser().resolve()
    state = json.loads((root / 'installation.json').read_text(encoding='utf-8'))
    workspace = root / 'workspace'
    serve = Path(state['current']) / 'dashboard' / 'serve.py'
    os.execv(sys.executable, [sys.executable, str(serve), '--port', str(a.port),
                              '--tasks', str(workspace / 'tasks.json'),
                              '--workflows', str(workspace / 'workflows.json'),
                              '--dashboard', str(workspace / 'dashboard.html')])
