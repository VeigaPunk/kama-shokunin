#!/usr/bin/env python3
"""V1Ctr round-48 finding fixtures for the frozen C1 counter.

F1: the stable leg (counter lines 748-757) accepts a base whose every event has
    graded == 0 -- restored_max/restored_best then compare 0/None to 0/None.
    Nothing else in `met` requires any graded line: the lane verdict (719-720)
    needs only ungraded_lines > 0.
F2: the contract leg's REQUIRED check (680-689) looks up by_path (last row per
    pattern) while recompute (341-360) unions ALL matching rows; the tool
    (append-only-audit.py file_regions, lines 350-360) does the same union. A
    narrowing duplicate row placed before the required row therefore hides from
    REQUIRED and silently drops the file's grading, with tool == counter.
"""
import importlib.util
import json
import os
import sys

CTR = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round48-append-audit-v3-check.py"
S = "/fast/scratch/hyaku/kama-r48/V1Ctr"
TOOL = S + "/tool.py"

spec = importlib.util.spec_from_file_location("ctr", CTR)
ctr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ctr)

ok = True


def mybase(f, rows, files, notes):
    files = dict(files)
    files["NOTES.md"] = notes
    files[ctr.CONTRACT] = [ctr.HEADER] + rows
    return f.commit(files)

# ---------------------------------------------------------------- F1
root = S + "/f1"
os.makedirs(root, exist_ok=True)
f = ctr.Fx(root, "repo")
ROW = "ledger.md\tA\tNOTES.md:2\tonly=## Nope@NOTES.md:3\tfixture"
NOTES = ["# notes",
         "ledger.md is append-only: entries are appended.",
         "ledger.md is append-only; the ## Nope section is graded."]
base = mybase(f, [ROW], {"ledger.md": ctr.L("t", 40)}, NOTES)
c1 = f.commit({"ledger.md": ctr.L("b", 40)})   # rewrite all 40: deleted 40, graded 0 (no ## Nope section)
c2 = f.commit({"ledger.md": ctr.L("c", 40)})   # another rewrite: deleted 40, graded 0

cb, jb, _ = ctr.run_tool(TOOL, f.d, c1)
ct, jt, _ = ctr.run_tool(TOOL, f.d, "HEAD")
print("F1 tool exits:", cb, ct)
print("F1 base events:", [(e["commit"][:8], "graded", e["graded"], e["status"]) for e in jb["events"]])
print("F1 tip events:", [(e["commit"][:8], "graded", e["graded"], e["status"]) for e in jt["events"]])

# verbatim replica of counter lines 748-757
eb = {(e.get("commit"), e.get("file")): e for e in jb.get("events") or []}
et = {(e.get("commit"), e.get("file")): e for e in jt.get("events") or []}
stab = len(eb) >= 1
for k, e in eb.items():
    t = et.get(k)
    if t is None or not isinstance(e.get("graded"), int) or any(
            t.get(x) != e.get(x) for x in ("deleted", "graded", "ungraded", "restored_max", "restored_best")):
        stab = False
print("F1 stable-leg replica on all-graded-0 base:", stab)
assert stab is True, "F1 replica unexpectedly False"
assert all(e["graded"] == 0 for e in jb["events"]) and len(eb) >= 1

# lane-verdict replica on the same repo (counter lines 718-720)
rows, why = ctr.parse_contract(open(os.path.join(f.d, ctr.CONTRACT)).read())
assert rows is not None, why
rc = ctr.recompute(f.d, "HEAD", rows)
s = rc["summary"]
failures = s["partial"] + s["unrestored"]
verdict = (failures == 0 and s["regressed"] == 0 and s["vanished"] == 0
           and s["bad_declarations"] == 0 and s["ungraded_lines"] > 0 and rc["exit"] == 0)
mism = ctr.diff_result(jt, rc, ct, [], "f1")
print("F1 recompute summary:", s, "exit", rc["exit"])
print("F1 lane-verdict replica:", verdict, "tool-vs-counter mismatches:", mism)
assert verdict and mism == 0 and s["ungraded_lines"] > 0 and all(e["graded"] == 0 for e in rc["events"])
print("F1 CONFIRMED: stable leg + lane verdict satisfiable with zero graded lines\n")

