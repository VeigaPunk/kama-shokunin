# KQ19 draft review — interplay with KQ4, KQ13, KQ17, KQ18

Seat: `KamaR16.ReviewKq19Interplay` (read-only). Sampled 2026-10-20 ~10:30 -03.
Inputs read: `corpus/QUALITY.md` (98 lines), `.ufo/waves/round-16/build/drafts/kq19.md`,
`tools/kama-probe.sh` (repaired, sha256 `d0d48d8d6a5d96553adb773ae7f75d4d0f47e19be6b2d7d8a1c9b7a83f6db8fe`),
`.ufo/waves/round-16/frozen/kama-probe-before.sh` + `manifest.json`,
`tests/probe-verdicts/{check.py,*.json}`, `.ufo/waves/round-16/measure.py`,
and llama.cpp `b11755` sources (GitHub raw/API). No probe or lane gate was run.

Axes served: **calibration** (exact envelope, discriminating controls, no-harm
invariant) and **operability** (which registered surfaces the admission actually
covers). This report is advice; L1 owns the measurement.

## Draft verdict

KQ19 is directionally correct and already avoids the main overreach: it is
llama.cpp-scoped, it keeps any non-exact 503 `FOREIGN_SERVICE`, and it names the
red/green pair. The remaining defects are all in the *evidence bar*, not the
rule: the bar is narrower than the probe surfaces the repair actually changes,
it asserts one property (`drift true`) the matrix schema cannot express, and it
does not state the no-harm half of the KQ18-style demonstration.

## Findings by severity

### H1 — the admission bar cannot see the snapshot/history and listeners surfaces the repair changes

The repaired probe changes the header comment (`tools/kama-probe.sh:28-33`),
`VOCAB` (`:60`), usage (`:115`), the classifier branch (`:501-507`), the
listeners counter and summary (`:731`, `:741`), and the baseline whitelist
(`:937`). The matrix runs
only `check --port` (`tests/probe-verdicts/check.py:60`:
`PROBE_ARGV_TAIL = ("check", "--json", "--timeout", "2", "--connect-timeout", "1")`),
which never reaches `diff_baseline` (`tools/kama-probe.sh:1045`) or
`cmd_listeners`. A green matrix is therefore compatible with a snapshot that
drops its own new verdict as malformed: the current whitelist does include
`*\ MODEL_LOADING\ *` (`:937`), but a future edit could omit it and the existing
`warn "latest.tsv: dropping malformed baseline row"` (`:938`) would fire while
the matrix stayed green. The same holds for a listeners summary that omits the
new class. This is exactly the
"only the guard changes" counterpart of `QUALITY.md:87` KQ18:
"The frozen original stays byte-intact as the red control; only the guard changes".
Fix: add the SnapshotCompat control (specified in this wave as
`SnapshotCompat`) plus a listeners
`--port` assertion that `probed == sum(counters)` to the KQ19 evidence, or
narrow the admitted proposition to "the `check --port` classifier path only"
and say the other surfaces are not certified by KQ19.

### H2 — `drift true` is in the admitted sentence but outside the matrix oracle

`drafts/kq19.md:21` says "with reason `llamacpp-loading` (drift true)". The
shared expected schema and the landed harness admit only three keys —
`tests/probe-verdicts/check.py:55`:
`EXPECTED_KEYS = {"verdict", "reason", "exit"}` — and unknown keys are a schema
error (`:131-135`). The record captures `drift` but never compares it
(`:322-329`). The property is true mechanically (`tools/kama-probe.sh:862`:
`if [ "$verdict" != "MODEL_OK" ]; then drift=true; fi`) but it is not measured.
Fix: drop it from the admission conjuncts and state it as recorded-only, or say
"drift=true follows from the existing non-MODEL_OK rule at `kama-probe.sh:862`;
the matrix does not grade it." Do not extend the shared schema mid-wave.

### H3 — the no-harm / changed-set invariant is weaker than "only the intended rows change", and the oracle-independence rule is unstated

