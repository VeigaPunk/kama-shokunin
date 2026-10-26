# V2Live — round 47 code review: kama-llamacpp-live.py v4

**Verdict: NO blocking defects. The v4 change is internally consistent and behavior-verified end to end; the three receipts carry exactly what the code writes. Three low-severity items: stale `v3` comments (L944/L988/L1221), `--selftest` covers none of the new paths, and the teardown fault-fallback dict omits `log_path` (pre-existing).**

Reviewed commit: lane `3a09a1d93dcc16799cf6c4b48786e6440af134c4` (wave build). Diff vs freeze `bbcc6dc2fbd7fc04b1d91a97ffa239a6601cd5ba` on `tools/kama-llamacpp-live.py`: 30 insertions / 4 deletions, hunks: docstring, `SCHEMA`, `teardown` dict, parser description, 4 new parser args, digest-validation loop, provenance block. No changes to this file between `3a09a1d` and lane HEAD `46a924e` (`git diff 3a09a1d 46a924e -- tools/kama-llamacpp-live.py` empty), so the review target is current.

## Findings by severity

### No blockers.

### Low 1 — stale `v3` strings in comments/docstrings (cosmetic; not functional schema refs)
Grep of the v4 file (`git grep -nE "v3" 3a09a1d -- tools/kama-llamacpp-live.py`):
- L944 `"""Return the v3 outcome and process exit code from check state."""` (`_outcome_exit`)
- L988 `# Byte-contiguous spans of the pinned llama.cpp commit that ground the v3` (source-binding comment)
- L1221 `"""Exercise procfs parsing, live tcp6 ownership rows, v3 verdicts and` (`_selftest` docstring)

All three describe behavior unchanged in v4, so they are harmless, but they violate the "every 'v3' string" bump-consistency ask. Proposed fix: s/v3/v4/ in those three strings (patch below). No `v3` appears in the parser description, `SCHEMA`, error paths, or receipts (receipts contain 0 `v3` mentions, 1 `v4`).

### Low 2 — `--selftest` covers none of the changed paths
`_selftest()` (L1220–1320) exercises: `_install_identity_selftest`, procfs tcp6 parsing, live loopback listeners, `_outcome_exit` mappings, `_emit` atomic publish (uses `SCHEMA` constant only), `_restore_signal_handlers`. It does NOT cover: the digest-validation loop (L1362–1367), the provenance block construction (L1381–1386), or `teardown()`'s `log_path=None` change (no server is ever started in selftest). Ran `python3 tools/kama-llamacpp-live.py --selftest` from a `git clone --shared` of the lane: exit 0 (`selftest: ok; closed tcp6 listeners ...`). The parser `--selftest` help ("run parser and outcome self-tests without a server") is accurate but the new paths have no self-test. Proposed fix: factor the validation loop into `_validate_digests(args)`, build the provenance dict in a small pure helper, and assert both from `_selftest()`.

### Info — teardown fault-fallback dict omits `log_path`
If `teardown()` raises, main's fallback `td` dict (L1655–1666) lacks `log_path` (and `log_lines_truncated`), so the receipt's `teardown` would omit those keys rather than carry `log_path: null`. Pre-existing (not part of the v4 diff) and only reachable via internal fault; the docstring's "teardown.log_path null" holds on every successful path. Noted for completeness.

## Verified claims (evidence)

### 1. Schema bump consistency
- `SCHEMA = 'kama-llamacpp-live/v4'` — L54.
- Parser description `'...emit a kama-llamacpp-live/v4 receipt.'` — L1097–1100.
- Docstring L20–28 documents v4 provenance block + `teardown.log_path` null.
- Consumer contract matches: `kama-live-replay.py` L38 `LIVE_SCHEMA = "kama-llamacpp-live/v4"`, refuses non-v4 (`not-a-v4-receipt`, L70–71).
- All three receipts: `"schema": "kama-llamacpp-live/v4"`.

