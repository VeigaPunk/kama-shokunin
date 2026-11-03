# Reviewed lessons: request recovery and capacity judgment, rounds 72–73

These are original synthesis notes, not copied third-party captures, full source history, a runtime test, or an admission of either round. Both exercises were independently closed partial/not admitted. Previous finite results and the preservation-conformance caveat remain unchanged.

## Request disposition (72)
Separate evidence about a specific request's acceptance and effect from process-level health or a general status code. A timeout or transient service response may leave the outcome unknown. Before retrying, establish the operation's identity, applicable idempotency contract, observed effects and authority to act; recommend reconciliation or a hold where those facts are missing. Ten first manual decisions met their decisive criteria, but two required consecutive source-change checks failed. A later clean comparison cannot retroactively replace those failures.

## Capacity arithmetic (73)
Use the exact pinned implementation and resolved inputs when estimating capacity across full, local and sliding-window cache groups. Preserve page rounding and alignment at the relevant stage, distinguish shared pool constraints and host/device accounting, and avoid substituting one specification class for another. A fractional concurrency estimate is not automatically a whole-request measurement. Computer floating-point multiplication followed by integer conversion can differ at a boundary from ideal rational arithmetic. These are source-grounded manual judgments, not measured serving capacity or live-performance claims.

All ten first manual decisions were source-faithful with a documented oracle arithmetic error, but the original mandatory append-only audit remained red on inherited preservation debt. No-new-harm is not a waiver and the round was not admitted. See the existing preservation caveat for the exact historical audit qualification. Primary source: [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html) and the [pinned vLLM source](https://github.com/vllm-project/vllm/tree/5df63a7203cdb9328d824a27b682e77c7b9928be/vllm/v1).
