# Round 89 — lesson (kama)

Base `56174a1fa6a27faa91d3664ef4730b48dd3149c0`; freeze `4eb75c62f6deb1a586a291d611b71775049b34a6`
(`plans/round-89-claims.md`); C1 measured commit `4f9eacf720aa59ed806b31b758571e364658179b`. Read first: the
round-86, round-87 and round-88 verifier spot-checks (all `rejected-honest-stop`; the lane's last six closures
are rejected). Protocol re-read: `MISSION.md`, `AXES.md`, `LEARNING.md`, `CORPUS.md` §SOURCES.md, the round
prompt §6 (run-15 amendments through 46).

## Claims

- **C1 operability (sourced S583/S584/S585):** a router entry whose model file cannot load was graded
  `MODEL_OK router-unloaded-autoload`; the router answers a real request with `500 model name=<id> failed to
  load`. Counter `tools/round89-unloadable-cells.py` (11 live cells, oracle = the real completion; no canned
  expectation). Base `mismatches=5 positive_mismatches=0`; forgeries F1 (round-88 measured probe) 3/3, F2
  (pre-router probe) 7/2; M `mismatches=0 positive_mismatches=0` (`.ufo/waves/round-89/measured/c1.out`).
- **C2 depth (lowest axis, 7):** SKILL §"Router error signatures (llama.cpp router mode)", eight rows each bound
  to a captured b12177 wire answer. Counter `tools/round89-signature-rows.py`; base `rows=0`; forgery battery
  `bound=1 unbound=5 duplicates=1` (`controls/c2-forgeries.out`).

## Gate

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S583 llama.cpp `tools/server/server-models.cpp` @ 6c01da6 (b12177) | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/6c01da6278ab6c69ed67d9124806b50d2b299ba7/tools/server/server-models.cpp — 2026-11-06, sha256 `cab14969b9e5adf08a057c622d1abfc30fd8a17484de5b35942632d739a71108` | `throw std::runtime_error("model name=" + name + " failed to load");` (line 1641) | Source of the frozen oracle mapping (1641, 1956, 1962) at the exact commit of the binary the counter pins; every mapped answer re-observed live (`measured/router-signatures.jsonl`). |
| S584 `ggml/src/gguf.cpp` @ 6c01da6 (b12177) | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/6c01da6278ab6c69ed67d9124806b50d2b299ba7/ggml/src/gguf.cpp — 2026-11-06, sha256 `51bd966ab0494aa20d4087975f17d8b9b8ed9c4b63d7cbffe9315ed45de5dd78` | `GGUFv1 is no longer supported, please use a more up-to-date version` (line 512) | The loader's own checks, so the probe's pre-load rule mirrors what actually rejects a file, not the format's ideal. |
| S585 `gguf-py/gguf/constants.py` @ 6c01da6 (b12177) | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/6c01da6278ab6c69ed67d9124806b50d2b299ba7/gguf-py/gguf/constants.py — 2026-11-06, sha256 `53e6dfa95083d5e81d1da316beb9ea1d4f943cec9dd450db54d849023c01df6c` | `GGML_QUANT_SIZES: dict[GGMLQuantizationType, tuple[int, int]] = {` (line 7035) | Upstream's own block/type-size table; the probe's `QSIZES` was generated from it (36 types, QK_K = 256), not hand-typed. |
| S586 ggml `docs/gguf.md` @ 57e2c2c | **reject** | https://raw.githubusercontent.com/ggml-org/ggml/57e2c2ca2a7cae756b1c4dfafa0cdfef9051d234/docs/gguf.md — 2026-11-06, sha256 `1dead27b6a522709f0127d194e58c21dbbbf00ba1c64fe37c54d1a9048b05020` | "Must be `3` for version described in this spec, which introduces big-endian support." (line 285) | The spec is the format, not the b12177 loader: the loader also loads v2 and requires exact tensor contiguity where the spec only asks for padding. A rule built from it would false-red v2 files. Flip: the loader enforces exactly the spec. |
| `corpus/knowledge/router-unloadable-model.md` | **admit** | cites S583–S585 + own receipts | — | Own-corpus sweep first (KQ143): `grep -ril -E "failed to load\|gguf.*header\|truncat" corpus/knowledge SKILL.md` at base → 7 knowledge files + SKILL. Topical hits: `gguf-declared-identity.md` (a header reader is not loader validation), SKILL E26-15/E26-16 (single-model startup log for a missing / non-GGUF `-m`); the others match "truncat" in unrelated senses (body truncation, untruncated remotes). Plus `grep -n failed corpus/knowledge/router-mode-readiness.md` → the `failed: true` status after a failed load. All three are cited as prior art in the entry. New ground: the pre-attempt state is indistinguishable in the listing, the path is exposed in `status.args`, and a header-only loader-check verdict with live oracle receipts. |
| S582 (README @ 954de24, rejected r88) | **unchanged** (stays rejected) | re-opened 2026-11-06 at b12177 commit 6c01da6: sha256 `eafc1b53…` — identical bytes to S582 | "The `status` object can be:" (unchanged status block, diff vs S581 empty) | Its flip condition (pinned build past b11755) now holds for C1, but no admitted entry cites the README this round (CORPUS rule 4), so the row is not flipped. Recorded, not changed. |

`status` / `recheck` / `used-by` changes on existing rows: none.

## Mistakes

**M1 — a readiness branch generalized from one healthy asset.** Class: verdict rule validated only on inputs
where the asset is good. Evidence: round-88 decision row "`unloaded` (not failed) + autoload → `MODEL_OK`, a
request loads it" (`corpus/knowledge/router-mode-readiness.md`, SKILL §Round-88); its oracle cells used one
valid `stories260K` copy; `controls/c1-base.out` shows the same branch false-green on 5 of 5 unloadable files.
Captured-by: none — KQ141 asks for an oracle cell per documented *configuration*, not per input the branch
silently assumes (here: that the listed file loads). Fix: C1 (`4f9eacf7`) and KQ144 (oracle cells include a
failing variant of every asset the branch assumes). Shown able to fail: `controls/c1-base.out` (red, 5) and
`controls/c1-f1.out`/`c1-f2.out`.

**M2 — a mutating git command in the lane.** Class: write-scope breach. Evidence: L1 ran `git worktree add` from
the lane to get a clean checkout of M for the harm suites; `git worktree list` showed
`/fast/scratch/hyaku/kama-r89/L1/m/wt` registered in the lane's `.git/worktrees`. Captured-by: round prompt §6
item 4 ("Never … a mutating git/jj command"); the L1 did not apply it to `worktree`. Fix: removed with
`git worktree remove --force` (list back to one entry, `jj-lane.sh state` tracked=0); clean checkouts use
`git clone --shared <lane> <scratch>` thereafter. Shown able to fail: `git worktree list` printed two entries
before removal.
