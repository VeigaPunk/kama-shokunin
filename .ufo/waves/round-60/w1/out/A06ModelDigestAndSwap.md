# A06ModelDigestAndSwap — model-pin attack (round 60, kama, wave w1)

Axes: **operability** (C1) and **calibration** (C2, lowest assigned = 7). Milestone: round60 C1 falsification.
Seat: leaf; advisory findings only. No lane source was edited; all runs used my own scratch
`/fast/scratch/hyaku/kama-r60/A06ModelDigestAndSwap` (removed after artifact copy; receipts preserved under
`receipts/` next to this report). Every `python3` below is `/usr/bin/python`; TMPDIR pointed at the seat scratch.
Attacked claim: **C1-r60** ("the lane ... imports the digest-pinned lane fixture GGUF under a caller nonce") via the
tool's `--model-gguf` surface, `tools/kama-ollama-live.py` at freeze base `ec3b0d583ed4eb05c7ae935dc59f560e86b0a80b`
(tool commit e0b5b1e, controls 8b9f306). Pinned fixture `model_sha256=270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`
(verified before the runs: 1185376 bytes, sha256 re-computed on this host = pin).

## Tool anatomy relevant to the pin (read, not run)

- `tools/kama-ollama-live.py:268-273` — the **only** content check: `sha256_file(gguf)` vs `pin['model_sha256']`;
  failure ⇒ `MODEL_DIGEST_MISMATCH`, exit 2. It runs **before** `free_port()` and before any child is spawned.
- `:337-341` — much later, the Modelfile `FROM {gguf}` is written and `ollama create` **re-reads the same path**.
  Window between the pre-hash and that read spans server boot + ready poll + 4 HTTP captures (measured ≈1.4 s of run).
- `:352-354` `tags-lists-model` and `:397-398` `ps-lists-loaded` check digest *shape* and tags↔ps *consistency* only;
  no post-create check re-hashes the imported blob against the pin. The receipt records `pin.model_sha256` (the pin),
  never the imported content's hash.

## Case results

Attack fixtures built from the pinned fixture copy (never touching the original, opened read-only):

| file | construction | size | sha256 |
|---|---|---|---|
| `corrupt.gguf` | copy, byte at offset 16 (GGUF header, kv-count field) XOR 0xFF | 1185376 | `6936cee88eda9d3e1a23900e5aeedbc1fe34878b39df07bf189965b653f1943a` |
| `truncated.gguf` | copy, first 1 000 000 bytes only | 1000000 | `27d4b24cf4d111b9e4a5367b849509ac78ed60a00ada7a9941a73a1bec28c05d` |
| `validdiff.gguf` | copy, byte at offset 1 000 000 (tensor data) XOR 0x01 → **still a valid GGUF container**, different weights | 1185376 | `bc1ad4c9c4bfba12054dd9b4fe5da463f1cc716c1748ebfd387d68bbed7b99e8` |
| `symlink.gguf` | symlink → real fixture | (target) | resolves to `270cba1b…` |

No second GGUF exists natively: `find /home/vgpnk/.cache /home/vgpnk/.local/opt -name '*.gguf'` returns exactly
`/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf`, so the "different valid GGUF" case is satisfied by the
crafted `validdiff.gguf` (a different *valid* model, which is the stronger probe).

Command form for every case (`W` = per-case work dir under the seat scratch):

```
/usr/bin/python tools/kama-ollama-live.py --work W --nonce <nonce> --out W/receipt.json --model-gguf <variant>
```

| case | variant | exit | verdict | `model-digest` check | serve.log | `models/blobs/` |
|---|---|---|---|---|---|---|
| 1 | corrupt (header byte) | 2 | `MODEL_DIGEST_MISMATCH` | `passed=false`, evaluated=true | **absent** | NONE |
| 2 | truncated (84.3 %) | 2 | `MODEL_DIGEST_MISMATCH` | `passed=false`, evaluated=true | **absent** | NONE |
| 3 | validdiff (valid container) | 2 | `MODEL_DIGEST_MISMATCH` | `passed=false`, evaluated=true | **absent** | NONE |
| 4 | symlink → fixture | **0** | **`MODEL_OK`** | `passed=true` | present | `sha256-270cba1b…` (1 185 376 B, re-hashed = `270cba1b…` = pin) + 2 manifest blobs |

All three static variants are stopped at the pre-hash gate in ~0.06 s: the server is never started (no serve.log, no
port bound, no blob imported — hence nothing in `models/blobs/` to compare; the pin check is the whole defense and it
holds). Note the gate rejects on digest alone: case 3 is a perfectly loadable model and is still rejected before Ollama
parses it. Case 4 shows the pin is **content-bound**: `realpath` resolves the symlink, so the run is a genuine pinned
run — every one of the 16 checks true (port 52519, teardown clean: `port_closed=true, sigkill_needed=false`), and the
imported blob re-hashes to the pin. No path-based bypass exists in either direction.

