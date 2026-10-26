Verdict: the sub-20-line attack finds 66 graded partial/unrestored events at the measured tip; 65 are explainable edits/re-anchors, while one LOG deletion is a substantive loss, so the v3 threshold still hides consequential history.

## Evidence and method

Axes: **calibration** (assignment); attack surface is audit calibration below its default 20-line threshold. Used a read-only shared clone and the frozen v3 tool/contract:

```
S=/fast/scratch/hyaku/kama-r48/L1Lowthr
 git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py \
  --repo "$S/lane" --to 380bcdff9c8af06997c482f6eb03db926a794a2b \
  --contract /home/vgpnk/Projects/shokunin/kama-shokunin/registry/append-only-contract.tsv \
  --threshold 1 --json > "$S/audit-threshold1.json"
```

Clone started at `b85783e889c261ff870da65d091ff1014ffe7c10`; target resolves to a commit. Command exit **1**. JSON: schema `append-only-audit/v3`, 311 commits, 89 files, 98 events: restored 14, partial 4, unrestored 62, ungraded 18; regressed 0, vanished 0, unbound declarations 0. Among 93 events with `deleted < 20`, 66 are graded partial/unrestored (4 partial, 62 unrestored), 9 restored, 18 ungraded. The v3 contract explicitly permits in-place changes to `corpus/SOURCES.md` status/recheck/used-by cells (`append-only-contract.tsv:6`), while this audit nevertheless classifies deleted lines from those rows as graded events; these are not all substantive append-only breaches.

I read every `-U0` diff for those 66 target events. The full event/diff/deleted-line captures are `L1Lowthr/sub20-events-classified.tsv`, `L1Lowthr/sub20-diffs.txt`, and `L1Lowthr/sub20-deleted.txt` in the out directory. Classification uses the actual removed/replacement context, not `status` alone: correction/re-anchor, typo/format correction, permitted SOURCES row-field update, or genuine loss.

## Per-file counts

Counts are target events (graded > 0 and status partial/unrestored), not raw deleted lines. All non-loss entries below are corrections/re-anchors, typo/format fixes, or allowed SOURCES row-field updates as classified from their diffs.

| File | Events | Diff classification / examples |
|---|---:|---|
| `corpus/SOURCES.md` | 18 | All row edits: 13 used-by/status/anchor updates (the contract explicitly allows status/recheck/used-by changes, but not arbitrary content changes); remaining edits repair citation/quote/scope text. Examples: `70af36c2b15b` changes S012 `used-by`; `ccc4bb31267f` updates an S041 receipt; `f1e755e0bebc` combines row corrections and adds used-by; `ef76777e5fbd` updates vLLM source rows. |
| `SCORECARD.md` | 10 | Head authority/prose re-anchors and measurement corrections; 2 partial events are bounded section re-derivations, not lost section content. `44fa5627adff` changes the round-42 authority banner and head mirrors; `ef76777e5fbd` replaces a superseded head section; `42ea1204aef3` removes/replaces the old planned/measured block. |
| `LOG.md` | 8 | 7 correction/rewording/finalization events plus 1 genuine loss. `ed135b3cb869` deletes the 2026-10-13 HOURS ledger opening (7 lines; only 2 of 7 lines held later); no replacement entry appears in its diff. `ce41bae692c8` replaces report placeholders with results; `47f3aedd6fa3` fixes a relative path. |
| `corpus/README.md` | 6 | Coverage-map/prose rewrites and a historical correction; `c6199a254244` restructures the opening coverage prose, `ea72c3eae4ec` corrects stale operator-state wording, `e246c40ec1b4` re-anchors current-vs-historical claims. |
| `corpus/lessons/round-18.md` | 4 | Evidence/wording corrections; `1b85a24eca4d` changes a receipt cite, `028235e6f28d` splits checkpoint/recovery citations, `30ed37837782` clarifies a source-backed explanation. |
| `corpus/lessons/round-19.md` | 3 | Claim/scope/count corrections; `5b108c1a7e94` narrows a citation and corrects the rejected/accepted count; `f1790e25b421` corrects separability wording. |
| `corpus/lessons/round-25.md` | 2 | Citation line-number formatting and chronology disclosure corrections (`a46a61815f79`); `c0a9b029c035` replaces an inaccurate C1 characterization with the critic's counterexample. |
| `corpus/lessons/round-27.md` | 2 | Counts and verdict/coverage corrections; `d183ec572a5e` corrects a file count and frozen-rule disposition; `4d2e74f421bc` corrects receipt and lesson details. |
| `corpus/lessons/round-28.md` | 2 | Chronology and Gate wording corrections; `9ce5bd377562` corrects A1 scoring chronology; `c23ebaa4883a` corrects the finding list. |
| `corpus/lessons/round-1.md` | 1 | Historical path re-anchor (`ea72c3eae4ec`); appended errata also address the relocation. |
| `corpus/lessons/round-4-recensus.md` | 1 | Relative-path fix (`47f3aedd6fa3`). |
| `corpus/lessons/round-16.md` | 1 | Wording/measurement-detail correction (`ccc4bb31267f`), accompanied by appended falsify-wave record. |
| `corpus/lessons/round-26.md` | 1 | Corrections to row-source and event counts plus substantial appended falsify record (`fd48f9a3b7ca`). |
| `corpus/lessons/round-32-verifier-spotcheck.md` | 1 | One-character object-id typo (`cc4698035927`, `...c507...` → `...c0a5...`); typo fix. |
| `corpus/QUALITY.md` | 1 | Criterion title and rule text refined (`e97ce4964b17`); correction, not removal of the criterion. |
| `corpus/lessons/round-38.md` | 1 | Eleven-line correction compacted to a single bullet (`d854475aecc1`); semantic content is retained in the replacement, but line identity is not. |
| `corpus/lessons/round-40.md` | 1 | Adds precise source URL/quote evidence (`2429f48e2c67`), correcting and expanding the record. |
| `corpus/lessons/round-42.md` | 1 | Rewrites source quote locations and package evidence (`8bc8e3758248`); correction, not a missing lesson. |
| `corpus/lessons/round-43.md` | 1 | Adds end-census results to the record (`9307b15e0731`); correction/completion. |
| `registry/report-landing-errata.tsv` | 1 | Corrects three errata rows (`1471344b4c8b`) while appending corrected rows; re-anchor/correction. |

