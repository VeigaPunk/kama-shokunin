#!/usr/bin/env python3
"""Extra discrimination controls for the after side (92063cf): does
errata_invalid track the resolvability/type of the correction token, or is it
hard-wired to this fixture?  Uses the same rebuilt fixture."""
import json
import os
import subprocess
import sys
from pathlib import Path

SCRATCH = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalConsumer04")
FIX = SCRATCH / "fixture"
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/postfix/out/FinalConsumer04")
AFTER = SCRATCH / "clone" / "tools" / "report-landing-audit.py"
BEFORE = SCRATCH / "tmp" / "before-report-landing-audit.py"
GITENV = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
          "PATH": "/usr/bin:/bin"}


def git(repo, *args, stdin=None):
    out = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch", "-C", str(repo), *args],
                         input=None if stdin is None else stdin.encode(),
                         capture_output=True, env=GITENV, timeout=30)
    if out.returncode != 0:
        raise SystemExit(f"git {args}: {out.stderr.decode()}")
    return out.stdout.decode()


def run(tool, lane, fleet, draft, errata_path):
    cmd = [sys.executable, str(tool), "--lane-repo", str(lane), "--fleet-repo", str(fleet),
           "--branch", "master", "--rounds", "1", "--report", f"1={draft}", "--json"]
    cmd += ["--errata", str(errata_path)] if errata_path else ["--no-errata"]
    p = subprocess.run(cmd, capture_output=True, timeout=60,
                       env={**os.environ, "TMPDIR": str(SCRATCH / "tmp")})
    rec = {"argv": cmd, "exit": p.returncode,
           "stderr_tail": p.stderr.decode("utf-8", "replace").strip().splitlines()[-1:]}
    try:
        doc = json.loads(p.stdout.decode("utf-8", "replace"))
        rec["summary"] = doc.get("summary")
        rec["defects"] = [d for r in doc.get("results", []) for d in r.get("defects", [])]
    except Exception as exc:
        rec["json_error"] = repr(exc)
    return rec


def main():
    lane, fleet = FIX / "lane", FIX / "fleet"
    draft = FIX / "draft.md"
    facts = json.loads((OUT / "fixture-facts.json").read_text())
    cited = facts["cited_body_blob"]
    a = facts["lane_commit_cited"]
    fleet_commit = facts["fleet_report_commit"]
    fleet_blob = facts["ledger_correction_blob"]
    lane_only_blob = git(lane, "hash-object", "-w", "--stdin", stdin="lane only control blob\n").strip()

    variants = {
        "V1-correction-lane-only-blob": lane_only_blob,
        "V2-correction-lane-commit": a,
        "V3-correction-fleet-commit": fleet_commit,
        "V4-correction-fleet-only-blob(replay)": fleet_blob,
    }
    rows = []
    for name, corr in variants.items():
        ep = FIX / f"errata-{name}.tsv"
        ep.write_text(f"1\tlanded-unresolved\t{cited}\t{corr}\tev\n", encoding="utf-8")
        for side, tool in (("before", BEFORE), ("after", AFTER)):
            rec = run(tool, lane, fleet, draft, ep)
            rec.update({"variant": name, "side": side, "correction": corr,
                        "correction_kind": git(lane, "cat-file", "-t", corr).strip()
                        if subprocess.run(["git", "-C", str(lane), "cat-file", "-e", corr],
                                          capture_output=True, env=GITENV).returncode == 0
                        else git(fleet, "cat-file", "-t", corr).strip()})
            rows.append(rec)
            (OUT / f"control-{name}-{side}.json").write_text(
                json.dumps(rec, indent=1, sort_keys=True) + "\n")
    (OUT / "control-variants.json").write_text(json.dumps(rows, indent=1, sort_keys=True) + "\n")
    for r in rows:
        s = r.get("summary") or {}
        print(f"{r['variant']:36s} {r['side']:6s} exit={r['exit']} "
              f"errata_invalid={s.get('errata_invalid')} "
              f"errata_unmatched={s.get('errata_unmatched')} "
              f"corrected={s.get('corrected')} uncorrected={s.get('uncorrected')} "
              f"status={s.get('status')} {r['stderr_tail']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
