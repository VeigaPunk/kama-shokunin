# U2Pins: pin gap and prerelease cliff (closure r47-D7)

Verdict: the witnessed replays are re-runnable today and no tag-count or prerelease threshold ends that. They stop when GitHub removes or alters the b11909 asset, or when the commit-pinned HF model object goes away. Nothing in the lane watches either condition: pin-watch tracks b11755 (not the b11909 the replays use) and exits 1 permanently.

All observations 2026-10-26 ~23:30 UTC. Receipts are in this directory.

## 1. Pin gap (pin-watch.py check)
`python3 tools/pin-watch.py check --pins registry/engine-pins.tsv` → exit 1 (`pin-watch-check.out`):
```
engine=llama.cpp pin=b11755 newest=b11912 newer=135 status=behind
pins=3 current=2 behind=1 missing=0 error=0
```
- registry/engine-pins.tsv row `llama.cpp ... b11755 S038`. The pin is the round-16/r41 b11755 (S038). The replays and the C1 counter use b11909 (S488 / S494 / digest-ledger.tsv:17). **b11909 appears in no pin row**, so pin-watch cannot say anything about the dependency the witness replays rest on. Proposed fix: add a second row `llama.cpp-replay ... b11909 S488 S494` (distinct engine name) so `behind` for the replay binary is measured separately.
- `git ls-remote --tags` b-tags above b11909: **2** (b11910, b11912; b11911 does not exist). Above the pin b11755: 135 (132 of them at or below b11909). The upstream cadence is ~22-26 tags/day (b11755 published 2026-10-20T11:18Z, b11912 2026-10-26T22:30Z). The `newer` count therefore grows by ~25 per day and carries no re-pin signal: `behind` is permanent. Exit 1 does not distinguish "recheck docs" from "replay inputs gone".
- b11910 and b11912 both have releases with 36 assets.

## 2. Is b11909 still a prerelease with digest bf94332a…?
One call, `gh api repos/ggml-org/llama.cpp/releases/tags/b11909` (`b11909-release.json`): `prerelease: true`, `draft: false`, published 2026-10-26T21:00:58Z, target caa8191df159f764fb0160e3d2fc6be008948aee, 36 assets; asset `llama-b11909-bin-ubuntu-x64.tar.gz` digest `sha256:bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b`, size 22475032. Equal to the receipt `asset_sha256` and to the host copy `~/.local/opt/llama-b11909-bin-ubuntu-x64.tar.gz` (sha256sum matches). `curl -sIL` on the asset URL → 200. HF model URL (commit 499bc882…) → 200.

## 3. The prerelease "cliff", located
Walking the release list (pages of 100, `releases-page10-prerelease-flip.tsv`):
- All 100 newest releases (b11777..b11912) are `prerelease=true`; all releases from page 20 (b8978, Apr 2026) down to the 2023 `master-*` builds are `prerelease=false`.
- The flip is on page 10 at ~2026-08-21: b10549 (08-21T09:23Z) false, b10566/b10573 true. In the same week upstream started a versioned stable series v0.1.2 (08-18) ... v0.7.0 (2026-10-15, `releases/latest`). The b-series became a nightly/prerelease series.
- **Stable v0.x releases carry no binaries**: v0.7.0, v0.6.0, v0.5.0 each have exactly one asset, `nightly-tag.txt` (v0.7.0 contains `b11669`). `releases/latest` therefore returns a tag with no llama-server. Only bN prereleases carry `llama-bN-bin-ubuntu-x64.tar.gz`.
- Consequences: (a) the prerelease flag itself does not affect download URLs, digests, or the tag API: it is not a replay cliff. (b) Any re-pin must be to a bN prerelease picked by number, never via `latest` or a stable tag. (c) pin-watch regex `b(\d+)` is correct for this (ignores v-tags).
- Retention evidence: every sampled old release still has its assets (page 40 Aug 2025, page 60 Jun 2024, page 79 Mar 2023 `master-*`; b11000, b11755, b11889, b11906 fetched with 33-36 assets). No deletion of a published release was observed.
- Risk that is real: **77 of 1023 b-tags ≥ b10545 have no release** (`tags-ge-b10545.txt` vs `releases-pages1-10-btags.txt`; e.g. b11902, b11903 → 404 on /releases/tags). I cannot tell from this whether those are CI builds that never published or published-then-deleted [INFERENCE: unobserved]. If upstream does delete prerelease objects, b11909 can vanish as a release object while the tag stays, which pin-watch (tags only) would never notice.

## 4. When witnessed replays stop being re-runnable
`tools/kama-live-replay.py` fetch (`:91-103`) is https-only, no cache, no file://; `acquire` (`:142-148`) hashes after download. So replay fails (loud, before extraction) when:
1. GitHub 404/410 on `releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz` (release or asset deleted), or the bytes differ (`digest-mismatch`). Probability no calendar date: no retention clock observed; the sole risk is deletion of a prerelease object.
2. HF `ggml-org/models-moved/resolve/499bc882…/tinyllamas/stories260K.gguf` removed. The repo name already records one move; the commit pin makes it content-stable but not location-stable. The C1 counter also downloads the same URL for its vocabulary.
3. Network-less host: replay has no offline path although the host holds the digest-matching archive (`~/.local/opt/llama-b11909-bin-ubuntu-x64.tar.gz`, 22475032 B) and an extracted `~/.local/opt/llama-b11909/`; `fetch` refuses `file://` outside selftest. Re-runnability is purely online.
Not causes: tag count above b11909 (2 now, +~25/day), the prerelease flag, `latest` pointing at v0.7.0.

## 5. What re-pins them
- Cheap guard (proposed, `replay-inputs-probe.py` here; run → `replayable`, exit 0, `probe.out`): one `gh api` release call comparing the asset digest to the receipt + two HEADs. Wire it beside pin-watch so the signal is "replay inputs missing", not "newer tags exist".
- If the asset is gone: pick a bN prerelease that has `llama-bN-bin-ubuntu-x64.tar.gz`; run `kama-llamacpp-live.py --server-asset-url … --server-asset-sha256 … --server-member llama-bN/llama-server --model-url <same HF commit URL>` to emit v5 receipts; freeze a new counter with that bN's `/proc/<pid>/exe` digest and a README commit at that tag (round-49 counter hard-codes the b11909 digest and caa8191d); add `S` rows and a `registry/release-recheck-bN.tsv`; set the `llama.cpp-replay` pin row. The old receipts remain historical but unreplayable and must be marked so.
- Cheaper hedge (proposed): let `acquire` try a digest-addressed local cache first (`~/.local/opt/<name>` keyed by sha256), still hash-verified, so deletion upstream does not kill replays while the host copy exists; and record the host archive in digest-ledger.tsv:17 as the fallback source (already listed as retained).

## Tooling
No installs. `pgrep -f llama-server` run: no leftovers from this seat (none started). Scratch removed.
