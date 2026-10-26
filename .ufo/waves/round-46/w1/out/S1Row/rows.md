# Round-46 registry rows for `corpus/SOURCES.md` — seat S1Row

**Verdict: two rows drafted and machine-validated — S486 (llama.cpp release b11906 identity, docs/A) and S487 (kama live
lifecycle receipts at b11906, own-work/A); both pass the frozen census on a scratch copy of `SOURCES.md` (exit 0,
`file ok`, findings byte-identical to the lane baseline), and S486 satisfies the frozen C1 counter's newrow leg
(`newrow=1`). Ids are proposals: the L1 assigns `S4NN`.**

Lane tip read: `0163fea2dab3f282ebd70c71da9ab5de4cedf733` working tree; `corpus/SOURCES.md` = 524 lines, registry table
11–238 (S001 at line 11, S485 at line 238), `## Paths` at line 240.

## 1. Insertion point

Insert both rows **after line 238 (`| S485 …`) and before the blank line 239**, i.e. inside the `## Registry` table.
Appending at the file tail is rejected: the control below puts the two rows after line 524 and the census prints
`E12 S486 row outside Registry section` / `E12 S487 row outside Registry section` (exit 1).

Both rows are single physical lines (Markdown table rows) and contain no `|` inside a cell; the parser is
`gawk -F'|'` (`scripts/sources-census.sh:582`), so a pipe in prose silently shifts every cell.

## 2. Row `S486` — llama.cpp release b11906 identity (model: S484/S482)

Full row (11 cells):

```
| S486 | llama.cpp release b11906 Linux x64 CPU binary — https://github.com/ggml-org/llama.cpp/releases/download/b11906/llama-b11906-bin-ubuntu-x64.tar.gz (asset record: https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/b11906) | docs | A | identity of the official b11906 Linux x64 CPU binary kama ran in round 46 and the commit its tag names; not runtime behaviour, not performance, not any later release | tag b11906 = 4d71b42fd87db24b8b7c808c151b713aa4459cfd (`git ls-remote --tags` refs/tags/b11906, 17 commits after b11889 d854d98bae598388ecea1ed84396587e5edc326d); release JSON `"target_commitish":"4d71b42fd87db24b8b7c808c151b713aa4459cfd"`, `"published_at":"2026-10-26T19:45:36Z"`, `"prerelease":true`; asset `llama-b11906-bin-ubuntu-x64.tar.gz` size 22478121, digest sha256:064ade6220799fd9e7b1804b574f5f92c38dde358cc987c6b8283cfaeb1eeef3; downloaded 2026-10-26 and sha256sum equal to the digest; extracted `llama-server` sha256 c949950ee76bf84e0dc8f537a98a2c702169f09b5a061c27c87edff753fac3ff and `libllama-server-impl.so` sha256 682717ba312caefda06be7b2e5a637d8af357ff1f1264f6f5624dc53212a8223; `--version` line `0.7.0-dev (build 11906, commit 4d71b42fd)` (`.ufo/waves/round-46/c1/live/install.txt`; release JSON `.ufo/waves/round-46/c1/release-b11906.json` sha256 b9041d4af30892fea64767acdcc3de5b9452a2d01f0b0e6fedef6c18976da6d7) | Ties the round-46 live receipts to one GitHub-computed asset digest and one server binary hash; b11906 is Pre-release and mutable, so cite the digest, not the tag alone. | mined | 2026-10-26 | on-release | corpus/knowledge/llamacpp-loading-lifecycle.md |
```

| cell | value |
|---|---|
| 1 id | `S486` (next free id at tip; S485 is the highest) |
| 2 source | llama.cpp release b11906 asset URL + `api.github.com` asset record |
| 3 kind | `docs` |
| 4 tier | `A` |
| 5 scope | identity of the official b11906 Linux x64 CPU binary and the commit its tag names; not runtime behaviour, not performance, not any later release |
| 6 anchor | tag→commit from `git ls-remote`, release JSON fields, asset size/digest, both extracted binary digests, `--version` line, evidence paths |
| 7 teaches | ties the round-46 live receipts to one GitHub-computed asset digest and one `llama-server` hash |
| 8 status | `mined` |
| 9 opened | `2026-10-26` |
| 10 recheck | `on-release` (same cadence as S482/S484) |
| 11 used-by | `corpus/knowledge/llamacpp-loading-lifecycle.md` (line 432 of that file is where S484/S485 are used; the round-46 paragraph is the same place) |

**Located quote (2 words, ≤ 25):** `"target_commitish":"4d71b42fd87db24b8b7c808c151b713aa4459cfd"` — location
`.ufo/waves/round-46/c1/release-b11906.json`, top-level `target_commitish` field (compact JSON, 69164 bytes, sha256
`b9041d4af30892fea64767acdcc3de5b9452a2d01f0b0e6fedef6c18976da6d7`). My own `gh api
repos/ggml-org/llama.cpp/releases/tags/b11906` fetch produced the same 69164 bytes and the same sha256, so the record is
reproducible, not just relayed.

