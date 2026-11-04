#!/usr/bin/env python3
"""round74-seat-count-check.py — kama round 74, seat SCR02Lesson.

Lesson-mined instrument. Two arms:

  --spec PATH
      Recompute the wave seat count from len(spec["items"]) and fail (exit 1)
      when a prose field ("milestone", "context") names a different count via
      a "N seats" / "N seat" token (case-insensitive). The r73 wave spec is
      the red demo: prose says "14 seats", the items array carries 15.

  --census-order DIR
      Assert that a committed mirror-census receipt recording exit 0 exists in
      the round dir and is recorded BEFORE the registry-append receipt, so a
      corpus/SOURCES.md append never precedes the first exit-0 mirror census.
      Receipt lines scanned (recursively, *.out only):
        mirror census line:  ^mode=mirror-<label> exit=0
        append marker:       a line carrying both `sha256 before=` and
                             `after=`, or a comment line naming the
                             `corpus/SOURCES.md append`
      Ordering is evaluated on the flattened (relpath, line-no) order; the
      r73 replay (append header at .ufo/waves/round-73/w1/SCR01Sources/
      census.out:2,4, first `mode=mirror-* exit=0` at :16) is the red demo.

  --selftest
      Build both fixture families under $TMPDIR and grade them; prints
      `SEAT_COUNT_CHECK_SELFTEST pass=<n> fail=0` and exits 0 only when every
      arm behaves (including the flip guards that prove a green is not
      vacuous).

Exit map: 0 clean, 1 findings, 2 could-not-evaluate (CLI misuse, unreadable
spec, no census or no append receipt in the census-order arm).
"""

import argparse
import json
import os
import re
import sys
import tempfile

PROSE_FIELDS = ("milestone", "context")
SEAT_TOKEN_RE = re.compile(r"(\d+)\s+seats?\b", re.IGNORECASE)
CENSUS_OK_RE = re.compile(r"^mode=mirror-\S+\s+exit=0\b")
CENSUS_ANY_RE = re.compile(r"^mode=mirror-\S+\s+exit=(\d+)\b")
APPEND_MARK_RE = re.compile(r"sha256\s+before=\S+\s+after=\S+|corpus/SOURCES\.md\s+append")


def out(msg):
    print(msg)


def check_spec(path):
    """Return (exit_code, lines)."""
    lines = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            spec = json.load(fh)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        out("SEAT_COUNT_CHECK_FINDING could-not-evaluate spec {!r}: {}".format(path, exc))
        return 2, lines
    items = spec.get("items")
    if not isinstance(items, list):
        out("SEAT_COUNT_CHECK_FINDING could-not-evaluate spec {!r}: no items array".format(path))
        return 2, lines
    n = len(items)
    findings = []
    prose_counts = []
    for field in PROSE_FIELDS:
        value = spec.get(field)
        if not isinstance(value, str):
            continue
        for match in SEAT_TOKEN_RE.finditer(value):
            p = int(match.group(1))
            prose_counts.append(p)
            if p != n:
                findings.append(
                    "SEAT_COUNT_CHECK_FINDING number-drift {}: prose names {} seats, "
                    "items carries {}".format(field, p, n))
    if findings:
        for f in findings:
            out(f)
        out("SEAT_COUNT_CHECK spec={} items={} prose_counts={} verdict=drift".format(
            path, n, ",".join(str(p) for p in prose_counts) or "-"))
        return 1, lines
    out("SEAT_COUNT_CHECK spec={} items={} prose_counts={} verdict=ok".format(
        path, n, ",".join(str(p) for p in prose_counts) or "-"))
    return 0, lines


def _scan_receipts(root):
    """Collect (relpath, lineno, kind) tuples over *.out files under root."""
    census_ok = []
    census_any = []
    append = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in sorted(filenames):
            if not name.endswith(".out"):
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root)
            try:
                with open(full, "r", encoding="utf-8", errors="replace") as fh:
                    for lineno, line in enumerate(fh, 1):
                        if CENSUS_OK_RE.match(line):
                            census_ok.append((rel, lineno, line.strip()))
                        m = CENSUS_ANY_RE.match(line)
                        if m:
                            census_any.append((rel, lineno, m.group(1)))
                        if APPEND_MARK_RE.search(line):
                            append.append((rel, lineno, line.strip()))
            except OSError:
                continue
    return census_ok, census_any, append


