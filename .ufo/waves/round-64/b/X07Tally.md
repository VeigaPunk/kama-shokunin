# X07Tally - shortcut-tally rounds 56-63 reader (round 64, wave b, C2 tally conjunct)

Seat verdict: none (advisory). Result: **8 of 8 rounds carry a statement in committed bytes; the reader was extended; patched tool + selftest delivered.** No STOP condition: the evidence reaches every round, so nothing was invented.

Bytes: lane `0c1eff3cb9ac4c11402ab0124c35842f06a436fc` (frozen base) read through git objects; fleet reports read with `git -C /home/vgpnk/Projects/shokunin show HEAD:.ufo/reports/round-N/kama.md` (fleet HEAD at read time `fe4fe45e4123fbc1f7dd39c3f3e564dd17edf29a`). Work done in a scratch clone at freeze `f6a4ea9a`; lane source untouched; scratch removed.

Deliverables (`.ufo/waves/round-64/b/out/X07Tally/`):
- `shortcut-tally.py` - patched tool (sha256 `85db3cffa0c4c4b4ada10d37a7fe27cc346dcebda0ee8d234e1489140d55ff9e`, 1347 lines); `shortcut-tally-r64.patch` - the diff vs the freeze blob (`D868`).
- `before-56-63.txt`, `after-56-63.txt`, `after-56-63-fleet.txt`, `after-56-63.json`, `before-40-63.txt`, `after-40-63.txt`, `after-40-63.json`, `before-selftest.txt`, `after-selftest.txt`, `mutants.txt`, `statements-by-round.txt` (every first citation, incl. fleet).

## 1. Investigation: what exists, per round (path:line, lane at 0c1eff3c unless marked fleet)

None of rounds 56-62 has the `What `met=True` does not show` block (only SCORECARD.md:3346, round 63). Every round has the same facts in other formats:

