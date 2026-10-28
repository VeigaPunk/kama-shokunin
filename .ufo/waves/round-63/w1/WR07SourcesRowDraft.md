# WR07SourcesRowDraft — round-63 drafting item (SOURCES row for llama.cpp server-task.cpp)

Seat: WR07SourcesRowDraft (leaf, drafting). Judged on: operability. Milestone: draft landing text.
Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09`.
Landing text: `.ufo/waves/round-63/w1/out/WR07SourcesRowDraft/sources-row.md` (one 11-column row).
Evidence: `.ufo/waves/round-63/w1/out/WR07SourcesRowDraft/`.

This is a draft for the L1. I did not edit `corpus/SOURCES.md`, did not commit, and made no
verdict on the round-63 claims.

## 1. Result in one paragraph

The draft row validates clean at the tip (census `validate`, exit 0). It cannot land as a new
row without a decision, for two reasons. (a) The requested id S527 is free at the tip but is
already taken by an **uncommitted** row in the lane working tree, and that row covers the same
file. (b) The census does not treat the raw-URL form and the blob-URL form of one file as a
duplicate, so the duplicate would pass validation silently. Recommendation to the L1: land the
uncommitted S527 row (blob URL, sha matches my own fetch) instead of this draft, or land this
draft only as a `supersedes S527` row if the raw URL form is wanted. Two rows for one file
should not land.

## 2. Id check (S527) — `grep` of the registry

| State | S527 | S528 | max id |
|---|---|---|---|
| tip `03a6a1d8` (`git show`, read-only) | unused | unused | S526 |
| lane working tree `corpus/SOURCES.md` (uncommitted, `git diff --stat` = 2 insertions) | used: server-task.cpp row | used: server-common.cpp row | S528 |

Command: `git -C <lane> archive 03a6a1d8 | tar -x` into scratch, then `grep -oE '^\| *S[0-9]+'`
on the mirror; the working-tree check was `grep -n '^| S52[78] '` on the lane file.
The tip's `knowledge/completion-request-plane.md` cites only S526 (2 hits). The working-tree
knowledge file (44 insertions, uncommitted) cites S527/S528. So at the tip there is no dangling
citation, and the S527/S528 pair exists only in the uncommitted round-63 work.

Because S527 is free at the tip under test, the draft keeps id S527 so that it validates at the
tip. If the L1 lands the working-tree rows, this draft must be dropped, not renumbered.
Next free id after the working tree is S529 (no hits for `S529` anywhere in the lane).

## 3. Own fetch and sha256 (not copied from any row)

```
curl -sL --max-time 60 -w 'http=%{http_code} bytes=%{size_download}' \
  https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-task.cpp
