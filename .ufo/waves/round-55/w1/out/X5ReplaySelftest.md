# X5ReplaySelftest — round-55 X5 sabotage re-verification (kama lane)

**Verdict: the two round-54 named sabotages both kill at 9c60eae6f7ed84f7da93d219a406aadc30958c6c — `code-hostonly-no-library` and `code-non-regular-member` each turn the selftest red with exactly that named case (pass=47 fail=1, exit 1) while the unmutated copy is green (pass=48 fail=0, exit 0) and `kama-llamacpp-live.py --selftest` prints `selftest: ok`; the round-54 routed defect 2 is now closed by committed receipts, and no defect was found in the lane tools.**

Axes (godspeed): **A — kill power** (does each named rule mutation turn its named case red?), **B — attribution** (is the red produced by the mutation and not by the scratch layout or an unrelated case?), **C — receipt completeness** (is every output verbatim, with its exit code, on a committed path?).

## 1. Setup and provenance

```
S=/fast/scratch/hyaku/kama-r55/w1/X5ReplaySelftest; export TMPDIR="$S"
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
git -C "$S/lane" rev-parse --show-toplevel  -> /fast/scratch/hyaku/kama-r55/w1/X5ReplaySelftest/lane
git -C "$S/lane" checkout -q 9c60eae6f7ed84f7da93d219a406aadc30958c6c
git -C "$S/lane" rev-parse HEAD              -> 9c60eae6f7ed84f7da93d219a406aadc30958c6c
```

The two tools under test are byte-identical at the freeze commit, in the clone, and in the
live lane worktree — so the lane-path run and the clone run are the same bytes:

```
git -C "$S/lane" show 9c60eae6...:tools/kama-live-replay.py   | sha256sum -> d9b1bdf2e1ba7f0976d1cb4a7bc435fb71e56e96c2dbf18d2fcc2f50201cc03b
git -C "$S/lane" show 9c60eae6...:tools/kama-llamacpp-live.py | sha256sum -> 98d2e6bb48a90e60797df0d2bee895eac4a6cdd9859af2dc47b64bdb4a36fbe9
sha256sum <lane>/tools/kama-live-replay.py                    -> d9b1bdf2e1ba7f0976d1cb4a7bc435fb71e56e96c2dbf18d2fcc2f50201cc03b
sha256sum <lane>/tools/kama-llamacpp-live.py                  -> 98d2e6bb48a90e60797df0d2bee895eac4a6cdd9859af2dc47b64bdb4a36fbe9
```

Full per-fixture provenance (toplevel assertion, base commit, mutant commit, tool sha256) is in
`X5ReplaySelftest/fixture-provenance.txt`. Every fixture repo was created with
`git -C "$D" init -q` and its `rev-parse --show-toplevel` was asserted to equal `$D` before the
first commit; all commits used `git -C "$D" -c user.name=fx -c user.email=fx@invalid commit`.
The lane itself was never mutated: `git -C <lane> status --porcelain -- tools/` is empty.

## 2. Baseline — both selftests green at the freeze commit

```
python3 $S/lane/tools/kama-live-replay.py --selftest --scratch $S
  -> KLR_SELFTEST pass=48 fail=0      exit=0
     (48 'pass' lines, 0 'FAIL' lines; the two round-53 cases are among them:
      'pass code-hostonly-no-library' at line 39, 'pass code-non-regular-member' at line 40)

python3 $S/lane/tools/kama-llamacpp-live.py --selftest
  -> selftest: ok; closed tcp6 listeners ::1:39261, ::ffff:127.0.0.1:46469      exit=0
```

Receipts: `X5ReplaySelftest/selftest-replay-base-9c60eae.log`,
`X5ReplaySelftest/selftest-llamacpp-base-9c60eae.log`.

The seat's literal commands against the lane path (not the clone) were run as well and gave the
same results byte-for-byte — this is the form the round-54 closure asked for:

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-live-replay.py --selftest --scratch $S
  -> KLR_SELFTEST pass=48 fail=0      exit=0     (X5ReplaySelftest/selftest-replay-lane-path.log)
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py --selftest
  -> selftest: ok; closed tcp6 listeners ::1:36693, ::ffff:127.0.0.1:36815      exit=0
     (X5ReplaySelftest/selftest-llamacpp-lane-path.log)
