"""Driver v2: the drv.py binding readout plus an in-window observer.

A sampler thread (not the counter) polls the run-port listener's holder set
from hold.json onward, ~1 ms apart, and each counter probe() call is timed.
The counter's own raw_a/raw_b, grade_binding and score_run are unchanged.
  python3 drv2.py <clone> <tip> <work>
"""
import importlib.util, json, os, random, sys, hashlib, threading, time

clone, tip, work = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3])
os.makedirs(work, exist_ok=True)
spec = importlib.util.spec_from_file_location(
    'c1', os.path.join(clone, 'tools', 'round64-c1-counter.py'))
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)

server = c1.pick_server()
model = os.path.realpath(os.path.expanduser(
    '~/.cache/kama-shokunin/models/stories260K.gguf'))
tool_path, err = c1.tool_files(clone, tip, work)
assert tool_path and not err, err
rng = random.Random(int.from_bytes(os.urandom(8), 'big'))
probe_nonce = 'r64p' + hashlib.sha256(os.urandom(8)).hexdigest()[:8]
reqs = c1.draw_probes(rng, probe_nonce)
ref = c1.reference_run(server, model, reqs, work)

samples, probe_t = [], []
hold_dir = os.path.join(work, 'live', 'hold')
stop = threading.Event()


def sampler():
    port = None
    last = None
    while not stop.is_set():
        if port is None:
            try:
                port = json.load(open(os.path.join(hold_dir, 'hold.json')))['port']
            except (OSError, ValueError, KeyError):
                time.sleep(0.001)
                continue
        ls = c1.listeners(port)
        pids = tuple(sorted(c1.holder_pids([i for i, _ in ls])[0]))
        if pids != last:
            samples.append((time.monotonic_ns(), pids))
            last = pids
        time.sleep(0.001)


_orig_probe = c1.probe


def timed_probe(port, req):
    t0 = time.monotonic_ns()
    out = _orig_probe(port, req)
    probe_t.append((t0, time.monotonic_ns(), req['n_predict']))
    return out


c1.probe = timed_probe
th = threading.Thread(target=sampler, daemon=True)
th.start()
receipt, witness, binding, nonce, notes = c1.witness_run(
    work, 'live', tool_path, server, model, reqs)
stop.set()
th.join(2)
c1.NONCE = nonce
witness['ref'] = ref
raw_a, raw_b = binding['raw_a'], binding['raw_b']
t_a, t_b = raw_a['t0_ns'], None
out = {
    'notes': notes,
    'grade_binding(raw_a)': c1.grade_binding(raw_a),
    'raw_a_holders': [h.get('pid') for h in raw_a['holders']],
    'raw_b_holders': [h.get('pid') for h in raw_b['holders']],
    'tool_pid': raw_a['tool_pid'],
    'holder_ppid': [h.get('ppid') for h in raw_a['holders']],
    'bind_stable_equal': c1.holders_signature(raw_a) == c1.holders_signature(raw_b),
    'hold_pid': witness['hold_pid'], 'child_pid': receipt.get('child_pid'),
    'teardown': binding.get('teardown'),
    'probe_windows_ms': [round((b - a) / 1e6, 1) for a, b, _ in probe_t],
    'holder_transitions': [(round((t - samples[0][0]) / 1e6, 2), list(p))
                           for t, p in samples],
    'probes': [{k: p.get(k) for k in ('status', 'text', 'n_predict',
                                       'usage_prompt_tokens',
                                       'usage_completion_tokens',
                                       'timings_prompt_n', 'tokenize_count')}
               for p in witness['probes']],
    'ref': [{k: p.get(k) for k in ('text', 'usage_prompt_tokens',
                                    'usage_completion_tokens',
                                    'timings_prompt_n', 'tokenize_count')}
            for p in ref],
}
s = c1.score_run(receipt, witness, binding, probe_nonce)
out['met'] = s['met']
out['fails'] = sorted(s['fails'])
print(json.dumps(out, indent=1, sort_keys=True, default=str))
