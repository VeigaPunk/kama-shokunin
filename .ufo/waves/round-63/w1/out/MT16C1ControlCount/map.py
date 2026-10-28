import importlib.util, json, os, sys
S = '/fast/scratch/hyaku/kama-r63/w/MT16C1ControlCount'
spec = importlib.util.spec_from_file_location('c1', os.path.join(S, 'clone/tools/round63-c1-counter.py'))
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
rc = json.load(open(os.path.join(S, 'work/base/receipt.json')))
w = os.path.join(S, 'work/map'); os.makedirs(w, exist_ok=True)
ctl = mod.build_controls(rc, w)
for i, (fam, m, wm, expect, cap) in enumerate(ctl):
    print(i, fam, expect, cap)
print('fake-inconsistent fake live_ptok')
print('fake-foreign fake live_pid')
print('total_build_controls', len(ctl))
