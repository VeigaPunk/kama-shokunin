Survived five replay mutants: current selftest and C1 leave close-on-exec, short-write handling, error-path fd close, dev/inode binding, and strict server-seal checking unprotected.

Scope and method
- Isolated fixture clone: /fast/scratch/hyaku/kama-r52/M2Replay/lane, verified top-level before commits; started at build commit `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`.
- Mutated only `tools/kama-live-replay.py` in scratch copies. Ran `python3 <mutant> --selftest --scratch /fast/scratch/hyaku/kama-r52/M2Replay` for each of 15 mutants. Nonzero / unexpected refusal cases count as killed; all exact stdout is in `M2Replay/<mutant>.out`.
- Each selftest survivor was separately committed in the fixture clone using fixture identity and tested with the frozen C1 counter. Commit IDs and full outputs are retained in `M2Replay/counter-results.json` and per-mutant `.c1.out` files. Counter command: `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round52-replay-memfd-audit.py --repo /fast/scratch/hyaku/kama-r52/M2Replay/lane --tip <fixture-commit> --scratch /fast/scratch/hyaku/kama-r52/M2Replay`.
- Baseline pristine build C1: exit 0, `bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True`. Restored fixture C1: same output, exit 0. Baseline and restored `--selftest`: `KLR_SELFTEST pass=31 fail=0`, exit 0.

Verdict counts: killed-by-selftest 7; killed-by-counter 2; survived 5; equivalent 1. See `M2Replay/mutant-hashes-and-verdicts.tsv` for each mutant SHA-256 and status.

Mutation outcomes
- `flags_no_cloexec` (line 237; remove `MFD_CLOEXEC`): selftest 0, C1 0/met=True — SURVIVED. A direct fd flag probe confirmed flags=0 yields `FD_CLOEXEC` false / inheritable true, while `MFD_CLOEXEC` yields true / non-inheritable false. Suggested case: assert the returned fd has `FD_CLOEXEC` set / `os.get_inheritable(fd) is False`.
- `flags_no_allow_sealing` (line 237; remove `MFD_ALLOW_SEALING`): selftest exit 1 with `PermissionError: [Errno 1] Operation not permitted` — KILLED BY SELFTEST.
- `digest_inverted` (line 245; reject when digest equals expected): selftest exit 1, `Refused: memfd-digest-mismatch` on good bytes — KILLED BY SELFTEST.
- `write_loop_no_retry` (line 244; issue one write and discard unwritten suffix): selftest 0, C1 0/met=True — SURVIVED. Suggested case: replace/patch `os.write` to return a short count on the first call, then assert `sealed_member` contains the complete archive bytes and expected digest.
- `no_close_on_error` (line 252; skip fd close after exception): selftest 0, C1 0/met=True — SURVIVED. Suggested case: invoke with a wrong digest and instrument `os.close` (or inspect `/proc/self/fd`) to assert the allocated memfd is closed on `Refused`.
- `member_basename` (line 231; call `getmember(basename)`): selftest exit 1, `member-absent-in-archive:build/bin/llama-server` — KILLED BY SELFTEST.
- `seal_mask_write_dropped` (line 219; `SEALS_ALL=14`): selftest 0, but C1 exit 1 (`bind=0 sealed=0 teardown=0`, no ready server) — KILLED BY COUNTER. Suggested selftest case: assert the literal required mask 15 / all four individual seal bits, not the mutable `SEALS_ALL` constant.
- `seal_verify_bypass` (line 249; remove post-F_ADD_SEALS mask check): selftest 0 and C1 0/met=True — EQUIVALENT on the supported Linux behavior exercised: successful `F_ADD_SEALS(fd, 15)` applies the requested seals; failure raises before continuation, and the external C1 independently checks the actual running image. Thus removing this redundant verification did not change reachable behavior in this probe.
- `identity_memfd_false` (line 255; report memfd false): selftest exit 1, `FAIL sealed-member-refuses-writes` — KILLED BY SELFTEST.
- `dev_inode_compare_bypass` (lines 431-433; bypass identity check): selftest 0, C1 0/met=True — SURVIVED. Existing `copy-live` test still fails for its link-count violation and therefore does not isolate identity. Suggested case: fake live receipt with correct digest, seals=15, nlink=0 and `/memfd:` path but a different dev or inode; expect `server-exe:not-own-memfd`.
- `server_seals_mask_weakened` (lines 434-435; accept only bit 1): selftest 0, C1 0/met=True — SURVIVED. Actual running server has 15 seals, so current tests never distinguish weaker receipt validation. Suggested case: otherwise matching fake `server_exe` with seals=1; expect `server-exe:not-sealed-memfd`.
- `server_nlink_check_bypass` (line 435; omit nlink/prefix requirements): selftest exit 1, FAIL `server-exe-linked` and `server-exe-path` — KILLED BY SELFTEST.
- `server_memfd_prefix_bypass` (line 435; accept arbitrary path): selftest exit 1, FAIL `server-exe-path` — KILLED BY SELFTEST.
- `own_server_omit` (line 426; emit empty own_server): selftest 0, C1 exit 1, `bind=1 sealed=0 teardown=1 newrow=1`; counter details say `replay own_server {} does not name the observed memfd` — KILLED BY COUNTER. Suggested selftest case: assert the replay result's `own_server` records memfd=true and the same dev/inode as `sealed_member` identity.
- `server_sha_compare_bypass` (line 429; skip digest comparison): selftest exit 1, FAIL `server-exe-digest-differs` — KILLED BY SELFTEST.

Restoration evidence
- Source pristine SHA-256: `9c11b2fbc77bd73e628b9870736f804c6b6be897ec59ca45ac16a81edafe7233`.
- Fixture clone replay bytes restored exactly to that SHA-256; restored fixture commit `22e05c3b88efe219efc2b7f57acfcb881cbe48c5`.
- Restored selftest and C1 both passed as recorded above. Every mutant hash is recorded in the TSV. Scratch was removed after evidence was copied; no live server was left running.

Evidence files are under `.ufo/waves/round-52/w1/out/M2Replay/`.