`measure.py:349-350` passes on `before failures >= 1`, `after failures == 0`,
and `all_changed_loading`; the diff itself is verdict-only (`:319-332`,
`_verdict(...)`), printed as "tests whose verdict differs before -> after"
(`:335`). Consequences:

- A repair that also changes a **non-loading reason** (verdict unchanged) can
  still pass: the frozen arm fails that row, the repaired arm matches its
  oracle, and the changed-verdict set stays loading-only. KQ18's "only the
  guard changes" discipline is not reproduced.
- A row that is red before but whose verdict does not change is invisible in
  the diff.
- `check.py` does compare reason and exit per record (`:326-329`:
  `record["reason"] == expected["reason"]`), so the *after* arm is exact; the
  before/after *set* is what is under-specified.

Fix: require, as the discriminating condition: (a) on the frozen arm, **every
MODEL_LOADING-expectation row fails** with `FOREIGN_SERVICE` /
`non-2xx-non-model-http` and **every non-loading row passes**; (b) on the
repaired arm, every row passes; (c) the before/after changed
`(verdict, reason, exit)` triple set equals exactly the MODEL_LOADING rows.
Also state that the `expected` values are literal strings authored from the
rule and the b11755 source, never captured from the repaired probe — the build
spec says this (`build/spec.json:19`: "never computed by running the probe")
but the lasting criterion does not.

### M1 — `/health` decoupling is pinned by matrix rows but absent from the criterion

The classifier decides on the `/v1/models` sample and then fetches `/health`
only for evidence (`tools/kama-probe.sh:506`). `LoadingRace.HealthAlreadyOk`,
`.HealthExplicit404`, `.HealthUnlisted`, `.HealthConnClosed` all expect
`MODEL_LOADING`; `.InverseHealthLoadingModelsOk` expects `MODEL_OK`. A future
reimplementation could reasonably require `/health` 503 too and flip these.
Add: "the verdict is decided by the `GET /v1/models` response alone; `/health`
is recorded evidence and never a gate; a race that straddles readiness between
the two requests still yields the verdict of the `/v1/models` sample."

### M2 — exactness negatives miss the integer-type and whitespace cases

The implementation's `integer` clause is real — `tools/kama-probe.sh:434`:
`not isinstance(code, bool) and isinstance(code, int)` — but no matrix row pins
it. `EnvelopeShapes.json` covers invalid JSON, top-level array, `error` string,
missing code, code string, extra fields, nesting, 64 KiB padding, BOM; it has no
`code: 503.0`. [INFERENCE] an equality-only helper (`code == 503`) would accept
`503.0` and the matrix would stay green. Add `EnvelopeShapes.CodeAsFloat`
expecting `FOREIGN_SERVICE` / `non-2xx-non-model-http`, and a
`message: " Loading model"` whitespace negative. (`Overbroad503.lowercase-loading`
already pins case sensitivity.)

### M3 — KQ13: "ready controls" are identity controls, not readiness evidence

KQ13 is `QUALITY.md:40`: "advertised identity and inference readiness are
separate propositions", rejecting "a matching `/v1/models` id is called a
readiness guarantee". The draft says positive controls are "a served model
[that] stays `MODEL_OK`" (`drafts/kq19.md:21`). `MODEL_OK` is still an identity
match. The existing knowledge entry states the limit directly:
`corpus/knowledge/runtime-health-surface-matrix.md:57`:
"A successful model-list identity match is not an inference-readiness guarantee."
Add: "ready-shaped 200 controls demonstrate only non-overreach of the loading
rule; they do not promote `MODEL_OK` to readiness (KQ13)." A concrete instance
already in the matrix is `ReadyControls.ollama-name-not-served-id`
(`--expect stories260K` over `data[0].id == kama-ready` plus Ollama
`models[].name == stories260K` → `MODEL_MISMATCH`): the Ollama-shaped inventory
does not establish served identity under the probe's extraction precedence
(`tools/kama-probe.sh:34-36`).

