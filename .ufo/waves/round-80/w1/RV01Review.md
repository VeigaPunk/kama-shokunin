# RV01Review — adversarial review of the C1 counter's grading rules

Seat: RV01Review (reviewer, kama r80 w1). Instrument under review:
`/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round80-selfrecord-round79.py`
(committed blob at the graded tip, sha256 `61e49d4fcdac3a4d987ef693f50c33b9ee5054905973d0981d535edc8129e46d` — identical to the worktree bytes I attacked).
Sealed revision graded: `a9b4543f14625d0f37daa42ef664ee6f6ea975ea`. Lane tip read with
`git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master`.
No lane file was edited; all fixtures live under the scratch root
`/fast/scratch/hyaku/kama-r80/RV01Review/` (deleted at yield). Receipt copies:
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/RV01Review/`.

## Grading rules under test (frozen text, plans/round-80-claims.md §C1)

A fact passes when it re-derives at the sealed revision AND at the tip, or when exactly one
committed `corrected F<n> old=<value> new=<value> at=<40-hex> date=<ISO>` block answers it:
`old` = the fact's sealed value, `at` = the sealed revision (40 hex, resolving to it),
`new` = the fact's tip value. Two blocks for one fact answer nothing; a 41-char or
unresolvable `at` answers nothing; a `new` that does not re-derive leaves the fact unbacked.
Facts are read from `git show <rev>:<path>`, never the worktree (round-78 F2 defect class).
Container: `corpus/lessons/round-80.md` §Corrections, read at the tip.

## Live grade at the settled tip (master 223c881a3ae74679ed5c8cbc713f331f97a12338)

- `python3 tools/round80-selfrecord-round79.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin`
  → prints `SELFRECORD_R79 claims=6 mismatches=0 corrected=3 unbacked=0`, exit 0.
  F1/F2/F3 fresh; F4/F5/F6 corrected. Receipt: `.ufo/waves/round-80/w1/RV01Review/live/final-score.out`.
- Control `... --no-corrections` → `SELFRECORD_R79 claims=6 mismatches=3 corrected=0 unbacked=0`, exit 1
  (exactly the frozen control line). Receipt: `live/final-nocorr.out`.
- `--enumerate` → `SELFRECORD_R79_ENUM claims=6 stale=0 corrected=3`, exit 0. Receipt: `live/final-enum.out`.
- `--selftest` → `SELFRECORD_R79_SELFTEST pass=9 fail=0`, exit 0. Receipt: `live/selftest-v2.out`.
- Declared values verified against sealed bytes directly: F1 `## Axes` (operability 8, calibration 7);
  F6 LOG sentence present at sealed but split across lines 3–4 ("all verified on\ntheir receipts:") —
  the counter flattens whitespace before matching, so `grep -c` on raw bytes shows 0 while the
  counter's declared value `log=all-verified` is correct. Receipts: `live/sealed-facts.out`, `live/sealed-log-round79.out`.

The target line and the control both behave as frozen: a do-nothing round cannot print the target,
and the corrected round does.

## Attacks (fixtures under the scratch root; every git call named `-C "$D"`)

Fixture shape per attack: commit A (ancestor) → commit S (sealed record: F4/F5/F6 stale by
construction, F1/F2/F3 fresh) → commit T (tip; lesson + case mutation). Command per attack:
`python3 <lane>/tools/round80-selfrecord-round79.py --repo <fixture> --sealed <S> --tip <T>`.
Full outputs: `.ufo/waves/round-80/w1/RV01Review/attacks/<case>.out`.

