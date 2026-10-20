source: S012 https://docs.ollama.com/api/ps §OpenAPI `Ps` / `GET /api/ps`; S031 https://docs.ollama.com/api/tags §OpenAPI `ModelSummary` / `GET /api/tags`; companion lane artifacts (not upstream sources): `tools/kama-ollama-evidence.py` and `tests/ollama-evidence/cases.json`, round-14 interface contract
verified-at: 2026-10-20 — both Ollama OpenAPI pages opened read-only; no serving endpoint, process, environment variable, config, log or credential was read; neither the classifier nor the fixtures were executed by this entry's author
recheck: 90d — S012 §OpenAPI `Ps` + `GET /api/ps`, S031 §OpenAPI `ModelSummary` + `GET /api/tags`; on-change — the `--tags/--ps/--expect/--selftest` flags, the `kama-ollama-evidence/v1` keys, the exit map, and the fixture IDs in `tools/kama-ollama-evidence.py` / `tests/ollama-evidence/cases.json`

# Ollama tags/ps evidence replay — a fail-closed offline classifier

## Claim

Two caller-exported Ollama JSON bodies (`/api/tags` and `/api/ps`) can be replayed
offline into one fixed verdict that separates *available*, *loaded*, *remote* and
*identity conflict*, without contacting a server. The runnable classifier is
`tools/kama-ollama-evidence.py`; this entry records its literal interface and the
lane policy that makes each verdict fail closed.

The verdicts are relative to the **supplied point-in-time captures**, not to the
daemon:

- `loaded_same_digest` means only that the expected name is *listed in the
  supplied ps capture with a digest equal to the supplied tags capture*.
- `available_not_loaded` means only that the expected name is *absent from the
  supplied ps capture* (and present in the supplied tags capture).

Capture times, same-instant capture and same-daemon origin are all unknown and
are not validated; `expires_at` is never evaluated. Neither result is a
readiness, liveness, local-weights or currently-serving claim:
`loaded_same_digest` is metadata correspondence between the two supplied
captures, and `available_not_loaded` is only absence from the supplied ps
capture.

## What the two documented pages actually provide

Both pages are undated Markdown carrying OpenAPI 3.1.0, `info.version 0.1.0`
(opened 2026-10-20). They document response fields; they do **not** document any
matching, precedence or readiness rule. Every classification rule below is
therefore kama lane policy, marked **[INFERENCE]**, not upstream behavior.

| Page | Documented body | Fields the replay may use | Fields the replay must not use |
|---|---|---|---|
| `/api/tags` (S031, `ModelSummary`) | 200 "List available models"; `models` array; entry summary "Summary information for a locally available model" | `name` and `model` (both "Model name"); `digest` ("SHA256 digest identifier of the model contents"); `remote_model` ("Name of the upstream model, if the model is remote"); `remote_host` ("URL of the upstream Ollama host, if the model is remote") | `modified_at`, `size`, `details` — no identity or residency work |
| `/api/ps` (S012, `Ps`) | 200 "Models currently loaded into memory"; summary "Retrieve a list of models that are currently running" | `name` and `model` (both "Name of the running model"); `digest` ("SHA256 digest of the model") | `expires_at` ("Time when the model will be unloaded") is **never** compared with a clock; `size`, `size_vram`, `context_length`, `details` are ignored |

The `/api/ps` OpenAPI schema declares no `remote_model` or `remote_host` field.
Accepting a ps entry that carries those fields as a remote marker is lane policy
**[INFERENCE]** for real-world exports, not a documented ps field. The tags
remote fields are documented; the conclusion that a remote tags entry cannot be
counted as locally loaded is also **[INFERENCE]** (and is already labeled that
way in `served-identity-crosswalk.md`).

## Prior coverage — credited, not re-claimed

The conceptual distinction is already in the corpus and this entry adds none of
it:

- `runtime-health-surface-matrix.md:17` records `/api/tags` = available models,
  `/api/ps` = running models.
- `served-identity-crosswalk.md` §Claim, its Ollama crosswalk row, §Grounded
  failure cases 3, 5 and 6, and §Aliases and path normalization limits already
  record: availability is not loaded residency; `expires_at` bounds a ps sample;
  tags entries may be remote; `name` and `model` are both merely "Model name";
  the tags-to-ps digest join is an inference; alias names can multiply; and
  kama's GGUF basename normalization is a lane convention, not an engine
  equivalence.

What is new here is **operational repertoire only**: a runnable, deterministic
classifier with a fixed exit map, an explicit error decision table, and a
committed fixture set (`tests/ollama-evidence/cases.json`). No new
conceptual coverage, no new engine fact and no runtime observation is claimed.

