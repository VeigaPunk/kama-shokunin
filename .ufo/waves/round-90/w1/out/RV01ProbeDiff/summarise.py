import json
R = json.load(open("results.json"))
rows = []
for k in sorted(R):
    v = R[k]
    if "error" in v:
        rows.append(f"{k} ERROR {v}")
        continue
    j, t = v["json"], v["table"]
    try:
        d = json.loads(j["stdout"])
        r = d["rows"][0] if "rows" in d else d["listeners"][0]
        jv = "verdict=%s reason=%s served=%r" % (r["verdict"], r["reason"], r["served_model"])
    except Exception as e:
        jv = "json-fail(%s)" % type(e).__name__
    rows.append("%-26s json_rc=%s table_rc=%s %s" % (k, j["rc"], t["rc"], jv))
open("summary.out", "w").write("\n".join(rows) + "\n")
print(len(rows), "rows")
