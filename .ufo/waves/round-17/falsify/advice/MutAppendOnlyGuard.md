VERDICT: partial — the guard grades S041 correctly (b8e485c→ccc4bb3 exit 1, S041 `anchor`+`teaches`) and its `--selftest` kills 4 of 7 mutants, but two genuine mutants survive both the selftest and every real commit pair: M3a silently drops the `opened` cell from comparison, M4b silently drops every row after the first blank line in the registry section.

## What I attacked

`tools/sources-append-only.py` at lane commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3`, sha256 `c477a172cd5ae1512a9f75456da216a7df8cfde1df7c28fd09e60b76054b1e05` (same object as `git show 54a2926:tools/sources-append-only.py`; matches `SentinelSeatWrites.md:5`). Baseline instrument: that file, unmodified, run in a `/tmp` clone.

Contract under enforcement: `CORPUS.md:116` — "Only `status`, `recheck` and `used-by` change in place"; `corpus/QUALITY.md:123` KQ22 — "Registry cells other than `status`, `recheck` and `used-by` stay byte-identical from a row's first commit… shown able to fail on `--from b8e485c --to ccc4bb3` (exit 1, S041 `anchor` and `teaches`)". Round claim resting on it: `corpus/lessons/round-17.md:74-76` — "No `status`, `recheck` or `used-by` cell of an existing row changed, and no immutable cell of any row changed (`tools/sources-append-only.py`, §Measurements)."

Registry shape at `ccc4bb3:corpus/SOURCES.md`: `## Registry` line 9, **blank line 10**, header 11, separator 12, 41 rows 13–53, blank 54, `## Paths` 55. The blank line immediately after the heading is what decides the M4a/M4b split below.

## Baseline (unmodified tool)

| command | rc | output |
|---|---|---|
| `python3 tools/sources-append-only.py --selftest` | 0 | 14/14 cases passed |
| `--from b8e485c --to ccc4bb3` | **1** | `VIOLATION S041: cell \`anchor\` changed in place` + `VIOLATION S041: cell \`teaches\` changed in place`; "1 append-only violation(s)" |
| `--from cff9e62 --to 54a29268…` | 0 | `added S042`…`S046`; "no append-only violations" |

Round-17 has exactly one commit touching `corpus/SOURCES.md` (`git log cff9e62..54a2926 -- corpus/SOURCES.md` → `54a2926` only), so those two pairs are the whole real gate surface.

## Mutants (each a separate copy under `/tmp`; one edit per copy)

| # | mutation | site | `--selftest` | S041 pair | round pair |
|---|---|---|---|---|---|
| M1 | `teaches` moved into `MUTABLE_CELLS` | `:43` | **rc1, 13/14** — `FAIL: teaches change (want exit 1 ids ['S001'], got exit 0)` | rc **1**, but only `anchor` flagged | 0 |
| M2 | removed rows skipped (`if new is None: continue`) | `:177-179` | **rc1, 13/14** — `FAIL: removed row (want exit 1 ids ['S002'], got exit 0)` | rc 1, `anchor`+`teaches` | 0 |
| M3a | immutable columns taken from `header[:8]` (first 8 columns) | `:172` | **rc0, 14/14 — not noticed** | rc 1, `anchor`+`teaches` | 0 |
| M3b | immutable list truncated `[:8]` | `:172` | rc0, 14/14 | rc 1, both | 0 |
| M3c | `header[:8]` compared ignoring mutability | `:172` | **rc1, 13/14** — `FAIL: status-only change (want exit 0, got exit 1 ids ['S001'])` | rc 1, both | 0 |
| M4a | parser breaks at the first blank line | `:116-118` | **rc1, 3/14** — 11 cases `got exit 2` | rc **2** | rc 2 |
| M4b | parser breaks at the first blank line *after the header* | `:116-120` | **rc0, 14/14 — not noticed** | rc 1, both | 0 |

