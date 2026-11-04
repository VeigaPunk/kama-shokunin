# RV01PinsReview — C1 interpretation-pin attack

## Findings, by severity

### Blocking verification gap: C1 counter absent

`tools/round75-interpretation-pins.py` was absent on repeated reads, including the last read before reporting. A real invocation exited 2 (Python cannot open file), not an instrument could-not-evaluate receipt. Last timed CLI attempt: 2026-11-04T05:20:01.598921+00:00. Therefore I cannot certify the counter, its error mapping, its mutation execution, or a green C1 receipt. This is absence of the assigned deliverable at review time, not a demonstrated implementation defect. No admission recommendation.

The actual lane diff command below returned exit 0 and no output; at that point the two reviewed r74 modules had no tracked changes against base and the r75 counter was absent. New C2 arms appeared in the live binding module during review; all executable evidence here deliberately uses the freeze clone, not those concurrent edits. No changes to those modules, freeze, or another seat's files were made in the lane.

## Scope and axes

Calibration + operability. Review axes: independent boundary evidence, mutation discrimination, interpretation defensibility, honest scope. Read the frozen round-75 claims in full and C1 predicate verbatim. This report does not change that predicate. One shared clone was made; its HEAD was exactly `0908bab5cbf0ab6b435144fc525a3e18443dc08f`. No other runtime/agent was invoked. LSP was unavailable: `read xd://lsp` returned `No such tool`; there was no answering server for references/definition/diagnostics. Text inspection and executable fixture evidence are fallback evidence, not semantic LSP proof.

## Frozen C1 predicate, verbatim joined blockquote

> `python3 tools/round75-interpretation-pins.py --repo <lane>` prints one `INTERPRETATION_PINS pins=2 declared=2 killed=2 escaped=0` line and exits 0 only when each of the lane's two routed interpretation debts is bound to a boundary fixture whose declared reading the committed module produces and whose reversed reading a mutated copy of that module is caught producing — P1 older-demonstrated: a capability table older than the canonical round that carries a name the canon lacks contributes no name to `total` (an older table with two extra names leaves `total` at the canonical row count) and the all-tables-union mutant scores above it; P2 revision-mention context: a paragraph whose only 40-hex token sits in a `recorded at` clause and is not introduced by `rev`/`revision` names no revision (the `nc2_recorded_at_hex` paragraph grades clean, exit 0) and the any-hex mutant reports `stale-revision` there — it exits 1 naming each `INTERPRETATION_PINS_FINDING <pin>` with the declared and observed values and 2 on could-not-evaluate (a module absent, a fixture build failure, CLI misuse).

## Independent fixture results

### P1: older-demonstrated

Built my own SCORECARD, with names unrelated to the counter fixtures:

```markdown
**Capabilities — canonical list as of round 71**

| Capability | Evidence |
| --- | --- |
| alpha | independent |
| beta | independent |
| gamma | independent |

### Capabilities demonstrated in round 60

| Capability | Evidence |
| --- | --- |
| alpha | independent |
| beta | independent |
| gamma | independent |
| delta | independent |
| epsilon | independent |

```

Pristine frozen module: exit 0, `canon_round=71 canon_rows=3 demonstrated=0 total=3 invisible=0`.
Exact older-union control mutant: exit 0, `total=5 invisible=0` on the same fixture.

`total=3` is defensible as the declared current repertoire: round 71 supersedes older round-60 names, rather than resurrecting dropped capabilities. `total=5` means all historically demonstrated names remain current despite omission from the later canon; `total=4` would add only one old-only name, requiring an extra selection rule absent from this freeze. The r74 docstring at `tools/round74-selfdesc-canon.py:45-54` defines bold canon plus newer tables; `resolve` at lines 233-244 implements it. I found no contradiction between the r75 declaration and that implementation. The broader phrase “full repertoire” alone could support historical union, but the explicit rule resolves it.

### P2: revision-mention context

Own fixture repository: stable `tools/counter.py` and `plans/round-74-claims.md` committed as c0; `.ufo/waves/round-74/measured/r.out` header `# rev=<c0>` committed as c1; then only SCORECARD and lesson were added. Record paragraph:

