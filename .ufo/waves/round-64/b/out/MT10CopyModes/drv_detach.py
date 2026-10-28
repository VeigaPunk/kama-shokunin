# Evidence driver for the detach scenario: genuine receipt as template, then the detach fake, procfs snapshot printed.
import importlib.util, json, os, random, sys, hashlib, time
cpath, repo, tip, work, mode = sys.argv[1:6]
spec = importlib.util.spec_from_file_location('c1', cpath)
c1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1)
os.makedirs(work, exist_ok=True)
server = c1.pick_server(); model = os.path.realpath(os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf'))
tool_path, err = c1.tool_files(repo, tip, work)
pn = 'r64p' + hashlib.sha256(os.urandom(8)).hexdigest()[:8]
reqs = c1.draw_probes(random.Random(int.from_bytes(os.urandom(8), 'big')), pn)
gr, gw, gb, gn, _ = c1.witness_run(work, 'genuine-'+str(os.getpid()), tool_path, server, model, reqs)
tpl = os.path.join(work, 'genuine-receipt.json'); json.dump(gr, open(tpl, 'w'))
stale = os.path.join(work, 'stale-hold.json'); json.dump({'schema': 'kama-completion-hold/v1', 'port': 1, 'pid': 1, 'alias': c1.ALIAS, 'model_sha256': c1.MODEL_SHA, 'server_sha256': c1.SERVER_SHA, 'prompt': c1.PROMPT, 'at': 'x'}, open(stale, 'w'))
fake = c1.write_fake(work, mode)
r, w, b, nonce, notes = c1.witness_run(work, 'fake-' + mode, fake, server, model, reqs, {'KAMA_FAKE_TEMPLATE': tpl, 'KAMA_FAKE_STALE': stale, 'KAMA_FAKE_MODE': mode})
if w is not None: w['ref'] = c1.reference_run(server, model, reqs, work)
c1.NONCE = nonce
s = c1.score(r, w, b) if r and w and b else None
print('notes', notes, 'fails', sorted(s['fails']) if s else None)
if b:
    ra = b['raw_a']
    print('tool_pid', ra['tool_pid'], 'hold_pid', ra['hold_pid'], 'unreadable_own', ra['unreadable_own'], 'unreadable_old', ra['unreadable_old'])
    for h in ra['holders']:
        print('holder', h['pid'], 'exe', h['exe'], 'ppids', h['ppids'][:4], 'cmdline', (h['cmdline'] or [])[:3])
    print('listeners', ra['listeners'], 'port', ra['port'], 'hold_port', ra['hold_port'])
