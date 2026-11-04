#!/usr/bin/env python3
"""CR01Critic C2 falsification fixtures. All git writes happen in fixture $D
(toplevel-asserted before every write); the lane is only read."""
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
ACC_INTRO = "10f37171fb696c542586cbee96ea4a509ab74afc"
EXM_INTRO = "c2aa7fb2c02dd95a185b728d5863f9ae492ecef4"
NOTE = "contract-exempt head re-derivation"


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
ctr = load(D / "tools/round76-append-exempt.py", "ctr")


def run_audit(to):
    p = subprocess.run([sys.executable, str(D / "tools/append-only-audit.py"),
                        "--repo", str(D), "--to", to, "--json"],
                       capture_output=True, text=True)
    assert p.returncode in (0, 1), p.stderr
    return json.loads(p.stdout)


def run_counter():
    p = subprocess.run([sys.executable, str(D / "tools/round76-append-exempt.py"),
                        "--repo", str(D)], capture_output=True, text=True)
    return p.returncode, p.stdout


def set_head(c):
    top_assert()
    git("update-ref", "HEAD", c)


def is_anc(c, base):
    return subprocess.run(["git", "-C", str(D), "merge-base", "--is-ancestor", c, base],
                          capture_output=True).returncode == 0


def blob(rev, path):
    return git("show", f"{rev}:{path}").stdout


def commit_tree(edits, parent=BASE, msg="fixture"):
    """edits: {path: bytes|None} (None deletes the path). Fixture index plumbing only."""
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


EXM = "registry/append-only-exempt.tsv"
ACC = "registry/append-only-accepted.tsv"
exm_text = blob(BASE, EXM).decode()
acc_text = blob(BASE, ACC).decode()

out = []

# ---------- base facts ----------
data = run_audit(BASE)
events = {(e["commit"], e["file"]): e for e in data["events"]}
sections = ctr.exemption_sections(D, data, audit_tool)
intros = ctr.introduction_history(D, data["to"])
pre_old = lambda c, _i=intros[0]: is_anc(c, _i)
prior = acc_tool.grade(data, acc_text, pre_old)
res_base = ctr.grade(data, acc_text, exm_text, sections, intros, pre_old, acc_tool)
findings41 = sorted(
    tuple(f["detail"].split()[:2]) for f in res_base["findings"]
    if f["class"] == "unaccounted" and len(f["detail"].split()) == 2
    and len(f["detail"].split()[0]) == 40)
out.append(f"BASE counter: {ctr.render(res_base).splitlines()[0]}")
out.append(f"BASE findings41 = {len(findings41)} "
           f"(SCORECARD={sum(1 for c, f in findings41 if f == 'SCORECARD.md')}, "
           f"SOURCES={sum(1 for c, f in findings41 if f.endswith('SOURCES.md'))}, "
           f"consumer={sum(1 for c, f in findings41 if f.endswith('consumer-registry.md'))})")

# ---------- the nine strict rows (C2 content checks, both admissibility readings) ----------
rows9, table = [], []
for (c, f) in findings41:
    e = events[(c, f)]
    exp, eligible = sections[(c, f)]
    strict = (e["status"] == "ungraded" and e["graded"] == 0
              and e["ungraded"] == e["deleted"] and eligible)
    if strict:
        rows9.append("\t".join([c, f, ctr.CLASS, str(e["ungraded"]), "|".join(exp), NOTE]))
        table.append((c[:12], f.split("/")[-1], e["ungraded"], "|".join(exp),
                      is_anc(c, ACC_INTRO), is_anc(c, EXM_INTRO), is_anc(c, data["to"])))
out.append(f"strict rows demanded by C2 content checks: {len(rows9)}")
out.append("commit       file        cnt sections                 <=ACC(intro) <=EXM(intro) <=to")
for t in table:
    out.append(f"{t[0]} {t[1][:11]:<11} {t[2]:>3} {t[3]:<24} "
               f"{str(t[4]):<12} {str(t[5]):<12} {t[6]}")

new_exm_9 = exm_text + "".join(r + "\n" for r in rows9)

