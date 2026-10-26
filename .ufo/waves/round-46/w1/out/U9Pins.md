# U9Pins - next-release frontier (round 46, kama)

Verdict: pin-watch is correct for the lane's llama.cpp pin: v0.7.0 is a real semver release but it is the same commit as bN tag b11669, 86 commits OLDER than the pin b11755, and its tag does not fullmatch `b(\d+)`, so it never enters the comparison. llama.cpp now ships two parallel streams (bN nightlies = GitHub *prereleases*; vX.Y.Z = the only non-prerelease releases, ~every 10-12 days). `releases/latest` therefore returns a stale tag. The bN assumption holds; the real defects are (a) `releases/latest` is the wrong oracle, (b) pin-watch counts tags, which run hours ahead of GitHub releases, (c) no semver axis exists in pin-watch for llama.cpp. No lane file edited.

Run: 2026-10-26T19:58Z, git ls-remote live. Receipts in this directory.

## 1. pin-watch status (all engines)

Command (TMPDIR=/fast/scratch/hyaku/kama-r46/U9Pins):
`python3 tools/pin-watch.py check --pins registry/engine-pins.tsv` -> exit 1

```
engine=sglang pin=v0.5.22 newest=v0.5.22 newer=0 status=current
engine=vllm pin=v0.32.0 newest=v0.32.0 newer=0 status=current
engine=llama.cpp pin=b11755 newest=b11907 newer=131 status=behind
pins=3 current=2 behind=1 missing=0 error=0
```
- sglang: current. vllm: current. llama.cpp: behind (recheck trigger per pin-watch.py:36-39; source S038).
- `newer=131` re-derived independently: 131 `refs/tags/b<N>` lines with N>11755 in `ls-remote-llama.cpp-20261026T1958Z.txt` (7461 bN tags total; awk count). 151 commits lie between b11755 and b11906 (`git rev-list --count b11755..b11906` on the bare clone), so not every commit gets a tag.
- Frontier moved since the last recorded sample: S477 (corpus/SOURCES.md:230) says highest bN b11887, 115 above b11755 at 2026-10-25T20:03Z; now b11907, 131. Round-46 C1 target b11906 is no longer newest: b11907 = 4b851fbee8867136a0c561c8a3521f2fe7d53252 (`gh api repos/ggml-org/llama.cpp/commits/b11907`: committed 2026-10-26T14:19:47Z, "models : replace ggml_tensor** out-params with output structs (#31142)"; not in the bare clone). C1 freeze at b11906 is unaffected (preregistered); b11907 is outside the 91-row verdicts.
- Selftest: `pin-watch.py selftest` -> `selftest pass=9 fail=0`.

## 2. What llama.cpp `v0.7.0` is

Located quotes:
- `gh api repos/ggml-org/llama.cpp/releases/latest`: `tag_name v0.7.0`, `name v0.7.0`, `prerelease False`, `published_at 2026-10-15T17:13:19Z`, `target_commitish 620d2225cc436ab0b001e3200e590e3b286ef9ab`, 1 asset: `nightly-tag.txt`.
- Body: `**Nightly build:** [b11669](https://github.com/ggml-org/llama.cpp/releases/tag/b11669)` and `## Changelog since [v0.6.0]` ... first line `620d2225c llama.cpp : bump version to 0.7.0 (#30603)`.
- ls-remote: `757cad02...  refs/tags/v0.7.0` (annotated) and `620d2225cc436ab0b001e3200e590e3b286ef9ab  refs/tags/v0.7.0^{}`; `620d2225...  refs/tags/b11669` (lightweight). Same commit, two tags. Tag object: `tagger github-actions[bot]`, message `Release v0.7.0` (git cat-file -p v0.7.0).
- Release b11669 (`gh api .../releases/tags/b11669`): `prerelease true`, published 2026-10-15T16:10:46Z, 36 assets, body `llama.cpp : bump version to 0.7.0 (#30603)`.
- CMakeLists.txt at v0.7.0 lines 5-9, 15-21: `set(LLAMA_VERSION_MINOR 7)`, `set(LLAMA_VERSION_PATCH 0)`, `option(LLAMA_BUILD_IS_DEV "llama: dev build" ON)` -> `LLAMA_VERSION "${LLAMA_VERSION_BASE}-dev"`; OFF gives the bare `0.7.0`. Introduced by 680a9ae63 "cmake : introduce semantic versioning (#26839)" 2026-08-12.
- So v0.7.0 = the version-bump commit of the master nightly stream, re-tagged and re-published by a release workflow as a non-prerelease with a changelog summary (body is auto-generated: Overview, Highlights, API changes, Server changes, ggml v0.27.0). It is not a branch/backport: `git merge-base --is-ancestor v0.7.0 b11755` true.

