# X1SelftestPower — selftest power of append-only-audit v3 (round 48, lane kama)

**Verdict:** v2 (base `33e0058`) fails **10 of the 27** v3 selftest cases — 8 of the 9 round-48-new-or-modified ones. **`clamp` passes on v2**, so it tests no new behaviour versus the base (v2 already clamped at `33e0058:tools/append-only-audit.py:253`); it is a regression guard, not round-48 coverage. Second finding: the case set does **not** cover a rewrite of lines *before the first `## ` heading* — the exact shape of the round-48 build finding (the round-45 SCORECARD banner at `SCORECARD.md:6`). A v3 mutant that exempts the pre-heading region passes **27/27** and would have missed that defect.

## Method

| step | command | result |
|---|---|---|
| v2 extracted | `git -C <lane> show 33e0058:tools/append-only-audit.py > $S/v2-append-only-audit.py` | 608 lines, sha256 `a32b5c2a…86fd`, identical to the blob (`git show … \| sha256sum` matches) |
| v2 baseline | `python3 $S/v2-append-only-audit.py --selftest --scratch $S/st-v2` | `AOA_SELFTEST pass=19 fail=0`, exit 0 |
| v3 baseline | `python3 <lane>/tools/append-only-audit.py --selftest --scratch $S/st-v3` | `AOA_SELFTEST pass=27 fail=0`, exit 0 |
| parity | 27 names/order extracted from `tools/append-only-audit.py:838-849` vs the port's list | 27 vs 27, identical order — no case dropped or added |
| port, verbatim | `python3 port_v3_cases_to_v2.py --v2 $S/v2-append-only-audit.py --mode verbatim --scratch $S --json results-verbatim.json` | `cases=27 pass=17 fail=10`, exit 1 |
| port, compat | same with `--mode compat` | `cases=27 pass=17 fail=10`, exit 1 |

Port (`port_v3_cases_to_v2.py`): each v3 case body is kept verbatim, term by term, but its module
names are bound to the **v2** module (`Fixture`, `lines`, `audit`, `exit_code`, `parse_contract`,
`split_lines`, `CONTRACT`, `HEADER`); each conjunction term became its own check so a failure names
the term. A case that raises counts as failed, exactly as v3's own `case()` does (`tools/append-only-audit.py:511-516`).

Two modes, because v3's fixtures carry the new five-cell `region` column and that is not a field name:

- **verbatim** — the v3 case text as written. A contract fixture dies at v2's four-cell validation (`contract line 2: 5 cells, want 4`).
- **compat** — the most generous adaptation that is not a rename: v2's `parse_contract` is wrapped to drop a fifth cell before validation. This isolates "v2 lacks the behaviour" from "v2 cannot parse the file". No assertion was relaxed.

`HEADER` in the ported cases resolves to v2's four-cell `HEADER`, as in v3 where it resolves to v3's five-cell one — the header/row mismatch is part of the fixture a v2 tool is asked to read.

## Result per case

| # | case | v2 verbatim | v2 compat | failing terms on v2 | classification |
|---|---|---|---|---|---|
| 1 | `no-deletion` | pass | pass | — | unchanged pre-48 case |
| 2 | `below-threshold` | pass | pass | — | unchanged |
| 3 | `exact-threshold-unrestored` | pass | pass | — | unchanged |
| 4 | `restored-later` | pass | pass | — | unchanged |
| 5 | `partial` | pass | pass | — | unchanged |
| 6 | `undeclared-file` | pass | pass | — | unchanged |
| 7 | `declared-file-removed` | pass | pass | — | unchanged |
| 8 | `merge-first-parent` | pass | pass | — | unchanged |
| 9 | `dashdash-lines` | pass | pass | — | unchanged |
| 10 | `crlf-and-eof` | pass | pass | — | unchanged |
| 11 | `multiset` | pass | pass | — | unchanged |
| 12 | `window-max` | **FAIL** | **FAIL** | `exit_code == 1` | behavioural (round 48) |
| 13 | `relocation` | pass | pass | — | unchanged |
| 14 | `contract` | **FAIL** | **FAIL** | verbatim: `AuditError 5 cells`; compat: `declarations[0].ok`, `bad contract 2/3/4 rejected` | behavioural + absent concept (round 48) |
| 15 | `threshold-flag` | pass | pass | — | unchanged |
| 16 | `crlf-restore-exact` | pass | pass | — | unchanged |
| 17 | `dup-kept-not-restored` | pass | pass | — | unchanged |
| 18 | `final-segment` | pass | pass | — | unchanged |
| 19 | `vanished-and-paths` | **FAIL** | **FAIL** | verbatim: `AuditError 5 cells`; compat: `summary.bad_declarations` | counter field only (round 48) |
| 20 | `exempt-rewritten` | **FAIL** | **FAIL** | verbatim: `AuditError`; compat: `graded==0`, `ungraded==24`, `status==ungraded`, `summary.ungraded_lines==24`, `exit_code==0` | behavioural (round 48) |
| 21 | `exempt-gutted` | **FAIL** | **FAIL** | verbatim: `AuditError`; compat: `graded==24` | counter field only (round 48) |
| 22 | `exempt-gutted-then-regrown` | **FAIL** | **FAIL** | verbatim: `AuditError`; compat: `ungraded==24`, `status==ungraded`, `exit_code==0` | behavioural (round 48) |
| 23 | `dated-rewritten` | **FAIL** | **FAIL** | verbatim: `AuditError`; compat: `graded==25`, `ungraded==0` | counter field only (round 48) |
| 24 | `only-errata` | **FAIL** | **FAIL** | verbatim: `AuditError`; compat: `c1 status==ungraded`, `c1 ungraded==25`, `c2 graded==20` | behavioural (round 48) |
| 25 | `clamp` | **pass** | **pass** | — | **discriminates nothing against v2** |
| 26 | `bad-declarations` | **FAIL** | **FAIL** | verbatim: `AuditError`; compat: `oks==[F,F,F,F,T]`, `exit_code==1` | absent concept (round 48) |
| 27 | `clean` | **FAIL** | **FAIL** | verbatim: `AuditError`; compat: `ungraded==1`, `bad_declarations==0`, `exit_code==0` | behavioural (round 48) |