### M4 — KQ4: preamble omits it; command/exit and probe-error separation are unstated

KQ4 is `QUALITY.md:12`: "the exact command/exit distinguishes drift from probe
failure", rejecting "fixtures are called real-runtime integration". The draft's
reject cell correctly says "A stub matrix is called real-runtime integration
(KQ4, KQ6)" (`drafts/kq19.md:21`), but the preamble (`:13-17`) does not name
KQ4, and the admission does not require the invocation/exit record. Add:
"KQ4 remains in force; the pair records the exact probe argv and each record's
probe exit; exit 1 is a probe error, never a red; the frozen red is the observed
`FOREIGN_SERVICE` / `non-2xx-non-model-http` verdict, not merely a nonzero
exit." (`check.py` already exits 1 on any test failure and 2 on schema, `:26`.)

### M5 — KQ17: borrow the per-test-vs-aggregate discipline, scope out "no network"

KQ17 is `QUALITY.md:72`: "An offline replay classifier reads caller-authorized
exported captures with no network", and "reports the selected outer finding and
exit … separately from every recorded subfinding and aggregate count". Only the
second half transfers: the matrix must report each test's expected/observed
verdict, reason and exit (it does, `check.py:390-393`) and an aggregate
`passes` count alone must not be offered (`measure.py:308-313` prints
per-family counts). The "no network" clause is scoped to an offline replay
classifier; `kama-probe` is a live prober and the harness binds a loopback stub
(`check.py:304`: `http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)`). The draft preamble's
"KQ17's classifier obligations … remain in force" (`drafts/kq19.md:15-16`)
should add: "KQ17's offline/no-network clause is scoped to replay classifiers
and does not forbid the loopback stub harness; only its per-record reporting
discipline is borrowed here."

### M6 — KQ18: frozen-control provenance and non-supersession need naming

KQ18 (`QUALITY.md:87`) is the pattern KQ19 reuses: "a discriminating red/green
pair through the actual runner CLI … The frozen original stays byte-intact as
the red control". KQ19 should say it does not supersede KQ18 and adopt KQ16's
provenance: the frozen arm is the manifest-pinned copy
(`.ufo/waves/round-16/frozen/manifest.json`:
`"capture": "git show 20e392e:tools/kama-probe.sh"`, `source_commit`,
`source_path`, `source_blob`, `sha256`), and `measure.py` verifies both the
sha256 and the `git cat-file blob` bytes (`:76-135`). The draft (`:23`) cites
only the sha256. Add the manifest path, the capture/comparison split (KQ16,
`QUALITY.md:61`), and the no-harm clause from H3. Also note KQ18's
"only the guard changes" cannot apply literally: the probe repair is
multi-surface (H1), so KQ19's analogue is "only the loading-expectation triples
change".

### M7 — KQ6: no opened `SOURCES.md` row for b11755

KQ6 is `QUALITY.md:28`: a vendor statement must name engine, documented revision
and section, and "cites an opened `SOURCES.md` row whose tier fits that scope."
The only llama.cpp row is `corpus/SOURCES.md:13` S001, pinned to
`c0fd78626405c6d9b934efef0ec7291fcc20e3d6` — not b11755. The draft cites the
revision inline (`drafts/kq19.md:21`) but no opened row. Add: "the b11755
README/source row is opened in `SOURCES.md` (S035+) and KQ6 remains in force."

### L1 — stale current-file anchor in the motivating-lesson column

`drafts/kq19.md:21` cites `tools/kama-probe.sh:521-522`; after the repair those
lines are inside `body_has_model_array`/`has_models`, not the old fallback. The
current fallback is `tools/kama-probe.sh:562`
(`C_REASON=non-2xx-non-model-http`). The frozen anchor
(`.ufo/waves/round-16/frozen/kama-probe-before.sh:521-522`) is still correct.
Fix: point the current-file anchor at `:562` (or at the new branch `:501-507`)
and keep the frozen anchor separate. This is a KQ3/KQ7 anchor-honesty issue.

