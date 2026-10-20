# RevengerPlannerWalk — why `non-2xx-non-model-http` swallows a loading llama.cpp

Bounded data-walk for the L1 planner seat: `git log -p --follow tools/kama-probe.sh`, `LOG.md`,
and the lane artifacts those two cite. Read-only; no install performed.

## Bottom line

The routing is **round-1 code, never revised** — commit `c6199a2` (2026-09-28 23:15:05 -0300),
lines 481-490 of that revision. Round-2 and round-3 do not touch a single branch line
(`git diff c6199a2 83bee7f` / `83bee7f ea72c3e` over that file: no hits on `is2`/`C_VERDICT=FOREIGN`),
and `git log --oneline --follow tools/kama-probe.sh` lists exactly three commits total. `git blame`
attributes the whole branch block — and every row of the published decision table — to `c6199a2`.

The original intent was **narrow and 4xx-shaped**: separate "live but foreign HTTP service" from
`DEAD` after the 8080 incident. The universal quantifier ("any non-2xx") was safe only over the
population the author measured — Jitsi 404 HTML, containerd/omp 404 `text/plain`, one 401 broker.
Round-1's tree contains **zero** occurrences of `503`, `5xx`, or the word "loading"
(`git grep 503|5xx|loading c6199a2 -- .` → no output).

No lane record has ever observed a loading llama.cpp before round 16. The only prior mention of the
503 envelope is **README mining** in rounds 10-11, which never fed back into `classify()`.
So C1 is not "repairing behaviour that once worked"; it is the first contact between the probe's
non-2xx catch-all and the one 5xx that a model runtime issues *before* it is ready. Calibration
wording should say that, not imply a regression.

## Dated timeline

| When | Event | Evidence |
|---|---|---|
| 2026-09-28 23:15:05 -0300 | Probe lands; `classify()` written from scratch. Non-2xx fallback at `c6199a2:481-490`, reason `non-2xx-non-model-http` at `:489`. | `git show --format=fuller c6199a2`; body: "Contract v3 precedence closes the 4xx-html and TCP-accept-then-RST rule gaps" |
| 2026-09-28 | Same round documents rule 5 as a universal: "Any non-`2xx` HTTP status other than `401`/`403`" → `FOREIGN_SERVICE`. | `corpus/knowledge/endpoint-identity.md:17` (blame `c6199a2`) |
| 2026-09-28 | Mutation matrix M1-M7 exercises 404 HTML (M1), 200 JSON look-alike (M4), 401 (M5), non-HTTP bytes (M6) — **no 5xx fixture**. | `corpus/lessons/probe-mutation-matrix.md:10,13,14,15` |
| 2026-09-28 | The one schema hole that would later matter is filed but scoped to 2xx: "Rejecting an unrecognized schema should have a specified verdict" | `corpus/lessons/probe-mutation-matrix.md:31` |
| 2026-09-29 01:34:16 -0300 | round-2 adds `snapshot`; classify untouched (commit body is literally `round-2`). | `git show --format=fuller 83bee7f` |
| 2026-10-14 09:46:23 -0300 | round-3 re-census: `--ufo-src`, registry 11→3 rows; classify untouched. Last time the probe is edited at all. | `git show --format=fuller ea72c3e` |
| 2026-10-19 19:34:42 -0300 | round-10 introduces the first `503` in the lane's corpus — from the llama.cpp README, provenance cell `mined`, dated 2026-10-19. Probe not touched. | `corpus/SOURCES.md:13`; `corpus/knowledge/runtime-health-surface-matrix.md:14` |
| 2026-10-20 00:56:15 -0300 | round-11 re-reads the README quote (`/health` 503 "Loading model") as documentation. Explicitly no runtime claim. | `.ufo/waves/round-11/advice/ReviewIdentity.md:43`; `LOG.md:543` "neither changes runtime health" |
| 2026-10-20 → 05:51:36 | rounds 12-15 (replay/guard/matrix work) land; `git log --follow` still shows only three probe commits. HEAD `20e392e`. | `git log --format='%h %ci' -6` |
| 2026-10-20 10:17 -03 | First **live** loading observation: `GET /v1/models` → 503 `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`. | `.ufo/waves/round-16/build/make_spec.py:16` |
| 2026-10-20 10:19 -0300 | Pre-change probe frozen, SHA-256 `93ee4302…cd64`, from `20e392e` (`classify()` at 415, fallback at 513-525). | `.ufo/waves/round-16/frozen/manifest.json` |
| 2026-10-20 10:26 | Stub families land (`tests/probe-verdicts/Overbroad503.json` mtime 10:26) while the working tree already carries `MODEL_LOADING`. | `ls -la tests/probe-verdicts/`; `tools/kama-probe.sh:30-33,60` |

## Why every non-2xx non-model response becomes `non-2xx-non-model-http`

Mechanically there is no 5xx concept at all; the last `else` is a catch-all:

1. `classify()` issues only `GET /v1/models` (`frozen:418`). Transport errors short-circuit to
   `DEAD`/`NOT_HTTP` (`frozen:424-456`), then 401/403 → `UNAUTHORIZED_SERVICE` (`frozen:458-465`).
