# ScribeScorecard — round-23 scorecard draft report

Verdict: **partially** — the round-23 SCORECARD block is drafted with its
measured table left as `[PENDING]`. The source-count and frozen-arm identity
checks were observed; the C1 grid and mutant numbers are the L1's declared
figures and were not re-executed (scribe rule: no rerun to decorate).

Lane HEAD measured: `245a37f69628c2c6bb29bbf17897d8fb5946c857` (`git rev-parse HEAD`).
Round base: `4fe9339f8fc3a4a4a479d9c938a850da12f1124d`.

## Deliverable

- Draft: `.ufo/waves/round-23/falsify/out/ScribeScorecard/SCORECARD-round-23.md`
  (not appended to `SCORECARD.md`; round-22 block at `SCORECARD.md:1035-1150`
  used as style reference).

## Observed (scribe)

| Check | Command | Observed |
|---|---|---|
| Frozen auditor identity | `git rev-parse 4fe9339f…:tools/report-landing-audit.py` | `fcc255ce5115a749dfbd09cf992ba9851a2dc90a` (blob). `git cat-file -t 4fe9339f…` → `commit` |
| Grid harness frozen pin | `tests/report-audit/repo-state-grid.py:31` | `FROZEN = "4fe9339f…"` (a commit); read via `cat-file blob FROZEN:AUDIT` at `:639-640` |
| Source rows | `grep -cE '^\| S0[0-9]{2} ' corpus/SOURCES.md` | HEAD 95; base `4fe9339` 88 |
| Source tiers | awk over column 5 | base A83 B2 C3 → HEAD A90 B2 C3 |
| Source delta | `git diff --numstat 4fe9339 HEAD -- corpus/SOURCES.md` | `7 0` (additions only) |
| Fault rows / mutants | `grep -oE '\bF[0-9]{2}\b'` / `M[0-9]{2}` | F01–F26 (26 IDs); M01–M24 (24 IDs) |
| Round-23 run receipt | `ls .ufo/waves/round-23/` | no `runs/` directory → no committed measurement exists |

## Findings

1. **Identifier mislabel (fix before publication).** The round-23 lesson
   (`corpus/lessons/round-23.md:15`) and the wave brief call the frozen arm
   "the `4fe9339f` blob" / "blob 4fe9339f…:tools/…". `4fe9339f` is a commit.
   The frozen blob is `fcc255ce5115a749dfbd09cf992ba9851a2dc90a`. The code is
   correct (`FROZEN` is a commit, resolved at `:640`); only the prose is wrong.
   Recommend the SCORECARD block and lesson say "commit `4fe9339f`, blob
   `fcc255ce…`". The draft uses this corrected form.

2. **No committed measurement receipt for round 23.** `.ufo/waves/round-23/`
   contains `build/`, `falsify/`, `probe/`, `sources/` only. Every C1 number
   (0/26, 26/26, 8/8, 24 mutants, 22 killed, selftest 50/50, 9 defects) is
   the L1's declared figure and is unverified by this seat. The draft keeps
   each as `[PENDING]` with the expected exit. Main agent should run the
   recipe once after integration, pinned to the committed tree, and fill the
   table from `runs/<SHA>/`.

3. **Expected-exit caveat.** `--arm frozen` and `--arm both` are red by design
   (`repo-state-grid.py:18`). The scorecard must not read a red frozen arm as
   a regression; the draft says so.

4. **Trend labels are inference.** The lesson names no capability row, so
   "expansion unchanged" is labelled `[INFERENCE]`. "Quality improved" and
   "discernment improved narrowly" are the scribe's reading of a closed D4
   gap and a frozen control that fails 26/26; L1 must ratify or revise.

5. **Sources census not run.** The round-22 block quotes the
   `scripts/sources-census.sh` census with W04 warnings. The round-23 census
   line is `[PENDING: run by main agent]`. Row counts were checked by grep and
   awk only.

6. **Open items carried, not graded.** O01 (alternates), O02 (gitfile),
   ambiguity overwrite, second Landed section, errata CR, unisolated sibling
   tools — listed under Planned, as in the lesson.

## Not verified by this seat

- No grid, mutant, selftest, ledger or census command was executed.
- Source quotes in S089–S095 were not re-opened; the lesson states they were
  opened 2026-10-21 by the L1 and build scouts.
- The lane `SCORECARD.md` was not modified; no commit, push or jj command.

## Files written

- `.ufo/waves/round-23/falsify/out/ScribeScorecard/SCORECARD-round-23.md` (new)
- `.ufo/waves/round-23/falsify/advice/ScribeScorecard.md` (new, this file)

## Tools installed or updated

None. All checks used git, grep, awk and sed already on the host.

## Checks for main agent after integration

1. `python3 tests/report-audit/repo-state-grid.py --arm current --json` (expect 0)
2. `python3 tests/report-audit/repo-state-grid.py --arm frozen --json` (expect 1)
3. `python3 tests/report-audit/isolation-mutants.py --json` (expect pristine pass, 22 killed)
4. `python3 tools/report-landing-audit.py --selftest` (expect 0, 50/50)
5. `python3 tools/report-landing-audit.py --rounds 10-22 --no-errata --json` (expect 1)
6. `python3 tools/report-landing-audit.py --rounds 10-22 --json` (expect 0)
7. Census: `scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama` (expect 95 rows)
