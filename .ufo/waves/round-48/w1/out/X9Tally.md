**Verdict:** the round-47 draft is now a lane tool: `shortcut-tally.py` v2 reads only committed bytes at `--repo`/`--rev`, runs eight rounds clean (round 47 = 4 gated shortcuts, 36 of 124 mutants survived, status `ok`), gates with `--check N` (fails at `--check 3`, passes at `--check 4` at `380bcdff`), and carries a 7-case `--selftest` with three cases that must fail. The draft could not certify round 47 at all (three mutation-report parse defects plus a fifth report family it never read); that is fixed and pinned, and rounds 40-46 reproduce its published table byte-for-byte.

# X9Tally — round 48: promote the shortcut tally to a lane tool

Deliverable (proposed, for `tools/shortcut-tally.py`): `.ufo/waves/round-48/w1/out/X9Tally/shortcut-tally.py` (sha256 `3ee41c877007188a3b205837d6e164060b4f978b058b09af2f291befe9a57c09`, 975 lines, stdlib + `git` subprocess).

## 1. Committed-bytes reads (`--repo`/`--rev`)

The draft took `--lane <dir>` and read the working tree, so a seat could tally its own uncommitted edits. v2 resolves `--rev` once (`git rev-parse --verify <rev>^{commit}`, full id printed and stored in the `--json` meta) and reads `SCORECARD.md` and `.ufo/waves/**` through `git ls-tree -r -z` and `git cat-file blob` only; there is no `open()` on a repository path anywhere in the tool.

Evidence at lane scale — an uncommitted rewrite of `SCORECARD.md` (added `V9Cheat`, `K1Extra`, changed `25 of 117` to `25 of 118`) leaves the tally identical:

```
$ git -C $S/lane status --porcelain          # SCORECARD.md modified, not committed
$ python3 <tool> --repo $S/lane --rev 380bcdff9c8af06997c482f6eb03db926a794a2b --rounds 40-47 > tally-worktree-dirty.out ; echo $?
0
$ diff -q tally.out tally-worktree-dirty.out && echo identical
identical
```

A bare clone proves the same with no worktree at all (`tally-bare.out`):

```
$ git clone --bare --shared -q .../kama-shokunin $S/lane-bare.git
$ python3 <tool> --repo $S/lane-bare.git --rev 380bcdff... --rounds 40-47   # [0]
$ diff <(grep -v '^repo=' tally.out) <(grep -v '^repo=' tally-bare.out)     # no output
```

## 2. Table at the build commit

```
$ python3 .ufo/waves/round-48/w1/out/X9Tally/shortcut-tally.py \
    --repo /fast/scratch/hyaku/kama-r48/X9Tally/lane \
    --rev 380bcdff9c8af06997c482f6eb03db926a794a2b --rounds 40-47          # [0]

repo=/fast/scratch/hyaku/kama-r48/X9Tally/lane rev=380bcdff9c8af06997c482f6eb03db926a794a2b rounds=40-47
round  shortcuts  ids                                                        counters  cheats           mutants  falsify              status
40     -          -                                                          -         0                -        yes(w1)              no-disclosure
41     -          -                                                          -         0                -        yes(w1)              no-disclosure
42     5          R42A05,R42A13,R42B05,R42B06,R42C06                         C1,C2,C3  0                -        yes(w1)              ok
43     2          W1R01,W1R02                                                C1,C2,C3  0                20/53    planned-not-run(w2)  ok
44     2          K1Cheat,K2Cheat                                            C1,C2     K1Cheat,K2Cheat  22/79    yes(w1,folded)       ok
45     -          -                                                          -         0                -        stalled(w1)          no-disclosure
46     8          K1Cheat,K1R01,K1R07,K1R10,K2Cheat,K2Hist,V1Code,X2Fixture  C1,C2     K1Cheat,K2Cheat  25/117   yes(w1,folded)       ok
47     4          K1Cheat,K2Cheat,X1Stable,X2Revision                        C1,C2     K1Cheat,K2Cheat  36/124   yes(w1,folded)       ok
detail: round 44: wide=3 (+K2Design)
detail: round 46: wide=9 (+K2Design)
detail: round 47: wide=10 (+K1Design,K1Fixture,K2Checks,K2Design,K2Tamper,V1Ctr)
detail: round 47: M1Ctr .ufo/waves/round-47/w1/out/M1Ctr.md 13/44
detail: round 47: M1Tool .ufo/waves/round-47/w1/out/M1Tool.md 3/33 (killed=3+22)
detail: round 47: M2Ctr .ufo/waves/round-47/w1/out/M2Ctr.md 10/23
detail: round 47: M2Replay .ufo/waves/round-47/w1/out/M2Replay.md 10/24 (killed=0+12)
detail: round 47: disclosure SCORECARD.md:2723
(full output: out/X9Tally/tally.out, table + every detail line)
```

