# MT01MutantGates - round-71 mutation test of the three gates (kama)

Seat: MT01MutantGates, leaf mutation-tester, axes **operability + calibration**. Scope: challenge the
three frozen round-71 invariants by mutating the landed tools in an isolated scratch copy. Advisory only:
no verdict on the claims, no lane edit, no subagent dispatch.

## 0. Substrate (shipped bytes actually mutated)

| tool | sha256 tested | drift seen while this seat ran |
|---|---|---|
| `tools/pre-report-gate.py` | `07cfc04fbba413f8…` | `d0957e0b` -> `07cfc04f` (recursion guard added); matrix re-run on `07cfc04f` |
| `tools/census-waiver-boundary.py` | `8922b954f481059a…` | `16e5cf4f` -> `3a9cec94` -> `fc988852` -> `8922b954` (case-4/5 hardening); matrix re-run on `8922b954` |
| `tools/round71-province-host-claims.py` | `1f6bb43aa9e9e0f0…` | stable throughout |

Lane HEAD at snapshot: `e2b860c8` (freeze `b43e71a8`). The C1/C2 executors were still revising their tools
when this seat started; every matrix below was re-run after the bytes settled, and the table names the
hash the row was measured on. Scratch root `/fast/scratch/hyaku/kama-r71/MT01MutantGates`; `TMPDIR` pinned
there for every child, so no run touched `/tmp`.

## 1. Method

- Pristine copy in `S/pristine`; each mutant is one exact single-hunk replacement in a copy under
  `S/host/tools` (a clone of the lane at `b43e71a8`, so the C3 selftest can `git show f3ee44f4:PROVINCE.md`).
  Every mutant was `compile()`-checked and its sha256 recorded (`logs/mutant-build-*.tsv`).
- Detectors, run on pristine and on every mutant: `--selftest` plus the tool's own defect fixtures.
  C1: green fixture + untracked file under `.ufo/waves/round-71/`, stale closure pointer, missing
  declared path (`LOG.md`), byte-changed declared path, CRLF-translated declared path.
  C2: the frozen counter (`--census tools/round65-host-census.py`), a shim used as the census under test,
  a shim corpus with one compliant census in a slot (`--shims`), and a defective landed census.
  C3: base (no corrections), verdict-equal corrections, one flipped verdict, wrong-tag corrections,
  deleted base marker block with `--base`.
- Verdict: **KILLED** when any detector's exit, verdict line, arm/check status or `REWRITTEN` line
  differs from pristine; **SURVIVED** when every detector reads exactly like pristine. A survivor is a
  coverage finding, not a change request.

## 2. C1 - `pre-report-gate.py`

Detector cells are the `PRE_REPORT` line's `failed=/uncommitted=` pair; `ST` is the selftest arm count.
| mutant | ST exit/`pass` | green | uncommitted | stale | missing | dirty | crlf |
|---|---|---|---|---|---|---|---|
| pristine | 0 `pass=6 fail=0` | 0 uncommitted=0 | PRE_REPORT round=71 arms=5 failed=1 uncommitted=1 | PRE_REPORT round=71 arms=5 failed=2 uncommitted=0 | failed=1 uncommitted=0 | failed=1 uncommitted=0 | failed=1 uncommitted=0 |
| m1-exit0 | 1 `pass=1 fail=5` | 0 uncommitted=0 | PRE_REPORT round=71 arms=5 failed=1 uncommitted=1 | PRE_REPORT round=71 arms=5 failed=2 uncommitted=0 | failed=1 uncommitted=0 | failed=1 uncommitted=0 | failed=1 uncommitted=0 |
| m2-uncommitted0 | 1 `pass=5 fail=1` | 0 uncommitted=0 | PRE_REPORT round=71 arms=5 failed=0 uncommitted=0 | PRE_REPORT round=71 arms=5 failed=2 uncommitted=0 | failed=1 uncommitted=0 | failed=1 uncommitted=0 | failed=1 uncommitted=0 |
| m3-fail-only-silent | 1 `pass=2 fail=4` | 0 uncommitted=0 | PRE_REPORT round=71 arms=5 failed=1 uncommitted=1 | PRE_REPORT round=71 arms=5 failed=0 uncommitted=0 | failed=0 uncommitted=0 | failed=0 uncommitted=0 | failed=0 uncommitted=0 |
| m4-roundclean-ok | 1 `pass=5 fail=1` | 0 uncommitted=0 | PRE_REPORT round=71 arms=5 failed=0 uncommitted=1 | PRE_REPORT round=71 arms=5 failed=2 uncommitted=0 | failed=1 uncommitted=0 | failed=1 uncommitted=0 | failed=1 uncommitted=0 |
| m5-failed0 | 1 `pass=1 fail=5` | 0 uncommitted=0 | PRE_REPORT round=71 arms=5 failed=0 uncommitted=1 | PRE_REPORT round=71 arms=5 failed=0 uncommitted=0 | failed=0 uncommitted=0 | failed=0 uncommitted=0 | failed=0 uncommitted=0 |
| m6-accept-dirty | 1 `pass=4 fail=2` | 0 uncommitted=0 | PRE_REPORT round=71 arms=5 failed=1 uncommitted=1 | PRE_REPORT round=71 arms=5 failed=2 uncommitted=0 | failed=1 uncommitted=0 | failed=0 uncommitted=0 | failed=0 uncommitted=0 |

