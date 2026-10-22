#!/usr/bin/env python3
"""FinalConsumer04: rebuild the driver's errata-fleet-only-blob fixture,
inspect the ACTUAL git object types/presence, and run both tool sides with
raw capture (with ledger / without ledger)."""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

SCRATCH = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalConsumer04")
CLONE = SCRATCH / "clone"
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/postfix/out/FinalConsumer04")
FIX = SCRATCH / "fixture"
BEFORE = SCRATCH / "tmp" / "before-report-landing-audit.py"
AFTER = CLONE / "tools" / "report-landing-audit.py"

GITENV = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
          "GIT_AUTHOR_NAME": "kama-shokunin", "GIT_COMMITTER_NAME": "kama-shokunin",
          "GIT_AUTHOR_EMAIL": "a@x", "GIT_COMMITTER_EMAIL": "a@x",
          "PATH": "/usr/bin:/bin"}


def git(repo, *args, stdin=None):
    out = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch", "-C", str(repo), *args],
                         input=None if stdin is None else stdin.encode(),
                         capture_output=True, env=GITENV, timeout=30)
    if out.returncode != 0:
        raise SystemExit(f"git {args} in {repo}: {out.stderr.decode()}")
    return out.stdout.decode()


def probe(repo, oid):
    """object type / presence / reachability inside one store"""
    t = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch", "-C", str(repo),
                        "cat-file", "-t", oid], capture_output=True, env=GITENV)
    present = t.returncode == 0
    typ = t.stdout.decode().strip() if present else None
    c = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch", "-C", str(repo),
                        "cat-file", "-e", oid], capture_output=True, env=GITENV)
    reachable = oid in git(repo, "rev-list", "--objects", "--all")
    loose = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch", "-C", str(repo),
                            "cat-file", "-s", oid], capture_output=True, env=GITENV)
    return {"store": str(repo), "type": typ, "cat_file_t_rc": t.returncode,
            "cat_file_e_rc": c.returncode, "present": present,
            "reachable_from_refs": reachable,
            "size": loose.stdout.decode().strip() if loose.returncode == 0 else None}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if FIX.exists():
        subprocess.run(["rm", "-rf", str(FIX)], check=True)
    lane, fleet = FIX / "lane", FIX / "fleet"
    for repo in (lane, fleet):
        repo.mkdir(parents=True)
        git(repo, "init", "-q", "-b", "master")
    (lane / "f").write_text("work\n", encoding="utf-8")
    git(lane, "add", "f")
    git(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: work")
    a = git(lane, "rev-parse", "HEAD").strip()
    report = fleet / ".ufo/reports/round-1/kama.md"
    report.parent.mkdir(parents=True)
    report.write_text("## Landed changes\n", encoding="utf-8")
    git(fleet, "add", ".ufo/reports/round-1/kama.md")
    git(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: kama report")
    fleet_commit = git(fleet, "rev-parse", "HEAD").strip()

    lane_blob = git(lane, "hash-object", "-w", "--stdin", stdin="known lane blob\n").strip()
    fleet_blob = git(fleet, "hash-object", "-w", "--stdin", stdin="other fleet blob\n").strip()
    draft = FIX / "draft.md"
    draft.write_text("## Landed changes\n- `" + a + "` work\n- `" + lane_blob
                     + "` under test\n", encoding="utf-8")
    errata = FIX / "errata.tsv"
    errata.write_text(f"1\tlanded-unresolved\t{lane_blob}\t{fleet_blob}\tev\n",
                      encoding="utf-8")

    facts = {
        "lane_commit_cited": a,
        "fleet_report_commit": fleet_commit,
        "cited_body_blob": lane_blob,
        "ledger_correction_blob": fleet_blob,
        "draft_text": draft.read_text(),
        "errata_text": errata.read_text(),
        "objects": {
            "cited_body_blob": {"lane": probe(lane, lane_blob), "fleet": probe(fleet, lane_blob)},
            "ledger_correction_blob": {"lane": probe(lane, fleet_blob), "fleet": probe(fleet, fleet_blob)},
            "lane_commit": {"lane": probe(lane, a), "fleet": probe(fleet, a)},
        },
        "tool_hashes": {
            "before": hashlib.sha256(BEFORE.read_bytes()).hexdigest(),
            "after": hashlib.sha256(AFTER.read_bytes()).hexdigest(),
        },
    }
    (OUT / "fixture-facts.json").write_text(json.dumps(facts, indent=1, sort_keys=True) + "\n")

    runs = []
    for side, tool in (("before", BEFORE), ("after", AFTER)):
        for mode in ("with-ledger", "no-ledger"):
            cmd = [sys.executable, str(tool), "--lane-repo", str(lane),
                   "--fleet-repo", str(fleet), "--branch", "master", "--rounds", "1",
                   "--report", f"1={draft}", "--json"]
            cmd += ["--errata", str(errata)] if mode == "with-ledger" else ["--no-errata"]
            proc = subprocess.run(cmd, capture_output=True, timeout=60,
                                  env={**os.environ, "TMPDIR": str(SCRATCH / "tmp")})
            rec = {"side": side, "mode": mode, "argv": cmd, "exit": proc.returncode,
                   "stdout_sha256": hashlib.sha256(proc.stdout).hexdigest(),
                   "stderr": proc.stderr.decode("utf-8", "replace")[-2000:]}
            try:
                doc = json.loads(proc.stdout.decode("utf-8", "replace"))
                rec["summary"] = doc.get("summary")
                rec["defects"] = [d for res in doc.get("results", []) for d in res.get("defects", [])]
                rec["errata_invalid_rows"] = doc.get("errata_invalid")
                rec["errata_unmatched_rows"] = doc.get("errata_unmatched")
            except Exception as exc:
                rec["json_error"] = repr(exc)
            name = f"{side}-{mode}.json"
            (OUT / name).write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
            (OUT / f"{side}-{mode}.stdout.txt").write_bytes(proc.stdout)
            (OUT / f"{side}-{mode}.stderr.txt").write_bytes(proc.stderr)
            runs.append({"side": side, "mode": mode, "exit": proc.returncode,
                         "kinds": sorted({d["kind"] for d in rec.get("defects", [])}),
                         "errata_invalid": (rec.get("summary") or {}).get("errata_invalid"),
                         "summary": rec.get("summary"),
                         "defects": rec.get("defects"),
                         "stderr_tail": rec["stderr"].strip().splitlines()[-1:] })
    (OUT / "raw-runs.json").write_text(json.dumps(runs, indent=1, sort_keys=True) + "\n")
    print(json.dumps(runs, indent=1, sort_keys=True))
    print("LANE_BLOB", lane_blob, "FLEET_BLOB", fleet_blob)
    return 0


if __name__ == "__main__":
    sys.exit(main())
