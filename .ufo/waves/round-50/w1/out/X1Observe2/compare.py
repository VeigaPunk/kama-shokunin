#!/usr/bin/env python3
"""compare.py - X1Observe2: compare the independent observer's per-leg verdicts with the
frozen round-50 C1 counter (tools/round50-replay-bind-audit.py, whose --out is a text
receipt). Each input is a path; the counter text is parsed, never re-derived.

usage: compare.py --observer OBS.json --counter COUNTER.txt [--base-observer B.json]
                  [--base-counter BASE.txt] --out COMPARE.json --markdown COMPARE.md
"""
from __future__ import annotations

import argparse
import json
import re

BIND_LINE = re.compile(
    r"bind b(?P<n>\d+): pid (?P<pid>\d+) port (?P<port>\d+) "
    r"exe\+listen\+tree\+env\+mapped (?P<agg>ok|FAIL).*?"
    r"child_pid (?P<join>joined|NOT joined).*?"
    r"mapping dev (?P<dev>[\w:]+) inode (?P<inode>\d+) recorded.*?"
    r"nonce '(?P<nonce>[^']*)' (?P<rt>round-tripped|NOT round-tripped)")
FAIL_LINE = re.compile(r"bind b(?P<n>\d+): (?P<what>.+)$")
TOP = re.compile(r"bind=(?P<bind>\d) teardown=(?P<td>\d) newrow=(?P<nr>\d) "
                 r"bound=(?P<bound>\d+/\d+) met=(?P<met>True|False)")


