import importlib.util, json, sys
spec = importlib.util.spec_from_file_location('c1', sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.NONCE = ''
import os
work = sys.argv[2]
tool = os.path.join(work, 'tip', 'tools', 'kama-completion-live.py')
rc, w, nonce = m.witness_run(os.path.join(work, 'diag'), tool)
m.NONCE = nonce
s = m.score(rc, w)
u = rc['captures']['completion'] and json.loads(rc['captures']['completion']['body'])['usage']
tk = json.loads(rc['captures']['tokenize']['body'])['tokens']
print('receipt usage.prompt_tokens=', u['prompt_tokens'], 'receipt tokenize len=', len(tk))
print('witness usage_prompt_tokens=', w['usage_prompt_tokens'], 'witness tokenize_count=', w['tokenize_count'])
print('score met=', s['met'], 'fails=', sorted(s['fails']))
