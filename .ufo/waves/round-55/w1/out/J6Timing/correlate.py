#!/usr/bin/env python3
"""J6Timing: join the flipper's per-replay log with each counter receipt's legs.

The counter emits the two-pass trip under the `code` prefix (the twopass leg is
computed from the code problems: any "two observation passes" problem fails both), so
the legs are derived from the detail text, not from the `twopass bN:` line (which only
appears when the passes agreed)."""
import json
import os
import re
from datetime import datetime

S = "/fast/scratch/hyaku/kama-r55/w1/J6Timing"


def ts(x):
    return datetime.fromisoformat(x.replace("Z", "+00:00"))


def legs_for(run, replay):
    path = os.path.join(S, "logs", f"mut{run}.out")
    res = {"code_trip": False, "twopass_trip": False, "rehash_trip": False,
           "twopass_line": None}
    if not os.path.isfile(path):
        return res
    for ln in open(path).read().splitlines():
        m = re.match(r"detail: (code|twopass|rehash) " + replay + r": (.*)", ln)
        if not m:
            continue
        kind, msg = m.group(1), m.group(2)
        if kind == "code":
            if "differ from the archive member" in msg:
                res["code_trip"] = True
            if "two observation passes" in msg:
                res["twopass_trip"] = True
        elif kind == "twopass":
            res["twopass_line"] = msg
        elif kind == "rehash" and "changed after the observation" in msg:
            res["rehash_trip"] = True
    return res


rows = []
for line in open(os.path.join(S, "j6-flip.log")):
    if not line.strip():
        continue
    e = json.loads(line)
    m = re.search(r"/run(\d+)/", e["tree"])
    k = re.search(r"/work-(b\d)/", e["tree"])
    if not m or not k:
        print("unmatched:", e["tree"])
        continue
    row = {"run": int(m.group(1)), "replay": k.group(1), "flips": e["flips"],
           "window_s": round((ts(e["stopped"]) - ts(e["started"])).total_seconds(), 3),
           "orig": e["orig"].get("libggml-cpu-zen4.so"),
           "final": e["final"].get("libggml-cpu-zen4.so")}
    row["left_flipped"] = row["final"] != row["orig"]
    row.update(legs_for(row["run"], row["replay"]))
    rows.append(row)
rows.sort(key=lambda r: (r["run"], r["replay"]))

print(f"{'run':>3} {'rp':>3} {'flips':>7} {'win_s':>6} {'left_fl':>7} "
      f"{'code':>5} {'twopass':>7} {'rehash':>6}")
for r in rows:
    print(f"{r['run']:>3} {r['replay']:>3} {r['flips']:>7} {r['window_s']:>6} "
          f"{str(r['left_flipped']):>7} {str(r['code_trip']):>5} "
          f"{str(r['twopass_trip']):>7} {str(r['rehash_trip']):>6}")

n = len(rows)
print(f"--- {n} replays ---")
for key in ("code_trip", "twopass_trip", "rehash_trip", "left_flipped"):
    t = sum(1 for r in rows if r[key])
    print(f"{key}: {t}/{n} ({100.0*t/n:.0f}%)")
clear = [r for r in rows if not (r["code_trip"] or r["twopass_trip"] or r["rehash_trip"])]
print("all-clear replays:", len(clear), [(r["run"], r["replay"]) for r in clear])
print("left_flipped == rehash_trip:", all(r["left_flipped"] == r["rehash_trip"] for r in rows))
print("twopass_trip subset of code_trip:",
      all((not r["twopass_trip"]) or r["code_trip"] for r in rows))
print("code-clean replays:", sum(1 for r in rows if not r["code_trip"]),
      "of which left flipped:", sum(1 for r in rows if not r["code_trip"] and r["left_flipped"]))
print("flip rate (min/median/max per s):",
      min(round(r["flips"]/r["window_s"]) for r in rows),
      sorted(round(r["flips"]/r["window_s"]) for r in rows)[n//2],
      max(round(r["flips"]/r["window_s"]) for r in rows))
json.dump(rows, open(os.path.join(S, "logs", "correlate.json"), "w"), indent=1, sort_keys=True)
