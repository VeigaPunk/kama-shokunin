#!/usr/bin/env python3
"""attack-reason-rows.py - CR02ClaimC2 attack harness for round90-reason-rows.py.

Builds a scratch git fixture whose SKILL.md is the real M2 SKILL.md mutated one case at a time and
whose receipt is rebuilt to a two-line stub probe, then runs the frozen counter against each commit.
No hardcoded /tmp; every path comes from arguments. Writes only inside --work.

Usage: python3 attack-reason-rows.py --lane <lane-repo> --work <scratch> --out <receipt-file> [--counter <py>]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

HEADING = "## Probe reason codes"
M2 = "2ee0b55f4d3fd0cb3157d26b03280c1d21e27b2d"
RECEIPT = ".ufo/waves/round-90/measured/reason-cells.jsonl"
PROBE = "tools/kama-probe.sh"
SKILL = "SKILL.md"
STUB = "#!/bin/sh\nexit 0\n"


def sh(args, **kw):
    return subprocess.run(args, capture_output=True, text=True, **kw)


def git(repo, *a, **kw):
    return sh(["git", "-C", repo, *a], **kw)


def section_bounds(lines):
    start = next(i for i, l in enumerate(lines) if l.rstrip() == HEADING)
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return start, end


def table_ix(sec):
    return [i for i, l in enumerate(sec) if l.startswith("|")]


def write_commit(repo, files, msg):
    for rel, text in files.items():
        p = os.path.join(repo, rel)
        os.makedirs(os.path.dirname(p) or repo, exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(text)
    git(repo, "add", "-A")
    r = git(repo, "-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
            "commit", "-q", "--allow-empty", "-m", msg)
    if r.returncode != 0:
        raise SystemExit(f"commit failed: {r.stdout}{r.stderr}")
    return git(repo, "rev-parse", "HEAD").stdout.strip()


def receipt_lines(entries, sha):
    out = []
    for cell, reason, verdict in entries:
        out.append(json.dumps({"cell": cell, "exit": 0, "probe_sha256": sha,
                               "reason": reason, "verdict": verdict}, sort_keys=True))
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--counter", default=None)
    ap.add_argument("--rev", default=M2)
    a = ap.parse_args()
    counter = a.counter or os.path.join(a.lane, "tools", "round90-reason-rows.py")
    os.makedirs(a.work, exist_ok=True)

    m2 = git(a.lane, "rev-parse", "--verify", a.rev + "^{commit}").stdout.strip()
    skill = git(a.lane, "show", f"{m2}:{SKILL}").stdout
    real_rec = git(a.lane, "show", f"{m2}:{RECEIPT}").stdout
    real_probe_sha = hashlib.sha256(subprocess.run(
        ["git", "-C", a.lane, "show", f"{m2}:{PROBE}"], capture_output=True).stdout).hexdigest()
    stub_sha = hashlib.sha256(STUB.encode()).hexdigest()

    entries = []
    for line in real_rec.splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        entries.append((d["cell"], d["reason"], d["verdict"]))
    entries.sort()
    assert len(entries) == 24, len(entries)

    lines = skill.split("\n")
    start, end = section_bounds(lines)
    sec = lines[start:end]
    before, after = lines[:start], lines[end:]
    tix = table_ix(sec)
    assert len(tix) == 26, len(tix)  # header + separator + 24 rows

    def rebuild(newsec, doc_crlf=False):
        out = before + newsec + after
        return ("\r\n".join(out) if doc_crlf else "\n".join(out))

    cases = []
    # A0 faithful control
    cases.append(("A0-control", rebuild(sec), receipt_lines(entries, stub_sha)))
    # A1 rows hidden in one HTML comment
    s1 = list(sec); t = table_ix(s1)
    s1.insert(t[-1] + 1, "-->"); s1.insert(t[0], "<!--")
    cases.append(("A1-html-comment", rebuild(s1), receipt_lines(entries, stub_sha)))
    # A2 setext heading
    s2 = ["Probe reason codes", "------------------"] + sec[1:]
    cases.append(("A2-setext", rebuild(s2), receipt_lines(entries, stub_sha)))
    # A3a table under a second heading after an intervening h2
    s3a = sec[:1] + ["", "Prose only, no table here.", "", "## Extra", ""] + sec[1:]
    cases.append(("A3a-second-heading", rebuild(s3a), receipt_lines(entries, stub_sha)))
    # A3b duplicate heading after the real section with a contradicting row
    s3b = sec + ["", HEADING, "", "| `router-unloaded` | `MODEL_OK` | contradicts the real table | `R-fake` |", ""]
    cases.append(("A3b-duplicate-contradiction", rebuild(s3b), receipt_lines(entries, stub_sha)))
    # A4 tab-indented rows
    s4 = [("\t" + l) if l.startswith("|") else l for l in sec]
    cases.append(("A4-tab-indent", rebuild(s4), receipt_lines(entries, stub_sha)))
    # A4b two-space-indented rows
    s4b = [("  " + l) if l.startswith("|") else l for l in sec]
    cases.append(("A4b-two-space-indent", rebuild(s4b), receipt_lines(entries, stub_sha)))
    # A5 CRLF document
    cases.append(("A5-crlf", rebuild(sec, doc_crlf=True), receipt_lines(entries, stub_sha)))
    # A6 escaped pipe in one trigger
    s6 = list(sec); hit = [i for i in table_ix(s6) if "`http-401`" in s6[i]]
    assert len(hit) == 1
    s6[hit[0]] = s6[hit[0]].replace("the model is not judged", "the model is not judged \\| key policy")
    cases.append(("A6-escaped-pipe", rebuild(s6), receipt_lines(entries, stub_sha)))
    # A7 hand-written receipt against a stub probe that cannot emit any reason
    cases.append(("A7-handwritten-receipt", rebuild(sec), receipt_lines(entries, stub_sha)))
    # A8 one foreign-sha line mixed into an otherwise valid receipt
    mixed = receipt_lines(entries, stub_sha) + json.dumps(
        {"cell": "R-matched", "exit": 0, "probe_sha256": real_probe_sha,
         "reason": "matched", "verdict": "MODEL_OK"}, sort_keys=True) + "\n"
    cases.append(("A8-mixed-stale-line", rebuild(sec), mixed))
    # A8b one non-JSON line
    cases.append(("A8b-malformed-line", rebuild(sec), receipt_lines(entries, stub_sha) + "{not json\n"))
    # A9 two backticked tokens in the reason cell
    s9 = list(sec); hit = [i for i in table_ix(s9) if s9[i].startswith("| `matched` ")]
    assert len(hit) == 1
    s9[hit[0]] = s9[hit[0]].replace("| `matched` |", "| `matched` `expected-wildcard` |", 1)
    cases.append(("A9-two-token-reason", rebuild(s9), receipt_lines(entries, stub_sha)))
    # A10 empty trigger cell
    s10 = list(sec); hit = [i for i in table_ix(s10) if s10[i].startswith("| `http-401` ")]
    assert len(hit) == 1
    s10[hit[0]] = "| `http-401` | `UNAUTHORIZED_SERVICE` |  | `R-http-401` |"
    cases.append(("A10-empty-trigger", rebuild(s10), receipt_lines(entries, stub_sha)))
    # A11 fenced block containing '## example' mid-table
    s11 = list(sec); t = table_ix(s11)
    ins = t[1] + 11
    s11[ins:ins] = ["", "```text", "## example", "```", ""]
    cases.append(("A11-fenced-h2-midtable", rebuild(s11), receipt_lines(entries, stub_sha)))
    # A12 literal heading inside a fence before the real section
    pre = ["```text", HEADING, "```", ""]
    cases.append(("A12-fenced-heading-before", rebuild(pre + sec), receipt_lines(entries, stub_sha)))
    # A14 blockquote table
    s14 = [("> " + l) if l.startswith("|") else l for l in sec]
    cases.append(("A14-blockquote", rebuild(s14), receipt_lines(entries, stub_sha)))
    # A15 valid receipt plus junk lines with the same sha
    junk = [" ".join(["junk"] * 3) for _ in range(50)]
    junk_rec = receipt_lines(entries, stub_sha) + "\n".join(
        json.dumps({"cell": f"R-junk-{i}", "exit": 0, "probe_sha256": stub_sha,
                    "reason": f"junk-{i}", "verdict": "MODEL_OK"}, sort_keys=True) for i in range(50)) + "\n"
    cases.append(("A15-junk-receipt-lines", rebuild(sec), junk_rec))
    # A13 whole table inside a fence (correct refusal control)
    s13 = list(sec); t = table_ix(s13)
    s13.insert(t[-1] + 1, "```"); s13.insert(t[0], "```text")
    cases.append(("A13-fenced-table", rebuild(s13), receipt_lines(entries, stub_sha)))

    results = []
    for name, skill_text, rec_text in cases:
        d = tempfile.mkdtemp(dir=a.work, prefix="fx-")
        r = git(d, "init", "-q")
        if r.returncode != 0:
            raise SystemExit(f"init failed {d}")
        top = git(d, "rev-parse", "--show-toplevel").stdout.strip()
        assert os.path.realpath(top) == os.path.realpath(d), (top, d)
        files = {SKILL: skill_text, PROBE: STUB, RECEIPT: rec_text}
        for rel, text in files.items():  # first write then commit
            p = os.path.join(d, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write(text)
        rev = write_commit(d, {}, name)
        rr = sh([sys.executable, counter, "--repo", d, "--rev", rev])
        last = rr.stdout.strip().splitlines()[-1] if rr.stdout.strip() else "<no stdout>"
        results.append((name, rr.returncode, last, rr.stdout, rr.stderr, rev))

    with open(a.out, "w", encoding="utf-8") as f:
        for name, rc, last, out, err, rev in results:
            f.write(f"=== {name} rev={rev} exit={rc}\n{last}\n")
            if out.strip().splitlines()[:-1]:
                f.write("-- full stdout --\n" + out.strip() + "\n")
            if err.strip():
                f.write("-- stderr --\n" + err.strip() + "\n")
            f.write("\n")
    for name, rc, last, _out, _err, _rev in results:
        print(f"{name:30s} exit={rc}  {last}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
