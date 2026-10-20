# Classifier — offline Ollama tags/ps evidence CLI

## Owned artifact

- `tools/kama-ollama-evidence.py` (new, 531 lines, executable)
- SHA-256: `38d1f5d216181bdb7693582027da83eace707f111f42dd32785d386ffe78fb02`
- No other file written. No git commit. No installs/upgrades (tooling record: none).

## Behavior

CLI: `--tags PATH --ps PATH --expect EXACT_NAME`; `--selftest`. Stdlib only
(`argparse, json, os, stat, subprocess, sys, tempfile, pathlib`); no network,
socket, urllib, time/datetime, environment/config/default-location reads, and
no acquisition path.

Classification output schema `kama-ollama-evidence/v1`; keys `schema,
finding_id, verdict_exit, expected_model, readiness, scope, reasons`; one JSON
object on stdout for every non-help invocation. `readiness` is always
`"unknown"`, `scope` always `"offline-captures-not-runtime"`. `--help` is
plaintext exit 0 and is documented as not a classification.

Final ladder (first match wins), exactly as L1's final no-tags precedence:

1. Structure/types, duplicate raw JSON keys, NaN/Infinity, unreadable/
   non-regular/oversized/non-UTF-8 input -> `invalid_input` 2.
2. More than one selected entry in tags or ps -> `invalid_input` 2.
3. No tags selection -> `unknown` 2, even when a ps entry matches, conflicts,
   or is remote.
4. Selected tags/ps nonempty `name` and `model` differ -> `identity_conflict` 1.
5. Selected tags or ps digest missing/empty -> `unknown` 2.
6. Selected tags or ps valid nonempty remote marker -> `remote_inventory` 1.
7. No selected ps entry (valid empty array allowed) -> `available_not_loaded` 1.
8. Unequal exact digest strings -> `identity_conflict` 1; equal nonempty ->
   `loaded_same_digest` 0.

Deliberate strict policy: identity is exact, case-sensitive `name` or `model`
equality; no trimming, `:latest` inference, GGUF basename stripping, digest
prefix/case normalization, digest-only join, hex validation, expiry/mtime
inspection, or same-file rejection. A selected entry may supply identity
through one field only. Any present recognized field that is not a string
(including `null`, bool, number, list, object) is `invalid_input`; absent or
empty-string remote markers are not markers; markers on unselected entries are
ignored for classification. Digests are compared only after remote and
missing-digest handling, so a missing selected digest is `unknown` before a
valid remote marker, per L1. Unselected entries with missing optional data are
tolerated; their present recognized fields are still type-checked. Inputs are
opened read-only, only regular files, capped at 4 MiB, strict UTF-8, duplicate
keys rejected via `object_pairs_hook`. Reasons are fixed tokens (entry index
and field name only); capture values, paths and remote hosts are never echoed.
Two constant reasons on every classification record state that capture timing/
simultaneity is unasserted and ps expiry is not evaluated.

`loaded_same_digest` is explicitly metadata correspondence only: the tags/ps
digest join is an inference, not vendor-guaranteed artifact equivalence, and
the result is not readiness, liveness, local residency, or current serving
proof. No timestamp, expiry, or cross-host/daemon origin claim is made.

## Selftest

`--selftest` loads the committed `tests/ollama-evidence/cases.json` resolved
from the script directory (no override surface), requires at least 16 unique
case names and all six case keys, then runs the real CLI as child processes
(`[sys.executable, '-I', '-B', script, ...]`, per-case temp dir, 30s timeout,
`shell=False`) and asserts, per case: process exit == `expected_exit`,
`finding_id` == `expected_finding`, schema == `kama-ollama-evidence/v1`,
`verdict_exit` == process exit, readiness/scope constants. Mismatches are
recorded as explicit per-record reason tokens with expected/observed IDs and
exits. Outer result uses schema `kama-ollama-evidence-selftest/v1`, finding_id
`clean|selftest_failed`, `verdict_exit` 0/1, passed/failed/total and records;
the distinct schema keeps clean0 from being read as loaded0. Writes only inside
`TemporaryDirectory` (index-named dirs; case names never used as paths). No
import of this module.

## Retained evidence (static)

- `.ufo/waves/round-14/rulings.json` — final L1 input/mode rules (types, exact
  selection, duplicates, alias conflict, missing digest, remote precedence,
  no expiry/mtime, selftest nonvacuity).
- L1 messages of this wave: final ordering correction (duplicates -> no-tags
  unknown before ps conflict/remote -> alias conflict -> missing digest ->
  remote -> available -> digest); catch-all emit guard; no samefile gate.
- `tests/ollama-evidence/cases.json` — final 51 records (distribution 10/13/28
  per Fixtures), six keys, 51 unique names statically confirmed; statically
  inspected against the ladder, including `remote_missing_digest` (unknown 2),
  `tags_none_ps_duplicates` (invalid_input 2), the renamed
  `unknown_ps_alias_without_tags_match` (unknown 2), name-only/model-only
  loaded pairs, empty-string markers, unselected-entry markers, duplicate raw
  JSON key, non-string/null markers, exact whitespace/prefix digest mismatches.
  Fixture bodies were not executed.
- Prior documentation checks: `corpus/knowledge/served-identity-crosswalk.md`
  (digest join labeled inference), round-11/12 Ollama tags/ps verification.
- ReviewCli/ReviewSchema/ReviewSelftest/SafetyInputs/Harness messages were
  applied where they did not conflict with `rulings.json` or later L1
  corrections: duplicate-key rejection, fixed reason codes, regular-file/byte
  bound, `-I -B` child, distinct selftest schema, >=16 unique cases, guarded
  fallback emit, removal of unrequested `--cases`.

## Verification status / limits

No CLI invocation, `--selftest`, harness, corpus gate, build, lint, formatter,
or test suite was run by this seat (per assignment). One static `ast.parse`
syntax check was performed on an intermediate revision; it is not behavioral
evidence. Static inspection only for the final revision. The L1 gate owns
execution.

Limits: no runtime readiness/liveness claim; captures may be from different
hosts/daemons/times; remote ps markers are a conservative inference from the
tags schema, not an /api/ps vendor field; a caller can supply two unrelated or
identical captures (origin is not validated); digest equality does not prove
artifact identity; unselected malformed identity fields that are valid strings
(e.g. empty strings) are ignored; the selftest requires the committed fixture
corpus, so a missing/partial cases.json yields `selftest_failed` exit 1 rather
than `clean`.

## Risks / blockers

- None blocking. Fixtures landed the final 51-case corpus after implementation
  (distribution 10/13/28); static alignment with the final ladder checked, not
  executed.
- Decision point recorded: outer selftest schema is deliberately
  `kama-ollama-evidence-selftest/v1` (mode-dependent per rulings and
  ReviewSelftest), while each child case is asserted against
  `kama-ollama-evidence/v1`.
- Earlier advisory proposals that conflicted with final authority were not
  adopted: PriorCoverage's duplicate-as-unknown and missing-digest-as-invalid;
  ReviewRemote's null-marker-invalid reading was later confirmed by L1, while
  its duplicate-before-unknown alternative was superseded by L1's explicit
  ordering; the samefile gate was explicitly declined by L1.
