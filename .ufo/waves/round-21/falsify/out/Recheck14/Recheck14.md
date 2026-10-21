VERDICT: confirm - C1 round-14 classification is correct; author-time and batch-check switches change nothing for round 14; no FP/FN found.

Attack target: C1 `tools/report-landing-audit.py` round-14 classification at
`a6617149722c73d90e142fbdc8154d6967055f7e`, vs the committed official raw stream
`.ufo/waves/round-21/runs/b76727f3/c1-audit-raw.stdout` (round-14 entry) and vs
my independent derivation from lane `git log` + fleet report round-14/kama.md.
Scratch: /tmp/kama-r21-Recheck14 (deleted after). No lane/fleet mutation; no
installs performed (none needed).

# Executed evidence (all commands run by me, exits observed)
1. clone + `checkout a6617149722c73d90e142fbdc8154d6967055f7e` -> HEAD matches.
2. `python3 tools/report-landing-audit.py --lane-repo <scratch> --fleet-repo
   /home/vgpnk/Projects/shokunin --rounds 14 --no-errata --json` -> exit 0;
   r14 = {cutoff 1792478534, defects [], post_report [], report_committed true,
   required 2, round_commits 2}.
3. Official stream round-14 entry == pristine entry (dict equality: True).
   On-disk stream is byte-identical to the committed blob at the pushed tip:
   `git cat-file blob a661714:...c1-audit-raw.stdout | git hash-object --stdin`
   = 6ed51d157a114a9b3137ea53f5e6c83ffc1ebc57 = on-disk hash-object. (Blob is
   absent at b76727f3 itself - results were committed after the measured commit;
   expected, since the run dir is named for the measured commit.)
4. Selftest: `python3 tools/report-landing-audit.py --selftest` -> exit 0,
   `cases=32 failed=0` (matches C1 claim; includes
   `author-time-cutoff-survives-rebase`).
5. Mutants (copies in out/Recheck14/, each run with the same args, exit 0):
   - m1-committed-membership.py: round-commit membership via %ct instead of %at
     -> r14 entry identical.
   - m2-committed-cutoff.py: first-add cutoff via %ct instead of %at
     -> r14 entry identical.
   - m3-catfile-e-lookup.py: per-token `git rev-parse --verify` object lookup
     instead of one `cat-file --batch-check` per repo -> r14 entry identical
     (statuses found/missing match; no ambiguous token exists in r14 inputs).
6. Cutoff provenance: fleet commit 52c833d19cf2429c47ccd57623470833e66e1484
   "round-14: kama report" first added `.ufo/reports/round-14/kama.md`;
   at==ct=1792478534 (so m2 is a no-op here by construction). Its blob
   f8d76a8fb1e5fab509fbbacc90f439477778d234 == current worktree blob; report
   clean vs fleet HEAD. The tool's on-disk report read is therefore equivalent
   to a committed-blob read for r14.
7. Round-14 population: exactly two lane commits match author `kama-shokunin` +
   subject `^round-14:` (no `checkpoint(r14)`): 06cc6dbea42b (at=1792478463)
   and e545ed99aaa5 (at=1792478292); both at==ct. Both <= cutoff -> required 2,
   post_report 0. The round-14 verifier spot-check 6e348e28 (protocol-shokunin,
   at=1792479085 > cutoff) is correctly excluded by the author filter, not by
   time (its author time is after cutoff; it is not a round commit at all).

# Answers
- Author vs committer time: no classification change for round 14 - every
  relevant timestamp pair is equal (both round commits; the first-add commit).
  The design rationale (jj rebase rewrites committer time, keeps author time)
  is stated in the tool docstring and pinned by the selftest rebase case.
- Batch-check vs plain lookup: no classification change for round 14 - m3
  (rev-parse --verify per token) reproduces the identical r14 entry, exit 0.
- False positives/negatives: none found. Independent reimplementation (my own
  regexes over the report + my own git-log selection) agrees with the tool on
  every r14 key: round_commits 2, required 2, post_report [], cutoff,
  defects []. All full-40 tokens in the report (e545ed99..., 06cc6dbe...,
  e1b3d746... x2, plus repeats) resolve; both round commits are cited in
  `## Landed changes` by 40-hex prefixes, so no landed-omitted; Landed cited
  set = {06cc6dbe..., e545ed99...}, both resolve as commits with `^{commit}`.

# Design observations (no r14 effect; for the L1's calibration ledger)
- `cited = ABBREV.findall(section)` feeds unfiltered 7..40-hex tokens into the
  landed-omitted startswith mask; checkable_abbrev filters only the resolution
  check. A pure-decimal >=7-digit number inside `## Landed changes` would enter
  `cited` and could theoretically mask an omitted commit whose sha starts with
  those digits. r14 is clean: verified cited set contains only the two round
  hashes. Purely theoretical; zero observed effect.
- The 64-hex cases.json SHA-256 (4a4de0b8...) in the report is invisible to
  both FULL and ABBREV regexes (hex-boundary guards reject all starts inside a
  64-hex run) - verified by direct regex extraction: no 64-hex token extracted.
  Correct non-behavior, worth keeping pinned against regex edits.
- Cross-repo clock skew (lane author time vs fleet author time) is documented
  as undetectable; for r14 the margin is 71s (06cc6dbe vs cutoff) - a fleet
  clock skew beyond that would have flipped it to post_report. Documented
  limitation, not a defect.

# Residual risk / verification gaps
- I did not re-execute the official measurement; I compared against the
  committed stream and byte-verified it against the pushed-tip blob (above).
- Mutation results are specific to round 14 inputs; other rounds (where at!=ct
  exists, e.g. round-19 24adc8ed at=1792565229 ct=1792565240) were not in my
  scope and may behave differently under the m1/m2 mutants by construction.
- m3 ambiguity semantics: rev-parse --verify reports ambiguity via stderr text;
  no r14 token was ambiguous, so ambiguous-path equivalence is untested here
  (the selftest's own ambiguous cases cover the batch-check path).

Artifacts: mutants m1/m2/m3 at
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/falsify/out/Recheck14/`.