### L2 — "all non-OPTIONS requests" is overbroad and contradicts the row's own reject cell

`drafts/kq19.md:23` calls `server-http.cpp:354` the "pre-routing gate for all
non-OPTIONS requests". The same function exempts frontend assets:
`server-http.cpp:309-311`: `if (frontend_paths.count(req.path)) { return true; // frontend asset, allow it to load`,
and `/` is in that set (`:243`). The row's reject cell correctly says
"frontend paths bypass the 503 gate, `server-http.cpp:310`"
(`drafts/kq19.md:21`). Fix the grounding to "every non-frontend, non-OPTIONS
path"; the probe paths `/v1/models` and `/health` are unaffected.

### L3 — reject-cell phrasing reads as an admission

`drafts/kq19.md:21`: "Any 503 whose message, type, code, body shape or path
differs from the triple above is admitted as loading". In the table's reject
idiom this means "reject that admission", but phrased positively it can be read
as the criterion's own rule. Reword to "is graded/offered as loading" (with the
`no slot available` example staying `FOREIGN_SERVICE`).

### L4 — body-shape evidence is not engine provenance or model identity

The new branch matches any emitter of the triple; `SERVER`/`Content-Type` are
not part of the predicate (`tools/kama-probe.sh:501`). [INFERENCE] a proxy or
relay replaying the body would be graded `MODEL_LOADING`. The lesson draft
already records this limit (`.ufo/waves/round-16/build/drafts/lesson-gate.md:7`:
"the rule checks body shape, not provenance"), but
KQ19 should carry it: the verdict asserts "the identity path answered with the
documented loading envelope", not "llama.cpp is running", not "this model is
loading", and not readiness.

### L5 — "drift true" needs its exit-contract meaning

Under the probe's contract, drift is any non-`MODEL_OK` gate result
(`tools/kama-probe.sh:862`), not evidence that the configured model changed.
If KQ19 keeps the word, gloss it as "gate exit 2 under the probe's non-OK
rule", so it is not read as a KQ4 identity-drift claim.

## Overlap / conflict table (required)

| Criterion | Line | Overlap | Conflict risk | Resolution in KQ19 |
|---|---|---|---|---|
| KQ4 | `QUALITY.md:12` | Both constrain how a measurement is admitted; both separate drift from probe failure and forbid fixture-as-integration. | KQ19's evidence is a stub matrix; read alone it could be taken as runtime proof, or a red could be an exit-1 probe error. | Keep the existing "stub matrix is not integration" reject; add exact argv/exit recording, exit-1-is-not-red, and name KQ4 in the preamble. |
| KQ13 | `QUALITY.md:40` | Both grade what a model-server HTTP response may assert; KQ19 classifies not-ready on the identity route. | "Ready controls" could re-import a readiness claim; `MODEL_LOADING` could be read as an identity negative. | Add "ready-shaped controls are identity-only; loading asserts no identity/readiness"; cite the KQ13 contrast and `ReadyControls.ollama-name-not-served-id`. |
| KQ17 | `QUALITY.md:72` | Both are classifier obligations: per-record vs aggregate reporting, fixed decision order, exact reasons. | KQ17's "no network" and `finding_id`/`verdict_exit` terms are replay-specific; importing them wholesale would forbid the loopback stub or demand fields the probe lacks. | Borrow only the per-test expected/observed discipline; state the offline/no-network clause is scoped to replay classifiers; keep `check.py`'s `verdict/reason/exit` (+ recorded drift) shape. |
| KQ18 | `QUALITY.md:87`; clarification `:89-98` | Both use a frozen-red / repaired-green pair and a byte-intact frozen control. | KQ18's "only the guard changes" cannot hold for a six-surface probe repair; two rows could read as competing general rules. | State non-supersession; replace "only the guard changes" with "the only changed `(verdict, reason, exit)` triples are the MODEL_LOADING rows"; cite the frozen manifest and KQ16. |
| KQ6 (extra) | `QUALITY.md:28` | Vendor revision + opened `SOURCES.md` row. | The inline b11755 citation is not an opened row; S001 pins a different commit. | Open the b11755 row and name it in KQ19. |
| KQ16 (extra) | `QUALITY.md:61` | Frozen-copy provenance: capture vs comparison, manifest-pinned. | The draft cites only the sha256. | Cite `frozen/manifest.json` and the `git show`/`git cat-file` split. |