http=200 bytes=67241
sha256  4c3f413b9b54d4cc0e7b5998e6979a2389f5ff716e20cb1510ca7745fa233495   (1904 lines)
```

This matches the sha256 recorded in the working-tree S527 row, so that row's pinned bytes are
the same file I fetched. Copy kept at `out/WR07SourcesRowDraft/server-task.cpp.704366d76`.

Located lines checked by `grep -n` on my fetch (the row's ranges are the same):

- 357 `json server_task_result_cmpl_final::usage_json_oaicompat() {`
- 366 `json server_task_result_cmpl_final::to_json_oaicompat() {`
- 374 `    json finish_reason = "length";`
- 376 `        finish_reason = "stop";`
- 390 `{"object", "text_completion"}` (grep matches at 390, 392 is `{"id", oaicompat_cmpl_id}`)
- 387 `{"created", t}`

The located quote lives in the `teaches` cell, as in S520/S521 (the table has 11 columns and no
separate quote column), not in `anchor`.

## 4. The draft row

File: `out/WR07SourcesRowDraft/sources-row.md` — 11 content cells, `NF=13` (census convention).
Fields: id `S527`; kind `code`; tier `A`; status `mined`; opened `2026-10-28`;
recheck `on-release`; used-by `corpus/knowledge/completion-request-plane.md` (only that path,
as instructed).

Recheck cadence: the S526 row's registry cell is `on-release`. S525, S526, S527-worktree and
S528-worktree all use `on-release`, so I copied it. The S526 knowledge entry's own header says
`recheck: 90d` plus a pin-change trigger. That is a separate surface (the knowledge entry, not
the registry cell); I did not change it.

Scope cell: the non-streaming response field set and `usage` at the pinned build. The timings
field list is noted as "separate server-common.cpp row" rather than as S528, because S528 is not
registered at the tip (a reference to a missing id would dangle).

## 5. Validation (census, `validate --file`, `--today 2026-10-28`)

Mirror: `git archive 03a6a1d8` (full tree) into scratch, `corpus/SOURCES.md` replaced with the
tip blob plus the draft row inserted after the S526 row (line 278). The seat spec named
`$S/validate/corpus/` as the mirror path. My first build used a `corpus`+`registry` only mirror,
which produced 74 spurious E11 findings because used-by paths like `SKILL.md` and `tools/` were
absent. I discarded that build; the full-tree mirror is the one reported here.

Run 1 — tip baseline, pristine:
```
file	ok	.../full/corpus/SOURCES.md      (exit 0)
file	W01	S481 tierC mined used-by=...    (pre-existing warning)
103 × W04                                   (pre-existing cross-scope URL warnings)
```

Run 2 — tip + draft row (S527, raw URL):
```
file	ok	/fast/scratch/hyaku/kama-r63/w/WR07SourcesRowDraft/full/corpus/SOURCES.md
file	W01	S481 tierC mined used-by=corpus/knowledge/runtime-health-surface-processes.md, ...
(103 W04 lines, unchanged)
exit=0
```
The draft row produces no E-code and no new W-code. The validate run's exit code is 0.

Earlier failures I fixed in the draft (kept here so the L1 does not repeat them):
- `||` in the teaches cell (the `STOP_TYPE_WORD || STOP_TYPE_EOS` expression) split the row:
  `E01 S527 fields=13`. Reworded to "the STOP_TYPE_WORD and STOP_TYPE_EOS branch".
- Missing closing `|` after used-by: `E01 S527 fields=10`. Added.

Run 3 — probe: tip + uncommitted worktree S527/S528 rows (blob URL) + draft as S529 (raw):
```
file	E11	S527 missing used-by corpus/lessons/round-63.md
file	E11	S528 missing used-by corpus/lessons/round-63.md
exit=1
```
No E04. The raw URL and the blob URL are not normalized to one URL by the census
(`sources-census.sh` line ~603 lowercases only the host segment).
The E11s are real: `corpus/lessons/round-63.md` is not at the tip, so the uncommitted rows name
a file that has not landed. That is the working tree's problem, not this draft's.

Run 4 — probe: same as run 3 but draft as S529 with the blob URL:
```
file	E11	S527 missing used-by corpus/lessons/round-63.md
file	E11	S528 missing used-by corpus/lessons/round-63.md
exit=1
```
No E04 either. The scope cells differ in wording, and E04 keys on (normalized URL, scope text).

Run 5 — probe: the uncommitted S527 row re-id'd to S529, byte-identical except the id:
```
file	E04	S529 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76.../tools/server/server-task.cpp within scope the field set ...
exit=1
```
E04 fires only when URL and scope text both match exactly.

Tallies: run 1 = ok 1, W01 1, W04 103, E 0. Run 2 = ok 1, W01 1, W04 103, E 0. Runs 3–4 =
E11 2 (worktree rows only, lessons file absent at tip). Run 5 = E04 1 (exact duplicate).

## 6. Findings for the L1 (operability)

1. **Id collision, not a free slot.** S527/S528 are uncommitted in the lane worktree
   (`git status`: `M corpus/SOURCES.md`, `M corpus/knowledge/completion-request-plane.md`,
   plus untracked round-63 files). Their owner is not visible to this seat. Do not renumber this
   draft into the worktree without that owner's say.
2. **One file, two rows is a silent duplicate.** The raw-URL form (this draft) and the blob-URL
   form (the worktree row) of the same blob both validate. E04 misses them. If the L1 wants both
   forms, it must mark one row `supersedes S527`, or it should keep only one row.
3. **Census blind spot (contract-level, reported not fixed).** E04's key is (normalized URL,
   scope text). A duplicate with different scope wording, or with a raw/blob URL difference,
   passes. Run 3, run 4 and run 5 are the evidence. Fixing the census is out of this seat's scope.
4. **Worktree used-by names a missing file at the tip.** `corpus/lessons/round-63.md` is cited by
   the working-tree S527/S528 rows and does not exist at `03a6a1d8`. It will be E11 until the
   lesson lands. Not a defect of this draft.
5. **Recheck wording.** The registry recheck `on-release` and the knowledge entry header's
   `recheck: 90d` describe different objects. The S526 convention in the registry is
   `on-release`; the 90-day cadence belongs to the knowledge entry. Noted, not changed.

## 7. Bounds and tools

- Writes: only my out dir `out/WR07SourcesRowDraft/` (sources-row.md, receipts) and this report.
  Nothing was written to `corpus/`, `registry/`, `CORPUS.md`, `SCORECARD.md`, or any tracked file.
- Git: read-only only (`archive` into scratch, `show`, `diff --stat`, `status`, `cat-file`,
  `log`, `rev-parse`). No commit, add, stash, checkout, or reset in the lane or fleet.
- Installs: none. Used existing `curl`, `git`, `awk` (gawk, required by the census), `grep`.
  No pacman transaction, no `~/.local/bin` writes.
- Network: one `curl -sL` GET of the raw URL. No live llama.cpp server was started (none needed).
- Scratch `/fast/scratch/hyaku/kama-r63/w/WR07SourcesRowDraft` removed after receipts were copied.

## 8. Checks the main agent should run once after landing decisions

- `scripts/sources-census.sh validate --file corpus/SOURCES.md --today <date>` on the landed tree.
- `grep -n '^| S52[78] ' corpus/SOURCES.md` to confirm exactly one S527 row exists.

Last line (validate, draft row at tip, run 2): `file	ok	…/full/corpus/SOURCES.md` — exit 0, W01 1, W04 103, E 0.
