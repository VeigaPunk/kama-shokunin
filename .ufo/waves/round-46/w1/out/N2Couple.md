# N2Couple — Round 46 separability (C1 freshness ↔ C2 calibration)

**Verdict: Separability holds.** C1's and C2's counters have disjoint read surfaces; a C1-shaped change (b11906 ledger + SOURCES section/row) creates no C2 lane event, and the C2-shaped SCORECARD capability line changes no C1 leg. All counter outputs are bit-identical to baseline modulo the `tip=` hash line (checked with `diff -q <(tail -n +2 ...)`).

## 1. Fixture construction (all under scratch, lane/upstream/fleet untouched)

- Scratch `S=/fast/scratch/hyaku/kama-r46/N2Couple`; one live clone `git clone --quiet --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/fix`, then `git -C $S/fix checkout -q 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050`.
- Guard before any mutation: `git rev-parse --show-toplevel` → `/fast/scratch/hyaku/kama-r46/N2Couple/fix` (GUARD-OK). All later git calls use `-C $S/fix`; commits use inline `-c user.name=n2couple-fix -c user.email=n2couple-fix@invalid -c commit.gpgsign=false` (never global, never outside the fixture).
- Branches:
  - `f0` = 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050 (baseline).
  - `fA` = f0 + **C1-shaped** commit: created `registry/release-recheck-b11906.tsv` (frozen 13-column C1 header + one S037 row, real b11906 blob `b6ebf752…` from upstream, valid machine witnesses) and appended a `## Round-46 release re-verification` section with a `| S486 | … b11906 … 4d71b42f… |` row to `corpus/SOURCES.md` → `b70c89492c00a21ea0e0540a49be7984d43e2863`.
  - `fB` = f0 + **C2-shaped** commit: appended one SCORECARD capability-table line (`| append-only-audit (round 46, C2) | … | 46 |`) → `d784b06d9e2eb4c447220961a6f876c1c1cecabc`.
  - `fAB` = fA + cherry-pick of the fB commit → `c6f4a3fa82cdd0c58f806f254590bae55f089c22`.
- Delta shape: `git diff --stat f0..fA` → `corpus/SOURCES.md | 10 ++++++++++`, `registry/release-recheck-b11906.tsv | 2 ++` (0 deletions anywhere, checked with `git diff f0..fA | grep -c '^-[^-]'` → `0`); `f0..fB` and `fA..fAB` → `SCORECARD.md | 1 +` (0 deletions).

## 2. Paths each counter reads (from counter source; full inventories in paths-c1.txt / paths-c2.txt)

- **C1** (`tools/round46-release-recheck-audit.py`) reads from `--repo`: `corpus/SOURCES.md` @ base (line 308) and @ tip (347), `registry/release-recheck-b11906.tsv` @ tip (314), used-by `corpus/knowledge/*.md` @ tip for valid drifted/removed rows (367–373); from `--upstream`: cat-file on `4d71b42f…` and every pin (307, 312–313), `<pin>:<path>` / `<release>:<path>` blobs and text (220–233).
- **C2** (`tools/round46-append-audit-check.py`) reads from `--repo`: `tools/append-only-audit.py` @ tip (201), the history of the five declared files (SCORECARD.md, LOG.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md) via rev-list/diff/show (106–129), `SCORECARD.md` @ tip (245).
- **Intersection: none.** C1 never reads SCORECARD.md/LOG.md/QUALITY.md/README.md/tools; C2 never reads the registry ledger or corpus/knowledge. The only file object both touch is `corpus/SOURCES.md` — C1 reads its content as data, C2 audits only deletion events in its git history.

## 3. Q1: can a C1 SOURCES.md append create a C2 lane event (≥ 20 deleted lines)? — No

- `python3 $S/fix/tools/round46-append-audit-check.py --repo $S/fix --tip $FA --scratch $S --out $S/a_c2.out` → exit 1 (met=False solely because `table=0`), `lane_events=5 lane_unrestored=0 lane_partial=2`, same five events as baseline (dd9f5dc6 SCORECARD partial 31/24; 0718b6ab SCORECARD partial 2417/2416; 0718b6ab LOG/QUALITY/README restored by 82b5e9d3).
- `diff -q <(tail -n +2 base.c2.out) <(tail -n +2 a_c2.out)` → IDENTICAL.
- Mechanism: the C1-shaped commit deletes 0 lines from the monitored files (grep count 0), and C2's event definition requires ≥ 20 deleted lines per (commit, file) (FILES list, THRESHOLD=20; `recompute` line 116). A pure append can never fire it. The new ledger file is not among the five monitored files. (The C2 counter's own fixture/self-test legs also pass: `selftest=1 fixture=1 lane=1`.)

## 4. Q2: can a C2 SCORECARD edit change a C1 leg? — No

- `python3 $S/fix/tools/round46-release-recheck-audit.py --repo $S/fix --tip $FB --upstream /fast/scratch/hyaku/kama-r46/L1/llama.git --out $S/b_c1.out` → exit 1, `pop=91 rows=0 valid=0 unverified=91 … met=False`; `diff -q <(tail -n +2 base.c1.out) <(tail -n +2 b_c1.out)` → IDENTICAL.
- Stronger: with C1's inputs actually present, `--tip $FA` vs `--tip $FAB` (fAB = fA + the same SCORECARD line): both `pop=91 rows=1 valid=1 unverified=90 reworded=1 section=1 newrow=1 met=False`; `diff -q <(tail -n +2 a_c1.out) <(tail -n +2 ab_c1.out)` → IDENTICAL (S037 re-verifies valid at b11906 in both).
- Mechanism: C1 never reads SCORECARD.md (path inventory §2), so no C1 computation leg can observe it. The C2-shaped edit is a single added line, and the C2 counter's own lane leg still reports the same 5 events; on fB the table leg flips to 1 and the C2 counter exits 0 (`met=True`).

## 5. Environment / tooling

- git 2.56.0, Python 3.14.8; upstream L1/llama.git present and read-only (holds `4d71b42f…` and `d854d98b…`, both `cat-file -t` → commit). No tools installed (nothing to record per RULES.md); no pacman use.

## 6. Findings

- No counter defect found. The only shared substrate is `corpus/SOURCES.md`; separability is structural: C1's claim shape is append-only (0 deletions), and C2's shape touches only SCORECARD.md, which C1's counter never reads. A future C1 edit that *rewrote* SOURCES deleting ≥ 20 lines would legitimately be flagged by C2 — that is C2's designed behavior, not interference.
- Crafting note (evidence for future seats): to satisfy C1's `newrow` leg the new row must match `^\s{0,3}\|\s*S\d{3,}\s*\|` with `b11906` and `4d71b42f…` in the same line — backticking the id (`| `S486` |`) breaks the regex (observed: newrow=0 with backticks, newrow=1 without).
- One harness observation: `bash -e`-style behavior terminates a compound command on the counters' nonzero exits; all rc values in this report were captured via `cmd || rc=$?` guards.

## Absolute paths written
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/N2Couple.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/N2Couple/paths-c1.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/N2Couple/paths-c2.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/N2Couple/base.c1.out, a_c1.out, b_c1.out, ab_c1.out, base.c2.out, a_c2.out, b_c2.out