def check_census_order(root):
    if not os.path.isdir(root):
        out("SEAT_COUNT_CHECK_FINDING could-not-evaluate census-order {!r}: not a directory".format(root))
        return 2
    census_ok, census_any, append = _scan_receipts(root)
    if not census_any:
        out("SEAT_COUNT_CHECK_FINDING could-not-evaluate census-order {!r}: "
            "no mirror-census receipt (mode=mirror-* line) under the round dir".format(root))
        return 2
    if not append:
        out("SEAT_COUNT_CHECK_FINDING could-not-evaluate census-order {!r}: "
            "no registry-append receipt (sha256 before=/after= or 'corpus/SOURCES.md append') "
            "under the round dir".format(root))
        return 2
    first_ok = min(census_ok) if census_ok else None
    first_append = min(append)
    if first_ok is None:
        out("SEAT_COUNT_CHECK_FINDING census-order mirror-census never exited 0 "
            "(modes seen: {}); first append marker at {}:{}".format(
                ",".join("exit={}".format(c[2]) for c in census_any),
                first_append[0], first_append[1]))
        out("SEAT_COUNT_CHECK census_order dir={} census_exit0_first=- append_first={}:{} "
            "verdict=ordering-violation".format(root, first_append[0], first_append[1]))
        return 1
    if (first_ok[0], first_ok[1]) < (first_append[0], first_append[1]):
        out("SEAT_COUNT_CHECK census_order dir={} census_exit0_first={}:{} append_first={}:{} "
            "verdict=ok".format(root, first_ok[0], first_ok[1], first_append[0], first_append[1]))
        return 0
    out("SEAT_COUNT_CHECK_FINDING census-order first exit-0 mirror census at {}:{} "
        "postdates the registry-append marker at {}:{}".format(
            first_ok[0], first_ok[1], first_append[0], first_append[1]))
    out("SEAT_COUNT_CHECK census_order dir={} census_exit0_first={}:{} append_first={}:{} "
        "verdict=ordering-violation".format(root, first_ok[0], first_ok[1],
                                            first_append[0], first_append[1]))
    return 1


