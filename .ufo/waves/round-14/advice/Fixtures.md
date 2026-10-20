# Fixtures — cases.json evidence and limits

## Changed artifact

- New `tests/ollama-evidence/cases.json`, owned and written by this seat.
- Top-level JSON array; 51 unique case names; every object has exactly `name`, `tags`, `ps`, `expect`, `expected_exit`, `expected_finding`; all expectations are hand-written literals, never computed.
- Encoding agreed with Classifier and Harness: object/array = serialized JSON; string = verbatim file bytes (invalid-JSON and duplicate-raw-key controls); `tags`/`ps` null = file not created, while both `--tags`/`--ps` flags are still passed (Harness correction). No path-valued fixture fields; names are `[a-z0-9_]`.

## Literal distribution

| finding | exit | count |
|---|---|---|
| loaded_same_digest | 0 | 10 |
| available_not_loaded | 1 | 3 |
| identity_conflict | 1 | 5 |
| remote_inventory | 1 | 5 |
| unknown | 2 | 10 |
| invalid_input | 2 | 18 |

Exit totals: 0=10, 1=13, 2=28. At least two loaded positives exist with different shapes (plain pair, unrelated inventory, shared-digest alias copy, optional identity fields, unselected remote markers, past `expires_at`).

## Covered controls

- Loaded: equal nonempty digest; extra unrelated entries; empty-string remote markers treated absent; exact `model.gguf` name (no stripping); shared digest under a different alias name; remote markers only on unselected tags/ps entries; past `expires_at` + future `modified_at` ignored; name-only and model-only optional identity field with digest.
- Available: matching local tag with no ps match; valid empty ps `models`; alias copy with same digest but absent selected ps name.
- Remote: selected tags marker; selected ps marker with equal digest; selected tags with unequal ps digest; remote tags with empty ps; both selected remote; all precede digest comparison.
- Identity: ps digest mismatch; selected tags name/model conflict; selected ps name/model conflict with a tags selection present; whitespace-prefixed digest not stripped; `sha256:`-prefix difference not stripped.
- Unknown: no tags match but ps match; empty tags inventory; case-sensitive mismatch; GGUF suffix mismatch; `:tag` qualifier mismatch; **`unknown_ps_alias_without_tags_match`** (ps name/model alias conflict is not reached when tags has no selection); missing selected tags digest; empty selected tags digest; missing selected ps digest; **`remote_missing_digest`** (remote marker + missing digest, missing digest wins).
- Invalid input: missing ps input; missing tags input; remote tags + missing ps input (input failure precedes remote); missing/non-array `models`; non-object entry; non-string digest; duplicate selected tags; duplicate selected ps; duplicate selected ps with one remote; **`tags_none_ps_duplicates`** (duplicate ps precedes no-tags unknown); number/boolean/null remote markers; unparsable raw JSON; duplicate raw JSON key; ps top-level array.

## Cross-seat alignment

- L1 final total order applied: structures/types -> duplicate selected in either list (`invalid_input`) -> no tags selection (`unknown`, even with selected ps conflict/remote) -> selected name/model conflict (`identity_conflict`) -> missing/empty selected digest (`unknown`) -> selected remote marker (`remote_inventory`) -> no ps entry (`available_not_loaded`) -> digest comparison (`identity_conflict`/`loaded_same_digest`). Classifier receives the same final order; earlier ladder proposals are superseded.
- L1 explicitly resolved the two reviewer-flagged controls: `unknown_ps_alias_without_tags_match` is `unknown`/exit 2 (no-tags precedes ps semantic conflict), while `tags_none_ps_duplicates` stays `invalid_input`/exit 2 because duplicate selection precedes no-tags. L1 is appending the duplicate-order exception to the rulings file.
- Both L1-required named controls are present: `remote_missing_digest` (`unknown`, exit 2) and `tags_none_ps_duplicates` (`invalid_input`, exit 2).
- Harness staging convention confirmed; raw-string and null-file cases require no special harness handling beyond the agreed convention.
- ReviewFixtures post-fix static verification against `rulings.json` `final_total_order`: 51 cases, 51 unique names, exit0 10 / exit1 13 / exit2 28; F1 (`unknown_ps_alias_without_tags_match`) conforms to the no-tags step and F2 (`tags_none_ps_duplicates`) to the duplicate step. Remaining G1-G10 items are advisory coverage suggestions, not conformance defects. This was static review only; no seat executed the classifier.

## Limits

- No classifier, selftest, harness, build, lint, or formatter was run by this seat; L1 owns final execution. `readiness` is `unknown` and scope is `offline-captures-not-runtime` throughout; no liveness or readiness is claimed.
- Expectations encode the L1 `rulings.json` contract, not empirical runtime classifications. The frozen pre-fix draft is expected to fail `remote_missing_digest` and `tags_none_ps_duplicates` per L1; this report does not assert observed red-before behavior.
- Duplicate-key rejection depends on duplicate-preserving JSON parsing; the current landed classifier uses `object_pairs_hook`, but this seat did not execute it.
- Structural malformation is exercised only on selected/only entries; unselected malformed entries are deliberately absent because the contract validates recognized types globally and such cases would not add a distinct verdict control.
- `expires_at`/`modified_at` appear only as inert fixture fields; no timestamp, expiry, mtime, or current-time inference is made.
- No tool installs or upgrades; no network, endpoint, secret, environment, or sibling-state access; no git commit.