Effective compared sets (introspected from the mutant modules, header `id,source,kind,tier,scope,anchor,teaches,status,opened,recheck,used-by`):

- base: `['source','kind','tier','scope','anchor','teaches','opened']` (7)
- M3a: `['source','kind','tier','scope','anchor','teaches']` — **`opened` is gone**
- M1: `['source','kind','tier','scope','anchor','opened']` — `teaches` gone
- M3b: identical to base. The immutable list has only 7 entries, so `[:8]` can never truncate: under the "first 8 columns *of the immutable list*" reading the mutation cannot be expressed, and M3b is a null mutant (SAME on all 10 historical pairs and all 14 synthetic probes). The reading that bites is M3a/M3c: **header positions 1–8**.

## Survivors (noticed by neither surface)

Synthetic two-commit repos under `/tmp/MutAppendOnlyGuard-synth` (single cell changed on S001; base rc / mutant rc):

| probe | base | M3a | M4b | M1 | M2 |
|---|---|---|---|---|---|
| `opened` 2026-10-19→2026-10-20 | 1:`opened` | **0 — accepted** | 1 | 1 | 1 |
| `teaches` rewritten | 1:`teaches` | 1 | 1 | **0 — accepted** | 1 |
| S002 row removed | 1:`removed` | 1 | 1 | 1 | **0 — accepted** |
| second table block, S002 removed from block 2 | 1:`removed` | 1 | **0 — accepted** | 1 | **0** |
| second table block, S003 added to block 2 | 0, added `S003` | same | **0, added list empty** | same | same |
| `kind`/`tier`/`scope`/`anchor`/`source` rewritten | 1 | 1 | 1 | 1 | 1 |
| `status`/`recheck`/`used-by` rewritten | 0 | 0 | 0 | 0 | 0 (M3c, not tabled here, returns **1 — false positive**) |

1. **M3a survives the selftest and both real pairs.** Root cause: the selftest never rewrites `opened` — it appears only as `_row()`'s default parameter (`:274`) and is never passed as a case argument (`:295-380`). Of the 7 immutable cells, cases exercise only `source` (`:371`), `anchor` (`:350`), `teaches` (`:306`); `opened`, `kind`, `tier`, `scope` have no case. The truncation removes exactly the one immutable cell the fixtures never disturb. KQ22 says *all* cells other than the three mutable ones stay byte-identical, so an in-place `opened` edit would pass the landed guard and the round claim at `round-17.md:74-76` would be false in that dimension.
2. **M4b survives the selftest and both real pairs.** The registry at `ccc4bb3`/`54a2926` is one table block, so stopping at the first blank line after the header is observationally equivalent on today's corpus and on all 10 historical pairs. Any future appended block separated by a blank line (a "Round-19 additions" table, or a row block split by a paragraph) is then parsed by neither the added-row list nor the removed/cell checks while the census (`sources-census.sh`, awk over all rows) still sees it. Latent, but it is an acceptance path, not a rejection path.
3. **M1 survives the S041 exit code but not the selftest.** `--from b8e485c --to ccc4bb3` still exits 1 because `anchor` remains compared, so KQ22's sentence "exit 1, S041 `anchor` and `teaches`" is only half-honoured: the violation list loses `teaches`. A reviewer accepting the exit code (as the KQ22 text invites) would not see it; only `--selftest` kills this mutant. M1 is the only mutant whose real-history difference is a *lost detection*: on `726f737..ccc4bb3` it drops `teaches` from the S041 violation (M3c's difference is a false positive, M4a's is parse failure).
4. **M2 survives both real pairs** (no pair removes a row) and is killed only by the selftest case at `:315`. Same load-bearing status as M1.

## Historical sweep (every consecutive commit pair touching `corpus/SOURCES.md`, 10 pairs: `1e41928…54a2926`)