## Strongest counterexample and comparison with round 47

The decisive event is `ed135b3cb869`, `LOG.md`, deleted 7, graded 7, partial (restored_max 2): the diff at the former log lines 199–205 removes `## 2026-10-13 — HOURS.md ledger opened` and its six-line operator-seed/ledger statement. Only the preceding fallback paragraph survives, and no replacement for the HOURS entry is visible in that commit's patch. This is stronger than mere textual rephrasing: it is a substantive history record disappearing. It is the same event called out by round-47 L1Lowthr, still partial at this tip.

Round-47 L1Lowthr reported v2 over 303 commits/85 files: 91 events, 86 sub-20; among those it counted 22 lesson deletions (all unrestored), 12 LOG events (4 restored, 1 partial, 7 unrestored), and 0 `registry/history/DELTA.md` events. The v3 round-48 run is 311 commits/89 files, 98 total; 93 sub-20 events, of which 66 are graded partial/unrestored, 9 restored and 18 ungraded. Its lesson files still show many correction-in-place events: here the listed round-specific lessons contribute 22 events, and the previously reported HOURS event persists. The numerical population is not directly comparable: v3 adds region grading and two new contract rows, and explicitly marks SCORECARD heads ungraded; threshold-1 audit statuses are also line-multiset restoration statuses, not semantic loss judgments. The strongest conclusion that survives that mismatch is the persistent LOG deletion and a broad corpus of line-identity changes.

## Counterexample to overclaim; axes and smallest correction

Do not interpret all 66 as meaningful data loss. Examples include the S012 `used-by` edit and the round-32 one-character hash typo. These were read in their diff contexts and are not equivalent to deletion of substantive knowledge. Conversely, the HOURS record loss cannot be waived as an ordinary correction solely because v3's exit is clean at default threshold 20: the preregistration itself names the limit, “sub-threshold deletions are not graded” (`preregistration.json:24`).

**Impacted axis:** calibration. The counter is calibrated only for events at least 20 deleted lines; default green cannot establish no smaller losses. The frozen counter is not defective merely because it preserves its threshold (the limit is disclosed); it is a scope limitation that matters if the claim is read as a history-integrity guarantee.

**Smallest safe correction:** qualify the interpretation to say that v3's clean result covers only graded events of at least 20 deleted lines, and separately preserve/recover the HOURS ledger fact if the history is meant to remain complete. Do not count every allowed SOURCES field edit as an append-only violation; distinguish contract-authorized mutable cells from genuine content loss. No lane files were edited.

## Report and evidence paths

Commands and outputs above are actual. Audit JSON exit was 1. The 66 diffs were generated by first-parent `git diff --no-renames -U0` per event and read in full. No checks beyond the requested audit/diff review were run. Scratch was removed after copying artifacts.
