# K2Fresh — fresh-session test transcript

Item: re-run the round-47 live evidence from scratch using **only** `SKILL.md`,
`receipt-1.json`, and the tools' `--help`, in a clean environment
(`HOME=$S/home`, no `~/.local/opt`, no cache), then record every guessed step,
every failed command, and what `SKILL.md` would need to say.

## Setup (auditor-side, not part of the simulated session)

```
S=/fast/scratch/hyaku/kama-r47/K2Fresh; mkdir -p $S/home $S/tmp
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
# clone HEAD 46a924e027f05614558c45ff02bf7a94ca57d3e1 (3a09a1d93dcc1679... is an ancestor)
# every run below uses: HOME=$S/home XDG_CACHE_HOME=$S/home/.cache TMPDIR=$S/tmp
```

Host facts relevant to the test: Python 3.14.8, git 2.56.0, `jq` present on
PATH, no packages installed by this seat. The lane clone is the only workspace
used; the lane itself was never modified (`git status --porcelain` clean).

## What the three allowed sources actually say

### SKILL.md (kama-shokunin/SKILL.md)

The live-lifecycle instrument rows, newest first:

| row | what it says |
|---|---|
| line 611 (Round-18, “Live v3 tool”) | `python3 tools/kama-llamacpp-live.py --server /home/vgpnk/.local/opt/llama-b11755/llama-server --model /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf --model-sha256 270cba1b…d256d --out /tmp/kama-live.json`; exit map 0/2; “Only loading-envelope grading may be null”; **schema named v3** |
| lines 575-576 (Round-17 v2) | same host paths; 11 checks; gate `tests/llamacpp-live/check-receipt.py` |
| line 537 (Round-16) | same host paths; 10 checks |
| line 656 (Round-20) | receipt gate, `--require-schema v3`; six pins |

Targeted search of `SKILL.md` for `kama-live-replay`, `llamacpp-live/v4`,
`b11909`, `fresh-home`, `--server-asset-url` (provenance flags): **zero hits**
(the only `provenance` occurrences are consumer/legacy/citation provenance,
unrelated). `SKILL.md` contains **no** mention of the replay tool, of the
round-47 receipts, of schema v4, or of the provenance block. The newest live
row (line 611) instructs running the live tool against `~/.local/opt/llama-b11755/llama-server`
and a `~/.cache/…/stories260K.gguf` model — host paths that a clean machine does
not have, and a build (b11755) that is not the frozen evidence (b11909).

### receipt-1.json

- `"schema": "kama-llamacpp-live/v4"` (line 402)
- `provenance` block (lines 391-401): server `asset_url`
  `https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz`,
  `asset_sha256` `bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b`,
  `member` `llama-b11909/llama-server`; model `url`
  `https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf`,
  `sha256` `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`
- `teardown.log_path: null` (line 559)
- `tool` field (lines 568-571) names only `tools/kama-llamacpp-live.py` — the
  receipt does not point to any replay tool
- alias `kama-r47-live`, ctx 256, threads 1 (lines 7-16)

### tools' `--help`

- `kama-llamacpp-live.py --help`: documents the provenance flags but says of
  `--server-asset-url` “provenance: URL of the release archive … **(recorded,
  not fetched)**”. So the live tool alone cannot re-acquire inputs; it needs a
  local `--server` binary and `--model` file.
- `kama-live-replay.py --help`: “kama-live-replay.py - re-run a
  kama-llamacpp-live/v4 receipt from its recorded provenance.” Options
  `--receipt/--work/--out/--live/--timeout/--selftest/--scratch`. The usage
  line prints all options in brackets (nothing marked required); no exit codes
  are documented; no network/digest/clean-home semantics are documented.

## The simulated session, step by step

**Step 1 — “How do I re-run the live evidence?” from SKILL.md.**
The only live-tool row is line 611. Following it literally:

```
$ python3 tools/kama-llamacpp-live.py --server /home/vgpnk/.local/opt/llama-b11755/llama-server \
    --model /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf \
    --model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d \
    --out $S/naive-a.json
$ echo $?
0
```

Exit 0, and the receipt is `schema kama-llamacpp-live/v4`, `outcome pass`,
11/11 evaluated checks passed — but its `server.realpath` is
`/home/vgpnk/.local/opt/llama-b11755/llama-server` (sha
`b6a31a8e…`) and `provenance` is all nulls. **Trap:** on this host the stale
b11755 install and cached model survive, so the documented command “works” and
silently re-runs a *different build* than the frozen b11909 evidence (and
produces a provenance-less v4 receipt). On a clean machine the same command
would fail setup (`server-not-found`/`model-not-found`, exit 2). Either way,
this route never touches the round-47 evidence.