## 3. Does llama.cpp ship semver beside bN? Yes (policy documented)

ggml-org discussion #1579 (https://github.com/ggml-org/ggml/discussions/1579, created 2026-08-07, updated 2026-10-15; receipt ggml-discussion-1579.json), llama.cpp section:
- `The nightly builds use commit number [NUM] for version: Git tags: b[NUM]; Build with CMake option -DLLAMA_BUILD_IS_DEV=ON`
- `Official release builds use semantic versioning: vX.Y.Z ... Build with CMake option -DLLAMA_BUILD_IS_DEV=OFF`
- `The release tags are created on the condition that the internal ggml copy is identical to the released ggml copy.`
- `llama.app ... Publishes the nightly builds instead of the official releases (TODO: switch to official releases?)`; winget same.

Observed semver tags (10, all non-peeled lines of `refs/tags/v[0-9]`): v0.1.0 2026-08-17 (tag exists; `releases/tags/v0.1.0` 404, no GitHub release), v0.2.0 08-21, v0.3.0 08-25, v0.4.0 09-04, v0.4.1 09-14, v0.5.0 09-23, v0.6.0 10-05 (target 8345f333), v0.7.0 10-15 (release published, all `prerelease false`). Gaps 4, 10, 10, 9, 12, 10 days: ~10-day cadence; no v0.8.0 as of 2026-10-26 (tag absent). All bN releases checked (b11669, b11897-b11906) are `prerelease true`; S038 already records `Pre-release` for b11755.

## 4. What it means for pin-watch

Experiments with the frozen tool on the live tag list (`--tags-dir`, files p1-p4.tsv):
| regex | pin | result |
|---|---|---|
| `b(\d+)` (the lane's) | b11755 | behind newest=b11907 newer=131, exit 1 |
| `b(\d+)` | v0.7.0 | missing newest=b11907, exit 2 |
| `v(\d+)\.(\d+)\.(\d+)` | v0.7.0 | **current newest=v0.7.0 newer=0, exit 0** |
| `v(\d+)\.(\d+)\.(\d+)` | b11755 | missing newest=v0.7.0, exit 2 |
- bN assumption (pin-watch.py:19-21, release style = whatever tag_regex admits) is valid: the lane pins bN (S038, S477) and the bN stream is the live frontier. v0.7.0 does not match `b(\d+)` (fullmatch, pin-watch.py:108), so the 10 semver tags are silently ignored; no miscount.
- Hazard: switching to semver silently loses freshness. A v0.7.0 pin reads `current` while master is 237 commits ahead (`git rev-list --count v0.7.0..b11906` = 237; 86 commits between b11669 and b11755). The doc (pin-watch.py:19-21) warns about `.postN` only; there is no note that llama.cpp is dual-stream. Semver would be a sound cadence ONLY as a coarse second axis (new engine row, e.g. `llama.cpp-semver`), never replacing the bN row.
- `gh api .../releases/latest` is not a frontier oracle: it returns v0.7.0 (= b11669), which is ~238 builds behind. GitHub "latest" skips prereleases, and every bN is a prerelease. Anyone following the task phrasing ("releases/latest returns tag v0.7.0") would conclude the pin b11755 is *ahead* of the latest release, which is false as a freshness statement.
- Tag vs release lag: b11907 tag exists but `releases/tags/b11907` is 404; `gh run list` shows release.yml runs `pending` for master commits. b11906: commit 2026-10-26T14:18:45Z, release published 19:45:36Z (~5.5 h). pin-watch counts tags (pin-watch.py:98-111, `git ls-remote --tags`), so `newest` can name a tag whose release/binaries do not yet exist; S038-type rows (asset digest) cannot be re-cited at it until the release lands. For C1, b11906 itself has a published release (`published_at 2026-10-26T19:45:36Z`, 36 assets).
- Lane on-release cadence: on bN granularity the trigger is effectively continuous (131 new tags in ~6 days, ~22/day); semver gives a ~10-day milestone. Recommend (not applied): keep bN row as the per-recheck trigger; add a semver row only to log "v0.8.0 landed (expected ~2026-10-25 +/- 2d)" as a rebase cue; add the tag-vs-release latency and the `releases/latest` stale-oracle note to pin-watch's docstring; do not use `releases/latest` in any lane check.

## Receipts (this directory)
ls-remote-llama.cpp-20261026T1958Z.txt (8215 lines), releases-latest.json, ggml-discussion-1579.json, p1-p4.tsv.

Not run / limits: release.yml scheduling inferred from `gh run list` status only; v0.1.0 no-release inferred from a 404. Tooling installed: none.