The row satisfies the frozen C1 counter's newrow rule
(`tools/round46-release-recheck-audit.py:78-80`, `:355-357`): it is a `| S###` row whose id is absent at base, and the
line contains both `b11906` and `4d71b42fd87db24b8b7c808c151b713aa4459cfd`. Evaluated with the counter's own `ROW`,
`RELEASE`, `RELEASE_COMMIT` and base tree: `newrow 1 ids ['S486']`. (The counter's `section` leg is the C1
re-verification heading, which is the L1's, not this row's: `section=0` at the scratch copy because no
`## Round-46 release re-verification` heading exists yet.)

## 3. Row `S487` — kama live lifecycle receipts at b11906 (model: S485)

Full row (11 cells):

```
| S487 | kama live llama.cpp lifecycle receipts at b11906 — `python3 tools/kama-llamacpp-live.py` (raw receipts `.ufo/waves/round-46/c1/live/receipt-1.json`, `-2.json`, `-3.json`) | own-work | A | three lane-owned b11906 runs on unregistered loopback ports at sampled instants, one model; not registered-consumer health, model quality, other builds or general timing | receipts kama-llamacpp-live/v3 2026-10-26T19:57:39.317Z–19:57:39.474Z, 19:57:39.532Z–19:57:39.691Z and 19:57:39.745Z–19:57:39.905Z, ports 33179, 46073, 44923; server sha256 c949950ee76bf84e0dc8f537a98a2c702169f09b5a061c27c87edff753fac3ff (S486), build_info b11906-4d71b42fd at `captures.props.fields`; alias kama-r46-live; model stories260K.gguf sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d; tool sha256 8c0dbb2b60da4d0e89ebe537b2f36b0b59356efedbe5f66c7364bdb6c8f662f3; probe sha256 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3; receipt sha256 9ad6ad36501f80a4ca3adef10275865a5faa401bfd57db0959bd243eda977e26, 09f049cff08b2d27a74f205db313dfdefb808740546e74d607414551c262562a, 33f1dd57e9f8a24c39718b4ffd5aef0936cdd395893c281c5c15c9aedae46632; model re-fetched 2026-10-26T19:57:36Z (`.ufo/waves/round-46/c1/live/model-fetch.txt`) | The S041, S046 and S055 lifecycle statements hold on b11906: each run's one loading 503 body is the exact envelope, the ready /health body is {"status":"ok"}, /v1/models id = alias with owned_by llamacpp, /metrics 501, probe grades MODEL_OK and MODEL_MISMATCH, all 11 checks passed, and SIGTERM teardown ends returncode 0 with no SIGKILL. | mined | 2026-10-26 | on-release | corpus/knowledge/llamacpp-loading-lifecycle.md |
```

| cell | value |
|---|---|
| 1 id | `S487` (next free after S486) |
| 2 source | `python3 tools/kama-llamacpp-live.py` + the three raw receipts |
| 3 kind | `own-work` |
| 4 tier | `A` |
| 5 scope | three lane-owned b11906 runs on unregistered loopback ports at sampled instants, one model; not registered-consumer health, model quality, other builds or general timing |
| 6 anchor | per-run windows and ports, server sha256, `build_info`, alias, model/tool/probe/receipt sha256s, model re-fetch note |
| 7 teaches | the S041/S046/S055 lifecycle statements hold on b11906, with the graded counts |
| 8 status | `mined` |
| 9 opened | `2026-10-26` |
| 10 recheck | `on-release` |
| 11 used-by | `corpus/knowledge/llamacpp-loading-lifecycle.md` |

**Located quote (1 word, ≤ 25):** `{"status":"ok"}` — location `.ufo/waves/round-46/c1/live/receipt-1.json`,
`captures.health.body` (identical in `receipt-2.json` and `receipt-3.json`).
**Second located quote (7 tokens, ≤ 25):** `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`
— location `captures.loading_503.body`, one body per run (`loading_503_bodies` length 1 in all three, `envelope_exact`
true in all three).

Facts behind the teaches cell, re-derived by `derive-row-facts.py` (in this directory, output below): all three receipts
`outcome=pass`, `11 of 11` checks passed, `build_info b11906-4d71b42fd`, alias `kama-r46-live`, `/metrics` 501,
`/v1/models` `owned_by` `llamacpp` (`captures.models.body`), teardown `returncode 0`, `sigkill_sent false`,
`term_wait_ms 3`. Unlike S485 (24/8/16 loading repeats) the round-46 runs observed **one** loading 503 body each, so the
row says "each run's one loading 503 body" rather than carrying S485's repeat counts forward.

