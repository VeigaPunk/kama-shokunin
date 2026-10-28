# EX08Scans - round 63 scan receipts at tip 03a6a1d850902a66a13dfad33f89cf3a8b759a09

Advisory leaf; no verdict on claims. Scratch export: `git archive 03a6a1d8… | tar -x` into
/fast/scratch/hyaku/kama-r63/w/EX08Scans/exp, commands run from there with `--repo` the lane
(read-only, git blobs at the rev). Raw outputs (stdout+stderr merged, exit appended) are in
`.ufo/waves/round-63/w1/out/EX08Scans/`: digest.txt, digest-details.txt, hexrun.txt,
selfdesc.txt, selfdesc-base.txt, repsel.txt. No tools installed or upgraded.

## 1. digest-ledger scan (exit=0)
`python3 tools/digest-ledger.py scan --repo <lane> --rev 03a6a1d8…`
```
tokens=145 blob=126 external_ok=10 external_absent=1 unverifiable=7 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0
exit=0
```
`--details` (extra run, digest-details.txt) lists the only two flagged tokens, both already ledger rows:
- wrong_flagged 5585f602f71c4d4fa5a20125b2b8e4a1132a2d41abf511d7ef09c43a91d950f2 class=wrong
- external_absent bcc55c92e8456e9515f58309953cf005b383a5b93c2dcaf3e68a2b09e8f7ea3e class=external
  (ledger row says: over 1 MiB, exists only in the parked round-35 lane worktree; counts as not-present on a fresh export by design).
unknown=0, so no token awaits classification.

## 2. hexrun-census scan --details (exit=0)
```
tokens=2071 distinct=399 lane_oid=277 md5_blob=1 upstream_ok=109 unverifiable=9 wrong_flagged=3 ledger_bad=0 unknown=0
exit=0
```
unknown=0, ledger_bad=0. Every non-lane_oid / non-upstream_ok token, with the first-occurrence file:line in
documents (.md/.tsv outside .ufo/) and the ledger row that classifies it (hexrun-ledger.tsv line):

| token | class | file:line | classified by |
|---|---|---|---|
| 00000000000000000000000000000000 | unverifiable | corpus/knowledge/loopback-listener-ownership.md:21 | ledger L72 |
| 00000000000000000000000001000000 | unverifiable | corpus/knowledge/loopback-listener-ownership.md:19; corpus/SOURCES.md:60; corpus/lessons/round-18.md:231 | ledger L71 |
| 3ad0df68e8423a3b…ce234ff (65 hex) | unverifiable | corpus/lessons/round-38.md:51, :139 | ledger L75 |
| 61e82ee22dc89292175c5431f1ed6dc1 | unverifiable | LOG.md:114 | ledger L67 |
| 860f26ac05938cdfc1a8816eff1570b4 | unverifiable | LOG.md:118; SCORECARD.md:26 | ledger L68 |
| 87eb156b7cc36e98f3cbfb37c00f5351 | unverifiable | LOG.md:14 | ledger L70 |
| 932ea3dc365e066e740731cf6a939506 | unverifiable | LOG.md:13 | ledger L69 |
| efb50993780079460b0cbed1363e2166a2de1d9f | unverifiable | corpus/lessons/round-1-critic.md:106 | ledger L34 |
| f7a779ba0a3544dc9e3673c7eb0b3d77 | unverifiable | plans/wwkd-round-5-interactive-freshness.md:5 | ledger L73 |
| 0957ce619789d13d894ef21bc863486bcb35b56c | wrong_flagged | corpus/lessons/round-21.md:63; registry/report-landing-errata.tsv:3 | ledger L45 (correct 0957ce619789d13bb577…) |
| 35ce313293052f8362e0829e7512bc9bc3d336c (39 hex) | wrong_flagged | SCORECARD.md:2231; corpus/lessons/round-40-verifier-spotcheck.md:25; corpus/lessons/round-41.md:118 | ledger L74 (correct …336c9, upstream L3) |
| 907cdcc0a76f8656fde4574c0c50725fcea42fa9 | wrong_flagged | corpus/lessons/round-32-verifier-spotcheck.md:93 | ledger L113 (correct …0a50725f…) |
| 1f81e859c2d7f43f87d1f7e01327b2cf | md5_blob | SCORECARD.md:25, :254; corpus/SOURCES.md:42 | no ledger row needed: equals the MD5 of a committed blob (tools/kama-probe.sh) |

All 13 non-lane/non-upstream tokens are already classified by a ledger row (or the md5_blob rule). No
token is unknown/unclassified, so no new ledger row is needed or could be "added to classify" anything.

## 3. round42-selfdesc-reconcile (exit=1)
```
tip=03a6a1d850902a66a13dfad33f89cf3a8b759a09
r41=1 banner=1 planned=2 retired=1 saturation=1 caps=1 receipts=0 readme=0 province=1 rel=0 mismatches=8 maxN=63 met=False
exit=1
```
Details: (1) r41: SCORECARD.md:17 coverage row says the run prints `36`, observed `38`;
(2) banner lacks 'Latest measured round: 63'; (3,4) no `### Planned (round 64)` section / numbered item;
(5) retired does not state '12 capabilities'; (6) saturation does not state the first-working rounds list
`10, 14, 16, 20, 25, 30, 41, 42, 43, 46, 47, 61`; (7) caps: head names 11 capabilities, canon (round 63) has
12 (head lacks `live-ollama-lifecycle`); (8) PROVINCE.md lacks `registry/ollama-live-claims-r61.tsv`.
Expected per freeze (8 at 03a6a1d8 on purpose; the head/PROVINCE/Planned are re-derived after measurement).
Observation for the L1 (a calibration finding, not a verdict): mismatch (1) is a stale NUMBER, not a missing
section - `python3 -c "import glob;…"` over corpus/knowledge prints 38 at 03a6a1d8, and also 38 at base
7ee8cbdf and at freeze 675cac02 (40 .md files, two excluded by name); base also reports r41=1 with the same detail
(selfdesc-base.txt: mismatches=8 maxN=62). So that mismatch is not remediated by re-deriving banner/Planned/
Retired/Saturation/Capabilities/PROVINCE text; the SCORECARD.md:17 `36` (plus its "(round 60 added …)" parenthetical)
needs its own edit to `38` - a ledger row cannot classify it. If the L1 only repairs the seven named head
items, the reconciler stays at mismatches=1 and the C2 claim's "reports mismatches=0" clause would miss.

## 4. capability-repertoire-audit --selftest (exit=0)
```
CAP_SELFTEST pass=2 fail=0
exit=0
```

## One-line tallies
digest: tokens=145 blob=126 external_ok=10 external_absent=1 unverifiable=7 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0 (exit 0)
hexrun: tokens=2071 distinct=399 lane_oid=277 md5_blob=1 upstream_ok=109 unverifiable=9 wrong_flagged=3 ledger_bad=0 unknown=0 (exit 0)
reconcile: r41=1 banner=1 planned=2 retired=1 saturation=1 caps=1 receipts=0 readme=0 province=1 rel=0 mismatches=8 maxN=63 met=False (exit 1)
repertoire: CAP_SELFTEST pass=2 fail=0 (exit 0)