## Literal replay interface (`kama-ollama-evidence/v1`)

```sh
# Classify two already-exported captures. Inputs are read-only files.
python3 tools/kama-ollama-evidence.py \
  --tags /path/to/exported-tags.json \
  --ps   /path/to/exported-ps.json \
  --expect 'qwen3:8b'
echo "EXIT=$?"

# Replay the fixed committed fixtures through the real child CLI.
python3 tools/kama-ollama-evidence.py --selftest
echo "SELFTEST_EXIT=$?"
```

`--expect` is one exact expected name, preserved verbatim (case included) and
echoed as `expected_model`. There is no endpoint, host, URL, `curl`, fetch,
watch, retry or acquisition flag: the caller must have exported both bodies
under their own authorization. The wave-local measurement wrapper
`.ufo/waves/round-14/measure.py --tool … --cases …` is a round artifact, not a
permanent lane command.

stdout is one JSON object carrying the schema tag `kama-ollama-evidence/v1` and
these keys:

| Key | Value |
|---|---|
| `schema` | the literal `"kama-ollama-evidence/v1"` |
| `finding_id` | one of `loaded_same_digest`, `available_not_loaded`, `remote_inventory`, `identity_conflict`, `unknown`, `invalid_input` |
| `verdict_exit` | the same exit the process returns: `0`, `1` or `2` |
| `expected_model` | the exact `--expect` string, unmodified |
| `readiness` | always the literal `"unknown"` |
| `scope` | always the literal `"offline-captures-not-runtime"` |
| `reasons` | explanatory string list; the verdict is `finding_id` + `verdict_exit`, not the prose |

| Exit | Findings | Meaning |
|---|---|---|
| `0` | `loaded_same_digest` only | the two selected entries agree on name and nonempty digest; this is metadata correspondence, not readiness |
| `1` | `available_not_loaded`, `remote_inventory`, `identity_conflict` | a non-loaded classification or identity conflict, relative to the supplied captures |
| `2` | `unknown`, `invalid_input` | expected model absent from the tags inventory, or the captures could not be safely used |

The replay digits are **not interchangeable** with the older live probe's digits:

| Surface | Exit | Meaning |
|---|---|---|
| `bash tools/kama-probe.sh check` (live gate) | `0` | registered rows reconciled — a live probe result |
| | `1` | could-not-evaluate / probe error |
| | `2` | failed or drift |
| `python3 tools/kama-ollama-evidence.py` (offline replay) | `0` | `loaded_same_digest` only — metadata correspondence |
| | `1` | `available_not_loaded` / `remote_inventory` / `identity_conflict` |
| | `2` | `unknown` / `invalid_input` |

The same digit answers different questions on each surface. Never chain the two
with `&&` or `||` as a routing gate, never read replay exit `0` as `MODEL_OK`,
and never read a probe exit as loaded-model evidence.

`--selftest` is a test-runner mode, not a classification: its own JSON carries
the schema `kama-ollama-evidence-selftest/v1` and reports `finding_id` `clean`
or `selftest_failed` with `verdict_exit` `0`/`1` and passed/failed counts plus
per-case expected/observed exit and finding. Those exits must never be read as a
model verdict. The harness aggregate exit (`0` all fixtures pass, `1` any
failure) is likewise a test result, not readiness. A malformed classification
invocation (including bad argparse argv) emits JSON `invalid_input` exit `2`;
`--help` is conventional plaintext exit `0`. Neither is a classification.

The committed fixture set covers each finding class with fixed adversarial
controls: loaded and available pairs, tags- and ps-side remote markers, name/model
alias conflicts, unequal digests, duplicate selections, missing or empty digests,
missing or malformed captures, and GGUF/case/qualifier non-normalization. The
fixture file is the fixed denominator; no external-authority or runtime claim
attaches to it.

### Matching and policy — all **[INFERENCE]** lane rules

1. **Exact, case-sensitive identity.** Selection is `name == --expect` OR
   `model == --expect`, both exact strings. No trimming, basename, `.gguf`
   stripping, `:latest` completion, case folding or digest normalization. The
   llama.cpp served-id normalization in `SKILL.md` does **not** apply here.
2. **Structure first.** Invalid JSON (including duplicate keys and non-finite
   numbers), unavailable/non-regular/oversized/non-UTF-8 input, a nonobject
   envelope, missing or nonarray `models`, a nonobject entry, or a recognized
   `name`/`model`/`digest`/`remote_model`/`remote_host` field present with a
   non-string type (including `null`) is `invalid_input` before every semantic
   row. Unknown unrelated fields are ignored. A malformed ps capture is never
   treated as an empty one.
