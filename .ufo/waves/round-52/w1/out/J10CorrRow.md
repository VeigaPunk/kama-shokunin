# J10CorrRow — round 52 ablation control C2 (an A-corr disclosure row added)

**Verdict: control `met=False` as required, in both row shapes; the frozen C2 counter rejects a disclosure row for an A-corr file on two independent legs, and the v6 cutoff rejects the row that v6's own JSON asks for.** A row naming a commit *before* the ledger's introduction is accepted by the tool (`ok`, no bad disclosure) but pays for nothing: the fresh deletion event stays `unrestored` with the same key, the historical event stays `regressed`, the tool still exits 1, and the counter still fails the lane leg because the row names an A-corr file.

## Construction

Fixture clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`, detached at the build `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`; `git -C $S/lane rev-parse --show-toplevel` = `$S/lane` asserted before every commit; commits made with `-c user.name=fx -c user.email=fx@invalid -c commit.gpgsign=false` (see `out/J10CorrRow/commits.txt`).

Deleted line: `LOG.md:2381` at the build blob — the `f4066979096e` fence of `## Restored lines (round 52)`:
`(12/14); A1 closed it before data (0/14). Wave 1 (36 seats) found 58`
`sha256 = 13740f679956a38559d1151ef3a9d0e891d2d76343b3060b4e655a239f9f0a82`.
Chosen because its deleting commit `f4066979096e3452ae731c0e09e50155c6d8258a` (2026-10-23) precedes the ledger's introduction `b6bed925b032ac2c19b63ef4af358ebdd5922c26` (2026-10-27, round-51 build; `git log --diff-filter=A --reverse -- registry/append-only-disclosures.tsv`), i.e. the "row names a commit before the ledger's introduction" shape.

