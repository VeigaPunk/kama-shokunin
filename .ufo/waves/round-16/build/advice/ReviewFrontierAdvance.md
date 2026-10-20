# ReviewFrontierAdvance — what C1/C2 advance, what stays open, and the README text to append

Seat: reviewer (leaf, read-only). Axes: calibration (7, lowest) + operability.
Assignment: read `corpus/README.md` §Known gaps / §Frontier and the later frontier
dispositions; decide which frontier items C1/C2 advance and which remain open; propose
append-only README text. This is advice for L1, not a verdict.

## 1. Reviewed state (times -03, 2026-10-20)

| Artifact | State at review |
|---|---|
| `.ufo/waves/round-16/frozen/kama-probe-before.sh` | sha256 `93ee4302…cd64`, byte-frozen red control |
| `tools/kama-probe.sh` | **repaired and landed** 10:27; sha256 `d0d48d8d6a5d96553adb773ae7f75d4d0f47e19be6b2d7d8a1c9b7a83f6db8fe`; 6 hunks, +50/−8 vs frozen (`ProbeLoadingVerdict.md` §Files changed) |
| `tests/probe-verdicts/*.json` | 8 families, 64 tests, unique names and `family` keys well formed; `LoadingEnvelope.json` added 10:28 |
| `tests/probe-verdicts/check.py` | **absent** at review (VerdictHarness item not landed) |
| `tools/kama-llamacpp-live.py`, `tests/llamacpp-live/` | harness absent; `tests/llamacpp-live/` empty at review |
| `corpus/`, `SKILL.md` | untouched by the build wave (`find … -newermt 10:20` → empty) |

No lane gate, harness, probe or test was run by this seat. An LSP server has nothing to
answer here: the reviewed artifacts are Markdown, JSON data and a shell script whose
requested claims are textual, not symbol-resolved. Evidence is literal reads, `diff`, and
byte-level fetches of the pinned upstream blobs. No installs.

## 2. New source fact this seat contributes — the anchor question is settled

`ScribeReadmeFrontier.md` lists as an unknown whether the older pin `c0fd7862` carries the
same `/health` text (its GitHub API call was rate-limited). `ScoutCorpusLoadingClaims.md`
(S-9/S-10/C-4) says the conflict "carries a revision skew that L1 must resolve". It is
resolved, and it resolves **against** the corpus premise, not against the newer revision:

- The pre-routing loading middleware already exists at the corpus pin:
  `https://raw.githubusercontent.com/ggml-org/llama.cpp/c0fd78626405c6d9b934efef0ec7291fcc20e3d6/tools/server/server-http.cpp`
  lines 308–320 carry the identical `is_ready` gate and envelope. At b11755 it is
  `server-http.cpp:307-328`, quote `:312`: "no endpoints are allowed to be accessed when the
  server is not ready".
- In single-model mode `routes.update_meta(ctx_server)` runs **before**
  `ctx_http.is_ready.store(true)` at both revisions: b11755 `server.cpp:514-515`,
  c0fd7862 `server.cpp:495-496`.
- Therefore, at the corpus's own pin, a single-model server that is still loading cannot
  return a `/v1/models` list with `meta: null`: while `is_ready` is false the route is
  gated to the 503 envelope, and once ready `meta` is already populated. The README sentence
  "The `meta` field can be `null` (for example, while the model is still loading)"
  (`README.md:1258` at b11755; `:1256` at c0fd7862) remains a documentation statement with
  no reachable single-model response behind it. Router mode is the plausible home of that
  sentence [INFERENCE]; it is unmeasured.

Consequence for the frontier disposition: the correction owed to
`corpus/knowledge/served-identity-crosswalk.md` is not a "newer anchor supersedes older
anchor" story. The overreach is in the inference itself — `:9` "can answer while that model
is still loading", `:27` the nullable-`meta` premise, `:33` failure case 1, `:50` "can
answer while loading", `:52` "can even be observed mid-load" — and the historical bytes stay
immutable while an appended note corrects the inference. `S001` at `corpus/SOURCES.md:13`
remains the c0fd7862 row; b11755 is an additional pin, not a supersession
(`ScribeSourcesRows.md` §Draft rows already says this).

## 3. Frontier map — advance vs open

Frontier items are `corpus/README.md:66-78`; known gaps are `:56-64`; later dispositions are
`:121-126` (R11), `:128-145` (R12), `:147-161` (R13), `:163-177` (R14), `:179-200` (R15).

