# EX05PinRecheck — C3 freshness

Axes: freshness (new upstream reads), byte consistency (located, hashed extracts), operability (all five relations graded).

## Result and integration

Deliver `registry/pin-recheck-rows.tsv` to the same lane-relative path and `anchors/llamacpp-b7200-health.txt` to `corpus/anchors/llamacpp-b7200-health.txt`. No other production file changes are proposed. All five verdicts are `holds`. The b7200 health statement at upstream line 406 occurs verbatim at b12111 line 482 (13 words).

The b7200 era-correct first candidate, `tools/server/README.md`, returned HTTP 200; the fallback `examples/server/README.md` was therefore unnecessary and not requested. All four curl reads exited 0 with HTTP 200. Their full received bodies and individual JSON receipts retain URL, status, SHA-256, byte count, and stderr.

The three newest documents' relevant committed extract ranges are byte-identical to the fresh corresponding ranges, including both llama.cpp health and router ranges. `comparisons.json` gives complete digests for each comparison. A whole-document SHA cannot equal an excerpt SHA; this report distinguishes full-document hashes from anchor-body hashes. No baseline full SGLang document was supplied, so byte-identity is established for its committed excerpt, not claimed for unretained surrounding baseline bytes. All full fresh documents are retained for downstream source registration.

The explicit upstream tag-list reads and scratch pin-watch agree: newest tags remain b12111, v0.5.23, v0.33.0. `pin-watch.out` exits 1 because the existing pins lag; this is expected, not a failed freshness fetch. No newest-tag STOP condition occurred.

## Exercised checks

`pin-rechecks.out` (exit 0):
```
PIN_RECHECK rows=5 graded=5 holds=5 reworded=0 moved=0 drifted=0 ungraded=0 bad=0
```
`selftest.out` (exit 0): `PIN_RECHECK_SELFTEST pass=14 fail=0`.

Only the specifically assigned scratch grader and selftest were run; no build, lint, formatter, or general integration gate ran. The grader was run after committing precisely the delivered TSV and new anchor in the exclusive shared scratch clone. Its repository root was asserted before staging/commit. The lane master observed at start was eb03a64bcd8e2faab0f4f9bcdc55bfc5c1ed2c85. Scratch commit output is retained; scratch is removed before handoff. Selftest TMPDIR was under the exclusive scratch root.

## Source handoff

For the round lesson Gate and SOURCES owner: use all four URLs/hashes in `*.receipt.json`; use the exact new health quote at b7200 line 406 and newest line 482, SGLang health line 109 (new routes at 111–112), and vLLM prefix-caching line 3. The grader does not alone establish the frozen predicate's separate lesson/Gate naming requirement; L1 must integrate these sources with its lesson/source owner. This seat does not own those files.

## Scope, risks, and tooling

All retained files are within this seat's exclusive out directory. The requested outer `.ufo/waves/round-84/w1/EX05PinRecheck.md` report conflicts with the explicit write-ONLY-out-directory rule; `EX05PinRecheck.md` here is the integration-ready report for L1 to place there. No lane/fleet git mutation, credential reads, PATH changes, installations, or background jobs were performed. LSP is unavailable in this seat's mounted tool inventory; no supported symbol refactor was needed (data-only move). No implementation blocker remains; production integration and the lesson Gate/source registration belong to L1.

## Retained evidence

- `registry/pin-recheck-rows.tsv`: byte-exact proposed register.
- `anchors/llamacpp-b7200-health.txt`: new header/body-digest-bound anchor.
- `b7200-tools.md`, `b12111.md`, `v0.5.23.mdx`, `v0.33.0.md` and their `.receipt.json` files: received full upstream bytes and HTTP receipts.
- `comparisons.json`: matching committed-body/fresh-range SHA-256 pairs.
- `llamacpp-tags.out`, `sglang-tags.out`, `vllm-tags.out` (+ `.err`), `newest-tags.json`: retained live tag inventories and interpreted maxima.
- `pin-watch.out/.err`, `pin-rechecks.out/.err`, `selftest.out/.err`, `scratch-commit.out`: exact subprocess receipts.
- `commands.json` and README command ledger: every directly invoked process and true exit status.

## Self-evaluation

Accuracy 4/5: received bytes and counters retained; excerpt/full-document distinction explicitly limited rather than overstated. Completeness 4/5: required outputs complete, outer report placement deferred solely to obey write scope. Clarity 4/5: file mapping explicit, though receipts are split across files. Actionability 4/5: two production files ready; lesson/source owner still must integrate its assigned surfaces. Conciseness 4/5: retained full documents intentionally exceed the extracts needed for grading. Overall 4.0/5. Improvement priorities: integrate the two mapped files and source Gate together; preserve the excerpt/full-document distinction. Would the user agree? Likely, given exact green receipts and clearly scoped integration caveats.
