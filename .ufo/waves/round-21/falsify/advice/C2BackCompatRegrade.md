VERDICT: partial - legacy receipts unchanged (18/18 exit and verdict identical at 7a6bc911 and a6617149), but integration 1471344 flips 16 committed round-21 VALID fixtures to INVALID via an undisclosed digest-encoding change, and an optional links block lets a v3 receipt downgrade to VALID unpinned.

Attacked: the C2 back-compat claim ("install_links optional for legacy receipts") by regrading every committed kama-llamacpp-live receipt at gate 7a6bc911 (check-receipt.py blob e90be78d) and gate a6617149 (blob 8d83fe7f, same as 1471344), no extra flags, plus the live receipt at a6617149.

## Scope (executed)
- 420 committed .ufo/waves JSON at a6617149 (293 at 7a6bc911; diff 7a..a6: 127 added, 0 modified, 0 deleted); 419 parse.
- 66 carry the schema marker: 44 top-level receipts (18 legacy, 26 with server.install_links*, incl. live), 21 non-receipt documents, 1 non-JSON. Plus 3 receipt objects nested in other documents (nested.py).
- Excluded as not receipt JSON: .md advice, a .stdout scan, a frozen gate copy.

## Results, 7a6bc911 vs a6617149 (no flags)
- Legacy 18 (v1 x4, v2 x3, v3 x11): 16 identical in exit and verdict line. 2 (GateSelftestCrash receipt-A, receipt-B) differ only in traceback text (path, line numbers, elided-call width); exit 1 both.
- Live receipt round-21/runs/b76727f3/live-receipt.json: VALID exit 0 both (blob e1fc04ab equals the lane file).
- Round-21 link fixtures (25): 20 exit flips VALID->INVALID; 1 stdout (listing-tree-only: 1 -> 12 problems); 1 crash stderr (cli-nonutf8-name, exit 1 both); 3 unchanged.
- Nested 3, non-receipt 21 and non-JSON 1: identical at both gates.

## Beyond-expected changes, attributed (arms: 7a6bc911 | a29bb84 draft gate 8a6b5dd2 | 1471344 = a6617149)
- 16 VALID at a29bb84 -> INVALID at 1471344, each with exactly one problem: "server.install_links_sha256 != recomputation over install_links". Stored digests equal the draft formula (sha256 of 'name -> text\n' lines) on all 16. Gate and producer moved to canonical JSON at 1471344 (check-receipt.py:173-178; tools/kama-llamacpp-live.py:205-210). Schema string stays kama-llamacpp-live/v3 (check-receipt.py:49). Affected: e9-leaf-omitted; LinksDigestEncoding cli-impl-removed-no-impl-pin, cli-impl-removed-with-impl-pin, cli-minimal-link-witness, cli-real-cpu-decoy, cli-real-legit, cli-real-soname-decoy; LinksPolicyCritic/p1 B-receipt, G-receipt; LinksRealReceipt spliced-real, spliced-retarget; LinksTreeDeterminism receipts healthy, race-libllama-server-impl.so, race-link-libllama.so, unreadable-libggml-cpu-haswell.so; RevengeGateConsumers synthetic-links-receipt.
- Same link map, two encodings: healthy.json's canonical digest is 5cb9f486, which is the live receipt's stored digest. Reverse direction: the live receipt is INVALID at a29bb84 (line digest) and VALID at 1471344; nothing in the schema tells the encodings apart.
- 4 VALID -> INVALID already at a29bb84 (chain rule: "not a pinned install_tree member"); 1471344 adds the digest problem: cli-real-impl-absorbed-with-impl-pin, LinksRealReceipt spliced-dangling, race-link-libllama.so.0, unreadable-libllama.so.0.7.0. [INFERENCE] negative fixtures by name.
- Provenance: all 25 fixtures were first committed in 1471344 (git log --diff-filter=A), the commit that changed the digest, and never regenerated. Lesson corpus/lessons/round-21.md:83-84 records the adoption, not the stale fixtures. LinksRealReceipt.md R1 (spliced-real VALID) and R3 (spliced-retarget VALID, no pin) are INVALID at a6617149 with no flags (executed). [INFERENCE] the fixtures came from the a29bb84-era producer and are intended VALID by name for healthy, cli-real-legit and spliced-real.

