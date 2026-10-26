#!/usr/bin/env python3
"""V1Ctr: dump the frozen C1 counter's eleven fixture scenarios in full (tool JSON
events + summary + counter-recompute agreement), as evidence for the by-construction
re-derivation. Read-only on the lane; fixtures under the seat scratch."""
import importlib.util
import os
import shutil

spec = importlib.util.spec_from_file_location(
    "ctr", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round48-append-audit-v3-check.py")
ctr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ctr)
TOOL = "/fast/scratch/hyaku/kama-r48/V1Ctr/tool.py"
root = "/fast/scratch/hyaku/kama-r48/V1Ctr/scen"
shutil.rmtree(root, ignore_errors=True)
os.makedirs(root)
for name, repo, evs, summ, want_exit, nev in ctr.scenarios(root):
    code, j, err = ctr.run_tool(TOOL, repo, "HEAD")
    print(f"== {name}: exit {code} (want {want_exit}), events {len(j['events'])} (want {nev})")
    for e in j["events"]:
        print(f"   {e['commit'][:8]} {e['file']} del={e['deleted']} gr={e['graded']} ung={e['ungraded']} "
              f"rmax={e['restored_max']} rbest={(e['restored_best'] or '-')[:8]} rby={(e['restored_by'] or '-')[:8]} "
              f"held={e['held_at_to']} {e['status']}")
    print("   summary:", {k: v for k, v in j["summary"].items() if k in (
        "restored", "partial", "unrestored", "ungraded", "ungraded_lines", "regressed",
        "vanished", "bad_declarations")})
    rows, _ = ctr.parse_contract(open(os.path.join(repo, ctr.CONTRACT)).read())
    rc = ctr.recompute(repo, "HEAD", rows)
    mism = ctr.diff_result(j, rc, code, [], name)
    print("   counter-recompute mismatches:", mism)
shutil.rmtree(root, ignore_errors=True)
