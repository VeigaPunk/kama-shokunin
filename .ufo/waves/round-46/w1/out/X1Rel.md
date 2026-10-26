# X1Rel — C1 sourced row evidence: llama.cpp release b11906 identity

**Verdict: b11906 identity confirmed from four independent angles (release JSON, `git ls-remote`, the bare clone object and the pinned diff): tag → 4d71b42fd87db24b8b7c808c151b713aa4459cfd, Pre-release published 2026-10-26T19:45:36Z, `llama-b11906-bin-ubuntu-x64.tar.gz` size 22478121 / sha256:064ade62…eeef3; one bN tag (b11907) sits above it and the reading list handed to this wave drops one changed-file row (S479), which the C1 ledger must still score `holds`, not `unchanged-file`.**

## Deliverables

| path (relative to the lane root unless absolute) | what | sha256 |
|---|---|---|
| `.ufo/waves/round-46/c1/release-b11906.json` | `gh api repos/ggml-org/llama.cpp/releases/tags/b11906`, byte-exact, 69164 bytes, one physical line, no trailing newline | `b9041d4af30892fea64767acdcc3de5b9452a2d01f0b0e6fedef6c18976da6d7` |
| `.ufo/waves/round-46/c1/ls-remote-llama.cpp.txt` | `git ls-remote --tags` snapshot, 8215 refs at 2026-10-26T19:57:59Z | `151c69113b7ba2e4299831226a1a313c60e9e8c46f3705f4f17588b23808a1b4` |
| `.ufo/waves/round-46/c1/commits-b11889-b11906.txt` | 17 commit lines `%H %cI %s` | `12c3dda4fbb2de30a14063feaa68cb519b59c1f548c990c0e89ddb1edf00d493` |
| `.ufo/waves/round-46/c1/diffstat-b11889-b11906.txt` | `diff --stat`, 65 files | `fd2d108477e344bf5ae442f07f1c05f70747394d614dc5321dab7626460b10fb` |
| `.ufo/waves/round-46/w1/out/X1Rel/run.txt` | 41-line run record: every command, UTC timestamp, exit code, hash | — |
| `.ufo/waves/round-46/w1/out/X1Rel/row.md` | the b11906 registry row draft (11 cells), quote check, cell map | — |
| `.ufo/waves/round-46/w1/out/X1Rel/release-b11907.404.json` | the b11907 release-object 404 body (successor-tag check) | — |

## What the item asked to confirm — all four confirmed

Commands and observed output, all with exit code 0 unless noted:

1. **`target_commitish` = 4d71b42fd87db24b8b7c808c151b713aa4459cfd** — yes.
   `json.load(...)['target_commitish']`; the same 40-hex string is the unique
   `refs/tags/b11906` ref in the ls-remote snapshot
   (`.ufo/waves/round-46/c1/ls-remote-llama.cpp.txt:1428`), and
   `git -C …/L1/llama.git rev-parse 4d71b42f…^{commit}` = the commit,
   `cat-file -t` = `commit` (run.txt:29–31).
2. **`prerelease` = `true`** (also `draft` = `false`, `immutable` = `false`,
   `name` = `b11906`, release id 424687637, author `github-actions[bot]`).
3. **`published_at` = 2026-10-26T19:45:36Z** (created 2026-10-26T14:18:45Z,
   updated 2026-10-26T19:49:05Z — i.e. mutated five minutes after publication).
4. **asset `llama-b11906-bin-ubuntu-x64.tar.gz`: size 22478121, digest
   sha256:064ade6220799fd9e7b1804b574f5f92c38dde358cc987c6b8283cfaeb1eeef3**,
   state `uploaded`, content type `application/json; charset=utf-8`, asset id
   679269652. 36 assets on the release, no duplicate asset name, exactly one
   match for that name.

Tag census at my time (`run.txt:13,14,18`): 7461 `refs/tags/bN` refs; max
`b11907` = `4b851fbee8867136a0c561c8a3521f2fe7d53252`; **1 bN tag above b11906**.
`b11907` is a pushed tag with **no release object**: `gh api
repos/ggml-org/llama.cpp/releases/tags/b11907` → HTTP 404 at
2026-10-26T19:58:14Z (`release-b11907.404.json`). `b11905` =
`70c5f26324…` = the second commit of the b11889..b11906 range, so releases are
cut per commit.

