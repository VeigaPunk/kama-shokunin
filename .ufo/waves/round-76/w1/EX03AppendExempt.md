# rev=1a85a991fce5b76b60f88a5cab3df98d253b1a4a
# EX03 — C3 counter and strictly admissible register

Axis: freshness. Outcome: honest frozen-target miss; no green claim.

## Implementation

`tools/round76-append-exempt.py` preserves the frozen PREDICATE constant, executes the audit, reads both registers and the contract at the audit's explicit `to` revision, reuses round75 line-bound validation, derives deleted-line parent sections using frozen audit helpers, and applies the earliest combined register introduction cutoff. It reports missing accounting, class/count/section mismatch, duplicate and temporal findings; unreadable required inputs/CLI misuse exit2. Restoration must remain held at audit revision. No worktree-register fallback.

Per L1 KamaR76's final strict-row ruling, `registry/append-only-exempt.tsv` now contains ONLY the 47 strictly admissible rows, not all83 proposed rows. This intentionally supersedes the original 83-row request; L1 accepted the target as unsatisfiable. No commit was made (seat prohibition).

## Exact retained evidence

Executed the assigned read-only audit input `python3 tools/append-only-audit.py --repo <absolute-lane> --json`, exit1 at the revision above. Actual JSON summary: events232 restored91 unrestored53 ungraded83 disclosed5, ungraded_lines341; bad_declarations/bad_disclosures/regressed/vanished/unmatched/binary all zero. `before.out` retains its extracted JSON summary, NOT a full byte transcript.

Classified the actual 83 ungraded events while constructing the register, using the audit's deleted_lines/sections/file_regions helpers and read-only git ancestry against cutoff `10f37171fb696c542586cbee96ea4a509ab74afc`:

- strictly-admissible: 47 events, retained as rows;
- wrong-class: 31 events, omitted;
- post-introduction: 5 additional events, omitted;
- total omitted/unaccounted class events: 36.

`register-rows.txt` retains these counts and the actual 47-row histogram exempt-head47. The 31/5 breakdown is exclusive (class failure checked first). Earlier CR01 peer output counted10 post-introduction FINDING INSTANCES, not10 distinct events: the counter emits two temporal diagnostics for each invalid class row. That peer output was not rerun here.

Counter and selftest execution were NOT performed under the fleet role's editing-wave check prohibition. `after.out` and `selftest.out` explicitly say NOT RUN; they are status records, not passing command receipts. There is no measured APPEND_EXEMPT verdict line or rotation-fixture result from this seat. Module imports were used only to derive assigned register data, not to execute verdict/selftest checks.

## Frozen contradictions and L1 disposition

1. Frozen missing-register exit2 contradicts requested absent-register before exit1. Preserved frozen exit2.
2. Audit v6 event JSON (source lines719-724) has no exemption class or section list. `status=ungraded` includes A-row permitted and only-prefix exclusions, not solely exempt-section deletions. Frozen all-deleted-parent-sections-exempt condition excludes31 events. Proposed name `exempt-head` comes from the plan's motivating description, NOT an audit-emitted class; no new exemption category is accepted.
3. The earliest combined register introduction excludes5 otherwise eligible events. Adding the new class register in a separate commit also raises combined introductions above the literal target1. Preserved frozen combined-history rule.
4. Newly written register is uncommitted; default committed-to reads cannot see it. Only parent can integrate/commit, and missing events remain honest findings afterward.

L1 initially requested separate cutoffs/fixed-base interpretation. Reported that as inconsistent with literal frozen rule and did not adopt it. L1 then explicitly ruled: preserve frozen rule, admit only strict rows, record C3 as `frozen-target-unsatisfiable`. Applied that final register ruling. L1 owns lesson changes; no plan/frozen module/other seat file changed.

## Parent-owned execution

Five named selftest arms are implemented: missing-row, wrong-count, wrong-class, rotation-reintroduced, audit-fixture-green. Actual audit data feeds generated fixtures. Rotation currently injects introduction/ancestry facts into grade; it is NOT an actual git delete/re-add fixture. Parent must execute a real reintroduction history fixture to exercise discovery end-to-end. The green arm exposes the frozen population contradiction rather than bypassing it.

Parent checks: counter default (missing committed register currently exit2), `--selftest`, real register delete/re-add fixture, then committed after capture with revision header. Do not treat NOT RUN status files as completed passing receipts. No check was outsourced; independent peer observations are attributed above.

LSP unavailable in mounted inventory; source definitions inspected with read. No tools installed/upgraded. No scratch created. No git/jj mutation, commit, push, external substrate change, or writes outside assigned paths.

Self-evaluation: accuracy4 (runtime unverified), completeness2 (frozen target impossible; real rotation fixture absent), clarity4 (distinct event/finding counts), actionability4 (parent checks/blockers explicit), conciseness3 (multiple contradictions). Overall3.4/5. Honest miss accepted by L1; cannot improve completeness by silently changing frozen eligibility.
