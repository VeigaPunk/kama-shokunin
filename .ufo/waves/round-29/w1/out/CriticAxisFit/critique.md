# C1 axis-fit critique — CriticAxisFit

Advisory adversarial review only: no judgment, admission, integration, counter execution, or correction data rows. The frozen claim, not control-report commentary, supplies the predicate.

## Axes and contract

- **Calibration:** the primary claimed axis. A self-assessment contradicted by the relevant observed state is a calibration mismatch; naming its uncertainty can improve calibration without increasing a numeric score.
- **Freshness:** a statement true when measured but later stale belongs here. Checking a writing revision avoids one drift confound, but does not establish that the extracted proposition is the self-assessment or that its failure proves overreach.
- **Depth / operability:** resolving evidence pointers and making an audit runnable can improve traceability or executable verification without establishing a calibration move.
- **Coverage / adjacency:** no new serving-domain surface or cross-domain ownership move is demonstrated by this counter. Checking more old strings is not, by itself, expansion.

Authority: `/home/vgpnk/Projects/shokunin/AXES.md:9-16,27-38`; `/home/vgpnk/Projects/shokunin/.ufo/prompts/kama-round-29.md:343-365`. In particular, the claim must count self-assessment versus observed-state mismatches, name its axis by the changed surface, and enumerate any universal target. The prior accepted distinction is recorded in `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:1267-1291`: instrument-anchor drift was not demonstrated calibration overreach. Binding the new audit to W addresses the timing objection, not automatically the semantic objection.

## Strongest counterexample: a supported self-assessment is called false

The frozen base receipt `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/before/c1-base.json` marks SCORECARD line 740, class P, token `round-17-verifier-spotcheck.md:217–221`, as `p:absent` at W = `c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d`.

Read-only inspection at that very W finds both:

- SCORECARD lines 739–741 report that the outside review judged **discernment improved**.
- The intended lane artifact, `corpus/lessons/round-17-verifier-spotcheck.md`, lines 217–221, says `- **discernment: improved** (this closure's outside judgment; the lane wrote` and explains the agreeing admit/reject sample.

Reproduction used, successfully, without running any instrument:

```sh
timeout 20s prlimit --as=536870912 --nproc=32 git --no-replace-objects -C /home/vgpnk/Projects/shokunin/kama-shokunin grep --threads=1 -n -B 1 -A 4 -F -e '**discernment: improved**' -e 'Round-17 outside review admitted' c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d -- SCORECARD.md corpus/lessons/round-17-verifier-spotcheck.md
```

Thus the substantive self-assessment matches the outside evidence at W. The counter instead treats the shortened filename as a repository-root path. A root-relative citation defect can be real pointer hygiene, but it is not evidence that the reported discernment verdict was false. Declaring this a factual self-assessment error would introduce false provenance rather than catch overreach.

A second, independent example is SCORECARD line 1375. The receipt marks `count-c1.py:384` as `p:absent` at W = `d183ec572a5eed5bedeb4bce0da02707d51df3dd`. Its sentence expressly says “round-26” and describes checking stored request text. At W, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/count-c1.py:384` is exactly:

```python
                    c["e_not_echoed"] = sig not in req_bytes
```

Read-only historical `git grep --threads=1 -n -F -e 'e_not_echoed' -e 'req_bytes ='` at W confirmed that line and the construction of `req_bytes` at line 372. Again, the named mechanism is present and the shorthand pointer, not that mechanism, is what fails the frozen test.

**Impacted axes:** calibration is unestablished by these failures and risks harm if true historical judgments are retracted; pointer traceability can still improve. No later drift is needed for either counterexample.

## Seven Q failures do not prove seven false measurements

The receipt's eleven failures consist entirely of four P and seven Q failures; H, N, C and T contribute none. The Q check at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py:259-264` asks only whether an exact quoted span occurs in a permitted committed blob at W. It excludes SCORECARD, SHONEN, LOG and the whole corpus. Absence proves absence from that search universe, not that a command did not produce the reported values. Conversely, arbitrary matching text in a permitted blob can satisfy Q without demonstrating execution or correct values. The latter is a code-derived counterexample, not an executed mutation.

For example, SCORECARD lines 833–834 at W = `7229fa95eb122310e9e5334ad799ee3006293ebd` summarize grid results with `baseline=VALID members=3 rejected=0/3` and `baseline=VALID rejected=3/3`. Historical source inspection finds the producer at `tests/llamacpp-live/install-tree-grid.py:113-115` always prints `members=...` between baseline and rejected, followed by `tree_pin=...`. Formatting or excerpting a count and failing to retain a raw output blob are distinct from incorrect counts. I did not re-execute these historical measurements, so their actual outcomes remain unverified here.

A real calibration repair could honestly downgrade “verified” to “not reproducible from retained evidence.” But that is not the same assertion as “the measurement was false when written,” and the frozen row parser does not require that distinction or any explanatory middle cell.

## RefPaste: real mechanical work, insufficient axis evidence

The claim expressly defines its work as running the frozen check and appending its observed values. Therefore automation alone is not a valid objection: RefPaste performs that declared operation rather than silently skipping it. The control evidence is not a do-nothing pass.

