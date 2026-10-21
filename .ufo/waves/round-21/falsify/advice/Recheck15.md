VERDICT: partial - round-15 verdict (3 required, 0 defects) and both switches survive; C1 overstated: landed-ambiguous never fires, and verdicts read fleet working-tree bytes (a6617149)
Attacked: C1 round-15 classification at a6617149 (committed tool): author-time vs committer-time cutoff, cat-file --batch-check vs per-token lookup, and the inputs read. Judged on the committed tool only; the live lane tree carries uncommitted edits to the same file (not measured).

## Executed checks (exit in brackets)
1. Scratch clone /tmp/kama-r21-Recheck15/lane: master = HEAD = a6617149 [git rev-parse, 0].
2. `python3 tools/report-landing-audit.py --lane-repo <clone> --fleet-repo /home/vgpnk/Projects/shokunin --rounds 15 --no-errata --json` [0]: status clean, cutoff 1792485831, round_commits 3, required 3, post_report [], defects []. JSON sha256 f9dbb033...
3. Same flags, `--rounds 10-20` [1]: stdout byte-identical to committed `runs/b76727f3/c1-audit-raw.stdout` (sha256 af2707ad..., equal to commands.json stdout_sha256). Real lane path, same flags [1]: same bytes.
4. Committed raw round-15 entry equals my run: cutoff, required 3, round_commits 3, defects [], post_report [].
5. `git log --format='%H %an %at %ct %s' master` [0], 86 lines: out/Recheck15/git-log-master.txt.

## Own derivation: `recheck15_probe.py derive` [0, MATCHES TOOL]
- kama-shokunin round-15 commits: 70af36c2 (at=ct=1792484951), 4b1b4ad1 (at=ct=1792485331), b8bdc56e (at=ct=1792485659).
- Fleet first add of the round-15 report: 402b93b5 (at=ct=1792485831). Working-tree report == HEAD blob.
- Required = 3 under author time and under committer time. All 3 are cited by full 40-hex in Landed; the 5 full hashes in the report all exist; no landed-unresolved.
- Correctly excluded: 20e392ea (protocol-shokunin, "round-15 verifier spot-check ...", at 1792486296): author and colon rules exclude it, and it is post-cutoff anyway.
- Round 15: no false positive, no false negative.

## Attack 1: author time vs committer time
- 17 master commits have at != ct (rebase-style; dt up to 10326 s). None crosses a cutoff: `recheck15_probe.py variants` [0]: committer-time vs committed differing_rounds=[] for 10-20 and 15.
- The selftest does see it: committer-time variant `--selftest` [1] fails 4/32 (author-time-cutoff-survives-rebase, post-report-excluded, subject-without-space-required, draft-uses-fleet-cutoff). Committed `--selftest` [0]: 32/32.
- So the switch changes classification only for rebased commits, and none exist in the real data.

## Attack 2: batch-check vs per-token
- Per-token variant [0]: differing_rounds=[] for 10-20 and 15. Its selftest 32/32 [0]: the suite cannot tell the two apart.
- Old a29bb84a (committer + per-token + no checkable filter) [0]: differing_rounds=[] for 10-20 and 15. The 1471344b switch changed no label on this data.
- Batch ambiguity, git 2.56.0: `cat-file --batch-check` prints "<p> ambiguous" for a plain name but "<p>^{commit} missing" when peeled, at 7 characters too (40000 synthetic commits, prefix 85ea120). Tool lookup: peeled -> missing, plain -> ambiguous [`recheck15_probe.py ambiguity` 0].
- Every call site that checks Landed tokens or errata corrections peels with ^{commit} (tool lines 189-190, 250-251). So landed-ambiguous is unreachable; an ambiguous Landed token is reported as landed-unresolved (still exit 1). The selftest mentions "ambiguous" 0 times.

## Attack 3: inputs (latent for round 15)
- Working-tree read: committed audit_round reads Path(fleet_repo)/rel (tool lines 168-169). Probe on a scratch fleet clone: one uncommitted line -> committed tool [1], unresolved-full-hash. Real-fleet control [0]. Uncommitted lane snapshot (sha256 4f090914..., reads HEAD: at line 174) [0] on the same probe (`recheck15_probe.py wtprobe` [0]).
- Latent, not active: `git --no-optional-locks status --porcelain -- .ufo/reports/` is empty [0]; each round 10-20 report has exactly one commit.
- Uppercase hex is invisible: FULL/ABBREV are lowercase only (regex check False/False [0]). An uppercase unresolved hash passes; an uppercase citation looks omitted. None occur in rounds 10-21.
- [INFERENCE, not executed] Author time is author-controlled (GIT_AUTHOR_DATE); the post_report split (tool lines 183-184) trusts it.
- Hex-word false positive (old tool, no checkable filter): none in rounds 10-20 Landed sections (scan), so no effect here.

## Implications for C1 (L1 decides; nothing applied)
- Round-15 claim survives. "Detects 5 defect kinds" and "0 FN" are overstated: landed-ambiguous never fires, and verdicts follow uncommitted fleet edits.
- Options: commit a HEAD-read fix with a working-tree selftest; add an ambiguity test and either use plain-name lookup or drop the kind; document lowercase-only hex.

## Tools and process
- Installed or updated: none. Used existing git 2.56.0 and Python 3.14.8.
- Processes started: none. Lane and fleet read-only. The lane has uncommitted edits by another party (tools/report-landing-audit.py, SCORECARD.md, tests/llamacpp-live/check-receipt.py, tools/kama-llamacpp-live.py); I did not touch them.
- Scratch /tmp/kama-r21-Recheck15 deleted at end.
- Deliverables in falsify/out/Recheck15/: recheck15_probe.py (derive|variants|ambiguity|wtprobe|all; `all` [0]), outputs.txt, outputs-variants-with-old.txt, committer-time.patch, per-token.patch, old-a29bb84a-vs-committed.patch, git-log-master.txt.
