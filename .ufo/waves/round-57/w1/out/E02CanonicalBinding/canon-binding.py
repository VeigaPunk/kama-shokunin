#!/usr/bin/env python3
"""canon-binding.py - seat E02CanonicalBinding prototype (round 57, operability side).

Question: can an instrument be causally bound to the lane's ACTUAL canonical
capability rows - the `**Capabilities - canonical list as of round N**` table of
SCORECARD.md at a revision - instead of to a typed literal or a row count?

Two modes, one source of truth (the tree at --tip / --root):

  audit   read the canonical table, and for every row bind its content:
          each backticked evidence token must resolve at the tip, its bytes must
          be read and hashed, and every `tools/*.py` token must EXECUTE at the tip
          (`--help`, exit 0, non-empty stdout). Emit one `row=` line per canonical
          row, so an omission cannot be summarised away: rows_bound must equal the
          number of rows the table actually has.

  verify  independently re-derive every fact from the same tree and compare to an
          instrument's `audit` output (--instrument-out). A summary that omits the
          canonical rows, or reports a digest/shape the tree does not support, is
          rejected (`rejected=1`, exit 1). This is the no-op omission control: a
          do-nothing instrument cannot fabricate canon_sha256 and the per-row
          digests without reading the table.

Legs (each failed leg adds 1 to mismatches):
  canon     a canonical capability heading exists and its table has >= 1 row
  evidence  every evidence path token of every row resolves at the tip
  content   every resolved evidence blob is non-empty (a declared path whose file
            is empty is a name, not content)
  exec      every distinct `tools/*.py` evidence token executes at the tip
            (exit 0, non-empty stdout) and at least one such token exists

Read-only on --repo (git show / cat-file only, GIT_* stripped); temporary
executables live under --scratch and are removed. Exit 0 met, 1 not met,
2 could not evaluate.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

CANON_RE = re.compile(r"canonical list as of round\s+(\d+)\*\*", re.I)
TOKEN_SKIP = set(" <>*$")


def clean_env():
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    return env


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, env=clean_env())


def sha(text):
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()


def canon_table(text):
    """Highest-numbered canonical heading and its contiguous table lines."""
    best, block, lines = -1, [], text.split("\n")
    for i, l in enumerate(lines):
        m = CANON_RE.search(l)
        if m and int(m.group(1)) > best:
            best = int(m.group(1))
            block = []
            for l2 in lines[i + 1:]:
                if l2.startswith("|"):
                    block.append(l2)
                elif block:
                    break
    return best, block


def rows_of(block):
    """Data rows of a markdown table (header + separator skipped)."""
    rows = []
    for l in block:
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        rows.append(cells)
    return rows[2:] if len(rows) >= 2 else []


def tokens_of(cell):
    out = []
    for tok in re.findall(r"`([^`]+)`", cell):
        if any(ch in tok for ch in TOKEN_SKIP):
            continue
        if "/" in tok or tok.endswith((".md", ".py", ".sh", ".tsv", ".json")):
            out.append(tok)
    return out


class Tree:
    """Uniform read surface: committed bytes at a tip, or a filesystem root."""

    def __init__(self, repo=None, tip=None, root=None, scratch=None):
        self.repo, self.tip, self.root = repo, tip, root
        self.scratch = scratch

    def show(self, path):
        if self.root is not None:
            p = os.path.join(self.root, path)
            if not os.path.isfile(p):
                return None
            with open(p, "rb") as f:
                return f.read().decode("utf-8", "replace")
        p = git(self.repo, "cat-file", "-p", f"{self.tip}:{path}")
        return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None

    def label(self):
        return self.tip if self.root is None else f"root={self.root}"


def derive(tree):
    """Every binding fact, derived from the tree alone."""
    facts = dict(canon_round=-1, canon_rows=0, canon_sha="", rows=[], evidence_total=0,
                 evidence_ok=0, content_ok=0, exec_total=0, exec_ok=0, tool_detail=[])
    sc = tree.show("SCORECARD.md")
    if sc is None:
        return facts, ["SCORECARD.md unreadable"]
    rnd, block = canon_table(sc)
    facts["canon_round"] = rnd
    if not block:
        return facts, ["no canonical capability heading"]
    table_text = "\n".join(block) + "\n"
    facts["canon_sha"] = sha(table_text)
    rows = rows_of(block)
    facts["canon_rows"] = len(rows)
    notes, exec_seen = [], {}
    ex_tmp = tempfile.mkdtemp(prefix="canon-exec-", dir=tree.scratch)
    try:
        for cells in rows:
            if len(cells) < 3:
                notes.append(f"short row {cells[:1]}")
                continue
            name = cells[0].strip("` *")
            toks = tokens_of(cells[2])
            ev_ok = ev_all = ct_ok = 0
            row_exec = [0, 0]
            for tok in toks:
                ev_all += 1
                body = tree.show(tok)
                if body is None:
                    notes.append(f"{name}: evidence missing {tok}")
                    continue
                ev_ok += 1
                if body.strip():
                    ct_ok += 1
                else:
                    notes.append(f"{name}: evidence empty {tok}")
                if re.match(r"^tools/.*\.py$", tok):
                    if tok not in exec_seen:
                        exec_seen[tok] = _exec(tree, tok, body, ex_tmp)
                    ok = exec_seen[tok]
                    row_exec[0] += int(ok)
                    row_exec[1] += 1
            facts["rows"].append({
                "name": name, "sha": sha("\t".join(cells))[:16],
                "ev_ok": ev_ok, "ev_total": ev_all, "content_ok": ct_ok,
                "exec_ok": row_exec[0], "exec_total": row_exec[1],
                "line": "|".join(cells)})
            facts["evidence_total"] += ev_all
            facts["evidence_ok"] += ev_ok
            facts["content_ok"] += ct_ok
            facts["exec_total"] += row_exec[1]
            facts["exec_ok"] += row_exec[0]
    finally:
        shutil.rmtree(ex_tmp, ignore_errors=True)
    facts["tool_detail"] = sorted(exec_seen.items())
    return facts, notes


def _exec(tree, token, body, tmpdir):
    """Execute a tip blob's bytes with --help; the leg is the exit, not the text."""
    dest = os.path.join(tmpdir, os.path.basename(token))
    with open(dest, "w") as f:
        f.write(body)
    try:
        p = subprocess.run([sys.executable, dest, "--help"], capture_output=True,
                           timeout=30, cwd=tmpdir, env=clean_env())
    except subprocess.TimeoutExpired:
        return False
    return p.returncode == 0 and bool(p.stdout.strip())


