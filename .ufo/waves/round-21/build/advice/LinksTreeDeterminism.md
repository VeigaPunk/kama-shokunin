VERDICT: confirm - one unreadable or unlinked member is silently dropped and the gate stays VALID (44/51 unreadable, 45/51 raced members, 5/10 raced links); the producer must fail closed; the install_links skip and null-digest rule are C2, install_tree is separate debt.

# LinksTreeDeterminism (round 21, leaf probe)

Subject: a29bb84. Producer `tools/kama-llamacpp-live.py` install_tree 178-202, install_links 205-226. Gate `tests/llamacpp-live/check-receipt.py` tree check 406-421, links block 441-477 (line 454 `allow_none=not links`).
Method: `cp -a` of ~/.local/opt/llama-b11755 (51 regular, 10 symlinks, 56,288,566 B) into scratch. Faults injected only there: chmod 000, unlink between listdir and lstat, listdir denied. Each restored and re-verified. Gate verdicts from the gate CLI (0 VALID, 1 INVALID). Commands and exits: out/LinksTreeDeterminism/COMMANDS.txt.

## Observed (executed)
1. Silent drop. chmod 000 on libggml-cpu-haswell.so: producer returns 50 members, digest f0975a70... (healthy 6c216313...), no error. Gate default exit 0 (VALID); with --expect-install-tree-sha256 6c216313... exit 1 (cli-matrix.txt). Matches R19 TreeDeterminism row 14 (prior run).
2. All 51 regular members (sweep.tsv, summary.json):
   - unreadable: 44 VALID with changed identity; 5 INVALID via link chain (link targets); 2 fail closed in main (llama-server access check; libllama-server-impl.so sha raises PermissionError). Tree pin catches 49/49.
   - unlinked between listdir and lstat: 45 VALID with changed identity; 5 chain + 1 server-basename INVALID; tree pin 51/51.
   - Share of total bytes per silent cell: min 0.0% (LICENSE), median 0.31%, max 17.3% (llama-connect, 9,729,072 B).
   - Silent set: 43 ELF outside llama-server's DT_NEEDED closure plus LICENSE. No tree ELF NEEDs a libggml-cpu-* variant (0/50). The race adds libllama-server-impl.so: VALID with server_impl_sha256 null.
3. install_links (new in a29bb84): an unlinked link vanishes silently. Outer links (libllama.so, libggml.so, libggml-base.so, libllama-common.so, libmtmd.so): 5/10 VALID with changed links identity. Middle links: 5/10 INVALID via chain. Links pin catches 10/10.
4. Gate hole (C2): `install_links: {}` with `install_links_sha256: null` is accepted (line 454). Links-only listing denied: gate exit 0 VALID; with --expect-install-links-sha256 exit 1. Tree listing denied: exit 1 (empty tree, fail closed).
5. The gate cannot see an omission in a self-consistent receipt; only a producer fail-closed or an operator pin can. The chain check catches the 5 link targets only incidentally. C2's own comment (check-receipt.py:441-443) requires every soname symlink to be "recorded, digested and resolve inside the pinned regular-file tree".
6. Provenance: install_tree and its silent skips first appear in b8e485c (round 16; `git log -S'return tree, None'`) and are unchanged at 7a6bc91 (lines 186/192/198). The install_links skip and gate line 454 are new in a29bb84.
7. The same producer raises on a non-UTF-8 member name (UnicodeEncodeError), so silence on OSError is a choice, not a constraint.

## Fail-closed proposal (scratch copies only; lane untouched)
- install_tree and install_links: remove the try/except around listdir/lstat/open/readlink so OSError propagates. main() then records internal:<Type>, outcome setup-error, exit 2, no identity. Checked in-process with Popen tripwired: exit 2, child_pid null, tree restored (failclosed_main.txt).
- Gate line 454: `allow_none=False`.
- Fix copy: unreadable 51/51, race-member 51/51, race-link 10/10, listing 3/3 become SETUP-ERROR. Healthy digests unchanged (6c216313..., b58f1b4d...). C2 grid `--arm current` JSON byte-identical to baseline (cmp exit 0). Grid selftest 12/12 exit 0; gate selftest exit 0 (9+1, 90 mutations).
- The gate change alone is insufficient: under the fixed gate, the haswell and outer-link receipts still exit 0.
- Patches: proposal.diff (both), proposal-C2.diff (install_links + gate), proposal-separate-install_tree.diff (install_tree); all `git apply --check` exit 0. Split runs: C2-only closes the 10/10 link races and the links-only listing but leaves 44/45 member cells silent; tree-only closes 102/102 member cells (51 unreadable + 51 race) but leaves 5 link-race cells and the links-only listing silent.

## C2 vs separate debt
- install_links skip and null-digest rule: belong to C2. C2 introduced both, and its claim (every soname symlink recorded and bound) does not hold while they stand. Fix inside C2. The C2-only variant was not grid-run; the combined fix was.
- install_tree skip: separate debt (name: TreeFailClosed). Pre-existing since round 16. C2 keeps install_tree untouched for back-compat, and C2's 13-cell grid has no unreadable or race cell, so folding it in would ship untested error-path behaviour under C2's name. Acceptance: grid cells for unreadable member, unlink race and listing denied, each expecting setup-error; healthy digest unchanged.

## Unknowns
- [INFERENCE] Runtime effect of a silently missing libggml-cpu-* variant: libggml exports ggml_backend_load_all_from_path (observed) and no tree ELF NEEDs a variant (observed), so variants are dlopen-loaded. The directory-scan behaviour was not verified live.
- [INFERENCE] With libllama-server-impl.so missing the receipt is VALID, but the server stub cannot load (DT_NEEDED observed; not launched).
- [INFERENCE] Likelihood of an unreadable or raced member in normal use is low; not measured.

## Installs, writes, processes
- Installs: none. Tools used: git, readelf, python3, diff (already present). No pacman, no uv.
- Writes: this report and out/LinksTreeDeterminism/ (new). Lane untouched; fleet repo read via clone only.
- No llama-server or live tool run. The one main() call ran on the fix copy with Popen tripwired. No persistent processes. Scratch deleted after copy.
