# Round 58 — execution-bound battery checker and closure-pointer binding

Author: KamaR58. Base: `2f53614e6f5895560edb775cc3e74841aa0dd44c`. Pre-data freeze: `dcd69473dd7e33b316e2ba238a48e5119a6cd809`; base and do-nothing control receipts: `cb1ef10228193d2134440bca1175bf560b2e67be` (both before any seat result).

## Claims

- C1 — operability 8→8: `tools/round58-battery-exec-check.py` accepts the genuine round-56 battery and 3/3 behaviour-preserving rewrites and rejects 11/11 enumerated no-op variants whose roster literal is intact, 0 evaluation errors (frozen counter `tools/round58-c1-counter.py`, variants `tests/round58-battery-variants/`). Sourced on S517.
- C2 — calibration 7→7: the SCORECARD calibration row's "latest outside closure" pointer names the highest-numbered verifier-spotcheck, repeats that round in "including round N" and carries the verdict token the fleet MANIFEST holds for kama lane_round N, and `tools/round42-selfdesc-reconcile.py` reports 0 mismatches (frozen counter `tools/round58-c2-counter.py`).

Predicates and kill rules: `.ufo/waves/round-58/controls/freeze.txt`.

## Gate

**S517 — ADMIT, tier A, mined.** https://docs.python.org/3/library/sys.html#sys.setprofile, accessed 2026-10-27 (page title "Python 3.15.2 documentation", "Last updated on Oct 27, 2026 (16:42 UTC)"). Located quote: “only on call and return, but the return event is reported even when an exception has been set” (18 words, verified present in the fetched page text). Grounds `teaches`: a profile hook sees frame entry, not line execution, so the checker pairs each watched frame with recorded stubbed side effects. Cited by `tools/round58-battery-exec-check.py`.

**S518 — ADMIT, tier A, mined; supersedes S513 as claim-scoped (the S513 reject is limited, not erased).** https://man7.org/linux/man-pages/man8/ld.so.8.html, accessed 2026-10-27 by live fetch (curl exit 0; sha256 `d9b7737e6c9a38f6c7ce11a4feec834704d6ad5139dc790afa9798faf0379f83`, byte-identical to the round-56 snapshot `.ufo/waves/round-56/sources/ld.so.8.html`); Linux man-pages 6.19, 2026-08-03. Located quote: “LD_AUDIT is ignored in secure-execution mode.” (6 words). I re-searched the committed rtld-audit(7) snapshot (S512) for `secure-execution` and `$ORIGIN`: neither occurs (only the unrelated `LA_SER_SECURE`), so S513's reason ("overlaps the dedicated rtld-audit(7) source for the claim's only need") was false for exactly the topics its own flip condition named. The round-56 outside closure (`corpus/lessons/round-56-verifier-spotcheck.md`) and round-57 closure (`corpus/lessons/round-57-verifier-spotcheck.md`, row S513) both disagreed; this round agrees with them on the topics the flip names. Dissent on record: seats Q03Source513Reopen and K10S513Disagreement (lane-dispatched, advisory) recommend keeping S513 rejected for the narrow LD_AUDIT name-presence claim, because rtld-audit(7) suffices for that claim; that is compatible with S518: S513 stays rejected for name detection and S518 records the delta (secure-execution, tokens) for a later claim on those topics. Criterion taught: `corpus/QUALITY.md` KQ98 (probe and controls under `.ufo/waves/round-58/w1/out/W03QualityCriterion/`). S513's row is unchanged (rule 2: a correction is a new row); status/recheck/used-by of every existing row: unchanged.

**S517 and S518 census:** `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` start exit 0 / 257 rows (`.ufo/waves/round-58/census/start.out`).

**Spot-check set for the non-author closure:** admit S517 (re-open the page, locate the quote); admit S518 (re-open the page, locate the quote, search S512's snapshot for `secure-execution`); reject carried forward: none new this round, the overturned reject is S513 (the closure may re-open it). Dispatched seats are the lane; their findings are advisory.

Assimilation: none. `considerthese/2026-10-26.md` was opened; no new proposal was implemented this round.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| false-status-claim | SCORECARD calibration row stated round 56 "(admitted)"; MANIFEST holds round 56 `rejected-honest-stop` (`corpus/lessons/round-57-verifier-spotcheck.md` Claims re-check). Frozen base counter: `closure pointer verdict=1 stale=1 including=1` (`.ufo/waves/round-58/controls/c2-base.out`). | none: the round-42 counter checked a count, not the status token. | `tools/round58-c2-counter.py` binds the pointer's round and token to the fleet MANIFEST; controls with the claim deleted or the token flipped fail it (`controls/c2-ctl-*.out`). |
| syntactic-call-site-as-execution | Round-57 checker accepted dead-code and unused-function no-ops (`corpus/lessons/round-57.md` Mistakes; base counter `noop_rejected=1/11`, `controls/c1-base-r57-checker.out`). | none: round-57's selftest found it after filing. | Execution-bound checker under a hermetic harness; frozen counter with 11 enumerated no-ops; do-nothing checkers (always-accept/reject, hash-only, base) fail the counter. |
| discernment-disagreement-unlearned | S513 reject disagreed with by closures 56 and 57; round 57 left it unlearned (`corpus/lessons/round-57.md` Mistakes). | outside closures. | S518 supersedes S513 after re-reading both pages; see Gate. KQ98 added to `corpus/QUALITY.md` (seat W03QualityCriterion's probe reproduces both closures' disagreement: frozen S513 row `supported=0 delta=3`, exit 1). |
| stale-count-recurrence | The verifier-spotcheck count in the same row went stale again within one round: the row said 43 after round 56; the round-57 closure made it 44 (`python3 tools/round42-selfdesc-reconcile.py --repo . --tip 2f53614e` printed `mismatches=1`). | none: any hard-coded count is stale after the next closure by construction. | The row says the count is re-derived at the measured tip; the closure pointer is graded against the ledger, not against a typed number. Residual: the typed `44` still goes stale after round 58's closure; reported, not fixed. |

**Gate correction (same round, before any outside reading):** the S517 anchor first read "Python 3.14 docs"; the fetched page title is "Python 3.15.2 documentation" (the local interpreter is 3.14.8; I mislabelled the page by the interpreter). S517's anchor cell was corrected in place in the same round the row was added; the base-to-tip append-only comparison sees S517 only as an added row.

## Census before → after

Before: exit 0, 257 rows (`.ufo/waves/round-58/census/start.out`). After: recorded at round end (`.ufo/waves/round-58/census/end.out`).
