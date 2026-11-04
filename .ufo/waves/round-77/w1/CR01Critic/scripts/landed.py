#!/usr/bin/env python3
"""Run the LANDED round77-append-registers.py against CR01 fixtures.
Registers are worktree files in $D (the landed counter reads them from the
working tree by design); all git writes are fixture plumbing, toplevel-asserted."""
import hashlib
import importlib.util
import json
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
acc_tool = load(D / "tools/round75-append-accepted.py", "acc")
ctr76 = load(D / "tools/round76-append-exempt.py", "ctr")
landed = load(D / "tools/round77-append-registers.py", "landed")


def blob(rev, path):
    return git("show", f"{rev}:{path}").stdout


def commit_tree(edits, parent=BASE, msg="fixture"):
    top_assert()
    git("read-tree", parent + "^{tree}")
    for path, content in edits.items():
        if content is None:
            git("update-index", "--force-remove", path)
        else:
            b = git("hash-object", "-w", "--stdin", inp=content).stdout.decode().strip()
            git("update-index", "--add", "--cacheinfo", f"100644,{b},{path}")
    tree = git("write-tree").stdout.decode().strip()
    return git("commit-tree", tree, "-p", parent, "-m", msg).stdout.decode().strip()


def run_landed(to):
    p = subprocess.run([sys.executable, str(D / "tools/round77-append-registers.py"),
                        "--repo", str(D), "--to", to], capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def put_regs(acc=None, exm=None):
    REG.mkdir(parents=True, exist_ok=True)
    (REG / "append-only-accepted.tsv").write_bytes(acc if acc is not None else acc_base)
    (REG / "append-only-exempt.tsv").write_bytes(exm if exm is not None else exm_base)


acc_base = blob(BASE, ACCP)
exm_base = blob(BASE, EXM)
data_base_lines = exm_base.decode().splitlines()
rows41 = None
out = []

# rebuild the deterministic fixture commits
rl = blob(BASE, "corpus/README.md").split(b"\n")
prose = next(i for i, ln in enumerate(rl) if ln.strip() and not ln.startswith(b"#")
             and not ln.startswith(b"|") and len(ln) > 60)
new_readme = b"\n".join(rl[:prose] + rl[prose + 1:])
nc4 = commit_tree({"corpus/README.md": new_readme}, msg="self-bless fixture")
digest = hashlib.sha256(rl[prose].rstrip(b"\r")).hexdigest()
row4 = "\t".join([nc4, "corpus/README.md", digest, "1", "removal",
                  "self-bless fixture; accepted history"]) + "\n"

lines = blob(BASE, "corpus/knowledge/consumer-registry.md").split(b"\n")
heading = next(i for i, ln in enumerate(lines) if ln.startswith(b"## Errata"))
victim = next(i for i in range(heading + 1, len(lines)) if lines[i].strip())
nc2 = commit_tree({"corpus/knowledge/consumer-registry.md":
                   b"\n".join(lines[:victim] + lines[victim + 1:])},
                  msg="delete one row inside ## Errata")
outside_victim = next(i for i, ln in enumerate(lines) if i < heading and ln.strip()
                      and not ln.startswith(b"#") and i > 2)
nc3 = commit_tree({"corpus/knowledge/consumer-registry.md":
                   b"\n".join(lines[:outside_victim] + lines[outside_victim + 1:])},
                  msg="delete one census line outside ## Errata")

# the 9 strict rows (recompute from the base audit)
data = audit_tool.audit(str(D), to=BASE)
events = {(e["commit"], e["file"]): e for e in data["events"]}
sections = ctr76.exemption_sections(D, data, audit_tool)
intros = ctr76.introduction_history(D, data["to"])
res_base = ctr76.grade(data, acc_base.decode(), exm_base.decode(), sections, intros,
                       lambda c: ctr76.ancestor(D, c, intros[0]), acc_tool)
findings41 = sorted(tuple(f["detail"].split()[:2]) for f in res_base["findings"]
                    if f["class"] == "unaccounted" and f["detail"].endswith("missing valid exempt row"))
rows9 = []
for (c, f) in findings41:
    e = events[(c, f)]
    exp, eligible = sections[(c, f)]
    if (e["status"] == "ungraded" and e["graded"] == 0 and e["ungraded"] == e["deleted"]
            and eligible):
        rows9.append("\t".join([c, f, "exempt-head", str(e["ungraded"]), "|".join(exp), NOTE]))
assert len(rows9) == 9, rows9
new_exm_9 = (exm_base.decode() + "".join(r + "\n" for r in rows9)).encode()

# exempt-register self-bless commit: same-commit ## Retired re-derivation
sc = blob(BASE, "SCORECARD.md").split(b"\n")
ret = next(i for i, ln in enumerate(sc) if ln.startswith(b"## Retired"))
content = next(i for i in range(ret + 1, len(sc))
               if sc[i].strip() and not sc[i].startswith(b"## "))
new_sc = b"\n".join(sc[:content] + [b"re-derived replacement line"] + sc[content + 1:])
nb = commit_tree({"SCORECARD.md": new_sc}, msg="head re-derivation")
erow = "\t".join([nb, "SCORECARD.md", "exempt-head", "1", "## Retired",
                  "same-commit head re-derivation"]) + "\n"

# rotation fixtures (rebuild)
nc6a = commit_tree({EXM: None}, msg="drop the exempt register")
nc6b = commit_tree({EXM: new_exm_9}, parent=nc6a, msg="re-add register with nine new rows")
nc6c = commit_tree({EXM: exm_base}, parent=nc6a, msg="re-add register unchanged")
row5 = "\t".join(["461d2adbf2b3fe596a53cb392e2bc6e82af79bfb", "SCORECARD.md", "exempt-head",
                  "1", "## Axes", "normal growth append"]) + "\n"
nc5 = commit_tree({EXM: (exm_base.decode() + row5).encode()}, msg="normal append of one growth row")


def case(name, to, acc=None, exm=None):
    put_regs(acc, exm)
    rc, so, se = run_landed(to)
    out.append(f"== {name}: --to {to[:12]} exit={rc}")
    out.append("   " + (so.splitlines()[0] if so else se))
    for ln in so.splitlines()[1:6]:
        out.append("   " + ln)
    return rc, so


out.append(f"fixture commits: nc4={nc4[:12]} nc2={nc2[:12]} nc3={nc3[:12]} "
           f"nb(exempt self-bless)={nb[:12]} nc5={nc5[:12]} nc6a={nc6a[:12]} "
           f"nc6b={nc6b[:12]} nc6c={nc6c[:12]}")

# 1. do-nothing control against the LANDED counter
case("do-nothing (BASE registers, --to BASE)", BASE)

# 2. the nine rows only (the claimed round's register work, no counter change)
case("nine strict rows appended, --to BASE", BASE,
     exm=new_exm_9)

# 3. ACCEPTED-register self-bless: fresh graded deletion at the audited tip,
#    blessed by an UNCOMMITTED worktree row naming the tip commit itself
case("ACCEPTED self-bless: fresh graded deletion + same-commit worktree row", nc4,
     acc=acc_base + row4.encode())

# 4. EXEMPT-register self-bless: same-commit head re-derivation + uncommitted row
case("EXEMPT self-bless: same-commit ## Retired re-derivation + worktree row", nb,
     exm=exm_base + erow.encode())

# 5. inside/outside ## Errata
case("deletion INSIDE ## Errata (must stay a finding)", nc2)
case("deletion OUTSIDE ## Errata (out_of_region class)", nc3)

# 6. rotation: normal append, re-add with new rows, re-add unchanged
case("normal append with one young row (must NOT be rotation)", nc5,
     exm=(exm_base.decode() + row5).encode())
case("delete + re-add with nine new rows (must be rotation)", nc6b,
     exm=new_exm_9)
case("delete + re-add unchanged (subset: must NOT be rotation)", nc6c,
     exm=exm_base)

put_regs()
(S / "receipts" / "landed.out").write_text("\n".join(out) + "\n")
print("\n".join(out))
