#!/usr/bin/env python3
"""M2Ctr summarizer: compares each mutant's (tip, ctl) normalized counter output
against the pristine patterns and assigns KILLED-TIP / KILLED-CTL / EXERCISED /
SURVIVED / INCONCLUSIVE verdicts, then diffs against preregistered predictions."""
import json
import os
import re

S = "/fast/scratch/hyaku/kama-r48/M2Ctr"
TIP = "380bcdff9c8af06997c482f6eb03db926a794a2b"
TS = re.compile(r"\d{4}-\d{2}-\d{2}T[\d:.]+(?:Z|[+-]\d{2}:\d{2})?")
FLAGS = re.compile(r"receipts=(\d) recordcheck=(\d) replay=(\d) compare=(\d) tamper=(\d) "
                   r"urlswap=(\d) newrow=(\d) replayed=(\d)/3 met=(True|False)")


def norm(text):
    out = []
    for ln in text.split("\n"):
        if ln.startswith("tip=") or re.match(r"^exit=\d+$", ln):
            continue
        ln = ln.split(" | ")[0]
        out.append(TS.sub("<TS>", ln))
    return "\n".join(out).strip()


def parse(rec):
    out = rec["stdout"]
    m = FLAGS.search(out.split("\n")[0]) if out else None
    return {"exit": rec["exit"], "flags": m.groups() if m else None,
            "detail": norm(out), "crash": not out.strip()}


def main():
    ledger = {}
    for ln in open(os.path.join(S, "ledger.jsonl")):
        r = json.loads(ln)
        ledger[r["tag"]] = r
    manifest = json.load(open(os.path.join(S, "mutants.json")))
    pris_tip = parse(ledger["M00-pristine@tip"])
    builder_ctl = open(os.path.join(S, "junk-c2-r47-relabel.c2.out")).read()
    pris_ctl = {"exit": 1, "flags": FLAGS.search(builder_ctl.split("\n")[0]).groups(),
                "detail": norm(builder_ctl), "crash": False}
    rows = []
    for m in manifest["mutants"]:
        mid = m["id"]
        t = parse(ledger[f"{mid}@tip"]) if f"{mid}@tip" in ledger else None
        c = parse(ledger[f"{mid}@ctl"]) if f"{mid}@ctl" in ledger else None
        if t is None or c is None or t["crash"] or c["crash"] or t["flags"] is None or c["flags"] is None:
            v = "INCONCLUSIVE-crash"
            why = f'tip_exit={t and t["exit"]} ctl_exit={c and c["exit"]} empty_stdout={bool(t and t["crash"]) or bool(c and c["crash"])}'
        elif t["exit"] != 0 or t["flags"] != pris_tip["flags"]:
            v, why = "KILLED-TIP", f"tip exit {t['exit']} vs 0 or flags {t['flags']} vs {pris_tip['flags']}"
        elif c["exit"] == 0 or c["flags"] != pris_ctl["flags"]:
            v, why = "KILLED-CTL", f"ctl exit {c['exit']} vs 1 or flags {c['flags']} vs {pris_ctl['flags']}"
        else:
            dt, dc = t["detail"] != pris_tip["detail"], c["detail"] != pris_ctl["detail"]
            if dt or dc:
                v, why = "EXERCISED", f"detail-only change tip={dt} ctl={dc}"
            else:
                v, why = "SURVIVED", "output identical to pristine on both targets"
        rows.append({"id": mid, "region": m["region"], "prediction": m["prediction"],
                     "verdict": v, "why": why, "match": v.split("-")[0] == m["prediction"].split("-")[0],
                     "tip": {"exit": t["exit"], "flags": t["flags"]}, "ctl": {"exit": c["exit"], "flags": c["flags"]},
                     "tip_detail": t["detail"], "ctl_detail": c["detail"]})
    with open(os.path.join(S, "verdicts.json"), "w") as fh:
        json.dump({"pristine_tip": pris_tip, "pristine_ctl": pris_ctl, "rows": rows}, fh, indent=1)
    n = {}
    for r in rows:
        n[r["verdict"]] = n.get(r["verdict"], 0) + 1
    print("verdicts:", n)
    for r in rows:
        flag = "OK " if r["match"] else "DIFF"
        print(f'{flag} {r["id"]:26s} pred={r["prediction"]:13s} got={r["verdict"]:18s} {r["why"][:100]}')


if __name__ == "__main__":
    main()
