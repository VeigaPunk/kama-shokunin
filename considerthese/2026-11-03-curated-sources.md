# kama: curated sources to consider after hyaku

Date: 2026-11-03

**Status: unassimilated future reading.** These are candidate references, not trained knowledge, verified local capabilities, adopted dependencies, or changes to current training. Reserved for possible post-hyaku assimilation under the lane’s normal admission review. Earlier dated reflections remain unchanged.

Selection checked against the supplied PROVINCE, source registry and considerthese context, including exact URLs and source-entity mentions. No candidate code was executed.

## 1. Open Inference Protocol: HTTP/REST health and metadata

- Type: Specification.
- Primary source: <https://raw.githubusercontent.com/kserve/open-inference-protocol/main/specification/protocol/inference_rest.md>
- Why this is worth considering: A serving contract that distinguishes server liveness, server readiness, model readiness, and model metadata. This supplies useful comparison vocabulary for kama’s existing separation of a correct consumer pin from an actually available model.
- Possible later exercise: After hyaku, draft a read-only contract matrix comparing these questions with the documented llama.cpp, Ollama and vLLM endpoints. Mark unsupported operations rather than treating all health URLs as equivalent.
- Boundaries and caveats: OIP is not the OpenAI-compatible API and does not imply local runtimes implement its routes. The fetched prose contains apparent readiness/body inconsistencies; cross-check its linked OpenAPI schema and a pinned implementation before deriving assertions. No deployment or config changes.
- License/reuse: Apache-2.0 per official repository. Evidence: <https://github.com/kserve/open-inference-protocol>.
- Currency/maintenance: Moving main specification; version and implementation compatibility must be pinned before use.
- Duplicate check: no exact primary URL or source-entity match in the supplied lane context.
- Supporting evidence: <https://github.com/kserve/open-inference-protocol>.

## 2. Prometheus blackbox exporter

- Type: Repository.
- Primary source: <https://github.com/prometheus/blackbox_exporter>
- Why this is worth considering: A mature external-probe implementation with explicit timeouts, protocol selection, status checks and body predicates. Its address-selection documentation is especially useful when a reachable address masks failure on another address family.
- Possible later exercise: After hyaku, compare existing kama probe verdicts against a paper fixture matrix: refused socket, timeout, redirect, wrong model identity, IPv4-only success and IPv6-only success. Keep model identity as a separate assertion from transport reachability.
- Boundaries and caveats: A successful probe does not establish model quality or authenticate a model artifact. Installation, credential configuration and endpoint repointing remain out of scope. Pin release-specific configuration before relying on newer JSON predicates.
- License/reuse: Apache-2.0. Evidence: <https://raw.githubusercontent.com/prometheus/blackbox_exporter/master/LICENSE>.
- Currency/maintenance: Official release page lists 0.29.1 dated 2026-10-21, verified 2026-11-03.
- Duplicate check: no exact primary URL or source-entity match in the supplied lane context.
- Supporting evidence: <https://raw.githubusercontent.com/prometheus/blackbox_exporter/master/CONFIGURATION.md>, <https://github.com/prometheus/blackbox_exporter/releases>.
