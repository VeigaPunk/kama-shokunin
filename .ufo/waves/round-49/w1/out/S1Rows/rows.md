# S1Rows — S494 and S495 re-opened against the live sources

Seat: S1Rows (round 49 wave w1, lane kama). Measured lane tip `122c4ee9` (build `74558c71`, freeze `36d5ed26`).
Sources opened myself on 2026-10-26 between 23:28Z and 23:33Z; nothing below is copied from a receipt.
Read-only: no lane file was edited; the proposed row lives in this directory only.

**Verdict.** S495 is clean in every cell (11/11) once the man page's hard wrap is normalised. S494 is clean in 9 of 11 cells: its `scope` cell (col 5) claims the README documents the `/detokenize` **response** shape, and it does not — the README gives that endpoint a heading and one request-option line, nothing else. The `anchor` cell (col 6) inherits the same over-claim in a milder form. Both rows' `used-by` cell (col 11) names `corpus/knowledge/llamacpp-loading-lifecycle.md`, which today cites neither source. The registry gate exits 0 with the proposed replacement row applied.

## 1. Sources actually opened

| what | command | HTTP | bytes | observation |
|---|---|---|---|---|
| raw README at `caa8191d` | `curl -sS -o raw-readme.md .../caa8191df159f764fb0160e3d2fc6be008948aee/tools/server/README.md` | 200 | 126663 | sha256 `009af291f69adaa041be4e79f1550e5f36bcaf3a929373091a7e4ac9b7bbac0c` |
| github blob view, same commit | `curl -sS 'https://github.com/ggml-org/llama.cpp/blob/caa8191d.../tools/server/README.md'` | 200 | 1232167 | page body carries the README text (`grep -c 'The `tokens` array'` > 0) |
| man7 page | `curl -sS 'https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html'` | 200 | 8377 | footline `Linux man-pages 6.19  2026-02-08  proc_pid_exe(5)`; colophon tarball `man-pages-6.19.tar.gz`, rendered `2026-09-09` |

Fidelity of the frozen copies (lane `.ufo/waves/round-49/c1/`):

```
009af291f69adaa041be4e79f1550e5f36bcaf3a929373091a7e4ac9b7bbac0c  raw-readme.md
009af291f69adaa041be4e79f1550e5f36bcaf3a929373091a7e4ac9b7bbac0c  .../.ufo/waves/round-49/c1/server-README-caa8191d.md
 2523 126663 raw-readme.md
 2523 126663 .../server-README-caa8191d.md        # ends 0x0a, so 2523 is the true line count
```

The copy is byte-identical to what the pinned URL serves now. Tag binding (one `gh api` per object):

```
repos/ggml-org/llama.cpp/commits/b11909 -> sha caa8191df159f764fb0160e3d2fc6be008948aee
                                           commit date 2026-10-26T15:21:14Z
repos/ggml-org/llama.cpp/git/ref/tags/b11909 -> refs/tags/b11909 -> commit caa8191df159f764fb0160e3d2fc6be008948aee
```

So the source cell's "at b11909" and the URL's `caa8191d` denote the same commit, and the round-48 receipts' `build_info b11909-caa8191df` is that commit.

## 2. S494 — every cell (`corpus/SOURCES.md:247`)

Row under test: `| S494 | llama.cpp server README at b11909 — <raw url caa8191d> | docs | A | ... | ... | ... | mined | 2026-10-26 | on-release | corpus/knowledge/llamacpp-loading-lifecycle.md, corpus/lessons/round-49.md |`