| Round | Statement kind | Where (path:line) |
|---|---|---|
| 56 | shortcut | SCORECARD.md:3129-3131 (C2 "counter target falsified for admission"; "frozen counter checks a declared ROSTER literal ... no-op fixture proves that target is reachable"); corpus/lessons/round-56.md:29 (vacuous-target: roster counter passes a no-op harness, `met=True`); corpus/lessons/round-56-verifier-spotcheck.md:14; fleet round-56 kama.md:10 |
| 56 | survivor | corpus/lessons/round-56.md:26 (`class: survivor`, M08ReceiptField mutated comparison survived); seat reports .ufo/waves/round-56/w1/out/M07BaseMutation.md:3 ("SURVIVED"), M08ReceiptField.md:10 |
| 56 | falsify wave | ran, folded: `.ufo/waves/round-56/w1/{spec,dispatch}.json`, 65 `.md` under the round (tool already read this: `yes(w1,folded)`) |
| 57 | shortcut | SCORECARD.md:3156 (no-op `met=True` -> `met=False`), SCORECARD.md:3186 ("dead-code and unused-function call-site no-ops still return `met=True`"); lessons/round-57.md:26,28; round-57-verifier-spotcheck.md:21,37; fleet round-57 kama.md:29,58,68 |
| 57 | survivor | SCORECARD.md:3186 ("two survivors"); lessons/round-57.md:28 (`residual-noop-survivor`); round-57-verifier-spotcheck.md:58; fleet round-57 kama.md:62 |
| 57 | falsify wave | named layout `.ufo/waves/round-57/w1-{spec,dispatch,results}.json` + `w1/out/*.md` (117 `.md`); fleet round-57 kama.md:32 ("swarmed falsification review remains unsettled at report time") |
| 58 | survivor | SCORECARD.md:3204 ("Survivors outside the 11 enumerated no-ops (decoy `--counter`, discarded leg verdict, thread-issued leg, copied legs) and mutants that the frozen sets cannot see ... are limits"); lessons/round-58.md:32,34; round-58-verifier-spotcheck.md:37; fleet round-58 kama.md:12,14 |
| 58 | shortcut | fleet round-58 kama.md:12 ("decoy/vacuous `--counter`, discarded leg verdict, copied legs"); lessons/round-58.md:29 (round-57 checker accepted dead-code/unused-function no-ops) |
| 58 | falsify wave | `.ufo/waves/round-58/w1-{spec,dispatch,results}.json`, 72 seats, 74 `.md`; SCORECARD.md:3204 "no seat falsified either frozen predicate" |
| 59 | shortcut | lessons/round-59.md:36 (R04 one-call decoy battery "accepted by the measured checker ... `met=True`"), :38 (K05 static assertion, "C2 still returns `mismatches=0 met=True`"; M12 eight clause mutants all meet); round-59-verifier-spotcheck.md:14; SCORECARD.md:3227-3228 ("Not verified. R04 ... passes ... K05 ... M12's eight one-clause counter mutants all meet"); fleet round-59 kama.md:10,11 |
| 59 | survivor | SCORECARD.md:3228 (M12 mutants all `met=True`) and wave seat reports (.ufo/waves/round-59/w1/out/M04DropLabelSet.md:7); the tool's reader does not match 3228's wording ("all meet") - not needed for the status |
| 59 | falsify wave | `.ufo/waves/round-59/w1/w1-{spec,dispatch,results}.json`, 61 `.md` |
| 60 | shortcut | SCORECARD.md:3232 ("falsified frozen claims"), SCORECARD.md:3239 (K01 do-nothing registry `met=True`, 5 unrelated literals + 9 boilerplate rows, `controls_rejected=35/35`); lessons/round-60.md:1,19; round-60-verifier-spotcheck.md:19,36,49 ("semantically gameable"); fleet round-60 kama.md:10 |
| 60 | survivor | none in lesson/SCORECARD wording (K01 is a do-nothing registry, not a mutant); wave seat MT-type reports exist under `.ufo/waves/round-60/w1/out/` (MT02ToolCheckNeutering, MT04FalsifiableGaming) |
| 60 | falsify wave | two waves: `w1` (build + first falsifiers) and `w2` ("w2 falsify", 32 seats); both with `-results.json`; 147 `.md` |
| 61 | no-falsify | lessons/round-61-verifier-spotcheck.md:59 ("the wave-level seat falsification never ran"), :91 (wave "never ran" - wrapped line, not matched by the reader); `.ufo/waves/round-61/w1/w1-dispatch.json` + `w1-spec.json` present, **no** `w1-results.json`, **zero** `.md` under the round |
| 61 | shortcut / survivor | none stated in lane or fleet bytes (SCORECARD.md:3250-3257 reads "PENDING wave verdicts" and "Limits the counters cannot see: hold-window contact proves one port's liveness ..., sensitivity mutates last-segment mutables only" - a limit statement, not a shortcut/survivor, not matched) |
| 62 | shortcut | SCORECARD.md:3271 (C2 "not verified", vacuous sensitivity); lessons/round-62.md:21,25 (`vacuous`: counter's sensitivity `pattern in out.replace(pattern, MUT)` false by construction); round-62-verifier-spotcheck.md:20,39; fleet round-62 kama.md:8 |
| 62 | no-falsify | lessons/round-62-verifier-spotcheck.md:17,40 ("the dispatched falsification wave had no WAVE-DONE/results handoff"); `.ufo/waves/round-62/w1/w1-{spec,dispatch}.json` but **no** `w1-results.json` (81 `.md` exist, seats wrote to `w1/*.md`); fleet round-62 kama.md:10 ("Honest stop") |
| 63 | disclosure block | SCORECARD.md:3346 (v2 reader already `ok`); plus MT15 forgeries `met=True 44/44` at lessons/round-63.md:48, round-63-verifier-spotcheck.md:38,52; fleet round-63 kama.md:12 |
| 63 | falsify wave | `.ufo/waves/round-63/w1/w1-{spec,dispatch,results}.json`, 76 `.md` |

Count: **8/8 rounds with at least one committed statement** (lane + fleet hits per round: R56 7, R57 12, R58 7, R59 7, R60 7, R61 1, R62 8, R63 22 + the block; lane-only: R56 4, R57 8, R58 5, R59 3, R60 5, R61 1, R62 7, R63 16 before the survivor-context/negation guards, see out/statements-by-round.txt for the guarded run). Weakest round: **61** (one lane hit, no fleet hit; its disclosure is the *absence* of a falsify wave, corroborated by dispatch-without-results/reports). Rounds 59 and 60 have no survivor wording in summary documents (shortcut only).

Reasons v2 printed 7/8 `no-disclosure`: (a) it reads only the SCORECARD block (rounds 56-62 never wrote one); (b) its falsify column looks for `<wave>/spec.json`/`dispatch.json`, but from round 57 the files are `w<N>-spec.json`/`w<N>-dispatch.json` (inside the wave dir or beside it), so rounds 57-63 printed `falsify=none` and notes `no wave dir` although every round ran a wave (round 61 stalled).

## 2. What changed in tools/shortcut-tally.py (v2 -> v3; patch in out/)

1. New status `disclosed:<kinds>` (kinds: `shortcut`, `survivor`, `no-falsify`, `+`-joined). `ok` stays reserved for the formal block; a statement is not a count, so shortcuts/ids/counters/mutants columns stay `-` and `--check` still cannot certify such a round (unchanged contract; note the latest round 63 already fails `--check` at base for the same reason: block names no `K..`-shaped id).
2. Statement reader (`STATEMENT_PATTERNS`, `read_statements`): sources are the SCORECARD `## Round N` section, `corpus/lessons/round-N.md`, `corpus/lessons/round-N-verifier-spotcheck.md`, and optional `--fleet-repo/--fleet-rev/--fleet-report` (default `.ufo/reports/round-{n}/kama.md`). Every hit is printed as `detail: round N: statement <kind> <source> path:line '<text>'` and counted per kind/source in the record's `statement_counts`.
3. Guards (each added after a measured false positive): negation in the 24 characters before a match (`no seat falsified`, `not vacuous`, `non-vacuous`, `no mutants survived`) is not a statement; a `survive*` mention must name what survived (mutant/counter/checker/control/fixture/...) within 80 chars. Wave seat reports are **not** read: a first run that included them produced noise (`non-vacuous` verdict lines, a PIT source row `survivor`, a copied canonical-noop SCORECARD control fixture under `.ufo/waves/round-57/controls/`), so status would have been inflated.
4. Named wave layout in `wave_falsify` (`_wave_dirs`): `w<N>-spec.json`/`w<N>-dispatch.json` inside `<wave>/` or at round level; reports = every `*.md` under `<wave>/`; context `w<N> falsify` counts as dedicated; a dispatched named wave without `w<N>-results.json` prints a note. Legacy waves keep the `out/` rule.
5. Docstring (v3, Status section, selftest list) updated; selftest grew from 7 to 10 cases.

## 3. Before / after

Command (frozen): `python3 tools/shortcut-tally.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev 0c1eff3c --rounds 56-63`

Before (v2, freeze blob):
```
56 -  -  -      0  -  yes(w1,folded)  no-disclosure
57 -  -  -      0  -  none            no-disclosure
58 -  -  -      0  -  none            no-disclosure
59 -  -  -      0  -  none            no-disclosure
60 -  -  -      0  -  none            no-disclosure
61 -  -  -      0  -  none            no-disclosure
62 -  -  -      0  -  none            no-disclosure
63 -  -  C1,C2  0  -  none            ok            -> tally_disclosed = 1/8
```
After (v3):
```
56 -  -  -      0  -  yes(w1,folded)     disclosed:shortcut+survivor
57 -  -  -      0  -  yes(w1,folded)     disclosed:shortcut+survivor
58 -  -  -      0  -  yes(w1,folded)     disclosed:survivor
59 -  -  -      0  -  yes(w1)            disclosed:shortcut
60 -  -  -      0  -  yes(w2,dedicated)  disclosed:shortcut
61 -  -  -      0  -  stalled(w1)        disclosed:no-falsify
62 -  -  -      0  -  yes(w1,folded)     disclosed:no-falsify+shortcut
63 -  -  C1,C2  0  -  yes(w1,folded)     ok                 -> tally_disclosed = 8/8
```
With `--fleet-repo /home/vgpnk/Projects/shokunin --fleet-rev HEAD` the statuses gain `no-falsify` for round 57 (`disclosed:no-falsify+shortcut+survivor`) and `shortcut` for 58; others unchanged (`out/after-56-63-fleet.txt`). tally_disclosed counted as rows whose status is neither `no-disclosure` nor `unreadable:*`.

Regression 40-63 (`before-40-63.txt` vs `after-40-63.txt`, record-by-record diff): rounds 42-44, 46-55 identical. Changed: 41 and 45 `no-disclosure` -> `disclosed:...` (they too have lesson statements), 56-62 as above, 63 falsify `none` -> `yes(w1,folded)`. **Round 40 still prints `no-disclosure`** (a real round with no statement in lane bytes), so the extension does not make every round non-silent. The rounds 42-53 `unreadable:*` values are unchanged and out of scope.

## 4. Selftest (still has fixtures that MUST print `no-disclosure`)

`python3 tools/shortcut-tally.py --selftest --scratch <dir>` -> `selftest pass=10 fail=0` (`after-selftest.txt`; base 7/7). New cases:
- `statement-formats`: rounds 20/21/23 with no block read `disclosed:shortcut+survivor` (lesson), `disclosed:no-falsify` (spotcheck + named-layout wave stalled), `disclosed:shortcut` (SCORECARD-only); falsify columns `yes(w1,folded)` / `stalled(w1)`.
- `no-disclosure-stays`: round 22 (only negated/unrelated wording: "No mutants survived", "non-vacuous", "no seat falsified a frozen predicate", "survey of survivors in the wild") and round 24 (nothing) both print `no-disclosure`.
- `fleet-report`: round 24 is `disclosed:survivor` with a fleet report, `no-disclosure` without.

Selftest mutants of the patched tool (`mutants.txt`): 6 of 6 KILLED - no-negation guard, always-disclosed (drop the "statements exist" condition), no survivor-context rule, no named-wave reading, status never set, lessons not read. The survivor-context rule was added because the round-22 fixture, run before the rule existed, failed with `disclosed:survivor` (a real false positive the first version had).

## 5. Limits and handoff to the L1

- The reader is regex-based over wording; each hit is cited so a human can verify it, but it does not prove a statement is *true* - only that the lane wrote it. Lines wrapped across newlines are missed (round 61 :91). A disclosure written only in a wave seat report is not read by design.
- The status is `disclosed:*`, not `ok`; if the C2 counter wants a different literal it must parse `status != no-disclosure` (the frozen predicate's wording). The extra `--fleet-*` flags are optional; the lane-only command reaches 8/8 alone.
- Pre-existing, not changed: `--check` at the latest round cannot certify when the block names no `K<d>Cheat`-style id (round 63 prints `latest round 63 cannot certify a shortcut count (ok)` and exits 1 at base and after).
- The pin table for `tools/shortcut-tally.py` (13 files) must use the sha256 of whatever blob the L1 integrates; the seat did not commit or place the file in the lane. Checks for the main agent after integration: the frozen tally command above, `--selftest` (expect pass=10 fail=0), `python3 -m py_compile tools/shortcut-tally.py`.
- Install/update log: none (standard-library Python only; no package changes).

One-line outputs: `tally_disclosed=8/8` (base `1/8`); `selftest pass=10 fail=0` (base `pass=7 fail=0`).
