import importlib.util, os, json, random, sys
spec = importlib.util.spec_from_file_location('c1', 'clone/tools/round64-c1-counter.py')
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
REPO = os.path.abspath('clone'); TIP = sys.argv[1]; WORK = os.path.abspath('work-futlive'); os.makedirs(WORK, exist_ok=True)
server = M.pick_server(); model = os.path.realpath(os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf'))
tool_path, err = M.tool_files(REPO, TIP, WORK)
rng = random.Random(4242); pn = 'r64p' + 'feedface'
reqs = M.draw_probes(rng, pn)
ref = M.reference_run(server, model, reqs, WORK)
r1, w1, b1, n1, _ = M.witness_run(WORK, 'live', tool_path, server, model, reqs)
tpl = os.path.join(WORK, 'genuine-receipt.json'); json.dump(r1, open(tpl, 'w'))
M.FAKE_MODES['futlive'] = r'''
port = free_port()
p = spawn_real(port); wait_health(port)
hp = os.path.join(A.hold_dir, 'hold.json')
json.dump(hold_doc(p.pid, port), open(hp, 'w'))
fut = time.time() + 3600
os.utime(hp, (fut, fut))
t0 = time.time()
while time.time() - t0 < float(A.hold_timeout):
    if os.path.exists(os.path.join(A.hold_dir, 'release')): break
    time.sleep(0.1)
os.unlink(hp)
p.terminate(); p.wait()
write_receipt(p.pid, port, good_holders(p.pid))
'''
fake = M.write_fake(WORK, 'futlive')
r2, w2, b2, n2, notes = M.witness_run(WORK, 'futlive', fake, server, model, reqs, {'KAMA_FAKE_TEMPLATE': tpl, 'KAMA_FAKE_STALE': tpl, 'KAMA_FAKE_MODE': 'futlive'})
w2['ref'] = ref; M.NONCE = n2
s2 = M.score_run(r2, w2, b2, pn)
print('future-dated hold.json, live genuine holder: met=', s2['met'], 'fails=', sorted(s2['fails']), 'notes=', notes)
print('hold_mtime_ns - t0_ns (s):', (b2['raw_a']['hold_mtime_ns'] - b2['raw_a']['t0_ns'])/1e9)