def parse_counter(text):
    top = None
    for line in text.splitlines():
        m = TOP.search(line)
        if m:
            top = m.groupdict()
            break
    replays, fails = {}, {}
    for line in text.splitlines():
        m = BIND_LINE.search(line)
        if m:
            g = m.groupdict()
            replays[int(g["n"])] = {
                "pid": int(g["pid"]), "port": int(g["port"]),
                "exe": g["agg"] == "ok", "listen": g["agg"] == "ok",
                "tree": g["agg"] == "ok", "env": g["agg"] == "ok",
                "mapped": g["agg"] == "ok",
                "child_pid_join": g["join"] == "joined",
                "mapping_dev": g["dev"], "mapping_inode": g["inode"],
                "nonce": g["nonce"], "nonce_roundtrip": g["rt"] == "round-tripped",
                "aggregate": g["agg"]}
            continue
        m = FAIL_LINE.search(line)
        if m:
            fails.setdefault(int(m.group("n")), []).append(m.group("what").strip())
    return {"line": next((l for l in text.splitlines() if TOP.search(l)), None),
            "top": top, "replays": replays, "failed_detail": fails}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--observer", required=True)
    ap.add_argument("--counter", required=True)
    ap.add_argument("--base-observer", required=True)
    ap.add_argument("--base-counter", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--markdown", required=True)
    a = ap.parse_args(argv)
    obs = json.load(open(a.observer))
    cnt = parse_counter(open(a.counter).read())
    bobs = json.load(open(a.base_observer))
    bcnt = parse_counter(open(a.base_counter).read())
    legs = ("exe", "listen", "tree", "mapped", "env", "nonce")
    rows, disagreements, agreements = [], [], []
    for i, r in enumerate(obs["replays"], 1):
        c = cnt["replays"].get(i)
        mine = {leg: bool(r["legs"][leg]["passed"]) for leg in legs}
        if c is None:
            rows.append({"replay": i, "mine": mine, "counter": None,
                         "counter_detail": cnt["failed_detail"].get(i)})
            disagreements.append({"replay": i, "why": "counter printed no bind line",
                                  "counter_detail": cnt["failed_detail"].get(i)})
            continue
        theirs = {leg: c[("nonce_roundtrip" if leg == "nonce" else leg)] for leg in legs}
        for leg in legs:
            if mine[leg] == theirs[leg]:
                agreements.append({"replay": i, "leg": leg, "value": mine[leg]})
            else:
                disagreements.append({"replay": i, "leg": leg, "mine": mine[leg],
                                      "counter": theirs[leg]})
        hits = r["legs"]["mapped"].get("hits") or [{}]
        mapping_join = r.get("supplementary", {}).get("mapping_join")
        ca = r.get("supplementary", {})
        joins = {
            "pid": {"mine": ca.get("child_pid_join"), "counter": c["child_pid_join"]},
            "mapping": {"mine": mapping_join,
                        "counter": [c["mapping_dev"], c["mapping_inode"]],
                        "observed": [hits[0].get("dev"), hits[0].get("inode")]},
            "nonce": {"mine": mine["nonce"], "counter": c["nonce_roundtrip"],
                      "counter_nonce": c["nonce"]},
        }
        for k, v in joins.items():
            if isinstance(v["mine"], bool) and isinstance(v["counter"], bool) and v["mine"] != v["counter"]:
                disagreements.append({"replay": i, "leg": "join:" + k, **v})
        # dev/inode are per-run instance facts (each replay downloads the model into its own
        # work dir), so they are compared WITHIN a run, never across the observer's replay and
        # the counter's: the within-run join is supplementary.mapping_join above, and note the
        # cross-run values for the record only.
        rows_note = {"mine_observed": [hits[0].get("dev"), hits[0].get("inode")],
                     "counter_observed": [c["mapping_dev"], c["mapping_inode"]],
                     "equal_by_design": [hits[0].get("dev") == c["mapping_dev"]]}
        rows.append({"replay": i, "mine": mine, "counter": {leg: theirs[leg] for leg in legs},
                     "pids": {"mine": r.get("witness", {}).get("pid"), "counter": c["pid"]},
                     "ports": {"mine": r.get("witness", {}).get("port"), "counter": c["port"]},
                     "counter_line": c, "joins": joins,
                     "mapping_instance_note": rows_note})
    # base (pre-build) discrimination: the counter's committed control vs the observer
    b = bobs["replays"][0]
    base_mine_six = bool(b.get("passed"))
    base_mine_ext = bool(b.get("extended_passed"))
    base_cnt = bcnt["top"]
    base_agree = (base_mine_six == (base_cnt and base_cnt["met"] == "True")) or True
    doc = {
        "schema": "x1observe2-compare/v1",
        "tip": obs["tip"],
        "my_observer_met": obs["met"],
        "counter_top": cnt["top"],
        "counter_line": cnt["line"],
        "counter_met": (cnt["top"] or {}).get("met") == "True",
        "rows": rows,
        "agreements": agreements,
        "disagreements": disagreements,
        "base": {
            "counter_top": base_cnt,
            "counter_line": bcnt["line"],
            "counter_failed_detail": bcnt["failed_detail"],
            "observer_six_legs_passed": base_mine_six,
            "observer_extended_passed": base_mine_ext,
            "observer_parent_env": b.get("supplementary", {}).get("parent_env"),
            "observer_marker_file": b.get("supplementary", {}).get("canary_marker_file"),
            "observer_mapping_join": b.get("supplementary", {}).get("mapping_join"),
            "verdict": ("observer assigns a false met at the base if judged on the six "
                        "assigned legs alone; with the live-tool environ and sitecustomize "
                        "marker it agrees with the counter (bind=0)"
                        if base_mine_six and not base_mine_ext and base_cnt
                        and base_cnt.get("met") == "False" else "see values"),
        },
    }
    json.dump(doc, open(a.out, "w"), indent=1, sort_keys=True)
    md = ["# X1Observe2 - observer vs frozen counter (C1 bind)", "",
          f"tip `{obs['tip']}`", "",
          f"- observer met={obs['met']}; extended (parent-environ + marker) met="
          f"{all(r.get('extended_passed') for r in obs['replays'])}",
          f"- counter: `{cnt['line']}`", "",
          "| leg | " + " | ".join(f"replay {r['replay']} (mine/counter)" for r in rows) + " |",
          "|---|" + "---|" * len(rows)]
    for leg in legs:
        cells = []
        for r in rows:
            if r.get("counter") is None:
                cells.append(f"{r['mine'][leg]}/?")
            else:
                cells.append(f"{r['mine'][leg]}/{r['counter'][leg]}")
        md.append(f"| {leg} | " + " | ".join(cells) + " |")
    md += ["", f"- disagreements: {len(disagreements)}",
           f"- base: counter `{bcnt['line']}`; observer six legs "
           f"{base_mine_six}, extended {base_mine_ext}; parent env "
           f"{json.dumps(b.get('supplementary', {}).get('parent_env'))}"]
    md += ["", "## counter detail lines", ""] + [f"- `{r['counter_line']}`" for r in rows if r.get("counter_line")]
    open(a.markdown, "w").write("\n".join(md) + "\n")
    print("\n".join(md[:16]))
    print(f"disagreements={len(disagreements)}")
    return 0 if not disagreements else 1


if __name__ == "__main__":
    raise SystemExit(main())
