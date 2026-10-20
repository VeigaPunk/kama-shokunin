# Round 13 — ReviewExit: KQ16 exit-map correction vs static fidelity.py precedence

Lane: KamaR13.ReviewExit (leaf reviewer). Scope: static review only. No fidelity.py execution, no tests, no builds, no gate runs. Tools installed or updated: none.

## Status of the target

At review time `corpus/QUALITY.md` has 49 lines; its last row is KQ15 (line 49). No KQ16 text has landed, and `.ufo/waves/round-13/advice/` contained only `swarm-registry.json`. This review therefore checks the proposed literal phrases from the round-13 shared contract (`dispatch.json`, Criterion item) against the code. Re-review is needed when the KQ16 row lands.

Proposed literal phrases under review:
- `source_mismatch=1; snapshot_tampered=2; source_unavailable=2`
- `capture: git show; comparison: git cat-file blob`

## Static precedence (from `.ufo/waves/round-12/fidelity.py`, read only)

- `PRIORITY` tuple, lines 64-72: `snapshot_unavailable, manifest_invalid, snapshot_tampered, source_unavailable, source_mismatch, unpinned, clean`.
- Finding selection, lines 317-318: the first PRIORITY id present in `findings` becomes `finding`.
- Exit mapping, line 319: `exit = 0 if finding == 'clean' else (1 if finding == 'source_mismatch' else 2)`.
- Exception path, lines 611-622: `internal_error` is returned with exit 2 directly, outside PRIORITY.

Consequence: exit 1 occurs only when `source_mismatch` is the top-ranked finding. Exit 2 is returned for every other non-clean finding.

Per-finding exit classes, as emitted by the code:

| Finding id | Emitted at | Exit |
|---|---|---|
| `source_mismatch` | lines 304-310 | 1 only if top-ranked |
| `snapshot_tampered` | lines 233-236 | 2 |
| `source_unavailable` | lines 254, 265, 276, 289 | 2 |
| `snapshot_unavailable` | lines 215-216 | 2 |
| `manifest_invalid` | line 225 (from `load_manifest` raises) | 2 |
| `unpinned` | lines 238-241 | 2 (ranked below source_mismatch) |
| `internal_error` | lines 614-618 | 2 |

## Case table (derived by reading lines 201-336 and 317-319)

| Inputs | Findings | Finding | Exit | Consistent with proposed phrase? |
|---|---|---|---|---|
| Snapshot unreadable | snapshot_unavailable | snapshot_unavailable | 2 | yes (exit-2 set) |
| Explicit manifest invalid, snapshot differs | manifest_invalid, source_mismatch | manifest_invalid | 2 | yes, but `source_mismatch=1` must be qualified |
| Valid manifest, pin mismatch, source matches | snapshot_tampered | snapshot_tampered | 2 | yes |
| Valid manifest, pin mismatch, source differs (selftest `snapshot-tampered`) | snapshot_tampered, source_mismatch | snapshot_tampered | 2, mismatches=1 | yes for exit; proves `source_mismatch=1` is not unconditional |
| Anchor (oid/sha/bytes) fails on retrieved blob | source_unavailable (+ source_mismatch if snapshot differs) | source_unavailable | 2, mismatches=0 | yes |
| Retrieval fails (empty repo) | source_unavailable | source_unavailable | 2 | yes |
| No manifest, snapshot differs (`before` receipt) | unpinned, source_mismatch | source_mismatch | 1 | yes; unpinned does NOT outrank it |
| Valid coherent manifest, snapshot differs (`coherent` case) | source_mismatch | source_mismatch | 1 | yes |
| No manifest, snapshot matches | unpinned | unpinned | 2 | yes; not clean |
| All match | none | clean | 0 | yes |

## Findings

### F1 — medium: `source_mismatch=1` is unqualified and misleading as written
Evidence: `fidelity.py:317-319`; selftest case `snapshot-tampered` (`fidelity.py:499-505`) expects exit 2 with `finding=snapshot_tampered` while `mismatches=1`. A reader of the bare literal `source_mismatch=1` could conclude that any byte mismatch exits 1. The code makes exit 1 conditional on no other exit-2 finding being present.
Fix for the Criterion writer: keep the literal phrase exact and add the qualifier in the same sentence, e.g. "exit 1 only when no other non-clean finding is present".

### F2 — medium: the exit-2 set in the literal phrase is incomplete
Evidence: the phrase names only `snapshot_tampered` and `source_unavailable` for exit 2. The code also emits exit 2 for `snapshot_unavailable` (line 215), `manifest_invalid` (line 225), `unpinned` (line 239) and `internal_error` (line 618). The registry (`SKILL.md:396`) and fidelity docstring (`fidelity.py:24-26`) both list them.
Fix: add "every other non-clean finding (snapshot_unavailable, manifest_invalid, unpinned, internal_error) is also exit 2; clean is 0" after the literal phrase. Without this, the correction is not a complete exit map.

### F3 — medium: `fidelity.py` header comment contradicts its own PRIORITY tuple
Evidence: header lines 55-56 say "Every exit-2 finding outranks source_mismatch (exit 1)". `unpinned` is exit 2 (line 319) but sits after `source_mismatch` in PRIORITY (lines 69-70). Counterexample: no manifest plus a differing snapshot gives `unpinned` and `source_mismatch`, and the code returns exit 1 (receipt `before`; selftest `unpinned-source-mismatch`, `fidelity.py:532-536`, expects exit 1). The docstring (lines 20-22) and registry (`SKILL.md:399-401`) both say an unpinned mismatch is exit 1, which matches the code. The header is the outlier.
Fix: the KQ16 text must not cite the header as precedence authority; cite PRIORITY (lines 64-72) and the docstring. The counterexample should be marked in the round-13 lesson (lesson owner's write set, not this seat's). The round-12 `fidelity.py` is not edited: it is immutable, receipt-bearing gate code.