Baseline on my clone at the build, frozen counter, exit 0:
```
fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True
```
(`out/J10CorrRow/base-build.c2.out`; matches the L1's `measured/c2-build.out`.)

## Fixture A — fx-pre, pre-introduction row (the shape the seat names)

Commit `fb730daf14e3d5696bc3188ee917acca0a49d78e`: delete the line + append
`f4066979096e…<full>\tLOG.md\t13740f67…\t1\tin-place-edit\t…` (class `in-place-edit` taken from the tool's own per-event demand; `out/J10CorrRow/pre.diff`).

Tool v6 (`python3 tools/append-only-audit.py --repo $S/lane --to fb730daf… --json`), **exit 1**:
- row verdict: `{"commit":"f4066979096e…","file":"LOG.md","line_sha256":"13740f67…","count":1,"class":"in-place-edit","ok":true,"reason":"ok"}` — the cutoff accepts it.
- `summary` = `restored 67, partial 0, unrestored 1, regressed 1, bad_disclosures 0, bad_declarations 0, disclosed_lines 11` (10→11).
- historical event `f4066979096e LOG.md`: `status restored, disclosed 1, held_at_to 2, restored_max 3` → contributes `regressed 1`.
- fresh event `fb730daf LOG.md`: `deleted 1 graded 1 status unrestored disclosed 0`, `undisclosed [{13740f67…, 1, ["removal"]}]` — the same key, still unheld.

Frozen counter, **exit 1** (`out/J10CorrRow/pre.c2.out`):
```
fixture=1 lane=0 scenarios=8/8 corr_lost=2 row_lost=10 disclosed=11 met=False
detail: lane: tool definition v6 threshold 1 exit 1 {'unrestored': 1, 'partial': 0, 'regressed': 1, 'bad_disclosures': 0, 'bad_declarations': 0}
detail: lane: ledger discloses f4066979096e LOG.md, an A-corr file (restore by append)
detail: lane: unheld lines in A-corr files: {'LOG.md': 2}
```
(flag emitted at `tools/round52-append-restore-check.py:484`; the A-corr leg is `:480-484`).

## Fixture B — fx-post, post-introduction row, exactly what v6's JSON asks for

C1 `8e1e55c584277df630509aa196325e41b01eae8f` deletes the line only (`git show … -- LOG.md`: `1 file changed, 1 deletion(-)`); the tool at C1 reports for that event `undisclosed [{13740f67…, 1, ["removal"]}]`, documented as "what a disclosure row would have to name" (`tools/append-only-audit.py:27-28`). C2 `b5680ec4a219969e09b3ebde94c1fb559d9949e0` appends exactly that row (`count 1`, `class removal`, `out/J10CorrRow/post.diff`).

Tool v6 at C2, **exit 1**:
```
{"commit":"8e1e55c5…","file":"LOG.md","ok":false,
 "reason":"names a commit at or after the ledger's introduction b6bed925b032: restore by append"}
summary: unrestored 1, regressed 1, bad_disclosures 1
```
(cutoff at `tools/append-only-audit.py:583`; exit rule `:775`.)

Frozen counter, **exit 1** (`out/J10CorrRow/post.c2.out`):
```
fixture=1 lane=0 scenarios=8/8 corr_lost=2 row_lost=10 disclosed=11 met=False
detail: lane: ledger discloses 8e1e55c58427 LOG.md, an A-corr file (restore by append)
detail: lane: unheld lines in A-corr files: {'LOG.md': 2}
```

## Positive control — fx-repair (same deletion, repaired by verbatim re-append)

Commit `cd25d8907ca4354f84e06c11181662818711882a`: the line deleted from the fence and re-appended verbatim inside a five-backtick fence at EOF under `## Restored lines (round 52, continuation)`.
Tool exit 0 (`unrestored 0 partial 0 regressed 0 bad_disclosures 0 bad_declarations 0`); counter exit 0:
```
fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True
```
(`out/J10CorrRow/repair.c2.out`.) So A and B fail because of the disclosure mechanism, not because the fixture tree is damaged; only restore-by-append passes.

## The two answers

1. **Would the round-51 counter accept the row?** No, on two legs. (a) Any ledger row naming an A-corr file fails the lane leg regardless of the row's commit age — fx-pre proves the pre-introduction row is flagged too (`corr_lost=2`, `met=False`). (b) A row naming the fresh commit is additionally a v6 `bad_disclosure`, so the tool leg fails (`exit 1`), and the counter's lane leg requires tool exit 0.
2. **Does the tool accept the pre-introduction row?** Yes — verdict `ok`, `bad_disclosures 0`, `disclosed_lines 11` — but it cannot lift the exit code: the same key is graded again in the fresh event and is not held at tip (`unrestored 1`), and the historical event is `regressed` (held 2 of `restored_max` 3). The cutoff's accepted shape buys `disclosed` status for the historical event only.

Per-event arithmetic of the one physically missing line (own recompute with the counter's `recompute()`, imported read-only):
```
fx-post: event 8e1e55c58427 LOG.md unheld 1 keys {'13740f679956': 1}
         event f4066979096e LOG.md unheld 1 keys {'13740f679956': 1}   LOG.md total 2, rule {('A-corr','*')}
fx-pre:  event f4066979096e LOG.md unheld 1; event fb730daf LOG.md unheld 1
```
`corr_lost` is event-summed, so one missing line reports as 2. This can only over-count failures; the predicate is `corr_lost=0`, so no `met=True` can come of it.

## Bounded observations (no claim; not defects in the frozen counter)

- v6's `undisclosed` is documented as "what a disclosure row would have to name" (`tools/append-only-audit.py:27-28`), yet for events at or after the ledger's introduction (`:583`) no row can name them — fx-post's tool JSON therefore advertises a row that is unconditionally bad. Suggested for a later round (not applied; lane frozen): add `"disclosable": false` to such events' `undisclosed` entries, or emit them under a separate `restore_only` key. Docstring/JSON wording only; no leg changes.
- v6 has no A-corr exclusion for disclosure rows: it accepted the fx-pre row for `LOG.md` (`ok`). The "A-corr restores, never discloses" rule lives only in the counter's lane leg (`tools/round52-append-restore-check.py:480-484`). That is exactly what this control exercises; if that leg were ever dropped, an A-corr disclosure row at a pre-introduction commit would pass v6.

## Constraints

Lane `/home/vgpnk/Projects/shokunin/kama-shokunin` read-only; all mutation in `$S/lane`. No subagents, no `agent://all`, no service started: `pgrep -af llama-server` at finish matched one process that is not a server — pid 2131195, a `sha256sum ./OpenBot-0.51.1-x86_64.AppImage … ./llama-server …` invocation whose argument list names `llama-server` (pgrep matches the full command line); no `llama-server` executable was running, and this seat launched none. No pacman/installs. No C1 counter run (its downloads/llama-server are outside this seat). Scratch `/fast/scratch/hyaku/kama-r52/J10CorrRow` removed after copying the receipts below.

## Files written

- `.ufo/waves/round-52/w1/out/J10CorrRow.md` (this report)
- `.ufo/waves/round-52/w1/out/J10CorrRow/` — `base-build.c2.out`, `pre.c2.out`, `post.c2.out`, `repair.c2.out` (frozen-counter receipts), `pre.diff`, `post.diff` (fixture diffs), `pre.json`, `post-c1.json`, `post-c2.json`, `repair.json` (tool v6 JSON at each tip), `commits.txt` (toplevel assertion, fixture commits/parents, deletion and repair diffs).
