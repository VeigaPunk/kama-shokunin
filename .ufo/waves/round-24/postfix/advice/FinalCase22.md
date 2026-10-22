# FinalCase22 — PG22-unknown-citation-incomplete-promisor (reviewer)

VERDICT: **MET on the amended/live view; the registered result is preserved.** No defect found in the assigned scope. The original withdrawn clause stays unmet (not achieved); no promotion, no admission, Git-floor H2 untouched.

## Pins and identities (observed)
- Pin `92063cfc60e217fa7e2098c568578119b16a1b95`, private clone `--no-hardlinks` at `/fast/scratch/hyaku/kama-r24/postfix/FinalCase22/clone` (worktree clean after the run).
- auditor `tools/report-landing-audit.py` = `b9be4f42…3b26f`; grid `tests/report-audit/promisor-grid.py` = `30483830…f270`; expectations `promisor-grid-expectations.json` = `d86b7bea…14cd1`; population `612b0a74…ed88` (all equal to the contract's producer identities; the grid re-read the pinned manifest — no expectation was edited).

## Attempted falsification (executed)
1. `TMPDIR=/fast/scratch/hyaku/kama-r24/postfix/FinalCase22/tmp python3 tests/report-audit/promisor-grid.py --arm current --case PG22-unknown-citation-incomplete-promisor --case PG37-unused-missing-blob-with-fabricated-citation-plain --json --out …/out` → **grid exit 0** (2 cells only; no full grid, no selftest, no mutant driver).
2. Builder-only premise capture (no auditor execution) for both builders → lane promisor facts, hole identity, twin object identity.
3. Read-only probe of the pinned auditor's `missing_reachable()` on a rebuilt PG22 fixture → missing set vs opaque set.

## Decisive observations
- PG22: exit **1** = amended expectation 1 (`met_amended` true, `problems`/`amended_problems` empty); defects exactly `[landed-unresolved $fake, unresolved-full-hash $fake]`, `raw_defects == defects` (no `corrected_by`); verdict document `status: failed`; `stderr` empty; no traceback/`internal_error`/timeout/leak; `objects_acquired {"lane": [], "fleet": []}`.
- PG22 premise really holds: lane `promisor_backed=true` (`remote.origin.promisor=true`, `extensions.partialclone=origin`, remote url = nonexistent `absent-remote.git`), `lane_missing=[b2c475fe…]` = the **unrelated** `notes/unused.txt` blob; fleet not promisor, `fleet_missing=[]`; fabricated token absent everywhere; cited lane commit and tip tree present. So exit 1 is not a vacuous pass over a non-promisor fixture.
- Scoped opacity is the reason, not luck (auditor `tools/report-landing-audit.py:733-810`, `:487-512`): `missing={b2c475fe…}`, `opaque=∅` (the hole is a blob, so the `--filter=blob:none` walk sees no opaque tree/commit), and `$fake` matches no missing oid ⇒ `unknown_citation`/`opaque_hole` do not fire ⇒ the ordinary absent-token findings survive; **no blanket unknown, no whole-tree precondition**.
- Twin: PG22 and PG37 fixtures share identical oids (lane_commit `9bad795e…`, f_blob `56d7b323…`, unused_blob `b2c475fe…`, report_blob `2d90c1fc…`) and differ only by the lane promisor config; the two normalised verdict documents are equal (`twin_equal: true`, `twin_mismatch: []`) — promisor metadata alone changed no verdict, as the amendment requires.
- Original view: `met_original=false` (`exit 1 != 2`) and the grid lists PG22 in `withdrawn_original_failures` ⇒ the original unknown-citation⇒exit-2 registration remains NOT-ACHIEVED, not relabelled.

## Residuals / verification gaps (not exercised here)
- **Authorized corrections are out of PG22's reach**: the grid passes `--no-errata` for this cell (fixture `errata=false`, `errata_rows 0`), so the selected-round errata ledger path (`apply_errata`, `tools/report-landing-audit.py:610-660`) is not exercised by either cell; the target clause "authorized corrections" is verified only by other errata cells, not here.
- The opaque-tree/commit refusal path (blob-only hole here) was not exercised in this seat; the `opaque=∅` probe covers only the negative side.
- Frozen arm (`--arm frozen`) for these two cells was not run; the historical r23 metadata refusal for PG22 is therefore not re-measured by me.
- Grid aggregate here is 2/2 on the two cells I ran — it is **not** a 47/47 claim.
- Raw evidence: `.ufo/waves/round-24/postfix/out/FinalCase22/{run-record.json,grid-current-PG22-PG37.json,grid-current-PG22-PG37.stderr,premise-capture.txt,opacity-probe.txt}`. No installs/upgrades; no production writes.
