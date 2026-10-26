# S1Section — round-46 `corpus/SOURCES.md` section draft (C1, freshness)

Verdict: section drafted and pre-flighted against the frozen C1 parser; the brief's byte-identity census is wrong — the measured split is **73 byte-identical / 18 changed files**, plus the 3 byte-identical `server.cpp` rows re-read for their b11889 `holds-reworded` state = **21 rows to read**, not 71/20 (S479, `tools/server/server-models.cpp`, is the changed-file row the brief's 20-row list omits).

## Deliverable

`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S1Section/section.md` (62 lines, 11416 bytes; 51 non-blank). Modelled on the round-44 section at `corpus/SOURCES.md:498-504`. Contains, in order: heading `## Round-46 release re-verification (llama.cpp b11906, appended 2026-10-26)`; trigger (pin still b11755, ls-remote line 1428, release JSON fields); population (91 rows, frozen in the preregistration); release row (new registry row above S485, the counter's newrow leg); ledger header + verdict definitions; the machine-witness rule (`witness_pin` / `witness_new`, `ws` collapse, >= 12 chars, pin-only / release-only, note >= 40); the 73 byte-identical rows grouped by file (14 files); the changed-file census; a 21-row verdict table with empty `b11906 verdict / witness / note` cells; the used-by file map; the append-only flag sentence template; closing (recheck cells stay `on-release`, live re-run outside the population, frontier b11907).

Integration: append the file verbatim after the round-45 section (`corpus/SOURCES.md:506` onward, currently the last section) and land the b11906 registry row. The counter's section leg is `tools/round46-release-recheck-audit.py:351-355` (`section` must be a `#` line containing `Round-46 release re-verification`); its flag leg (`:359-375`) needs one section line per drifted/removed id and a `<id>` + `b11906` line in each `corpus/knowledge/*.md` used-by; its newrow leg (`:357-359`) needs a `| S### ` row absent at base whose line carries both `b11906` and `4d71b42fd87db24b8b7c808c151b713aa4459cfd`.

Table ids are wrapped in backticks on purpose: `scripts/sources-census.sh:619` flags any line matching `^\|[ \t]*S[0-9]{3,}[ \t]*\|` outside `## Registry` as E12, and the round-45 table (`corpus/SOURCES.md:512-522`) uses the same escape. The C1 `ROW` regex (`tools/round46-release-recheck-audit.py`, `ROW`) also matches nothing in the draft, so the table cannot fake a population row or the newrow leg.

## Evidence

All commands read-only; cwd `/home/vgpnk/Projects/shokunin/kama-shokunin` unless noted. No clone was created (the shared bare clone `/fast/scratch/hyaku/kama-r46/L1/llama.git` holds every pin, b11889 and b11906). Scratch `/fast/scratch/hyaku/kama-r46/S1Section` removed after use.

Population is the frozen one, re-derived from base bytes (not trusted from the brief):

```
$ git show 0163fea2dab3f282ebd70c71da9ab5de4cedf733:corpus/SOURCES.md > $S/SOURCES.base.md      # exit 0
$ python3 -c "import importlib.util; spec=...('c1','tools/round46-release-recheck-audit.py'); m=...;
  pop=m.population(open('$S/SOURCES.base.md').read())"
pop 91 prereg 91 ids equal: True
diff: [] []
pins: Counter({'704366d76f8748cf9ad3df62a464bfcc8d1ae6ad': 89, 'c0fd78626405c6d9b934efef0ec7291fcc20e3d6': 1, 'ad1b88ca0d37a2171efba1c04f1a3531c78f1b52': 1})
paths: 16 distinct (server-schema.cpp 36, server-context.cpp 17, server-common.cpp 13, server/README.md 4, server.cpp 3, ...)
```

Byte census, all 91 population paths (`registry/release-recheck-b11889.tsv` supplies id/path), both sides via `git -C <bare> rev-parse <commit>:<path>`:

```
total 91 same 73 diff 18
DIFF rows: S042 S060 S109 S114 S115 S116 S117 S118 S119 S120 S121 S122 S123 S124 S125 S133 S138 S479
```

which is 17 rows on `tools/server/server-context.cpp` + 1 on `tools/server/server-models.cpp`, exactly the prereg's "18 population rows' files changed since b11889". Identical groups (14 files, 73 rows): server-schema.cpp 36 (S140–S173, S190, S191); server-common.cpp 13 (S126, S127, S137, S180–S189); server/README.md 4 (S001, S035, S112, S134); server.cpp 3 (S037, S043, S108); arg.cpp 3 (S054, S056, S110); llama-context.cpp 3 (S107, S130, S132); fit.cpp 2 (S106, S131); llama-kv-cache.cpp 2 (S113, S135); gguf.cpp 2 (S128, S129); gguf_reader.py S059; common.cpp S111; quantize/README.md S015; server-http.cpp S036; server-queue.cpp S047. Machine-readable copy: `.../out/S1Section/census.tsv` (91 rows, id/path/pin_commit/blob_b11889/blob_b11906/file_identical; `awk -F'\t' 'NR>1&&$6==\"1\"' | wc -l` = 73, the `0` rows print the 18 ids above).

Release facts cited in the draft, each read from a lane receipt or the bare clone:

```
$ git -C <bare> rev-list --count d854d98bae598388ecea1ed84396587e5edc326d..4d71b42fd87db24b8b7c808c151b713aa4459cfd
17
$ wc -l .ufo/waves/round-46/c1/ls-remote-llama.cpp.txt        # 8211
$ grep -n "b1190[67]" .ufo/waves/round-46/c1/ls-remote-llama.cpp.txt
1428:4d71b42fd87db24b8b7c808c151b713aa4459cfd	refs/tags/b11906
1429:4b851fbee8867136a0c561c8a3521f2fe7d53252	refs/tags/b11907
$ sha256sum .ufo/waves/round-46/c1/release-b11906.json
b9041d4af30892fea64767acdcc3de5b9452a2d01f0b0e6fedef6c18976da6d7   (69164 bytes)
   tag_name=b11906 target_commitish=4d71b42fd87db24b8b7c808c151b713aa4459cfd
   published_at=2026-10-26T19:45:36Z prerelease=True draft=False assets=36
```

Diff shape quoted in the draft (`git -C <bare> diff -U0 d854..4d71 -- tools/server/server-context.cpp tools/server/server-models.cpp`, exit 0):

```
server-context.cpp hunks: -1014,0 +1015,1 | -1020,1 +1021,1 | -1024,1 +1025,1 | -1399,0 +1401,2 | -1708,3 +1711,3 | -5130,1 +5133,1
deleted old lines [1020, 1024, 1708, 1709, 1710, 5130]  additions 9   (7070 -> 7073 lines, net +3)
server-models.cpp hunk: -536,1 +536,1   (2931 lines both)
```
The 3-line commit pair is the mtmd capability refactor `c6fb3b5b` "mtmd: add mtmd_helper_get_capabilities (#31183)" (`.ufo/waves/round-46/c1/commits-b11889-b11906.txt`): `has_cap_tts`, `has_cap_chat`, `allow_image/audio/video`, `has_audio_stream` now read `mtmd_cap` from `mtmd_helper_get_capabilities(model_tgt, mctx)`; `server-models.cpp:536` only renames the comment that cites the helper. Checked that no population row's b11889 anchored ranges intersect a deleted line (a set intersection over the 18 changed rows: every hit list empty, `-`), and that no population row's source/anchor/teaches cell names the refactored helpers (token search over cells 1/5/6/10 for mtmd/audio/vision/tts/capab/chat: only S125, via its "no multimodal projector or audio is not allowed" teaches text).

Pre-flight of the draft against the frozen parser (import of the frozen module, no clone, exit 0):

```
section heading ok: True   heading: ['## Round-46 release re-verification (llama.cpp b11906, appended 2026-10-26)']
ROW matches (must be none): []
ids missing from section body: []
header quote has 13 cols: True      # literal tabs in the ledger header sentence, verified with cat -A
```

b11889 verdict baseline used by the table (`registry/release-recheck-b11889.tsv`, 92 lines = header + 91): unchanged-file 6 (`S015 S059 S106 S128 S129 S131`), holds 82, holds-reworded 3 (`S037 S043 S108`). Cross-check for the 73 identical rows: 6 + 64 + 3 = 73, so the draft says "64 holds" for the identical set, not 67.

Live re-run cited in the closing paragraph (another seat's receipts, read not re-run): `.ufo/waves/round-46/c1/live/receipt-{1,2,3}.json`, `outcome=pass`, 11/11 checks each (`health_ready … model_unchanged`), `llama-server` sha256 `c949950e…ac3ff`, asset digest `sha256:064ade62…eef3` (`live/install.txt`), model re-fetched with sha256 `270cba1b…bd256d` equal to S485's (`live/model-fetch.txt`).

## Findings

1. **Census in the seat brief is off by two rows (affects which rows get read).** Brief: "71 rows' files are byte-identical … 20 rows need reading". Measured with the brief's own command: 73 identical, 18 changed, and the brief's 20-row list omits `S479` (`tools/server/server-models.cpp`), whose blobs are `e1e006f1018fdcfd76f9f20f5a1a638c7f3245d6` (b11889) vs `5751401328682cfaae705b57536778566885e7ce` (b11906) — `git -C /fast/scratch/hyaku/kama-r46/L1/llama.git rev-parse d854d98b…:tools/server/server-models.cpp 4d71b42f…:tools/server/server-models.cpp`. The prereg itself says "18 population rows' files changed", so the brief, not the prereg, is the discordant source. Proposed read set: the 18 changed-file rows **plus** S037/S043/S108 = 21 (the draft's table). Leaving S479 unread still needs a ledger row whose ranges re-derive at b11906 (`changed=1`, text-equal pairs against the renamed comment at 536); the file's only delta is that comment line.
2. **The 71/20 arithmetic cannot be right under any reading**: 91 − 20 = 71 assumes 20 changed files, but only 18 files changed and three of the 20 listed rows (`S037`, `S043`, `S108`) sit on the byte-identical `server.cpp`. Both halves of the brief's split are inconsistent with the bytes.
3. **b11907 is already tagged at the same sample** while the prereg's `release.observed` says "highest bN tag b11906" at freeze: `.ufo/waves/round-46/c1/ls-remote-llama.cpp.txt:1429` carries `4b851fbee8867136a0c561c8a3521f2fe7d53252 refs/tags/b11907`, captured 2026-10-26T19:57:59Z (7 min after the 19:50:02Z freeze). Not a defect for C1 (the claim pins b11906 and the tag exists); the draft records b11907 as frontier. Do not widen the claim to b11907 — its commit is not in the bare clone (`git tag -l b11907` empty).
4. **S125's b11889 support note is stale at b11906**: `registry/release-recheck-b11889.tsv:33` argues `chat_params.allow_audio is still mctx ? mtmd_support_audio(mctx) : false (pin 1632, release 1709)`, and release line 1709 is one of the six replaced lines (now `mtmd_cap.audio`). S125's anchored range (b11889 5969-5975) is untouched, so the counter will accept `holds`, but the note's claim about the guard expression no longer describes b11906. The reading seat for S125 should land `holds` with a note that restates the condition via `mtmd_cap.audio`; a `drifted` there would be honest only if the teaches sentence itself moved (it does not).
5. **Counter flag leg cannot see the lane's real users of S114–S125**: `tools/round46-release-recheck-audit.py:368` only matches `corpus/knowledge/[\w.\-]+\.md`, while those twelve rows are used by `SKILL.md` and `registry/error-signatures-r26.json` (base registry, used-by cells). A `drifted`/`removed` verdict there would satisfy the counter with just the SOURCES table line and leave the lane's actual consumers unflagged. The draft's flag paragraph says "flagged by hand"; a later round should extend the regex (frozen counter here — finding only).
6. **No E12/newrow hazard from the draft's table** (`scripts/sources-census.sh:619` vs the frozen `ROW`): verified by simulation above. If any later editor un-backticks the ids in that table, the census will read 21 phantom registry rows outside `## Registry` and C1's newrow leg could match one of them.

## Out of scope (not done, by seat bounds)

- No ledger row, no verdict, no witness: `registry/release-recheck-b11906.tsv` is the read seats' + L1's artifact. Nothing here decides a row's b11906 verdict.
- No edit to `corpus/SOURCES.md`, `corpus/knowledge/*.md`, `SKILL.md`, `registry/`, counters, preregistration or controls; the section is a proposal file only. No flags were appended anywhere.
- No new registry row for b11906 (the draft states the requirement; landing it is the L1's append).
- No re-run of the b11906 live receipts, no re-fetch, no tool install, no pacman, no service start/stop, no subagent, no `agent://all`.
- No verification of the final lane tip (impossible without the ledger); the C1 counter must be run by the L1 after integration.

## Artifacts

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S1Section/section.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S1Section/census.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S1Section.md` (this report)
