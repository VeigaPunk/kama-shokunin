VERDICT: confirm - spliced real-tree receipt: the links pin accepts the real digest (exit 0) and rejects a libllama.so.0 retarget (exit 1) that the tree pin still accepts (exit 0); SPLICED, not a live capture

Scope: SPLICED receipt, NOT a live capture. Nothing was launched (no llama-server, no model, no port). Producer install_tree()/install_links() were imported read-only from lane a29bb84 (scratch clone) and run over ~/.local/opt/llama-b11755. Only the four install fields were spliced into round-18 receipt-1.json; no other field was recomputed. Deliverables: .ufo/waves/round-21/build/out/LinksRealReceipt/ (links-real-receipt.py, verdicts.txt, identities.json, spliced-real.json, spliced-retarget.json, spliced-dangling.json).

Provenance (executed):
- git clone + checkout a29bb84 -> exit 0; HEAD a29bb84bb8b4d328f5970a89e448330a3a42ac.
- producer sha256 c05cd8bf36668b841246e9a8fdf9cf351b63a3d8423a154233230ceb69ae764e (equals `git show a29bb84:tools/kama-llamacpp-live.py | sha256sum`, exit 0); gate sha256 01fbf81387f1a72bebf0b3ca76b9c50d9850300c5776ee49bcfcba709d46a121.
- Baseline: unmodified round-18 receipt on the a29bb84 gate -> `VALID ...receipt-1.json`, exit 0.

Real tree (read-only; untouched: dir mtime 2026-10-20 08:10:36, libllama.so.0 08:10:28, readlink -> libllama.so.0.7.0):
- install_tree: 51 members, sha256 6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c. Equals the round-18 recorded tree, digest and server.sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804.
- install_links: 10 symlinks, sha256 b58f1b4df160c4e2accb95bac964a5648d24fc31e769f8044296a1fa431b9e10. Independent shell recomputation (`for f in *`; `[ -L ]`; `readlink`; `LC_ALL=C sort`; `sha256sum`) gives the same value, exit 0. The tree shell recomputation gives 6c216313..., exit 0.

Gate matrix (`links-real-receipt.py`, exit 0, 8/8 rows matched predeclared exits, stderr empty). Verdict lines, verbatim from verdicts.txt:
  [B0] exit=0  VALID .../round-18/live-recovery/receipt-1.json
  [B1] exit=1  INVALID .../receipt-1.json: --expect-install-links-sha256 given but receipt has no server.install_links_sha256 digest
  [R1] exit=0  VALID .../out/LinksRealReceipt/spliced-real.json
  [R2] exit=0  VALID .../spliced-real.json  (argv --expect-install-links-sha256 b58f1b4d...)
  [R3] exit=0  VALID .../spliced-retarget.json  (libllama.so.0 -> libllama-common.so.0.7.0, no pin)
  [R4] exit=1  INVALID .../spliced-retarget.json: server.install_links_sha256 a1afacc2c04d554d4d08666a0272d6d1f128c1071c236a8cbc5409b1c1926036 != expected b58f1b4df160c4e2accb95bac964a5648d24fc31e769f8044296a1fa431b9e10
  [R5] exit=0  VALID .../spliced-retarget.json  (--expect-install-tree-sha256 6c216313...)
  [R6] exit=1  INVALID .../spliced-dangling.json: 2 problems, chain ends at 'libllama.so.9' (libllama.so, libllama.so.0)
Retarget shell check (while-read substitution of the links listing): a1afacc2... (exit 0); dangling be498580... (exit 0).

Findings:
1. On the real tree the links pin closes the R19 gap. The tree pin is blind to the retarget (R5 VALID; tree_sha identical), and the links pin rejects it (R4).
2. Without a pin the gate accepts a consistent retarget onto a pinned member (R3). The gate says so itself: "A consistent retarget onto another pinned member is VALID without a links pin (documented limit) and INVALID with one." (tests/llamacpp-live/check-receipt.py:1977-1978, a29bb84).
3. The gate's recomputed links digest equals the producer's on real data (R1 VALID), and both match the shell recomputation.
4. install_tree() is unchanged 7a6bc91 -> a29bb84: `git diff --numstat` -> `28 0`; hunks +24 @205, +1 @1230, +1 @1294, +2 @1308; the install_tree block sha256 is b68a5018a7f1d30801879f36baa8f837bfc80da1d3298c88a70f5439894209eb at both revs.
5. Only the chain check (R6) and the pin (R4) reject links; the unpinned gate passes any consistent pinned-member retarget.

Caveats:
- Spliced, not live. The VALID verdicts cover round-18 remainder fields that were not recomputed, including tool.sha256 83eac5c0... (round-18 tool, not a29bb84's c05cd8bf...). The gate checks tool.sha256 only with --expect-tool-sha256, so these verdicts do not show that a29bb84 produced the receipt.
- Not executed: the live call site (tools/kama-llamacpp-live.py:1292-1309). [INFERENCE] a live run records the same fields via the same install_links() call (lines 1294, 1308-1309).
- Not exercised here: the gate's tampered-digest check (selftest `links-sha-tampered`); single tree and single soname retarget tested.

Reproduce: git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin <dir>/lane && git -C <dir>/lane checkout -q a29bb84bb8b4d328f5970a89e448330a3a42ac && python3 .../out/LinksRealReceipt/links-real-receipt.py --lane <dir>/lane --work <dir>/work  (exit 0).

Process and tooling: no installs or updates (python 3.14.8, git, bash 5.2.37 pre-existing). Only gate subprocesses ran and all exited; `pgrep -fa kama-r21-LinksRealReceipt|links-real-receipt` -> exit 1 (none). No llama-server, model, port or subagent. Lane untouched; writes limited to out/LinksRealReceipt/ and this report. Scratch /tmp/kama-r21-LinksRealReceipt removed at finish.