## 4. Placeholder variant of `S487` (per the seat item)

If the live run is repeated before the L1 appends (a second executor, a re-run, or a replaced install), the row text must
be re-derived from the final receipt bytes. This variant is the placeholder form the seat item asks for:

```
| S4NN | kama live llama.cpp lifecycle receipts at b11906 — `python3 tools/kama-llamacpp-live.py` (raw receipts `.ufo/waves/round-46/c1/live/receipt-1.json`, `-2.json`, `-3.json`) | own-work | A | three lane-owned b11906 runs on unregistered loopback ports at sampled instants, one model; not registered-consumer health, model quality, other builds or general timing | receipts kama-llamacpp-live/v3 {{STARTED_UTC}}–{{ENDED_UTC}} with ports {{PORT1}}, {{PORT2}}, {{PORT3}}; server sha256 {{SERVER_SHA256}} ({{RELEASE_ROW_ID}}); build_info {{BUILD_INFO}} at `captures.props.fields`; alias {{ALIAS}}; model stories260K.gguf sha256 {{MODEL_SHA256}}; tool sha256 {{TOOL_SHA256}}; probe sha256 {{PROBE_SHA256}}; receipt sha256 {{RECEIPT1_SHA256}}, {{RECEIPT2_SHA256}}, {{RECEIPT3_SHA256}} | {{TEACHES}} | mined | {{OPENED}} | on-release | corpus/knowledge/llamacpp-loading-lifecycle.md |
```

Substitutions as of the receipts read by this seat (2026-10-26T19:57:39Z):

| placeholder | value |
|---|---|
| `{{STARTED_UTC}}` | `2026-10-26T19:57:39.317Z` |
| `{{ENDED_UTC}}` | `2026-10-26T19:57:39.905Z` (receipt-3 end) |
| `{{PORT1}}` / `{{PORT2}}` / `{{PORT3}}` | `33179` / `46073` / `44923` |
| `{{SERVER_SHA256}}` | `c949950ee76bf84e0dc8f537a98a2c702169f09b5a061c27c87edff753fac3ff` |
| `{{RELEASE_ROW_ID}}` | `S486` (or whatever id the L1 assigns the release row) |
| `{{BUILD_INFO}}` | `b11906-4d71b42fd` |
| `{{ALIAS}}` | `kama-r46-live` |
| `{{MODEL_SHA256}}` | `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` |
| `{{TOOL_SHA256}}` | `8c0dbb2b60da4d0e89ebe537b2f36b0b59356efedbe5f66c7364bdb6c8f662f3` |
| `{{PROBE_SHA256}}` | `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3` |
| `{{RECEIPT1_SHA256}}` … `3` | `9ad6ad36501f80a4ca3adef10275865a5faa401bfd57db0959bd243eda977e26`, `09f049cff08b2d27a74f205db313dfdefb808740546e74d607414551c262562a`, `33f1dd57e9f8a24c39718b4ffd5aef0936cdd395893c281c5c15c9aedae46632` |
| `{{TEACHES}}` | the teaches sentence of §3 |
| `{{OPENED}}` | `2026-10-26` |

Re-derive every value with `python3 derive-row-facts.py` (no arguments, read-only); it prints one `key=value` per line.

## 5. Census rules each row must pass

`SOURCES-CONTRACT-v1`: one registry table, 11 cells (`NF=13` with the outer pipes). Enforced by
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate`; line numbers are that file.

| code | rule | line | S486 | S487 |
|---|---|---|---|---|
| E01 | malformed row, `NF!=13` (11 cells) | 636 | 11 cells | 11 cells |
| E02 | id not `S[0-9]{3,}` | 640 | `S486` | `S487` |
| E03 | duplicate id | 641 | absent at tip | absent at tip |
| E04 | duplicate URL+scope without `supersedes S###` | 649 | new asset URL, new scope | no URL (own-work command) |
| E05 | kind enum `spec|docs|paper|code|tool|dataset|talk|book|community|own-work` | 656 | `docs` | `own-work` |
| E06 | tier enum `A|B|C` | 657 | `A` | `A` |
| E07 | status enum `queued|mined|rejected` | 659 | `mined` | `mined` |
| E08 | `opened` a past/present ISO date | 662 | `2026-10-26` (today) | `2026-10-26` |
| E09 | recheck ISO date, `NNd`, or symbolic cadence | 664/666 | `on-release` | `on-release` |
| E10 | `community` never tier A | 668 | kind `docs` | kind `own-work` |
| E11 | used-by path must exist on disk | 567 | `corpus/knowledge/llamacpp-loading-lifecycle.md` exists | same |
| E12 | row must sit inside `## Registry` | 621 | inserted at line 239 | inserted at line 240 |
| W01 | tier-C mined with used-by | 670 | n/a (tier A) | n/a |
| W03 | mined row with used-by `—` | 674 | used-by set | used-by set |
| W04 | same URL across scopes (warning) | 645 | new URL | no URL |

