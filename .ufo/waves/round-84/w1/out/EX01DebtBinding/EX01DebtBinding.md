# EX01DebtBinding — C1(a)

Completed byte-complete replacement: `.ufo/waves/round-84/w1/out/EX01DebtBinding/round81-append-debt.py`.

Behavior: pure `grade()` accepts an injectable subject-round callable; after the same-round check it rejects a resolved note/event-round mismatch as `note-wrong-deletion-round`, includes both rounds, and continues. None leaves grading unchanged. `main()` caches per-commit `git log -1 --format=%s` parsing with `^round-([0-9]+):`. Exactly two new selftest arms follow the row-introduction arms; existing cases remain intact.

Evidence at cloned HEAD `eb03a64bcd8e2faab0f4f9bcdc55bfc5c1ed2c85`, all under the same out directory:

- `selftest.out`: pass=31 fail=0, exit 0.
- `fixture.out`: exactly one note-wrong-deletion-round finding (78 versus 79), bad_rows=1, unaccepted=2, exit 1; two count-short findings also retained.
- `real-register.out`: bad_rows=10 unaccepted=1, exit 1. This is the current register summary, not a green integrated claim.
- `red-debt-fixture-before.out`: copied frozen pre-fix receipt, bad_rows=0 unaccepted=1, recorded exit 1, not rerun.
- `replacement.diff`: tool-only patch against HEAD, command exit 0.
- `commands.json`, `install-scratch.out`, and `README.md`: exact executed commands, actual exits, scratch setup/cleanup, scope and integration notes.

Risks: full C1 remains dependent on sibling stale-row rotation, acceptance row, and gate integration. No gate/mutation/network checks run. LSP unavailable in mounted tool inventory; no tools installed. Exclusive scratch was removed after evidence retention. No production files, registers, gates, commits, or external state changed.

Path restriction: this report is retained inside the seat-exclusive out directory, honoring the explicit write-only-own-directory contract; the requested outside-out trailer destination `.ufo/waves/round-84/w1/EX01DebtBinding.md` is left for the L1 integration owner to populate.
