# MutationDesign — round 24

**Verdict: one bounded wrong-type mutant KILLED; exact scratch bytes restored.** The other three mutation classes below are proposals, **unrun/unverified**. This is mutation-design advice and a base-control sensitivity measurement, not a verdict on the round-24 candidate or its complete grid.

## Axes and scope

- **Calibration:** C1 remains the preregistered 7→7 claim; distinguish a justified substantive verdict from unavailable evidence, and a detector failure from a killed mutant.
- **Operability:** complete local repositories must retain clean/omission verdicts despite promisor metadata; unavailable required evidence must not become a guessed verdict.
- **Coverage/no-harm constraint:** exercise both audited repositories, local cross-repository resolution, and known object types without weakening Git isolation. No score increase or broader hardening is claimed.

Read `.ufo/waves/round-24/preregistration.json` first. Its lines 7–12 define the substantive outcomes; lines 15–16 define a fixed history-derived oracle and planned grid. Own scratch was created with:

```text
git clone --no-hardlinks --quiet /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r24/MutationDesign
git -C /fast/scratch/hyaku/kama-r24/MutationDesign rev-parse HEAD
# observed: 0df800e896f6bce285a81e794ad4ae1d1e6c3a71
```

Only this scratch auditor was mutated, then restored. Lane production sources, Git index, `.jj`, siblings, fleet files and operator settings were not edited. Synthetic fixture histories were constructed by offline Git object plumbing in `probe-wrongtype/` inside the scratch clone; no transport URLs, hooks or executable payloads were installed. No full tests, selftest, historical grid, candidate grid, transport checks or other runtime were run.

At inspection, `tests/report-audit/` contained `repo-state-grid.py` and `isolation-mutants.py`; the preregistered `promisor-grid.py` was absent. Therefore no claim below asserts that the new grid already implements or kills these proposals. MutationOracle supplied its intended interface: `promisor-grid.py --arm current --current <auditor> --json`, with detector exits 0 expectations met / 1 graded expectation violated / 2 could-not-evaluate.

## Expected outcomes to freeze before candidate execution

| Fixture premise | Expected audit outcome |
|---|---|
| Required history, trees, source/report blobs and valid citations locally available; complete full clone versus otherwise identical promisor-marked lane or fleet | Same substantive result: clean exit 0 with no defects, or exit 1 with the same genuine `landed-omitted` finding. Metadata alone must not produce exit 2. |
| Required commit/tree/source blob/committed report blob unavailable locally | Exit 2 with evidence of that unavailable required object, not clean/failed. Do not use a missing unrelated blob as a substitute for a missing required blob. |
| Citation absent from both audited repositories; at least one is promisor-backed | Exit 2, not `unresolved-full-hash`/`landed-unresolved` as proved absence. |
| Citation missing from the first, promisor-backed repository but locally available as a commit in the other audited repository | Continue resolution and return the otherwise justified clean/omission outcome, not premature exit 2. |
| A full-40 Landed citation is locally available as a **blob**, while every actual required round commit is cited | Exit 1 with `landed-unresolved` for the blob; no `unresolved-full-hash`, because the object itself exists. A failed `^{commit}` peel alone is not proof of unavailable evidence. Use full-40 IDs to avoid adding short-prefix ambiguity to this type test. |

The last two rows follow from preregistration lines 7 and 10 together with the existing lookup/type contract at the restored base auditor lines 139–174 and 335–342. They are not permission to relax missing-object uncertainty.

## Minimal semantic mutation proposals

All source locations here refer to the **restored base snapshot** `/fast/scratch/hyaku/kama-r24/MutationDesign/tools/report-landing-audit.py`, not unobserved candidate line numbers. Remap each proposal to its actual behavior-bearing point once the repair lands; do not force a stale replacement pattern to match.