| # | attack | verdict | exit | evidence |
|---|---|---|---|---|
| a0 | baseline: three valid corrections | CATCHES (grades) | 0 | `claims=6 mismatches=0 corrected=3 unbacked=0` |
| a1 | forged correction, wrong `old` (`c2=other`) | CATCHES | 1 | `reasons=old-mismatch`, `unbacked=1` |
| a2 | `at` = 41 hex (sealed + `0`) | CATCHES | 1 | `reasons=at-malformed`, `unbacked=3` |
| a3 | `at` = resolvable 40-hex ANCESTOR commit (≠ sealed) | CATCHES | 1 | `reasons=at-not-sealed`, `unbacked=3` |
| a4 | two blocks for one fact | CATCHES | 1 | `reasons=duplicate-blocks`, `unbacked=1` |
| a5 | `new` that does not re-derive at the tip | CATCHES | 1 | `reasons=new-not-rederived`, `unbacked=1` |
| a6 | worktree shadow (uncommitted edits refuting every fact) | CATCHES | 0 | unchanged `corrected=3` line; graded bytes are `git show` only |
| a7 | `corrected=` counted from prose | CATCHES | 1 | prose w/o field syntax scores `corrected=0`; field-syntax text is parsed as a block (see a8) |
| a8 | valid block outside §Corrections (`## Narrative`) | MISSES | 0 | `claims=6 mismatches=0 corrected=3 unbacked=0` — accepted |
| a9a | tip record bytes differ from sealed; blocks carry SEALED-declared `old` | CATCHES | 0 | `corrected=3` — declared is read at sealed, observed at tip (round-78 F2 defect fixed) |
| a9b | same tip; blocks carry TIP-declared `old` | CATCHES | 1 | `reasons=old-mismatch` ×2 — tip-declared cannot be passed off as sealed-declared |
| a10 | lesson valid but uncommitted | CATCHES | 1 | `corrected=0` — only the committed tip blob is read |
| a13 | tip grows SOURCES rows + knowledge (F2 drift) | CATCHES (repair) | 0 | F2 stays fresh under `SEALED_BOUND` |
| a14 | F2 correction asserting the changed tip population | CATCHES | 1 | row reason `new-not-rederived`, `unbacked=1` (sealed-bound `new` check) |

13 of 14 attacks behave per the frozen rules; 1 miss (a8).

## Findings

