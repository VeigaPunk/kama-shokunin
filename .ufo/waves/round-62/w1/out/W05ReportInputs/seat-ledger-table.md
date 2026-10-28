| # | Seat | Role | Axes | Milestone | Deliverable under `out/<Seat>/` | Report | At read |
|---|---|---|---|---|---|---|---|
| 1 | `M01C1AttackThe` | mutation-tester | operability | falsify C1 counter | `out/M01C1AttackThe/receipt.json` | `w1/M01C1AttackThe.md` | R+1 |
| 2 | `M02C1AttackThe` | mutation-tester | operability | falsify C1 counter | — | `w1/M02C1AttackThe.md` | R |
| 3 | `M03C1AttackThe` | mutation-tester | operability | falsify C1 counter | `out/M03C1AttackThe/findings.md` | `w1/M03C1AttackThe.md` | R+1 |
| 4 | `M04C1AttackThe` | mutation-tester | operability | falsify C1 counter | — | — | none |
| 5 | `M05C1AttackThe` | mutation-tester | operability | falsify C1 counter | `out/M05C1AttackThe/receipt-pristine.json` | `w1/M05C1AttackThe.md` | R+5 |
| 6 | `M06C1AttackThe` | mutation-tester | operability | falsify C1 counter | — | `w1/M06C1AttackThe.md` | R |
| 7 | `M07C1AttackThe` | mutation-tester | operability | falsify C1 counter | — | — | none |
| 8 | `M08C1AttackThe` | mutation-tester | operability | falsify C1 counter | — | — | none |
| 9 | `M09C2AttackDrop` | mutation-tester | calibration | falsify C2 counter | — | `w1/M09C2AttackDrop.md` | R |
| 10 | `M10C2AttackRename` | mutation-tester | calibration | falsify C2 counter | `out/M10C2AttackRename/M10C2AttackRename.md` | `w1/M10C2AttackRename.md` | R+1 |
| 11 | `M11C2AttackBinding` | mutation-tester | calibration | falsify C2 counter | — | — | none |
| 12 | `M12C2AttackVerdict` | mutation-tester | calibration | falsify C2 counter | — | — | none |
| 13 | `M13C2AttackQuote` | mutation-tester | calibration | falsify C2 counter | — | `w1/M13C2AttackQuote.md` | R |
| 14 | `M14C2AttackFree` | mutation-tester | calibration | falsify C2 counter | — | — | none |
| 15 | `M15C2AttackWeak` | mutation-tester | calibration | falsify C2 counter | — | — | none |
| 16 | `M16C2AttackNotobs` | mutation-tester | calibration | falsify C2 counter | — | — | none |
| 17 | `M17C1ConstDrift` | mutation-tester | operability | falsify C1 counter | — | `w1/M17C1ConstDrift.md` | R |
| 18 | `M18C2ManifestForger` | mutation-tester | calibration | falsify C2 counter | — | — | none |
| 19 | `A01C1PortRace` | critic | operability | falsify C1 live plane | — | `w1/A01C1PortRace.md` | R |
| 20 | `A02C1HoldTamper` | critic | operability | falsify C1 live plane | `out/A02C1HoldTamper/c1-hold-tamper-counter-live-receipt.json` | `w1/A02C1HoldTamper.md` | R+1 |
| 21 | `A03C1WitnessSpoof` | critic | operability | falsify C1 live plane | `out/A03C1WitnessSpoof/receipt.json` | `w1/A03C1WitnessSpoof.md` | R+3 |
| 22 | `A04C1SchemaFuzz` | critic | operability | falsify C1 live plane | `out/A04C1SchemaFuzz/probe-output.txt` | `w1/A04C1SchemaFuzz.md` | R+2 |
| 23 | `A05C2Sensitivity` | critic | calibration | falsify C2 semantics | `out/A05C2Sensitivity/sensitivity-probe.txt` | `w1/A05C2Sensitivity.md` | R+1 |
| 24 | `A06C2Population` | critic | calibration | falsify C2 semantics | — | `w1/A06C2Population.md` | R |
| 25 | `A07C2Template` | critic | calibration | falsify C2 semantics | — | `w1/A07C2Template.md` | R |
| 26 | `A08C2CacheScope` | critic | calibration | falsify C2 semantics | — | `w1/A08C2CacheScope.md` | R |
| 27 | `R01C1Gap` | reviewer | operability,calibration | review gaps | — | `w1/R01C1Gap.md` | R |
| 28 | `R02C2Gap` | reviewer | operability,calibration | review gaps | — | `w1/R02C2Gap.md` | R |
| 29 | `R03ClaimBoundary` | reviewer | operability,calibration | review gaps | — | `w1/R03ClaimBoundary.md` | R |
| 30 | `R04HarmAudit` | reviewer | operability,calibration | review gaps | — | `w1/R04HarmAudit.md` | R |
| 31 | `R05FreezeFidelity` | reviewer | calibration | freeze fidelity audit | — | `w1/R05FreezeFidelity.md` | R |
| 32 | `N01CompletionSecurity` | sentinel | operability | security review | — | — | none |
| 33 | `E01CompletionRepeat` | executor | operability | build & verify | `out/E01CompletionRepeat/derived-2line.stderr.txt` | `w1/E01CompletionRepeat.md` | R+14 |
| 34 | `E02ReceiptGrade` | executor | operability,calibration | build & verify | `out/E02ReceiptGrade/report.md` | `w1/E02ReceiptGrade.md` | R+5 |
| 35 | `E03SelftestsA` | executor | operability | build & verify | `out/E03SelftestsA/E03SelftestsA.md` | `w1/E03SelftestsA.md` | R+4 |
| 36 | `E04SelftestsB` | executor | operability,calibration | build & verify | `out/E04SelftestsB/aoa-selftest.txt` | `w1/E04SelftestsB.md` | R+2 |
| 37 | `E05LedgerScans` | executor | operability | build & verify | `out/E05LedgerScans/digest-scan-details.txt` | `w1/E05LedgerScans.md` | R+10 |
| 38 | `E06FixtureForgery` | executor | operability,calibration | build & verify | `out/E06FixtureForgery/d_synthetic_receipt.json` | `w1/E06FixtureForgery.md` | R+16 |
| 39 | `E07CompletionEdge` | executor | operability | build & verify | `out/E07CompletionEdge/A-edge-t05-np1.json` | `w1/E07CompletionEdge.md` | R+8 |
| 40 | `E08DepsAudit` | executor | operability,calibration | build & verify | — | — | none |
| 41 | `E09ConsumersCheck` | executor | operability | build & verify | `out/E09ConsumersCheck/receipt-proxy.json` | `w1/E09ConsumersCheck.md` | R+11 |
| 42 | `E10CounterAST` | executor | operability,calibration | build & verify | — | — | none |
| 43 | `E11ScratchGuard` | executor | operability | build & verify | — | — | none |
| 44 | `E12KillSwitch` | executor | operability,calibration | build & verify | — | — | none |
| 45 | `L01HostLife` | executor | operability | lane duty | `out/L01HostLife/pass1-a-receipt.json` | `w1/L01HostLife.md` | R+8 |
| 46 | `L02LogTail` | executor | operability | lane duty | `out/L02LogTail/run1-completion-hold.receipt.json` | — | 26f |
| 47 | `L03CensusDelta` | executor | operability | lane duty | `out/L03CensusDelta/census-delta.out` | `w1/L03CensusDelta.md` | R+5 |
| 48 | `L04LessonsSweep` | executor | operability | lane duty | — | — | none |
| 49 | `S01CensusRerun` | scout | coverage | recon & sources | — | `w1/S01CensusRerun.md` | R |
| 50 | `S02LlamaCppSpec` | scout | calibration,freshness | recon & sources | — | `w1/S02LlamaCppSpec.md` | R |
| 51 | `S03FrontierRecon` | scout | coverage | recon & sources | — | `w1/S03FrontierRecon.md` | R |
| 52 | `S04ConsiderThese` | scout | calibration,freshness | recon & sources | — | `w1/S04ConsiderThese.md` | R |
| 53 | `S05SourcesAudit` | scout | coverage | recon & sources | — | `w1/S05SourcesAudit.md` | R |
| 54 | `S06OllamaDoc` | scout | calibration,freshness | recon & sources | — | `w1/S06OllamaDoc.md` | R |
| 55 | `W01LessonDraft` | scribe | calibration | draft artifacts | `out/W01LessonDraft/W01LessonDraft.md` | `w1/W01LessonDraft.md` | R+2 |
| 56 | `W02KnowledgeDraft` | scribe | calibration | draft artifacts | — | — | none |
| 57 | `W03QualityDraft` | scribe | calibration | draft artifacts | `out/W03QualityDraft/probe-output.txt` | — | 1f |
| 58 | `W04ScorecardDraft` | scribe | calibration | draft artifacts | — | — | none |
| 59 | `W05ReportInputs` | scribe | calibration | draft artifacts | — | — | none |
| 60 | `W06FixLog` | scribe | calibration | draft artifacts | `out/W06FixLog/head-docstring.txt` | `w1/W06FixLog.md` | R+9 |
| 61 | `X01SiblingPattern` | connector | calibration | cross-pattern scan | — | `w1/X01SiblingPattern.md` | R |
| 62 | `X02DuplicationCheck` | connector | calibration | cross-pattern scan | — | `w1/X02DuplicationCheck.md` | R |
| 63 | `X03ClaimCov` | connector | calibration | cross-pattern scan | — | `w1/X03ClaimCov.md` | R |
| 64 | `X04ConsidertheseMap` | connector | calibration | cross-pattern scan | — | `w1/X04ConsidertheseMap.md` | R |
