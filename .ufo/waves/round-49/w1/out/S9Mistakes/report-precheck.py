#!/usr/bin/env python3
"""report-precheck.py -- check a filed round report for two round-48 closure
conformance defects before it is filed (round 49, seat S9Mistakes).

Both defects were found only after the report had been committed, by the round-48
verifier spot-check (corpus/lessons/round-48-verifier-spotcheck.md, section 6):

  R2  the filed report carried unfilled template placeholders (`__TIP__`,
      `__WAVEDONE__`, `__YIELD__`, `__DEAD__`, `__LASTROW__`) because it was
      committed before the values existed.  Placeholders are checked over the
      whole file: `__[A-Z][A-Z0-9_]*__`.

  R3  the `## Sources & frontier` census line paraphrased the census receipt:
      it said the end census was "93 W04, 0 E" while the receipt also holds
      `W01` (S481).  Every code the receipt carries is required on the census
      line with the receipt's own count.

This is a precheck, not a counter: it has no preregistration, no frozen digest and
no claim.  It reads ONE file plus the receipt(s) it names, so it cannot see R2's
second half (the in-place rewrite of filed bytes) -- that needs the git history of
the report path (`git log --format=%H -- <report>` and a diff between the commits)
-- nor R4 (route map vs live config).

Usage:
  report-precheck.py --report .ufo/reports/round-49/kama.md \
                     --census .ufo/waves/round-49/census/end.out
  report-precheck.py --report R.md --census start.out --census end.out --json
  report-precheck.py --selftest

Exit codes: 0 pass (no finding), 1 defect found, 2 usage/IO error or unreadable input.

Census receipt format (scripts/sources-census.sh validate, `emit`): one
`<lane>\t<CODE>\t<text>` line per finding, plus a trailing `exit=<n>` line that is
not a finding.  Only codes with a non-zero count are required in the report; a code
absent from the receipt (its count is 0) is never required, so a report that writes
"0 E" for a code family the receipt does not flag is not a finding.
"""

import argparse
import json
import os
import re
import sys
import tempfile

PLACEHOLDER_RE = re.compile(r"__[A-Z][A-Z0-9_]*__")
HEADING_RE = re.compile(r"^##\s+(?:Sources\s*(?:&|and)\s*frontier)\s*$", re.IGNORECASE)
ANY_HEADING_RE = re.compile(r"^##\s+\S")
RECEIPT_LINE_RE = re.compile(r"^(?P<lane>[^\t]+)\t(?P<code>[A-Z][0-9]{2,})\t(?P<text>.*)$")
# "93 W04", "93 `W04`", "93x W04", "1 W01 (S481)" -> (count, code)
CLAIM_RE = re.compile(r"(?<![\w.])(\d+)\s*[x×]?\s*`?([A-Z][0-9]{2,})`?")


def load_receipt(path):
    """Return (counts_by_code, finding_line_count) or raise ValueError."""
    counts = {}
    findings = 0
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n")
            m = RECEIPT_LINE_RE.match(line)
            if not m:
                continue
            findings += 1
            code = m.group("code")
            counts[code] = counts.get(code, 0) + 1
    return counts, findings


def find_placeholders(text, allowed=()):
    out = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for tok in PLACEHOLDER_RE.findall(line):
            if tok in allowed:
                continue
            out.append((lineno, tok))
    return out


