VERDICT: confirm - round-11 C1 audit at a6617149 reproduces the official raw byte-for-byte; author-vs-committer and batch-check mutants change no classification; no FP/FN found.

Attack target: C1 detector `tools/report-landing-audit.py` (new this round; absent at
round-start tip 7a6bc911 — `git cat-file -e 7a6bc911:tools/report-landing-audit.py`
exit 128 in official commands.json `c1-absent-at-base`), round-11 slice, evaluated at
`a6617149722c73d90e142fbdc8154d6967055f7e` in scratch clone `/tmp/kama-r21-Recheck11/lane`
(clone master == lane master == a6617149, verified). Lane untouched.

Executed checks (command → observed exit):
1. `python3 tools/report-landing-audit.py --lane-repo <clone> --fleet-repo <fleet> --rounds 11 --no-errata --json` → exit 0.
   Round-11 entry identical to official `.ufo/waves/round-21/runs/b76727f3/c1-audit-raw.stdout`
   (dict equality via json compare: True): cutoff 1792468776, round_commits 2, required 2,
   defects [], post_report [], report_committed true.
2. `--rounds 10-20 --no-errata --json` → exit 1; stdout byte-identical to official
   c1-audit-raw.stdout (str ==: True; sha256 af2707ad… equals commands.json `c1-audit-raw`
   stdout_sha256). Tool identical between a6617149 and b76727f3 (`git diff --stat` empty).
3. Independent derivation from `git log --format='%H|%an|%at|%ct|%s' master` (exit 0):
   - Qualifying round-11 commits (author `kama-shokunin`, subject `^round-11:|^checkpoint(r11)`):
     exactly 3285cdf7a504… (at=ct=1792468575), fe57cc8a01ac… (at=ct=1792468676).
     `git log --all` over the only refs (master, origin/master) finds no others; no
     checkpoint(r11) commit exists.
   - Cutoff: fleet `git log --diff-filter=A -- .ufo/reports/round-11/kama.md` → single
     commit dff173077a88… at 1792468776 ("round-11: kama report") == tool cutoff. Only one
     add-commit ever touched the path, so `out[-1]` (first add) is unambiguous.
   - Both atimes <= cutoff → required 2, round_commits 2, post_report []; both cited by
     full hash in §Landed changes → 0 landed-omitted; all three distinct 40-hex report
     tokens (3285cdf7…, fe57cc8a…, 2f7303c2…) resolve as lane commits → 0 unresolved-full-hash.
4. Author→committer mutant (only `%at`→`%ct` inside round_commits; copy at
   out/Recheck11/audit-ct.py): stdout byte-identical to baseline for `--rounds 11`
   (exit 0) and `--rounds 10-20` (exit 1). No classification flips anywhere in the
   audited range. Ground truth: every round-11-era commit has at==ct; the 9 commits with
   at≠ct (r17–r21: c6dc46fa, 7229fa95, 84cf2f76, 05f0f6c7, 30ed3783, 24adc8ed, 33a67778,
   7a6bc911, 1471344b) all have ct>=at and stay on the same side of every round cutoff.
5. Batch-check equivalence (executed via importlib + subprocess): batch-check
   found/missing maps == per-token `git rev-parse --verify --quiet <t>^{commit}` maps for
   both token sets (FULL tokens of report text: {3285cdf7, fe57cc8a, 2f7303c2} all found
   in lane, absent in fleet; Landed citable tokens: the two full hashes, found with peel).
   No classification difference.

FP/FN hunt: none found.
- FN impossible here: the only two qualifying commits are cited by full hash (startswith
  check satisfied); no other refs or checkpoint(r11) commits exist.
- protocol-shokunin spot-check 79fa2577 ("round-11 verifier spot-check …") is
  double-excluded (author ≠ kama-shokunin; subject lacks the colon after `round-11`) and
  at 1792469263 > cutoff would be post_report, not a defect, even if included.
- 2f7303c2 (protocol commit cited in prose, "frozen from") resolves in lane → correctly
  not unresolved-full-hash.

Residual risk (not round-11 defects):
- audit_round reads the fleet WORKTREE report file while report_committed is derived
  from history; a dirty fleet worktree would audit uncommitted text under
  report_committed=true. Round 11 unaffected: worktree file == dff17307 blob (`cmp`
  exit 0; `git status --porcelain` clean for the path). [INFERENCE: latent gap, not
  exercised by this measurement]
- lookup's "ambiguous" branch and the errata machinery are unexercised by --no-errata
  round-11 data (all cited tokens are full 40-hex, unique by construction); outside this
  slice's scope.

Tool installs/updates: none. Artifacts (new files only):
.ufo/waves/round-21/falsify/out/Recheck11/{audit-ct.py,base-11.json,base-10_20.json,ct-11.json,ct-10_20.json}.
Scratch /tmp/kama-r21-Recheck11 deleted after writing this report.