All six mutants were killed. Kill surfaces: `m1-exit0` by all five selftest defect arms (exit=0 want 1)
and every external defect fixture; `m2-uncommitted0` by `wave-uncommitted` (uncommitted=0 want 1) and
`fx-uncommitted` (`failed=0 uncommitted=0`); `m3-fail-only-silent` by the four selftest arms and the four
external fixtures (all green); `m4-roundclean-ok` by `wave-uncommitted` (failed=0 want 1) and
`fx-uncommitted failed=0 uncommitted=1`; `m5-failed0` by five selftest arms and four external fixtures
(`failed=0`); `m6-accept-dirty` by `dirty`/`crlf` (failed=0 want 1) and `fx-dirty`/`fx-crlf` green.
No C1 mutant survived. The selftest alone killed all six, so a mutant special-casing `--selftest` would
need the external fixtures; none of the six does.

## 3. C2 - `census-waiver-boundary.py`

`R` is the frozen counter; `BAD` runs the `s4` shim as the census under test (cases 1-5 must fail);
`HOLE` puts a compliant census in one shim slot; `LB` plants a defective landed census (case 7).
| mutant | ST | R | BAD | HOLE | LB |
|---|---|---|---|---|---|
| pristine | 0 `pass=19 fail=0` | 0 `BOUNDARY cases=7 killed=5 survivors=0` | 1 c1-5=FAILFAILFAILFAILFAILheldheld | 1 `BOUNDARY cases=7 killed=4 survivors=1` | 1 c7=FAIL |
| m1-exit0 | 0 `pass=19 fail=0` | 0 `BOUNDARY cases=7 killed=5 survivors=0` | 0 c1-5=FAILFAILFAILFAILFAILheldheld | 0 `BOUNDARY cases=7 killed=4 survivors=1` | 0 c7=FAIL |
| m2-survivors0 | 0 `pass=19 fail=0` | 0 `BOUNDARY cases=7 killed=5 survivors=0` | 1 c1-5=FAILFAILFAILFAILFAILheldheld | 1 `BOUNDARY cases=7 killed=4 survivors=0` | 1 c7=FAIL |
| m3-killedfalse | 1 `pass=13 fail=6` | 1 `BOUNDARY cases=7 killed=0 survivors=5` | 1 c1-5=FAILFAILFAILFAILFAILFAILheld | 1 `BOUNDARY cases=7 killed=0 survivors=5` | 1 c7=FAIL |
| m4-drop-fail-waiver | 1 `pass=18 fail=1` | 1 `BOUNDARY cases=7 killed=5 survivors=0` | 1 c1-5=FAILFAILFAILFAILFAILFAILheld | 1 `BOUNDARY cases=7 killed=4 survivors=1` | 1 c7=FAIL |
| m5-accepted-as-killed | 0 `pass=19 fail=0` | 0 `BOUNDARY cases=7 killed=5 survivors=0` | 1 c1-5=FAILFAILFAILFAILFAILheldheld | 0 `BOUNDARY cases=7 killed=5 survivors=0` | 1 c7=FAIL |
| m6-landed-blind | 0 `pass=19 fail=0` | 0 `BOUNDARY cases=7 killed=5 survivors=0` | 1 c1-5=FAILFAILFAILFAILFAILheldheld | 1 `BOUNDARY cases=7 killed=4 survivors=1` | 0 c7=FAIL |
| m7-drop-waiver-ne | 0 `pass=19 fail=0` | 0 `BOUNDARY cases=7 killed=5 survivors=0` | 1 c1-5=FAILFAILFAILFAILFAILheldheld | 1 `BOUNDARY cases=7 killed=4 survivors=1` | 1 c7=FAIL |

