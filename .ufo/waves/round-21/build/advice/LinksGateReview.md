VERDICT: confirm - C2 gate diff reproduces at a29bb84 (selftest 9+1/90 exit 0; the 13 new invalid cases fail for their intended reasons; producer and gate digests agree on the real tree; no committed-receipt verdict change); residual MEDIUM risks F1-F2.

# C2 gate review (check-receipt.py) - KamaR21.LinksGateReview-6
Scope: tests/llamacpp-live/check-receipt.py, 7a6bc911 -> a29bb84 (+121/-2, six hunks). Read-only; stdlib only; python3 3.14.8 as installed (no installs, no upgrades). Snapshots via `git archive` into scratch. Logs: .ufo/waves/round-21/build/out/LinksGateReview/.

## Executed (exit)
- `git diff 7a6bc911 a29bb84 -- tests/llamacpp-live/check-receipt.py` -> 0 (out/check-receipt-C2.diff); producer diff `-- tools/kama-llamacpp-live.py` -> 0
- `check-receipt.py --selftest` base -> 0: 6 VALID + 1 NOT-EVALUATED, 77 mutations; head -> 0: 9 VALID + 1 NOT-EVALUATED, 90 mutations
- `driver_cases.py base|head` -> 0|0: per-case exit and gate stdout, 84 and 100 cases (out/selftest-cases-*.txt)
- `receipt_gate_matrix.py` -> 0: receipts 1-3 x 10 argument sets x {base, head} = 60 gate runs (out/receipt-matrix-stdout.txt)
- `synthetic_link_checks.py` -> 0: real-tree digests, synthetic retarget/dangling/form/surrogate cases (out/synthetic-stdout.txt)
- `git grep -n expect-install-links a29bb84 -- ':!.ufo'` -> 0: only check-receipt.py references the flag
- `sha256sum` of lane receipts = snapshot blobs -> 0; `pgrep -af` for leftover processes -> 1 (none)

## Findings (severity order)
- F1 MEDIUM, wiring + design: a member-retarget is VALID unpinned. Synthetic: libllama.so.0 -> libllama-common.so.0.7.0 leaves install_tree_sha256 unchanged, changes install_links_sha256, gate VALID; pinned to the base digest -> INVALID. The selftest documents this (check-receipt.py:1977-1978; cases 40 VALID, 41 INVALID). Detection exists only with --expect-install-links-sha256 and no caller passes it: SKILL.md:654 ("six pins"), SCORECARD.md:828-835 and corpus/knowledge/llamacpp-loading-lifecycle.md:315-322 list only the tree pin; install-tree-grid.py:51 passes only the tree pin. Fix: add the pin to the official counting command and SKILL row, or scope the claim to "recorded; enforced when pinned".
- F2 MEDIUM, design: "optional for legacy" has no discriminator. SCHEMA stays kama-llamacpp-live/v3 (producer line 49, unchanged by the diff) and the committed receipts are v3 without the key. Deleting both keys from a v3 receipt -> VALID unpinned (selftest links-absent-legacy-valid; synthetic stripped-both). Only a pin catches it. [INFERENCE] Clean fix: schema v4 for receipts that must carry the block.
- F3 LOW: a digest without its map is never checked unpinned: install_links absent + install_links_sha256 "0"*64 -> VALID. Pinned, the message says "receipt has no server.install_links_sha256 digest" although the digest is present (misleading). Fix: reject a digest without its map; correct the message.
- F4 LOW, robustness: a lone surrogate in an install_links key raises UnicodeEncodeError inside install_links_sha. Head CLI: exit 1, empty stdout, traceback. Base ignores the field and exits 0. The same crash already exists for install_tree keys (base tree-key: exit 1, traceback). No false acceptance. Fix: encode with surrogatepass or reject before digesting.
- F5 LOW, test strength: _selftest_receipt() and the pins are computed with install_links_sha(), the function under test, so --selftest cannot detect producer/gate drift. Agreement is shown only by synthetic_link_checks.py (gate_links_digest_equals_producer True). Fix: golden hex constant for SELFTEST_LINKS.
- F6 LOW, docs: the usage block (check-receipt.py:23-31) omits [--expect-install-links-sha256 HEX]; SKILL.md:654 still says "six pins" (dated tally 77 mutations).
- F7 NIT: keys are not checked as basenames ("sub/../libllama.so" -> VALID). The gate never opens files, so no security effect. "./x" and same-directory absolute targets are rejected by the "/" rule (fail-closed) [INFERENCE: intended].
- F8 NIT: docstring "Recompute producer install_links_sha256()" names no producer function (it is install_links()); same pattern as install_tree_sha.

## Checked and correct
- link_chain_problem terminates (seen-set); "/", "", ".", ".." targets rejected; non-string values rejected by the upstream all() check; terminal must be an install_tree key; the shadow check (lines 458-462) runs before the chain check.
- Digests: gate and producer both hash sorted "name -> text\n" as UTF-8; equal on the real tree (verified, see below).
- allow_none only for an empty map (the producer's listdir-failure encoding); a non-empty map requires a 64-char lowercase digest (null and uppercase flagged).
- Pins: malformed, absent-map and mismatch all flagged; pins never bypass chain checks; `tree` (line 385) is defined before its use at line 463.
- The 13 new invalid cases fail for the stated reason: absent-with-pin (no digest); retarget-pinned and dropped-pinned (digest mismatch); sha-tampered (recomputation); sha-null-nonempty (not hex); dangling (chain ends 'libllama.so.9'); absolute-outside and dotdot-outside (leaves directory); loop (symlink loop); not-object and non-string-target (not an object); shadows-member (also a tree member); pin-malformed. The 3 new valid cases (links-pin-valid, links-absent-legacy-valid, links-retarget-unpinned-valid) exit 0.

## Verdict changes
- Committed receipts 1-3: none. VALID at base and head for bare, --require-schema v3 and the six self-pins; 24 of 30 pairs identical.
- The 6 DIFF pairs are the new flag only: base exit 2 (argparse, unrecognized argument), head exit 1 (no install_links digest on a legacy receipt). Expected.
- Real tree (read-only, producer install_links/install_tree on ~/.local/opt/llama-b11755): 51 regular members, tree_sha 6c216313...; 10 soname symlinks, links_sha b58f1b4df160c4e2accb95bac964a5648d24fc31e769f8044296a1fa431b9e10; all 10 chains VALID. Committed receipts' install_tree_sha256 equals the current tree digest.
- Surrogate-keyed link receipt (synthetic): base exit 0, head exit 1 with traceback (F4).

## Gaps
- No live run and no receipt regeneration (prohibited). The real-tree check used the producer function read-only.
- No lsp device in my tool inventory: grep and git grep used as literal, not semantic, checks.
- install-links-grid.py reviewed only for how it invokes the gate (module import, no CLI pins); its cell counts were not verified here.
- [INFERENCE] One `git status --short` at round start may have refreshed the lane's .git/index stat cache; it wrote no object and changed no tracked file.
- Scratch /tmp/kama-r21-LinksGateReview is removed at the end; the saved scripts rebuild it from `git archive` of both revisions.
