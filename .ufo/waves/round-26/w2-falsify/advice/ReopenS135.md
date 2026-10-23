ATTACK S135: partial — every one of the row's eleven SOURCES cells and the lesson Gate quote hold against a fresh 704366d76 fetch, but the lesson Gate's blanket "the fetched bytes equal the lane snapshot" sentence was false for S135's file at the landed tip, and three snapshot files appeared untracked in the working tree during this seat.

# Scope and method

Target: `corpus/SOURCES.md:147` (S135), `corpus/lessons/round-26.md:48` (Gate
quote), `corpus/lessons/round-26.md:13-16` (Gate sentence), routed defect 3 at
`corpus/lessons/round-25-verifier-spotcheck.md:213-216`, errata at
`corpus/knowledge/context-capacity.md:258-262`. Lane tip claimed
`f4066979096e3452ae731c0e09e50155c6d8258a`; `git rev-parse HEAD` prints exactly
that (exit 0), and `SOURCES.md` (sha256 `1e26818e85aa8e6d45fd0c6c2014f320a5b35f87a96a06e6f5d5ff47c64f8cf2`),
`SKILL.md` (`081a8d24e6522709a7540471c691f3dc36e1acb85ee4bc73da4ceecaee2bedca`) and
`corpus/lessons/round-26.md` (`dbb69c042b5ed547fffd43845546f113301edc794532354965636a68153722fe`)
are byte-identical to the receipt's measured scratch tree
`/fast/scratch/hyaku/kama-r26/tip-7e5ff9b5454dd27f0520cb36a3cbc3a995e48162`
(sha256sum output, exit 0). The landed-tip receipt therefore applies to the same
lesson/row bytes I checked.

Fresh fetches (access date 2026-10-23), all from commit
`704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`:

- `curl -sS -L https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-kv-cache.cpp`
  → `http=200 size=98638`; sha256 `d0739eaf00d8457f4109a616e0beb1cf07ea074c9b460d92a7b6d48c4519d294`, 2962 lines.
- A second raw fetch of the same URL → same sha256; `cmp` with the first fetch exit 0 (identical).
- `https://codeload.github.com/ggml-org/llama.cpp/tar.gz/704366d76...` → `http=200 bytes=38390537`;
  `src/llama-kv-cache.cpp` in the extracted commit tree → same sha256; `cmp` with the raw fetch exit 0.
- `git ls-remote --tags https://github.com/ggml-org/llama.cpp 'refs/tags/b11755*'`
  → `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad	refs/tags/b11755`, exit 0. The "release b11755"
  label attached to this commit in S113/S135 is exact.

No `lsp` device is exposed to this seat; all source and table checks are literal
grep/sed on the fresh bytes and file reads, not semantic-server proof. No
llama-server was started (this item names no port block) and none is mine:
`pgrep -af llama-server` → no output (`|| echo none` printed `none`). The frozen
counter was not run: S135 is a KQ31 supersession row, not a counted signature row,
and the counter needs a server.

# Per-cell verdict (`corpus/SOURCES.md:147`)

Column order (`corpus/SOURCES.md:11`): id | source | kind | tier | scope | anchor |
teaches | status | opened | recheck | used-by.