Range evidence (`run.txt:21–26,35`): `rev-list --count
d854d98b…..4d71b42f…` = **17**; the log's first line is b11906
`4d71b42fd87db24b8b7c808c151b713aa4459cfd 2026-10-26T16:18:45+02:00 ggml-cpu :
rewrite concat as one row kernel for all types (#31179)`; `diff --stat` =
**65 files changed, 4323 insertions(+), 2128 deletions(-)**. The three server
files behave as the prereg's `release.observed` says (`run.txt:37–40`):

| path | blob at b11889 | blob at b11906 |
|---|---|---|
| `tools/server/server-context.cpp` | a5cba1d71d46c1c87ca868ac4a6a8b4c8902ca45 | 9043fa2c02905495f55045d8d0fc978b1f94e027 |
| `tools/server/server-models.cpp` | e1e006f1018fdcfd76f9f20f5a1a638c7f3245d6 | 5751401328682cfaae705b57536778566885e7ce |
| `tools/server/server.cpp` | b6ebf7523364109181ff3447a8bdf4843a3947cb | identical |
| `tools/server/README.md` | 8e27e37b8d4aa623006e413e7c8c4062a542e079 | identical |

## The row draft

`.ufo/waves/round-46/w1/out/X1Rel/row.md:15` is the whole row, one line, 11
cells, kind `docs`, tier `A`, scope = release identity, `status mined`,
`opened 2026-10-26`, `recheck on-release`, `used-by
registry/release-recheck-b11906.tsv`. Id proposal `S486` (highest id at base
0163fea2 and at my read of the tree is `S485`; `S486` absent at base, `| S48[6-9]`
count = 0) — **the L1 assigns the final id and it must be three digits**, because
`tools/round46-release-recheck-audit.py` parses `^\| S\d{3}` and its `newrow`
leg needs an id absent at base.

The located quote (verbatim, unique, 1 whitespace token, well under 25 words),
byte offset 1521, JSON pointer `/target_commitish`:

```
"target_commitish":"4d71b42fd87db24b8b7c808c151b713aa4459cfd","name":"b11906","draft":false,"immutable":false,"prerelease":true
```

Checked: `raw.find(q)` = 1521, `raw.count(q)` = 1; the row contains both
`b11906` and `4d71b42fd87db24b8b7c808c151b713aa4459cfd` (the counter's newrow
test); cell count = 11 (`12` pipes).

## Findings

### F1 — the wave's reading list is short by one row and its arithmetic contradicts the blobs (affects C1 scoring, not my row)

