import importlib.util, os, random, sys, hashlib
spec = importlib.util.spec_from_file_location('c1', sys.argv[1])
c1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c1)
work = sys.argv[2]; os.makedirs(work, exist_ok=True)
server = c1.pick_server(); model = os.path.realpath(os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf'))
same = 0; N = int(sys.argv[3])
for i in range(N):
    rng = random.Random(int.from_bytes(os.urandom(8), 'big'))
    nonce = 'r64p' + hashlib.sha256(os.urandom(8)).hexdigest()[:8]
    reqs = c1.draw_probes(rng, nonce)
    ref = c1.reference_run(server, model, reqs, work)
    if len(ref) != 2 or None in ref: print('ref-fail', i); continue
    eq = ref[0]['text'] == ref[1]['text']
    same += eq
    print(i, 'texts_equal' if eq else 'texts_differ', repr(ref[0]['text'])[:40], repr(ref[1]['text'])[:40], ref[0]['usage_completion_tokens'], ref[1]['usage_completion_tokens'], flush=True)
print('equal', same, 'of', N)
