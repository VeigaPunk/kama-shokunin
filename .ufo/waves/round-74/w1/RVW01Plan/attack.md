# RVW01Plan — frozen-plan attack

Axes: calibration (assigned), with operability and freshness contracts reviewed. Recommendation only; no admission, implementation, freeze edit, route change, or runtime invocation.

## Findings, by severity

### High — C3 clean fixture cannot satisfy the literal frozen preservation rule

`plans/round-74-claims.md:151-156,165-169` requires block bytes at the token's revision A and requires `c3_clean` to exit 0. But `controls/build-survivors.py:232-236` commits only LOG.md as A, then creates PROVINCE.md in the next commit while stamping it `recorded at A`. The edited fixture has the same seed-before-block construction at lines 223-228. Therefore neither fixture has ANY PROVINCE.md at its claimed recorded revision. The clean arm is not “same block unchanged after A”: there was no block at A.

Executed on freshly rebuilt pinned fixtures (retained in `shortcut-runs.out`):

```
$ git -C <rebuilt-c3_clean> show <recorded_rev>:PROVINCE.md
exit=128
fatal: path 'PROVINCE.md' exists on disk, but not in '<recorded_rev>'
$ git -C <rebuilt-c3_edited> show <recorded_rev>:PROVINCE.md
exit=128
fatal: path 'PROVINCE.md' exists on disk, but not in '<recorded_rev>'
```

A byte-preserving comparator must reject or fail evaluation of BOTH; making clean green requires a fallback to some revision after A, contrary to the frozen sentence. Minimal disambiguation cannot repair these frozen fixture bytes: the intended A must actually contain the original block (without a self-referential token), or the predicate must explicitly define a first-post-A recording rule. The latter changes the contract rather than merely explaining it. Report disagreement; do not silently adopt it.

### High — C3 mandated live bootstrap changes bytes that the predicate requires preserved

`plans/round-74-claims.md:152-159` simultaneously requires “byte-identical block text” / “any other byte” and instructs adding a token to the existing Round-73 block naming the pre-token base. The inspected actual diff of `PROVINCE.md:310` adds:

```
recorded at 868dd701bff531be6a36da742d3418f98818e5eb (round-74 freeze base; the v2 preservation leg compares the block text with this token sentence stripped).
```

This is a worktree-only edit at inspection; `git log 868dd701..master -- PROVINCE.md` was empty and status showed ` M PROVINCE.md`. The stripping exception exists in record prose, NOT in the frozen blockquote. Literal whole-block comparison must flag that live edit. An implementation stripping the token sentence passes this bootstrap but does not implement literal “any other byte.” Minimal clarification for a future explicitly acknowledged contract: “compare after removing only the recorded-at annotation; all other bytes are preserved.” It does not cure the absent-baseline fixture defect above. Do not let artifact prose amend the freeze.

### Medium — counting command does not enforce C1's numeric kill target

Frozen C1 requires `total=7 invisible=4` and each invisible capability (`claims.md:64-67`). `controls/score-survivors.py:84` accepts ANY exit-1 output containing `SELFDESC_CANON_V2_FINDING invisible`; its clean check at line 91 checks exit 0 only. A module reporting one finding, wrong total, or wrong/missing names can score `v2_killed=1 clean=True`. Exact numeric and name inspection remains necessary; the SURVIVORS summary is not equivalent to the frozen predicate. No frozen scorer was edited.

### Medium — C1 exit-map and fixture input types disagree

`claims.md:55-56` lists “not a git repository” as exit 2. Yet `build-survivors.py:132-144` builds both C1 fixtures as plain directories without git init. An implementation enforcing that exit-map cause cannot pass either fixture. The blockquote itself only needs readable SCORECARD bytes. Minimal non-widening resolution of the contradictory wording: explicitly permit plain-directory SCORECARD inputs and remove the unsupported git requirement in a future contract; this is a reported disagreement, not permission to change the freeze now.

