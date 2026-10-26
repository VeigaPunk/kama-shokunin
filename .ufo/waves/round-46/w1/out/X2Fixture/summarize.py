#!/usr/bin/env python3
"""Render results.json + lane.json into evidence.md (X2Fixture receipts)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
rs = json.load(open(os.path.join(HERE, "results.json")))
lane = json.load(open(os.path.join(HERE, "lane.json")))


def ev(e):
    return (f"{e['commit'][:12]} {e['file']} deleted={e['deleted']} "
            f"restored_at_tip={e['restored_at_tip']} status={e['status']} "
            f"restored_by={(e['restored_by'] or '-')[:12]}")


out = ["# X2Fixture evidence (generated from results.json / lane.json)", ""]
out.append("tool = `python3 kama-shokunin/tools/append-only-audit.py --repo D --to <tip> --json`")
out.append("counter = `round46-append-audit-check.py :: recompute(D, <tip>)` (importlib, frozen)")
out.append("oracle = byte-exact: `git diff -U0` parsed positionally per file section, tip lines from "
           "`git cat-file blob` bytes without the phantom trailing empty element")
out.append("")
out.append("| case | tool rc | tool ev | counter ev | tool vs counter | tool vs oracle | counter vs oracle | both wrong |")
out.append("|---|---|---|---|---|---|---|---|")
for r in rs:
    out.append(f"| {r['case']} | {r['tool']['rc']} | {len(r['tool']['events'] or [])} | "
               f"{len(r['counter']['events'] or [])} | {r['tool_vs_counter']} | {r['tool_vs_oracle']} | "
               f"{r['counter_vs_oracle']} | {r['both_wrong_vs_oracle']} |")
out.append("")
for r in rs:
    out.append(f"## {r['case']}")
    out.append(f"- expectation: {r['expect']}")
    out.append(f"- fixture note: {r['note']}")
    out.append(f"- tool rc={r['tool']['rc']} events=" + (json.dumps(r['tool']['events']) if r['tool']['events'] is not None else "NONE (no JSON)"))
    out.append(f"- counter events=" + (json.dumps(r['counter']['events']) if r['counter']['events'] is not None else f"NONE error={r['counter']['error']}"))
    out.append("- oracle events=" + json.dumps(r["oracle"]["events"]) + f" binary={r['oracle']['binary']}")
    if r["tool"]["stderr"].strip():
        out.append("- tool stderr (tail): `" + r["tool"]["stderr"].strip().splitlines()[0][:200] + "`")
    for extra in ("numstat", "show_tree", "tip_bytes", "numstat_patch"):
        if extra in r:
            out.append(f"- {extra}: `{json.dumps(r[extra])[:1200]}`")
    out.append("")
out.append("# lane leg (read-only, lane HEAD)")
out.append(f"- to={lane['to']} tool_rc={lane['tool_rc']} counter_error={lane['counter_error']} "
           f"tool_vs_counter={lane['tool_vs_counter']} tool_events={lane['tool_events']} "
           f"counter_events={lane['counter_events']}")
out.append(f"- numstat_sweep_events={lane['numstat_sweep_events']} "
           f"in_counter_not_in_sweep={lane['in_counter_not_in_sweep']} "
           f"in_sweep_not_in_counter={lane['in_sweep_not_in_counter']} sweep_binary={lane['sweep_binary']}")
out.append(f"- tool_secs={lane['tool_secs']} counter_secs={lane['counter_secs']}")
out.append("")
out.append("| event (tool/counter) | byte-exact deleted | byte-exact restored | byte-exact status |")
out.append("|---|---|---|---|")
for e in lane["events"]:
    key = (e["commit"], e["file"])
    br = next((b for b in lane["byte_recheck"] if b["commit"] == key[0] and b["file"] == key[1]), None)
    out.append(f"| {ev(e)} | {br['deleted_bytes']} | {br['restored_bytes']} | {br['status_bytes']} |")
out.append("")
out.append("numstat per (commit,file) on the lane (no diff text involved):")
for k, v in lane["sweep"].items():
    out.append(f"- {k} deleted={v}")
with open(os.path.join(HERE, "evidence.md"), "w") as fh:
    fh.write("\n".join(out) + "\n")
print("\n".join(out[:12]))
print("wrote evidence.md")
