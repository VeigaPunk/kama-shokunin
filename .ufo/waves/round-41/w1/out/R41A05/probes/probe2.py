#!/usr/bin/env python3
"""R41A05 probe controls v2: self-contained minimal fixtures.

For each C1-counter survivor mutant, build the control shape the committed
control set lacks, as a tiny standalone git fixture (fixture identity used only
inside the fixture), and score the probe revision with the pristine counter and
the mutant. The probe kills the mutant iff pristine and mutant disagree on met.
Every probe variant is applied to a fresh copy of the GOOD table (no chaining).

  P-M2-score-corrupt   calibration score 7 -> 8, evidence untouched
                       (good evidence, wrong score) -> kills m2-drop-score
  P-M3-substring-cite  run citation `RESULT pass=30`, a strict substring of the
                       real stdout line -> kills m3-run-substring
  P-M4-brace-cite      coverage row cites `docs/{coverage,adjacency}.md`, both
                       files exist -> kills m4-no-brace-expand (false reject)
  P-M6-missing-axis    adjacency row removed -> kills m6-ignore-missing-axes
"""
import hashlib, os, subprocess, sys, tempfile

WORK = "/home/vgpnk/R41A05/probe-work"
OUT = "/home/vgpnk/R41A05/probe-receipts"
PRISTINE = "/home/vgpnk/R41A05/mut/pristine.py"
MUT = {
    "m2-drop-score": "/home/vgpnk/R41A05/mut/m2-drop-score.py",
    "m3-run-substring": "/home/vgpnk/R41A05/mut/m3-run-substring.py",
    "m4-no-brace-expand": "/home/vgpnk/R41A05/mut/m4-no-brace-expand.py",
    "m6-ignore-missing-axes": "/home/vgpnk/R41A05/mut/m6-ignore-missing-axes.py",
}

def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

def nlines(p):
    return open(p, "rb").read().count(b"\n")

def build_fixture():
    D = tempfile.mkdtemp(prefix="r41a05-fx-", dir=WORK)
    def g(*a, ck=True):
        return subprocess.run(["git", "-C", D, *a], check=ck,
                              capture_output=True, text=True)
    subprocess.run(["git", "init", "-q", D], check=True)
    assert g("rev-parse", "--show-toplevel").stdout.strip() == os.path.realpath(D), \
        "fixture toplevel mismatch"
    ID = ["-c", "user.name=r41a05-probe", "-c", "user.email=r41a05-probe@fixture.invalid"]
    def write(p, s):
        fp = os.path.join(D, p)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        open(fp, "w").write(s)
    write("tools/probe.sh", "#!/bin/sh\necho probe-ok\n")
    write("tools/snap.sh", "#!/bin/sh\necho snap-ok\n")
    write("tools/selftest.sh", "#!/bin/sh\necho 'RESULT pass=30 fail=0'\n")
    write("docs/depth.md", "depth rule\n")
    write("docs/coverage.md", "coverage row\n")
    write("docs/adjacency.md", "adjacency row\n")
    h_cov, n_cov = md5(D + "/docs/coverage.md"), nlines(D + "/docs/coverage.md")
    good_table = (
        "| Axis | Before → After | Evidence pointer (re-derivable at the measured commit) | Last change |\n"
        "|---|---|---|---|\n"
        f"| **operability** | **8** | `tools/probe.sh` md5 `{md5(D + '/tools/probe.sh')}` ({nlines(D + '/tools/probe.sh')} lines) | round 41 |\n"
        f"| **freshness** | **8** | `tools/snap.sh` md5 `{md5(D + '/tools/snap.sh')}` ({nlines(D + '/tools/snap.sh')} lines) | round 41 |\n"
        f"| depth | **7** | `docs/depth.md` md5 `{md5(D + '/docs/depth.md')}` ({nlines(D + '/docs/depth.md')} lines) | round 41 |\n"
        f"| coverage | **9** | `docs/coverage.md` md5 `{h_cov}` ({n_cov} lines) | round 41 |\n"
        "| calibration | **7** | run `bash tools/selftest.sh` → `RESULT pass=30 fail=0` | round 41 |\n"
        f"| adjacency | **7** | `docs/adjacency.md` md5 `{md5(D + '/docs/adjacency.md')}` ({nlines(D + '/docs/adjacency.md')} lines) | round 41 |\n")
    write("SCORECARD.md", "# kama\n\n## Axes\n\n" + good_table + "\n## Next\n\nProbe fixture body.\n")
    g("add", "-A")
    g(*ID, "commit", "-q", "-m", "good table")
    return D, g, ID, write, good_table, h_cov, n_cov

def score(D, rev, tag, ctr, name):
    os.makedirs(OUT, exist_ok=True)
    p = subprocess.run([sys.executable, ctr, "--repo", D, "--tip", rev,
                        "--out", os.path.join(OUT, f"{name}.{tag}.out")],
                       capture_output=True, text=True)
    first = p.stdout.splitlines()[1] if p.stdout else p.stderr.strip()
    return p.returncode, first

def main():
    os.makedirs(WORK, exist_ok=True)
    D, g, ID, write, good_table, h_cov, n_cov = build_fixture()
    GOOD = g("rev-parse", "HEAD").stdout.strip()
    rc, v = score(D, GOOD, "pristine", PRISTINE, "GOOD")
    print(f"FIXTURE sanity (good table, pristine): exit={rc} | {v}")
    assert "met=True" in v, "fixture sanity failed: good table must be met=True"

    probes = [
        ("P-M2-score-corrupt", "m2-drop-score",
         lambda t: t.replace("| calibration | **7** |", "| calibration | **8** |")),
        ("P-M3-substring-cite", "m3-run-substring",
         lambda t: t.replace("→ `RESULT pass=30 fail=0`", "→ `RESULT pass=30`")),
        ("P-M4-brace-cite", "m4-no-brace-expand",
         lambda t: t.replace(f"`docs/coverage.md` md5 `{h_cov}` ({n_cov} lines)",
                             f"`docs/coverage.md` md5 `{h_cov}` ({n_cov} lines); `docs/{{coverage,adjacency}}.md`")),
        ("P-M6-missing-axis", "m6-ignore-missing-axes",
         lambda t: "\n".join(l for l in t.split("\n") if not l.startswith("| adjacency"))),
    ]
    for name, mut, fn in probes:
        write("SCORECARD.md",
              "# kama\n\n## Axes\n\n" + fn(good_table) + "\n## Next\n\nProbe fixture body.\n")
        g("add", "-A")
        g(*ID, "commit", "-q", "-m", name)
        rev = g("rev-parse", "HEAD").stdout.strip()
        rc0, v0 = score(D, rev, "pristine", PRISTINE, name)
        rc1, v1 = score(D, rev, "mutant", MUT[mut], name)
        pm = "met=True" in v0
        mm = "met=True" in v1
        print(f"PROBE {name} vs {mut}")
        print(f"  pristine exit={rc0} | {v0}")
        print(f"  mutant   exit={rc1} | {v1}")
        print(f"  -> {'KILLS ' + mut if pm != mm else 'does NOT kill ' + mut}")
    print("fixture:", D)

if __name__ == "__main__":
    main()
