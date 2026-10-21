VERDICT: partial - grid counts reproduce and the gate's pin is an exact equality check, but the sixth pin does not authenticate execution and does not bind the SONAME symlinks the loader executes (a retarget passes); the lesson inverts the grid's count and overstates "swaps".

# CritC2Inflation — C2 attack (round 19 sixth pin)

Question: does `--expect-install-tree-sha256` authenticate execution? No. The lesson (corpus/lessons/round-19.md:29) and SCORECARD.md:834-835 already reject that reading. The defects are in what the pin covers and in the wording around it.

Evidence: `/tmp/kama-r19-CritC2Inflation/out/COMMANDS.md` (every command, exit, artifact). Lane not modified.

## Findings (weight order)

1. **Counterexample — a retargeted SONAME symlink passes the pin (executed).**
   - The producer hashes regular files only; symlinks are skipped (tools/kama-llamacpp-live.py:178-202, skip at :194-195). The install dir has 10 SONAME symlinks (`libllama.so.0 -> libllama.so.0.7.0`, `libllama-common.so.0`, `libggml-base.so.0`, `libggml.so.0`, `libmtmd.so.0`, and their dev names). The upstream tarball lists the same 10 links; its sha256 is `753bfa73…e226` (SOURCES S038 digest).
   - `readelf -d`: `llama-server` NEEDs `libllama-server-impl.so`, which NEEDs `libllama.so.0` and `libllama-common.so.0`. The loader opens the symlink names.
   - Test: copy the install dir with links kept; relink `libllama.so.0` to an alternate object outside the tree (real bytes plus 64 zero bytes). Producer `install_tree()` gives identical members and combined digest `6c216313…5a2c`, so the pin passes. `llama-server --version` exits 0. strace: `openat(…/inst/libllama.so.0) = 3</…/alt/libllama.so.0.7.0>`; control maps to `ctl/libllama.so.0.7.0`.
   - The receipt would record the real `libllama.so.0.7.0` digest while the executed object is different. The alternate's sha256 is `3026d19b…c73`; the pinned real member is `983e1a2a…19fb6`.
   - Byte-flip control on the regular file changes the combined digest, so the pin does catch regular-file swaps. The gap is symlinks.
   - Threat model is the lesson's own: write access to the install dir, the same as its "consistent swaps".
   - [INFERENCE] A live receipt for the retargeted tree would be VALID on all six pins. No live run: I avoided listeners.

2. **The grid cannot see links, and "swap" is a receipt edit.** install-tree-grid.py:86-89 sets one member digest to `"a"*64` and recomputes the combined digest. No file changes and no process runs. Link names passed as `--members` report `absent` (`baseline=VALID members=2 rejected=0/2`, exit 1). With the pin on, 3/3 follows from the equality check alone, because any changed member changes the combined digest. The grid does not measure producer coverage.

3. **The lesson inverts the count.** round-19.md:17 says the swaps "are accepted 0/3 before the pin". The grid measured `rejected=0/3` without the pin (exit 1, all three `accepted`). That is 3/3 accepted. SCORECARD.md:833 has the right form.

4. **The grid's text line reads as success on invalid baselines.** install-tree-grid.py:96-111 prints `rejected=N/N` before returning 2 for an INVALID baseline. A zero-digest pin and a missing `--gate` both print `baseline=INVALID members=3 rejected=3/3` with exit 2. Any non-zero gate exit counts as "rejected" (:94), including 2 and 3. The exit code protects run.py:66-68, but the printed line is vacuous.

5. **The knowledge entry misstates its citation.**
   - Word counts are wrong against the fetched ld.so(8) page. The DT_NEEDED quote is 10 words, not 11 (round-19.md:28; SOURCES.md:69). The `$ORIGIN … expands to…` quote is 11 words, not 14 (round-19.md:27). The full span matches neither: 15 words.
   - Row 29, "identity is not authentication", is attributed to the same page. The page has 0 hits for authentic, digest, hash, integrity or identity. The reject is correct; its basis is the lesson's inference and must be marked [INFERENCE] or cited to repo evidence.

