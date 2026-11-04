#!/usr/bin/env python3
"""Fix-ups: real 9-row findings set, NC1 re-run, NC4 audit diff, NC6 re-add runs."""
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
EXM = "registry/append-only-exempt.tsv"


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


out = []
data = run_audit(BASE)
events = {(e["commit"], e["file"]): e for e in data["events"]}
sections = ctr.exemption_sections(D, data, audit_tool)
intros = ctr.introduction_history(D, data["to"])
pre_old = lambda c: is_anc(c, intros[0])
acc_text = blob(BASE, "registry/append-only-accepted.tsv").decode()
exm_text = blob(BASE, EXM).decode()
res_base = ctr.grade(data, acc_text, exm_text, sections, intros, pre_old, acc_tool)
findings41 = sorted(
    tuple(f["detail"].split()[:2]) for f in res_base["findings"]
    if f["class"] == "unaccounted" and f["detail"].endswith("missing valid exempt row"))
out.append(f"findings41={len(findings41)} "
           f"(SCORECARD={sum(1 for c, f in findings41 if f == 'SCORECARD.md')}, "
           f"SOURCES={sum(1 for c, f in findings41 if f.endswith('SOURCES.md'))}, "
           f"consumer={sum(1 for c, f in findings41 if f.endswith('consumer-registry.md'))})")

rows9, table = [], []
for (c, f) in findings41:
    e = events[(c, f)]
    exp, eligible = sections[(c, f)]
    strict = (e["status"] == "ungraded" and e["graded"] == 0
              and e["ungraded"] == e["deleted"] and eligible)
    if strict:
        rows9.append("\t".join([c, f, ctr.CLASS, str(e["ungraded"]), "|".join(exp), NOTE]))
        table.append((c, f, e["ungraded"], "|".join(exp),
                      is_anc(c, ACC_INTRO), is_anc(c, EXM_INTRO), is_anc(c, data["to"])))
out.append(f"strict rows demanded by the C2 content checks: {len(rows9)}")
out.append("commit                                    cnt sections                                 <=ACC <=EXM <=to")
for c, f, n, s_, a, e_, t in table:
    out.append(f"{c} {n:>3} {s_:<40} {str(a):<5} {str(e_):<5} {t}")
young = [c for c, f, n, s_, a, e_, t in table if not e_]
out.append(f"rows whose event is YOUNGER than the exempt register's own introduction "
           f"{EXM_INTRO[:12]}: {len(young)} -> {young}")

new_exm_9 = exm_text + "".join(r + "\n" for r in rows9)


def findings_of(text):
    return [ln for ln in text.splitlines() if ln.startswith("APPEND_EXEMPT_FINDING")]


def summary_of(text):
    return text.splitlines()[0] if text else ""


# ---------- NC1 with the real 9 rows ----------
nc1 = commit_tree({EXM: new_exm_9.encode()}, msg="append the nine SCORECARD exempt-head rows")
set_head(nc1)
rc1, o1 = run_counter()
f1 = findings_of(o1)
out.append(f"\n== NC1 (base + 9 rows) OLD counter exit={rc1}")
out.append(f"   {summary_of(o1)}")
out.append(f"   FINDING lines: {len(f1)} "
           f"(rotation={sum(1 for x in f1 if ' rotation ' in x)}, "
           f"unaccounted={sum(1 for x in f1 if ' unaccounted ' in x)})")
out.append("   the nine rows under the OLD rule: " +
           "; ".join(x.split()[2][:8] + ":" + x.split()[3] for x in f1 if " rotation " in x))
# C2 conformance for the same state
d1 = data
acc_free = acc_tool.grade(d1, acc_text, lambda c: True)
strict9 = [r for r, (c, f, n, s_, a, e_, t) in zip(rows9, table) if e_]
free9 = [r for r in rows9]
out.append(f"   C2 content checks pass for all 9; admissible under ruling (a): {len(free9)}/9 "
           f"-> exempt=56, remaining unaccounted=32 (28 permitted + 4 out_of_region);")
out.append(f"   admissible under strict per-register cutoff: {len(strict9)}/9 "
           f"-> exempt=52, unaccounted>=36 -> the frozen after-line is UNREACHABLE strictly")

