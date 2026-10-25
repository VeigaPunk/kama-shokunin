VERDICT: killed. Exit code **1**. A staged row copied with one escaped pipe fails census. Baseline (header only) exited 0, so the kill is not inconclusive. 1 killed, 0 survived, 0 inconclusive.

# MutCensusPipe — escaped-pipe census probe

## Axes

- Operability: the assigned detector runs on an isolated scratch and returns a decisive exit. Judged axis. Improved: exit code captured.
- Isolation: lane `corpus/SOURCES.md` and the staged append file are not written. Improved: both hashes unchanged. No sibling seat, fleet repo, git index, or jj state was touched.
- Attribution: the failure is tied to the one `\|` byte pair, and the shifted-cell E11 is named rather than folded into E01. No contract change.
- Restoration: pre-mutation scratch bytes are recovered, re-detected, and hash-matched. Done. The task then requires the scratch `SOURCES.md` to keep the bad row, so that file was rewritten to the measured mutant after the restore check. Restored bytes remain at `SOURCES.restored.md`.

C1 and C2 predicates were not retargeted. `MISSION.md` was not edited; axis authority was not touched.

## Mutant

Smallest behavior-bearing point: the two-byte sequence `\|` (0x5c 0x7c) in the first staged data row that contains it.

- Source: `/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md` line 7, id S325, copied byte-exact (not rewritten).
- One escaped pipe, in the recheck cell: `v1_guide/' \| grep -c 'unified sche`.
- Pipe count on that row: 13 (12 structural pipes for an 11-column row, plus this one).
- Scratch: `.ufo/waves/round-35/w1/out/MutCensusPipe/SOURCES.md` = lane registry header (exact bytes of `corpus/SOURCES.md` lines 1–12, through the separator) plus that one row. 13 lines, 1 data row, 1 `\|`.
- Not appended to the lane registry. `| S325 |` is absent from `corpus/SOURCES.md`.

## Expected detector

```text
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file .ufo/waves/round-35/w1/out/MutCensusPipe/SOURCES.md
```

Detector sha256 `3fb7261569f46423dd80ecc23e0a23789a7926f667c7a3fc559d2439d4a64e30`. No `--today` override. Claim under test: a staged row copied with an escaped pipe must fail census. Expected: non-zero, specifically exit 1 (E-finding). `gawk -F'|'` does not treat `\` as an escape, so one extra `|` makes `NF=14` and E01 (`fields=NF-2=12`, want 11).

## Output

Same command on three byte states of that path:

| State | sha256 | stdout | exit | verdict |
|---|---|---|---:|---|
| pristine (header only) | `93d51561bc5af73a3af96c9ac2edf4ac41396dfa1049495cdb99cd676eae36ca` | `file	ok	.../MutCensusPipe/SOURCES.md` | 0 | baseline passes |
| mutant (header + S325) | `8741f2edca52b826c7e97f75fc3521c69f54819a40d6580cb0cf5e032cb0e8b4` | E01 fields=12; E11 shifted used-by (verbatim below) | **1** | **killed** |
| restored (header only) | `93d51561bc5af73a3af96c9ac2edf4ac41396dfa1049495cdb99cd676eae36ca` | `file	ok	.../MutCensusPipe/SOURCES.md` | 0 | restored |

Mutant stdout, verbatim:

```text
file	E01	S325 fields=12
file	E11	S325 missing used-by grep -c 'unified scheduler'` (expect ≥1) (ran 2026-10-23)
```

Exit code: **1**.

stderr was empty on all three runs. The detector did not rewrite the file (sha256 unchanged across each run).

E11 is the same pipe, not a second defect: the extra `|` sits in the recheck cell, after status, so the bash used-by splitter still sees status `mined` and then reads the post-`\|` fragment as the used-by path. This probe did not run a well-formed-row control. `--file` resolves used-by against the parent of the scratch directory (`.../w1/out`), so a clean mined row placed here could also E11 on its real used-by path. That possible confound does not erase this kill: E01 `fields=12` is the field-count failure the escaped pipe produces, and the baseline header exited 0.

A surviving mutant would have been a coverage finding. This one did not survive. Not permission to change the census contract.

## Restoration evidence

- Lane registry before and after: sha256 `d88e497c5c10ffacb7caed0c137a9bf4c6b1bbc0e7520749bdae9f9dfa855603` (unchanged).
- Staged append before and after: sha256 `3f4cd9d713885efd2ec868065ee227317a556da157c8f48af36ecc9cde96de2f` (unchanged; read only).
- Restored scratch bytes match pristine: `cmp` equal, sha256 `93d51561bc5af73a3af96c9ac2edf4ac41396dfa1049495cdb99cd676eae36ca`, detector exit 0 while those bytes were in `SOURCES.md`.
- Copy kept at `.ufo/waves/round-35/w1/out/MutCensusPipe/SOURCES.restored.md` (same sha256). Pristine copy: `SOURCES.pristine.md` (same sha256).
- Task requires the scratch to remain header plus the bad row, so `SOURCES.md` was rewritten to the measured mutant after that check. Final scratch sha256 `8741f2edca52b826c7e97f75fc3521c69f54819a40d6580cb0cf5e032cb0e8b4`, `cmp`-equal to `SOURCES.mutant.md`, equal to pristine bytes plus the exact staged line.

Log: `.ufo/waves/round-35/w1/out/MutCensusPipe/probe.log`.

Report: .ufo/waves/round-35/w1/out/MutCensusPipe.md