No `|` character appears in any cell of either row (asserted at build time), so no cell shifts.

## 6. Validation evidence (commands, outputs, exit codes)

Scratch copy: `$S/chk/corpus/SOURCES.md` where `$S=/fast/scratch/hyaku/kama-r46/S1Row`, built as a **symlink farm**
(see finding F1) — every lane top-level entry symlinked into `$S/chk`, `corpus/` real with `knowledge` and `lessons`
symlinked and `SOURCES.md` the copy with the two rows at lines 239–240. `sha256` of the validated copy is in
`rows-validated.txt`'s companion evidence (`rows-validated.txt` holds the two row lines verbatim).

```
$ bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate \
    --file $S/chk/corpus/SOURCES.md --today 2026-10-26
exit=0
```
```text
file	W04	S031 duplicate url docs.ollama.com/api/tags across scopes
file	W04	S043 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp across scopes
file	W04	S056 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp across scopes
file	W04	S060 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S064 duplicate url docs.python.org/3.14/library/subprocess.html across scopes
file	W04	S065 duplicate url docs.python.org/3.14/library/sys.html across scopes
file	W04	S067 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes
file	W04	S071 duplicate url git-scm.com/docs/git-cat-file across scopes
file	W04	S077 duplicate url docs.python.org/3.14/library/os.html across scopes
file	W04	S078 duplicate url man7.org/linux/man-pages/man8/ldconfig.8.html across scopes
file	W04	S079 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes
file	W04	S080 duplicate url nix.dev/manual/nix/2.34/protocols/nix-archive across scopes
file	W04	S081 duplicate url go.googlesource.com/mod/+/refs/tags/v0.42.0/sumdb/dirhash/hash.go across scopes
file	W04	S082 duplicate url git-scm.com/docs/gitrevisions across scopes
file	W04	S083 duplicate url git-scm.com/docs/git-cat-file across scopes
file	W04	S084 duplicate url docs.jj-vcs.dev/latest/cli-reference across scopes
file	W04	S085 duplicate url git-scm.com/docs/git-log across scopes
file	W04	S086 duplicate url tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html across scopes
file	W04	S087 duplicate url docs.python.org/3.14/builtins/functions.html across scopes
file	W04	S088 duplicate url docs.python.org/3.14/library/os.html across scopes
file	W04	S093 duplicate url git-scm.com/docs/git-log across scopes
file	W04	S097 duplicate url docs.python.org/3.14/library/subprocess.html across scopes
file	W04	S100 duplicate url git-scm.com/docs/git-config across scopes
file	W04	S103 duplicate url git-scm.com/docs/partial-clone across scopes
file	W04	S105 duplicate url docs.python.org/3.14/builtins/stdtypes.html across scopes
file	W04	S108 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp across scopes
file	W04	S109 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S110 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp across scopes
file	W04	S112 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md across scopes
file	W04	S114 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S115 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S116 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S117 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S118 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S119 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S120 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S121 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S122 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S123 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S124 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S125 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S127 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S129 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/ggml/src/gguf.cpp across scopes
file	W04	S130 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp across scopes
file	W04	S131 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp across scopes
file	W04	S132 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp across scopes
file	W04	S133 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S134 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md across scopes
file	W04	S135 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-kv-cache.cpp across scopes
file	W04	S137 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S141 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S142 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S143 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S144 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S145 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S146 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S147 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S148 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S149 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S150 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S151 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S152 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S153 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S154 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S155 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S156 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S157 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S158 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S159 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S160 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S161 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S162 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S163 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S164 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S165 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S166 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S167 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S168 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S169 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S170 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S171 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S172 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S173 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S181 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S182 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S183 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S184 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S185 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S186 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S187 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S188 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S189 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S191 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W01	S481 tierC mined used-by=corpus/knowledge/runtime-health-surface-processes.md, corpus/lessons/round-43.md, corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/endpoint-health-probe-conventions.md, corpus/knowledge/served-model-id-resolution.md, corpus/knowledge/engine-pin-watch.md
file	ok	/fast/scratch/hyaku/kama-r46/S1Row/chk/corpus/SOURCES.md
```

Lane baseline for comparison (same command on the unmodified lane file — read-only):

