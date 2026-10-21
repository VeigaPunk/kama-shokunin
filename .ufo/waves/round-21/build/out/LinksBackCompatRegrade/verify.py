#!/usr/bin/env python3
"""Round-21 LinksBackCompatRegrade: independent checks over regrade.py outputs.

Read-only over the files in this directory (run-base.log, run-work.log,
regrade.tsv, regrade-mention-only.tsv). Checks:
  1. both arms cover the same invocations (no duplicates, same keys);
  2. exit codes are identical per regrade invocation (schema + mention-only);
  3. raw output differences are listed; differences that remain after masking
     traceback line numbers and traceback elided-line counts must be empty;
  4. each TSV verdict column equals the first stdout line (else first stderr
     line) of the matching block in that arm's log.
Writes verify.txt. Exit 0 when checks 1-4 hold, else 1.
"""
import os
import re
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
MASKS = ((r"line \d+, in", "line N, in"),
         (r"\.\.\.<\d+ lines>\.\.\.", "...<K lines>..."))


def load(arm):
    with open(os.path.join(OUT, f"run-{arm}.log"), encoding="utf-8") as fh:
        text = fh.read()
    blocks = {}
    for chunk in re.split(r"(?m)^(?=### )", text):
        if not chunk.startswith("### "):
            continue
        header, _, body = chunk.partition("\n")
        m = re.match(r"^### \[(base|work)\] (.*)$", header)
        if not m or m.group(1) != arm:
            raise SystemExit(f"FATAL: unexpected header in run-{arm}.log: {header!r}")
        if m.group(2) in blocks:
            raise SystemExit(f"FATAL: duplicate invocation {m.group(2)!r} in run-{arm}.log")
        blocks[m.group(2)] = body
    return blocks


def exit_of(body):
    m = re.search(r"(?m)^exit=(\d+)$", body)
    if not m:
        raise SystemExit("FATAL: block without an exit= line")
    return int(m.group(1))


def verdict_of(body):
    head, _, rest = body.partition("--- stdout ---\n")
    out, _, err = rest.partition("--- stderr ---\n")
    text = out if out.strip() else err
    lines = text.splitlines()
    return (lines[0] if lines else "<no output>").replace("\t", " ").strip()


def masked(body):
    for pattern, repl in MASKS:
        body = re.sub(pattern, repl, body)
    return body


def read_tsv(name):
    with open(os.path.join(OUT, name), encoding="utf-8") as fh:
        rows = [line.rstrip("\n").split("\t") for line in fh]
    if rows[0] != ["path", "base_verdict_line", "work_verdict_line"]:
        raise SystemExit(f"FATAL: unexpected header in {name}: {rows[0]}")
    return rows[1:]


def main():
    base, work = load("base"), load("work")
    report, ok = [], True
    if base.keys() != work.keys():
        ok = False
        report.append("FAIL 1: invocation key sets differ between arms")
    else:
        report.append(f"1 keys: {len(base)} invocations per arm, identical key sets")

    regrade = [k for k in base if k.startswith("[schema] ") or k.startswith("[mention-only] ")]
    probes = sorted(k for k in base if k not in regrade)
    exit_diff = [k for k in regrade if exit_of(base[k]) != exit_of(work[k])]
    raw_diff = [k for k in regrade if base[k] != work[k]]
    masked_diff = [k for k in regrade if masked(base[k]) != masked(work[k])]
    report.append(f"regrade invocations per arm: {len(regrade)}; probe invocations: {probes}")
    report.append(f"2 exit-code differences: {len(exit_diff)} {exit_diff}")
    if exit_diff:
        ok = False
    report.append(f"3 raw output differences: {len(raw_diff)}")
    for k in raw_diff:
        report.append(f"    raw: {k}")
    report.append(f"3 output differences after masking traceback line numbers and "
                  f"elided-line counts: {len(masked_diff)} {masked_diff}")
    if masked_diff:
        ok = False

    for name, scope in (("regrade.tsv", "schema"), ("regrade-mention-only.tsv", "mention-only")):
        rows = read_tsv(name)
        expected = sum(1 for k in regrade if k.startswith(f"[{scope}] "))
        mismatches = []
        for path, base_v, work_v in rows:
            key = f"[{scope}] {path}"
            if key not in base:
                mismatches.append(f"no block for {path}")
            elif verdict_of(base[key]) != base_v or verdict_of(work[key]) != work_v:
                mismatches.append(path)
        report.append(f"4 {name}: rows={len(rows)} expected={expected} "
                      f"mismatches={len(mismatches)} {mismatches}")
        if mismatches or len(rows) != expected:
            ok = False

    report.append("RESULT: " + ("PASS" if ok else "FAIL"))
    text = "\n".join(report) + "\n"
    with open(os.path.join(OUT, "verify.txt"), "w", encoding="utf-8") as fh:
        fh.write(text)
    sys.stdout.write(text)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
