# RerunCtlSourceBounds — re-execution of control CtlSourceBounds (C1 pre-data controls)

Seat `kama-r29-w2-RerunCtlSourceBounds`, kama lane round 29 wave 2, 2026-10-23.
Claim served: **C1 (calibration), pre-data controls**.
Full report + evidence: `.ufo/waves/round-29/w2/out/kama-r29-w2-RerunCtlSourceBounds/report.md`.

## Result

The committed control reproduces exactly; the expected `valid 9 false 7 unresolved 9 met False`
is confirmed.

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 9 false_corrections 7 unresolved 9 met False tip af96283389de
exit=0
```

- Counter: lane `.ufo/waves/round-29/count-c1.py`, sha256
  `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`, verified before the first
  run and again after all arms (unchanged).
- vs recorded `.ufo/waves/round-29/controls/CtlSourceBounds/counter.out`: **byte-identical**
  (141 B, sha256 `8aa1b087da51988a314f4fc23b73c1e308cec0cf2ae4a2f46d7c18587dd299e2`).
- `receipt.json`, `pristine-receipt.json`, `restored-receipt.json`, `pristine-counter.out`,
  `restored-counter.out` and `change.diff`: **byte-identical** to the recorded files.
- Control outcome **refused** (`met False`). Mutation-frame verdict **inconclusive**: the pristine
  baseline already fails the target (`unresolved 11`, `met False`), as attempt-1 also classified.
  The counter was never modified.

## Reproduced pieces

Fresh clone of the lane at `827d1365…1290` (tree `efe74520…`), policy = path-adjusted copy of the
committed `source-policy.py` (only `ROOT`/`REPO` constants changed). Regenerated
`source-statements.json`, `source-hashes.json`, `predictions.json`, `policy-hashes.json`,
`correction-rows.md` are all byte-identical to the recorded artifacts. Mutated `SCORECARD.md`
sha256 `f3f5a351…df17b`; `SHONEN.md` untouched `1ff9e2f3…d3fb5`.

Commit reproduced with the metadata read from the surviving attempt-1 clone (`ctl <ctl@local>`,
`1792753374 -0300`): `af96283389ded62899b386fdc988bd3ddcbca9e2`, parent
`827d136546b85059a984b34970f5b493d9a71290`, tree `410fb6f8d771558caa812dde93711e15cfb9e065`;
`change.diff` 1748 B, sha256 `34f45afc…51adb` — identical to recorded. The restored commit
reproduced too: `6df2824e7e43a74809aed51570171ed308818367`, tree `efe74520…`.

Additional arm for the item's literal "fresh clone at 2aa46e24": commit
`f341be9da6924cc1f59afe77812aa62ea902715b`, same policy artifacts, counter line

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 9 false_corrections 7 unresolved 9 met False tip f341be9da692
```

Receipt fields identical to the recorded receipt except `tip`. The base and freeze blobs of
`SCORECARD.md`/`SHONEN.md` are identical (`7af59cc0…`, `1ff9e2f3…`), so the counts are invariant to
the clone point; exact artifact reproduction needs the `827d1365` parent.

## Findings for the L1

1. **No substantive defect.** Recorded evidence for CtlSourceBounds is faithful and reproducible
   end-to-end from a fresh clone.
2. **Capture-format discrepancy (minor, not the measured line).** The recorded `*-counter.out`
   files are in attempt-1 `score-probe.py` format — `stdout + "\n" + "exit=N\n"` — one extra blank
   line before `exit=N` versus the literal CONTEXT step-3 command. Literal command sizes are
   140 B (mutated), 141 B (pristine), 141 B (restored) vs recorded 141/142/142 B. Re-composing the
   log the way `score-probe.py` does reproduces all three recorded files byte-identically. No effect
   on the counter line, receipt or verdict.
3. **Valid-row mechanism (disclosed limit).** The 9 "valid" rows come from constant P/Q failure
   strings (`p:absent`, `q:no-artifact`) matching by coincidence; 7 rows name holding Q statements
   and 2 mismatches are missed (`SCORECARD.md:Q:a7e98b1030:0`, `SCORECARD.md:Q:f1021c03db:0`), so
   `unresolved = 2 + 7 = 9`. This matches `controls/SUMMARY.md`; the counter tests false-statement
   selection (and observed values for H/N/C/T), not the provenance of the value string.
4. **Wording mismatch, harmless.** The item says clone at `2aa46e24`; the committed procedure used
   `827d1365` as parent. Both arms give the same measured result; only the tip differs. Worth
   noting so the L1 does not treat `af962833…` as reproducible from a base-parented clone.

## Restoration and bounds

Scratch clones restored to pristine bytes: `repo` worktree `SCORECARD.md` `7af59cc0…`, `SHONEN.md`
`1ff9e2f3…`, clean; `repo-base` worktree also restored to `SCORECARD.md` `7af59cc0…` (its HEAD is
the scored mutant commit, so it shows one modified file), with scored commits
`af962833…`, `6df2824e…`, `f341be9d…` retained. No tracked lane file, lane index, jj state, fleet
file, `.ufo/state/`, watchdog log or `MANIFEST.json` was written; the only lane writes are this
report and `report.md`. All scratch is under `/tmp/kama-r29-w2-RerunCtlSourceBounds/`.
No tools installed or updated (no pacman; no uv/npx).

## Evidence paths

Recorded: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlSourceBounds/`
(`counter.out`, `receipt.json`, `pristine-*`, `restored-*`, `change.diff`, `predictions.json`,
`correction-rows.md`, `policy-hashes.json`, `source-statements.json`, `source-hashes.json`).
Mine: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/kama-r29-w2-RerunCtlSourceBounds/evidence/`
plus `evidence-manifest.txt`; canonical-format outputs kept alongside the wrapper-format ones
(`canon-*.out`), and `aux-mistaken-pristine-slot-tip-ctl-mutant.out` retained for transparency.
