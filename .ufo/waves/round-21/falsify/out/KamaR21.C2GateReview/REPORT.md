VERDICT: partial - the claimed gate outputs reproduce exactly; the gate accepts orphan/null/empty digests and unvalidated link keys, and the producer fails open on read-time errors
Attacked: tests/llamacpp-live/check-receipt.py @ a6617149 (install_links_sha, link_chain_problem, install_links block, --expect-install-links-sha256, --require-install-links, 5 new VALID cases, 14 new mutations) plus the producer install_links()/install_tree() that feed it. Gate, producer and grid blobs are identical at b76727f3 (git diff empty, exit 0).

## Reproduced (run in /tmp/kama-r21-C2GateReview/lane @ a6617149)
- `python3 tests/llamacpp-live/check-receipt.py --selftest`: exit 0, "11 VALID and 1 NOT-EVALUATED receipts accepted; 91 mutations + unreadable case rejected". Round-20 stdout (04de7a87) shows 6/77, so +5 VALID and +14 INVALID, matching the diff (11 mut() + 3 cases).
- Six R18 receipts (live/ and live-recovery/, receipt-1..3; distinct files by sha256): default exit 0 VALID x6; --require-install-links exit 1 x6 ("no server.install_links block").
- live-receipt.json with the measured argv: pinned exit 0 VALID; wrong links pin exit 1; --require-install-links alone exit 0.
- Canonical digest: SELFTEST_LINKS literal 83bdd3cc... equals sha256 of the canonical bytes (printf | sha256sum, exit 0). Gate encoder is the same call as producer links_digest (producer 205-210). Producer writes receipts ensure_ascii=True, allow_nan=False (producer 1268).
- Real tree today (read-only producer calls): install_tree_sha256 and install_links_sha256 match the live receipt; 51 members, 10 links, problems [].

## Problems (out/KamaR21.C2GateReview/attack_gate.py: 45 mutants, 0 differ from the source-predicted verdict; attack-output.txt)
G1 [medium, design] The new retarget detection is inert without the new pin. Consistent libggml.so.0 -> libggml-base.so.0.27.0: tree pin only exit 0 VALID; tree pin + --require-install-links exit 0; only with --expect-install-links-sha256 exit 1 (probe_extra.py). Stripping the links block and digest is VALID in default mode (exit 0).
G2 [low] Orphan digest never checked: no block + install_links_sha256 "zz" / null / correct hex -> exit 0. The digest is checked only inside `if links is not MISSING`.
G3 [low] Empty block with null digest accepted: install_links {} + null -> exit 0 default and with --require; the pin rejects (exit 1). Cause: allow_none=not links (check-receipt ~455). Producer success always writes hex (producer 1376-1394; links_digest never returns None). Null appears only in the setup-error default (producer 1312), which setup_error already rejects.
G4 [low] Link KEYS are unvalidated (only targets are): "", ".", "..", "glibc-hwcaps/x86-64-v3/libggml.so.0" -> exit 0; control-char keys 0x01, LF, NUL -> exit 0. Producer refuses LF (measured, control-character-in-name) and 0x01 (by code, producer 231-233) and subdirectories (measured, not-regular-or-symlink).
G5 [low] Producer and gate disagree on targets: producer records './name', '.', absolute, dangling, loop and hwdir -> '.' with no problem; gate rejects all (exit 1). Fail-closed, but producer "fails closed" wording overstates it and the operator gets an unexplained INVALID.
G6 [low] Chain walk is O(n^2): 2000 links 0.19 s, 8000 links 2.56 s (x13.5 for x4). Validator DoS on adversarial input only.
G7 [info] Any pinned regular member is a legal chain end: libalias.so -> llama-server (ET_DYN/PIE, readelf -h) and -> LICENSE are exit 0. Whether the loader would map them is [INFERENCE].
G8 [info] Selftest gaps: none of G2-G4, the '.', '' and '/' targets, tree-end removal or an uppercase digest is among the 91. `not isinstance(target, str)` in link_chain_problem is unreachable from validate. Missing-pin message says "no digest" even when an orphan digest exists.

## Producer (feeds the gate; C2 claim "fails closed on unreadable members")
P1 [low-med] A read error after os.access passes is silently dropped: install_tree `except OSError: continue` (producer 198-199); install_links checks only os.access. Simulated by making sha256_file raise: producer OK, problems [], tree missing the member; gate VALID unless a link points at it (then exit 1). Needs a real I/O error or lstat-then-open race.
P2 [info] Reproduced refusals (uid 1000): unreadable member, glibc-hwcaps/ subdir, FIFO, LF name. Simulated readlink EIO and lstat ENOENT report problems (probe_extra.py).
P3 [info, INFERENCE] Producer selftest unreadable check (line 1155) runs only when os.access says unreadable, so it is vacuous under root.
P4 [info, INFERENCE] install_tree (1375) and install_links (1376) list the directory separately; a swap between them yields a mixed-state receipt. Most such mixes fail closed at the gate.

## Residual scope
R1 [info] RUNPATH is $ORIGIN only (readelf -d on llama-server and libllama-server-impl.so). The impl lib also NEEDs libssl.so.3, libcrypto.so.3, libstdc++.so.6, libgcc_s.so.1, libc.so.6, libm.so.6, none in the pinned directory; those system libraries sit outside every pin.

## Recommendations (not applied; FALSIFY seat is read-only)
- Make --expect-install-links-sha256 part of the lane's standard invocation, or mark round-21+ receipts so default mode cannot downgrade (G1).
- Gate: reject install_links_sha256 without a block; require hex whenever the block exists; validate keys as basenames (no '/', not '', '.', '..', no control chars); memoize chain ends (G2-G4, G6).
- Producer: install_tree must fail closed on OSError; refuse non-basename targets so producer and gate agree (P1, G5).
- Add selftest mutants for G2-G5 and the '.', '' and '/' target cases.

## Verification gaps
- Not run as root; read errors and races simulated only. Producer selftest and any server launch not run (bounds). Tool installs: none.
- Files: out/KamaR21.C2GateReview/{attack_gate.py, attack-output.txt, probe_extra.py}. Scratch clone removed after writing.
