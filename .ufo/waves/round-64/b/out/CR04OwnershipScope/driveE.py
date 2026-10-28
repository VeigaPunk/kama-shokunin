import os, sys, json, random, hashlib
sys.path.insert(0, os.environ['S_WORK']); os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
import c1
REPO = os.environ['S_CLONE']; TIP = 'f6a4ea9a8b5a876d685b08e7e582ec0723412a4a'
W = os.path.join(os.environ['S_WORK'], 'e'); os.makedirs(W, exist_ok=True)
server = c1.pick_server(); model = os.path.realpath(os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf'))
rng = random.Random(7); probe_nonce = 'r64p' + hashlib.sha256(os.urandom(8)).hexdigest()[:8]
reqs = c1.draw_probes(rng, probe_nonce)
ref = c1.reference_run(server, model, reqs, W)
tp, err = c1.tool_files(REPO, TIP, W); assert tp and not err, err
rg, wg, bg, ng, ng_notes = c1.witness_run(W, 'genuine', tp, server, model, reqs)
wg['ref'] = ref; c1.NONCE = ng
sg = c1.score_run(rg, wg, bg, probe_nonce)
print('GENUINE met=%s fails=%s teardown=%s' % (sg['met'], sorted(sg['fails']), (bg or {}).get('teardown')))
tpl = os.path.join(W, 'genuine', 'receipt.json')
fp = os.path.join(os.environ['S_WORK'], 'forged_e.py')
rf, wf, bf, nf, nf_notes = c1.witness_run(W, 'forged', fp, server, model, reqs,
                                           extra_env={'KAMA_FAKE_TEMPLATE': tpl})
print('FORGED notes=%s receipt=%s witness=%s' % (nf_notes, bool(rf), bool(wf)))
if wf:
    wf['ref'] = ref; c1.NONCE = nf
    sf = c1.score_run(rf, wf, bf, probe_nonce)
    print('FORGED met=%s fails=%s' % (sf['met'], sorted(sf['fails'])))
    print('FORGED probe_text=%s' % [p.get('text') for p in wf['probes']])
    import json as J; J.dump({'raw_a':bf['raw_a'],'raw_b':bf['raw_b']}, open(os.path.join(W,'forged-binding.json'),'w'), default=str)
    print('FORGED hold_pid=%s receipt_child=%s teardown=%s' % (wf.get('hold_pid'), rf.get('child_pid'), (bf or {}).get('teardown')))
