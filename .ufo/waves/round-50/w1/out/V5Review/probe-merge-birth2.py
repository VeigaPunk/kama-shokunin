import importlib.util, json, os, shutil
spec = importlib.util.spec_from_file_location("ctr", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round50-append-audit-v5-check.py")
ctr = importlib.util.module_from_spec(spec); spec.loader.exec_module(ctr)
S = "/fast/scratch/hyaku/kama-r50/V5Review/probe2"
shutil.rmtree(S, ignore_errors=True); os.makedirs(S)
NOTES = ["F.md is append-only", "the ## Axes head of F.md is re-derived in place"]
contract = ctr.HEADER + "\nF.md\tA-corr\tNOTES.md:1\texempt=## Axes@NOTES.md:2\tprobe\n"
f = ctr.Fx(S, "mb")
L = ctr.L
base = {"NOTES.md": NOTES, "registry/append-only-contract.tsv": contract.split("\n")}
c1 = f.commit({**base, "F.md": ["# s", "## Axes"] + L("hd", 24) + ["## Round 1"] + L("r", 3)})
ca = f.commit({"F.md": ["# s", "## Axes"] + L("hd", 24) + ["## Round 1"] + L("r", 3) + ["extra a"]}, [c1])
cb = f.commit({"F.md": ["# s", "## Axes"] + L("hd", 24) + ["## Round 1"] + L("r", 3) + ["merge key"]}, [c1])
cm = f.commit({"F.md": ["# s", "## Axes"] + L("hd", 24) + ["merge key", "## Round 1"] + L("r", 3) + ["extra a"]}, [ca, cb])
ce = f.commit({"F.md": ["# s", "## Axes"] + L("nh", 30) + ["## Round 1"] + L("r", 3) + ["extra a"]}, [cm])
detail = []
ok = ctr.lane_leg("/fast/scratch/hyaku/kama-r50/V5Review/tree-v5", f.d, "HEAD", detail)
print("lane_leg", ok)
for d in detail: print(d)
