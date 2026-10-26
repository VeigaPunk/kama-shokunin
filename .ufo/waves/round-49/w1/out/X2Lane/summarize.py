#!/usr/bin/env python3
"""summarize.py - X2Lane (round 49) table builder for the v3-vs-v4 history sweep.

Inputs: runs/*.json written by the sweep driver (each holds the counter-side record
{tool, tip, contract, threshold, exit, raw, json}), the 8-tip selection in tips.json, and
the lane clone used for subjects / contract headers (path given as argv[1]).

Outputs: matrix.tsv, events.tsv in this directory. Read-only on the lane.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")


def lane_subject(lane, c):
    return subprocess.run(["git", "-C", lane, "show", "-s", "--format=%s", c],
                          capture_output=True, text=True).stdout.strip()


def contract_version(lane, c):
    p = subprocess.run(["git", "-C", lane, "show", f"{c}:registry/append-only-contract.tsv"],
                       capture_output=True, text=True)
    if p.returncode != 0:
        return "absent"
    head = p.stdout.split("\n")[0]
    n = len(head.split("\t"))
    return f"{n}-col" + (f" {len(p.stdout)}B" if n else "")


def main():
    lane = sys.argv[1]
    meta = json.load(open(os.path.join(HERE, "tips.json")))
    tips = meta["tips"]
    rows, events = [], []
    order = []
    for f in sorted(os.listdir(RUNS)):
        if not f.endswith(".json"):
            continue
        order.append((f, json.load(open(os.path.join(RUNS, f)))))
    for f, r in order:
        if "thr" in r:
            continue
        j = r["json"]
        s = (j or {}).get("summary")
        mode = "tip" if "_tipcontract" in f else "pinned"
        rows.append([
            f, r["tip"][:12], lane_subject(lane, r["tip"])[:60], contract_version(lane, r["tip"]),
            r["tool"].replace(".py", ""), mode, str(r["threshold"]), str(r["exit"]),
            "na" if not s else str(s["events"]),
            "na" if not s else str(sum(e["graded"] for e in j["events"])),
            "na" if not s else str(sum(e["deleted"] for e in j["events"])),
            "na" if not s else str(s["ungraded_lines"]),
            "na" if not s else f"{s['restored']}/{s['partial']}/{s['unrestored']}/{s['ungraded']}",
            "na" if not s else str(s["regressed"]),
            "na" if not s else str(s["bad_declarations"]),
            "" if s else (r["raw"] or r["stderr"]).strip().split("\n")[0][:120],
            j.get("schema", "") if j else "", (j or {}).get("definition", "none") if j else "",
        ])
        if s:
            for e in j["events"]:
                events.append([f, r["tool"].replace(".py", ""), mode, str(r["threshold"]),
                               e["commit"][:12], e["file"], str(e["deleted"]), str(e["graded"]),
                               str(e["ungraded"]), str(e["restored_max"]), str(e["held_at_to"]),
                               e["status"], ""])
    with open(os.path.join(HERE, "matrix.tsv"), "w") as fh:
        fh.write("\t".join(["run", "tip", "subject", "contract_at_tip", "tool", "contract_mode", "threshold",
                            "exit", "events", "graded", "deleted", "ungraded_lines",
                            "R/P/U/G", "regressed", "bad_decls", "could_not_evaluate", "schema",
                            "definition"]) + "\n")
        for r in rows:
            fh.write("\t".join(r) + "\n")
    # classify each event by (tool, mode, threshold, commit, file), then flag differences
    idx = {}
    for e in events:
        idx.setdefault((e[2], e[3], e[0].split("_")[1], e[4], e[5]), {})[e[1]] = e
    for key, pair in idx.items():
        if "v3" in pair and "v4" in pair:
            a, b = pair["v3"], pair["v4"]
            a[12] = "" if (a[7], a[8], a[11]) == (b[7], b[8], b[11]) else "DIFF"
            b[12] = a[12]
        elif "v3" in pair:
            pair["v3"][12] = "v4-missing"
        else:
            pair["v4"][12] = "v3-missing"
    with open(os.path.join(HERE, "events.tsv"), "w") as fh:
        fh.write("\t".join(["run", "tool", "contract_mode", "threshold", "commit", "file", "deleted",
                            "graded", "ungraded", "restored_max", "held_at_to", "status", "v3_v4"]) + "\n")
        for e in events:
            fh.write("\t".join(e) + "\n")
    print(f"matrix rows {len(rows)} event rows {len(events)} differing pairs "
          f"{sum(1 for e in events if e[12] == 'DIFF') // 2}")


if __name__ == "__main__":
    main()
