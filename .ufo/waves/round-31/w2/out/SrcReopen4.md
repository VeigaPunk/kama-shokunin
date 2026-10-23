# SrcReopen4 — C1 depth claim, re-open S186/S187 (falsifier)

Full report: `.ufo/waves/round-31/w2/out/SrcReopen4/report.md`; receipts:
`.../SrcReopen4/receipts.log`.

## FINDING:
Rows S186 and S187 both hold; no disagreement found.
- S186: quote-verbatim yes; words 9; line match yes; used-by `corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json` exists yes.
- S187: quote-verbatim yes; words 5; line match yes; used-by `corpus/knowledge/chat-adapter-outcomes.md, registry/chat-param-outcomes-r31.json` exists yes.

Evidence summary: URL fragment `#L1517`/`#L1519` on `tools/server/server-common.cpp` at commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` resolves to the local pinned snapshot `llama.cpp-704366d/server-common.cpp` (SNAPSHOT.json pin `b4f4aae7…` matches local sha256 and the upstream GitHub raw blob sha256, curl exit 0). `sed -n '1517p'` prints `throw std::invalid_argument("logprobs is not supported with tools + stream");`; `sed -n '1519p'` prints `llama_params["n_probs"] = json_value(body, "top_logprobs", 20);`. Byte-hash of each row quote equals the byte-hash of its anchor line (leading whitespace trimmed), so each quote occurs verbatim on its line. Word counts 9 and 5 (≤ 25). Both used-by names exist in the lane repo.

## LIMITS:
- Covers only S186/S187, not the other new rows (S180-S185, S188-S191), not C1 counter behavior; not a verdict.
- Line match judged against the local snapshot; upstream byte-identity cross-check succeeded (curl exit 0), so a discrepancy with the GitHub blob at 704366d is unobserved.
- used-by existence only; does not check downstream consumption of the rows.
- One earlier `read`-tool line-label display was shifted +2 versus sed/awk/grep; all conclusions use sed/awk/grep numbering.
