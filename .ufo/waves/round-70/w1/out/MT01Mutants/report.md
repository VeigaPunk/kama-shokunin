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
  `e0acb993…`) and the integrated file (`c9bb4eae…`) differ: the integrated file adds
  `git update-ref refs/heads/master <tip>`. The delivered candidate does **not** provide a
  local `master` in its checkout; `gate-registry-check.py --selftest`'s lane-tip arm resolves
  `master`, so on a detached-HEAD source the candidate's nested checkouts are branchless and
  the arm fails. Measured (this report, §3, row `ex01-out`): the delivered candidate leaves
  `r41=1` on the green fixture while the integrated bytes leave `r41=0`. The integration
  addition is load-bearing, not cosmetic.
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
also has a `master` (see §3 F3).

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
$ python3 .ufo/waves/round-70/controls/refused-member-control.py v/L-c2c/round65-host-census.py
{"refused_fixture": ["pass [A] synthetic-pass", "refused [A] synthetic-refused: ... ", "HOST_CENSUS pass=1 fail=0 not_evaluated=1 total=2 tierA_fail=0 tierB_fail=0", "CENSUS_NOT_EVALUATED 1 member(s) without a waiver: synthetic-refused \u2014 exit 1"], "allpass_fixture": [...]}
REFUSED_MEMBER_CONTROL refused_fixture_exit=1 allpass_fixture_exit=0
(exit 0)

$ python3 $S/fail-waiver-probe.py v/L-c2e/round65-host-census.py
  FAIL [A] synthetic-fail: exit=1 tail='boom'
  HOST_CENSUS pass=0 fail=1 not_evaluated=0 total=1 tierA_fail=1 tierB_fail=0
FAIL_WAIVER_PROBE fail_member_waived_exit=0     <-- mutant; the repair prints 1
```

Reading: the frozen counter is a **two-point probe on the exit code only**. It kills the two
mutants that move an exit code, and it is blind to a deleted field, a deleted member and a
waiver that covers a fail. Those three are exactly the clauses the freeze's KILL RULE states in
prose (line content, `total=22`, "a waiver never covers a fail"); none of them is mechanised by
`refused-member-control.py`.

## 3. C1 matrix — `round42-selfdesc-reconcile.py` (+ the round-41 harness)

<!-- C1_TABLE -->

## 4. Findings the L1 should act on

<!-- FINDINGS -->

## 5. Not verified by this seat

- The real 22-member census was **not** executed end-to-end by this seat; `total` is read from
  the module's `MEMBERS` (bounded detector). The L1's own receipt
  (`measured/after/census-at-tip.out`) carries the full run.
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
- `logs/` — `c1-landed.jsonl`, `c2-latest.jsonl`, `c2-early.jsonl`, plus the raw detector output.
- `mkfix.py`, `mkneg2.py`, `mkvar.py`, `c2latest.py`, `matrix2.py`, `fail-waiver-probe.py` —
  the reproducible driver scripts (fixture-only; they write nothing outside the scratch tree
  and the out dir).
