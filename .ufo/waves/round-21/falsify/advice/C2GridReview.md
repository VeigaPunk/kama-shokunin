VERDICT: partial - grid outputs reproduce byte-for-byte at a6617149, but unreadable-member and fail-closed coverage are incomplete (hash-time fail-open, grid blind to refusal removal, root-dependent)
Attacked: tests/llamacpp-live/install-links-grid.py @ a6617149722c73d90e142fbdc8154d6967055f7e (NEEDED_SONAMES cells, dev-link cell, hwcaps and unreadable cells, realpath, exit-2 boundary, selftest), plus the producer install_tree/install_links and gate link_chain_problem it drives.
Live lane is NOT at a6617149 (uncommitted edits, section 4). Findings apply to a6617149 unless marked. Evidence with every command and exit: out/C2GridReview/evidence.md.

## 1. Discrepancies vs measured: none
- --selftest rc 0, --arm current rc 0, --arm frozen rc 1, --arm both --json rc 1: all match commands.json.
- Stdout byte-identical to c2-grid-selftest, -current, -frozen, -both .stdout (diff rc 0).

## 2. Findings at a6617149 (severity order)
F1 [medium] Grid cannot see loss of the unreadable refusal. Mutant M1 (producer: remove install_links unreadable branch, kama-llamacpp-live.py:241-242): grid --selftest rc 0 (13/13); grid --arm current rc 0; regular-unreadable reads changed with refused=false. Only the producer's non-root self-test catches it (rc 1). Cause: install_tree drops the member (F2), so the cell passes on "changed", not "refused". Fix: assert refused for regular-unreadable in selftest and run.
F2 [medium] Partial identity on hash-time read error. install_tree `except OSError: continue` (kama-llamacpp-live.py:196-199) drops the member; install_links only probes os.access (:241). Injected EIO on libggml.so.0.27.0: members omit it, problems = [], so main (:1376-1379) would not refuse (code reading; main not executed). Contradicts install_links docstring (:221-222 "instead of recording a partial identity"). Likelihood low [INFERENCE: EIO, or LSM denial on open only].
F3 [low-med] Root-dependent. Under uid 0, os.access(R_OK) is true for mode-0 files (probe: access True, read True). Correct producer under root: grid --selftest rc 1 (3 FAIL: current-catches-all-via-symlinked-tree, controls-both-arms, current-only-exit-0); grid --arm current rc 1 (regular=2/3 wrong=1). Producer unreadable check is conditional on `not os.access(lib, os.R_OK)` (:1155), so it is vacuous under root (root run of M1 returns OK). Fix: verify the chmod took effect (else could-not-evaluate); test with open().
F4 [low] Dev-link coverage: real tree has 5 dev links; grid tests only dev[0]=libggml-base.so (install-links-grid.py:143-146). `if dev:` (:144) silently drops the cell: no-dev-link tree gives rc 0, link=12/12 status=pass.
F5 [low] Gate mislabels "./libllama.so.0.7.0" as "leaves the pinned directory" (check-receipt.py:192-194); it resolves inside the pinned directory. Producer records it with no problem (grid row link-same-resolution-text: changed, no +refused). Producer and gate disagree.
F6 [low] Producer enforces no chain rule at a6617149: dangling, absolute, dotdot and loop soname links are recorded with refused=false (grid rows); only check-receipt rejects them.
F7 [nit] Dangling soname in real tree: rc 1 while the arm line reads status=pass (real_tree_gate_clean=False). Docstring says llama-server's DT_NEEDED lists the soname links; only libllama-server-impl.so does (readelf). `--tree <file>` error does not say "not a directory".
F8 [info] Producer main's refusal branch (:1377-1379) is referenced by no test (grep over lane). Not executed (no-launch bound).

## 3. Confirmed holds
- NEEDED_SONAMES equals exactly the five in-tree soname links NEEDED by any ELF in the tree (49 scanned); dev links are NEEDED by none.
- hwcaps premise is real on this host: ld.so --list resolves libllama.so.0 to the glibc-hwcaps/x86-64-v3/ copy (v3 active, dl_hwcaps_subdirs_active=0x7). Frozen misses it; current refuses it. M6 (non-regular refusal removed) fails grid --selftest, grid run and producer self-test (rc 1 each).
- realpath: symlinked --tree gives JSON identical to measured (rc 0); in-tree links are 10/10 same-directory basenames.
- Exit 2 for missing tree, missing server, missing soname, hwcaps dir, FIFO, unreadable member, and non-git frozen arm; current arm without git rc 0; dangling soname rc 1 (documented).
- Real tree unchanged (ctime 2026-10-20 10:17:53); no leftover mirror dirs.

## 4. Live worktree (uncommitted; snapshot: grid ae248248, producer cec67949, gate 0ba37be3; gate moved during review)
- Closed in worktree: F2 (not-hashed; injected EIO refused), F6 (link-not-to-member), F7 dangling now exit 2 (selftest dangling-real-tree-unpinnable passes).
- F1 consequence closed: M1 on worktree still refused via not-hashed (grid rc 0, producer self-test rc 1); cause attribution still conflated.
- Still present: F3 (conditional check :1194), F4 (single dev cell, :147-150), F5 (gate :194).
- Measured producer e4cc6d88 and gate 6b876437 are a6617149 blobs; a new measurement from the worktree would not be the measured code.
- Lane status: M SCORECARD.md, corpus/SOURCES.md, tests/llamacpp-live/check-receipt.py, install-links-grid.py, tools/kama-llamacpp-live.py, tools/report-landing-audit.py.

## 5. Tools, bounds, disclosures
- No installs or upgrades. Used GNU readelf 2.47, ld.so/ldd glibc 2.44, python 3.14.8, git 2.56.0, sudo -n (passwordless) for four root runs on scratch and read-only inputs.
- One `git status` on the live lane ran without --no-optional-locks (may refresh the index stat cache; no content change). Otherwise the lane was read-only; all grid runs used a scratch clone; no servers; producer main not executed.
- Deliverables in out/C2GridReview/: evidence.md, outputs, boundary-matrix.json, mutant patches, worktree diff. Scratch removed.