Base vs each mutant, per pair: M2, M3a, M3b, M4b are **SAME on all 10**; M4a is rc 2 on all 10; M3c is DIFF on `1e41928..3285cdf` (false-positive `status` changes on S011, S012, S016 where base exits 0); M1 is DIFF on `726f737..ccc4bb3` (S041 `teaches` missing). No historical pair removes a row, changes `opened`, or carries a second table block, so M2/M3a/M4b leak nowhere in current history — they are acceptance paths waiting for the first input that exercises them.

## Advisory repairs (L1-owned; I edited nothing)

1. **Pin the compared set, don't derive it by slice.** Assert the compared columns equal exactly `[c for c in header if c not in MUTABLE_CELLS and c != "id"]` as a *set equality* against the expected 7 names — this kills M3a/M3c and every truncation instantly, without new fixtures.
2. **One selftest case per immutable cell.** Add rewrites of `opened`, `kind`, `tier`, `scope` (each expected exit 1 on S001). With those, M3a fails 1/14 at minimum; `opened` alone is the cells-to-mutant mapping that is currently missing.
3. **A two-table-block fixture** — block 1 with S001, blank line, block 2 with S002; the `to` doc removes S002 from block 2 and expects exit 1. This kills M4b. If stopping at the end of the first block is intended, the header must say so and the census must agree; today the tool's docstring only promises the `## Registry` section.
4. Keep the existing `teaches`/`removed`/`anchor`/`source` cases: they are the sole detectors for M1 and M2, since no real pair distinguishes either.

## Commands run (all in `/tmp` clones; `PYTHONDONTWRITEBYTECODE=1`)

```
git clone -q … /tmp/MutAppendOnlyGuard-clone && git -C … checkout -q 54a29268…   # rc 0
python3 tools/sources-append-only.py --selftest                                   # rc 0, 14/14
python3 tools/sources-append-only.py --from b8e485c --to ccc4bb3                  # rc 1
python3 tools/sources-append-only.py --from cff9e62 --to 54a29268…                # rc 0
python3 <mutant>.py --selftest                                                    # M1 1, M2 1, M3a 0, M3b 0, M3c 1, M4a 1, M4b 0
python3 <mutant>.py --repo … --from b8e485c --to ccc4bb3 --json                  # M1 1, M2 1, M3a 1, M3b 1, M3c 1, M4a 2, M4b 1
python3 <mutant>.py --repo … --from cff9e62 --to 54a29268… --json                # 0/2 as tabled
# synthetic two-commit repos (14 probes) and the 10-pair historical sweep; rc per tables above
```

No lane file was edited; only this report was written. No lane tool, gate or counting command ran inside the lane directory (read-only `git log/show/grep/sed` only). No installs, no upgrades, no pacman. No ports bound or contacted.

## Limitations

- M4a's literal implementation (break at the first blank line in the section) is caught by everything and by both real pairs because line 10 of the real registry is blank; M4b is my nearest *working* implementation of "rows only before the first blank line" and is the one that survives. Both are reported so L1 can judge which reading was meant.
- Synthetic repos are single-author `/tmp` fixtures with the tool's own header shape, not the 41-row corpus; they prove acceptance, not corpus state. The real-pair and 10-pair sweep use the lane's actual blobs.
- I mutated only `MUTABLE_CELLS`, the removed-row branch, `immutable_cols`, and the section scan loop. `split_cells`, `ID_RE`, the `--json` path, `git_show` guards and `main()` were not mutated (out of assignment; `SentinelSeatWrites.md:32-33` already routes the non-UTF-8 `text=True` residual).
- No pre-round frozen copy of this tool exists (`frozen/manifest.json` lists `round-13_measure.py`, both `check*.py`, `tools_kama-llamacpp-live.py`, `tools_kama-probe.sh`); the mutation baseline is therefore the committed tool at `54a2926`, not a frozen artifact.
- Scratch `/tmp/MutAppendOnlyGuard-*` removed after the run.