Text under test: `.ufo/waves/round-46/w1/spec.json:9` and
`.ufo/waves/round-46/w1/dispatch.json:694` ("71 rows' files are byte-identical
between b11889 and b11906; 20 rows need reading: S037 S042 S043 S060 S108 S109
S114 … S125 S133 S138"), repeated per item at `spec.json:246` /
`dispatch.json:283,824`.

Recomputed from the base registry and the two release trees (read-only,
`git rev-parse <rev>:<path>` per distinct path of the 91 population rows):

- population rule re-implemented from the counter docstring → **91 rows, 16 distinct paths**, ids exactly equal to `preregistration.json` `claims[0].population` (set comparison `True`).
- **14 paths → 73 rows byte-identical; 2 paths → 18 rows changed**: `tools/server/server-context.cpp` (S042 S060 S109 S114 S115 S116 S117 S118 S119 S120 S121 S122 S123 S124 S125 S133 S138) and `tools/server/server-models.cpp` (**S479**).
- rows that actually need reading = changed ∪ (b11889 verdict `holds-reworded`) = **21**: those 18 plus **S037, S043, S108** (all `tools/server/server.cpp`, blob identical).

So "71/20" is wrong on both numbers (73/18 by blob identity), and the 20-id list
is neither of the two defensible sets: it drops **S479** and keeps the three
unchanged-file reworded rows. The frozen preregistration is *not* wrong — its
`claims[0].release.observed` says "18 population rows' files changed since
b11889 (tools/server/server-context.cpp, tools/server/server-models.cpp)", which
matches my recompute; the mangled 71/20 exists only in the wave's spec/dispatch
prose.

Consequence if a seat follows the list: S479 gets filed `unchanged-file`, and
the counter rejects it, because `changed` re-derives to `1`
(`e1e006f1…` → `57514013…`). The whole `server-models.cpp` delta is one comment
line at release 535 (`mtmd_helper_model_can_chat()` →
`mtmd_helper_get_capabilities()`), and S479's own ranges are **text-equal at
b11906 at the same release lines as at b11889** — `2329→2276`
`this->get_router_models = [this](const server_http_req & req) {`,
`2378-2379→2325-2326` `if (meta.n_ctx_train > 0) {` /
`model_info["context_length"] = meta.n_ctx_train;` — so the correct verdict is
`holds` with `release_blob 5751401328682cfaae705b57536778566885e7ce`, no
witness required.

Proposed fix (not applied — the lane is read-only for me; the L1 owns these
files): in `.ufo/waves/round-46/w1/spec.json:9` / `dispatch.json:694` and the
per-item copies, replace "71 rows … 20 rows need reading: …" with "73 rows …
18 rows changed: S042 S060 S109 S114–S125 S133 S138 (server-context.cpp) and
S479 (server-models.cpp); additionally S037 S043 S108 need reading for their
b11889 `holds-reworded` verdict (files byte-identical)". Repro (any reader):

```
python3 - <<'EOF'
import re,subprocess
B='/fast/scratch/hyaku/kama-r46/L1/llama.git'
t=subprocess.run(['git','-C','/home/vgpnk/Projects/shokunin/kama-shokunin','show',
  '0163fea2dab3f282ebd70c71da9ab5de4cedf733:corpus/SOURCES.md'],capture_output=True,text=True).stdout
# ... population rule of tools/round46-release-recheck-audit.py, then per path:
#   git -C $B rev-parse d854d98b…:<path>   vs   git -C $B rev-parse 4d71b42f…:<path>
EOF
```

### F2 — b11906 is already superseded by a *tag* (freshness caveat, not a defect in the frozen claim)

`refs/tags/b11907` = `4b851fbee8867136a0c561c8a3521f2fe7d53252` existed at
2026-10-26T19:57:59Z (`c1/ls-remote-llama.cpp.txt:1429`), it is a descendant of
b11906 (`git merge-base --is-ancestor 4d71b42f… 4b851fbee…` exit 0), and its
release object did not exist yet at 19:58:14Z (HTTP 404). The round-46 claim was
frozen against b11906 before any seat ran, so the claim stands; but no lane file
may describe b11906 as "the current/newest release", and the next on-release
round starts from b11907 (its release object may appear later, assets and digest
will then differ).

### F3 — the release object is mutable: cite commit + digest, never the tag

`prerelease: true`, `immutable: false`, `updated_at 2026-10-26T19:49:05Z` >
`published_at 2026-10-26T19:45:36Z`. Any ledger row or knowledge entry that says
"b11906 means these bytes" is only true for the commit and the digest recorded
here.

### F4 — provenance limit on the digest

`sha256:064ade…eeef3` is **GitHub's computed asset digest as published in the
release JSON**; I did not download the tarball, so the row must not be read as
local byte verification. Download-and-hash is X1Live/X1Replica territory
(`llama-b11906-bin-ubuntu-x64.tar.gz`, 22478121 bytes).

## Risks / limits of this seat

- No build, lint, test or formatter was run (editing wave; the L1 owns the gate).
- The b11906 ledger's 91 rows were not touched here; my only registry-facing
  output is the row draft and the identity evidence.
- `gh` quota: 2 requests this seat (`releases/tags/b11906`, `releases/tags/b11907`
  → 404), each object once.
- Tooling: nothing installed; `gh`, `git`, `python3` were already present.
- Scratch `/fast/scratch/hyaku/kama-r46/X1Rel` contained only `run_record.sh`
  (the script that produced `run.txt`) and was removed after the report was
  written; no clone was made (the shared L1 bare clone was used read-only), so
  `/tmp` holds nothing to cite.

## Exact paths written

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/c1/release-b11906.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/c1/ls-remote-llama.cpp.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/c1/commits-b11889-b11906.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/c1/diffstat-b11889-b11906.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X1Rel/run.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X1Rel/row.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X1Rel/release-b11907.404.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X1Rel.md