6. **The knowledge file is not corrected for the sixth pin.** corpus/knowledge/llamacpp-loading-lifecycle.md:309-310 still says only one of 51 members is pinned. There is no sixth-pin text in corpus/knowledge. Nothing says the sixth pin is opt-in: the flagless gate accepts a self-consistent tree (grid no-pin, exit 1).

7. **The pin is self-referential and pre-launch.** run.py:57-60 computes the pin with the producer's own `install_tree()` over the same directory. The tool computes the receipt field with the same function once, at :1268, before `Popen` at :1341. There is no re-digest after launch or teardown and no `/proc/<pid>/exe` or maps check. The receipt's server block (arg, install_tree, install_tree_sha256, realpath, server_impl_sha256, sha256) records no loaded objects. So a blind spot in `install_tree()` is shared by pin and receipt. Window size not measured [INFERENCE].

8. **The gate selftest fixture is not producer-shaped.** check-receipt.py:1566-1572 builds its synthetic tree with `libllama.so`, a link name the producer never emits. The tree-pin cases (:1781-1784, :1864-1872) pass only on that fixture.

9. **The claim omits a boundary.** The loader also opens system NEEDED libraries outside the tree and the pin. In the control trace, libssl.so.3, libcrypto.so.3, libstdc++.so.6, libgcc_s.so.1, libc.so.6, libm.so.6 and libgomp.so.1 all resolve under /usr/lib.

10. **Process.** Lane HEAD is `8bf99ca`, one commit after the declared round-start `1b85a24`. The C2 bytes are uncommitted: check-receipt.py (M), install-tree-grid.py (untracked), runs/run.py (M). run.py refuses a dirty tree (run.py:8-16), so the official measurement must follow a commit.

## What holds

- The grid pair reproduces exactly: no pin, exit 1, `rejected=0/3`; pin, exit 0, `rejected=3/3`.
- The gate's pin is an exact equality check: pin matches gives VALID exit 0; pin 0×64 gives INVALID exit 1; `--selftest` exits 0.
- Regular-file swaps change the producer digest (byte-flip control).
- The lesson's authentication rejection and SCORECARD.md:834-835 are correct.

## Axes

- Calibration (7, lowest): findings 3, 5, 6, 9 — wording, counts, citation, stale knowledge, unnamed boundary.
- Operability: findings 1, 2, 4, 7, 8 — coverage and measurement. The C2 delta 0 stands; the numbers are real.

## Smallest safe correction

1. Scope the claim: "observed identity of the 51 depth-1 regular files; opt-in; not authentication; excludes the 10 SONAME links and system NEEDED libraries." SCORECARD planned item (3), "state the boundary as policy", is the smallest honest route.
2. round-19.md:16-18: rewrite as "receipt-level member substitution (placeholder digest, combined digest recomputed, no file touched): without the pin all three accepted (rejected=0/3, exit 1); with it all three rejected (rejected=3/3, exit 0)."
3. round-19.md:27-28: correct the counts to 11 and 10 (the full span is 15). Mark row 29's "identity is not authentication" as [INFERENCE] or drop the page citation for that clause.
4. Append a sixth-pin correction to llamacpp-loading-lifecycle.md: opt-in, regular files only, links excluded, receipt-level. Retire the "only one of 51" residual at :309-310.
5. Grid text: print `rejected=n/a` when the baseline is not VALID; count only exit 1 as rejected. Add link rows that must be rejected; they fail until the producer changes, which gives an honest coverage number.
6. Only if the claim must cover loader-executed objects: hash links by resolved target (or fail closed on links leaving the directory) in `install_tree()`, re-run the grid, and replace the synthetic `libllama.so` fixture (check-receipt.py:1568) with a producer-shaped name.

Checks for the main agent after edits (not run by me): the grid pair, `python3 tests/llamacpp-live/check-receipt.py --selftest`, and the official harness on a clean commit.