| cell | verdict | proof (exact output) |
|---|---|---|
| id `S135` | holds | `grep -n "^| S135 " corpus/SOURCES.md` → `147:| S135 |`; `grep -c "S135"` on `git show 1560e4d8:corpus/SOURCES.md` → `0` (grep exit 1), so the id is new at base. |
| source | holds | URL `.../704366d76.../src/llama-kv-cache.cpp` → HTTP 200, 98638 bytes; commit prefix `704366d76` matches the 40-hex commit; path exists in the commit tarball. |
| kind `code` | holds | primary C++ source, not docs; matches S113. |
| tier `A` | holds | immutable pinned upstream source, directly read. |
| scope | holds | "not how kv_size derives from n_ctx": `grep -n "n_ctx" src/llama-kv-cache.cpp` shows only `n_ctx_orig_yarn` at 1952, 1977, 1987 (YaRN); `kv_size` is a constructor parameter at line 73 and the derivation lives in callers (e.g. `src/llama-kv-cache-iswa.cpp:69,95-98,102-105`). |
| anchor "stream count 84" | holds | `grep -n "n_stream(unified ? 1 : n_seq_max)"` → `84:    n_seq_max(n_seq_max), n_stream(unified ? 1 : n_seq_max), ...`. |
| anchor "per-stream cells 142-145" | holds | `sed -n '142,145p'` → `142 v_cells.resize(n_stream);` / `143 for (uint32_t s = 0; s < n_stream; ++s) {` / `144 v_cells[s].resize(kv_size);` / `145 }`. |
| anchor "per-layer K/V tensor dimensions 233-234" | holds | `sed -n '233,234p'` → `ggml_new_tensor_3d(ctx, type_k, n_embd_k_gqa, kv_size, n_stream)` and the type_v twin (both inside the per-`il` loop). |
| anchor "size log 301-304" | holds | `sed -n '301,304p'` → one `LLAMA_LOG_INFO` statement, lines 301-304 exactly. |
| anchor "raw sha256 d0739eaf…d294" | holds | three independent fetches (raw ×2, codeload tarball) and the current lane snapshot file all hash to `d0739eaf00d8457f4109a616e0beb1cf07ea074c9b460d92a7b6d48c4519d294`; `cmp -s` lane-snapshot vs fresh → exit 0, "snapshot==fresh". |
| teaches prefix `supersedes S113 —` | holds | exact cell starts `supersedes S113 ` then bytes `342 200 224` (U+2014 em dash) then ` each`; `grep -c "supersedes S113" corpus/SOURCES.md` → `1`. |
| teaches "each stream has kv_size cells (142-145)" | holds | same 142-145 lines above. |
| teaches dims "(embedding, kv_size, n_stream)" and product | holds, low nit F3 | 233-234 give `(n_embd_k_gqa, kv_size, n_stream)` / `(n_embd_v_gqa, kv_size, n_stream)`; per-tensor cell axis is `kv_size × n_stream`. |
| teaches "total K+V MiB" | holds | log arg 1 at 302 is `(float)(memory_size_k + memory_size_v) / (1024*1024)`; `size_k_bytes`/`size_v_bytes` sum `ggml_nbytes(layer.k/.v)` over all layers (`src/llama-kv-cache.cpp:1922-1940`). |
| teaches "kv_size in its cells field" | holds | arg list at 302: `..., kv_size, (int) layers.size(), n_seq_max, n_stream,`. |
| teaches "layers.size() in its layers field" | holds | format `%3d layers`, arg `(int) layers.size()` at 301-302. |
| teaches "n_seq_max/n_stream as seq counts" | holds | format `%2u/%u seqs`, args `n_seq_max, n_stream` at 301-302. |
| teaches "does not print the product" | holds | neither the format string nor the eight arguments at 301-304 contain the product; it prints kv_size and the seq pair separately. |
| teaches "shared-source cache may override kv_size (93-97)" | holds, low nit F2 | `sed -n '92,97p'` → `92 if (other) {` / `93 size_other = other->get_size();` / `94 if (kv_size != size_other) {` / `95 warn` / `96 kv_size = size_other;` / `97 }`; the override statement is at 96, inside the cited range, but the guard is at 92. |
| status `mined` | holds | matches S113 and S131-S134. |
| opened `2026-10-23` | holds | today's date at access. |
| recheck `on-release` | holds | matches S113's policy. |
| used-by | holds | `corpus/knowledge/context-capacity.md:258` names S135; `corpus/lessons/round-26.md:19` and `:48` name it. |

KQ31 form and routed defect:

- New row, old row intact: `git show 1560e4d8:corpus/SOURCES.md` vs `corpus/SOURCES.md`
  for `^| S113 ` → both at line 125, `diff` exit 0 ("S113 row identical"). The
  round-25 errata at `context-capacity.md:258-262` is appended, not a rewrite
  ("The old rows stay as written.").
