"""Driver: import the unmutated counter from a clone and print the binding
values the one-line met= output does not show. Usage:
  python3 drv.py <clone> <tip> <work>
Calls the counter's own witness_run/grade_binding/score_run; nothing else."""
import importlib.util, json, os, random, sys, hashlib

clone, tip, work = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3])
os.makedirs(work, exist_ok=True)
spec = importlib.util.spec_from_file_location(
    'c1', os.environ.get('C1PATH') or os.path.join(clone, 'tools', 'round64-c1-counter.py'))
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
receipt, witness, binding, nonce, notes = c1.witness_run(
    work, 'live', tool_path, server, model, reqs)
c1.NONCE = nonce
witness['ref'] = ref
raw_a, raw_b = binding['raw_a'], binding['raw_b']
out = {
    'notes': notes,
    'grade_binding(raw_a)': c1.grade_binding(raw_a),
    'raw_a_states': [h.get('state') for h in raw_a['holders']],
    'raw_b_states': [h.get('state') for h in raw_b['holders']],
    'raw_a_holders': [(h.get('pid'), h.get('exe_sha256') == c1.SERVER_SHA)
                      for h in raw_a['holders']],
    'raw_b_holders': [(h.get('pid'), h.get('exe_sha256') == c1.SERVER_SHA)
                      for h in raw_b['holders']],
    'bind_stable_equal': c1.holders_signature(raw_a) == c1.holders_signature(raw_b),
    'hold_pid': witness['hold_pid'], 'child_pid': receipt.get('child_pid'),
    'teardown': binding.get('teardown'),
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