| # | cell | claim in the row | what I observe | verdict |
|---|---|---|---|---|
| 1 | id | `S494` | unique (`validate` reports no E02/E03; `grep -c` of `^| S494 |` = 1) | **ok** |
| 2 | source | "llama.cpp server README at b11909 — raw URL at `caa8191d`" | URL 200, 126663 B, sha256 equals the frozen copy; `refs/tags/b11909` peels to `caa8191d`; blob view 200 and serves the same body | **ok** |
| 3 | kind | `docs` | it is a repository README | **ok** |
| 4 | tier | `A` | upstream project's own documentation at a pinned commit; not community | **ok** |
| 5 | scope | "documented **request and response shape** of the server's `/tokenize` (with `with_pieces`) **and `/detokenize`** endpoints …" | `/tokenize`: true — options at 690-696, `**Response:**` at 698, shape at 700, JSON examples 705-729. `/detokenize`: **false for the response** — the whole section is `731` heading, `733` `*Options:*`, `735` `` `tokens`: Set the tokens to detokenize.``, `737` next heading. No `Response` text anywhere (`grep -n detokenize` = 731 and 735 only) | **DEFECT (F1)** |
| 6 | anchor | "§POST `/tokenize`: Tokenize a given text → Response, **and §POST `/detokenize`** (lines 686-735 of the copy)" | span is exact — 686 is the `/tokenize` heading, 731 the `/detokenize` heading, 735 its last line; `**Response:**` is at 698 and the quoted text at 700. But read together with col 5 it implies `/detokenize` has a response citation | **imprecise (F3, same root as F1)** |
| 7 | teaches | quote + "so an observer outside a replay can send a fresh nonce … and check each returned piece against the model's own vocabulary" | quote 20 words, verbatim at README line 700 (`quote-check.txt`); the inference is marked "so" and follows from `with_pieces` returning `id`+`piece` per token | **ok** |
| 8 | status | `mined` | the row was admitted this round (lesson `## Gate` line 21) | **ok** |
| 9 | opened | `2026-10-26` | today; ISO past/present | **ok** |
| 10 | recheck | `on-release` | symbolic cadence; the URL is commit-pinned, so "look again when a new llama.cpp release lands" is the honest trigger | **ok** |
| 11 | used-by | `corpus/knowledge/llamacpp-loading-lifecycle.md`, `corpus/lessons/round-49.md` | lesson: true — `corpus/lessons/round-49.md:12,21` cite S494. Knowledge: **false today** — that file's only S49x citations are S488/S489/S490 (`:434`) and S492/S493 (`:436`, `:438`); `grep -n 'tokenize\|proc/<pid>/exe'` finds nothing | **DEFECT (F2)** |

## 3. S495 — every cell (`corpus/SOURCES.md:248`)

| # | cell | claim in the row | what I observe | verdict |
|---|---|---|---|---|
| 1 | id | `S495` | unique | **ok** |
| 2 | source | "Linux proc_pid_exe(5) — https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html" | 200, 8377 B; page is the man-pages 6.19 rendering | **ok** |
| 3 | kind | `docs` | manual page | **ok** |
| 4 | tier | `A` | kernel man-pages project, canonical man7.org rendering | **ok** |
| 5 | scope | "what `/proc/<pid>/exe` names and that opening it opens the running executable; Linux only; not other platforms, **not a permission model**" | ¶1 (copy lines 73-83) names the link and says it opens the executable; ¶2 (85-87) is the ptrace access-mode rule, correctly excluded; the " (deleted)" clause (78-80) also supports the exclusion | **ok** |
| 6 | anchor | "§DESCRIPTION ¶1; man-pages 6.19, page dated 2026-02-08 (text copy …)" | DESCRIPTION at copy line 71, ¶1 = 73-83; live footline `Linux man-pages 6.19  2026-02-08`; colophon tarball `man-pages-6.19.tar.gz` | **ok** |
| 7 | teaches | quote + "so hashing `/proc/<pid>/exe` identifies the binary a listener is really running, whatever path or wrapper started it" | quote 15 words; verbatim at copy 75-76 after collapsing the page's hard wrap (75 ends "attempting", 76 starts "to open it"); inference follows, and the " (deleted)" clause makes it hold even after the path is replaced | **ok (wrap note)** |
| 8 | status | `mined` | admitted this round (lesson line 22) | **ok** |
| 9 | opened | `2026-10-26` | today | **ok** |
| 10 | recheck | `on-release` | man page is versioned by man-pages releases; a new tarball can rewrite the paragraph | **ok** |
| 11 | used-by | same two paths | same F2 finding as S494 | **DEFECT (F2)** |

