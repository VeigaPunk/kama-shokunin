# SR01 — independent pin inventory (scout, read-only)

- Seat: `SR01ScoutPins`, role scout, axis **freshness**, milestone `kama r80 w1`.
- Lane tip at read: `fe7b978013bd1aa6d67a7e0fbf6369b8d7a9b023` (`git -C …/kama-shokunin rev-parse master`, exit 0). Base revision named by the plan: `c45fc7d1a8427e9c98a9dd7befa542c7b5caed38`.
- Writes confined to this seat directory `.ufo/waves/round-80/w1/SR01ScoutPins/` plus this report. No tool installed; nothing to record under the tooling directive.
- Source of truth: live upstream `git ls-remote` only. The lane's `tools/pin-watch.py` was **not run** (per the item); only its documented tag semantics were read from `tools/pin-watch.py:1-40` so the release-tag set matches the lane's own definition (fullmatch of `tag_regex`, peel lines skipped).

## Method and receipts

All commands run at **2026-11-04T10:40Z** from seat scratch (`/fast/scratch/hyaku/kama-r80/SR01ScoutPins`, deleted before yield); the raw outputs and the derived receipt were copied into this seat dir.

| Command | Exit | Receipt (absolute) | Size / sha256 |
|---|---|---|---|
| `git ls-remote --tags https://github.com/sgl-project/sglang.git` | 0 | `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/SR01ScoutPins/sglang.tags.txt` | 11889 B, `882d79469bda171ae675882a10735f39e953193c02f7251d8f76bfae1e7463dc` |
| `git ls-remote --tags https://github.com/vllm-project/vllm.git` | 0 | `…/SR01ScoutPins/vllm.tags.txt` | 14014 B, `5406e20a6aacef2cc4ce75b71073afa4ff674323f23ffd34278fd0381617a870` |
| `git ls-remote --tags https://github.com/ggml-org/llama.cpp.git` | 0 | `…/SR01ScoutPins/llamacpp.tags.txt` | 485524 B, `a2de12bed05a81e08aeaf6dff51a40e0f092ad67bf1551007a36e37f893134fa` |
| `git ls-remote <llama.cpp> refs/tags/<t> refs/tags/<t>^{}` for `b11963`, `b7200`, `b11755` (three runs) | 0 | cross-check of `llamacpp.tags.txt` | one line each, no `^{}` line |
| `curl https://api.github.com/repos/ggml-org/llama.cpp/commits/<sha>` for `39febd2a…`, `ab49f094…`, `704366d76…` | 0 (HTTP 200 each) | `…/SR01ScoutPins/{39febd2a…,ab49f094…,704366d76…}.commit.json` | object type `commit` for all three |

Single-ref cross-check transcript (each run requested both the ref and its `^{}` form; only the ref pattern matched, so no peel line exists):

```
39febd2adb947b70da35e95f9351b3bf58ad170a	refs/tags/b11963
ab49f094d29057b2c4d2b0f1e822c9140df1b0e1	refs/tags/b7200
704366d76f8748cf9ad3df62a464bfcc8d1ae6ad	refs/tags/b11755
```

