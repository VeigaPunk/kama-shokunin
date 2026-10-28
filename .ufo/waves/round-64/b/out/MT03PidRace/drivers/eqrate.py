import importlib.util, os, random, hashlib, sys
clone = sys.argv[1]; n = int(sys.argv[2])
spec = importlib.util.spec_from_file_location('c1', os.path.join(clone, 'tools', 'round64-c1-counter.py'))
c1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1)
server = c1.pick_server(); model = os.path.realpath(os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf'))
work = os.path.abspath(sys.argv[3]); os.makedirs(work, exist_ok=True)
eq = 0; rows = []
for i in range(n):
    rng = random.Random(int.from_bytes(os.urandom(8), 'big'))
    nonce = 'r64p' + hashlib.sha256(os.urandom(8)).hexdigest()[:8]
    reqs = c1.draw_probes(rng, nonce)
    ref = c1.reference_run(server, model, reqs, work)
    if len(ref) == 2:
        same = ref[0].get('text') == ref[1].get('text')
        eq += int(same); rows.append((ref[0].get('text'), ref[1].get('text'), same))
print(f'draws={n} ref_texts_equal={eq}/{len(rows)}')
for r in rows[:6]: print(repr(r))
