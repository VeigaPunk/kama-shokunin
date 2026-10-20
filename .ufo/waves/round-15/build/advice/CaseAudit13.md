# CaseAudit13 — cases indexes 26 and 27 vs the duplicate-corpus guard

Seat: scout, read-only. Reviewed 2026-10-20. No code executed; findings are static reads.
Files read: `tests/ollama-evidence/cases.json` (indexes 26–27 only, plus corpus-level name
counts), `tools/kama-ollama-evidence.py` (`FINDING_EXIT`, `validate_capture`, `_matching`,
`_remote_marker`, `classify`, `run_selftest`, `_run`), `.ufo/waves/round-14/measure.py`
(`corpus_problems`, `run`, `measure_case`, `write_capture`),
`.ufo/waves/round-15/frozen/measure-before.py` (`corpus_problems` only), and
`.ufo/waves/round-15/build/spec.json` (context + item contract).

Axes: (1) literal expectation fidelity, (2) guard non-interference, (3) precedence-order
discrimination.

## Case 26 — `remote_inventory_ps_same_digest`

Literal fixture (cases.json index 26):

- `tags.models = [{name:"llama3:8b", model:"llama3:8b", digest:"sha256:1111…1111"}]`
- `ps.models   = [{name:"llama3:8b", model:"llama3:8b", digest:"sha256:1111…1111",
  remote_host:"https://remote.invalid"}]`
- `expect = "llama3:8b"`, `expected_exit = 1`, `expected_finding = "remote_inventory"`.

Exact classifier path (`tools/kama-ollama-evidence.py`, `classify`, lines 218–264):

1. `validate_capture` accepts both envelopes: both are objects with `models` arrays; every
   present `name`/`model`/`digest`/`remote_model`/`remote_host` is a `str` (lines 172–187).
   `remote_host` is a declared `MARKER_FIELDS` member (line 100), so its string value is
   legal and is not an `invalid_input` type failure.
2. `_matching` returns exactly one tags match and exactly one ps match (`name == expect`,
   also `model == expect`; list membership is per entry, not per field, so this is one
   element each). `len(...) > 1` duplicate-selection branches do not fire (lines 226–229).
3. Tags match exists; `_identity_conflict(tag)` is False (`name == model == "llama3:8b"`);
   ps identity conflict False for the same reason (lines 233–237).
4. Both selected digests are nonempty strings (lines 238–242).
5. Tags marker: `_remote_marker(tag)` is None.
6. Ps marker: `_remote_marker(ps_matches[0])` iterates `MARKER_FIELDS` in order
   `('remote_model','remote_host')`; `remote_model` absent, `remote_host` is the nonempty
   string `https://remote.invalid` → returns `'remote_host'` (lines 205–210).
   Branch at lines 246–252 returns `remote_inventory` with reasons
   `selected_ps_entry_remote_host_present` and
   `ps_remote_marker_conservative_inference_not_vendor_schema`.
7. `FINDING_EXIT['remote_inventory'] = 1` (line 94); `_run` returns it as the process exit
   (line 515). Payload `verdict_exit` is also 1; `readiness="unknown"`,
   `scope="offline-captures-not-runtime"`.

Why this is the discriminating control: the two digests are equal, so if the ps marker
branch were absent or the digest comparison ran first, the same fixture would return
`loaded_same_digest` / exit 0. The literal expectation `remote_inventory`/1 is exactly the
"equal digest does not override a remote marker" precedence, and it is evaluated before
digest comparison (marker block lines 244–252 precedes digest block lines 256–261).

## Case 27 — `remote_inventory_tags_without_ps_match`

Literal fixture (cases.json index 27):

- `tags.models = [{name:"llama3:8b", model:"llama3:8b", digest:"sha256:1111…1111",
  remote_model:"llama3-cloud"}]`
- `ps.models   = []` (present, valid, empty array)
- `expect = "llama3:8b"`, `expected_exit = 1`, `expected_finding = "remote_inventory"`.

Exact classifier path:

1. `validate_capture` accepts both envelopes; `ps.models` is an empty list, so validation
   passes rather than failing (lines 172–187). The empty array is not a missing ps input:
   `measure.py` writes `ps.json` because `case["ps"] is not None` (lines 223–226).
