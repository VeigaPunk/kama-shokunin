# S1Rows — round 49, lane kama: S494/S495 re-open

**Verdict: both rows are real sources and both located quotes are verbatim (20 and 15 words), but S494's `scope` cell is wrong — it claims the pinned README documents the `/detokenize` *response*, and the README documents only that endpoint's request option — and both rows' `used-by` names a knowledge file that cites neither source today; the registry gate passes (exit 0) with my replacement S494 row and passes (exit 0, 0 E11) untouched apart from that used-by issue.**

Tip measured: lane `122c4ee9` (build `74558c71`, freeze `36d5ed26`). All re-opened live by me on 2026-10-26 23:28–23:33Z; no lane file touched, nothing committed.

## Evidence — the sources are what the rows say

| check | command | result |
|---|---|---|
| S494 URL | `curl -sS -o raw-readme.md <raw URL at caa8191d>` | 200, 126663 B, sha256 `009af291f69adaa041be4e79f1550e5f36bcaf3a929373091a7e4ac9b7bbac0c` |
| S494 frozen copy | `sha256sum` both | identical digest; 2523 lines, ends `0x0a` — the copy is byte-exact |
| S494 "at b11909" | `gh api repos/ggml-org/llama.cpp/git/ref/tags/b11909` | `refs/tags/b11909 -> commit caa8191df159f764fb0160e3d2fc6be008948aee` (commits/b11909 same sha, 2026-10-26T15:21:14Z) |
| S494 blob view | `curl -sS <github.com/.../blob/caa8191d/.../README.md>` | 200, 1232167 B; body carries the README text |
| S495 URL | `curl -sS -o proc_pid_exe.5.html <man7 URL>` | 200, 8377 B; footline `Linux man-pages 6.19  2026-02-08  proc_pid_exe(5)`; colophon tarball `man-pages-6.19.tar.gz` |
| S495 quote | verbatim test | in DESCRIPTION ¶1 at copy `.ufo/waves/round-49/c1/proc_pid_exe.5.txt:75-76`; byte-exact only after collapsing the page's hard wrap (`:75` ends "attempting", `:76` starts "to open it") |

Cell tables are in `out/S1Rows/rows.md` §2–§3: S495 is 11/11 correct; S494 is 9/11 (id, source, kind, tier, teaches, status, opened, recheck, anchor-span all verified; `scope` wrong, `used-by` wrong).

## Defects

### F1 — S494 scope over-claims the `/detokenize` response (`corpus/SOURCES.md:247`, col 5)

Row text: "documented request and response shape of the server's `/tokenize` (with `with_pieces`) and `/detokenize` endpoints at the b11909 commit".

Command that shows it:

```
$ grep -n 'detokenize' .ufo/waves/round-49/c1/server-README-caa8191d.md
731:### POST `/detokenize`: Convert tokens to text
735:`tokens`: Set the tokens to detokenize.
```

That is the entire section (`:731` heading, `:733` `*Options:*`, `:735` the one option, `:737` next heading). `/tokenize`, by contrast, has `**Response:**` at `:698` and the quoted shape at `:700`. The counter relies on the undocumented field — `tools/round49-replay-witness-audit.py:284` `post(port, "/detokenize", {"tokens": ids})["content"]`; the behaviour is real in the same commit (`tools/server/server-context.cpp` at `caa8191d`, fetched, sha256 `61c1afcf…c61114`, `:6293` handler, `:6303` `res->ok(json{{"content", …}})`), but not in this document.

Fix: full replacement row in `out/S1Rows/rows.md` §6 (`scope` narrowed, `anchor` split `686-730` / `731-735`) — diff at `out/S1Rows/s494-row.diff`, gate `exit 0` on the replaced copy (`out/S1Rows/validate.proposed.tsv`). Alternative if the response must be licensed: one extra row for `tools/server/server-context.cpp` at `caa8191d` (`:6293-6305`). The counter's `newrow` leg (`:394-405`) needs the README URL plus `/tokenize` in a new row and stays satisfied under either fix.

### F2 — both rows' `used-by` names a knowledge file that does not use them (`corpus/SOURCES.md:247` and `:248`, col 11)

```
$ grep -n 'tokenize\|proc/<pid>/exe\|proc_pid_exe\|S49[0-9]' corpus/knowledge/llamacpp-loading-lifecycle.md
434: ... (S488, S489, S490) ... build_info `b11909-caa8191df` ...
436: ... (appended 2026-10-26; S492, S493) ...
438: ... S492 ... S493 ... S490 ...
```

No `/tokenize`, no `/proc/<pid>/exe`, no S494/S495. The second path is honest: `corpus/lessons/round-49.md` (untracked scribe file) cites both at `:12`, `:21`, `:22`. Fix (a) preferred: let integration append the round-49 witness paragraph to that knowledge file naming S494/S495; fix (b) otherwise: drop that path from col 11 of both rows.

### F3 — minor: S494 anchor inherits F1's implication

`corpus/SOURCES.md:247` col 6: "§POST `/tokenize` … → Response, and §POST `/detokenize` (lines 686-735)". The span is exact (686 heading, 731 detokenize heading, 735 last line), but it should say the `/detokenize` citation is request-only. Covered by the replacement row.

### Gate-usage note (row-neutral)

`scripts/sources-census.sh:497-502` sets `dir = realpath(dirname(file)/..)`, so a copy must sit at `<X>/corpus/SOURCES.md`, and `:563-567` tests `-e "$dir/$path"`. On a bare copy (my first, literal run) every used-by path reads "missing": **441 E11, 93 W04, 1 W01, exit 1**. With the used-by tree mirrored under `<X>` (64 symlinks): **`file ok`, 93 W04, 1 W01, 0 E11, exit 0**; with my replacement S494 row: **exit 0**, identical finding set. Receipts: `validate.bare.tsv`, `validate.mirror.tsv`, `validate.proposed.tsv`.

## Gate receipt

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate \
    --file $S/mirror/corpus/SOURCES.md --today 2026-10-26
file	ok	/fast/scratch/hyaku/kama-r49/S1Rows/mirror/corpus/SOURCES.md
... 93 × W04, 1 × W01 ...
exit=0
```

## Lesson Gate entries

`corpus/lessons/round-49.md:19-22` already carries both entries and both filed quotes are verbatim with correct word counts, line references and access time (`2026-10-26T23:11:45Z` = the copies' mtime `20:11:45 -0300`). My draft (`out/S1Rows/gate-entries.md`, also `rows.md` §8) keeps them and adds the S494 `/detokenize` caveat in `Why` and the S495 hard-wrap note in the quote cell.

## Limits

- No llama-server started; `/detokenize`'s `content` is grounded on the README's silence plus the same commit's source, not a live response.
- Neither round-49 counter re-run (`witness=1 cap=1 newrow=1`, `fixture=1 lane=1` not re-verified here).
- Man copy compared to the live HTML by content/colophon/quote, not rebuilt.
- Lane moved under me: `corpus/lessons/round-49.md` appeared untracked, `tools/append-only-audit.py` is `M`. Not mine, not touched.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S1Rows.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S1Rows/rows.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S1Rows/gate-entries.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S1Rows/{validate.bare.tsv,validate.mirror.tsv,validate.proposed.tsv,quote-check.txt,copies-check.txt,fetch-receipts.txt,gh-b11909.json,readme-686-737.txt,detokenize-handler.txt,s494-row.diff}`
