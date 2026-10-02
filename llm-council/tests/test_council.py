import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import subprocess
import sys
import time
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1]/'scripts'/'council.py'
spec = importlib.util.spec_from_file_location('council', SCRIPT)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)

class CouncilTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.env = patch.dict(os.environ, {'XDG_CONFIG_HOME': str(self.root/'config'), 'XDG_STATE_HOME': str(self.root/'state'), 'CODEX_HOME': str(self.root/'codex')})
        self.env.start()
    def tearDown(self):
        self.env.stop()
        self.temp.cleanup()
    def call(self, args):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            result = c.main(['--cwd', str(self.root), *args])
        return result, json.loads(stream.getvalue())
    def test_precedence_and_subdirectory_discovery(self):
        (self.root/'.git').mkdir()
        user = self.root/'config'/'llm-council'/'config.json'
        c.write_private(user, {'members': ['opus'], 'default_harness': 'claude', 'timeout_seconds': 20})
        (self.root/'.llm-council.json').write_text('{"timeout_seconds":30,"default_harness":"codex"}')
        sub = self.root/'nested';sub.mkdir()
        cfg, root = c.config_for(sub)
        self.assertEqual(root, self.root)
        self.assertEqual(cfg['members'], ['claude:opus@default'])
        self.assertEqual(cfg['timeout_seconds'],30)
    def test_repo_bare_members_bind_to_own_default(self):
        user=self.root/'config'/'llm-council'/'config.json'
        c.write_private(user,{'default_harness':'claude','members':['opus']})
        (self.root/'.llm-council.json').write_text('{"members":["gpt-5"]}')
        config,_=c.config_for(self.root)
        self.assertEqual(config['members'],['codex:gpt-5@default'])
    def test_invalid_config_does_not_fallback(self):
        for data in [{'default_harness':[]}, {'command':'rm -rf x'}, {'concurrency':True}, {'members':[]}]:
            with self.assertRaises(c.CouncilError):c.validate_config(data)
        (self.root/'.llm-council.json').write_text('{broken')
        with self.assertRaises(c.CouncilError):c.config_for(self.root)
    def test_sessions_isolated_and_prompt_cannot_mutate(self):
        self.call(['--session','alpha','members','claude:opus'])
        _, data = self.call(['--session','beta','members'])
        self.assertEqual(len(data['members']),3)
        _, data = self.call(['--session','alpha','--dry-run','--','members','codex:other'])
        self.assertEqual(data['members'][0]['member'],'claude:opus@default')
        _, data = self.call(['--session','alpha','members'])
        self.assertEqual(data['members'],['claude:opus@default'])
        self.assertEqual(c.state_path('alpha').stat().st_mode & 0o777,0o600)
    def test_prompt_subcommand_names_and_explicit_override(self):
        _, data = self.call(['--dry-run','--','setup'])
        self.assertIn('argv',data['members'][0])
        self.call(['--session','alpha','members','claude:opus'])
        _, data = self.call(['--session','alpha','--dry-run','codex:other','--','prompt'])
        self.assertEqual(data['members'][0]['member'],'codex:other@default')
    def test_safe_selector_and_default_effort(self):
        for bad in ['codex:model;echo','codex:model@invalid','cursor:default@high','unknown:model']:
            with self.assertRaises(c.CouncilError):c.member(bad)
        self.assertNotIn('--model',c.command_for(c.member('claude:default')))
        self.assertNotIn('--effort',c.command_for(c.member('claude:default')))
        self.assertIn('opus[effort=high]', c.command_for(c.member('cursor:opus@high')))
    def test_partial_failure_remains_visible(self):
        def result(m,*args):
            return {'member':m['selector'],'status':'failed','error':'missing'} if m['harness']=='cursor' else {'member':m['selector'],'status':'ok','answer':'answer'}
        with patch.object(c,'run_member',side_effect=result):
            code, data = self.call(['--','answer'])
        self.assertEqual(code,1)
        self.assertFalse(data['complete'])
        self.assertEqual(data['succeeded'],2)
        self.assertEqual(len(data['results']),3)
    def test_cursor_permissions_exist_before_launch(self):
        def result(m,prompt,config,cwd,*args):
            if m['harness']=='cursor':
                permissions=json.loads((Path(cwd)/'.cursor'/'cli.json').read_text())['permissions']
                self.assertEqual(permissions['allow'],[])
                self.assertIn('Mcp(*:*)',permissions['deny'])
                self.assertIn('Read(/**)',permissions['deny'])
                self.assertIn('Shell(*)',permissions['deny'])
            return {'member':m['selector'],'status':'ok','answer':'answer'}
        with patch.object(c,'run_member',side_effect=result):
            code,data=self.call(['--','answer'])
        self.assertEqual(code,0)
        self.assertTrue(data['complete'])
    def test_io_exception_retains_other_answers(self):
        for error_type in (OSError, RuntimeError):
            def result(m,*args):
                if m['harness']=='cursor': raise error_type('private path must not be exposed')
                return {'member':m['selector'],'status':'ok','answer':'answer'}
            with patch.object(c,'run_member',side_effect=result):
                code, data = self.call(['--','answer'])
            self.assertEqual(code,1)
            self.assertEqual(data['succeeded'],2)
            self.assertNotIn('private path',json.dumps(data))
    def test_real_process_stdin_and_nonzero_exit(self):
        binary = self.root/'bin';binary.mkdir()
        fake=binary/'claude'
        fake.write_text('#!/usr/bin/env python3\nimport json,sys\nprompt=sys.stdin.read()\nprint(json.dumps({"result":prompt}))\n')
        fake.chmod(0o700)
        with patch.dict(os.environ,{'PATH':str(binary)+os.pathsep+os.environ['PATH']}):
            result=c.run_member(c.member('claude:default'), 'literal $(touch sentinel)', c.DEFAULTS, self.root)
            self.assertEqual(result['status'],'ok')
            self.assertEqual(result['answer'],'literal $(touch sentinel)')
            self.assertFalse((self.root/'sentinel').exists())
            fake.write_text('#!/usr/bin/env python3\nimport sys\nsys.stderr.write("Unauthorized secret-value")\nsys.exit(4)\n')
            result=c.run_member(c.member('claude:default'), 'prompt', c.DEFAULTS, self.root)
            self.assertEqual(result['status'],'failed')
            self.assertIn('authentication',result['error'])
            self.assertNotIn('secret-value',json.dumps(result))
    def test_auth_redaction_stops_before_process(self):
        with patch.dict(os.environ,{'CURSOR_API_KEY':'  "[SENSITIVE]"  '}), patch.object(c.subprocess,'Popen') as launch:
            result=c.run_member(c.member('cursor:default'), 'prompt', c.DEFAULTS, self.root)
        launch.assert_not_called()
        self.assertEqual(result['status'],'failed')
        self.assertIn('CURSOR_API_KEY',result['error'])
        self.assertNotIn('[SENSITIVE]',result['error'])
    def test_invalid_unicode_file_is_controlled_error(self):
        prompt = self.root/'invalid.txt'; prompt.write_bytes(b"\xff")
        result = subprocess.run([sys.executable,str(SCRIPT),'--cwd',str(self.root),'--prompt-file',str(prompt)],capture_output=True)
        self.assertEqual(result.returncode,2)
        self.assertNotIn(b'Traceback',result.stderr)
    def test_opt_in_diagnostics_are_private(self):
        binary=self.root/'bin';binary.mkdir()
        fake=binary/'claude';fake.write_text('#!/usr/bin/env python3\nimport sys\nsys.stderr.write("private diagnostic")\nsys.exit(1)\n');fake.chmod(0o700)
        with patch.dict(os.environ,{'PATH':str(binary)+os.pathsep+os.environ['PATH']}):
            result=c.run_member(c.member('claude:default'), 'prompt', c.DEFAULTS, self.root, self.root)
        diagnostic=Path(result['diagnostics'])
        self.assertEqual(diagnostic.stat().st_mode & 0o777,0o600)
        self.assertIn('private diagnostic',diagnostic.read_text())
        self.assertNotIn('private diagnostic',result['error'])
    def test_stderr_storm_keeps_valid_answer(self):
        binary=self.root/'bin';binary.mkdir()
        fake=binary/'claude';fake.write_text('#!/usr/bin/env python3\nimport sys,json\nsys.stderr.write("x"*1100000)\nprint(json.dumps({"result":"valid answer"}))\n');fake.chmod(0o700)
        with patch.dict(os.environ,{'PATH':str(binary)+os.pathsep+os.environ['PATH']}):
            result=c.run_member(c.member('claude:default'),'prompt',c.DEFAULTS,self.root)
        self.assertEqual(result['status'],'ok')
        self.assertEqual(result['answer'],'valid answer')
        self.assertTrue(result['stderr_truncated'])
    def test_cursor_shell_snapshot_skips_user_dotfiles(self):
        with patch.dict(os.environ,{'SHELL':'/bin/zsh'}):
            self.assertEqual(c.clean_environment('cursor')['SHELL'],'/bin/sh')
            self.assertEqual(c.clean_environment('claude')['SHELL'],'/bin/zsh')
    def test_timeout_kills_descendant_in_its_own_process_group(self):
        binary=self.root/'bin';binary.mkdir()
        pidfile=self.root/'grandchild.pid'
        fake=binary/'claude'
        fake.write_text('#!/usr/bin/env python3\nimport subprocess,sys,time\n'
                        'p=subprocess.Popen([sys.executable,"-c","import time; time.sleep(60)"],process_group=0)\n'
                        f'open({str(pidfile)!r},"w").write(str(p.pid))\ntime.sleep(60)\n')
        fake.chmod(0o700)
        with patch.dict(os.environ,{'PATH':str(binary)+os.pathsep+os.environ['PATH']}):
            result=c.run_member(c.member('claude:default'),'prompt',{**c.DEFAULTS,'timeout_seconds':3},self.root)
        self.assertEqual(result['status'],'failed')
        self.assertIn('Still running at timeout',result['error'])
        grandchild=int(pidfile.read_text())
        for _ in range(50):
            try: os.kill(grandchild,0)
            except ProcessLookupError: break
            time.sleep(0.1)
        else:
            self.fail('grandchild in its own process group survived the timeout')
    def test_output_limit(self):
        binary=self.root/'bin';binary.mkdir()
        fake=binary/'claude';fake.write_text('#!/usr/bin/env python3\nimport sys\nsys.stdout.write("x"*1000000)\n');fake.chmod(0o700)
        with patch.dict(os.environ,{'PATH':str(binary)+os.pathsep+os.environ['PATH']}):
            result=c.run_member(c.member('claude:default'), 'prompt', {**c.DEFAULTS,'max_output_chars':1000}, self.root)
        self.assertEqual(result['status'],'failed')

if __name__=='__main__':unittest.main()
