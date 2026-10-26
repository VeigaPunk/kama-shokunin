#!/usr/bin/env python3
"""Round-45 C2 amendment v2: score the base and the two C2 shortcut controls with
tools/round45-claim-outcome-audit-v2.py, reusing build_controls.py's builders.
Receipts: <outdir>/v2-<name>.c2.out. Scratch under --work, removed on exit."""
import argparse
import importlib.util
import os
import shutil
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
V2 = f"{LANE}/tools/round45-claim-outcome-audit-v2.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default=os.path.join(os.environ.get("HYAKU_SCRATCH", "/fast/scratch/hyaku"),
                                                  "kama-r45", "L1", "controls-v2"))
    ap.add_argument("--outdir", default=f"{LANE}/.ufo/waves/round-45/controls")
    a = ap.parse_args()
    bc = load("bc", f"{LANE}/.ufo/waves/round-45/controls/build_controls.py")
    c2 = load("c2v2", V2)
    os.makedirs(a.work, exist_ok=True)

    def score(name, d, tip):
        p = subprocess.run([sys.executable, V2, "--repo", d, "--tip", tip, "--fleet", FLEET,
                            "--out", f"{a.outdir}/v2-{name}.c2.out"], capture_output=True, text=True)
        with open(f"{a.outdir}/v2-{name}.c2.out", "a") as fh:
            fh.write(f"exit={p.returncode}\n")
        print(name, p.stdout.splitlines()[2] if p.stdout else p.stderr.strip(), f"exit={p.returncode}")

    try:
        d = bc.clone(a.work, "base")
        score("base", d, bc.BASE)
        for name in ("junk-c2-allmet", "junk-c2-grepdraft"):
            d = bc.clone(a.work, name)
            rows = ["\t".join(c2.HEADER)]
            for r, cl in c2.KEYS:
                for side in ("self", "outside"):
                    repo, rev, path = c2.side_spec(int(r), side)
                    if name == "junk-c2-allmet":
                        out, line = "met", "1"
                    else:
                        t = (c2.show(FLEET if repo == "fleet" else LANE, rev, path) or "").splitlines()
                        attr = c2.read_file(t, int(r))
                        out, line = "absent", "-"
                        single = [(i, next(iter(x[cl]))) for i, x in enumerate(attr, 1) if len(x.get(cl, ())) == 1]
                        multi = [i for i, x in enumerate(attr, 1) if len(x.get(cl, ())) >= 2]
                        if single:
                            line, out = str(single[0][0]), single[0][1]
                        elif multi:
                            line, out = str(multi[0]), "mixed"
                    rows.append("\t".join([r, cl, side, out, repo, rev, path, line,
                                           "automatic draft, no line read by anyone"]))
            bc.write(d, c2.LEDGER, "\n".join(rows) + "\n")
            tip0 = bc.commit(d, name + " ledger")
            p = subprocess.run([sys.executable, V2, "--repo", d, "--tip", tip0, "--fleet", FLEET],
                               capture_output=True, text=True)
            want = [x.split("summary line wanted: ", 1)[1] for x in p.stdout.splitlines() if "summary line wanted: " in x]
            miss = [x.split("table missing ", 1)[1] for x in p.stdout.splitlines() if "detail: table missing " in x]
            sc = open(os.path.join(d, "SCORECARD.md")).read().splitlines()
            out = [x.rstrip().rstrip("|") + f"; {c2.LEDGER} |" if x.startswith("| calibration |") else x for x in sc]
            out += ["", c2.HEADING, ""] + want + ["", "| round | claim | self | outside |", "|---|---|---|---|"]
            out += ["| {} | {} | {} | {} |".format(*eval(m)) for m in miss]
            bc.write(d, "SCORECARD.md", "\n".join(out) + "\n")
            score(name, d, bc.commit(d, name))
    finally:
        shutil.rmtree(a.work, ignore_errors=True)


if __name__ == "__main__":
    main()
