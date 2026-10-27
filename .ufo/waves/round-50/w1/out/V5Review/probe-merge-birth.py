# Fixture: key born on second parent under ## Round 1; merge (parents [ca,cb])
# holds the key under ## Axes. Tool (first-parent birth) sees birth at merge
# under Axes; spec/counter (all-parents) does not. Then an event deletes 25
# lines under ## Axes incl. the key. Exempt={## Axes}.
import importlib.util, json, subprocess, sys, os, shutil
spec = importlib.util.spec_from_file_location("ctr", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round50-append-audit-v5-check.py")
ctr = importlib.util.module_from_spec(spec); spec.loader.exec_module(ctr)
S = "/fast/scratch/hyaku/kama-r50/V5Review/probe1"
shutil.rmtree(S, ignore_errors=True); os.makedirs(S)
NOTES = ["F.md is append-only", "the ## Axes head of F.md is re-derived in place"]
row = ctr.HEADER + "\nF.md\tA-corr\tNOTES.md:1\texempt=## Axes@NOTES.md:2\tprobe\n"
f = ctr.Fx(S, "mb")
L = ctr.L
c1 = f.commit({"NOTES.md": NOTES, "F.md": ["# s", "## Axes"] + L("hd", 24) + ["## Round 1"] + L("r", 3)})
ca = f.commit({"F.md": ["# s", "## Axes"] + L("hd", 24) + ["## Round 1"] + L("r", 3) + ["extra a"]}, [c1])
cb = f.commit({"F.md": ["# s", "## Axes"] + L("hd", 24) + ["## Round 1"] + L("r", 3) + ["merge key"]}, [c1])
# merge: parents [ca, cb]; blob holds 'merge key' under ## Axes (and not under Round 1)
cm = f.commit({"F.md": ["# s", "## Axes"] + L("hd", 24) + ["merge key", "## Round 1"] + L("r", 3) + ["extra a"]}, [ca, cb])
# event: rewrite Axes, deleting 25 (24 fillers + merge key)
ce = f.commit({"F.md": ["# s", "## Axes"] + L("nh", 30) + ["## Round 1"] + L("r", 3) + ["extra a"]}, [cm])
code, j = ctr.run_tool("/fast/scratch/hyaku/kama-r50/V5Review/tree-v5", f.d, row, S, "mb")
print("tool exit", code)
for e in (j or {}).get("events", []):
    print("TOOL EVENT", json.dumps(e)[:200])
# counter lane leg on this fixture repo
detail = []
ok = ctr.lane_leg("/fast/scratch/hyaku/kama-r50/V5Review/tree-v5", f.d, "HEAD", detail)
print("lane_leg", ok)
for d in detail: print(d)
