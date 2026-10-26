# R2Provenance — round 47 lane kama, receipt provenance vs the outside

**Verdict: VERIFIED — every provenance value recorded in receipt-1/2/3.json (asset name, size, sha256, member, model URL, model sha256, b11909 = caa8191df159f764fb0160e3d2fc6be008948aee) matches the live outside sources exactly, including a fresh full re-download of both artifacts; no defect found. One hardening observation (revision pinning), no contract breach.**

Seat: R2Provenance (leaf). Date: 2026-10-26. Lane read-only; scratch `/fast/scratch/hyaku/kama-r47/R2Provenance` (removed at end). No tools installed; `gh` + `curl` already present. One GitHub API request total (`gh api repos/ggml-org/llama.cpp/releases/tags/b11909`, exit 0). No clone taken (item needs no lane git access).

## 1. GitHub release b11909 vs receipts (one API request)

`gh api repos/ggml-org/llama.cpp/releases/tags/b11909` (raw saved to scratch `release-b11909.json`; jq locally, no extra quota):

| Field | API | Receipt/install.txt | Match |
|---|---|---|---|
| tag_name / name | `b11909` | b11909 | yes |
| target_commitish | `caa8191df159f764fb0160e3d2fc6be008948aee` | preregistration, receipts `build_info` `b11909-caa8191df` | yes |
| prerelease / draft | `true` / `false` | frozen in `tools/round47-live-replay-audit.py:19-21` ("prerelease true") | yes |
| published_at | `2026-10-26T21:00:58Z` | same as frozen value | yes |
| asset name | `llama-b11909-bin-ubuntu-x64.tar.gz` | receipts `provenance.server.asset_url` | yes |
| asset size | `22475032` | `install.txt` "22475032 bytes" | yes |
| asset digest | `sha256:bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b` | receipts `provenance.server.asset_sha256`; frozen at `round47-live-replay-audit.py:23-25` | yes |
| asset state | `uploaded` (all 36 assets) | — | yes |
| browser_download_url | `https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz` | receipts `provenance.server.asset_url`, byte-identical | yes |

## 2. Artifact ground truth (fresh downloads, not cache)

- Asset: `curl -sL <asset_url>` → HTTP 200, `size=22475032`; `sha256sum` = `bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b` — equals the API digest and the receipts. GitHub release digests are computed server-side at upload, so the release record itself pins the bytes.
- Member: `tar -tzf` (62 entries) contains exactly `llama-b11909/llama-server` — equals receipts `provenance.server.member`.
- Extracted `llama-b11909/llama-server`: sha256 `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0` — equals `server.sha256` in all three receipts and the `llama-server` hash in `install.txt`. Ran it (`--version`, prints and exits, no service started): `version: 0.7.0-dev (build 11909, commit caa8191df)`, exit 0 — first-hand tie of binary → release commit `caa8191df…`.
- Model: `curl -sIL <model url>` → 302 then 200; download 1,185,376 bytes, `sha256sum` = `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` — equals receipts `provenance.model.sha256`, `model.sha256`, `model_sha256_post`, and `install.txt`.

## 3. Receipt invariants (jq on receipt-1/2/3.json)

All three, identical: `schema=kama-llamacpp-live/v4`, `outcome=pass`, 11 checks all `passed:true`, `build_info=b11909-caa8191df` (starts `b11909-`, per counter leg), `teardown.log_path=null` (matches claim: temp log always deleted), `ctx=256`, `threads=1`, `alias=kama-r47-live`. `jq -cS .provenance | sha256sum` identical across all three (`3dd9370b…`): the provenance block is uniform, no per-receipt drift. Contract shape matches `tools/kama-llamacpp-live.py:1123-1131,1381` and the frozen receipt contract in `tools/round47-live-replay-audit.py:30-38`.

## 4. Is the HF resolve URL stable?

Observed behavior (`curl -sIL`, 2026-10-26 ~21:30Z):

- `https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf` itself is a **stable re-resolvable pointer**: both an independent HEAD and GET resolved (302 from `x-powered-by: huggingface-moon`, ratelimit `"resolvers";q=3000;w=300`).
- Each redirect target is a **signed, expiring CDN URL**: `https://us.aws.cdn.hf.co/xet-bridge-us/658084…/7cfbf69e…?…Expires=1793053834&Policy=…` — `Expires=1793053834` = 2026-10-26T22:30:34Z, i.e. a ~1-hour window from my 21:31Z request; the 302 carries `cache-control: no-store`. The GitHub asset URL behaves the same way (302 to `release-assets.githubusercontent.com/...&se=2026-10-26T22:20:39Z&sig=…`, a ~1h SAS).
- **What the receipt needs to record — and does record**: the stable resolve/download URL plus the sha256, never the CDN URL. The C2 replay contract (`tools/round47-live-replay-audit.py:30-52`) re-acquires from those URLs into `--work`, verifies both digests before use, and its tamper leg proves a digest mismatch is refused. Both URLs point at immutably-hashed artifacts (GitHub server-side digest; HF `x-linked-etag: "270cba…"` = the sha256, `x-linked-size: 1185376`), so a ~1h CDN token is invisible to the receipt. Verdict: recorded form is the correct, stable form.

## 5. Finding (hardening observation, not a defect)

- **F1 (info)** — the model pointer pins the mutable branch, not a revision: `resolve/main` in receipts' `provenance.model.url`. HF exposes the repo commit `x-repo-commit: 499bc8821c6b12b4e53c5bffcb21ec206f212d81` on the 302; recording it (e.g. a `model.commit` field, or `resolve/<commit>` as url) would make the source pointer immutable as well, not just integrity-verified. Integrity today is fully carried by the sha256 (contract leg + tamper refusal), so nothing is broken; if `ggml-org/models-moved` (name suggests migration risk) ever moved the blob under `main`, replay would refuse rather than silently substitute. Proposed fix (optional, v5 schema): add `model.commit`; no current evidence or behavior is wrong.

## 6. Residual risk / verification gaps

- I verified the receipts' provenance against the outside and the tamper contract text; I did not execute `kama-live-replay.py` or the C2 counter itself (that is the counter's leg, run by L1/integration).
- CDN expiry post-`Expires` is asserted from the signed-URL structure (`Expires`/`Policy`/`sig`, `cache-control: no-store`), not by waiting for token death; irrelevant to receipts since they never store CDN URLs.
- HF rate limits are unauthenticated (`x-hf-warning`); repeated replays are small (1.2 MB) and well inside the 3000/300s resolver window.
- Receipt `started_utc` values are ~21:16Z, before my verification; per counter leg `replay` the rerun-time check is enforced by the counter, not re-proven here.

## Evidence copies

`receipt-1.json`, `receipt-2.json`, `receipt-3.json` copied unchanged to `.ufo/waves/round-47/w1/out/R2Provenance/`. Scratch removed.