### F4 — low/medium: "capture: git show" is authored registry provenance, not checker-verified (corrected)
Correction to the earlier draft: that draft said `SKILL.md` contains neither `git show` nor `cat-file`, and that the verifier lesson's registry claim was only half true. Both statements were wrong. Raw `SKILL.md:396` states that the default snapshot `.ufo/waves/round-12/frozen/corpus/SOURCES.md` was "captured byte-exactly via `git show`, never tool-rendered text". The registry does distinguish capture from comparison, so the verifier lesson's claim at `corpus/lessons/round-12-verifier-spotcheck.md:147` is accurate on that point.
Remaining evidence, unchanged:
- `fidelity.py:261-273` and `reproduce.py:79-80` use only `rev-parse --verify` and `git cat-file blob`. Neither invokes `git show`. So the comparison half is machine-checked; the capture half is not.
- No committed round-12 receipt records the command that produced `frozen/corpus/SOURCES.md`. The `git show` provenance rests on the registry text, `corpus/lessons/round-12.md:14`, and S032 (`corpus/SOURCES.md:44`).
- Dispatch cites "S033 Git cat-file"; `corpus/SOURCES.md` has no S033 row at review time, so do not cite S033 until the row lands.
Fix: KQ16 may state `capture: git show` as the authored method, citing `SKILL.md:396` and S032, and must state that fidelity.py enforces only the `git cat-file blob` comparison.

### F5 — low, outside the two routed propositions: KQ15 wording narrower than code
Evidence: KQ15 (`corpus/QUALITY.md:49`) says an overridden snapshot without its manifest "may only expose a mismatch". For a matching overridden snapshot the code yields `unpinned` (exit 2), not a mismatch (`fidelity.py:237-241`; selftest `unpinned-matching-snapshot-is-not-clean`, lines 526-530). The "never authorize a pass" half is correct.
Status: the dispatch says "rest KQ15 preserved", so this is not in the fixed two-proposition denominator. It is recorded for L1's decision and is not a blocker for KQ16.

## Verified correct (static)
- Exit classes for `source_mismatch` (1), `snapshot_tampered` (2) and `source_unavailable` (2) match the code (`fidelity.py:234, 254-289, 305, 319`).
- "Distinct finding ids with shared exit 2" is accurate for tamper versus unavailable (both exit 2, distinct ids).
- The `git cat-file blob` comparison half is accurate (`fidelity.py:271-273`).
- The mismatch counter (`fidelity.py:323`) counts only anchored correspondence failures, consistent with the docstring.

## Residual risk and verification gaps
- All findings are static reads. No execution, per assignment. The case table is a hand trace of the code, not an observed run; round-12 receipts in `acceptance.json` are reused only as "receipt observations", not new results.
- KQ16 is not yet present; F1-F2 apply to the proposed literal phrases and must be re-checked against the landed text.
- Whether the frozen snapshot was actually produced by `git show` is documented (F4) but not verified by any committed command record.

## Coordination
`KamaR13.Criterion` was messaged with the F1-F3 fixes. Re-read the Criterion row when notified; the F4 correction affects only the capture-half wording.

## Final static verdict on landed KQ16 (QUALITY.md:61; SKILL.md:409-436)

Read-only, static, no checks executed. Verdict: **substantively correct; one precision defect remains, plus the requested wording fix is present.**

Verified against `fidelity.py` (round-12, unchanged):
- Primary-finding rule: exit is that of the first `PRIORITY` id present (lines 64-72, 317-319); `source_mismatch=1; snapshot_tampered=2; source_unavailable=2` is correct for the ids named.
- "`source_mismatch` yields exit 1 only when it is the selected primary finding and no higher-precedence could-not-evaluate finding is present" is correct; `unpinned` is correctly not described as outranking it.
- Other exit-2 ids (`snapshot_unavailable`, `manifest_invalid`, `unpinned`, `internal_error`) match lines 215, 225, 239, 614-618.
- Overridden snapshot without manifest: matching bytes yield `unpinned` exit 2; byte mismatch yields `source_mismatch` (lines 186-190, 237-241).
- Comparator: `rev-parse --verify` plus `cat-file blob` (lines 261-273); anchor check on OID/sha/bytes (lines 283-285). `git show` is documented as capture only, consistent with SKILL.md:396 and S032 (SOURCES.md:44). S033 now exists (SOURCES.md:45).
- Wording fix applied: "a textual gate does not establish semantic admission" is present in the row's reject clause.

**Defect (precision, must fix in the KQ16 row before it is relied on):** the sentence "A byte mismatch that co-occurs with a higher-precedence finding exits 2 while the correspondence count still records the mismatch" is true only when the anchor verified. `mismatches` is `int(source_matches is False and anchor_matches is True)` (fidelity.py:323). When `source_unavailable` comes from an anchor failure (retrieved blob's oid/sha/bytes wrong) and the snapshot differs, the finding is `source_unavailable` (exit 2) and `mismatches` is 0. Fix: add "when the pinned anchor verified" after "correspondence count still records the mismatch", or equivalent. The registry's "Notes" and fidelity docstring do not make this claim, so only the KQ16 row needs the qualifier.

Residual, not blocking: SKILL.md registry row for `measure.py` was not reviewed here (ReviewProbe's item). The KQ16 row's lesson citation (`lessons/round-13.md`) was not reviewed beyond existence.

Checks executed: none. Tools installed or updated: none.