Kill surfaces: `m1-exit0` by `BAD`, `HOLE` and `LB` (exit 1 -> 0; the selftest computes its own exit and
stays green); `m2-survivors0` by the `HOLE` summary token (`killed=4 survivors=1` -> `survivors=0`, both
exits 1); `m3-killedfalse` by `R` (`killed=0 survivors=5`, exit 1); `m4-drop-fail-waiver` by the `s6w`
attribution check (the shim stays killed by other checks but the named check never fires);
`m5-accepted-as-killed` by `HOLE` (a compliant census counted killed, exit 1 -> 0); `m6-landed-blind` by
`LB` (defective landed census accepted, exit 1 -> 0). `m7-drop-waiver-ne` SURVIVED every detector (see F2).

## 4. C3 - `round71-province-host-claims.py`

Fixture cells are `uncovered` (and exit) for base / corrected / flipped / wrongtag / rewritten.
| mutant | ST exit/`pass` | base | corrected | flipped | wrongtag | rewritten |
|---|---|---|---|---|---|---|
| pristine | 0 `pass=7 fail=0` | 14 exit=1 | 0 exit=0 | 1 exit=1 | 14 exit=1 | 1/REWRITTEN |
| m1-accept-any | 1 `pass=5 fail=2` | 14 exit=1 | 0 exit=0 | 0 exit=0 | 14 exit=1 | 1/REWRITTEN |
| m2-ignore-verdict | 1 `pass=5 fail=2` | 14 exit=1 | 0 exit=0 | 0 exit=0 | 14 exit=1 | 1/REWRITTEN |
| m3-wrong-tag | 1 `pass=4 fail=3` | 14 exit=1 | 0 exit=0 | 0 exit=0 | 0 exit=0 | 1/REWRITTEN |
| m4-drop-rewritten | 1 `pass=6 fail=1` | 14 exit=1 | 0 exit=0 | 1 exit=1 | 14 exit=1 | 1/no-line |
| m5-uncovered0 | 1 `pass=3 fail=4` | 0 exit=0 | 0 exit=0 | 0 exit=0 | 0 exit=0 | 1/REWRITTEN |
| m6-drop-date | 0 `pass=7 fail=0` | 14 exit=1 | 0 exit=0 | 1 exit=1 | 14 exit=1 | 1/REWRITTEN |

Kill surfaces: `m1-accept-any` and `m2-ignore-verdict` by the `flipped-verdict` and
`shortcut-all-flipped` selftest arms (and the external flipped fixture, exit 1 -> 0); `m3-wrong-tag` by
`wrong-tag` (uncovered 14 -> 0); `m4-drop-rewritten` by `rewritten-marker` (the selftest checks the
`PROVINCE_HOST_CLAIMS_REWRITTEN` line, while the external fixture still exits 1 from `uncovered=14`);
`m5-uncovered0` by `base-uncovered` plus three more selftest arms. `m6-drop-date` SURVIVED (see F1).

## 5. Findings

**F1 - the correction-date guard has no kill surface (C3 `m6-drop-date`, SURVIVED).**
Removing `if correction["date"] <= claim["date"]: continue` leaves every detector byte-identical to
pristine: `PROVINCE_HOST_CLAIMS_SELFTEST pass=7 fail=0` and all five external fixtures at the pristine
exits (`base=1`, `corrected=0`, `flipped=1/uncovered=1`, `wrongtag=1/uncovered=14`,
`rewritten=1/REWRITTEN`). Every fixture dates its corrections with `draft_date` (today), so no fixture
carries a correction dated on or before its claim (2026-10-31). A same-dated or back-dated correction is
therefore accepted by the mutant exactly as by the shipped tool. Missing check to add: one fixture with
`- correction-on-host (2026-10-31)` (claim date) and one earlier, each expected to leave `uncovered`
unchanged. The freeze's KILL RULE does not name the date guard, so this is coverage, not a claim defect.

