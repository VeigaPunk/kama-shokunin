#!/usr/bin/env python3
"""M1Ctr addendum: fixed F27b/F28b fixtures (cap-legal beyond-end ranges) + M36 redundancy check."""
import importlib.util, json, os, re, shutil, subprocess, sys

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


def led_path(d):
    return os.path.join(d, LEDGER_REL)


def read_led(d):
    return open(led_path(d)).read()


def write_led(d, t):
    open(led_path(d), "w").write(t)


def edit_row(text, sid, col, value):
    out, hit = [], 0
    for x in text.splitlines():
        f = x.split("\t")
        if len(f) == 11 and f[0] == sid:
            f[col] = value
            hit += 1
            out.append("\t".join(f))
        else:
            out.append(x)
    if hit != 1:
        print(f"DEBUG edit_row sid={sid} col={col} hit={hit} textlines={len(text.splitlines())}",
              file=sys.stderr)
        for x in text.splitlines():
            f2 = x.split("\t")
            if f2 and f2[0] == sid:
                print(f"DEBUG line fields={len(f2)}: {x[:120]}", file=sys.stderr)
        raise SystemExit(3)
    return "\n".join(out) + "\n"


# S001 facts
ent = c1.population(c1.show(LANE, BASE, c1.SOURCES))["S001"]
plen = len((c1.show(UP, ent["pin"], ent["path"]) or "").splitlines())
rlen = len((c1.show(UP, REL, ent["path"]) or "").splitlines())
print("S001 plen", plen, "rlen", rlen)

for name, col, val in (("F27b-reloutside", 8, f"{rlen - 4}-{rlen + 3}"),
                       ("F28b-pinoutside", 7, f"{plen - 4}-{plen + 3}")):
    d = os.path.join(CTL, name)
    shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(pass_tree, d, symlinks=True)
    write_led(d, edit_row(read_led(d), "S001", col, val))
    fixtures[name] = {"repo": d, "tip": bc.commit(d, name)}
    p = subprocess.run([sys.executable, COUNTER, "--repo", d, "--tip", fixtures[name]["tip"], "--upstream", UP],
                       capture_output=True, text=True)
    baseline[name] = {"exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr[-500:]}
    print(f"baseline {name}: exit={p.returncode}",
          p.stdout.splitlines()[1] if len(p.stdout.splitlines()) > 1 else p.stderr[:150])
    detail = [x for x in p.stdout.splitlines() if x.startswith("detail:")]
    print("  detail:", detail[:2])

json.dump({"fixtures": fixtures, "baseline": baseline},
          open(os.path.join(SCRATCH, "fixtures.json"), "w"), indent=1)

# M36 redundancy check: ROW-matching 11-cell rows vs counter population
ROW = c1.ROW
cand = 0
for line in c1.show(LANE, BASE, c1.SOURCES).splitlines():
    if ROW.match(line):
        cs = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cs) == 11:
            cand += 1
print("M36 check: ROW-matching 11-cell rows =", cand, "| counter pop =", 91,
      "| filter redundant:", cand == 91)
