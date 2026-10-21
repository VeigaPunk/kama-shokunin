VERDICT: confirm - the committed live receipt reproduces from committed bytes (10 links, install_links 5cb9f486…, tree 6c216313…, tool e4cc6d88…, recipe gate argv all as recorded); six gaps below, none refutes C2
Attacked: live receipt runs/b76727f3/live-receipt.json (identity fields, source_binding, pins) and the gate paths it exercises (empty/null links, dropped block, pins). Read-only: no launches, no installs, no lane writes.

## Commit facts
- `git show b76727f3:.ufo/waves/round-21/runs/b76727f3/live-receipt.json` -> "does not exist", exit 128. The receipt is first committed in a6617149 (child of b76727f3, "official measurement at b76727f3 ... live v3 receipt"); blob sha256 e1fc04ab… equals the worktree file.
- `git diff --quiet b76727f3 a6617149 -- <producer, gate, grid, probe, audit>` -> exit 0 (identical).
- `git show b76727f3:tools/kama-llamacpp-live.py | sha256sum` = e4cc6d88… = receipt.tool.sha256 (exit 0).

## Independent recomputation: verify_live_receipt.py -> exit 0, 64/64 gating PASS
- install_links via `find -printf '%y\0%f\0%l\0'`: 10 symlinks, equal to the receipt map. Canonical JSON (sort_keys, compact, ASCII) sha256 = 5cb9f486… (manual construction identical). os.lstat/os.readlink pass agrees.
- install_tree: 51 regular files, equal to the receipt; digest 6c216313…; no other entry types. All 10 links realpath to pinned members.
- llama-server b6a31a8e…, libllama-server-impl.so e404b91a…, model 270cba… (1185376 bytes; equals SOURCES S039 LFS digest), probe 36b64978….
- source_binding: 5 spans. Fetched llama.cpp @704366d76 (curl exit 0 x3): file sha256 = receipt file_sha256 (dd1de0f2…, 24ede172…, 21439622…); span_text equals the upstream lines; span_sha256 recomputes.
- check_source_binding_vs_producer.py (ast-extracts only pure producer defs at b76727f3) -> exit 0: receipt.source_binding EQUAL producer.source_bindings() (5 entries).

## Gate re-run: run-gate-recipe.sh -> exit 0, gate_cases_failed=0 (gate = committed b76727f3 copy)
- selftest exit 0 "11 VALID and 1 NOT-EVALUATED, 91 mutations". Pinned argv exit 0 VALID (committed copy and worktree path). Wrong links pin exit 1: "server.install_links_sha256 5cb9… != expected 000…".
- Extra pins (server, impl, tool, probe) bind, exit 0; wrong tool, tree or model pin exit 1 each.
- Legacy receipt-1/2/3 exit 0 VALID; each with --require-install-links exit 1 ("no server.install_links block").
- Official recorded exits and stdout in runs/b76727f3 match the re-run after path normalisation (5 of 5 compared).

## Negative controls (scratch copies; verifier exit 1 each, as required)
- A: libllama.so.0 retargeted -> FAIL links map + digest only; tree PASS.
- B: glibc-hwcaps/ added -> FAIL "no entries other than regular files and symlinks".
- C: byte appended to libggml-rpc.so -> FAIL tree members + tree digest only; links PASS.
- server.realpath fails in all three (scratch path); expected, not a mutation effect.

## Gaps
- G1 gate: `install_links: {}` + digest null -> VALID with --require-install-links (probe R0, exit 0). check-receipt.py:454-455 (allow_none=not links); :469-471 checks presence only. The producer never emits it (producer:245 always returns links_digest). The recipe's pinned run rejects it (exit 1, "no server.install_links_sha256 digest"), so the gap is for unpinned use only.
- G2 gate: block dropped, digest kept -> VALID without the flag (R2, exit 0); digest unchecked. Legacy-compatible by design; with the flag, INVALID (exit 1).
- G3 producer: a non-UTF-8 regular-file name makes install_tree() raise UnicodeEncodeError (producer:200-201 strict .encode()). main() catch-all (producer:1565-1566) records internal:UnicodeEncodeError, not install-tree-unpinnable. Fail-closed in effect [INFERENCE: the producer was not run]. Control-char name, glibc-hwcaps/ and non-UTF-8 dir fail closed as claimed (probe_edges.py, exit 0).
- G4 drift (not a receipt defect): worktree tools/kama-llamacpp-live.py (1c24ffe3…, mtime 08:23:17 -0300) and tests/llamacpp-live/check-receipt.py (b26dd0bf…, mtime 08:21:47) differ from b76727f3 (e4cc6d88…, 6b876437…). Diffs in drift/: +3 and +8 lines, both inside _selftest; production paths unchanged. The receipt still binds e4cc6d88. Lane .git/HEAD is a bare commit id (detached at a661714).
- G5 provenance: source_binding health_ready row is null (producer:997), but corpus/SOURCES.md:54 (S042, committed at b76727f3) cites the same span (get_health 5288-5299, dd1de0f2…). Values are right; the registry link is stale.
- G6 scope: the pin covers the install dir only. libllama-server-impl.so NEEDs libssl.so.3, libcrypto.so.3, libstdc++, libgcc_s, libc, libm, ld-linux (system, unpinned; dynamic-deps.txt). In-tree NEEDED sonames are all in install_links. The gate never reads disk and does not authenticate upstream bytes (check-receipt.py:90-93 says so).

## Not verified
- Install-tree provenance against release asset S038 (22 MB; not downloaded). llama-connect (9.7 MB) has no b11755/704366d build tag (llama-server does); it is pinned by digest, origin unchecked.
- Grid arms and the live run were not re-run (launches forbidden).

## Tooling
No installs or upgrades. Pre-existing tools used: /usr/bin/python3 3.14.8, jq, git 2.56.0, readelf, curl.

## Output
.ufo/waves/round-21/falsify/out/C2LiveReceiptVerify/ (~1 MB; MANIFEST.sha256 lists every file): verify_live_receipt.py, check_source_binding_vs_producer.py, run-gate-recipe.sh, probe_edges.py, probe_gate_edges.sh, fixtures/, verify/, verify-worktree/, negative-controls/{A,B,C}, gate-runs/, gate-edges/, source-binding/, drift/, dynamic-deps.txt.
Re-running the scripts needs the scratch clone: `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r21-C2LiveReceiptVerify/lane && git -C /tmp/kama-r21-C2LiveReceiptVerify/lane checkout -q b76727f31e522763ce24e43d6ec86d21b507a11f`. Scratch was deleted after outputs were written; no processes left running.
Lane action: none required for C2 as committed. If the lane will bind the working-tree producer, the receipt must be re-captured after the drift is committed or reverted.
