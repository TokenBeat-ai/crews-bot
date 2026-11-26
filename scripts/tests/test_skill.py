import importlib.util,json,subprocess,tempfile,unittest,shutil,socket,os,signal,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
installer=module('installer',ROOT/'scripts/install_skill.py')
class SkillTest(unittest.TestCase):
 def test_registration_and_start(self):
  with tempfile.TemporaryDirectory() as td:
   t=Path(td);root=t/'install';release=root/'releases'/'test';shutil.copytree(ROOT,release,ignore=shutil.ignore_patterns('.git','__pycache__'));w=root/'workspace';w.mkdir()
   (root/'installation.json').write_text(json.dumps({'current':str(release)}));(w/'tasks.json').write_text('{"tasks":[]}');(w/'workflows.json').write_text('[]')
   skills=t/'skills';(skills/'aiworkflow').mkdir(parents=True);(skills/'aiworkflow/SKILL.md').write_text('untouched')
   with socket.socket() as occupied:
    occupied.bind(('127.0.0.1',0));occupied.listen();port=occupied.getsockname()[1]
    if port>65516: self.skipTest('ephemeral port too high')
    target=installer.register(root,skills,port)
    starter=module('starter',target/'scripts/start.py')
    before=(w/'tasks.json').read_bytes()
    first=starter.start(target);second=starter.start(target)
    try:
     self.assertFalse(first['reused']);self.assertTrue(second['reused']);self.assertEqual(first['url'],second['url']);self.assertNotIn(':'+str(port)+'/',first['url'])
     installer.register(root,skills,port);self.assertEqual((w/'tasks.json').read_bytes(),before);self.assertEqual((skills/'aiworkflow/SKILL.md').read_text(),'untouched')
     other=t/'other';shutil.copytree(root,other)
     with self.assertRaises(ValueError):installer.register(other,skills,port)
     (target/'SKILL.md').write_text('user modification')
     with self.assertRaises(ValueError):installer.register(root,skills,port)
    finally:
     # Only terminate our isolated server, identified by its unique temporary root.
     for line in subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines():
      if str(release/'dashboard/serve.py') in line:
       os.kill(int(line.strip().split(None,1)[0]),signal.SIGTERM)
if __name__=='__main__':unittest.main()