Round 47's mutant column cross-checks against its own prose: `13/44` + `3/33` + `10/23` + `10/24` = `36/124`, and `SCORECARD.md:2725-2726` says "13 of 44 counter mutants survive", "10 of 23 counter mutants and 10 of 24 replay mutants survive", `M1Tool.md:3` says 3 survived of 33.

Equivalence with the promoted draft (rounds 40-46 are its published table verbatim):

```
$ diff <(grep -E '^(round|4[0-6] )' tally.out) \
       <(grep -E '^(round|4[0-6] )' .ufo/waves/round-47/w1/out/X9Tally/tally.out)   # no output
```

Determinism: a second identical run diffs clean against `tally.out` (`[0]`).

## 3. One failing `--check` invocation

```
$ python3 .ufo/waves/round-48/w1/out/X9Tally/shortcut-tally.py \
    --repo /fast/scratch/hyaku/kama-r48/X9Tally/lane \
    --rev 380bcdff9c8af06997c482f6eb03db926a794a2b --rounds 40-47 --check 3 ; echo "exit=$?"
latest=47 shortcuts=4 limit=3 result=FAIL (latest round 47 shortcuts=4 > limit 3)
exit=1
```

`--check 4` on the same bytes: `latest=47 shortcuts=4 limit=4 result=PASS`, `[0]` (`check-pass.out`, `check-fail.out`). Error paths: a non-git directory and an empty `--rounds` range both exit `2` with `could-not-evaluate:` on stderr (`nongit.out`, `badrounds.out`); an unresolvable `--rev` exits `2` (`bad-rev` selftest case).

## 4. `--selftest` (7 cases, 3 that must fail)

```
$ python3 .ufo/waves/round-48/w1/out/X9Tally/shortcut-tally.py --selftest --scratch $S ; echo $?
case readable-round: PASS exit=0 round10={'shortcuts': 1, 'ids': ['K1Cheat'], 'counters': ['C1'], 'mutants': '1/3', 'falsify': 'yes(w1,folded)', 'status': 'ok'}
case check-fails: PASS exit=1 verdict='latest=10 shortcuts=1 limit=0 result=FAIL (latest round 10 shortcuts=1 > limit 0)' (rounds 10-11 limit 2 exit=0)
case committed-bytes: PASS exit=0 identical=yes worktree_edit=ignored
case bad-rev: PASS exit=2 msg="shortcut-tally: could-not-evaluate: .../a: cannot resolve 'no-such-rev' to a commit (no such revision)"
case unreadable-round: PASS exit=1 verdict='latest=12 shortcuts=- limit=99 result=FAIL (unreadable rounds [12])'
case split-slash-uppercase-kill: PASS exit=0 mutants=26/101 status=ok
case contradictory-report: PASS exit=1 verdict='latest=10 shortcuts=1 limit=99 result=FAIL (unreadable rounds [10])'
selftest pass=7 fail=0
0
```

