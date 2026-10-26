Verdict: llama.cpp pin b11755 is behind (newest b11910, 134 newer; 1 tag above b11909, 4 above b11906); sglang v0.5.22 and vllm v0.32.0 current; b11906 population and S488 triggers are both already met by b11910 (no server/common file changed).

# U2Pins: engine pin status and next release triggers (sampled 2026-10-26T21:25Z)

## Pin-watch result
Command: `TMPDIR=$S python3 tools/pin-watch.py check --pins registry/engine-pins.tsv` -> exit 1 (behind), ~2 s.

| engine | pin | newest | newer | status |
|---|---|---|---|---|
| sglang | v0.5.22 | v0.5.22 | 0 | current |
| vllm | v0.32.0 | v0.32.0 | 0 | current |
| llama.cpp | b11755 | b11910 | 134 | behind |

Footer `pins=3 current=2 behind=1 missing=0 error=0`.

## llama.cpp tag count (`git ls-remote --tags https://github.com/ggml-org/llama.cpp.git`, exit 0)
- 7,464 `bN` tags, highest b11910 = `63b4b303bd87456adc2f09d56c7e1f74e9e26673`; no peeled `^{}` bN lines.
- Above b11909: **1** (b11910). Above b11906: 4 (b11907..b11910). Above the pin b11755: 134 (matches pin-watch).
- Tag->commit: b11906 `4d71b42f…`, b11907 `4b851fbe…`, b11908 `a4699400…`, b11909 `caa8191d…` (matches the C2 claim), b11910 `63b4b303…`.
- Both b11909 and b11910 already have GitHub releases (prerelease, 36 assets each): b11909 published 2026-10-26T21:00:58Z, b11910 2026-10-26T21:20:07Z. So b11909 asset rows (S488) can cite a live release. (The round-46 note that b11907 returned 404 does not apply to b11909.)

## What changed upstream after b11906 (gh compare, 2 requests)
- b11906..b11909: 3 commits (models: output structs #31142; llama: no_alloc out of hparams #31141; hexagon MUL_MAT_ID #31169). Touches src/llama-kv-cache*, llama-memory*, llama-context.cpp, llama-hparams.h, hexagon.
- b11909..b11910: 1 commit (opencl KV-cache set_tensor #30471), only `ggml/src/ggml-opencl/ggml-opencl.cpp`.
- b11906..b11910: no file under tools/server, common/, tools/quantize or gguf-py. So the b11906 population's source files (server-context.cpp, server-http.cpp, arg.cpp etc.) are byte-identical at b11909 and b11910 by path, which makes a mechanical carry cheap, but only `git rev-parse b11909:<path>` per row proves it; this seat did not run that check.

## Next re-verification triggers
1. **b11906 ledger population** (91 on-release rows, `registry/release-recheck-b11906.tsv`; trigger text in `corpus/README.md` ~741): next `bN` tag above b11906. That trigger is already met: b11907, b11908, b11909 and b11910 exist. It is not new with round 47; the population is 4 tags stale now. Practical next re-verification point: the next round's re-check should anchor on the highest bN with a published release at sample time (b11910 now), not on a tag above b11906 alone. Because no server/common/quantize/gguf-py file changed through b11910, a re-check at b11910 would be a mechanical carry (blob-identical) for all rows whose path is outside src/llama-*; the rows touching src/llama-kv-cache/memory/context/hparams (if any in the population) need a real re-read since those files changed at b11909.
2. **S488 (b11909 row the L1 adds, release identity + live receipts at caa8191d)**: trigger is the next bN above b11909, **already met by b11910** (published 2026-10-26T21:20:07Z, 19 min after b11909). S488 is a release-asset identity/receipt row, so a newer tag does not falsify it; it only makes it non-newest. Its meaningful triggers are: (a) a new release the lane chooses to adopt (re-run the C2 replay with `kama-live-replay.py` against the new asset URL/sha256); (b) the asset digest at the release URL changing (re-fetch `gh api repos/ggml-org/llama.cpp/releases/tags/b11909` digest vs bf94332a…); (c) the 30-day recheck. Calendar due: sample date + 30 d = **2026-11-25** if S488 is dated 2026-10-26 (S477's own 30 d recheck is due 2026-11-24).
3. **Lane pin b11755 (S038)** behind by 134 builds; round 41 seat R41F09 read b11755->b11887 server sources (unchanged) but that is a lead, not admitted. engine-pins.tsv still names b11755 although the live receipts are now at b11909: the pin and the live-run release have diverged (b11909 is 154 builds ahead). Whether to bump the pin is a lane decision; the file's S column cites only S038.
4. sglang v0.5.22 and vllm v0.32.0: no newer release; next trigger is any `vX.Y.Z` tag above them (`.postN`/rc are not releases by the tag regex).

## Notes / caveats
- pin-watch tags are tags, not releases: S477-style inventory figures go stale within hours (it was 130/b11907 at 19:57Z, 134/b11910 at 21:25Z). Any row quoting "N tags above pin" must carry its sample timestamp.
- Tool reads: `gh api` x5 total (2 compare, 1 commit sha, 1 ref, 2 release). No installs. Scratch /fast/scratch/hyaku/kama-r47/U2Pins removed.
