#!/usr/bin/env python3
"""Round-16 C1 doc-side counting command: stale lane statements about the
llama.cpp loading state or the six-verdict vocabulary, before -> after.

Each ledger row names a lane line (path, 1-based line, an anchor substring that
must be on that line) and the round-16 correction that must cite it (corrector
path and a citation token that must appear after the corrector's first
round-16 marker). A row is UNCORRECTED when the anchor is present and the
citation is absent. A missing anchor is a ledger error (exit 2), never a pass.

Reads only git objects (`git show REV:path`) or, with --worktree, the files.
This counts textual coverage only (QUALITY KQ14): the content of each
correction is judged by human review, not by this script.

Usage: stale-statements.py [--rev REV | --worktree]   (default --worktree)
Exit: 0 no uncorrected row; 1 uncorrected rows remain; 2 ledger error.
"""
import argparse, pathlib, subprocess, sys

LANE = pathlib.Path(__file__).resolve().parents[3]
MARKERS = ("round 16", "Round-16", "round-16", "Round 16")
SKILL = "SKILL.md"
EI = "corpus/knowledge/endpoint-identity.md"
CR = "corpus/knowledge/consumer-registry.md"
LC = "corpus/knowledge/listener-census.md"
SX = "corpus/knowledge/served-identity-crosswalk.md"
HM = "corpus/knowledge/runtime-health-surface-matrix.md"
SH = "corpus/knowledge/snapshot-history.md"
RD = "corpus/README.md"
TSV = "registry/endpoint-consumers.tsv"

# (id, path, line, anchor, corrector path, citation token)
LEDGER = [
    ("V1", SKILL, 12, "`MODEL_OK` | `MODEL_MISMATCH`", SKILL, "lines 11-14"),
    ("L1", SKILL, 361, "llama.cpp may list an id during loading", SKILL, "Line 361"),
    ("V2", EI, 3, "verdict vocabulary is fixed", EI, "Line 3"),
    ("F1", EI, 17, "A live HTTP error response from a non-model service", EI, "line 17"),
    ("F2", EI, 126, "Treating every HTTP error as dead", EI, "line 126"),
    ("L2", EI, 161, "permits `meta: null` while loading", EI, "Line 161"),
    ("V3", EI, 163, "verdict vocabulary are unchanged", EI, "line 163"),
    ("V4", CR, 85, "`NOT_HTTP`. Labels", CR, "lines 84-85"),
    ("V5", LC, 7, "frozen L1 binding contract", LC, "lines 7-8"),
    ("F3", LC, 363, "only assigns a verdict for **2xx**", LC, "line-363"),
    ("L3", SX, 33, "while the model is still loading", SX, "line 33"),
    ("L4", SX, 50, "No universal readiness predicate", SX, "line 50"),
    ("L5", SX, 52, "A `MODEL_OK` verdict is an inventory statement", SX, "line 52"),
    ("L6", HM, 55, "documents nullable `/v1/models` `meta` while loading", HM, "Line 55"),
    ("H1", SH, 66, "RESULT pass=24 fail=0", SH, "24/0"),
    ("L7", RD, 119, "llama.cpp nullable loading metadata", RD, "Line 119"),
]
# In-place registry header: the vocabulary comment itself must carry the verdict.
TSV_ROW = ("V6", TSV, 32, "MODEL_OK | MODEL_MISMATCH")


def read(rev, path):
    if rev is None:
        return (LANE / path).read_text(encoding="utf-8")
    return subprocess.run(["git", "-C", str(LANE), "show", f"{rev}:{path}"],
                          check=True, capture_output=True).stdout.decode("utf-8")


def after_marker(text):
    idx = [text.find(m) for m in MARKERS if m in text]
    return text[min(idx):] if idx else ""


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--rev")
    g.add_argument("--worktree", action="store_true")
    a = ap.parse_args()
    rev = a.rev
    uncorrected, errors = [], []
    for rid, path, line, anchor, cpath, token in LEDGER:
        lines = read(rev, path).splitlines()
        if line > len(lines) or anchor not in lines[line - 1]:
            errors.append(f"{rid} {path}:{line} anchor missing: {anchor!r}")
            continue
        if token not in after_marker(read(rev, cpath)):
            uncorrected.append(f"{rid} {path}:{line} (needs {token!r} in {cpath})")
    rid, path, line, anchor = TSV_ROW
    lines = read(rev, path).splitlines()
    if line > len(lines) or anchor not in lines[line - 1]:
        errors.append(f"{rid} {path}:{line} anchor missing")
    elif "MODEL_LOADING" not in lines[line - 1]:
        uncorrected.append(f"{rid} {path}:{line} (vocabulary comment lacks MODEL_LOADING)")
    total = len(LEDGER) + 1
    print(f"revision={rev or 'worktree'} ledger_rows={total} "
          f"uncorrected={len(uncorrected)} errors={len(errors)}")
    for u in uncorrected:
        print("  UNCORRECTED", u)
    for e in errors:
        print("  ERROR", e)
    if errors:
        return 2
    return 1 if uncorrected else 0


if __name__ == "__main__":
    sys.exit(main())
