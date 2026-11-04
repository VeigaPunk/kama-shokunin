# SCR01Sources — round 74 w1 seat summary

Sourced-claim seat (C3 frontier step): opened the `os-release(5)` registry row and drafted
the `host-block-base-revision.md` knowledge entry. Full evidence, verbatim command output,
quote location, id derivation and census transcript:
`.ufo/waves/round-74/w1/SCR01Sources/report.md`.

Result: **done — staged for L1 append.**

- Id-reuse check: no os-release row in the lane registry (`grep -i 'os-release'
  corpus/SOURCES.md` → no match). Next id derived by parsing the Registry table:
  max = S545 → row drafted as **S546** (`grep -rn 'S546' corpus/` → no dangling use).
- Live fetch 2026-11-04: sha256
  `c7ba68ea45180c33bad72a3b47cf09e3d6d34d0a5313a5acf73a14fc64f8a74e`, retained at
  `.ufo/waves/round-74/w1/SCR01Sources/source/os-release.5.html` (45K).
- Located quote (16 words): "A lower-case string … identifying the operating system,
  excluding any version information and suitable for processing by scripts" — §OPTIONS,
  `ID=` entry, retained HTML lines 187–194.
- Drafts staged at `.ufo/waves/round-74/w1/SCR01Sources/drafts/`:
  `SOURCES-S546-row.md` (kind docs, tier A, scope host-triple distribution component,
  status queued→mined at integration, opened 2026-11-04, recheck 180d, used-by
  `corpus/knowledge/host-block-base-revision.md`) and `host-block-base-revision.md`
  (provenance trio + v2 block grammar: `recorded at <rev>` token, strip-convention
  byte-preservation at rev and tip, append-never-edit, os-release `ID=` grounding).
- Scratch-mirror census gate (routed defect 6 order — census before append):
  `sources-census.sh validate --file <mirror>/corpus/SOURCES.md` → **exit 0**,
  non-warning output identical to the no-S546 baseline, no new W-codes. Live registry
  control run: exit 0 (pre-existing W01/W04 warnings only).
- Real `corpus/SOURCES.md` and `corpus/knowledge/` untouched; scratch dir deleted at
  yield. No git mutations; no frozen tool touched; no tools installed.
- Observation (not a disagreement): the frozen predicate's "byte-identical" is
  implemented with the `recorded at` token sentence stripped, per the Round-73 block's own
  parenthetical at `PROVINCE.md:310`; the counter leg belongs to EX03HostDrift.
