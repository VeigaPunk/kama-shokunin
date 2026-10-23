# VerifyTimingTranscripts — round 29 attempt 2, wave 2 (seat kama-r29-w2-VerifyTimingTranscripts-3)

Item: verify the attempt-1 routed-repair-3 artifact `.ufo/waves/round-29/w1/out/ExecTimingTranscript/`
(recompute sha256 of both excerpts, compare with provenance.json recorded hashes, open excerpts and
confirm embedded tool_call timestamps match the lesson claims).

All checks were read-only on the fleet/lane (no git/jj mutation, no edits to lane files). No tools
installed. Report written to seat out dir per bounds.

## 1. Recomputed sha256 vs provenance.json

| file | recomputed sha256 | provenance.json `excerpt_sha256` | README table | match |
|---|---|---|---|---|
| `excerpt-DataG01-2.jsonl` | `66d5e1fc6f0306a2099bdae466c3f3873023951d1c50f8a2c2b22f8ee7750b3b` | `66d5e1fc6f0306a2099bdae466c3f3873023951d1c50f8a2c2b22f8ee7750b3b` | same | **MATCH** |
| `excerpt-DataG15-2.jsonl` | `107687f951dd41ad19fa6852d04c177686c016d845cf6a2d60ca1a1f1845d65e` | `107687f951dd41ad19fa6852d04c177686c016d845cf6a2d60ca1a1f1845d65e` | same | **MATCH** |

Also verified (beyond the requested pair):

- Bytes: `wc -c` = 6670 (G01) / 11006 (G15) — match provenance `excerpt_bytes`.
- `provenance.json` self-hash recomputed `88efc778436d924ddf740ce88ccdf315f00f89ff767dc9846948f0d0be8fa818` — matches README table.
- Source files exist at the provenance `source_path` and their sha256 match:
  - `…/KamaR28/KamaR28.DataG01-2.jsonl` = `34251f82f564d9192009865de61fa14d99cbba48d769b6ace979bdc43d82615e`, 315041 bytes, 102 lines.
  - `…/KamaR28/KamaR28.DataG15-2.jsonl` = `82052c46d6789d613a443383465100a794fed7e6d7d8feada2e94a93904d3f8c`, 340785 bytes, 100 lines.
  - `…/KamaR28/KamaR28.DataG11-2.jsonl` = `adf08e0d9c608f9181d2436a44206ac16b9dcfa77115558f651f5520ea8fbe3a`, 332826 bytes, 96 lines.
- Excerpt content is byte-for-byte identical to the cited source line ranges: `sed -n '98,100p' …DataG01` | `cmp` excerpt G01 → BYTE-IDENTICAL; `87,89p` G15 → BYTE-IDENTICAL; `83,85p` G11 → BYTE-IDENTICAL.
- Per-line sha256 in provenance (9 records) all match recomputed sha256 of the corresponding excerpt lines excluding the trailing newline.

## 2. Embedded timestamp verification (the lesson's claims)

Lesson `corpus/lessons/round-29.md` repair-3 row:

> `w1/out/ExecTimingTranscript/provenance.json`, `excerpt-DataG01-2.jsonl` (tool call 08:35:53.929Z, result 08:35:54.037Z), `excerpt-DataG15-2.jsonl` (08:36:53.343Z / .398Z)

Verified against actual excerpt JSON:

| claim | excerpt line | `timestamp` field | verdict |
|---|---|---|---|
| DataG01 tool call 08:35:53.929Z | G01 line 1 (assistant message, toolCall `call_a49eb97deb664aa3acc7264c`, intent "Cross-checking rows with counter primitives") | `2026-10-23T08:35:53.929Z` | **MATCH** |
| DataG01 result 08:35:54.037Z | G01 line 3 (message role toolResult, isError false) | `2026-10-23T08:35:54.037Z` | **MATCH** |
| DataG15 tool call 08:36:53.343Z | G15 line 1 (assistant message, toolCall `call_00_cs8hczum5hr1d5rlc00ylyu2`, intent "Rebuilding and fully validating rows") | `2026-10-23T08:36:53.343Z` | **MATCH** |
| DataG15 result 08:36:53.398Z | G15 line 3 (message role toolResult, isError false, stdout contains "ALL FOUR ROW CHECKS PASS") | `2026-10-23T08:36:53.398Z` | **MATCH** |

(Line 2 of each excerpt is `tool_execution_start`: G01 08:35:53.930Z, G15 08:36:53.344Z — consistent with the assistant-message timestamps above.)

## 3. Other checks and one finding

- All four timestamps appear in the round-28 critic evidence `.ufo/waves/round-28/w2/out/CriticA1Legitimacy/evidence.md` (lines 27 & 51; DataG15 at line 63) and the excerpt `timestamp` fields match them.
- The DataG01 tool result stdout contains `all rows pass counter primitives: True`, `sse_ping_interval True …`, etc. — the counter-primitive evaluation did run on live row drafts before the A1 edit (08:35:54Z < A1 commit 75b78bb4 at 08:38:16Z).
- **Finding (low severity, wording imprecision).** `provenance.json` (and the w1 `README.md`/`advice/ExecTimingTranscript.md`) record the verified claim as `stdout ending 'all rows pass counter primitives: True'`. The raw stdout in excerpt G01 line 3 does *not* end there — it continues with `48201 closed` and `no server process`; `all rows pass counter primitives: True` is the penultimate content line. This does not weaken the substance (the line is present verbatim and the transcript record is intact), but the wording should be "stdout contains … (… : True before final lines)" rather than "ending". The underlying round-28 critic evidence quoted the same stdout as a *selective* block (lines 53-58), so the original quote was accurate; the "ending" phrasing was introduced by the attempt-1 writer.
  - Also: the toolResult inner `message.timestamp` of G01 (epoch ms 1792744554036 → 08:35:54.036Z) is 1 ms before the outer JSON `timestamp` 08:35:54.037Z (truncation of sub-millisecond time; outer field is the one quoted everywhere). Not a defect.

## 4. Conclusion

The item's verification is **PASS**: recomputed sha256 match provenance.json for both excerpts; the excerpts are byte-identical to their cited source transcript lines; the four embedded timestamps exactly equal the lesson's claims. No blocking defect. One low-severity wording nit (provenance "stdout ending" vs actual final lines) for the L1 to optionally correct in a later amendment; the frozen round-28 bytes need no change.
