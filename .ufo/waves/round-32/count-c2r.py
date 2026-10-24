#!/usr/bin/env python3
"""Round-32 C2r counter (calibration): round-qualified, uniqueness-preconditioned
correction keys over the round-31 claim-row-evidence census.

Repairs the frozen round-31 counter (`.ufo/waves/round-31/count-c2.py`, sha256
`2d06f38d5a686b4d7a316c8db67256ff862fa6e922c1603c156341ff9a33c6fe`):
its correction key `(row, class)` is non-injective -- three claim rows of
rounds 11-13 all carry the Claim cell `C1`, so one collapsed correction
silently resolves three dispositions. This counter keys corrections by
`(round, row, class)`, where `round` is the round of the problem row's
`## Round N` section. Declared uniqueness precondition: at most one
correction per qualified key; every duplicate is a false correction.

Correction id format: `CR<F>:<N>:<text>:<class>` where `F` is the correcting
round and `N` is the corrected claim row's round (`RE_CID`). A correction
whose id carries no round, or whose row text matches problem rows of more
than one round, keys to round None and can never match: it is false.

Correction tables are read from every heading matching
`## Round <digits> -- claim-row evidence corrections` from the first such
heading to EOF, so later rounds append their own correction tables instead
of editing the round-31 table.

Population, problem classes (p1 no-revision / p2 no-evidence-path /
p3 counter-absent|digest-mismatch), base prefix `append_only`, and the
`met` formula are byte-for-byte the frozen counter's; only the correction
key and the heading match change. Predicate (frozen in
`.ufo/waves/round-32/preregistration.json`): met iff
rows >= 28 and unresolved == 0 and false_corrections == 0 and append_only.

Usage: count-c2r.py --repo GITDIR --tip REV [--out receipt.json] [--list]
Exit: 0 evaluated (whatever met), 2 could not evaluate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

BASE = "07794a4d30a54a60ebdff50ac76d12c6df40a0f1"
GIT = "/usr/bin/git"
EXT = r"(?:md|py|sh|json|jsonl|tsv|txt|out|conf|cpp|hpp|h|yml|yaml|toml|err|log|gguf|so)"
RE_HEX = re.compile(r"(?<![0-9a-zA-Z])([0-9a-f]{7,40})(?![0-9a-zA-Z])")
RE_PATH = re.compile(r"(?<![\w./~:-])((?:[\w.-]+/)*[\w.-]+\." + EXT + r")(?![\w])")
RE_DIGEST = re.compile(r"((?:[\w.-]+/)*[\w.-]+\." + EXT + r")[^|]{0,80}?\b(sha256|md5)\b"
                       r"[^|]{0,40}?`?([0-9a-f]{32}|[0-9a-f]{64})`?")
RE_SECTION = re.compile(r"^## Round (\d+)\b")
RE_CORR_HEAD = re.compile(r"^## Round (\d+) — claim-row evidence corrections")
RE_CID = re.compile(r"^CR\d+:(\d+):")
CORR_HEADER = ["id", "row", "class", "observed"]
LANE_ROOT_FILES = ("SKILL.md", "SCORECARD.md", "SHONEN.md", "LOG.md", "MISSION.md",
                   "PROVINCE.md", "README.md", "AGENTS.md", "MINT.md")


def git(repo, *args, check=True):
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR")}
    p = subprocess.run([GIT, "-C", repo, *args], capture_output=True, env=env)
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.decode('utf-8', 'replace')[:300]}")
    return p


class Repo:
    def __init__(self, path):
        self.path = path
        self._blobs = {}
        self._anc = {}

    def blob(self, rev, path):
        key = (rev, path)
        if key not in self._blobs:
            p = git(self.path, "cat-file", "blob", f"{rev}:{path}", check=False)
            self._blobs[key] = p.stdout if p.returncode == 0 else None
        return self._blobs[key]

    def commit(self, token):
        p = git(self.path, "rev-parse", "--verify", "--quiet", f"{token}^{{commit}}", check=False)
        out = p.stdout.decode("ascii", "replace").strip()
        return out or None

    def ancestor(self, a, w):
        key = (a, w)
        if key not in self._anc:
            p = git(self.path, "merge-base", "--is-ancestor", a, w, check=False)
            self._anc[key] = p.returncode == 0
        return self._anc[key]


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_tables(lines):
    """Yield (start_index, heading_text, header_cells, [(line_index, cells)])."""
    heading = ""
    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i]
        if ln.startswith("## "):
            heading = ln.strip()
        if ln.lstrip().startswith("|"):
            j = i
            block = []
            while j < n and lines[j].lstrip().startswith("|"):
                block.append((j, lines[j]))
                j += 1
            if len(block) >= 2:
                hdr = cells(block[0][1])
                sep = cells(block[1][1])
                if all(set(s) <= set(":- ") for s in sep):
                    rows = [(idx, cells(l)) for idx, l in block[2:]]
                    yield i, heading, hdr, rows
            i = j
            continue
        i += 1


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--out")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    tip = Repo(a.repo).commit(a.tip)
    if not tip:
        print(f"cannot evaluate: tip {a.tip!r} does not resolve", file=sys.stderr)
        return 2
    repo = Repo(a.repo)
    raw = repo.blob(tip, "SCORECARD.md")
    if raw is None:
        print("cannot evaluate: no SCORECARD.md at tip", file=sys.stderr)
        return 2
    text = raw.decode("utf-8", errors="replace")
    lines = text.split("\n")
    base_raw = repo.blob(BASE, "SCORECARD.md")
    append_only = base_raw is not None and raw.startswith(base_raw)

    # Split off the appended correction sections (round-31 table and any later
    # round-qualified tables appended under their own headings).
    corr_start = None
    for idx, ln in enumerate(lines):
        if RE_CORR_HEAD.match(ln):
            corr_start = idx
            break
    main_lines = lines if corr_start is None else lines[:corr_start]
    corr_lines = [] if corr_start is None else lines[corr_start:]

    problems = []      # list of dicts
    rows_checked = 0
    exempt = []
    for start, heading, hdr, rows in parse_tables(main_lines):
        if not hdr or hdr[0].strip().lower() != "claim":
            continue
        m = RE_SECTION.match(heading)
        rnd = m.group(1) if m else None
        hdr_l = [c.lower() for c in hdr]
        for li, cs in rows:
            if not cs or not cs[0].strip():
                continue
            r = dict(zip(hdr_l, cs))
            rid = cs[0].strip()
            row_text = " | ".join(cs)
            rows_checked += 1
            cmd = r.get("counting command", "") or r.get("counting commands", "")
            if "(exploratory)" in rid.lower() and norm(cmd).lower().startswith("none"):
                exempt.append(rid)
                continue
            rev = None
            pin_text = r.get("measured commit", "") or row_text
            for tok in RE_HEX.findall(pin_text) + RE_HEX.findall(row_text):
                c = repo.commit(tok)
                if c and repo.ancestor(c, tip):
                    rev = c
                    break
            if rev is None:
                problems.append({"row": rid, "line": li + 1, "round": rnd, "class": "p1",
                                 "observed": "p1:no-revision"})
                continue

            def resolve(tok, where):
                cands = [tok]
                if rnd:
                    cands.append(f".ufo/waves/round-{rnd}/{tok}")
                for cand in cands:
                    if repo.blob(where, cand) is not None:
                        return cand
                return None

            paths = [t for t in RE_PATH.findall(row_text)
                     if not (t.startswith("../") or t.startswith("/"))]
            if not any(resolve(t, tip) for t in paths):
                problems.append({"row": rid, "line": li + 1, "round": rnd, "class": "p2",
                                 "observed": "p2:no-evidence-path"})
                continue
            bad = None
            scripts = [t for t in RE_PATH.findall(cmd) if t.endswith(".py")]
            for script in scripts:
                if resolve(script, tip) is None:
                    bad = {"row": rid, "line": li + 1, "round": rnd, "class": "p3",
                           "observed": f"p3:counter-absent:{script}"}
                    break
            if bad is None:
                for pth, algo, dig in RE_DIGEST.findall(row_text):
                    res = resolve(pth, rev)
                    if res is None:
                        continue
                    blob = repo.blob(rev, res)
                    actual = hashlib.sha256(blob).hexdigest() if algo == "sha256" \
                        else hashlib.md5(blob).hexdigest()
                    if not actual.startswith(dig) and not dig.startswith(actual[:len(dig)]):
                        bad = {"row": rid, "line": li + 1, "round": rnd, "class": "p3",
                               "observed": f"p3:digest-mismatch:{res}={actual}"}
                        break
            if bad:
                problems.append(bad)

    # Parse corrections from every round-qualified correction heading to EOF.
    corrections = []
    for start, heading, hdr, rows in parse_tables(corr_lines):
        if not RE_CORR_HEAD.match(heading):
            continue
        if [h.strip().lower() for h in hdr] != CORR_HEADER:
            print(f"cannot evaluate: correction table header {hdr!r} != {CORR_HEADER!r}",
                  file=sys.stderr)
            return 2
        for li, cs in rows:
            if len(cs) != 4:
                corrections.append({"id": cs[0] if cs else "", "row": "", "class": "",
                                    "observed": "", "ok": False})
                continue
            corrections.append({"id": cs[0], "row": cs[1], "class": cs[2].strip(),
                                "observed": cs[3].strip(), "ok": None})

    def corr_round(c):
        m = RE_CID.match(c["id"])
        if m:
            return m.group(1)
        hits = {p["round"] for p in problems if p["row"] == c["row"].strip()}
        return hits.pop() if len(hits) == 1 else None

    # Round-qualified key with declared uniqueness precondition.
    by_key = {}
    for c in corrections:
        key = (corr_round(c), c["row"].strip(), c["class"])
        by_key.setdefault(key, []).append(c)
    false_corrections = 0
    valid_map = {}
    problem_by_key = {(p["round"], p["row"], p["class"]): p for p in problems}
    for c in corrections:
        key = (corr_round(c), c["row"].strip(), c["class"])
        p = problem_by_key.get(key)
        ok = (p is not None and len(by_key[key]) == 1
              and c["observed"] == p["observed"]
              and re.match(r"^CR\d+:", c["id"]) is not None)
        c["ok"] = ok
        c["key"] = "|".join("" if k is None else str(k) for k in key)
        if ok:
            valid_map[key] = c
        else:
            false_corrections += 1
    unresolved = [p for p in problems
                  if (p["round"], p["row"], p["class"]) not in valid_map]
    valid = len(valid_map)
    met = (rows_checked >= 28 and not unresolved and false_corrections == 0 and append_only)

    summary = (f"rows {rows_checked} base_mismatched {len(problems)} exempt {len(exempt)} "
               f"valid_corrections {valid} false_corrections {false_corrections} "
               f"unresolved {len(unresolved)} append_only {append_only} met {met} tip {tip[:12]}")
    print(summary)
    if a.list:
        for p in problems:
            print(f"  {p['row']}: {p['class']} round {p['round']} line {p['line']} {p['observed']}")
        for c in corrections:
            print(f"  corr {c['id']} key=({c['key']}) ok={c['ok']}")
    if a.out:
        with open(a.out, "w") as fh:
            json.dump({"summary": summary, "tip": tip, "base": BASE,
                       "rows": rows_checked, "exempt": exempt,
                       "problems": problems, "corrections": corrections,
                       "valid_corrections": valid, "false_corrections": false_corrections,
                       "unresolved": [p["row"] for p in unresolved],
                       "append_only": append_only, "met": met, "list": a.list}, fh, indent=1)
            fh.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
