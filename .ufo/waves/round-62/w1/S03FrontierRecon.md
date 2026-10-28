# Round 62 frontier recon — endpoint health

Read-only source findings; this is a coverage map, not a verdict on either frozen claim.

## Frontier surfaces still not governed

- **Registered-consumer live health / reconciliation**: the probe's registry and dated history govern pin drift and prior samples, but the three consumers' current state remains `DEAD`; the lane-owned fixture request does not sample them. Evidence: `PROVINCE.md` lines 19–31 and `corpus/knowledge/completion-request-plane.md` lines 41–46. This is distinct from a live fixture proving that an endpoint can answer.
- **Other engines and engine-specific health semantics / runtime integration**: sources and fixture-shaped parsers do not amount to integration with installed vLLM/SGLang runtimes; the existing runtime-health matrix is documentation, not local integration. Evidence: `corpus/README.md` lines 59–64, 97–99; `PROVINCE.md` lines 14, 84–90.
- **Router and sleep-mode readiness**: the existing live lifecycle sample is direct-mode; router/sleep behavior remains source-only/frontier. Evidence: `corpus/README.md` lines 224–231, 248–252.
- **Declared-versus-served context capacity (K05)**: context declarations and fixture capacity are not a real runtime comparison; authorized runtime/consumer comparison remains open. Evidence: `corpus/README.md` lines 63, 71–72 and 224–231.
- **Live grading of the loading transition**: the prior tiny model reaches ready too quickly to establish a live loading observation; the receipt treats no observation as not-evaluated, not success. Evidence: `corpus/README.md` lines 224–230, 262–275.
- **Remote endpoint health** is explicitly outside this lane (kake/kumitate territory). Evidence: `corpus/README.md` line 64.

## Surface moved by C1

The frontier item C1 moved is the **lane-owned llama.cpp `POST /v1/completions` request plane**: previously the lifecycle harness established startup/inventory surfaces but no committed tool graded a real completion response. The new request-plane evidence captures the route's observed response envelope, alias/build identity, usage/timing accounting, deterministic repeat, and malformed-request surface; its stated non-invariants explicitly exclude text quality and registered consumers. Evidence: frozen definition `.ufo/waves/round-62/controls/freeze.txt` lines 11–27; `corpus/knowledge/completion-request-plane.md` lines 5–17, 19–47. This does not close other-engine, consumer-health, or context-capacity gaps.

## Next-ranked frontier proposal

**Prioritize registered-consumer live health/reconciliation**, not another lane-owned fixture endpoint: it is the most operationally consequential gap because current inventory identifies three consumer pins while all recorded live states are dead, and the new C1 explicitly leaves consumer-facing endpoints untouched. Evidence pointer: `PROVINCE.md` lines 19–31; `corpus/knowledge/completion-request-plane.md` lines 41–46. Keep any future sample within the lane's authority and explicit port/authorization boundaries; current evidence does not establish that a registered consumer can safely or presently be contacted.

Confidence: high for the stated gaps and C1 scope (directly documented). Remaining unknown: no fresh consumer probe was performed or authorized by this read-only assignment; current registered endpoint state beyond the cited dated evidence is unmeasured.
