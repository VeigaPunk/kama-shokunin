VERDICT: confirm - a null install_tree_sha256 with --expect-install-tree-sha256 exits 1 INVALID, and the sole problem names server.install_tree_sha256; without the pin the null form is VALID (open gap; candidate guard verified on lane bytes, not applied)

# C2NullTree - null install_tree_sha256 with the pin

Scope: copy /tmp/kama-r19-C2NullTree; this run wrote no lane file except this report. Receipts, exact argv and exits: /tmp/kama-r19-C2NullTree/out/C2NullTree/ (COMMANDS.md, manifest.json, candidate/, candidate-lane/). Every claim below was executed; unexecuted reasoning is tagged [INFERENCE].

## Assigned result: confirmed

| Arm (base: round-18 live-recovery receipt-1, schema v3, outcome pass) | Pin | Exit | Output |
|---|---|---|---|
| A1: server.install_tree_sha256 = null | --expect-install-tree-sha256 | 1 | `INVALID ...: 1 problem(s)` / `- --expect-install-tree-sha256 given but receipt has no server.install_tree_sha256 digest` |
| A2: same receipt | none | 0 | `VALID` |

The pin is the sole cause. Key-absent (A3) and empty-tree null (A4) give the same message. Checked on the copy gate (sha afc9e79b...) and on the lane's current gate bytes (sha 10912f24...): identical exit and stdout.

## Findings

1. [Medium] Without the pin, a null digest disables the recomputation. VALID, exit 0: A2, A5; C x3 (member swapped, digest nulled); D0 and D2 (impl digest nulled). Recomputed-digest swaps (B x3) are also VALID without the pin and are rejected 3/3 with it. The grid reproduces the C2 numbers: no pin `baseline=VALID members=3 rejected=0/3` (exit 1); with pin `rejected=3/3` (exit 0). The null form is at least as weak as the recomputed form without the pin, and the grid never measures it.
2. [Low] Selftest coverage. The lane's current selftest has `tree-sha-absent-expect` (null plus pin), which was added after my copy by someone other than me. No arm covers a null digest without the pin, for either the tree or the impl digest. `impl-digest-absent-expect` is pinned.
3. [Low, residual] Empty-tree erasure: install_tree {} plus a null digest without the pin is VALID (A5). This is the falsify S2 class; the candidate below does not close it.

## Candidate (OUT only; lane not changed)

Two guards inserted after `check_digest` in check-receipt.py:
- (a) install_tree non-empty and install_tree_sha256 is None -> bad("server.install_tree_sha256 is null but server.install_tree has members ...").
- (b) server_impl_sha256 is None while libllama-server-impl.so is in install_tree -> bad("server.server_impl_sha256 is null but install_tree contains ...").

Verified on lane bytes (out/C2NullTree/candidate-lane/, candidate-lane-diff.json):
- Candidate selftest exit 0 (76 mutations rejected; 6 valid accepted).
- 11/11 committed receipts identical in both pin modes.
- Without the pin, 13 files flip VALID -> INVALID (A1, A2, A3, C x6, D0, D1, D2, D3).
- With the pin, the tree-null arms stay INVALID and gain a second problem line naming the field; D0 and D1 flip VALID -> INVALID (impl digest null).
- Unchanged in both modes: A0, A4, A5, B x6, D4.

Producer consistency (code read, tools/kama-llamacpp-live.py:178-202 and 1267-1283): the tree digest is None only on listdir failure, where tree = {}; impl is None only when the file is absent. Neither guard fires on those shapes. [INFERENCE: producer outputs beyond the committed receipts were not exercised.]

Suggested L1 follow-up: add guards (a) and (b), and selftest arms `tree-sha-null-no-pin` and `impl-digest-null-no-pin` (expect 1). I did not edit the lane.

## Lane drift observed

- check-receipt.py: lane sha 10912f24... differs from my copy's afc9e79b... by 6 added selftest lines. Gate logic is identical on all 34 targets (exit and stdout); re-verified.
- tools/citation-provenance.py: modified in the lane at 03:37:55, after my copy. I did not execute or write it.

## Verification gaps

- Grid and receipt numbers come from the copy, not official measurements (L1 owns those).
- Finding 3 and the missing no-pin selftest arms are not fixed in the lane; the candidate is not merged.
- Installs: none. Servers: none started (`pgrep -x llama-server` exit 1).
