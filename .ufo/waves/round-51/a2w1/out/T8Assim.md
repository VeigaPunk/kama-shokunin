# Round 51 T8Assim — Shokuknow assimilation pre-check

**Verdict: the indented-row guard works, but the staged package still has the same nine ID collisions as round 50; S499 did not change the assimilation result.**

## 1. ID collision check

Ran the requested extraction with `LC_ALL=C` against the lane's current `corpus/SOURCES.md` and `/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md`:

```sh
grep -oE '^ {0,3}\\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md | grep -oE 'S[0-9]+' | sort > reg-ids
grep -oE '^ {0,3}\\|[[:space:]]*S[0-9]{3,}' /home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md | grep -oE 'S[0-9]+' | sort > staged-ids
comm -12 reg-ids staged-ids > collisions
```

All commands exited 0. Counts: registry **240**, staged **142**, collisions **9**. Collision ids, exactly the round-50 set: `S330 S333 S334 S335 S346 S347 S352 S353 S363`. `cmp` of the new collisions file against `.ufo/waves/round-50/X1Assimilation/collisions` exited 0. Every one of the nine staged rows is 12 cells (the round-50 E01 escaped-pipe shape); each lane row is still `mined`, has 11 cells, and its document URL matches the staged row byte-for-byte. Details and extracted ids are in `out/T8Assim/{reg-ids,staged-ids,collisions}`.

The staged source file has 142 rows: 108 contain a URL and 34 do not. This matches the round-50 counts. The round-50 report's additional document-overlap finding (33 of 108 URLs already held: 9 same IDs plus 24 different lane IDs) is unchanged at the staged-input level: the staged ID list is byte-identical to round 50, and the lane registry ID delta is only S499 (below). Current URL match checks confirm all nine same-ID documents still match. Do not adopt or renumber the nine same-document ID collisions; the round-50 report recommends dropping those staged rows.

## 2. Indented-row guard proof

Built a scratch-only registry containing a normal `| S001 |` row and an indented `  | S002 |` row, then staged IDs `S002` and `S999`.

- `bash scripts/sources-census.sh validate --file <fixture>`: exit **0**; parser warnings W03 only. `census` reports **2** rows, confirming the two-space row is parsed.
- Maintained extractor `^ {0,3}\\|[[:space:]]*S[0-9]{3,}` extracts S001 and S002; `comm` returns S002 (one collision).
- Column-zero-only extractor `^\\|...` sees only S001; `comm` is empty (false green).
- Appending a second indented S002 row and validating returns **1**, with `file E03 S002 duplicate id`.

Thus the prescribed 0–3-space guard catches the indented collision, while the column-zero-only variant misses it; the census independently catches the duplicate. Fixture and command outputs are copied into `out/T8Assim/guard-*`.

## 3. Round-50 comparison and S499

Round 50 recorded 239 registry IDs, 142 staged IDs, and these same nine collisions. Current `diff` of the sorted registry IDs against round-50 `reg-ids` shows exactly one addition: `S499`. It is `corpus/SOURCES.md:252`, the Linux `proc_pid_exe(5)` row. Current staged IDs are byte-identical to round-50 `staged-ids` (`cmp` exit 0; staged file SHA-256 `3ad0df68504e1f49a0ab23e68b2034a9d6258345468fa03013737ced7ce234ff`; mtime 2026-10-24 23:33:20 -0300). Current collisions are also byte-identical to round 50. `S499` and `proc_pid_exe` both occur zero times in staged `SOURCES.append.md`; staged IDs end at S471. Therefore S499 changed neither collision count nor collision membership, and introduced no staged-document overlap.

## 4. One candidate for a later adoption round

Candidate: `corpus/knowledge/runtime-health-surface-matrix-amendment-2026-10-24-r16.md`.

This concerns vLLM readiness-route/proposal state, fitting PROVINCE.md lines 13–14 (liveness/readiness conventions and vLLM `/health` process ownership). The exact staged filename is not held in lane `corpus/knowledge/`; current lane files contain no `wants to merge`, `862047`, or `503322` evidence. Its staged sources are S469 (vLLM PR #46811 contrasted with #59179; extracted page and saved copy) and S468 (the lane's own health matrix; its seven-column header at `corpus/knowledge/runtime-health-surface-matrix.md:12` still has no process column). `corpus/lessons/round-39-verifier-spotcheck.md:67` rejected this candidate for that round's different theme and said a later theme switch was reasonable.

Calibration caveat: the separate round-43 `runtime-health-surface-processes.md` entry already covers process ownership, so the process-column observation is partly superseded. Preserve only the still-unheld readiness-proposal state/route distinction if considered later; re-open both PRs before adopting. S469 has no corresponding lane registry source row (`grep` for #46811/#59179 in current `corpus/SOURCES.md` returned zero), so that is a prerequisite. Candidate detail is in `out/T8Assim/candidate-knowledge-entry.md`.

## Files and checks

Written under `out/T8Assim/`: this report, the candidate note, sorted ID sets, collisions, staged-vs-lane name classification, and guard fixture/proof artifacts. No lane files or shared inputs were modified; no tools were installed; no server was started. No checks beyond the scoped collision/guard commands and read-only content comparisons were run.
