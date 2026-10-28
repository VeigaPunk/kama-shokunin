import importlib.util, os, json, random, sys
spec = importlib.util.spec_from_file_location('c1', 'clone/tools/round64-c1-counter.py')
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
REPO = os.path.abspath('clone'); TIP = sys.argv[1]; WORK = os.path.abspath('work-st'); os.makedirs(WORK, exist_ok=True)
server = M.pick_server(); model = os.path.realpath(os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf'))
tool_path, _ = M.tool_files(REPO, TIP, WORK)
pn = 'r64p' + '0badc0de'; reqs = M.draw_probes(random.Random(9), pn)
ref = M.reference_run(server, model, reqs, WORK)
r1, w1, b1, n1, _ = M.witness_run(WORK, 'live', tool_path, server, model, reqs)
w1['ref'] = ref; M.NONCE = n1
print('real evaluator selftest =', M.eval_selftest_run(r1, w1, b1, pn), 'genuine met', M.score_run(r1, w1, b1, pn)['met'])
# item 2 detail: how many failures the envelope break produces, and whether it is credited at default cap
env = M.edit_body(r1, 'completion', lambda o: o.update({'object': 'chat.completion'}))
s = M.score_run(env, w1, b1, pn)
print('envelope break: fails=%d expect completion_envelope in fails=%s is_hit(cap=5)=%s is_hit(cap=30)=%s' % (len(s['fails']), 'completion_envelope' in s['fails'], M.is_hit(s,'completion_envelope'), M.is_hit(s,'completion_envelope',30)))
# constant-met evaluator
M_score = M.score
M.score = lambda r, w, b: {'met': True, 'fails': set()}
print('constant-met=True evaluator selftest =', M.eval_selftest_run(r1, w1, b1, pn))
M.score = M_score
