#!/usr/bin/env python3
"""Re-verify the round-20 landed-omitted rows in registry/report-landing-errata.tsv.

Read-only: git plumbing under --no-optional-locks; writes nothing. Exit 0 only when
every check passes; 1 when any commit fact or evidence claim fails.
"""
import re
import subprocess
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
FLEET = Path("/home/vgpnk/Projects/shokunin")
REL = ".ufo/reports/round-20/kama.md"
TIP = "7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d"    # round-20 final pushed lane HEAD
DRAFT = "a29bb84abbb8b4d328f5970a89e448330a3a42ac"  # round-21 draft under review
ABBREV = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{7,40}(?![0-9A-Za-z])")


def git(repo, *args):
    p = subprocess.run(["git", "-C", str(repo), "--no-optional-locks", *args],
                       capture_output=True, text=True)
    return p.returncode, p.stdout


def section(text, prefix):
    m = re.search(r"^" + re.escape(prefix) + r"[^\n]*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1) if m else ""


def longest_shared(h, text):
    for k in range(40, 5, -1):
        if any(h[i:i + k] in text for i in range(41 - k)):
            return k
    return 0


def main():
    ok = True
    tsv = (LANE / "registry/report-landing-errata.tsv").read_text(encoding="utf-8")
    rows = [ln.split("\t") for ln in tsv.splitlines() if ln and not ln.startswith("#")]
    lo = [r for r in rows if r[0] == "20" and r[1] == "landed-omitted"]
    ok &= len(lo) == 4
    print(f"ledger round-20 landed-omitted rows: {len(lo)} (expect 4)")

    rc, out = git(FLEET, "log", "--diff-filter=A", "--format=%H %ct", "--", REL)
    add_sha, add_ct = out.split()[0], int(out.split()[1])
    ok &= rc == 0 and add_sha.startswith("04eb5d2")
    print(f"first fleet commit adding {REL}: {add_sha[:7]} ct={add_ct}")

    text = (FLEET / REL).read_text(encoding="utf-8")
    lines = text.splitlines()
    landed = section(text, "## Landed changes")
    measured = section(text, "## Before")
    cited = set(ABBREV.findall(landed))

    for r in lo:
        token, correction, evidence = r[2], r[3], r[4]
        rc, out = git(LANE, "show", "-s", "--format=%H%x1f%an%x1f%cn%x1f%ct%x1f%s", token)
        if rc != 0:
            print(f"FAIL {token[:7]} commit not found")
            ok = False
            continue
        sha, author, committer, ct, subject = out.strip().split("\x1f", 4)
        _, kind = git(LANE, "cat-file", "-t", token)
        checks = {
            "object is a commit": kind.strip() == "commit",
            "author kama-shokunin": author == "kama-shokunin",
            "committer kama-shokunin": committer == "kama-shokunin",
            "subject starts round-20:": subject.startswith("round-20:"),
            "committed no later than first fleet commit": int(ct) <= add_ct,
            "ancestor of round-20 tip": git(LANE, "merge-base", "--is-ancestor", token, TIP)[0] == 0,
            "ancestor of draft": git(LANE, "merge-base", "--is-ancestor", token, DRAFT)[0] == 0,
            "ledger token == correction": token == correction,
            "ledger evidence starts with subject": evidence.startswith(subject),
            "not cited in Landed changes (>=7-hex prefix)": not any(token.startswith(t) for t in cited),
        }
        shared = longest_shared(token, text)
        hits = [n for n, ln in enumerate(lines, 1) if token[:7] in ln]
        if "absent from the whole report" in evidence:
            checks["evidence 'absent from the whole report' (no >=6-hex shared substring)"] = shared < 6
        if "measurement table" in evidence:
            checks["evidence 'measurement table' cites it"] = token[:7] in measured
        for name, passed in checks.items():
            ok &= bool(passed)
            print(f"  {'PASS' if passed else 'FAIL'} {token[:7]} {name}")
        print(f"       report lines with {token[:7]} prefix: {hits}; longest shared substring with report: {shared} hex")
    print("RESULT: all checks pass" if ok else "RESULT: failures present")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