```text
probe recorded at <c1> naming `.ufo/waves/round-74/measured/r.out` (content id, not a run revision).
```

Pristine frozen module: exit 0, `cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=0 unbound_claims=0 bound_revisions=0`.
Exact literal-hex control mutant: exit 1, `RECEIPT_CLAIM_V2_FINDING stale-revision` on that paragraph; base binding remains green.

This reading is defensible: a content object identifier is not necessarily a declared run revision. `REVISION_RE` requires `rev`/`revision` and `_claim_pass_v2` consumes that match (live source lines 83 and 178, with line shifts as C2 edits land). The inherited r74 predicate's “explicit 40-hex revision” was ambiguous, so the r75 freeze's narrower contextual declaration is doing real interpretive work. This is not proof that every possible natural-language revision claim is recognized; that broader grammar is outside C1.

Dead end retained: my first P2 fixture created the plan after c0. Both versions exited 1 because the base correctly emitted `RECEIPT_TIP_FINDING shifted ... plans/round-74-claims.md touched`. I rebuilt an independent fixture with the plan committed before c0; only that clean fixture decides P2. I did not suppress the base finding.

## Exact frozen control reruns

Read `.ufo/waves/round-75/controls/mutation-control.py:24-40`, and applied its exact replacements only to my clone copies. Freeze source bytes were materialized with `git show <freeze>:<path>`; no checkout/reset or other git mutation was used in the clone.

- Older-union: adds `_older` names from tables with `_r < canon_round` to `total`. Selftest exit 0, `SELFDESC_CANON_V2_SELFTEST pass=11 fail=0`.
- Literal-hex: changes `REVISION_RE` from contextual `rev`/`revision` to an arbitrary bounded 40-hex token. Selftest exit 0, `RECEIPT_CLAIM_V2_SELFTEST pass=9 fail=0`.

Thus independently re-derived **killed=0 escaped=2** against the base selftests. The canonical original receipt is `.ufo/waves/round-75/measured/before/control.out:3`, not the plan's absent per-claim `c1-mutants.out`. KamaR75 explained the latter is a derived view; freeze was not edited.

## Counter attacks and scores

| Attempt | Construct/evidence | Frozen-counter score |
| --- | --- | --- |
| Hardcoded success print | Proposed counterfeit green line without running modules/mutants | NOT RUN: counter absent; cannot claim caught |
| Mutant equals declared value | Independent P1 control fixture with older table containing only alpha/beta/gamma produces total=3 in both pristine and exact older-union mutant | NOT RUN against counter; module runs both exit 0; frozen kill rule requires escaped/failure |
| Mutant changes nothing semantically | No-op mutation is distinct bytes but same declared output; must not count as kill | NOT RUN: counter absent; cannot claim caught |
| Fixture both readings satisfy | P1 same-name older table, as above; P2 paragraph's recorded-at hash equals receipt header c0, so pristine and any-hex mutant both exit 0 | NOT RUN against counter; both independent fixture tests executed |

The P2 non-discriminating fixture still exposes `bound_revisions=0` vs `1`, but both exit 0 and the mutant produces no stale-revision. It cannot discharge the declared P2 kill. Source inequality is not semantic evidence, and an exit-0/exit-0 pair is not a P2 kill. A hardcoded instrument itself cannot be disproved merely by accepting its printed green line; actual runtime evidence or attack harness observation is required. Those counter-specific attacks remain explicit verification gaps, not inferred passes.

## Per-pin verdict

- **P1: load-bearing semantic boundary**, decided by independent CLI observations pristine `total=3`, mutant `total=5`, both exit 0. Base selftests do not protect it. The r75 counter's enforcement is **unverified**, not certified load-bearing.
- **P2: load-bearing semantic boundary**, decided by independent CLI observations pristine exit 0 versus literal-hex mutant exit 1 with `stale-revision`. Base selftests do not protect it. The r75 counter's enforcement is **unverified**, not certified load-bearing.

Neither pin is shown wrong on its declared boundary. Neither counter pin is admitted on evidence from an absent implementation. Residual risk: no counter references/diagnostics, CLI/error-path review, hardcode resistance, vacuous mutation rejection, or actual counter kill receipt was possible. Single canonical runtime, identity rerouting, saturation, and resume-continuity are not changed by this scoped Python interpretation review; no claims are made about them.