3. **Duplicate selection before the inventory gate.** More than one selected
   entry in *either* array is `invalid_input`, even when the tags array has no
   selection at all. There is no arbitrary pick.
4. **Inventory gate next.** No tags selection is `unknown`, even when ps selects,
   even when a ps entry has a name/model conflict, and even when a ps entry is
   remote. This precedes every selected-entry rule below.
5. **Alias conflict.** A selected entry (tags or ps) whose nonempty `name` and
   nonempty `model` differ is `identity_conflict`, before digest presence,
   remote markers and digest comparison. A selected entry may supply identity
   through either field; the other may be absent.
6. **Digest presence.** A missing or empty digest on the selected tags or ps
   entry is `unknown`, before remote markers and before an availability verdict.
7. **Remote before availability and digest.** Any nonempty string
   `remote_model` or `remote_host` on the selected tags or ps entry is
   `remote_inventory`, before the no-ps verdict and before unequal digests are
   compared. Absent or empty-string markers are not remote. Recognizing ps-side
   markers is a conservative lane inference, not a ps OpenAPI field.
8. **Available is tags-only.** A selected local tags entry with a nonempty string
   digest plus no selected ps entry yields `available_not_loaded`. This means
   only "absent from the supplied ps capture": a valid empty ps array is a valid
   capture with no running entries, not proof that the daemon had the model
   unloaded, that a later request would not load it, or that the two files share
   a capture time. The prior rule is `served-identity-crosswalk.md:35-36`:
   absence at one sample must not be concluded either way.
9. **Digest comparison last.** With one selected tags entry and one selected ps
   entry, both digests nonempty, no remote marker, unequal digests are
   `identity_conflict`; equal digests are `loaded_same_digest`. That result is
   metadata correspondence only, never readiness, liveness or local residency.
10. **No time or origin reasoning.** `expires_at`, `modified_at`, wall-clock
    time and file mtime are never inspected; a file stat is allowed only for
    regular-file safety, not timestamp evidence. Both capture times,
    simultaneity and same-host or same-daemon origin are unknown. Passing the
    same path for `--tags` and `--ps` is accepted as unverified caller evidence;
    no origin is inferred from it. Replay does not claim the captures are
    simultaneous, current, unexpired or live.
11. **No normalization back into identity.** Digests are compared as exact
    strings; a digest prefix, case variant or hash-like filename is not a match.

## Error decision table

The first applicable row wins after both files are read; rows 1–2 are structural
validity, row 3 duplicate selection, row 4 the inventory gate, row 5 identity,
row 6 digest presence, row 7 remote, row 8 availability, rows 9–10 digest
comparison.

| # | Condition | `finding_id` | Exit |
|---|---|---|---|
| 1 | tags or ps path missing/unreadable/non-regular/oversized/non-UTF-8, body is not valid JSON, an object repeats a key, or the body carries NaN/Infinity | `invalid_input` | 2 |
| 2 | envelope not an object, `models` absent or not an array, an entry not an object, a recognized field present with a non-string type (including `null`) | `invalid_input` | 2 |
| 3 | more than one selected entry in the tags array or in the ps array (preempts a no-tags verdict) | `invalid_input` | 2 |
| 4 | no tags entry selects `--expect` exactly (preempts ps alias conflict and ps remote markers) | `unknown` | 2 |
| 5 | a selected tags or ps entry has nonempty `name` and nonempty `model` and they differ | `identity_conflict` | 1 |
| 6 | a selected tags or ps entry has a missing or empty digest | `unknown` | 2 |
| 7 | a selected tags or ps entry carries a nonempty string `remote_model`/`remote_host` | `remote_inventory` | 1 |
| 8 | selected local tags entry has a nonempty digest; the supplied ps capture has no selected entry (including empty `models`) | `available_not_loaded` | 1 |
| 9 | selected tags and ps entries both have nonempty digests and they differ | `identity_conflict` | 1 |
| 10 | selected tags and ps entries both have nonempty equal digests, no remote marker | `loaded_same_digest` | 0 |

Rows 1–2 precede every semantic verdict. Duplicate selection preempts the
no-tags verdict; the no-tags verdict preempts alias conflict and remote markers
even when those appear on a selected ps entry; alias conflict precedes missing
digest and remote handling; missing selected digest precedes remote handling;
remote markers precede the ps-absence and digest-comparison verdicts. A malformed
or duplicate-selected ps capture therefore cannot be silently treated as empty,
and neither a malformed, duplicate, conflicting nor remote entry can produce
`loaded_same_digest`.

## What this does not establish