- Defect 3: `corpus/lessons/round-25-verifier-spotcheck.md:213-216` routes
  "`supersedes` rows (KQ31) for S106 … Do the same for S109 (the idle-slot purge
  precondition) and S113 ("per layer")". The round-26 errata says the S135 row
  corrects "the per-layer wording of the size log (S113)"
  (`context-capacity.md:258-262`). S135's new content is exactly that
  disambiguation: it says the log prints `kv_size` in the cells field and does not
  print `kv_size × n_stream` as a per-layer total. **[INFERENCE]** the spot-check
  gives only the parenthetical "per layer", so this is a judgement that the row
  matches its intent; nothing in the row contradicts it. S113's assertions were not
  false, so this is a wording correction, consistent with the spot-check calling
  these "wording defects" (`:191`).

Gate quote:

- `corpus/lessons/round-26.md:48` carries the URL `...#L301` and the quote
  `(%6u cells, %3d layers, %2u/%u seqs)`; `grep -nF` of that string returns only
  `301:` in both the fresh fetch and the current lane snapshot (exit 0), so it is
  located and unique at line 301; Python `len(quote.split())` → `6` (well under 25).
- The quote is an interior fragment of line 301 (not a line prefix), but it is
  verbatim and on the cited line; the table's own rule is "the source line, cut to
  at most 25 words".

# Findings

## F1 — defect (medium): lesson Gate claims snapshot equality that the landed tree did not have for S135

`corpus/lessons/round-26.md:13-16`: "Every row below was opened … from a fresh
fetch at llama.cpp commit 704366d76…; the fetched bytes equal the lane snapshot
`.ufo/waves/round-26/sources/llama.cpp-704366d/` (sha256 in each row's anchor
cell; …)". "Every row below" includes S135.

At the landed tip that sentence was false for S135's file:

- `git ls-tree -r --name-only <rev> -- .ufo/waves/round-26/sources/llama.cpp-704366d/ | wc -l`
  → `13` for `7f84cd0` (C1/lesson landing commit), `7e5ff9b` (the receipt's
  measured tip) and `f406697` (lane tip). The 13 names contain no
  `llama-kv-cache.cpp`.
- The receipt's own scratch tree has the same 13 files
  (`ls -1 /fast/scratch/hyaku/kama-r26/tip-7e5ff9b…/…/llama.cpp-704366d/ | wc -l` → `13`).
- `git log --all --oneline -- '.ufo/waves/round-26/sources/llama.cpp-704366d/llama-kv-cache.cpp'`
  → no output (exit 0): the file was never in a commit at that path.
- Wave-1's own drafter recorded the hole:
  `.ufo/waves/round-26/w1-build/advice/ScribeSupersedes.md` — "The final checks
  printed `fit.cpp snapshot missing`, `llama-kv-cache.cpp snapshot missing`,
  `README.md snapshot missing` … This report does not claim those comparisons passed."
- The 17 counted rows are unaffected: every file cited by S114-S130 is present in
  the 13-file snapshot (per-row basename check, exit 0), so `counted 17` does not
  depend on the missing supersession files.

Corroboration (peer seats, not my evidence): `ReopenS131.md:97-140` and
`ReopenS134.md:98-112` report the same Gate sentence false for S131/S134;
`ReopenS132.md:32-34` reports it true for S132 (file present).

Live change during this seat (observed, not made by me): three files appeared in
the lane snapshot directory **untracked** at `2026-10-23 01:01:39 -0300`
(04:01:39Z), after my first listing (13 files, mtimes 00:16:59) and before this
report:

```
-rw-r--r-- 119661 2026-10-23 01:01:39.108448899 -0300 README.md
-rw-r--r--  52124 2026-10-23 01:01:39.062448697 -0300 fit.cpp
-rw-r--r--  98638 2026-10-23 01:01:39.086448803 -0300 llama-kv-cache.cpp
```

