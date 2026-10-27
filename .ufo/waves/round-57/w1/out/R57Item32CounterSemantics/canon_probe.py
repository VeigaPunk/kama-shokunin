import importlib.util, re, os, subprocess
R = "/home/vgpnk/Projects/shokunin/kama-shokunin"
S = "/fast/scratch/hyaku/kama-r57/R57Item32CounterSemantics"
spec = importlib.util.spec_from_file_location("c", f"{R}/tools/round42-selfdesc-reconcile.py")
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
for tip in ["7c873d7b4e3839489a93d6334cdf93fe5d34d19f", "8640e34c"]:
    t = subprocess.run(["git","-C",R,"cat-file","-p",f"{tip}:SCORECARD.md"],capture_output=True,text=True).stdout
    print(f"== tip {tip}")
    hs = [(i+1, l) for i, l in enumerate(t.split("\n")) if re.search(r"canonical list as of round", l, re.I)]
    for i, l in hs:
        matched = bool(re.search(r"canonical list as of round\s+(\d+)\*\*", l, re.I))
        print(f"  line {i} matched_by_canon={matched}: {l[:90]}")
    n, rows = c.canon(t)
    print("  canon() picks round", n, "rows", len(rows))
    # heading-independent probe: which table rows does canon read from a heading lacking its own table?
