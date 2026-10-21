VERDICT: partial - default member set and tree_sha() check out, but absent default members are silently dropped (or, if all absent, silently substituted), so the absent-member check is refuted on the lane file; a 3-line fix is in out/ and tested in my copy only.

# GridDefaults - tests/llamacpp-live/install-tree-grid.py (round 19)

Subject: lane file at sha256 49a42f81ac06... (a sibling added --selftest during this seat; I re-synced and re-ran on that version). Lane not modified. Workspace /tmp/kama-r19-GridDefaults; receipts and exit codes in its out/RECEIPT.md and out/receipt-grid-compare.json. No installs.

## Checks
1. Default set exists in receipt - CONFIRMED. All 11 receipts (round-16/17/18 live, round-18 live-recovery) contain libggml-base.so.0.27.0, libllama-common.so.0.7.0 and libllama.so.0.7.0, n=51, with full digests equal to the real tree (out/defaults-vs-receipts.json). The real tree has 51 regular files; all three defaults are regular, not symlinks.
2. tree_sha() matches producer - CONFIRMED. Producer install_tree() (tools/kama-llamacpp-live.py:178-202) on the real tree gives combined 6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c. Grid tree_sha() (lane :32-34) and gate install_tree_sha() (check-receipt.py:165-170) return the same value, and stored install_tree_sha256 equals it on all 11 receipts. Same formula: sorted names, "name sha\n" lines, sha256 of utf-8.
3. Absent members reported, not skipped - REFUTED on lane file.
   - Lane :80 `members = args.members or [m for m in DEFAULT_MEMBERS if m in tree]` drops an absent default with no row. R6 (libllama-common removed, digest recomputed, pinned): members=2 rejected=2/2, exit 0, no mention of the dropped member.
   - Lane :81-82 `if not members: members = sorted(tree)[:3]` substitutes arbitrary members. R7 (all three removed): ran LICENSE, ggml-rpc-server, libggml-cpu-alderlake.so, rejected=3/3, exit 0.
   - Explicit --members absent is reported (status absent, R8) but exits 1, the same code as a surviving mutant.

## Fix (out/install-tree-grid.patch, applied in my copy only)
- Lane :80-82 becomes `members = args.members or list(DEFAULT_MEMBERS)`.
- Results: R5/R6/R7 print absent rows and exit 1 (R7 now 3 absent, rejected=0/3). R2, R3, R4, R8, R9 unchanged. Sibling's --selftest exits 0 on both versions.
- Exit stays 1 deliberately: the new --selftest "absent member" case pins explicit-absent to exit 1. Moving to 2 changes that expectation too - owner decision.
- [INFERENCE] the hunk applies to lane 49a42f81 by context (lines outside the sibling's hunks). Not verified against a lane merge.

## Not fixed here (flag to owner)
- Attribution gap: the grid counts any non-zero gate exit as "rejected". R9 (fake gate rejecting everything) gives rejected=3/3, exit 0. For the real gate the reason is right: R4 stdout names server.install_tree_sha256 for each mutant. Suggest requiring gate exit 1 plus that problem line.
- Producer silent skip: tools/kama-llamacpp-live.py:198-199 `except OSError: continue` drops an unreadable regular file from install_tree and from the combined digest (R10: locked.so absent, uid 1000). A receipt can be self-consistent yet incomplete; the grid cannot see it.
- [INFERENCE] DEFAULT_MEMBERS hard-codes .0.27.0 / .0.7.0. A llama.cpp bump would, on the lane file, silently measure other files (the R7 behavior).

## Checks main agent should run after integration
- `python3 tests/llamacpp-live/install-tree-grid.py --selftest` (expect exit 0)
- pinned grid on .ufo/waves/round-18/live-recovery/receipt-1.json with --tree-sha 6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c (expect exit 0, rejected=3/3)
- pre-pin grid on the same receipt (expect exit 1, rejected=0/3)
- after applying the patch: pinned grid with one default removed from a copy receipt (expect exit 1 and an absent row)
