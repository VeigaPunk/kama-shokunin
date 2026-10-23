#!/usr/bin/env python3
"""Round-31 C2 counter (calibration): every SCORECARD claim row carries revision-keyed evidence.

Frozen predicate (the same sentence as preregistration.json C2.predicate and the summary label
`unresolved`):

  Claim met iff rows >= 28 and unresolved == 0 and false_corrections == 0 and append_only is
  True and every non-exempt claim row is either RESOLVED or has exactly one VALID correction row.

Population: every data row of every table in SCORECARD.md whose header's first cell is `Claim`
(case-insensitive), read from the measured commit only; rows inside the appended correction
section are not population rows.

Per row (id = first cell; round = nearest preceding `## Round <N>` heading):
  EXEMPT   the id marks the claim `(exploratory)` and its counting-command cell (when the table
           has one) starts with `none` -> observed `x:exploratory-exempt`; never a mismatch.
  P1       the row text names at least one hex token of 7..40 chars that resolves to a commit at
           the tip and is the tip or an ancestor of it; else `p1:no-revision` with the observed
           string `p1:no-revision`.
  P2       the row text names at least one lane path (a token with an extension, resolved (i) as
           written, (ii) beneath `.ufo/waves/round-<N>/` of the row's round, (iii) as a
           lane-root file) that exists as a blob at the TIP; else `p2:no-evidence-path`.
  P3       the counter script the row names (a `.py` path in its counting-command cell, resolved
           the same three ways) exists as a blob at the TIP; else `p3:counter-absent:<token as
           written>`. When the row also pins a full `sha256`/`md5` digest for a named path, the
           blob digest at the resolved revision must match it; a mismatch is
           `p3:digest-mismatch:<path>=<actual>`.

Corrections live only in the appended section whose heading starts with
`## Round 31 — claim-row evidence corrections`, first table header exactly
`| id | row | class | observed |`. A correction is VALID iff its `row` cell names an existing
population row id, its `class` equals the counter's recomputed failing token (p1/p2/p3), and its
`observed` equals the counter's recomputed observed string byte for byte. Any other correction is
counted in `false_corrections`. Two corrections for one row/class: the second is false.
`append_only` is True iff the tip's SCORECARD.md begins with the base commit's SCORECARD.md bytes.

Usage: count-c2.py [--repo DIR] [--tip REV] [--out FILE] [--list]
Reads committed objects only (git --no-replace-objects); never the working tree.
Exit: 0 ran (whatever the count), 2 could not evaluate (repo or tip unusable).
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
CORR_HEADING = "## Round 31 — claim-row evidence corrections"
CORR_HEADER = ["id", "row", "class", "observed"]
LANE_ROOT_FILES = ("SKILL.md", "SCORECARD.md", "SHONEN.md", "LOG.md", "MISSION.md",
                   "PROVINCE.md", "README.md", "AGENTS.md", "MINT.md")


def git(repo, *args, check=True):
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
                        "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_REPLACE_REF_BASE")}
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    p = subprocess.run([GIT, "--no-replace-objects", "-C", repo, *args],
                       capture_output=True, env=env)
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.decode(errors='replace').strip()}")
    return p


class Repo:
    def __init__(self, path):
        self.path = path
        self._blob = {}
        self._anc = {}

    def blob(self, rev, path):
        key = (rev, path)
        if key not in self._blob:
            p = git(self.path, "cat-file", "blob", f"{rev}:{path}", check=False)
            self._blob[key] = p.stdout if p.returncode == 0 else None
        return self._blob[key]

    def commit(self, token):
        p = git(self.path, "rev-parse", "--verify", "--quiet", f"{token}^{{commit}}", check=False)
        return p.stdout.decode().strip() if p.returncode == 0 else None

    def ancestor(self, a, w):
        if a == w:
            return True
        key = (a, w)
        if key not in self._anc:
            self._anc[key] = git(self.path, "merge-base", "--is-ancestor", a, w,
                                 check=False).returncode == 0
        return self._anc[key]


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_tables(lines):
    """Yield (start_index, heading_text, header_cells, [(line_index, cells)])."""
    heading = ""
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("## "):
            heading = ln
        if ln.startswith("|"):
            hdr = cells(ln)
            rows = []
            j = i + 1
            if j < len(lines) and set(lines[j].replace("|", "").replace(" ", "")) <= set("-:"):
                j += 1
            while j < len(lines) and lines[j].startswith("|"):
                rows.append((j, cells(lines[j])))
                j += 1
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

    # Split off the appended correction section.
    corr_start = None
    for idx, ln in enumerate(lines):
        if ln.startswith(CORR_HEADING):
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

    # Parse corrections.
    corrections = []
    for start, heading, hdr, rows in parse_tables(corr_lines):
        if not heading.startswith(CORR_HEADING):
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

    by_key = {}
    for c in corrections:
        key = (c["row"].strip(), c["class"])
        by_key.setdefault(key, []).append(c)
    false_corrections = 0
    valid_map = {}
    problem_by_key = {(p["row"], p["class"]): p for p in problems}
    for c in corrections:
        key = (c["row"].strip(), c["class"])
        p = problem_by_key.get(key)
        ok = (p is not None and len(by_key[key]) == 1
              and c["observed"] == p["observed"] and c["id"].startswith("CR31:"))
        c["ok"] = ok
        if ok:
            valid_map[key] = c
        else:
            false_corrections += 1
    unresolved = [p for p in problems if (p["row"], p["class"]) not in valid_map]
    valid = len(valid_map)
    met = (rows_checked >= 28 and not unresolved and false_corrections == 0 and append_only)

    summary = (f"rows {rows_checked} base_mismatched {len(problems)} exempt {len(exempt)} "
               f"valid_corrections {valid} false_corrections {false_corrections} "
               f"unresolved {len(unresolved)} append_only {append_only} met {met} tip {tip[:12]}")
    print(summary)
    if a.list:
        for p in problems:
            print(f"  {p['row']}: {p['class']} line {p['line']} {p['observed']}")
        for c in corrections:
            print(f"  corr {c['id']} row={c['row']} class={c['class']} ok={c['ok']}")
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