## Commands, exits, and relied-on output

All executed subprocess commands are recorded below, except source-dump stdout is reduced to its source identity (not a scored check). Each invocation had explicit `TMPDIR=/fast/scratch/hyaku/kama-r75/RV01PinsReview` and `PYTHONDONTWRITEBYTECODE=1`. Commands repeated under the same pathname are distinguished by ordering and the mutation descriptions above. Fixture git commits were preceded by a matching `git -C <fixture> rev-parse --show-toplevel` assertion.

```text
git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff dc58e51315e79d36df5fc530c95fbd3aecbf7593 -- tools/round74-selfdesc-canon.py tools/round74-receipt-claim-binding.py tools/round75-interpretation-pins.py
exit=0; stdout empty
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/clone rev-parse HEAD
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
0908bab5cbf0ab6b435144fc525a3e18443dc08f
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/clone show 0908bab5cbf0ab6b435144fc525a3e18443dc08f:tools/round74-selfdesc-canon.py
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
[freeze source bytes read successfully; stdout omitted]
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/clone show 0908bab5cbf0ab6b435144fc525a3e18443dc08f:tools/round74-receipt-claim-binding.py
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
[freeze source bytes read successfully; stdout omitted]
```

```text
python3 /fast/scratch/hyaku/kama-r75/RV01PinsReview/clone/tools/round74-selfdesc-canon.py --selftest --repo /fast/scratch/hyaku/kama-r75/RV01PinsReview/clone --work /fast/scratch/hyaku/kama-r75/RV01PinsReview/selftest-c1_f1b_older_union
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
SELFDESC_CANON_V2_ARM predicate ok
SELFDESC_CANON_V2_ARM predicate-at-tip ok
SELFDESC_CANON_V2_ARM kill-invisible ok
SELFDESC_CANON_V2_ARM clean-bold-covers ok
SELFDESC_CANON_V2_ARM bold-only ok
SELFDESC_CANON_V2_ARM demo-newer-round ok
SELFDESC_CANON_V2_ARM scorecard-missing ok
SELFDESC_CANON_V2_ARM no-capability-table ok
SELFDESC_CANON_V2_ARM cli-misuse ok
SELFDESC_CANON_V2_ARM repo-not-directory ok
SELFDESC_CANON_V2_ARM work-not-empty ok
SELFDESC_CANON_V2_SELFTEST pass=11 fail=0
```

```text
python3 /fast/scratch/hyaku/kama-r75/RV01PinsReview/clone/tools/round74-receipt-claim-binding.py --selftest --repo /fast/scratch/hyaku/kama-r75/RV01PinsReview/clone --work /fast/scratch/hyaku/kama-r75/RV01PinsReview/selftest-c1_f2c_literal_hex
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
RECEIPT_CLAIM_V2_ARM predicate ok one_line=True shape=True plan=True
RECEIPT_CLAIM_V2_ARM predicate-at-tip ok plan_at_master=True
RECEIPT_CLAIM_V2_ARM committed-fixtures ok c2_wrapped rc=1 kinds=['wrapped-claim'] bound_revisions=0 | c2_offset rc=1 kinds=['offset-claim'] bound_revisions=0 | c2_mixed_honest rc=0 kinds=[] bound_revisions=1 | c2_clean_realizable rc=0 kinds=[] bound_revisions=1
RECEIPT_CLAIM_V2_ARM blob-reader-seam ok pristine claims=1 unbound=0 mutant_case_sensitive_rev=None
RECEIPT_CLAIM_V2_ARM stale-revision ok exit=1 kinds=['stale-revision']
RECEIPT_CLAIM_V2_ARM same-line-stale-claim ok exit=1 kinds=['stale-claim']
RECEIPT_CLAIM_V2_ARM base-absent ok rc=2
RECEIPT_CLAIM_V2_ARM record-missing ok rc=2
RECEIPT_CLAIM_V2_ARM cli-misuse ok rc=2
RECEIPT_CLAIM_V2_SELFTEST pass=9 fail=0
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture init -q
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture rev-parse --show-toplevel
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
/fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture
```