Derived machine receipt: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/SR01ScoutPins/SR01.json` (per-pin cells, llama ref relations, the five C2 register refs, the lane ref inventory, drift series).

Ref-line counts: sglang 192 lines / 167 tag names / 25 peel lines; vllm 230 / 219 / 11; llama.cpp 8364 / 8339 / 25.

## (a) Release-tag status of the three `registry/engine-pins.tsv` pins

Release set = tag names that **fullmatch** the row's `tag_regex` (`v(\d+)\.(\d+)\.(\d+)`, `b(\d+)`), i.e. `.postN`, `rcN`, four-part and `gguf-*`/`ci_*`/`backup/*` names are not releases — the same rule `tools/pin-watch.py` documents.

| Engine | Pin | Pin is a release tag | Pin tag kind → target | Newest release tag | Release tags sorting **above** the pin | Status |
|---|---|---|---|---|---|---|
| sglang | `v0.5.22` | yes (of 73 release tags) | annotated → tag object `35ce313293052f8362e0829e7512bc9bc3d336c9`, peeled commit `baa9befa381511cd4d56f83980951e5a45fffc6d` | `v0.5.23` (annotated; tag `7df5dd09bc2f0e7e1509a1f7c2a40dff00ad8a01`, peeled `297e54fd105e974cdf401e5b4d20253a22c16f90`) | **1** | behind |
| vllm | `v0.32.0` | yes (of 88 release tags) | lightweight → commit `5df63a7203cdb9328d824a27b682e77c7b9928be` | `v0.33.0` (annotated; tag `3a4d82f569a9f57054ba81633e9b6c73b34b51fe`, peeled `4ba787ec9959e566d3b587a796dff07673324da5`) | **1** | behind |
| llama.cpp | `b11755` | yes (of 7608 release tags) | lightweight → commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` | `b12103` (lightweight → commit `6900fb5ac8344afd4103b136cfd631ca6707e038`) | **278** | behind |

No release tag sorts above `v0.5.23` (sglang) or `v0.33.0` (vllm); nothing sorts above `b12103`. Pin-watch-equivalent summary at the measurement instant:

```
engine=sglang pin=v0.5.22 newest=v0.5.23 newer=1 status=behind
engine=vllm pin=v0.32.0 newest=v0.33.0 newer=1 status=behind
engine=llama.cpp pin=b11755 newest=b12103 newer=278 status=behind
pins=3 current=0 behind=3 missing=0 error=0
```

This agrees with the plan's `Before` value `pins=3 current=0 behind=3 missing=0 error=0`. **Observed gap:** the plan cites `.ufo/waves/round-80/measured/before/c2-pinwatch.out`, but that path does **not exist** at my read — `measured/before/` holds only `c1-enum.out`, `measured/control/` only `c1-score-nocorrections.out`. The line is re-derivable (above) but its cited receipt is presently absent; the C2 seat owns producing it.

## (b) `39febd2adb947b70da35e95f9351b3bf58ad170a` (S553's commit anchor)

- **Not any llama.cpp tag's peeled (`^{}`) commit.** The whole tag list carries 25 peel lines, all on annotated non-release tags (`gguf-v0.4.0 … gguf-v0.19.0`, `v0.1.0 … v0.8.0`); none peels to `39febd2a…`. No `bNNNN` tag is annotated — every b-tag is a one-line lightweight ref.
- **But it is not an untagged commit either.** `refs/tags/b11963` → `39febd2adb947b70da35e95f9351b3bf58ad170a` exactly (single line, verified by a targeted `git ls-remote … refs/tags/b11963 refs/tags/b11963^{}`: one line, exit 0). GitHub's commit API returns object type `commit` for that sha, dated `2026-10-28T14:18:07Z`, `"sycl: work-group argmax for short TOP_K rows (#31110)"`. So the anchor is precisely **the commit release tag `b11963` names** — the tag list identifies it exactly, so no bracketing inference is needed.
- Relation to newest: `b11963` has **110** release tags above it (newest `b12103`). Numeric neighbours among existing tags: `b11962` (`f5222f25c18da062ab2b8a2dbbfbf4feae398566`) below and `b11965` (`838093f192e8cf918b08bc9289493598e0a5a81e`) above; `b11964` does **not** exist upstream.
- **Plainly stated limitation:** for a commit that *no* tag names, the tag list alone cannot bracket or order it. `git ls-remote --tags` exposes ref names and target oids only — no parents, no commit dates — and `bN` numbers are build numbers that skip values (`b11754`, `b11964` are absent), so numeric adjacency is not ancestry adjacency.

**Freshness consequence for C2 (the sibling):** the predicate's test "a commit row's 40-hex anchor is not any upstream tag's peeled oid" is satisfied by `39febd2a…` under a peel-line-only implementation while the commit *is* release tag `b11963`. A register that files S553 as an untagged commit would pass the counter and be wrong. The test must compare the anchor against every ref's **target oid** as well as peel lines — the lane already records this semantics in `registry/hexrun-ledger.tsv` (`caa8191d…  commit tagged b11909 (lightweight tag, ls-remote one line)`; `0a14a962…  blob not commit: … b11889 is a lightweight tag`).

## (c) kengaku's S178 pin `b7200`

`b7200` **is** a llama.cpp release tag: lightweight, target commit `ab49f094d29057b2c4d2b0f1e822c9140df1b0e1` (GitHub: `2025-11-29T21:04:44Z`, `"server: move server-context to its own cpp|h (#17595)"`). This matches kengaku's own cell exactly — `kengaku-shokunin/corpus/SOURCES.md:193` names `tag b7200 (ab49f094d29057b2c4d2b0f1e822c9140df1b0e1)` (read-only read outside the lane; no write). Relation at measurement: **3395** release tags above it, newest `b12103` → behind. It trails the lane's own `b11755` by 3117 release tags, a cross-lane divergence the relation row should make visible.

## (d) Every llama.cpp ref the lane's registry and source rows name

**Release-tag names in `corpus/SOURCES.md` rows** (293 rows total; row ids that name each): `b11755` (87 rows: S035–S191, S477, S479, S526–S528), `b11757` (S042), `b11887` (S477, as that sample's highest), `b11889` (S482, S484, S485, S486), `b11906` (S486, S487), `b11909` (S488, S489, S494, S505, S509) — **six** names. The round-45/46 narrative body additionally mentions `b11890`, `b11897` and the range `b11895–b11907` (`corpus/SOURCES.md:594,598`); those are sample values, not pins.

**Commit identities in `corpus/SOURCES.md`**: `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (**94 rows**; = `b11755`), `39febd2adb947b70da35e95f9351b3bf58ad170a` (S553 only; = `b11963`, unnamed in the lane), `caa8191df159f764fb0160e3d2fc6be008948aee` (S488, S494; = `b11909`), `d854d98bae598388ecea1ed84396587e5edc326d` (S482 `target_commitish`; = `b11889`), `4d71b42fd87db24b8b7c808c151b713aa4459cfd` (S486; = `b11906`), `c0fd78626405c6d9b934efef0ec7291fcc20e3d6` (S001 file anchor), `ad1b88ca0d37a2171efba1c04f1a3531c78f1b52` (S015 file anchor), `aec7bdb42b33b3177ae232ba36d08535eeaae1fe` (S026 PR head).

**Registry refs**: `engine-pins.tsv` → `b11755` (S038); `digest-ledger.tsv` → `b11755`, `b11889`, `b11906`, `b11909`; `capability-claims-r62/r63/r64.tsv` and `claim-outcome-ledger.tsv` → `b11755`; `cited-path-corrections.tsv` → `704366d76…` (4 rows); `release-recheck-b11889.tsv` / `release-recheck-b11906.tsv` → `release` cells `b11889`/`b11906`, `pin_commit` cells `704366d76…`, `c0fd7862…` (S001), `ad1b88ca…` (S015); `hexrun-ledger.tsv` commit-class rows → `704366d76…`, `c0fd7862…`, `6050b467c…` (`b11887`), `ad1b88ca…`, `aec7bdb4…`, `4b851fbee…` (`b11907`), `4d71b42f…` (`b11906`), `d854d98b…` (`b11889`), `caa8191d…` (`b11909`) — and 13 explicitly blob-classified rows (`57514013…`, `9043fa2c…`, `0a14a962…`, `27384beb…`, `4ab280a6…`, `80a9f2d7…`, `9706b3ac…`, `a4b4feae…`, `bf3e0838…`, `c4ce9072…`, `d5a66a49…`, `e1e006f1…`, `ec82db00…`). Every `pin_blob`/`release_blob` cell and those 13 are **git blob oids, not commits** — `hexrun-ledger.tsv` labels each one, and `SOURCES:598` confirms `b11889` is a lightweight tag on `d854d98b…`.

So the lane names **ten distinct llama.cpp commit identities** (`704366d76`, `c0fd7862`, `ad1b88ca`, `aec7bdb4`, `6050b467c`, `39febd2a`, `d854d98b`, `4d71b42f`, `4b851fbe`, `caa8191d`) and **six release-tag names** in source rows (seven across registry+sources: `b11907` enters via `hexrun-ledger.tsv:79`); `b11963` is reachable only through the commit `39febd2a…`, and `b12103`/`b7200` are named nowhere in the lane (`b7200` only by kengaku). Live target oid per named tag: `b11755`→`704366d76…`, `b11757`→`13786fbb3a1aaf4ff445c0b92d9f21cbe0af6d42`, `b11887`→`6050b467…`, `b11889`→`d854d98b…`, `b11906`→`4d71b42f…`, `b11907`→`4b851fbe…`, `b11909`→`caa8191d…`, `b7200`→`ab49f094…`, `b11963`→`39febd2a…`.

## What the C2 register must carry (computed cells for the sibling)

Five refs, as the predicate requires (`refs=5`); every cell below is a live computation at 2026-11-04T10:40Z:

| Ref | Row class | Newest | Newer | Relation |
|---|---|---|---|---|
| sglang `v0.5.22` | tag (engine pin) | `v0.5.23` | 1 | behind |
| vllm `v0.32.0` | tag (engine pin) | `v0.33.0` | 1 | behind |
| llama.cpp `b11755` | tag (engine pin) | `b12103` | 278 | behind |
| `39febd2a…` (S553) | **commit that equals tag `b11963`** | `b12103` | 110 | behind, and tagged — *not* an untagged commit |
| kengaku `b7200` | tag (cross-lane) | `b12103` | 3395 | behind |

Three hazards this inventory makes concrete:

1. **Cell determinism.** `newer` for `b11755` moved 115 (S477, 2026-10-25) → 117 (`b11889`, round 44) → 121 (`b11897`, round 45) → 131 (`b11906`, round 46) → **278** (`b12103`, now). Upstream added 165 ref lines in ~10 days. A "live" comparison at grading time cannot equal a cell measured hours earlier; the register must freeze the tag list (plan's `--tags-dir`, committed under `measured/after/c2-tags/<engine>.txt`) and date it, with the live leg informational.
2. **Lightweight tags.** Three of the five rows (`vllm v0.32.0`, `llama.cpp b11755`, kengaku `b7200`) are lightweight tags, and `39febd2a…` is the commit of the lightweight tag `b11963`; a peel-line-only test cannot see that equality. Compare anchors against ref target oids too.
3. **`newer` for a commit row is derivable only when the commit equals a tag.** Here it does (110). For a genuinely untagged commit the tag list yields no ordering at all — the register must not pretend otherwise.

## Confidence and remaining unknowns

- **(a), (b), (c): high** — three independent live sources agree (tag list, targeted single-ref `ls-remote`, GitHub commit API); hashes, byte counts and timestamps recorded above.
- **(d): high for the inventory**, read at lane tip `fe7b9780`; blob-vs-commit classification follows `hexrun-ledger.tsv`'s own `class`/note columns, not my guesswork.
- **Unresolved:** (i) whether the C2 counter computes peel oids from `^{}` lines only — `tools/round80-engine-pin-relations.py` and `registry/engine-pin-relations.tsv` did **not** exist at my start, so the hazard in (b) is `[INFERENCE]` until its source is read; (ii) whether `corpus/SOURCES.md` gains an S554 row later this round — **no S554 row exists at read** (last row is S553; 293 rows, matching F2's `sources:293`); (iii) upstream moves continuously — every number here is the stated 2026-11-04T10:40Z snapshot.
- **Own defects:** none known; seat scratch `/fast/scratch/hyaku/kama-r80/SR01ScoutPins` removed after copying receipts into this seat dir.