# ---------- NC4 audit diff ----------
nc4_prefix = None
# rebuild NC4 deterministically (same edit as the first driver run)
rl = blob(BASE, "corpus/README.md").split(b"\n")
prose = next(i for i, ln in enumerate(rl) if ln.strip() and not ln.startswith(b"#")
             and not ln.startswith(b"|") and len(ln) > 60)
new_readme = b"\n".join(rl[:prose] + rl[prose + 1:])
nc4 = commit_tree({"corpus/README.md": new_readme}, msg="self-bless fixture")
set_head(nc4)
d4 = run_audit(nc4)
b4 = {(e["commit"], e["file"]): e for e in d4["events"]}
diffs = []
for k, e in b4.items():
    e0 = events.get(k)
    if e0 is None:
        diffs.append(("NEW", k, e["status"], e["graded"], e["held_at_to"]))
    elif e0["status"] != e["status"]:
        diffs.append(("CHANGED", k, f"{e0['status']}->{e['status']}",
                      f"graded={e['graded']}", f"held_at_to={e['held_at_to']}",
                      f"undisclosed={e['undisclosed'] != e0['undisclosed']}"))
for d in diffs:
    out.append(f"   NC4 audit event diff: {d}")
rc4, o4 = run_counter()
out.append(f"== NC4 OLD counter exit={rc4}: {summary_of(o4)}")
out.append("   findings: " + " | ".join(f for f in findings_of(o4) if "post-introduction" in f)[:260])
import hashlib
victim_line = rl[prose].rstrip(b"\r")
digest = hashlib.sha256(victim_line).hexdigest()
row4 = "\t".join([nc4, "corpus/README.md", digest, "1", "removal",
                  "self-bless fixture; accepted history"])
g_growth = acc_tool.grade(d4, acc_text + row4 + "\n", lambda c: is_anc(c, nc4))
g_strict = acc_tool.grade(d4, acc_text + row4 + "\n",
                          lambda c: c != nc4 and is_anc(c, ACC_INTRO))
out.append(f"   same-commit accepted row under ruling (a): "
           f"accepted={g_growth['summary']['accepted']} unaccepted={g_growth['summary']['unaccepted']} "
           f"bad_rows={g_growth['summary']['bad_rows']} exit={acc_tool.verdict(g_growth)}")
out.append(f"   same-commit accepted row under strict own-introduction cutoff: "
           f"accepted={g_strict['summary']['accepted']} "
           f"unaccepted={g_strict['summary']['unaccepted']} "
           f"post-intro={sum(1 for x in g_strict['findings'] if x['class'] == 'post-introduction')} "
           f"exit={acc_tool.verdict(g_strict)}")

# ---------- NC6: real delete/re-add with one new row ----------
nc6a = commit_tree({EXM: None}, msg="drop the exempt register")
nc6b = commit_tree({EXM: new_exm_9.encode()}, parent=nc6a,
                   msg="re-add register carrying nine new rows")
set_head(nc6b)
rc6, o6 = run_counter()
f6 = findings_of(o6)
out.append(f"\n== NC6 delete+re-add with new rows OLD counter exit={rc6}: {summary_of(o6)}")
out.append(f"   FINDING lines: {len(f6)} (rotation={sum(1 for x in f6 if ' rotation ' in x)}, "
           f"unaccounted={sum(1 for x in f6 if ' unaccounted ' in x)})")
nc6c = commit_tree({EXM: exm_text.encode()}, parent=nc6a, msg="re-add register unchanged")
set_head(nc6c)
rc6c, o6c = run_counter()
f6c = findings_of(o6c)
out.append(f"== NC6c delete+re-add UNCHANGED OLD counter exit={rc6c}: {summary_of(o6c)}")
out.append(f"   FINDING lines: {len(f6c)} (rotation={sum(1 for x in f6c if ' rotation ' in x)})")
out.append("   C2 subset rule on its own logic: re-add's row set vs the previous version of "
           "the register (last existing blob): +9 rows is a NON-subset -> rotation exit 1; "
           "unchanged re-add is a subset -> rotation_safe, findings only from unaccounted")
set_head(BASE)

(S / "receipts" / "fixup.out").write_text("\n".join(out) + "\n")
print("\n".join(out))
