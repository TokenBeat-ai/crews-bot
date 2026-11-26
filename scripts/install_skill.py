#!/usr/bin/env python3
"""Register a separate Codex skill without altering other skills or workspace data."""
import argparse, hashlib, json, os, shutil, tempfile
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'skills/crews-bot'

def inventory(path):
    return {str(p.relative_to(path)): hashlib.sha256(p.read_bytes()).hexdigest() for p in path.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in {'installation.json', '.managed.json'}}

def register(root, skills_dir, port=18761, local_entry=None):
    root = Path(root).expanduser().resolve(); skills_dir = Path(skills_dir).expanduser().resolve()
    state = json.loads((root / 'installation.json').read_text())
    if not (Path(state['current']) / 'general/router-method.md').is_file(): raise ValueError('Invalid installed package')
    if local_entry and not Path(local_entry).is_file(): raise ValueError('Local entry does not exist')
    if not 1 <= port <= 65516: raise ValueError('Invalid port')
    skills_dir.mkdir(parents=True, exist_ok=True); target = skills_dir / 'crews-bot'
    if target.exists():
        config = json.loads((target / 'installation.json').read_text())
        if config.get('root') != str(root): raise ValueError('Skill belongs to another installation; refusing to switch it')
        manifest = json.loads((target / '.managed.json').read_text())
        if inventory(target) != manifest: raise ValueError('Skill locally edited; preserve changes before reinstalling')
    with tempfile.TemporaryDirectory(dir=skills_dir) as td:
        staged = Path(td)/'crews-bot'; shutil.copytree(SOURCE, staged, ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        (staged / 'installation.json').write_text(json.dumps({'root':str(root),'port':port,'local_entry':str(Path(local_entry).resolve()) if local_entry else None},indent=2)+'\n')
        (staged / '.managed.json').write_text(json.dumps(inventory(staged),indent=2)+'\n')
        backup = Path(td)/'previous'
        if target.exists(): target.rename(backup)
        try: staged.rename(target)
        except Exception:
            if backup.exists(): backup.rename(target)
            raise
    return target

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=Path);p.add_argument('--skills-dir',type=Path,default=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'skills');p.add_argument('--port',type=int,default=18761);p.add_argument('--local-entry');a=p.parse_args()
    print(register(a.root,a.skills_dir,a.port,a.local_entry))
