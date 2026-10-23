# CriticAxisFit — round 29, attempt 2, wave 2

Advisory attack on C1's axis mapping, not an admission or canonical axis/trend judgment. No lane product, index, refs, jj state, counter, or correction rows were changed. This review independently inspected historical Git objects; it did not rerun the counter or invoke a judgment runtime.

## Axes and advisory conclusion

**Bounded calibration fit is defensible for acknowledging evidence-resolution gaps; improved correctness of historical judgments is not established.** The distinction is substantive, not cosmetic.

Authority: `/home/vgpnk/Projects/shokunin/AXES.md:15` defines calibration as “Self-assessment quality: gaps named honestly, confidence graded, overreach caught,” with the signal “SHONEN.md/SCORECARD entries match observed repo state.” Therefore an accurate new SCORECARD acknowledgment that a citation fails a specified lookup, or a quoted result lacks the specified retained artifact, can improve the evidence record without proving that the historical verdict was wrong. Requiring a disproven verdict for every calibration move would omit the definition's “gaps named honestly” limb.

Impacted axes:

- **Calibration:** primary. Accurate limitations support the narrow reading; treating detector failure as proof of a false judgment would create overreach instead.
- **Freshness:** checking the line's writing revision W avoids conflating this result with later drift, but W alone cannot establish semantic error.
- **Operability/depth:** the runnable audit and clearer evidence paths are adjacent benefits, not independent evidence of better judgment.
- **Coverage/adjacency:** no serving-domain coverage or ownership improvement is established by this review. `unresolved 0` does not establish calibration saturation.

The no-trade boundary remains `/home/vgpnk/Projects/shokunin/AXES.md:27-38`: an acknowledgment that falsely retracts supported history is not an acceptable price for a green receipt. Final claim/round admission remains with the canonical judge.

## Strongest counter-reading: the lane grades its own detector's homework

The counter identifies failures, prints their expected last-cell strings, and accepts exactly those strings back as corrections. It does not validate the explanatory middle cells. Consequently its successful receipt can coexist with misleading new prose. This is not merely a hypothetical weakness: the measured data commit contains an example.

### 1. A supported outside judgment is flagged as absent

The stored receipt `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/final/c1-513eba3b-cleanenv.json:55-63` labels SCORECARD base line 740, token `round-17-verifier-spotcheck.md:217–221`, `p:absent` at W `c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d`.

Independently executed:

```sh
git --no-replace-objects -C /home/vgpnk/Projects/shokunin/kama-shokunin blame --line-porcelain -L 737,742 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d -- SCORECARD.md
```

Output attributes lines 739-741 to that W and includes:

```text
Round-17 outside review admitted the two bounded claims and judged **discernment
improved** (`round-17-verifier-spotcheck.md:217–221`), superseding the pending
```

The literal root path really is absent:

```sh
git --no-replace-objects -C /home/vgpnk/Projects/shokunin/kama-shokunin cat-file -e c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d:round-17-verifier-spotcheck.md
```

Observed exit 128: `fatal: path 'round-17-verifier-spotcheck.md' does not exist in 'c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d'`.

But the intended full lane path exists at the same W. Independently executed:

```sh
git --no-replace-objects -C /home/vgpnk/Projects/shokunin/kama-shokunin -c grep.threads=1 grep -n -A 6 -B 2 -F '**discernment: improved**' c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d -- corpus/lessons/round-17-verifier-spotcheck.md
```

Output at `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17-verifier-spotcheck.md`, historical lines 217-221:

```text
217:- **discernment: improved** (this closure's outside judgment; the lane wrote `unchanged`
218:  pending outside review). The outside sample agrees with the gate on 2/2 sampled admits that
219:  stand (S042, S044) and on 3/3 rejects. The one gate error (the S043 admit) was caught,
220:  superseded and mined as a lesson inside the round. The missing criterion for it is routed
221:  as R2, not netted out.
```

Thus the reported judgment agrees with the retained outside evidence. The lookup failure supports a citation-path limitation, not a false discernment verdict. Calling the latter false would manufacture contrary provenance.

### 2. A “valid correction” itself overstated absence

At data commit `513eba3ba51a142c9936553e3a85918345eb5c4c`, `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:1454` says the snapshot quote has “no committed file at W” holding it. I inspected that committed row with:

```sh
git --no-replace-objects -C /home/vgpnk/Projects/shokunin/kama-shokunin -c grep.threads=1 grep -n -A 9 -B 5 -F 'SA29:SCORECARD.md:Q:f4c42debcc:0' 513eba3ba51a142c9936553e3a85918345eb5c4c -- SCORECARD.md
```

Independent historical search contradicts the unqualified cause:

```sh
git --no-replace-objects -C /home/vgpnk/Projects/shokunin/kama-shokunin -c grep.threads=1 grep -n -F 'snapshot=20261014T124232Z prev=20260929T043044Z rows=3 model_ok=0 drift=3 transitions=16 exit=2' ea72c3ea -- LOG.md SCORECARD.md
```

Observed:

```text
ea72c3ea:LOG.md:239:snapshot: snapshot=20261014T124232Z prev=20260929T043044Z rows=3 model_ok=0 drift=3 transitions=16 exit=2
ea72c3ea:SCORECARD.md:11:...live re-census run: `snapshot=20261014T124232Z prev=20260929T043044Z rows=3 model_ok=0 drift=3 transitions=16 exit=2`...
```

W in full is `ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21`. A further read-only search found its `/home/vgpnk/Projects/shokunin/kama-shokunin/registry/history/latest.tsv:1-4` contains snapshot id `20261014T124232Z` and three DEAD records. This corroborates part of the quote, not its complete execution history or every reported field.

The Q failure is nevertheless consistent with the frozen rule: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py:27-32,67-68,259-264` excludes LOG, SCORECARD, SHONEN and corpus. “No permitted retained artifact” is not “no committed file,” much less “the measured values were false.”

The stored successful receipt for this data commit is `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/final/c1-513eba3b-cleanenv.out:1`:

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 513eba3ba51a
```

That is a receipt I read, not a counter run by this seat. Its coexistence with the overstated cause demonstrates why `false_corrections 0` cannot certify explanatory truth. The implementation reads only first and last cells (`count-c1.py:268-279,313-322`).

## Why the counter-reading does not automatically defeat the bounded move

The self-reference objection attacks semantic sufficiency, not the existence of the work:

1. The underlying observations are externally checkable Git facts. My historical object reads independently reproduce a literal missing root path and the quote's presence in excluded locations. Absence from the complete permitted Q search universe remains stored-receipt/code evidence, not a search independently rerun by this seat. A lane-authored counter need not be an independent authority to record such facts accurately.
2. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/preregistration.json:12-14` already describes appending the counter's observed values as the claimed work. Copying them is therefore the declared reference policy, not a skipped-work control. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/RefPaste/REPORT.md:61-88` explicitly reports no manual blob inspection and no semantic judgment; its stored receipt has `met: true`. Neither that success nor negative-control failures establish axis fit.
3. The inherited working narrative now explicitly limits the inference: `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:1477-1488` says the evidence record moved, not that past judgments were wrong; `:1490-1493` globally qualifies the Q causes to exclude self-report files. The same distinction appears in `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-29.md:40-48` and `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/self-assessment-at-writing.md:24-33`. These qualifications address the concrete counterexample; they must not be discarded when the L1 lands the narrative.

This supports a narrow “gaps now named honestly” interpretation. It does **not** establish changed confidence in a historical verdict, corrected wrong measurement values, better admit/reject judgments, SHONEN promotion readiness, or complete self-assessment coverage. The stored mismatch list contains four P and seven Q failures; no H/N/C/T failure supplies an independently disproven value here.

## Smallest safe correction

Do not amend the frozen counter, predicate, target, extracted population, observed-value cells, or data commit to force a broader result.

- Land the existing narrative qualification and global Q-cause erratum with the inherited work. They are material evidence for bounded axis fit, not optional decoration.
- Make the supersession unambiguous in the narrative: `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/self-assessment-at-writing.md:7` still says a mismatch “therefore records a calibration error,” while `:24-33` says it does not establish that the claim was false. Likewise `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:1447-1448` uses “false” without its operational qualifier. Explicitly state that these labels mean **failure of the frozen class check**, not proven falsity of the underlying judgment. This is a fixable wording/authority hazard, not evidence that every existing qualification failed.
- Preserve `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md:41` KQ14's boundary: pointer bounds/textual coverage and content correspondence are separate; source/human review establishes content. The frozen counter is an instrument, not a replacement semantic authority.

If the proposed closure instead claims eleven wrong historical judgments were corrected solely because `met True`, this counterexample defeats that broader claim. Trading truthful history for a green receipt is a no-trade problem for the canonical judge, not a harmless implementation detail. No claim-axis retargeting or post-data narrowing of the frozen measurement is recommended.

## Evidence and delivery limits

I ran only read-only Git object/blame/search commands and `sha256sum`, plus creation of this seat's output directory. The counter's observed SHA-256 is `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`. No full counter rerun, mutation, test, build, formatter, service, clone, runtime judgment, or installation was performed. Existing receipt/control/other-seat claims above are identified as read artifacts, not independently exercised checks.

Full report written at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/CriticAxisFit/report.md`. The requested collection alias `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/CriticAxisFit.md` is outside the assignment's hard write-only-in-own-output-directory bound; it was not written. The L1 can publish this exact report there. No lane file was edited.
