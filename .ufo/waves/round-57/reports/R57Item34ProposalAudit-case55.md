# R57Item34ProposalAudit — distinct case 55: independent test of considerthese proposal 3

Seat `R57Item34ProposalAudit`, distinct case 55. This file is the separate evidence file for the independent test of `considerthese/2026-10-26.md` proposal 3 (“Keep a running count of counters that a shortcut can satisfy”). It does not repeat the proposal-audit narrative; that is in `.ufo/waves/round-57/reports/R57Item34ProposalAudit.md`.

Wave base `b89bdab2cc114735ec5d331c6c610134258f7864`; instrument under test `tools/shortcut-tally.py` (975 lines, v2, added in `c4b2175d`, registered at `SKILL.md:1476`). All runs were read-only on the lane (`--repo . --rev b89bdab2…`) or inside a throwaway fixture repo under `/fast/scratch/hyaku/kama-r57/R57Item34ProposalAudit/fixture`. No lane file was edited.

## Test 1 — does the tally trend the recent record at the frozen base?

Commands (cwd lane) and exact results:

1. `python3 tools/shortcut-tally.py --repo . --rev b89bdab2cc114735ec5d331c6c610134258f7864`
   → exit 0; header `rounds=40-47` (default from `tools/shortcut-tally.py:895`); rows 40–47 only. Receipt `R57Item34ProposalAudit.receipts/tally-base.out`.

2. same, `--rounds 40-56`
   → exit 0; header `rounds=40-56`; rows:
   - 48–53: `unreadable:mutation-report` (notes: “inconsistent killed=… survived=… equivalent=… total=…”, “no survived count”, “ambiguous survived”);
   - 54: `unreadable:no-section` (“SCORECARD.md has no `## Round N` heading”, “no wave dir”);
   - 55: `ok` but `shortcuts -` with note “frozen family matched no id; wide names K2Predicate,K4Sizing (naming blind spot, not a zero)”;
   - 56: `no-disclosure`.
   Receipt `tally-base-40-56.out`.

3. same, `--rounds 40-56 --check 99`
   → exit 1; `latest=56 shortcuts=- limit=99 result=FAIL (unreadable rounds [48, 49, 50, 51, 52, 53, 54])`. Receipt `tally-check99.out`.

4. `python3 tools/shortcut-tally.py --selftest --scratch …/selftest`
   → exit 0; seven cases + summary `selftest pass=7 fail=0`: `readable-round`, `check-fails`, `committed-bytes`, `bad-rev`, `unreadable-round`, `split-slash-uppercase-kill`, `contradictory-report`. Receipt `selftest.out`.

5. `grep -rn "shortcut-tally.py.*--check" .ufo/waves/round-4*/measured .ufo/waves/round-5*/measured`
   → no match. (The standing `measure.sh` lines run `python3 tools/shortcut-tally.py --repo . --rev "$TIP"` only.)

Interpretation: at the frozen base the instrument is red on coverage — it cannot read seven rounds (48–54) and its default range stops at 47 — but its plain invocation exits 0. The gate exists and fails when invoked (`--check`), yet no standing receipt invokes it. So proposal 3's “running count” is not running over the recent record, and its plain-run exit does not distinguish “cannot read” from “no shortcuts”.

## Test 2 — can the tally see a do-nothing control, or only disclosure prose?

Fixture repo (scratch only): `SCORECARD.md` with `## Round 56` / `## Round 57` sections, `## Round 57` containing a `### What \`met=True\` does not show (round-57)` block, plus `.ufo/waves/round-57/controls/c1-noop.py` copied byte-for-byte from the frozen control (prints `mismatches=0 maxN=46 met=True`). Repo initialised and committed locally; `git rev-parse --show-toplevel` asserted the fixture dir before the commit. Commit `8eeecb662b4214fcd2d90fb52a8c8401d6395b8a`.

1. `tools/shortcut-tally.py --repo <fixture> --rev 8eeecb66… --rounds 57-57`
   → exit 0; row `57  -  -  -  0  -  none  unreadable:no-claim-ids`; notes “disclosure block names no C1/C2/C3”, “no wave dir”. No output line references the control file, and the tool's documented sources (`tools/shortcut-tally.py:49-62`) are `SCORECARD.md` and `.ufo/waves/round-N` `*.md` reports, not `controls/`. Receipt `fixture-57.out`.

2. Fixture disclosure rewritten to name a seat and a claim in one sentence: “Seat K1Cheat: a no-op control prints the frozen literal and executes nothing, yet C2 reports met=True.” (commit `04f9ff610cf55c58ccdfc3aeef2ecfdebfe929ce`), run `--check 5`
   → exit 0; row `57  1  K1Cheat  C2  K1Cheat  -  none  ok`; `latest=57 shortcuts=1 limit=5 result=PASS`. Receipt `fixture-57-named.out`.

3. Reverted the fixture SCORECARD to variant 1 (`f53fc88f2901d314da757678d1b787dce0e5da4d`) and ran `--check 0`
   → exit 1; `latest=57 shortcuts=- limit=0 result=FAIL (unreadable rounds [57])`. Receipt `fixture-57-check0.out`.

Interpretation: the tally's unit is a sentence in the lane's own SCORECARD disclosure; the control artifact is not an input. A round can be “counted” by declaring a shortcut in prose with a claim id, and a round whose only shortcut evidence is a no-op control file is either unreadable or absent. This is the exact gap the round-57 C1 target (bind declared roster to executed calls) is about, and the tally cannot substitute for it.

## Test 3 — is the premise “nothing trends it” true today?

- `git log --diff-filter=A --format='%h %ci %s' -- tools/shortcut-tally.py` → `c4b2175d 2026-10-26 19:51:07 -0300 round-48: integration (measured) … shortcut tally …`.
- `tools/shortcut-tally.py:10-13` names “`considerthese/2026-10-26.md` proposal 3” and the round-47 draft as its origin.
- `SKILL.md:1476` registers the Round-48 shortcut tally with `selftest pass=7 fail=0`.
- Standing runs exist for rounds 48–53 (`.ufo/waves/round-48/measured/tally.out`; round-49..53 `measure.sh` + `tally-build.out`/`tally.out`), none for 54–56.

Conclusion: the premise is false; the residual is cadence and read coverage, matching the round-55 seat S6Considerthese finding, not a missing instrument.

## Limits of this test

- I ran the tool against the lane repository read-only at the frozen base, not a fresh clone; the tool's own `committed-bytes` selftest case is the evidence that a worktree edit cannot change `--rev` bytes.
- The fixture is a minimal git repo built in scratch, not the lane; it exercises the parser and the gate, not the lane's full SCORECARD text.
- I did not modify the fixture to make the tally read `controls/*.py`; the test demonstrates invisibility, not a proposed fix.
- No lane counter was re-run for this case; the base/tip counter values cited in the report are quoted from committed receipts.

## Artifacts

- Receipts: `.ufo/waves/round-57/reports/R57Item34ProposalAudit.receipts/` (`tally-base.out`, `tally-base-40-56.out`, `tally-check99.out`, `selftest.out`, `fixture-57.out`, `fixture-57-check0.out`, `fixture-57-named.out`, `s515-quote-check.txt`, `source-hashes.txt`).
- Scratch: `/fast/scratch/hyaku/kama-r57/R57Item34ProposalAudit/` (fixture repo + selftest fixtures; removed after receipts were copied).
- Report: `.ufo/waves/round-57/reports/R57Item34ProposalAudit.md`
- Case 55: `.ufo/waves/round-57/reports/R57Item34ProposalAudit-case55.md`
