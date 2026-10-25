#!/usr/bin/env python3
"""capability-repertoire-audit.py - the lane's capability self-assessment census.

Contract:
    - Population: every capability-shaped table in SCORECARD.md - a markdown
      table with four columns whose last header cell contains "First working
      round". The rows of such a table are the capabilities the lane declares.
    - Canonical table: the first capability-shaped table after the line that
      names it, matching "**Capabilities - canonical list as of round N**";
      the highest N wins.
    - listed    - capability names carried by the canonical table.
    - observed  - capability names carried by ANY capability-shaped table
      (the union over the whole file).
    - missing   - observed minus listed: a capability the lane demonstrated
      that its canonical repertoire table does not carry.
    - unsubstantiated - canonical rows whose evidence cell carries no
      repo-relative path token that resolves at the evaluated revision.
    - met       - missing == 0 and unsubstantiated == 0.

Output line:
    listed L observed O missing M unsubstantiated U met B

Exit codes:
    0  met True
    1  met False
    2  could not evaluate (bad revision, missing SCORECARD.md, git failure)

Read-only: it issues only ``git show`` / ``git cat-file -e`` and reads files.

Usage:
    capability-repertoire-audit.py [--repo DIR] [--tip REV] [--out FILE]
                                   [--selftest]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

SKILL_FILE = "SCORECARD.md"
PATH_RE = re.compile(
    r"(?<![\w./~:-])((?:[\w.-]+/)+[\w.-]+\.(?:md|py|json|out|txt|tsv|sh))(?![\w])"
)
CANON_RE = re.compile(r"canonical list as of round\s+(\d+)\*\*", re.IGNORECASE)
GIT_TIMEOUT = 30


def git(root: str, args: list[str]) -> tuple[int, bytes, str]:
    try:
        p = subprocess.run(["git", "-C", root, *args], capture_output=True,
                           timeout=GIT_TIMEOUT)
    except (OSError, subprocess.TimeoutExpired) as e:
        return 127, b"", str(e)
    return p.returncode, p.stdout, p.stderr.decode("utf-8", "replace").strip()


def scorecard_text(root: str, rev: str | None) -> tuple[str | None, str]:
    if rev is None:
        path = os.path.join(root, SKILL_FILE)
        try:
            return open(path, encoding="utf-8", errors="surrogateescape").read(), ""
        except OSError as e:
            return None, "cannot read %s: %s" % (path, e)
    rc, out, err = git(root, ["show", "%s:%s" % (rev, SKILL_FILE)])
    if rc != 0:
        return None, "git show %s:%s failed: %s" % (rev, SKILL_FILE, err or rc)
    return out.decode("utf-8", "surrogateescape"), ""


def cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def tables(text: str) -> list[tuple[int, list[str], list[list[str]]]]:
    """(start line, header cells, body rows) for every markdown table."""
    lines = text.split("\n")
    out = []
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].lstrip().startswith("|"):
            j = i
            block = []
            while j < n and lines[j].lstrip().startswith("|"):
                block.append(lines[j])
                j += 1
            if len(block) >= 2:
                hdr = cells(block[0])
                sep = cells(block[1])
                if sep and all(set(s) <= set(":- ") for s in sep):
                    body = [cells(l) for l in block[2:] if any(cells(l))]
                    out.append((i, hdr, body))
            i = j
            continue
        i += 1
    return out


def is_capability_table(hdr: list[str]) -> bool:
    if len(hdr) != 4:
        return False
    low = hdr[3].lower()
    return "first-working round" in low or "first working round" in low


def name_of(row: list[str]) -> str:
    return (row[0] if row else "").strip().strip("`").strip()


def evaluate(root: str, rev: str | None) -> tuple[int, dict, str]:
    text, err = scorecard_text(root, rev)
    if text is None:
        return 2, {}, err
    lines = text.split("\n")
    caps = [(start, hdr, body) for start, hdr, body in tables(text)
            if is_capability_table(hdr)]
    marks = []
    for idx, line in enumerate(lines):
        m = CANON_RE.search(line)
        if m:
            marks.append((int(m.group(1)), idx))
    if not marks:
        return 2, {}, "no canonical capabilities list marker found"

    canonical = None
    best = max(marks, key=lambda t: t[0])
    for start, hdr, body in caps:
        if start > best[1]:
            canonical = (start, hdr, body)
            break
    if canonical is None and caps:
        canonical = caps[-1]
    if canonical is None:
        return 2, {}, "no canonical capabilities list found"
    listed = set()
    unsubstantiated = 0
    for row in canonical[2]:
        nm = name_of(row)
        if nm:
            listed.add(nm)
        evidence = row[2] if len(row) > 2 else ""
        tokens = [t for t in PATH_RE.findall(evidence or "")
                  if not t.startswith(("/", "~"))]
        if not any(path_exists(root, rev, t) for t in tokens):
            unsubstantiated += 1
    observed = set()
    for _start, _hdr, body in caps:
        for row in body:
            nm = name_of(row)
            if nm:
                observed.add(nm)
    missing = sorted(observed - listed)
    met = not missing and unsubstantiated == 0
    out = {"listed": len(listed), "observed": len(observed),
           "missing": len(missing), "missing_names": missing,
           "unsubstantiated": unsubstantiated, "met": met,
           "canonical_line": canonical[0] + 1,
           "capability_tables": len(caps)}
    return (0 if met else 1), out, ""


def path_exists(root: str, rev: str | None, rel: str) -> bool:
    if rev is None:
        return os.path.exists(os.path.join(root, rel))
    rc, _, _ = git(root, ["cat-file", "-e", "%s:%s" % (rev, rel)])
    return rc == 0


def selftest() -> int:
    passed = failed = 0
    hdr = "| Capability | What it can now do | Evidence pointer | First-working round |\n|---|---|---|---|\n"
    obs = "| Name | What it can do | Demonstration | First-working round |\n|---|---|---|---|\n"
    with tempfile.TemporaryDirectory(prefix="cap-selftest-") as tmp:
        repo = os.path.join(tmp, "r")
        os.makedirs(repo)
        # arm 1: a demonstrated capability the canonical table does not carry
        body = (hdr + "| a | does a | `tools/a.py` | 1 |\n\n" + obs +
                "| a | does a | `tools/a.py` | 1 |\n"
                "| b | does b | `tools/b.py` | 2 |\n")
        open(os.path.join(repo, SKILL_FILE), "w").write(body)
        open(os.path.join(repo, "tools"), "w") if False else None
        os.makedirs(os.path.join(repo, "tools"))
        open(os.path.join(repo, "tools/a.py"), "w").write("# a\n")
        open(os.path.join(repo, "tools/b.py"), "w").write("# b\n")
        # insert the canonical marker before the canonical table
        body2 = body.replace(hdr, "**Capabilities - canonical list as of round 4**\n\n" + hdr)
        open(os.path.join(repo, SKILL_FILE), "w").write(body2)
        rc, out, err = evaluate(repo, None)
        ok = rc == 1 and out.get("missing") == 1 and out.get("met") is False
        passed += int(ok); failed += int(not ok)
        # arm 2: a name-only canonical row is unsubstantiated
        body3 = body2.replace("| a | does a | `tools/a.py` | 1 |",
                               "| a | does a | no path here | 1 |")
        body3 = body3.replace(hdr, hdr.replace("tools/a.py", "tools/a.py"))
        open(os.path.join(repo, SKILL_FILE), "w").write(body3)
        rc, out, err = evaluate(repo, None)
        ok = rc == 1 and out.get("unsubstantiated", 0) >= 1
        passed += int(ok); failed += int(not ok)
    print("CAP_SELFTEST pass=%d fail=%d" % (passed, failed))
    return 0 if failed == 0 else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--tip", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    root = os.path.abspath(args.repo)
    rc, out, err = evaluate(root, args.tip)
    if rc == 2:
        print("CAP_REPERTOIRE_ERROR %s" % err, file=sys.stderr)
        return 2
    line = ("listed %d observed %d missing %d unsubstantiated %d met %s"
            % (out["listed"], out["observed"], out["missing"],
               out["unsubstantiated"], "True" if out["met"] else "False"))
    print(line)
    if args.out:
        doc = {"schema": "kama-capability-repertoire-v1", "line": line,
               "tip": args.tip, "repo": root, **out}
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=1)
    return 0 if out["met"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
