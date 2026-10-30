import importlib.util, pathlib, json, sys, os
from unittest.mock import patch
root=pathlib.Path(sys.argv[1]); module_path=root/'clone/tools/round64-c1-counter.py'
spec=importlib.util.spec_from_file_location('counter',module_path); c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
# Pure fault injection: no procfs change, no real signals, no foreign listener contact.
with patch.object(c,'stat_fields',return_value=(None,None)):
    print('D12 stat unreadable => pid_gone:',c.pid_gone(999999,123))
with patch.object(c,'stat_fields',return_value=(42,123)), patch('builtins.open',side_effect=PermissionError), patch.object(c.os,'kill') as k:
    c.kill_if_same(999999,123)
    print('N2 unreadable state with matching ticks => mocked kill:',k.call_args)
# Any holder returned from untrusted hold port is sent to cleanup before ownership admission.
class FakeProc:
    pid=999990
    def __init__(self,*a,**kw):
        hold=root/'mock-case/hold/hold.json'
        hold.write_text(json.dumps({'port':45678,'pid':999991}))
    def poll(self): return 0
    def wait(self,timeout=None): return 0
raw={'holders':[{'pid':999991,'start_ticks':456}], 'tool_pid':999990}
with patch.object(c.subprocess,'Popen',FakeProc), patch.object(c,'start_ticks_of',return_value=123), patch.object(c,'collect',return_value=raw), patch.object(c,'probe',return_value={}), patch.object(c,'pid_gone',return_value=True), patch.object(c,'listeners',return_value=[]), patch.object(c,'kill_if_same') as k, patch.object(c.os,'killpg') as kg:
    c.witness_run(str(root),'mock-case','unused','unused','unused',[],{'prompt':'x','n_predict':3,'seed':1})
    print('N1 unowned recorded holder cleanup:',k.call_args,'process-group cleanup:',kg.call_args)
# Readability failure at readlink level is silently dropped, unlike listdir failure.
with patch.object(c.os,'listdir',side_effect=lambda p: ['999991'] if p=='/proc' else ['7']), patch.object(c.os,'readlink',side_effect=PermissionError):
    print('N3 readable fd directory, denied fd links => holder_pids:',c.holder_pids([7],retries=0))
# stat-unreadable process is dropped by start-ticks gating.
with patch.object(c,'listeners',return_value=[]),patch.object(c,'holder_pids',return_value=(set(),{999991})),patch.object(c,'start_ticks_of',return_value=None),patch.object(c,'ns_of',return_value={}):
    r=c.collect(45678,{},0,0,999990,123,'/server','/model')
    print('N3 unreadable fd and stat => graded unreadable:',r['unreadable_own'],'recorded count:',r['unreadable_old'])
# Same path at two inode identities is collapsed before file_set receives it.
from io import StringIO
maps='1000-2000 r--p 00000000 08:01 11 /usr/lib/example.so\n2000-3000 r-xp 00000000 08:01 22 /usr/lib/example.so\n'
with patch('builtins.open',return_value=StringIO(maps)):
    print('N4 same-path different-inode maps => file_set:',c.file_set(c.read_maps(999991,'/server')))
# Globals restore even when scorer raises; REF_FILES is not consumed by score_run.
c.NONCE='outer'; c.TOOL_REQ.update({'prompt':'outer'})
with patch.object(c,'score',side_effect=RuntimeError('injected')):
    try:c.score_run({}, {'tool_req':{'prompt':'inner'}},{},'probe',nonce='inner')
    except RuntimeError:pass
print('global restoration:',c.NONCE,c.TOOL_REQ)
