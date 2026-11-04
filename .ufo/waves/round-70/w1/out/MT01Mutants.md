# MT01Mutants — round 70 mutation-test of the two repairs (kama)

Seat: MT01Mutants, leaf mutation-tester, axes **calibration + operability**.
Scope: mutation-test C1 (`tools/round42-selfdesc-reconcile.py` + the run-fact harness in
`tools/round41-scorecard-reconcile.py`) and C2 (`tools/round65-host-census.py`) against the
frozen counters in `.ufo/waves/round-70/controls/`. Advisory only: no verdict on the claims,
no edit to any tracked lane file.

## 0. Substrate — what was actually mutated, and when

The wave landed while this seat ran, so the matrix is reported on the **landed bytes**, with the
pre-repair bytes kept as the do-nothing control. Every row of `mutants.tsv` names its substrate.

| substrate | commit / path | sha256 |
|---|---|---|
| C1 counter, landed | `73597158:tools/round42-selfdesc-reconcile.py` (= `0e14facd` bytes) | `3d9aff8f9c2236c2cb9337b08846da82de718bc1d9e8f1d283f1a71a03acd5c0` |
| C1 harness, landed | `73597158:tools/round41-scorecard-reconcile.py` (EX01) | `c9bb4eae7f228f2a8e56f3df3392d54e182c9fe8e594792266618b07726e9f3e` |
| C1 harness, pre-repair (control) | `0e14facd:tools/round41-scorecard-reconcile.py` | `eff934a27b3e7525226c78e376ce774f3ab0b225ab98427b19201e5312176cd6` |
| C2 census, landed | `af6eb6c2:tools/round65-host-census.py` | `44bebd671c0d12118c92ace1ef6bd7491a60c7acbce79f1668b81a822b245919` |
| C2 census, first candidate (superseded by `af6eb6c2`) | `EX02CensusVerdict/round65-host-census.py` | `a82cad11d777aa4b34d8ae96b66250d52853ed880d4c2eaa510ea8b4bf37dc68` |
| C2 census, frozen pre-repair (control) | `.ufo/waves/round-70/measured/before/round65-host-census-base.py` | `463899182af0d154859e86da785051760e4bc314f5489659ea32424c18374513` |

Notes on the substrate handoff:

- EX01's delivered candidate (`EX01ReconHarness/round41-scorecard-reconcile.py`,
  `e0acb993…`) and the integrated file (`c9bb4eae…`) differ textually: the integrated file adds
  `git update-ref refs/heads/master <tip>`. Measured: the two are **behaviourally identical on
  every detector of this matrix** — both green on `G/NB/NP/NC/NH`, both red on `BASE`, both
  `SELFDESC_SELFTEST … pass=5 fail=0` (rows `ex01`, `ex01-out` in
  `logs/c1-synthetic.jsonl`). The addition covers a source whose clone has no local branch at
  all (a detached HEAD with no `refs/heads/*`); this seat reproduced exactly that failure
  (`gate-registry-check.py --selftest` lane-tip arm: `fatal: Needed a single revision`) on a
  fixture clone whose HEAD was detached with no local branch, and the arm went green only once
  the fixture was placed on a local `master`. So: not a defect in the delivered candidate, but
  the integration line is the thing that makes the checkout independent of the source's HEAD
  shape.
- The first C2 candidate (`a82cad11…`) and the landed census (`44bebd67…`) differ only in the
  verdict-line rendering (`waived=` printed only when used; a `CENSUS_NOT_EVALUATED` line
  instead of a second `HOST_CENSUS` line). The mutant matrix was run on **both**; the results
  are identical row for row, so the table cites the landed hash.

Tooling installed/upgraded by this seat: **none** (python3 3.14.8 and git 2.56.0 sufficed;
no pacman transaction was attempted).

## 1. Method

Two questions per mutant: (i) does the frozen counter change verdict where the repair must be
green, and (ii) does it change verdict where the repair must be red?