**F2 - `waiver_keeps_not_evaluated` has no own kill surface (C2 `m7`, SURVIVED).**
Forcing that check true changes no detector: the five embedded shims are each rejected by several other
checks, so the corpus never exercises a census that zeroes `not_evaluated` under a waiver. The check is
real (it is the only guard on that clause in case 3) but no fixture isolates it.

**F3 - C2's case-7 and case-6 kills are not in the shipped selftest.**
`m5-accepted-as-killed` and `m6-landed-blind` are invisible to the frozen counter and to `--selftest`;
they die only on fixtures this seat built (`--shims` with a compliant census in a slot; a defective
landed census). The shipped negative arm (`mutant:gutted-exit-killed`) covers case 1 only. Two cheap
arms would close it: run `case_shims` over a shim dir with the landed census in one slot and require
`survivors==1`; run `case_landed` over a truncated verdict (`pass=21`).

**F4 - C1's kill rule is fully mechanised.**
All four freeze clauses map to distinct checks (uncommitted file -> `round-clean`; stale pointer ->
`newest-closure`; missing/dirty declared path -> `worktree-landing` `MISSING`/`DIRTY`). CRLF is distinct
from a same-content edit because the landing check compares bytes; the `crlf-declared-path` arm proves it.

**F5 - the C3 REWRITTEN clause is exit-invisible in a marker-deleted tree.**
`m4-drop-rewritten` still exits 1 on the external deleted-marker fixture because the remaining 14 claims
are uncovered; only the `REWRITTEN <tag>` line distinguishes it. Any future counter that grades the exit
code alone will not detect a dropped rewrite check. The shipped selftest already checks the line.

## 6. Restoration and hygiene

- The lane's three tools were never opened for writing. Their sha256 before and after this seat:
  `pre-report-gate.py 07cfc04fbba413f851034734bfee1122b12463ed5d65486762d6bd736cb3bd0b`,
  `census-waiver-boundary.py 8922b954f481059a4d89690326e01f59e1c24af608f6d3c93a6d86b14f427013`,
  `round71-province-host-claims.py 1f6bb43aa9e9e0f0f43e096cfcce2b677dcaa0cdfab266bb1975dc90fea8b0ff` (the only movement is the
  executors' own revisions, recorded in section 0; the tested hashes are the ones in that table).
- Mutants are separate files in `S/host/tools`; pristine copies in `S/pristine` were re-run after the
  matrices and read identically to their pre-matrix baselines (`logs/c1-matrix-v2.json`,
  `logs/c2-matrix-final.json`, `logs/c3-matrix.json` all carry a `pristine` row).
- Fixture git repos were created with `git clone`/`git init` under S and each asserted
  `git rev-parse --show-toplevel` equals the fixture directory before the only commits made there.
- No git/jj mutation was run in the lane; no serving process, port or credential was touched.
- Tooling installed/upgraded: none (python3 3.14.8, git sufficed; no pacman transaction attempted).

## 7. Not verified

- The C1/C2 tools may have moved again after the final hash read; section 0's hashes are the tested
  substrate. Rows are not claims about any later revision.
- The full 22-member census was executed only through the tools' own case 7 (`pass=22 total=22`); this
  seat did not independently re-run all 22 members.
- The claims themselves (scores, axes, population deltas) were not judged; only the tools' kill surfaces
  were probed.

## 8. Deliverables in this directory

- `mutants.tsv` - 19 rows: tool, mutant, change, verdict, changed detectors, killing check.
- `mutants/` - the 19 mutated tool files plus the three pristine copies they were derived from.
- `logs/` - the three matrix JSONs, the drivers (`c1detect.py`, `c3detect.py`, `build_mutants.py`,
  `c1driver.py`, `c2driver.py`, `c3driver.py`), build/hash records and baseline outputs.
