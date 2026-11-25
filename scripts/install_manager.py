#!/usr/bin/env python3
"""Isolated GitHub installs. Releases are immutable; workspace is never updated."""
import argparse, hashlib, json, os, re, subprocess, sys, tarfile, tempfile, urllib.error, urllib.request, uuid
from pathlib import Path

if sys.version_info < (3, 12):
    sys.exit(f'Crews Bot needs Python 3.12 or newer; this is Python {sys.version.split()[0]}.')

PROJECT = json.loads((Path(__file__).resolve().parents[1] / 'project.json').read_text(encoding='utf-8'))
API = 'https://api.github.com'

def read(p): return json.loads(p.read_text(encoding='utf-8'))
def atomic(p, data):
    tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(tmp,p)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def inventory(root):
    result={}
    for p in root.rglob('*'):
        if any(part in {'.git','__pycache__'} for part in p.relative_to(root).parts):continue
        if p.is_symlink():raise ValueError('Symlinks are not supported in method packages')
        if p.is_file():result[str(p.relative_to(root))]=digest(p)
    return result

def validate(root):
    for f in ['README.md','general/router-method.md','dashboard/render_dashboard.py','dashboard/serve.py']:
        if not (root/f).is_file():raise ValueError('Missing package file: '+f)
    return inventory(root)

def github_token():
    if token:=os.environ.get('GITHUB_TOKEN'):return token
    try:return subprocess.run(['gh','auth','token'],capture_output=True,text=True,timeout=10).stdout.strip() or None
    except (OSError,subprocess.SubprocessError):return None

def fetch(url, accept, out=None):
    """Public repositories need no credentials; private ones use GITHUB_TOKEN or the gh login."""
    headers={'Accept':accept,'User-Agent':'crews-bot-installer'}
    if token:=github_token():headers['Authorization']='Bearer '+token
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=60) as response:
            if out is None:return response.read().decode().strip()
            while chunk:=response.read(1<<16):out.write(chunk)
    except urllib.error.HTTPError as e:
        if e.code in (401,403,404):
            sys.exit(f'GitHub refused access ({e.code}). If the repository is private, log in with `gh auth login` '
                     'or set GITHUB_TOKEN to a token that can read it, then run the command again.')
        raise

def download(root,repo,ref):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo):raise ValueError('Expected owner/repo')
    sha=fetch(f'{API}/repos/{repo}/commits/{ref}','application/vnd.github.sha')
    if not re.fullmatch('[0-9a-f]{40}',sha):raise ValueError('Invalid commit')
    releases=root/'releases';releases.mkdir(exist_ok=True)
    target=releases/sha
    if target.exists():
        manifest=read(root/'evidence'/f'{sha}.json')
        if inventory(target)!=manifest['files']:raise ValueError('Installed release modified; preserve and resolve before updating')
        return sha,target
    with tempfile.TemporaryDirectory(dir=root) as temp:
        temp=Path(temp);archive=temp/'source.tar.gz'
        with archive.open('wb') as f:fetch(f'{API}/repos/{repo}/tarball/{sha}','application/vnd.github+json',f)
        unpack=temp/'unpack';unpack.mkdir()
        with tarfile.open(archive) as tar:
            for member in tar.getmembers():
                p=Path(member.name)
                if p.is_absolute() or '..' in p.parts or not (member.isdir() or member.isfile()):raise ValueError('Unsafe archive entry')
            tar.extractall(unpack,filter='data')
        dirs=list(unpack.iterdir())
        if len(dirs)!=1 or not dirs[0].is_dir():raise ValueError('Unexpected archive layout')
        files=validate(dirs[0]);os.replace(dirs[0],target)
        atomic(root/'evidence'/f'{sha}.json',{'repository':repo,'commit':sha,'requested_ref':ref,'archive_sha256':digest(archive),'files':files})
    return sha,target

def operate(root,repo=PROJECT['repository'],ref='main',action='install'):
    root=Path(root).expanduser().resolve()
    if action=='install':
        root.mkdir(parents=True,exist_ok=False)
        (root/'evidence').mkdir();(root/'workspace').mkdir()
        atomic(root/'workspace'/'tasks.json',{'controller':'Crews Bot','updated_at':'Not verified yet','tasks':[]})
        atomic(root/'workspace'/'workflows.json',[])
        (root/'workspace'/'runs').mkdir()
        atomic(root/'workspace'/'workspace.json',{'schema_version':'workspace-v1','root':str(root/'workspace')})
        state={'schema_version':1,'repository':repo,'current':None,'previous':None}
    else:
        state=read(root/'installation.json')
        if state['schema_version']!=1:raise ValueError('Unsupported installation schema')
        current=Path(state['current'])
        if inventory(current)!=read(root/'evidence'/(current.name+'.json'))['files']:raise ValueError('Current method files changed; resolve without overwriting')
        repo=state['repository']
    if action=='rollback':
        if not state['previous']:raise ValueError('No previous release')
        previous=Path(state['previous'])
        if inventory(previous)!=read(root/'evidence'/(previous.name+'.json'))['files']:raise ValueError('Previous release changed')
        state['current'],state['previous']=state['previous'],state['current']
    else:
        sha,target=download(root,repo,ref)
        if state['current']==str(target):return state
        state['previous']=state['current'];state['current']=str(target)
    atomic(root/'installation.json',state)
    return state

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['install','update','rollback']);p.add_argument('--root',type=Path,required=True);p.add_argument('--repo',default=PROJECT['repository']);p.add_argument('--ref',default='main');a=p.parse_args()
    print(json.dumps(operate(a.root,a.repo,a.ref,a.action),ensure_ascii=False,indent=2))
