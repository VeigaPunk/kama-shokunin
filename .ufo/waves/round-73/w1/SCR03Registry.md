# SCR03Registry — kama round 73, wave 1 (operability)

Record-only seat. Wrote the three new registry rows, amended the `Pre-report gate` row's description,
appended the round's `LOG.md` entry, created the `corpus/lessons/round-73.md` skeleton (`## Claims` +
`## Mistakes` only), and recorded every selftest this seat ran. No tool bytes, no `SCORECARD.md`, no
`corpus/SOURCES.md`, no `PROVINCE.md`, no commit.

Revision read at write time: `bc9e30599b6c6133bb094f0e7abd1a9f512778ec` (`git -C L rev-parse master`).
The freeze's base is `6e9619963fef5a3f8899324e9497416a00eab7e6`; the delta is the round's own two freeze
commits (`24bc96ad` claims + controls, `bc9e3059` wave spec), verified with `git log --oneline -3`.

## Touched surfaces

| Path | Change |
|---|---|
| `SKILL.md` | three rows added after `Receipt-tip binding` — `Round scope v2` (C1, `ROUND_SCOPE_V2 … cases=6`, exit 0/1/2, `ROUND_SCOPE_V2_SELFTEST pass=26 fail=0`), `Receipt-claim binding` (C2, `RECEIPT_CLAIM_BINDING … claims=<k> unbound_claims=<j>`, exit 0/1/2, `RECEIPT_CLAIM_BINDING_SELFTEST pass=14 fail=0`), `Province host drift` (C3, `PROVINCE_HOST_DRIFT blocks=<b> recorded=… live=… stale=<n>`, exit 0/1/2, `PROVINCE_HOST_DRIFT_SELFTEST pass=9 fail=0`); each row quotes its frozen predicate verbatim; the `Pre-report gate` row's description is amended **by append only** ("from round 73 on arm 6 `round-scope` calls `tools/round73-round-scope-cases.py`") and its round-72 `pass=8` tally is untouched |
| `LOG.md` | `## Round 73 (2026-11-03) — …` appended after the round-72 entry: base `6e961996`, freeze `24bc96ad`, the three condensed claims, the pre-freeze control lines, frontier step, axis note, wave shape, registry/lesson pointers |
| `corpus/lessons/round-73.md` | created by this seat (108 lines): `## Claims` (three frozen predicates verbatim + case population/exit map/kill rule) and `## Mistakes` (3 entries, each class · evidence pointer · captured-by · fix). SCR01Sources then appended `## Gate` (with the CORPUS.md rule-2 used-by table) at 23:44 and revised its citation sentence at 23:46; the file is now 141 lines and co-assigned by the two spec items. `## Wave` does not exist |
| `.ufo/waves/round-73/w1/SCR03Registry/selftests.out` | new (538 lines, first line `# rev=bc9e3059…`): module hashes, selftest/live/control runs, fixture demonstrations and lesson predicate comparisons |
| `.ufo/waves/round-73/w1/SCR03Registry.md` | this report |

## Commands and observed output

Identity and provenance:

```
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master
bc9e30599b6c6133bb094f0e7abd1a9f512778ec
$ git log --oneline -3
bc9e3059 round-73: freeze w1 wave spec (15 seats) and dispatch evidence
24bc96ad round-73: freeze three claims (round-scope v2 cases, receipt-claim binding, province host drift) with pre-freeze survivor controls
6e961996 round-72 verifier spot-check (integrator, hyaku): non-author admit/reject
```

Module bytes at the runs below (`sha256sum`, `wc -l`):

```
65d9a753067e1d2e72eb58e082e317c8aa9242d2495e65f3b4123c837527c577  tools/round73-round-scope-cases.py   825 lines
888eb0755df7a5b3424900ad6dd1e862c5ea9ab90140867adb008b968503be54  tools/round73-receipt-claim-binding.py 755 lines
ec7bfd3fdf26be7338975c07443cdd15945f378d6f01774a70ef8e71934cd919  tools/round73-province-host-drift.py   424 lines
59842d4604a2d0b85db428b7b79a6758ca0dd1ffdbdc651a31a53bfbd94893e9  tools/pre-report-gate.py
```

Selftests (all `PYTHONDONTWRITEBYTECODE=1`, all in the seat receipt):

```
$ python3 tools/round73-round-scope-cases.py --selftest
ROUND_SCOPE_V2_SELFTEST pass=26 fail=0            EXIT=0
$ python3 tools/round73-receipt-claim-binding.py --selftest
RECEIPT_CLAIM_BINDING_SELFTEST pass=14 fail=0     EXIT=0
$ python3 tools/round73-province-host-drift.py --selftest
PROVINCE_HOST_DRIFT_SELFTEST pass=9 fail=0        EXIT=0
$ python3 tools/pre-report-gate.py --selftest
PRE_REPORT_SELFTEST pass=12 fail=0                EXIT=0
$ python3 tools/gate-registry-check.py --selftest
GATE_SELFTEST pass=7 fail=0                       EXIT=0   (arm 6: registered 82 unregistered 0 defective 0 at bc9e3059)
```

