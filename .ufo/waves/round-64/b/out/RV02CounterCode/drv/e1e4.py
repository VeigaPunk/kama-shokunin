import importlib.util, sys, json, os, random, shutil, copy
REPO, TIP, W = sys.argv[1], sys.argv[2], sys.argv[3]
spec = importlib.util.spec_from_file_location('c1c', REPO + '/tools/round64-c1-counter.py')
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
os.makedirs(W, exist_ok=True)
server = c.pick_server(); model = os.path.realpath(os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf'))
tool_path, err = c.tool_files(REPO, TIP, W)
assert tool_path, err
PN = 'r64pTEST0001'
reqs = c.draw_probes(random.Random(42), PN)
ref = c.reference_run(server, model, reqs, W)
print('ref answers', len(ref))
# ---- E1: genuine run, then a receipt whose completion answer is fabricated
rcpt, wit, bnd, nonce, notes = c.witness_run(W, 'e1-live', tool_path, server, model, reqs)
wit['ref'] = ref; c.NONCE = nonce
g = c.score_run(rcpt, wit, bnd, PN)
print('E1 genuine met=%s fails=%s' % (g['met'], sorted(g['fails'])))
print('E1 held child probe0 text=%r' % wit['probes'][0]['text'])
print('E1 receipt completion text=%r' % json.loads(rcpt['captures']['completion']['body'])['choices'][0]['text'])
fab = c.edit_body(rcpt, 'completion', lambda o: o['choices'][0].update({'text': ' FABRICATED BY TOOL'}))
fab = c.edit_body(fab, 'completion2', lambda o: o['choices'][0].update({'text': ' FABRICATED BY TOOL'}))
f = c.score_run(fab, wit, bnd, PN)
print('E1 fabricated-answer receipt met=%s fails=%s' % (f['met'], sorted(f['fails'])))
# ---- E4: holder launched with an extra model flag; with and without --no-mmap
def run_argv(label, extra):
    mode = 'argv_' + label
    c.FAKE_MODES[mode] = r'''
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
    copyp = os.path.join(W, 'decoy-copy-' + label + '.gguf'); shutil.copy(model, copyp)
    fake = c.write_fake(W, mode)
    env = {'KAMA_FAKE_TEMPLATE': tpl, 'KAMA_FAKE_STALE': tpl, 'KAMA_FAKE_MODE': mode,
           'KAMA_FAKE_EXTRA': json.dumps(extra(copyp))}
    r, w, b, nn, notes = c.witness_run(W, 'e4-' + label, fake, server, model, reqs, env)
    w['ref'] = ref; c.NONCE = nn
    s = c.score_run(r, w, b, PN)
    print('E4 %s met=%s fails=%s argv_probes_model=%s' % (label, s['met'], sorted(s['fails']), 'n/a'))
    # what the holder actually loaded: its log
    import re
    log = open(os.path.join(W, 'e4-' + label, 'fake-' + mode, 'srv.log') if False else os.path.join(W, 'e4-' + label, 'tool-work', 'srv.log')).read()
    print('E4 %s srv.log load line: %s' % (label, [l for l in log.splitlines() if 'loading model' in l][:1]))
run_argv('mmap', lambda cp: ['-m', cp])
run_argv('nomm', lambda cp: ['-m', cp, '--no-mmap'])
# synthetic: argv/env allow-list gaps on the genuine raw snapshot
raw = copy.deepcopy(bnd['raw_a'])
raw['holders'][0]['cmdline'] += ['--log-file', '/tmp/x.log', '-c', '4096']
raw['holders'][0]['environ_keys'] += ['LLAMA_ARG_NO_MMAP']
gb = c.grade_binding(raw)
print('E5 synthetic extra-flags/env snapshot bind_argv=%s bind_env=%s' % (gb['bind_argv'], gb['bind_env']))