1. **MISSES — correction container section is not enforced (medium).** `corrections()` runs the
   block regex over the whole lesson file, never `block(text, "Corrections")`, so a correctly
   formatted block anywhere in `corpus/lessons/round-80.md` answers a fact, contrary to the
   frozen scope ruling ("The correction container is `corpus/lessons/round-80.md` §Corrections,
   appended"). Attack a8 exits 0 with `corrected=3` from blocks placed in `## Narrative`.
   Not exploited in the landed lesson — at master all three blocks sit inside `## Corrections`
   (`git show master:corpus/lessons/round-80.md`) — but the grading rule as coded is wider
   than the frozen container. Missing selftest arm: `correction-outside-corrections-section`.
2. **Missing selftest arm — `at-resolvable-ancestor` (the arm the suite claims to have).** The
   selftest case named `at-is-ancestor` truncates the sealed hash to 39 characters
   (`m_wrong_at` does `f"at={sealed[:-1]}"`), which fails the 40-hex fullmatch and records
   `at-malformed`; it never tests a resolvable non-sealed commit. `at-short-hex` likewise
   appends `0` (41 chars). Attack a3 is the missing arm: a real ancestor 40-hex is rejected
   with `at-not-sealed`, exit 1, so the rule holds — it is simply unarmed in `--selftest`.
3. **F5 receipt filename: prose vs code (informational).** The plan's F5 row and the counter
   docstring name `.ufo/waves/round-79/measured/before/c2-gate-arms.out`; the code reads
   `c2-gate-selftest.out`. At sealed and tip the arms file carries only `BASE_ARM_ORDER 9`,
   the selftest line `PRE_REPORT_SELFTEST pass=22 fail=0` lives in `c2-gate-selftest.out`, and
   the derived value string `before-selftest=pass=22` is identical either way. Cosmetic naming
   drift between plan/docstring and code; grading unaffected.
4. **Instrument evolved mid-wave; both generations attacked (disclosure).** Generation v1 (the
   bytes present when this seat started) live-graded master fe7b978 as
   `claims=6 mismatches=1 corrected=3 unbacked=0`, exit 1 — F2 stale, tip
   `population=sources:296,knowledge:53` vs sealed `293,52`: the freeze commit itself had
   appended S554–S556 and `corpus/knowledge/unregistered-class-second-engine.md`, falsifying
   the plan's F2 row ("observed at sealed and at the tip"). Receipt: `live/score-now.out`.
   The counter owner then landed generation v2 (sha256 `61e49d4f…`), adding
   `SEALED_BOUND = {"F2"}` so F2's observed value is pinned to the sealed tree
   ("later growth by the grading round cannot stale it", code comment at line 57).
   Consequences, verified: the frozen predicate's literal "matches the same fact re-derived
   at the tip" no longer holds for F2 (the tip tree is not consulted for it at all), and an F2
   correction whose `new` is the true tip population is now unbacked (attack a14). The frozen
   PREDICATE docstring sentence is byte-identical to the plan's; the deviation is documented
   only in the code comment. All 14 attacks were re-run against v2 (this report's table is v2;
   v1 results were identical except a13/a14 which target the new mechanism). At the settled
   tip 223c881a the frozen line and the frozen control both print as required (see Live grade).

## Answers to the seat's grading-rule questions

- Forged correction with wrong `old`? Rejected (`old-mismatch`).
- `at` with 41 hex? Rejected (`at-malformed`).
- `at` an ancestor but not the sealed revision? Rejected (`at-not-sealed`) — and this is the
  selftest's unarmed gap.
- Two blocks for one fact? Rejected (`duplicate-blocks`).
- `new` that does not re-derive at the tip? Rejected (`new-not-rederived`); the fact stays stale/unbacked.
- Fact graded against the worktree instead of `git show <sealed>`? No — worktree shadowing changes
  nothing (a6); derive/show/ls-tree/resolve are all rev-qualified.
- `corrected=` counted from prose rather than blocks? Ordinary prose cannot inflate it (a7);
  only regex-shaped text counts, and that text is accepted wherever it sits in the file (a8 gap).
- Round-78 F2 defect (declared from sealed bytes, observed from tip bytes)? Fixed and verified
  both directions (a9a accepts sealed-declared `old` against a changed tip record; a9b refuses
  tip-declared `old`), plus the live F2 drift catch in generation v1.

## Residual risk and verification gaps

- a8's container gap is the one rule violation found; recommend an owner-seat follow-up arm
  (`block(text, "Corrections")` scoping) in a future round, not a mid-wave edit of an instrument
  whose bytes receipts already cite.
- F2's sealed-binding means tip-side population drift is invisible to C1 from here on; if the
  lane wants tip-population coverage it needs a separate fact, not a silent widening of this one.
- I did not re-verify C2/C3 instruments (out of scope for this seat); C1's own selftest is 9/9
  and my 14-attack battery is the independent check.
- Poll window: master moved fe7b978 → 223c881a during this seat (five L1 commits); the counter
  was stable at `61e49d4f…` for the final 2.5 minutes and at every attack run after the v2
  landing. If the L1 lands further commits, re-run the frozen command (it is read-only).

## Receipt index (absolute paths; command + exit)

- Live: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/RV01Review/live/`
  — `final-score.out` (`--repo <lane>`, exit 0), `final-nocorr.out` (`--no-corrections`, exit 1),
  `final-enum.out` (`--enumerate`, exit 0), `selftest-v2.out` (`--selftest`, exit 0),
  `score-now.out` (v1 counter at fe7b978, exit 1 — the F2 drift record), `sealed-facts.out`,
  `sealed-log-round79.out`, `poll2.log` (tip/counter stability poll).
- Attacks: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/RV01Review/attacks/*.out`
  — each records the exact fixture command, sealed/tip oids, exit code, and full counter output
  (including the `--json` reason dump for a14, reproduced in its log).
- Driver (scratch, deleted at yield): `attack_driver.py` built each fixture with
  `git -C "$D" init -q`, asserted `rev-parse --show-toplevel == $D`, and ran the lane counter
  with explicit `--sealed/--tip`.