2. `_matching`: one tags match, zero ps matches. No duplicate-selection branch.
3. Tags match exists; no name/model conflict (`name == model`); tags digest nonempty
   (lines 233–242).
4. Tags marker: `remote_model` is checked first and is the nonempty string
   `"llama3-cloud"` → branch at lines 244–245 returns `remote_inventory` with reason
   `selected_tags_entry_remote_model_present`.
5. Exit 1 via `FINDING_EXIT`; `readiness`/`scope` constants as above.

Why this is the discriminating control: with no ps match, the fallback branch at lines
256–258 would return `available_not_loaded` — also exit 1. So the exit code alone cannot
distinguish this case; only the literal `expected_finding = "remote_inventory"` proves the
tags marker is checked before the absent-ps branch. The current order satisfies that.

## Why the new duplicate-corpus guard cannot alter these two results

Observed guard shape (`.ufo/waves/round-14/measure.py`, `corpus_problems`, lines 350–362;
identical in `.ufo/waves/round-15/frozen/measure-before.py`): it builds `declared` from
`case["name"]` values that are strings and nonempty after `.strip()`, computes
`unique = len(set(declared))`, and currently rejects only `unique < MINIMUM_UNIQUE_CASES`
(16). The round-15 repair adds the missing condition `len(declared) != unique`
("duplicate case names"). That is the entire guard.

- Its only input is the stripped `name` field. It never reads or rewrites `tags`, `ps`,
  `expect`, `expected_exit`, or `expected_finding`, and it returns before
  `measure_case`/child spawn (`run`, lines 372–379).
- Corpus-level query over `cases.json` shows zero groups of duplicate names, and the two
  assigned names each occur exactly once:
  `remote_inventory_ps_same_digest` → count 1,
  `remote_inventory_tags_without_ps_match` → count 1. Declared count equals unique count
  (51 = 51), so `len(declared) != unique` is False and the minimum condition is False
  (51 ≥ 16). The repaired guard passes this corpus; no child is suppressed.
- Even on a hypothetical rejection, the guard's effect is whole-corpus
  `unmeasured_record(..., detail="corpus: …", finding=None)` for every fixture
  (lines 375–378), i.e. a harness-level status, never a rewritten per-case expectation.
- The classifier's normal CLI path does not read `cases.json` at all: `_run` reads only
  `--tags`/`--ps` files and `--expect` (lines 483–516). `measure_case` stages those
  verbatim from `case["tags"]`/`case["ps"]` (`write_capture`, `json.dumps(...,
  ensure_ascii=False)`) and passes `case["expect"]` on argv (lines 223–232). With the guard
  passing, the child inputs for cases 26 and 27 are byte-identical to the pre-repair
  measurement, so the branch sequence above is unchanged.
- `--selftest` is a separate runner and already rejects duplicate raw names before
  spawning children (`run_selftest`, lines 360–371); the measure guard does not feed it.

## Contrary evidence / residual risks (bounded)

- The two runners canonicalize differently: measure strips names, selftest compares raw
  names. A corpus with whitespace-padded name variants could be rejected by measure and
  accepted by selftest. Not applicable here: both assigned names are plain ASCII with no
  leading/trailing whitespace, so raw == stripped.
- `measure.py`'s `case_name` returns the unstripped name for the record label while the
  guard uses the stripped name. Again not applicable to these names.
- Case 27's exit 1 is insensitive to precedence (both `remote_inventory` and
  `available_not_loaded` exit 1); only the finding ID is discriminating. A future reorder
  of the marker/no-ps branches would silently change the ID while keeping exit 1.
- Case 26 would flip to `loaded_same_digest`/0 if the ps-marker branch were removed or the
  digest comparison moved ahead of it. Current static order does not do that.
- `measure.py` may be under in-flight repair by its owner; I read the live file and the
  frozen snapshot, both still showing the minimum-only guard. The repair as specified adds
  a condition without touching case bodies, so the conclusion holds for the planned change.
- No execution was performed, per assignment; the branch walk is static. The `lsp` device
  is not mounted in this session, so no definition/references server answered; text search
  was used for discovery only and is not presented as semantic proof.

## Confidence

High for the two literal expectations, the exact branch order, and guard non-interference
(guarded by the corpus-level uniqueness query). Medium only for any future measure.py edit
that would change staging or `case_name`; none is specified.