## Predicate unambiguity: all three claims

- **C1:** “newest capability table” (singular, `claims.md:42`) versus cumulative `total=7` is ambiguous in isolation; the fixture's 3+2+2 distinct names and exact kill target disambiguate it for these inputs. Missing-bold-canon behavior remains unspecified: treating “newer than the newest bold canonical heading” as an empty population can green a demonstrated-only record even though r42 sees no canonical list. Minimal clarification: no bold heading means an empty bold-name set and all demonstrated tables participate. No missing-bold case exists in this battery. Also see plain-directory contradiction above.
- **C2:** the tip-clause (`claims.md:97-99`) requires header=tip; the explicit-revision clause (`100-102`) binds header=the named ancestor. A paragraph saying both “at the report tip” and “re-run at revision A” with header=A≠tip creates competing readings. The strict conjunction rejects it; an explicit-revision-overrides-tip implementation greens it and still passes all four frozen fixtures (none is hybrid). Minimal clarification: explicit revisions never waive a tip claim's header=tip requirement. Treat this as an uncovered interpretation risk, not an observed v2 implementation bug. Multiple explicit revisions in one paragraph also lack a citation-to-revision assignment rule.
- **C3:** see the two high findings. “block text” cannot simultaneously include all bytes and exclude the newly added annotation. No certification of unambiguity is possible.

## Control reachability — reproduced, no before-receipt mismatch

Read r42 canon/parser, r73 receipt-claim tool, its r72 base dependency, and r73 host-drift tool. The proposed r74 modules were absent during this review's replay, as expected for the before state.

All seven hashes matched `controls/freeze.txt`: plan, builder, scorer, probe, meta, and both before receipts. The four base tool files also matched their archived `868dd701` bytes (sha256s retained in `shortcut-runs.out`). Controls and receipts were introduced by `df18ad1e`, not present in the base archive; reproduction therefore uses pinned control bytes with byte-identical base tools, not a claim that the controls existed at base.

Commands exercised (all scratch paths under this seat):

```
git -C <lane> archive 868dd701bff531be6a36da742d3418f98818e5eb | tar -x -C <scratch>/base
python3 <lane>/.ufo/waves/round-74/controls/probe-canon-base.py --repo <scratch>/base
BASE_C1 canon_round=71 canon_rows=17
python3 <lane>/.ufo/waves/round-74/controls/probe-canon-base.py --repo <lane>
BASE_C1 canon_round=71 canon_rows=17
python3 <lane>/.ufo/waves/round-74/controls/build-survivors.py --work <scratch>/controls-work --meta <scratch>/my-meta.json
python3 <lane>/.ufo/waves/round-74/controls/score-survivors.py --meta <scratch>/my-meta.json
diff -u <lane>/.ufo/waves/round-74/measured/before/score-survivors-base.out <scratch>/my-score.out
RECEIPT_REPRODUCED_BYTE_IDENTICAL
```

The exact seven-line survivor output is retained in `before-replay.out`. Successful reproduction validates BEFORE observations only; it does not make the malformed C3 clean control valid.

## Kill-rule shortcut attempts — at least three per claim

Actual native outputs/commands are retained in `shortcut-runs.out`. No outputs were relabeled as v2.

| Claim | Shortcut attempted | Observed result and why it does not meet full target |
|---|---|---|
| C1 | unchanged base over invisible fixture | exit 0, round=71 rows=3; no v2 invisible finding |
| C1 | record-only bold74 covering all seven (clean fixture), base tool unchanged | exit 0, round=74 rows=7; achieves visibility by markup alone, not invisible-fixture kill |
| C1 | rebold ONLY demo74 as canonical74 in a scratch copy | exit 0, round=74 rows=2; newer heading alone does not recover seven-name repertoire |
| C2 | unchanged r73 over wrapped fixture | exit 0, claims=0; still misses required wrapped kill |
| C2 | unchanged r73 over offset fixture | exit 0, claims=0; still misses required offset kill |
| C2 | honest explicit-revision wording only, unchanged r73 over clean_realizable | exit 0, claims=0; achieves realizable cleanliness without v2 but cannot supply its bound_revisions count or kill either escape |
| C3 | unchanged r73 over date-edited fixture | exit 0, stale=0; date mutation invisible |
| C3 | unchanged r73 over clean fixture | exit 0, stale=0; green is not evidence of preservation (A lacks file) |
| C3 | remove recorded-at token in scratch alternate --file, keep date edit | exit 0, stale=0; absence of marker evades any preservation leg but cannot satisfy frozen tokenized fixture target |

