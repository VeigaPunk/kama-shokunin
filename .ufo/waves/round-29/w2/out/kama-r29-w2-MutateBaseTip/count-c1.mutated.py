#!/usr/bin/env python3
"""Round-29 C1 counter (calibration): self-assessment statements false at the revision that wrote them.

Frozen predicate (the same sentence as preregistration.json C1.predicate and the label
`unresolved` in the receipt):

  A base statement is one checkable assertion that the frozen extractor finds on a line of
  SCORECARD.md or SHONEN.md at base 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d. Its writing
  revision W is the commit `git blame --line-porcelain <base> -- <file>` names for that line.
  A statement HOLDS iff its check passes against the lane tree and history at W:
    P  `path:L` or `path:L-M` (also an en dash; path not starting ../ / ~ or a URL scheme):
       the blob W:path exists and has at least max(L, M) lines   (fail: p:absent, p:beyond-eof)
    H  "md5"/"sha256" and a hex token (>= 8 hex) written directly after a backticked lane path
       (`path` md5 `hex`): the blob W:path exists and its digest starts with the hex
                                                                   (fail: h:absent, h:digest)
    N  "(<n> lines" written directly after a backticked lane path, or after that path's H
       token: the blob W:path exists and n equals its newline count, or its newline count + 1
       when the last line is unterminated                          (fail: n:absent, n:count)
    C  the first 7-40 hex token of a "Measured commit" cell (table column or
       "Measured commit:" line), and every 7-40 hex token (with a digit and a letter) written
       directly after one of the words at, base, tip, commit, commits, epoch, revision, rev,
       measured (optionally backticked), unless the 40 characters before the token contain
       "llama.cpp", "upstream", "ufo-fsd" or "@": it names a lane commit that is a strict
       ancestor of W                                               (fail: c:unresolved, c:not-ancestor)
    T  a time YYYY-MM-DD(T| ~|T~)HH:MM[:SS]Z on the line: it is not later than W's committer
       time                                                        (fail: t:future)
    Q  a backticked span of 6-200 characters that contains a digit and either "=" or (a space
       and one of the words met, registered, counted, stale, observed, verified, RESULT), and
       does not start with python3, python, bash, sh, git, node, ./, tools/ or / (a quoted
       measurement output):
       the span occurs verbatim in at least one blob of the tree at W other than SCORECARD.md,
       SHONEN.md, LOG.md and corpus/** (committed evidence at writing)  (fail: q:no-artifact)
  A base statement is UNRESOLVED iff it does not hold and the tip SCORECARD.md does not carry
  exactly one valid correction row for it. A correction row is a table row under the heading
  "## Round 29 — self-assessment corrections" whose first cell is `SA29:<sid>` and whose last
  cell is the observed value this counter prints for that statement (exact string). A
  correction row naming a statement that holds, naming no base statement, carrying a wrong
  observed value, or duplicating another row's sid is a FALSE correction; each false
  correction is itself counted as unresolved. The tip SCORECARD.md must begin with the base
  SCORECARD.md bytes (append-only); otherwise every base statement is unresolved.

Claim met iff mismatched_at_base >= 1 and unresolved == 0 at the measured tip
(preregistration.json C1.target). Exit 0 ran (whatever the count), 2 could not evaluate.

Usage: count-c1.py [--repo DIR] [--tip REV] [--out FILE] [--list]
Reads committed objects only (git --no-replace-objects); never the working tree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

BASE = "2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d"
FILES = ("SCORECARD.md", "SHONEN.md")
HEADING = "## Round 29 — self-assessment corrections"
GIT = "/usr/bin/git"
EXT = r"(?:md|py|sh|json|jsonl|tsv|txt|out|conf|cpp|yml|yaml|toml|err|log)"
RE_P = re.compile(r"(?<![\w./~:-])((?:[\w.-]+/)*[\w.-]+\." + EXT + r"):(\d+)(?:[-–](\d+))?(?![\w])")
RE_Q = re.compile(r"`([^`\n]{6,200})`")
Q_WORD = re.compile(r"=|\b(?:met|registered|counted|stale|observed|verified|RESULT)\b")
Q_CMD = ("python3", "python", "bash", "sh ", "git", "node", "./", "tools/", "/")
Q_EXCLUDE = (":(exclude)SCORECARD.md", ":(exclude)SHONEN.md", ":(exclude)LOG.md",
             ":(exclude)corpus")
UPSTREAM = ("llama.cpp", "upstream", "ufo-fsd", "@")
RE_HN = re.compile(r"`((?:[\w.-]+/)*[\w.-]+\." + EXT + r")`"
                   r"(?: (md5|sha256) `?([0-9a-f]{8,64})`?)?(?: \((\d+) lines\b)?")
RE_T = re.compile(r"\b(20\d\d-\d\d-\d\d)(?:T| ~|T~)(\d\d):(\d\d)(?::(\d\d))?Z")
RE_HEX = re.compile(r"(?<![0-9a-zA-Z])([0-9a-f]{7,40})(?![0-9a-zA-Z])")
RE_CWORD = re.compile(r"\b(?:at|base|tip|commit|commits|epoch|revision|rev|measured) `?([0-9a-f]{7,40})(?![0-9a-zA-Z])")


def git(repo, *args, data=None, check=True):
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
                        "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_REPLACE_REF_BASE")}
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    p = subprocess.run([GIT, "--no-replace-objects", "-C", repo, *args], input=data,
                       capture_output=True, env=env)
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.decode(errors='replace').strip()}")
    return p


class Repo:
    def __init__(self, path):
        self.path = path
        self._blob = {}
        self._ct = {}
        self._anc = {}

    def blob(self, rev, path):
        key = (rev, path)
        if key not in self._blob:
            p = git(self.path, "cat-file", "blob", f"{rev}:{path}", check=False)
            self._blob[key] = p.stdout if p.returncode == 0 else None
        return self._blob[key]

    def commit(self, token):
        p = git(self.path, "rev-parse", "--verify", "--quiet", f"{token}^{{commit}}", check=False)
        if p.returncode != 0:
            return None
        return p.stdout.decode().strip()

    def ctime(self, rev):
        if rev not in self._ct:
            self._ct[rev] = int(git(self.path, "show", "-s", "--format=%ct", rev).stdout.decode())
        return self._ct[rev]

    def strict_ancestor(self, a, w):
        if a == w:
            return False
        key = (a, w)
        if key not in self._anc:
            self._anc[key] = git(self.path, "merge-base", "--is-ancestor", a, w,
                                 check=False).returncode == 0
        return self._anc[key]


def nlines(data: bytes) -> int:
    return data.count(b"\n") + (0 if data.endswith(b"\n") or not data else 1)


def blame(repo: Repo, path: str) -> list[str]:
    out = git(repo.path, "blame", "--line-porcelain", BASE, "--", path).stdout.decode()
    revs, cur = [], None
    for line in out.split("\n"):
        m = re.match(r"^([0-9a-f]{40}) \d+ \d+", line)
        if m:
            cur = m.group(1)
        elif line.startswith("\t"):
            revs.append(cur)
    return revs


def in_lane(path: str) -> bool:
    return not (path.startswith("../") or path.startswith("/") or path.startswith("~")
                or "://" in path)



def measured_cells(lines: list[str]) -> dict[int, str]:
    """line index -> text of its Measured-commit cell (table column or 'Measured commit:' line)."""
    cells, col = {}, None
    for i, line in enumerate(lines):
        if line.startswith("|"):
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            if any(c.lower() == "measured commit" for c in cols):
                col = [c.lower() for c in cols].index("measured commit")
                continue
            if col is not None and not set(line.replace("|", "").strip()) <= set("-: "):
                if col < len(cols):
                    cells[i] = cols[col]
        else:
            col = None
            m = re.match(r"^Measured commit:\s*(.*)$", line)
            if m:
                cells[i] = m.group(1)
    return cells


def extract(repo: Repo, fname: str) -> list[dict]:
    text = repo.blob(BASE, fname)
    if text is None:
        raise RuntimeError(f"base {fname} missing")
    lines = text.decode().split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    revs = blame(repo, fname)
    if len(revs) != len(lines):
        raise RuntimeError(f"blame/line mismatch in {fname}: {len(revs)} vs {len(lines)}")
    cells = measured_cells(lines)
    out, seen = [], {}
    for i, line in enumerate(lines):
        lsha = hashlib.sha256(line.encode()).hexdigest()[:10]
        if lsha in seen:
            seen[lsha] += 1
            lsha = f"{lsha}#{seen[lsha]}"
        else:
            seen[lsha] = 0
        found = []
        for k, m in enumerate(RE_P.finditer(line)):
            if in_lane(m.group(1)):
                end = max(int(m.group(2)), int(m.group(3) or 0))
                found.append(("P", k, m.group(0), {"path": m.group(1), "end": end}))
        kh = kn = 0
        for m in RE_HN.finditer(line):
            if not in_lane(m.group(1)):
                continue
            if m.group(2):
                found.append(("H", kh, m.group(0), {"path": m.group(1), "algo": m.group(2),
                                                    "hex": m.group(3)}))
                kh += 1
            if m.group(4):
                found.append(("N", kn, m.group(0), {"path": m.group(1), "n": int(m.group(4))}))
                kn += 1
        ctoks = []
        if i in cells:
            m = RE_HEX.search(cells[i])
            if m:
                ctoks.append(m.group(1))
        for m in RE_CWORD.finditer(line):
            t = m.group(1)
            before = line[max(0, m.start(1) - 40):m.start(1)]
            if any(u in before for u in UPSTREAM):
                continue
            if re.search(r"\d", t) and re.search(r"[a-f]", t) and t not in ctoks:
                ctoks.append(t)
        for k, t in enumerate(ctoks):
            found.append(("C", k, t, {"token": t}))
        for k, m in enumerate(RE_T.finditer(line)):
            found.append(("T", k, m.group(0), {"date": m.group(1), "h": m.group(2),
                                               "m": m.group(3), "s": m.group(4) or "00"}))
        kq = 0
        for m in RE_Q.finditer(line):
            span = m.group(1)
            if (re.search(r"\d", span) and ("=" in span or (" " in span and Q_WORD.search(span)))
                    and not span.startswith(Q_CMD)):
                found.append(("Q", kq, span, {"span": span}))
                kq += 1
        for cls, k, tok, args in found:
            sid = f"{fname}:{cls}:{lsha}:{k}"
            out.append({"sid": sid, "file": fname, "line": i + 1, "class": cls,
                        "token": tok, "W": revs[i], "args": args})
    return out


def check(repo: Repo, st: dict) -> tuple[bool, str]:
    W, a, cls = st["W"], st["args"], st["class"]
    if cls in ("P", "H", "N"):
        data = repo.blob(W, a["path"])
        if data is None:
            return False, f"{cls.lower()}:absent"
        if cls == "P":
            n = nlines(data)
            return (n >= a["end"]), (f"eof={n}" if n < a["end"] else "ok")
        if cls == "H":
            d = hashlib.new(a["algo"], data).hexdigest()
            return d.startswith(a["hex"]), f"{a['algo']}={d}"
        nl = data.count(b"\n")
        unterminated = bool(data) and not data.endswith(b"\n")
        ok = a["n"] == nl or (unterminated and a["n"] == nl + 1)
        return ok, f"newlines={nl} unterminated={str(unterminated).lower()}"
    if cls == "C":
        c = repo.commit(a["token"])
        if c is None:
            return False, "c:unresolved"
        return repo.strict_ancestor(c, W), f"commit={c}" + ("" if repo.strict_ancestor(c, W) else " not-ancestor")
    if cls == "T":
        import calendar
        import time as _t
        ts = calendar.timegm(_t.strptime(f"{a['date']}T{a['h']}:{a['m']}:{a['s']}", "%Y-%m-%dT%H:%M:%S"))
        ct = repo.ctime(W)
        return ts <= ct, f"time={ts} committed={ct}"
    if cls == "Q":
        p = git(repo.path, "grep", "-F", "-q", "-e", a["span"], W, "--", ".", *Q_EXCLUDE,
                check=False)
        if p.returncode not in (0, 1):
            raise RuntimeError(f"git grep failed: {p.stderr.decode(errors='replace').strip()}")
        return p.returncode == 0, ("ok" if p.returncode == 0 else "q:no-artifact")
    raise RuntimeError(cls)


def corrections(text: str) -> list[tuple[str, str]]:
    rows, on = [], False
    for line in text.split("\n"):
        if line.startswith("## "):
            on = line.strip() == HEADING
            continue
        if on and line.startswith("|"):
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            first = cols[0].strip("`")
            if first.startswith("SA29:"):
                rows.append((first[5:], cols[-1].strip("`")))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="/home/vgpnk/Projects/shokunin/kama-shokunin")
    ap.add_argument("--tip", default="refs/heads/master")
    ap.add_argument("--out")
    ap.add_argument("--list", action="store_true")
    o = ap.parse_args()
    repo = Repo(o.repo)
    receipt = {"counter": "kama round-29 count-c1 v1", "base": BASE,
               "counter_sha256": hashlib.sha256(open(__file__, "rb").read()).hexdigest()}
    try:
        tip = repo.commit(o.tip)
        if tip is None:
            raise RuntimeError(f"tip {o.tip} unresolved")
        receipt["tip"] = tip
        stmts = []
        for f in FILES:
            stmts += extract(repo, f)
        sids = [s["sid"] for s in stmts]
        if len(set(sids)) != len(sids):
            raise RuntimeError("duplicate statement ids")
        mism = {}
        for s in stmts:
            ok, obs = check(repo, s)
            s["holds"], s["observed"] = ok, obs
            if not ok:
                mism[s["sid"]] = obs
        base_sc = repo.blob(BASE, "SCORECARD.md")
        tip_sc = repo.blob(tip, "SCORECARD.md")
        append_only = tip_sc is not None and tip_sc.startswith(base_sc)
        rows = corrections(tip_sc.decode()) if tip_sc is not None else []
        seen, valid, false_rows = set(), set(), []
        for sid, obs in rows:
            if sid in seen or sid not in mism or obs != mism[sid]:
                false_rows.append({"sid": sid, "observed": obs,
                                   "why": "duplicate" if sid in seen else
                                   ("not-a-mismatch" if sid not in mism else "wrong-observed")})
            else:
                valid.add(sid)
            seen.add(sid)
        valid -= {r["sid"] for r in false_rows}
        if append_only:
            unresolved_ids = sorted(set(mism) - valid) if valid else []
        else:
            unresolved_ids = sorted(sids)
        unresolved = len(unresolved_ids) + len(false_rows)
        receipt.update({
            "statements": len(stmts),
            "by_class": {c: sum(1 for s in stmts if s["class"] == c) for c in "PHNCTQ"},
            "mismatched_at_base": len(mism),
            "append_only": append_only,
            "correction_rows": len(rows),
            "valid_corrections": len(valid),
            "false_corrections": false_rows,
            "unresolved": unresolved,
            "unresolved_ids": unresolved_ids,
            "mismatches": [{k: s[k] for k in ("sid", "file", "line", "class", "token", "W", "observed")}
                           for s in stmts if not s["holds"]],
            "target": "mismatched_at_base >= 1 and unresolved == 0",
            "met": len(mism) >= 1 and unresolved == 0,
        })
        if o.list:
            receipt["all_statements"] = [{k: s[k] for k in ("sid", "line", "class", "token", "W", "holds", "observed")}
                                         for s in stmts]
        code = 0
    except Exception as e:  # could not evaluate
        receipt["error"] = str(e)
        code = 2
    text = json.dumps(receipt, indent=1, sort_keys=True)
    if o.out:
        if os.path.exists(o.out):
            print(f"refusing to overwrite {o.out}", file=sys.stderr)
            return 2
        with open(o.out, "w") as fh:
            fh.write(text + "\n")
    if code == 0:
        print(f"statements {receipt['statements']} mismatched_at_base {receipt['mismatched_at_base']} "
              f"append_only {receipt['append_only']} valid_corrections {receipt['valid_corrections']} "
              f"false_corrections {len(receipt['false_corrections'])} unresolved {receipt['unresolved']} "
              f"met {receipt['met']} tip {receipt['tip'][:12]}")
    else:
        print(f"could-not-evaluate: {receipt['error']}")
    return code


if __name__ == "__main__":
    sys.exit(main())