# ---------- NC1: append only the nine SCORECARD rows; old counter ----------
nc1 = commit_tree({EXM: new_exm_9.encode()}, msg="append the nine SCORECARD exempt-head rows")
set_head(nc1)
rc1, o1 = run_counter()
out.append(f"\n== NC1 (base + 9 rows), OLD counter, exit={rc1}")
out.append("\n".join(o1.strip().splitlines()[:3]))
old9 = [ln for ln in o1.splitlines() if "SCORECARD.md" in ln and "unaccounted" not in ln]
out.append(f"non-unaccounted findings on the 9 rows: {len([l for l in o1.splitlines() if 'rotation' in l or 'post-introduction' in l])} rotation/post-introduction lines")

# ---------- NC2: delete one line INSIDE ## Errata (consumer-registry.md) ----------
lines = blob(BASE, "corpus/knowledge/consumer-registry.md").split(b"\n")
heading = next(i for i, ln in enumerate(lines) if ln.startswith(b"## Errata"))
victim = next(i for i in range(heading + 1, len(lines)) if lines[i].strip())
inside_line = lines[victim]
new_cr = b"\n".join(lines[:victim] + lines[victim + 1:])
nc2 = commit_tree({"corpus/knowledge/consumer-registry.md": new_cr},
                  msg="delete one row inside the declared ## Errata region")
set_head(nc2)
d2 = run_audit(nc2)
ev2 = [e for e in d2["events"] if e["commit"] == nc2]
out.append(f"\n== NC2 deletion inside ## Errata (deleted line {victim+1}: {inside_line[:48]!r})")
for e in ev2:
    out.append(f"   audit: deleted={e['deleted']} graded={e['graded']} ungraded={e['ungraded']} "
               f"permitted={e['permitted']} status={e['status']} undisclosed={len(e['undisclosed'])}")
out.append(f"   C2 ruling (c): line sits INSIDE the only=## Errata region -> "
           f"out_of_region must NOT apply (graded={ev2[0]['graded']}>0); not exempt-head "
           f"(no exempt titles on this file), not permitted (A-corr file) -> class must be "
           f"unaccounted/finding without an accepted-register row")

# ---------- NC3: delete one line OUTSIDE ## Errata ----------
outside_victim = next(i for i, ln in enumerate(lines) if i < heading and ln.strip()
                      and not ln.startswith(b"#") and i > 2)
new_cr3 = b"\n".join(lines[:outside_victim] + lines[outside_victim + 1:])
nc3 = commit_tree({"corpus/knowledge/consumer-registry.md": new_cr3},
                  msg="delete one census line outside the declared ## Errata region")
set_head(nc3)
d3 = run_audit(nc3)
ev3 = [e for e in d3["events"] if e["commit"] == nc3]
out.append(f"\n== NC3 deletion outside ## Errata (deleted line {outside_victim+1})")
for e in ev3:
    out.append(f"   audit: deleted={e['deleted']} graded={e['graded']} ungraded={e['ungraded']} "
               f"permitted={e['permitted']} status={e['status']}")
out.append(f"   C2 ruling (c): every deleted line lies outside the declared region -> "
           f"out_of_region applies (graded={ev3[0]['graded']}==0, permitted==0)")

# ---------- NC4: self-blessing accepted register row for a fresh graded deletion ----------
rl = blob(BASE, "corpus/README.md").split(b"\n")
prose = next(i for i, ln in enumerate(rl) if ln.strip() and not ln.startswith(b"#")
             and not ln.startswith(b"|") and len(ln) > 60)
victim_line = rl[prose].rstrip(b"\r")
digest = hashlib.sha256(victim_line).hexdigest()
new_readme = b"\n".join(rl[:prose] + rl[prose + 1:])
row4 = "\t".join(["PARENTHASH", "corpus/README.md", digest, "1", "removal",
                  "placeholder; accepted history"])
