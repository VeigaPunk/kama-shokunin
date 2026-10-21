VERDICT: partial - links digest is injective on every producer-reachable map and the C0/subdir/unreadable rules hold; silent drops, out-of-dir PASS, a 41-hop gate accept and the single pre-launch snapshot let the loader resolve differently while the gate stays VALID.

# C2DigestSentinel: canonical links digest and fail-closed rules at a6617149

Attacked: producer `install_tree`/`install_links`/`links_digest` (tools/kama-llamacpp-live.py:178-245) and snapshot-to-launch in `main()` (:1374-1396, launch :1454); gate `install_links_sha` (tests/llamacpp-live/check-receipt.py:173-178), `link_chain_problem` (:181-198), links block of `validate` (:442-481). Scratch clone only; lane untouched; no llama-server, no live tool. Producer `main()` ran with `subprocess.Popen` replaced by a launch sentinel. Evidence: `falsify/out/C2DigestSentinel/` (attacks/, results/ with exits.txt, receipts/). Reproduced from scratch with `attacks/setup.sh` then `run_all.sh`: all 9 steps exit 0; only the E4 timing line differs.

Findings (severity is my estimate):
- F1 Med. Tree and links are read once, pre-launch (:1375-1376); no later call (grep). The model gets a post-run rehash (:1676); tree/links do not. Retarget `libllama.so.0` after snapshot: loader 1 -> 2 and the links digest changes, yet the gate on the pre-retarget receipt with its own pins is VALID: `check-receipt.py receipts/b2-snapshot-before-retarget.json --require-install-links --expect-install-links-sha256 deb111fa5739ffa31de111667ad4b1f085391143f1b88c757b5801364ce4aac9 --expect-install-tree-sha256 cde95062dc3ac3f6097b6566046dfd8abd669fa069f956587352818167b437f1` -> VALID, exit 0 (b_loader B2). Adding `libz.so.1` beside a RUNPATH=$ORIGIN binary after snapshot: system zlib 1.3.2 -> attacker lib; gate VALID with its tree pin, exit 0 (e_extra E1). Needs a same-user write in the window [INFERENCE: window not timed].
- F2 Med-Low. `install_tree` drops a member on OSError at lstat or read (:191-199). `install_links` only tests `os.access(R_OK)` (:241) and never opens files. Fault-injected EIO or an unlink race: `main()` reaches launch (sentinel=1) with 2 of 3 members and install_links problems `[]` (d_producer_main D1, D2). Gate: VALID without pin (exit 0), INVALID with honest pin (exit 1). Violates the docstring's "never a silently smaller identity".
- F3 Med-Low. Producer PASS on out-of-directory links. A symlink named `glibc-hwcaps` to an external dir (absolute or `../`) makes glibc 2.44 load external `libllama.so.0`, 1 -> 2, since x86-64-v4 is searched first (f_hwcaps F2, F3). install_links reports no problem; `main()` reaches launch; `_outcome_exit` (:916-930) ignores links. Only the gate rejects it ("leaves the pinned directory", exit 1).
- F4 Low-Med. Gate accepts a 41-hop symlink chain. Kernel: open() ELOOP at 41, OK at 40; dlopen fails "Too many levels of symbolic links" (b_loader B1). Gate: no hop bound; producer-shaped receipt VALID with its own pins (c_gate C5, exit 0). Load fails closed, but the receipt claims a resolution the loader cannot perform.
- F5 Low. Gate accepts C0 control characters in tree names; producer rejects them (:231-234); the gate's tree check is value-only (:394-397). Merged key `"libA <h1>\nlibB"` -> h2 gives the same install_tree_sha256 (a_producer_names A7; c_gate C1 exit 0 with honest pin). Pins bind digests, not member sets.
- F6 Low. `--require-install-links` passes `install_links: {}` with null digest (allow_none=not links, :455). Producer never emits null; its digest of `{}` is 44136fa3... (c_gate C3 exit 0).
- F7 Low. Duplicate JSON keys: gate `json.load` (:2344-2345) is last-wins, VALID (c_gate C4, exit 0); a first-wins reader gets another digest and a chain to a missing `libllama.so.0.7.1`.
- F8 Low. Non-UTF-8 link names/targets accepted (:229-245, no encoding check); keys are lone-surrogate escapes. jaq 3.1.1 (the `jq` here) merges `\udcfe` and `\udcff` into one key and keeps the valid value; gate exit 1 on the same receipt; node JSON.parse keeps both (e_extra E2).
- F9 Low, claim. `links_digest` says "injective for any {str: str} map" (:206-207). False: `{'\ud83d\ude00':x}` and `{'😀':x}` hash equal (a_producer_names A1). Unreachable: surrogateescape yields only U+DC80-DCFF (A2, e_extra); gate reads strict UTF-8 (c_gate C2, exit 2) and json.loads joins escape pairs. Injective on every producer-reachable map.
- F10 Info. "Canonical JSON" is Python-specific: an RFC 8785-style serialization of `{"libé.so.0":...}` hashes differently (e_extra E3).
- F11 Info. Gate on a surrogate tree name: UnicodeEncodeError traceback, exit 1, no problem list (c_gate C7). Producer maps the same case to `internal:UnicodeEncodeError`, exit 2 (d_producer_main D3): fail-closed, undocumented token.
- F12 Info. Gate chain walk is O(n^2): 4000 links, 0.60 s (e_extra E4).

