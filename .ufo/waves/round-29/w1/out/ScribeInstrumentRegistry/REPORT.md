# ScribeInstrumentRegistry report

## Behavior
Drafted an appended Round-29 SKILL registry section. It re-states all five Round-28 registry rows with `gate`/`probe` kinds, explicitly marks the retired Round-27 counter `probe` and non-runnable with its retirement reason, and registers Round-29 C1 with the preregistered command, exit map, `unresolved` label, full counter SHA256, and the control-receipt location. A v2 gate-registry-check row slot is reserved for `ExecGateRegistryV2`.

The draft carries all eight logical fields read from `/home/vgpnk/Projects/shokunin/PROTOCOL.md` §Gate standard, lines 398–403: name, kind, entry command, verdict map, self-test command and spelling, pinned-value path, write scope, owner. Kind and entry command are grouped in one `Kind / entry command` cell to match the v2 executor's stated checker shape; the remaining fields are explicit. Round-28 measured counters are classified as probes because their recorded contracts report observations (Round-28 C1 exits 0 for any count; Round-25 C2 exits 0 whenever its receipt parses). These classifications are based on the opened counter source and registry rows.

## Gates and verification
No gate, build, test, linter, formatter, or runtime was executed. Static source reads only. The count-C1 self-test evidence requested for the draft is the control receipts under `.ufo/waves/round-29/controls/`, summarized by `controls/SUMMARY.md`; this report does not claim a new self-test run. The Round-29 C1 control summary states no control meets the target and RefPaste meets it by design.

## Touched surfaces
- Created `.ufo/waves/round-29/w1/out/ScribeInstrumentRegistry/skill-section.md` (proposed text only; no tracked `SKILL.md` edit).
- Created `.ufo/waves/round-29/w1/out/ScribeInstrumentRegistry/REPORT.md`.
- Created `.ufo/waves/round-29/w1/advice/ScribeInstrumentRegistry.md`.

## Out of scope
No lane or fleet git/jj writes; no tracked lane-file edits; no sibling-lane, manifest, state, or watchdog access; no llama-server; no tool installation. The v2 gate row's final command, verdict map, self-test, pin, and scope are not supplied here: the row is explicitly reserved for the named executor.

## Findings and known limits
- The Round-28 section has five rows: request-field outcomes, retired Round-27 C1, Round-25 C2, gate-registry completeness, and echo recheck. Its two `measurement:` counters were mapped to `probe`; prior explicit `gate`/`probe` kinds were retained.
- The retired Round-27 row is marked non-runnable because its recorded C1 was a miss, never run on data, and was superseded for method by KQ37 and the Round-28 qualification.
- Round-29 preregistration C1 specifies exit 0 ran / exit 2 could-not-evaluate, receipt label `unresolved`, command `/usr/bin/python3 .ufo/waves/round-29/count-c1.py --tip refs/heads/master --out <fresh receipt.json>` from a fresh clone with `--repo <clone>`, and counter SHA256 `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`. Its frozen commit is `827d136546b85059a984b34970f5b493d9a71290`.
- The Round-28 gate-registry-check row records an occurrence-only check and says it does not inspect columns. Its output at base `4179301f` reported the Round-25 C2 and Round-27 C1 paths as unregistered.
- Static search for `--selftest`, `--self-test`, `selftest`, and `self-test` found no matches in the Round-29 C1, Round-28 C1, Round-25 C2, or echo-recheck sources. The Round-29 draft names the required control-receipt evidence without inventing a CLI spelling. No runtime behavior was re-tested.
- `KamaR29.ExecGateRegistryV2` replied that the v2 checker accepts the Round-28 `Kind / entry command` table shape and requires a row's kind and command in the same cell. The proposed Round-29 C1 row now uses that shape while keeping the other logical PROTOCOL fields distinct. The executor requested its exact row for checker review; the row text appears in `skill-section.md`. The reserved v2 row remains for that executor to complete.

## Provenance and actions
Opened: `preregistration.json` (C1 lines 8–48); Round-28 lesson routed defect 5 (lines 220–238); `SKILL.md` Round-28 registry (lines 1219–1230); `PROTOCOL.md` §Gate standard (lines 380–417); Round-29 counter docstring (lines 1–47); Round-28 and Round-25 counter headers/exit contracts; `tools/gate-registry-check.py` header/contract; `tools/echo-recheck.py` header/contract; controls `SUMMARY.md` and `RefPaste/REPORT.md`.

Directory setup command: `timeout 10 mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeInstrumentRegistry /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/advice` — tool returned no output. No tools were installed or updated.

## Artifact paths
- `.ufo/waves/round-29/w1/out/ScribeInstrumentRegistry/skill-section.md`
- `.ufo/waves/round-29/w1/out/ScribeInstrumentRegistry/REPORT.md`
- `.ufo/waves/round-29/w1/advice/ScribeInstrumentRegistry.md`