```text
python3 /fast/scratch/hyaku/kama-r75/RV01PinsReview/clone/tools/round74-selfdesc-canon.py --repo /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
SELFDESC_CANON_V2 canon_round=71 canon_rows=3 demonstrated=0 total=3 invisible=0
```

```text
python3 /fast/scratch/hyaku/kama-r75/RV01PinsReview/clone/tools/round74-selfdesc-canon.py --repo /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
SELFDESC_CANON_V2 canon_round=71 canon_rows=3 demonstrated=0 total=5 invisible=0
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture rev-parse --show-toplevel
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
/fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture add -A
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture -c user.name=fixture -c user.email=fixture@invalid commit -qm seed
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture rev-parse HEAD
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
10e784ee59859c7978e3db733f996f60c4ed7fd4
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture rev-parse --show-toplevel
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
/fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture add -A
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture -c user.name=fixture -c user.email=fixture@invalid commit -qm receipt
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture rev-parse HEAD
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
07984fbdf9f8ccf2992ae2a50ea5631ea063efc0
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture rev-parse --show-toplevel
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
/fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture add -A
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture -c user.name=fixture -c user.email=fixture@invalid commit -qm content-id record
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
```

```text
python3 /fast/scratch/hyaku/kama-r75/RV01PinsReview/clone/tools/round74-receipt-claim-binding.py --repo /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture --round 74 --tip HEAD
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=1
RECEIPT_TIP_FINDING shifted .ufo/waves/round-74/measured/r.out :: plans/round-74-claims.md touched by 2854ec02793f
RECEIPT_CLAIM_V2 round=74 cited=1 bound=0 unbound=0 shifted=1 stale=0 claims=0 unbound_claims=0 bound_revisions=0
```

```text
python3 /fast/scratch/hyaku/kama-r75/RV01PinsReview/clone/tools/round74-receipt-claim-binding.py --repo /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture --round 74 --tip HEAD
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=1
RECEIPT_TIP_FINDING shifted .ufo/waves/round-74/measured/r.out :: plans/round-74-claims.md touched by 2854ec02793f
RECEIPT_CLAIM_V2_FINDING stale-revision .ufo/waves/round-74/measured/r.out :: 5: probe recorded at 07984fbdf9f8ccf2992ae2a50ea5631ea063efc0 naming `.ufo/waves/round-74/measured/r.out` (content id, not a run revision).
RECEIPT_CLAIM_V2 round=74 cited=1 bound=0 unbound=0 shifted=1 stale=0 claims=0 unbound_claims=0 bound_revisions=0
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean init -q
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean rev-parse --show-toplevel
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
/fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean rev-parse --show-toplevel
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
/fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean add -A
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean -c user.name=fixture -c user.email=fixture@invalid commit -qm stable surfaces
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean rev-parse HEAD
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
3e925d534bd99fda4b49a7db57037ae5253a60c6
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean rev-parse --show-toplevel
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
/fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean add -A
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean -c user.name=fixture -c user.email=fixture@invalid commit -qm receipt
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean rev-parse HEAD
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
9f9b1f4032998b65daaa09013ab4eac03d202ac5
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean rev-parse --show-toplevel
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
/fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean add -A
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean -c user.name=fixture -c user.email=fixture@invalid commit -qm record only
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
```

```text
python3 /fast/scratch/hyaku/kama-r75/RV01PinsReview/clone/tools/round74-receipt-claim-binding.py --repo /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean --round 74 --tip HEAD
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
RECEIPT_CLAIM_V2 round=74 cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=0 unbound_claims=0 bound_revisions=0
```

```text
python3 /fast/scratch/hyaku/kama-r75/RV01PinsReview/clone/tools/round74-receipt-claim-binding.py --repo /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean --round 74 --tip HEAD
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=1
RECEIPT_CLAIM_V2_FINDING stale-revision .ufo/waves/round-74/measured/r.out :: 5: probe recorded at 9f9b1f4032998b65daaa09013ab4eac03d202ac5 naming `.ufo/waves/round-74/measured/r.out` (content id, not a run revision).
RECEIPT_CLAIM_V2 round=74 cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=0 unbound_claims=0 bound_revisions=0
```

