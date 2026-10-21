VERDICT: partial - happy path is correct and back-compatible (real tree: 10 relative links resolve, install_tree digest unchanged), but install_links fails open on per-entry OSError, its digest is non-injective, v3 accepts link-free receipts without a pin, and the producer --selftest exercises none of it.

# LinksProducerReview - C2 producer diff (round 21)

Scope: `git diff 7a6bc91 a29bb84 -- tools/kama-llamacpp-live.py` (exit 0; 28 insertions, 0 deletions, 4 hunks). Reviewed in a scratch clone at a29bb84 (sha256 c05cd8bf...). Lane HEAD = a29bb84 (`git rev-parse HEAD`, exit 0). No installs or updates performed. Evidence: `.ufo/waves/round-21/build/out/KamaR21.LinksProducerReview-6/` (probe.py, probe-transcript.txt, selftest and gate transcripts, e9-leaf-*, sha256.txt, lane-worktree-vs-commit.diff).

## Findings
1. HIGH - fail-open on per-entry OSError. `install_links` L219-223 is `except OSError: continue` around lstat/readlink; a listdir failure returns `({}, None)` at L215-216. A dropped entry vanishes from the map, the digest covers the partial set, and nothing is recorded.
   - E3a: lstat ENOENT on `libllama.so.0` -> `{'libllama.so': 'libllama.so.0'}`, no error. The gate chain rule flags it only incidentally ("chain ends at 'libllama.so.0'").
   - E3b: lstat ENOENT on both chain links -> `({}, e3b0...)`, identical to an empty directory. Gate VALID without pin (E9 "emptied", exit 0); exit 1 with a pin.
   - E3c: readlink EIO on `libllama.so` -> the map silently keeps only `libllama.so.0`. Gate acceptance of a leaf-omitted map, on a fixture (e9-leaf-transcript.txt): VALID exit 0 without pin, exit 1 with the full digest.
   - Impact: `libllama.so.0` and `libggml.so.0` are NEEDED by `libllama-server-impl.so` (readelf -d, exit 0), so omitted soname links are runtime identity gaps. A production trigger (concurrent replace or EIO during the scan) is [INFERENCE]; the failure was emulated by monkeypatch, not reproduced live.
   - Fix: fail closed (SetupError `install-links-unreadable:<name>`) on any OSError in the scan; never digest a partial scan. `install_tree` L190-199 has the identical pattern (pre-existing); the same fix leaves its success-path digest unchanged.
