#!/usr/bin/env python3
"""MT13 fuzz: 100 draws of the counter's draw_probes against the genuine
pinned server, answers taken through the counter's own probe() and graded
by the counter's own probe_fails(). Two modes:
  fresh  - live and reference are each a fresh pinned server per draw
           (the counter's own reference_run; the live child is fresh too)
  shared - one live server kept alive across all 100 draws (cache carries)
"""
import importlib.util, json, os, random, subprocess, sys, time, collections
import hashlib, signal
S = '/fast/scratch/hyaku/kama-r64/b/MT13ProbeTokens'
spec = importlib.util.spec_from_file_location(
    'c1c', S + '/clone/tools/round64-c1-counter.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
mode = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 100
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 64
server = C.pick_server()
model = os.path.realpath(os.path.expanduser(
    '~/.cache/kama-shokunin/models/stories260K.gguf'))
assert server and C.sha256_path(model) == C.MODEL_SHA
work = os.path.join(S, 'work', 'fuzz-' + mode)
os.makedirs(work, exist_ok=True)


def start(tag):
    port = C.free_port()
    log = open(os.path.join(work, tag + '.log'), 'wb')
    proc = subprocess.Popen(
        [server, '--model', model, '--alias', C.ALIAS, '--port', str(port),
         '--host', '127.0.0.1', '-c', '512', '-t', '1'],
        stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
        env={k: v for k, v in os.environ.items() if k in C._TOOL_ENV_KEYS})
    t0 = time.monotonic()
    while time.monotonic() - t0 < 60:
        st, _, body, _ = C.http(port, '/health', timeout=2.0)
        if st == 200 and body == '{"status":"ok"}':
            return proc, port
        if proc.poll() is not None:
            break
        time.sleep(0.2)
    raise SystemExit('server did not come up: ' + tag)


def stop(proc):
    proc.send_signal(signal.SIGTERM)
    try:
        proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill(); proc.wait(timeout=10)


rng = random.Random(seed)
rows = []
fails_ct = collections.Counter()
draws_bad = 0
live_shared = None
if mode == 'shared':
    live_shared = start('live-shared')
for i in range(N):
    nonce = 'r64p' + hashlib.sha256(os.urandom(8)).hexdigest()[:8]
    reqs = C.draw_probes(rng, nonce)
    # reference: the counter's own reference_run (fresh server, same flags)
    ref = C.reference_run(server, model, reqs, work)
    if mode == 'fresh':
        lp, lport = start('live')
        try:
            live = [C.probe(lport, r) for r in reqs]
        finally:
            stop(lp)
    else:
        live = [C.probe(live_shared[1], r) for r in reqs]
    bad_this = False
    for idx, p in enumerate(live):
        f = sorted(C.probe_fails(p, ref, idx))
        for k in f:
            fails_ct[k] += 1
        bad_this = bad_this or bool(f)
        rows.append({
            'draw': i, 'idx': idx, 'k_words': len(reqs[idx]['prompt'].split()) - 1,
            'n_predict': reqs[idx]['n_predict'], 'seed': reqs[idx]['seed'],
            'status': p.get('status'), 'finish_reason': p.get('finish_reason'),
            'uc': p.get('usage_completion_tokens'),
            'up': p.get('usage_prompt_tokens'), 'tc': p.get('tokenize_count'),
            'pn': p.get('timings_prompt_n'), 'cn': p.get('timings_cache_n'),
            'pred': p.get('timings_predicted_n'),
            'text_live': p.get('text'), 'text_ref': (ref[idx] or {}).get('text'),
            'uc_ref': (ref[idx] or {}).get('usage_completion_tokens'),
            'up_ref': (ref[idx] or {}).get('usage_prompt_tokens'),
            'cn_ref': (ref[idx] or {}).get('timings_cache_n'),
            'fails': f})
    draws_bad += int(bad_this)
if live_shared:
    stop(live_shared[0])
out = {'mode': mode, 'draws': N, 'seed': seed, 'answers': len(rows),
       'draws_with_any_fail': draws_bad,
       'fail_counts': dict(fails_ct), 'rows': rows}
path = os.path.join(S, 'work', f'fuzz-{mode}-{seed}.json')
json.dump(out, open(path, 'w'), indent=1)
print(f'mode={mode} draws={N} answers={len(rows)} draws_with_any_fail={draws_bad} fail_counts={dict(fails_ct)}')
print('wrote', path)
