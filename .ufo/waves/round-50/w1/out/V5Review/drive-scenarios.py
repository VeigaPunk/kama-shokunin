import importlib.util, sys, os, json
spec = importlib.util.spec_from_file_location("ctr", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round50-append-audit-v5-check.py")
ctr = importlib.util.module_from_spec(spec); spec.loader.exec_module(ctr)
S = "/fast/scratch/hyaku/kama-r50/V5Review"
tree = sys.argv[1]; fxroot = sys.argv[2]
os.makedirs(fxroot, exist_ok=True)
detail = []
res = ctr.scenarios(tree, fxroot, detail)
print("RESULTS", list(zip([d.split(':')[0] for d in detail], res)))
for d in detail: print(d)
