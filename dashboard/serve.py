#!/usr/bin/env python3
"""Serve only the dashboard and design on loopback; no directory listing."""
import argparse
import json
import re
import os, hashlib, secrets, tempfile
from datetime import datetime, timezone
from render_dashboard import render
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

D = Path(__file__).resolve().parent

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        origin = 'http://' + self.headers.get('Host', '')
        expected = 'http://127.0.0.1:' + str(self.server.server_port)
        if origin != expected or self.headers.get('Origin') != expected or self.headers.get('X-Dashboard-Token') != self.server.token:
            self.send_error(403); return
        if self.path not in {'/refresh', '/task-action'} or not self.server.tasks_path or not self.server.workflows_path:
            self.send_error(400, 'Explicit tasks and workflows configuration required'); return
        lock = self.server.tasks_path.with_suffix('.dashboard.lock')
        acquired = False
        try:
            length = int(self.headers.get('Content-Length','0'))
            if length > 10000: raise ValueError('Request too large')
            body = json.loads(self.rfile.read(length) or '{}')
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.close(fd); acquired = True
            source = self.server.tasks_path
            raw = source.read_bytes(); data = json.loads(raw)
            if self.path == '/task-action':
                if body.get('revision') != hashlib.sha256(raw).hexdigest(): raise ValueError('Task records changed. Refresh the dashboard first.')
                matches = [t for t in data['tasks'] if t['id'] == body.get('id')]
                if len(matches) != 1: raise ValueError('Task not uniquely found')
                task = matches[0]; action = body.get('action')
                now = datetime.now(timezone.utc).isoformat()
                if action == 'remove':
                    data['tasks'] = [t for t in data['tasks'] if t['id'] != task['id']]
                else:
                    raise ValueError('Your agent verifies and records completion. The dashboard only supports removing tasks from view.')
                data['updated_at'] = now
            with tempfile.TemporaryDirectory(dir=source.parent) as temp:
                staged = Path(temp)/'tasks.json'; staged.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
                page = Path(temp)/'dashboard.html'
                render(staged if self.path=='/task-action' else source,self.server.workflows_path,page, workspace_path=source.parent)
                if source.read_bytes() != raw: raise ValueError('Another writer changed the task. Refresh and try again.')
                if self.path=='/task-action':
                    source.with_suffix('.dashboard-backup.json').write_bytes(raw)
                    os.replace(staged,source)
                os.replace(page,self.server.dashboard_path)
            self.server.dashboard_path.with_suffix('.error.json').unlink(missing_ok=True)
            self.send_response(200); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(b'{"ok":true}')
        except Exception as e:
            self.send_response(409); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(json.dumps({'error':str(e)},ensure_ascii=False).encode())
        finally:
            if acquired: lock.unlink(missing_ok=True)

    def do_GET(self):
        route = urlsplit(self.path).path
        if route == '/artifact':
            try:
                content = self.server.dashboard_path.read_text()
                data = json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>', content, re.S).group(1))
                task_id = parse_qs(urlsplit(self.path).query).get('id', [''])[0]
                task = next(t for t in data['tasks'] if t['id'] == task_id)
                path = Path(task['artifact'])
                if not path.is_absolute(): path = self.server.dashboard_path.parent / path
                if path.suffix.lower() not in {'.md', '.txt'}: raise ValueError('unsupported preview')
                payload = path.read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.end_headers()
                self.wfile.write(payload)
            except Exception:
                self.send_error(404, 'Artifact not available for text preview')
            return
        if route == '/snapshot-status':
            try:
                page = self.server.dashboard_path
                error_file = page.with_suffix('.error.json')
                error = json.loads(error_file.read_text())['error'] if error_file.exists() else None
                content = page.read_text()
                data = json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>', content, re.S).group(1))
                payload = json.dumps({'revision': data['snapshot_revision'], 'error': error}).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                self.wfile.write(payload)
            except Exception:
                self.send_error(503, 'Snapshot unavailable')
            return
        if route not in {'/', '/dashboard.html', '/design'}:
            self.send_error(404)
            return
        path = D / 'guide.md' if route == '/design' else self.server.dashboard_path
        if not path.is_file():
            self.send_error(503, 'Run render_dashboard.py first')
            return
        content = path.read_bytes()
        if route != '/design':
            content = content.replace(b'__ACTION_TOKEN__', self.server.token.encode())
        self.send_response(200)
        self.send_header('Content-Type', ('text/plain' if route == '/design' else 'text/html') + '; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=18761)
    parser.add_argument('--dashboard', type=Path, default=D / 'dashboard.html')
    parser.add_argument('--tasks', type=Path)
    parser.add_argument('--workflows', type=Path)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    server.token = secrets.token_urlsafe(32)
    server.tasks_path = args.tasks.resolve() if args.tasks else None
    server.workflows_path = args.workflows.resolve() if args.workflows else None
    server.dashboard_path = args.dashboard.resolve()
    if server.tasks_path and server.workflows_path and not server.dashboard_path.is_file():
        render(server.tasks_path, server.workflows_path, server.dashboard_path)
    print(f'Open http://127.0.0.1:{args.port}/dashboard.html', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
