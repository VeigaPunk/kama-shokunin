VERDICT: partial - literal 83bdd3cc, receipt digest 5cb9f486 and encoder identity recompute exactly; at a6617149 the literal misses ensure_ascii and key-order drift, and --require-install-links passes an empty map with a null digest.
Attacked: SELFTEST literal (check-receipt.py:1512, canonical case :2015-2023); live receipt server.install_links digest 5cb9f486 (runs/b76727f3/live-receipt.json); encoder pair check-receipt.py:173-178 vs kama-llamacpp-live.py:205-210. Pinned commit a6617149 plus the lane worktree, which is dirty (see Lane state). Line numbers are a6617149's.

## Confirmed (commands run; exit in brackets)
1. printf '%s' '{"libllama-alias.so":"libllama.so.0","libllama.so.0":"libllama.so"}' | sha256sum = 83bdd3ccfa67701a8531e8fad561d5765c61410f060eb203c4646521749f704e = literal [0].
2. printf of the hand-written 10-entry receipt map (sorted keys, compact separators, ASCII) = 5cb9f4865c8e1315dbd1baa99310c9bc65ddcf469929488359c66587b6470060 = stored digest [0]. Receipt parsed with duplicate-key rejection: 10 entries; stored value equals the gate and producer recomputation.
3. Receipt file sha256 e1fc04ab...; equals git show a6617149:<receipt> | sha256sum [0].
4. diff of sed -n 173,178p (gate) vs 205,210p (producer): exit 1, only the def line and docstring differ. Body diff 176-178 vs 208-210: exit 0, empty.
5. AST identical modulo name and docstring. Both functions hash identical bytes on a 10-input battery (newline, ' -> ', U+00E9, astral, lone surrogate, control char, SELFTEST and receipt maps): 10/10.
6. Encoder blobs identical at measured b76727f and attacked a6617149 (git rev-parse): check-receipt.py 8d83fe7f, kama-llamacpp-live.py 4d7bdce7, install-links-grid.py 4ffcca76 [0].
7. All 10 receipt link chains end at a pinned install_tree member (gate link_chain_problem). Installed tree, read-only lstat/readlink, reproduces the map and digest [0].
8. Official c2-gate-selftest.stdout equals the frozen run output: "11 VALID and 1 NOT-EVALUATED ...; 91 mutations" [0].

## Mutation results (literal_check.py, scratch copies; the literal is the only guard for this drift)
drift               | gate@a6617149              | producer@a6617149  | gate@worktree                  | producer@worktree
sort_keys removed   | exit 1, fails canonical    | passes (missed)    | exit 1, fails canonical+unicode| raises not key-sorted
default separators  | exit 1, fails canonical    | raises mismatch    | exit 1, fails canonical+unicode| raises mismatch
ensure_ascii off    | exit 0 (missed)            | passes (missed)    | exit 1, fails unicode          | passes (missed)

## Findings
F1 LOW, open at a6617149, closed in worktree: the gate literal cannot see ensure_ascii drift; SELFTEST_LINKS and every link case are ASCII. Worktree adds links-unicode-canonical-valid, literal 9e226427... (printf [0], matches).
F2 LOW, open at a6617149, closed in worktree: the producer literal cannot see key-order drift because install_links inserts in sorted(os.listdir) order (kama-llamacpp-live.py:226) [INFERENCE from code; mutant outcome executed]. Worktree adds {"a":"y","b":"x"} = 7951deff... (printf [0]).
F3 LOW, open in both: --require-install-links accepts install_links {} with install_links_sha256 null on outcome pass (VALID, exit 0, no pin). Cause: check_digest(allow_none=not links) at check-receipt.py:454-455 skips the recomputation at :456 for empty maps, although the comment at :442-444 says links are "digested". Pinning sha256('{}') gives INVALID (exit 1). Producer never emits this on pass [INFERENCE from code]: success path sets the digest at kama-llamacpp-live.py:1387-1396; a None digest comes only with a listdir problem, which raises SetupError at :1376-1379. Reachable by hand edit or regression. Fix: require a 64-hex digest when outcome == 'pass'.
F4 LOW, open in both: the producer selftest does not pin non-ASCII output (producer ensure_ascii-off passes in both states); the gate's unicode literal does not cover producer output. Fix: add the unicode literal to _install_identity_selftest.

## Lane state (process flag)
- HEAD is still a6617149 (git rev-parse [0]). The worktree is not at HEAD: check-receipt.py (mtime 08:21:47, +17 lines) and kama-llamacpp-live.py (mtime 08:23:17, +12 lines) are uncommitted. They were written after my clone (08:17) and not by this seat.
- Worktree gate selftest now prints "12 VALID" (exit 0); producer selftest prints ok (exit 0). The claims' 11-VALID count is a6617149's. Commit and re-measure before citing the worktree.

## Commands (all run)
git clone + checkout a6617149 [0]; sha256sum lane vs clone, 2 files [0]; git cat-file -t b76727f31e52... [0]; git rev-parse on b76727f and a6617149 blobs [0]; git show a6617149:<receipt> | sha256sum [0]; diff of sed ranges [1, 0]; diff -u clone vs worktree [1, 1]; /usr/bin/python3 out/C2LiteralCheck/literal_check.py <clone> literal_check.a6617149.log [0]; ... <lane> literal_check.worktree.log [0]; check-receipt.py --selftest (worktree) [0]; kama-llamacpp-live.py --selftest (worktree) [0]; printf for producer literal deb111fa..., unicode 9e226427..., key-sort 7951deff... [0 each]; git rev-parse HEAD, git log -4, git hash-object [0] (read-only; no index writes).

## Tooling and cleanup
No installs. /usr/bin/python3 stdlib only. Scratch /tmp/kama-r21-C2LiteralCheck removed [0]; no processes left running.
Deliverables: falsify/out/C2LiteralCheck/{literal_check.py, literal_check.a6617149.log, literal_check.worktree.log}.
Not done: no live llama-server, no lane edits.
