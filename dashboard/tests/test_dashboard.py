"""Regression checks for task identity, custom methods and protected local actions."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
import threading
import unittest
import urllib.request
import urllib.error

D = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(D))
from render_dashboard import render
from serve import Handler, ThreadingHTTPServer

class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.tasks = self.root/'tasks.json'
        self.workflows = self.root/'workflows.json'
        self.output = self.root/'dashboard.html'
        self.task = dict(id='T-TEST', title='Example', status='review', next='Review output', verified_at='', evidence='', execution_provider='other', execution_url='https://example.com/task/1')
        self.tasks.write_text(json.dumps(dict(tasks=[self.task])))
        self.method = self.root/'method.md'
        self.method.write_text('Test method </script><script>alert(1)</script>')
        self.custom = dict(id='WF-OPS-012',name='User method',category='Work',purpose='test',path=str(self.method),builtin=False,source='imported')
        self.workflows.write_text(json.dumps([self.custom]))
    def tearDown(self): self.temp.cleanup()
    def payload(self, id):
        return json.loads(re.search(r'<script type="application/json" id="'+id+r'">(.*?)</script>', self.output.read_text(),re.S).group(1))
    def test_custom_identity_and_source_preserved(self):
        render(self.tasks,self.workflows,self.output)
        items=self.payload('workflow-data')
        self.assertEqual({w['id'] for w in items},{'WF-SAMPLE-001','WF-OPS-012'})
        custom=next(w for w in items if w['id']=='WF-OPS-012')
        self.assertFalse(custom['builtin']);self.assertEqual(custom['source'],'imported')
        self.assertNotIn('is_example',custom)
    def test_execution_target_preserved_without_inventing_chat(self):
        before=self.tasks.read_bytes()
        render(self.tasks,self.workflows,self.output)
        t=self.payload('data')['tasks'][0]
        self.assertEqual(t['execution_url'],self.task['execution_url'])
        self.assertNotIn('thread_id',t)
        self.assertEqual(t['main_status'],'pending')
        self.assertEqual(before,self.tasks.read_bytes())
    def test_method_script_cannot_escape_json(self):
        render(self.tasks,self.workflows,self.output)
        self.assertNotIn('</script><script>alert(1)</script>',self.output.read_text())
        self.assertIn('</script>',next(w for w in self.payload('workflow-data') if w['id']=='WF-OPS-012')['content'])
    def test_duplicate_task_rejected_without_replacing_snapshot(self):
        render(self.tasks,self.workflows,self.output); before=self.output.read_bytes()
        self.tasks.write_text(json.dumps(dict(tasks=[self.task,self.task])))
        with self.assertRaises(AssertionError):render(self.tasks,self.workflows,self.output)
        self.assertEqual(before,self.output.read_bytes())
    def test_personal_index_not_filtered_by_shared_defaults(self):
        index=self.root/'index.md'
        index.write_text('| WF-PROJECT-009 | Project | Personal | My router | Personal purpose | [method](<'+str(self.method)+'>) |\n| WF-GTM-012 | GTM | Social | My social method | Reply | [method](<'+str(self.method)+'>) |\n')
        config={'scope':'personal','index_path':str(index),'overrides':[dict(self.custom,id='WF-PROJECT-009',name='Wrong shared name',builtin=True,visible=False)]}
        self.workflows.write_text(json.dumps(config))
        render(self.tasks,self.workflows,self.output)
        items=self.payload('workflow-data')
        self.assertEqual({w['id'] for w in items},{'WF-PROJECT-009','WF-GTM-012'})
        self.assertEqual(items[0]['name'],'My router')
        self.assertTrue(all(w['source']=='personal' and not w['builtin'] for w in items))
        self.assertEqual(self.payload('data')['workflow_scope'],'personal')
        with index.open('a') as out:out.write('| WF-LOCAL-015 | Local | Custom | New personal method | New | [method](<'+str(self.method)+'>) |\n')
        render(self.tasks,self.workflows,self.output)
        self.assertEqual(len(self.payload('workflow-data')),3)

    def test_personal_missing_index_preserves_last_snapshot(self):
        render(self.tasks,self.workflows,self.output);before=self.output.read_bytes()
        self.workflows.write_text(json.dumps({'scope':'personal','index_path':str(self.root/'missing.md'),'overrides':[]}))
        with self.assertRaises(FileNotFoundError):render(self.tasks,self.workflows,self.output)
        self.assertEqual(before,self.output.read_bytes())

    def test_refresh_and_remove_preserve_existing_boundaries(self):
        render(self.tasks,self.workflows,self.output)
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        server.token='test-token';server.tasks_path=self.tasks;server.workflows_path=self.workflows;server.dashboard_path=self.output
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base='http://127.0.0.1:'+str(server.server_port)
        def post(route,body,valid=True):
            req=urllib.request.Request(base+route,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','Origin':base,'X-Dashboard-Token':server.token if valid else 'invalid'},method='POST')
            try:
                with urllib.request.urlopen(req) as response:return response.status
            except urllib.error.HTTPError as e:
                code=e.code;e.close();return code
        try:
            original=self.tasks.read_bytes();revision=hashlib.sha256(original).hexdigest()
            self.assertEqual(post('/refresh',{}),200);self.assertEqual(original,self.tasks.read_bytes())
            self.assertEqual(post('/task-action',dict(id='T-TEST',action='remove',revision='stale')),409)
            self.assertEqual(post('/task-action',dict(id='T-TEST',action='done',revision=revision)),409)
            self.assertEqual(post('/task-action',dict(id='T-TEST',action='remove',revision=revision),False),403)
            self.assertEqual(original,self.tasks.read_bytes())
            self.assertEqual(post('/task-action',dict(id='T-TEST',action='remove',revision=revision)),200)
            self.assertEqual(json.loads(self.tasks.read_text())['tasks'],[])
            self.assertEqual(self.tasks.with_suffix('.dashboard-backup.json').read_bytes(),original)
            self.assertTrue(self.method.exists())
        finally:server.shutdown();server.server_close();thread.join()

if __name__=='__main__':unittest.main()