Held (executed):
- C0 name in any entry -> `control-character-in-name`, exit 2 (D5). `glibc-hwcaps/` directory -> refused (D6). Mode-000 regular file -> `unreadable` (D7).
- NFC vs NFD: distinct keys; gate matches kernel bytes (A4). No `normalize` in producer or gate. [INFERENCE] casefold/APFS-style normalizing filesystems not exercised.
- Long targets bounded by the filesystem (XFS, 1023 B on /tmp; B0); no producer/gate divergence (A5).
- DEL, C1, U+2028/U+0085, U+200B, U+202E names accepted; ensure_ascii escapes them (g_extra G2).
- Surrogate-escaped key maps back to the kernel's bytes (g_extra G1).
- Retargets move the links digest, not the tree digest (B2): as designed.
- Gate rejects absolute, `../`, dangling and loop links (c_gate C8; selftest covers them).
- Gate selftest exit 0: 11 VALID + 1 NOT-EVALUATED, 91 mutations (results/gate-selftest.txt). Its link cases do not cover hop count, duplicate keys, C0 tree names, empty links with null digest, or surrogate names.
- Real tree reproduces: 51 members `6c216313...`, 10 links `5cb9f486...`, problems `[]` (read-only, exit 0).

Can a tree make the producer record links the gate accepts while the loader resolves differently?
- File-level, static: not found. Targets with `/`, `.`, `..` are gate-rejected; hwcaps shadows need those or a directory (producer-rejected).
- Failure-level, static: yes at 41 hops (F4).
- Dynamic: yes (F1, F2). The receipt is a pre-launch snapshot; nothing binds the loader's view afterwards.

Smallest fixes:
1. Re-run install_tree/install_links after the run; fail on mismatch (the round-16 `install_tree_stable` design; absent at a6617149).
2. install_links: open and read each regular member; propagate OSError from install_tree; flag targets with `/`, `.`, `..`, the name `glibc-hwcaps`, and non-UTF-8 names.
3. Gate: hop bound 40; reject C0 or surrogate tree names; require a non-empty links block when present; `object_pairs_hook` rejecting duplicate keys.
4. Correct the `links_digest` docstring and the "canonical JSON" label.

Limits: EIO and the unlink race are injected by monkeypatch. Tested on XFS /tmp with glibc 2.44; the install directory's filesystem was not tested.

Tools: none installed or updated. Present and used: gcc, readelf, ld.so, jq (jaq 3.1.1), node v24.21.0, python 3.14.8. Scratch removed after the out-dir copy.