## 4. Located quotes

| row | quote | words | verbatim | location |
|---|---|---|---|---|
| S494 | "The `tokens` array contains either just token IDs or objects with `id` and `piece` fields, depending on the `with_pieces` parameter." | 20 | yes, byte-exact | README line 700 (inside `/tokenize` 686-730) |
| S495 | "This symbolic link can be dereferenced normally; attempting to open it will open the executable." | 15 | yes after whitespace normalisation | copy `.txt:75-76`, live HTML text line 75 |

Both are ≤ 25 words. The S495 split is the man page's own wrap, not a misquote: `.txt:75` ends `attempting`, `:76` begins `to open it`; the HTML `<p>` holds the sentence unbroken.

## 5. Defects and proposed fixes

### F1 (substantive) — S494 scope over-claims the `/detokenize` response

- Exact location: `corpus/SOURCES.md:247`, col 5 (`scope`): "documented request and response shape of the server's `/tokenize` (with `with_pieces`) and `/detokenize` endpoints at the b11909 commit".
- Command that shows it: `grep -n 'detokenize' .ufo/waves/round-49/c1/server-README-caa8191d.md` → `731:### POST \`/detokenize\`: Convert tokens to text`, `735:\`tokens\`: Set the tokens to detokenize.` Only two lines; no `Response` block.
- Why it matters: the frozen counter reads exactly that undocumented field — `tools/round49-replay-witness-audit.py:284` `post(port, "/detokenize", {"tokens": ids})["content"]`. The behaviour is real: the same commit's handler returns it (`tools/server/server-context.cpp` at `caa8191d`, fetched and hashed `61c1afcf…c61114`, `:6293` `post_detokenize`, `:6303` `res->ok(json{{"content", std::move(content)}})`), but the row as written points a reader at a document that does not contain it.
- Fix (primary): replace the row with §6 below — scope narrowed to what the README documents, anchor split at 730/731.
- Fix (alternative, if the lane wants the response licensed by a source): keep this row for `/tokenize` only and open one more row for `https://raw.githubusercontent.com/ggml-org/llama.cpp/caa8191d.../tools/server/server-context.cpp`, scope "the `post_detokenize` handler's response body (`{"content": …}`) at b11909", anchor `:6293-6305`. The counter's `newrow` leg (`tools/round49-replay-witness-audit.py:394-405`) needs only a new row containing the README URL and `/tokenize`, so it stays satisfied either way.

### F2 (substantive, both rows) — `used-by` names a knowledge file that does not use either source

- Exact location: `corpus/SOURCES.md:247` and `:248`, col 11, first path `corpus/knowledge/llamacpp-loading-lifecycle.md`.
- Command: `grep -n 'tokenize\|proc/<pid>/exe\|proc_pid_exe\|S49[0-9]' corpus/knowledge/llamacpp-loading-lifecycle.md` → only `:434` (round-47 section, S488-S490, `caa8191d` appears solely inside `build_info b11909-caa8191df`), `:436` and `:438` (round-48, S492/S493). No `/tokenize`, no `/proc/<pid>/exe`, no S494/S495.
- Note: `corpus/lessons/round-49.md` — untracked at the tip, written by the scribe seat — does use both (`:12`, `:21`, `:22`), so the second path is honest.
- Fix (a), preferred if integration appends the round-49 witness paragraph to that knowledge file: no row change; verify after the append that the paragraph names S494/S495.
- Fix (b), otherwise: drop `corpus/knowledge/llamacpp-loading-lifecycle.md,` from col 11 of both rows, leaving `corpus/lessons/round-49.md`.

