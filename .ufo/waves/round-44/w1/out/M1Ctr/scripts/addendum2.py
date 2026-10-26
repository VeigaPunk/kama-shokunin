#!/usr/bin/env python3
"""M1Ctr addendum 2: F33 (release range a=0 kills M06) + S037/S043 cited-text-absence check."""
import importlib.util, json, os, shutil, subprocess, sys

SCRATCH = "/fast/scratch/hyaku/kama-r44/M1Ctr"
LANE = os.path.join(SCRATCH, "lane")
UP = "/fast/scratch/hyaku/kama-r44/shared/llama.cpp"
BASE = "9d9cc93ec50783cd114829a91757b90d57c78dc6"
REL = "d854d98bae598388ecea1ed84396587e5edc326d"
BC_PATH = os.path.join(LANE, ".ufo", "waves", "round-44", "controls", "build_controls.py")
CTL = os.path.join(SCRATCH, "ctl")
LEDGER_REL = "registry/release-recheck-b11889.tsv"
COUNTER = os.path.join(LANE, "tools", "round44-release-recheck-audit.py")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


c1 = load(COUNTER, "c1")
bc = load(BC_PATH, "bc")
fx = json.load(open(os.path.join(SCRATCH, "fixtures.json")))
fixtures, baseline = fx["fixtures"], fx["baseline"]
pass_tree = fixtures["pass"]["repo"]

# F33: S001 release_lines "0-3" — parses only when ranges() drops the a<1 guard
d = os.path.join(CTL, "F33-relzero")
shutil.rmtree(d, ignore_errors=True)
shutil.copytree(pass_tree, d, symlinks=True)
lp = os.path.join(d, LEDGER_REL)
text = open(lp).read()
out = []
for x in text.splitlines():
    f = x.split("\t")
    if len(f) == 11 and f[0] == "S001":
        f[8] = "0-3"
        out.append("\t".join(f))
    else:
        out.append(x)
open(lp, "w").write("\n".join(out) + "\n")
fixtures["F33-relzero"] = {"repo": d, "tip": bc.commit(d, "F33-relzero")}
p = subprocess.run([sys.executable, COUNTER, "--repo", d, "--tip", fixtures["F33-relzero"]["tip"],
                    "--upstream", UP], capture_output=True, text=True)
baseline["F33-relzero"] = {"exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr[-500:]}
print("baseline F33-relzero: exit=%d" % p.returncode,
      p.stdout.splitlines()[1] if len(p.stdout.splitlines()) > 1 else p.stderr[:150],
      [x for x in p.stdout.splitlines() if x.startswith("detail:")][:1])

json.dump({"fixtures": fixtures, "baseline": baseline},
          open(os.path.join(SCRATCH, "fixtures.json"), "w"), indent=1)

# M28 proof fact: for S037/S043/S108 is some strong-cited line's text absent from the release file?
pop = c1.population(c1.show(LANE, BASE, c1.SOURCES))
for sid in ("S037", "S043", "S108"):
    ent = pop[sid]
    ptext = (c1.show(UP, ent["pin"], ent["path"]) or "").splitlines()
    rtext = (c1.show(UP, REL, ent["path"]) or "").splitlines()
    rset = {x.strip() for x in rtext}
    strong = sorted(n for n in c1.cited(ent["cells"])[0] if 1 <= n <= len(ptext))
    absent = [n for n in strong if ptext[n - 1].strip() not in rset]
    print(f"{sid}: strong cited {strong[:6]}{'...' if len(strong) > 6 else ''} "
          f"absent-from-release-text: {len(absent)}/{len(strong)} {absent[:4]}")