def _write(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def _mk_spec(path, prose_seats, n_items):
    items = [{"name": "SEAT{:02d}".format(i + 1), "role": "executor"}
             for i in range(n_items)]
    spec = {
        "wave": "fixture",
        "milestone": "fixture wave (v1, {} seats: filler)".format(prose_seats),
        "context": "# Goal\nfixture wave of {} seats (build + attack).".format(prose_seats),
        "items": items,
    }
    _write(path, json.dumps(spec, indent=1))


def _mk_round(dirpath, ordering):
    """ordering 'honest' -> exit-0 census recorded before append marker;
    'r73' -> append marker first (the r73 replay);
    'nocensus' -> only an append marker; 'noappend' -> only census lines."""
    os.makedirs(dirpath)
    receipt = os.path.join(dirpath, "census.out")
    if ordering == "honest":
        _write(receipt, "# rev=fixture0000000000000000000000000000000 round=99\n"
                        "mode=mirror-gate exit=0\n"
                        "file\tok\tmirror/SOURCES.md\n"
                        "# corpus/SOURCES.md append, round-99 Frontier step\n"
                        "# lane file: corpus/SOURCES.md  sha256 before=aaaa after=bbbb\n")
    elif ordering == "r73":
        _write(receipt, "# rev=fixture0000000000000000000000000000000 round=98\n"
                        "# corpus/SOURCES.md append, round-98 Frontier step\n"
                        "# lane file: corpus/SOURCES.md  sha256 before=aaaa after=bbbb\n"
                        "# [1] mirror, candidate in place\n"
                        "mode=mirror-preland exit=1\n"
                        "# [2] mirror after landing\n"
                        "mode=mirror-postland exit=0\n")
    elif ordering == "nocensus":
        _write(receipt, "# rev=fixture0000000000000000000000000000000 round=97\n"
                        "# corpus/SOURCES.md append, round-97 Frontier step\n"
                        "# lane file: corpus/SOURCES.md  sha256 before=aaaa after=bbbb\n")
    elif ordering == "noappend":
        _write(receipt, "# rev=fixture0000000000000000000000000000000 round=96\n"
                        "mode=mirror-gate exit=0\n"
                        "file\tok\tmirror/SOURCES.md\n")
    else:
        raise ValueError(ordering)


def selftest():
    work = tempfile.mkdtemp(prefix="seat-count-check-", dir=os.environ.get("TMPDIR") or None)
    arms = []

    def arm(name, got, want, cond):
        arms.append((name, got, want, cond))

    # --- seat-count arms ---
    drift = os.path.join(work, "spec-drift.json")
    _mk_spec(drift, prose_seats=14, n_items=15)
    rc = check_spec(drift)[0]
    arm("spec-drift-red", rc, 1, rc == 1)

    clean = os.path.join(work, "spec-clean.json")
    _mk_spec(clean, prose_seats=13, n_items=13)
    rc = check_spec(clean)[0]
    arm("spec-clean-green", rc, 0, rc == 0)

    # flip guard: a do-nothing check (constant 0) would also pass spec-clean;
    # prove the red arm is reachable by re-running the drift spec inverted
    rc = check_spec(clean)[0]
    arm("spec-clean-not-vacuous", rc, 0, rc == 0 and check_spec(drift)[0] == 1)

    noitems = os.path.join(work, "spec-noitems.json")
    _write(noitems, json.dumps({"wave": "fixture", "milestone": "no items here"}))
    rc = check_spec(noitems)[0]
    arm("spec-noitems-exit2", rc, 2, rc == 2)

    rc = check_spec(os.path.join(work, "absent.json"))[0]
    arm("spec-absent-exit2", rc, 2, rc == 2)

    # --- census-order arms ---
    honest = os.path.join(work, "round-honest")
    _mk_round(honest, "honest")
    rc = check_census_order(honest)
    arm("census-honest-green", rc, 0, rc == 0)

    r73 = os.path.join(work, "round-r73")
    _mk_round(r73, "r73")
    rc = check_census_order(r73)
    arm("census-r73-ordering-red", rc, 1, rc == 1)

    flip = os.path.join(work, "round-flip")
    _mk_round(flip, "honest")
    receipt = os.path.join(flip, "census.out")
    _write(receipt, "# rev=fixture flipped: append recorded before the exit-0 census\n"
                    "# corpus/SOURCES.md append, round-95 Frontier step\n"
                    "mode=mirror-gate exit=0\n")
    rc = check_census_order(flip)
    arm("census-flip-guard-red", rc, 1, rc == 1)

    nocensus = os.path.join(work, "round-nocensus")
    _mk_round(nocensus, "nocensus")
    rc = check_census_order(nocensus)
    arm("census-nocensus-exit2", rc, 2, rc == 2)

    noappend = os.path.join(work, "round-noappend")
    _mk_round(noappend, "noappend")
    rc = check_census_order(noappend)
    arm("census-noappend-exit2", rc, 2, rc == 2)

    npass = sum(1 for a in arms if a[3])
    nfail = len(arms) - npass
    for name, got, want, ok in arms:
        out("SEAT_COUNT_CHECK_SELFTEST_ARM {} got={} want={} {}".format(
            name, got, want, "PASS" if ok else "FAIL"))
    out("SEAT_COUNT_CHECK_SELFTEST pass={} fail={}".format(npass, nfail))
    return 0 if nfail == 0 else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description="round-74 seat-count and census-order check")
    parser.add_argument("--spec", metavar="PATH", help="wave spec JSON to grade")
    parser.add_argument("--census-order", metavar="DIR", help="round dir to grade for census ordering")
    parser.add_argument("--selftest", action="store_true", help="run fixture selftest under TMPDIR")
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.spec and not args.census_order:
        parser.print_usage(sys.stderr)
        return 2
    worst = 0
    if args.spec:
        worst = max(worst, check_spec(args.spec)[0])
    if args.census_order:
        worst = max(worst, check_census_order(args.census_order))
    return worst


if __name__ == "__main__":
    sys.exit(main())