Totals: **17 pass / 10 fail** in both modes, and the failing *set* is identical in both modes — no case becomes passable once the region column is tolerated, so the failures are missing behaviour/fields, not missing TSV cells.

## Finding A — `clamp` passes on v2: it is a regression guard, not round-48 coverage

The ticket expects every round-48 case to fail on v2. `clamp` (`tools/append-only-audit.py:803-813`) does not:

```
pass clamp
```

v2 already clamps, at `git show 33e0058:tools/append-only-audit.py:253`:

```
h = sum(min(n, max(0, M[l] - K[l])) for l, n in D.items())
```

v3 only renames `D` to `G` (`tools/append-only-audit.py:424`). On the `clamp` fixture v2 reports `deleted=40 restored_max=20 status=partial` — the case's expected values exactly (see `results-compat.json`, case `clamp`).

The case is not empty: mutant **M4** (drop `max(0, …)`, line 424) is killed by `clamp` alone (`selftest-M4-no-clamp.log`: `pass=26 fail=1`, `restored_max=10` instead of 20). So `clamp` guards pre-existing v2 behaviour; it contributes **zero** discrimination between v2 and v3 and should not be counted as round-48 selftest growth. The Round-47 attribution to seat K1Fixture is correct as provenance of the *bug*, the base already carried the *fix*.

## Finding B — no case covers the pre-heading region: the round-48 build finding is outside the suite

The build finding is a rewrite of `SCORECARD.md:6`, before any `## ` heading (section `None`). No case exercises that shape: `exempt-rewritten` rewrites lines *inside* `## Axes`.

Mutant **M2** makes the plausible mistake ("the head is re-derived too") by adding `eligible.add(None)` when a file has `exempt=` titles — a three-line diff after `tools/append-only-audit.py:411`:

```
== M2-preheading-exempt exit=0 AOA_SELFTEST pass=27 fail=0
```

27/27, exit 0: the whole suite passes while the tool stops grading the class of line that round 48 fixed. Direct behavioural probe (`probe_preheading.py`, 24 banner lines before the first heading, rewritten in place, `exempt=## Axes|## Plan` on the same file):

| tool | graded | ungraded | status | exit |
|---|---|---|---|---|
| v3 (`probe-v3.json`) | 24 | 0 | `unrestored` | 1 |
| M2 (`probe-M2.json`) | 0 | 24 | `ungraded` | 0 |

Consequence for the counter: C1's `selftest` control is only `--selftest` exit 0 with `AOA_SELFTEST pass=n fail=0`, `n >= 20` (`tools/round48-append-audit-v3-check.py:71-75,654-663`). A build carrying M2 would report `selftest=1` and would not have surfaced the base's `regressed=1` — the lane measurement, not the selftest control, held the detection power here.

**Proposed fix** (`proposed-preheading-case.diff`, verified, not applied to the lane): add case `pre-heading-graded` — a file with `exempt=## Axes|## Plan` whose 24 pre-heading lines are rewritten, expecting `deleted=24 graded=24 ungraded=0 status=unrestored exit 1`.

