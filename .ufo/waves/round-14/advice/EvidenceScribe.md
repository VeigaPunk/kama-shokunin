# Round 14 — EvidenceScribe: L1 final-gate evidence checklist

Scope: static observation only. No tests, builds, classifier/measure/census runs, or
network. Read-only except this file. No tools installed or updated by this seat.
Owner files were not edited.

## 1. Observed state at scribe time (static)

| Item | Observed | Source |
|---|---|---|
| Start commit | `e1b3d746dbfd2100b61c67b6389217252592460f` | `.ufo/waves/round-14/inherited-state.json` |
| Current HEAD | `e1b3d74` (equals start) | `git rev-parse HEAD` |
| Git status | only `?? .ufo/waves/round-14/` (untracked wave receipts) | `git status --porcelain` |
| `tools/kama-ollama-evidence.py` | ABSENT (pending Classifier) | path check |
| `tests/ollama-evidence/cases.json` | ABSENT (pending Fixtures) | path check |
| `.ufo/waves/round-14/measure.py` | ABSENT (pending Harness) | path check |
| `corpus/knowledge/ollama-evidence-replay.md` | ABSENT (pending ReplayKnowledge) | path check |
| `corpus/lessons/round-14.md` | ABSENT (pending QualityCriterion) | path check |
| `corpus/QUALITY.md` KQ IDs | KQ1–KQ16 (16 IDs); KQ17 not yet appended | read |
| `corpus/SOURCES.md` rows | S001–S033 (33 unique IDs) | read |

Counting caveat: a naive `^\| KQ\d+ \|` match returns 15, not 16, because the KQ14 row
reads `| KQ14 (supersedes KQ7's ...` and has no space-pipe after the ID. The
L1 count must use `^\| KQ\d+` (or equivalent) and report 16 before, 17 after.

## 2. Source census (observed, not re-run)

Parsed from `corpus/SOURCES.md` table rows (status column = 9th field).

| Measure | Observed now |
|---|---|
| Rows | 33 (S001–S033, no duplicate IDs) |
| Tier | A 30, B 0, C 3 |
| Status | mined 23, queued 5, rejected 5 |
| Kind | docs 26, spec 2, code 1, community 3, own-work 1 |
| Rows whose used-by names `ollama-evidence-replay.md` | 0 |
| S011 used-by | `runtime-health-surface-matrix.md`, `served-identity-crosswalk.md` (no replay path yet) |
| S012 used-by | same two paths (no replay path yet) |
| S031 used-by | `served-identity-crosswalk.md` (no replay path yet) |

Round-13 receipt (`.ufo/waves/round-13/sources-final.json`) shows the census command
used for this lane: `scripts/sources-census.sh validate --root <shokunin> kama` and
`... census --root <shokunin> kama`. That script lives at the fleet root, outside the
lane. This seat did not inspect or execute it (fleet-path bound), so its existence and
behavior are UNOBSERVED here. L1 must confirm before citing its output. The round-13
validate output carried a warning `W04 S031 duplicate url docs.ollama.com/api/tags across scopes`;
that is a round-13 observation, not a current one.

Expected census after the round-14 Sources seat, by case:
- No S034 added: rows 33, A30, C3, mined23, queued5, rejected5 (unchanged); only
  used-by cells of S011/S012/S031 differ.
- S034 added with tier A and status mined: rows 34, A31, mined24. Any other tier or
  status needs a recorded reason.

## 3. Final-gate evidence checklist (L1 runs; this seat does not)

Commands L1 must run and record with exit codes and literal stdout. Expected
values come from the owner contracts, not from this report.

1. Revision and scope
   - `git rev-parse HEAD` before and after the round commit.
   - `git status --porcelain` clean after commit. No round-14 commit exists yet.
   - `git diff --numstat e1b3d74..HEAD` lists only expected paths:
     `tools/kama-ollama-evidence.py`, `tests/ollama-evidence/cases.json`,
     `.ufo/waves/round-14/measure.py`, `corpus/knowledge/ollama-evidence-replay.md`,
     `corpus/SOURCES.md`, `corpus/QUALITY.md`, `corpus/lessons/round-14.md`,
     `SKILL.md`, `SCORECARD.md`, `LOG.md`, and round-14 receipt files.
     Any other path is a scope defect.
2. Historical immutability
   - `git diff --numstat` deletions = 0 for `corpus/lessons/round-1*.md` through
     `round-13*.md` and all `*-verifier-spotcheck.md`.
   - `corpus/QUALITY.md`: deletions = 0 (append-only KQ17).
   - `corpus/SOURCES.md`: deletions only in used-by cells of S011/S012/S031 (and S034
     append if added). Existing S001–S033 cells otherwise byte-identical.
   - Old source-row prose lines (for example the round-12 and round-13 correction
     paragraphs) keep their text.
   - `.ufo/waves/round-12/acceptance.json` and `.ufo/waves/round-12/record.json` (historical receipts, outside the `corpus/lessons` glob above): `git diff --numstat` shows no changes. Round-12 `corpus/lessons/round-12.md` also byte-identical; D2 presentation debt is handled by an appended clarification in round-14 files only.
