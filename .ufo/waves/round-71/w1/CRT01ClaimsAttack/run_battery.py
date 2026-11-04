#!/usr/bin/env python3
"""C1 battery on a green fixture (fx/nocite): can the gate print failed=0 uncommitted=0
while round work is unclean, and do the freeze's four kill-rule fixtures exit 1?"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r71/CRT01ClaimsAttack")
BASE = S / "fx" / "nocite"
OUT = S / "c1" / "battery"
IDENT = ["-c", "user.name=r71", "-c", "user.email=r71@example.invalid"]
VERDICT = re.compile(r"^PRE_REPORT round=(-?\d+) arms=(\d+) failed=(\d+) uncommitted=(\d+)$", re.M)


def sh(*cmd, cwd=None, timeout=900):
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True,
                          text=True, timeout=timeout)


def case(name):
    d = S / "fx" / f"case-{name}"
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(BASE, d, symlinks=True)
    top = sh("git", "-C", str(d), "rev-parse", "--show-toplevel").stdout.strip()
    assert Path(top).resolve() == d.resolve(), f"{name}: toplevel {top}"
    return d


def commit(d, msg):
    sh("git", "-C", str(d), "add", "-A")
    r = sh("git", "-C", str(d), *IDENT, "commit", "-q", "-m", msg)
    assert r.returncode == 0, f"commit failed: {r.stderr}"
    return sh("git", "-C", str(d), "rev-parse", "--short", "HEAD").stdout.strip()


def gate(d, rnd="71", tip="master", repo=None):
    p = sh(sys.executable, "tools/pre-report-gate.py", "--repo", repo or ".",
           "--round", rnd, "--tip", tip, cwd=d)
    m = VERDICT.search(p.stdout)
    arms = [ln for ln in p.stdout.splitlines() if ln.startswith("PRE_REPORT_ARM round-clean")]
    clean = arms[0] if arms else "<no round-clean arm>"
    return p.returncode, (m.group(0) if m else "<no verdict>"), clean, p.stdout


def show(label, d, rnd="71"):
    rc, verdict, clean, _ = gate(d, rnd)
    print(f"  {label}: exit={rc} | {verdict} | {clean}")
    return rc, verdict, clean


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    lines = []

    def rec(text):
        lines.append(text)
        print(text)

    # baseline: the green tip
    d = case("baseline")
    rec("## baseline green fixture")
    for rnd in ("71", "70", "9999", "0", "-1"):
        rc, v, c = show(f"--round {rnd}", d, rnd)
        rec(f"baseline round={rnd} exit={rc} {v} | {c}")

    # 1. one uncommitted file under the wave dir
    d = case("wave-uncommitted")
    (d / ".ufo/waves/round-71/w1/leak.md").write_text("uncommitted round artifact\n")
    rec("\n## one uncommitted file under .ufo/waves/round-71/")
    rec(f"--round 71   {show('r71', d)[1]} | {show('r71', d)[2]}")
    rec(f"--round 70   {show('r70', d, '70')[1]} | {show('r70', d, '70')[2]}")
    rec(f"--round 9999 {show('r9999', d, '9999')[1]} | {show('r9999', d, '9999')[2]}")
    rec("status: " + sh("git", "-C", str(d), "status", "--porcelain", "-uall", "--",
                        ".ufo/waves/round-71").stdout.strip())

    # 2. uncommitted round artifact outside the wave dir and outside the declared set
    d = case("outside-wave")
    p = d / "corpus/lessons/round-70.md"
    p.write_text(p.read_text(encoding="utf-8") + "\nUNCOMMITTED round-70 lesson edit\n", encoding="utf-8")
    rec("\n## uncommitted round artifact outside the wave dir (corpus/lessons/round-70.md)")
    rc, v, c = show("r71", d)
    rec(f"status: {sh('git','-C',str(d),'status','--porcelain','--','corpus/lessons/round-70.md').stdout.strip()}")
    rec(f"-> gate exit={rc} {v} | {c}")

    # 3. CRLF: committed (should be clean) vs uncommitted translation (should be DIRTY)
    d = case("crlf-committed")
    sk = d / "SKILL.md"
    sk.write_bytes(sk.read_bytes().replace(b"\n", b"\r\n"))
    head = commit(d, "fixture: SKILL.md committed with CRLF")
    rec(f"\n## committed CRLF SKILL.md (fixture commit {head})")
    rec(f"--round 71 {show('r71', d)[1]} | {show('r71', d)[2]}")
    sk.write_bytes(sk.read_bytes() + b"\r\nextra line\r\n")
    rec("## same file then modified (uncommitted CRLF translation)")
    rec(f"--round 71 {show('r71', d)[1]} | {show('r71', d)[2]}")

    # 4. git-invisible uncommitted wave files
    d = case("hidden-ignored")
    sd = d / ".ufo/waves/round-71/w1/scratch"
    sd.mkdir(parents=True)
    (sd / ".gitignore").write_text("*\n")
    (sd / "leak.out").write_text("hidden round artifact\n")
    rec("\n## uncommitted wave files hidden by a nested .gitignore '*'")
    rec(f"--round 71 {show('r71', d)[1]} | {show('r71', d)[2]}")
    rec("status: " + repr(sh("git", "-C", str(d), "status", "--porcelain", "-uall", "--",
                             ".ufo/waves/round-71").stdout))

    d = case("hidden-exclude")
    (d / ".ufo/waves/round-71/w1/leak2.md").write_text("excluded round artifact\n")
    ex = d / ".git/info/exclude"
    ex.write_text(ex.read_text() + ".ufo/waves/round-71/w1/leak2.md\n")
    rec("\n## uncommitted wave file hidden by .git/info/exclude")
    rec(f"--round 71 {show('r71', d)[1]} | {show('r71', d)[2]}")

    d = case("hidden-assume-unchanged")
    f = d / ".ufo/waves/round-71/w1-spec.json"
    sh("git", "-C", str(d), "update-index", "--assume-unchanged", ".ufo/waves/round-71/w1-spec.json")
    f.write_text(f.read_text() + "\n")
    rec("\n## committed wave file byte-changed with --assume-unchanged")
    rec(f"--round 71 {show('r71', d)[1]} | {show('r71', d)[2]}")
    rec("status: " + repr(sh("git", "-C", str(d), "status", "--porcelain", "-uall", "--",
                             ".ufo/waves/round-71").stdout))

    # 5. missing instrument
    d = case("missing-instrument")
    (d / "tools/round67-worktree-landing-check.py").unlink()
    rec("\n## missing instrument (tools/round67-worktree-landing-check.py removed)")
    rc, v, c, out = gate(d)
    arm = [ln for ln in out.splitlines() if "worktree-landing" in ln]
    rec(f"exit={rc} {v} | {arm[0] if arm else '<none>'}")

    # 6. subdirectory --repo
    d = case("subdir-repo")
    (d / ".ufo/waves/round-71/w1/leak3.md").write_text("dirty round artifact\n")
    rec("\n## --repo .ufo (subdirectory) with a dirty wave dir")
    rc, v, c, out = gate(d, repo=".ufo")
    rec(f"exit={rc} {v} | {c}")

    # 7. --tip that is not the branch tip
    d = case("tip-base")
    rec("\n## --tip f3ee44f4 (round-start base, branch tip is the fixture HEAD)")
    rc, v, c, out = gate(d, tip="f3ee44f4")
    rec(f"exit={rc} {v} | {c}")

    # 8. freeze kill rules (ii)-(iv) on the composed instruments
    d = case("kill-stale-pointer")
    sc = d / "SCORECARD.md"
    sc.write_text(sc.read_text(encoding="utf-8").replace(
        "latest outside closure `corpus/lessons/round-70-verifier-spotcheck.md`",
        "latest outside closure `corpus/lessons/round-69-verifier-spotcheck.md`", 1), encoding="utf-8")
    commit(d, "fixture: stale newest-closure pointer")
    rc, v, c, out = gate(d)
    arm2 = [ln for ln in out.splitlines() if ln.startswith("PRE_REPORT_ARM newest-closure")]
    rec(f"\n## kill rule (ii) stale newest-closure pointer: exit={rc} {v} | {arm2[0] if arm2 else ''}")

    d = case("kill-missing-path")
    (d / "PROVINCE.md").unlink()
    rc, v, c, out = gate(d)
    arm4 = [ln for ln in out.splitlines() if ln.startswith("PRE_REPORT_ARM worktree-landing")]
    rec(f"\n## kill rule (iii) missing declared path: exit={rc} {v} | {arm4[0] if arm4 else ''}")

    d = case("kill-dirty-path")
    sc = d / "SCORECARD.md"
    sc.write_text(sc.read_text(encoding="utf-8") + "\ndirty trailing line\n", encoding="utf-8")
    rc, v, c, out = gate(d)
    arm4 = [ln for ln in out.splitlines() if ln.startswith("PRE_REPORT_ARM worktree-landing")]
    rec(f"\n## kill rule (iv) dirty declared path: exit={rc} {v} | {arm4[0] if arm4 else ''}")

    (OUT / "c1_battery.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
