# N2Couple — round-48 separability (leaf seat)

**Verdict: SEPARABLE.** C1 reaches all five legs alone (`met=True`, exit 0) on a clone at freeze `12284ba39` plus only the C1 build; C2 reaches all seven legs alone (`met=True`, exit 0) on a clone at freeze `12284ba39` plus only the C2 build. The C1 SCORECARD banner append depends on nothing C2 changed: it is byte-exact copies of pre-round-48 commit lines, C2 touched no shared path, and the C1-only fixture reproduces the full-build measured numbers exactly (`files=89 lane_events=5 lane_failures=0 ungraded_lines=89`).

## 1. Paths each counter reads (from the counter code)

C1 `tools/round48-append-audit-v3-check.py` (repo side; read-only):
- `tools/append-only-audit.py` at tip — `show()` L164-166, main L647-653.
- `registry/append-only-contract.tsv` at tip — main L665-673.
- Every path named by contract rows at tip, plus the `declared_at`/region pointer lines: `LOG.md` (declares at `README.md:16`), `SCORECARD.md` (row; pointer line 6), `corpus/QUALITY.md`, `corpus/README.md` (pointer `corpus/README.md:761`), `corpus/SOURCES.md` (declares at `SKILL.md:578`), `corpus/lessons/*.md` (pattern; row declares at `corpus/lessons/round-23.md:100`), `registry/history/DELTA.md` (`:3`), `registry/report-landing-errata.tsv` (`:1`), `corpus/knowledge/consumer-registry.md` (`:30`) — contract leg L140-146, `row_binds` L236-255.
- Git history of `--repo`: `rev-list --topo-order --reverse` (L301+), `rev-parse`, `show <rev>:<path>`, `diff --numstat --no-renames`, `cat-file -e` (stable base `33e00582`, L738).
- Scratch: eleven self-constructed fixture repos.
- Not read: `tools/kama-*`, `.ufo/waves/round-48/c2/live/*`, `prereg-time-check.out`; SOURCES only via its contract row (pattern `*`, so appends are additions, never deletions).

C2 `tools/round48-live-replay-v5-audit.py` (repo side; read-only):
- `.ufo/waves/round-48/c2/live/receipt-{1,2,3}.json` at tip — L143, L378-389.
- `tools/kama-live-replay.py` and `tools/kama-llamacpp-live.py` at tip — `git archive` of the whole tree (L360-375), executed from the extracted tree.
- `corpus/SOURCES.md` at tip (newrow leg, L545-547).
- Network: github.com release asset and huggingface.co model (replay, tamper, urlswap legs).
- Not read: `tools/append-only-audit.py`, `registry/append-only-contract.tsv`, `SCORECARD.md` (present in the archive but unused), `prereg-time-check.out`.

## 2. Build partitions (diff `12284ba39..380bcdff`, 11 paths)

- C1-only: `tools/append-only-audit.py`, `registry/append-only-contract.tsv`, `SCORECARD.md` (+8: banner append).
- C2-only: `tools/kama-llamacpp-live.py`, `tools/kama-live-replay.py`, `.ufo/waves/round-48/c2/live/{install.txt,receipt-1.json,receipt-2.json,receipt-3.json}`, `corpus/SOURCES.md` (+2: S492, S493).
- Neither: `.ufo/waves/round-48/freeze/prereg-time-check.out` (freeze-time control artifact; read by no counter).

No path appears in both partitions.

## 3. Fixtures (commands in `fixture-build.sh`; all in scratch)

- `fdA` (C1-only): `git clone --shared <lane> $S/fdA`; `git checkout 12284ba39…`; `git checkout 380bcdff… -- tools/append-only-audit.py registry/append-only-contract.tsv SCORECARD.md`; commit → tip `08943d8f0071bd691c445c3f7fcc3a4bb236c9a6`. Delta vs freeze matches the C1 partition exactly.
- `fdB` (C2-only): same + `git checkout 380bcdff… -- tools/kama-llamacpp-live.py tools/kama-live-replay.py corpus/SOURCES.md .ufo/waves/round-48/c2/live` → tip `a27a3fcb9ef4b7a3faab0982abba6a3f16462034`. Delta vs freeze matches the C2 partition exactly.
- Toplevel asserted equal to the fixture dir before every commit; identity set per-invocation.

## 4. Results (counters frozen from the lane; clones are read-only inputs)

| Run | Tip | Output | Exit |
|---|---|---|---|
| C1 on fdA | 08943d8f | `selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True` | 0 |
| C2 on fdB | a27a3fcb | `receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True` (started 2026-10-26T22:35:22Z) | 0 |
| C1 on fdB (negative) | a27a3fcb | `met=False`; selftest pass=19 (v2 tool), contract header not v3, fixture leg fail 11 | 1 |
| C2 on fdA (negative) | 08943d8f | `met=False`; receipts absent, newrow no S492 row, v4 live tool rejects `--server-archive` | 1 |
| C1 at freeze | 12284ba39 | `met=False` (before-build control) | 1 |
| C2 at freeze | 12284ba39 | `met=False` (before-build control) | 1 |

C1's measured numbers on the C1-only fixture equal the L1 dry-run at the full build (`files=89 lane_events=5 lane_failures=0 ungraded_lines=89 met=True`): the C1 verdict is unchanged when all C2 changes are removed. C2 passes all seven legs with the C1 build removed.

## 5. Does the C1 banner append depend on anything C2 changed? No.

- The append is `### Superseded head banners (kept verbatim; round 48)` plus two lines at the end of SCORECARD.md (2736-2742). Each appended line is byte-exact (`sha256` match) with line 6 of SCORECARD.md at the pre-round-48 commits `82b5e9d3` (round-45 banner, `01f0f0fa65dee59f…`) and `42ea1204` (round-46 banner, `ee3ce7e2405bdee3…`).
- C2 changed only `corpus/SOURCES.md`, `tools/kama-*`, `.ufo/waves/round-48/c2/live/*` — no overlap with `SCORECARD.md` or any C1 read path (Section 2).
- The C1-only fixture (no C2 changes at all) passes with identical event set and ungraded_lines, so the regressed=1 fix (the r45/r46 banners held again) is achieved without any C2 file.

## 6. Defects

None found. Frozen counters, preregistration and controls untouched; no lane or fleet writes. This seat's runs used only scratch clones (`git clone --shared`) and read-only git on the lane.

Evidence files: `.ufo/waves/round-48/w1/out/N2Couple/` (`sep-c1-only.c1.out`, `sep-c2-only.c2.out`, `cross-c1-on-c2only.c1.out`, `cross-c2-on-c1only.c2.out`, `before-c1-freeze.c1.out`, `before-c2-freeze.c2.out`, `fixture-build.sh`, `read-paths-inventory.txt`, `evidence/receipts/`).