```text
python3 /fast/scratch/hyaku/kama-r75/RV01PinsReview/clone/tools/round74-selfdesc-canon.py --repo /fast/scratch/hyaku/kama-r75/RV01PinsReview/both-readings
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
SELFDESC_CANON_V2 canon_round=71 canon_rows=3 demonstrated=0 total=3 invisible=0
```

```text
python3 /fast/scratch/hyaku/kama-r75/RV01PinsReview/clone/tools/round74-selfdesc-canon.py --repo /fast/scratch/hyaku/kama-r75/RV01PinsReview/both-readings
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
SELFDESC_CANON_V2 canon_round=71 canon_rows=3 demonstrated=0 total=3 invisible=0
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean rev-parse --show-toplevel
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
/fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean add -A
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
```

```text
git -C /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean -c user.name=fixture -c user.email=fixture@invalid commit -qm non-discriminating record
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
```

```text
python3 /fast/scratch/hyaku/kama-r75/RV01PinsReview/clone/tools/round74-receipt-claim-binding.py --repo /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean --round 74 --tip HEAD
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
RECEIPT_CLAIM_V2 round=74 cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=0 unbound_claims=0 bound_revisions=0
```

```text
python3 /fast/scratch/hyaku/kama-r75/RV01PinsReview/clone/tools/round74-receipt-claim-binding.py --repo /fast/scratch/hyaku/kama-r75/RV01PinsReview/own-fixture-clean --round 74 --tip HEAD
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview/clone
exit=0
RECEIPT_CLAIM_V2 round=74 cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=0 unbound_claims=0 bound_revisions=1
```

```text
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round75-interpretation-pins.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --work /fast/scratch/hyaku/kama-r75/RV01PinsReview/counter-work
cwd=/fast/scratch/hyaku/kama-r75/RV01PinsReview
exit=2
python3: can't open file '/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round75-interpretation-pins.py': [Errno 2] No such file or directory
```

## Bounds, cleanup, and self-evaluation

No tool installed or upgraded. Only own scratch and the two explicitly requested report paths were written. Scratch is removed after preserving these receipts; cleanup result is recorded below. Initial shell setup failed before running because its requested cwd did not exist; retried from fleet cwd with absolute scratch path, successfully. The absent C1 file was re-read repeatedly as requested, and a timed CLI invocation confirms absence. No module lane writes or git mutations occurred.

Self-evaluation (not an admission): accuracy 4/5 (counter claims deliberately withheld); completeness 3/5 (four counter-specific attacks blocked by absent deliverable); clarity 4/5 (semantic boundary distinguished from counter certification); actionability 4/5 (specific missing attacks named); conciseness 3/5 (full command receipts intentionally retained). Mean 3.6/5. Highest-impact next review is the real counter's rejection of vacuous mutants and non-discriminating fixtures once it exists. User should agree that no absent counter is certified.

Cleanup: `shutil.rmtree(Path("/fast/scratch/hyaku/kama-r75/RV01PinsReview"))` completed without exception; scratch removed.

## Addendum — counter attacks after the C1 module landed (L1 run, 2026-11-04T05:24:43.331739+00:00)

This addendum supersedes the earlier absence finding and NOT RUN entries for the four scoped counter attacks. L1 reported the counter landed; I then read its complete implementation and independently ran it. The L1 green receipt itself was not treated as my executed evidence. Reviewed counter SHA-256: `fac5ffbb8c2e6eb0e135581353352c59fa605beb68fd9abded1295cc61ec0d21`.

### Findings by severity

No actionable defect reproduced in the requested C1 attacks. The earlier missing-deliverable gap is now closed. Findings below are recommendations, not an admission.

### Hardcoded success print / counterfeit measurements

`grade` reads P1 values from imported pristine and source-mutated `resolve` results at `tools/round75-interpretation-pins.py:111-124`. It reads P2 process exits and mutant finding output from actual subprocess results at lines 139-157. `evaluate` derives declared/killed/escaped from those measurements (95-101); `emit` formats that derived document (161-168); main returns its derived exit (245-247). A constant summary is not accepted as an input and is not how this implementation earns green. There is no external receipt authentication: replacing the counter itself with a dishonest printer would trivially forge stdout, and the counter cannot defend against replacement of its own code. That is a trust boundary, not a demonstrated defect in the frozen implementation.

