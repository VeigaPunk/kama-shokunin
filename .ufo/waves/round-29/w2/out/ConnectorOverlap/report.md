# ConnectorOverlap — round 29, attempt 2, wave 2

## Axes and scope

**Assigned axes: calibration + operability.** Proposed benefit is more accurate calibration/novelty attribution; operability must remain unchanged. This is an advisory evidence-and-proposal report, not an admission, ownership ruling, integration, or endpoint-health result.

Read-only scan of the four requested sibling repositories for `blame`, `writing revision`, and `self-assessment`, followed by inspection of matching implementations and province declarations. Only this seat's permitted output directory is written. No sibling instrument, counter, self-test, endpoint, service, package manager, alternate runtime, or dispatch was invoked. No tools were installed or updated.

## Evidence

Observed `git -C <absolute lane path> rev-parse HEAD` results:

| Repository | Observed commit |
|---|---|
| `/home/vgpnk/Projects/shokunin/tsukuroi-shokunin` | `cefe752d9facf74113bb00a5925e3bfd0c863659` |
| `/home/vgpnk/Projects/shokunin/kaidoku-shokunin` | `f432c8e3bc58934887c83f1db2b26f9910a9d87f` |
| `/home/vgpnk/Projects/shokunin/kake-shokunin` | `5949e66ffe803859372adc975dd7392f0f07d626` |
| `/home/vgpnk/Projects/shokunin/kotoba-shokunin` | `79cf263800552812ce6a45f4bb0313668b576749` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin` | `513eba3ba51a142c9936553e3a85918345eb5c4c` |

For the sibling implementations and province files below, `git ls-tree <listed commit> -- <paths>` and read-only `git hash-object <paths>` returned matching blob identities. This binds the inspected working-tree bytes to those commits without assuming the whole repositories are clean.

### 1. Non-obvious exact mechanism overlap: kaidoku already compares timestamps with their lines' writing commits

`/home/vgpnk/Projects/shokunin/kaidoku-shokunin/.ufo/waves/round-20/tools/evidence-timestamps.py`:

- Lines 2–11 explicitly describe timestamps later than the commit introducing a line and Git-object reads using `git blame --porcelain`.
- Lines 129–163 parse each line's blamed commit and `committer-time`.
- Lines 188–229 enumerate tracked text at the selected revision, blame each path, then test `timestamp > committer_time`.
- Lines 251–257 describe the rule as zoned timestamp occurrences later than their line's introducing committer time.
- Lines 59–114 allow repository-relative file/directory scopes; the mechanism is not restricted to one hard-coded report filename. Its documented lane use is evidence-tree timestamp linting, not kama's frozen SCORECARD/SHONEN correction task.

Immutable blob: `be0452eb44294d69d121d04ab571cf0252f2d8c2`.

Executed command:

```text
git -C /home/vgpnk/Projects/shokunin/kaidoku-shokunin log --format='%H %cI %s' -- .ufo/waves/round-20/tools/evidence-timestamps.py
```

Output excerpts:

```text
a65bb98deb327afd38207518adfa9c2e4ed5eba9 2026-10-21T04:44:23-03:00 round-20: integrate wave-2 (71 reports), wave outcomes/causes, D5/D6d/D6e/D2 fixes, S048 provenance, registry/QUALITY corrections
808cbb31a1e24656da5ba4967497e602fbca7415 2026-10-20T18:01:54-03:00 round-20: integrate W1 tools and routed-defect fixes; freeze C3 v2 first-failure predictions (19 go1.24.6 labels, link excluded); arm carrier guards; C2 run evidence
```

Both precede kama's supplied freeze `827d136546b85059a984b34970f5b493d9a71290` on October 23. This is substantive prior overlap with kama **T**, not a full six-class C1 duplicate. Kaidoku recognizes a different timestamp grammar and has allowance machinery; kama's frozen counter has its own grammar and rules.

### 2. Other sibling comparisons are adjacent, not interchangeable with C1

| Sibling | Inspected implementation / claim | Comparison with kama C1 |
|---|---|---|
| tsukuroi | `/home/vgpnk/Projects/shokunin/tsukuroi-shokunin/tools/check-self-assessment.py:2-46,434-443` — K01–K27, SCORECARD/SHONEN and other inputs read at one requested revision. Blob `ac28365ff10e8a8c91747bf6b08d3df1a5b3b5aa`. | Same self-assessment surfaces, but selected-revision consistency rather than assigning W independently to each base line. Its dated-outcome selection is not Git writing-revision attribution. |
| kaidoku | `/home/vgpnk/Projects/shokunin/kaidoku-shokunin/tools/round-25/a2/c1-calibration.py:2-10,42-53` and `/home/vgpnk/Projects/shokunin/kaidoku-shokunin/tools/round-26/c2-calibration.py:4-35`. Blobs `dbca8aaa7a6f91acd67961f38f05bbe9547b2588` and `0e2b3043ab3bc0e7f5a9a9af5805b46f59422948`. | Five/six fixed self-assessment obligations at REV, including named historical measurement commits; no per-line W selection. Separately, current `/home/vgpnk/Projects/shokunin/kaidoku-shokunin/SCORECARD.md:1009` records a historical R1–R4 audit at cited commits: historical assessment auditing is not novel fleet-wide. |
| kake | `/home/vgpnk/Projects/shokunin/kake-shokunin/scripts/receipt_replay.py:2-28` and `/home/vgpnk/Projects/shokunin/kake-shokunin/scripts/citing_set.py:2-15`. Blobs `b9196b19a68f5659083e89bc6636c633da7ad61a` and `e18cb0da847d92587c406b0e0b58c87e811cf20d`. | Receipt timestamps are bounded by selected REV's committer time, not their own lines' W; citation-pair completeness explicitly does not establish statement truth. No requested-keyword matches were returned from kake's scripts in the bounded implementation sweep. |
| kotoba | `/home/vgpnk/Projects/shokunin/kotoba-shokunin/verifiers/check_correction_sweep.py:2-18,31-37` and `/home/vgpnk/Projects/shokunin/kotoba-shokunin/verifiers/check_gate_finding_delta.py:2-21`. Blobs `c94b771fa7d798ef45fc3bb640422ee7910f81a6` and `be7bdae091f62c3dacdbb42cc3d2901c5fc02e0a`. | One checks fixed supersession wording; the other compares findings from each revision's own gate. Neither is the frozen six-class, per-line-W comparator. The only requested-keyword implementation hits in kotoba's verifiers were ordinary English “does not blame the revision” test labels, not Git blame calls. |

No identical full P/H/N/C/T/Q plus SA29 append-only correction instrument was found in this bounded scan. That is not a proof of fleet-wide absence.

## Contradictions and contested scope

1. **Literal-command absence does not establish absence of the technique.** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ConnectorSiblings/overlap.md:14-18,44-48` searches especially for `line-porcelain`; kaidoku uses `--porcelain` in a cached tool outside the root `tools/` directory. Its T-equivalent comparator is therefore omitted from that account. The narrow observation “no identical six-class instrument found” can coexist with this prior art; any stronger inference “writing-revision checking is unique to kama” conflicts with the implementation evidence above.
2. **Tool overlap is not province ownership.** `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-29.md:59-63` says no sibling province owns writing-revision checks and “No contested scope.” The reviewed declarations do not assign a general historical-auditing province to these siblings, but that does not erase technique overlap or authorize kama to take fleet-wide checker ownership.
3. **The actual corrected cohort is narrower than the comparator design.** `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:1477-1493` identifies four P and seven Q failures, explicitly not eleven proven-wrong historical judgments. Thus kaidoku's T overlap does not duplicate the eleven corrections or contradict the inherited C1 receipt. No claim regrade is made here.