The opened receipt `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/RefPaste/receipt.json` names tip `a59f90ec1d7077a482ada768be8cb7d976b96a71`: 69 statements, eleven mismatches, eleven valid corrections, no false corrections, unresolved 0, met true. Its report `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/RefPaste/REPORT.md:65-88` explicitly says no lane blob was manually inspected and no semantic judgment was required. This is pre-existing control evidence, not a run by this reviewer.

The substantive objection is that this success is equally compatible with copying a detector's category errors into the self-assessment. The parser reads only statement id and last-cell observed value (`count-c1.py:268-279,313-322`), not whether the original judgment was actually wrong, confidence was honestly revised, or the explanation is true. Calling RefPaste a reference policy cannot answer that objection. The mechanically added historical-audit surface is real; a calibration inference still needs an independently grounded mapping from detector failures to honest self-assessment gaps.

## Existing authority: partial overlap, not the same composite instrument

At freeze `827d136546b85059a984b34970f5b493d9a71290`:

- `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/citation-provenance.py:2-20,31-35,71-124` verifies registry-selected `cite(rev, path, sha256=...)` tokens, target bytes and ancestry. SCORECARD was already among its documents. It does not extract arbitrary SCORECARD/SHONEN statements or assign per-line W.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/prereg-time-check.py` already compares file timestamps with a Git committer time, using the last commit touching the file and a future-time horizon (or strict mode). It is not literally limited to one preregistration filename; `--path` is general. It does not blame each line or implement the six-class ledger. I opened its frozen blob because the live working copy already contains this round's timestamp-regex repair.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py:8-45` already checks fleet-report commit citations and landed omissions, with a validated errata ledger. Its population is fleet reports, not these two lane documents; its commit checks are not the new per-line strict-ancestor test.

A read-only base-tree search over `tools`, `tests` and `registry` for `line-porcelain|git blame|"blame"|unresolved_ids|self-assessment` returned no matches (exit 1). This supports only that bounded search, not universal absence of every possible implementation.

The combination of free-text extraction, per-line historical checks and this correction ledger is new relative to the inspected instruments. The atomic verification rules are not all new. More importantly, `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md:41` already holds KQ14: textual coverage, pointer bounds and content correspondence must be separated; human/source review establishes content. KQ27 and KQ28 already govern quoted-count revisions and report provenance. The new counter cannot become a second authority that overrides that semantic boundary merely because it returns zero.

## Is `unresolved == 0` fully enumerated?

**Yes, for the frozen operational set; no, for all semantic self-assessment errors.** The code enumerates every match of its six extractor classes at fixed base `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`, guards unique ids, checks each, and enumerates the correction-shaped rows under its heading. With an intact base SCORECARD prefix, `unresolved` is unmatched failed ids plus false correction rows; without that prefix every extracted base id is unresolved (`count-c1.py:297-341`). This is a concrete finite target, not an unenumerated universal over that definition.

The receipt contains 69 extracted statements, all from SCORECARD; the SHONEN selection is empty. It does not assess the promotion checklist's prose. It also does not extract ordinary numerical assertions such as SCORECARD line 824's `selftest 5 cases`. At that line's W, the code in `tools/citation-provenance.py:166` prints `selftest: ok (12 cases)`; the receipt extracts only the line's backticked Q span. That visible text/code disagreement is outside the denominator. This is static source evidence, not a rerun of the selftest or proof of which earlier version was executed.

Accordingly zero can mean only “the frozen extracted failures have exactly the required ledger acknowledgments, with no counted bad acknowledgment.” It does not mean all historical statements were false as labeled, all errors were found, all current self-assessment matches the repo, or calibration is saturated.

## Smallest safe correction and answering evidence

1. **Preserve the freeze.** Do not change the extractor, predicate, target or correction acceptance, and do not drop the counterexamples after data. The prerecorded kill rule requires counter defects to remain disclosed limits.
2. **Separate facts from detector observations.** In explanatory text outside any data rows, distinguish root-path lookup failure, missing retained output, actual contrary observed value, and later drift. Do not call a supported historical outside verdict false. This reviewer supplies no correction data rows.
3. **Answer the strongest objection with a source-backed crosswalk for each flagged assertion:** full original context; intended repository, path and measurement revision; independently observed fact; and why it changes a self-assessment rather than merely its citation. For line 740 that evidence must confront the agreeing outside verdict already present at W, not repeat `p:absent`. For Q it must distinguish wrong values from missing committed raw output and state any justified uncertainty downgrade.
4. **Keep receipt success separate from axis fit.** Supplemental evidence can substantiate the claimed calibration interpretation; it cannot silently redefine what the frozen target counts. If the evidence only supports pointer hygiene or provenance-quality work, report that limit and leave calibration movement unestablished for the canonical judge. Exchanging truthful assessment for a passing ledger would be the prohibited trade, not a harmless implementation detail.

No installs, services, clones, tests, counters or other runtimes were started. Commands were bounded read-only Git inspection. Two initial Git searches hit Git's thread-creation limit; both were retried successfully with `--threads=1`. Only this critique and the assigned advice file were written. Admission and all final axis/trend verdicts remain with the canonical judge.
