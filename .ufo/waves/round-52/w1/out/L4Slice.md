PASS — all 67 restored lines in the seven assigned lesson files have correct deleting-commit attribution; no scoped defect found.

## Evidence

**Scope/contract.** Audited build commit `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8` against round-51 base `9ff76b1f763512be2f554cbbfd0b2213b63b0847`, for `corpus/lessons/round-{16,18,19,25,26,27,28}.md`. The C2 docstring defines the normalized line key at `tools/round52-append-restore-check.py:21-22`, first-parent deletion events at `:35-37`, and the lane/restoration predicate at `:54-62`.

**Per-line attribution audit.** On a single `git clone --shared` at the build commit, ran:

```sh
python3 /fast/scratch/hyaku/kama-r52/L4Slice/audit_slice.py
```

Exit `0`; receipt: `.ufo/waves/round-52/w1/out/L4Slice/audit_slice.out`. It parsed every restored block and verified all 67 lines (not just the 25-line minimum): each block's line multiset exactly equals the lines removed from that file in the named commit's first-parent diff; the block subject matches the commit; each restored line was still absent at base; and each line's SHA-256 and deleting commit agree with the base disclosure ledger. All 15 blocks are unique per file and in history order. Summary: `TOTAL restored lines across 7 files: 67 (expected 67); FAILURES: 0`.

Per-file counts and block attribution (each block count equals the deletion multiset for that commit):

| File | Restored lines | Deleting commit(s), short hash: lines |
|---|---:|---|
| `corpus/lessons/round-16.md` | 11 | `ccc4bb31267f`: 11 |
| `corpus/lessons/round-18.md` | 4 | `1b85a24eca4d`: 1; `f1790e25b421`: 1; `028235e6f28d`: 1; `30ed37837782`: 1 |
| `corpus/lessons/round-19.md` | 6 | `5b108c1a7e94`: 3; `f1790e25b421`: 2; `028235e6f28d`: 1 |
| `corpus/lessons/round-25.md` | 10 | `c0a9b029c035`: 8; `a46a61815f79`: 2 |
| `corpus/lessons/round-26.md` | 17 | `fd48f9a3b7ca`: 17 |
| `corpus/lessons/round-27.md` | 13 | `d183ec572a5e`: 8; `4d2e74f421bc`: 5 |
| `corpus/lessons/round-28.md` | 6 | `9ce5bd377562`: 3; `c23ebaa4883a`: 3 |

**Line sample.** The audit covered every line; a 28-line sample (four from each file, with exact file line, block commit, SHA-256, and line bytes) is in `.ufo/waves/round-52/w1/out/L4Slice/sample-lines.tsv`. Example anchors: round 16 lines 208–211 → `ccc4bb31267f`; round 18 lines 489, 495, 501, 507 → `1b85a24eca4d`, `f1790e25b421`, `028235e6f28d`, `30ed37837782`; round 19 lines 143–144, 151, 158 → `5b108c1a7e94`, `5b108c1a7e94`, `f1790e25b421`, `028235e6f28d`; round 25 lines 155–157, 168 → `c0a9b029c035`, `c0a9b029c035`, `c0a9b029c035`, `a46a61815f79`; round 26 lines 117–120 → `fd48f9a3b7ca`; round 27 lines 175–177, 188 → `d183ec572a5e`, `d183ec572a5e`, `d183ec572a5e`, `4d2e74f421bc`; round 28 lines 207–209, 215 → `9ce5bd377562`, `9ce5bd377562`, `9ce5bd377562`, `c23ebaa4883a`.

**Cross-checks.** At base, the disclosure ledger has respectively `11, 4, 6, 10, 17, 13, 6` rows for these seven files (67 total); each row matched a restored line SHA and the block's deleting commit. Independently counted the fenced restored payloads across the lane's restored sections: `155` lines, matching the frozen C2 scope. Ran the frozen counter read-only against the same clone:

```sh
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round52-append-restore-check.py --repo "$S/lane" --tip 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 --scratch "$S/c2scratch" --out "$S/c2-build.out"
```

Exit `0`; receipt `.ufo/waves/round-52/w1/out/L4Slice/c2-build.out` reports `fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True`.

## Residual risk / verification gaps

This seat's line-level history audit is limited to the seven assigned lesson files; other restored files were not independently attributed here. The official C2 lane run covered the frozen counter predicate. No LSP caller/definition checks were applicable to this Markdown/history-only slice.

## Deliverables

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/L4Slice.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/L4Slice/audit_slice.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/L4Slice/audit_slice.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/L4Slice/sample-lines.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/L4Slice/c2-build.out`
