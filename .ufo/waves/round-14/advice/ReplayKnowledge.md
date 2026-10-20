# ReplayKnowledge — round 14

## Status

Knowledge entry landed. No verification run by this seat; no tests, builds,
formatters or live endpoint reads.

## Files changed

- `corpus/knowledge/ollama-evidence-replay.md` (new, ~15 KB). No other file
  written.

## Behavior documented

- Provenance trio first: `source:` S012 `/api/ps` + S031 `/api/tags` plus
  companion artifacts; `verified-at: 2026-10-20`; 90d/on-change `recheck:`.
- Literal CLI: `python3 tools/kama-ollama-evidence.py --tags PATH --ps PATH
  --expect EXACT_NAME`, `--selftest`; stdout `kama-ollama-evidence/v1` with
  `schema`, `finding_id`, `verdict_exit`, `expected_model`, `readiness="unknown"`,
  `scope="offline-captures-not-runtime"`, `reasons`; selftest schema
  `kama-ollama-evidence-selftest/v1`.
- Verdict glosses relative to the supplied captures only:
  `loaded_same_digest` = expected name listed in the supplied ps capture with a
  digest equal to the supplied tags capture; `available_not_loaded` = expected
  name absent from the supplied ps capture. Capture times, simultaneity and
  same-host/same-daemon origin are unknown; same input path is unverified caller
  evidence; `expires_at`/mtime/clock are not evaluated.
- Final total order recorded in both prose and the error table:
  structure/types -> duplicate selected (exit 2) -> no tags unknown (even with
  ps alias conflict or remote) -> selected name/model conflict (1) -> missing
  selected digest unknown (2) -> remote (1) -> no ps available (1) -> unequal
  digest (1) / equal digest (0).
- Side-by-side exit mapping old probe vs replay; explicit warning never to chain
  the two with `&&`/`||` as a routing gate and never to read replay exit 0 as
  `MODEL_OK`.
- Prior-coverage credit to `runtime-health-surface-matrix.md:17` and
  `served-identity-crosswalk.md` (claim, Ollama row, failure cases 3/5/6, alias
  limits, lines 35-36 absence rule). New claim limited to operational repertoire,
  not a new conceptual distinction.
- Boundaries: no acquisition/network feature; classification reads only the two
  paths; no config/env/token/log/process reads (selftest tempdir follows
  `tempfile`/TMPDIR, not evidence); raw input preserved; stdout only.
- Every matching/precedence rule labeled **[INFERENCE]** lane policy. ps-side
  remote markers explicitly labeled conservative inference, not ps OpenAPI
  schema; S012 is not cited for remote fields.

## Retained evidence (read-only; nothing executed)

- `https://docs.ollama.com/api/tags` and `https://docs.ollama.com/api/ps`
  opened 2026-10-20, OpenAPI 3.1.0 info.version 0.1.0:
  - tags: 200 "List available models"; `ModelSummary` "Summary information for a
    locally available model"; `name`/`model` "Model name"; `digest` "SHA256
    digest identifier of the model contents"; `remote_model`/`remote_host`
    descriptions.
  - ps: 200 "Models currently loaded into memory"; `name`/`model` "Name of the
    running model"; `digest` "SHA256 digest of the model"; `expires_at` "Time
    when the model will be unloaded"; no remote fields in the schema.
- `.ufo/waves/round-14/rulings.json` read in full; final parent order applied.
- `tools/kama-ollama-evidence.py` source read: `SCHEMA`, `FINDING_EXIT`,
  `validate_capture`, `classify`, `classify_payload`; output keys confirmed.
- `tests/ollama-evidence/cases.json` read: 51 literal cases; expectations observed
  include `remote_missing_digest = unknown`, `tags_none_ps_duplicates =
  invalid_input`, `invalid_duplicate_selected_ps_with_remote_marker =
  invalid_input`.
- `served-identity-crosswalk.md:35-36` read: absence at one ps sample must not be
  concluded either way; expiry is a time-bounded observation.

## Alignment and blockers

- Latest read of `tools/kama-ollama-evidence.py` (2026-10-20 03:35) has
  `classify()` in the final total order: duplicate selected -> no tags unknown ->
  tags/ps name/model conflict -> missing selected digest -> tags/ps remote ->
  no-ps available -> unequal/equal digest. This matches the entry and
  rulings.json. An earlier 03:31 read had the older order; that snapshot was
  superseded by the owner's update and is not a current blocker.
- `tests/ollama-evidence/cases.json` at 03:35 has 51 unique case names; the
  former `identity_conflict_ps_alias_without_tags_match` case is now
  `unknown_ps_alias_without_tags_match` with expected `unknown`/2, matching the
  final order. `remote_missing_digest = unknown`, `tags_none_ps_duplicates =
  invalid_input` and `invalid_duplicate_selected_ps_with_remote_marker =
  invalid_input` also match.
- No external independence is claimed for the fixture author: prose says
  "committed fixture set" only.
- No current blocker observed in the final source/fixture/entry alignment. Final
  build, selftest and measurement runs remain L1-owned.
- No tool installation or update occurred.

## Limits

No classifier invocation, selftest, measurement wrapper, fixture run, live
Ollama contact, network request, environment/config/credential read, or file
write beyond this report and the knowledge entry. The entry is documentation and
does not establish installed Ollama, current residency, readiness or local
weights.
