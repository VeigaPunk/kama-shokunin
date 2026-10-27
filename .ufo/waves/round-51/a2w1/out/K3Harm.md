Verdict: No demonstrated calibration harm in the disclosure-ledger scope carve-out or A-row permission; threshold 1 is noisier by event volume, not a demonstrated material runtime regression; v5 C2 failure is superseded, not evidence of harm.

Axes reviewed: calibration (primary); operability only insofar as a slower audit could burden routine use.

## 1. digest-ledger excludes the new disclosure ledger

Evidence / command:

```sh
git -C "$S/lane" diff 57a2e25bf702b03aa61f9265e968cf68058ecb82 138af25b963450b6520794995605fa7dbbcd87e0 -- tools/digest-ledger.py
git -C "$S/lane" show 138af25b963450b6520794995605fa7dbbcd87e0:registry/append-only-disclosures.tsv | wc -l
```

Observed diff adds `registry/append-only-disclosures.tsv` to `is_doc`'s explicit exclusions (digest-ledger.py lines 73, 79-81) and documents why at lines 12-15. The ledger has 167 lines: 166 line-key hashes, not artifact hashes. This is a real reduction in digest-ledger coverage for that one file, not a no-op. It avoids treating line identity hashes as claims about whole-file artifacts, and C2 separately audits the ledger's semantics: its frozen lane leg reports `fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True`, exit 0. The ledger is not thereby authoritative without validation; the append-only audit rejects bad rows.

Counterexample tested: a forged digest-style value placed in this ledger will no longer be visited by digest-ledger. Yet the excluded values are defined as source-line keys and the dedicated C2 checks each against the relevant history event, count and class. No extant grounded evidence shows the exclusion hides an artifact-integrity digest. This is therefore an intentional change of authority/scope, not a demonstrated axis harm. Smallest safe correction: none indicated; retain both explicit exclusion rationale and C2 validation. If a future use stores artifact digests in this file, move them to the digest-ledger's intended input or add an independently validated field rather than silently treating line-key hashes as artifact digests.

## 2. round-50 C2 returns lane=0 on v6

Evidence / command:

```sh
python3 "$S/lane/tools/round51-append-audit-v6-check.py" --repo "$S/lane" --tip 138af25b963450b6520794995605fa7dbbcd87e0 --scratch "$S" --out "$S/c2.out"
```

Observed: `fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True`, exit 0. The frozen counter docstring explicitly defines v6 and the lane predicate. C2's changed contract is explicit: threshold 1, permitted exact A-row mutable cells, disclosure ledger. A round-50 checker targeting v5 definitions is no longer the current definition; its `lane=0` on v6 alone is an expected supersession signal, not evidence v6 is worse. The new counter reconstructs lost lines independently for whole-file graded events; its own run succeeds. Minimal correction: none; report the version boundary and don't count the old counter's mismatch as a regression.

## 3. Are SOURCES edits that v5 graded now invisible?

Evidence / commands:

```sh
git -C "$S/lane" log --first-parent --oneline 57a2e25bf702b03aa61f9265e968cf68058ecb82..138af25b963450b6520794995605fa7dbbcd87e0 -- corpus/SOURCES.md
git -C "$S/lane" diff 57a2e25bf702b03aa61f9265e968cf68058ecb82 138af25b963450b6520794995605fa7dbbcd87e0 -- corpus/SOURCES.md
```

Observed: in this round the only SOURCES change is additive S499 plus a blank separator; the first-parent path log reports only the round-51 build commit, and the diff contains no deleted S-row. (The supplied round-50 closure also documents a prior deleted blank separator, not a registry row.) Thus no real A-row violation in the examined round became invisible. By implementation, v6 `permitted_edits()` only permits a deleted registry row if the same id survives and all non-mutable cells remain byte-equal; the frozen C2 fixture tests mutable edit permitted, immutable `teaches` edit graded, code-span pipe parsing, and dropped row graded. In lane run, 58 permitted lines are counted separately from 142 lost graded lines, not hidden as ungraded omissions. This is a narrow exception explicitly licensed by the `corpus/SOURCES.md` contract (only status/recheck/used-by change in place), and only for those cells.

Strong counterexample to watch: changing `teaches`, source, anchor or another immutable cell while preserving the row id must not be permitted. The nine fixtures exercise that category via `teaches` and do not show a defect. Smallest safe correction: none supported by local evidence; keep the immutable-cell test and use-by/status scope exact.

## 4. Does threshold 1 make routine runs slower/noisier?

Evidence / commands:

```sh
python3 "$S/lane/tools/append-only-audit.py" --repo "$S/lane" --to 138af25b963450b6520794995605fa7dbbcd87e0 --json > "$S/audit.json"
python3 -c 'import json; d=json.load(open("'"$S"'/audit.json")); from collections import Counter; s=d["summary"]; print("threshold",d["threshold"],"events",s["events"],"permitted",s["permitted_lines"],"disclosed",s["disclosed_lines"],"unrestored",s["unrestored"],"bad_disclosures",s["bad_disclosures"]); print("events under old 20-line default",sum(e["deleted"]<20 for e in d["events"]))'
```

Observed: exit 0; `threshold 1 events 106 permitted 58 disclosed 166 unrestored 0 bad_disclosures 0`; 101 of 106 events have fewer than 20 deleted lines and would not have been events under the old default. This does increase output and history accounting substantially; that is the direct tradeoff that closes the known blind spot (round-50 closure R6 says 97 hidden events including the real LOG.md loss at ed135b3c). The audit is a CLI, and the counter's entire fixture+lane measurement took about 16 seconds in this run (includes fixtures and history recomputation); I have no v5 timing baseline, so cannot substantiate a material slowdown. Current run is finite and passed; do not claim zero cost or no runtime change. Smallest safe correction: none unless measured normal-use latency proves problematic; retain the explicit `--threshold` override for callers that deliberately need a narrower view, but keep the required default at 1.

## Evidence provenance

Clone: `$S/lane`, verified `git rev-parse --show-toplevel` = `/fast/scratch/hyaku/kama-r51/K3Harm/lane`. C2 output copied to the seat out directory as `c2.out`; raw JSON audit output copied as `audit.json`. No tools installed. I did not stop any process owned by another seat.
