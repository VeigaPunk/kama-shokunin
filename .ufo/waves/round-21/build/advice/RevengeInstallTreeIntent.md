VERDICT: confirm - a separate install_links map preserves install_tree's regular-file membership, digest and back-compat; no consumer asserts link absence, but the R21 gate rule, the grid back-compat check and the pinned digests encode it.

# RevengeInstallTreeIntent (KamaR21, revenger, read-only)
Basis: committed draft a29bb84 read via `git show` (HEAD line numbers). Lane not modified. Producer working tree differs from HEAD by one blank line at line 1152 (selftest, after install_tree/install_links); observed, not investigated.

## 1. Original intent (reconstructed)
- Introduced in b8e485c (round 16). Docstring: "Symlinks are skipped as members (they are not regular files)." Code: `os.lstat` + `stat.S_ISREG` (producer 178-202; lstat 191, S_ISREG 194). Never `islink`/`is_file`.
- Body unchanged since: `git log -L :install_tree:tools/kama-llamacpp-live.py` lists only b8e485c (exit 0). Body sha256[:16] = 7a5990c1e7b691c0 at b8e485c, 7a6bc911 (frozen) and a29bb84 (draft). No commit body states a reason.
- R16 design text: LiveHarness.md:10 "install_tree ... over regular files only, symlinks excluded"; SentinelInstallChain.md:56 "All 10 point to relative in-tree targets" (`.ufo/waves/round-16/build/advice/`).
- Lineage [INFERENCE]: fleet digest-scope convention. souji `corpus/QUALITY.md:49` (Q20: "regular non-symlink file digests"); ConnectSouji.md:86-87 proposes "refuse a symlinked tree - the same refusal souji applies to digest scopes, SKILL.md:35".
- Divergence: souji `corpus/lessons/round-5.md:9-13` classed silent symlink omission from a digest scope (`find -type f`) as a false-SAFE defect and fixed it fail-closed (`symlink-present`). kama skips silently; R19 named that debt.
- Unstated side effect [INFERENCE]: lstat+S_ISREG also keeps FIFOs and devices out of the read set (TreeCap.md fixture-main: fifo=1, excluded). `isfile` would follow links.

## 2. R19 lesson text (verbatim)
`corpus/lessons/round-19.md:53-57`: "Symlinked sonames are unpinned (TreeCap). `install_tree()` pins regular files only; the launcher's `libllama.so.0`/`libggml.so.0` soname symlinks are skipped, so retargeting one leaves `install_tree_sha256` unchanged. The sixth pin is therefore regular-file identity, not complete install identity; a symlink-aware pin is named debt."
Also round-19.md:77 (M3) and `SKILL.md:646-648`: "binds the observed regular-file install tree, not soname-symlink destinations or authenticated execution."

## 3. Consumers of install_tree (HEAD)
- `check-receipt.py:459-461` rejects a link name that is also an install_tree member; `:181-198` requires each chain to end at a member. With links as members, all 10 would fail (intent_check: 10/10).
- `install-links-grid.py:43` frozen arm (FROZEN_REV 7a6bc911) and `:218-226` back-compat assertion: depend on the unchanged digest.
- Pin `6c216313...85a2c`: 11 live receipts; `knowledge/llamacpp-loading-lifecycle.md:107,316-322`; `round-19-verifier-spotcheck.md:85-86`; `.ufo/waves/round-18/runs/run.py:58-68` (derived at run time). Links-as-members digest = f2e76823...; every cross-version `--expect-install-tree-sha256` would fail.
- `check-receipt.py:406-421` recomputes and pins the stored map; `install-tree-grid.py` (0 symlink refs) and `controls.py:128-129` (tree timing only) depend on nothing about links.
- No consumer explicitly asserts link absence (scan: producer 220 only). `receipt_scan.py`: 20 receipts, 11 live; no live receipt lists a link name. Synthetic round-20 `GateSelftestCrash` receipts list `libllama.so` as a regular member; the gate cannot see kinds.

## 4. Does a separate install_links map preserve the intent? Yes, with caveats
- Preserved: install_tree body identical; install_tree_sha256 on the real tree = 6c216313 for frozen and draft, 51 members. Links are read by lstat+readlink (producer 219-223), never followed or hashed as members.
- Sandbox (intent_check.py, /tmp, removed): same-dir and absolute soname retargets both leave install_tree_sha256 unchanged and change install_links_sha256; the gate rule rejects the absolute target.
- (a) New opt-in surface: benign link churn moves install_links_sha256 only. Say so in the pin wording.
- (b) Recording, not refusal, departs from the fleet rule (Q20; SKILL.md:36). Refusal would reject the upstream release, which ships the same 10 links with identical text (tarfile check PASS). [INFERENCE on the choice]
- (c) readlink OSError is silently dropped (producer 221-223), the omission class of souji `round-12.md:76` (M14). Fail-closed would fit the fleet rule and touch install_links only.
- (d) Legacy receipts lack install_links; their symlink gap stays by design.

## 5. Evidence (commands, exits)
- `git -C <lane> log -L :install_tree:tools/kama-llamacpp-live.py --format=...` -> 0; `log -S install_tree` -> 0; `log -S islink`, `log -S is_symlink` -> 0, no output.
- `git show <rev>:<path>` reads in the probes -> rc 0.
- `python3 .ufo/waves/round-21/build/out/RevengeInstallTreeIntent/intent_check.py` -> 0, ALL_OK, 19 checks (summary.json).
- `python3 .ufo/waves/round-21/build/out/RevengeInstallTreeIntent/receipt_scan.py` -> 0 (receipt-scan.json).
- Not run: selftests and grids (outside scope). Tools installed: none. Scratch removed (`find /tmp` -> 0, empty).

## 6. Advice
1. Keep install_tree's formula and membership frozen; never add link names to it.
2. Consider fail-closed readlink in install_links (fleet M14), or name it as a residual.
3. Pin wording: "observed regular-file identity plus link name -> text; not authentication".

Confidence: high for membership and back-compat (executed); medium for lineage (documents only). No original rationale is recorded anywhere in the lane. Evidence: `.ufo/waves/round-21/build/out/RevengeInstallTreeIntent/`.
