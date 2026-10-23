VERDICT: holds — All three round-27 Gate rows (S136, S137, S138) re-verified byte-for-byte on 2026-10-23: my fresh sha256s match the claimed raw-fetch hashes, each quote is verbatim at the stated location, every location claim is correct (including S138's 1835 closing-brace correction over S133), and all quotes are ≤25 words.

# Method

Re-opened each URL myself with `curl -fsSL --max-time 80` under `ulimit -f 1048576`, fetched to `/fast/scratch/hyaku/kama-r27c/ReviewLessonGate/`, hashed with `sha256sum`, and pinned exact line numbers with `sed -n -e 'N,M=' -e 'N,Mp'` (numbered output, not counted by eye). All commands exited 0. No tool installs were needed (none performed). Blob-page URLs from the lesson additionally confirmed live (HTTP 200 via `curl -s -o /dev/null -w '%{http_code}'`).

# Per-row verdicts

## S136 — RFC 8259 — HOLDS

- Lesson row: corpus/lessons/round-27.md:82; SOURCES row: corpus/SOURCES.md:148.
- Command: `timeout 90 curl -fsSL --max-time 80 -o rfc8259.txt https://www.rfc-editor.org/rfc/rfc8259.txt && sha256sum rfc8259.txt && wc -l rfc8259.txt` → exit 0, 899 lines.
- My sha256: `61a5378f4255c720beb2a4b4a63b29540147c140f36988bf086291989b4cd2d7` — matches lesson `61a5378f…2d7` and SOURCES full hash exactly.
- Quote `"Any character may be escaped."` is verbatim at rfc8259.txt:433 (numbered fetch: `433` → `   Any character may be escaped.  If the character is in the Basic`). The RFC's double space after the period is inside line 433; the quoted sentence itself is byte-exact.
- Location claim "§7 Strings": heading `7.  Strings` at rfc8259.txt:424, next heading `8.  String and Character Issues` at line 481, so lines 433-440 (SOURCES anchor) lie entirely inside §7. ✓
- Word count: 5 ≤ 25. ✓
- Access date 2026-10-23T06:48Z: content re-fetched later the same UTC day reproduces the claimed hash; time-of-day itself is not independently verifiable ([INFERENCE] same-day access consistent).

## S137 — server-common.cpp @ 704366d76 — HOLDS

- Lesson row: corpus/lessons/round-27.md:83; SOURCES row: corpus/SOURCES.md:149.
- Command: `timeout 90 curl -fsSL --max-time 80 -o server-common.cpp https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp && sha256sum server-common.cpp` → exit 0, 2147 lines.
- My sha256: `b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442` — matches lesson `b4f4aae7…d442` and SOURCES exactly.
- Quote verbatim at server-common.cpp:1375 (numbered fetch: `1375` → `throw std::invalid_argument("response_format type must be one of \"text\" or \"json_object\", but got: " + response_type);`, modulo leading indent). Context 1363-1377 matches the SOURCES anchor range (`// Handle "response_format" field` at 1363, block closes 1376-1377). ✓
- Blob URL with `#L1375` resolves HTTP 200 at the pinned commit. ✓
- Word count: 15 ≤ 25. ✓
- Access date 2026-10-23T06:48Z: same-day re-fetch byte-identical ([INFERENCE] as above).

## S138 — server-context.cpp @ 704366d76 — HOLDS

- Lesson row: corpus/lessons/round-27.md:84; SOURCES row: corpus/SOURCES.md:150 (supersedes S133, corpus/SOURCES.md:147).
- Command: `timeout 90 curl -fsSL --max-time 80 -o server-context.cpp https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp && sha256sum server-context.cpp` → exit 0, 6320 lines.
- My sha256: `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329` — matches lesson `dd1de0f2…2329`, SOURCES S138, and the old S133 row (same file, same commit — supersession is an anchor correction only, as claimed).
- Numbered fetch confirms the correction: `1810` → `    bool try_clear_idle_slots() {`; `1834` → `        return res;`; `1835` → `    }` — the closing brace IS line 1835, so S138's `1810-1835` is correct and S133's `1810-1834` was indeed off by one (round-26 spot-check defect 7 fix verified against the bytes). Next function `construct_lora_list` opens at 1837. ✓
- Word count of quoted open: 3 (the closing-brace note is a location, not quote text). ≤ 25. ✓
- Blob URL resolves HTTP 200 at the pinned commit. ✓
- Access date 2026-10-23T06:53Z: same-day re-fetch byte-identical ([INFERENCE] as above).

# Cross-checks

- Lesson line 86 "No existing row's `status`, `recheck` or `used-by` changed": out of my fetch scope; not verified (flagged for the registry reviewer, not a quote defect).
- The two lesson URLs are GitHub blob (HTML) URLs while the sha256 labels say "raw fetch"; I verified the raw content at the identical pinned commit and confirmed both blob pages resolve 200 — same commit, same content source ([INFERENCE] blob HTML wraps the raw bytes; only the raw file was hashed).

# Residual risk

- Access timestamps' time-of-day (06:48Z/06:53Z) cannot be reproduced; only same-day content stability is proven.
- GitHub raw content at a pinned commit is immutable, so hash match was expected; the real risk was quote/line transcription, which is exactly what I verified against the numbered bytes.

# Verification gaps

- None within scope. All three rows: hash, verbatim quote, stated location, word limit, and (for S138) the superseding correction all reproduce from my own fetches.
