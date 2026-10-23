# VerifyMistakeFix — kama round 29, wave 2 (attempt 2)

Seat: `kama-r29-w2-VerifyMistakeFix-6` (executor)
Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin` @ `513eba3ba51a142c9936553e3a85918345eb5c4c`
Full report: `.ufo/waves/round-29/w2/out/kama-r29-w2-VerifyMistakeFix-6/report.md`

No lane mutation: `git archive` extraction + scratch `git clone` under `/tmp/kama-w2-VerifyMistakeFix/`,
seat-unique `--scratch` under `/tmp`. No `git worktree add`, no lane `git add/commit/checkout/reset`.

## Verdict

The mined fix itself is **correct, minimal and harmless**. The attempt-1 narrative around it has
four defects the L1 must repair before landing.

| Claim | Verdict |
|---|---|
| Patched tool @ `75b78bb4` exits 1 flagging `2026-10-23 ~08:45Z (later than commit by 404s)` | **PASS** — byte-identical to `mined/patched-75b78bb4.out` |
| Patched tool @ `d8bf1804` exits 0 | **PASS** — byte-identical to `mined/patched-d8bf1804.out` |
| Original tool @ `75b78bb4` exits 0 (the mined blindness) | **PASS** — byte-identical to `mined/orig-75b78bb4.out` |
| `--selftest` in working tree: 15 PASS, exit 0 | **FAIL — 13 `[PASS]` (14 lines containing "PASS"), exit 0** |
| Patched tool @ `513eba3b` exits 0 | **FAIL on the round-28 prereg path (exit 1); exit 0 only on the round-29 prereg path** |
| Widened regex harms nothing else | **PASS** — 8662 files scanned, exactly 1 new flag, the intended target |
| Fix kills the 3 MutateTimeCheck survivors | **PASS only with the uncommitted working-tree case**; at committed HEAD all 3 survive |
| The mined receipts are committed | **FAIL — 2 of 7 untracked** |

## Measured exit codes

`python3 <tool> --repo /tmp/kama-w2-VerifyMistakeFix/clone --path <path> --rev <rev> --strict`

| tool | rev | path | exit |
|---|---|---|---|
| patched (`ca72edf2…`) | 75b78bb4 | `.ufo/waves/round-28/preregistration.json` | **1** (matches receipt, byte-identical) |
| patched | d8bf1804 | `.ufo/waves/round-28/preregistration.json` | **0** (matches receipt, byte-identical) |
| original (`3d508f77…`) | 75b78bb4 | `.ufo/waves/round-28/preregistration.json` | **0** (matches receipt, byte-identical) |
| patched | 513eba3b | `.ufo/waves/round-28/preregistration.json` | **1** — no receipt exists |
| patched | 513eba3b | `.ufo/waves/round-29/preregistration.json` | **0** — no receipt exists |
| patched | 75b78bb4 | `.ufo/waves/round-29/preregistration.json` | **2** — path absent at that rev |
| original | d8bf1804 / 513eba3b | round-28 prereg | **0** / **0** — controls |

Self-test: working tree **exit 0, 13 `[PASS]`**; committed `513eba3b` exit 0, 12 `[PASS]`;
original `75b78bb4` exit 0, 10 `[PASS]`.

## Harm surface (measured)

Both tools run over **every** tracked file at `513eba3b` (8662 files), default horizon and `--strict`:

```
### mf=86400 (default-horizon): 8662 files; PATCHED-only extra flags in 1 file(s)
  FILE .ufo/waves/round-28/preregistration.json
    ORIG   : (none)
    PATCHED: FLAG line 41: 2026-10-23 ~08:45Z (later than commit by 404s)
