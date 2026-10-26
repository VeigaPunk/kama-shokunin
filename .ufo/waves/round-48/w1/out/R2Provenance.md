# R2Provenance — round 48, lane kama

**Verdict: PASS — every recorded provenance value in `.ufo/waves/round-48/c2/live/receipt-1..3.json` matches independent upstream evidence (GitHub release API, HF HEAD headers, HF revision API, and fresh downloads re-hashed in scratch); `server.sha256` equals the freshly extracted archive member's sha256. No defect found.**

## What was checked (receipt claim → outside source)

| Receipt field (all 3 receipts, identical) | Value | Outside source | Result |
|---|---|---|---|
| `provenance.server.asset_sha256` = `provenance.verified.archive_sha256` | `bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b` | `gh api repos/ggml-org/llama.cpp/releases/tags/b11909` → asset `llama-b11909-bin-ubuntu-x64.tar.gz`, `digest: sha256:bf94332a…`, `size: 22475032` | MATCH |
| same, re-hashed | — | fresh `curl -sSL` of `provenance.server.asset_url` → 22,475,032 bytes, `sha256 bf94332a…` | MATCH (size and digest) |
| `provenance.verified.member_sha256` = `server.sha256` | `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0` | extracted member `llama-b11909/llama-server` from the freshly downloaded archive (62 members, member present) → `sha256 35ac50fb…` (17,864 bytes, mode 755) | MATCH |
| `provenance.model.commit` | `499bc8821c6b12b4e53c5bffcb21ec206f212d81` | HF HEAD on the pinned URL → `x-repo-commit: 499bc8821c6b12b4e53c5bffcb21ec206f212d81`; `https://huggingface.co/api/models/ggml-org/models-moved/revision/499bc8821c6b12b4e53c5bffcb21ec206f212d81` → `"sha": "499bc8821c6b12b4e53c5bffcb21ec206f212d81"` | MATCH (both) |
| `provenance.model.sha256` = `provenance.verified.model_sha256` = `model.sha256` = `model_sha256_post` | `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` | HF HEAD → `x-linked-etag: "270cba1b…"`, `x-linked-size: 1185376`; fresh download of the pinned URL → 1,185,376 bytes, `sha256 270cba1b…` | MATCH (etag, size, digest) |
| pinned URL targets an existing file at that revision | — | HF revision API tree lists `tinyllamas/stories260K.gguf` in `ggml-org/models-moved` @ `499bc882…` | MATCH |

`provenance.verified.at` is `"record"` in all three receipts, which per `tools/kama-llamacpp-live.py:193-196,40-41,1559-1566` means the digests were verified at record time (`verify_archive_member` hashes the archive against `asset_sha256` and its member against the server binary's sha256 before the server starts, extracting nothing). The recorded values are consistent with that semantics and now independently reproduced.

## Receipt-to-receipt consistency

- `jq -c '{schema, provenance, server_sha256: .server.sha256, model_sha256: .model.sha256, model_sha256_post, outcome}' receipt-N.json | sort | uniq -c` → exactly one distinct line, count 3: schema `kama-llamacpp-live/v5`, provenance block as above, `outcome=pass`, `internal_fault=null`.
- Full `diff` of receipt-1 vs 2 and 1 vs 3 shows only run-local variance: port (33779 / 41891 / 45023), `child_pid`, `started_utc`/`ended_utc`, `total_503_responses` (23/42/25), `/api/tags` body `created=1793053583` vs `1793053584` (hence differing `body_sha256`), and log-line timings. No provenance/server/model hunk appears in any diff.
- `install.txt` records the server as the round-47 install `/home/vgpnk/.local/opt/llama-b11909/llama-server`; since `server.sha256` equals the archive member I extracted from a fresh download, the installed binary is byte-identical to the pinned release member.

## Commands and exit codes (scratch `/fast/scratch/hyaku/kama-r48/R2Provenance-2`)

1. `gh api repos/ggml-org/llama.cpp/releases/tags/b11909` — exit 0 (one request; full response kept as `release-b11909.json`).
2. `curl -sS https://huggingface.co/api/models/ggml-org/models-moved/revision/499bc8821c6b12b4e53c5bffcb21ec206f212d81` — exit 0 (`hf-model.json`).
3. `curl -sSI https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf` — exit 0, HTTP/2 302 with `x-repo-commit`, `x-linked-etag`, `x-linked-size` (`model-head.txt`).
4. `curl -sSL -o llama-b11909-bin-ubuntu-x64.tar.gz <asset_url>` — exit 0; `sha256sum` → `bf94332a…`.
5. `curl -sSL -o stories260K.gguf <pinned_model_url>` — exit 0; `sha256sum` → `270cba1b…`.
6. `tar tzf` (62 members; `llama-b11909/llama-server` present) + `tar xzf … llama-b11909/llama-server` + `sha256sum` → `35ac50fb…`.
7. `sha256sum receipt-*.json`, `diff` receipt-1 vs 2 and 1 vs 3, `jq` provenance equality — exit 0.

Raw command/output transcript: `verification-log.txt` in the out directory.

## Findings

None. No defect in the recorded provenance; nothing to fix.

## Residual risk / scope notes

- GitHub's `digest` field and HF's `x-linked-etag` are upstream-computed values; the chain is closed locally because both artifacts were independently re-downloaded and re-hashed this session.
- The goal text estimated "~70 MB" for the C2 counter's GitHub download; the pinned asset is 22,475,032 bytes (~22.5 MB). Estimate discrepancy in the goal text only — not a receipt or tool defect.
- I did not re-run the C2 counter or the live tool (out of this seat's scope; covered by the L1 dry run and other seats).
- Tooling directive: no tools installed or upgraded this session (`gh`, `curl`, `jq`, `tar` preexisting); no pacman use.
- Scratch removed (`rm -rf /fast/scratch/hyaku/kama-r48/R2Provenance-2`) after copying all cited evidence to the out directory.