### F3 (minor) — S494 anchor should say which half is documented

Covered by the replacement row: `§POST /tokenize … → Response (lines 686-730), then §POST /detokenize request options only (lines 731-735)`.

### Gate-usage note (not a row defect) — `validate --file` resolves used-by against the copy's parent-of-`corpus`

`scripts/sources-census.sh:497-502` sets `dir_abs=realpath(dirname(file)/..)` and `scripts/sources-census.sh:563-567` tests `[ ! -e "$dir/$path" ]`. A copy dropped at `<X>/SOURCES.md` gets `dir = <X>/..`; a copy at `<X>/corpus/SOURCES.md` gets `dir = <X>`, which is the lane-root convention. My first, literal run on a bare copy therefore reported 441 E11 (every used-by path "missing") and exit 1; with the used-by tree mirrored under `<X>` it reports 0 E11 and exit 0. Nothing in the two rows depends on this, but the gate is only meaningful with the tree in place.

## 6. Proposed replacement row for S494 (full text, 11 cells)

```
| S494 | llama.cpp server README at b11909 — https://raw.githubusercontent.com/ggml-org/llama.cpp/caa8191df159f764fb0160e3d2fc6be008948aee/tools/server/README.md | docs | A | documented request/response shape of the server's POST `/tokenize` (options `content`, `add_special`, `parse_special`, `with_pieces`; response `tokens` as IDs or `{id, piece}` objects, `piece` a byte list when the piece is not valid unicode) and the request option of POST `/detokenize` (`tokens`); it does not document the `/detokenize` response body, not tokenizer internals, not other releases | §POST `/tokenize`: Tokenize a given text → Response (lines 686-730), then §POST `/detokenize` request options only (lines 731-735) of the copy `.ufo/waves/round-49/c1/server-README-caa8191d.md` | "The `tokens` array contains either just token IDs or objects with `id` and `piece` fields, depending on the `with_pieces` parameter." — so an observer outside a replay can send a fresh nonce to the running server and check each returned piece against the model's own vocabulary | mined | 2026-10-26 | on-release | corpus/knowledge/llamacpp-loading-lifecycle.md, corpus/lessons/round-49.md |
```

Unchanged: id, source URL, kind, tier, teaches, status, opened, recheck, used-by. Changed: col 5 (narrowed, exclusions kept) and col 6 (span split, `/detokenize` labelled request-only).
Diff: `s494-row.diff` in this directory. Gate on the replaced copy: exit 0, findings identical to the untouched registry (93 W04 + 1 W01, no E-code) — `validate.proposed.tsv`.

S495 needs no replacement row; the only open cell (col 11) is F2, fixed by (a) or (b) above.

## 7. Gate runs

| run | command | exit | output |
|---|---|---|---|
| bare copy (`$S/bare/corpus/SOURCES.md`) | `scripts/sources-census.sh validate --file $S/bare/corpus/SOURCES.md --today 2026-10-26` | **1** | 441 E11, 93 W04, 1 W01 — all E11 are the path-base artefact (S494/S495 contribute 4: the two used-by paths each) — `validate.bare.tsv` |
| mirrored tree, untouched registry (`$S/mirror/corpus/SOURCES.md` + 64 symlinks) | same, `--file $S/mirror/corpus/SOURCES.md` | **0** | `file ok`, 93 W04, 1 W01, **0 E11** — `validate.mirror.tsv` |
| mirrored tree, proposed S494 row | same, `--file $S/mirror-proposed/corpus/SOURCES.md` | **0** | identical finding set (only the path line differs) — `validate.proposed.tsv` |

## 8. Lesson `## Gate` entries (draft)

