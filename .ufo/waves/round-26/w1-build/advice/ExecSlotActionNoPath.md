# ExecSlotActionNoPath — recommendation (round-26 C1, wave 1)

Verdict: 4 slot-action faults confirmed live on the fixture (llama-server b11755 / 704366d), each with a >=20-byte signature that is verbatim in a pinned source and absent at base; the frozen counter counts 2 of the 4 in any order due to clause (g), and the recommended counted pair is save-no-path + restore-missing-file.

## Faults confirmed (each reproduced twice on ports 47608-47611, `-t 2`, timeout 90, logs under /fast/scratch/hyaku/kama-r26/ExecSlotActionNoPath/)

1. POST /slots/0?action=save (also restore/erase) without `--slot-save-path` -> 501; body:
   `{"error":{"code":501,"message":"This server does not support slots action. Start it with `--slot-save-path`","type":"not_supported_error"}}`
   Signature: `This server does not support slots action. Start it with `--slot-save-path`` (75 B) — server-context.cpp:5408.
2. POST /slots/abc?action=save with `--slot-save-path` set -> 400; body:
   `{"error":{"code":400,"message":"Invalid slot ID","type":"invalid_request_error"}}`
   Signature candidate: `invalid_request_error` (21 B) — server-common.cpp:96 (the only >=20B verbatim source literal in this body; "Invalid slot ID" is 15 B).
3. POST /slots/0?action=bogus with `--slot-save-path` set -> 400; body:
   `{"error":{"code":400,"message":"Invalid action","type":"invalid_request_error"}}`
   Signature candidate: `invalid_request_error` (same shared token as #2).
4. POST /slots/0?action=restore with a nonexistent save file (--slot-save-path set) -> 400; body:
   `{"error":{"code":400,"message":"Unable to restore slot: No available space in KV cache or invalid slot save file","type":"invalid_request_error"}}`
   Signature: `No available space in KV cache or invalid slot save file` (56 B) — server-context.cpp:3084.

Body sha256 identical between both reproduction runs for every trigger (no-path-save 93b83e653dfd, invalid-slot-id-nonnum d4928b601943, invalid-action 05cfb9478bc9, restore-missing-file b7d816d8b7dc).

## Extra observations

- POST /slots/999?action=save (nonexistent numeric id) succeeds with 200 `{"id_slot":999,...,"n_saved":0,...}` — the slot is created on demand, so a numeric id is never "invalid" unless it can't be parsed (stoi) or the task-level slot lookup misses; the 400 "Invalid slot ID" path is reachable with a non-numeric id (route-level stoi) — but not with a large valid integer.
- All three of #2/#3/#4 emit the shared `invalid_request_error` type token in their channel text; no >=20B *distinct* static literal exists for #2 vs #3 beyond the shared token (the per-fault messages "Invalid slot ID"/"Invalid action" are under MIN_BYTES and the JSON punctuation flanking `invalid_request_error` is assembled at runtime, not verbatim in source).

## Counter result (scratch extract of frozen tip a23c0e0, placeholder SKILL rows + SOURCES S901-S904 + registry; lane untouched)

- Order [save, invalid-id, restore-missing, invalid-action]: `registered 4 counted 2 target 12 met False`; not-counted: restore-missing (g_distinct), invalid-action (g_distinct). Receipt: out/ExecSlotActionNoPath/count-receipt.json.
- Order [save, restore-missing, invalid-id, invalid-action]: `registered 4 counted 2`; not-counted: invalid-id, invalid-action. Receipt: out/ExecSlotActionNoPath/count-receipt2.json.
- Cause: clause (g) — `invalid_request_error` occurs in the channel text of whichever invalid-request row counts first, blocking every later row whose own signature or channel text contains it. At most 2 of the 4 candidates can count in any order.

## Recommendation to L1 (integration)

- Register the counted pair: S901 save-no-path (501, distinctive literal) + S903 restore-missing-file (long distinctive literal). Prefer these over `invalid_request_error` rows: the generic token can be claimed first by any 400 row from another seat this round, silently killing the invalid-id/invalid-action rows.
- Keep #2 (invalid-slot-id) as the fallback if the L1 wants one "Invalid slot ID" variant instead of restore-missing — it counts in the same slot (first invalid-request row in order). Never register two of {invalid-id, invalid-action, restore-missing-file} in one round; the second fails clause (g) regardless of order.
- candidates.json ships all four entries with id/row "TBD" per the schema (L1 assigns real ids/S-rows). Scratch counter used ids exec-slot-action-no-path-* and S901-S904.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w1-build/out/ExecSlotActionNoPath/`: candidates.json, RUNS.txt, count-receipt.json, count-receipt2.json, raw/ (7 trigger bodies+logs from run 1/2), raw/run2/ (4 second-reproduction bodies+logs).
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w1-build/advice/ExecSlotActionNoPath.md` (this report).
- Scratch only (not delivered, not lane): /fast/scratch/hyaku/kama-r26/ExecSlotActionNoPath/{run-triggers.py,run2.py,candidates-check.py,cfg/,extract/}.

## Risks

- `invalid_request_error` collision with sibling seats (see recommendation).
- The `/slots/0?action=save` trigger is echoed in no request bytes; the 501 message contains `--slot-save-path` as text — clause (e) is about request echo only, and `--slot-save-path` never appears in these requests (verified by the counter's e_not_echoed=True).
- All servers stopped; ports 47608-47611 closed (ss clean); no processes of this seat remain (pgrep shows only sibling seats on other ports).
- No installs performed (no new tools needed).
