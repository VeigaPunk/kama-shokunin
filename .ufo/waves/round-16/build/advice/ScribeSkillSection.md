# ScribeSkillSection — round-16 SKILL.md draft report

Access date for every source: 2026-10-20. Lane root: `/home/vgpnk/Projects/shokunin/kama-shokunin`.

## Behavior
Drafted the append-ready round-16 SKILL.md section at `.ufo/waves/round-16/build/drafts/skill-section.md`. It covers the seven-verdict vocabulary with `MODEL_LOADING`, one decision-table row plus a near-miss row, the exact loading envelope with an error-signature table, and seven-column gate/capability rows for `tests/probe-verdicts/check.py`, `tools/kama-llamacpp-live.py` and `tests/llamacpp-live/check-receipt.py`. Nothing was integrated into `SKILL.md`; L1 integrates.

## Gates
None run. Only read-only facts were gathered: `sha256sum`, `ls`, grep, and public-source fetches via `curl` piped to `grep -n` (no files written outside the owned paths). No lane gate, harness or probe was executed.

## Findings (path:line, quote, access 2026-10-20)

1. **Envelope source is confirmed, with corrected line numbers.** Raw llama.cpp b11755 `tools/server/server-http.cpp` (`https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/server-http.cpp`): line 308 `if (!is_ready.load()) {`; line 314 `res.status = 503;`; line 318 `{"message", "Loading model"},`; line 319 `{"type", "unavailable_error"},`; line 323 `"application/json; charset=utf-8"`. The spec's cited range `307-325` is a few lines wide of the exact 308–323 block.
2. **The state middleware precedes auth and routing.** `server-http.cpp:354` `if (!middleware_server_state(req, res)) {` then `:357` `if (!middleware_validate_api_key(req, res)) {`. Frontend paths are exempt at 309–310 (`frontend asset, allow it to load and show "loading"`). [INFERENCE for runtime: a keyed loading server returns 503 before 401; source-derived, not observed.]
3. **Documentation matches the body.** README `tools/server/README.md` @ b11755 line 479 `### GET \`/health\`` and line 487 "Explanation: the model is still being loaded." Line 486 documents the body with code-first key order.
4. **Server key order is insertion order.** `common/json.h:24` "object keys keep the order in which they are added". So the server output is `message, type, code`, matching the L1 smoke body. Parsers must compare fields, not order. Serialization is compact: `tools/server/server-common.cpp:1696` `return data.dump_safe();` (default indent −1). [INFERENCE: compact spacing inferred from `dump_safe()` default plus the L1 smoke body.]
5. **Tag commit verified.** GitHub API `https://api.github.com/repos/ggml-org/llama.cpp/git/refs/tags/b11755` → `"sha": "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"`, matching the spec's `704366d76`.
6. **Frozen probe matches the current probe.** `sha256sum` on `.ufo/waves/round-16/frozen/kama-probe-before.sh` and `tools/kama-probe.sh` both give `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64`. The repair has not landed.
7. **Drift is automatic.** `tools/kama-probe.sh:820` `if [ "$verdict" != "MODEL_OK" ]; then drift=true; fi`. A `MODEL_LOADING` row will therefore count as drift and exit 2 with no extra code.
8. **Existing FOREIGN_SERVICE fallback (the overreach).** `tools/kama-probe.sh:520–522` `C_REASON=non-2xx-non-model-http` / `C_EVIDENCE="$base (non-2xx HTTP from a non-model service)..."`.
9. **Listener summary has no MODEL_LOADING arm.** `tools/kama-probe.sh:684–690` `case "$C_VERDICT" in` with only MODEL_OK|MODEL_MISMATCH, DEAD, FOREIGN_SERVICE, NOT_HTTP, UNAUTHORIZED_SERVICE counters. A loading endpoint would go uncounted in `listeners` summary unless the repair adds an arm. Also the VOCAB comments at `tools/kama-probe.sh:29`, `:55`, `:110`.
10. **Exit meanings do not transfer.** `SKILL.md:463–466` "Do not transfer exit meanings across tools". The receipt validator's exit 1 (invalid) differs from the probe's exit 1 (probe error); the draft registers this explicitly.
11. **No-slot envelope is a different message.** `tools/server/server-context.cpp:5396` `res->error(format_error_response("no slot available", ERROR_TYPE_UNAVAILABLE));`. Its code value was not inspected; the exact-message rule keeps it `FOREIGN_SERVICE`.
12. **Planned directories absent.** `tests/probe-verdicts/` and `tests/llamacpp-live/` do not exist on 2026-10-20 (`ls`). The draft's gate rows describe planned state and say so.
13. **Build contract exit maps** (`.ufo/waves/round-16/build/make_spec.py`): line 46 harness "Exit 0 all pass, 1 any failure, 2 harness/schema error."; line 69 live capture "Exit 0 all checks pass, 1 any fail, 2 setup error, 3 digest mismatch."; line 76 receipt validator "Exit 0 valid, 1 invalid (list every problem), 2 unreadable."

## Integration notes for L1
- Vocabulary edits: `SKILL.md:11–14` stays as history; the new section supersedes by addition. Probe edits belong to the probe item (`VOCAB` line 55, header line 29, `usage()` line 110, listeners arm 684–690). Not my file.
- Decision-table and error-signature rows are appended at the end of `SKILL.md` (current last line 505), following the round-14/15 registry style.
- The draft asserts the target state, so integrate only after the repaired probe is in place and measured.

## Unknown / not verified by this seat
- The llama-server asset sha256 `753bfa73…e226` and the stories260K model sha256 `270cba1b…d256`: taken from the build contract, not verified here.
- The reason phrase of the 503 status line: not observed.
- Whether the `Server: llama.cpp` header appears on the 503 response at runtime: source-derived (`server-http.cpp:180` `set_default_headers`), not observed.
- `check.py`, `kama-llamacpp-live.py` and `check-receipt.py` do not exist yet: their exit maps are from the build contract, not from running code. The live capture has no self-test specified; none is claimed.
- The `code` value of the `no slot available` envelope: not inspected.
- The `snapshot`/`diff_baseline` acceptance of `MODEL_LOADING` (SnapshotCompat item): not read by this seat.

## Installs
None. No tool was installed or updated.

## Files written
- `.ufo/waves/round-16/build/drafts/skill-section.md` (owned draft)
- `.ufo/waves/round-16/build/advice/ScribeSkillSection.md` (this report)
