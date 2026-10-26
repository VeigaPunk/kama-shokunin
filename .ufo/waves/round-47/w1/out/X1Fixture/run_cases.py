#!/usr/bin/env python3
"""X1Fixture: adversarial fixtures for kama tools/append-only-audit.py v2.

Builds one git repo per case under <scratch>/fx/, runs the pinned tool with
--json, cross-checks every reported event against `git diff --numstat`, and
compares the whole event list with a hand-derived expectation (symbolic commit
names c1, c2, ...).

Usage: run_cases.py SCRATCH TOOL OUTJSON [LANE_COUNTER]
No network; writes only under SCRATCH and OUTJSON.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import time

SCRATCH, TOOL, OUTJSON = sys.argv[1], sys.argv[2], sys.argv[3]
LANE_COUNTER = sys.argv[4] if len(sys.argv) > 4 else None
ENV = dict(os.environ,
           GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
           GIT_AUTHOR_NAME="x1fixture", GIT_AUTHOR_EMAIL="x1fixture@invalid",
           GIT_COMMITTER_NAME="x1fixture", GIT_COMMITTER_EMAIL="x1fixture@invalid")
HEADER = "path\trule\tdeclared_at\tnote"
RESULTS = []


def run(args):
    return subprocess.run(args, capture_output=True, env=ENV)


class Fx:
    def __init__(self, name):
        self.name = name
        self.d = os.path.join(SCRATCH, "fx", name)
        os.makedirs(self.d, exist_ok=False)
        self.g("init", "-q")
        top = self.g("rev-parse", "--show-toplevel").stdout.decode().strip()
        if os.path.realpath(top) != os.path.realpath(self.d):
            raise SystemExit(f"toplevel mismatch {top} != {self.d}")
        self.n = 0
        self.C = {}

    def g(self, *args, check=True):
        p = run(["git", "-C", self.d, *args])
        if check and p.returncode:
            raise SystemExit(f"git {' '.join(args)}: {p.stderr.decode()[:400]}")
        return p

    def w(self, name, data):
        full = os.path.join(self.d, name)
        os.makedirs(os.path.dirname(full) or self.d, exist_ok=True)
        with open(full, "wb") as fh:
            fh.write(data)

    def rm(self, name):
        self.g("rm", "-q", name)

    def commit(self, msg=None):
        self.g("add", "-A")
        self.n += 1
        self.g("commit", "-q", "--allow-empty", "-m", msg or f"c{self.n}")
        c = self.g("rev-parse", "HEAD").stdout.decode().strip()
        self.C[f"c{self.n}"] = c
        return c

    def contract(self, rows, crlf=False):
        nl = "\r\n" if crlf else "\n"
        body = HEADER + nl + "".join("\t".join(r) + nl for r in rows)
        self.w("registry/append-only-contract.tsv", body.encode())

    def audit(self, to="HEAD"):
        t0 = time.time()
        p = run([sys.executable, TOOL, "--repo", self.d, "--to", to, "--json"])
        dt = time.time() - t0
        try:
            obj = json.loads(p.stdout)
        except ValueError:
            obj = None
        return {"rc": p.returncode, "obj": obj, "stdout": p.stdout.decode("utf-8", "replace"),
                "stderr": p.stderr.decode("utf-8", "replace"), "secs": round(dt, 3)}

    def audit_files(self, files, to="HEAD"):
        p = run([sys.executable, TOOL, "--repo", self.d, "--to", to, "--files", ",".join(files), "--json"])
        try:
            obj = json.loads(p.stdout)
        except ValueError:
            obj = None
        return {"rc": p.returncode, "obj": obj, "stderr": p.stderr.decode("utf-8", "replace")}

    def numstat(self, parent, commit, path, no_renames=True):
        args = ["git", "-C", self.d, "diff", "--numstat"]
        if no_renames:
            args.append("--no-renames")
        args += [parent, commit, "--", path]
        return run(args).stdout.decode("utf-8", "replace").rstrip("\n")

    def diff(self, a, b, path, stats=False):
        args = ["git", "-C", self.d, "diff", "--no-renames", "--no-color", "--no-ext-diff", "--text"]
        args.append("--stat" if stats else "-U0")
        return run(args + [a, b, "--", path]).stdout.decode("utf-8", "replace")


def lines(tag, n, start=0):
    return [f"{tag} line {i}" for i in range(start, start + n)]


def nd(items):
    return "".join(x + "\n" for x in items).encode()


def sym(fx, cid):
    if cid is None:
        return None
    for k, v in fx.C.items():
        if v == cid:
            return k
    return cid[:12]


def check(case, fx, res, expect_events, expect_exit, truth, extra=None):
    rec = {"case": case, "repo": fx.d, "rc": res["rc"], "stderr": res["stderr"].strip()[:500],
           "stdout_head": res["stdout"][:400], "secs": res["secs"], "truth": truth,
           "expect_exit": expect_exit, "expect": expect_events, "got": [], "numstat": [],
           "verdict": "", "problems": []}
    rec.update(extra or {})
    if res["obj"] is None:
        if res["rc"] == expect_exit:
            rec["verdict"] = f"AS-EXPECTED (exit {res['rc']}, no JSON)"
        else:
            rec["verdict"] = "NO-JSON"
            rec["problems"].append(f"no JSON, rc={res['rc']} != expected {expect_exit}: {res['stderr'].strip()[:300]}")
        RESULTS.append(rec)
        return rec
    rec["files"] = res["obj"].get("files")
    rec["summary"] = res["obj"].get("summary")
    for e in res["obj"].get("events", []):
        rec["got"].append({"commit": sym(fx, e["commit"]), "file": e["file"], "deleted": e["deleted"],
                           "restored_max": e["restored_max"], "status": e["status"],
                           "restored_best": sym(fx, e.get("restored_best")),
                           "restored_by": sym(fx, e.get("restored_by"))})
        par = fx.g("rev-parse", e["commit"] + "^").stdout.decode().strip()
        rec["numstat"].append({
            "event": f"{sym(fx, e['commit'])} {e['file']}", "deleted": e["deleted"],
            "numstat_no_renames": fx.numstat(par, e["commit"], e["file"]),
            "numstat_default_renames": fx.numstat(par, e["commit"], e["file"], no_renames=False),
        })
    if res["rc"] != expect_exit:
        rec["problems"].append(f"exit {res['rc']} != expected {expect_exit}")
    if len(rec["got"]) != len(expect_events):
        rec["problems"].append(f"event count {len(rec['got'])} != expected {len(expect_events)}")
    for want, got in zip(expect_events, rec["got"]):
        for k, v in want.items():
            if got.get(k) != v:
                rec["problems"].append(f"{k}: got {got.get(k)!r} want {v!r} ({got})")
    for ns in rec["numstat"]:
        cells = ns["numstat_no_renames"].split("\t")
        if len(cells) < 2 or cells[1] != str(ns["deleted"]):
            rec["problems"].append(f"numstat disagreement {ns}")
    rec["verdict"] = "AS-EXPECTED" if not rec["problems"] else "MISMATCH"
    RESULTS.append(rec)
    return rec


# ---------------------------------------------------------------- C01 binary
def c01():
    fx = Fx("c01-binary-nul")
    fx.w("README.md", b"append-only rules live here\n")
    body = nd(lines("bin", 40)).replace(b"bin line 3", b"bin\x00line 3")   # NUL -> git says binary
    fx.w("assets/blob.bin", body)
    fx.w("assets/plain.txt", nd(lines("txt", 40)))
    fx.contract([("assets/*.bin", "A-corr", "README.md:1", "binary archive"),
                 ("assets/*.txt", "A-corr", "README.md:1", "text sibling")])
    fx.commit()
    fx.w("assets/blob.bin", nd(lines("bin", 5)))            # 35 lines gone, child has no NUL
    fx.w("assets/plain.txt", nd(lines("txt", 5)))           # 35 lines gone, plain text
    c2 = fx.commit()
    res = fx.audit()
    return check("C01 binary (NUL) declared file loses 35 lines, text sibling loses 35", fx, res,
                 [{"commit": "c2", "file": "assets/plain.txt", "deleted": 35, "restored_max": 0,
                   "status": "unrestored"}], 1,
                 "only the text sibling is an event; the declared binary file's 35 deletions are skipped with no warning",
                 extra={"numstat_raw": {
                     "binary_default": fx.numstat(fx.C["c1"], c2, "assets/blob.bin", no_renames=False),
                     "binary_no_renames": fx.numstat(fx.C["c1"], c2, "assets/blob.bin"),
                     "plain": fx.numstat(fx.C["c1"], c2, "assets/plain.txt")},
                     "diff_binary": fx.diff(fx.C["c1"], c2, "assets/blob.bin", stats=True)})


# ---------------------------------------------------------------- C02 rename
def c02a():
    fx = Fx("c02-rename-out-back")
    fx.w("README.md", b"append-only rules live here\n")
    fx.w("data/doc.md", nd(lines("doc", 30)))
    fx.contract([("data/*.md", "A-corr", "README.md:1", "doc")])
    c1 = fx.commit()
    os.makedirs(os.path.join(fx.d, "moved"), exist_ok=True)
    fx.g("mv", "data/doc.md", "moved/doc.md")
    c2 = fx.commit()
    fx.g("mv", "moved/doc.md", "data/doc.md")
    c3 = fx.commit()
    res = fx.audit()
    return check("C02a declared file git mv out of the contract, then renamed back", fx, res,
                 [{"commit": "c2", "file": "data/doc.md", "deleted": 30, "restored_max": 30,
                   "restored_best": "c3", "restored_by": "c3", "status": "restored"}], 0,
                 "rename out reads as delete-30 (--no-renames); rename back restores it; git's rename-detecting numstat says 0 0",
                 extra={"numstat_raw": {
                     "out_default_renames": fx.numstat(c1, c2, "data/doc.md", no_renames=False),
                     "out_no_renames": fx.numstat(c1, c2, "data/doc.md"),
                     "back_default_renames": fx.numstat(c2, c3, "data/doc.md", no_renames=False)}})


def c02b():
    fx = Fx("c02b-rename-inside-contract")
    fx.w("README.md", b"append-only rules live here\n")
    fx.w("data/doc.md", nd(lines("doc", 30)))
    fx.contract([("data/*.md", "A-corr", "README.md:1", "doc")])
    fx.commit()
    fx.g("mv", "data/doc.md", "data/doc2.md")                # both names are in the contract
    c2 = fx.commit()
    fx.w("data/doc2.md", nd(lines("doc", 30) + ["tail"]))
    c3 = fx.commit()
    res = fx.audit()
    ctl = fx.audit_files(["data/doc.md"])
    return check("C02b declared file git mv to a sibling path also inside the contract", fx, res, [], 0,
                 "all 30 lines survive under data/doc2.md; the old path is absent at the tip, so the contract expansion drops it and the move is invisible (--files sees it)",
                 extra={"control_files_run": {"rc": ctl["rc"], "events": ctl["obj"]["events"] if ctl["obj"] else None},
                        "numstat_out": fx.numstat(fx.C["c1"], c2, "data/doc.md"),
                        "numstat_back": fx.numstat(c2, c3, "data/doc2.md")})


# ---------------------------------------------------------------- C03 recreate
def c03():
    fx = Fx("c03-delete-recreate")
    fx.w("README.md", b"append-only rules live here\n")
    fx.w("data/doc.md", nd(lines("doc", 30)))
    fx.contract([("data/*.md", "A-corr", "README.md:1", "doc")])
    fx.commit()
    fx.rm("data/doc.md")
    c2 = fx.commit()
    fx.w("data/doc.md", nd(lines("doc", 30)))
    c3 = fx.commit()
    res = fx.audit()
    return check("C03 declared file deleted and recreated with identical text", fx, res,
                 [{"commit": "c2", "file": "data/doc.md", "deleted": 30, "restored_max": 30,
                   "restored_best": "c3", "restored_by": "c3", "status": "restored"}], 0,
                 "delete-30 then a byte-identical recreate is restored in the recreate commit")


# ---------------------------------------------------------------- C04 blank lines
def c04():
    fx = Fx("c04-blank-lines")
    fx.w("README.md", b"append-only rules live here\n")
    head, tail = lines("head", 30), lines("tail", 10)
    fx.w("data/notes.md", nd(head) + b"\n" * 25 + nd(tail))
    fx.contract([("data/*.md", "A-corr", "README.md:1", "notes")])
    c1 = fx.commit()
    fx.w("data/notes.md", nd(head) + nd(tail))               # exactly the 25 blank lines deleted
    c2 = fx.commit()
    # 25 blank lines inserted *between head line 14 and head line 15*: a different, unrelated place
    fx.w("data/notes.md", nd(head[:15]) + b"\n" * 25 + nd(head[15:]) + nd(tail))
    c3 = fx.commit()
    res = fx.audit()
    return check("C04 delete 25 blank lines only, then add 25 unrelated blank lines", fx, res,
                 [{"commit": "c2", "file": "data/notes.md", "deleted": 25, "restored_max": 25,
                   "restored_best": "c3", "restored_by": "c3", "status": "restored"}], 0,
                 "the 25 deleted empty lines are not back; 25 different empty lines were inserted 15 lines higher",
                 extra={"diff_c1_c2": fx.diff(c1, c2, "data/notes.md"),
                        "diff_c2_c3": fx.diff(c2, c3, "data/notes.md")})


# ---------------------------------------------------------------- C05 merge
def _merge_repo(name):
    fx = Fx(name)
    fx.w("README.md", b"append-only rules live here\n")
    fx.w("data/doc.md", nd(lines("doc", 40)))
    fx.w("notes.md", b"x\n")
    fx.contract([("data/*.md", "A-corr", "README.md:1", "doc")])
    base = fx.commit()
    fx.g("checkout", "-q", "-b", "side")
    fx.w("data/doc.md", nd(lines("doc", 10)))
    fx.commit()                                              # c2 on side
    fx.g("checkout", "-q", base)                             # detached on the base commit
    fx.w("notes.md", b"x\ny\n")
    fx.commit()                                              # c3 on the detached HEAD
    return fx


def c05a():
    fx = _merge_repo("c05-merge-side-deletes")
    fx.g("merge", "-q", "--no-edit", "side")                 # doc.md changed only on side -> side wins
    fx.C["cm"] = fx.g("rev-parse", "HEAD").stdout.decode().strip()
    res = fx.audit()
    order = [sym(fx, x.split()[0]) for x in
             fx.g("rev-list", "--topo-order", "--reverse", "--parents", "HEAD").stdout.decode().strip().split("\n")]
    return check("C05a merge whose second parent deleted 30 lines (merge keeps them)", fx, res,
                 [{"commit": "c2", "file": "data/doc.md", "deleted": 30, "restored_max": 0,
                   "restored_best": None, "status": "unrestored"},
                  {"commit": "cm", "file": "data/doc.md", "deleted": 30, "restored_max": 0,
                   "restored_best": None, "status": "unrestored"}], 1,
                 "both events unrestored: after the merge the audited file holds 10 lines. The side commit is NOT credited with c3, which still holds all 40 lines, because topo-order puts c3 before it",
                 extra={"merge_parents": fx.g("rev-list", "--parents", "-1", "HEAD").stdout.decode().strip(),
                        "topo_order": order,
                        "lines_at_c3": fx.g("show", fx.C["c3"] + ":data/doc.md").stdout.count(b"\n"),
                        "lines_at_cm": fx.g("show", "HEAD:data/doc.md").stdout.count(b"\n")})


def c05b():
    fx = _merge_repo("c05b-merge-ours")
    fx.g("merge", "-q", "-s", "ours", "--no-edit", "side")
    fx.C["cm"] = fx.g("rev-parse", "HEAD").stdout.decode().strip()
    res = fx.audit()
    return check("C05b merge -s ours: side's 30-line deletion never lands", fx, res,
                 [{"commit": "c2", "file": "data/doc.md", "deleted": 30, "restored_max": 30,
                   "restored_best": "cm", "restored_by": "cm", "status": "restored"}], 0,
                 "the merge discards the side tree: no merge event; the side event is credited to cm, not to the c3 that already held all 40 lines",
                 extra={"merge_parents": fx.g("rev-list", "--parents", "-1", "HEAD").stdout.decode().strip()})


# ---------------------------------------------------------------- C06 60k
def c06():
    fx = Fx("c06-60k-lines")
    fx.w("README.md", b"append-only rules live here\n")
    big = lines("big", 60000)
    fx.w("data/big.md", nd(big))
    fx.w("data/other.md", b"a\n")
    fx.contract([("data/*.md", "A-corr", "README.md:1", "big")])
    fx.commit()
    fx.w("data/big.md", nd(big[30000:]))                     # delete the first 30000 lines
    c2 = fx.commit()
    for k in range(20):                                      # 20 distinct ~30k-line blobs in the window
        fx.w("data/big.md", nd(big[30000:] + [f"pad {k}"]))
        fx.commit()
    fx.w("data/big.md", nd(big))                             # full restoration
    fx.commit()                                              # c22
    fx.w("data/other.md", b"a\nb\n")
    fx.commit()
    res = fx.audit()
    rec = check("C06 60k-line file, 30000 deleted, 20 window commits, then restored", fx, res,
                [{"commit": "c2", "file": "data/big.md", "deleted": 30000, "restored_max": 30000,
                  "restored_best": "c23", "restored_by": "c23", "status": "restored"}], 0,
                "30000 deleted equals numstat; restoration only at the commit that puts all 60000 originals back")
    rec["commits_total"] = (res["obj"] or {}).get("commits")
    return rec


# ---------------------------------------------------------------- C07 CRLF
def c07a():
    fx = Fx("c07-crlf-lf-restore")
    fx.w("README.md", b"append-only rules live here\n")
    crlf = b"".join(f"crlf {i}\r\n".encode() for i in range(30))
    fx.w("data/crlf.md", crlf)
    fx.contract([("data/*.md", "A-corr", "README.md:1", "crlf")])
    fx.commit()
    fx.w("data/crlf.md", b"".join(f"crlf {i}\r\n".encode() for i in range(5)))   # 25 deleted
    c2 = fx.commit()
    fx.w("data/crlf.md", b"".join(f"crlf {i}\r\n".encode() for i in range(5))
         + b"".join(f"crlf {i}\n".encode() for i in range(5, 30)))
    fx.commit()
    res = fx.audit()
    return check("C07a CRLF file: 25 lines restored with LF endings", fx, res,
                 [{"commit": "c2", "file": "data/crlf.md", "deleted": 25, "restored_max": 0,
                   "restored_best": None, "restored_by": None, "status": "unrestored"}], 1,
                 "byte-exact identity: b'crlf N\\r' != b'crlf N', so an LF recopy restores nothing")


def c07b():
    fx = Fx("c07b-crlf-crlf-restore")
    fx.w("README.md", b"append-only rules live here\n")
    crlf = b"".join(f"crlf {i}\r\n".encode() for i in range(30))
    fx.w("data/crlf.md", crlf)
    fx.contract([("data/*.md", "A-corr", "README.md:1", "crlf")])
    fx.commit()
    fx.w("data/crlf.md", b"".join(f"crlf {i}\r\n".encode() for i in range(5)))
    c2 = fx.commit()
    fx.w("data/crlf.md", crlf)
    c3 = fx.commit()
    res = fx.audit()
    return check("C07b CRLF file: 25 lines restored with CRLF endings", fx, res,
                 [{"commit": "c2", "file": "data/crlf.md", "deleted": 25, "restored_max": 25,
                   "restored_best": "c3", "restored_by": "c3", "status": "restored"}], 0,
                 "identical CRLF lines count as restored (control for C07a)")


# ---------------------------------------------------------------- C08 no newline
def c08():
    fx = Fx("c08-no-newline-both")
    fx.w("README.md", b"append-only rules live here\n")
    # 31 logical lines, the last one without a newline
    fx.w("data/nonl.md", nd(lines("L", 5)) + nd(lines("F", 25)) + b"OLDLAST")
    fx.contract([("data/*.md", "A-corr", "README.md:1", "nonl")])
    c1 = fx.commit()
    fx.w("data/nonl.md", nd(lines("L", 5)) + b"NEWLAST")     # 26 deleted, 1 added, both sides end bare
    c2 = fx.commit()
    res = fx.audit()
    return check("C08 '\\ No newline at end of file' on both sides of a 26-deletion hunk", fx, res,
                 [{"commit": "c2", "file": "data/nonl.md", "deleted": 26, "restored_max": 0,
                   "status": "unrestored"}], 1,
                 "hunk header says 26 deletions (25 filler + the bare final line); the two '\\ No newline' markers must not be counted and must not swallow a real line",
                 extra={"diff": fx.diff(c1, c2, "data/nonl.md")})


def c08b():
    fx = Fx("c08b-newline-only-churn")
    fx.w("README.md", b"append-only rules live here\n")
    fx.w("data/nonl.md", nd(lines("L", 30)))                 # 30 lines, final newline present
    fx.contract([("data/*.md", "A-corr", "README.md:1", "nonl")])
    c1 = fx.commit()
    fx.w("data/nonl.md", nd(lines("L", 4)) + b"L line 4")    # 26 deleted; the last line loses its newline
    c2 = fx.commit()
    res = fx.audit()
    return check("C08b removing the final newline is counted as a deletion restored in the same commit", fx, res,
                 [{"commit": "c2", "file": "data/nonl.md", "deleted": 26, "restored_max": 1,
                   "status": "partial"}], 1,
                 "numstat also says 26 deletions / 1 addition: the '-L4'/'+L4' terminator pair contributes a deleted line whose text is present in the same commit, so held=1 at the event commit",
                 extra={"diff": fx.diff(c1, c2, "data/nonl.md")})


# ---------------------------------------------------------------- C09 patterns
def c09():
    fx = Fx("c09-contract-patterns")
    fx.w("README.md", b"append-only rules live here\n")
    for p in ["corpus/lessons/r1.md", "corpus/lessons/sub/r2.md", "docs/c[1].md"]:
        fx.w(p, nd(lines("x", 30)))
    fx.w("docs/b1.md", nd(lines("b", 30)))
    fx.w("docs/c1.md", nd(lines("c", 30)))
    fx.contract([("corpus/lessons/**/*.md", "A-corr", "README.md:1", "globstar"),
                 ("docs/c[1].md", "A-corr", "README.md:1", "literal bracket name"),
                 ("corpus/lessons/**/nomatch/*.md", "A-corr", "README.md:1", "matches nothing")])
    fx.commit()
    fx.w("corpus/lessons/r1.md", b"")                        # 30 lines deleted from the missed file
    c2 = fx.commit()
    res = fx.audit()
    t = sym(fx, "c2")
    return check("C09 contract patterns with ** and []", fx, res, [], 0,
                 "corpus/lessons/r1.md loses all 30 lines and is silent: '**' needs a directory level, '[1]' is a character class, the literal docs/c[1].md is never matched, and the zero-match row is accepted",
                 extra={"tree": sorted(p for p in fx.g("ls-tree", "-r", "--name-only", "HEAD").stdout.decode().split("\n") if p),
                        "numstat_r1": fx.numstat(fx.C["c1"], c2, "corpus/lessons/r1.md"),
                        "fnmatch_translate": {p: _translate(p) for p in
                                              ["corpus/lessons/**/*.md", "docs/c[1].md"]}})


def _translate(pat):
    import fnmatch
    return fnmatch.translate(pat)


# ---------------------------------------------------------------- C10 declared_at
def c10():
    fx = Fx("c10-declared-at-missing")
    fx.w("README.md", b"no declaration on this line\nsecond line\n")
    fx.w("data/doc.md", nd(lines("doc", 40)))
    fx.contract([("data/*.md", "A-corr", "MISSING.md:1", "declaration file absent"),
                 ("data/*.md", "A-corr", "README.md:999", "line beyond EOF"),
                 ("data/*.md", "A-corr", "README.md:2", "line exists, says nothing about append")])
    fx.commit()
    fx.w("data/doc.md", nd(lines("doc", 5)))                 # 35 deleted, file stays in the tree
    c2 = fx.commit()
    res = fx.audit()
    return check("C10 contract declared_at that resolves to nothing", fx, res,
                 [{"commit": "c2", "file": "data/doc.md", "deleted": 35, "restored_max": 0,
                   "status": "unrestored"}], 1,
                 "the tool audits normally and never resolves declared_at; the counter's contract leg rejects all three rows",
                 extra={"counter": counter_view(fx)})


def c10b():
    fx = Fx("c10b-declared-at-malformed")
    fx.w("README.md", b"append-only rules live here\n")
    fx.w("data/doc.md", nd(lines("doc", 30)))
    fx.contract([("data/*.md", "A-corr", "README.md", "no line number")])
    fx.commit()
    res = fx.audit()
    return check("C10b contract declared_at without :line", fx, res, [], 2,
                 "the tool refuses the contract (exit 2); the counter records a prob",
                 extra={"counter": counter_view(fx)})


def c11():
    fx = Fx("c11-crlf-contract")
    fx.w("README.md", b"append-only rules live here\n")
    fx.w("data/doc.md", nd(lines("doc", 30)))
    fx.contract([("data/*.md", "A-corr", "README.md:1", "crlf contract")], crlf=True)
    fx.commit()
    fx.w("data/doc.md", nd(lines("doc", 3)))                 # 27 deleted
    c2 = fx.commit()
    res = fx.audit()
    return check("C11 contract written with CRLF line endings", fx, res,
                 [{"commit": "c2", "file": "data/doc.md", "deleted": 27, "restored_max": 0,
                   "status": "unrestored"}], 1,
                 "the tool rstrips \\r on the header and strips cells, so it accepts a CRLF contract; the counter compares the header byte-exact and rejects it",
                 extra={"counter": counter_view(fx),
                        "header_bytes": repr(open(os.path.join(fx.d, "registry/append-only-contract.tsv"), "rb").readline())})


def c12():
    fx = Fx("c12-contract-absent")
    fx.w("data/doc.md", nd(lines("doc", 30)))
    fx.commit()
    fx.w("data/doc.md", nd(lines("doc", 3)))
    fx.commit()
    res = fx.audit()
    return check("C12 contract absent at the audited tip", fx, res, [], 2,
                 "the tool exits 2 (could-not-evaluate); the counter reports contract=0 'absent at tip'",
                 extra={"counter": counter_view(fx)})


# ---------------------------------------------------------------- C13 deleted at tip
def c13():
    fx = Fx("c13-file-deleted-at-tip")
    fx.w("README.md", b"append-only rules live here\n")
    fx.w("data/doc.md", nd(lines("doc", 40)))
    fx.contract([("data/*.md", "A-corr", "README.md:1", "doc")])
    fx.commit()
    fx.rm("data/doc.md")
    c2 = fx.commit()
    res = fx.audit()
    ctl = fx.audit_files(["data/doc.md"])
    return check("C13 declared file deleted and left deleted (the violation the audit exists for)", fx, res, [], 0,
                 "40 lines deleted and the file is absent at the tip, so the contract expansion does not contain it: 0 events, exit 0. The same repo with --files data/doc.md reports the event as unrestored, exit 1",
                 extra={"numstat_raw": fx.numstat(fx.C["c1"], c2, "data/doc.md"),
                        "control_files_run": {"rc": ctl["rc"], "events": ctl["obj"]["events"] if ctl["obj"] else None},
                        "summary": res["obj"].get("summary") if res["obj"] else None})


# ---------------------------------------------------------------- counter view
_COUNTER = None


def counter_mod():
    global _COUNTER
    if _COUNTER is None:
        spec = importlib.util.spec_from_file_location("c1counter", LANE_COUNTER)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _COUNTER = mod
    return _COUNTER


CITABLE = ("declared_at", "header", "absent at tip", "cells", "rule ", "no rows")


def counter_view(fx):
    if not LANE_COUNTER:
        return ["(counter path not supplied)"]
    try:
        m = counter_mod()
        tip = fx.g("rev-parse", "HEAD").stdout.decode().strip()
        detail = []
        ok, files = m.leg_contract(fx.d, tip, detail)
        return {"leg_contract_ok": ok, "files": files,
                "probs": [d for d in detail if any(k in d for k in CITABLE)],
                "all_prob_count": len(detail), "all_probs": detail[:12]}
    except Exception as e:  # noqa: BLE001
        return [f"counter raised {type(e).__name__}: {e}"]


def main():
    import shutil
    shutil.rmtree(os.path.join(SCRATCH, "fx"), ignore_errors=True)
    for fn in [c01, c02a, c02b, c03, c04, c05a, c05b, c06, c07a, c07b, c08, c08b, c09, c10, c10b, c11, c12, c13]:
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            import traceback
            RESULTS.append({"case": fn.__name__, "verdict": "DRIVER-ERROR",
                            "problems": [f"{type(e).__name__}: {e}", traceback.format_exc()[-1200:]]})
    with open(OUTJSON, "w", encoding="utf-8") as fh:
        json.dump(RESULTS, fh, indent=1)
    for r in RESULTS:
        print(f"{r['verdict']:22s} {r['case']}")
        for p in r.get("problems", []):
            print(f"    - {p}")
    print(f"{len(RESULTS)} cases -> {OUTJSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