```

## 3. The two named sabotages — both kill, each with its named case

The two round-54 sabotages are the round-53 mutations **c** and **d**, whose definitions are
committed at `.ufo/waves/round-53/w1/out/X5Selftest/mutations-replay.diff` (copied into this
seat's out dir as `source-round53-mutations-replay.diff`) and were re-applied here to scratch
copies of the frozen tool:

| # | sabotage | site at 9c60eae | selftest result | killed? |
|---|---|---|---|---|
| c | the `no-archive-library` rule deleted (`if not members:` block removed) | `tools/kama-live-replay.py:366-367` (`verify_code`) | `FAIL code-hostonly-no-library: own_code={'verified': False, 'members': {}, 'host': ['/usr/lib/libc.so.6']} probs=['code-mapping:required-absent:libggml-base.so*']` — `KLR_SELFTEST pass=47 fail=1`, exit 1 | **yes** |
| d | `member_digests` hashes non-regular members (`and ti.isreg()` removed) | `tools/kama-live-replay.py:311` (`member_digests`) | `FAIL code-non-regular-member: own_code={'verified': True, 'members': {'build/bin/libhard.so': '15d7c2…'}, 'host': []} probs=[]` — `KLR_SELFTEST pass=47 fail=1`, exit 1 | **yes** |

Unified diffs of the two mutations, against the frozen file:
`X5ReplaySelftest/mutation-c.diff`, `X5ReplaySelftest/mutation-d.diff`.

Commands (each run in its own fixture repo, cwd = that repo):

```
cd $S/sab-c && python3 $S/sab-c/tools/kama-live-replay.py --selftest --scratch $S/sab-c
  -> FAIL code-hostonly-no-library ... KLR_SELFTEST pass=47 fail=1     exit=1
cd $S/sab-d && python3 $S/sab-d/tools/kama-live-replay.py --selftest --scratch $S/sab-d
  -> FAIL code-non-regular-member ... KLR_SELFTEST pass=47 fail=1     exit=1