Executed attack: loader injection makes BOTH pristine and mutated P1 modules return a hardcoded `total=3`. The unmodified counter evaluator reports `declared=2 killed=1 escaped=1`, names `declared=3 mutant=3 observed=3 mutant_ok=False`, and returns 1. Hardcoded module success does not discharge P1.

### Mutant equals declared value

Executed with only the in-memory declaration changed to 5: real old-union mutant still produces 5; pristine produces 3. Counter reports `declared=1 killed=1 escaped=1`, finding `declared=5 mutant=5 observed=3 mutant_ok=True`, exit 1. Equality cannot count as a kill even when mutant shape is otherwise expected. The no-op and both-readings attempts below also test equality while pristine equals the declaration.

### Distinct-bytes, semantic no-op mutants

The attack driver replaces each in-memory mutation replacement with its original source anchor plus a comment. The copies differ in bytes, but both semantic outputs remain declared values. The original mutation function still applies the replacements and executes the real modules. Counter reports `declared=2 killed=0 escaped=2`, findings P1 `mutant=3` and P2 `mutant=0`, exit 1. Neither is counted as a kill; no false green.

### Fixtures both readings satisfy

No CLI fixture input exists: the counter constructs both fixtures internally, so `--repo`/`--work` cannot supply arbitrary SCORECARD content. To adversarially test that builder boundary without changing counter source, the driver changes only imported fixture-builder data in memory: P1 canon is alpha/older-one/older-two, so both “extra” older rows duplicate current names; P2 record uses the receipt-header c0 instead of c1 in its recorded-at clause. Real resolvers and real subprocesses still run against the generated fixtures. Both readings then satisfy each declared output. Counter reports `declared=2 killed=0 escaped=2`, both pin findings, exit 1. Such fixtures cannot discharge either pin.

All perturbations are isolated to the scratch driver process; the counter, lane modules, freeze and other seats' files remain unchanged. This is fault injection into imported data/functions, not a claim that these attacks are exposed CLI options. The driver's calls to frozen `grade`/`evaluate`/`emit` are the actual scoring path. The fixture helpers create their scratch git repositories as part of that path; no manual git/jj command or new clone was used in this addendum.

### Commands, exits, observed lines

Every command below used cwd `/fast/scratch/hyaku/kama-r75/RV01PinsReview` and explicit `TMPDIR` of that same path, plus `PYTHONDONTWRITEBYTECODE=1`. Modes ran concurrently in separate work directories.

```text
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round75-interpretation-pins.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --work /fast/scratch/hyaku/kama-r75/RV01PinsReview/cli-work --json
exit=0
INTERPRETATION_PINS pins=2 declared=2 killed=2 escaped=0
```

```text
python3 /fast/scratch/hyaku/kama-r75/RV01PinsReview/attacks.py baseline
exit=0
INTERPRETATION_PINS pins=2 declared=2 killed=2 escaped=0
```

```text
python3 /fast/scratch/hyaku/kama-r75/RV01PinsReview/attacks.py hardcoded
exit=1
INTERPRETATION_PINS pins=2 declared=2 killed=1 escaped=1
INTERPRETATION_PINS_FINDING P1-older-demonstrated declared=3 mutant=3 observed=3 mutant_ok=False
```

```text
python3 /fast/scratch/hyaku/kama-r75/RV01PinsReview/attacks.py equals-declared
exit=1
INTERPRETATION_PINS pins=2 declared=1 killed=1 escaped=1
INTERPRETATION_PINS_FINDING P1-older-demonstrated declared=5 mutant=5 observed=3 mutant_ok=True
```

```text
python3 /fast/scratch/hyaku/kama-r75/RV01PinsReview/attacks.py noop
exit=1
INTERPRETATION_PINS pins=2 declared=2 killed=0 escaped=2
INTERPRETATION_PINS_FINDING P1-older-demonstrated declared=3 mutant=3 observed=3 mutant_ok=False
INTERPRETATION_PINS_FINDING P2-revision-mention-context declared=0 mutant=0 observed=0 mutant_ok=False
```