Every fixture `git init`s its own repo and asserts `git -C <fixture> rev-parse --show-toplevel` equals the fixture path before the first commit; commit identity is passed per-command (`-c user.name= "shortcut-tally selftest" -c user.email=selftest@example.invalid -c commit.gpgsign=false`), never written to any config; the fixture root is removed in a `finally`.

## 5. Defects the promotion had to fix (draft evidence, exact lines)

Run of the frozen draft on the same clone and commit — `out/X9Tally/round47-draft-at-380bcdff.out` — ends with:

```
47     4  K1Cheat,K2Cheat,X1Stable,X2Revision  C1,C2  K1Cheat,K2Cheat  -  yes(w1,folded)  unreadable:mutation-report
note: round 47: .ufo/waves/round-47/w1/out/M1Ctr.md: ambiguous killed [29, 44]
note: round 47: .ufo/waves/round-47/w1/out/M1Tool.md: ambiguous killed [3, 22]
note: round 47: .ufo/waves/round-47/w1/out/M2Ctr.md: ambiguous killed [13, 23]
```

Because round 47 is the latest round, the draft's own `--check` would have exited 1 forever on the lane's newest evidence. Four causes, all in the draft's parse (the reports themselves are correct):

- **D1 — `/` denominator leaks into the killed set.** `.ufo/waves/round-47/w1/out/M1Ctr.md:3` (`29/44 mutants killed`) and `M2Ctr.md:3` (`13/23 mutants killed`): the generic `N mutants killed` pattern matched `44 mutants killed` / `23 mutants killed` after `29/` / `13/`, so killed became `{29,44}` / `{13,23}`. Shown by the two `ambiguous killed` notes above. Fix (in v2): `(?<![\d/])` before the bare killed patterns. Rounds 43/44/46 use `A of B ... killed` and are untouched (rows identical, §2).
- **D2 — split kills treated as a contradiction.** `.ufo/waves/round-47/w1/out/M1Tool.md:3`: `33 mutants ... 22 killed by the tool's own selftest, 3 killed by the frozen counter, 5 equivalent, 3 survived`. Fix: several killed counts now sum (`22+3`), and the sum must still close `killed+survived+equivalent == total`; the tally prints the split (`M1Tool ... 3/33 (killed=3+22)`). A battery that does not close stays unreadable (selftest `contradictory-report`, `5/9 killed, 6 survived` → exit 1).
- **D3 — `M<d>Replay.md` outside the report family, and an uppercase verdict.** `.ufo/waves/round-47/w1/out/M2Replay.md:3`: `24 mutants of tools/kama-live-replay.py ... 10 SURVIVED both ..., 2 equivalent`. The draft's `REPORT_NAME` was `M<d>(Ctr|Tool)`, so this seat's 24 mutants were silently dropped (round 47 would have read `26/100`, not `36/124`); its `surviv` pattern is also case-sensitive. Fix: family `M<d>(Ctr|Tool|Replay)` and a case-insensitive survived pattern.
- **D4 — `--json` output was not parseable under `--check`.** The draft printed the `latest=... result=...` verdict on stdout after the JSON array; any consumer doing `json.loads(stdout)` fails (`Extra data: line 59 column 1`, reproduced while building the selftest). v2 prints `{"meta": {repo, rev, rounds}, "records": [...]}` and sends the check verdict to stderr when `--json` is set.

Reported as findings, not repaired in place: the draft under `.ufo/waves/round-47/w1/out/X9Tally/` is frozen.

## 6. Finding the promotion does **not** fix: the gated id family is a lower bound

