#!/usr/bin/env python3
"""Replay the live tags/ps pairs through tools/kama-ollama-evidence.py for each name form."""
import json
import os
import subprocess
import sys

OUT = sys.argv[1]
TMP = os.environ["TMPDIR"]
TOOL = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-evidence.py"
rows = [json.loads(l) for l in open(os.path.join(OUT, "captures.jsonl"))]
by = {r["name"]: r for r in rows}
NAME, ALIAS, NAME2 = "kama-p02b-43f9adcc", "kama-p02b-43f9adcc-alias", "kama-p02b-43f9adcc-b"
UPPER = "P02UPPER"
EX = [NAME, f"{NAME}:latest", ALIAS, f"{ALIAS}:latest", NAME2, f"{NAME2}:latest",
      UPPER, f"{UPPER}:latest", UPPER.lower(), f"{UPPER.lower()}:latest",
      NAME.upper(), f"{NAME.upper()}:latest", "P02NoSuchModel", "kama-p02b-missing:latest"]
PS = ["ps-before", "ps-after-alias", "ps-after-name2", "ps-after-upper-lower"]

# raw capture facts
tags = json.loads(by["tags-all"]["body"])["models"]
print("tags_names", [m["name"] for m in tags])
print("tags_digests_equal", len({m["digest"] for m in tags}) == 1,
      "name_eq_model", all(m["name"] == m["model"] for m in tags),
      "digest", tags[0]["digest"])
print("sizes", [m["size"] for m in tags])
v1 = json.loads(by["v1-all"]["body"])
print("v1_ids", [d["id"] for d in v1["data"]], "owned_by", {d["owned_by"] for d in v1["data"]})
for p in PS:
    ms = json.loads(by[p]["body"])["models"]
    print(p, "entries", len(ms), [(m["name"], m["digest"][:12]) for m in ms])
for g in ("generate-ALIAS-unqualified", "generate-NAME2-unqualified", "generate-UPPER-unqualified"):
    b = json.loads(by[g]["body"])
    print(g, "status", by[g]["status"], "model_echo", b.get("model"), "eval_count", b.get("eval_count"),
          "done", b.get("done"), "response", repr(b.get("response")))
print("show_status", {n.split(":", 1)[1]: by[n]["status"] for n in by if n.startswith("show:")})
sh = json.loads(by["show:P02UPPER"]["body"])
print("show_upper_parent", sh["details"]["parent_model"], "template", repr(sh["template"]),
      "caps", sh.get("capabilities"))

# writes: two temp capture files, reused
tp = os.path.join(TMP, "tags-all.json")
pp = os.path.join(TMP, "ps.json")
open(tp, "w").write(by["tags-all"]["body"])
out = []
for ps in PS:
    open(pp, "w").write(by[ps]["body"])
    for ex in EX:
        p = subprocess.run([sys.executable, TOOL, "--tags", tp, "--ps", pp, "--expect", ex],
                           capture_output=True, text=True)
        try:
            j = json.loads(p.stdout)
        except ValueError:
            j = {}
        row = {"tags": "tags-all", "ps": ps, "expect": ex, "exit": p.returncode,
               "finding_id": j.get("finding_id"), "readiness": j.get("readiness"),
               "scope": j.get("scope"), "stderr": p.stderr[:200]}
        out.append(row)
        print(f"{ps:22s} expect={ex:28s} exit={p.returncode} {j.get('finding_id')}")
with open(os.path.join(OUT, "replay-matrix.jsonl"), "w") as f:
    for r in out:
        f.write(json.dumps(r, sort_keys=True) + "\n")
print("rows", len(out))
