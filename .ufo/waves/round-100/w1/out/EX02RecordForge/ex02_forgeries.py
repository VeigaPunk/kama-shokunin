#!/usr/bin/env python3
"""EX02RecordForge: C1 record forgeries beyond committed F1-F7.

Pattern mirrors controls/c1_forgeries.py: scratch git clone of the lane,
checkout 6776c667, copy SCORECARD.md / LOG.md / .ufo/waves/round-100/r99-measured.json
from `git show 2e27e6f1:` (i.e. the current working-tree lane copies which match M
for those 3 files), apply ONE edit, commit with fixture identity, run the frozen
counter `--repo <clone> --rev HEAD`.

usage: ex02_forgeries.py --lane <lane> --scratch <dir>
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FILES = ["SCORECARD.md", "LOG.md", ".ufo/waves/round-100/r99-measured.json"]


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


# Each forgery: (description, file, old, new) — old must occur exactly once in file.
# "Expect" is our prediction of the counter exit: 1 = should be caught, 0 = green
# (counter goes green on a narrowing / on a property weaker than the wording).
FORGERIES = [
    # G1: contradiction in words, no digit percentage (disclosed limit (a)).
    ("G1-words-seven-attack",
     "LOGSCORECARD", None),
]
# We build the list imperatively below for clarity.

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", required=True)
    ap.add_argument("--scratch", required=True)
    a = ap.parse_args()
    lane = Path(a.lane).resolve()
    counter = lane / "tools/round100-record-audit.py"
    Path(a.scratch).mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="ex02-forge-", dir=a.scratch)).resolve()
    try:
        # --- define forgeries as (name, expect_rc, kind, payload) ---
        # kind: "edit" -> (file, old, new)
        #       "append" -> (file, text) appended at end of file
        #       "insert-log-block" etc handled via edit anchors
        cases = []

        def edit(name, expect, file, old, new):
            cases.append((name, expect, "edit", (file, old, new)))

        def append(name, expect, file, text):
            cases.append((name, expect, "append", (file, text)))

        # G1: second contradicting sentence in words (disclosed (a)). Green expected.
        edit("G1-words-seven-attack", 0,
             "SCORECARD.md",
             "had 12 seats, 0 dead (`.ufo/waves/round-99/w1-results.json`",
             "had 12 seats, 0 dead (seven attack seats, in words) (`.ufo/waves/round-99/w1-results.json`")
        # G2: wrong seats named as attack seats (no percentage). Green expected.
        edit("G2-wrong-seats-named", 0,
             "SCORECARD.md",
             "RV01Wording, RV02Counter,\n  CR01Records, MT01Mutants.",
             "RV01Wording, RV02Counter,\n  CR01Records, DT01Desk (not an attack seat).")
        # G3: bound pointer whose phrase is a substring that also occurs elsewhere
        # on a different line: change phrase to a common word found on that line AND
        # on many other lines. Counter only checks `phrase in lines[n-1]`, so still
        # resolves. Narrows check 8 (presence on the line, not identity of the quote).
        edit("G3-substring-phrase", 0,
             "SCORECARD.md",
             '("58% attack")', '("attack")')
        # G4: duplicated heading inside block — duplicates? heading check: block text is
        # after the ONE heading line; a second heading line INSIDE would be inside block
        # (heading regex counts lines starting with HEADING in whole file; a dup inside the
        # block at EOF region makes len(heads)==2 -> block None -> mismatch). Expect 1 (caught).
        edit("G4-duplicated-heading", 1,
             "SCORECARD.md",
             ".ufo/waves/round-100/r99-measured.json`.",
             ".ufo/waves/round-100/r99-measured.json`.\n## Round 100 correction \u2014 round-99 records")
        # G5: block moved inside another section — heading follows a preceding `## `
        # heading closer: inserting content before the correction heading is not inside
        # the block; instead we append the correction text after EOF... Better model:
        # put a `## ` line BEFORE the block's content such that the block is truncated:
        # insert `## Interlude` right after the heading line: block = text between heading
        # and next `## ` = empty -> checks 3/4 fail. Expect 1 (caught).
        edit("G5-block-truncated", 1,
             "SCORECARD.md",
             "not rewritten)\n\nRouted by",
             "not rewritten)\n## Interlude\n\nRouted by")
        # G6: percentages written as '50 %' / '33 %' with a space.
        # Counter PCT_RE = \d+(\.\d+)?\s?% matches '50 %', then m.replace(' ','') = '50%'
        # in allowed -> passes. But presence checks 3/4 need exact '4 of 12 (33%)' /
        # '6 of 12 (50%)' strings. Add a spaced variant as an EXTRA sentence: green.
        edit("G6-spaced-percent-extra", 0,
             "LOG.md",
             "6 of 12 (50%): the four",
             "6 of 12 (50%) (50 %, spaced): the four")
        # G7: '50.0%' — PCT_RE matches '50.0%', replace -> '50.0%' NOT in allowed {'33%','50%'}
        # -> caught. Expect 1.
        edit("G7-decimal-percent", 1,
             "LOG.md",
             "6 of 12 (50%): the four",
             "6 of 12 (50.0%): the four")
        # G8: measured json with an extra key. Check 9 requires set(doc)=={C1,C2,C3} -> caught. Expect 1.
        edit("G8-extra-json-key", 1,
             ".ufo/waves/round-100/r99-measured.json",
             '"C3":', '"CX": "extra", "C3":')
        # G9: correction naming the wrong seats as attack seats WITH a fraction stated
        # correct elsewhere: swap SN01Bounds/CN01Overlap line to name two non-attack seats.
        # Counter never checks the seat-name lists. Green expected.
        edit("G9-wrong-seat-names-ledger", 0,
             "LOG.md",
             "6 of 12 (50%): the four above plus SN01Bounds and CN01Overlap.",
             "6 of 12 (50%): the four above plus SC02Sources and TV01Tables.")
        # G10: pointer to a fake revision that happens to resolve.
        # Use a different real commit that also has the phrase on that line: rev 2e27e6f1
        # is M; the lane's own correction pointers use 6776c667. SCORECARD.md@6776c667:6446
        # has "10 reported, 2 dead". Does another rev also have it on line 6446? M itself
        # inserted lines above, so line numbers shifted; find a rev whose line 6446 (or any
        # line) contains the phrase. Simplest: point at the scratch HEAD... can't know hash
        # pre-commit. Alternative: point to a self-referential line: use rev 2e27e6f1
        # (M) with a line that exists at M and contains the phrase — check M's SCORECARD
        # line for "10 reported, 2 dead" at M (post-insertion lines shifted by the plan
        # block; grep found heading at 6538, the stale-pointer sentence at ~6553-6555 below
        # the insertion point, so line numbers > insertion point are same-shifted).
        # Safer: use a phrase known on a specific line at a known rev from the committed
        # blocks themselves: SCORECARD.md@2e27e6f1:6549 contains "58% attack" (the quoted
        # pointer in the existing block references @6776c667:6500). At M, line 6549 is the
        # sentence carrying that pointer; the line text contains "58% attack". So add a
        # pointer to M with that line: resolves -> counter green although it points at the
        # very commit under test (self-resolving). Expect 0.
        edit("G10-self-resolving-rev", 0,
             "SCORECARD.md",
             "are recorded in `.ufo/waves/round-100/r99-measured.json`.",
             "are recorded in `.ufo/waves/round-100/r99-measured.json`; see also `SCORECARD.md@2e27e6f1:6549` (\"58% attack\").")
        # G11: phrase that is a single common character, e.g. ("e") on a line containing 'e'.
        # Counter: phrase non-empty and in line -> resolves. Weakens check 8 to trivial.
        edit("G11-single-char-phrase", 0,
             "SCORECARD.md",
             '(`SCORECARD.md@6776c667:6500` ("58% attack")',
             '(`SCORECARD.md@6776c667:6500` ("e")')
        # G12: pointer to a non-lane / other-surface file tools/x.py:12 (disclosed (b)).
        edit("G12-nonlane-pointer-tools", 0,
             "SCORECARD.md",
             ".ufo/waves/round-100/r99-measured.json`.",
             ".ufo/waves/round-100/r99-measured.json`; see tools/round100-record-audit.py:999 (not a lane record).")
        # G13: digit percentage inside a QUOTED pointer phrase that is not a bound pointer.
        # Check 5 strips only BOUND_RE phrases; a quoted phrase not in bound form keeps
        # its percentages and check 5 catches it -> caught. Expect 1.
        edit("G13-stray-pct-in-quotes-unbound", 1,
             "SCORECARD.md",
             ".ufo/waves/round-100/r99-measured.json`.",
             ".ufo/waves/round-100/r99-measured.json`; the old text said \"58% attack\" there.")
        # G14: dead-count contradicted in words in LOG only.
        edit("G14-words-two-dead-log", 0,
             "LOG.md",
             "had 12 seats, 0 dead (`.ufo/waves/round-99/w1-results.json`",
             "had 12 seats, 0 dead (but two seats were dead in prose) (`.ufo/waves/round-99/w1-results.json`")

        results = []
        for name, expect, kind, payload in cases:
            d = root / name
            r = run(["git", "clone", "-q", "--shared", "--no-checkout", str(lane), str(d)])
            if r.returncode:
                print(f"{name} CLONE-FAIL {r.stderr}"); continue
            top = run(["git", "-C", str(d), "rev-parse", "--show-toplevel"]).stdout.strip()
            assert Path(top).resolve() == d, f"toplevel mismatch {top} != {d}"
            run(["git", "-C", str(d), "checkout", "-q", "6776c667372a0da8635ebfbda6cbc92d8fb17304"])
            for f in FILES:
                (d / f).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(lane / f, d / f)
            if kind == "edit":
                f, old, new = payload
                p = d / f
                s = p.read_text()
                if s.count(old) != 1:
                    print(f"{name} ANCHOR-FAIL count={s.count(old)}"); continue
                p.write_text(s.replace(old, new, 1))
            elif kind == "append":
                f, text = payload
                with open(d / f, "a") as fh:
                    fh.write(text)
            env = dict(os.environ, GIT_AUTHOR_NAME="fixture", GIT_AUTHOR_EMAIL="fixture@scratch.invalid",
                       GIT_COMMITTER_NAME="fixture", GIT_COMMITTER_EMAIL="fixture@scratch.invalid")
            run(["git", "-C", str(d), "add", "--", *FILES])
            c = run(["git", "-C", str(d), "commit", "-q", "-m", name], env=env)
            if c.returncode:
                print(f"{name} COMMIT-FAIL {c.stderr}"); continue
            p = run([sys.executable, str(counter), "--repo", str(d), "--rev", "HEAD"])
            last = [ln for ln in p.stdout.splitlines() if ln.startswith("RECORD_AUDIT100 ")]
            detail = [ln for ln in p.stdout.splitlines() if "DETAIL" in ln]
            got = p.returncode
            verdict = "GREEN" if got == 0 else "CAUGHT"
            expect_word = "green" if expect == 0 else "caught"
            results.append((name, got, expect, verdict))
            print(f"EX02_FORGERY {name} rc={got} expect={expect_word} {verdict} "
                  f"::{last[0] if last else p.stdout[-160:]!r} {detail if detail else ''}")
        print(f"EX02_FORGERIES cases={len(results)} green={sum(1 for _, g, _, _ in results if g == 0)} caught={sum(1 for _, g, _, _ in results if g != 0)}")
        # write receipts table
        out = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-100/w1/out/EX02RecordForge/ex02_forgeries.tsv")
        out.write_text("".join(f"{n}\trc={g}\texpect={e}\t{v}\n" for n, g, e, v in results))
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
