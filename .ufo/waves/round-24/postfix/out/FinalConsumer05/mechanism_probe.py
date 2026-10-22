#!/usr/bin/env python3
"""Mechanism probe: the auditor's own lookup() classification of the
same-tag-both-stores citation, before vs after, on the exact fixture.

Determines the internal state ('found'|'wrongtype'|'unknown'|'absent')
that the CLI only exposes indirectly through the defect kind / refusal.
"""
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalConsumer05")
C = S / "clone"
AFTER = C / "tools/report-landing-audit.py"
BEFORE = S / "out/before-report-landing-audit.py"
CASE = S / "fixture/case-same-tag-both-stores"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(repo, *args):
    p = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch", "-C",
                        str(repo), *args], capture_output=True, timeout=30,
                       env={"GIT_CONFIG_GLOBAL": "/dev/null",
                            "GIT_CONFIG_NOSYSTEM": "1", "PATH": "/usr/bin:/bin"})
    return p.stdout.decode("utf-8", "replace").strip()


lane, fleet = CASE / "lane", CASE / "fleet"
draft = (CASE / "draft.md").read_text(encoding="utf-8")
tokens = re.findall(r"`([0-9a-f]{40})`", draft)
tag = tokens[-1]

tip = git(lane, "rev-parse", "master")
fleet_tip = git(fleet, "rev-parse", "HEAD^{commit}")

out = {"tokens": tokens, "tag": tag, "lane_tip": tip, "fleet_tip": fleet_tip}
for label, path in (("before", BEFORE), ("after", AFTER)):
    m = load("auditor_" + label, path)
    stores = (m.build_store(lane, tip), m.build_store(fleet, fleet_tip))
    rec = {"lookup_bare": m.lookup(stores, tokens),
           "lookup_peel_commit": m.lookup(stores, tokens, "^{commit}")}
    for i, st in enumerate(stores):
        try:
            missing, opaque = st.missing()
            rec[f"store{i}_path"] = str(st.path)
            rec[f"store{i}_missing"] = sorted(missing)
            rec[f"store{i}_opaque"] = sorted(opaque)
        except Exception as exc:
            rec[f"store{i}_missing_error"] = repr(exc)
    try:
        rec["unknown_citation"] = str(m.unknown_citation(stores, tag))
    except Exception as exc:
        rec["unknown_citation_error"] = repr(exc)
    out[label] = rec

(S / "out/mechanism-probe.json").write_text(
    json.dumps(out, indent=1, sort_keys=True), encoding="utf-8")
print(json.dumps(out, indent=1, sort_keys=True))
