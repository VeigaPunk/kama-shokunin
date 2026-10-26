#!/usr/bin/env python3
"""probe_preheading.py - does the tool grade a rewrite of lines that sit BEFORE the first `## `
heading, when the contract exempts some titled sections of the same file?

This is the exact shape of the round-48 build finding: SCORECARD.md:6, the round-45 authority
banner, sits before any `## ` heading and was rewritten in place by rounds 46-47.

Not one of the 27 selftest cases: it isolates `sections()` returning None. Prints the event and
the summary, so a mutant that exempts the pre-heading region is visible as status=ungraded.
"""
import argparse
import importlib.util
import json
import os
import sys
import tempfile


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tool", required=True)
    ap.add_argument("--scratch", required=True)
    a = ap.parse_args(argv)

    v = load(a.tool, "aoa_probe_" + str(abs(hash(a.tool)) % 10 ** 8))
    root = tempfile.mkdtemp(prefix="x1-prehead-", dir=a.scratch)
    NOTES = ["# notes", "score.md is append-only below its head.",
             "The ## Axes and ## Plan heads of score.md are re-derived in place."]
    ROW = "score.md\tA-corr\tNOTES.md:2\texempt=## Axes|## Plan@NOTES.md:3\tx"
    banner = [f"banner {i} {os.urandom(4).hex()}" for i in range(24)]
    keep = v.lines("h", 24)
    body = ["# score"] + banner + ["## Axes"] + keep + ["## Round 1"]
    f = v.Fixture(root)
    f.commit({"NOTES.md": NOTES, v.CONTRACT: [v.HEADER, ROW], "score.md": body})
    c = f.commit({"score.md": ["# score"] + [f"banner {i} new {os.urandom(4).hex()}" for i in range(24)]
                  + ["## Axes"] + keep + ["## Round 1"]})
    res = v.audit(f.d, c)
    print(json.dumps({"schema": v.SCHEMA, "events": res["events"], "summary": res["summary"],
                      "exit": v.exit_code(res)}, indent=1, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
