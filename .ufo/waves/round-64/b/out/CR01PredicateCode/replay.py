import importlib.util, os, json, random, sys
spec = importlib.util.spec_from_file_location('c1', 'clone/tools/round64-c1-counter.py')
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
REPO = os.path.abspath('clone'); TIP = sys.argv[1]; WORK = os.path.abspath('work-replay'); os.makedirs(WORK, exist_ok=True)
server = M.pick_server(); model = os.path.realpath(os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf'))
tool_path, err = M.tool_files(REPO, TIP, WORK); assert tool_path and not err, err
rng = random.Random(12345); pn = 'r64p' + 'deadbeef'
reqs = M.draw_probes(rng, pn)
ref = M.reference_run(server, model, reqs, WORK)
r1, w1, b1, n1, notes1 = M.witness_run(WORK, 'live', tool_path, server, model, reqs)
w1['ref'] = ref; M.NONCE = n1
s1 = M.score_run(r1, w1, b1, pn)
print('genuine run met=', s1['met'], sorted(s1['fails']))
tpl = os.path.join(WORK, 'genuine-receipt.json'); json.dump(r1, open(tpl, 'w'))
M.FAKE_MODES['replay'] = r'''
port = free_port()
p = spawn_real(port); wait_health(port)
hold_and_release(hold_doc(p.pid, port))
p.terminate(); p.wait()
write_receipt(p.pid, port, good_holders(p.pid))
'''
fake = M.write_fake(WORK, 'replay')
env = {'KAMA_FAKE_TEMPLATE': tpl, 'KAMA_FAKE_STALE': tpl, 'KAMA_FAKE_MODE': 'replay'}
r2, w2, b2, n2, notes2 = M.witness_run(WORK, 'replay', fake, server, model, reqs, env)
w2['ref'] = ref; M.NONCE = n2
s2 = M.score_run(r2, w2, b2, pn)
print('replayed-capture run met=', s2['met'], 'fails=', sorted(s2['fails']), 'notes=', notes2)
print('replayed receipt completion.created/id:', json.loads(r2['captures']['completion']['body'])['created'], json.loads(r2['captures']['completion']['body'])['id'], '| genuine:', json.loads(r1['captures']['completion']['body'])['created'], json.loads(r1['captures']['completion']['body'])['id'])
print('replayed nonce', r2.get('nonce'), 'run nonce', n2, 'child_pid', r2.get('child_pid'), 'hold_pid', w2.get('hold_pid'))
