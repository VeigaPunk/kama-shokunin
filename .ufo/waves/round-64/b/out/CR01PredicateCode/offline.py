import importlib.util, os, time
spec = importlib.util.spec_from_file_location('c1', 'clone/tools/round64-c1-counter.py')
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
sp = os.path.expanduser('~/.local/opt/llama-b11755/llama-server')
mp = os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf')
def raw(**kw):
    h = {'pid': 500, 'exe': sp, 'exe_sha256': M.SERVER_SHA, 'start_ticks': 1000,
         'cmdline': [sp, '--port', '8123', '--host', '127.0.0.1', '--alias', M.ALIAS, '--model', mp],
         'environ_keys': ['PATH'], 'maps': [{'path': sp, 'deleted': False, 'sha256': M.SERVER_SHA}],
         'ppids': [400, 1], 'pid_': None}
    r = {'holders': [h], 'server_path': sp, 'model_path': mp, 'port': 8123, 'hold_port': 8123,
         'hold_pid': 500, 'listeners': [{'inode': 1, 'loopback': True}], 'unreadable_own': [],
         'tool_pid': 400, 'tool_start_ticks': 900, 'hold_mtime_ns': 2_000_000_000,
         't0_ns': 1_000_000_000, 'hold_schema': 'kama-completion-hold/v1'}
    r.update(kw); return r
base = M.grade_binding(raw())
print('baseline all-true:', all(base.values()), [k for k,v in base.items() if not v])
# 1 future-dated hold.json (mtime far in future) 
g = M.grade_binding(raw(hold_mtime_ns=time.time_ns()+3600*10**9))
print('future mtime -> hold_fresh', g['hold_fresh'])
# 2 holder ticks equal to tool ticks (non-strict 'after')
h = raw(); h['holders'][0]['start_ticks'] = 900
print('holder started same tick as tool -> hold_fresh', M.grade_binding(h)['hold_fresh'])
# 3 extra argv flag not in pinned set
h = raw(); h['holders'][0]['cmdline'] += ['--lora', '/tmp/x.gguf']
print('extra --lora argv -> bind_argv', M.grade_binding(h)['bind_argv'])
# 4 extra env key outside LD_ denylist
h = raw(); h['holders'][0]['environ_keys'] = ['PATH', 'LLAMA_ARG_CHAT_TEMPLATE_FILE']
print('LLAMA_ARG_* env -> bind_env', M.grade_binding(h)['bind_env'])
# 5 unhashed system library mapping (e.g. preload dropped into /usr/lib)
h = raw(); h['holders'][0]['maps'].append({'path': '/usr/lib/libevil.so', 'deleted': False, 'sha256': None})
print('/usr/lib/libevil.so unhashed -> bind_maps', M.grade_binding(h)['bind_maps'])
# 6 holder set missing: hold_pid mismatch covered; holders unreadable other-uid invisible (code path, not testable here)
# 7 future mtime with a lone holder: stale_future style raw with NO holders
h = raw(holders=[]); print('no holders + future mtime -> hold_fresh', M.grade_binding(h)['hold_fresh'])
# 8 hold_fresh with a non-hold schema
print('schema v2 hold -> hold_fresh', M.grade_binding(raw(hold_schema='kama-completion-hold/v0'))['hold_fresh'])
# 9 _flag_values with --port=... form
h = raw(); h['holders'][0]['cmdline'] = [sp, '--port=8123', '--host=127.0.0.1', '--alias=' + M.ALIAS, '--model=' + mp]
print('--flag=value form -> bind_argv', M.grade_binding(h)['bind_argv'])
