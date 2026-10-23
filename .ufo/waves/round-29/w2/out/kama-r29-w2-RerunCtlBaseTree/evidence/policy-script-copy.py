#!/usr/bin/env python3
"""CtlBaseTree policy: check every base statement against the BASE tree 2aa46e24
instead of the writing revision W.

Extraction mirrors the frozen counter's extractor (same regexes/rules, same base,
same file set) so that statement ids line up; the CHECK is deliberately run
against BASE for every class:
  P/H/N -> blob at BASE
  C     -> the named commit must be a strict ancestor of BASE
  T     -> timestamp must not be later than BASE's committer time
  Q     -> the span must occur in the BASE tree with the counter's exclusions

Emits one correction row per statement that FAILS at base, in the counter's
observed-string format.
"""
from __future__ import annotations

import calendar
import hashlib
import os
import re
import subprocess
import sys
import time as _t

BASE = "2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d"
FILES = ("SCORECARD.md", "SHONEN.md")
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


def in_lane(path: str) -> bool:
    return not (path.startswith("../") or path.startswith("/") or path.startswith("~")
                or "://" in path)


def measured_cells(lines: list[str]) -> dict[int, str]:
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
                        "token": tok, "args": args})
    return out


def check_at_base(repo: Repo, st: dict) -> tuple[bool, str]:
    """Same class checks as the frozen counter, but every lookup is at BASE."""
    a, cls = st["args"], st["class"]
    if cls in ("P", "H", "N"):
        data = repo.blob(BASE, a["path"])
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
        anc = repo.strict_ancestor(c, BASE)
        return anc, f"commit={c}" + ("" if anc else " not-ancestor")
    if cls == "T":
        ts = calendar.timegm(_t.strptime(f"{a['date']}T{a['h']}:{a['m']}:{a['s']}", "%Y-%m-%dT%H:%M:%S"))
        ct = repo.ctime(BASE)
        return ts <= ct, f"time={ts} committed={ct}"
    if cls == "Q":
        p = git(repo.path, "grep", "-F", "-q", "-e", a["span"], BASE, "--", ".", *Q_EXCLUDE,
                check=False)
        if p.returncode not in (0, 1):
            raise RuntimeError(f"git grep failed: {p.stderr.decode(errors='replace').strip()}")
        return p.returncode == 0, ("ok" if p.returncode == 0 else "q:no-artifact")
    raise RuntimeError(cls)


def main() -> int:
    repo = Repo(sys.argv[1])
    stmts = []
    for f in FILES:
        stmts += extract(repo, f)
    sids = [s["sid"] for s in stmts]
    assert len(set(sids)) == len(sids), "duplicate sids"
    rows = []
    by_class = {}
    for s in stmts:
        ok, obs = check_at_base(repo, s)
        by_class[s["class"]] = by_class.get(s["class"], 0) + 1
        if not ok:
            rows.append((s["sid"], obs))
    print(f"statements {len(stmts)} by_class {by_class}")
    print(f"failing_at_base {len(rows)}")
    for sid, obs in rows:
        print(f"ROW\t{sid}\t{obs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
