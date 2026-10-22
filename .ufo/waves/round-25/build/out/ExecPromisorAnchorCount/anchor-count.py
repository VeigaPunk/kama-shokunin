#!/usr/bin/env python3
"""Count how often every promisor-mutant edit matches the lane auditor.

Read-only. It loads the frozen mutant table of
tests/report-audit/promisor-mutants.py and counts, for every edit of every
mutant, how many times the literal or the regular expression occurs in
tools/report-landing-audit.py at the lane base revision.

The counts follow the instrument's own apply rule (apply_mutation in
tests/report-audit/promisor-mutants.py):

  replace  source.count(old)            -- must be exactly 1
  regex    len(re.findall(pattern, source, re.DOTALL))  -- must be exactly 1
  insert   source.count(anchor)          -- must be exactly 1

The alternatives of a mutant are tried in order; the first one whose
count is exactly 1 is the applied alternative. A mutant with no such
alternative does not apply at all: the instrument reports it as
could-not-evaluate and it kills nothing.

No grid is run and no mutant is applied to any file.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

LANE = Path(__file__).resolve().parents[6]
INSTRUMENT = LANE / "tests/report-audit/promisor-mutants.py"
AUDIT_REL = "tools/report-landing-audit.py"


def load_instrument(path):
    spec = importlib.util.spec_from_file_location("promisor_mutants", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def base_auditor(clone, base, rel):
    """The auditor's bytes at the base revision, read out of the clone."""
    out = subprocess.run(
        ["git", "-C", str(clone), "show", f"{base}:{rel}"],
        capture_output=True, check=True)
    return out.stdout.decode("utf-8")


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def count_matches(source, alt):
    """The instrument's own count for one alternative."""
    if alt["kind"] == "replace":
        return source.count(alt["old"])
    if alt["kind"] == "regex":
        return len(re.findall(alt["pattern"], source, re.DOTALL))
    return source.count(alt["anchor"])


def compiles(source, name):
    try:
        compile(source, f"<{name}>", "exec")
        return True
    except SyntaxError:
        return False


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default="147f5bdd3228ab712520b5f377346cb2d9a64769")
    ap.add_argument("--clone", required=True,
                    help="a clone of the lane used to read the base revision")
    ap.add_argument("--instrument", default=str(INSTRUMENT))
    ap.add_argument("--out", required=True, help="write the report here")
    args = ap.parse_args(argv)

    module = load_instrument(Path(args.instrument))
    source = base_auditor(Path(args.clone), args.base, AUDIT_REL)

    rows = []
    stale_mutants = []
    for mutant in module.MUTANTS:
        counts = []
        for index, alt in enumerate(mutant["alternatives"]):
            if alt["kind"] == "replace":
                shown = alt["old"]
            elif alt["kind"] == "regex":
                shown = alt["pattern"]
            else:
                shown = alt["anchor"]
            counts.append({"index": index, "kind": alt["kind"],
                           "anchor_text": shown,
                           "matches": count_matches(source, alt)})
        applicable = [c["index"] for c in counts if c["matches"] == 1]
        chosen = applicable[0] if applicable else None
        stale_alternatives = [c for c in counts if c["matches"] != 1]
        row = {
            "mutant": mutant["id"],
            "execution": mutant["execution"],
            "alternatives": counts,
            "applicable_alternatives": applicable,
            "applied_alternative": chosen,
            "mutant_applies": chosen is not None,
            "stale_alternatives": stale_alternatives,
            "blocking": (mutant["execution"] != "review-only"
                          and chosen is None),
        }
        if chosen is not None:
            mutated, index = module.apply_mutation(source, mutant)
            row["mutant_compiles"] = (compiles(mutated, mutant["id"])
                                      if mutated is not None else False)
        else:
            row["mutant_compiles"] = None
        if row["blocking"]:
            stale_mutants.append(mutant["id"])
        rows.append(row)

    edits = [c for row in rows for c in row["alternatives"]]
    doc = {
        "measure": "match count of every promisor-mutant edit in "
                   f"{AUDIT_REL} at base {args.base}",
        "base": args.base,
        "auditor_sha256": digest(source),
        "auditor_bytes": len(source.encode("utf-8")),
        "instrument": str(args.instrument),
        "instrument_sha256": digest(Path(args.instrument).read_text(
            encoding="utf-8")),
        "mutants_total": len(module.MUTANTS),
        "mutants_executed": sum(1 for row in rows
                                if row["execution"] != "review-only"),
        "edits_total": len(edits),
        "edits_matching_exactly_once": sum(1 for c in edits
                                           if c["matches"] == 1),
        "edits_matching_zero_times": sum(1 for c in edits
                                         if c["matches"] == 0),
        "edits_matching_more_than_once": sum(1 for c in edits
                                             if c["matches"] > 1),
        "edits_matching_zero_times_detail": [
            {"mutant": row["mutant"], "index": c["index"],
             "kind": c["kind"], "anchor_text": c["anchor_text"]}
            for row in rows for c in row["alternatives"]
            if c["matches"] == 0],
        "mutants_with_no_applicable_alternative": stale_mutants,
        "answer_stale_anchors_present": bool(stale_mutants),
        "mutants": rows,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8")

    print(f"base {args.base}")
    print(f"auditor sha256 {doc['auditor_sha256']}")
    print(f"mutants {doc['mutants_total']}")
    for row in rows:
        marks = " ".join(f"[{c['index']}]{c['kind']}x{c['matches']}"
                         for c in row["alternatives"])
        if row["execution"] == "review-only":
            print(f"{row['mutant']}: review-only (no source assertion)")
            continue
        verdict = ("applies via alternative "
                   f"{row['applied_alternative']}, compiles="
                   f"{row['mutant_compiles']}"
                   if row["mutant_applies"]
                   else "NO ALTERNATIVE APPLIES (stale anchor)")
        print(f"{row['mutant']}: {marks} -> {verdict}")
    print(f"mutants with no applicable alternative: "
          f"{len(stale_mutants)} {stale_mutants}")
    print(f"edits total {doc['edits_total']}: exactly once "
          f"{doc['edits_matching_exactly_once']}, zero times "
          f"{doc['edits_matching_zero_times']}, more than once "
          f"{doc['edits_matching_more_than_once']}")
    for item in doc["edits_matching_zero_times_detail"]:
        print(f"  zero-match edit: {item['mutant']} alternative "
              f"{item['index']} ({item['kind']}): {item['anchor_text']!r}")
    print(f"stale anchors present: {doc['answer_stale_anchors_present']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