## Optional-links path (check-receipt.py:442-458 at a6)
- Absent install_links skips the whole block, so a stray digest is never checked. An empty map permits a null digest (allow_none=not links; recompute skipped). The comment says "optional (receipts before round 21 lack it)", but the rule is not keyed on schema.
- Downgrade probe on a scratch copy of the live v3 receipt (downgrade-probe.tsv): strip both keys -> VALID 0 at a6617149 (7a6bc911 also 0); empty map + null digest -> VALID 0; strip map, keep digest -> VALID 0; strip digest, keep map -> INVALID 1. With --expect-install-links-sha256 5cb9f486...: all four mutants -> INVALID 1; control VALID 0.
- Committed instance: LinksTreeDeterminism/receipts/listing-links-only.json (51-entry install_tree, install_links {}, digest null): VALID 0 at all four arms, no flags. Only the pin catches it.

## Supplementary and pre-existing (identical in both gates)
- --require-install-links at a6617149 (outside the no-flag target): all 18 legacy exit 1, incl. round-18 live-recovery 1-3 and live 1-3; live receipt VALID 0. Matches the C2 R18/live claims.
- Uncaught exceptions exit 1 with no verdict: GateSelftestCrash receipt-A (TypeError at validate, `if refusal != sorted(refusal)`), receipt-B (UnicodeEncodeError after the INVALID header), cli-nonutf8-name (UnicodeEncodeError in install_tree_sha). Exit 1 collides with INVALID; the contract reserves 2 for unreadable. NOT-EVALUATED (exit 3) occurs in no committed receipt.

## Commands executed (exit)
- git clone -q lane -> scratch; checkout a6617149 (0); clone g7 and checkout 7a6bc911 (0); git archive a29bb84 and 1471344 | tar -x (0, 0).
- git ls-tree -r -z --full-tree <commit> -- .ufo/waves (0); git diff --name-status 7a6bc911 a6617149 -- .ufo/waves (0; 127 A).
- check-receipt.py --help at both gates (0, 0); sample round-18 receipt-1 VALID at both (0, 0).
- python3 -B out/C2BackCompatRegrade/regrade.py (0); arms.py (0); nested.py (0).
- git log --diff-filter=A on the fixtures (0); sha256sum of the lane live receipt vs blob (0, equal).
- Downgrade probe and stderr normalization: python subprocess inside the Python kernel (no shell exit; per-run results in downgrade-probe.tsv and transcript).
- Outputs: out/C2BackCompatRegrade/{regrade-matrix.tsv, regrade-changes.txt, arms-matrix.tsv, arms-stderr-diff.txt, digest-check.tsv, nested-matrix.tsv, downgrade-probe.tsv} and scripts regrade.py, arms.py, nested.py.
- Tooling: none installed or updated (system python3 3.14.8, git). Lane not modified: reads via scratch clones; writes only new files under out/ and this advice. Scratch /tmp/kama-r21-C2BackCompatRegrade removed (rm -rf exit 0).

## For L1 (advice only)
1. Regenerate the 16 flipped fixtures under the canonical digest, or record their expected verdicts; correct LinksRealReceipt R1/R3.
2. For v3, require install_links when install_tree is non-empty; reject a digest without its map; treat empty-map + null digest as absent.
3. Add an encoding discriminator (schema v4, per LinksGateReview F2) so line and canonical digests cannot be confused.
4. Map uncaught exceptions to exit 2.

Limits: fixture intent inferred from names and advice [INFERENCE]; no live capture; gate selftest not run (outside target).