Because both repairs are *green at the landing tip*, the frozen counters cannot kill a mutant
that disables a check on the tip tree alone — a disabled check cannot fail on a tree that
passes. Each mutant is therefore also run against **single-violation fixtures**: clones of the
landed tip with exactly one planted violation of the fact that mutant disables. A mutant is
**KILLED** when it turns a planted-violation fixture green, or turns the green fixture / the
five-arm selftest red; **SURVIVES** when every detector reads exactly like the unmutated repair.

Detectors used for C1 (all run from the pinned tool-bytes directory against pinned fixture revs):

| id | fixture | pinned rev | unmutated expectation |
|---|---|---|---|
| G | `L` — clean clone of the landed tip | `73597158` | `mismatches=0 met=True`, exit 0 |
| NB | `fx2-nbanner` — head says `Latest measured round: 69` | `5bc6e2ac` | `banner=1 mismatches=1`, exit 1 |
| NP | `fx2-nprovince` — one indicted token removed from `PROVINCE.md` (coverage hash re-anchored) | `12e6e5e4` | `province=1 mismatches=1`, exit 1 |
| NC | `fx2-nclosure` — calibration row names round-68 while round-69 is newest | `9d2c709f` | `closure_ptr=0 mismatches=1`, exit 1 |
| NH | `fx2-nharness` — calibration row gains a **third** git-dependent run fact (`git rev-parse HEAD` in a `python3 -c`) | `d78f8ddb` | `mismatches=0 met=True`, exit 0 under a checkout; exit 1 under a metadata-free export |
| TIP | the landed tip in the lane itself | `73597158` | `mismatches=0 met=True`, exit 0 |
| BASE | the pre-round tip in the lane itself (red tree = do-nothing control) | `0e14facd` | `mismatches>0`, exit 1 |
| ST | `--selftest` on `G` | — | `pass=5 fail=0`, exit 0 |

The fixture revs are commits created **only** in this seat's scratch clones (fixture identity
`mt01fixture <mt01@fixture.invalid>`); each clone was asserted to be its own toplevel before the
first commit, and its `HEAD` is a local `master` so that the repaired harness's nested clone
also has a `master` (see §0, EX01 bullet).

Detectors used for C2:

| id | what | unmutated expectation |
|---|---|---|
| control | `refused-member-control.py <census>` (the frozen counter) | `refused_fixture_exit=1 allpass_fixture_exit=0`, exit 0 |
| line | refused-fixture verdict line contains `not_evaluated=1`; all-pass line `not_evaluated=0` | true |
| total | `len(MEMBERS)` (the registered population; the freeze's `total=22`) | 22 |
| probe | `fail-waiver-probe.py <census>` — one member that ran and failed, passed `--waive <its name>` | exit 1 (a waiver never covers a fail) |

## 2. C2 matrix — `round65-host-census.py`

Command (verbatim; `$S` = `/fast/scratch/hyaku/kama-r70/MT01Mutants`):

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-70/controls/refused-member-control.py "$S/v/L-c2a/round65-host-census.py"
python3 "$S/fail-waiver-probe.py" "$S/v/L-c2a/round65-host-census.py"
```

| mutant | change | control exit | refused / all-pass | line | total | probe | verdict |
|---|---|---|---|---|---|---|---|
| (baseline, landed `44bebd67`) | — | 0 | 1 / 0 | ok | 22 | 1 | green premise |
| (pre-repair `4638991`) | — | 1 | **0** / 0 | absent | 22 | 1 | the frozen fail-open |
| c2a | count refusals as passes | **1** | **0** / 0 | absent | 22 | 1 | **KILLED** (refused fixture went green) |
| c2b | always exit 1 | **1** | 1 / **1** | ok | 22 | 1 | **KILLED** (all-pass fixture went red) |
| c2c | drop the `not_evaluated` field | 0 | 1 / 0 | **absent** | 22 | 1 | **SURVIVES the frozen control**; killed only by a verdict-line check |
| c2d | drop one member (the reconciler arm) | 0 | 1 / 0 | ok | **21** | 1 | **SURVIVES the frozen control**; killed only by the registered `total=22` |
| c2e | let a failing member be waived | 0 | 1 / 0 | ok | 22 | **0** | **SURVIVES the frozen control**; killed only by the fail-waiver probe |

Exact outputs (landed bytes):

```
$ python3 "$S/../../controls/refused-member-control.py" "$S/v/L-c2c/round65-host-census.py"
{"refused_fixture": ["pass [A] synthetic-pass", "refused [A] synthetic-refused: ... ", "HOST_CENSUS pass=1 fail=0 not_evaluated=1 total=2 tierA_fail=0 tierB_fail=0", "CENSUS_NOT_EVALUATED 1 member(s) without a waiver: synthetic-refused \u2014 exit 1"], "allpass_fixture": [...]}
REFUSED_MEMBER_CONTROL refused_fixture_exit=1 allpass_fixture_exit=0
(exit 0)

$ python3 "$S/fail-waiver-probe.py" "$S/v/L-c2e/round65-host-census.py"
  FAIL [A] synthetic-fail: exit=1 tail='boom'
  HOST_CENSUS pass=0 fail=1 not_evaluated=0 total=1 tierA_fail=1 tierB_fail=0
FAIL_WAIVER_PROBE fail_member_waived_exit=0     <-- mutant; the repair prints 1
```

Reading: the frozen counter is a **two-point probe on the exit code only**. It kills the two
mutants that move an exit code, and it is blind to a deleted field, a deleted member and a
waiver that covers a fail. Those three are exactly the clauses the freeze's KILL RULE states in
prose (line content, `total=22`, "a waiver never covers a fail"); none of them is mechanised by
`refused-member-control.py`.

Commands (verbatim; `$S` = `/fast/scratch/hyaku/kama-r70/MT01Mutants`):

```
python3 "$S/v/L-c1a/round42-selfdesc-reconcile.py" --repo "$S/L" --tip 73597158ec1cd6707a6f3abe0814615b82580d49
python3 "$S/v/L-c1a/round42-selfdesc-reconcile.py" --repo "$S/fx2-nbanner" --tip 5bc6e2acc5dfeee68c93a20d7ae7301d9921c9f7
python3 "$S/v/L-c1a/round42-selfdesc-reconcile.py" --selftest --repo "$S/L" --tip 73597158ec1cd6707a6f3abe0814615b82580d49 --work "$S/work-L-c1a"
```

Cells are `exit/mismatches` from the verdict line; the `ST` column is `exit/pass-fail`.
Source: `logs/c1-landed.jsonl`.

| mutant | change | G | NB | NP | NC | NH | TIP | BASE | ST | verdict | selftest arm that catches it |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **landed** | — (the repair) | 0/0 | 1/1 | 1/1 | 1/1 | 0/0 | 0/0 | 1/9 | 0/5-0 | baseline | — |
| **base-harness** | pre-repair `git archive` export | 1/1 | 1/2 | 1/2 | 1/2 | 1/2 | 1/1 | 1/10 | 1/4-1 | red control | `ok` (its run fact fails → `ok_m=1 ≠ 0`) |
| **c1a** | delete the `banner` check | 0/0 | **0/0** | 1/1 | 1/1 | 0/0 | 0/0 | 1/8 | 0/5-0 | **KILLED** by `NB` | none |
| **c1b** | delete the `province` check | 0/0 | 1/1 | **0/0** | 1/1 | 0/0 | 0/0 | 1/5 | 0/5-0 | **KILLED** by `NP` | none |
| **c1c** | `closure_ptr` always `True` | 0/0 | 1/1 | 1/1 | **0/0** | 0/0 | 0/0 | 1/8 | 1/1-4 | **KILLED** by `NC` + `ST` | `stale_ptr`, `stale_both`, `stale_incl`, `no_ptr` |
| **c1d** | keep `git archive`, special-case the two failing commands | 0/0 | 1/1 | 1/1 | 1/1 | **1/1** | 0/0 | 1/8 | 0/5-0 | **KILLED** only by `NH` | none |
| **c1e** | `mismatches` always 0 | 0/0 | **0/0** | **0/0** | **0/0** | 0/0 | 0/0 | **0/0** | 1/1-4 | **KILLED** by `BASE`, every planted fixture, and `ST` | all four planted arms (`ok` passes; the plants collapse to `ok_m`) |

Readings worth carrying into the receipt:

- The frozen counter at the landed tip (`TIP`) is green for **every** mutant, `c1e` included:
  a check disabled on a tree that passes cannot fail. The counter is a claim-verifier, not a
  regression detector; the planted fixtures are what make the matrix meaningful.
- `c1e` is the only mutant the red-tree control kills (`BASE 0/0` where `1/9` is required).
  For the other four, the base tree stays red for the other mismatches, so the do-nothing
  control says nothing about them.
- The pre-repair harness (`base-harness`) fails the **selftest** (`ok` arm) as well as the claim
  at the landed tip: the selftest is a genuine regression detector for the harness *when the
  harness can no longer execute the facts*, but it is blind to a harness that executes a
  special-case (c1d) because the special-case answers `ok` without running anything.
- `c1d` is invisible to the frozen counter, to `TIP`, and to all five selftest arms. Only a
  git-dependent fact the special-case does not name (`NH`) exposes it.

## 4. Findings the L1 should act on

**F1 — `banner` and `province` have no kill surface of their own.**
Deleting either check leaves the green fixture green (obviously), leaves the frozen counter at the
landed tip green, and leaves all five selftest arms green — the selftest plants closure-pointer
variants only. Measured: `c1a`/`c1b` rows, `ST=pass=5 fail=0`; the kills come only from
`fx2-nbanner` (`0/0` where `1/1` is required) and `fx2-nprovince` (`0/0` where `1/1`).
The base-red-tree control only *exercises* them: deleting `banner` moves that red tree's
verdict line 9→8 and deleting `province` moves it 9→5 (the base tree violates both facts), but
the verdict stays red, so neither is a kill. Cheap mechanisation: two more selftest arms
that rewrite the head's `Latest measured round:` number and drop a `tools/` token from
`PROVINCE.md` — both are one-line edits on the fixture tree the selftest already commits.
The L1's own `check-kill-probe-gutted.out` demonstrates the `province` half on a planted tree;
the `banner` half is unmeasured in the lane.

**F2 — `closure_ptr` is doubly killed.**
`c1c` (always `True`) turns `fx2-nclosure` green (`0/0` where `1/1` required) and fails four
selftest arms (`pass=1 fail=4`: `stale_ptr`, `stale_both`, `stale_incl`, `no_ptr` all read
`closure_ptr=1`). No action needed.

**F3 — the harness repair cannot be killed by the frozen counter on the landed tree.**
`c1d` (keep `git archive`, special-case `gate-registry-check.py --selftest` and
`round69-newest-closure-counter.py --since-round` to `return True, "ok"`) reads **identical to the
repair** on `G`, `NB`, `NP`, `NC`, `TIP` and on the five-arm selftest (`pass=5 fail=0`). It is
killed only by `fx2-nharness`, a third git-dependent fact the special-case does not name
(`1/1` where `0/0` required). Consequence for the freeze's KILL RULE: "a mutation run that
disables a fact check must change the verdict line" is true only for a fixture that carries a
git-dependent fact other than the two the mutant names — the landed tree carries exactly two, so
a future special-case would be invisible to the registered counter. Keep the `fx2-nharness`
recipe (or add such a fact to the selftest fixture) as the anti-cheat receipt.

**F4 — the calibration row cannot carry a `row_current`-dependent run fact without breaking the
five-arm selftest (fixture design constraint the landing already respects).**
With such a fact present, planting a stale pointer falsifies the row's own fact as well, so each
planted arm gains **two** mismatches instead of one and the selftest's `ok_m+1` assertion fails:
measured `SELFDESC_SELFTEST … ok:closure_ptr=1,mismatches=1 stale_ptr:…,mismatches=2
stale_both:2 stale_incl:2 no_ptr:2 pass=1 fail=4` on `fixture-coupling`. Dropping the fact gives
`ok:0 / 1 / 1 / 1 / 1 pass=5 fail=0` (`fixture-gl`). The landed calibration row does **not**
carry a `--since-round 63` run fact (verified against `73597158:SCORECARD.md`), so the landed
tree is on the green side of this constraint — restoring such a fact in a later round would
silently re-break the selftest. State it in the round-70 lesson so it is not re-added.

**F5 — `mismatches` always 0 is killed three ways.**
`c1e` turns the red base tree green (`BASE=0/0` where `1/9` required), turns every planted
fixture green, and fails the four planted selftest arms (`pass=1 fail=4`). Robust.

**F6 — the Axes table is pipe- and cell-count-fragile, silently.**
Two measured instances: (i) a run fact whose command contains `|` splits the row, truncates
cell 2 and drops every fact after it — the counter then reads `rel=1` and
`closure_ptr: … names 0 'latest outside closure' pointers` on a row that carries both; (ii) a
fact appended after the row's trailing `|` lands in a fifth cell and is never evaluated — the
fixture read green with a planted `GIT_FACT_OK` fact that no checkout could satisfy. Both fail
*silently*, i.e. in the direction of lost coverage. Suggestion: `axes_table()` (round 41) or
`evaluate()` should warn/fail on a row whose cell count is not 4 and on an evidence cell
containing a bare `|`; this is a two-line change and does not weaken any fact. (Not applied —
this seat does not edit lane tools.)

**F7 — C2: the frozen control is exit-code-only, and three of its five clauses live only in
prose.** The table in §2 shows the control killing exactly the two mutants that move an exit
code. A field drop (`c2c`), a member drop (`c2d`) and a waiver that covers a fail (`c2e`) all
pass it. All three are named in the freeze's KILL RULE, but none is mechanised by
`refused-member-control.py`. Cheapest hardening inside the existing counter (no new file):
compare the refused fixture's verdict line for `not_evaluated=1` and the all-pass line for
`not_evaluated=0`, assert `total=` equals the module's registered member count (22), and add the
fail-waiver fixture (`fail-waiver-probe.py` in `logs/` is a 40-line implementation of that
fixture). Each clause is one assertion in the control's `main()`.

## 5. Not verified by this seat

- The real 22-member census was **not** re-executed by this seat; `total` is read from the
  module's `MEMBERS` (bounded detector, exact for the population question). The L1's receipt
  `measured/after/census-at-tip.out` (written 21:00, census bytes `a82cad11…`) carries the full
  run: 22 `pass` lines then `HOST_CENSUS pass=22 fail=0 not_evaluated=0 waived=0 total=22
  tierA_fail=0 tierB_fail=0`, exit 0.
- No mutant was run against the *authoring* Windows/MinGW host; this box is Linux and the
  NTFS refusal paths were exercised only through the frozen control's synthetic markers.
- `EX01ReconHarness`'s and `EX02CensusVerdict`'s `demo.md`/`report.md` claims were not audited
  beyond the byte-level checks above.

## 6. Hygiene and restoration evidence

- Lane files: read-only. `sha256sum tools/round41-scorecard-reconcile.py
  tools/round42-selfdesc-reconcile.py tools/round65-host-census.py` before and after this seat
  (§7) — unchanged by me; the only movement is the L1's own landing commits.
- Every mutant lives under `/fast/scratch/hyaku/kama-r70/MT01Mutants/v/`; the lane tool bytes
  were never edited in place. Each mutated file was re-parsed (`ast.parse`) before use and its
  sha256 recorded (`variants.txt`).
- `TMPDIR` was pinned to `/fast/scratch/hyaku/kama-r70/MT01Mutants/tmp` for every counter run,
  so the harness's throwaway checkouts and the selftest fixtures never touched `/tmp`.
- Scratch `/fast/scratch/hyaku/kama-r70/MT01Mutants/` is deleted before this seat yields; the
  out dir keeps the scripts and the JSON logs so the matrix can be re-run.

## 7. Deliverables in this directory

- `mutants.tsv` — the matrix (tool | mutant | killed? | counter output | why).
- `report.md` — this file.
- `fixtures.md` — exact fixture recipes, revs and the one-line plants.
- `variant-hashes.txt` — sha256 of every pristine/mutated tool byte plus the pinned fixture revs.
- `logs/` — `c1-landed.jsonl` (the §3 matrix), `c1-synthetic.jsonl` (the cross-check on this
  seat's reference-repair fixtures), `c2-latest.jsonl` (the §2 matrix on the landed census
  bytes), `c2-early.jsonl` (the same matrix on the superseded first candidate), plus the driver
  scripts and `variant-hashes.txt`.
- `mkfix.py`, `mkneg2.py`, `mkvar.py`, `c2latest.py`, `matrix2.py`, `fail-waiver-probe.py` —
  the reproducible driver scripts (fixture-only; they write nothing outside the scratch tree
  and the out dir).

## 8. Final-tip verification (run at close of this seat)

The lane advanced while the matrix ran (`0e14facd → 7be07423 → 73597158 → 910e6747 → af6eb6c2 →
…`). Tool bytes did not move after `73597158`/`af6eb6c2`, so every row above still describes the
shipped bytes. Re-verified at the tip current at close:

```
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD
61f3ec423acb642370e3e56395c28b8b6332aa44

$ sha256sum tools/round41-scorecard-reconcile.py tools/round42-selfdesc-reconcile.py tools/round65-host-census.py
c9bb4eae7f228f2a8e56f3df3392d54e182c9fe8e594792266618b07726e9f3e  tools/round41-scorecard-reconcile.py
3d9aff8f9c2236c2cb9337b08846da82de718bc1d9e8f1d283f1a71a03acd5c0  tools/round42-selfdesc-reconcile.py
44bebd671c0d12118c92ace1ef6bd7491a60c7acbce79f1668b81a822b245919  tools/round65-host-census.py

$ python3 tools/round42-selfdesc-reconcile.py --repo . --tip 61f3ec42
tip=61f3ec423acb642370e3e56395c28b8b6332aa44
r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 closure_ptr=1 mismatches=0 maxN=70 met=True
EXIT=0

$ python3 .ufo/waves/round-70/controls/refused-member-control.py tools/round65-host-census.py | tail -1
REFUSED_MEMBER_CONTROL refused_fixture_exit=1 allpass_fixture_exit=0
EXIT=0
```

Both frozen counters are green on the shipped bytes at the final tip; the five-arm selftest on
the shipped bytes reads `pass=5 fail=0` (row `landed`, `logs/c1-landed.jsonl`). The mutation
matrix therefore measures the shipped artifacts, not a stand-in.

Lane hygiene at close: no tracked lane file was created, modified or deleted by this seat except
this directory's own contents; `git status --porcelain -- .ufo/waves/round-70/w1/out/MT01Mutants`
lists only this seat's files. Scratch `/fast/scratch/hyaku/kama-r70/MT01Mutants/` was removed
after the final read of the logs copied here.

---

Artifacts: `MT01Mutants/` (`mutants.tsv`, `fixtures.md`, `variant-hashes.txt`, `logs/`).
Everything above is `MT01Mutants/report.md` verbatim; only this trailing pointer is added.
