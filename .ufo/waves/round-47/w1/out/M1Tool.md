# M1Tool — round 47 C1 tool mutation test (`append-only-audit.py` v2)

**Verdict: 33 mutants on the C1 tool at 3a09a1d — 22 killed by the tool's own selftest, 3 killed by the frozen counter, 5 equivalent, 3 survived (B2, K2, S1) with proposed selftest cases; the claim's calibration is not contradicted.**

## Scope
C1 (calibration, 7->7) tool `tools/append-only-audit.py` at lane commit `3a09a1d93dcc16799cf6c4b48786e6440af134c4` (frozen tool blob `9442eb8c47a7cb75c9562ed72c1c640b359de8a4`; identical to the working-tree file). Frozen counter `tools/round47-append-audit-v2-check.py` (sha256 `a180ab84cc642731a6bd5fca92e5218dfaa6c074279e2f001110b348d73755ed`, matches preregistration). Baseline reproduced: pristine tool selftest `pass=15 fail=0` exit 0; counter at tip: `selftest=1 contract=1 lane=1 fixture=1 stable=1 files=85 lane_events=5 lane_mismatch=0 fixture_mismatch=0 met=True`, exit 0 (matches the pre-wave dry run).

## Method
1. Mutant sources generated from the pristine tool by single-anchor edits (each anchor asserted unique); 33 mutants across the 12 requested areas.
2. Per mutant: direct `python3 <mutant> --selftest --scratch $S/st/<id>`; then a fixture clone of the lane at `3a09a1d` (`git clone --shared --no-checkout $S/lane $D`, `git checkout -q 3a09a1d`, toplevel asserted `== $D` before the first commit), the mutant written to `tools/append-only-audit.py`, committed with fixture identity (`GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=fixture@kama.invalid GIT_COMMITTER_*=fixture GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`); then the frozen counter `python3 tools/round47-append-audit-v2-check.py --repo $D --tip <mutant commit> --scratch $S/ctr/<id>`.
3. Classification: **killed-by-selftest** if the mutant's own `--selftest` fails (fail>0 or exit!=0); else **killed-by-counter** if counter `met=False`; else **equivalent** (counter met=True and lane JSON byte-identical to pristine); else **survived** (counter met=True and a behavior divergence demonstrated). Survivors were cross-checked with standalone repro repos.

No tools installed (system `python3` 3.14.8, `git` 2.56.0 used; no pacman/uv/npx actions needed). Lane and fleet repos read-only; all work under `S=/fast/scratch/hyaku/kama-r47/M1Tool`; fixture clones removed after each run.

## Results (per area)
| area | mutants | killed-by-selftest | killed-by-counter | equivalent | survived |
|---|---|---:|---:|---:|---:|
| hunk parse | H1–H7 | H3 H4 H5 H7 | H1 H2 | H6 | — |
| byte vs text | B1–B3 | B1 B3 | — | — | B2 |
| final-segment rule | S1 | — | — | — | S1 |
| K subtraction | K1 K2 | K1 | — | — | K2 |
| window start | W1 W2 | W1 W2 | — | — | — |
| max vs last | Mx1 Mx2 | Mx1 Mx2 | — | — | — |
| restored_by break | R1 R2 | R1 R2 | — | — | — |
| status thresholds | St1–St4 | St1–St4 | — | — | — |
| numstat equality | N1–N3 | N1 N2 | — | N3 | — |
| contract parse | C1–C3 | — | C1 | C2 C3 | — |
| fnmatch expansion | F1 F2 | F1 | — | F2 | — |
| exit code | E1 E2 | E1 E2 | — | — | — |
| **total** | **33** | **22** | **3** | **5** | **3** |

Full per-mutant table with selftest pass/fail, counter header line and classification: `M1Tool/results.tsv`. Every counter run used the mutant commit as `--tip`, so the counter always exercised the mutant's code (extracted via `git show <tip>:tools/append-only-audit.py`); none of the mutants altered `SCHEMA` or introduced the string `round47` (lane-leg independence check unaffected).

