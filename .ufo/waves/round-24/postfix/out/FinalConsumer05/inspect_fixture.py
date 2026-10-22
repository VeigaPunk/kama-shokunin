#!/usr/bin/env python3
"""Independent inspection of the same-tag-both-stores fixture built by the
COMMITTED replay-v3 scenario() function, plus raw per-side tool output."""
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalConsumer05")
C = S / "clone"
DRV = C / ".ufo/waves/round-24/fixes/StoreLocalPresence/proof-driver-replay-v3.py"
BEFORE_COMMIT = "2e254a1763a9c08aa07fc53081287f506c447d84"
AFTER = C / "tools/report-landing-audit.py"

spec = importlib.util.spec_from_file_location("replay3", DRV)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

case = S / "fixture/case-same-tag-both-stores"
if case.exists():
    shutil.rmtree(case)
case.mkdir(parents=True)
lane, fleet, draft, errata = mod.scenario(str(case), "same-tag-both-stores")

out = {"driver_path": str(DRV),
       "driver_sha256": hashlib.sha256(DRV.read_bytes()).hexdigest(),
       "driver_lane_root": str(mod.LANE_ROOT),
       "lane": str(lane), "fleet": str(fleet),
       "draft": str(draft), "errata": None if errata is None else str(errata)}


def git(repo, *args):
    p = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch", "-C",
                        str(repo), *args], capture_output=True, timeout=30,
                       env={"GIT_CONFIG_GLOBAL": "/dev/null",
                            "GIT_CONFIG_NOSYSTEM": "1",
                            "PATH": "/usr/bin:/bin"})
    return {"rc": p.returncode,
            "out": p.stdout.decode("utf-8", "replace").strip(),
            "err": p.stderr.decode("utf-8", "replace").strip()}


# ---- the report draft the fixture cites -----------------------------------
text = Path(draft).read_text(encoding="utf-8")
out["draft_text"] = text
tokens = re.findall(r"`([0-9a-f]{40})`", text)
out["cited_tokens"] = tokens

# ---- the before side, extracted from the PINNED commit (never production) ---
raw = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch", "-C",
                      str(C), "show", f"{BEFORE_COMMIT}:tools/report-landing-audit.py"],
                     capture_output=True, timeout=30,
                     env={"GIT_CONFIG_GLOBAL": "/dev/null",
                          "GIT_CONFIG_NOSYSTEM": "1", "PATH": "/usr/bin:/bin"}).stdout
before_path = S / "out/before-report-landing-audit.py"
before_path.write_bytes(raw)
out["before_path"] = str(before_path)
out["before_sha256"] = hashlib.sha256(raw).hexdigest()
out["after_sha256"] = hashlib.sha256(AFTER.read_bytes()).hexdigest()

# ---- object types / presence in BOTH stores --------------------------------
objects = {}
for token in tokens:
    per = {}
    for label, repo in (("lane", lane), ("fleet", fleet)):
        t = git(repo, "cat-file", "-t", token)
        p = git(repo, "cat-file", "-p", token)
        per[label] = {"cat_file_t_rc": t["rc"], "type": t["out"] or t["err"][:160],
                      "cat_file_p_rc": p["rc"], "raw": p["out"][:600],
                      "err": p["err"][:160]}
        if per[label]["type"] == "tag":
            tgt = git(repo, "rev-parse", token + "^{}")  # may fail
            objline = git(repo, "cat-file", "tag", token)
            target = None
            for line in objline["out"].splitlines():
                if line.startswith("object "):
                    target = line.split(" ", 1)[1].strip()
            per[label]["tag_target_oid"] = target
            per[label]["tag_target_type_in_store"] = (
                git(repo, "cat-file", "-t", target)["out"]
                or git(repo, "cat-file", "-t", target)["err"][:160])
            per[label]["tag_target_peel_rc"] = tgt["rc"]
    objects[token] = per
out["objects"] = objects

# lane HEAD (the valid work commit cited in the draft)
out["lane_head"] = git(lane, "rev-parse", "HEAD")
out["fleet_head"] = git(fleet, "rev-parse", "HEAD")
out["lane_git_objects_path"] = git(lane, "rev-parse", "--git-path", "objects")
out["fleet_git_objects_path"] = git(fleet, "rev-parse", "--git-path", "objects")

# ---- raw per-side runs on this very fixture --------------------------------
def run(label, version, with_ledger):
    cmd = [sys.executable, str(version), "--lane-repo", str(lane),
           "--fleet-repo", str(fleet), "--branch", "master", "--rounds", "1",
           "--report", f"1={draft}", "--json"]
    cmd += ["--errata", str(errata)] if with_ledger else ["--no-errata"]
    p = subprocess.run(cmd, capture_output=True, timeout=60)
    rec = {"argv": cmd, "exit": p.returncode,
           "stdout": p.stdout.decode("utf-8", "replace"),
           "stderr": p.stderr.decode("utf-8", "replace")}
    (S / f"out/raw-{label}.stdout.txt").write_text(rec["stdout"], encoding="utf-8")
    (S / f"out/raw-{label}.stderr.txt").write_text(rec["stderr"], encoding="utf-8")
    try:
        doc = json.loads(rec["stdout"])
        rec["parsed"] = True
        rec["kinds"] = sorted({d["kind"] for res in doc["results"]
                               for d in res["defects"]})
        rec["summary_errata_invalid"] = doc["summary"].get("errata_invalid")
        rec["defects"] = [d for res in doc["results"] for d in res["defects"]]
        rec["summary"] = doc.get("summary")
        rec["results_count"] = len(doc.get("results", []))
    except Exception as exc:
        rec["parsed"] = False
        rec["parse_error"] = repr(exc)
    return rec


out["runs"] = {
    "before_with_ledger": run("before-ledger", before_path, errata is not None),
    "after_with_ledger": run("after-ledger", AFTER, errata is not None),
    "before_no_ledger": run("before-noledger", before_path, False),
    "after_no_ledger": run("after-noledger", AFTER, False),
}

(S / "out/fixture-inspection.json").write_text(
    json.dumps(out, indent=1, sort_keys=True), encoding="utf-8")
print(json.dumps(out, indent=1, sort_keys=True))
