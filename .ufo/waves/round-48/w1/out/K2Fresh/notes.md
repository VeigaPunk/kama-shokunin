# K2Fresh fresh-session journal (round 48)

Test: using ONLY `SKILL.md`, the v5 receipt `receipt-1.json`, and the `--help`
of `tools/kama-llamacpp-live.py` + `tools/kama-live-replay.py`:
(1) re-run the live evidence from scratch in a clean environment (HOME=$S/home),
(2) record a new v5 receipt after downloading the release archive and pinned model.

Environment: `S=/fast/scratch/hyaku/kama-r48/K2Fresh`; one shared clone
`$S/lane` of the lane (HEAD b85783e8, build commit 380bcdff present).

## Step 1 — re-run the live evidence (clean HOME)

Counter (the lane's machine form of the evidence re-run):
```
HOME=$S/home XDG_CACHE_HOME=$S/cache TMPDIR=$S/tmp \
python3 tools/round48-live-replay-v5-audit.py --repo $S/lane \
  --tip 380bcdff9c8af06997c482f6eb03db926a794a2b --scratch $S
```
Output (exit 0):
```
receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True
tip=380bcdff9c8af06997c482f6eb03db926a794a2b started=2026-10-26T22:34:34.748708+00:00
```
(Full text copied to `c2-counter.out`.)

Fallback form constructible from the three allowed sources (replay tool):
```
HOME=$S/home python3 tools/kama-live-replay.py --receipt \
  .ufo/waves/round-48/c2/live/receipt-1.json --work $S/replay-standalone \
  --out $S/replay-standalone.json
```
Output: `replay match=True refused=None mismatches=0 exit=0` (exit 0); rerun
receipt saved; `inputs` hashes: archive bf94332a…, model 270cba1b…, server
35ac50fb… (the frozen digests).

## Step 2 — record a new v5 receipt (fresh downloads)

1. Download asset (from `provenance.server.asset_url`, verify
   `asset_sha256`): `curl -sSL -o llama-b11909-bin-ubuntu-x64.tar.gz https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz`
   → sha256 `bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b` ✓
2. Download model (from `provenance.model.url`, verify `sha256`):
   `curl -sSL -o stories260K.gguf https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf`
   → sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` ✓
3. Extract `provenance.server.member` (`llama-b11909/llama-server`) → sha256
   `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0` ✓
4. Record (flags from `--help`; values from the receipt):
```
HOME=$S/home XDG_CACHE_HOME=$S/cache TMPDIR=$S/tmp \
python3 tools/kama-llamacpp-live.py \
  --server $S/newlive/llama-b11909/llama-server \
  --model $S/newlive/stories260K.gguf \
  --model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d \
  --alias kama-r48-live --ctx 256 --threads 1 \
  --server-asset-url https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz \
  --server-asset-sha256 bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b \
  --server-member llama-b11909/llama-server \
  --model-url https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf \
  --server-archive $S/newlive/llama-b11909-bin-ubuntu-x64.tar.gz \
  --out $S/newlive/receipt-k2fresh.json
```
   Exit 0. Receipt: schema `kama-llamacpp-live/v5`, outcome pass, 11/11
   evaluated checks passed, `provenance.verified` = {at: record,
   archive_sha256: bf94332a…, member_sha256: 35ac50fb…, model_sha256:
   270cba1b…}, build_info `b11909-caa8191df`, loading observed (same 503 body
   sha baa09177…), teardown graceful (returncode 0, SIGTERM, no SIGKILL).

Validation (C2 comparison contract):
```
python3 tools/kama-live-replay.py --compare \
  .ufo/waves/round-48/c2/live/receipt-1.json $S/newlive/receipt-k2fresh.json
```
Output: `compare match=True mismatches=0`, exit 0.

## Guesses / gaps (what the three sources did NOT say)

- G1 — The counter (`tools/round48-live-replay-v5-audit.py`) and its usage are
  not derivable from SKILL.md, the receipt or the two tools' --help. SKILL.md
  (HEAD and @380bcdff) has NO round-48 section and no mention of `--server-archive`,
  v5, or the round-48 counters (grep: zero hits for `server-archive`, `round-48`);
  the fresh round-47 rows (1451-1462) document only v4. The per-receipt replay
  command IS constructible from the three sources (used as fallback).
- G2 — The recording recipe (alias/ctx/threads, URLs, member, five provenance
  flags) is fully derivable from receipt + --help; no runtime guess failed. I chose
  download/extraction paths, default port (bind :0), and `--out` myself (instance facts).
- G3 — `--help` does not state that the provenance flags are all-or-nothing
  (any partial set → exit 2, no receipt). It is only in the module docstring
  (`tools/kama-llamacpp-live.py` lines 30-43), which `--help` does not print.
  Same for the replay tool's v5 commit/verified-at-record requirements
  (`tools/kama-live-replay.py` lines 27-29).

## Failures

None. No user command failed; every step exited as expected. (An early
`curl -sI … | head -5` probe showed curl exit 23 from the closed pipe — pipe
artifact, not a network failure.)

## SKILL.md draft lines (to remove each guess)

See `proposed-skill-lines.md` in this directory.
