#!/usr/bin/env python3
"""FinalConsumer06 E3/E4: does an UNSELECTED row cause a REQUIRED READ?

The correction of the row is a hex-looking NAME that is also a ref in the
lane store.  Looking it up is a required read: `lookup()` refuses a
citation that a ref shadows ("citation <token> names a ref").

E3  the row is in an UNSELECTED round: the after must not read it, so the
    selected audit must not fail.  The before reads every row.
E4  the same row in the SELECTED round: both sides read it and refuse, so
    the lookup is not skipped for selected rows.
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalConsumer06")
CLONE = BASE / "clone"
DRIVER = CLONE / ".ufo/waves/round-24/fixes/StoreLocalPresence/proof-driver-replay-v3.py"
AFTER = CLONE / "tools/report-landing-audit.py"
BEFORE = BASE / "insp/before-report-landing-audit.py"
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/postfix/out/FinalConsumer06")
os.environ["TMPDIR"] = str(BASE / "tmp")
spec = importlib.util.spec_from_file_location("replay3", DRIVER)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
ENV = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
       "PATH": "/usr/bin:/bin", "GIT_AUTHOR_NAME": "kama-shokunin",
       "GIT_COMMITTER_NAME": "kama-shokunin", "GIT_AUTHOR_EMAIL": "a@x",
       "GIT_COMMITTER_EMAIL": "a@x"}
REFLIKE = "abcdef1"


def g(repo, *args):
    p = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch",
                        "-C", str(repo), *args],
                       capture_output=True, env=ENV)
    return {"rc": p.returncode, "out": p.stdout.decode("utf-8", "replace").strip(),
            "err": p.stderr.decode("utf-8", "replace").strip()}


def run_tool(tool, lane, fleet, draft, errata):
    cmd = [sys.executable, str(tool), "--lane-repo", str(lane),
           "--fleet-repo", str(fleet), "--branch", "master", "--rounds", "1",
           "--report", f"1={draft}", "--json"]
    cmd += ["--errata", str(errata)] if errata else ["--no-errata"]
    p = subprocess.run(cmd, capture_output=True, timeout=60)
    rec = {"argv": cmd, "exit": p.returncode,
           "stderr": p.stderr.decode("utf-8", "replace").strip()[:600]}
    try:
        rec["doc"] = json.loads(p.stdout.decode("utf-8", "replace"))
    except Exception:
        rec["stdout"] = p.stdout.decode("utf-8", "replace")[:1200]
    return rec


def summarise(rec):
    doc = rec.get("doc", {})
    return {"exit": rec["exit"], "stderr": rec["stderr"],
            "summary": doc.get("summary"),
            "kinds": sorted({d["kind"] for res in doc.get("results", [])
                             for d in res["defects"]}),
            "errata_invalid": doc.get("errata_invalid"),
            "errata_unmatched": doc.get("errata_unmatched")}


def fresh(tag):
    d = BASE / ("fx-" + tag)
    subprocess.run(["rm", "-rf", str(d)], check=True)
    d.mkdir(parents=True)
    lane, fleet, draft, errata = mod.scenario(d, "unselected-invalid-correction")
    # a hex-looking ref that shadows the object namespace in the lane store
    g(lane, "update-ref", "refs/heads/" + REFLIKE, "HEAD")
    return lane, fleet, draft, errata, d


out = {}
for label, rnd in (("E3_unselected_round_ref_shadowed_correction", "2"),
                   ("E4_selected_round_ref_shadowed_correction", "1")):
    lane, fleet, draft, errata, d = fresh(label)
    zero = "0" * 40
    errata.write_text(f"{rnd}\tunresolved-full-hash\t{zero}\t{REFLIKE}\tev\n",
                      encoding="utf-8")
    probe = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch",
                             "-C", str(lane), "cat-file", "--batch-check"],
                            input=(REFLIKE + "\n").encode(), capture_output=True,
                            env=ENV)
    out[label] = {
        "errata_text": errata.read_text(encoding="utf-8"),
        "draft_text": draft.read_text(encoding="utf-8"),
        "ref_exists": g(lane, "show-ref", "--verify", "refs/heads/" + REFLIKE),
        "batch_check_raw": {"rc": probe.returncode,
                            "out": probe.stdout.decode().strip(),
                            "err": probe.stderr.decode().strip()},
        "before": summarise(run_tool(BEFORE, lane, fleet, draft, errata)),
        "after": summarise(run_tool(AFTER, lane, fleet, draft, errata)),
        "after_no_ledger": summarise(run_tool(AFTER, lane, fleet, draft, None)),
        "before_no_ledger": summarise(run_tool(BEFORE, lane, fleet, draft, None)),
    }

(OUT / "experiments-E3-E4.json").write_text(json.dumps(out, indent=1, sort_keys=True),
                                             encoding="utf-8")
for label, v in out.items():
    print("==", label)
    print("   errata:", repr(v["errata_text"]))
    print("   batch-check raw:", v["batch_check_raw"])
    for side in ("before", "after", "before_no_ledger", "after_no_ledger"):
        s = v[side]
        print(f"   {side:17s} exit={s['exit']} kinds={s['kinds']} "
              f"invalid={len(s['errata_invalid'] or [])} "
              f"unmatched={len(s['errata_unmatched'] or [])} "
              f"status={(s['summary'] or {}).get('status')} "
              f"stderr={s['stderr'][:160]!r}")