2. `is2` is computed exactly once — `case "$F_CODE" in 2*) is2=1 ;; esac` (`frozen:468`). It is used
   **only** to choose a reason string; `5xx` is indistinguishable from `404` here.
3. HTML is excluded at any status (`frozen:470-475`, reason `html-non-model`).
4. `MODEL_OK` requires a model array (`frozen:477-479`); the loading envelope is an `error` object,
   so `has_models=0`.
5. Everything left splits on `is2` (`frozen:513-523`): 2xx gets `schema-unrecognized` /
   `non-model-2xx`; **non-2xx gets `non-2xx-non-model-http`** and the hardcoded evidence text
   "non-2xx HTTP from a non-model service" (`frozen:521-522`) — that phrase is an assertion, not an
   observation, and it is the string that overreaches.

Original intent, stated verbatim by the round-1 record:

- `LOG.md:62-63` — "`systems` 8080 family has no verbatim rule for 4xx-non-model or
  TCP-accept-then-RST, hence contract v3's ordered precedence." The gap being closed was **4xx**.
- `corpus/knowledge/endpoint-identity.md:17` — "A live HTTP error response from a non-model service
  is foreign, not dead."
- `corpus/knowledge/endpoint-identity.md:16` — "HTML is not the model-list API, even on `2xx`;
  HTML `404` is foreign too."
- Real population the rule was fitted to: Jitsi 404 HTML (`listener-census.md:50`), containerd 404
  `text/plain` (`:55`), omp 404 `text/plain` (`:60,61`), auth broker 401 (`:52`). All 4xx (401-404).

Readiness was never an input: the probe *does* fetch `/health`, but only inside the already-proven
`MODEL_OK` branch (`frozen:500`), and only appends it as evidence when the reply is `200`/JSON
(`frozen:501`). A not-ready server can never reach that code, so the load-state surface exists in
the file yet is unreachable for the case that needs it.

## Did any lane record ever observe a loading llama.cpp?

**No — round 16 is the first.** Four independent checks:

- `grep -c '503' LOG.md` → **0** across all 923 lines. `LOG.md:542`'s "nullable-loading" is a
  documentation limit of the round-11 crosswalk, not a measurement.
- `registry/history/latest.tsv` has 3 data rows, all `DEAD connection-refused`; no snapshot ever
  persisted a non-2xx reason (`grep -rn 503 registry/history/` → nothing).
- Repo-wide, the literal `non-2xx-non-model-http` appears only at its definition, the frozen copy,
  and round-16 build artifacts — **never in a recorded probe output**.
- The 503 knowledge that does exist is source-mined, not device-measured: `corpus/SOURCES.md:13`
  carries provenance `mined | 2026-10-19`, and `runtime-health-surface-matrix.md:14` says
  "503 `unavailable_error` \"Loading model\" while loading".

[INFERENCE] Therefore C1's stub matrix is the first conformance test this branch has ever had, and a
red-before result is guaranteed by construction rather than evidence of recent drift. The stronger
calibration claim is "the universal non-2xx quantifier was never constrained by a 5xx case", not
"the probe used to classify loading correctly".

## Divergences and risks the planner should carry into the claim

1. **Doc coupling is mandatory, not optional.** `corpus/knowledge/endpoint-identity.md:17` publishes
   rule 5 as "Any non-`2xx` … `FOREIGN_SERVICE`" in a *first-match precedence* table. A verdict
   insertion without a new/qualified row makes the published contract false. `SKILL.md:12` holds the
   vocabulary line (`MODEL_OK | MODEL_MISMATCH | FOREIGN_SERVICE | …`), so it needs the same edit.
2. **Precedence constraint.** The loading 503 is `application/json`; it currently reaches the final
   `else` because `is2=0`, `ishtml=0`, `has_models=0`. The new branch must sit after the 401/403 and
   HTML tests, or an nginx HTML 503 (`Overbroad503.nginx-html-503`) silently changes verdict.
3. **Exactness is what keeps the fix from becoming "5xx = loading".** Non-envelope 503s are real:
   vLLM returns 503 on `EngineDeadError` (`runtime-health-surface-matrix.md:15`), and llama.cpp's own
   "no slot available" 503 is a different `error` body. Gating on message+type+code exactness is
   load-bearing for the observed contract, not stylistic.
4. **Evidence-string honesty.** Even after the fix, the surviving `non-2xx-non-model-http` evidence
   text still asserts "from a non-model service" for arbitrary 5xx. That wording survives for
   non-envelope 503s and remains an interpolation. Cheapest correct follow-up (out of C1 scope) is
   to make the evidence text state only the observation: status, content-type, no model array.
5. **Working tree is live.** During this walk a sibling added `MODEL_LOADING` to `tools/kama-probe.sh`
   (`:30-33` header, `:60` VOCAB, `:115` verdict list), shifting the fallback to `:526`. Historical
   line numbers here are cited from the frozen snapshot so the planner has stable anchors.

## Method and limits

Searches bounded to the named file's history, `LOG.md`, `corpus/`, `registry/`, `tests/`,
`.ufo/waves/round-11`, `.ufo/waves/round-16`. No lane gate, harness or probe run was executed;
no `.ufo/interactive-sessions`, session or credential store read. No tools installed.
