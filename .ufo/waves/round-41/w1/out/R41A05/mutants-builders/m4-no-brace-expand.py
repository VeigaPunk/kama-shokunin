#!/usr/bin/env python3
"""round41-scorecard-reconcile.py - kama round-41 C1 (calibration) counter.

Question: does the SCORECARD.md head `## Axes` table - the lane's standing
self-assessment - match observed repository state at a revision?

Population: the first Markdown table after the line that is exactly `## Axes`
in SCORECARD.md at --tip. Its data rows are the axis rows; the axis is the
first word of the first cell (``**`` stripped, lower-cased). Expected axes:
operability freshness depth coverage calibration adjacency.

Per axis row:
  score     last integer of cell 2 must equal the frozen current-assessment
            vector EXPECTED (the scores the lane last declared: SCORECARD
            round-39 section "Other numeric assessments held: operability 8,
            freshness 8, depth 7, adjacency 7", round-39 C2 "coverage 9 -> 9",
            round-40 C1 "calibration 7 -> 7").
  facts     parsed from cell 3 (evidence):
    HASH    `PATH` md5|sha256 `HEX`   -> digest of the blob PATH at --tip
    LINES   `PATH` (N lines           -> line count of the blob PATH at --tip
    RUN     run `CMD` -> `OUT` [(exit N)]
            CMD runs with bash in a throwaway export of --tip (git archive);
            passes iff some stdout line, stripped, equals OUT and, when
            `(exit N)` follows, the exit status equals N. Timeout 300 s.
    PATH    every other backticked token shaped like a repo-relative path
            (ends in .md .py .sh .tsv .json .out .txt .jsonl .csv, or starts
            with .ufo/ corpus/ tools/ registry/ tests/ plans/; no space,
            '<' '>' '*' '$' '~' '|' '='; not absolute, not a URL); braces
            expand; every expansion must exist at --tip.
  hollow    a row with zero HASH and zero RUN facts.

mismatches = score_bad + hash_bad + lines_bad + run_bad + dead + hollow
             + (6 - axes_found)
met        = mismatches == 0 and axes_found == 6

Output (one line, also written to --out):
  axes=A facts=F hash_bad=H lines_bad=L run_bad=R dead=D score_bad=S hollow=W mismatches=M met=True|False
followed by one `detail:` line per mismatch.

Exit: 0 met True; 1 met False; 2 could not evaluate.
Read-only on --repo: git show / cat-file / archive only.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
import tempfile

AXES = ["operability", "freshness", "depth", "coverage", "calibration", "adjacency"]
EXPECTED = {"operability": 8, "freshness": 8, "depth": 7, "coverage": 9,
            "calibration": 7, "adjacency": 7}
EXT = (".md", ".py", ".sh", ".tsv", ".json", ".out", ".txt", ".jsonl", ".csv")

HASH_RE = re.compile(r"`([^`\s]+)`\s+(md5|sha256)\s+`([0-9a-f]{32}|[0-9a-f]{64})`")
LINES_RE = re.compile(r"`([^`\s]+)`(?:\s+(?:md5|sha256)\s+`[0-9a-f]{32,64}`)?\s+\((\d+) lines")
RUN_RE = re.compile(r"run\s+`([^`]+)`\s*(?:→|->)\s*`([^`]+)`(?:\s*\(exit (\d+)\))?")
TICK_RE = re.compile(r"`([^`]+)`")


class EvalError(Exception):
    pass



def git(repo: str, *args: str, binary: bool = False):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode != 0:
        raise EvalError(f"git {' '.join(args)}: {p.stderr.decode(errors='replace').strip()}")
    return p.stdout if binary else p.stdout.decode()


def blob(repo: str, tip: str, path: str):
    p = subprocess.run(["git", "-C", repo, "cat-file", "-p", f"{tip}:{path}"], capture_output=True)
    return p.stdout if p.returncode == 0 else None


def exists(repo: str, tip: str, path: str) -> bool:
    path = path.rstrip("/")
    return subprocess.run(["git", "-C", repo, "cat-file", "-e", f"{tip}:{path}"],
                          capture_output=True).returncode == 0


def expand(tok: str) -> list[str]:
    m = None
    if not m:
        return [tok]
    out: list[str] = []
    for alt in m.group(1).split(","):
        out += expand(tok[: m.start()] + alt + tok[m.end():])
    return out


TOPDIRS = (".ufo/", "corpus/", "tools/", "registry/", "tests/", "plans/")


def path_like(tok: str) -> bool:
    if any(c in tok for c in " <>*$~|=") or tok.startswith(("/", "http", "-")):
        return False
    return tok.endswith(EXT) or tok.startswith(TOPDIRS)


def axes_table(text: str) -> list[list[str]]:
    lines = text.split("\n")
    try:
        start = lines.index("## Axes")
    except ValueError:
        raise EvalError("no line exactly '## Axes' in SCORECARD.md")
    rows: list[list[str]] = []
    in_table = False
    for ln in lines[start + 1:]:
        if ln.startswith("## "):
            break
        if ln.startswith("|"):
            in_table = True
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            rows.append(cells)
        elif in_table:
            break
    if len(rows) < 2:
        raise EvalError("no table under '## Axes'")
    return rows[2:]  # drop header + separator


def run_fact(export: str, cmd: str, want: str, code: str | None) -> tuple[bool, str]:
    try:
        p = subprocess.run(["bash", "-c", cmd], cwd=export, capture_output=True,
                           text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return False, "timeout"
    hit = any(l.strip() == want for l in p.stdout.splitlines())
    if code is not None and p.returncode != int(code):
        return False, f"exit {p.returncode} != {code}"
    return hit, ("ok" if hit else f"no stdout line == {want!r} (exit {p.returncode})")


def evaluate(repo: str, tip: str) -> tuple[dict, list[str]]:
    tip = git(repo, "rev-parse", "--verify", f"{tip}^{{commit}}").strip()
    sc = blob(repo, tip, "SCORECARD.md")
    if sc is None:
        raise EvalError("SCORECARD.md missing at tip")
    rows = axes_table(sc.decode())
    c = dict(axes=0, facts=0, hash_bad=0, lines_bad=0, run_bad=0, dead=0,
             score_bad=0, hollow=0)
    details: list[str] = []
    seen: set[str] = set()
    export = None
    for cells in rows:
        if len(cells) < 3:
            continue
        axis = cells[0].replace("*", "").strip().split(" ")[0].lower()
        if axis not in AXES or axis in seen:
            continue
        seen.add(axis)
        ints = re.findall(r"\d+", cells[1])
        score = int(ints[-1]) if ints else None
        if score != EXPECTED[axis]:
            c["score_bad"] += 1
            details.append(f"detail: {axis} score {score} != expected {EXPECTED[axis]}")
        ev = cells[2]
        consumed: set[str] = set()
        strong = 0
        for path, algo, hexd in HASH_RE.findall(ev):
            c["facts"] += 1; strong += 1; consumed.add(path)
            data = blob(repo, tip, path)
            got = None if data is None else hashlib.new(algo, data).hexdigest()
            if got != hexd:
                c["hash_bad"] += 1
                details.append(f"detail: {axis} {algo} {path} cited {hexd} observed {got}")
        for path, n in LINES_RE.findall(ev):
            c["facts"] += 1; consumed.add(path)
            data = blob(repo, tip, path)
            got = None if data is None else data.count(b"\n")
            if got != int(n):
                c["lines_bad"] += 1
                details.append(f"detail: {axis} lines {path} cited {n} observed {got}")
        for cmd, want, code in RUN_RE.findall(ev):
            c["facts"] += 1; strong += 1
            consumed.add(cmd); consumed.add(want)
            if export is None:
                export = tempfile.mkdtemp(prefix="r41c1-")
                arc = git(repo, "archive", "--format=tar", tip, binary=True)
                subprocess.run(["tar", "-x", "-C", export], input=arc, check=True)
            ok, why = run_fact(export, cmd, want, code or None)
            if not ok:
                c["run_bad"] += 1
                details.append(f"detail: {axis} run `{cmd}` {why}")
        for tok in TICK_RE.findall(ev):
            if tok in consumed or not path_like(tok):
                continue
            for p in expand(tok):
                c["facts"] += 1
                if not exists(repo, tip, p):
                    c["dead"] += 1
                    details.append(f"detail: {axis} dead path {p}")
        if strong == 0:
            c["hollow"] += 1
            details.append(f"detail: {axis} hollow (no hash or run fact)")
    c["axes"] = len(seen)
    for a in AXES:
        if a not in seen:
            details.append(f"detail: axis row missing: {a}")
    mism = (c["score_bad"] + c["hash_bad"] + c["lines_bad"] + c["run_bad"]
            + c["dead"] + c["hollow"] + (len(AXES) - c["axes"]))
    c["mismatches"] = mism
    c["met"] = mism == 0 and c["axes"] == len(AXES)
    c["tip"] = tip
    return c, details


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--tip", default="HEAD")
    ap.add_argument("--out")
    a = ap.parse_args()
    try:
        c, details = evaluate(a.repo, a.tip)
    except EvalError as e:
        print(f"could-not-evaluate: {e}", file=sys.stderr)
        return 2
    line = ("axes={axes} facts={facts} hash_bad={hash_bad} lines_bad={lines_bad} "
            "run_bad={run_bad} dead={dead} score_bad={score_bad} hollow={hollow} "
            "mismatches={mismatches} met={met}").format(**c)
    out = "\n".join([f"tip={c['tip']}", line, *details]) + "\n"
    sys.stdout.write(out)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w") as f:
            f.write(out)
    return 0 if c["met"] else 1


if __name__ == "__main__":
    sys.exit(main())