```text
file	W04	S031 duplicate url docs.ollama.com/api/tags across scopes
file	W04	S043 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp across scopes
file	W04	S056 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp across scopes
file	W04	S060 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S064 duplicate url docs.python.org/3.14/library/subprocess.html across scopes
file	W04	S065 duplicate url docs.python.org/3.14/library/sys.html across scopes
file	W04	S067 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes
file	W04	S071 duplicate url git-scm.com/docs/git-cat-file across scopes
file	W04	S077 duplicate url docs.python.org/3.14/library/os.html across scopes
file	W04	S078 duplicate url man7.org/linux/man-pages/man8/ldconfig.8.html across scopes
file	W04	S079 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes
file	W04	S080 duplicate url nix.dev/manual/nix/2.34/protocols/nix-archive across scopes
file	W04	S081 duplicate url go.googlesource.com/mod/+/refs/tags/v0.42.0/sumdb/dirhash/hash.go across scopes
file	W04	S082 duplicate url git-scm.com/docs/gitrevisions across scopes
file	W04	S083 duplicate url git-scm.com/docs/git-cat-file across scopes
file	W04	S084 duplicate url docs.jj-vcs.dev/latest/cli-reference across scopes
file	W04	S085 duplicate url git-scm.com/docs/git-log across scopes
file	W04	S086 duplicate url tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html across scopes
file	W04	S087 duplicate url docs.python.org/3.14/builtins/functions.html across scopes
file	W04	S088 duplicate url docs.python.org/3.14/library/os.html across scopes
file	W04	S093 duplicate url git-scm.com/docs/git-log across scopes
file	W04	S097 duplicate url docs.python.org/3.14/library/subprocess.html across scopes
file	W04	S100 duplicate url git-scm.com/docs/git-config across scopes
file	W04	S103 duplicate url git-scm.com/docs/partial-clone across scopes
file	W04	S105 duplicate url docs.python.org/3.14/builtins/stdtypes.html across scopes
file	W04	S108 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp across scopes
file	W04	S109 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S110 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp across scopes
file	W04	S112 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md across scopes
file	W04	S114 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S115 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S116 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S117 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S118 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S119 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S120 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S121 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S122 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S123 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S124 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S125 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S127 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S129 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/ggml/src/gguf.cpp across scopes
file	W04	S130 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp across scopes
file	W04	S131 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp across scopes
file	W04	S132 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp across scopes
file	W04	S133 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S134 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md across scopes
file	W04	S135 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-kv-cache.cpp across scopes
file	W04	S137 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S141 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S142 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S143 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S144 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S145 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S146 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S147 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S148 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S149 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S150 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S151 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S152 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S153 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S154 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S155 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S156 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S157 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S158 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S159 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S160 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S161 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S162 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S163 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S164 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S165 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S166 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S167 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S168 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S169 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S170 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S171 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S172 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S173 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S181 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S182 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S183 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S184 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S185 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S186 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S187 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S188 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S189 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S191 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W01	S481 tierC mined used-by=corpus/knowledge/runtime-health-surface-processes.md, corpus/lessons/round-43.md, corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/endpoint-health-probe-conventions.md, corpus/knowledge/served-model-id-resolution.md, corpus/knowledge/engine-pin-watch.md
file	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
```

and the two findings sets are identical — the two rows add nothing but the `rows` count:

```
$ diff <lane findings> <scratch findings>
IDENTICAL-FINDINGS
```

```text
$ bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --file $S/chk/corpus/SOURCES.md
exit=0
file	rows	228
file	tier.A	217
file	tier.B	7
file	tier.C	4
file	status.mined	209
file	status.queued	8
file	status.rejected	11
FLEET	rows	228
FLEET	tier.A	217
FLEET	tier.B	7
FLEET	tier.C	4
FLEET	tier.invalid	0
FLEET	status.queued	8
FLEET	status.mined	209
FLEET	status.rejected	11
FLEET	status.invalid	0
FLEET	missing	0
```
`rows 228` against `rows 226` on the lane file: exactly the two added rows, all other counters unchanged.

Control for the insertion point (rows appended after line 524 instead of inside the registry, same symlink farm):

