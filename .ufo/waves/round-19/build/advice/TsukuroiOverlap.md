VERDICT: confirm - no tsukuroi claim is contradicted by the install-tree digest; the boundary is pacman local-DB membership, and llama-server's 13 pacman-owned /usr runtime paths sit outside the digest.

Scope: tsukuroi-shokunin HEAD 2fd1e67 (5 uncommitted entries; scanned as a frozen copy). Every command, exit and hash: /tmp/kama-r19-TsukuroiOverlap/out/receipt.md. Only lane write: this file, as the trailer requires.
Axes: operability (C2 pin scope), calibration (C2 claim wording). No sibling edited.

## Boundary line
- `pacman -Qo <path>` rc 0 -> tsukuroi's arms: ownership, `-Qkk`, `-Qu`, foreign census, `IgnorePkg`/`IgnoreGroup` pins.
- rc 1 -> no tsukuroi arm. `llama-server`, `libllama-server-impl.so`, `libllama.so.0.7.0` under `~/.local/opt/llama-b11755` all return rc 1. For those files the install-tree digest is the only identity.
- Digest membership: 51 depth-1 regular files (`os.lstat` + `S_ISREG`, tools/kama-llamacpp-live.py:191-194). Excluded: 10 SONAME symlinks, 0 subdirectories.
- The two sets meet at the dynamic loader. `ldd llama-server` resolves 13 `/usr` paths, all pacman-owned: openssl 3.6.5-1 (libssl, libcrypto); glibc 2.44 (libc, libm, ld-linux); libstdc++, libgcc, libgomp 16.2.1; zlib 1:1.3.2-4; zstd 1.5.7-3; brotli 1.2.0-1. The digest cannot see them.

## Sibling claims checked
| tsukuroi claim | source | result |
|---|---|---|
| "pins" = pacman config pins; `pins=none holds=pacman glibc` | tools/tsukuroi-census.sh:696-717; SKILL.md:397-399 | Not contradicted. IgnorePkg, IgnoreGroup, NoUpgrade, NoExtract all empty (rc 0). HoldPkg is removal-only, so `-Syu` can still upgrade glibc. `pins=none` says nothing about `~/.local/opt`. |
| `-Syu` touch surface; pins/holds | PROVINCE.md:8-14 | Not contradicted. [INFERENCE] No owner means no pacman write to the 51 tree files. `-Syu` can change the 13 runtime paths. |
| foreign = local DB minus sync DBs | corpus/knowledge/aur-risk-plane.md:30-31 | Not contradicted. llama is in neither `-Qm` nor `-Qo`. Matches tsukuroi's r18 note (.ufo/waves/round-18/build/ConnSibling.md:13). |
| linkage/ABI out of province; route to kaidoku/revenger | aur-risk-plane.md:289-295; update-safety-v2.md:164 | Not contradicted, but a gap: owners are visible, linkage verdicts are not. Nothing currently witnesses what llama loads. |
| install-tree or llama identity claims | negative search, receipt Q6 | None in tsukuroi-owned areas. Only observations of kama's server. |

## Findings
1. Stale tsukuroi baseline (not caused by kama). Live `pacman -Qm` = 17; embedded r6 baseline = 16. Live census prints `foreign=17(known=3 new=1 drift=13 gone=0) base=r6(16) new=[zcode]`, packages DEGRADED (receipt row 17). tsukuroi's own r18 notes already record this (corpus/knowledge/foreign-provenance-r6.md:339-341). Route to tsukuroi's owner; do not patch in kama.
2. C2 grid is receipt-level. tools/.../install-tree-grid.py:86-91 deep-copies the stored receipt JSON, forges one member digest, and recomputes the combined digest. Its 3/3 result tests the gate on forged receipts, not on-disk swaps or runtime identity. Re-run here: pin positive exit 0 VALID; all-zero pin exit 1 INVALID.
3. In-tree seam (kama-owned). The 10 SONAME symlinks sit outside the digest. [INFERENCE, not run] Retargeting one (e.g. `libllama.so.0`) would change what loads while `install_tree_sha256` stays fixed. `ldd` shows SONAMEs resolving through these links.

## Proposed move (one)
Scope, don't extend.
(a) Rewrite C2's claim as: "the gate rejects a stored receipt whose install_tree differs from the pin." Zero code.
(b) Record the runtime closure as a separate, non-gated side artifact: the child's `ldd`-resolved paths with sha256 at readiness. Leave owner attribution to tsukuroi.
This makes a pacman-driven runtime change visible as a receipt diff, without putting `pacman` queries into kama's gate, which would overlap tsukuroi's surface. Harm: none to check-receipt keys (side artifact only). Cost: one `ldd` and sha256 per run.

## Risks
- If L1 reads C2 as runtime identity, a `-Syu` of openssl, glibc or libgomp would leave the pin green while behavior changed. Local sync DB shows no pending row for those owners (`pacman -Qu` rc 1, 0 lines), but upstream state is [unk] (SKILL.md:391).
- "pin" means three things across the fleet: tsukuroi's pacman IgnorePkg, kama's baseURL pins, kama's install-tree digest. Keep them apart in claims.

## Verification (executed; exits in receipt.md section A)
- `pacman -Qo` on the three llama files: rc 1 each. `pacman-conf` IgnorePkg, IgnoreGroup, NoUpgrade, NoExtract: rc 0, empty. HoldPkg: rc 0 (`pacman`, `glibc`).
- `pacman -Qm`: rc 0, 17 rows. diff vs embedded r6: rc 1 (13 drift, 1 new).
- `pacman -Qu`: rc 1, 0 lines.
- census in frozen copy (read-only): rc 1, stderr 0 bytes, packages DEGRADED, foreign=17.
- producer `install_tree` on the server path: rc 0, 51 files, `6c216313...5a2c`. One misuse (directory argument) disclosed in receipt row 19 and not used.
- `ldd` and `readelf`: rc 0. The 13 `/usr` owners: rc 0 each.

Checks for the main agent to run: none for this verdict. Item 1 belongs to tsukuroi's next round.
