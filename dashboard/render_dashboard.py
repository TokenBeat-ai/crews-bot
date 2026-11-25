#!/usr/bin/env python3
"""Build a read-only local snapshot using only explicitly configured files."""
import argparse
import json
import re
import os
import hashlib
import tempfile
from datetime import datetime, timezone
from pathlib import Path

D = Path(__file__).resolve().parent

def main_status(task):
    status = task['status']
    if status == 'running': return 'running'
    if status in {'done', 'cancelled', 'unknown'}: return status
    if status == 'waiting' and task.get('started_at') is None and task.get('has_started') is False: return 'not_started'
    return 'pending'

DEFAULT_IDS = {'001'}

def load_workflows(config_path):
    """Personal indexes are authoritative; shared defaults never filter them."""
    config_path = Path(config_path)
    config = json.loads(config_path.read_text(encoding='utf-8'))
    if isinstance(config, list):
        return config, 'shared'
    if not isinstance(config, dict) or config.get('scope') != 'personal':
        raise ValueError('Unsupported workflow configuration')
    index = Path(config['index_path'])
    if not index.is_absolute(): index = config_path.parent / index
    overrides = config.get('overrides', [])
    if not isinstance(overrides, list): raise ValueError('Workflow overrides must be a list')
    metadata = {}
    for item in overrides:
        if item['id'] in metadata: raise ValueError('Duplicate workflow override')
        metadata[item['id']] = item
    entries = []
    seen = set()
    for line in index.read_text(encoding='utf-8').splitlines():
        if not line.startswith('| WF-'): continue
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        if len(cells) < 6: raise ValueError('Malformed workflow index row')
        match = re.search(r'\(<([^>]+)>\)', cells[5])
        if not match: raise ValueError('Workflow index entry has no method path')
        identity = cells[0]
        if identity in seen: raise ValueError('Duplicate workflow index identity')
        seen.add(identity)
        method_path = Path(match.group(1))
        if not method_path.is_absolute(): method_path = index.parent / method_path
        item = dict(metadata.get(identity, {}))
        # Preserve canonical personal names/paths and status metadata. Shared flags
        # cannot hide, rename, or renumber an item in this explicit personal scope.
        item.update(id=identity, name=cells[3], purpose=cells[4], category=cells[2],
                    path=str(method_path.resolve()), builtin=False, visible=True,
                    source='personal')
        item.setdefault('availability', 'not_checked')
        entries.append(item)
    # Explicit locally registered additions may not yet be in the long-term index.
    for original in overrides:
        if original['id'] in seen: continue
        item = dict(original)
        method_path = Path(item['path'])
        if not method_path.is_absolute(): method_path = config_path.parent / method_path
        item.update(path=str(method_path.resolve()), builtin=False, visible=True)
        item.setdefault('source', 'personal')
        entries.append(item)
    return entries, 'personal'

def render(tasks_path, workflows_path, output, workspace_path=None):
    tasks_path, workflows_path, output = (Path(p).resolve() for p in (tasks_path, workflows_path, output))
    data = json.loads(tasks_path.read_text(encoding='utf-8'))
    assert isinstance(data.get('tasks'), list), 'tasks must be a list'
    seen = set()
    for task in data['tasks']:
        assert task['id'] not in seen, 'duplicate task id'
        seen.add(task['id'])
        assert task['status'] in {'running', 'waiting', 'blocked', 'review', 'done', 'unknown', 'cancelled'}, 'invalid status'
        for key in ['id', 'title', 'next', 'verified_at', 'evidence']:
            assert isinstance(task.get(key), str), key
    data['workspace_id'] = hashlib.sha256(str(Path(workspace_path).resolve() if workspace_path else tasks_path.parent).encode()).hexdigest()[:20]
    for task in data['tasks']:
        task['main_status'] = main_status(task)
    workflows, workflow_scope = load_workflows(workflows_path)
    data['workflow_scope'] = workflow_scope
    for w in workflows:
        if w.get('builtin') and w['id'].rsplit('-',1)[-1] not in DEFAULT_IDS:
            w['visible'] = False
    # Workspace additions complement builtins. An explicit user override retains its identity.
    defaults_path = D / 'example.workflows.json'
    if workflow_scope == 'shared' and workflows_path != defaults_path and defaults_path.is_file():
        defaults = json.loads(defaults_path.read_text(encoding='utf-8'))
        for item in defaults:
            item['path'] = str((D / item['path']).resolve())
        overridden = {w['id'] for w in workflows}
        workflows = [w for w in defaults if w['id'] not in overridden] + workflows
    workflows = [w for w in workflows if w.get('visible', True) and (not w.get('builtin') or w['id'].rsplit('-',1)[-1] in DEFAULT_IDS)]
    assert isinstance(workflows, list), 'workflows must be a list'
    seen = set()
    for item in workflows:
        assert item['id'] not in seen, 'duplicate workflow id'
        seen.add(item['id'])
        for key in ['id', 'name', 'category', 'purpose', 'path']:
            assert isinstance(item.get(key), str), key
        path = Path(item['path'])
        if not path.is_absolute():
            path = workflows_path.parent / path
        item['content'] = path.read_text(encoding='utf-8') if path.is_file() else 'Method file unavailable. Check the configuration.'
    workflows.sort(key=lambda item: int(item['id'].rsplit('-', 1)[1]))
    def encode(value):
        return json.dumps(value, ensure_ascii=False).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    data['tasks_revision'] = hashlib.sha256(tasks_path.read_bytes()).hexdigest()
    data['snapshot_generated_at'] = datetime.now(timezone.utc).isoformat()
    data['snapshot_revision'] = hashlib.sha256(encode([data, workflows]).encode()).hexdigest()
    html = (D / 'template.html').read_text(encoding='utf-8').replace('__TASK_DATA__', encode(data)).replace('__WORKFLOW_DATA__', encode(workflows))
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=output.parent, delete=False) as f:
        f.write(html)
        temp = Path(f.name)
    os.replace(temp, output)
    output.with_suffix('.error.json').unlink(missing_ok=True)
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tasks', type=Path, default=D / 'example.tasks.json')
    parser.add_argument('--workflows', type=Path, default=D / 'example.workflows.json')
    parser.add_argument('--output', type=Path, default=D / 'dashboard.html')
    args = parser.parse_args()
    print(render(args.tasks, args.workflows, args.output))
