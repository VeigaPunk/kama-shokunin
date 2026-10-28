import importlib.util, sys, json, os, random, shutil
REPO, TIP, W = sys.argv[1], sys.argv[2], sys.argv[3]
spec = importlib.util.spec_from_file_location('c1c', REPO + '/tools/round64-c1-counter.py')
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
os.makedirs(W, exist_ok=True)
server = c.pick_server(); model = os.path.realpath(os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf'))
tool_path, err = c.tool_files(REPO, TIP, W)
PN = 'r64pTEST0002'
reqs = c.draw_probes(random.Random(43), PN)
ref = c.reference_run(server, model, reqs, W)
# genuine receipt template from the tip tool (needed for the fake's receipt copy)
rcpt, wit, bnd, nonce, notes = c.witness_run(W, 'e4b-genuine', tool_path, server, model, reqs)
c.FAKE_MODES['argv_nomm'] = r'''
port = free_port()
extra = json.loads(os.environ['KAMA_FAKE_EXTRA'])
env = {k: v for k, v in os.environ.items() if k in ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR')}
p = subprocess.Popen([A.server, '--model', A.model, '--alias', A.alias, '--port', str(port),
    '--host', '127.0.0.1', '-c', '512', '-t', '1'] + extra,
    stdout=open(os.path.join(A.work, 'srv.log'), 'wb'), stderr=subprocess.STDOUT,
    stdin=subprocess.DEVNULL, env=env)
wait_health(port)
hold_and_release(hold_doc(p.pid, port))
p.terminate(); p.wait()
write_receipt(p.pid, port, good_holders(p.pid))
'''
tpl = os.path.join(W, 'genuine-receipt.json'); json.dump(rcpt, open(tpl, 'w'))
copyp = os.path.join(W, 'decoy-copy-nomm.gguf'); shutil.copy(model, copyp)
fake = c.write_fake(W, 'argv_nomm')
extra = ['-m', copyp, '--load-mode', 'none']
env = {'KAMA_FAKE_TEMPLATE': tpl, 'KAMA_FAKE_STALE': tpl, 'KAMA_FAKE_MODE': 'argv_nomm', 'KAMA_FAKE_EXTRA': json.dumps(extra)}
r, w, b, nn, notes = c.witness_run(W, 'e4b-nomm', fake, server, model, reqs, env)
w['ref'] = ref; c.NONCE = nn
s = c.score_run(r, w, b, PN)
print('E4b argv -m copy + --load-mode none met=%s fails=%s notes=%s' % (s['met'], sorted(s['fails']), notes))
log = os.path.join(W, 'e4b-nomm', 'tool-work', 'srv.log')
print('E4b load lines:', [l for l in open(log, errors='replace').read().splitlines() if 'loading model' in l or 'mmap' in l.lower()][:3])
