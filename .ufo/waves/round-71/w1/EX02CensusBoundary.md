# EX02CensusBoundary — C2 build, kama r71 w1

Seat: executor, builds `tools/census-waiver-boundary.py` (frozen C2). Judged on operability.
Lane tip at freeze: `b43e71a8`. Lane tip at measurement: `e2b860c8` (the L1's round-71 commit).
Tool under test (worktree): `tools/census-waiver-boundary.py`
sha256 `7c75963300dbb46b030a856636cb39ffc97dd42be3f528de1868e07a365c060e` (1,087 lines).
Census bytes: `tools/round65-host-census.py` sha256 `44bebd671c0d12118c92ace1ef6bd7491a60c7acbce79f1668b81a822b245919`
(unchanged from the freeze).

## 1. What was built

One file, `tools/census-waiver-boundary.py`. CLI exactly `--census PATH` (default
`tools/round65-host-census.py`), `--shims DIR`, `--selftest`, `--json`.

Seven cases, each driving the census's `main()` in-process with a two-member synthetic table
(the round-70 frozen control's protocol, extended):

1. refused fixture: exit nonzero, `not_evaluated=1 fail=0 total=2`, the refusal line keeps its
   declared reason, and a second in-process call repeats the same verdict.
2. all-pass fixture: exit 0, `pass=2 fail=0 not_evaluated=0 total=2`.
3. `--waive` on the not-evaluated member: exit 0, `not_evaluated=1 waived=1 total=2`.
4. `--waive` on an evaluated failing member: exit nonzero, `fail=1`, no positive `waived`
   credit, `not_evaluated=0`; plus two declared strengthenings — a waiver on a *passing*
   member earns no credit, and a repeated call with the same waiver set repeats the verdict.
5. unknown waiver name: warns on stderr, exit and every verdict token unchanged, on the
   all-pass and on the refused fixture (no phantom `not_evaluated`, no forged `waived`).
6. the five named shims: each rejected, with the check that rejects it named.
7. landed census bytes: real 22-member run, exit 0, `pass=22 fail=0 not_evaluated=0 total=22`,
   no `waived` token.

Waiver channel: `main(waive=...)` when the signature exposes it, else `--waive NAME` on
`sys.argv`; `CENSUS_WAIVE` is cleared (not part of the census CLI). Shim corpus: the five
sources embedded byte-exactly with pinned sha256, materialized into a temp dir; `--shims DIR`
drives another copy and reports `BOUNDARY_SHIMS_DRIFT` on stderr. `--json` emits one object
with per-case checks, per-shim rejections and sha256s. `--selftest` prints
`BOUNDARY_SELFTEST pass=<n> fail=<n>` over 18 arms (7 cases, 5 shim rejections, 5 frozen-pair
holes, 1 distinctness) — the count the registered SKILL row names.

Exit map: 0 boundary holds; 1 a case failed or a shim survived; 2 could-not-evaluate.

Receipts in `.ufo/waves/round-71/w1/EX02CensusBoundary/`: `real-run.out`, `final-predicate.out`,
`selftest.out`, `shim-verdicts.out`, `fail-waiver-probe.out`, `attack-cases-probe.out`,
`boundary.json`, `shims5/` (the five named shims), `probes/` (the H1/H2 mutants and the two
drivers that produced the shim and attack receipts), `collision/competing-2148.py`.

## 2. Predicate, measured

At `b43e71a8` (21:38, before the L1 commit) the landed census was green —
`HOST_CENSUS pass=22 fail=0 not_evaluated=0 total=22`, exit 0 (30.3 s).

At `e2b860c8` (21:57, worktree, my build):

```
BOUNDARY_CASE 1 held refused-fixture exit=1 pass=1 fail=0 not_evaluated=1 total=2 repeat=stable
BOUNDARY_CASE 2 held all-pass exit=0 pass=2 fail=0 not_evaluated=0 total=2
BOUNDARY_CASE 3 held waived-not-evaluated exit=0 not_evaluated=1 waived=1 total=2
BOUNDARY_CASE 4 held waived-fail exit=1 fail=1 not_evaluated=0 waived=<absent> pass-waiver exit=0 waived=<absent> second-call exit=1 stderr="warning: --waive 'synthetic-broken' unused: member was evaluated (fail); a waiver covers only not-evaluated members"
BOUNDARY_CASE 5 held unknown-waiver all-pass 0->0 refused 1->1 verdict-unchanged stderr="warning: --waive 'no-such-member' is not a census member name"
BOUNDARY_CASE 6 held killed=5/5 s4-refusal-as-fail<-refusal_not_evaluated s5t-hardcoded-total<-allpass_population_total s6w-waiver-swallows-failure<-waiver_never_covers_fail s8r-second-call-silent<-reentrant_call s10d-refusal-branch-deleted<-refusal_marker_recognized
BOUNDARY_CASE 7 FAIL FAILED landed exit=1 pass=21 fail=1 not_evaluated=0 total=22 no-waived-token elapsed=76.0s | landed_exit_zero (exit=1); landed_pass_22 (pass=21); landed_fail_zero (fail=1)
BOUNDARY cases=7 killed=5 survivors=0
EXIT=1
```

A second attempt at 22:03:18 (`final-predicate.out`, 64.5 s, same HEAD, same tool sha) reproduces
case 7 exactly (`landed exit=1 pass=21 fail=1`), `BOUNDARY cases=7 killed=5 survivors=0`, EXIT=1;
`SCORECARD.md` was still being edited at 22:02:33, so the two record facts were not yet repaired.
Every other case is byte-identical across both runs.

Case 7 is red for one census member, not for the boundary:

```
FAIL [A] round42-selfdesc-reconcile selftest: exit=1 tail='SELFDESC_SELFTEST newest=70 planted_stale=57 ok:closure_ptr=1,mismatches=2 stale_ptr:closure_ptr=0,mismatches=3 ... pass=4 fail=1'
HOST_CENSUS pass=21 fail=1 not_evaluated=0 total=22
```

Standalone reproduction (82 s):
`python3 tools/round42-selfdesc-reconcile.py --selftest --work <tmp>` → EXIT=1, the failing arm
is the `ok` arm (`closure_ptr=1, mismatches=2`, expected 0). EX01PreReportGate independently
measured the two mismatches and confirmed they are **record** facts at `e2b860c8` (a stale
`SKILL.md` depth sha in the row, and the `run_bad` calibration fact) — no change to the census
bytes or to `round42` is required; repairing the record makes the member green. So C2's case 7
is currently measuring a red record, exactly as designed (specificity), and the freeze-time
green run above shows the clause is not vacuous.

`--selftest` at the same tip: `BOUNDARY_SELFTEST pass=17 fail=1` (only case 7 red); the frozen
18-arm count and every shim/specificity arm are green.

## 3. The five named shims, with the check that rejects each

Shims generated with the frozen generator, not re-authored (generation dir
`/fast/scratch/hyaku/kama-r71/EX02CensusBoundary/shims`, preserved here as `shims5/`;
sha256 equal to the tool's embedded pins). On the same five files the frozen round-70
control prints `PASS (hole)` for all five, exit 0 (`measured/before/shim-control-table.out`) —
the do-nothing control this gate has to beat.

```
python3 .ufo/waves/round-70/w1/out/CRT01ClaimC2/counterexamples.py --dir <dir>
```

| shim | sha256 | mechanism | rejecting check |
|---|---|---|---|
| s4-refusal-as-fail | `50d0bc3a…` | refusal counted as a failure | `refusal_not_evaluated` (verdict has no `not_evaluated=1`; also `refusal_not_fail`, `refusal_marker_recognized`) |
| s5t-hardcoded-total | `e2fc4fa1…` | `total=22` literal | `allpass_population_total` (2-member fixture prints `total=22`) |
| s6w-waiver-swallows-failure | `911f4cf8…` | a waiver greens a failing member | `waiver_never_covers_fail` (exit=0 on the waived-fail fixture; `fail_still_counted`, `fail_waiver_reentrant`) |
| s8r-second-call-silent | `8c6580bd…` | second call returns 0 with no output | `reentrant_call` (second verdict `<no verdict line>`) |
| s10d-refusal-branch-deleted | `60a3f1ce…` | refusal branch deleted | `refusal_marker_recognized` (no `refused [A] synthetic-refused: <reason>` line; also `refusal_not_evaluated`) |

Full lines: `shim-verdicts.out` (`BOUNDARY_SHIM_CASE held=True checks=10 failed=0`, sha256 per
shim). The embedded corpus sha256s equal the generated files' — the tool refuses to run
(`exit 2`) if its embedded bytes drift from the pins.

## 4. Beyond the frozen five (reviewer holes H1-H4)

RVW01C2Attack's round-71 holes, measured against the same case functions
(`attack-cases-probe.out`): H1 (waiver credited on a passing member) is rejected by
`waiver_never_covers_pass`; H2 (forged `waived` on an unknown waiver) and H4 (phantom
`not_evaluated` on an unknown waiver) by `unknown_waiver_(refusal_)verdict_unchanged`; H3
(second call with the same waiver set silenced) by `fail_waiver_reentrant`. H1/H3/H4 are the
round-71 reviewer's mutants; H2 is my reproduction of its forged-token probe. The landed census
holds all five case groups under the same clauses (`attack-cases-probe.out`, first block).

H1 is killed by a clause I added beyond the frozen case-4 minimum; it is declared here so a
reviewer can score the strengthening, not mistake it for a frozen requirement.

## 5. Specificity

- Landed bytes: cases 1-5 held (above); case 7 held at `b43e71a8` (21:38) and is red only for
  the record member at `e2b860c8`.
- `shims_distinct_from_census` arm: every shim differs from the census bytes.
- Case 7 is pinned to the landed path `tools/round65-host-census.py` (not to `--census`), so a
  shim candidate can never satisfy the specificity arm by being green on the real host.

## 6. Collision on the assigned path — the L1 must choose

- HEAD `e2b860c8` commits `tools/census-waiver-boundary.py` as blob `0ea22998` =
  sha256 `3a9cec94d3414e84d23ecfc019735649384198c6669172265602c216d0340790` (16,417 B).
  That is **not** this build: it is a concurrent 16.4 KB implementation (checks `c1..c7` plus an
  extra `c8` real-run line, argv-only waiver channel, shims regenerated from
  `.ufo/waves/round-70/.../counterexamples.py`, `--selftest` prints `pass=8`, no `--json`).
  Preserved at `collision/competing-2148.py` (sha256 identical to the commit).
- The committed `SKILL.md:310` row describes **this** build: seven waiver/not-evaluated cases,
  "the five shims … re-embedded by the tool", `BOUNDARY_SELFTEST pass=18 fail=0`. All three are
  false for `3a9cec94` and true for `7c759633`.
- The worktree file is that uncommitted modification; every receipt here measures it.
- Measured consequence of the committed build: its own receipt
  `measured/boundary-worktree.out` shows s5t/s6w/s8r killed through `c3`/`c5` (the GOOD-derived
  shims ignore argv, so the channel fails before the hole is tested), not through their named
  mechanisms; and it prints `BOUNDARY cases=7` while evaluating an eighth check.
- Reconciliation is one of: commit the worktree build (row becomes true), or revert it and
  rewrite the row to `c1..c8`/`pass=8`/generator-path shims. I did not commit or revert either.

## 7. What I could not verify

- Case 7 green at the final report tip: blocked by the two record mismatches above (C1 owns
  them; EX01 confirmed the diagnosis). The tool's clause is unchanged and was green at the
  freeze tip.
- Windows-host behaviour (the fixtures use `bash -c`; the census's Windows adaptation is
  untouched and out of this seat's scope).
- The registry population: EX01 reports the gate's declared regex does not match
  `tools/census-waiver-boundary.py`, so adding the row does not move `registered 79`; that is a
  freeze-drift fact (EX01 D3), not a property of this tool.
- `--json` on the final build parses (`boundary.json`, exit 1): cases 1-6 `held=true`, case 7
  `held=false`, all five shims keyed with their sha256. The only red is the record-bound case 7.
- The generated shim files are byte-identical to the frozen copies at
  `/fast/scratch/hyaku/kama-r71/l1/shim-control/shims` (sha256 equal for all five).

## 8. Exact commands

```
# frozen predicate
python3 tools/census-waiver-boundary.py --census tools/round65-host-census.py; echo EXIT=$?
# 18-arm selftest
python3 tools/census-waiver-boundary.py --selftest; echo EXIT=$?
# machine detail
python3 tools/census-waiver-boundary.py --json --census tools/round65-host-census.py
# the corpus the tool embeds (frozen generator)
python3 .ufo/waves/round-70/w1/out/CRT01ClaimC2/counterexamples.py --dir <dir>
# the C1-side red that keeps case 7 red at e2b860c8
python3 tools/round42-selfdesc-reconcile.py --selftest --work <empty-tmp-dir>; echo EXIT=$?
```
