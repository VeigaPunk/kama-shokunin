# R4Check — round 50, lane kama — receipt-shape compatibility

**Verdict: PASS — no schema drift that breaks any consumer.** `check-receipt.py` (v1–v5 gate) and `gguf-identity.py` selftests pass; the gate accepts the round-47 v4 receipt, the round-48 v5 receipt, and all three round-50 rerun receipts (witnessed v5, unwitnessed v4, witnessed v4). The only schema drift is **additive and gate-inert**: the round-50 live tool adds top-level `model_mapping` (always) and `witness` (when `--witness-dir` is given); the gate has no closed-world key-set rule, so unknown top-level keys do not affect any verdict.

## Environment

- Tools run from my own shared clone `S/lane` (clone HEAD `3b79eaddf38246c637cc7ba1a94ab363422876b6`, same as lane working tree HEAD at run time; tools are the round-50 build). Selftests were invoked from the lane path with `TMPDIR` in scratch; every replay used `python3 $S/lane/tools/kama-live-replay.py` (default `--live` resolves to the clone's `tools/kama-llamacpp-live.py`).
- `S=/fast/scratch/hyaku/kama-r50/R4Check`; `TMPDIR=$S`; scratch removed at the end (see Cleanup).
- No tool installed or upgraded; no pacman; no services started by hand (all llama-server processes were started and torn down by the lane replay tool). `pgrep -af llama-server` after everything: `none`.
- Network: three real downloads per replay of `https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz` (22,475,032 bytes — not the ~75 MB the goal text estimates) and `https://huggingface.co/ggml-org/models-moved/resolve/.../stories260K.gguf` (1,185,376 bytes), each sha256-verified by the replay before extraction/execution.

## 1. Selftests

| Check | Command | Result | Exit |
|---|---|---|---|
| Gate selftest | `python3 .../tests/llamacpp-live/check-receipt.py --selftest` | `selftest: 16 VALID and 1 NOT-EVALUATED receipts accepted; 107 mutations + unreadable case rejected` | 0 |
| GGUF selftest | `python3 .../tools/gguf-identity.py --selftest` | `status: passed, passed: 30, failed: []` (schema `gguf-identity-selftest/v2`) | 0 |

## 2. Gate on existing receipts (backward compatibility)

| Receipt | Schema | Result | Exit |
|---|---|---|---|
| (b) `.ufo/waves/round-47/c2/live/receipt-1.json` | `kama-llamacpp-live/v4` | `VALID` | 0 |
| (c) `.ufo/waves/round-48/c2/live/receipt-1.json` | `kama-llamacpp-live/v5` | `VALID` | 0 |

Copies: `out/R4Check/round47-v4-receipt-1.json`, `out/R4Check/round48-v5-receipt-1.json`.

## 3. Round-50 rerun receipts through the gate (forward compatibility)

All three replays: `replay match=True refused=None mismatches=0 exit=0`.

| Rerun | Source receipt | Replay invocation | Gate result | Gate exit |
|---|---|---|---|---|
| (a) `rerun-A-witnessed-v5.json` | round-48 v5 (input a) | `--witness-dir $S/wA/witness --witness-timeout 120`; I acted as observer: polled `ready.json` (`{"schema":"kama-live-witness/v1","port":33793,"pid":3312523,...}`), created `release` at loop 7 | `VALID`; also `VALID` with `--require-schema v5` | 0; 0 |
| `rerun-B-unwitnessed-v4.json` | round-47 v4 | no `--witness-dir` | `VALID`; also `VALID` with `--require-schema v4` | 0; 0 |
| `rerun-C-witnessed-v4.json` | round-47 v4 | `--witness-dir $S/wC/witness`; observer released at loop 7 (port 41007, pid 3313047) | `VALID` | 0 |

Replay result JSONs: `out/R4Check/replay-{A,B,C}-result.json`. Rerun receipt highlights:

- `model_mapping` present in all three: `{"dev":"103:05","inode":...,"mapped":true,"path":"<work>/download/stories260K.gguf","sha256":"270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d","size":1185376}` — path is the replay's fresh download, not the read-only install.
- `witness` present only in A and C: `{"released":true,"orphaned":false,"waited_ms":501|450,"port":...,"pid":...,"dir":...}`. B has no `witness` key at all (omitted, not null) — correct for unwitnessed runs.
- Rerun receipt `child_env_keys` = `["HOME","LANG","PATH","TMPDIR"]`, unchanged from originals; replay `live_child` block records `{"isolated":true,"env_keys":["HOME","LANG","PATH","TMPDIR"],"pdeathsig":"SIGTERM"}`.
- No-network re-check: `kama-live-replay.py --compare` original↔rerun for A and B: `compare match=True mismatches=0`, exit 0 both.

## 4. Schema drift (complete)

Top-level key-set diff, rerun vs original: new = `model_mapping` (+ `witness` when witnessed); lost = none. Emission sites in the producer: `tools/kama-llamacpp-live.py:1763` (`'model_mapping': None` init), `:678` (`model_mapping()`), `:2002-2005` (populate), `:2006-2009` (`receipt['witness'] = hold_for_witness(...)`), `WITNESS_SCHEMA` at `:286`.

**The gate never reads either key**: `grep -n 'witness|model_mapping' tests/llamacpp-live/check-receipt.py` → no matches (checked before and re-confirmed). The gate enforces presence/types of known keys and exact check-id sets (`:1041-1043`) but has no unknown-top-level-key rejection, so the additive keys are inert: old receipts stay VALID, new receipts stay VALID. The new keys are instead bound by the frozen counter C1 (`model_mapping` hashed against the receipt's model at the rerun `child_pid`), which is the right owner for them.

Non-drift notes (informational, no action):
- `replay-A-result.json` notes `tool.sha256 1e5ea0fd…->61e777b7…` — the live tool changed between round 48 and round 50; the replay docstring classifies producer/probe digest deltas as informational notes, not mismatches.
- `pdeathsig` block shape identical in originals and reruns (`{"requested":true,"prctl_ok":"unknown"}`) — no drift.
- Goal-text download estimate "~75 MB per replay" vs actual 22,475,032-byte b11909 ubuntu-x64 archive — estimate only, no behavioral impact.

## Findings

None at defect severity. One watch item: the gate's selftest fixtures (and hence the gate's notion of the receipt shape) do not yet include the two round-50 keys; compatible today because the gate is open-world on top-level keys. If a future round wants the gate itself to bind `model_mapping`/`witness`, that is a change request, not a regression — C1 already binds both.

## Residual risk / verification gaps

- Witness `released=false` / timeout-expiry shape (`orphaned` path) not exercised here — both witnessed runs were released; the un-released shape is covered by lane selftests, not by this seat.
- `gguf-identity.py` was run in selftest only, as scoped; no GGUF file reconciliation against these receipts was requested.
- C1/C2 counter runs and lane-level dry runs are other seats'/L1's; nothing here restates them.

## Cleanup

Scratch `$S` (clone, work dirs, download caches, witness dirs, staged receipt copies) removed after the artifacts above were copied out. No llama-server leftovers (`pgrep -af llama-server` → none). Lane untouched: no writes outside `out/R4Check/` and scratch; the shared clone's working tree was never mutated.

## Artifacts (absolute paths)

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R4Check.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R4Check/round47-v4-receipt-1.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R4Check/round48-v5-receipt-1.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R4Check/rerun-A-witnessed-v5.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R4Check/rerun-B-unwitnessed-v4.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R4Check/rerun-C-witnessed-v4.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R4Check/replay-A-result.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R4Check/replay-B-result.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R4Check/replay-C-result.json
