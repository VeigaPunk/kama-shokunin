# Evidence driver: imports the counter (committed, unmutated), runs ONE witness_run at a tip,
# re-scores exactly as main() does, and prints the procfs observations the binding decided on.
import importlib.util, json, os, random, sys, hashlib, time
cpath, repo, tip, work, label = sys.argv[1:6]
spec = importlib.util.spec_from_file_location('c1', cpath)
c1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1)
os.makedirs(work, exist_ok=True)
server = c1.pick_server(); model = os.path.realpath(os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf'))
tool_path, err = c1.tool_files(repo, tip, work)
assert tool_path, err
pn = 'r64p' + hashlib.sha256(os.urandom(8)).hexdigest()[:8]
reqs = c1.draw_probes(random.Random(int.from_bytes(os.urandom(8), 'big')), pn)
ref = c1.reference_run(server, model, reqs, work)
r, w, b, nonce, notes = c1.witness_run(work, label, tool_path, server, model, reqs)
w['ref'] = ref; c1.NONCE = nonce
s = c1.score_run(r, w, b, pn)
ra = b['raw_a']
out = {'met': s['met'], 'fails': sorted(s['fails']), 'notes': notes,
       'server_path': ra['server_path'], 'tool_pid': ra['tool_pid'], 'hold_pid': ra['hold_pid'],
       'hold_minus_t0_s': (ra['hold_mtime_ns'] - ra['t0_ns']) / 1e9,
       'now_minus_hold_mtime_s': (time.time_ns() - ra['hold_mtime_ns']) / 1e9,
       'holders': [{'pid': h['pid'], 'exe_sha_ok': h['exe_sha256'] == c1.SERVER_SHA,
                    'ppids': h['ppids'], 'start_ticks': h['start_ticks'], 'tool_ticks': ra['tool_start_ticks'],
                    'cmdline': h['cmdline']} for h in ra['holders']],
       'probe_texts': [p['text'] for p in w['probes']], 'ref_texts': [p['text'] for p in ref]}
print(json.dumps(out, indent=1))