Frozen counting command over the round's committed survivor fixtures
(`.ufo/waves/round-73/controls/score-survivors.py`, fixtures from `build-survivors.py`):

```
BASE_C1 c1_a5 exit=0 verdict=GREEN ROUND_SCOPE round=73 cases=3 findings=0
BASE_C1 c1_a6e exit=0 verdict=GREEN ROUND_SCOPE round=71 cases=3 findings=0
BASE_C1 c1_a7sub2 exit=0 verdict=GREEN ROUND_SCOPE round=73 cases=3 findings=0
V2_C1 c1_a5 exit=1 verdict=KILLED ROUND_SCOPE_V2 round=73 cases=6 findings=2
V2_C1 c1_a6e exit=1 verdict=KILLED ROUND_SCOPE_V2 round=71 cases=6 findings=1
V2_C1 c1_a7sub2 exit=1 verdict=KILLED ROUND_SCOPE_V2 round=73 cases=6 findings=3
V2_C1 c1_clean exit=0 verdict=GREEN ROUND_SCOPE_V2 round=73 cases=6 findings=0
SURVIVORS c1 base_green=3 v2_killed=3 v2=present clean=green
BASE_C2 c2_b6 exit=0 verdict=GREEN RECEIPT_TIP_BINDING round=72 cited=1 bound=1 unbound=0 shifted=0 stale=0
V2_C2 c2_b6 exit=1 verdict=KILLED RECEIPT_CLAIM_BINDING round=72 cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=1 unbound_claims=1
SURVIVORS c2 base_green=1 v2_killed=1 v2=present
BASE_C3 c3_stale exit=0 verdict=GREEN block-exists-shortcut blocks=1
V2_C3 c3_stale exit=1 verdict=KILLED PROVINCE_HOST_DRIFT blocks=1 recorded=Windows/AMD64/win live=Linux/x86_64/arch stale=1
SURVIVORS c3 base_green=1 v2_killed=1 v2=present
# exit=0
```

Live lane runs:

```
$ python3 tools/round73-province-host-drift.py --repo .
PROVINCE_HOST_DRIFT blocks=1 recorded=Linux/x86_64/arch live=Linux/x86_64/arch stale=0     EXIT=0
    # before EX03HostDrift appended the block, the same run read:
    # PROVINCE_HOST_DRIFT_FINDING no-block no Round-<N> host-identity block in …/PROVINCE.md
    # PROVINCE_HOST_DRIFT blocks=0 recorded=-/-/- live=Linux/x86_64/arch stale=1            EXIT=1
$ python3 tools/round73-receipt-claim-binding.py --repo . --round 73 --tip master
RECEIPT_CLAIM_BINDING_UNREADABLE base tool could not evaluate: RECEIPT_TIP_BINDING_UNREADABLE
  SCORECARD.md at master carries no '## Round 73' section; the round's self-record cannot be read     EXIT=2
$ python3 tools/round72-receipt-tip-binding.py --repo . --round 73 --tip master
RECEIPT_TIP_BINDING_UNREADABLE SCORECARD.md at master carries no '## Round 73' section …              EXIT=2
```

Predicate agreement (plan blockquote vs module `PREDICATE`, quote marks and line breaks removed):

```
C1 plan_chars=658 constant_chars=658 equal=True
C2 plan_chars=659 constant_chars=659 equal=True
C3 plan_chars=564 constant_chars=564 equal=True
```

Wave shape, read from the committed spec and dispatch record:

```
spec items=15  (EX01ScopeV2, EX02ClaimBinding, EX03HostDrift, EX04GateArm, SCR01Sources,
                SCR02Knowledge, SCR03Registry, SCT01SurvivorRecon, CON01Overlap, LAB01Probes,
                RVW01Attack, CRT01ClaimCritic, MT01Mutants, CRT02RecordCritic, SEN01ScopeAudit)
dispatched keys=15
context says "ONE v1 wave of 14 seats": True
```