nc4 = commit_tree({"corpus/README.md": new_readme}, msg="self-bless fixture")
row4 = row4.replace("PARENTHASH", nc4)
set_head(nc4)
rc4, o4 = run_counter()
out.append(f"\n== NC4 fresh graded deletion + same-commit accepted row (self-bless)")
out.append(f"   deleted corpus/README.md line {prose+1}: {victim_line[:60]!r}")
out.append(f"   OLD counter exit={rc4}: " + " | ".join(
    ln for ln in o4.splitlines() if "post-introduction" in ln or "rotation" in ln)[:300])
d4 = run_audit(nc4)
ev4 = [e for e in d4["events"] if e["commit"] == nc4][0]
out.append(f"   audit at NC4: graded={ev4['graded']} status={ev4['status']} "
           f"undisclosed={ev4['undisclosed']}")
g_strict = acc_tool.grade(d4, acc_text + row4 + "\n",
                          lambda c: c != nc4 and is_anc(c, ACC_INTRO))
g_growth = acc_tool.grade(d4, acc_text + row4 + "\n",
                          lambda c: is_anc(c, nc4))
g_old = acc_tool.grade(d4, acc_text, pre_old)
out.append(f"   accepted-tool under ruling (a) 'ancestor of audit revision': "
           f"accepted={g_growth['summary']['accepted']} unaccepted={g_growth['summary']['unaccepted']} "
           f"bad_rows={g_growth['summary']['bad_rows']} (the same-commit row is VALID)")
out.append(f"   accepted-tool under strict 'own introduction cutoff' (<= {ACC_INTRO[:12]}): "
           f"accepted={g_strict['summary']['accepted']} "
           f"post-introduction findings={sum(1 for f in g_strict['findings'] if f['class']=='post-introduction')}")
out.append(f"   base register alone at NC4 (old counter path): "
           f"unaccepted={g_old['summary']['unaccepted']} (finding exists as expected)")

# ---------- NC5: normal append (modify, not re-add) carrying one young row ----------
row5 = "\t".join(["461d2adbf2b3fe596a53cb392e2bc6e82af79bfb", "SCORECARD.md", ctr.CLASS,
                  str(events[("461d2adbf2b3fe596a53cb392e2bc6e82af79bfb", "SCORECARD.md")]["ungraded"]),
                  sections[("461d2adbf2b3fe596a53cb392e2bc6e82af79bfb", "SCORECARD.md")][0][0],
                  "normal growth append"])
nc5 = commit_tree({EXM: (exm_text + row5 + "\n").encode()}, msg="normal append of one growth row")
set_head(nc5)
rc5, o5 = run_counter()
out.append(f"\n== NC5 normal append with a young row, OLD counter exit={rc5}")
out.append("   " + " | ".join(ln for ln in o5.splitlines() if "rotation" in ln)[:220])
out.append("   introductions at NC5: " + str(ctr.introduction_history(D, nc5))[:120])
out.append("   C2 rule: append is a modification, --diff-filter=A unchanged -> no "
           "re-introduction -> rotation must NOT fire; ruling (a) admits the row")

# ---------- NC6: delete + re-add the register with one extra row ----------
nc6a = commit_tree({EXM: None}, msg="drop the exempt register")
nc6b = commit_tree({EXM: new_exm_9.encode()}, parent=nc6a, msg="re-add register with one new row")
set_head(nc6b)
rc6, o6 = run_counter()
out.append(f"\n== NC6 delete+re-add register carrying one new row, OLD counter exit={rc6}")
out.append("   " + " | ".join(ln for ln in o6.splitlines() if "rotation" in ln)[:220])
out.append(f"   introductions={len(ctr.introduction_history(D, nc6b))} (2 original + re-add)")
nc6c = commit_tree({EXM: exm_text.encode()}, parent=nc6a, msg="re-add register unchanged")
set_head(nc6c)
rc6c, o6c = run_counter()
out.append(f"== NC6c delete+re-add register UNCHANGED, OLD counter exit={rc6c}, "
           f"rotation findings={sum(1 for ln in o6c.splitlines() if 'rotation' in ln)}")
out.append("   C2 subset rule: re-add rows vs previous VERSION (last existing blob): "
           "9-row re-add is a non-subset -> rotation; unchanged re-add is a subset -> safe")

(S / "receipts" / "fixtures.out").write_text("\n".join(out) + "\n")
print("\n".join(out))