def legs(facts):
    c = dict(canon=0, evidence=0, content=0, exec=0)
    if facts["canon_round"] < 0 or facts["canon_rows"] == 0:
        c["canon"] += 1
    if all(r["ev_ok"] == r["ev_total"] for r in facts["rows"]) and facts["evidence_ok"] == facts["evidence_total"]:
        if facts["evidence_ok"] == 0:
            c["evidence"] += 1
    else:
        c["evidence"] += 1
    if facts["content_ok"] != facts["evidence_ok"]:
        c["content"] += 1
    if facts["exec_ok"] != facts["exec_total"] or facts["exec_total"] == 0:
        c["exec"] += 1
    return c, sum(c.values())


def audit_line(facts, c, mism, label, nonce=None):
    out = [f"tip={label}",
           f"canon_round={facts['canon_round']} canon_rows={facts['canon_rows']} "
           f"canon_sha256={facts['canon_sha'] or '-'}"]
    if nonce is not None:
        out.append(f"nonce={nonce}")
    for r in facts["rows"]:
        out.append(f"row={r['name']} ev={r['ev_ok']}/{r['ev_total']} "
                   f"ex={r['exec_ok']}/{r['exec_total']} content={r['content_ok']}/{r['ev_ok']} "
                   f"sha={r['sha']}")
    bound = sum(1 for r in facts["rows"] if r["ev_ok"] == r["ev_total"] and r["ev_total"])
    out.append(f"rows_bound={bound}/{facts['canon_rows']} evidence={facts['evidence_ok']}/{facts['evidence_total']} "
               f"content={facts['content_ok']}/{facts['evidence_total']} "
               f"exec={facts['exec_ok']}/{facts['exec_total']}")
    out.append(f"{' '.join(f'{k}={v}' for k, v in c.items())} mismatches={mism} met={mism == 0}")
    return "\n".join(out) + "\n"