`shortcuts` counts only `K<d>Cheat|K<d>Hist|K<d>R<d>|V<d>Code|X<d><Name>|W<d><X><d>|R4<d><X><d>|M<d>Ctr|M<d>Tool`. Round 47's paragraph names twelve attack seats — K1Cheat, V1Ctr, K1Fixture, X1Stable, L1Lowthr, K1Design, K2Cheat, K2Tamper, K2Checks, K2Design, X2Revision, Sen2Replay (`SCORECARD.md:2725-2727`) — and the gate sees four. The new `wide` field (diagnostic, never gated) reads the same sentences under generalised seat shapes and gets 10: round 47 `4 → 10`, round 46 `8 → 9`, round 44 `2 → 3`. It is still not a faithful count: it misses `L1Lowthr` and `Sen2Replay` (shapes outside the family), and it over-counts round 44 by adding `K2Design`, which `SCORECARD.md:2396` names as a reviewer of the landed ledgers ("6 independent reviewers and K2Design for C2"), not an attacker. So making it a gate would trade a stable undercount for an unstable overcount. Recommendation for round 49, not this wave: keep `--check` on the frozen family and record in the tally's own docstring (done) that the column is a lower bound; a real count needs a per-round seat census, not a name regex.

## 7. Promotion notes for the L1 (integration)

- Target `tools/shortcut-tally.py` is outside `tools/gate-registry-check.py`'s population (`.ufo/waves/round-*/count-*.py`, `tools/round<N>-*.py`), so no registry row is forced. SKILL.md registration is the lane's habit for general tools (`tools/append-only-audit.py`, `tools/kama-live-replay.py` have rows); proposed row text:

  `| Shortcut tally | trend: python3 tools/shortcut-tally.py --repo <clone> --rev <full-commit> [--rounds 40-47] [--json] | 0 every round readable, 1 --check missed (latest round's shortcut count above N, latest cannot certify, or a round unreadable), 2 could not evaluate (repo/rev/tree unreadable) | python3 tools/shortcut-tally.py --selftest --scratch <dir> prints selftest pass=7 fail=0; pinned at 380bcdff9c8af06997c482f6eb03db926a794a2b rounds 40-47: shortcuts 5,2,2,8,4 (40/41/45 no-disclosure), mutants 20/53, 22/79, 25/117, 36/124, round 47 ok | read-only; git rev-parse/ls-tree/cat-file only |`

- Default range is `--rounds 40-47`; extend to `...-48` when the round-48 wave files its `What met=True does not show` paragraph (the wave spec landed at `b85783e8`, no disclosure yet at `380bcdff`). Round 48 currently has no `## Round 48` heading, so including it today would read `unreadable:no-section` and fail `--check` by design.
- Suggested gate value: `--check 4` is the measured floor at `380bcdff`. A round that discloses only wide-shape seats leaves `shortcuts=None` and `--check` exits 1 ("cannot certify") — the conservative direction, deliberate.

## 8. Risks

- `wide` is heuristic and is documented as diagnostic; it must not be used as an exit signal.
- The mutant column becomes non-comparable with earlier rounds' readings from the draft for round 47 only (`36/124` here vs `26/100` if `M2Replay` is dropped); the additional 24 are the round's own replay-tool mutants, so the new number is the correct one.
- The tool needs `git` on PATH (the draft needed none); every error path that leaves the repository unreadable exits 2, never 0.
- No tool was installed or upgraded in this seat (`git 2.56.0`, `python3 3.14.8` as shipped; pacman untouched per the host-wide pause).

## 9. Files

- `kama-shokunin/.ufo/waves/round-48/w1/out/X9Tally/shortcut-tally.py` — proposed lane tool (v2).
- `kama-shokunin/.ufo/waves/round-48/w1/out/X9Tally/tally.out`, `tally.json`, `check-pass.out`, `check-fail.out`, `selftest.out`.
- `kama-shokunin/.ufo/waves/round-48/w1/out/X9Tally/tally-bare.out`, `tally-worktree-dirty.out`, `nongit.out`, `badrounds.out`.
- `kama-shokunin/.ufo/waves/round-48/w1/out/X9Tally/round47-draft-at-380bcdff.out` — draft defect evidence.
- `kama-shokunin/.ufo/waves/round-48/w1/out/X9Tally/run.txt` — commands, exit codes, clone/commit, fixture description.