2. HIGH - receipt optionality without a schema bump. `SCHEMA` stays `kama-llamacpp-live/v3` (L49). The gate treats `server.install_links` as optional (check-receipt.py L441-446) while `server.install_tree` is required (L385-391). E9: links stripped -> exit 0 VALID under `--require-schema v3`; exit 1 with `--expect-install-links-sha256`. A round-21 receipt with the fields removed is indistinguishable from a round-20 receipt, so its identity is unbound unless a consumer passes the pin. Decision for L1: bump to `kama-llamacpp-live/v4` (producer always emits install_links, gate requires it for v4, v3 stays legacy).
3. MEDIUM - digest is not injective. The line format `f'{n} -> {t}\n'` (producer L224-225; gate L173-178) collides when names or targets contain ' -> '. E5: `{'a': 'b -> c'}` and `{'a -> b': 'c'}` both give install_links_sha256 `a956b706...`; both pass the gate chain checks (None/None) and their tree digests are equal, so a pin computed on state A accepts state B. Fix: unambiguous per-entry encoding (NUL- or length-prefixed) in producer and gate together. Safe now: no committed receipt carries install_links.
4. MEDIUM (loud, exotic) - new crash path. A non-UTF-8 symlink NAME or TARGET makes `install_tree` return a digest (E4a/E4b), but `install_links` raises UnicodeEncodeError at `.encode()` (L224-225). Base 7a6bc91 had no such call, so such a directory previously ran. main `except BaseException` -> `_record_internal` -> setup_error `internal:UnicodeEncodeError`, exit 2 (main L1476-1481; L912-915) [INFERENCE: full run not executed]. Non-UTF-8 regular names already crash `install_tree` (E4c, pre-existing). Fix both sites with one helper.
5. LOW - producer selftest covers none of the change. `_selftest` L1082-1180 never references install_tree or install_links (grep). A mutant whose install_links raises still gives `--selftest` exit 0 (E10). The gate selftest covers the gate side (exit 0). Add an install_links case: chain digest equals recomputation; an injected OSError must fail closed.
6. LOW - tool pin and worktree hazards. (a) The lane working copy `tools/kama-llamacpp-live.py` (sha256 7de1e81e...) differs from the committed c05cd8bf... by one added blank line at lane L1152 (diff exit 1; mtime 2026-10-21 07:48:01 -03:00). Receipts record `tool.sha256` of the file actually run, so L1 must commit or remove it before measurement. (b) `tool.sha256` moves 83eac5c0... (7a6bc91) -> c05cd8bf... (a29bb84); no non-.ufo file pins either value (git grep, exit 1). Every further producer edit re-pins.
7. LOW - null digest accepted without pin. check-receipt.py L453-454 `allow_none=not links`: links `{}` with a null digest -> exit 0 without pin (E9); exit 1 with pin. Reachable only if listdir fails for install_links but not for install_tree; resolved by finding 2.
8. INFO - docs and scope. No doc names install_links (`git grep -n install_links -- ':!.ufo' ':!tools/...' ':!tests/...'`, exit 1); corpus/knowledge/llamacpp-loading-lifecycle.md:107 mentions only install_tree. Absolute or `/`-bearing symlinks in the same directory make the gate INVALID (E11). The real tree has 10 relative top-level links and no subdirectories, so no current impact [INFERENCE for shared-directory use].

## Verified OK (executed)
- install_tree untouched. Real-tree install_tree_sha256 = 6c216313... = R20 pin, 51 regular members (E7).
- install_links happy path: normal soname chain (E1; gate recomputation equal True); empty dir -> sha256('') (E2); listing denied -> `({}, None)`, as install_tree (E2b); real tree: 10 links, gate recomputation equal True, every chain resolves (E7).
- Init L1229-1230; fill L1302-1311, after pick_port L1301. Setup-error receipts keep `{}`/null, as install_tree does (code reading).
- SCHEMA string, source_binding and its 5 spans unchanged; spans match the gate pins (list vs tuple normalised) and recompute (E8).
- Producer `--selftest`: exit 0 at scratch a29bb84 and at the lane path. Gate `--selftest`: exit 0, "9 VALID and 1 NOT-EVALUATED receipts accepted; 90 mutations + unreadable case rejected".

## Fix order for L1 (before measurement)
1) fail-closed scan plus injective digest, one shared helper in producer and gate; 2) schema decision (v4 recommended); 3) producer selftest case; 4) commit or remove the lane blank line, re-pin tool sha after the final edit; 5) rerun both selftests. Official grid runs stay with L1.

## Executed commands (exit)
- git diff --stat and git diff 7a6bc91 a29bb84 -- tools/kama-llamacpp-live.py: 0
- git clone + checkout a29bb84 (scratch): 0; git rev-parse HEAD (lane): 0
- python3 tools/kama-llamacpp-live.py --selftest (scratch): 0; python3 -B <lane>/tools/kama-llamacpp-live.py --selftest: 0
- python3 -B tests/llamacpp-live/check-receipt.py --selftest (scratch): 0
- python3 -B probe.py (E1-E11, scratch plus read-only real tree): 0
- check-receipt.py e9-leaf-omitted.json --require-schema v3: 0; with --expect-install-links-sha256 5e1129f2...: 1
- diff committed-a29bb84 vs lane worktree file: 1; git grep 83eac5c0/c05cd8bf (non-.ufo): 1; git grep install_links docs (non-.ufo): 1
- readelf -d llama-server and libllama-server-impl.so: 0; find real tree -type l: 10 links; find -mindepth 1 -maxdepth 1 -type d: no output
Tooling: none installed or updated.
