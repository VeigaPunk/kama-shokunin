#!/usr/bin/env python3
"""depth-count.py - is the C2 table new knowledge or a re-statement? Counts against base SKILL.md.

Usage: python3 depth-count.py --repo <lane> [--base 99cdb4d6...] [--m2 2ee0b55f...]
Prints: per-code backticked/substring counts at base, verdict-on-same-line, and the base facts the
table's triggers add (curl rc numbers, size cap, sniff phrase).
"""
from __future__ import annotations

import argparse
import difflib
import subprocess

POPULATION = (
    "connection-refused timeout empty-reply connection-reset no-http-response http-401 http-403 "
    "llamacpp-loading expected-wildcard matched unresolvable-id served-id-mismatch html-non-model "
    "schema-unrecognized non-model-2xx non-2xx-non-model-http router-sleeping router-unloaded-autoload "
    "router-loading router-downloading router-model-missing router-model-invalid router-unloaded"
).split()
VERDICTS = ("DEAD", "NOT_HTTP", "MODEL_OK", "MODEL_LOADING", "MODEL_UNLOADED", "MODEL_MISMATCH",
            "UNAUTHORIZED_SERVICE", "FOREIGN_SERVICE")
HEADING = "## Probe reason codes"


def show(repo, rev, path="SKILL.md"):
    return subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"],
                          capture_output=True).stdout.decode("utf-8", "replace")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--base", default="99cdb4d6270455494dd27901efe84a0f3b342062")
    ap.add_argument("--m2", default="2ee0b55f4d3fd0cb3157d26b03280c1d21e27b2d")
    a = ap.parse_args()
    base = show(a.repo, a.base)
    m2 = show(a.repo, a.m2)
    BL = base.split("\n")
    ML = m2.split("\n")
    start = next(i for i, l in enumerate(ML) if l.rstrip() == HEADING)
    end = next((i for i in range(start + 1, len(ML)) if ML[i].startswith("## ")), len(ML))
    rows = [l for l in ML[start:end] if l.startswith("|")][2:]

    print(f"rows_at_m2={len(rows)} population={len(POPULATION)}")
    named = 0
    mapped = 0
    for code in POPULATION:
        bt = [i + 1 for i, l in enumerate(BL) if f"`{code}`" in l]
        sub = sum(1 for l in BL if code in l)
        same = any(any(v in BL[i - 1] for v in VERDICTS) for i in bt)
        named += bool(bt)
        mapped += same
        print(f"{code:28s} backticked_lines={bt} substring_lines={sub} verdict_same_line={same}")
    print(f"codes_named_at_base={named}/{len(POPULATION)} codes_with_verdict_at_base={mapped}/{len(POPULATION)}")
    for fact in ("rc 7", "rc 28", "rc 52", "rc 56", "rc 63", "4 MiB", "max-filesize",
                 "header or body sniff", "models_autoload", "GGUF header", "unavailable_error"):
        print(f"fact {fact!r}: base_substring={base.count(fact)}")
    ratios = []
    for r in rows:
        trig = r.strip().strip("|").split("|")[2].strip()
        best = max(difflib.SequenceMatcher(None, trig, b).ratio() for b in BL)
        ratios.append(best)
    ratios.sort()
    print(f"trigger_similarity_to_base max={ratios[-1]:.3f} median={ratios[len(ratios) // 2]:.3f} "
          f"rows_ge_0.8={sum(1 for x in ratios if x >= 0.8)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