- **Not readiness.** `loaded_same_digest` says two supplied metadata bodies agree
  on a name and nonempty digest. `readiness` stays `"unknown"` for every result,
  including exit `0`. Nothing here proves the model can answer, is resident now,
  or is the model a request would reach.
- **Not current, same-origin or local.** No `expires_at`, `modified_at`, mtime or
  clock check, no liveness probe, no "currently loaded" claim. The two files may
  have been captured at different times, from different daemons, or even be the
  same caller-supplied path; origin and simultaneity are unverified. A local tags
  entry plus a ps match does not prove local weights beyond the digest
  correspondence, and a remote entry is explicitly not local. `available_not_loaded`
  is absence from the supplied ps capture, not proof the daemon would not load
  the model on demand (`served-identity-crosswalk.md:35-36`).
- **Not integration.** No server was contacted; no claim that Ollama is
  installed, running, configured or conforming. The captures are historical
  caller exports, not live state.
- **Not a new conceptual finding.** The tags/ps/digest/remote distinctions are
  the crosswalk's; this entry supplies only an executable replay procedure and
  its failure cases.
- **Not a matching standard.** The docs do not define name matching. Exact,
  case-sensitive comparison, no GGUF normalization and duplicate rejection are
  kama policy choices, not Ollama behavior. An actual server may resolve aliases
  differently.
- **Not a quality or routing verdict.** Whether the model is good is kengaku's;
  which upstream answers is kumitate's; credentials are kagi's.

## Input handling and boundaries

- Inputs are explicitly caller-authorized, already-exported metadata files.
  The tool has no acquisition feature: it cannot query `/api/tags`, `/api/ps`,
  `localhost:11434`, a remote host, or any URL.
- In classification mode the tool reads only the two named paths, opens them
  read-only and preserves their raw bytes. Classification writes no files;
  stdout is the only output. `--selftest` uses a temporary directory and never
  touches a live host.
- The classification path reads no `~/.ollama`, server or client configuration,
  environment variables (including `OLLAMA_HOST`), tokens, logs, process state or
  session material. `--selftest`'s temporary directory location follows Python
  `tempfile` (`TMPDIR`/`TEMP`/`TMP`), and that path is not evidence and is not
  classified. Reports and JSON carry nonsecret shape evidence only.
- A doctored or hostile capture is data, not instruction: fields are compared
  as strings and are never executed, templated or interpreted as commands.
- Restoring or probing a serving runtime remains operator-owned; this replay is
  not a service action and changes no probe behavior.

## kama use

- Use this replay when the question is "given these two exported captures, what
  can be concluded about the expected model?" — not when the question is "is the
  endpoint serving now?" (that remains `tools/kama-probe.sh check` plus a fresh
  sample).
- Quote the `finding_id` with its exit and the two capture identities; quote
  `loaded_same_digest` as metadata correspondence only.
- For a live Ollama endpoint, capture `/api/tags` and `/api/ps` under the
  operator's authorization first, then replay the files offline. Do not add a
  fetch mode to this classifier.
- Keep the GGUF normalization rule for llama.cpp `/v1/models`; do not reuse it
  for Ollama native names.

## QUALITY clearance

- KQ1: no current endpoint claim; no probe was run and no verdict is offered.
- KQ2: pin provenance and effective-runtime selection are untouched; no URL or
  environment value is inferred.
- KQ3: both external anchors name page + OpenAPI revision + section, with the
  2026-10-20 open date; the companion artifacts are identified by path. No old
  file bytes are changed.
- KQ4: offline replay is not runtime integration; the docs are not a live
  service, and fixtures are not host evidence.
- KQ5: no service, config, credential or external state is touched; inputs are
  caller-authorized exports only.
- KQ6: the two upstream statements are field semantics from opened tier-A rows
  S012/S031; every classification rule is labeled **[INFERENCE]** lane policy.
- KQ7–KQ10: not a correction entry (KQ7); no privilege-bounded verdict (KQ8);
  absences are "no match in this capture", not non-existence (KQ9); no census or
  probe was run for this entry (KQ10).
- KQ11: the provenance trio is present; no historical supplement is revived.
- KQ12: prior coverage and the fixed fixture denominator are named; no coverage
  percentage or score is claimed.
- KQ13: available inventory, loaded residency, advertised identity and inference
  readiness stay separate; the digest join is **[INFERENCE]**.
- KQ14–KQ16: no frozen-copy, receipt or byte-comparison claim is made.

## Cited sources

- S012 — Ollama List running models, §OpenAPI `Ps` / `GET /api/ps`, OpenAPI 3.1.0
  info.version 0.1.0; opened 2026-10-20.