## Residual risk and verification gaps

- **Harness timing.** `tests/probe-verdicts/check.py` landed during this review
  (484 lines); it was absent at my first read. I did not run it or the probe
  (read-only seat; measurements are L1's). The matrix's 64 tests are statically
  consistent with the shared schema and with `classify()`, but no green/red
  measurement exists in this report.
- **Oracle independence.** The matrix files are literal JSON; whether their
  expectations were authored from the rule or captured from the repaired probe
  is not recorded in the files. KQ19 must require the former (H3).
- **No-harm coverage.** `measure.py`'s stated exit condition is verdict-only
  (H3). A reason-only change outside the loading family can pass unremarked.
- **`python3`-absent path.** The helper fails closed to the old verdict
  (`tools/kama-probe.sh:426-428`), but the matrix cannot exercise a host
  without python3; KQ19 should list this as an untested branch, not a certified
  one.
- **Probe freshness.** `check.py` records `probe_sha256` (`:460`) and
  `measure.py` stores `parsed` in each receipt, so the measured digests are
  available; KQ19 should require them to be quoted in the admission, because
  the probe file can change after the run.
- **Matrix file identity.** `check.py`'s `matrix_sources` is only file names
  (`load_matrix` returns `[s.name …]`), not digests. [INFERENCE] a later matrix
  edit would not be detectable from the receipt alone.
- **Live runtime.** The b11755 behaviour is source-documented here
  (`server-http.cpp:307-325`, README `:479-487`), not observed by this seat;
  L1's 10:17 smoke and the C2 live harness are separate evidence. No claim is
  made that the live envelope matches the stub.
- **Other engines.** [INFERENCE] vLLM/TGI/Ollama not-ready responses lacking
  this exact triple keep their current verdicts; the generic normative phrase
  "must not grade a documented not-ready model-server state as a foreign
  service" is false as a cross-engine rule and must stay scoped to b11755.

## Minimal amendments for L1 / ScribeKq19

1. `drafts/kq19.md:21`: change "(drift true)" to "(non-OK; `drift` recorded,
   not graded)".
2. Add to the admit cell: "The verdict is decided by the `GET /v1/models`
   response alone; `/health` is evidence only. Expected values are literal,
   authored from the rule/b11755 source, never captured from the repaired
   probe. The run records both probe sha256 values and the manifest-pinned
   frozen control (KQ16)."
3. Add to the admit cell: "Before: every MODEL_LOADING row fails
   `FOREIGN_SERVICE`/`non-2xx-non-model-http`, every non-loading row passes.
   After: every row passes. The changed `(verdict, reason, exit)` set is exactly
   the MODEL_LOADING rows."
4. Add to the reject cell: "an equality-only `code` test accepting `503.0`; a
   message with whitespace; a `/health`-only observation; a proxy replay of the
   body offered as engine provenance."
5. Preamble: name KQ4 and KQ6; scope KQ17's no-network clause; state KQ18
   non-supersession; cite the frozen manifest and KQ16.
6. Grounding: "all non-OPTIONS" → "all non-frontend, non-OPTIONS"; current
   anchor `:521-522` → `:562` (or `:501-507`), frozen anchor unchanged.
7. If snapshot/history and listeners are in the admitted scope, add the
   SnapshotCompat baseline round-trip and a listeners counter-sum control;
   otherwise state that KQ19 admits only the `check --port` classifier path.

## Limitations / installs

Read-only seat: the only write is this report. No installs, no upgrades, no
package transactions (pacman is paused host-wide). Network reads were GitHub
raw/API for the b11755 pin and source lines; no local runtime was contacted.
