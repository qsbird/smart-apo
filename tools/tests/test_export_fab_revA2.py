"""Exercise export orchestration in temporary projects; CLI fixtures are not KiCad validation."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'export_fab_revA2.sh'
FAKE_CLI = '''#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
args=sys.argv[1:]
with open(os.environ['TEST_TRACE'],'a') as f:f.write(json.dumps(args)+'\\n')
case=os.environ['TEST_CASE']
if args[:2]==['sch','erc']:
 report={'sheets':[{'violations':([] if case!='erc' else [{'severity':'warning'}])}]}
elif args[:2]==['pcb','drc']:
 if case=='tool_error':sys.exit(9)
 report={'violations':([{'severity':'error'}] if case=='error' else [{'severity':'warning'}]),'unconnected_items':([{}] if case=='open' else []),'schematic_parity':([{}] if case=='parity' else [])}
else:
 if os.environ.get('TEST_NO_EXPORT')=='1':sys.exit(99)
 sys.exit(0)
Path(args[args.index('-o')+1]).write_text(json.dumps(report))
'''

class ExportModeTests(unittest.TestCase):
    def invoke(self, case='pass', args=('--check-only',), forbid_export=True):
        with tempfile.TemporaryDirectory(prefix='apo-export-test-') as temp:
            root=Path(temp);(root/'tools').mkdir();rev=root/'hardware/revA2';rev.mkdir(parents=True)
            script=root/'tools/export_fab_revA2.sh';shutil.copy2(SCRIPT,script)
            for extension in ['kicad_pcb','kicad_sch']:
                (rev/f'smart_apo_common_revA2.{extension}').write_text('test placeholder')
            fab=rev/'fab_export';fab.mkdir();sentinel=fab/'existing.txt';sentinel.write_text('preserve me')
            cli=root/'fake-cli';cli.write_text(FAKE_CLI);cli.chmod(0o755);trace=root/'trace.jsonl'
            env={**os.environ,'KICAD_CLI':str(cli),'TEST_TRACE':str(trace),'TEST_CASE':case,'TEST_NO_EXPORT':str(int(forbid_export))}
            result=subprocess.run(['bash',str(script),*args],env=env,text=True,capture_output=True)
            calls=[json.loads(line) for line in trace.read_text().splitlines()] if trace.exists() else []
            return result,calls,sentinel.read_text() if sentinel.exists() else None

    def test_passing_check_only_never_exports_or_cleans(self):
        result,calls,saved=self.invoke()
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual([c[:2] for c in calls],[['sch','erc'],['pcb','drc']])
        self.assertEqual(saved,'preserve me')
        self.assertIn('NOT_FAB_RELEASED',result.stdout)

    def test_electrical_failures_stop_both_modes(self):
        for case in ['erc','error','open','parity']:
            for args in [(),('--check-only',)]:
                with self.subTest(case=case,args=args):
                    result,calls,saved=self.invoke(case,args)
                    self.assertEqual(result.returncode,2,result.stderr)
                    self.assertFalse(any('export' in c for c in calls))
                    self.assertEqual(saved,'preserve me')
                    if case=='erc':self.assertEqual(len(calls),1)

    def test_cli_failure_is_not_a_pass(self):
        result,calls,saved=self.invoke('tool_error')
        self.assertEqual(result.returncode,9)
        self.assertEqual(saved,'preserve me')
        self.assertFalse(any('export' in c for c in calls))

    def test_default_export_behavior_preserved(self):
        result,calls,saved=self.invoke(args=(),forbid_export=False)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIsNone(saved)
        self.assertEqual([c[:3] for c in calls if 'export' in c],[['pcb','export','gerbers'],['pcb','export','drill'],['pcb','export','pos'],['pcb','export','pos'],['sch','export','bom']])

    def test_options_are_validated_before_tools(self):
        for args,code in [(('--unknown',),64),(('--check-only','extra'),64),(('--help',),0)]:
            with self.subTest(args=args):
                result,calls,saved=self.invoke(args=args)
                self.assertEqual(result.returncode,code)
                self.assertEqual(calls,[])
                self.assertEqual(saved,'preserve me')

if __name__=='__main__':unittest.main()
