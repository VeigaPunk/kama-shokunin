#!/usr/bin/env python3
"""tip-receipt-check.py -- flag round-report hash claims not backed by receipts.

Round-48 item D9Receipts checker (stdlib only). Cross-checks every
"measured at / re-run at / holds at <hash>" statement in a round report
against the `tip=` line (or equivalent) of the receipt it cites or implies.

Claim forms recognised (per report line):

  Form A (explicit citation): the line contains hex hash(es) (>= 8 chars)
      and receipt reference(s) `<name>.out`. Each receipt is paired with
      the NEAREST hash preceding it on the line. Glob refs (`*-fix.out`)
      are ignored.

  Form B (instrument claim): the line has a claim marker ("measured",
      "re-run", "holds", or " at `<hash>`") and names instruments
      (r40..r49, pointer, gate, cap, digest, hexrun, c1, c2) without a
      receipt citation. Each instrument resolves to a receipt by suffix
      priority <name>-final.out, <name>-fix.out, <name>-after.out.

Verdicts:
  AGREE     receipt records the claimed hash (tip=/tip:/commit=/lane_oid=/
            head= field, prefix match allowed)
  MISMATCH  receipt records a different hash                  -> exit 1
  NO_TIP    receipt has no hash-bearing line (warn by default,
            fail under --strict; strict also fails MISSING_RECEIPT)
  MISSING_RECEIPT cited receipt file does not exist           -> exit 1

Exit codes: 0 all good; 1 findings; 2 usage/IO error.

Usage:
  python3 tip-receipt-check.py --report REPORT.md --receipts DIR [--strict]
"""

import argparse
import re
import sys
from pathlib import Path

HEX = re.compile(r"(?<![\w])([0-9a-f]{8,40})(?![\w])")
# Receipt ref, not preceded by a path/glob char, so `*-fix.out` never matches.
RECEIPT = re.compile(r"(?<![\w*./-])((?:[\w.-]+/)*[\w-]+\.out)(?![\w-])")
TIPFIELD = re.compile(
    r"^\s*(?:tip|commit|lane_oid|head)\s*[=:]\s*([0-9a-f]{8,40})\b", re.M)
CLAIMMARK = re.compile(r"re-?run|re-?measured|measured|holds|\bat\s+`", re.I)
INSTRUMENT = re.compile(r"\b(r4[0-9]|pointer|gate|cap|digest|hexrun|c1|c2)\b",
                        re.IGNORECASE)
SUFFIXES = ("-final.out", "-fix.out", "-after.out")
FAIL = ("MISMATCH", "NO_TIP", "MISSING_RECEIPT")


def receipt_tip(path):
    """Return (hash, line_no) of the first tip-bearing line, else (None, None)."""
    try:
        text = path.read_text()
    except OSError:
        return None, None
    m = TIPFIELD.search(text)
    if m:
        return m.group(1), text.count("\n", 0, m.start()) + 1
    return None, None


def resolve_instrument(name, receipts):
    for suf in SUFFIXES:
        cand = receipts / f"{name.lower()}{suf}"
        if cand.exists():
            return cand
    return None


def pair(receipt_name, claimed, rpath):
    """Verdict tuple for one (claim, receipt, hash) triple."""
    tip, tl = receipt_tip(rpath)
    if tip is None:
        return ("NO_TIP", receipt_name, claimed, "<no hash field>")
    if tip.startswith(claimed) or claimed.startswith(tip):
        return ("AGREE", receipt_name, claimed, f"{tip}:{tl}")
    return ("MISMATCH", receipt_name, claimed, f"{tip}:{tl}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True, type=Path)
    ap.add_argument("--receipts", required=True, type=Path)
    ap.add_argument("--strict", action="store_true",
                    help="NO_TIP and MISSING_RECEIPT also fail")
    args = ap.parse_args()

    try:
        lines = args.report.read_text().splitlines()
    except OSError as e:
        print(f"error: cannot read report: {e}", file=sys.stderr)
        return 2

    out = []
    for no, raw_line in enumerate(lines, 1):
        line = re.sub(r"sha256\s+[`:\"]?[0-9a-f…]+", " ", raw_line,
                      flags=re.IGNORECASE)  # digest literals are not claims
        hashes, hspans = [], []
        for m in HEX.finditer(line):
            hashes.append(m.group(1))
            hspans.append(m.span())
        refs = list(dict.fromkeys(m.group(1) for m in RECEIPT.finditer(line)))
        instruments = (list(dict.fromkeys(
            m.group(0).lower() for m in INSTRUMENT.finditer(line)))
            if (hashes and CLAIMMARK.search(line) and not refs) else [])

        # Form A: explicit receipt citations, nearest preceding hash wins.
        for ref in refs:
            rpath = args.receipts / Path(ref).name
            before = [h for h, (s, e) in zip(hashes, hspans) if e <=
                      line.find(ref)]
            claimed = before[-1] if before else (hashes[0] if hashes else None)
            if claimed is None:
                continue
            if not rpath.exists():
                out.append((no, "MISSING_RECEIPT", ref, claimed, "-"))
                continue
            v = pair(ref, claimed, rpath)
            out.append((no,) + v)

        # Form B: instrument names with a claim marker.
        for name in instruments:
            rpath = resolve_instrument(name, args.receipts)
            if rpath is None:
                continue
            out.append((no,) + pair(rpath.name, hashes[0], rpath))

    failed = False
    for no, verdict, ref, claimed, actual in out:
        mark = {"AGREE": "ok", "MISMATCH": "FAIL", "NO_TIP": "warn",
                "MISSING_RECEIPT": "FAIL"}[verdict]
        if verdict in FAIL and (args.strict or verdict != "NO_TIP"):
            failed = True
            mark = "FAIL"
        print(f"{mark:>4}  {args.report.name}:{no}  {ref}  "
              f"claimed={claimed or '-'}  receipt={actual}")

    n = len(out)
    print(f"summary claims={n} agree={sum(1 for f in out if f[1]=='AGREE')} "
          f"mismatch={sum(1 for f in out if f[1]=='MISMATCH')} "
          f"no_tip={sum(1 for f in out if f[1]=='NO_TIP')} "
          f"missing={sum(1 for f in out if f[1]=='MISSING_RECEIPT')} "
          f"failed={int(failed)} exit={1 if failed else 0}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