Conclusion: none of these unchanged-base attempts meets the FULL frozen targets on the fixed kill populations. Record-only shortcuts can achieve individual clean/live outcomes, so those alone are not causal evidence of v2 work. Output-prefix-only scoring is weaker still (C1 finding above). No malicious surrogate tool was built.

## §9 sizing / one-command derivability

The frozen claims file contains no numbered §9; applying the assignment's sizing criterion to its actual after-states:

- C1 finite target: one kill + one clean, total=7 and invisible=4/0. One scorer command emits results, but does not enforce those numbers or names. Universal “every capability” is larger than its 7-name fixture. No-bold, duplicate-round, unbolded-canonical-only, and removed-capability populations are not exercised.
- C2 finite target: two kills + two cleans, including bound_revisions=1 for mixed hex. One scorer command derives those four outcomes. “Every paragraph” covers both self-record sources, but fixtures place operative claims only in SCORECARD. No stale-explicit-revision kill, uppercase header-key control, multi-revision/hybrid paragraph, or base-red composition control occurs in the frozen four-arm set. Do not equate 2/2 kills with universal correctness.
- C3 finite target: one edited kill + one clean (`edited=0`). One scorer command emits outcomes, but literal clean reachability fails because A lacks the file. “Every host-identity block” exceeds one-block fixtures; multiple old blocks, block deletion, token removal, and exact whitespace/encoding preservation are not counted. Removing a tokenized block entirely also removes it from a current-tip-only quantifier; the frozen predicate is not an append-only-history proof.

## Honesty pre-check / record edits

Both required edits are explicitly in scope: bold round74 list of 22 rows (`claims.md:67-68`) and Round-73 annotation (`158-159`). “Does not edit SCORECARD.md” (`74-75`) constrains the module, not the integrator's record commit. “Nothing on the host is written” (`175`) cannot mean no repository output, otherwise every module/report delivery contradicts it; it concerns host state.

At inspection SCORECARD still had bold71 (17 rows), unbolded canonical72 (19), demonstrated73 (3), and no bold74. The annotation was already present only in the worktree. These are observations, not claims that record edits were committed.

Forgotten dependent maintenance: adding a visible 22-row canon changes r42's derived Retired capability count, Saturation first-working-round facts and head Capabilities-table equality (r42 docstring lines 29-40). The plan excludes re-grading those arms from the module, but does not state whether the record will synchronize them. Inspect/update the standing facts as part of record maintenance or disclose them intentionally unchanged; do not assume adding the bold table makes the rest of self-description green. The source row/knowledge entry, mistakes lesson, calibration classification and assimilation receipts ARE named in the Frontier section, not omissions.

## Residual risk and verification gaps

LSP device unavailable: `read xd://lsp` returned “No such tool”; semantic references/definitions/diagnostics could not be requested. Findings rely on explicit source locations, actual diff and executed controls, not grep as semantic proof. No r74 implementation verdict is issued; modules were absent during replay. No base selftests were run by this reviewer. No canonical-runtime, rerouting, saturation, or resume path was changed or exercised; this plan-only assignment cannot certify those separate contracts. No tool installs/updates. No git mutation outside scratch fixtures; fixtures use pinned builder identity/toplevel assertions. Scratch is removed after preserving receipts.
