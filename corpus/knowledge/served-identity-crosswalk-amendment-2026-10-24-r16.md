source: S473 — https://developers.openai.com/api/reference/resources/models/methods/list/index.md — §List models → Returns → `created`, line 17 (opened 2026-10-25)
verified-at: 2026-10-25
recheck: 90d — re-open the Markdown List models reference at `created`; verify the quoted creation-time definition and the card-field scope below.

# Amendment — `created` is catalog time, not local artifact identity (round 39)

The OpenAI List models schema defines `created` as: “The Unix timestamp (in seconds) when the model was created.” The field records the model's creation time in the public API's catalog; it does not identify bytes served by a local endpoint or establish local readiness.

The existing crosswalk already lists `created` in the OpenAI card's field set (`corpus/knowledge/served-identity-crosswalk.md`, Crosswalk table). This amendment adds the narrower interpretation needed to keep that timestamp separate from artifact identity. It does not claim that `created` is a digest, a local model load time, or evidence that a particular endpoint answered.
