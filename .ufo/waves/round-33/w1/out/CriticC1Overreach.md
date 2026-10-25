# CriticC1Overreach — round-33 w1 critique (calibration axis, C1 scope)

Seat: CriticC1Overreach (critic, leaf). Lane: kama-shokunin. Tip examined:
`7c35289da5f4b94e062cd900eb086919e5094003` (HEAD at review time). Target: does
C1's "KQ39 correction census" overstate the three-receipt scope?

## Verdict

**No overreach found.** The counter proves exactly the three named round-32 C2
evidence mismatches and nothing else; every wording surface — preregistration,
SCORECARD round-33 section, round-33 lesson, tool output — is three-bounded or
names the three files. It is not described anywhere as a general
SCORECARD/SHONEN audit; the lesson carries an explicit scope fence against that
reading.

## Counterexample tested (strongest available)

The frozen C2 row cites a wildcard, `c2/controls/*-v2.out`, and claims "each
fixture exits 1 with its named defect". The strongest overreach attack is that
"three false references" under- or over-counts what the wildcard covered.

Evidence (`git ls-tree` at `dc4258bdb08d658f1c5b15abc8378461659bd155`):
the glob matched **six** files in `.ufo/waves/round-32/c2/controls/`:

- `thin-row-v2.out`, `empty-exit-v2.out`, `nonexistent-path-v2.out` — bodies are
  the base-tree output (`unregistered round-17/round-26`, `registered 7
  unregistered 2 defective 0`); named defect lines absent → **false**.
- `thin-v2.out`, `noexit-v2.out`, `badpath-v2.out` — bodies contain the named
  defect lines → correct receipts the statement never singled out.

So "three false" is the *exact* false subset of the wildcard population: not a
cherry-pick, not an undercount, and the claim's phrase "a wildcard control set
containing three receipts whose bodies do not show the named defects" is
literally true of the six-member set. The claim does not assert — and the
counter does not prove — that the *other* components of the same C2 row (v1
controls `*-v1.out`, `gate-tip.out`, `before-base.out`, S193 quote) were all
correct; C1 never claims that.

## What the counter enumerates

`tools/round33-claim-audit.py` (read at tip, tag #4E2F):

- `FAULTS` hardcodes exactly three keys — `thin-row`, `empty-exit-map`,
  `missing-path` — each pinning one stale `*-v2.out` path, one correct
  replacement path, and one expected defect line (lines 19–35).
- `unresolved = len(FAULTS) − valid`; `met` requires `false_at_writing == 3 ∧
  valid == 3` (lines 145–148). Nothing outside the dict is counted; extra
  correction-table rows or other SCORECARD faults are ignored, i.e. the counter
  is narrower than "any SCORECARD mismatch", never wider.
- Duplicate correction rows for one fault fail `len(entries) != 1` — no
  inflate-by-repetition.
- `legacy_mislabels_at_tip=3` re-verifies the three stale files still exist
  byte-intact at tip, matching the "explicitly disclosed as legacy evidence"
  wording instead of silently absolving them.

Independent replay at current tip (read-only; the tool only reads Git blobs):

```
R33_CLAIM_AUDIT statement_rev=dc4258…bd155 tip=7c35289…94003
false_at_writing=3 valid_corrections=3 unresolved=0 legacy_mislabels_at_tip=3 met=True   exit 0
```

consistent with recorded `.ufo/waves/round-33/c1/after-evidence-tip.out`
(tip `1c881bbd…`) and `base-control-amend1.out` (base `cc469803…` →
`3/0/3 met=False`, exit 1).

## Universal-wording scan (flagging per task)

Grepped every C1-bearing surface (`preregistration.json` claims.C1,
`SCORECARD.md` round-33 section lines 1826–1882, `corpus/lessons/round-33.md`,
tool docstring). Universals found and dispositions:

1. **KQ39 criterion text** — "every checkable self-assessment statement is
   evaluated at its writing revision" (`round-33.md` mistake row 2). Universal,
   but it defines the *criterion that caught the defect*, not the claim's
   measured population. Not overreach.
2. **Lesson scope fence** — "Do not count the whole SCORECARD or SHONEN
   population" (`round-33.md` §Claims, C1 bullet). An explicit narrowing — the
   opposite of overreach; this is the sentence that keeps `unresolved=0` scoped.
3. **Round-34 plan** — "Use KQ39 to identify *any* separate SCORECARD/SHONEN
   statement mismatch at its writing revision … Do not repeat the three
   resolved round-32 receipt references" (`SCORECARD.md` Planned round 34).
   Universal only as *future* work; it treats the three as resolved, not as the
   whole-population census.
4. **Frozen C2 row's own "each fixture"** — applies to the four named fixtures
   (thin, empty-exit-map, missing-path, prose-only), not a claim about all six
   `*-v2.out` files; the correction correctly targets only the three receipts
   that falsified it.

No wording claims "all mismatches corrected", "no remaining SCORECARD
inconsistency", or a whole-file/whole-SHONEN audit.

## Residual nit (disclosure-grade, not a defect)

Bare `unresolved=0` / `met=True` detached from context could be misread as "the
SCORECARD is now consistent". Every in-repo appearance prints the full tuple
(`false_at_writing=3 valid_corrections=3 unresolved=0 …`), the correction table
names the three receipts, and the lesson fence is adjacent — so a faithful
reader cannot reach the universal reading. A canonical Rust judge should accept
the claim as scoped; no correction required.

## Smallest safe correction

None needed for C1 as written. If the L1 wants belt-and-braces for future
rounds, a field rename (`unresolved_of_named=0`) would remove the last
misreading surface — optional, not this round's work.

## Tooling record

None installed or upgraded. Used only read-only `git` (log/show/ls-tree/
rev-parse) and `python3 tools/round33-claim-audit.py` (reads Git blobs, never
writes; verified at tip `7c35289d`, exit 0). Pacman untouched per the
host-wide pause ruling.
