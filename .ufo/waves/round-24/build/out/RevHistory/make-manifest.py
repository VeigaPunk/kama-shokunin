#!/usr/bin/env python3
"""Build the round-24 historical-parity manifest (rounds 10-23).

Read-only: reads committed objects from the lane and fleet repositories and
records the exact committed inputs that determine the historical verdicts,
plus the byte digests of the base tool's outputs for those rounds.
"""
from __future__ import annotations

import hashlib
import re
import json
from pathlib import Path
import subprocess
import sys

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
FLEET = Path("/home/vgpnk/Projects/shokunin")
BASE = "0df800e896f6bce285a81e794ad4ae1d1e6c3a71"
ROUNDS = list(range(10, 24))


def git(repo, *args):
    p = subprocess.run(["git", "--no-optional-locks", "-C", str(repo), *args],
                       capture_output=True)
    if p.returncode:
        raise SystemExit(f"git {args} in {repo}: {p.stderr.decode()}")
    return p.stdout


def gits(repo, *args):
    return git(repo, *args).decode().strip()



def git_in(repo, *args, data=""):
    p = subprocess.run(["git", "--no-optional-locks", "-C", str(repo), *args],
                       input=data.encode(), capture_output=True)
    if p.returncode:
        raise SystemExit(f"git {args} in {repo}: {p.stderr.decode()}")
    return p.stdout

def blob_digest(repo, rev):
    data = git(repo, "cat-file", "blob", rev)
    return {"git_blob": gits(repo, "rev-parse", rev),
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data)}


def norm(path: Path, text: str) -> str:
    return text.replace(str(path), "<FLEET>")


man = {
    "generated_by": "make-manifest.py",
    "base_commit": BASE,
    "repos": {
        "lane": {"path": str(LANE),
                 "master_tip_at_base": gits(LANE, "rev-parse", f"{BASE}^{{commit}}"),
                 "master_tip_now": gits(LANE, "rev-parse", "refs/heads/master^{commit}")},
        "fleet": {"path": str(FLEET),
                  "head": gits(FLEET, "rev-parse", "HEAD^{commit}")},
    },
    "frozen_auditors": {
        "r23_base_for_round24_grid": dict(
            blob_digest(LANE, f"{BASE}:tools/report-landing-audit.py"),
            rev=BASE),
        "r22_base_for_historical_grid": dict(
            blob_digest(LANE, "4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py"),
            rev="4fe9339f8fc3a4a4a479d9c938a850da12f1124d"),
    },
    "lane_inputs": {
        "errata_ledger": blob_digest(LANE, f"{BASE}:registry/report-landing-errata.tsv"),
        "sources_registry": blob_digest(LANE, f"{BASE}:corpus/SOURCES.md"),
    },
    "repo_state": {},
    "rounds": [],
    "baseline_outputs": {},
}

for repo, key in ((LANE, "lane"), (FLEET, "fleet")):
    cfg = gits(repo, "config", "--list")
    man["repo_state"][key] = {
        "object_format": gits(repo, "rev-parse", "--show-object-format"),
        "is_shallow": gits(repo, "rev-parse", "--is-shallow-repository"),
        "show_prefix": gits(repo, "rev-parse", "--show-prefix"),
        "promisor_config_keys": sorted(
            line.split("=")[0] for line in cfg.splitlines()
            if "promisor" in line or "partialclone" in line),
        "promisor_pack_markers": sorted(
            p.name for p in (repo / ".git/objects/pack").glob("*.promisor")),
        "alternates": (repo / ".git/objects/info/alternates").exists(),
        "grafts": (repo / ".git/info/grafts").exists(),
    }

log = git(LANE, "log", "-z", "--format=%H%x00%an%x00%at%x00%s",
          f"{BASE}^{{commit}}").decode("utf-8", "surrogateescape")
fields = [f for f in log.split("\0") if f != ""]
lane_rows = []
for i in range(0, len(fields) - 3, 4):
    sha, author, atime, subject = fields[i:i + 4]
    lane_rows.append((sha, author, int(atime), subject))

for rnd in ROUNDS:
    rel = f".ufo/reports/round-{rnd}/kama.md"
    adds = gits(FLEET, "log", "--diff-filter=A", "--format=%H %at", "--", rel).splitlines()
    adds = [a for a in adds if a.strip()]
    report_blob = gits(FLEET, "rev-parse", f"HEAD:{rel}")
    pat = (f"round-{rnd}:", f"checkpoint(r{rnd})")
    commits = [{"sha": s, "author": a, "atime": t, "subject": su}
               for s, a, t, su in lane_rows
               if a == "kama-shokunin" and su.startswith(pat)]
    man["rounds"].append({
        "round": rnd,
        "fleet_report": rel,
        "fleet_report_blob": report_blob,
        "fleet_report_sha256": hashlib.sha256(
            git(FLEET, "cat-file", "blob", report_blob)).hexdigest(),
        "fleet_add_events": [{"commit": a.split()[0], "author_time": int(a.split()[1])}
                             for a in adds],
        "lane_round_commits": commits,
    })

out = Path(__file__).resolve().parent

# per-round expected verdicts (base tool, real repositories)
base_doc = json.loads((out / "base-10-23.json").read_text())
for res in base_doc["results"]:
    for entry in man["rounds"]:
        if entry["round"] == res["round"]:
            entry["expected_verdict"] = {
                "cutoff": res["cutoff"], "required": res["required"],
                "round_commits": res["round_commits"],
                "post_report": res["post_report"],
                "defects": res["defects"],
                "report_committed": res["report_committed"]}

# token universe of the historical range and the tokens absent from both repos
FULL = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{40}(?![0-9A-Za-z])")
tokens = set()
for entry in man["rounds"]:
    text = git(FLEET, "cat-file", "blob", entry["fleet_report_blob"]).decode(
        "utf-8", "surrogateescape")
    tokens |= set(FULL.findall(text))
present = {}
for repo, key in ((LANE, "lane"), (FLEET, "fleet")):
    q = git_in(repo, "cat-file", "--batch-check",
               data="".join(f"{t}\n" for t in sorted(tokens))).decode()
    st = {}
    for tok, line in zip(sorted(tokens), q.splitlines()):
        st[tok] = line.split(" ")[-1]
    present[key] = st
absent_both = sorted(t for t in tokens
                     if present["lane"][t] == "missing"
                     and present["fleet"][t] == "missing")
absent_lane = sorted(t for t in tokens
                     if present["lane"][t] == "missing"
                     and present["fleet"][t] != "missing")
absent_fleet = sorted(t for t in tokens
                      if present["fleet"][t] == "missing"
                      and present["lane"][t] != "missing")
man["token_universe"] = {
    "tokens": len(tokens), "absent_from_both": absent_both,
    "absent_from_lane_only": absent_lane, "absent_from_fleet_only": absent_fleet}


for name in ("base-10-23.json", "base-10-23.txt", "base-10-23-noerrata.json"):
    p = out / name
    raw = p.read_text()
    man["baseline_outputs"][name] = {
        "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        "sha256_path_normalized": hashlib.sha256(
            norm(FLEET, raw).encode()).hexdigest(),
        "bytes": len(p.read_bytes()),
    }

( out / "parity-manifest.json").write_text(json.dumps(man, indent=1, sort_keys=True) + "\n")
print("wrote", out / "parity-manifest.json")