def parse_instrument(path):
    """Facts an instrument CLAIMS. Anything absent stays absent (no defaulting)."""
    claim = dict(canon_round=None, canon_rows=None, canon_sha=None, rows={}, met=None,
                 evidence=None, exec_=None, bound=None, nonce=None)
    with open(path) as f:
        for l in f:
            l = l.rstrip("\n")
            m = re.match(r"^nonce=(\S+)$", l)
            if m:
                claim["nonce"] = m.group(1)
                continue
            m = re.match(r"^canon_round=(\S+) canon_rows=(\d+) canon_sha256=(\S+)$", l)
            if m:
                claim["canon_round"] = int(m.group(1))
                claim["canon_rows"] = int(m.group(2))
                claim["canon_sha"] = m.group(3)
                continue
            m = re.match(r"^row=(\S+) ev=(\d+)/(\d+) ex=(\d+)/(\d+) content=(\d+)/(\d+) sha=(\w+)$", l)
            if m:
                claim["rows"][m.group(1)] = (int(m.group(2)), int(m.group(3)), int(m.group(4)),
                                             int(m.group(5)), int(m.group(6)), int(m.group(7)),
                                             m.group(8))
                continue
            m = re.match(r"^rows_bound=(\d+)/(\d+) evidence=(\d+)/(\d+) content=(\d+)/(\d+) exec=(\d+)/(\d+)$", l)
            if m:
                claim["bound"] = int(m.group(1))
                claim["evidence"] = (int(m.group(3)), int(m.group(4)))
                claim["content_"] = (int(m.group(5)), int(m.group(6)))
                claim["exec_"] = (int(m.group(7)), int(m.group(8)))
                continue
            m = re.match(r"^.*\bmet=(True|False)$", l)
            if m:
                claim["met"] = m.group(1) == "True"
    return claim


def run_instrument(cmd, nonce, scratch):
    """Run the instrument afresh with a per-run nonce; a copied receipt cannot carry it."""
    argv = shlex.split(cmd) + ["--nonce", nonce]
    p = subprocess.run(argv, capture_output=True, timeout=300, cwd=scratch, env=clean_env())
    path = os.path.join(scratch, f"instrument-{nonce}.out")
    with open(path, "w") as f:
        f.write(p.stdout.decode("utf-8", "replace"))
    return path, p.returncode, p.stderr.decode("utf-8", "replace")