### mf=-1 (strict): 8662 files; PATCHED-only extra flags in 1 file(s)   [same single file]
```

Exactly one new flag lane-wide, and it is the intended target. No collateral false positives.

## Mutants (in-process and subprocess)

```
M02-no-plain-space-in-TIME_RE    committed: SURVIVED (exit 0) | working-tree: KILLED (exit 1)
M05-no-plain-space-in-parse_iso  committed: SURVIVED (exit 0) | working-tree: KILLED (exit 1)
M07surgical-zero-seconds-only    committed: SURVIVED (exit 0) | working-tree: KILLED (exit 1)
   each killed by: [FAIL] flag: space-separated seconds-precision time 7 s after commit: expect 1, got 0
```

Confirms the lesson's claim — **only for the uncommitted working-tree tool**.

## Defects for the L1 to repair

**D1 — wrong self-test PASS count.** Spec says "15 PASS"; measured **13 `[PASS]`** (11 `case()` +
missing-path + bad-revision), exit 0. `LOG.md:1858` and `corpus/lessons/round-29.md:125` both say
"14 PASS" — that is the count of lines *containing* "PASS" (13 + `SELFTEST PASS`), not the case
count. This is exactly the Q-class off-by-one that C1 measures. Say "13 cases, 13 PASS, exit 0".

**D2 — the spec's "at 513eba3b expect exit 0" is false for the round-28 prereg path.** Measured
**exit 1** there: the false `~08:45Z` bytes are still in the frozen file and `75b78bb4` (08:38:16Z)
is still its last committer, so it is still 404 s in the future. Correct behaviour, but no
`513eba3b` receipt exists and the append-only repair is recorded only in `LOG.md` /
`corpus/lessons/round-29.md`. Add the receipt and state the design intent. Exit 0 at `513eba3b`
holds only on the *round-29* prereg path, which has no timestamps at all — a different fact.

**D3 — the mutant-killing selftest case is uncommitted.** The working tree adds exactly one case
(`flag: space-separated seconds-precision time 7 s after commit`) over `513eba3b`; that one case is
what kills M02/M05/M07. Landed without it, the lane ships a falsifier whose selftest still passes
for all three mutants. Land the working-tree tool change together with the mined receipts.

**D4 — two mined receipts are untracked.** `UNTRACKED patched-selftest-v2.out`,
`UNTRACKED survivor-recheck.out`; the other five are tracked. The lesson cites both untracked files
as the proof the mutants are killed. Commit them.

**D5 — minor:** the tool's module docstring and `--help` still say it reads only
`YYYY-MM-DDTHH:MM[:SS]Z`, stale since the fix. The in-code comment at lines 39–41 is current.

**D6 — minor, disclosed:** residual notation limits — `2026-10-23 ~ 08:45Z`, `2026-10-23t08:45Z`,
`2026-10-23T08:45:00.123Z`, `2026-10-23~08:45Z` are all still missed. Also the counter's T-class
regex (`count-c1.py:72`, `(?:T| ~|T~)`) and the tool's `(?:T| ~| )` now differ in **both**
directions: the counter matches `T~` but not a plain space; the tool matches a plain space but not
`T~`. Disclose rather than leave accidental.

## Checks the L1 should run after landing

```
python3 tools/prereg-time-check.py --selftest --scratch /tmp/ptc-selftest-postland
# expect: exit 0, 13 [PASS], "SELFTEST PASS"
```
plus re-running the three one-line mutants against the landed tool — all three must be KILLED.

## Notes

- The mined fix is committed in `513eba3b` and minimal: 2 regex strings + a comment
  (`diff tree-75b78bb4 → tree-513eba3b`).
- The legitimate-future case is unaffected: `2026-10-25T14:27:28Z` still `clean` under the default
  horizon and `flag` under `--strict`, in all three tool versions.
- `sha256(.ufo/waves/round-29/count-c1.py) = fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`
  — matches the frozen counter named in the spec. The counter references neither
  `prereg-time-check.py` nor `08:45`, so the mined-fix claim is a repair outside C1's universe.
- No tools installed or updated (no `uv`/`npx`/binary installs, no `pacman`); Python 3.14.8 and
  Git 2.56.0 used as-is.
