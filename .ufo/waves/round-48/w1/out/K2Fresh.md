# K2Fresh — round-48 fresh-session test (lens kama, C2 operability)

**Verdict: PASS.** Using only `SKILL.md`, the v5 receipt
`.ufo/waves/round-48/c2/live/receipt-1.json` and the `--help` of
`tools/kama-llamacpp-live.py` + `tools/kama-live-replay.py`, a fresh session
re-ran the live evidence in a clean environment (`HOME=$S/home`) and recorded a
new v5 receipt from fresh downloads. Every step exited as expected; there are no
tool defects. Findings are documentation gaps: SKILL.md has no round-48/v5
rows, so the evidence's *measurement form* (C2 counter) is not discoverable from
the three allowed sources, and two validation rules live only in module
docstrings, not in `--help`.

## Evidence

All runs used the scratch clone `$S/lane` (HEAD b85783e8; measured build commit
`380bcdff9c8af06997c482f6eb03db926a794a2b`), `S=/fast/scratch/hyaku/kama-r48/K2Fresh`.

### 1. Re-run of the live evidence (C2 counter) in a clean env

```
HOME=$S/home XDG_CACHE_HOME=$S/cache TMPDIR=$S/tmp \
python3 tools/round48-live-replay-v5-audit.py --repo $S/lane \
  --tip 380bcdff9c8af06997c482f6eb03db926a794a2b --scratch $S
```
Output (full copy: `K2Fresh/c2-counter.out`), exit **0**:
```
receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True
tip=380bcdff9c8af06997c482f6eb03db926a794a2b started=2026-10-26T22:34:34.748708+00:00
```
Reproduces the L1 pre-wave dry-run numbers exactly (met=True, replayed=3/3).

### 2. Per-receipt replay (constructible from the three allowed sources)

```
HOME=$S/home python3 tools/kama-live-replay.py --receipt \
  .ufo/waves/round-48/c2/live/receipt-1.json --work $S/replay-standalone \
  --out $S/replay-standalone.json
```
Output: `replay match=True refused=None mismatches=0 exit=0`, exit **0**.
Rerun receipt written; the counter-style input hashes recompute to the frozen
digests: archive `bf94332a…`, model `270cba1b…`, server `35ac50fb…`.

### 3. Fresh record of a v5 receipt (downloads first)

Downloads (URLs and sha256 from the receipt's `provenance` block):
```
curl -sSL -o llama-b11909-bin-ubuntu-x64.tar.gz https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz
curl -sSL -o stories260K.gguf https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf
tar -xzf llama-b11909-bin-ubuntu-x64.tar.gz
```
sha256 verified: archive `bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b`,
model `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`,
member `llama-b11909/llama-server` `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0`.

Record (flags from `--help`, values from the receipt; full argv in
`K2Fresh/notes.md`), exit **0**: `python3 tools/kama-llamacpp-live.py
--server $S/newlive/llama-b11909/llama-server --model $S/newlive/stories260K.gguf
--model-sha256 270cba1b… --alias kama-r48-live --ctx 256 --threads 1
--server-asset-url https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz
--server-asset-sha256 bf94332a… --server-member llama-b11909/llama-server
--model-url https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf
--server-archive $S/newlive/llama-b11909-bin-ubuntu-x64.tar.gz
--out $S/newlive/receipt-k2fresh.json`.

Receipt (`K2Fresh/receipt-k2fresh.json`): schema `kama-llamacpp-live/v5`,
outcome pass, 11/11 evaluated checks passed; `provenance.verified` = {at:
record, archive_sha256: bf94332a…, member_sha256: 35ac50fb…, model_sha256:
270cba1b…}; `build_info` `b11909-caa8191df`; loading observed (same 503 body
sha `baa09177…`); teardown graceful (returncode 0, SIGTERM sent, no SIGKILL,
port refuses, `log_path` null).

### 4. Comparison against the frozen evidence

```
python3 tools/kama-live-replay.py --compare \
  .ufo/waves/round-48/c2/live/receipt-1.json $S/newlive/receipt-k2fresh.json
```
Output: `compare match=True mismatches=0`, exit **0** — the new receipt's
stable projection equals the committed one.

## Guesses and gaps (the three sources could not answer)

- **G1 — the measurement form is not discoverable.** The C2 counter
  (`tools/round48-live-replay-v5-audit.py`) and its usage (`--repo`,
  `--tip`, `--scratch`, expected output) are absent from all three sources.
  `SKILL.md` at HEAD and at `380bcdff` contains **no** round-48 section and no
  mention of `--server-archive`, v5, or the round-48 counters (grep for
  `server-archive`/`round-48`: 0 hits; the newest rows, lines 1451-1462,
  document only round-47 v4 replay). The live/replay `--help` never
  cross-reference the counter, and the receipt names no measurement tool.
  The per-receipt replay command *is* constructible from the three sources
  (shown in evidence 2), which is how the fresh session satisfies "re-run the
  live evidence" without the counter. Fix: register the counter and the
  receipts path in SKILL.md (proposed lines, see below).
- **G2 — recording is fully derivable; no guess failed.** Alias, ctx, threads
  come from the receipt's `argv`; URLs, digests and the member path from its
  `provenance` block; flag names from `--help`; `--server` must be given
  explicitly (the `--help` default, `shutil.which("llama-server")`, finds
  nothing in a clean HOME). Free instance choices (port via default bind(:0),
  `--out`, download/extraction paths) caused no step to fail.
- **G3 — two validation rules are docstring-only.** The live tool's
  all-or-nothing provenance rule (the five provenance flags must come together;
  a partial set → exit 2 with no receipt) appears only in the module docstring
  (`tools/kama-llamacpp-live.py:30-43`), which `--help` does not print. The
  replay tool's v5 requirements (commit matching the URL's `/resolve/<commit>/`
  and `provenance.verified.at == "record"`) likewise appear only in its
  docstring (`tools/kama-live-replay.py:27-29`). Both rules are enforced, so
  this is a discoverability gap, not a defect.

## Known integration items (context only, NOT re-reported)

Confirmed present at the tip and left to L1: gate-registry-check lists the two
round-48 counters unregistered (SKILL.md has no round-48 rows — the same root
cause as G1); round-41/42/43 counters read the spot-check count 33 vs 34;
hexrun-census has one unknown commit (d0012618).

## Deliverables written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/K2Fresh.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/K2Fresh/notes.md` (per-step journal: derivable vs guessed, commands)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/K2Fresh/proposed-skill-lines.md` (SKILL.md rows removing G1/G2/G3)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/K2Fresh/receipt-k2fresh.json` (new v5 receipt)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/K2Fresh/c2-counter.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/K2Fresh/replay-standalone.json` + `replay-rerun-receipt.json`