`corpus/lessons/round-49.md` already carries a Gate table (`:19-22`) written by the scribe seat; both entries are **accurate** as filed — quotes verbatim, word counts 20 and 15, copy line counts and access time (`2026-10-26T23:11:45Z` = the copy mtimes, `20:11:45 -0300`) correct. Two edits are worth making for precision, given F1 and the S495 wrap:

| Row | Decision | URL | Opened (UTC) | Located quote (≤ 25 words) | Why |
|---|---|---|---|---|---|
| S494 | admit (tier A, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/caa8191df159f764fb0160e3d2fc6be008948aee/tools/server/README.md | 2026-10-26T23:11:45Z (copy `.ufo/waves/round-49/c1/server-README-caa8191d.md`, 2523 lines, sha256 `009af291…ac0c` = the live raw) | "The `tokens` array contains either just token IDs or objects with `id` and `piece` fields, depending on the `with_pieces` parameter." (§POST `/tokenize` → Response, line 700) | the documented surface the witness challenges — `/tokenize` request **and** response; **the README documents only the request option of `/detokenize` (lines 731-735), so the row's scope was narrowed (F1)**; pinned to b11909 = `caa8191d` (tag ref checked); the README's own example uses `tinyllama/stories260k` |
| S495 | admit (tier A, mined) | https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html | 2026-10-26T23:11:45Z (text copy `.ufo/waves/round-49/c1/proc_pid_exe.5.txt`; man-pages 6.19, page dated 2026-02-08) | "This symbolic link can be dereferenced normally; attempting to open it will open the executable." (§DESCRIPTION ¶1, copy lines 75-76; the page's hard wrap splits the sentence after "attempting") | grounds hashing `/proc/<pid>/exe` as the identity of the binary a listener runs, whatever wrapper or path started it; the scope leaves the ptrace access-mode paragraph (¶2) out |

## 9. Limits

- I did not start a llama-server, so I did not observe `/detokenize`'s `content` field live; the response shape in F1 is grounded in the pinned README (absence) and the same commit's source (`server-context.cpp:6293-6305`). The counter's own use is at `tools/round49-replay-witness-audit.py:284`.
- I did not re-run either round-49 counter; claim numbers (`witness=1 cap=1 newrow=1`, `fixture=1 lane=1`) are not re-verified here.
- The frozen copies were compared by sha256 (README) and by content/lines/colophon (man text copy vs live HTML text); I did not rebuild the man text copy from HTML, so a rendering-level difference in the `.txt` beyond the checked lines cannot be excluded.
- The lane tip moved under me: `corpus/lessons/round-49.md` appeared (untracked) while I worked; `tools/append-only-audit.py` is `M` in the working tree. Neither is mine and neither is touched.

## 10. Reproduction

```sh
S=/fast/scratch/hyaku/kama-r49/S1Rows; mkdir -p "$S"; cd "$S"
curl -sS -o raw-readme.md 'https://raw.githubusercontent.com/ggml-org/llama.cpp/caa8191df159f764fb0160e3d2fc6be008948aee/tools/server/README.md'
curl -sS -o proc_pid_exe.5.html 'https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html'
sha256sum raw-readme.md /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/c1/server-README-caa8191d.md
gh api repos/ggml-org/llama.cpp/git/ref/tags/b11909 --jq '{ref,type:.object.type,sha:.object.sha}'
grep -n 'detokenize' raw-readme.md                       # 731, 735 only
sed -n '686,737p' raw-readme.md                          # section boundaries
# gate (mirror the used-by tree first: see §7)
mkdir -p "$S/mirror/corpus"; cp /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md "$S/mirror/corpus/SOURCES.md"
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file "$S/mirror/corpus/SOURCES.md" --today 2026-10-26
```

## 11. Artifacts in this directory

`validate.bare.tsv`, `validate.mirror.tsv`, `validate.proposed.tsv`, `quote-check.txt`, `copies-check.txt`, `fetch-receipts.txt`, `gh-b11909.json`, `readme-686-737.txt`, `detokenize-handler.txt`, `s494-row.diff`.
