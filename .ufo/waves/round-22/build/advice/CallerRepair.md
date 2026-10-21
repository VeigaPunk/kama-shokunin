# CallerRepair — install_tree consumers (round 22)

## Scope and provenance

Axes: fail-closed correctness, legacy compatibility, root-independent operability, and minimal caller changes.

This is a resumed report: the original turn terminal-failed on capacity; the same seat resumed, created its required isolated clone, and edited only the two assigned sandbox files. Parent reported that L1 had already integrated canonical caller changes in the lane. I made no lane code edits, ran no checks, and did not reconcile or copy the sandbox draft into the lane.

Owned sandbox paths:
- `.ufo/waves/round-22/build/sandboxes/CallerRepair/tests/llamacpp-live/install-links-grid.py`
- `.ufo/waves/round-22/build/sandboxes/CallerRepair/tests/llamacpp-live/unpinnable-e2e.py`

## Sandbox draft behavior

- `install-links-grid.py`: `identity()` catches the dynamically loaded producer module's own `module.SetupError`. A refusal becomes an identity with null tree/link digests and a nonempty `problems` list, so a mutated cell is classified as changed and refused instead of falling through the grid's evaluation-error exit. Successful tuple handling is unchanged.
- Replaced `regular-unreadable`'s `chmod(..., 0)` with a scoped `sha256_file` mock that injects EACCES for the selected exact regular-member path and requires the injection to fire. The same cell exercises both arms: frozen still returns a digest omitting that member (red/before), while current refusal is recorded as changed+refused. Removed the mode-reset cleanup, which is no longer needed. This avoids root-sensitive permission semantics.
- `unpinnable-e2e.py`: converts a `SetupError` during its in-process pristine scan to `RuntimeError`, allowing the existing outer boundary to report `could-not-evaluate`/exit 2 rather than an uncaught traceback/exit 1. Receipt grading accepts either the declared bare `install-tree-unpinnable` token or a colon-qualified legacy/detail token; the existing child/argv pre-launch checks remain.

Frozen behavior is not rewritten: only the test's failure injection changed. The historical arm's swallowed read failure remains the intended red control. Successful return values and the ordinary symlink/nonregular cases are not altered. The matrix owns listdir/lstat fault rows and pinned positive digest controls; no endpoint-health or authentication claim is made.

## Difference from the integrated lane state (read-only observation)

The lane files read after the parent notice contain L1's integration, and differ from this isolated draft:

- Lane `install-links-grid.py` catches `module.SetupError` for `with_links=True` and returns `setup_error`/`problems`/`unpinned`, but retains the chmod-based `regular-unreadable` cell and mode-reset cleanup (`:169-170`, `:239-250`). The sandbox instead supplies null digest fields and a deterministic mock fault, eliminating root dependence.
- Lane `unpinnable-e2e.py` has the same exit-2 conversion with different wording (`pristine identity unavailable`) but still requires `setup.startswith('install-tree-unpinnable:')`. The sandbox accepts both the shared-interface bare token and colon-qualified receipts.
- No source from this sandbox was integrated by this seat. L1 owns any further lane decision.

## Matrix/API agreement needed

The shared interface declares `SetupError('install-tree-unpinnable')`, and Matrix.md:7 says its refusal oracle requires that exact `.code`. The integrated lane producer currently emits colon-qualified values at `tools/kama-llamacpp-live.py:188-203` (`...:listdir:...`, `...:lstat:...`, `...:read:...`). Matrix/API owners should align this final code contract: under the currently observed producer text, an exact-bare Matrix oracle would not accept those current-arm refusals. MatrixMutation described the bare value as its planned contract, not as an executed confirmation. The e2e draft tolerates both forms; no Matrix code was edited here.

## Evidence, checks, and risks

Source evidence: pre-integration caller observations in `CallLinks.md` and `CallE2E.md`; lane integration read at `tests/llamacpp-live/install-links-grid.py:177-190`, `tests/llamacpp-live/unpinnable-e2e.py:73-97`, and `tools/kama-llamacpp-live.py:178-206`; Matrix refusal contract at `Matrix.md:7`. These are source observations only, not execution evidence.

No build, test, lint, formatter, or smoke check was run. No tool was installed. Remaining risk: this sandbox's deterministic readability case and bare-token receipt acceptance differ from the already-integrated lane callers; L1 should decide whether to adopt those deltas and align the Matrix/API token contract after the wave.

Report: `.ufo/waves/round-22/build/advice/CallerRepair.md`

## Addendum — token-shape clarification

After the initial report was written, MatrixMutation reported static confirmation from the ApiFix draft: `SetupError.code` is the bare `install-tree-unpinnable`, with detail stored separately, while producer receipt serialization adds the detail suffix. The exact-code Matrix oracle aligns with that ApiFix draft; this is static confirmation, not a run. The lane producer source snapshot read for the initial report instead passed colon-qualified strings as the `SetupError` code. These observations describe differing source snapshots; this seat did not reconcile them or edit the lane. The e2e draft grades the receipt shape and therefore accepts either the bare token or its colon-qualified detail form.

L1 should ensure the integrated producer keeps the bare `.code` contract expected by Matrix while preserving receipt detail serialization. No Matrix changes were made here.
