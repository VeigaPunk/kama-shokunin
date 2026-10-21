#!/usr/bin/env python3
"""Measure the OracleMissingSourceTree fixtures against the round-23 base
auditor and two labelled scratch derivatives of it.

Arms (all scratch copies; the repository file is never modified):
  base     tools/report-landing-audit.py as committed at the round-24 base
  lifted   base with the blanket promisor refusal removed (the r24 shape:
           promisor metadata alone no longer refuses)
  exempt   lifted plus a catch-and-pass around the SOURCES read, i.e. the
           "no-source exemption" shortcut that must not survive

Usage: measure_base_probes.py FIXTURE_ROOT OUT.json
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

BASE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/tools/"
             "report-landing-audit.py")
VARIANTS = ("A-corpus-tree-absent", "B-sources-blob-absent",
            "C-content-complete-control", "D-sources-path-never-committed",
            "E-tip-tree-absent")

PACK_REFUSAL = """        if rel == "objects/pack" and path.is_dir() and any(
                p.suffix == ".promisor" and p.with_suffix(".pack").exists()
                for p in path.iterdir()):
            raise EvalError(f"{repo}: partial clone (promisor pack)")
"""
CONFIG_REFUSAL = """        if key == "extensions.partialclone" or (
                re.fullmatch(r"remote\\..+\\.promisor", key)
                and git_bool(value)):
            raise EvalError(f"{repo}: partial clone ({key})")
"""
LOAD_CALL = "    source_urls = load_source_urls(lane_repo, tip)\n"
LOAD_EXEMPT = """    try:
        source_urls = load_source_urls(lane_repo, tip)
    except EvalError:
        source_urls = None
"""


def env():
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    return e


def derive(src, lifted):
    if not lifted:
        return src
    for block in (PACK_REFUSAL, CONFIG_REFUSAL):
        if block not in src:
            raise SystemExit("refusal block not found; base changed")
        src = src.replace(block, "")
    return src


def derive_exempt(src):
    if LOAD_CALL not in src:
        raise SystemExit("SOURCES load call not found; base changed")
    return src.replace(LOAD_CALL, LOAD_EXEMPT)


def run(auditor, lane, fleet):
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--no-errata",
            "--json"]
    p = subprocess.run(argv, capture_output=True, env=env(), timeout=120)
    out = {"exit": p.returncode}
    try:
        doc = json.loads(p.stdout)
        out["status"] = doc["summary"]["status"]
        out["kinds"] = sorted({d["kind"] for r in doc["results"]
                               for d in r["defects"]})
        out["tokens"] = sorted({d["token"] for r in doc["results"]
                                for d in r["defects"]})
        out["source_url_hashes"] = sorted(
            {h for r in doc["results"] for h in r["source_url_hashes"]})
        out["verdict_json"] = True
    except (ValueError, KeyError, TypeError):
        out["verdict_json"] = False
        out["stdout"] = p.stdout.decode(errors="replace")[:300]
    err = p.stderr.decode(errors="replace").strip()
    out["stderr"] = err[:400]
    out["traceback"] = "Traceback (most recent call last)" in err
    return out


def main(argv=None):
    argv = list(argv or sys.argv)
    if len(argv) < 3:
        print("usage: measure_base_probes.py FIXTURE_ROOT OUT.json",
              file=sys.stderr)
        return 2
    root, out_path = Path(argv[1]).resolve(), Path(argv[2]).resolve()
    src = BASE.read_text(encoding="utf-8")
    work = root / "auditors"
    work.mkdir(parents=True, exist_ok=True)
    arms = {}
    for arm, text in (("base", derive(src, False)),
                      ("lifted", derive(src, True)),
                      ("exempt", derive_exempt(derive(src, True)))):
        path = work / f"{arm}-audit.py"
        path.write_text(text, encoding="utf-8")
        arms[arm] = path
    doc = {"base_file": str(BASE), "fixtures": {}}
    for variant in VARIANTS:
        base = root / variant
        lane, fleet = base / "lane", base / "fleet"
        entry = {"lane": str(lane), "fleet": str(fleet), "arms": {}}
        for arm, path in arms.items():
            marker = base / "transport-ran"
            if marker.exists():
                marker.unlink()
            entry["arms"][arm] = run(path, lane, fleet)
            entry["arms"][arm]["transport_attempted"] = marker.exists()
        doc["fixtures"][variant] = entry
    out_path.write_text(json.dumps(doc, indent=1, sort_keys=True),
                        encoding="utf-8")
    print(json.dumps(doc, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
