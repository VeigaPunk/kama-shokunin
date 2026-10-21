VERDICT: partial - the pin detects link-text changes, but "identity" overclaims: the digest is non-injective (a crafted name passes pin and gate), VALID-without-pin admits a non-loadable tree, and 9/9 is one-directional sensitivity on 8 cells that hit one dev link.

# LinksPolicyCritic - C2 policy critique (round 21, lane kama, draft a29bb84)

Axes weighed: false-accept of identity; false-reject cost; claim calibration; operability (AXES.md:13, runnable artifacts) vs freshness (AXES.md:14, drift detection). Lane untouched. Evidence and scripts: `build/out/LinksPolicyCritic/` (probe*.py, *-output.txt, grid/gate outputs, p1/ receipts, frozen-producer.py used by probe.py).

## 1. The four policy points
- **(a) Same-resolution rewrite counts as identity change?** Right for a topology pin; over-strict for a loaded-bytes claim. P3: tree digest unchanged, link digest changed, resolved bytes identical; gate VALID without pin, INVALID with the old pin. Keep the code (fail-closed, one re-pin); fix the claim.
- **(b) Reject every target containing '/'?** Over-strict for `./x` and same-directory absolute targets (P2: producer records them; gate reports "leaves the pinned directory", false for `./x`). Right for `../x` and `sub/x`, which leave the depth-1 tree the pin covers. Rejects no real install today: all 10 links in the real tree and all 10 in the upstream tarball are bare basenames (tar listing; grep for '/' in link targets exit 1).
- **(c) Link onto another pinned member is VALID without a pin?** Structurally right, but neither identity nor loadability. The grid's own cell retargets `libmtmd.so.0` to `LICENSE`: gate VALID with no pin; `ld.so --list` on a scratch mirror exits 127 (`libmtmd.so.0: invalid ELF header`) against 0 at baseline (P4b). "Pinned" is a misnomer: the target only has to appear in the same receipt's `install_tree` (check-receipt.py:196-197).
- **(d) Frozen 0/9 true by construction?** Yes. Frozen `install_tree` reads lstat-regular files only, and no link cell changes that set (P7: 4 of 4 link edits leave its digest unchanged). It is a control, not evidence of anything.

## 2. Is 9/9 meaningful? Not as a detection rate.
- Any change to the link map moves SHA-256, so 9/9 restates the cell design. It tests one direction only (changed when it should); it never tests equal-digest-different-topology (E1).
- Population: 8 of 9 cells mutate `libggml-base.so`, and no ELF in the tree lists a dev link in DT_NEEDED (P6). The ninth cell mutates `libmtmd.so.0`.
- The informative number is the gate without a pin: 4/9 rejected (dangling, absolute, `../`, loop), 5/9 VALID.
- No committed receipt carries `install_links` (`grep -rl '"install_links"' .ufo`: exit 1). Nothing was measured on a live run.

## 3. Defects beyond the four points
- **E1 digest not injective.** A link named `libllama.so -> libllama.so.0\nlibllama.so.0` with target `libllama.so.0.7.0` produces the same `install_links_sha256` (`a49818c8...`) as the two-link good tree. Gate CLI VALID with `--expect-install-links-sha256 a49818c8...` and with the tree pin (P1-CLI, exit 0 each). That directory has no `libllama.so.0`, so it is non-loadable [INFERENCE]. `install_tree` has the same ambiguity (P1b: frozen digests equal; current install_tree is byte-identical per the diff).
- **E2 optional field is a downgrade path.** Schema stays `kama-llamacpp-live/v3` (producer:49, unchanged). Strip `install_links` from a new receipt and the gate says VALID with no pin (P5; selftest case `links-absent-legacy-valid`).
- **E3 snapshot is pre-launch only.** `install_tree`/`install_links` are called once (producer:1293-1294); `Popen` at 1369; teardown at 1488; no post-run recheck. The repeat-after-teardown design in `.ufo/waves/round-16/build/advice/ConnectSouji.md:90` is not implemented.
- **E4 non-UTF-8 target** raises `UnicodeEncodeError` inside the snapshot (probe2 E5). Producer:1270 and 1480 route it to an internal setup-error, exit 2 [INFERENCE from code reading; not run live]. Fail-closed, but a robustness hole that `ensure_ascii` JSON removes.
- **E5 listing failure** returns `({}, None)` (P8) and is VALID without a pin, inherited from `install_tree`.

