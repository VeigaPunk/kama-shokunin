VERDICT: partial - round-12 result reproduces exactly; author-vs-committer time and batch-check change no classification on rounds 10-20; the ambiguity path has latent defects not exercised by measured data.
Attacked: C1 round-12 audit at a6617149722c73d90e142fbdc8154d6967055f7e (tools/report-landing-audit.py author-time cutoff and `cat-file --batch-check` lookup with `^{commit}` peel) on fleet `.ufo/reports/round-12/kama.md` (add commit 5ee71e4c).
Scope: round-12 classification, FP/FN, time-rule and batch-check sensitivity; rounds 10-20 as control. Lane not modified. Installs: none (pre-existing git 2.56.0, Python 3.14.8).

## Executed (exit)
- Clone lane to /tmp/kama-r21-Recheck12/lane and checkout a6617149: chain completed, rev-parse HEAD = master = a6617149.
- `python3 tools/report-landing-audit.py --lane-repo <clone> --fleet-repo /home/vgpnk/Projects/shokunin --rounds 12 --no-errata --json; echo exit=$?` -> exit=0; cutoff 1792471121, defects [], post_report [], required 2, round_commits 2, status clean.
- `python3 tools/report-landing-audit.py --selftest; echo exit=$?` -> cases=32 failed=0, exit=0. None of the 32 cases covers ambiguity.
- `--rounds 10-20 --no-errata --json` -> exit 1; results and summary equal to committed c1-audit-raw.stdout (round-12 entry included).
- Fleet `git log --follow -- .ufo/reports/round-12/kama.md` -> exit 0; one commit, 5ee71e4c, author = committer = 1792471121.
- Lane `git log --format=%H|%an|%at|%ct|%s a6617149...` (same fields as `git log --format='%H %an %at %ct %s' master`; master = a6617149 in clone) -> exit 0; 86 commits; 17 with at != ct (16 kama-shokunin, 1 protocol-shokunin); 0 with at > ct.
- `git merge-base --is-ancestor b76727f3... a6617149...` -> exit 0 (official measured commit is an ancestor).
- Per-object `git cat-file -t` and `git hash-object --no-filters` on fleet reports r10-r20: working tree = add blob = HEAD blob for all 11.
- `python3 out/Recheck12/recheck12.py --lane-repo ... --fleet-repo ... --tool ... --raw ...` -> "recheck12: checks=29 fails=0", exit 0 (stdout in out/Recheck12/recheck12.stdout).
- `git cat-file --batch-check` on two lane commits sharing a 7-char prefix, stdin `P7^{commit}` and `P7` -> `missing`, `ambiguous`; exit 0.
- `git rev-list --all --count`: lane 210 (exit 0), fleet 967 (exit 0).

## Round 12, independent derivation (git log %at/%ct; no tool)
- 33f46685b418af868259952884e34b93633820cb kama-shokunin A=C 04:35:52Z and 1df80eab01bc5663deea65680673fef24f35d5b0 kama-shokunin A=C 04:37:20Z (both `round-12:` subjects). Fleet add 5ee71e4c A=C 04:38:41Z is the cutoff. Margins 169 s and 81 s.
- Required = {33f46685, 1df80eab}; post = {}. The Landed table and the "Pushed lane HEAD" line cite exactly these, so omitted = {} and unresolved = {}.
- Window (r11 cutoff 03:59:36, r12 cutoff]: only these two kama-shokunin commits. protocol-shokunin commits 79fa2577 and 941bb32c are not kama. No unlabelled round-12 commit. No round-subject commit is reachable from a non-master ref.
- Other 40-hex tokens (79fa2577, 2f7303c2 lane commits; 7de13606 lane blob) resolve. Hand check of an unverified claim: 2f7303c2:corpus/SOURCES.md = 7de13606, 18898 bytes, sha256 9dc40d25... as the report states. The detector does not check this.

## Answers
- Q1 author vs committer time: no classification change. Per-round required and post sets are identical under both rules for r10-r20 (script B). All fleet adds have A = C. Closest committer-time margins: r19 24adc8ed (C 06:47:20 vs cutoff 06:47:37, 17 s) and r18 1b85a24e (C 05:38:35 vs 05:39:12, 37 s). Rebases move committer time by up to 56 min (33a6777866d0), so a committer-time rule would be fragile; author time is the right key. [INFERENCE for the general case]
- Q2 batch-check vs per-object: 76 token statuses (Landed abbreviations and full hashes, r10-r20), 0 mismatches (script C1). Round 12 identical.
- Q3 false positives: none in round 12. Q4 false negatives: none in round 12.

## Latent defects (not exercised by measured data)
- L1 landed-ambiguous is unreachable for abbreviations. Landed tokens are peeled with `^{commit}` (lines 189-190). For a commit collision git answers `missing`, so the tool emits landed-unresolved (lines 191-193); fixture F2 gives exit 1 with kind landed-unresolved. The "five kinds" claim is overstated, and errata rows keyed on landed-ambiguous can never match.
- L2 cross-repo masking: lookup() (lines 106-116) lets any repo's "found" override another repo's ambiguity. Fixture F3: lane ambiguous plus fleet copy of X gives exit 0 and no defect, with both commits counted as cited. [INFERENCE] Probability: a second lane commit sharing a given 7-hex prefix is about 210/16^7, roughly 8e-7 per token, before the fleet condition.
- L3 audited text is the fleet working tree (lines 168-169); committed-blob equality is never checked. Not triggered: working tree equals committed blob (hash-object check above).
- L4 post-report commits are never audited: r19 has four (3389513f, 464ea5a3, 60e8fd8a, 8d9191f5), none cited in any report r10-r21. Design gap, not round 12.
- L5 abbreviations outside Landed are not checked: 15 occurrences (12 distinct) in r10, r16, r17, r19, r20. By context they are digests, external commit 704366d76 (r16; [INFERENCE] upstream llama.cpp release), or tree SHA 6c216313 (r19). No lane-commit false negative found; round 12's four outside tokens all resolve.

## Refuted
- Re-added report cutoff: git lists commits topologically, and report_cutoff picks the topologically first add (fixture F6: 2000, not 2500). No defect.
- Blob sharing a commit's prefix causes false ambiguity: `P^{commit}` resolves to the commit (type-aware; exploratory 4-char fixture, not in script: found). No false positive.

## Residual risk and suggestions (not applied; lane is read-only for this seat)
Count two or more commit candidates across both repos as ambiguous before accepting found. Restore or relabel landed-ambiguous. Add a 7-char collision selftest. Read the committed blob (`git show <add>:<rel>`). Flag author time > committer time as an integrity defect.
Limit: the round-12 verdict rests on the stated rule; I did not adjudicate ground truth for rounds 10-20 beyond the rule.
Artifacts: out/Recheck12/recheck12.py, out/Recheck12/recheck12.stdout. Scratch /tmp/kama-r21-Recheck12 removed (verified: directory absent).
