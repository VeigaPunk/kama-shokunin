# kama round 38 fleet report

attempt: 2 (attempt 1 died at watchdog 1293 with no work — refused on the parked worktree, no scratch clone opened; this launch 1294 ran everything)
lane work: scratch clone `/fast/scratch/hyaku/kama-r38`; the parked worktree base left alone on its foreign-identity chain (L0 open)
base: 2a4a97dc890fe393035986c951797c5d65b6cc69 (round-37 verifier spot-check)
tip: d854475aecc1d793f84c10021daaed46f735f270
warnings: 93 (lane baseline; no E findings; census start and end both exit 0)

# Claims

Three claims frozen in `.ufo/waves/round-38/preregistration.json` at `41e149ceee28b24596b5d8567a0ccf43ebbc6d50` before any seat scored. The C2 counter was repaired before data (wave-1 seats reproduced that the `corpus/` prefix was missing and ids were not registry-validated; `PREDICATE` and the measurement-line shape are unchanged and all three failing controls re-ran byte-identically at the base). All three claims measure **met False at base → met True at tip**.

| Claim | Axis, score | Before → after (measured) | Counter | Measured commit |
|---|---|---|---|---|
| C1 — the R36-D2 third sub-fact (R36-D2C) corrected by append | calibration 7 → 7 | `uncorrected 1 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False` (exit 1) → `uncorrected 0 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met True` (exit 0) | `tools/round38-statement-audit.py` | d854475a |
| C2 — coverage map names the two SGLang docs version-pinning entries | coverage 9 → 9 | `named 0 files_exist 0 cited_new 0 met False` (exit 1) → `named 2 files_exist 2 cited_new 3 met True` (exit 0) | `tools/round38-coverage-audit.py` | d854475a |
| C3 — the round-37 counting instruments and the wave's 37th seat report land | operability 8 → 8 | `found 0 base_found 0 help_ok 2 rerun_ok 2 report_37 0 receipt_ok 0 met False` (exit 1) → `found 2 base_found 0 help_ok 2 rerun_ok 2 report_37 1 receipt_ok 1 met True` (exit 0) | `tools/round38-operability-audit.py` | d854475a |

Controls: `.ufo/waves/round-38/controls/c1-noop.out`, `c2-base.out`, `c3-base.out` (all met False, exit 1). After-receipts: `.ufo/waves/round-38/{c1,c2,c3}/after.out`.

# Work performed

- **Inherited round-37 closure** (commit 2f780765, after the freeze): landed `tools/round37-statement-audit.py` and `tools/round37-coverage-audit.py` (round 37 cited both but never committed them), `.ufo/waves/round-37/w1/out/CriticEntries.md` (the 37th seat report; 21012 bytes — the round-37 verifier recorded 20238 bytes at spotcheck:72,196 in the parked worktree; the difference is unexplained), and an enriched `.ufo/waves/round-37/w1/out/seat-exit-codes.json` (37 members, hashes tied to the committed blobs, `rc: null` with reason). Caveat: the round-37 report's "Dead seats: none" closes as **report presence**, not exit status, because per-seat process records were not persisted.
- **R36-D2C correction** (C1): the round-36 Gate's range "it cites S331 to S334" was wrong; the five staged rows citing that entry are S332, S336, S337, S338, S339 (`SOURCES.append.md` lines 9, 13, 14, 15, 16). Appended as a `## Corrections` row in `corpus/lessons/round-38.md`; the r37 lesson and fleet report blobs are unchanged.
- **Assimilation theme** (C2): SGLang documentation version pinning. Two admitted entries: `corpus/knowledge/sglang-docs-version-pinning.md` and `corpus/knowledge/sglang-docs-version-pinning-amendment-2026-10-23.md`; three registry rows S352, S353 (v0.5.22 raw `.mdx` sources; 6243 and 2820 bytes; sha256 in the rows) and S472 (own-work `git ls-remote --tags` inventory; first id free in both the lane registry and the staged package). Staged S360 rejected (GitHub REST `/tags` → HTTP 403 rate limit on this host) with flip: a fetchable anchor. Also rejected: staged `runtime-health-surface-matrix-amendment-2026-10-24-r7.md` (new source S396 duplicates lane S329's URL) and staged `spot-check-protocol.md` (fleet-protocol method). README coverage block added; quarantine slice re-derived (7 kama rows, all `payload-absent`, verdicts unchanged); collision guard re-proven and id lists re-derived.
- **Wave evidence**: one v1 wave of 36 seats (reviewer 8, scout 9, critic 4, scribe 5, executor 5, mutation-tester 3, connector 1, revenger 1); 36/36 seat identities returned reports. Disclosure: the wave payload was dispatched twice from the L1 kernel, so each seat identity ran two instances; both instances' reports were merged, and the wave registry records the 36 `-2` handles. Seat exit receipts: `.ufo/waves/round-38/w1/out/seat-exit-codes.json` (36 members, `rc: null`, report presence recorded).
- **Frontier**: rows 1293–1294 in `.ufo/watchdog.log` (attempts) recorded per `considerthese/2026-10-24.md` proposal 4 (landed as KQ47). Search log: no external web search; all sources opened by direct fetch. Misroot sweep: only the driver's `.ufo/state/kama.report-baseline` changed; no lane files misrooted.
- KQ47 criterion appended to `corpus/QUALITY.md`; PROVINCE round-38 note added (engine-doc re-pin ownership); SCORECARD round-38 section and LOG round-38 entry written.

# Sources

S352, S353 opened 2026-10-25 (HTTP 200) and re-opened in-round by seats (byte counts and sha256 in the Gate); live docs pages read (no version marker; `lastModified` 2026-10-24T12:16:03Z; wording unchanged); S472 run twice by independent executors with byte-identical capture. All rejects carry flip conditions. Attribution: `corpus/lessons/round-38.md` §Gate.

# Mistakes

instrument-not-landed (round 37 counters absent from tip e97ce496; verifier §6 item 1) → C3; dropped-sub-fact (round-37 C1 fixed two of the three D2 sub-facts; the third stood uncorrected; verifier §6 item 4) → R36-D2C row.

# Trends

- calibration: improved. A routed, un-corrected statement is now corrected by append, re-derived by a counter at the tip.
- coverage: improved. Two admitted entries/three rows add coverage the map did not hold; the theme is provenance re-pinning of held rows, not new serving surface.
- operability: improved. The round-37 counting commands are reproducible from landed bytes; the C2 counter now reads source-lines and registry-validates (KQ46, verifier §6 item 5).
- freshness: held at 8. One 90d recheck runs.
- depth, adjacency: held at 7. No capability row enters.

# SHONEN

[~] calibration: R36-D2C appended, C1 met False → met True.
[~] coverage: S352/S353/S472 admitted; S360 + two rejects with flips; C2 met False → met True.
[~] operability: r37 instruments and 37th seat report land; C3 met False → met True.
[~] frontier: one theme, two entries, three rows; mistake mining yielded `instrument-not-landed`; census start/end exit 0.

## Notes

- Boundary: MISSION.md:29 still says operability + freshness; not edited, no duplicate L0 filed (round-35 question stands open).
- Instrument limits disclosed in `corpus/lessons/round-38.md` and the SCORECARD instrument notes (C1 over-credit probes; staged package working-tree bytes; C3 working-tree legs).
- The `KQ46`-narrowed C2 counter is the round-38 instrument; the round-37 counter is unchanged bytes under tools/.
