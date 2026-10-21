# MutProbeSensitivity — L1 probe detector sensitivity

## Scope and axes

Axes: **C1 calibration / detector sensitivity (axis 7)**, **operability / exit specificity (axis 8)**, and exact restoration/isolation. This tests the assigned `/tmp/kama-r23-probe/probe.sh`, not a proposed auditor fix. No contract change or integration was made.

**Result:** the printed-output oracle distinguishes **6/9** single-point mutants; **3/9 survive**. The script's own exit-status oracle distinguishes **0/9**: pristine, all mutants, and all restores exit **0**. Most importantly, **F6 does not change at all when `log.follow` is disabled**. F3/F4 also have surviving missing-premise mutants. These are coverage findings, not proof that their underlying Git behaviors are absent.

## Method and evidence

- Isolated checkout: `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r23/MutProbeSensitivity`; observed HEAD `4fe9339f8fc3a4a4a479d9c938a850da12f1124d`, audit blob `fcc255ce5115a749dfbd09cf992ba9851a2dc90a`.
- Copied the probe byte-for-byte to `/tmp/kama-r23/MutProbeSensitivity/mutation-probe.sh`. Changed only one fixture operation/value at a time; restored exact bytes after each mutant and reran the same complete probe.
- Command for each observation: `python3 record-mutation.py LABEL`, cwd `/tmp/kama-r23/MutProbeSensitivity`; it runs `bash /tmp/kama-r23/MutProbeSensitivity/mutation-probe.sh` with `AUDIT=/tmp/kama-r23/MutProbeSensitivity/tools/report-landing-audit.py` and a 60-second process-group deadline. All 19 observations completed; no timeouts.
- Environment is explicitly constructed, not inherited: `/usr/bin:/bin`, UTF-8 locale, UTC, scratch HOME, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, fixed fixture identity and dates. The fixed identity supplies F3's otherwise-unconfigured `commit-tree` identity. No environment values or credentials were inspected.
- Fresh fixture repositories are those created by the unmodified probe under `/tmp/kama-r23-probe/run.*`; each run has its own root. The SSH fixture retains only `example.invalid` and the existing local `touch ...; false` marker command.
- Tools observed: Git **2.56.0**, Python **3.14.8**, Bash **5.3.20**. No installs/updates.

Evidence directory, abbreviated **OUT** below:
`.ufo/waves/round-23/build/out/MutProbeSensitivity/`.

`OUT/runs.jsonl:1-19` retains each exact probe snapshot, hashes before/after execution, command/environment, complete wrapper output, individual audit stdout/stderr, parsed observations, actual marker presence, and fresh fixture root. Triplets in the table are **pristine-before / mutant / exact-restored** JSONL line numbers. The previous restoration is the next mutant's pristine baseline.

**Display oracle:** compare complete probe stdout after replacing only its final random `T=...` line, plus wrapper stderr/exit. Audit JSON comparisons exclude the fresh report pathname by using the recorded observation fields. A “killed” result below means an emitted-output difference, **not** an assertion or failure supplied by the probe itself. Baseline reproduction succeeded: the frozen auditor emitted the expected known-fault signatures; the auditor's intentional fault exits are not mistaken for harness baseline failures.

## Mutants, expected detectors, and observed outputs

All source lines below refer to `/tmp/kama-r23-probe/probe.sh`, identical to the restored scratch copy.

| Mutant / source | Smallest changed behavior | Expected detector | Actual pristine → mutated → restored | Display verdict / evidence |
|---|---|---|---|---|
| M1, F1, `:39` | `ISO-8859-1` → `UTF-8` | Lose the decoding-crash signature | `f1-logenc exit=1`, `UnicodeDecodeError` byte `0xe9` → `exit=0`, `defects [] required 1 cutoff 2000` → original crash | **Killed**, JSONL **1/2/3** |
| M2, F2, `:41` | Invalid `\xff\xfe` payload → valid ASCII payload | Lose the report-decoding crash | `f2-report-bytes exit=1`, `UnicodeDecodeError` byte `0xff` → `exit=0`, `defects [] required 1 cutoff 2000` → original crash | **Killed**, **3/4/5** |
| M3, F3, `:43` | Omit only `git ... replace "$X" "$Y"` | Previously hidden omission becomes visible | `exit=0`, `defects [] required 1` → `exit=1`, `defects [('landed-omitted', '4312b0a58238')] required 2` → original clean result | **Killed**, **5/6/7** |
| M4, F4, `:45` | Omit only the fabricated replacement `update-ref` | Fake citation becomes unresolved | `exit=0`, `defects []` → `exit=1`, `unresolved-full-hash` plus `landed-unresolved` for `1234567890ab...` → original clean result | **Killed**, **7/8/9** |
| M5, F5, `:48` | `FAKE2=<missing hash>` → `FAKE2=$LC` | Remove missing-object fetch trigger and marker | `exit=1`, two unresolved-citation defects, `MARKER CREATED (command executed)` → `exit=0`, `defects []`, `no marker` → original failure/marker | **Killed**, **9/10/11**; actual marker true → false → true |
| M6, F6, `:51` | `config log.follow true` → `false` | A claimed follow-dependent cutoff should differ | **All three:** `f6-follow exit=0`, `defects [] required 1 cutoff 2000`; entire normalized probe output unchanged | **Survived**, **11/12/13** |
| M7, F3, `:43` | Omitted commit subject `round-1: more` → `unrelated more` | Missing required-round-commit premise should be distinguishable if the probe establishes it | **All three:** `f3-replace-omit exit=0`, `defects [] required 1 cutoff 2000`; entire normalized output unchanged despite no omitted qualifying round commit | **Survived**, **13/14/15** |
| M8, F4, `:45` | Omit only the `printf` that adds the fabricated citation | Missing fabricated-citation premise should be distinguishable if the probe establishes it | **All three:** `f4-replace-fake exit=0`, `defects [] required 1 cutoff 2000`; entire normalized output unchanged despite no fabricated citation to resolve | **Survived**, **15/16/17** |
| M9, F5, `:49` | Check `"$M.wrong"` instead of `"$M"` | Marker report changes when its observation path is broken | `MARKER CREATED (command executed)` → **`no marker`** → original marker message. Audit still `exit=1` with the same two defects. Independent actual marker check is **true in all three**, wrong path absent | **Killed by display only**, **17/18/19**; demonstrates a false-negative marker report |