def census_section(text):
    """Return (start_lineno, end_lineno, [(lineno, line)]) for the section, or None."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if HEADING_RE.match(line):
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if ANY_HEADING_RE.match(lines[j]):
            end = j
            break
    body = [(n, lines[n - 1]) for n in range(start + 1, end + 1)]
    return (start + 1, end, body)


def census_findings(text, receipt_path, counts, findings):
    """Findings for one receipt: codes with a non-zero count must appear with that count."""
    if findings == 0:
        return []
    section = census_section(text)
    basename = os.path.basename(receipt_path)
    if section is None:
        return ["no-sources-frontier-section: receipt %s carries %d finding line(s) %s but the report has no `## Sources & frontier` heading"
                % (basename, findings, fmt_counts(counts))]
    _, _, body = section
    named = [(n, l) for (n, l) in body if basename in l]
    claim_lines = [(n, l) for (n, l) in body if CLAIM_RE.search(l)]
    targets = named or claim_lines or body
    out = []
    for code in sorted(counts):
        want = counts[code]
        got = []
        for _, line in targets:
            for num, found_code in CLAIM_RE.findall(line):
                if found_code == code:
                    got.append(int(num))
        where = "line(s) %s" % ",".join(str(n) for n, _ in targets) if targets else "no line"
        if not got:
            out.append("omits %s=%d (%s, receipt %s carries %d %s line(s))"
                       % (code, want, where, basename, want, code))
        elif want not in got:
            out.append("count %s: report says %s, receipt %s carries %d (%s)"
                       % (code, "/".join(str(g) for g in got), basename, want, where))
    return out


def fmt_counts(counts):
    return " ".join("%s=%d" % (k, counts[k]) for k in sorted(counts)) or "none"


def check(report_path, census_paths, allowed=()):
    """Return dict(findings=[...], detail={...}). Raises OSError/ValueError."""
    with open(report_path, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    findings = []
    for lineno, tok in find_placeholders(text, allowed):
        findings.append("placeholder line %d: %s" % (lineno, tok))
    detail = []
    for receipt in census_paths:
        counts, n = load_receipt(receipt)
        detail.append({"receipt": receipt, "lines": n, "counts": counts})
        findings.extend("census: %s" % f
                        for f in census_findings(text, receipt, counts, n))
    return {"report": report_path, "findings": findings, "receipts": detail}


# --------------------------------------------------------------------------- selftest

def _selftest():
    ok = 0
    tmp = tempfile.mkdtemp(prefix="precheck-selftest-")

    def w(name, body):
        p = os.path.join(tmp, name)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(body)
        return p

    receipt = w("end.out",
                "kama\tW04\tS001 duplicate url a across scopes\n"
                "kama\tW04\tS002 duplicate url b across scopes\n"
                "kama\tW01\tS003 tier-C mined with non-dash used-by\n"
                "exit=0\n")
    good = w("good.md",
             "# r\n\n- placeholders filled.\n\n## Sources & frontier\n\n"
             "- census end exit 0 (2 W04, 1 W01 (S003), 0 E; `end.out`).\n")
    bad_line = w("bad-line.md",
                 "# r\n\n## Sources & frontier\n\n"
                 "- census end exit 0 (2 W04, 0 E; `end.out`).\n")
    wrong_count = w("wrong-count.md",
                    "# r\n\n## Sources & frontier\n\n"
                    "- census end exit 0 (1 W04, 1 W01; `end.out`).\n")
    no_section = w("no-section.md", "# r\n\n- census end exit 0 (2 W04, 1 W01).\n")
    backticked = w("backticked.md",
                   "# r\n\n## Sources & frontier\n\n"
                   "- end: `2 W04`, `1 W01` (`end.out`).\n")
    placeholders = w("ph.md",
                     "# r\nlane tip `__TIP__`\n- __WAVEDONE__\n- __DEAD__\n\n"
                     "## Sources & frontier\n\n- end (2 W04, 1 W01; `end.out`).\n")
    unnamed = w("unnamed.md",
                "# r\n\n## Sources & frontier\n\n"
                "- rows 232 -> 234.\n\n"
                "- census end exit 0 (2 W04, 0 E).\n")

    def expect(label, path, want_n, want_pass, allowed=()):
        nonlocal ok
        res = check(path, [receipt], allowed)
        n = len(res["findings"])
        good_case = (n == want_n) and ((n == 0) == want_pass)
        print("%s %s (%d finding(s), want %d)" % ("ok  " if good_case else "FAIL",
                                                  label, n, want_n))
        for f in res["findings"]:
            print("      %s" % f)
        if good_case:
            ok += 1

    expect("pass-on-complete-line", good, 0, True)
    expect("fail-on-omitted-code", bad_line, 1, False)
    expect("fail-on-wrong-count", wrong_count, 1, False)
    expect("fail-on-missing-section", no_section, 1, False)
    expect("pass-with-backticked-claims", backticked, 0, True)
    expect("fail-on-placeholders-and-nothing-else-wrong", placeholders, 3, False)
    expect("pass-placeholders-allowed", placeholders, 2, False,
           allowed=("__WAVEDONE__",))
    expect("fail-on-unnamed-receipt-falls-back-to-claim-line", unnamed, 1, False)

    # a receipt with no findings requires nothing of the report
    empty = w("empty.out", "exit=0\n")
    res = check(good, [empty])
    case = len(res["findings"]) == 0
    print("%s empty-receipt-requires-nothing" % ("ok  " if case else "FAIL"))
    ok += 1 if case else 0

    total = 9
    print("selftest: %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="Precheck a round report for the "
                                             "round-48 R2 (placeholders) and R3 "
                                             "(census paraphrase) defects.")
    ap.add_argument("--report", help="report markdown path")
    ap.add_argument("--census", action="append", default=[],
                    help="census receipt path from scripts/sources-census.sh validate "
                         "(repeatable)")
    ap.add_argument("--allow", action="append", default=[],
                    help="placeholder token to allow (repeatable), e.g. a token the "
                         "report quotes as repaired text")
    ap.add_argument("--json", action="store_true", help="emit a JSON object")
    ap.add_argument("--selftest", action="store_true", help="run the built-in tests")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()
    if not args.report or not args.census:
        ap.error("--report and at least one --census are required (or --selftest)")

    try:
        res = check(args.report, args.census, tuple(args.allow))
    except (OSError, ValueError) as exc:
        print("report-precheck: error: %s" % exc, file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(res, indent=2, sort_keys=True))
    else:
        print("report-precheck: %s" % res["report"])
        for r in res["receipts"]:
            print("census receipt: %s (finding lines=%d codes=%s)"
                  % (r["receipt"], r["lines"], fmt_counts(r["counts"])))
        for f in res["findings"]:
            print("finding: %s" % f)
        print("RESULT %s findings=%d exit=%d"
              % ("fail" if res["findings"] else "pass",
                 len(res["findings"]), 1 if res["findings"] else 0))
    return 1 if res["findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
