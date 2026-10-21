#!/usr/bin/env python3
"""Mutation-sensitivity check for the missing-errata-blob oracle.

Two anchors, because the failure modes live in different auditors:

  base      the r23 base (tools/report-landing-audit.py at 0df800e). The
            policy mutants show that the oracle separates the two absence
            classes and rejects an absent-ledger fallback.
  repaired  a reference repair of the base that satisfies all twelve arms.
            The mutants on this anchor show that the oracle still rejects a
            candidate that regresses on the safety properties: a fetch-
            enabled read, or an over-relaxed promisor refusal that lets a
            missing blob pass as an empty ledger.

Every mutant must be rejected. If a mutant passes, the oracle does not
discriminate that failure mode.

Usage:
  mutation_check.py --base PATH --repaired PATH --fixtures DIR
                    --expected PATH --grader PATH [--json]
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

BASE_LEDGER = '''    return parse_errata(git(lane_repo, "show", f"{tip}:{ERRATA}"),
                        f"{args.branch}:{ERRATA}")'''

BASE_EMPTY_FALLBACK = '''    try:
        return parse_errata(git(lane_repo, "show", f"{tip}:{ERRATA}"),
                            f"{args.branch}:{ERRATA}")
    except EvalError:
        return []'''

BASE_ABSENT_PATH = '''    entry = git(lane_repo, "ls-tree", tip, "--", ERRATA).rstrip("\\n")
    if not entry:
        return []
    return parse_errata(git(lane_repo, "show", f"{tip}:{ERRATA}"),
                        f"{args.branch}:{ERRATA}")'''

NO_LAZY_OLD = '''GIT_ISOLATION = ("--no-replace-objects", "--no-lazy-fetch",'''
NO_LAZY_NEW = '''GIT_ISOLATION = ("--no-replace-objects",'''

PACK_REFUSAL = '''        if rel == "objects/pack" and path.is_dir() and any(
                p.suffix == ".promisor" and p.with_suffix(".pack").exists()
                for p in path.iterdir()):
            raise EvalError(f"{repo}: partial clone (promisor pack)")'''

PACK_REFUSAL_DROPPED = '''        if rel == "objects/pack" and path.is_dir() and any(
                p.suffix == ".promisor" and p.with_suffix(".pack").exists()
                for p in path.iterdir()):
            pass'''

REPAIRED_NO_PACK_REFUSAL = '''    path = Path(repo, git(repo, "rev-parse", "--git-path",
                          "info/grafts").strip())
    if grafts_effective(path):
        raise EvalError(f"{repo}: {path} rewrites history")'''

REPAIRED_PACK_REFUSAL = '''    path = Path(repo, git(repo, "rev-parse", "--git-path",
                          "info/grafts").strip())
    if grafts_effective(path):
        raise EvalError(f"{repo}: {path} rewrites history")
    pack = Path(repo, git(repo, "rev-parse", "--git-path",
                          "objects/pack").strip())
    if pack.is_dir() and any(p.suffix == ".promisor"
                             and p.with_suffix(".pack").exists()
                             for p in pack.iterdir()):
        raise EvalError(f"{repo}: partial clone (promisor pack)")'''

REPAIRED_NO_METADATA_REFUSAL = '''    fmt = git(repo, "rev-parse", "--show-object-format").strip()'''

REPAIRED_METADATA_REFUSAL = '''    listing = git(repo, "config", "--null", "--list",
                  errors="surrogateescape")
    for entry in filter(None, listing.split("\\0")):
        key, _, value = entry.partition("\\n")
        if key == "extensions.partialclone" or (
                re.fullmatch(r"remote\\..+\\.promisor", key)
                and git_bool(value)):
            raise EvalError(f"{repo}: partial clone ({key})")
    fmt = git(repo, "rev-parse", "--show-object-format").strip()'''

REPAIRED_LEDGER_UNAVAILABLE = '''    try:
        text = git(lane_repo, "cat-file", "blob", fields[2])
    except EvalError as exc:
        raise EvalError(f"{tip}:{ERRATA}: ledger committed but its blob is "
                        f"not available locally: {exc}") from exc'''

REPAIRED_LEDGER_EMPTY = '''    try:
        text = git(lane_repo, "cat-file", "blob", fields[2])
    except EvalError:
        return []'''

REPAIRED_CITATION_EXIT2 = '''    missing = [t for t, s in status.items() if s == "missing"]
    if missing and any(promisor_backed(repo) for repo in repos):
        raise EvalError(
            f"citation(s) {', '.join(sorted(missing))} are not present locally "
            f"and a promisor-backed repository may still hold them: absence "
            f"is not evidence")
    return status'''

REPAIRED_CITATION_PLAIN = '''    return status'''


def mutants_for(base_text, repaired_text):
    out = {}

    def add(name, anchor, source, why):
        if source == anchor:
            raise SystemExit(f"mutant {name}: no edit applied")
        out[name] = {"source": source, "why": why, "anchor": "base" if
                     anchor == base_text else "repaired"}

    add("M1-empty-ledger-fallback", base_text,
        base_text.replace(BASE_LEDGER, BASE_EMPTY_FALLBACK, 1),
        "an unreadable ledger becomes zero rows, so every missing-ledger arm "
        "proceeds to a verdict")
    add("M2-empty-ledger-fallback-narrow", base_text,
        base_text.replace(BASE_LEDGER, BASE_EMPTY_FALLBACK, 1),
        "the same fallback in its narrowest form: it still hides missing "
        "evidence behind a clean verdict")
    add("M3-absent-path-fallback", base_text,
        base_text.replace(BASE_LEDGER, BASE_ABSENT_PATH, 1),
        "a ledger path absent from the tree is treated as no ledger, a "
        "policy change that is not a repair")
    add("M4-fetch-enabled-read", base_text,
        base_text.replace(NO_LAZY_OLD, NO_LAZY_NEW, 1),
        "the ledger read drops --no-lazy-fetch, so a promisor-backed "
        "repository silently fetches the missing blob")
    add("M5-repaired-fetch-enabled-read", repaired_text,
        repaired_text.replace(NO_LAZY_OLD, NO_LAZY_NEW, 1),
        "the repaired auditor, with the fetch guard removed: the missing "
        "ledger blob is silently restored from the origin and the audit "
        "emits a clean verdict on evidence it never read")
    add("M6-repaired-promisor-pack-refusal-reinstated", repaired_text,
        repaired_text.replace(REPAIRED_NO_PACK_REFUSAL,
                              REPAIRED_PACK_REFUSAL, 1),
        "the promisor-pack refusal is reinstated: a hydrated blobless lane "
        "is refused on the declaration alone, the blanket precondition the "
        "amendment forbids")
    add("M7-repaired-empty-ledger-fallback", repaired_text,
        repaired_text.replace(REPAIRED_LEDGER_UNAVAILABLE,
                              REPAIRED_LEDGER_EMPTY, 1),
        "the repaired auditor falls back to an empty ledger when the "
        "committed blob is unavailable")
    add("M8-promisor-metadata-refusal-reinstated", repaired_text,
        repaired_text.replace(REPAIRED_NO_METADATA_REFUSAL,
                              REPAIRED_METADATA_REFUSAL, 1),
        "the promisor metadata refusal is reinstated: a content-complete "
        "marked lane is refused before the authorized errata matching")
    add("M9-citation-exit2-on-promisor", repaired_text,
        repaired_text.replace(REPAIRED_CITATION_PLAIN,
                              REPAIRED_CITATION_EXIT2, 1),
        "the withdrawn preregistration rule (a missing citation in a "
        "promisor-backed repository is unknown => exit2) is reinstated: it "
        "aborts before the authorized errata matching can happen")
    add("M10-errata-correction-exit2-on-promisor", repaired_text,
        repaired_text.replace(REPAIRED_CITATION_PLAIN,
                              REPAIRED_CITATION_EXIT2, 1)
        .replace(REPAIRED_LEDGER_UNAVAILABLE, REPAIRED_LEDGER_EMPTY, 1),
        "the withdrawn rule is reinstated AND the ledger read falls back to "
        "an empty ledger: the marked and unmarked twins of E8/E9 then differ "
        "on promisor metadata alone, which the amendment forbids")
    return out


# A mutant that the oracle TOLERATES is not a defect: it is a second
# acceptable implementation. The oracle states which behaviour is required,
# not which mechanism produces it.
TOLERATED = {}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", required=True)
    ap.add_argument("--repaired", required=True)
    ap.add_argument("--fixtures", required=True)
    ap.add_argument("--expected", required=True)
    ap.add_argument("--grader", required=True)
    ap.add_argument("--json")
    args = ap.parse_args(argv)
    base_text = Path(args.base).read_text()
    repaired_text = Path(args.repaired).read_text()
    mutants = mutants_for(base_text, repaired_text)
    results = {}
    required_ok = True
    tolerated_ok = True
    with tempfile.TemporaryDirectory(prefix="oracle-mutants-") as tmp:
        for name, spec in mutants.items():
            path = Path(tmp, f"{name}.py")
            path.write_text(spec["source"])
            proc = subprocess.run(
                [sys.executable, args.grader, "--auditor", str(path),
                 "--fixtures", args.fixtures, "--expected", args.expected,
                 "--json", str(Path(tmp, f"{name}.json"))],
                capture_output=True,
                env={k: v for k, v in os.environ.items()
                     if not k.startswith("GIT_")})
            try:
                doc = json.loads(Path(tmp, f"{name}.json").read_text())
            except (OSError, ValueError):
                doc = {"violations": ["harness-error"],
                       "stderr": proc.stderr.decode(errors="replace")[-300:]}
            rejected = proc.returncode == 1
            tolerated = name in TOLERATED
            results[name] = {"rejected": rejected, "anchor": spec["anchor"],
                             "grader_exit": proc.returncode,
                             "violations": doc.get("violations"),
                             "why": spec["why"],
                             "expectation": ("tolerated" if tolerated
                                             else "must be rejected"),
                             "tolerated_reason": TOLERATED.get(name)}
            if tolerated:
                if rejected:
                    tolerated_ok = False
            elif not rejected:
                required_ok = False
    doc = {"mutants": results, "required_all_rejected": required_ok,
           "tolerated_all_accepted": tolerated_ok,
           "ok": required_ok and tolerated_ok}
    if args.json:
        Path(args.json).write_text(json.dumps(doc, indent=1, sort_keys=True)
                                   + "\n")
    for name, r in results.items():
        tolerated = name in TOLERATED
        good = (not r["rejected"]) if tolerated else r["rejected"]
        mark = "ok  " if good else "MISS"
        print(f"{mark} {name} [{r['anchor']}] "
              f"({r['expectation']}): violations={r['violations']}")
    print(f"required mutants all rejected={required_ok}; "
          f"tolerated mutants all accepted={tolerated_ok}")
    return 0 if required_ok and tolerated_ok else 1


if __name__ == "__main__":
    sys.exit(main())