Scope evidence:

- `/home/vgpnk/Projects/shokunin/kama-shokunin/PROVINCE.md:3-15,40-53` retains local serving/endpoint health and report-only out-of-province handoffs.
- `/home/vgpnk/Projects/shokunin/tsukuroi-shokunin/PROVINCE.md:3-4,25-28,41-52` retains host state, explicitly sends endpoint health to kama, and says shared evidence is not shared ownership. Its kaidoku/revenger RE dispute remains unresolved and is not triggered by this documentary calibration check.
- `/home/vgpnk/Projects/shokunin/kaidoku-shokunin/PROVINCE.md:3-6,64-71` concerns shipped-artifact RE and rejects treating its live surface map as another lane's current capability.
- `/home/vgpnk/Projects/shokunin/kake-shokunin/PROVINCE.md:3-6,32-41` explicitly splits remote web properties from kama's local endpoints.
- `/home/vgpnk/Projects/shokunin/kotoba-shokunin/PROVINCE.md:3-17,34-54` retains prompt/skill craft; its kama row preserves instruction wording versus independent endpoint verification. `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/cross-lane-scope.md:29,49-51` states the same boundary.

No direct C1-specific ownership dispute is evidenced among these four declarations. A proposed general fleet auditor or an audit of sibling-owned instruction semantics would raise a different, unresolved scope question; this report does not settle it.

