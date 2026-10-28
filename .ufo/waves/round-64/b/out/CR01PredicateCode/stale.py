import importlib.util, os, json, random, sys
spec = importlib.util.spec_from_file_location('c1', 'clone/tools/round64-c1-counter.py')
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
REPO = os.path.abspath('clone'); TIP = sys.argv[1]; WORK = os.path.abspath('work-stale'); os.makedirs(WORK, exist_ok=True)
server = M.pick_server(); model = os.path.realpath(os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf'))
tool_path, err = M.tool_files(REPO, TIP, WORK)
rng = random.Random(777); pn = 'r64p' + 'cafef00d'
reqs = M.draw_probes(rng, pn)
ref = M.reference_run(server, model, reqs, WORK)
r1, w1, b1, n1, _ = M.witness_run(WORK, 'live', tool_path, server, model, reqs)
w1['ref'] = ref; M.NONCE = n1
print('genuine met=', M.score_run(r1, w1, b1, pn)['met'])
tpl = os.path.join(WORK, 'genuine-receipt.json'); json.dump(r1, open(tpl, 'w'))
stale_doc = os.path.join(WORK, 'stale-hold.json')
json.dump({'schema': 'kama-completion-hold/v1', 'port': w1['hold_port'], 'pid': w1['hold_pid'], 'alias': M.ALIAS,
           'model_sha256': M.MODEL_SHA, 'server_sha256': M.SERVER_SHA, 'prompt': 'x', 'at': 'x'}, open(stale_doc, 'w'))
env_base = {'KAMA_FAKE_TEMPLATE': tpl, 'KAMA_FAKE_STALE': stale_doc}
for mode in ('stale_old', 'stale_future'):
    fake = M.write_fake(WORK, mode)
    r, w, b, n, notes = M.witness_run(WORK, mode, fake, server, model, reqs, dict(env_base, KAMA_FAKE_MODE=mode))
    if w: w['ref'] = ref
    M.NONCE = n
    s = M.score_run(r, w, b, pn) if (r and w and b) else {'met': None, 'fails': 'no-run'}
    print(mode, 'met=', s['met'], 'fails=', sorted(s['fails']), 'notes=', notes)
    print('  binding raw_a holders:', len((b or {}).get('raw_a', {}).get('holders', [])) if b else None, 'hold_mtime_ns vs t0', (b or {}).get('raw_a', {}).get('hold_mtime_ns'), (b or {}).get('raw_a', {}).get('t0_ns'))