| Item | C1 (probe) | C2 (live harness) | Disposition |
|---|---|---|---|
| F1 stale anchors via cited corrections (`:68-70`) | **Conditional advance.** Supplies b11755 plus the contradicting evidence above; no corpus file corrected yet, and the probe header comment (`tools/kama-probe.sh:29-34`) is not a corpus correction. | No. | Open until an append-only correction + an S-row/supplement lands. With those, this is the round's cleanest frontier advance. |
| F2 declared-vs-served **context size** (`:71-72`; gap `:63`) | No. Snapshot schema untouched; only the baseline whitelist gained `MODEL_LOADING` (`tools/kama-probe.sh:937`). | **No.** The receipt's checks are `health_ready, models_alias_id, models_owned_by_llamacpp, metrics_not_enabled, props_alias, probe_model_ok, probe_mismatch, teardown_exited, teardown_port_closed` (LiveReceiptGate item); `--ctx 256` is launch argv, there is no `n_ctx` reconciliation and no declared consumer. | **Open**, unchanged. |
| F3 non-author admit/reject sample (`:73-74`; R14 `:176-177`) | No. | No. | **Open.** QUALITY criteria headers still read "author-appended; no outside review yet" (`corpus/QUALITY.md:43,63,74`). Round 16 adds no outside sample. |
| F4 operator/integrator prerequisites (`:75-78`) | No. | **Mechanism only.** Proves a lane-owned ephemeral runtime can be acquired, launched, probed and torn down without a unit, timer, config write or registered port; it does not dispose the operator's serving runtime. | **Open.** Registered rows are still the 2026-10-14 DEAD census (`corpus/knowledge/consumer-registry.md:70-75`: "Neither port answers."). |
| Gap: real-runtime proven for llama.cpp only (`:60-62`) | No. | **Narrows the qualifier, not the engine set.** A genuine llama.cpp body is now parsed ("parser evidence, not runtime integration" stops applying to llama.cpp); vLLM/Ollama remain uninstalled. | llama.cpp half reproducible; engine coverage unchanged. |
| K02 held by `served-identity-crosswalk.md` (R11 `:123-124`) | Correction owed (see §2). | No. | K02 stays held; the entry's single-model wording needs the appended note. |
| K05 context capacity (R11 `:125`, R12 `:142`, R13 `:159-160`, R14 `:173`, R15 `:197-198`) | No. | No (§F2). | **Open**, still operator-runtime dependent. |
| R15 "No authorized serving runtime was sampled or restored" (`:198-199`) | No. | **Partial.** A lane-owned ephemeral runtime is sampled; nothing is restored, and "authorized" in the operator sense is not established. | Phrase the round as a lane-owned fixture sample, never as restoration or disposition. |

"served-model reconciliation against a real runtime" is therefore **half-advanced**: the
*mechanism* (declared id vs served id on a real llama.cpp `/v1/models`) is exercised against
a live process for the first time, but every *real declared consumer* remains unmeasured and
the fixture's id is the caller's own `--alias` (llama.cpp reports no digest;
`CriticC2ToyModel.md` N1). That distinction is the load-bearing sentence for the README.

## 4. Review of the sibling README draft (`drafts/readme-frontier.md`)

The drafted coverage rows and open-item analysis are sound. Four defects block pasting it
as-is into a permanent corpus file:

- **D1 (high) — transient status is written as permanent disposition.** The draft says
  "C1 … the probe repair is not yet on disk" and cites `tools/kama-probe.sh:513`; the probe
  is on disk (sha `d0d48d8d…`, diff +50/−8, `ProbeLoadingVerdict.md`). A README section is
  corpus history; freezing a mid-flight snapshot makes the corpus false the moment L1
  integrates it. Rewrite as *outcome* prose, or as an explicit "not admitted" disposition.
- **D2 (high) — "C2 not advanced on disk" has the same hazard in the other direction.** If
  the harness lands green, the section understates the round forever; if it does not, the
  correct README statement is "not admitted", not a narration of a build in progress.
- **D3 (medium) — its "unknown" #4 is now answered** (§2). Keeping it as unknown would leave
  a stale caveat and invite the wrong "revision skew" framing.
- **D4 (medium) — vocabulary parity debt is unowned.** The probe and (drafted) SKILL section
  gain `MODEL_LOADING`, but `registry/endpoint-consumers.tsv:32`
  ("`MODEL_OK | MODEL_MISMATCH | FOREIGN_SERVICE | UNAUTHORIZED_SERVICE | DEAD | NOT_HTTP`"),
  `corpus/knowledge/endpoint-identity.md:3` ("The verdict vocabulary is fixed"),
  `corpus/knowledge/consumer-registry.md:84-85` and `SKILL.md:11-13` still enumerate six.
  ScribeSkillSection covers SKILL; no item owns the registry header. Either update it or
  record the deferral in the round lesson; do not let the README assert a shared vocabulary
  while three live surfaces disagree.
