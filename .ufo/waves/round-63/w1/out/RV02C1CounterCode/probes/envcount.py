import importlib.util, json
spec = importlib.util.spec_from_file_location('c1', '/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round63-c1-counter.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
S = '/fast/scratch/hyaku/kama-r63/w/RV02C1CounterCode'
rc = json.load(open(S + '/work/receipt.json')); m.NONCE = rc['nonce']
ctl = m.build_controls(rc, S + '/covwork')
w = None
import subprocess
for fam, mm, wm, e, cap in ctl:
    if fam in ('tamper','log','idcr','shape') and e in ('completion_envelope','health_ready','completion_choice_shape','completion_id_created'):
        s = m.score(mm, {'status':200}) 
        print(fam, e, 'cap', cap, 'nfails', len(s['fails']), sorted(s['fails'])[:12])
print('--- receipt-side fail counts only (live_* excluded, dummy witness):')
for fam, mm, wm, e, cap in ctl:
    if e in ('completion_envelope','health_ready','completion_choice_shape','completion_id_created','nonce_match','hold_released'):
        s = m.score(mm, {'status':200})
        rs = {x for x in s['fails'] if not x.startswith('live_')}
        print(fam, e, 'cap', cap, 'receipt-side fails', len(rs))
