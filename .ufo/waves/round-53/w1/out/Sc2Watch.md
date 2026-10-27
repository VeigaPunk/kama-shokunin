Verdict: llama.cpp b11909 pin is 3 published releases behind the latest (b11913) and is still a prerelease; the pinned b11909 asset URL resolves byte-for-byte to the frozen digest `bf94332a…` and the pinned model URL still serves the frozen sha256 `270cba1b…`. No defect found; the round-52 unresolved "has b11909 graduated from prerelease" is resolved: no.

All observations 2026-10-27T06:14–06:16Z. Evidence bundle: `.ufo/waves/round-53/w1/out/Sc2Watch/` (evidence.txt, releases-tags.txt, release-b11909-today.json, model-head.txt).

## 1. Release state — how far behind is b11909

Command (one request): `gh api repos/ggml-org/llama.cpp/releases?per_page=5 --jq '.[].tag_name'`, exit 0 (`.ufo/waves/round-53/w1/out/Sc2Watch/releases-tags.txt`):

```
b11913
b11912
b11910
b11909
b11908
```

- Three published releases are newer than the b11909 pin: **b11910, b11912, b11913** (latest = b11913). Note the list skips b11911 — no b11911 release exists; the numeric delta is +4 but the release-count delta is +3.
- Same top-5 list the round-52 Sc2Watch seat observed (`.ufo/waves/round-52/w1/out/Sc2Watch.md`), consistent with b11909 having been published 2026-10-26T21:00:58Z, i.e. ~9 h before this check.

Follow-up one request to resolve the round-52 unresolved: `gh api repos/ggml-org/llama.cpp/releases/tags/b11909`, exit 0 (`release-b11909-today.json`): `prerelease: true`, `draft: false`, `published_at: 2026-10-26T21:00:58Z`, `target_commitish: caa8191df159f764fb0160e3d2fc6be008948aee` (matches the frozen round-47 record `.ufo/waves/round-47/c2/release-b11909.json`). **b11909 has not graduated from prerelease.**

## 2. b11909 asset URL — resolves and hashes to the pin

```
$ curl -sSL -o llama-b11909-bin-ubuntu-x64.tar.gz -w 'http_code=%{http_code} size=%{size_download}' \
    https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz
http_code=200 size=22475032        (exit 0; final URL a release-assets.githubusercontent.com signed URL)
$ sha256sum llama-b11909-bin-ubuntu-x64.tar.gz
bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b
```

Matches the frozen pin (`bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b`, e.g. `.ufo/waves/round-47/c2/live/receipt-1.json:397`) and the live GitHub release record's digest field for `llama-b11909-bin-ubuntu-x64.tar.gz` (22475032 bytes, `release-b11909-today.json`). Extra member check: `tar -xOf … llama-b11909/llama-server | sha256sum` → `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0`, equal to the installed binary and the receipts' `server.sha256`. **The mutable-prerelease asset has not changed since freeze.**

## 3. Pinned model URL — HEAD

```
$ curl -sIL https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf
HTTP/2 302 → HTTP/2 200   (exit 0; full headers in out/Sc2Watch/model-head.txt)
```

- `content-length: 1185376`, `x-linked-size: 1185376` — the tiny model.
- `x-linked-etag: "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"` — exactly the pinned model sha256 (`MSHA`, recorded `.ufo/waves/round-47/c2/live/install.txt:6`).
- `x-repo-commit: 499bc8821c6b12b4e53c5bffcb21ec206f212d81` — same repo revision the round-52 seat HEADed.
- The 302 target is a `us.aws.cdn.hf.co` signed URL with `Expires=1793085285` (~1 h validity). Consequence already noted round 52: only the stable resolve URL + pinned sha256 are safe to record; a receipt pinning the CDN URL would rot within the hour. Current receipts do the right thing.

## Cross-references (not re-run, in scope notes only)

- The lane's registry pin `registry/engine-pins.tsv:4` still names llama.cpp **b11755** (source S038) — the pin-watch framing, distinct from the live-serving pin b11909 this seat watches. Round-52 Sc2Watch recorded pin-watch counting 136 release tags beyond b11755 (carried, not re-counted here).
- Frontier disposition for the L1: re-verification trigger for the b11909-sourced rows should note upstream is 3 releases ahead and moving roughly 3 tags/day; a future pin bump is due but not urgent — the pinned bytes are intact and replay-verifiable today.

## Confidence / unresolved

- High confidence in all three observed statuses (commands, exits, hashes above; raw artifacts in the out bundle).
- Time-sensitive: release list, prerelease flag, URL availability and digests are as of 2026-10-27T06:14–06:16Z; the asset remains mutable upstream (prerelease), so this is a point-in-time check.
- No defects to propose fixes for; counters, preregistration and controls were not touched (frozen).
- No tools installed this round (gh, curl, sha256sum, tar already present; pacman paused host-wide per orchestrator ruling).