3. Classifier
   - `python3 tools/kama-ollama-evidence.py --help` exits 0 with plaintext help.
   - `python3 tools/kama-ollama-evidence.py --selftest` exits 0. Output finding_id
     `clean`; `passed` = total fixtures; `failed` = 0; records list expected and
     observed exit and finding for every case.
   - Static: no `import urllib|http|socket|requests|subprocess`; no `expires_at`
     timestamp validation; no GGUF basename normalization; no file writes beyond
     stdout (selftest temp only, removed).
4. Fixtures
   - `cases.json` loads; `len(cases) >= 16`; `name` values unique.
   - Every case has literal `expected_exit` and `expected_finding`; none is computed.
   - Each verdict appears at least once in `expected_finding`:
     `loaded_same_digest`, `available_not_loaded`, `remote_inventory`,
     `identity_conflict`, `unknown`, `invalid_input` (exact literal set pending
     Classifier confirmation).
   - Inline `tags` and `ps` JSON values present; no fixture refers to a host path or network.
5. Harness
   - `python3 .ufo/waves/round-14/measure.py` exits 0. JSON `total` = `len(cases)`,
     `passed` = total, `failed` = 0, `verdict_exit` = 0.
   - Negative control: `measure.py --tool <absent path>` exits 1 with `failed` = total
     and an unsupported-case reason for each case. A skip or a zero denominator counts as a defect.
6. Source census
   - `validate` and `census` outputs as in section 2, with exit codes, after the Sources seat lands.
7. Quality
   - `corpus/QUALITY.md` has KQ17 with the same row prefix pattern `| KQ17 |`.
   - Count of KQ IDs: 16 before, 17 after.
   - Lesson `corpus/lessons/round-14.md` exists (pending QualityCriterion); outer
     verdict and selected subfinding counts are kept distinct.
   - `corpus/lessons/round-14.md` contains a D2 historical clarification (LegacyCount §4 text or equivalent) naming `corpus/lessons/round-12.md:207–214` and the `"repoint"` record in `.ufo/waves/round-12/acceptance.json` (exit 2 `manifest_invalid`, mismatches 1 under verified anchor). Check by reading the round-14 lesson; the clarification must be appended, with no edit to any historical file.
8. Tools and installs
   - Record `tools installed/updated: none` unless a classifier-owner install is
     reported with tool, version, channel and reason.

## 4. Nonauthor limits (state explicitly in the closure)

- Every round-14 artifact is authored in this wave by lane seats (executors, scouts,
  reviewers, critics). Their agreement inside the wave is not nonauthor evidence.
- The round-13 precedent is a separate, non-author closure (`CloseKamaR13`,
  integrator `hyaku`) that re-read and sampled admits and rejects. No equivalent
  round-14 closure is dispatched or observed. Round-14 admission is therefore
  **pending**, not claimed.
- The `Review*` and `Attack*` seats are static reviews, not runs. Their findings
  are advice to owners. Their output is not execution evidence.
- A fixed selftest with fixtures authored by the same lane proves that the classifier
  matches the lane's own literals. It does not prove external calibration of the
  Ollama field semantics. The score remains `calibration 7 → 7` unless a
  nonauthor admission exists.
- Runtime/readiness is not claimed. `readiness = "unknown"` is an output
  contract, not a finding. Loaded-same-digest is metadata correspondence from
  exported captures, not runtime readiness, and not a current-liveness check.
- Expiry and capture timing are not validated; two captures do not imply
  simultaneous state.

## 5. Measured revision

- The measured revision for round 14 is the L1 commit containing the final bytes.
  No such commit exists at scribe time. A measurement taken before commit measures
  the working tree, not the revision; the receipt must say which.
- Round-13 comparison convention: measured commit = author-delivered HEAD; verifier
  commit is a later one. Round 14 should follow the same split, recording
  `start_commit`, `measured_commit` and any later `verifier_commit` separately.

## 6. Owner recommendations (bounded; no edits to owner files)

- **Classifier (`KamaR14.Classifier`)**: pin the exact `finding_id` literal set and
  the exit map in the file's help text and in `cases.json`. Confirm whether
  `--selftest` emits `clean`/`selftest_failed` on the same `kama-ollama-evidence/v1`
  schema or on a separate one. State that selftest writes only to a removed temp
  directory, since "no writes beyond stdout" and "temp fixtures" both appear in the contract.
- **Fixtures (`KamaR14.Fixtures`)**: include one case per verdict class, using the
  literal IDs agreed with Classifier. Keep `cases.json` at 16 or more with unique
  names. Do not derive `expected_*` from the classifier.
- **Harness (`KamaR14.Harness`)**: take `total` from the cases file length, not
  a computed denominator. Record the unsupported-tool negative control explicitly.
- **Sources (`KamaR14.Sources`)**: keep S011/S012/S031 cells except used-by. If
  S034 is added, report census 33→34 with tier and status. No S034 is needed to
  support the classifier's documented behavior.
- **QualityCriterion (`KamaR14.QualityCriterion`)**: use the `| KQ17 |` prefix so
  the row is counted by the same pattern as KQ1–KQ13 and KQ15–KQ16. The KQ14 row's
  `(supersedes ...)` suffix is historical and must stay as is.

## 7. Limits

- Observed only what is in the working tree, the git index, and the wave receipts
  listed above. Owner files were pending at observation time.
- Did not read fleet or sibling receipts, secrets, environment, configuration, or
  endpoints. Did not run the census script or any test.
- Some of this checklist is inferred from the spec contract. Each item marked as an
  owner expectation is not yet observed in a file.
