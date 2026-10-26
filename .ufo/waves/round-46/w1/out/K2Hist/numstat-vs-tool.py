"""For each event the tool reports at --to <rev>, print git's own deletion count
(--numstat, first parent) next to the tool's `deleted` field."""
import json, subprocess, sys
repo, to = sys.argv[1], sys.argv[2]
tooljson = sys.argv[3]
events = json.load(open(tooljson))["events"]
bad = 0
for e in events:
    c, f = e["commit"], e["file"]
    par = subprocess.run(["git","-C",repo,"rev-parse",c+"^1"],capture_output=True,text=True).stdout.strip()
    out = subprocess.run(["git","-C",repo,"diff","--no-renames","--numstat",par,c,"--",f],
                         capture_output=True,text=True).stdout.split("\t")
    ns = int(out[1])
    mark = "MISMATCH" if ns != e["deleted"] else "ok"
    bad += ns != e["deleted"]
    print(f"{mark} {c[:12]} {f} numstat_deleted={ns} tool_deleted={e['deleted']} "
          f"delta={ns-e['deleted']}")
print(f"rows_mismatched={bad} of {len(events)}")
