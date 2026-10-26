#!/usr/bin/env python3
"""append-only-audit.py - set the lane's append-only self-description against its git history.

The lane treats five files as append-only (SCORECARD.md, LOG.md, corpus/QUALITY.md,
corpus/README.md, corpus/SOURCES.md). This tool lists every commit that deletes at
least --threshold lines (default 20) from one of them, how many of the deleted lines
the file holds again at the audited revision, and which later commit first held all
of them again. It is read-only on --repo.

Definitions (round-46 claim C2 contract; the counter tools/round46-append-audit-check.py
recomputes them independently):
  commits          `git rev-list --topo-order --reverse <to>`
  diff             against the first parent: `git diff --no-renames -U0 <c>^1 <c> -- <file>`;
                   a root commit has no parent and no deletions
  deleted          `-` lines of that diff (the `---` header excluded)
  event            (commit, file) with deleted >= threshold
  restored_at_tip  deleted lines (exact text) occurring as some line of <file> at <to>
                   (each deleted line counted on its own; duplicates may share one line)
  status           restored (all), unrestored (none), partial (some)
  restored_by      the first commit after the event commit in the rev-list order at which
                   <file> holds every deleted line text again, else null

Usage:
  append-only-audit.py --repo DIR [--to REV] [--threshold N] [--files a,b,...] [--json]
  append-only-audit.py --selftest [--scratch DIR]
Output: text lines `event <commit12> <file> deleted=N restored_at_tip=K status=S
restored_by=<commit12|->` then `summary commits=C events=E restored=R partial=P
unrestored=U`; --json prints {"to", "threshold", "files", "commits", "events": [...],
"summary": {...}} with full commit ids.
Exit: 0 no event partial or unrestored; 1 at least one; 2 could not evaluate.
Fixtures (selftest) live under --scratch or $TMPDIR and are removed on exit.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

FILES = ["SCORECARD.md", "LOG.md", "corpus/QUALITY.md", "corpus/README.md", "corpus/SOURCES.md"]


class AuditError(Exception):
    pass


def _git(repo, *args, inp=None):
    p = subprocess.run(["git", "-C", repo, *args], input=inp, capture_output=True, text=True)
    if p.returncode != 0:
        raise AuditError(f"git {' '.join(args)[:100]}: {p.stderr.strip()[:200]}")
    return p.stdout


class Repo:
    def __init__(self, path):
        self.path = path
        self._blob_lines = {}

    def blobs(self, specs):
        """Map each `<rev>:<path>` spec to its blob id or None (one cat-file call)."""
        if not specs:
            return {}
        out = _git(self.path, "cat-file", "--batch-check=%(objectname) %(objecttype)", inp="\n".join(specs) + "\n")
        res = {}
        for spec, line in zip(specs, out.split("\n")):
            parts = line.split()
            res[spec] = parts[0] if len(parts) == 2 and parts[1] == "blob" else None
        return res

    def lines(self, blob):
        if blob is None:
            return frozenset()
        if blob not in self._blob_lines:
            self._blob_lines[blob] = frozenset(_git(self.path, "cat-file", "blob", blob).split("\n"))
        return self._blob_lines[blob]


def audit(repo_path, to="HEAD", threshold=20, files=None):
    files = files or FILES
    r = Repo(repo_path)
    to_full = _git(repo_path, "rev-parse", "--verify", to + "^{commit}").strip()
    commits = _git(repo_path, "rev-list", "--topo-order", "--reverse", to_full).split()
    parents = {}
    for line in _git(repo_path, "rev-list", "--topo-order", "--reverse", "--parents", to_full).split("\n"):
        parts = line.split()
        if parts:
            parents[parts[0]] = parts[1] if len(parts) > 1 else None
    tip_blobs = r.blobs([f"{to_full}:{f}" for f in files])
    events = []
    for i, c in enumerate(commits):
        p = parents.get(c)
        if p is None:
            continue
        changed = set(_git(repo_path, "diff", "--no-renames", "--name-only", p, c, "--", *files).split("\n")) - {""}
        for f in files:
            if f not in changed:
                continue
            d = _git(repo_path, "diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0", p, c, "--", f)
            dele = [x[1:] for x in d.split("\n") if x.startswith("-") and not x.startswith("---")]
            if len(dele) < threshold:
                continue
            tip_lines = r.lines(tip_blobs[f"{to_full}:{f}"])
            k = sum(1 for x in dele if x in tip_lines)
            status = "restored" if k == len(dele) else ("unrestored" if k == 0 else "partial")
            later = commits[i + 1:]
            later_blobs = r.blobs([f"{c2}:{f}" for c2 in later])
            need = set(dele)
            rb = None
            for c2 in later:
                if need <= r.lines(later_blobs[f"{c2}:{f}"]):
                    rb = c2
                    break
            events.append({"commit": c, "file": f, "deleted": len(dele), "restored_at_tip": k,
                           "status": status, "restored_by": rb})
    summary = {"commits": len(commits), "events": len(events),
               "restored": sum(e["status"] == "restored" for e in events),
               "partial": sum(e["status"] == "partial" for e in events),
               "unrestored": sum(e["status"] == "unrestored" for e in events)}
    return {"to": to_full, "threshold": threshold, "files": files, "commits": len(commits),
            "events": events, "summary": summary}


def render(res):
    out = [f"event {e['commit'][:12]} {e['file']} deleted={e['deleted']} restored_at_tip={e['restored_at_tip']} "
           f"status={e['status']} restored_by={(e['restored_by'] or '-')[:12]}" for e in res["events"]]
    s = res["summary"]
    out.append(f"summary commits={s['commits']} events={s['events']} restored={s['restored']} "
               f"partial={s['partial']} unrestored={s['unrestored']}")
    return "\n".join(out)


def exit_code(res):
    s = res["summary"]
    return 1 if s["partial"] or s["unrestored"] else 0


# ---------------------------------------------------------------- selftest
class Fixture:
    IDENT = ["-c", "user.name=aoa-selftest", "-c", "user.email=aoa-selftest@invalid", "-c", "commit.gpgsign=false"]

    def __init__(self, root):
        self.d = tempfile.mkdtemp(prefix="aoa-st-", dir=root)
        _git(self.d, "init", "-q")
        top = _git(self.d, "rev-parse", "--show-toplevel").strip()
        if os.path.realpath(top) != os.path.realpath(self.d):
            raise AuditError("fixture toplevel mismatch")
        self.n = 0

    def commit(self, files, delete=()):
        for name, body in files.items():
            path = os.path.join(self.d, name)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as fh:
                fh.write("".join(x + "\n" for x in body))
        for name in delete:
            _git(self.d, "rm", "-q", name)
        _git(self.d, "add", "-A")
        self.n += 1
        _git(self.d, *self.IDENT, "commit", "-q", "--allow-empty", "-m", f"c{self.n}")
        return _git(self.d, "rev-parse", "HEAD").strip()


def lines(tag, n):
    return [f"{tag} line {i} {os.urandom(4).hex()}" for i in range(n)]


def selftest(root):
    cases = []

    def case(name, fn):
        try:
            ok, why = fn()
        except Exception as e:  # noqa: BLE001 - a crash is a failed case
            ok, why = False, f"exception {e}"
        cases.append((name, ok, why))

    def t_none():
        f = Fixture(root)
        a = lines("a", 30)
        f.commit({"LOG.md": a})
        t = f.commit({"LOG.md": a + lines("b", 5)})
        res = audit(f.d, t)
        return res["events"] == [] and exit_code(res) == 0, str(res["summary"])

    def t_below():
        f = Fixture(root)
        a = lines("a", 40)
        f.commit({"LOG.md": a})
        t = f.commit({"LOG.md": a[:21]})          # 19 deleted
        res = audit(f.d, t)
        return res["events"] == [] and exit_code(res) == 0, str(res["summary"])

    def t_exact_unrestored():
        f = Fixture(root)
        a = lines("a", 40)
        f.commit({"corpus/QUALITY.md": a})
        c = f.commit({"corpus/QUALITY.md": a[20:]})   # exactly 20 deleted
        res = audit(f.d, c)
        e = res["events"]
        return (len(e) == 1 and e[0]["commit"] == c and e[0]["deleted"] == 20 and e[0]["status"] == "unrestored"
                and e[0]["restored_by"] is None and exit_code(res) == 1), str(e)

    def t_restored():
        f = Fixture(root)
        a = lines("a", 50)
        f.commit({"SCORECARD.md": a})
        c = f.commit({"SCORECARD.md": a[:10]})
        f.commit({"notes.md": ["x"]})
        r = f.commit({"SCORECARD.md": a + ["appended"]})
        t = f.commit({"SCORECARD.md": a + ["appended", "more"]})
        res = audit(f.d, t)
        e = res["events"]
        return (len(e) == 1 and e[0]["commit"] == c and e[0]["restored_by"] == r and e[0]["status"] == "restored"
                and e[0]["restored_at_tip"] == 40 and exit_code(res) == 0), str(e)

    def t_partial():
        f = Fixture(root)
        a = lines("a", 60)
        f.commit({"corpus/README.md": a})
        f.commit({"corpus/README.md": a[:20]})        # 40 deleted
        t = f.commit({"corpus/README.md": a[:40]})    # 20 back
        res = audit(f.d, t)
        e = res["events"]
        return (len(e) == 1 and e[0]["status"] == "partial" and e[0]["restored_at_tip"] == 20
                and e[0]["restored_by"] is None and exit_code(res) == 1), str(e)

    def t_undeclared():
        f = Fixture(root)
        a = lines("a", 50)
        f.commit({"notes.md": a, "corpus/other.md": a})
        t = f.commit({"notes.md": a[:5], "corpus/other.md": a[:5]})
        res = audit(f.d, t)
        return res["events"] == [] and exit_code(res) == 0, str(res["events"])

    def t_file_removed():
        f = Fixture(root)
        a = lines("a", 25)
        f.commit({"corpus/SOURCES.md": a})
        c = f.commit({}, delete=["corpus/SOURCES.md"])
        res = audit(f.d, c)
        e = res["events"]
        return (len(e) == 1 and e[0]["deleted"] == 25 and e[0]["status"] == "unrestored"
                and exit_code(res) == 1), str(e)

    def t_to_earlier():
        f = Fixture(root)
        a = lines("a", 50)
        f.commit({"LOG.md": a})
        mid = f.commit({"LOG.md": a + ["x"]})
        f.commit({"LOG.md": a[:5]})
        res = audit(f.d, mid)
        return res["events"] == [] and res["commits"] == 2, str(res["summary"])

    def t_merge_first_parent():
        f = Fixture(root)
        a = lines("a", 40)
        f.commit({"LOG.md": a})
        base = _git(f.d, "rev-parse", "HEAD").strip()
        _git(f.d, "checkout", "-q", "-b", "side")
        f.commit({"LOG.md": a[:10]})                  # side deletes 30
        _git(f.d, "checkout", "-q", "-")
        main_c = f.commit({"LOG.md": a + ["main"]})
        _git(f.d, *Fixture.IDENT, "merge", "-q", "-s", "ours", "--no-edit", "side")
        m = _git(f.d, "rev-parse", "HEAD").strip()
        res = audit(f.d, m)
        e = res["events"]
        # the side commit is an event; the merge (first parent = main) deletes nothing
        ok = (len(e) == 1 and e[0]["commit"] != m and e[0]["deleted"] == 30 and e[0]["status"] == "restored"
              and base != main_c)
        return ok, str(e)

    def t_threshold_flag():
        f = Fixture(root)
        a = lines("a", 40)
        f.commit({"LOG.md": a})
        t = f.commit({"LOG.md": a[:35]})              # 5 deleted
        res = audit(f.d, t, threshold=5)
        return len(res["events"]) == 1 and exit_code(res) == 1, str(res["events"])

    for name, fn in [("no-deletion", t_none), ("below-threshold", t_below), ("exact-threshold-unrestored", t_exact_unrestored),
                     ("restored-later", t_restored), ("partial", t_partial), ("undeclared-file", t_undeclared),
                     ("declared-file-removed", t_file_removed), ("to-earlier-rev", t_to_earlier),
                     ("merge-first-parent", t_merge_first_parent), ("threshold-flag", t_threshold_flag)]:
        case(name, fn)
    for name, ok, why in cases:
        print(f"{'pass' if ok else 'FAIL'} {name}" + ("" if ok else f": {why[:300]}"))
    fails = sum(1 for _, ok, _ in cases if not ok)
    print(f"AOA_SELFTEST pass={len(cases) - fails} fail={fails}")
    return 0 if fails == 0 else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--to", default="HEAD")
    ap.add_argument("--threshold", type=int, default=20)
    ap.add_argument("--files", help="comma list of repo-relative paths (default: the five declared files)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--scratch", help="fixture root for --selftest (default $TMPDIR)")
    a = ap.parse_args(argv)
    if a.selftest:
        root = tempfile.mkdtemp(prefix="aoa-", dir=a.scratch or tempfile.gettempdir())
        try:
            return selftest(root)
        finally:
            shutil.rmtree(root, ignore_errors=True)
    if a.threshold < 1:
        print("could-not-evaluate: --threshold must be >= 1", file=sys.stderr)
        return 2
    files = [x.strip() for x in a.files.split(",") if x.strip()] if a.files else None
    try:
        res = audit(a.repo, a.to, a.threshold, files)
    except AuditError as e:
        print(f"could-not-evaluate: {e}", file=sys.stderr)
        return 2
    print(json.dumps(res, indent=1) if a.json else render(res))
    return exit_code(res)


if __name__ == "__main__":
    sys.exit(main())
