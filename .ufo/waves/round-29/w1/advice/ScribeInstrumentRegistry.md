# ScribeInstrumentRegistry — scoped findings

## Draft behavior
Proposed `.ufo/waves/round-29/w1/out/ScribeInstrumentRegistry/skill-section.md` re-states all five rows in `SKILL.md` §Round-28 instrument registry with `gate`/`probe` kinds, explicitly marks the retired Round-27 C1 counter as `probe` and non-runnable, registers Round-29 C1, and reserves the v2 gate-registry-check row for `ExecGateRegistryV2`.

The logical row fields are the eight listed in `/home/vgpnk/Projects/shokunin/PROTOCOL.md:398-403`. `KamaR29.ExecGateRegistryV2` confirmed its checker accepts the `Kind / entry command` cell shape and requires the command in the same cell as the kind. The draft uses that grouped cell while keeping verdict map, self-test, pinned-value path, write scope, and owner explicit. The older Round-28 table contains five rows at `SKILL.md:1219-1230`; its measurement rows are Round-28 C1 and Round-25 C2. Their opened source contracts report observations, so the proposed kinds are `probe`; explicit old `gate` and `probe` kinds are retained.

## Frozen Round-29 C1 facts
`preregistration.json` C1 (`.ufo/waves/round-29/preregistration.json:8-48`) specifies the command `/usr/bin/python3 .ufo/waves/round-29/count-c1.py --tip refs/heads/master --out <fresh receipt.json>` from a fresh clone with `--repo <clone>`, exit 0 ran / 2 could-not-evaluate, receipt label `unresolved`, counter SHA256 `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`, and freeze commit `827d136546b85059a984b34970f5b493d9a71290`. The requested self-test evidence is the control receipts in `.ufo/waves/round-29/controls/`; `controls/SUMMARY.md` records that no control meets the target and RefPaste does by design.

## Retired and v2 rows
The Round-28 retired row says Round-27 C1 was a miss, never run on data, and superseded for method by KQ37 and the Round-28 qualification; it identifies the original counter SHA and last-run output. The draft makes this explicitly non-runnable rather than inventing a replacement entry command.

The existing gate-registry-completeness row says its check is occurrence-only and does not inspect registry columns. Its base `4179301f` output is `.ufo/waves/round-28/w1/out/ExecGateRegistryCheck/base-4179301.out`. A field-set message was sent to `KamaR29.ExecGateRegistryV2`; the executor replied that its checker accepts a combined `Kind / entry command` cell and requested the exact Round-29 C1 row for checker review. That exact row is in `skill-section.md`. The v2 row itself remains marked for that executor to supply.

## Scope and limits
Static reading and drafting only. No tracked lane file, git/jj state, build/test/gate, model server, or runtime was touched. No tool was installed. The draft does not claim that any counter or gate was rerun. The Round-28 v1 gate row does not state a self-test command; this omission is recorded rather than guessed.

Artifacts:
- `.ufo/waves/round-29/w1/out/ScribeInstrumentRegistry/skill-section.md`
- `.ufo/waves/round-29/w1/out/ScribeInstrumentRegistry/REPORT.md`
- `.ufo/waves/round-29/w1/advice/ScribeInstrumentRegistry.md`
