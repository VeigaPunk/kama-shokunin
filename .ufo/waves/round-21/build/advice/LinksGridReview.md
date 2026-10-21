VERDICT: partial - real-tree counts reproduce exactly (frozen link 0/9, current 9/9, controls 3/3, null 0/1, back-compat equal; selftest 12/12), but three could-not-evaluate paths exit 1, a symlinked --tree gives a false FAIL, and SERVER resolution diverges from the producer.

Scope: tests/llamacpp-live/install-links-grid.py @ a29bb84 (lane HEAD a29bb84; lane file sha256 4a538de2...ee93 == git blob). Executed from a scratch clone, never the lane. Frozen arm = 7a6bc911 producer via git show. Tools: none installed (python3 3.14.8, git 2.56.0, system). Full exit list: build/out/KamaR21.LinksGridReview-6/exit-matrix.txt

## Executed commands and exits
- --selftest exit 0; --arm both exit 1; --arm current exit 0; --arm frozen exit 1; --json exit 1; --arm current --json exit 0
- Verbatim, --arm both:
  summary arm=frozen link=0/9 regular=2/2 type=1/1 null=0/1 wrong=9 status=fail
  summary arm=current link=9/9 regular=2/2 type=1/1 null=0/1 wrong=0 status=pass
  back_compat install_tree_sha256 equal=True
- Verbatim, --arm current: summary arm=current link=9/9 regular=2/2 type=1/1 null=0/1 wrong=0 status=pass
- --json summary: frozen {link 0/9, regular 2/2, type 1/1, null 0/1, wrong = 9 link cells, status fail}; current {link 9/9, regular 2/2, type 1/1, null 0/1, wrong [], status pass}; back_compat_install_tree_sha256_equal true
- --selftest: 12 `ok` lines, then `selftest cases=12 failed=0`.

## Verified OK
- Cells (cell-effects.txt): the 9 link cells touch only links; the 2 regular cells only regular files; the type cell replaces a link with a regular copy; null touches nothing.
- Frozen sha256_file and install_tree are AST-identical at 7a6bc911 and a29bb84 (ast_equal=True); install_links is new. The frozen arm is the faithful pre-round identity.
- Standalone re-derivation (digest_check.py, 51 regular + 10 symlinks) equals JSON real_identity: install_tree 6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c; install_links b58f1b4df160c4e2accb95bac964a5648d24fc31e769f8044296a1fa431b9e10.
- Mirror fidelity guard fires on a lossy mirror: "could-not-evaluate: mirror identity differs ... (current)", exit 2.
- Gate chain verdicts match cell semantics: dangling, outside, '..' and loop flagged; valid retargets quiet.
- Real tree untouched: 61 entries, none newer than 2026-10-20 08:11; no leftover temp dirs.

## Findings (severity order)
1. MEDIUM exit contract. Docstring lines 22-25 and sibling install-tree-grid.py lines 21-23 (exit 2 for "the grid's own fault") reserve 2 for could-not-evaluate. Three paths exit 1 instead:
   a. build_cells line 115: next() raises StopIteration when no regular member other than the first link's target exists. Synthetic tree -> exit 1 with traceback.
   b. selftest path (main lines 314-319) catches EvalError only. Forced tempfile.tempdir failure: --selftest exit 1; --arm current exit 2.
   c. frozen_producer line 62 uses text=True (locale codec). LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0 --arm frozen -> exit 1 (UnicodeDecodeError); --arm current (utf-8 read, line 72) -> 0. None of the 12 non-ASCII lines fall inside install_tree/sha256_file (lines 171-202).
   Fix: map any exception at the evaluation boundary to 2; next(..., None) -> EvalError; encoding="utf-8" on the frozen read.
2. MEDIUM-LOW false FAIL on a non-canonical --tree. Line 116 compares unresolved str(tree / r) with resolved realpath(first). Synthetic tree reached through a symlink -> exit 1, both retarget cells current=same (wrong=2); canonical path -> 0. The real tree is unaffected only because its first sorted regular file (LICENSE) is not the first link's target. Fix: compare os.path.realpath(tree / r).
3. DECISION default --arm both (line 310) can never exit 0: the frozen arm always misses by design (selftest line 275 asserts it). Any caller that omits --arm reports failure. Make current the default, or document it.
4. DECISION the gate verdict is informational. Synthetic tree with dangling soname liby.so -> liby.so.9: --arm current exit 0, null row gate=liby.so:chain ends at 'liby.so.9'. Docstring says "reports"; decide whether real-tree chain problems should fail the run.
5. LOW latent SERVER mismatch. identities() receives unresolved tree / SERVER (line 173); the producer resolves os.path.realpath(server_arg) (tools/kama-llamacpp-live.py:1276). Executed probe (ast_and_realpath.py) with a symlinked llama-server: install_tree(unresolved) = ['libx.so.1'], install_tree(realpath) = ['a.so.1', 'llama-server'], digests differ. Inert today: the real llama-server is a regular file. Fix: realpath in run().
6. LOW coverage and cell defects.
   a. link-same-resolution-shortcut's './' branch (lines 133-136) runs only for a single-level first link. Neither the real tree nor the selftest tree has one, so no test reaches it. Its gate message "leaves the pinned directory" is wrong for same-directory './x'.
   b. link-dotdot's target is unresolved in the mirror (cell-effects.txt), so it never tests a resolvable parent-directory target.
   c. selftest omits the fidelity guard (positive control above), frozen-load failure, and render/main output.
   d. Retarget cells point to LICENSE, not a soname member (valid, but not the R19 libllama.so.0 case).
7. LOW provenance. The current arm reads the working tree (lines 70-73). JSON records only frozen_rev, not the current producer/gate sha256 or revision.
8. NIT. gate_module (lines 76-80) writes tests/llamacpp-live/__pycache__/check-receipt.cpython-314.pyc (git-ignored; visible in git status --ignored after runs). Docstring lines 19-20 say "for every link cell" but the code (195-204) reports every row. regular-append-byte (line 141) leaves its file handle unclosed.

## Residual risk / gaps
- Real-tree evidence is single-host (51 regular, 10 symlinks). The gate selftest and receipt validation were not reviewed (out of scope). No llama-server launched; no model touched.
- Findings 1b, 1c, 2, 5 and the cell effects are executed probes. Findings 3, 4, 6a, 6b, 7 and 8 are code-reading claims backed by cited lines; no measured count rests on [INFERENCE].

## Outputs
- build/out/KamaR21.LinksGridReview-6/: arm-*.txt/.err, both.json, current.json, selftest.txt, cell-effects.txt, real-tree-digest-recompute.txt, exit-matrix.txt, probe scripts (inspect_cells.py, digest_check.py, ast_and_realpath.py, fidelity_control.py).
- Scratch /tmp/kama-r21-LinksGridReview removed after this report was written.