`git status --porcelain` shows them as `??`; `git ls-files --error-unmatch` on
`llama-kv-cache.cpp` exits 1. Their sha256 match the pinned values
(`1f83da2a…dd58`, `714c067b…6a37`, `d0739eaf…d294`), and `cmp` against the fresh
fetch exits 0. They postdate the 00:51 receipt and are not in any commit, so the
landed tip still does not carry them. I did not write them; all this seat's writes
went to `/fast/scratch/hyaku/kama-r26w2/ReopenS135/`. Attribution is unresolved.

Smallest correction (pick one, then re-check):

1. Commit `llama-kv-cache.cpp`, `fit.cpp` and `README.md` into the snapshot with a
   disclosed later-change note (KQ36 "landed tip" definition), and re-run/annotate
   the C1/C2 receipt so the measured bytes are the committed ones; or
2. Narrow `corpus/lessons/round-26.md:14-15` to what held at landing, e.g. "the
   fetched bytes equal the lane snapshot for the files the snapshot holds
   (`llama-context.cpp`, `server-context.cpp`, …); `fit.cpp`, `README.md` and
   `llama-kv-cache.cpp` are pinned by the sha256 in their rows' anchor cells only".

## F2 — low nit: the override citation drops the guard line

`corpus/SOURCES.md:147` teaches: "A shared-source cache may override kv_size
(93-97)." Lines 93-97 show the override body, but the precondition `if (other) {`
is line 92. S113's own anchor cell already cites "shared-source override 92-97".
Smallest correction: change `(93-97)` to `(92-97)`.

## F3 — low nit (inherited from S113): "K/V tensors" on MLA layers

`src/llama-kv-cache.cpp:231` `const bool has_v = !is_mla;` and `:233-234` create
V only when `has_v`; `:163` sets `is_mla = hparams.is_mla()`. On an MLA model the
cache has no V tensor, so "each layer's K/V tensors have dimensions …" is an
overgeneralisation; and "embedding" is shorthand for `n_embd_k_gqa` /
`n_embd_v_gqa` (the GQA-grouped K/V width, not necessarily the model `n_embd`).
Smallest correction: "each layer's K tensor (and its V tensor except on MLA
layers) has dimensions `(n_embd_k_gqa`, resp. `n_embd_v_gqa, kv_size, n_stream)`".
This does not change the row's substantive point and is inherited from S113.

# Verdict summary

- S135 row cells: **all hold** (F2/F3 are nits, not false statements that affect
  the correction).
- KQ31 form: **holds** (new row, prefix exact, old S113 row byte-identical to base).
- Routed defect 3 match: **holds** with the `[INFERENCE]` noted.
- Gate quote at `round-26.md:48`: **holds** (6 words, unique at line 301).
- Lesson Gate sentence at `round-26.md:13-16`: **does not hold for S135 at the
  landed tip** (F1); the current working tree masks it only through three
  uncommitted, untracked files added mid-seat.

# Remaining unknowns

- Who wrote the three untracked snapshot files at 04:01:39Z, and whether the lane
  will commit them or revert them. Until then the Gate sentence is true only of
  uncommitted working-tree bytes.
- Whether defect 3's intended S113 fix was exactly this log-field disambiguation;
  the spot-check supplies only the parenthetical "per layer" (`:216`), so F1's
  match judgement is labelled `[INFERENCE]`.

# Files written

Lane (report only):
- `.ufo/waves/round-26/w2-falsify/advice/ReopenS135.md`

Scratch (`/fast/scratch/hyaku/kama-r26w2/ReopenS135/`):
- `llama-kv-cache.cpp`, `llama-kv-cache.2.cpp`, `llama-kv-cache.h`
- `src.tar.gz` (codeload commit tarball), extracted tree `llama.cpp-704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/`
- `src-list.json`, `SOURCES.base.md`, `s113.base.txt`, `s113.now.txt`, `evidence.txt`

No tools were installed. No sandbox git was created; only read-only
`git show`/`ls-tree`/`ls-files`/`log`/`ls-remote`/`status` were used in the lane.
One stray typo-path write of a placeholder outside the lane
(`/home/vgpnk/Projects/shoukounin/...`, caused by a misspelled lane path) was
removed immediately in the same step; `ls` on that path now fails, exit 2.
