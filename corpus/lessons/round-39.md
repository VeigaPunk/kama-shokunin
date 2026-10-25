# kama round 39 lesson

author: kama L1
date: 2026-10-25
base: d7954be870a785054287ef5d7b3690e6cca0478e (attempt-1 base was 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea; the attempt-1 commits never reached the lane remote)

## Claims

C1 calibration 7 → 7: record one source-grounded assimilation admission and at least one non-fitting package-theme rejection with reason and flip. The frozen predicate, base control and after evidence are `.ufo/waves/round-39/assimilation/preregistration-frozen.json`, `c1-noop.out`, and `claim-after.out`. The counter is intentionally a minimum decision-count check; outside calibration remains pending a non-author admit/reject spot-check.

C2 coverage 9 → 9: add a round-39 coverage-map pointer and amendment on the specific `created`-field distinction, the amendment file must exist, and S473 must be absent at base and present at tip. The predicate measures pointer/file/source presence, not semantic novelty against existing corpus entries. Frozen predicate and controls: `.ufo/waves/round-39/assimilation/preregistration-frozen.json`, `c2-noop.out`, and `claim-after.out`.

Both score readings are held. The replay base `d7954be8` holds 213 source rows; the tip holds 214. No live endpoint was sampled.

## Gate

Selected one theme from the read-only `corpus-expansion-1` package: what a served model-card field establishes. The campaign package was opened under `/home/vgpnk/Projects/shokuknow/merge/kama/`; that source repository was not modified. The package's round-16 candidate carries a stale premise that the lane lacked the consumer reconciliation rule; the lane's `consumer-registry.md` and the base crosswalk already carry that material. The adopted text was therefore narrowed rather than copied: the only new distinction is the meaning of `created`, and its location in the existing crosswalk is made explicit.

Admit `corpus/knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md`. S473 was opened directly by this lane on 2026-10-25 at https://developers.openai.com/api/reference/resources/models/methods/list/index.md, Markdown `## List models` → `### Returns` → `created`, line 17. Located quote (10 words): “The Unix timestamp (in seconds) when the model was created.” The saved Markdown is 1,657 bytes, SHA-256 `2bbf06bb7a1687dbc9d25ce86c5d249b3f9d1e2c60efc32dbf7af2e4d052793f`; the sentence is also present in the 609,612-byte saved HTML rendition. This supports the creation-time meaning, not local endpoint identity, loaded weights, or readiness. The existing crosswalk already lists `created` in the OpenAI card row; the amendment adds the narrower field interpretation, not another API card or engine.

Reject staged `runtime-health-surface-matrix-amendment-2026-10-24-r16.md`: process ownership and health-route proposals are a different theme and not part of this card-field amendment. Flip: a later round selects the health-route/process theme and reopens its cited upstream and lane evidence. Reject staged `hosted-health-route-configuration.md`: remote platform container configuration is outside kama's local-serving province (PROVINCE.md:40-53; corpus/README.md:64). Flip: province assignment changes or an in-scope local platform surface is demonstrated. Both rejects remain unadopted.

### Id collision and append validation

Before append, attempt 1's 0–3-space extractor found 203 lane ids at base `6a4afdfe` and 142 staged ids (S330–S471); `comm -12` was empty, 0 collisions. The trap fixture used two indented `  | S471 |` rows and returned S471 (one collision), so the guard handles supported indentation. The lane remote then moved: `d7954be8` carries 213 registry rows, and round 38 already holds S472 for the SGLang release-tag inventory, so the adopted row's staged id collided at the replay base. Attempt 2 renumbered it to S473 — the next unused lane id — by document: the URL, anchor and quote are unchanged and the id follows the evidence, never arithmetic. Replay receipts `.ufo/waves/round-39/assimilation/{reg-ids-replay,staged-ids-replay,collisions-replay,renumber-map.md}`; the attempt-1 receipts keep their bytes.

S473 was transformed to the lane registry's 11-column shape, one row, `mined`, opened 2026-10-25, recheck 90d and `used-by` exactly the admitted amendment. A full lane-repository scratch mirror placed that row inside Registry and the amendment at its target path; `sources-census.sh validate --file .ufo/waves/round-39/assimilation/validate/corpus/SOURCES.md` exited 0 with 93 pre-existing W04 warnings and no E findings. Receipt: `validate.out`.

### Quarantine and consideration

The campaign absent-defect register slice has seven rows: S200, S202, S206, S210, S211, S224, S230. Round 36 already hand-checked each (`corpus/lessons/round-36.md` Gate rows 51–57): S200 absent; S202 present/not appended; S206 present/out of province; S210 absent; S211 absent; S224 quote not located; S230 present and covered by S329. No quarantine row is appended or edited.

Opened operator-authored `considerthese/2026-10-24.md`; proposal 2 asks to reopen source-row quotes at their anchors. This round re-opened the source used by S473 and located its quote at Markdown line 17. The reflection file was not edited. Proposal 1 was already recorded as KQ44; proposals 3 and 4 were not adopted.

Non-author admit/reject spot-check is pending. No author-dispatched seat is an outside verifier.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| source-schema | `.ufo/waves/round-39/assimilation/validate-partial.out` records E11 when only `corpus/SOURCES.md` and no repository-root `used-by` paths are mirrored; the exact error class is from `scripts/sources-census.sh` E11 | CORPUS.md §SOURCES census and `scripts/sources-census.sh` E11 contract | use a full repository mirror before append validation. The same validator is red on the partial mirror (exit 1, E11) and green on the full mirror (exit 0, 0 E findings; W04 warnings only); receipts `validate-partial.out` and `validate.out` |
| stale-premise | Staged r16 identity amendment repeats the package's old claim that no lane entry named the consumer reconciliation gap; `consumer-registry.md` and `served-identity-crosswalk.md` in the base already contain it | none — package prose was not checked against the base corpus before the staged entry was assembled | discard the repeated premise; retain only the `created`-field distinction and cite the source actually opened this round |
| unlanded-commit | Attempt 1 committed `eaa4106c` and `8e953f68` in the parked lane worktree on stale base `6a4afdfe` and filed a report citing both; `git ls-remote origin refs/heads/master` printed `d7954be8`, not those hashes, and the report was filed anyway | the lane's own pre-report gate (`kama-round-39.md` §4: the `ls-remote` MUST print the final lane hash) — it existed and was skipped | replay the content on the current tip in a scratch clone, land through `jj-lane.sh`, cite only the helper's `landed <hash>`, and file an erratum naming the unlanded hashes |
| id-collision | Staged id S472 is already held by round 38's own-work SGLang tag-inventory row at the replay base; attempt 1's `comm -12` ran against the stale base and found 0 collisions | the §10 id-collision check must run against the base the round lands on, not the worktree's base | renumber by document to S473 and re-point every live citation; replay receipts `reg-ids-replay`, `staged-ids-replay`, `collisions-replay`, `renumber-map.md` |

## Frontier

The crosswalk now distinguishes the OpenAI card's `created` catalog timestamp from local serving identity (S473). No endpoint/runtime sampled. The broad served-identity topic was already held; the round's specific field interpretation and coverage-pointer predicate are bounded as such. The considered proposal's source-reopening practice was applied to the new row.
