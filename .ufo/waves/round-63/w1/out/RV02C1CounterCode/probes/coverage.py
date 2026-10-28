import importlib.util, json, collections
spec = importlib.util.spec_from_file_location('c1', '/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round63-c1-counter.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
S = '/fast/scratch/hyaku/kama-r63/w/RV02C1CounterCode'
rc = json.load(open(S + '/work/receipt.json'))
m.NONCE = rc['nonce']
ctl = m.build_controls(rc, S + '/covwork')
expects = collections.Counter(e for _, _, _, e, _ in ctl)
print('controls built:', len(ctl))
universe = sorted(set(m.STORED) | {'schema','nonce_match'} | {'live_status','live_ctype','live_object','live_model','live_text','live_created','live_fp_shape','live_fp_capture','live_pid','live_port','live_owned','live_nonce','live_ptok','live_server_sha','live_model_sha','listener_owned','fake-only:none'} - {'fake-only:none'})
print('expect names targeted:', len(expects), sorted(expects))
print('UNTARGETED:', [u for u in universe if u not in expects])
# duplicate mutations: compare serialized receipts
import hashlib
seen = collections.defaultdict(list)
for i,(fam, mm, wm, e, cap) in enumerate(ctl):
    key = json.dumps(mm, sort_keys=True) + ('|W' if wm else '') + '|' + e
    seen[key].append(fam)
print('duplicate mutation groups:', [v for v in seen.values() if len(v) > 1])