# ---------------------------------------------------------------- F2
root = S + "/f2"
os.makedirs(root, exist_ok=True)
f = ctr.Fx(root, "repo")
NOTES = ["# notes",
         "LOG.md is append-only: entries are appended.",            # line 2: binds both LOG.md rows
         "LOG.md is append-only; the ## Nope section is graded."]   # line 3: only-pointer, names Nope
NARROW = "LOG.md\tA\tNOTES.md:2\tonly=## Nope@NOTES.md:3\tfixture"   # narrowing row, FIRST
REQSHAPE = "LOG.md\tA\tNOTES.md:2\t*\tfixture"                      # required-shape row, LAST
NOTES2 = ["# notes",
          "LOG.md is append-only: entries are appended.",            # line 2: binds both LOG.md rows
          "LOG.md is append-only; the ## Nope section is graded."]   # line 3: only-pointer, names Nope
base = mybase(f, [NARROW, REQSHAPE], {"LOG.md": ctr.L("t", 40)}, NOTES2)
c1 = f.commit({"LOG.md": ctr.L("b", 40)})   # rewrite all 40: deleted 40, graded 0

rows, why = ctr.parse_contract(open(os.path.join(f.d, ctr.CONTRACT)).read())
assert rows is not None, why
# verbatim replica of counter lines 680-689 (REQUIRED loop), REQUIRED["LOG.md"] = ("*",)
by_path = {r["path"]: r for r in rows}
want = ctr.REQUIRED["LOG.md"]
r = by_path.get("LOG.md")
reg = r["region"]
req_ok = want[0] == reg[0] and not (want[0] in ("exempt", "only") and reg[1] != want[1])
print("F2 REQUIRED-loop replica for LOG.md passes:", req_ok, "| by_path row region:", reg[0])
assert req_ok
for row in rows:
    okr, whyr = ctr.row_binds(f.d, "HEAD", row)
    assert okr, (row, whyr)
print("F2 both rows bind at tip: True")

rc = ctr.recompute(f.d, "HEAD", rows)
s = rc["summary"]
print("F2 recompute events:", [(e["deleted"], e["graded"], e["ungraded"], e["status"]) for e in rc["events"]],
      "exit", rc["exit"])
assert all(e["graded"] == 0 for e in rc["events"]) and rc["exit"] == 0

code, j, err = ctr.run_tool(TOOL, f.d, "HEAD", contract=os.path.join(f.d, ctr.CONTRACT))
mism = ctr.diff_result(j, rc, code, [], "f2")
print("F2 tool exit:", code, "| tool-vs-counter mismatches:", mism)
assert mism == 0, json.dumps(j, indent=1)[:800]

failures = s["partial"] + s["unrestored"]
verdict = (failures == 0 and s["regressed"] == 0 and s["vanished"] == 0
           and s["bad_declarations"] == 0 and s["ungraded_lines"] > 0 and rc["exit"] == 0)
print("F2 lane-verdict replica:", verdict, "| summary:", s)
assert verdict
print("F2 CONFIRMED: REQUIRED passes, LOG.md grading fully dropped, tool agrees, verdict met")

# control: same repo, ONLY the required-shape row -> grading restored
f2 = ctr.Fx(root, "ctrl")
base = ctr.base(f2, [REQSHAPE], {"LOG.md": ctr.L("t", 40)})
c1 = f2.commit({"LOG.md": ctr.L("b", 40)})
rows2, _ = ctr.parse_contract(open(os.path.join(f2.d, ctr.CONTRACT)).read())
rc2 = ctr.recompute(f2.d, "HEAD", rows2)
print("F2 control (single * row):", [(e["deleted"], e["graded"], e["status"]) for e in rc2["events"]],
      "exit", rc2["exit"])
assert all(e["graded"] == 40 for e in rc2["events"]) and rc2["exit"] == 1
print("F2 control CONFIRMED: without the duplicate the same deletion is graded 40, exit 1")
print("ALL FINDING FIXTURES CONFIRMED")