Representative killed-by-counter evidence (selftest passes, counter `met=False`):
- **H1** (hunk regex requires comma counts): counter `selftest=1 contract=0 lane=0 fixture=0 stable=0 … met=False`, `detail: lane: tool exit=2, stdout is not one JSON object` (AuditError `hunk count != numstat` on bare `@@ -N +N @@` hunks) — `runs/H1.counter.out`.
- **H2** (absent hunk count → 0): same shape — `runs/H2.counter.out`.
- **C1** (contract split on whitespace): counter `… contract=0 lane=0 … met=False` — `runs/C1.counter.out`.

## Survivors (findings) — defect, evidence, proposed selftest case
All three pass the 15-case selftest and the full counter (`met=True`); each changes observable behavior on crafted inputs. Repro evidence: `findings/repro-evidence.txt`; proposed cases (each validated: PASS on pristine, FAIL on the mutant) in `findings/proposed_cases.py`.

### B2 — `split_lines` uses `bytes.splitlines()` (defect: `tools/append-only-audit.py:111`)
`data.splitlines()` strips a trailing `\r` from CRLF lines, so a deleted CRLF line restored **byte-exact as CRLF** never matches D (D keeps the `\r`); the existing `crlf-and-eof` case only asserts an LF copy does *not* count, never that an exact CRLF copy *does*. Repro (event `54843519`, 21 deletions): pristine `deleted=21 restored_max=21 status=restored`; B2 `deleted=21 restored_max=20 status=partial`. Proposed case: `t_crlf_restore_exact` (CRLF deleted in a ≥20 event, restored byte-exact → must be restored 21/21).

### K2 — `K = D - r.lines(pb)` (defect: `tools/append-only-audit.py:206`)
Reversed K subtraction; `collections.Counter` subtraction zeroes negatives, so the kept copies of a triplicated deleted line are lost from K and the still-present kept copy is credited as a restoration. The existing `multiset` case covers delete-3-restore-1, not delete-2-keep-1. Repro (event `9749cfd6`, 22 deletions: 20 plain + 2 of 3 trip copies; 1 copy kept): pristine `restored_max=0 status=unrestored`; K2 `restored_max=1 status=partial`. Proposed case: `t_dup_kept_not_restored`.

### S1 — trailing-empty segment kept (defect: removal of `tools/append-only-audit.py:112-113`)
Without the pop, any blob ending in `\n` carries a phantom empty line; when an empty line is among D and the audited tip/final-line newline state differs from the parent's, `held` credits the phantom. No existing case deletes an empty line at all. Repro (event `4920d880`, 22 deletions incl. a blank line, file flips to trailing newline): pristine `restored_max=1`; S1 `restored_max=2`. Proposed case: `t_split_lines_final_segment` (unit check of the v2 line-splitting definition: `split_lines(b"a\n\n") == [b"a", b""]`, `split_lines(b"a\r\n") == [b"a\r"]`, etc.).

## Equivalents (5) — no observable divergence found
- **H6** (hunk loop stops after nd deletions): git unified hunks order `-` lines before `+` lines, so the deletion collection is unchanged.
- **N3** (numstat-equality raise removed): the counter's own recomputation raises on any such mismatch (exit 2), so the mutant cannot survive mismatched data; on matching data behavior is identical.
- **C2** (declared_at validation dropped), **C3** (note dropped): only exercised on contracts the counter already rejects / fields never read downstream.
- **F2** (expansion returned unsorted): the `files` list came out sorted in all 14 probes (8 default runs + 6 `PYTHONHASHSEED` variations); flagged as a theoretical determinism risk only, since it depends on set-iteration order.

## Notes
- The 3 survivors are all cases the frozen counter's random fixture generator cannot produce: it deletes 1-of-3 trip copies (never 2), restores an LF copy of CRLF (never an exact CRLF copy), and never deletes an empty line.
- All counter runs printed `files=85 lane_events=5` (the lane's frozen expectation) except where the tool could not evaluate; per-mutant detail lines are in `runs/` and `results.tsv`.

## Files written
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/M1Tool.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/M1Tool/results.tsv` (full 33-row classification)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/M1Tool/mutants/` (33 mutant sources + unified diffs + meta)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/M1Tool/findings/proposed_cases.py`, `findings/repro-evidence.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/M1Tool/runs/` (representative counter receipts)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/M1Tool/contract-at-tip.tsv`, `tool-blob-hash.txt`
