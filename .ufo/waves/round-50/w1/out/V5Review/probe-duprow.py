# Contract with TWO rows on one pattern: exempt=## Axes then exempt=## Planned.
# Tool unions (file_regions); counter titles[pat] overwrites -> last row wins.
import importlib.util, json, os, shutil
spec = importlib.util.spec_from_file_location("ctr", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round50-append-audit-v5-check.py")
ctr = importlib.util.module_from_spec(spec); spec.loader.exec_module(ctr)
S = "/fast/scratch/hyaku/kama-r50/V5Review/probe3"
shutil.rmtree(S, ignore_errors=True); os.makedirs(S)
NOTES = ["docs files are append-only",
         "the ## Axes head of docs files is re-derived in place",
         "the ## Planned head of docs files is re-derived in place"]
contract = (ctr.HEADER + "\n"
            "docs/*.md\tA-corr\tNOTES.md:1\texempt=## Axes@NOTES.md:2\tprobe\n"
            "docs/*.md\tA-corr\tNOTES.md:1\texempt=## Planned@NOTES.md:3\tprobe\n")
f = ctr.Fx(S, "dup")
L = ctr.L
files = {"NOTES.md": NOTES, "registry/append-only-contract.tsv": contract.split("\n")}
for i in range(1, 6):
    files[f"docs/F{i}.md"] = ["# s", "## Axes"] + L(f"ax{i}", 25) + ["## Round 1"] + L("r", 3)
c1 = f.commit(files)
upd = {}
for i in range(1, 6):
    upd[f"docs/F{i}.md"] = ["# s", "## Axes"] + L(f"new{i}", 30) + ["## Round 1"] + L("r", 3)
c2 = f.commit(upd)
detail = []
ok = ctr.lane_leg("/fast/scratch/hyaku/kama-r50/V5Review/tree-v5", f.d, "HEAD", detail)
print("lane_leg", ok)
for d in detail: print(d)