| Class | Smallest behavior-bearing change | Intended bounded detector and attribution |
|---|---|---|
| **Over-refusal** | Reintroduce one `raise EvalError` on a positive promisor-metadata predicate, equivalent to the frozen refusal at lines 454–465. Do not change Git flags. | Complete paired lane/fleet fixtures: metadata-off clean 0 / metadata-on clean 0; genuine pre-cutoff omission remains 1 with the same `landed-omitted` token in both. A metadata-on 2 is a violated expectation only after pristine repaired candidate passes. The r23 base already over-refuses: its failure is the known baseline, **not a killed over-refusal mutant**. **Unrun.** |
| **Missing required evidence accepted** | At current line 268, replace `text = git(lane_repo, "cat-file", "blob", fields[2])` with `text = ""` to treat the required SOURCES blob as absent legacy content. If the repaired candidate has a separate required-closure refusal, MutationOracle should instead weaken that single refusal at its actual source point, rather than suppress the generic Git error wrapper. | Keep the committed SOURCES tree entry but remove its object locally; keep refs, commits, trees, report and citations otherwise valid. Expect audit 2 with a source-blob premise proved independently. Mutation returning a substantive 0/1 violates the row. If a second required-evidence guard still refuses correctly, this specific bypass survives due to that remaining guard; do not invent a kill or weaken the contract. **Unrun.** |
| **Premature unknown rejection** | Change the missing-result `continue` at lines 159–160 to an immediate `raise EvalError` before searching the next repository. In a repaired implementation the equivalent defect is moving the promisor-unknown decision inside the per-repository loop instead of after aggregation. | First repository promisor-backed and missing a full-40 token; second repository locally contains the cited commit. With all round commits cited, expect 0 / no defects. Early 2 violates this row. Pair it with absent-in-both → 2 so that merely deleting uncertainty handling cannot pass. **Unrun.** |
| **Wrongtype misclassification** | Remove only `^{commit}` at line 337: `lookup(..., "^{commit}")` → `lookup(..., "")`. This accepts any locally present object as a Landed commit. | Full-40 local blob under Landed plus the actual required commit. Expected 1 / exactly `landed-unresolved` for the blob. Observed mutant 0 / no defects. **Executed and killed below.** A separate unrun failure shape worth preserving in the repaired grid is reporting this known local wrong type as unknown/2 merely because the commit peel says `missing`. |

Coordinate complete-metadata rows with GridOracle's actual case IDs; this slice does not invent IDs for its unpublished grid. MutationOracle was told the known-local-blob distinction and the optional additional wrongtype mutant.

## One executed probe: M-WRONGTYPE-ACCEPT

**Mutant:** one literal argument change at base auditor line 337; exact fault patch retained as `build/out/MutationDesign/M-WRONGTYPE-ACCEPT.fault.patch`. This is deliberately defective code, **not a candidate production repair**.

**Fixture:** one non-promisor lane/fleet pair, all local. Lane commit `2559a6d1421bf6e0c98d26589ced20f947f4ed06` is authored by `kama-shokunin` at time 1000. Fleet report commit `4654ebba3d602981ea2c057ec26d8644d39e371e` is time 2000 and cites that commit plus blob `4547589ed0b83b19f013d94823c9be43811f42d6` under Landed. The detector independently checks the two commits' types and the blob's type with `git --no-lazy-fetch --no-replace-objects ... cat-file -t`; each stage observed the same local types.

**Exact same command used on pristine, mutated and restored bytes:**

```text
/usr/bin/python /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/MutationDesign/wrongtype-detector.py /fast/scratch/hyaku/kama-r24/MutationDesign/tools/report-landing-audit.py /fast/scratch/hyaku/kama-r24/MutationDesign/probe-wrongtype
```

The detector invokes the auditor with `--branch master --lane kama --rounds 1 --no-errata --json`, the fixture's absolute `--lane-repo`/`--fleet-repo`, and a 25-second outer audit deadline. Its exact argv and raw stdout/stderr are retained in each stage artifact.

| Bytes | Detector exit | Audit exit | Exact finding | Result |
|---|---:|---:|---|---|
| Pristine | 0 | 1 | `landed-unresolved:4547589ed0b83b19f013d94823c9be43811f42d6` | Expected behavior established |
| Mutated | 1 | 0 | none | Substantive mismatch: killed |
| Restored | 0 | 1 | `landed-unresolved:4547589ed0b83b19f013d94823c9be43811f42d6` | Expected behavior recovered |