Across all 19 runs the control remained exactly `exit=0`, `defects [] required 1 cutoff 2000`. Every restoration's complete normalized probe output equals the initial pristine output. No triplet is inconclusive under the declared display oracle.

## Which cases fail to establish their own exercise?

1. **F6 is insensitive to its named fault.** Turning `log.follow` off does not change even the printed cutoff, much less the verdict. Do not count this recipe as evidence of a follow-dependent cutoff or verdict difference. The recipe already commits the report at its final path in `base()` (`:23-24`) before moving it out/back (`:51`); the frozen cutoff implementation returns the oldest addition (`tools/report-landing-audit.py:165-168`). No replacement fixture was designed or substituted here.
2. **F3 and F4 have premise-observability holes.** Their actual replacement operations are falsifiable (M3/M4), but a clean printed result is also obtained when there is no omitted round commit (M7) or no fabricated citation (M8). Their summary alone cannot prove those premises were exercised. This is narrower than calling every aspect of either fixture unfalsifiable.
3. **F5's negative marker message is not execution evidence.** M9 prints `no marker` while the real marker exists. Audit exit/JSON alone also cannot detect this observer defect; only the display changes. M5 does show sensitivity to the missing-object trigger. Neither result licenses treating any arbitrary `no marker` as proof of nonexecution.
4. **As an executable pass/fail detector, the whole probe is unfalsified by all nine mutants.** It has `set -u`, not fixture assertions (`:3`); `run()` prints audit status and a JSON summary (`:26-35`); the final successful `echo T=$T` (`:52`) returns zero. All measured wrapper exits are zero. A caller checking only shell success would miss every mutant, including those whose output changed.

These findings apply to this exact probe/frozen-auditor pair, not to a subsequently revised assertion harness or auditor.

## Hashes and exact restoration

Original probe and every pristine/restored scratch probe SHA-256 (**P**):
`3e9a6e4daae3a634be19e0a6705591cd85dacedc06965ef7c2e57b37ffb1221a`.

Each row is **P → mutant hash → P**; hashes before and after each individual execution also match.

| Mutant | Mutated probe SHA-256 |
|---|---|
| M1 | `a75ca49d7356dab43afbe691a3bfe672419827d15b8b77ba0f0492ca70c8696c` |
| M2 | `36df739b60ba29a6cc82924c57bf2bd59c9f8cb700dfd7d25392da35723dd5b5` |
| M3 | `1c0d4123dc9cafe8a1971454f750327664df63c2039695039dc522ab29dd36ec` |
| M4 | `1032768e45b952fabb2171166707a3631f001586fba610e908672a5f9f75b59b` |
| M5 | `fe89671f4b86903bc6d64ab4c7c18f65394cdc3d53df0c4a6b211c278419a496` |
| M6 | `ad13156b824a5536e8c68f8049676b421ffa5caf11dbf34dad0eb0f79e17c4f8` |
| M7 | `271e46affeca003801c01ae433c5669a9b6a671ed4dadfe08de516bbdf67fd60` |
| M8 | `619df5e61afa0d3279dc342e422e13569eff42424b00bc455fae1920132936f3` |
| M9 | `75a3b2dc86b676fd878f2243251993abfe5397455be5b1eee084bf9410e83c29` |

Final `sha256sum /tmp/kama-r23-probe/probe.sh mutation-probe.sh tools/report-landing-audit.py record-mutation.py OUT/runs.jsonl` observed the original and restored probe both equal **P**; auditor unchanged at `09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f`; recorder `424753979591d64fb27142cc74e64ab13e6ab24708b788db08b041f2180332b2`; evidence JSONL `a4c587281142954d0633492bd579b6e33c58f1373803e270ef2b717276b56c7b`.

## Files written and limits

Authored files:
- `/tmp/kama-r23/MutProbeSensitivity/mutation-probe.sh` — exact-restored probe copy.
- `/tmp/kama-r23/MutProbeSensitivity/record-mutation.py` — observation recorder.
- `OUT/record-mutation.py` — identical exported recorder.
- `OUT/runs.jsonl` — append-only 19-run evidence, including every pristine/mutated/restored probe snapshot.
- `OUT/comparison.txt` — recorded comparison results.
- `.ufo/waves/round-23/build/advice/MutProbeSensitivity.md` — this report, written once.

The clone and fresh Git fixture trees were also generated; their roots are recorded per observation in `runs.jsonl`. No lane tracked file, lane index, sibling source, original probe, global config, or domain source was modified. No commits/pushes/jj commands, subagent dispatch, or REA devices.

**Not verified:** proposed/current hardened auditor, existing 50-case selftest, historical rounds 10–22, alternate Git versions/locales, a repaired F6 recipe, or actual network behavior. No general repository-hardening conclusion. Only the assigned local mutation probe was exercised.

Report: .ufo/waves/round-23/build/advice/MutProbeSensitivity.md
