#!/usr/bin/env python3
"""Round-45 controls: score the frozen C1/C2 counters on trees that skip the claimed work.

Each control is a commit in a throwaway clone of the lane at the frozen base, built under
--work (default $HYAKU_SCRATCH/kama-r45/L1/controls). Receipts go to --outdir.
Controls:
  base                  the lane base, no round-45 work
  junk-c1-allholds      11 C1 rows classed holds, copies are placeholder bytes, no receipts
  junk-c1-massdrifted   real upstream copies fetched, every file row classed drifted with
                        filler notes and a witness_new taken from the new copy's last line;
                        live/identity/inventory rows classed holds with no evidence
  junk-c2-allmet        126 C2 rows outcome met citing line 1, generated table and summary
  junk-c2-grepdraft     the unread automatic draft: first line whose tokens give the claim
                        one outcome, else absent; generated table, summary and axes cite
"""
import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
import urllib.request

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
BASE = "6b8ccfb310de339e9452514aea3a9402a970c3e6"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run(*a, cwd=None):
    p = subprocess.run(list(a), cwd=cwd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"{a}: {p.stderr}")
    return p.stdout


def clone(work, name):
    d = os.path.join(work, name)
    shutil.rmtree(d, ignore_errors=True)
    run("git", "clone", "-q", "--shared", "--no-checkout", LANE, d)
    run("git", "-C", d, "checkout", "-q", "--detach", BASE)
    if run("git", "-C", d, "rev-parse", "--show-toplevel").strip() != os.path.realpath(d):
        raise SystemExit("fixture toplevel mismatch")
    return d


def commit(d, msg):
    run("git", "-C", d, "add", "-A")
    run("git", "-C", d, "-c", "user.name=control", "-c", "user.email=control@fixture.invalid",
        "commit", "-q", "-m", msg)
    return run("git", "-C", d, "rev-parse", "HEAD").strip()


def score(outdir, name, d, tip):
    c1 = subprocess.run([sys.executable, f"{LANE}/tools/round45-recheck-audit.py", "--repo", d, "--tip", tip,
                         "--out", f"{outdir}/{name}.c1.out"], capture_output=True, text=True)
    c2 = subprocess.run([sys.executable, f"{LANE}/tools/round45-claim-outcome-audit.py", "--repo", d, "--tip", tip,
                         "--fleet", FLEET, "--out", f"{outdir}/{name}.c2.out"], capture_output=True, text=True)
    for k, p in (("c1", c1), ("c2", c2)):
        with open(f"{outdir}/{name}.{k}.out", "a") as fh:
            fh.write(f"exit={p.returncode}\n")
        print(name, k, p.stdout.splitlines()[1 if k == "c1" else 2] if p.stdout else p.stderr.strip(),
              f"exit={p.returncode}")


def write(d, rel, data):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb" if isinstance(data, bytes) else "w") as fh:
        fh.write(data)


def c1_rows(c1, cls_file, fetch):
    rows = ["\t".join(c1.HEADER)]
    files = {}
    for key in c1.POP:
        rid = key.split(":")[0]
        kind = c1.KIND[key]
        pin_ref, new_ref = c1.REFS[key]
        if kind == "file":
            _, repo, path, pr, nr, _ = c1.FILES[key]
            safe = key.replace(":", "_")
            pc, nc = f".ufo/waves/round-45/c1/upstream/{safe}/pin", f".ufo/waves/round-45/c1/upstream/{safe}/new"
            if fetch:
                pb = urllib.request.urlopen(f"https://raw.githubusercontent.com/{repo}/{pr}/{path}").read()
                nb = urllib.request.urlopen(f"https://raw.githubusercontent.com/{repo}/{nr}/{path}").read()
            else:
                pb, nb = b"placeholder pin bytes for control\n", b"placeholder new bytes for control\n"
            files[pc], files[nc] = pb, nb
            wp = pb.decode("utf-8", "replace").strip().splitlines()[0][:80] or "placeholder pin bytes"
            wn = nb.decode("utf-8", "replace").strip().splitlines()[-1][:80] or "placeholder new bytes"
            rows.append("\t".join([key, rid, kind, pin_ref, new_ref, pc, nc, wp, wn, cls_file,
                                   "filler note filler note filler note filler note"]))
        else:
            ev = {"live": c1.LIVE_DIR, "identity": ".ufo/waves/round-45/c1/identity/S038-release.json",
                  "inventory": ".ufo/waves/round-45/c1/inventory/ls-remote-llama.cpp.txt"}[kind]
            rows.append("\t".join([key, rid, kind, pin_ref, new_ref, "-", ev, "-", "-", "holds", "filler"]))
    return "\n".join(rows) + "\n", files