No stage reported detector/auditor stderr. `probe-summary.json:14–48` records the actual rows; lines 9–10 record exact restoration and unchanged fixture-manifest identity.

### Before/after SHA-256

```text
pristine auditor: da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1
mutated auditor:  bfc516217f4b44c255d186b51b54bd8dd54d4826f99e4599dfc700d200668736
restored auditor: da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1
fixture manifest (all stages): daaf92fda79638896bc9555fe4e2f1d9d60e65253f906d0608fd7c31bc1352e9
```

The source edit was explicitly reversed immediately after the mutated measurement. The restored detector invocation proves behavioral recovery on the same fixture; the identical complete-file digest proves restoration, not merely a return to similar output. The unchanged source isolation constants at base lines 93–96 and timeout at line 108 were not mutation targets.

## Detector errors are not kills

- Require pristine detector exit 0 before counting any mutant; expected auditor exit 1 or 2 is not itself a detector failure.
- A **detector** exit 2, fixture-premise failure, missing/duplicate replacement match, timeout, malformed output or unrelated inability to run is **inconclusive**, never a killed mutant. The bounded detector implements this separation at `wrongtype-detector.py:23–60,73–79`.
- Count a kill only for a confirmed semantic mismatch on the intended row with the fixture premise intact. This probe changed a valid typed lookup into a valid type-blind lookup, not a syntax/startup failure.
- Restoration must preserve the complete-file digest and recover the pristine result. A surviving mutant is evidence to examine coverage or remaining independent guards, not authority to change expected outcomes.
- Do not infer round-24 candidate sensitivity from this base-only control.

## Historical expectation review — not executed

The frozen `tests/report-audit/repo-state-grid.py:630–708` currently declares:

- `F06-lazy-fetch-command`: exit 2 remains appropriate for its absent citation plus promisor metadata, but the old reason requirement `partial clone` at line 697 must not be used to force blanket metadata refusal back into the repair.
- `F23-promisor-pack-without-config`: exit 2 remains appropriate because its cited blob is actually missing (`195–212`); use missing-evidence/uncertainty justification rather than refusing every paired pack marker. Its old reason literal at line 704 is not the repaired policy.
- `F27-filter-only-promisor-remote`: the old exit 1 / `landed-unresolved` + `unresolved-full-hash` expectation at lines 674–675 conflicts with preregistered unknown-citation semantics. The repaired expectation is exit 2 while the citation remains absent locally; document this as a policy-row expectation change, not regression or kill.
- `C09-promisor-false-config` and `C10-orphan-promisor-marker` remain clean controls at lines 679–680. Non-promisor substantive outcomes remain frozen.

The old F06/F27 builders execute configured SSH-command payloads to establish their premises (`272–287,482–498`), and F23/T01 builders perform `file://` transports. They were **not run** by this slice. The new offline grid must establish metadata/object availability premises directly without reusing those transport/payload setup steps. Removing `--no-lazy-fetch`, `--no-replace-objects`, log/signature suppression or timeout is outside these executable semantic probes; static preservation can be reviewed without executing transports.

## Named artifacts

All persistent artifacts below are under `.ufo/waves/round-24/build/out/MutationDesign/`:

- `wrongtype-detector.py` — fixed bounded detector, no suite dispatch.
- `fixture-setup.json` — offline Git-plumbing command observations, object IDs and committed report text.
- `M-WRONGTYPE-ACCEPT.fault.patch` — exact one-point defect, not production code.
- `probe-pristine.json`, `probe-mutated.json`, `probe-restored.json` — full detector outputs and exit codes, including raw auditor stdout/stderr and local object-type probes.
- `probe-summary.json` — stage results, command, hashes, restoration evidence and scoped verdict.

Observed tools: Git **2.56.0**, Python **3.14.8**. **No installs or updates.** No production candidate patch was authored by this design slice. Broader candidate/grid/selftest/historical-parity results remain **unverified here** and belong to L1's assigned integration measurement.