- v3 + case (`v3-plus-preheading.py --selftest`): `pass=28 fail=0`, exit 0 — the case is consistent with the shipped grader.
- M2 + case (`mutant-M2-plus-preheading.py --selftest`): `pass=27 fail=1`, killed by `pre-heading-graded` (`graded=0 status=ungraded`), exit 1.

Kill matrix for the other mutants (`kill-matrix.md`, logs `selftest-M*.log`):

| mutant | killed by |
|---|---|
| M1 exemptions disabled (`if s in eligible:` → `if False:`, line 417) | 3 cases: `exempt-rewritten`, `exempt-gutted-then-regrown`, `clean` |
| M2 pre-heading exempt | **none (survives 27/27)** |
| M3 `exit_code` ignores `regressed` (line 473) | `window-max` only |
| M4 clamp removed (line 424) | `clamp` only |

M3 is the same defect v2 carries at `33e0058:289` (`return 1 if s["partial"] or s["unrestored"] or s.get("vanished") else 0`), which is why `window-max` fails on v2 on exactly one term while its other six terms (including `summary.regressed == 1`) already pass: v2 *computes* `regressed` and ignores it.

## Secondary observations

- `contract` and `vanished-and-paths` are pre-existing case names whose v3 bodies were extended for round 48 (five-cell rows, `declarations`, `bad_declarations`); both now fail on v2. They belong in the round-48 delta but are not among the "added" cases the ticket lists.
- In compat mode `exempt-gutted` and `dated-rewritten` agree with v3 on `status` and `exit` — they fail only on `graded`/`ungraded`. A v3-shaped tool that carried those two counters but no eligibility window would pass both. If the claim is "these cases pin region grading", only `exempt-rewritten`, `exempt-gutted-then-regrown`, `only-errata` and `clean` pin behaviour; the window-max eligibility rule (`>= pcount[t]`) is pinned by `exempt-gutted-then-regrown` and `clean` (both killed by M1).
- `bad-declarations` fails in compat only because v2 has no declaration binding at all; it is the strongest of the new cases, since the whole concept is absent at the base.

## Evidence

All under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1SelftestPower/`:

| file | content |
|---|---|
| `port_v3_cases_to_v2.py` | the port harness (both modes, per-term checks) |
| `results-verbatim.json`, `results-compat.json` | per-case, per-term results plus v2's captured event/summary |
| `run-verbatim.log`, `run-compat.log` | port runs: `cases=27 pass=17 fail=10`, exit 1 each |
| `run-v3-selftest.log`, `run-v2-selftest.log` | baselines `pass=27 fail=0` / `pass=19 fail=0`, exit 0 |
| `table.md` | the per-case matrix with full failing-term text |
| `probe_preheading.py`, `probe-v3.json`, `probe-M2.json` | pre-heading probe, both tools |
| `gen_mutants.py`, `kill-matrix.md`, `selftest-M1..M4*.log` | mutants (regenerated byte-identically by `gen_mutants.py`), kill matrix, runs |
| `mutant-M2-preheading-exempt.py`, `v3-plus-preheading.py` | the surviving mutant and v3 with the proposed case |
| `selftest-v3-plus-preheading.log`, `selftest-M2-plus-preheading.log` | `pass=28 fail=0` / `pass=27 fail=1` |
| `proposed-preheading-case.diff` | unified diff against `tools/append-only-audit.py` (proposal only) |

Runs were made with `PYTHONHASHSEED` default, Python 3.14.8, git 2.56.0. Fixtures were created under `/fast/scratch/hyaku/kama-r48/X1SelftestPower` (one scratch root, one `tempfile.mkdtemp` per run); no live clone was needed because the v2 blob is read by `git show` and every fixture repo is a fresh `git init` under that scratch root. The scratch root was removed after the artifacts above were copied. Lane, fleet repo and counters were not modified; no tool was installed (nothing was needed; pacman untouched).

## Risks / limits

- The port is a re-expression of 27 case bodies in one file; a transcription slip would show as a spurious pass or failure. Mitigation: each case's term order matches the v3 source, the case-name list and order were compared programmatically against `tools/append-only-audit.py:838-849`, and the v3/v2 baselines reproduce (`27/0`, `19/0`). The ported cases are not the shipped ones — only the shipped `--selftest` on v3 is authoritative.
- "compat" mode is a judgement call about the most generous adaptation; it changed no verdict (same 10 cases fail with and without it), so the conclusion does not rest on it.
- `clamp` passing on v2 says the case adds no discrimination against the base; it does not say the case is worthless (M4 shows it kills). If C1's calibration claim counts it as round-48 coverage, the delta is 7 discriminating cases, not 8.
- M2 is one plausible mutation of the region logic; the claim is "no case pins the pre-heading region", not "no case pins region grading" (M1 is killed three times).