- **D5 (medium) — "all exact" needs its scope stated.** The C1 claim says the `error` object's
  three fields are exact, but the matrix admits extra top-level keys:
  `EnvelopeShapes.ExtraFieldsAllowed` sends `meta` and `n_ctx_train` alongside `error` and
  still expects `MODEL_LOADING`. Prose should say "the three named fields are exact;
  additional top-level keys are ignored", or the positive control contradicts the claim.
- **D6 (low) — coverage rows can dangle.** Both rows name files that did not exist at
  review. The README already carries the lesson for this at `:32` corrected by `:102-106`.
  Gate the rows on the files existing and on the entry name matching exactly.
- **D7 (low) — sleep/router predictions.** Keep the draft's `[INFERENCE]` markers and add
  that the C2 receipt cannot settle them: the probe runs only after `/health` 200
  (`CriticC2ToyModel.md` N4/N8), so no live measurement of a sleeping or router-mode verdict
  exists this round.

## 5. Proposed append-only README text

Both variants are appended at EOF only (no line moves, `corpus/README.md:86`, `QUALITY.md`
KQ7/KQ14). Paste exactly one, after the landing gate in §5.3.

### 5.1 Variant A — the wave lands and L1's measurement is green

```markdown
## Frontier disposition — round 16 (2026-10-20)

Round 16 adds `MODEL_LOADING` to the probe vocabulary and a lane-owned live fixture.
Neither expands the corpus's serving surface beyond llama.cpp.

C1 (calibration). The probe no longer grades a pre-ready llama.cpp server as a foreign
service. At `704366d76` the pre-routing middleware answers every non-frontend path with
503 `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` while
`is_ready` is false (`tools/server/server-http.cpp:307-328`; `:312` "no endpoints are
allowed to be accessed when the server is not ready"). The verdict is exact-envelope and
drift-true; `no slot available`, other 503 bodies and every non-503 status keep their prior
verdicts. `MODEL_LOADING` is neither readiness nor identity evidence.

C1 also supplies the correction owed to `served-identity-crosswalk.md`. The same middleware
exists at the older S001 pin `c0fd7862` (`server-http.cpp:308-320`), and in single-model mode
`routes.update_meta` runs before `is_ready.store(true)` (`server.cpp:495-496` at c0fd7862;
`:514-515` at b11755). The documented "`meta` can be `null` … while the model is still
loading" (`README.md:1258`) is therefore not observable through single-model `/v1/models`:
during load the route is gated to 503, and once ready `meta` is populated. The entry's
"can answer while loading" / "observed mid-load" statements are corrected by the appended
note; the historical bytes and the c0fd7862 pin are unchanged. Router mode is not covered by
this correction and is not measured.

C2 (operability). An ephemeral, lane-owned llama.cpp b11755 fixture on an unregistered
loopback port exercises served-id reconciliation, `/props`, `/slots` and `/metrics`-disabled
against a real runtime, then tears down and proves the port closed. It retires the
"parser evidence, not runtime integration" qualifier for llama.cpp only: the probe now
parses a genuine runtime body. It does not serve a registered consumer port, is not a unit
or timer, restores no service, and its toy GGUF is not model-identity evidence (llama.cpp
reports no digest; the served id is the caller's `--alias`). Registered consumers were not
re-measured by this fixture; their last admitted state is the 2026-10-14 errata, three
`DEAD` rows.

Remains open: K05 declared-vs-served context size (no consumer endpoint and no `n_ctx`
reconciliation; the snapshot schema is unchanged); sleeping and router-mode loading
(documented, not measured against the probe); vLLM/Ollama/SGLang runtime integration (not
installed); the non-author admit/reject sample; operator serving-runtime disposition and
registry re-measurement.
```

### 5.2 Variant B — the wave is not admitted (current state at review)

```markdown
## Frontier disposition — round 16 (2026-10-20): not admitted

Round 16's probe change and live fixture were not admitted: <one line, L1: why, plus the
receipt path>. No corpus entry, source pin, capability row or frontier item is advanced by
this round. The single-model loading correction described in `.ufo/waves/round-16/` remains
open, and the items at `corpus/README.md:66-78` are unchanged.
```

Do not paste Variant A with "not yet on disk" sentences from the draft; and do not paste
Variant B while the probe change is in the tree — say what the round *did*, not what was
in flight.