## One bounded proposed move

**Have L1 append one scope-and-prior-art note to the existing round-29 lesson, explicitly superseding only an overbroad reading of its sibling-scan sentence.** Do not add a checker, new claim, capability, province surface, or sibling dependency. Suggested content:

> The sibling scan found no identical six-class/SA29 correction instrument, not a novel writing-revision technique. Kaidoku's round-20 `evidence-timestamps.py` already compares zoned timestamps with their lines' blamed committer times (partial overlap with T); tsukuroi and kaidoku also have selected-revision self-assessment checkers. C1's measured move is kama's own frozen self-assessment evidence correction: four P and seven Q acknowledgements under the unchanged predicate. It neither transfers generic auditing/instruction ownership nor measures current endpoint health.

### Second-order effects and risks

- **Calibration:** [INFERENCE] the note improves attribution by distinguishing prior technique, selected-REV checks, per-line W, and the actual corrected P/Q cohort. It avoids silently converting “missing retained evidence” into “wrong historical judgment.” No numeric uplift is proposed.
- **Operability/runtime:** text-only proposal; no probe, consumer, serving tool, registry, endpoint, unit, or route changes. A corrected evidence record remains no evidence of a restored/healthy endpoint. No operational improvement is claimed.
- **Contract:** keep base `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`, freeze, controls, data commit, predicate, classes, and target unchanged. Treat this as narrative scope correction, not retrospective respecification or independent admission.
- **Substrate:** cite immutable sibling blobs; do not run or import either sibling's checker into C1. In particular, kotoba's per-revision-own-gate comparison is not a replacement for kama's one frozen counter. No environment-hardening changes are proposed.
- **Verification risk:** lexical search misses synonyms and unusual storage locations; the discovered `--porcelain`/cached-tool case demonstrates why a universal “none exists” claim is unsafe. Conversely, the shared T primitive does not justify calling the entire C1 duplicate. Future timestamps can also be planned deadlines, as kaidoku's own `/home/vgpnk/Projects/shokunin/kaidoku-shokunin/SCORECARD.md:3297` records; this observation is a limit, not permission to amend kama's frozen rule.

## Verification performed / integrator checks

Performed: specialized read/grep/glob source inspection, read-only commit identity and path-history commands, and matching `ls-tree`/`hash-object` bindings for the cited sibling implementation/province files. No build, lint, formatter, test, mutation, counter, or live endpoint check ran.

Read, not rerun: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/final/c1-513eba3b-cleanenv.out:1-2` reports:

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 513eba3ba51a
```

This is inherited evidence, not this seat's execution. The canonical assignment supplies the independent attempt-2 re-verification.

For the proposed note, L1 should review that it cites the timestamp prior art, narrows rather than expands the scope, preserves the eleven correction rows and all frozen inputs, and adds no runtime/health assertion. No repeat of the already re-verified C1 measurement is needed merely to reconfirm the supplied observation.

## Output-bound conflict

The requested trailer destination `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/ConnectorOverlap.md` is outside the explicitly hard, seat-only write scope. It was not written. The complete report is instead at the authorized `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/ConnectorOverlap/report.md`; L1 alone can publish it to the trailer destination.
