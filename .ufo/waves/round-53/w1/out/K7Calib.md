# K7Calib — verdict: `undisclosed 16 → 0` is a closure count over a registered miss ledger (the same bounded shape as rounds 51–52), not a census of self-assessment-vs-repo mismatches; disclosure is the maximum compliant disposition for the append-only surface and a real calibration improvement of the surface+ledger system, but one live existence claim (SCORECARD.md:2136) still stands undisclosed at the point of the sentence — a structural tradeoff, not a counter defect.

## Axes
Calibration (C2) only. No operability (C1) claim assessed. Independent rerun of the frozen counter, base/build diff inspection, sentence-level reading of all 16 base misses, ledger-reachability checks.

## Evidence
- Ran the frozen counter at the build tip on my own `--shared` clone, three times (fleet HEAD advanced between runs: `ee9f7341` in the L1 receipt, `71256a5` and `33540c6` in mine): every run reads `fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True`, exit 0 (~2 s). Receipt: `.ufo/waves/round-53/w1/out/K7Calib/c2-k7calib-rerun.out`. Matches `.ufo/waves/round-53/measured/c2-build.out`; the frozen predicate holds at the build.
- Build diff on C2 surfaces (`git diff 4229ea1b... c22602bd...`): SCORECARD.md +4 lines (appended section only, file end); SKILL.md two 1-line in-place corrections (113, 895); new ledger 27 lines = 9 comments + 14 data rows; SHONEN.md untouched. Full detail: `.ufo/waves/round-53/w1/out/K7Calib/evidence.md` §2.
- Sentence-level reading of all 16 base misses (evidence.md §3): 12 of 16 are self-disclosing (the citing sentence itself says the path is absent/dangling: SCORECARD.md 491, 1503, 1732, 1741, 1844, 1901, 2228) or content-pinned upstream files whose bytes the counter re-fetches (SKILL.md 1143, 1245–1248). Two are live existence claims, both on SCORECARD.md:2136.

## 1. Is `undisclosed 16 → 0` a count of mismatches between self-assessment and repo state?

Not by itself — and this is the same verdict I filed at round 52 for `corr_lost 151 → 0`. The quantity is a count of *citation-resolution misses lacking a ledger row* over three registered surfaces under a frozen parser: `undisclosed = unresolved ∧ ¬disclosed`. Three boundaries keep it from being a general mismatch census, all acknowledged in the preregistration's own `limits`:

1. **Existence, not content** — the counter checks that a cited path resolves, not that the file says what the citing sentence claims (preregistration limits, C2 bullet 1). A resolving citation can still support a false sentence.
2. **Registered surfaces only** — SCORECARD.md, SHONEN.md, SKILL.md. Existence claims in LOG.md, lessons, corpus/README.md, knowledge entries are out of scope (limit 2).
3. **The disclosed residue still stands.** At the build, `unresolved=14` — the 14 misses remain in the prose, now with re-derivable reasons. The predicate's improvement is that they are *known and classified*; the prose sentences citing them are unchanged (four of them self-disclose; ten do not locally).

The preregistration's C2 `type` text is precise about the OR ("resolves, or its miss is disclosed"), so the frozen contract does not overclaim; the framing risk is only in paraphrases like "calibration = self-assessment matched to repo state" that drop the second disjunct. This is the third consecutive round of the same operationalization: round 51 (append-audit-v6: every graded lost line restored or disclosed by name), round 52 (corr_lost 151→0), round 53 (undisclosed 16→0). Consistent, bounded, and each time a closure-of-ledger measure rather than a sentence-truth measure.

## 2. Is disclosure, rather than repair, a calibration improvement?

Yes under the frozen contract, and the build uses each disposition where the contract allows it:

- **Repair where allowed.** SKILL.md is not append-only; its two wrong citations were corrected in place (113: `scripts/local-helper.mjs` → `~/Projects/ufo-fsd-alpha/scripts/local-helper.mjs`; 895: `tests/report-audit/…` → `tests/report-audit/`, the one `fixed` ledger row). This follows the lane's own round-52 precedent (lesson Mistakes #4 fix: "amended at integration (SKILL.md is not an append-only file)").
- **Disclosure where repair is barred.** SCORECARD.md is declared append-only outside its head tables, and the counter's `dropped=0` leg treats removal or in-place correction of a cited token as a *worse* defect ("a dropped citation is a deleted claim, not a corrected one"). For its 10 misses the only compliant disposition is the ledger + an appended pointer section — which is what landed.
- **The improvement is real but located in the system, not the prose.** The motivating round-52 lesson (Mistakes #4) was that W3Mistakes found 51 misses and 50 were called "pre-existing" and never examined. The build examines and classifies all 16 with history-re-derivable evidence (the counter re-ran those derivations in my rerun: no bad row). A reader holding the ledger can discount every miss. A reader of the prose alone cannot. The flat score 7→7 matches this: closure of a hygiene ledger, not a deepening claim — consistent with the preregistration authority note that calibration is the lowest assigned axis.

## 3. Does any SCORECARD sentence still claim a dead path exists without the ledger reaching the reader?

Yes — exactly one location, two sentences: **SCORECARD.md:2136** (round-38 frontier step) asserts "wave-1 fetches returned HTTP 200, 6243 and 2820 bytes, receipts in `.ufo/waves/round-38/w1/out/FetchS352/` and `.../FetchS353/`" and cites `(`.ufo/waves/round-38/w1/out/ExecTagInventory/api-status.txt`, `api-body.json`)` as the record of an HTTP 403. `git ls-tree -r` at the build tip shows no path matching `FetchS35*` or `ExecTagInventory` anywhere in the tree; the ledger rows for both say class `never`, "no seat report of that name was committed in round 38" (evidence.md §3). The sentence does not say so.

Ledger reachability at the build commit (evidence.md §4): the ledger is named exactly once in SCORECARD.md, in the appended end-of-file section (line 3029) — nothing at line 2136 points there. SKILL.md contains no mention of the ledger or the counter at all, so its four upstream rows and one `fixed` row are unreachable from the surface they correct (the round-53 SKILL instrument-registry entry that would route readers is a known pending integration item, absent from the build). Reachability for a careful reader is: read SCORECARD to EOF → section → ledger → grep; for a line-by-line reader of SCORECARD, or any reader of SKILL.md, the disclosure does not arrive at the point of the claim.

**Classification: structural tradeoff, not a fixable defect.** The frozen counter *requires* the sentence to persist (`dropped=0` kill leg) and the append-only declaration bars in-place correction; the lane chose the only compliant disposition. Two optional, non-blocking polish items for integration: (a) name line 2136 in the appended section's summary (it names the self-disclosing lines' classes but not this one); (b) the pending SKILL.md round-53 registry entry can name `registry/cited-path-corrections.tsv` so SKILL.md readers are routed. Neither changes any counter verdict.

## Smallest safe correction
None required for calibration framing: keep describing C2 as "closure of the cited-path miss ledger — every miss resolved or disclosed with a re-derivable reason, no bad/stale row, no dropped citation," exactly as the preregistration's `type` and the round-53 lesson already do; do not paraphrase `undisclosed=0` as "self-assessment now matches repo state" without the second disjunct. If the lane wants the stronger quantity later, that is a new instrument (sentence-claim grading), out of scope here.

## Paths written
- `.ufo/waves/round-53/w1/out/K7Calib.md` (this report)
- `.ufo/waves/round-53/w1/out/K7Calib/evidence.md`
- `.ufo/waves/round-53/w1/out/K7Calib/c2-k7calib-rerun.out`