```

Receipts: `X5ReplaySelftest/sabotage-c-code-hostonly-no-library.log`,
`X5ReplaySelftest/sabotage-d-code-non-regular-member.log`.
Both were re-run a second time and are bit-identical in verdict
(`sabotage-c-repeat2.log`, `sabotage-d-repeat2.log`): pass=47 fail=1, exit 1, same named case
each time. The `FAIL` line is deterministic in content except for the payload digest the
fixture draws from `os.urandom(16)`.

**Positive control.** An unmutated copy of the same file placed in the same scratch layout
(`$S/sab-base/tools/kama-live-replay.py`, no `registry/` sibling needed by this tool) is green:
`KLR_SELFTEST pass=48 fail=0`, exit 0 — `X5ReplaySelftest/control-unmutated-copy.log`. So the
red in §3 is produced by the mutation, not by the scratch layout, and not by the missing lane
tree around the copy.

## 4. Attribution — the red is the rule, not a neighbouring case

A rule-level probe (not a selftest run) calls `verify_code` directly with each named case's
exact input, on all three trees — `X5ReplaySelftest/attribution-rule-level.log`:

```
[unmutated-9c60eae] A host-only probs=['code-mapping:no-archive-library', 'code-mapping:required-absent:libggml-base.so*']  case_passes=True
[unmutated-9c60eae] B hardlink  probs=['code-mapping:not-a-member:build/bin/libhard.so', 'code-mapping:no-archive-library']    case_passes=True
[sabotage-c]        A host-only probs=['code-mapping:required-absent:libggml-base.so*']            has_no_archive_library=False  case_passes=False
[sabotage-d]        B hardlink  probs=[]  members={'build/bin/libhard.so': '87a79b5c…'}  member_admitted=True  refused_as_not_a_member=False
```

So mutation c removes exactly the `code-mapping:no-archive-library` string that the
`code-hostonly-no-library` assertion demands, and mutation d admits the hardlinked member
`build/bin/libhard.so` that the `code-non-regular-member` assertion demands to be refused. Each
mutation moves exactly one rule; the other named case is unaffected in the opposite direction
(`[sabotage-c] B case_passes=True`, `[sabotage-d] A case_passes=True`).

## 5. The two literal seat-wording readings, also measured

The seat text names the sabotages by their *case* ("the `code-hostonly-no-library` assertion
reverted to required-only form", "the `code-non-regular-member` block removed"), which reads
either as the rule mutations of §3 or as edits to the selftest cases themselves. Both readings
were measured so the ambiguity is discharged rather than assumed.

**Reading A — the rule mutations (§3).** Removing the rule is what a "sabotage" means: the tool
is broken and the selftest must catch it. Both kill, with the named case. This is the round-54
sabotage set and it reproduces the round-54 report's numbers exactly
(`.ufo/reports/round-54/kama.md`, copied as `source-round54-kama-report.md`: "mutation c →
`FAIL code-hostonly-no-library` (pass=47 fail=1); mutation d → `FAIL code-non-regular-member`
(pass=47 fail=1); unmutated copy → `KLR_SELFTEST pass=48 fail=0`").

**Reading B — weaken the assertion instead of the rule.** Reverting the assertion to
required-only form (`tools/kama-live-replay.py:765-767`, dropping the
`"code-mapping:no-archive-library" in probs` conjunct):

```
FAIL? no -> 'pass code-hostonly-no-library';  KLR_SELFTEST pass=48 fail=0   exit=0
```

(`aux-assertion-reverted-to-required-only.log`, diff
`aux-mutation-assertion-reverted.diff`.) This is **not** a kill: the weakened assertion still
passes when the rule is intact, and — the reason it is not a substitute for §3 — it *also*
passes when the rule is removed, because the surviving `required-absent` conjunct is satisfied
by the same fixture:

```
aux combo (weakened assertion + mutation c) -> 'pass code-hostonly-no-library'; pass=48 fail=0  exit=0
```

(`aux-combo-weakened-assertion-plus-mutation-c.log`.) Reading B therefore cannot detect the
sabotage it names; §3's reading is the one that holds, and the round-54 numbers reproduce.

**Reading C — delete the `code-non-regular-member` case block.** Removing the whole block
(`tools/kama-live-replay.py:769-790`) drops the suite to 47 cases:

```
-> 'code-non-regular-member' absent from the output;  KLR_SELFTEST pass=47 fail=0   exit=0
```

(`aux-case-block-removed.log`, diff `aux-mutation-case-block-removed.diff`.) Also not a kill —
it silences the case rather than exercising it, and the green suite would be a false negative.
Recorded so the closure does not read the `pass=47` of a deleted case as coverage.

**Conclusion on the wording.** The seat's requirement "show each selftest FAILs with the named
case" is satisfied by the round-54 sabotage set (rule mutations c and d), which is the only one
of the three readings under which the named case actually fails. Readings B and C are recorded
as evidence that the other two readings are vacuous, not as the deliverable.

## 6. Round-54 routed defect 2 — status

`corpus/lessons/round-54-verifier-spotcheck.md:43` records the X5 sabotage re-verification as
"not re-run (sibling selftest); no receipt path cited … unverifiable at closure — routed", and
line 79 asks for the receipts to be committed under a waves directory. The receipts now exist
under a waves directory with verbatim output and exit codes (§7). The round-54 claim of
"48/48, two FAIL mutants" is reproduced from the frozen bytes: `pass=48 fail=0` at the
freeze commit and at the live lane path, `pass=47 fail=1` with the named case for each of the
two mutants, `selftest: ok` for the llamacpp tool.

## 7. Artifacts (all under `.ufo/waves/round-55/w1/out/X5ReplaySelftest/`)

| file | what it is |
|---|---|
| `selftest-replay-base-9c60eae.log` | frozen-clone baseline replay selftest, `pass=48 fail=0`, exit 0 |
| `selftest-llamacpp-base-9c60eae.log` | frozen-clone baseline llamacpp selftest, `selftest: ok`, exit 0 |
| `selftest-replay-lane-path.log` | the seat's literal lane-path command, `pass=48 fail=0`, exit 0 |
| `selftest-llamacpp-lane-path.log` | the seat's literal lane-path command, `selftest: ok`, exit 0 |
| `sabotage-c-code-hostonly-no-library.log` | mutation c run: `FAIL code-hostonly-no-library`, `pass=47 fail=1`, exit 1 |
| `sabotage-d-code-non-regular-member.log` | mutation d run: `FAIL code-non-regular-member`, `pass=47 fail=1`, exit 1 |
| `sabotage-c-repeat2.log`, `sabotage-d-repeat2.log` | second runs of the same two mutants (same verdicts) |
| `control-unmutated-copy.log` | unmutated copy in the same scratch layout: `pass=48 fail=0`, exit 0 |
| `attribution-rule-level.log` | rule-level probe showing which string/member each mutation changes |
| `mutation-c.diff`, `mutation-d.diff` | unified diffs of the two rule mutations vs the frozen file |
| `aux-assertion-reverted-to-required-only.log` | reading B: weakened assertion → `pass=48 fail=0` (not a kill) |
| `aux-case-block-removed.log` | reading C: case block deleted → `pass=47 fail=0` (not a kill) |
| `aux-combo-weakened-assertion-plus-mutation-c.log` | weakened assertion + mutation c → `pass=48 fail=0` (reading B cannot detect the sabotage) |
| `aux-mutation-assertion-reverted.diff`, `aux-mutation-case-block-removed.diff` | unified diffs of the two auxiliary mutants |
| `frozen-kama-live-replay-9c60eae.py` | the exact bytes the diffs are against |
| `fixture-provenance.txt` | per-fixture toplevel assertion, commits, tool sha256s |
| `source-round53-mutations-replay.diff` | committed source of the two mutation definitions (round-53 seat) |
| `source-round54-kama-report.md` | the round-54 lane report whose numbers this reproduces |
| `RECEIPTS.sha256` | sha256 of every artifact above |

## 8. Risks, limits, and what is not established

- **The mutation set is the round-53 pair (c, d) re-applied at the freeze commit**, i.e. the
  round-54 sabotage set named in `.ufo/reports/round-54/kama.md`. It is the set the round-54
  closure reported; this seat did not re-derive it from scratch, and the round-53 seats' other
  four mutations (a, b, e, g) are out of this seat's scope.
- **The `code-hostonly-no-library` case is a `verify_code` unit case, not an end-to-end replay
  case.** It calls the rule function directly. That is what lets the rule be isolated, but it
  means the case proves the *rule* is exercised, not that a live replay with a host-only
  mapping is rejected end to end. [INFERENCE from `tools/kama-live-replay.py:760-769`; no live
  replay was run here.]
- **Two of the three selftests bind and immediately close their own loopback listeners** (the
  llamacpp selftest prints the ports it closed). No service was started, stopped or restarted by
  this seat; `pgrep -af llama-server` shows only another seat's (`J5EnvNames`) processes, none
  under this seat's scratch. No `llama-server` was started here at all — both selftests are
  offline.
- **No counter was run.** The C1/C2 counters belong to other seats; this seat ran only the two
  live/replay selftests named in the assignment.
- **The lane was not modified.** `git -C <lane> status --porcelain -- tools/` is empty; every
  edit was made in scratch fixture repos and every receipt was written to this seat's out
  directory only. Nothing was committed anywhere by this seat (the receipts are written for the
  integrator to commit — the lane's Git index was not touched, per the lane bounds).
- **The frozen file's digests vary per run** for the hardlink payload (the fixture uses
  `os.urandom(16)`), so the `FAIL` line's member digest differs between runs. The case name,
  the pass/fail counts and the exit codes are stable.

## 9. Cleanup

`$S` (the scratch tree: lane clone, four fixture repos, helper scripts) was removed after the
receipts were written; the only things that survive are the files under
`.ufo/waves/round-55/w1/out/X5ReplaySelftest/` listed in §7. No tool was installed or upgraded
this round, so there is nothing to record against the tooling directive.