def verify(tree, instrument, nonce=None):
    facts, notes = derive(tree)
    c, mism = legs(facts)
    indep_met = mism == 0
    claim = parse_instrument(instrument)
    problems = []
    if nonce is not None and claim["nonce"] != nonce:
        problems.append(f"nonce claim {claim['nonce']} != run nonce {nonce}")
    if claim["canon_sha"] != facts["canon_sha"] or not facts["canon_sha"]:
        problems.append(f"canon_sha256 claim {claim['canon_sha']} != derived {facts['canon_sha'] or 'absent'}")
    if claim["canon_rows"] != facts["canon_rows"]:
        problems.append(f"canon_rows claim {claim['canon_rows']} != derived {facts['canon_rows']}")
    want = {r["name"]: (r["ev_ok"], r["ev_total"], r["exec_ok"], r["exec_total"],
                        r["content_ok"], r["ev_ok"], r["sha"]) for r in facts["rows"]}
    if claim["rows"] != want:
        missing = sorted(set(want) - set(claim["rows"]))
        extra = sorted(set(claim["rows"]) - set(want))
        differ = sorted(n for n in set(want) & set(claim["rows"]) if want[n] != claim["rows"][n])
        problems.append(f"row lines: missing={missing} extra={extra} differ={differ}")
    bound = sum(1 for r in facts["rows"] if r["ev_ok"] == r["ev_total"] and r["ev_total"])
    if claim["bound"] != bound:
        problems.append(f"rows_bound claim {claim['bound']} != derived {bound}")
    if claim["evidence"] != (facts["evidence_ok"], facts["evidence_total"]):
        problems.append(f"evidence claim {claim['evidence']} != derived "
                        f"({facts['evidence_ok']}, {facts['evidence_total']})")
    if claim["exec_"] != (facts["exec_ok"], facts["exec_total"]):
        problems.append(f"exec claim {claim['exec_']} != derived "
                        f"({facts['exec_ok']}, {facts['exec_total']})")
    if claim["met"] != indep_met:
        problems.append(f"instrument met={claim['met']} vs independently derived met={indep_met}")
    accepted = not problems
    out = [f"tip={tree.label()}", f"instrument={instrument}"]
    if nonce is not None:
        out.append(f"nonce={nonce}")
    out += [
           f"claims_met={claim['met']} tree_met={indep_met} "
           f"claimed_rows={len(claim['rows'])} derived_rows={facts['canon_rows']} "
           f"mismatches={len(problems)} rejected={int(not accepted)} accepted={int(accepted)}"]
    out += [f"detail: {p}" for p in problems]
    out += [f"detail: derive {n}" for n in notes]
    return accepted, "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("audit", "verify"))
    ap.add_argument("--repo")
    ap.add_argument("--tip")
    ap.add_argument("--root")
    ap.add_argument("--scratch")
    ap.add_argument("--instrument-out")
    ap.add_argument("--instrument-cmd")
    ap.add_argument("--nonce")
    ap.add_argument("--out")
    a = ap.parse_args()
    scratch = a.scratch or tempfile.mkdtemp(prefix="canon-bind-")
    os.makedirs(scratch, exist_ok=True)
    if (a.repo is None) == (a.root is None):
        print("could-not-evaluate: pass exactly one of --repo/--tip or --root")
        return 2
    try:
        if a.root is not None:
            tree = Tree(root=os.path.abspath(a.root), scratch=scratch)
        else:
            if not a.tip:
                print("could-not-evaluate: --repo needs --tip")
                return 2
            tip = git(a.repo, "rev-parse", "--verify", f"{a.tip}^{{commit}}")
            if tip.returncode:
                print("could-not-evaluate: invalid tip")
                return 2
            tree = Tree(repo=os.path.abspath(a.repo), tip=tip.stdout.decode().strip(),
                        scratch=scratch)
        if a.mode == "audit":
            facts, notes = derive(tree)
            c, mism = legs(facts)
            text = audit_line(facts, c, mism, tree.label(), a.nonce)
            text += "".join(f"detail: {n}\n" for n in notes)
            ok = mism == 0
        else:
            if bool(a.instrument_out) == bool(a.instrument_cmd):
                print("could-not-evaluate: verify needs exactly one of --instrument-out/--instrument-cmd")
                return 2
            nonce = None
            src = a.instrument_out
            if a.instrument_cmd:
                nonce = hashlib.sha256(os.urandom(16)).hexdigest()[:16]
                src, rc, err = run_instrument(a.instrument_cmd, nonce, scratch)
                if rc != 0:
                    print(f"detail: instrument exit={rc} stderr={err.strip()[:200]}")
            ok, text = verify(tree, src, nonce)
    except (RuntimeError, OSError, subprocess.SubprocessError, ValueError) as e:
        print(f"could-not-evaluate: {e}")
        return 2
    sys.stdout.write(text)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w") as f:
            f.write(text)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