```text
$ bash .../sources-census.sh validate --file $S/chk/corpus/SOURCES-tail.md --today 2026-10-26
exit=1
file	W04	S031 duplicate url docs.ollama.com/api/tags across scopes
file	W04	S043 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp across scopes
file	W04	S056 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp across scopes
file	W04	S060 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S064 duplicate url docs.python.org/3.14/library/subprocess.html across scopes
file	W04	S065 duplicate url docs.python.org/3.14/library/sys.html across scopes
file	W04	S067 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes
file	W04	S071 duplicate url git-scm.com/docs/git-cat-file across scopes
file	W04	S077 duplicate url docs.python.org/3.14/library/os.html across scopes
file	W04	S078 duplicate url man7.org/linux/man-pages/man8/ldconfig.8.html across scopes
file	W04	S079 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes
file	W04	S080 duplicate url nix.dev/manual/nix/2.34/protocols/nix-archive across scopes
file	W04	S081 duplicate url go.googlesource.com/mod/+/refs/tags/v0.42.0/sumdb/dirhash/hash.go across scopes
file	W04	S082 duplicate url git-scm.com/docs/gitrevisions across scopes
file	W04	S083 duplicate url git-scm.com/docs/git-cat-file across scopes
file	W04	S084 duplicate url docs.jj-vcs.dev/latest/cli-reference across scopes
file	W04	S085 duplicate url git-scm.com/docs/git-log across scopes
file	W04	S086 duplicate url tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html across scopes
file	W04	S087 duplicate url docs.python.org/3.14/builtins/functions.html across scopes
file	W04	S088 duplicate url docs.python.org/3.14/library/os.html across scopes
file	W04	S093 duplicate url git-scm.com/docs/git-log across scopes
file	W04	S097 duplicate url docs.python.org/3.14/library/subprocess.html across scopes
file	W04	S100 duplicate url git-scm.com/docs/git-config across scopes
file	W04	S103 duplicate url git-scm.com/docs/partial-clone across scopes
file	W04	S105 duplicate url docs.python.org/3.14/builtins/stdtypes.html across scopes
file	W04	S108 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp across scopes
file	W04	S109 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S110 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp across scopes
file	W04	S112 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md across scopes
file	W04	S114 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S115 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S116 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S117 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S118 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S119 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S120 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S121 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S122 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S123 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S124 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S125 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S127 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S129 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/ggml/src/gguf.cpp across scopes
file	W04	S130 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp across scopes
file	W04	S131 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp across scopes
file	W04	S132 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp across scopes
file	W04	S133 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S134 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md across scopes
file	W04	S135 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-kv-cache.cpp across scopes
file	W04	S137 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S141 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S142 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S143 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S144 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S145 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S146 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S147 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S148 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S149 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S150 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S151 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S152 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S153 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S154 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S155 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S156 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S157 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S158 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S159 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S160 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S161 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S162 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S163 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S164 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S165 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S166 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S167 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S168 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S169 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S170 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S171 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S172 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S173 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S181 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S182 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S183 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S184 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S185 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S186 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S187 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S188 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S189 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S191 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W01	S481 tierC mined used-by=corpus/knowledge/runtime-health-surface-processes.md, corpus/lessons/round-43.md, corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/endpoint-health-probe-conventions.md, corpus/knowledge/served-model-id-resolution.md, corpus/knowledge/engine-pin-watch.md
file	E12	S486 row outside Registry section
file	E12	S487 row outside Registry section
```

Counter newrow leg evaluated with the frozen counter's own regexes (`tools/round46-release-recheck-audit.py`):

```text
$ python3 - <<'EOF'   # imports the frozen counter module, reads lane base + scratch tip
newrow 1 ids ['S486']
EOF
```

`derive-row-facts.py` output (every value cited by the two rows, re-derived from the bytes on disk):

