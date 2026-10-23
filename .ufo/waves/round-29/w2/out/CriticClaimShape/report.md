# CriticClaimShape — round 29, attempt 2

Advisory adversarial review only. This is not a canonical judgment, admission, or whole-round verification. No counter, test suite, server, or judging runtime was executed. No lane source, frozen artifact, Git index, or jj state was changed.

## Axes

- **Calibration:** primary claim; distinguish honest acknowledgment of an evidence gap from declaring a historically correct judgment false.
- **Operability:** supporting reproducibility, not an additional claim earned by this review.
- **Freshness:** checking the writing revision avoids confusing later drift with a defect present at writing.
- **Depth, coverage, adjacency:** no movement established here. A zero over the extractor's bounded population establishes neither complete semantic coverage nor saturation.

Authority examined: `/home/vgpnk/Projects/shokunin/.ufo/prompts/kama-round-29.md:9-23,157-172,350-372` and `/home/vgpnk/Projects/kimi-shokunin/skills/shokunin/protocol/AXES.md:9-38`. Artifact commentary was treated as evidence, not as authority to change the assignment or predicate.

## Strongest rejection case: the detector can call a correct self-assessment false

This is stronger than objecting to one claim, inherited work, or automated transcription.

The inherited final receipt `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/final/c1-513eba3b-cleanenv.json:55-63` flags SCORECARD line 740, `round-17-verifier-spotcheck.md:217–221`, as `p:absent` at writing revision `c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d`. I independently inspected that committed revision with:

```sh
git --no-replace-objects -C /home/vgpnk/Projects/shokunin/kama-shokunin grep --threads=1 -n -B 1 -A 4 -F -e '**discernment: improved**' -e 'Round-17 outside review admitted' c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d -- SCORECARD.md corpus/lessons/round-17-verifier-spotcheck.md
```

Observed excerpts:

```text
SCORECARD.md:739:Round-17 outside review admitted the two bounded claims and judged **discernment
SCORECARD.md-740-improved** (`round-17-verifier-spotcheck.md:217–221`), superseding the pending
corpus/lessons/round-17-verifier-spotcheck.md:217:- **discernment: improved** (this closure's outside judgment; the lane wrote `unchanged`
```

The substantive assessment agrees with its intended source at W. What fails is a literal repository-root lookup of a shortened filename. That is a real citation-resolution defect, not a demonstrated wrong discernment verdict.

A second independently checked counterexample concerns false provenance in the correction explanation. At data commit `513eba3ba51a142c9936553e3a85918345eb5c4c`, the appended row for `RESULT pass=24 fail=0` says that no committed file held it at W. The counter nevertheless excludes LOG and corpus by design. This read-only command:

```sh
git -C /home/vgpnk/Projects/shokunin/kama-shokunin grep -n -F -e 'RESULT pass=24 fail=0' ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21 -- LOG.md corpus
```

returned the exact span in `LOG.md:142,215,242`, `corpus/knowledge/snapshot-history.md:66`, and `corpus/lessons/round-2.md:49`. Another executed Git query found `rows=50 resolved=48 terminal=2 unresolved=0` at `40660352d4a9eb00a5d6195f0f064f5c64618143:corpus/lessons/round-10.md:148`.

Thus `q:no-artifact` does not mean no committed occurrence exists, and certainly does not prove the reported numerical outcome was wrong. It means no verbatim occurrence was found in the permitted search universe. The inherited correction table's broader wording is false for these examples.

The source of the category distinction is inspectable at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py:232-264`: P checks literal path existence/bounds; Q searches for a string while excluding SCORECARD, SHONEN, LOG and corpus. All eleven flagged items in the final receipt are four P and seven Q items; no H/N/C/T contradiction contributes to that eleven.

**Impacted axes:** falsely retracting the supported historical assessment would harm calibration. Honest evidence-gap disclosure can improve calibration without that harm. Changing the target after seeing this objection would also compromise the frozen claim's identity.

## Standing-feedback checks

### (a) ONE concrete after-value, ONE command over committed bytes

**Survives as `unresolved = 0`, not as a bundle of universal correctness assertions.** The frozen preregistration names `unresolved` and the target `mismatched_at_base >= 1 and unresolved == 0` at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/preregistration.json:14-24`. The counter computes that value at lines 297-341; the additional printed counts explain validity rather than requiring separate after-states.

A single audit invocation, from a fresh full clone containing the measured commit and the frozen script, is:

```sh
/usr/bin/python3 .ufo/waves/round-29/count-c1.py --repo . --tip 513eba3ba51a142c9936553e3a85918345eb5c4c
```

This exact invocation was **not executed by this critic**. Pinning the measured commit makes the historical result stable as a reference; the prescribed live-tip form uses `--tip refs/heads/master` in the fresh clone. Explicit `--repo .` matters: the frozen default otherwise names the original lane checkout, not the clone (`count-c1.py:284-285`). No `--out` is needed to obtain the counter line.

The opened inherited clean-environment receipt reads:

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 513eba3ba51a
```

Evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/final/c1-513eba3b-cleanenv.out:1-2`. Its fresh-clone provenance is inherited evidence, not a run by this seat.

I independently read the committed data diff: `git show 513eba3ba51a142c9936553e3a85918345eb5c4c -- SCORECARD.md SHONEN.md` showed 23 SCORECARD additions, including eleven correction rows, and no SHONEN change in that commit. `git ls-tree` at freeze `827d136546b85059a984b34970f5b493d9a71290` and data `513eba3ba51a142c9936553e3a85918345eb5c4c` returned the same counter blob `4adc6dfebd37b31de8fbf0e4362449728f4ca94d` and preregistration blob `5e4b49a7ba5c99577f55514e474efd3d7a5d0037`. SHA-256 of the counter read directly from the freeze object was:

```text
fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383
```

The numerical after-state does not depend on landing the inherited narrative edits first.

### (b) Calibration counts mismatches rather than asserting them

**Mechanically yes; semantically bounded.** The counter obtains statements from frozen SCORECARD/SHONEN bytes, blames each source line to W, checks the class against committed state at W, and counts failing IDs. It then separately counts unresolved failures and bad correction rows. The count is not obtained from an author's scalar calibration score or a prose declaration of success.

However, the after-state is **unacknowledged recognizer failures 11 → 0**, not historical false judgments 11 → 0. `mismatched_at_base` remains eleven. Neither `met True` nor RefPaste can make the semantic counterexample disappear.

The inherited narrative already supplies the narrower reading at `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:1477-1493`: evidence did not resolve under the frozen checks; this does not show past judgments were wrong; the two Q causes are qualified for the exclusions. `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/self-assessment-at-writing.md:24-33` makes the same distinction. These are current inherited working-tree text, not additional committed evidence at data commit 513eba3b.

### (c) A do-nothing control cannot reach the target

**Survives for the frozen before-state.** I read the actual committed baseline and control outputs, without executing the counter:

```sh
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 827d136546b85059a984b34970f5b493d9a71290:.ufo/waves/round-29/before/c1-base.out
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 35b90184f638ab6a4149092b93143c7a2b873787:.ufo/waves/round-29/controls/CtlDoNothing/counter.out
```

Both report `valid_corrections 0 false_corrections 0 unresolved 11 met False`; their tips are respectively base `2aa46e2481d2` and freeze `827d136546b8`. The base receipt was already carried by the freeze commit, so a null baseline is not first supplied after the correction data. The separate fourteen-seat control/reference batch was after the freeze and before data; it should not be described as fourteen failed seats, since RefPaste is included and passes.

RefPaste's passing receipt at reference-clone commit `a59f90ec1d7077a482ada768be8cb7d976b96a71` is not a do-nothing pass. The frozen preregistration, before scoring, expressly declares running the check and recording its observed values as the work (`preregistration.json:13`). RefPaste performs exactly that operation. Evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/RefPaste/REPORT.md:13-30,65-99` and its `receipt.json:119-124`. This answers the skipped-work objection, not the independent semantic axis-fit objection.

The broader control outcomes are inherited evidence at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/SUMMARY.md:14-43`; this critic did not rerun them.

### (d) One inherited claim versus “prefer 2”

**Not a fatal violation.** The governing prompt explicitly permits 1–3 claims (`kama-round-29.md:9-19`) and says “Prefer 2” (`:357`), not “at least 2.” Canonical AXES likewise permits 1–3 (`AXES.md:25-38`). Adding a second claim solely to satisfy a preference would not repair C1's semantic limitations.

The attempt-2 prompt expressly permits reuse of re-verified same-round inherited work (`kama-round-29.md:157-172`). Read-only Git history identifies the sequential round-29 freeze `827d136546b85059a984b34970f5b493d9a71290`, controls `35b90184f638ab6a4149092b93143c7a2b873787`, and data `513eba3ba51a142c9936553e3a85918345eb5c4c`, following the round-28 closure base `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`. Their predating attempt 2 does not turn them into a different round or invalidate reuse. It does prohibit representing them as newly frozen or newly measured by this critic.

## Advisory conclusion and smallest safe correction

**C1 survives the claim-shape objections as the frozen, bounded acknowledgment of self-assessment evidence gaps. It does not survive the stronger description “eleven historically false self-assessment judgments were corrected.”** The supported historical verdict counterexample refutes that description. The standing operator feedback does not require a second claim, fresh attempt-2 authorship, or manual transcription; it does require retaining the distinction between the computed receipt and what it actually establishes.

Smallest safe correction for the integrator:

1. Preserve the frozen counter, predicate, target, base and eleven counted rows. Do not refreeze or add newly discovered semantic errors to this claim.
2. Land an explicit explanatory erratum with the existing evidence-gap qualification: the count records unresolved frozen-check failures, P failures are literal lookup failures, and Q failures are absence from the allowed search universe. Correct the broad “false judgment”/“no committed file” reading without retracting the agreeing outside verdict or presenting the erratum as a changed target.
3. State one after-value, `unresolved = 0`, with the full measured commit and an explicit clone `--repo` argument. Report the other counts as diagnostics and report inherited versus new evidence honestly.
4. Do not infer exhaustive self-assessment correctness, score promotion, or saturation from the bounded zero. If the operator requires actual incorrect-judgment counts rather than honest evidence-gap acknowledgment for this calibration claim, the evidence here does not satisfy that stronger requirement; a passing receipt cannot overrule it or be relabeled into satisfaction after data.

The overbroad explanation and command ambiguity are fixable reporting defects. Trading a truthful historical verdict for a detector-approved false retraction is not a harmless tradeoff; it must not be accepted. Admission and all final axis/trend judgments remain outside this critic's authority.

## Execution and delivery bounds

Only read-only Git inspection, source/receipt reads, searches, and SHA-256 computation were exercised. No tools were installed or updated. No tests, counter reruns, services, model calls, or other judging runtime were started.

The assignment's hard write bounds permit only this seat's output directory, conflicting with the requested trailer destination `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/CriticClaimShape.md`. That outside-directory path was not written. Full report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/CriticClaimShape/report.md`.