```text
python3 /fast/scratch/hyaku/kama-r75/RV01PinsReview/attacks.py both-readings
exit=1
INTERPRETATION_PINS pins=2 declared=2 killed=0 escaped=2
INTERPRETATION_PINS_FINDING P1-older-demonstrated declared=3 mutant=3 observed=3 mutant_ok=False
INTERPRETATION_PINS_FINDING P2-revision-mention-context declared=0 mutant=0 observed=0 mutant_ok=False
```

### Reproducible driver source (scratch deleted after capture)

```python
import importlib.util
import pathlib
import re
import sys

sys.dont_write_bytecode = True
LANE = pathlib.Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
ROOT = pathlib.Path('/fast/scratch/hyaku/kama-r75/RV01PinsReview')
spec = importlib.util.spec_from_file_location('reviewed_counter', LANE / 'tools/round75-interpretation-pins.py')
counter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(counter)
mode = sys.argv[1]
original_load = counter.load

if mode == 'equals-declared':
    counter.DECLARED_TOTAL = 5
elif mode == 'noop':
    counter.MUTANTS = {name: (filename, old, old + '\n# distinct bytes, identical semantics\n')
                       for name, (filename, old, new) in counter.MUTANTS.items()}
elif mode in ('hardcoded', 'both-readings'):
    def load(path, name):
        module = original_load(path, name)
        if mode == 'hardcoded' and 'canon' in name:
            module.resolve = lambda text, inherited: {'total': 3}
        if mode == 'both-readings' and name == 'pins_pristine_canon':
            module.BOLD71 = ('**Capabilities — canonical list as of round 71**\n\n'
                             '| Capability | Evidence | Pointer | Round |\n'
                             '| --- | --- | --- | --- |\n'
                             '| alpha | present | `a` | 71 |\n'
                             '| older-one | present | `b` | 71 |\n'
                             '| older-two | present | `c` | 71 |\n')
        if mode == 'both-readings' and name == 'pins_pristine_binding':
            original_record = module._record
            def record(fixture, round_no, body, lesson_body='No citation here.\n'):
                receipt = pathlib.Path(fixture.path) / '.ufo/waves/round-74/r.out'
                c0 = re.search(r'rev=([0-9a-f]{40})', receipt.read_text()).group(1)
                body = re.sub(r'recorded at [0-9a-f]{40}', 'recorded at ' + c0, body)
                return original_record(fixture, round_no, body, lesson_body)
            module._record = record
        return module
    counter.load = load
elif mode != 'baseline':
    raise SystemExit('unknown mode')

document = counter.grade(ROOT / ('work-' + mode))
counter.emit(document, True)
raise SystemExit(document['exit'])
```

### Final per-pin verdict and residual risk

- **P1: load-bearing.** Independent boundary produced 3 versus 5; real counter measured 3 versus 5 and green. Hardcoded 3, equal declaration, no-op mutant, and non-discriminating fixture were rejected (exit 1, escaped >= 1).
- **P2: load-bearing.** Independent boundary produced exit 0 versus stale-revision exit 1; real counter measured the same distinction and green. No-op mutant and non-discriminating fixture were rejected (exit 1, escaped=2 with both attacks).

No scoped attack made C1 green without the declared boundary distinction. The declared readings remain defensible for the reasons in the original report. This does not establish arbitrary printer tamper-resistance, an exhaustive natural-language grammar, or all possible mutants. LSP remains unavailable; exact runtime fault-injection results and cited code paths are the evidence. No unrelated resume/rerouting/saturation claim is made.

Updated self-evaluation: accuracy 4/5 (trust boundary explicitly limited), completeness 4/5 (all four attacks now exercised or source-reviewed as requested; not an exhaustive tampering audit), clarity 4/5 (original absence chronology retained but superseded here), actionability 4/5 (exact commands and driver retained), conciseness 3/5 (two chronological reports and embedded receipts are lengthy). Mean 3.8/5. No missing scoped counter attack remains; broader runtime security testing is outside this ticket.

Addendum cleanup: own scratch removed with `shutil.rmtree(S)` without exception; no tools installed/updated.