### 2. Provenance block recorded verbatim
Code (L1381–1386): `'provenance': {'server': {'asset_url': args.server_asset_url, 'asset_sha256': args.server_asset_sha256, 'member': args.server_member}, 'model': {'url': args.model_url, 'sha256': args.model_sha256}}` — straight attribute copy, no transformation; digest keys were lowercased earlier by the validation loop (consistent with replay's lowercase-only `HEX64`).
Receipts (all three identical):
```
{"model": {"sha256": "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d",
            "url": "https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf"},
 "server": {"asset_sha256": "bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b",
            "asset_url": "https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz",
            "member": "llama-b11909/llama-server"}}
```
Matches the item's expected values and `install.txt` (asset digest, model digest, member path) exactly. Replay's `provenance()` requires exactly these five keys, rejects missing/unsafe member, and requires provenance model digest == receipt model digest — all satisfied (L68–86).

### 3. Digest validation (case, length)
Code (L1362–1367): `re.fullmatch(r'[0-9a-fA-F]{64}', value)` for `model_sha256` and `server_asset_sha256`; rejects anything but 64 hex digits (any case), lowercases before recording; `parser.error` names the exact flag (`name.replace("_","-")`). Probes (run from the clone, `TMPDIR=$S`):
- `--model-sha256 <12 hex>` → `error: --model-sha256 must be 64 hex digits`, exit 2.
- `--server-asset-sha256 nope` (valid model digest) → `error: --server-asset-sha256 must be 64 hex digits`, exit 2.
- `--model-sha256 $(printf 'A%.0s' {1..64})` (64 uppercase) → accepted past the parser (run then fails later on a missing model file, exit 2) — case-insensitive accept confirmed.
- `--model-sha256 $(printf 'g%.0s' {1..64})` → error, exit 2.
Empty-string/whitespace-padded would also fail fullmatch; `None` (default) is skipped. Normalization to lowercase matches replay's `HEX64 = re.compile(r"[0-9a-f]{64}")` (replay L41).

### 4. `log_path` null vs docstring
`teardown()` (L868–924) always returns `'log_path': None` (L876) and unlinks the temp log in a `finally` (L919–923) even if reduction raises; the outer epilogue additionally unlinks when `teardown` didn't run (L1759–1762). Docstring L24–25 states exactly this. Receipts: `teardown.log_path: null`; kept `log_lines` inlined (> L918-918). Confirmed by live run (below).

### 5. Receipt fidelity — receipts carry exactly what the code writes
- Tool hash: `sha256sum` of the lane/clone file = `65301a3c76f925bf3316673d3774269f6d93ca22f4ccdb7c7139e6826b8ae65d` == `receipt-*.json` `tool.sha256` → receipts were produced by this exact file version.
- Working tree receipts at the lane are byte-identical to the versions committed at `3a09a1d` (md5 `e3ffeb82…`/`4032d2dd…`/`b8a06d50…` both sides).
- Receipts 1–3 differ only in volatile fields (started/ended_utc, port, child argv port, child_pid, transitions, t_ms inside captures/loading_503); all non-volatile fields identical, all 11 checks `passed=true, evaluated=true`, outcome `pass`, `port_listener_ownership: child`.
- Live reproduction: ran the same binary from the clone with the identical inputs (server binary, model, digests, provenance args) → exit 0, receipt `rerun-receipt.json` with schema v4, provenance identical, `teardown.log_path: null`, server sha256 `35ac50fb…`, model sha256 `270cba1b…`, same 11 passed checks; non-volatile diffs vs receipt-1 were only `loading_503.t_ms` (8 vs 10) and capture timing fields. Server torn down (no `llama-server` processes after; no temp log left in `$S`).

## Proposed edits (also as unified diff in out/V2Live/v4-review-fix.patch)
1. L944, L988, L1221: `v3` → `v4` in the three comment/docstring strings.
2. Factor digest validation (L1362–1367) into `_validate_digests(args)` and provenance dict (L1381–1386) into `_provenance(args)`; call both from `_selftest()` with a 64-uppercase, a non-hex, a short, and a `None` case, asserting acceptance/`parser.error`/lowercasing and exact dict equality.

## Verification gaps
- C1/C2 counter runs are the L1 integration's measurement; not re-run here (frozen; not this seat).
- No network fetch was performed; replay behavior is read (L1–124), not executed (C2 dry run already reports `met=False` only because the b11909 SOURCES row lands at integration).