## Race: swap between hash and `ollama create` (TOCTOU)

Method: run the tool on a copy of the fixture; a watcher polls (1 ms) for the appearance of `W/serve.log` — which the
tool opens **after** the gate (`:275` region) — then flips byte 1 000 000 in place to the `validdiff` value before
`ollama create` reads the file. Same length, single-byte write.

4/4 attempts landed (`race-attempt1..4/receipt.json`):

```
attempt 1: trigger +0.055 s after start, swap done +0.057 s (delta 1.3 ms) → exit 0, verdict MODEL_OK
attempt 2: +0.056 s / +0.057 s (1.0 ms) → exit 0, MODEL_OK
attempt 3: +0.055 s / +0.056 s (1.1 ms) → exit 0, MODEL_OK
attempt 4: +0.053 s / +0.054 s (1.1 ms) → exit 0, MODEL_OK
```

Raced work dir (attempt 1) contents: `models/blobs/` = `sha256-bc1ad4c9c4bfeb…` (**the different valid GGUF**),
`sha256-8d45426565…` (its manifest), `sha256-d7560296…`; the pinned blob `sha256-270cba1b…` is **absent**. The manifest
`models/manifests/.../kama-a06race01/latest` names `sha256:bc1ad4c9…`, not the pin. Every tool check is `passed=true`
in all four receipts — the tool reported `MODEL_OK`, exit 0, for a model that is not the pinned fixture.

## Answers

**Can the tool end MODEL_OK with a model that is not the pinned fixture? YES — demonstrated 4/4.** The single
pre-hash gate (`:272-273`) is check-then-use: the file is re-read at `ollama create` (`:338-341`) with no re-verify.
Post-create checks cannot see the swap: `tags-lists-model` only demands a 64-hex digest; `ps-lists-loaded` compares
ps digest to tags digest (internal consistency). Note also that `/api/tags`/`/api/ps` digests are *manifest* digests
(case 4: `8cf91c7109e7…`, 475 B), never the pinned file digest — no HTTP surface exposes file content.

**What the counter's blob-sha check adds — it is the only content proof after the gate.** Importing
`tools/round60-c1-counter.py` (module level = frozen constants only) and running its `verify()`:

- raced receipt attempt 1 (all 16 tool checks green): `['manifest-layer', 'blob-missing']` —
  `:122-123` manifest text must contain `sha256:FROZEN_MODEL_SHA` (raced manifest names the wrong digest),
  `:126-131` re-hashes `models/blobs/sha256-FROZEN_MODEL_SHA` (file absent ⇒ `blob-missing`);
- symlink case 4 receipt (true pinned run): `[]` — accepted, so the verifier does not over-reject;
- corrupt case 1 receipt (`MODEL_DIGEST_MISMATCH`, exit 2): 23 failure ids (`verdict`, `check:model-digest`, … `blob-missing`) — rejected;
- raced receipt replayed under a stale nonce: `['nonce', 'capture-parse', 'manifest', 'blob-missing']` — rejected.

So `round60-c1-counter.py`'s work-dir re-derivation closes exactly the hole the tool's own verdict leaves open: a
`MODEL_OK` receipt alone is **not** evidence that the served model is the pinned fixture; the C1 predicate holds only
because the counter independently re-derives manifest + blob from the run's work dir.

## Fix-shaped suggestion (not applied — advisory only)

Close the window inside the tool: after `ollama create`, re-hash the imported blob
(`work/models/blobs/sha256-<manifest layer>`) or simply re-hash `gguf` and add a `blob-digest` check vs
`pin['model_sha256']`; passing the already-open file descriptor (or a private copy) to the create step removes the
read-twice surface entirely.

## Limits (stated)

One Ollama version (pinned v0.40.11, `binary-digest`/`running-exe-digest` both verified in the full-lifecycle runs),
CPU-only child, one fixture model, window timings measured on this host (1 ms poller; swap landed within ~1 ms of the
log-open trigger). The race required local write access to the `--model-gguf` path — in-scope threat for a tool whose
contract is "imports the digest-pinned fixture".

## Artifacts preserved

`receipts/<case>/receipt.json` (+ `serve.log` where a server ran, + `manifests/` for `case4-symlink` and
`race-attempt1`): case1-corrupt, case2-truncated, case3-validdiff, case4-symlink, race-attempt1..4. Scratch
`/fast/scratch/hyaku/kama-r60/A06ModelDigestAndSwap` removed after copy. No tools were installed or upgraded for this
seat (stdlib-only work). Disk guard checked pre-run: `/fast/scratch/hyaku 27% use, 592.3G free`.
