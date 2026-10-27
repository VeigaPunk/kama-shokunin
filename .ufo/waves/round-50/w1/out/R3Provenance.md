# R3Provenance — round 50, lane kama (C1 frozen constants vs outside)

**Verdict: PASS — all three frozen constants of the C1 counter (`tools/round50-replay-bind-audit.py`) match the outside world byte-for-byte today; no defect found.**

Scope: SERVER_SHA, MODEL_SHA, MAPS_URL content. No counter run, no lane mutation, no install. Scratch cleaned.

## 1. SERVER_SHA — MATCH

Frozen (counter line 101):
`SERVER_SHA = "35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0"`

Commands (all exit 0, in my scratch):
```
curl -sSL -o llama-b11909-bin-ubuntu-x64.tar.gz \
  https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz
#   http=200 size=22475032
sha256sum llama-b11909-bin-ubuntu-x64.tar.gz
#   bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b
tar -xzf llama-b11909-bin-ubuntu-x64.tar.gz -C asset/        # top dir: llama-b11909/
sha256sum asset/llama-b11909/llama-server
#   35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0
```
Corroboration of the whole chain:
- GitHub release record (one `gh api repos/ggml-org/llama.cpp/releases/tags/b11909` call): asset `llama-b11909-bin-ubuntu-x64.tar.gz` size 22475032, `digest = sha256:bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b` — equals the asset hash I downloaded and the `ASSET_SHA` the round-47/48 counters freeze (`tools/round47-live-replay-audit.py:95`, `tools/round48-live-replay-v5-audit.py:135`).
- The installed binary the round-48 receipts exercised, `/home/vgpnk/.local/opt/llama-b11909/llama-server`, hashes to the same `35ac50fb…` — frozen constant == release member == installed binary.

## 2. MODEL_SHA — MATCH

Frozen (counter lines 102–105): commit `499bc8821c6b12b4e53c5bffcb21ec206f212d81`, URL `https://huggingface.co/ggml-org/models-moved/resolve/499bc882…/tinyllamas/stories260K.gguf`, `MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"`.

```
curl -sSL -o stories260K.gguf '<MODEL_URL>'   # http=200 size=1185376; resolve accepted the pinned commit
sha256sum stories260K.gguf
#   270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d
```
Pinned URL resolves (HF redirect to its xet CDN served 200) and the served bytes hash exactly to MODEL_SHA. Evidence copy kept: `out/R3Provenance/stories260K.gguf`.

## 3. MAPS_URL content — MATCH

Frozen (counter line 106): `MAPS_URL = "man7.org/linux/man-pages/man5/proc_pid_maps.5.html"`. Lane text copy: `.ufo/waves/round-50/c1/proc_pid_maps.5.txt` (7564 bytes, sha256 `e7cdf0ff1c8d8d87e5c92e529a09270945ca3b7cafb8e823a7ca3d294f3c16a2`).

```
curl -sS -o proc_pid_maps.5.fresh.html https://man7.org/linux/man-pages/man5/proc_pid_maps.5.html
#   http=200 size=11702
sha256sum proc_pid_maps.5.fresh.html
#   3a33949653ca5132a368ed40d74b8e56ea4a8bb6b8f364fe615ddfd994d0be18
```
The lane copy is a tag-strip text extraction (it even retains script leftovers such as `})();`), so raw-byte equality with the HTML is not the criterion. Reproduced the extraction on the fresh fetch:

```python
html.unescape(re.sub(rb'<[^>]*>', b'', fresh_html))   # strip tags, decode entities
```
Result: **byte-identical** to the lane copy (difflib ratio 0.991 before entity decoding; the only deltas were `&gt;`, `&mdash;`, `&nbsp;` vs their decoded forms). Verified: the `.txt` is a faithful text copy of the page man7.org serves today. Evidence copy kept: `out/R3Provenance/maps-fresh.html`.

Note: the counter itself only checks the MAPS_URL *string* appears in new SOURCES rows (`tools/round50-replay-bind-audit.py:537`); the `.txt` is supporting copy, verified here independently.

## Findings

None. No defect in the frozen constants; nothing to fix, no proposed edit.

## Residual risk / verification gaps

- Provenance is point-in-time (2026-10-26): man7.org and both release/model URLs serve matching bytes today; upstream could change later, but the counter re-downloads and hash-checks server and model on every run (`round50-replay-bind-audit.py:337,345-347,571`), so drift becomes a loud failure, not a silent pass.
- Extraction method for the maps `.txt` was inferred from the artifact (tag-strip + entity decode); the exact producing command is not recorded in the lane. The reproduction is exact and deterministic, so this does not weaken the match.

## Housekeeping

- Tools installed/upgraded: none (curl, sha256sum, tar, python3, gh already present).
- Processes: I started no llama-server; the two live ones found (`pgrep -f llama-server`) belong to peer seat J2NoPdeathsig's scratch run and were left untouched.
- Scratch `/fast/scratch/hyaku/kama-r50/R3Provenance` removed after copying evidence.

## Files written (absolute)

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R3Provenance.md (this report)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R3Provenance/verification.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R3Provenance/maps-fresh.html
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R3Provenance/stories260K.gguf