### 5.3 Landing gate for Variant A (all required)

1. `tools/kama-probe.sh` differs from the frozen `93ee4302…` and L1's matrix run is green on
   the repaired probe, red on the frozen one, including positive controls
   (`tests/probe-verdicts/` families, `check.py` must exist and be the runner).
2. The C2 receipt validates (`tests/llamacpp-live/check-receipt.py`) and L1's independent
   `pgrep -x llama-server` / `ss` check shows no survivor and the port closed.
3. An append-only correction for the crosswalk items in §2 exists, with the b11755 and
   c0fd7862 anchors and the `update_meta` ordering.
4. An S-row or appended supplement pins b11755 (`ScribeSourcesRows.md` drafts S035–S038);
   `S001` stays.
5. Verdict vocabulary is consistent on every live surface: probe, SKILL, `endpoint-identity`
   (append), `consumer-registry` (append), `registry/endpoint-consumers.tsv:32`.
6. The knowledge entry and lesson named in the coverage rows exist, with exact paths.
7. If L1 ran an authorized live `check`, cite its time and exit; otherwise keep "not
   re-measured" and the 2026-10-14 state.

## 6. Residual risks and verification gaps

- `tests/probe-verdicts/check.py` did not exist at review; the JSON families are unexecuted
  data, so "64 tests" is a count, not a measurement.
- The C2 harness and receipt validator were absent; their scope decisions are reviewed from
  the spec text and `CriticC2*.md`, not from code.
- I did not reproduce the L1 smoke observation. The b11755 code path is proven from source;
  the observed wire body remains planner-supplied.
- Without `python3`, the repair fails closed to `FOREIGN_SERVICE` (probe limitation,
  `ProbeLoadingVerdict.md`), so the calibration claim is conditional on the probe
  environment.
- `MODEL_LOADING` matches any service that emits the exact envelope; the matrix has no
  server-identity control for that mimic case beyond the exact fields. [INFERENCE] low risk
  at loopback scope.
- Sleeping and router-mode verdicts remain source-level predictions; the round measures
  neither. Do not let the README or knowledge entry promote them.

## 7. Installs

None. Tools used in place: `curl`, `diff`, `sha256sum`, `python3`, `nl`, `grep`, `find`.
No pacman transaction (host-wide pause observed), no `uv`/`npx` install, no service touched.
Scratch fetches lived in `/tmp` (`rc0f.md`, `r11755.md`, `sh11755.cpp`, `shc0f.cpp`,
`b_server.cpp`, `b_c0f_server.cpp`) and are outside the lane.

## 8. Post-revision verification (2026-10-20 10:31 -03)

`ScribeReadmeFrontier` revised `drafts/readme-frontier.md` and its Report against §4.
Re-read at 10:31: D1, D2, D3, D4 and D7 are resolved in the draft.

- The transient "not yet on disk" block is gone; the draft states outcomes and gates
  admission at the end (`### Admission gate for this section`, six conditions).
- The c0fd7862 anchors are carried correctly, and the draft states the `update_meta`-before-
  `is_ready` ordering at both pins without a revision-skew framing.
- The fixture limit is explicit: "It cannot evidence registered-consumer health or
  served-model identity".
- The extra-key rule now reads "Other top-level keys are ignored", matching
  `EnvelopeShapes.ExtraFieldsAllowed`.
- Sleeping/router remain `[INFERENCE]` and the draft states the C2 probe runs only after a
  200 `/health`.

Verified against the repaired probe (read-only): helper `tools/kama-probe.sh:426-445`,
branch `:501-506`, predicate `:440`; sha prefix `d0d48d8d…` matches.

Two residual nits, both cosmetic for L1's integration pass:

1. The coverage-map cells literally contain "(gated on file existence)". The preamble
   already says an absent file means the row is omitted, so the parenthetical should be
   stripped before appending or it becomes permanent table text describing a condition.
2. The vocabulary anchor `SKILL.md:12` names one line of a three-line enumeration; the
   precise anchor is `SKILL.md:11-13` (the six-verdict list spans those lines).

Nothing else in §3 changes: C1 still advances F1 only once the correction and S-row land,
and C2 still advances llama.cpp reproducibility only, not engine coverage or consumer state.

Both §8 nits were applied by `ScribeReadmeFrontier` (draft mtime 10:32:38 -03) and
verified here: no "(gated on file existence)" marker remains, and the vocabulary
anchor reads `SKILL.md:11-13` in the frontier bullet and in the sources table
(draft lines 29 and 55). No residual draft defect remains in this seat's scope.
