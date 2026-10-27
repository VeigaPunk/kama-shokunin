# X01ReplayC1 — round-56 C1 battery replay vs committed receipts

Seat: executor (leaf), lane `kama-shokunin`. Judged on operability + calibration.
Run once, from the lane root, on freeze tip `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7`.

## Verdict

C1 replays exactly against its committed receipts. All three legs reproduce the
recorded field values and exits; the kill mutant's detected-expectation run fails as
the frozen target requires; the counter digest equals the frozen digest.

## Surface verification (before running)

| Item | Observed | Frozen | Match |
|---|---|---|---|
| `tools/round56-replay-code-audit.py` sha256 | `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f` | same (prereg C1 `counter_sha256`) | yes |
| Lane HEAD | `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7` (freeze tip) | freeze tip | yes |
| Base tip tools | `git ls-tree -r e10b6d39 tools/` lists `round54-replay-code-audit.py` as the newest replay counter | claim names "the round-55 counter" | resolved, same artifact; see D2 |
| Base `BAD_ENV` | `("LD_PRELOAD", "DYLD_INSERT_LIBRARIES")` — no `LD_AUDIT` | red-baseline premise | yes |
| Freeze `BAD_ENV` | `("LD_PRELOAD", "DYLD_INSERT_LIBRARIES", "LD_AUDIT")` | detection premise | yes |
| Battery `ROSTER` (AST) vs prereg `battery.roster` | dict-equal, 3 entries, 1 kill, 2 controls | identical | yes |

Environment: cwd `/home/vgpnk/Projects/shokunin/kama-shokunin`, `TMPDIR=/fast/scratch/hyaku/kama-r56/X01ReplayC1`,
python3 3.14.8. Scratch removed after the run.

## Battery execution

The frozen battery `tools/round56-env-leg-battery.py` hardcodes its receipt directory to
`.ufo/waves/round-56/measured` (outside this seat's write bounds), so it was run once via
an unmodified-logic copy whose only change is that `OUT` points at this seat's output
directory and its mutant `TemporaryDirectory` points at this seat's scratch. Legs,
expectations, anchor and assertion code are byte-identical to the committed battery.

```
$ python3 <battery copy>.py     # from lane root
base-old-counter: ld_audit=missed exit=0 -> pass
round56-counter: ld_audit=detected exit=0 -> pass
m-drop-ldaudit: ld_audit=missed exit=0 -> pass
battery_exit=0
```

Raw legs were also driven directly through `tools/round56-env-leg-test.py` (receipts
`replay-*.out`), plus the falsification-side run of the mutant against the *detected*
expectation:

```
$ python3 tools/round56-env-leg-test.py --counter tools/round54-replay-code-audit.py --expect missed
ld_audit=missed pid=1886001 problems=[]
exit=0

$ python3 tools/round56-env-leg-test.py --counter tools/round56-replay-code-audit.py --expect detected
ld_audit=detected pid=1886003 problems=['env: server environment carries LD_AUDIT']
exit=0

$ python3 tools/round56-env-leg-test.py --counter <scratch>/m-drop-ldaudit.py --expect missed
ld_audit=missed pid=1886283 problems=[]
exit=0

$ python3 tools/round56-env-leg-test.py --counter <scratch>/m-drop-ldaudit.py --expect detected
ld_audit=missed pid=1886285 problems=[]
exit=1        # expected-detected assertion fails, as the frozen target states
```

Every leg also emitted the glibc line on stderr
`ERROR: ld.so: object '/usr/lib/libexpat.so.1' cannot be loaded as audit interface: undefined symbol: la_version; ignored.`
— the DSO is refused by this glibc, so the probe is a name-presence test, exactly the
scope stated in the preregistration `limits`.

## Leg-by-leg comparison with committed receipts

| Leg | Committed receipt | Replay (pid-normalized diff) | Prereg target | Result |
|---|---|---|---|---|
| base-old-counter (`round54`, expected missed) | `measured/base-c1.out` | identical, `diff_exit=0` | `ld_audit=missed exit=0` | met |
| round56-counter (expected detected) | `measured/build-c1.out` | identical, `diff_exit=0` | `ld_audit=detected exit=0` | met |
| m-drop-ldaudit (expected missed) | `measured/m-drop-ldaudit.out` | identical, `diff_exit=0` | `ld_audit=missed` | met |
| m-drop-ldaudit vs `--expect detected` | (implied by target) | `exit=1` | expected-detected check fails | met |

The base control `controls/base-c1.out` (`ld_audit=missed exit=0 problems=[]`) is the same
shape as the replayed baseline leg; no divergence.

Mutant is a strict one-line deletion, anchor unique (`src.count(old) == 1` asserted before
write); `m-drop-ldaudit.diff` records the single hunk. Frozen counter
`fc3d4b63…ff6f`, mutant `a3faaf6e…ddb4`.

## Findings

No falsifier fired:

- base counter detects LD_AUDIT? No (`missed`).
- round-56 counter misses it? No (`detected`, with the named problem string).
- single-line mutant still detects it? No (`missed`; fails `--expect detected` with exit 1).
- measured counter sha256 differs from frozen? No.

### D1 — battery is not seat-runnable unmodified (minor, operability)

`tools/round56-env-leg-battery.py` writes to a fixed `.ufo/waves/round-56/measured` and a
fixed `/fast/scratch/hyaku/kama-r56/l1-battery` scratch root. Any replay seat confined to
its own output directory cannot execute the frozen battery as committed without either
violating write bounds or copying it. Proposed fix (for a future round, not this frozen
tip): add `--out` and `--scratch` arguments defaulting to today's paths; the replay above
only substituted those two constants.

### D2 — claim says "round-55 counter", battery names the round-54 file (naming only)

The C1 claim's red baseline is described as "the round-55 counter", while the battery
uses `tools/round54-replay-code-audit.py`. At the round-55 base tip `e10b6d39` that file
is the newest replay counter in `tools/`, so the two names denote the same artifact; the
baseline's `BAD_ENV` confirms the expected miss. Not a falsifier, but the report should
say "the counter in force at the round-55 tip (`tools/round54-replay-code-audit.py`)".

### D3 — kill leg passes on a miss (expected, worth stating)

The battery runs the mutant with `--expect missed`, so the mutant scoring "pass" means it
misses; the falsification signal is the separate `--expect detected` run (exit 1, shown
above). Reading only the battery exit code without that second run would not discriminate.

## Bounds observed

- Lane tree untouched: no git/jj mutation, no `git add/commit/reset`; no writes outside
  `.ufo/waves/round-56/w1/out/X01ReplayC1/`.
- No pacman; no tool installs (`tool_installs: []` unchanged).
- Scratch `/fast/scratch/hyaku/kama-r56/X01ReplayC1` removed after the run; no `/tmp` use.

## Evidence retained in this seat's output directory

`base-c1.out`, `build-c1.out`, `m-drop-ldaudit.out` (battery-produced, redirected),
`replay-base-c1.out`, `replay-build-c1.out`, `replay-m-drop-ldaudit.out`,
`replay-m-drop-ldaudit-expect-detected.out`, `replay-battery-stdout.txt`,
`m-drop-ldaudit.py`, `m-drop-ldaudit.diff`.
