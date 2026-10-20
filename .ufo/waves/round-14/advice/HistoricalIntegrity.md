# HistoricalIntegrity — round 14

## Historical design and evidence

- The original crosswalk treats the Ollama `/api/tags` ↔ `/api/ps` digest join as an **`[INFERENCE]` candidate, not a documented mapping** (`corpus/knowledge/served-identity-crosswalk.md:45`). The source rows document a `digest` field separately on each route: S011 describes a SHA256 digest identifier for model contents; S012 describes a SHA256 digest of the model (`corpus/SOURCES.md:23–24`). Neither row specifies cross-route join semantics.
- The design favors digest comparison over names because the crosswalk records that both `name` and `model` are merely “Model name,” and `ollama cp` / `ollama create` can make additional names; it says whether a copy keeps the digest is undocumented (`served-identity-crosswalk.md:37,45`). Thus a name/alias match helps select entries but is not itself content identity. Equality of the returned digest strings is still the crosswalk's analytical join, not vendor-certified artifact equivalence.
- This was explicit in the author record as well: the round-11 Crosswalk report says the digest join was labeled `[INFERENCE]` “with no artifact proof” (`.ufo/waves/round-11/advice/Crosswalk.md:44`). KQ13 requires a digest join beyond the documentation to be labeled inference (`corpus/QUALITY.md:40`).
- The round-12 append did not revise this digest claim. Its stated scope is the remote-locality inference and registry-only `supersedes S011` wording; it preserves the old body and says no other failure-case sentence is reclassified (`served-identity-crosswalk.md:87–94,124–134`). The historical digest status therefore remains as written.

## Round-14 boundary

The round-14 contract turns that candidate into a deterministic **offline-capture classification policy**: only a unique selected tags entry and ps entry with exact case-sensitive expected-name/model-alias match, equal nonempty string digests, and no nonempty `remote_model`/`remote_host` markers may produce `loaded_same_digest`. This is an implementation rule over caller-provided files, not a claim that Ollama documentation defines a cross-route join. Preserve `readiness="unknown"` and `scope="offline-captures-not-runtime"`; the verdict is metadata correspondence, not inference readiness, host liveness, or a global proof of local weights. Do not normalize GGUF paths or infer timestamp/expiry/current liveness.

The old crosswalk says a tags entry absent from one `/api/ps` sample does not establish on-demand loading behavior either way (`served-identity-crosswalk.md:35`). The new contract's `available_not_loaded` is therefore the classifier's requested label for the supplied capture under its explicit policy—not a new vendor-documented behavior claim or readiness claim. A remote marker takes precedence as `remote_inventory`; missing/malformed or ambiguous identity/digest evidence fails closed as unknown/invalid or conflict per the contract. The crosswalk's separate remote-locality conclusion is itself explicitly `[INFERENCE]` in its round-12 append (`served-identity-crosswalk.md:96–108,124–134`).

## Status and limits

At inspection time, `tools/kama-ollama-evidence.py` and `tests/ollama-evidence/cases.json` were absent; the round-14 spec says missing in-flight files are pending, not defects. No runtime, endpoint, network, test, build, or verification was used. Findings are limited to the recorded crosswalk, source registry, quality rule, round-11 author report, and round-14 contract. No tools installed or updated.

I sent the classifier owner a bounded note distinguishing the historical inference from the round-14 capture policy and clarifying that an absent ps entry does not establish on-demand behavior.