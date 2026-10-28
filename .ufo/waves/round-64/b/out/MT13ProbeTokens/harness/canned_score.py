#!/usr/bin/env python3
"""Score a forged tool through the counter's own witness_run/score_run path
(same draws, same reference, same procfs binding). Prints the probe-level
failure set (per outside probe) and the full score failure set."""
import importlib.util, os, random, hashlib, json, sys
S = '/fast/scratch/hyaku/kama-r64/b/MT13ProbeTokens'
spec = importlib.util.spec_from_file_location(
    'c1c', S + '/clone/tools/round64-c1-counter.py')
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
tool = sys.argv[1]
label = sys.argv[2]
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 64
server = C.pick_server()
model = os.path.realpath(os.path.expanduser(
    '~/.cache/kama-shokunin/models/stories260K.gguf'))
work = os.path.join(S, 'work', 'score-' + label)
os.makedirs(work, exist_ok=True)
tpl = S + '/work/live/receipt.json'
rng = random.Random(seed)
probe_nonce = 'r64p' + hashlib.sha256(os.urandom(8)).hexdigest()[:8]
reqs = C.draw_probes(rng, probe_nonce)
ref = C.reference_run(server, model, reqs, work)
receipt, witness, binding, nonce, notes = C.witness_run(
    work, 'live', tool, server, model, reqs,
    extra_env={'CANNED_TEMPLATE': tpl})
C.NONCE = nonce
print('notes:', notes)
if witness is None:
    print('no witness'); sys.exit(2)
witness['ref'] = ref
for i, p in enumerate(witness['probes']):
    print(f'probe{i} probe_fails={sorted(C.probe_fails(p, ref, i))} '
          f'text={p.get("text")!r} ref_text={ref[i].get("text")!r} '
          f'finish={p.get("finish_reason")} uc={p.get("usage_completion_tokens")} '
          f'n={p.get("n_predict")} up={p.get("usage_prompt_tokens")} tc={p.get("tokenize_count")}')
s = C.score_run(receipt, witness, binding, probe_nonce)
print('met=', s['met'], 'fails=', sorted(s['fails']))