Frontier rows, measured against `HEAD` while this report was written (SCR01Sources' append landed
mid-seat; nothing here is copied from that seat's report):

```
$ git diff --numstat corpus/SOURCES.md
4       2       corpus/SOURCES.md
$ grep -c '^| *S[0-9]' corpus/SOURCES.md
285
# S544 (new) = GNU coreutils uname(1), C3's `uname -s`/`uname -m` row
# S545 (new) = Git gitmodules, C1's `submodule.<name>.ignore` row
# S175 and S542 changed only in their `used-by` cell, each adding `corpus/lessons/round-73.md`
```

## Gates

- **C1**: my run `ROUND_SCOPE_V2_SELFTEST pass=26 fail=0`; the frozen kill rule holds on the committed
  fixtures — direct runs, after the control's summary: `c1_a5` → `ROUND_SCOPE_V2_FINDING worktree
  …/c1_a5-wt LOG.md status= M` + `…/stray-in-wt.txt status=??`, `findings=2`, exit 1; `c1_a6e` →
  `ROUND_SCOPE_V2_FINDING ignored-older-label .ufo/waves/round-72/hidden.log`, `findings=1`, exit 1;
  `c1_a7sub2` → three `submodule` findings (`sub child.txt status= M`, `sub leak.txt status=??`,
  `parent-record=M sub`), `findings=3`, exit 1; `c1_clean` exit 0. The base counter still accepts all
  three (`base_green=3`), so the target is not reachable by doing nothing.
- **C2**: my run `RECEIPT_CLAIM_BINDING_SELFTEST pass=14 fail=0`; B6 is killed by the new module
  (`exit=1`, `claims=1 unbound_claims=1`) while the base tool accepts it (`exit=0`). The round's own
  record cannot be graded until `SCORECARD.md` carries a `## Round 73` section — see finding 5.
- **C3**: my run `PROVINCE_HOST_DRIFT_SELFTEST pass=9 fail=0`; the Windows fixture is killed by the new
  module and still accepted by the block-exists shortcut; the live lane exits 0 on the appended block.
- **Registry**: the three rows and the description append are in place; `gate-registry-check.py` is green
  at HEAD (82 registered / 0 unregistered / 0 defective). Its population is `git ls-tree -r HEAD`, so the
  three new rows (naming untracked modules) are graded only after the landing commit — finding 7.

## Findings

1. **A tally must be taken at the bytes that land.** The C2 module was edited while this seat held it:
   the first bytes I read/ran printed `RECEIPT_CLAIM_BINDING_SELFTEST pass=13 fail=0` at 728 lines
   (sha256 `7c9ca07b…`); the settled bytes (mtime 23:39:17) are 755 lines, sha256 `888eb075…`, and print
   `pass=14 fail=0` with the added arm `base-finding-then-claim`. The row carries the settled run. The
   class is the round's own mistake 1 ("a tally is a run fact") applied to a moving file: the row was
   first written from a run that was true when made and stale when landed, and the correction is a
   re-run, not an edit of the printed line.
2. **The `Pre-report gate` row's tally is now a round-72 measurement only.** The gate's selftest grew
   from 8 to 12 arms with EX04's re-point; my run prints `PRE_REPORT_SELFTEST pass=12 fail=0`. Per the
   assignment the existing tally is not rewritten, so the row still reads `pass=8` and the current 12 is
   recorded here and in `LOG.md`. Next round's registry pass (or the L1) should append the 12 with its
   revision; leaving the row as-is is a known staleness, not a claim that the gate still has 8 arms.
3. **A mid-edit gate was red and the seat's own run is what caught it.** At my first run,
   `tools/pre-report-gate.py --selftest` printed `PRE_REPORT_SELFTEST pass=0 fail=8`: `ARM_SPECS` already
   named `round73-round-scope-cases.py` while the selftest still wrote its stub as
   `round72-round-scope.py` and expected `ROUND_SCOPE round=70 cases=3 findings=1`, so every arm died on
   `can't open file …/tools/round73-round-scope-cases.py`. EX04 then moved the stub target and the
   expected `ROUND_SCOPE_V2 … cases=6` strings (and added the a6/selector arms); the re-run at the
   settled bytes is `pass=12 fail=0`. Mined as lesson mistake 3.
4. **The wave-shape count in the seat text is 14; the committed spec carries 15.** `w1-spec.json` has 15
   items and `w1.ready.dispatched` 15 dispatch names, while the spec's own `context` says "ONE v1 wave of
   14 seats". The `LOG.md` entry records the measured 15 and names the delta; the freeze is untouched
   (a rule changed after scoring is not the claim's rule — this is a record-count disagreement, reported,
   not edited).
5. **The round's own C2 run is exit 2 at this writing, not green.** `SCORECARD.md` has no `## Round 73`
   section until the L1 writes it, so both the base tool and the v2 module return
   `RECEIPT_TIP_BINDING_UNREADABLE … no '## Round 73' section` (exit 2). The claim's own-record duty
   (`unbound=0 shifted=0 stale=0 unbound_claims=0` at the record tip, or a recorded could-not-evaluate
   with its reason — KQ119) is therefore the L1's to produce and cannot be claimed from this seat.
6. **The lesson's citation surface is clean now; both hazards were measured.** The sections this seat
   wrote cite no round-73 receipt. SCR01Sources' `## Gate` (appended 23:44) briefly backticked
   `.ufo/waves/round-73/w1/SCR01Sources/source/` and `SCR01Sources/fetch.out`; at 23:46 it rewrote that
   sentence as prose, and the current 141-line file carries no round-73 receipt token (157 backticked
   spans; the only wave paths left are two round-72 receipts, round 29's `count-c1.py`, and the
   `.ufo/waves/round-<M>/` template — all outside the base tool's population). Two hazards are real and
   demonstrated in throwaway fixtures, both recorded in the seat receipt: (a) a backticked directory
   whose tree holds no `.out/.txt/.log/.json` raises
   `CouldNotEvaluate: cited directory carries no receipt file: .ufo/waves/round-73/w1/SCR01Sources/source`
   — and that `source/` holds only four `.html` files — so the whole self-record would exit 2, not just
   that citation; (b) a round-73 receipt cited from the lesson carries `# rev=bc9e3059`, and once the
   landing commit touches `tools/**` the base tool's delta rule grades it `shifted` (control run:
   `RECEIPT_TIP_BINDING round=73 cited=1 bound=0 unbound=0 shifted=1 stale=0`), so a receipt pointer
   belongs in a seat report or the LOG unless the L1 re-derives it at the instrument tip. Measured for
   the claim pass: over a fixture carrying this lesson, `claims=0 unbound_claims=0 findings=0`, and
   `claims=1 unbound_claims=1` when one tip-claim line citing a headerless receipt is added (positive
   control).
7. **The registry gate cannot see the new rows before the landing commit.** `gate-registry-check.py`
   takes its population from `git ls-tree -r HEAD`; the three rows name untracked modules, so the
   post-landing run is the real one. Every repo-relative path token in the added rows resolves now
   (`tools/round73-*.py`, `.ufo/waves/round-73/w1/EX0{1,2,3}*/`, this seat's receipt), which is what the
   checker's `missing-path` defect tests once the rows enter its population.
8. **Column discipline.** The C3 predicate and the C2/C3 exit maps contain a literal `|`
   (`<no-block|stale-host>`, `<unbound|shifted|stale>`); the rows escape it as `\|` so each new row stays
   five cells. The frozen predicates themselves are unescaped in the modules and the plan (escape is a
   Markdown-table concern only).
9. **Two seats wrote `corpus/lessons/round-73.md`, and the two spec items assign both.** This seat's item
   says to leave `## Gate` and `## Wave` to the L1; SCR01Sources' item says CORPUS.md rule 2 requires its
   `used-by` old→new table in the lesson, and it appended `## Gate` at 23:44 (the file grew 108 → 141
   lines). This seat created only the preamble, `## Claims` and `## Mistakes`; it did not create
   `## Gate` and did not delete it, because deleting another seat's required curation artifact is not
   this seat's call and the heading is inside the C2 population whose citations are clean at this
   writing (finding 6). The L1's landing should decide whether `## Gate` stays as written or is moved.

## Out of scope / not done here

- `SCORECARD.md` round-73 section, the integration block, the scored at-tip runs and every commit — L1.
- `tools/round73-*.py` and `tools/pre-report-gate.py` — EX01ScopeV2, EX02ClaimBinding, EX03HostDrift,
  EX04GateArm; read only, never edited.
- `PROVINCE.md` (the round's host block) — EX03HostDrift; read only. `corpus/SOURCES.md` and the
  knowledge entries — SCR01Sources / SCR02Knowledge; read only.
- `## Wave` in the lesson — the L1's heading, not created. `## Gate` exists but was written by
  SCR01Sources under its own item (CORPUS.md rule 2's used-by table); its content is not this seat's —
  see finding 9.
- No tool was installed or upgraded, no pacman transaction ran, no network call was made.
- The gate keeps its selftest work root on failure (`/tmp/pre-report-gate-selftest-*`); eight such root
  directories were present at this writing. They are outside the lane and outside this seat's scratch, so
  none was touched. This seat's scratch root `/fast/scratch/hyaku/kama-r73/SCR03Registry/` is deleted
  before the yield (verified absent).

## Artifacts

- `.ufo/waves/round-73/w1/SCR03Registry/selftests.out` — 538 lines, first line `# rev=bc9e3059…`:
  module sha256/line counts; C1/C2/C3/gate/registry selftests; live C3, C2 and base-binding runs; the
  control run over the committed survivors; the three C1 survivor fixtures' direct finding lines;
  predicate equality; wave counts; the lesson claim-population check (with positive control); the
  directory-citation demonstration; and the `__pycache__` check (no output).
- `.ufo/waves/round-73/w1/SCR03Registry.md` — this report.
- `SKILL.md` (row 309 amended, rows 314–316 added), `LOG.md` (§Round 73), `corpus/lessons/round-73.md`
  (this seat's 108-line preamble/`## Claims`/`## Mistakes` plus SCR01Sources' appended `## Gate`).