**Step 2 — discovery of the replay tool [GUESS G1].**
Nothing in SKILL.md, the receipt, or the live tool's help names a replay tool.
A fresh session has to guess one exists and find it:

```
$ ls tools/ | grep -iE 'live|replay'
kama-live-replay.py
kama-llamacpp-live.py
round47-live-replay-audit.py
```

`kama-live-replay.py` matches the intent; its `--help` confirms it replays a
v4 receipt. (`tools/round47-live-replay-audit.py` is the counter, not an entry
tool; nothing in SKILL.md distinguishes them — SKILL.md does not register the
round-47 counters at all.)

**Step 3 — locating the receipt [GUESS G2].**
SKILL.md never states where round-47 receipts live. A fresh session must browse
wave dirs to find `.ufo/waves/round-47/c2/live/receipt-1.json` (the three
receipts sit there; the assignment gave me that path, the docs do not).

**Step 4 — running the replay.**
Using the discovered tool with the discovered receipt:

```
$ cd $S/lane
$ HOME=$S/home XDG_CACHE_HOME=$S/home/.cache TMPDIR=$S/tmp \
    python3 tools/kama-live-replay.py \
    --receipt .ufo/waves/round-47/c2/live/receipt-1.json \
    --work $S/work --out $S/replay-out.json
replay match=True refused=None mismatches=0 exit=0
$ echo $?
0
```

Result (`$S/replay-out.json`): `schema kama-live-replay/v1`, `match true`,
`refused null`, `mismatches []`; acquired `archive_sha256
bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b` and
`model_sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`
(equal to the frozen digests); archive/model/server all under
`$S/work/` (`download/llama-b11909-bin-ubuntu-x64.tar.gz`,
`download/stories260K.gguf`, `server/llama-b11909/llama-server`). The rerun
receipt is `kama-llamacpp-live/v4`, `outcome pass`, started
2026-10-26T21:25:56Z, `server.sha256` and `model.sha256` equal to receipt-1's
(35ac50fb… / 270cba1…), 11/11 evaluated checks identical to receipt-1, provenance
echoed. No `llama-server` child left behind; no received port left listening.

So once discovered, the mechanism is executable end-to-end in a clean env with
no host installs. The gaps are all in the **discovery/documentation** chain.

**Step 5 — failed commands recorded.**
- `kama-llamacpp-live.py` with no `--model/--model-sha256`: exit 2,
  `error: --model and --model-sha256 are required unless --selftest is used`
  (self-explanatory).
- `kama-live-replay.py` without `--out` (help shows brackets, so requiredness is
  not visible):
  ```
  $ python3 tools/kama-live-replay.py --receipt .ufo/waves/round-47/c2/live/receipt-1.json --work $S/work2
  kama-live-replay.py: error: --receipt, --work and --out are required
  $ echo $?
  2
  ```

## Guesses required (not in the allowed sources)

| # | guess | where the instruction should have been |
|---|---|---|
| G1 | that a replay tool exists and is named `kama-live-replay.py` | SKILL.md live section |
| G2 | where the round-47 receipts live (`.ufo/waves/round-47/c2/live/`) | SKILL.md live section |
| G3 | that `--receipt/--work/--out` are all required | `--help` usage line |
| G4 | exit-code meanings (0 match, 1 ran-and-differs, 2 refused/could-not-run) | `--help` |
| G5 | network + disk cost (~23 MB github + 1.2 MB HF per replay) | `--help` / SKILL.md |
| G6 | that a lane checkout must be reachable (registry/endpoint-consumers.tsv + tools/kama-probe.sh are resolved from the tools/ location) | SKILL.md live section |
| G7 | clean-env recipe (HOME/XDG_CACHE_HOME/TMPDIR isolation) | SKILL.md live section |

## What SKILL.md would need to say (draft in skill-draft.md)

1. A “Round-47 live evidence replay (v4)” section naming the receipts, the
   replay command, exit codes, network/digest behavior, and the clean-home
   recipe (drafted).
2. A forward-pointing note on the stale live rows (lines 537/575/611): they are
   historical b11755/v3 guidance; the current schema is v4 and the current
   re-run path is `kama-live-replay.py`, not the live tool alone. The live
   tool's provenance flags are recorded-only (`--help` says so) — the receipt is
   so re-run by replay.

## Context not judged by this seat

The C2 counter's `newrow` leg (corpus/SOURCES.md `| S` row naming b11909 and
caa8191df) is absent at clone HEAD — consistent with the L1 dry-run
(`newrow=0`, row “lands at integration”). Not a fresh-session defect.
