# Proposed append to `corpus/README.md` at 37bd4c5

Append after current EOF; do not insert or rewrite existing lines.

## Coverage map — round 20 additions

| Entry | Covers | Round |
|---|---|---|
| `knowledge/gguf-declared-identity.md` | bounded offline decoding of GGUF header metadata (file-declared architecture, name, context and selected structural fields) plus SHA-256 / retained-receipt reconciliation; not proof of load, authenticated identity or model quality | 20 |
| `knowledge/error-is-not-a-verdict.md` | Kama-instrument outcomes: observed verdict vs error vs could-not-evaluate; exit-1 ambiguity, signal termination, unusable inputs and early-abort selftests; applies verdict-line discipline to a fixed error-injection census | 20 |
| `lessons/round-20.md` | C1 error-injection census and C2 GGUF declared-identity capability, their frozen/current comparisons, prior overlap and residual limits | 20 |

These entries deepen distinct pre-existing coverage rather than erase it. The round-10 GGUF row is about filenames, naming conventions and cross-engine/hardware compatibility, not parsing a file header. Round-16 advice had already read the stories260K header and proposed comparing served metadata to it; the round-20 contribution is the bounded reusable decoder and receipt reconciliation, not first discovery of that fixture's metadata. Error-vs-verdict is likewise not wholly new: KQ20/KQ24, the round-18 receipt rules and the signal/return-code notes already hold parts of the rule. Round 20 adds the cross-instrument error-injection census and explicit exit-1/crash distinction; it does not replace those earlier criteria.

## Frontier disposition — round 20

Frontier advanced: file-declared GGUF metadata can be read offline and reconciled against a digest-bound retained receipt. For the pinned stories260K fixture, the header declares `llama.context_length=2048`; the round-18 v3 receipt with the same model SHA records `/props default_generation_settings.n_ctx=256` and launch `-c 256`. This is a fixture/receipt comparison, not a new live sample, current endpoint state, proof that the file's declarations are authentic, or a model-quality claim.

The original K05 consumer/config-to-serving question remains open: round 1 names `limit.context=32768` versus `--ctx-size 16384`, while the round-18 comparison is model-declared training context versus a separate fixture's served slot context. It does not establish the consumer's effective setting or current registered-consumer health. Round-18's fixture remains pending L0 ratification in `PROVINCE.md`; no registered consumer is sampled by this comparison.

Still open: an authorized current consumer-context comparison; router/sleep and other-engine behavior; and independent authentication of header claims (a file digest binds bytes, not the truth of their metadata). The error census calibrates kama's own instruments; reusable verdict-line / mutation-testing method remains tameshi's province, and quality remains kengaku's.