- S031 — Ollama List models (remote entries), §OpenAPI `ModelSummary` /
  `GET /api/tags`, OpenAPI 3.1.0 info.version 0.1.0; opened 2026-10-20.
- Companion (not sources): `tools/kama-ollama-evidence.py` and
  `tests/ollama-evidence/cases.json` — round-14 classifier and fixed fixtures.
- Cross-references (not re-derived): `served-identity-crosswalk.md` §Claim,
  Ollama row, failure cases 3/5/6, alias limits; `runtime-health-surface-matrix.md:17`;
  `SKILL.md` §Served-id normalization.

## Round-15 correction — measurement runner duplicate-corpus promise was false (R1)

Appended 2026-10-20 as the named correction routed by
`corpus/lessons/round-14-verifier-spotcheck.md` R1. This corrects a harness
guard claim only: it adds no new API fact, engine behavior, runtime
observation or classification rule, and changes nothing above about the
classifier's own duplicate-*selection* finding (`invalid_input`, row 3).

- **The promise was false for ≥16 unique names.** The round-14 measurement
  wrapper `.ufo/waves/round-14/measure.py` declared (docstring and
  `LIMITS`) that "narrower or duplicated corpora fail before any child
  runs", but its `corpus_problems()` only counted unique `name.strip()`
  values against the 16-name minimum and never compared the declared-name
  total against the unique count. A corpus with ≥16 distinct names plus a
  repeated name therefore passed the guard and spawned child processes.
- **Repair.** The runner now additionally rejects any repeated declared
  name (`"duplicate case names"`) before the minimum-unique check and
  before any child process; a valid all-distinct ≥16-name corpus measures
  exactly as before. The domain classifier `tools/kama-ollama-evidence.py`
  is unchanged — this was a measurement-harness defect, not a replay
  verdict defect. The pre-repair source is frozen at
  `.ufo/waves/round-15/frozen/measure-before.py`.
- **Committed fail-capable tests.** `python3
  tests/ollama-corpus-guard/check.py` replays the literal matrices in
  `tests/ollama-corpus-guard/*.json` — duplicate placements (prepend,
  append, middle, adjacent, distant, multiple, triplicate), whitespace and
  tab collisions, a non-ASCII duplicate, the object `cases` envelope, and
  valid ≥16-unique controls — through the real runner; `--selftest` runs
  the same matrix, and `--runner .ufo/waves/round-15/frozen/measure-before.py`
  exercises the frozen snapshot to expose the old duplicate-admission
  defect. Its exit digits are a test contract result, never a model or
  readiness verdict.
- **Historical receipt stands as the actual unique result.** The round-14
  receipt's corpus was independently recounted as 51 cases / 51 unique
  names, so its recorded fixture results and denominator remain the
  historical actual unique-corpus measurement and are not rewritten. Only
  the generalized "duplicated corpora fail" guarantee was wrong; arbitrary
  caller-corpus quality beyond this finite test matrix is still not
  certified.
- **Historical command versus current path.** The old description of the
  measurement wrapper as a round artifact is retained. Round15 registers
  a regression gate for that artifact, not a permanent serving command or
  new domain capability. Its current path now contains the corrected guard.
  Reconstruct round14's runner from measured revision
  `e545ed99aaa519196a2a7779b0a293b2ce4c765c` at
  `.ufo/waves/round-14/measure.py`, or use the byte-identical preserved
  round15 baseline with explicit `--tool` and `--cases`. Do not reproduce
  a historical run by silently treating the repaired current path as the
  original bytes. Source correspondence and literal digest are recorded
  with the round15 acceptance evidence.
- **Final declared-name boundary.** The runner's active docstring and
  `LIMITS` now explicitly mean declared nonblank string names under the
  existing strip policy. Missing, blank and non-string names remain outside
  that guard; this repair adds no new schema validation. The original
  general wording is not certified even after the predicate fix. Outside
  R1 was a static diagnosis; actual red/green execution is recorded by L1
  in round15. A final-prose-matched causal control removes only the two
  predicate lines and is distinct from the preserved historical source.

- **Repair ordering precision (appended round 16; routed defect 5 of the
  outside round-15 spot-check).** The Repair bullet's "before the minimum-unique check" means
  evaluation order, not a short-circuit. `corpus_problems()`
  (`.ufo/waves/round-14/measure.py:351-365`) appends `duplicate case names`
  first and then still evaluates `unique < MINIMUM_UNIQUE_CASES`, so a
  duplicated and undersized corpus can report both problems. `run()`
  (`.ufo/waves/round-14/measure.py:375-381,396-398`) rejects with per-case
  unmeasured records and exit 1 before spawning any child.