```text
release_json_sha256 b9041d4af30892fea64767acdcc3de5b9452a2d01f0b0e6fedef6c18976da6d7
release_tag b11906
release_target_commitish 4d71b42fd87db24b8b7c808c151b713aa4459cfd
release_published_at 2026-10-26T19:45:36Z
release_prerelease True
asset_name llama-b11906-bin-ubuntu-x64.tar.gz
asset_size 22478121
asset_digest sha256:064ade6220799fd9e7b1804b574f5f92c38dde358cc987c6b8283cfaeb1eeef3
install_txt_sha256 dc65047e8fafdb367ad2f71edf3a07e62f7775ed4a28938b83a2826fda5d51d4
install_line c949950ee76bf84e0dc8f537a98a2c702169f09b5a061c27c87edff753fac3ff  /home/vgpnk/.local/opt/llama-b11906/llama-server
install_line 682717ba312caefda06be7b2e5a637d8af357ff1f1264f6f5624dc53212a8223  /home/vgpnk/.local/opt/llama-b11906/libllama-server-impl.so
install_line version: 0.7.0-dev (build 11906, commit 4d71b42fd)
receipt-1_sha256 9ad6ad36501f80a4ca3adef10275865a5faa401bfd57db0959bd243eda977e26
receipt-1_schema kama-llamacpp-live/v3
receipt-1_window 2026-10-26T19:57:39.317Z 2026-10-26T19:57:39.474Z
receipt-1_port 33179
receipt-1_outcome pass
receipt-1_checks_passed 11 of 11
receipt-1_server_sha256 c949950ee76bf84e0dc8f537a98a2c702169f09b5a061c27c87edff753fac3ff
receipt-1_build_info b11906-4d71b42fd
receipt-1_alias kama-r46-live
receipt-1_health_body {"status":"ok"}
receipt-1_metrics_status 501
receipt-1_loading_bodies 1 exact True
receipt-1_model_sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d
receipt-1_tool_sha256 8c0dbb2b60da4d0e89ebe537b2f36b0b59356efedbe5f66c7364bdb6c8f662f3
receipt-1_probe_sha256 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3
receipt-1_teardown 0 False True 3
receipt-2_sha256 09f049cff08b2d27a74f205db313dfdefb808740546e74d607414551c262562a
receipt-2_schema kama-llamacpp-live/v3
receipt-2_window 2026-10-26T19:57:39.532Z 2026-10-26T19:57:39.691Z
receipt-2_port 46073
receipt-2_outcome pass
receipt-2_checks_passed 11 of 11
receipt-2_server_sha256 c949950ee76bf84e0dc8f537a98a2c702169f09b5a061c27c87edff753fac3ff
receipt-2_build_info b11906-4d71b42fd
receipt-2_alias kama-r46-live
receipt-2_health_body {"status":"ok"}
receipt-2_metrics_status 501
receipt-2_loading_bodies 1 exact True
receipt-2_model_sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d
receipt-2_tool_sha256 8c0dbb2b60da4d0e89ebe537b2f36b0b59356efedbe5f66c7364bdb6c8f662f3
receipt-2_probe_sha256 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3
receipt-2_teardown 0 False True 3
receipt-3_sha256 33f1dd57e9f8a24c39718b4ffd5aef0936cdd395893c281c5c15c9aedae46632
receipt-3_schema kama-llamacpp-live/v3
receipt-3_window 2026-10-26T19:57:39.745Z 2026-10-26T19:57:39.905Z
receipt-3_port 44923
receipt-3_outcome pass
receipt-3_checks_passed 11 of 11
receipt-3_server_sha256 c949950ee76bf84e0dc8f537a98a2c702169f09b5a061c27c87edff753fac3ff
receipt-3_build_info b11906-4d71b42fd
receipt-3_alias kama-r46-live
receipt-3_health_body {"status":"ok"}
receipt-3_metrics_status 501
receipt-3_loading_bodies 1 exact True
receipt-3_model_sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d
receipt-3_tool_sha256 8c0dbb2b60da4d0e89ebe537b2f36b0b59356efedbe5f66c7364bdb6c8f662f3
receipt-3_probe_sha256 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3
receipt-3_teardown 0 False True 3
```

## 7. Provenance

