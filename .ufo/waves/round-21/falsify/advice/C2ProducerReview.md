VERDICT: partial - fail-closed holds for the enumerated entry classes under uid 1000, but "never a silently smaller identity" is refuted (install_tree drops unhashable members silently) and uid 0 voids the unreadable branch.
Scope: committed a6617149 (scratch clone); uncommitted fleet edits are checked separately under WORKTREE.
Attacked: install_links() L213-245, links_digest() L205-210, producer install-tree-unpinnable path L1376-1379 (receipt L1305-1342, handler L1561-1562), _install_identity_selftest() L1101-1158; gate fields judging them (check-receipt.py L181-198, L307-310, L454-455).

FINDINGS
F1 MEDIUM fail-open. install_tree() swallows OSError on lstat and on hash (L192-193, L198-199). install_links() tests readability with os.access (L241), not an open. A member that access() passes but open()/read() refuses is dropped from the identity and never flagged.
- Simulated at the failing step (c_silent_drop_eio, c_silent_drop_unlink_race): uid 1000 and uid 0 record ['llama-server'] against full ['libextra.so','llama-server']; install_links problems [].
- Real kernel: landlock_demo.py (unprivileged Landlock ABI 10, READ_FILE granted only on the server): os.access(lib)=true, open(lib)=EACCES, recorded tree ['llama-server'], problems [], producer_would_fail_closed=false.
- Gate is blind: omit-nonchain-member (libggml-cpu-x64.so dropped, digest recomputed) is VALID exit 0; with --expect-install-tree-sha256 it is exit 1. A chain-target omission is caught (exit 1).
F2 LOW uid 0 voids the unreadable branch: os.access(R_OK) is true for mode-000 files under CAP_DAC_OVERRIDE.
- c_unreadable_member: uid 1000 gives 'libllama.so.0.7.0:unreadable'; uid 0 gives []. c_selftest_unreadable_branch: unreadable_problem_seen true (uid 1000), false (uid 0).
- `sudo -n python3 -B tools/kama-llamacpp-live.py --selftest` prints "selftest: ok" and exits 0: the assertion at L1154-1158 never runs.
- Grid --arm current on the real tree: uid 1000 exit 0, status pass; uid 0 exit 1, status fail, wrong ['regular-unreadable'] (changed=false).
- uid 0 production identity stays complete for DAC-only denials (root opens the mode-0 member). The defect is a dead branch and a root-variant measurement.
F3 LOW gate laxity: check-receipt.py L454-455 (`allow_none=not links`) accepts install_links_sha256=null when install_links={}. links-empty-null-digest: VALID exit 0 (exit 1 with --expect-install-links-sha256). By code (L1376-1394) a complete run always sets a digest; the empty-map digest is 44136fa3....
F4 LOW names: the control-character rule is C0 only (L231-234). 'lib\x7fx.so' and 'lib\x85x.so' pass (c_del_regular, c_nel_regular); '\n' and '\t' are refused. No digest collision found ('name sha\n' is ambiguous only on '\n'; links use canonical JSON). The claim wording "control-character names" overstates the rule.
- A non-UTF-8 regular member makes install_tree raise UnicodeEncodeError (L201, pre-existing). The real producer records setup_error 'internal:UnicodeEncodeError' (receipts/receipt-nonutf8-regular.json): fail-closed, but not the install-tree-unpinnable token. A non-UTF-8 symlink is accepted as key 'lib\udcff.so'.
F5 INFO races: vanished or ghost entries refuse ('ghost.so.0:No such file or directory', readlink EINVAL): benign false positives. install_tree (L185) and install_links (L226) each list the directory. [INFERENCE] a change between the two snapshots can yield a tree and links describing different instants (not executed).
F6 INFO setup-error grading unchanged: real pre-launch runs (control name, FIFO, non-UTF-8, glibc-hwcaps/) give outcome setup-error, exit 2, install_tree {}, install_links {}, digests null. Gate: INVALID exit 1, 33 problems, same template as the pre-existing model-digest-mismatch (receipts/old-gate-on-old.txt). Intended behaviour change: old install_tree silently returns ['llama-server'] for a directory with glibc-hwcaps/ (c_subdir_hwcaps); [INFERENCE] such runs previously completed as VALID.
F7 INFO coverage: _install_identity_selftest omits listdir/lstat/readlink failures, FIFO/socket entries, silent drops, and control characters other than '\n'.
F8 INFO pre-existing [INFERENCE]: identity is captured once before launch (call sites L1375-1376 only); nothing re-hashes after launch; dlopen-loaded backends (libggml-cpu-*.so) are not re-checked.

OPERABILITY: real tree ~/.local/opt/llama-b11755 has 10 soname symlinks, no subdirectories or non-regular entries (find: empty output); producer problems [] (grid real_identity); live receipt 10 links, digest 5cb9f486..., gate VALID. Trade-off: any future subdirectory, FIFO or socket in that directory refuses every run (no allowlist).

WORKTREE (uncommitted fleet edits; not measured; not mine; checked on scratch copies)
- Fleet tools/kama-llamacpp-live.py (sha cec67949...) differs from a6617149 (e4cc6d88...); tests/ gate and grid and tools/report-landing-audit.py are also modified.
- Closes F1 for the cases tested: EIO-style hash failure gives problems ['libextra.so:not-hashed']; Landlock run gives producer_would_fail_closed=true (install_links(server, tree)).
- Closes F3: gate links-empty-null-digest gives INVALID exit 1.
- Still open (diff read, not executed): F4 C0-only rule; F2 os.access unreadable check; gate omit-nonchain-member still VALID exit 0.
- Selftests: working-tree producer --selftest exit 0; working-tree gate --selftest exit 0 (12 VALID, 1 NOT-EVALUATED, 99 mutations); committed producer --selftest exit 0.
GIT NOTE: one `git status --short` ran in the fleet checkout without --no-optional-locks (may refresh the index stat cache; no content change). Six /tmp/kama-llamacpp-live-*.log files predate this session and are untouched.

VERIFICATION (exit codes)
- git clone, checkout a6617149, rev-parse, diff --stat: 0
- producer --selftest: uid 1000 -> 0; sudo -n uid 0 -> 0. probe_links.py: uid 1000 -> 0; uid 0 -> 0.
- landlock_demo.py: 0 (rerun 0). setup_error.sh: producers 2, 2; gates 1, 1, 1, 1.
- gate-mutations.py: 0. check-receipt.py --selftest: 0 (11 VALID, 1 NOT-EVALUATED, 91 mutations).
- grid --arm current: uid 1000 -> 0; uid 0 -> 1.
- ACL grant: access true, open ok; mask none: access false, open EACCES (exit 0, 0, 0).
- readelf -d llama-server: 0 (RUNPATH [$ORIGIN]); lane L84 CHILD_ENV_KEYS excludes LD_LIBRARY_PATH.
- Installs: none. No server launched; no background processes; scratch removed.

GAPS (not executed): real EIO, real concurrent unlink, AppArmor/FUSE denials, NFS, two-snapshot race, glibc-hwcaps search order (docstring), dlopen timing, pinnable live path (would launch llama-server; out of bounds).
EVIDENCE: .ufo/waves/round-21/falsify/out/C2ProducerReview/ (scripts, outputs, receipts/, gate/).
