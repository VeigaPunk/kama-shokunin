# Round 14 planner walk — offline Ollama evidence

## Axes and selection

- **Calibration: 7**; **operability: 8**. The latest scorecard round-13 text says calibration is the lowest assigned axis and leaves its numeric score at 7 (`SCORECARD.md:340-359`). No score increase is justified by this bounded capability.
- The scorecard’s latest plan (`SCORECARD.md:363-366`) is outside sampling of round-13 admit/reject decisions and later externally steered serving-domain work; earlier planned freshness text is explicitly superseded. The round-14 task contract instead selects the single calibration C1 offline tags/ps replay classifier. Treat that as the current steering, not as a plan already recorded in SCORECARD or as a reason to replace L1’s plan.

## Data walk: positive control, then counterexample

1. **Exact loaded-positive control (contract-derived; not yet observed in a committed case fixture):** use one exact, case-sensitive expected identity matching the selected `name` or `model` in exactly one tags entry and exactly one ps entry; both carry the same nonempty digest; neither selected record has a nonempty `remote_model` or `remote_host`. This is `loaded_same_digest`, exit 0, while `readiness` remains `unknown`. It demonstrates only the classifier’s correspondence rule over these two supplied records.
2. **Counterexample to “equal digest means local loaded model”:** keep the same matching identity and equal nonempty digests, but give the selected tags entry a nonempty `remote_model` or `remote_host` (and exercise the selected-ps marker separately if available). The contract requires `remote_inventory`, exit 1, despite the digest match. A valid tags record plus an explicitly empty ps `models` array is another distinct control: `available_not_loaded`, exit 1, meaning only that the model is absent from this supplied ps capture.

This sequence is bounded by the sources: Ollama `/api/tags` describes available inventory and may expose remote-origin fields; `/api/ps` describes running models and includes `expires_at` (`corpus/knowledge/served-identity-crosswalk.md:29,35-38`; `corpus/SOURCES.md` S011, S012, S031). The same crosswalk explicitly labels tags-to-ps digest joining an **inference**, not a documented identity mapping (`:45`). Therefore `loaded_same_digest` must not be generalized into proof of artifact identity, local weights, present runtime state, or readiness; `available_not_loaded` must not be read as a claim about a live service. The crosswalk says absence from one ps sample is not conclusive about on-demand load behavior (`:35`), and warns that ps residency is time-bounded (`:36,51-53,64-65`). Exact name matching must not import kama’s GGUF basename normalization (`:43-45`).

## Divergences and limits

- Prior prose already separates available, loaded, and remote observations and warns that a digest join is inferential (`SKILL.md:359-367`; `served-identity-crosswalk.md:13,29,35-45`). The gap identified by the round-14 contract is executable offline replay classification and fixed adversarial cases, not new documentation of those concepts.
- On my read, the assigned `tools/kama-ollama-evidence.py` and `tests/ollama-evidence/cases.json` were absent. Per round contract these are in-flight/pending, not final defects; thus no actual fixture/result can yet be credited. I sent the classifier owner the bounded positive/remote-counterexample recommendation. The `lsp` device is not mounted in this session; no source server answered, so no references/definition/implementation result or code-semantic claim is made. Literal search was discovery only.
- No runtime, network, endpoint, test, build, formatter, or smoke run was used; no tool was installed.

**Confidence:** high for the axis values, scorecard-plan discrepancy, and documentary inference/readiness boundaries; provisional for the round-14 implementation because its code and case registry were not present at inspection.
