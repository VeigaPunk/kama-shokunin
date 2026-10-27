# Z02 EvidenceFootprint — round-58 footprint, replay necessity, commit exclusions
Seat Z02EvidenceFootprint (simplifier, advisory). Lane read-only; scratch `/fast/scratch/hyaku/kama-r58/Z02EvidenceFootprint` removed before yield. Attacks: C1/C2 claim text, the counters'
dependency surface, the committed-evidence set at HEAD, and the output set the L1 would commit. `w1/out` grew +190 KB during this seat; every count carries its snapshot.
## 1. Committed evidence (pre-seat-output)
`git diff --shortstat 2f53614e e4891d8a` → `42 files changed, 2125 insertions(+), 1 deletion(-)`. At HEAD, `git ls-tree -r -l` over `.ufo/waves/round-58/ tests/round58-battery-variants
tools/round58*` = 45 files / 355,643 B, of which the 3 dispatch artifacts are 248,862 B (70 %): w1-dispatch.json 152,595 · w1-spec.json 72,227 · build_spec.py 24,040. Substantive evidence =
42 files / 106,781 B: variants 60,062 (15) · tools 22,487 (3) · census 13,302 (2) · controls 10,673 (21) · measured 257 (1) · SCORECARD +1/−1 line (210 B). Repository cost, scratch fixture
after `git gc`: 42 substantive files → `.git/objects` 22,625 B; 45 files incl. spec/dispatch → 55,127 B. One round-58 evidence set costs ≈22–55 KB packed.
## 2. Necessary for independent replay — measured, not assumed
C1: 23 files / 182,710 B = c1-counter 6,419 · checker under test 9,737 · 15 variants 60,062 · round-56 preregistration 3,689 · battery 4,012 · env-leg-test 1,295 · round54-replay-code-audit
47,418 · round56-replay-code-audit 47,530 · controls/freeze.txt 2,548 (provenance; no tool reads it).
Proof of sufficiency: a 25-file / 198,870 B fixture (C1 set + 2 C2 files) replays the frozen result exactly — `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True`, exit 0, 1.16 s
(`Z02EvidenceFootprint/c1-min.out`).
Proof of necessity: same checker over a 2-file fixture (battery + prereg only) → `present=1 roster_match=1 … executed=0 legs=2/3 met=False`, checker exit 1 (`sideprobe.out`) ⇒ the 96,243 B
of SIDE_FILES is load-bearing, not padding.
C2 cannot be packaged at all: the r42 term is tree-global. A 47-file subset (SCORECARD.md + 44 spotchecks + r41 + r42) yields the pointer term 0 but `r42=58 mismatches=58 met=False`
(`c2min.out`). Real C2 replay input = the whole tip tree (`git ls-tree -r -l e4891d8a`) = 32,372 files / 352,918,176 B **plus** fleet blob `941acf…:MANIFEST.json` (2,403,984 B). With
`--fleet-repo` at a repo lacking that rev: `could-not-evaluate: missing SCORECARD, lessons tree or MANIFEST blob`, exit 2 ⇒ the lane-only package is not replayable without the rev pin.
## 3. Wave outputs: measured now, projected to 72 seats
19:58:18Z: `w1/out` = 361 files / 1,844,725 B, 56 reports delivered. Top-level reports mean 3,920 B → 72 ≈ 282 KB of report text. Full-out projection at the observed ratio ≈2.3–2.5 MB /
370–400 files; round-57 precedent was 368 files / 2,401,877 B committed, so committing everything repeats that size. Packed cost, 19:53Z snapshot: 261 files / 1,653,056 B → 302,230
B; reports-only (50 md / 441,853 B) → 167,817 B.
## 4. Should NOT be committed (19:58Z snapshot)
- Scratch/host dumps: 17 files / 907,157 B = 49 % of `w1/out`. `*.strace` 5 files / 187,518 B (the 185,435 B trace opens `/usr/lib/libpython3.14.so.1.0`); `tmp-*-before/after.txt` 10 files /
393,005 B (bare scratch dir entries); `SOURCES.with.md` 256,953 B (whole-file copy for a one-row edit); `swarm-registry.json` 69,681 B (agentId/config state).
- Byte-identical duplicates: 146,479 B in the non-excluded set at 19:58Z, 332,404 B at the earlier 261-file snapshot — 28 copies of one 754 B counter output, 6 of the 13,300 B census
`now.out`, 3 of the 9,737 B checker source.
- `w1-dispatch.json` 152,595 B re-embeds the 4,854-char context, all 72 seat prompts and the registry (`schema=ufo-swarm-wave-dispatch-v1`) ⇒ superset copy of w1-spec.json. Both are produced
by `build_spec.py` from an external `~/.agents/.../directive.md`, so the spec is not byte-reproducible off-host: keep build_spec.py + w1-spec.json (96 KB), drop the dispatch.
- `census/start.out`+`start.exit` 13,302 B: no round-58 tool reads it (`grep -n census tools/round58-*.py controls/*.py` → 0 hits); pre-wave snapshot, not a replay input.
- `controls/*.out`/`*.exit` (18 files / 3,928 B) are regenerable receipts: re-running `always-accept.py` at the build tip reproduced the committed body byte-for-byte, only `tip=` differing,
1.2 s, exit 1. Cheap — keep or regenerate, but they are not replay inputs.
- Host-layout leaks: `X04ScratchHygiene/{c1,c2,checker}-strace-extract.txt`, `commands.txt`, `checker.strace` carry `/fast/scratch/...`; `swarm-registry.json` and `W05LogDraft.md` carry
`/home/vgpnk/.agents|.omp`.
## 5. Commands / exit codes (read-only; only this report + receipts written)
`git diff --shortstat 2f53614e e4891d8a` → 42 files, +2125/−1 (0) · `git ls-tree -r -l e4891d8a` → 32,372 / 352,918,176 B (0) · `git -C /home/vgpnk/Projects/shokunin cat-file -s
941acf…:MANIFEST.json` → 2,403,984 (0) · `c1-counter --repo <25-file fixture> --checker checker.py` → met=True (0, 1.16 s) · `c1-counter --repo <lane> --tip e4891d8a --checker-blob
e4891d8a:tools/…` → met=True (0) · `c1-counter … --checker controls/checkers/always-accept.py` → 0/11 met=False (1) · `c2-counter --repo <lane> --tip e4891d8a --manifest-rev 941acf…` →
mismatches=0 met=True (0) · `c2-counter --repo <subset> --manifest-rev 941acf…` → r42=58 met=False (1) · `c2-counter --repo <subset> --fleet-repo <repo-without-rev>` → could-not-evaluate (2)
· `git gc` in 5 scratch fixtures → packed sizes §1–§3 (0).
## 6. Observations / limits (no claim changed, no counter edited)
- The C2 note in `controls/freeze.txt` is stale against the measured tip: it says "r42 stays 1 until the L1 lands the round-58 SCORECARD section", but `--tip e4891d8a` already gives `r42=0
mismatches=0 met=True`; the r42=1 state lives only in `measured/c2-build.out` (tip bfaea953). The predicate holds at both readings; the expectation sentence is what a reader will mis-verify.
- LIMIT: `w1/out` is a live target; the projection is an interval, not a measurement of the final tree.
- LIMIT: the "42 substantive / 45 total" split is my classification of the HEAD tree; the L1 decides what is committed. No production file was edited and no integration tooling was run.