| object | value |
|---|---|
| release record | `.ufo/waves/round-46/c1/release-b11906.json`, 69164 bytes, sha256 `b9041d4af30892fea64767acdcc3de5b9452a2d01f0b0e6fedef6c18976da6d7`; an independent `gh api repos/ggml-org/llama.cpp/releases/tags/b11906` fetch by this seat reproduced the same 69164 bytes and sha256 |
| tag → commit | `git ls-remote --tags https://github.com/ggml-org/llama.cpp.git refs/tags/b11906 refs/tags/b11889` → `4d71b42fd87db24b8b7c808c151b713aa4459cfd refs/tags/b11906`, `d854d98bae598388ecea1ed84396587e5edc326d refs/tags/b11889` (exit 0) |
| commit distance | `git -C /fast/scratch/hyaku/kama-r46/L1/llama.git rev-list --count d854d98b..4d71b42f` → `17` |
| release fields | `tag_name b11906`, `target_commitish 4d71b42fd87db24b8b7c808c151b713aa4459cfd`, `published_at 2026-10-26T19:45:36Z`, `prerelease true`, 36 assets |
| asset | `llama-b11906-bin-ubuntu-x64.tar.gz` 22478121 bytes, `sha256:064ade6220799fd9e7b1804b574f5f92c38dde358cc987c6b8283cfaeb1eeef3` (matches the seat item's digest) |
| install | `.ufo/waves/round-46/c1/live/install.txt` (written by X1Live): `llama-server` `c949950ee76bf84e0dc8f537a98a2c702169f09b5a061c27c87edff753fac3ff`, `libllama-server-impl.so` `682717ba312caefda06be7b2e5a637d8af357ff1f1264f6f5624dc53212a8223`, `version: 0.7.0-dev (build 11906, commit 4d71b42fd)` |
| receipts | `.ufo/waves/round-46/c1/live/receipt-1..3.json`, sha256 `9ad6ad36…`, `09f049cf…`, `33f1dd57…`; schema `kama-llamacpp-live/v3`; written 2026-10-26T19:57:39Z |
| model re-fetch | `.ufo/waves/round-46/c1/live/model-fetch.txt`; 1185376 bytes, sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`, fetched 2026-10-26T19:57:36Z, `curl_exit 0` |

## 8. Caveats and actions for the L1

1. **Ids.** The rows are validated with `S486`/`S487` because E02 needs digits. Assign the final `S4NN`; if any other
   round-46 seat also proposes an id, re-run the census copy so E03 stays clean. `S486` is the id the C1 counter's
   newrow leg will read; the C1's own ledger/flag legs never mention it.
2. **Section heading.** `section=0` on the scratch copy: `## Round-46 release re-verification` is the C1 integration
   text, not a row. Add it (with the drifted/removed ids) and `section` becomes 1.
3. **`corpus/lessons/round-46.md`.** Not on disk yet, so it is *not* in either used-by cell (E11 would fail now). S484/S485
   both list `corpus/lessons/round-45.md`; append `corpus/lessons/round-46.md` to both rows **after** S9Lesson's draft lands
   and passes the census.
4. **`install.txt` was rewritten during the wave.** At 16:58:51 (after the 16:57:39 receipts) it gained
   `install_tree_sha256 89fbc38997001c02fe7daae0fcc32c6aa9e7c585f455d8809ddefe42ed7bdf0f`,
   `install_links_sha256 5cb9f4865c8e1315dbd1baa99310c9bc65ddcf469929488359c66587b6470060 (no unpinned links)` and a harness
   line; its sha256 moved from `15131698da32294918655b1f992b2365aff23ceac82bfe04a9c0647588534cec` to
   `dc65047e8fafdb367ad2f71edf3a07e62f7775ed4a28938b83a2826fda5d51d4`. The row therefore cites the file's **content**
   (`--version` line, binary digests) and not its hash; if the L1 wants the two new fields in the anchor, they are stable
   for the current extract.
5. **Live evidence is still mutable.** The receipts were the final bytes when read (hashes above), but X1Live or a replica
   may rewrite them before integration. If any receipt hash changes, run `derive-row-facts.py` and rebuild §3's row from
   its output; do not splice old ports/timestamps into new bytes.
6. **Pre-existing warnings.** The lane file already returns 93 `W04` and 1 `W01` with exit 0; the scratch copy returns the
   same 94 lines. They are not caused by these rows and do not affect the exit status.

## 9. Findings (defects, exact lines, proposed fixes)

**F1 — `validate --file` resolves used-by paths against `dirname(file)/..`, so a plain "scratch copy" produces hundreds
of false `E11`.** `scripts/sources-census.sh:497-503` sets the lane dir to `realpath(dirname(file)/..)`; `:567` then tests
`-e "$dir/$path"`. Copying `SOURCES.md` to a bare scratch directory yields
`E11 S484 missing used-by corpus/knowledge/llamacpp-loading-lifecycle.md`, … for ~200 rows and exit 1 — a false alarm
for every seat that follows "validate on a scratch copy" literally. Reproduce: copy the file to any directory whose parent
is not a lane root and run `validate --file`. Proposed fix: teach `--file` a `--dir` option (or default `dir` to the
`--root`/`conf` lane that owns the file) so a copy can be validated without a symlink farm; alternatively document that
`--file` requires a mirrored tree. This seat used a symlink farm (`$S/chk` symlinks every lane top-level entry, `corpus/`
real with symlinked children) to get the honest answer.

**F2 — rows appended at the end of `SOURCES.md` are rejected.** `scripts/sources-census.sh:621` flags any `| S###` row
outside the `## Registry` section as `E12`; the file's last sections (`## Round-44 …`, `## Round-45 …`) invite appending
at the tail. Control run above: `E12` for both rows, exit 1. Proposed fix: none needed in the script — the fix is the
registry insertion point documented in §1; if the round section is meant to carry rows, the contract would need a second
admitted registry, which it does not have.

**F3 — a wave evidence file changed under a row's feet.** `.ufo/waves/round-46/c1/live/install.txt` gained three lines
mid-wave and its sha256 moved (`15131698…` → `dc65047e…`) while receipts kept their hashes. A row that pinned
`install.txt`'s sha256 would have gone stale within minutes. Proposed fix (process, not code): anchor rows on the
**content** the row depends on plus the hash of the object that owns that content (here the release JSON), and treat
engine-side evidence files as moving targets until the lane integrates.

## 10. Reproduction

```bash
S=/fast/scratch/hyaku/kama-r46/S1Row; mkdir -p "$S"; export TMPDIR="$S"
gh api repos/ggml-org/llama.cpp/releases/tags/b11906 > "$S/release-b11906.json"
sha256sum "$S/release-b11906.json"            # b9041d4a…, equal to the lane copy
git ls-remote --tags https://github.com/ggml-org/llama.cpp.git refs/tags/b11906 refs/tags/b11889
git -C /fast/scratch/hyaku/kama-r46/L1/llama.git rev-list --count \
    d854d98bae598388ecea1ed84396587e5edc326d..4d71b42fd87db24b8b7c808c151b713aa4459cfd   # 17
python3 derive-row-facts.py
# scratch copy + validation (symlink farm, see F1)
```

All commands above were run by this seat; the outputs are quoted verbatim in §6 and §7.