def c2_scorecard(c2, sc, d, tip):
    """Strongest cheap scorecard: ask the frozen counter what it wants and write exactly that."""
    p = subprocess.run([sys.executable, f"{LANE}/tools/round45-claim-outcome-audit.py", "--repo", d, "--tip", tip,
                        "--fleet", FLEET], capture_output=True, text=True)
    want = [x.split("summary line wanted: ", 1)[1] for x in p.stdout.splitlines() if "summary line wanted: " in x]
    miss = [x.split("table missing ", 1)[1] for x in p.stdout.splitlines() if "detail: table missing " in x]
    out = []
    for x in sc.splitlines():
        if x.startswith("| calibration |"):
            x = x.rstrip().rstrip("|") + f"; {c2.LEDGER} |"
        out.append(x)
    out += ["", c2.HEADING, ""] + want + ["", "| round | claim | self | outside |", "|---|---|---|---|"]
    for m in miss:
        r, cl, s_, o = eval(m)
        out.append(f"| {r} | {cl} | {s_} | {o} |")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default=os.path.join(os.environ.get("HYAKU_SCRATCH", "/fast/scratch/hyaku"),
                                                  "kama-r45", "L1", "controls"))
    ap.add_argument("--outdir", default=f"{LANE}/.ufo/waves/round-45/controls")
    a = ap.parse_args()
    os.makedirs(a.work, exist_ok=True)
    c1 = load("c1", f"{LANE}/tools/round45-recheck-audit.py")
    c2 = load("c2", f"{LANE}/tools/round45-claim-outcome-audit.py")
    try:
        d = clone(a.work, "base")
        score(a.outdir, "base", d, BASE)

        d = clone(a.work, "junk-c1-allholds")
        led, files = c1_rows(c1, "holds", fetch=False)
        write(d, c1.LEDGER, led)
        for k, v in files.items():
            write(d, k, v)
        score(a.outdir, "junk-c1-allholds", d, commit(d, "junk-c1-allholds"))

        d = clone(a.work, "junk-c1-massdrifted")
        led, files = c1_rows(c1, "drifted", fetch=True)
        write(d, c1.LEDGER, led)
        for k, v in files.items():
            write(d, k, v)
        score(a.outdir, "junk-c1-massdrifted", d, commit(d, "junk-c1-massdrifted"))

        for name in ("junk-c2-allmet", "junk-c2-grepdraft"):
            d = clone(a.work, name)
            rows = ["\t".join(c2.HEADER)]
            for r, cl in c2.KEYS:
                for side in ("self", "outside"):
                    repo, rev, path = c2.side_spec(int(r), side)
                    if name == "junk-c2-allmet":
                        out, line = "met", "1"
                    else:
                        root = FLEET if repo == "fleet" else LANE
                        t = (c2.show(root, rev, path) or "").splitlines()
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
            write(d, c2.LEDGER, "\n".join(rows) + "\n")
            tip0 = commit(d, name + " ledger")
            sc = open(os.path.join(d, "SCORECARD.md")).read()
            write(d, "SCORECARD.md", c2_scorecard(c2, sc, d, tip0))
            score(a.outdir, name, d, commit(d, name))
    finally:
        shutil.rmtree(a.work, ignore_errors=True)


if __name__ == "__main__":
    main()
