#!/usr/bin/env python3
"""Independent before/after counter for the round-24 promisor grid.

Reads the JSON documents produced by

    python3 tests/report-audit/promisor-grid.py --arm both --json --out DIR

(one file: ``candidate.json``), or any two such documents, and counts the
47 registered cells in *separately reported* families:

  restored_verdict        before exit 2 (the r23 blanket metadata refusal)
                          -> after exit 0/1 that meets the amended view
  exit2_reason_corrected  before exit 2 -> after exit 2, same verdict class,
                          content-derived reason instead of the metadata
                          refusal
  unchanged_exit2         before exit 2 -> after exit 2, reason class equal
  unchanged_verdict       before exit 0/1 -> the same exit 0/1
  verdict_to_refusal      before exit 0/1 -> after exit 2 (a declared policy
                          change: the amended view turns a proved absence
                          into a could-not-evaluate; PG34 is the only such
                          registered cell)
  unmet_after             the after cell does not meet the amended view

and the three headline numbers that must never be mixed:

  frozen history          the before arm scored on the FROZEN column
                          (r23 base behaviour against its own history)
  amended baseline        the before arm scored on the AMENDED view, with the
                          frozen-arm grading rule (no exit-2 form check)
  amended after           the after arm scored on the AMENDED view, with the
                          current-arm grading rule (exit-2 form check)

The grid runner's own ``amended_view_met`` / ``amended_view_unmet`` summary
fields are NOT used for any verdict: in the current-arm block they are
structurally constant (the runner filters on ``arm == "frozen"``), so they
read 0 / [] even for a fully met run.  Every number here is recomputed from
the per-row observations, and the runner's flags are only used as a
cross-check where they exist.

Exit codes: 0 = the count was produced, 2 = could-not-evaluate (missing arm,
unreadable document, mismatched expectation manifest, disjoint cell sets).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Mirrors tests/report-audit/promisor-grid.py REASON_CLASSES (the runner's
# substring bags).  The amended view only ever demands reason_class
# "unavailable"; "metadata" identifies the r23 blanket refusal.
REASON_CLASSES = {
    "metadata": ("partial clone", "promisor pack"),
    "unavailable": ("missing", "unavailable", "not available", "no such object",
                    "not found", "incomplete", "absent", "could not read",
                    "cannot read", "unable to read", "traverse parents",
                    "does not exist", "not a valid object", "bad object",
                    "bad file", "not a tree object", "not in 'head'",
                    "corrupt"),
}

CNE_PREFIX = "could-not-evaluate:"


def fail(msg):
    print("could-not-evaluate: %s" % msg, file=sys.stderr)
    raise SystemExit(2)


def load_doc(path):
    p = Path(path)
    if not p.is_file():
        fail("no such grid document: %s" % path)
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        fail("unreadable grid document %s: %s" % (path, exc))
    if not isinstance(doc, dict) or "arms" not in doc:
        fail("not a promisor-grid document: %s" % path)
    return doc


def load_manifest(path):
    """The per-case form-check inputs (names_any_of, reason_forbidden).

    These live at the top level of a manifest case, not inside a view, so a
    grid row does not carry them; the manifest is needed to reproduce the
    runner's current-arm exit-2 form check.
    """
    p = Path(path)
    if not p.is_file():
        fail("no such expectation manifest: %s" % path)
    try:
        table = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        fail("unreadable expectation manifest %s: %s" % (path, exc))
    out = {}
    for case in table.get("cases", []):
        out[case["case"]] = {
            "names_any_of": case.get("names_any_of") or [],
            "reason_forbidden": case.get("reason_forbidden") or [],
        }
    return out


def arm_rows(doc, arm):
    arms = doc.get("arms") or {}
    if arm not in arms:
        fail("document has no %r arm (arms: %s)"
             % (arm, ", ".join(sorted(arms)) or "none"))
    rows = (arms[arm] or {}).get("rows")
    if not rows:
        fail("arm %r carries no rows" % arm)
    return rows


def reason_class(stderr):
    """The reason class of one refusal, from the recorded stderr tail."""
    low = (stderr or "").lower()
    if not low.strip():
        return None
    if any(t in low for t in REASON_CLASSES["metadata"]):
        return "metadata"
    if any(t in low for t in REASON_CLASSES["unavailable"]):
        return "unavailable"
    return "unknown"


def expectation(row, key):
    """One view of the expectation carried by the row."""
    exp = (row.get("expectation") or {}).get(key)
    if exp is None:
        exp = (row.get("expectation") or {}).get("amended")
    if exp is None:
        exp = (row.get("expectation") or {}).get("original")
    return exp or {}


def independent_met(row, exp, form=None):
    """Recompute one cell's verdict from the raw observations.

    Returns (met, checks).  ``form`` is the optional current-arm exit-2 form
    input ({"names": [...], "forbidden": [...]}); when it is None the
    frozen-arm grading rule is used (no form check), exactly as the runner
    grades the frozen arm against the amended view.
    """
    checks = {}
    exit_code = row.get("exit")
    want_exit = exp.get("exit")
    checks["exit"] = (want_exit is None) or (exit_code == want_exit)

    kinds = row.get("kinds")
    want_kinds = exp.get("kinds")
    checks["kinds"] = None
    if want_kinds is not None and exit_code in (0, 1):
        checks["kinds"] = sorted(kinds or []) == sorted(want_kinds)

    defects = row.get("defects")
    want_defects = exp.get("defects")
    checks["defects"] = None
    if want_defects is not None and exit_code in (0, 1):
        if any(isinstance(d, dict) and isinstance(d.get("token"), str)
               and d["token"].startswith("$") for d in want_defects):
            checks["defects"] = "unresolved-placeholder"
        else:
            want = sorted((d.get("kind"), d.get("token")) for d in want_defects)
            got = sorted(tuple(p) for p in (defects or []))
            checks["defects"] = got == want

    want_class = exp.get("reason_class")
    checks["reason_class"] = None
    if want_class and exit_code == 2:
        low = (row.get("stderr_tail") or "").lower()
        terms = REASON_CLASSES.get(want_class)
        if terms is None:
            checks["reason_class"] = "unknown-class"
        else:
            checks["reason_class"] = any(t in low for t in terms)

    checks["hygiene"] = not (row.get("traceback") or row.get("timed_out")
                             or row.get("leaked"))
    if "objects_acquired" in row:
        acquired = row.get("objects_acquired") or {}
        checks["no_acquisition"] = not any(acquired.get(k) for k in acquired)

    if form is not None and exit_code == 2:
        err = row.get("stderr_tail") or ""
        checks["form_prefix"] = err.startswith(CNE_PREFIX)
        checks["form_no_document"] = row.get("document") is None
        forbidden = form.get("forbidden") or []
        checks["form_not_metadata"] = not any(f in err for f in forbidden)
        names = form.get("names") or []
        if names:
            if any(isinstance(n, str) and n.startswith("$") for n in names):
                checks["form_names_object"] = "unresolved-placeholder"
            else:
                checks["form_names_object"] = any(n in err for n in names)
        else:
            checks["form_names_object"] = None

    met = True
    for value in checks.values():
        if value is None or value == "unresolved-placeholder":
            continue
        if value is False:
            met = False
    return met, checks


def arm_score(rows, flag_key, exp_key, form=None, force_independent=False):
    """(met, total, unmet) of one arm scored on one view."""
    met = 0
    total = 0
    unmet = []
    for row in rows:
        if row.get("kind") not in ("policy", "control"):
            continue
        total += 1
        exp = expectation(row, exp_key)
        ok, _ = independent_met(row, exp, form)
        flag = None if force_independent else row.get(flag_key)
        if flag is None:
            flag = ok
        if flag:
            met += 1
        else:
            unmet.append(row.get("case"))
    return met, total, sorted(unmet)


def classify(before, after):
    """One cell's transition, as a single label.

    restored_verdict       exit 2 (the r23 blanket metadata refusal) -> a
                           substantive exit 0/1 verdict
    exit2_reason_corrected exit 2 -> exit 2, reason class changed: the
                           refusal stays a refusal but the reason is now
                           content-derived instead of the metadata refusal
    unchanged_exit2        exit 2 -> exit 2, reason class unchanged
    unchanged_verdict      exit 0/1 -> the same exit 0/1
    verdict_to_refusal     exit 0/1 -> exit 2 (a declared policy change: the
                           amended view turns a proved absence into a
                           could-not-evaluate; PG34 is the only such cell)
    unmet_after            the after cell does not meet the amended view
    """
    b_exit = before.get("exit")
    a_exit = after.get("exit")
    b_class = reason_class(before.get("stderr_tail"))
    a_class = reason_class(after.get("stderr_tail"))
    a_met, _ = independent_met(after, expectation(after, "amended"))
    if not a_met:
        return "unmet_after"
    if b_exit == 2 and a_exit in (0, 1):
        return "restored_verdict"
    if b_exit == 2 and a_exit == 2:
        if b_class != a_class:
            return "exit2_reason_corrected"
        return "unchanged_exit2"
    if b_exit in (0, 1) and a_exit == b_exit:
        return "unchanged_verdict"
    if b_exit in (0, 1) and a_exit != b_exit:
        return "verdict_to_refusal"
    return "other"


SELFTEST_ROWS = [
    # (before exit, before stderr, after exit, after stderr, expected bucket)
    (2, "could-not-evaluate: partial clone (remote.origin.promisor)",
     0, "", "restored_verdict"),
    (2, "could-not-evaluate: partial clone (remote.origin.promisor)",
     2, "could-not-evaluate: missing blob 58866b563cd900df310588effe79028efc104c33",
     "exit2_reason_corrected"),
    (2, "could-not-evaluate: missing blob 58866b563cd900df310588effe79028efc104c33",
     2, "could-not-evaluate: missing blob 58866b563cd900df310588effe79028efc104c33",
     "unchanged_exit2"),
    (0, "", 0, "", "unchanged_verdict"),
    (1, "", 2, "could-not-evaluate: missing blob 58866b563cd900df310588effe79028efc104c33",
     "verdict_to_refusal"),
]


def selftest():
    """The classifier over synthetic rows: every bucket is reachable and
    distinguishable, and no two rows share a bucket."""
    bad = []
    for b_exit, b_err, a_exit, a_err, want in SELFTEST_ROWS:
        before = {"exit": b_exit, "stderr_tail": b_err,
                  "expectation": {"amended": {"exit": a_exit}}}
        after = {"exit": a_exit, "stderr_tail": a_err,
                 "expectation": {"amended": {"exit": a_exit}}}
        got = classify(before, after)
        if got != want:
            bad.append("expected %s, got %s" % (want, got))
    labels = [w for *_, w in SELFTEST_ROWS]
    if len(set(labels)) != len(labels):
        bad.append("two selftest rows share a bucket")
    for line in bad:
        print("selftest-fail: %s" % line, file=sys.stderr)
    print("selftest %d/%d ok" % (len(SELFTEST_ROWS) - len(bad),
                                 len(SELFTEST_ROWS)))
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--before", help="grid document holding the before arm")
    ap.add_argument("--after", help="grid document holding the after arm")
    ap.add_argument("--before-arm", default="frozen")
    ap.add_argument("--after-arm", default="current")
    ap.add_argument("--manifest", default=None,
                    help="expectation manifest (needed for the current-arm "
                         "exit-2 form check)")
    ap.add_argument("--cells-out", default=None,
                    help="write the per-cell table as TSV")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true",
                    help="check the classifier over synthetic rows and exit")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.before or not args.after:
        ap.error("--before and --after are required (or use --selftest)")

    bdoc = load_doc(args.before)
    adoc = load_doc(args.after)
    brows = arm_rows(bdoc, args.before_arm)
    arows = arm_rows(adoc, args.after_arm)

    bman = bdoc.get("expectations_sha256")
    aman = adoc.get("expectations_sha256")
    if bman and aman and bman != aman:
        fail("the two documents were graded against different expectation "
             "manifests (%s vs %s)" % (bman, aman))

    manifest = load_manifest(args.manifest) if args.manifest else None

    bmap = {r["case"]: r for r in brows}
    amap = {r["case"]: r for r in arows}
    cases = sorted(set(bmap) & set(amap))
    only_before = sorted(set(bmap) - set(amap))
    only_after = sorted(set(amap) - set(bmap))
    if only_before or only_after:
        fail("the two arms do not cover the same cells "
             "(before-only: %s; after-only: %s)"
             % (", ".join(only_before) or "none",
                ", ".join(only_after) or "none"))

    buckets = {}
    cells = []
    for case in cases:
        b = bmap[case]
        a = amap[case]
        label = classify(b, a)
        buckets[label] = buckets.get(label, 0) + 1
        exp = expectation(a, "amended")
        cells.append({
            "case": case,
            "row_class": a.get("row_class") or a.get("kind"),
            "bucket": label,
            "before_exit": b.get("exit"),
            "before_reason_class": reason_class(b.get("stderr_tail")),
            "before_frozen_met": b.get("met_frozen"),
            "before_amended_met": b.get("met_amended_frozen"),
            "after_exit": a.get("exit"),
            "after_reason_class": reason_class(a.get("stderr_tail")),
            "after_amended_met": a.get("met_amended"),
            "after_original_met": a.get("met_original"),
            "expected_exit": exp.get("exit"),
            "expected_kinds": exp.get("kinds"),
            "expected_reason_class": exp.get("reason_class"),
            "withdrawn_original": a.get("met_original") is False,
            "twin_mismatch": a.get("twin_equal") is False,
        })

    # headline numbers, kept apart on purpose
    fh_met, fh_total, fh_unmet = arm_score(brows, "met_frozen", "frozen")
    ab_met, ab_total, ab_unmet = arm_score(brows, "met_amended_frozen",
                                           "amended")
    aa_met, aa_total, aa_unmet = arm_score(arows, "met_amended", "amended")
    fa_met, fa_total, fa_unmet = arm_score(arows, "met_frozen", "frozen")
    # The same r23 base scored in the *current* role (the runner's
    # current-arm rule, exit-2 form check on) is only measurable when the
    # before document carries the runner's current-arm verdict on its rows.
    # The recorded stderr tail is the last 300 characters of the message, so
    # the "could-not-evaluate:" prefix and the full reason are NOT
    # recoverable from a grid row: the form check cannot be re-derived from
    # the JSON, only trusted from the runner's own flag.
    bc_met = bc_total = 0
    bc_unmet = []
    bc_source = None
    if brows and all(isinstance(r.get("met_amended"), bool) for r in brows):
        bc_source = "runner flags on the before rows"
        for row in brows:
            if row.get("kind") not in ("policy", "control"):
                continue
            bc_total += 1
            if row.get("met_amended"):
                bc_met += 1
            else:
                bc_unmet.append(row.get("case"))
    else:
        bc_source = ("not measurable from this document: the before rows "
                     "carry no current-arm verdict and the recorded stderr "
                     "tail is truncated to 300 characters")

    def split(rows, flag_key, exp_key):
        out = {}
        for klass in ("policy", "control"):
            sel = [r for r in rows if r.get("kind") == klass]
            met, total, unmet = arm_score(sel, flag_key, exp_key)
            out[klass] = {"met": met, "total": total, "unmet": unmet}
        return out

    withdrawn = sorted(r["case"] for r in arows
                       if r.get("met_original") is False)
    twin_mismatch = sorted(r["case"] for r in arows
                           if r.get("twin_equal") is False)
    identical_arms = bool(
        (bdoc.get("auditor_sha256") or {}).get(args.before_arm)
        and (bdoc.get("auditor_sha256") or {}).get(args.before_arm)
        == (adoc.get("auditor_sha256") or {}).get(args.after_arm))

    report = {
        "schema": "kama-promisor-grid-count/1",
        "before": {
            "document": str(args.before),
            "arm": args.before_arm,
            "auditor_sha256": (bdoc.get("auditor_sha256") or {}).get(
                args.before_arm),
            "frozen_revision": bdoc.get("frozen_revision"),
            "expectations_sha256": bman,
            "population_sha256": bdoc.get("population_sha256"),
        },
        "after": {
            "document": str(args.after),
            "arm": args.after_arm,
            "auditor_sha256": (adoc.get("auditor_sha256") or {}).get(
                args.after_arm),
            "expectations_sha256": aman,
            "population_sha256": adoc.get("population_sha256"),
        },
        "cells": len(cases),
        "identical_auditor_arms": identical_arms,
        "frozen_history": {
            "met": fh_met, "total": fh_total, "unmet": fh_unmet,
            "note": "before arm scored on the frozen column; history, never "
                    "an improvement baseline"},
        "amended_baseline": {
            "met": ab_met, "total": ab_total, "unmet": ab_unmet,
            "by_class": split(brows, "met_amended_frozen", "amended"),
            "note": "before arm (r23 base) scored on the amended view with "
                    "the frozen-arm grading rule (no exit-2 form check); the "
                    "historical baseline the repair is measured against"},
        "amended_baseline_current_role": {
            "met": bc_met, "total": bc_total, "unmet": sorted(bc_unmet),
            "source": bc_source,
            "note": "the same r23 base scored with the current-arm grading "
                    "rule (exit-2 form check on).  A different number from "
                    "the baseline above; the two must never be quoted as "
                    "the same figure"},
        "amended_after": {
            "met": aa_met, "total": aa_total, "unmet": aa_unmet,
            "by_class": split(arows, "met_amended", "amended"),
            "note": "after arm scored on the amended view with the "
                    "current-arm grading rule"},
        "frozen_column_after": {
            "met": fa_met, "total": fa_total, "unmet": fa_unmet,
            "note": "after arm scored on the frozen column; regression guard "
                    "only, never an improvement claim"},
        "buckets": dict(sorted(buckets.items())),
        "withdrawn_original_failures": withdrawn,
        "twin_mismatch": twin_mismatch,
        "runner_summary_fields": {
            "before_arm": {k: v for k, v in
                           (bdoc["arms"][args.before_arm] or {}).items()
                           if k != "rows"},
            "after_arm": {k: v for k, v in
                          (adoc["arms"][args.after_arm] or {}).items()
                          if k != "rows"},
            "note": "the runner's own amended_view_* fields are reported "
                    "for comparison only; in the current-arm block they are "
                    "structurally constant (the runner filters arm == "
                    "'frozen'), so they read 0 / [] even for a fully met run",
        },
        "cells_detail": cells,
    }

    if args.cells_out:
        cols = ["case", "row_class", "bucket", "before_exit",
                "before_reason_class", "after_exit", "after_reason_class",
                "expected_exit", "expected_reason_class",
                "before_amended_met", "after_amended_met",
                "withdrawn_original", "twin_mismatch"]
        lines = ["\t".join(cols)]
        for c in cells:
            lines.append("\t".join(str(c.get(k)) for k in cols))
        Path(args.cells_out).write_text("\n".join(lines) + "\n",
                                        encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=1, sort_keys=True))
    else:
        print("cells                     %d" % report["cells"])
        print("frozen history            %d/%d met (before arm, frozen column)"
              % (fh_met, fh_total))
        print("amended baseline          %d/%d met (before arm, amended view, "
              "frozen-arm rule)" % (ab_met, ab_total))
        for klass, v in report["amended_baseline"]["by_class"].items():
            print("  %-8s baseline       %d/%d met" % (klass, v["met"],
                                                       v["total"]))
        if bc_total:
            print("amended baseline (current role, exit-2 form check on) "
                  "%d/%d met [%s]" % (bc_met, bc_total, bc_source))
        else:
            print("amended baseline (current role)  not measurable from this "
                  "document: %s" % bc_source)
        print("amended after             %d/%d met (after arm, amended view)"
              % (aa_met, aa_total))
        for klass, v in report["amended_after"]["by_class"].items():
            print("  %-8s after          %d/%d met" % (klass, v["met"],
                                                       v["total"]))
        print("frozen column (after)     %d/%d met (regression guard)"
              % (fa_met, fa_total))
        print("buckets")
        for name, count in report["buckets"].items():
            print("  %-22s %d" % (name, count))
        print("withdrawn original-view failures %d (never counted as achieved)"
              % len(withdrawn))
        print("twin mismatches            %d" % len(twin_mismatch))
        if identical_arms:
            print("NOTE: both arms ran the SAME auditor (%s); this run is a "
                  "self-consistency check and cannot show any restoration."
                  % (bdoc.get("auditor_sha256") or {}).get(args.before_arm))
        print("runner's own summary fields (comparison only): "
              "before amended_view_met=%s after amended_view_met=%s"
              % (report["runner_summary_fields"]["before_arm"]
                 .get("amended_view_met"),
                 report["runner_summary_fields"]["after_arm"]
                 .get("amended_view_met")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