## 4. Is C2 an operability capability move?
It is hardening of `live-llamacpp-lifecycle`'s identity evidence, not a new capability, so it earns no capability row (AXES.md:62-64). Lane precedent: SCORECARD.md:828-838, round 18 "sixth pin", operability 8 -> 8, delta 0, "Capabilities unchanged". Use "hardening, 8 -> 8, delta 0"; "capability-shaped" invites a pre-claimed row. Freshness (drift detection, AXES.md:14) fits the pin better [INFERENCE]; the axis choice is the assignment's. Self-test green is capability, not measurement (PROTOCOL.md:390).

## 5. Proposed claim wording (C2)
> C2, operability hardening (8 -> 8, delta 0; no capability row). The receipt records the raw text of each symlink directly inside the server's install directory (`install_links`, `install_links_sha256`), read before launch. The gate recomputes that digest, requires each link chain to stay in the directory and end at a regular member recorded in the same receipt, and compares to `--expect-install-links-sha256` when given. Without the pin a receipt is self-consistent, not identity-verified; a retarget onto another recorded member is VALID and loadability is not checked. This is a topology pin: a same-resolution relink changes it by design. Measured: a 13-cell synthetic grid over a read-only mirror of the real install. Link digest changed in 9 of 9 link cells (sensitivity on hand-picked cells); frozen tree digest changed in 0 of 9 (true by construction); the gate without a pin rejects 4 of 9 structurally. Not shown: injectivity (E1), live runs with a changed tree, post-launch stability, file modes, upstream authenticity.

## 6. Smallest corrections before admission (cheap now: no receipt carries install_links)
1. Encode `install_links` canonically, e.g. `json.dumps(sorted(items), ensure_ascii=True, separators=(',',':'))`, in producer and gate. Tested in scratch only (probe3): collision gone, E4 encodable. Leave `install_tree` encoding (recorded digests depend on it) and state its limit.
2. Bump to schema v4 for receipts carrying `install_links`; gate requires the field for v4; v3 stays legacy (E2).
3. Reword the '/' message to "target contains '/'; only bare same-directory basenames are followed"; optionally normalise `./x`.
4. Reword "pinned" to "recorded in this receipt", "snapshot" to "pre-launch snapshot", and VALID to "self-consistent". LessonDraftC2's Limits omit E1, E3 and the loadability gap.
5. Optional: repeat the snapshot after teardown (E3); an soname-stem check so `libmtmd.so.0 -> LICENSE` fails without a pin.

## 7. Commands (scratch clone at a29bb84 unless noted; exit codes)
- `git clone -q` + `git checkout -q a29bb84`: 0. `git show --numstat a29bb84`: 0 (2 benign deleted lines in check-receipt.py; producer 28+/0-).
- `install-links-grid.py --selftest`: 0 (12/12). `check-receipt.py --selftest`: 0 (9 VALID + 1 NOT-EVALUATED; 90 mutations).
- Grid on `~/.local/opt/llama-b11755` (mirrored, never written): `--arm current`: 0 (link 9/9, wrong 0); `--arm frozen`: 1 (link 0/9, expected); default and `--json`: 1 (frozen arm expected to fail).
- `probe.py`: 0 (P1-P8). `probe2.py`: 0 (E5; P1-CLI four gate runs, each exit 0 VALID). `probe3.py`: 0.
- `ld.so --list` on scratch mirror: 0 baseline, 127 after retarget. Loader trace mode only; no program run; llama-server not launched.
- `tar -tvzf ~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz`: 0; sha256 `753bfa73...e226` matched (exit 0); grep '/' in link targets: 1 (none).
- `find ~/.local/opt/llama-b11755 -newermt 2026-10-21 | wc -l`: 0, count 0 (real tree unmodified). `grep -rl '"install_links"' .ufo`: 1 (none). No llama-server or harness process left running (ps grep: 1).
- Not run by rule: the live harness, any llama-server launch, any write to the real tree or the lane.

Tooling: no installs or updates (used git, python3 3.14.8, binutils readelf, tar, sha256sum). Scratch `/tmp/kama-r21-LinksPolicyCritic` removed at end.
