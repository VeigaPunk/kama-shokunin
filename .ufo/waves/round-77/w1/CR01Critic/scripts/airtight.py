#!/usr/bin/env python3
"""Airtight demonstrations against the LANDED counter:
A) exit 0 with a fresh graded deletion at the audited tip blessed by an
   uncommitted worktree accepted-register row naming the tip commit itself;
B) exit 0 with a same-commit head re-derivation blessed by an uncommitted
   worktree exempt-head row (9 strict rows + the self-bless row);
C) receipt rot: one extra row naming an event outside the --to audit flips the
   green receipt to exit 1 wrong-class."""
import hashlib
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r77/CR01Critic")
D = Path((S / "fixture-path.txt").read_text().strip())
BASE = "cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7"
EXM = "registry/append-only-exempt.tsv"
ACCP = "registry/append-only-accepted.tsv"
NOTE = "contract-exempt head re-derivation"
REG = D / "registry"


def git(*a, inp=None, check=True):
    p = subprocess.run(["git", "-C", str(D), *a], input=inp, capture_output=True)
    if check and p.returncode:
        raise RuntimeError(f"git {' '.join(a)[:80]}: {p.stderr.decode()[:300]}")
    return p


def top_assert():
    t = git("rev-parse", "--show-toplevel").stdout.decode().strip()
    assert os.path.realpath(t) == os.path.realpath(str(D)), f"toplevel {t} != {D}"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


audit_tool = load(D / "tools/append-only-audit.py", "aud")
ctr76 = load(D / "tools/round76-append-exempt.py", "ctr76")


def blob(rev, path):
    return git("show", f"{rev}:{path}").stdout


def commit_tree(edits, parent=BASE, msg="fixture"):
    top_assert()
    git("read-tree", parent + "^{tree}")
    for path, content in edits.items():
        b = git("hash-object", "-w", "--stdin", inp=content).stdout.decode().strip()
        git("update-index", "--add", "--cacheinfo", f"100644,{b},{path}")
    tree = git("write-tree").stdout.decode().strip()
    return git("commit-tree", tree, "-p", parent, "-m", msg).stdout.decode().strip()


def run_landed(to):
    p = subprocess.run([sys.executable, str(D / "tools/round77-append-registers.py"),
                        "--repo", str(D), "--to", to], capture_output=True, text=True)
    return p.returncode, p.stdout


def put_regs(acc, exm):
    REG.mkdir(parents=True, exist_ok=True)
    (REG / "append-only-accepted.tsv").write_bytes(acc)
    (REG / "append-only-exempt.tsv").write_bytes(exm)


acc_base = blob(BASE, ACCP)
exm_base = blob(BASE, EXM)
data = audit_tool.audit(str(D), to=BASE)
events = {(e["commit"], e["file"]): e for e in data["events"]}
sections = ctr76.exemption_sections(D, data, audit_tool)
intros = ctr76.introduction_history(D, data["to"])
res_base = ctr76.grade(data, acc_base.decode(), exm_base.decode(), sections, intros,
                       lambda c: ctr76.ancestor(D, c, intros[0]), load(D / "tools/round75-append-accepted.py", "acc"))
findings41 = sorted(tuple(f["detail"].split()[:2]) for f in res_base["findings"]
                    if f["class"] == "unaccounted" and f["detail"].endswith("missing valid exempt row"))
rows9 = []
for (c, f) in findings41:
    e = events[(c, f)]
    exp, eligible = sections[(c, f)]
    if (e["status"] == "ungraded" and e["graded"] == 0 and e["ungraded"] == e["deleted"]
            and eligible):
        rows9.append("\t".join([c, f, "exempt-head", str(e["ungraded"]), "|".join(exp), NOTE]))
new_exm_9 = (exm_base.decode() + "".join(r + "\n" for r in rows9)).encode()

out = []

# ---------- A: collision-free fresh deletion + same-commit uncommitted accepted row ----------
rl = blob(BASE, "corpus/README.md").split(b"\n")
candidates = [i for i, ln in enumerate(rl) if ln.strip() and not ln.startswith(b"#")
              and not ln.startswith(b"|") and len(ln) > 50]
