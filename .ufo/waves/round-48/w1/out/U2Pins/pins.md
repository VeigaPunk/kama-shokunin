# U2Pins: pin gap at 2026-10-26T22:34Z

Verdict: two of three pins are current (sglang, vllm); llama.cpp pin b11755 (S038) is 135 bN tags behind, but the v5 receipts and S488 are at b11909 and trail upstream by only 2 tags (b11910, b11912). Both tags above b11909 are prereleases like b11909 itself.

## Commands and outputs
`TMPDIR=$S python3 tools/pin-watch.py check --pins registry/engine-pins.tsv` (exit 1):
```
engine=sglang pin=v0.5.22 newest=v0.5.22 newer=0 status=current
engine=vllm pin=v0.32.0 newest=v0.32.0 newer=0 status=current
engine=llama.cpp pin=b11755 newest=b11912 newer=135 status=behind
pins=3 current=2 behind=1 missing=0 error=0
```
`git ls-remote --tags https://github.com/ggml-org/llama.cpp.git` (8219 lines; 7465 `refs/tags/b<N>` tags, bare, no `^{}`), parsed with awk on field 2:
- highest bN = b11912. Top four: b11908, b11909, b11910, b11912. There is no b11911 tag, and `gh api .../releases/tags/b11911` returns 404.
- above b11909: **2** (b11910 = 63b4b303bd87456adc2f09d56c7e1f74e9e26673, b11912 = 961c376a2daa42220ec09663b9bde32c5fba1f70).
- above b11755 (the registry pin): 135, identical to the pin-watch `newer=135`.
- above b11889 (round-44 re-verification build): 18. Above b11897 (round-45 sample): 14.
- b11909 still resolves to caa8191df159f764fb0160e3d2fc6be008948aee, the S488 commit.
Saved raw output: `llamacpp-ls-remote-tags.txt` in this directory.

`gh api repos/ggml-org/llama.cpp/releases/tags/b11909 --jq '{tag,prerelease,draft,published,target}'`:
`{"draft":false,"prerelease":true,"published":"2026-10-26T21:00:58Z","target":"caa8191df159f764fb0160e3d2fc6be008948aee"}`.
So **b11909 is still a prerelease** (not a draft). I ran the same call for b11910 (prerelease true, 2026-10-26T21:20:07Z) and b11912 (prerelease true, 2026-10-26T22:30:51Z), plus one 404 for b11911; four calls total, not one.

## Gap per engine
| engine | pin | newest | tags above pin | status | notes |
|---|---|---|---|---|---|
| sglang | v0.5.22 | v0.5.22 | 0 | current | no trigger |
| vllm | v0.32.0 | v0.32.0 | 0 | current | no trigger |
| llama.cpp (registry pin, S038) | b11755 | b11912 | 135 | behind | the 91+11 rows re-verified at b11889 (round 44/45) are already past the registry pin; the registry row was not moved, so pin-watch overstates the gap relative to the corpus (b11889: 18 behind) |
| llama.cpp (v5 receipts, S488/S489) | b11909 | b11912 | 2 | behind by 2, prerelease | |

Observation (not a defect in the frozen counters): `registry/engine-pins.tsv` line 4 still says b11755 with source S038; neither the b11889 re-verification nor S488 (b11909) is a pinned row. pin-watch therefore reports 135 whichever build the freshest work used, and it reports tags, not releases: it cannot say that every one of those tags is a prerelease.

## Next re-verification trigger
- S488 and the v5 receipts (S489/S490 successor; receipts `.ufo/waves/round-48/c2/live/receipt-{1,2,3}.json`): the S488 recheck column and `llamacpp-loading-lifecycle.md:3` say `recheck: on-release`, "when the installed llama.cpp build changes". Concretely a trigger has **already fired in the weak sense**: b11910 and b11912 exist. If the rule is read as "any newer bN tag", re-run now with `kama-live-replay.py` against a b11912 asset (new asset URL, digest, member; v5 pins the model at /resolve/<40-hex>/ so only the server side moves). If the rule is read as "the build the lane actually installs", no trigger has fired and none is dated. I recommend the lane write one: re-run when pin-watch shows at least one tag above the pinned build **and** that tag is a non-prerelease release, or after 14 days whichever is first; as of now every tag above b11909 is a prerelease, so by the stricter reading the trigger has not fired. [INFERENCE: the threshold is my proposal, not an existing lane rule.]
- S488 identity claim: it asserts b11909 = caa8191d... and prerelease:true; both still hold at 22:34Z. It re-opens when the tag moves (ls-remote SHA differs), or the release record flips `prerelease` to false (the claim then stays true as of its date but the stale `"prerelease":true` quote needs a dated successor).
- Registry pin llama.cpp b11755: the dated trigger is already met (behind, exit 1) and was filed as such in `corpus/knowledge/engine-pin-watch.md:51`; the next action is re-pinning the registry row to b11909 with source S488, which makes the gap 2 and the pin consistent with the newest evidence.
- sglang and vllm: next trigger is any new `vX.Y.Z` tag; both gaps are 0 today.

## Remaining unknowns
- Whether b11910/b11912 changed the loading envelope, /health, /v1/models or props (no release notes read, no b11912 binary run; I started no server).
- `immutable` flag of b11909 not re-read (the S488 quote has `"immutable":false`).
