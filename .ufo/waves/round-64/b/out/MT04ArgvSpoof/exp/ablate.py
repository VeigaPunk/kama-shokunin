import os, subprocess, sys
sys.path.insert(0, '/fast/scratch/hyaku/kama-r64/b/MT04ArgvSpoof/exp')
import drive
from drive import D, S, BASE, TOOL
CTR = f'{D}/tools/round64-c1-counter.py'
ctr_base = subprocess.run(['git', '-C', D, 'show', f'{BASE}:tools/round64-c1-counter.py'], capture_output=True, check=True).stdout.decode()
SUBS = {
    'exe': [("out['bind_exe'] = bool(hs) and all(", "out['bind_exe'] = True or bool(hs) and all(")],
    'maps': [("out['bind_maps'] = bool(hs) and all(maps_ok(h) for h in hs)", "out['bind_maps'] = True")],
    'claim': [("    if mine != theirs:\n        fails.add('bind_claim')", "    if False:\n        fails.add('bind_claim')")],
}
def ablate(name, variant, neuter):
    text = variant()
    with open(TOOL, 'w') as f: f.write(text)
    subprocess.run(['git', '-C', D, 'add', '-A'], check=True)
    subprocess.run(['git', '-C', D, '-c', 'user.name=seat', '-c', 'user.email=seat@seat.invalid', 'commit', '-q', '-m', f'wip {name}'], check=True)
    tip = subprocess.run(['git', '-C', D, 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
    c = ctr_base
    for k in neuter:
        for old, new in SUBS[k]:
            assert c.count(old) == 1, (k, old[:40], c.count(old))
            c = c.replace(old, new, 1)
    with open(CTR, 'w') as f: f.write(c)
    work = f'{S}/work/{name}'; os.makedirs(work, exist_ok=True)
    r = subprocess.run([sys.executable, CTR, '--repo', D, '--tip', tip, '--work', work], capture_output=True, text=True, cwd=f'{D}/tools', timeout=900)
    subprocess.run(['git', '-C', D, 'checkout', '--', 'tools/round64-c1-counter.py'], check=True)
    print(f'== {name} neutered={neuter} tip={tip[:12]} exit={r.returncode}\n{r.stdout.strip()}\n{r.stderr.strip()[:600]}\n', flush=True)
    subprocess.run(['git', '-C', D, 'reset', '-q', '--hard', BASE], check=True)
if __name__ == '__main__':
    ablate('X1_fabR_no_exe_maps_claim', drive.variants['A_retitle_fab'], ['exe', 'maps', 'claim'])
    ablate('X2_fabR_no_exe_claim', drive.variants['A_retitle_fab'], ['exe', 'claim'])
    ablate('X3_fabR_no_maps_claim', drive.variants['A_retitle_fab'], ['maps', 'claim'])