hit = None
for i in candidates:
    new_readme = b"\n".join(rl[:i] + rl[i + 1:])
    tip = commit_tree({"corpus/README.md": new_readme}, msg="fresh graded deletion")
    d = audit_tool.audit(str(D), to=tip)
    summ = d["summary"]
    newev = [e for e in d["events"] if e["commit"] == tip]
    if not newev:
        continue
    if summ["restored"] == 95 and newev[0]["status"] == "unrestored" and newev[0]["graded"] == 1:
        hit = (tip, i, newev[0])
        break
if hit is None:
    out.append("A) no collision-free candidate found among README prose lines")
else:
    tip, lineno, ev = hit
    digest = hashlib.sha256(rl[lineno].rstrip(b"\r")).hexdigest()
    row = "\t".join([tip, "corpus/README.md", digest, str(ev["undisclosed"][0]["count"]),
                     ev["undisclosed"][0]["classes"][0],
                     "fresh graded deletion; accepted history"]) + "\n"
    put_regs(acc_base + row.encode(), exm_base)
    rc, so = run_landed(tip)
    out.append(f"A) fresh graded deletion of corpus/README.md line {lineno+1} at tip {tip[:12]}, "
               f"blessed by an UNCOMMITTED worktree accepted row naming the tip: exit={rc}")
    out.append("   " + (so.splitlines()[0] if so else ""))
    out.append("   findings: " + ("; ".join(so.splitlines()[1:4]) or "NONE"))

# ---------- B: same-commit head re-derivation + uncommitted exempt row, with the 9 rows ----------
sc = blob(BASE, "SCORECARD.md").split(b"\n")
ret = next(i for i, ln in enumerate(sc) if ln.startswith(b"## Retired"))
content = next(i for i in range(ret + 1, len(sc))
               if sc[i].strip() and not sc[i].startswith(b"## "))
new_sc = b"\n".join(sc[:content] + [b"re-derived replacement line"] + sc[content + 1:])
nb = commit_tree({"SCORECARD.md": new_sc}, msg="head re-derivation")
erow = "\t".join([nb, "SCORECARD.md", "exempt-head", "1", "## Retired",
                  "same-commit head re-derivation"]) + "\n"
put_regs(acc_base, (exm_base.decode() + "".join(r + "\n" for r in rows9) + erow).encode())
rc, so = run_landed(nb)
out.append(f"B) same-commit ## Retired re-derivation at {nb[:12]} + uncommitted exempt row "
           f"(plus the 9 strict rows): exit={rc}")
out.append("   " + (so.splitlines()[0] if so else ""))

# ---------- C: receipt rot - one extra row naming an event outside the --to audit ----------
lines = blob(BASE, "corpus/knowledge/consumer-registry.md").split(b"\n")
heading = next(i for i, ln in enumerate(lines) if ln.startswith(b"## Errata"))
victim = next(i for i in range(heading + 1, len(lines)) if lines[i].strip())
nc2 = commit_tree({"corpus/knowledge/consumer-registry.md":
                   b"\n".join(lines[:victim] + lines[victim + 1:])},
                  msg="delete one row inside ## Errata")
extra = "\t".join([nc2, "corpus/knowledge/consumer-registry.md", "exempt-head",
                   "1", "## Errata — 2026-10-14 re-census (append-only; rows below keep their round-1 text)",
                   "a future round's row"]) + "\n"
put_regs(acc_base, (exm_base.decode() + "".join(r + "\n" for r in rows9) + extra).encode())
rc, so = run_landed(BASE)
out.append(f"C) green registers + ONE row naming an event that exists only at a LATER tip "
           f"({nc2[:12]}), counting command pinned to --to {BASE[:12]}: exit={rc}")
out.append("   " + (so.splitlines()[0] if so else ""))
out.append("   " + (so.splitlines()[1] if len(so.splitlines()) > 1 else ""))

put_regs(acc_base, exm_base)
(S / "receipts" / "airtight.out").write_text("\n".join(out) + "\n")
print("\n".join(out))
