VERDICT: partial — kagi-shokunin's `/health` rule (`SKILL.md:43` + `corpus/knowledge/op-cli-surface.md:88-91`) is correct for a ready llama.cpp but has no branch for the 503 `Loading model` state that kama now grades `MODEL_LOADING`; its literal `curl -fsS` command discards the body that distinguishes loading from a foreign 503. The handoff note is drafted below; no kagi file was written.

Seat: falsify connector, read-only on `kagi-shokunin`. Report only at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/falsify/advice/ConnectKagiHealthBranch.md`. No subagents. Installs/upgrades: **none**.

## Axes named

| Axis | Verdict | Why |
|---|---|---|
| **adjacency** | improves (report-only) | kama's new verdict is carried to the consumer that owns the endpoint rule; the finding is reported, not absorbed, and kagi keeps edit authority. |
| **calibration** | protected, not claimed | the note keeps `MODEL_LOADING` as body-shape/not-ready, never runtime identity or auth; `/health` 200 remains liveness only. |
| operability / coverage / freshness / depth | unchanged | no kama code, registry row, receipt, or score moves. |

One bounded move: make the handoff a four-state patch — ready / loading / auth / foreign-or-dead — with status+body capture, exact-envelope matching, and an explicit "do not apply this to the 40961 readiness loop" boundary.

## What I ran (exit codes)

1. `grep -n -i health /home/vgpnk/Projects/shokunin/kagi-shokunin/SKILL.md` → matches at `:26,:43,:56,:85,:113,:314,:458,:566` (exit 0).
2. Read-only `sed`/`read` of kagi `SKILL.md:30-130`, `:300-320`, `:540-600`; `corpus/knowledge/op-cli-surface.md:60-115`; `corpus/knowledge/janitor-command-surface.md:45-60`; `PROVINCE.md:1-20`; `corpus/stamps.tsv` rows 24/63.
3. `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py --probe /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh --json` → **exit 0**; `passes: 72`, `failures: 0`; probe sha256 `6edd3c4cfdf3f86c98202cef58859c29406d4a9cec17495454c514ac5972fa50` (matches `sha256sum tools/kama-probe.sh`); **17** `MODEL_LOADING` rows, each `probe_exit: 2`, `drift: true`.
4. Throwaway 503 stub on `127.0.0.1:0` (port 43335; never 8080/34113) + curl:
   - `curl -fsS --max-time 2 http://127.0.0.1:43335/health` → **rc 22**, 0 stdout bytes, stderr `curl: (22) The requested URL returned error: 503`.
   - `curl -sS --max-time 2 -w '\nHTTP %{http_code}\n' …` → **rc 0**, exact body + `HTTP=503`.
   - `curl -sS --fail-with-body …` → **rc 22**, exact body on stdout.
   - stub killed (rc 143); post-kill curl rc 7 (connection refused).
5. `git -C /home/vgpnk/Projects/shokunin/kagi-shokunin status --porcelain` → **exit 0, empty** (no kagi file touched). Kama tree: no edits by this seat outside this Report; the untracked entries are pre-existing round-16 artifacts and pre-existing `__pycache__` dirs (mtimes 10:54-10:59, before this seat).
6. Did **not** run `measure.py`, did **not** start `llama-server`, did **not** bind or probe 8080 or 34113.

## Evidence

| Fact | Evidence |
|---|---|
| kagi's `/health` rule expects only the ready body | `kagi-shokunin/SKILL.md:43` — "`curl -fsS <endpoint-minus-/v1>/health` → `{"status":"ok"}`"; `corpus/knowledge/op-cli-surface.md:88-90` carries the runnable form. |
| kagi's only named foreign shape is 404/close | `corpus/knowledge/op-cli-surface.md:91` — "a foreign listener 404s or closes"; a 503 is not classified. |
| kagi's readiness loop is a different health surface | `corpus/knowledge/janitor-command-surface.md:52-54` — readiness is `client.py health` → `GET http://127.0.0.1:40961/global/health`, `healthy === true`; it never probes the model endpoint. |
| kagi's literal `/health` curl cannot be a claim row | `SKILL.md:299` — claim commands deny `curl`; both files the patch would touch are stamped (`corpus/stamps.tsv:24` op-cli-surface, `:63` SKILL.md). |
| kagi's substrate is declared absent | `PROVINCE.md:10-15` — round-18 erratum: "the surfaces below are HISTORICAL … no `the-janitor`, no `~/.config/the-janitor`". This is a doc correction, not a live gate. |
| kama's verdict contract | `tools/kama-probe.sh:30-36` — `MODEL_LOADING` = GET `/v1/models` 503 + exact envelope; "Drift (exit 2): not ready. A body-shape match only — runtime identity and served model are unverified." |
| exact parser and precedence | `tools/kama-probe.sh:426-445` exact JSON match (integer 503, bool/float/string rejected); `:493-498` 401/403 first; `:501-506` loading branch. |
| loading stub covers `/health` too | `tests/probe-verdicts/LoadingEnvelope.json` row `LoadingEnvelope.canonical-alias`: both `/v1/models` and `/health` return 503 with the same body; expected `MODEL_LOADING`, exit 2. |
| non-exact 503 is not loading | `tests/probe-verdicts/Overbroad503.json` 8 rows — HTML 503, `no slot available`, lowercase `loading model`, string/float/bool code, missing wrapper, plaintext → `FOREIGN_SERVICE`. |
| gate applies to `/health` and precedes API-key auth | `corpus/knowledge/llamacpp-loading-lifecycle.md:27-36` — "every other path, `/health` and `/v1/models` included"; "A loading server with `--api-key` therefore answers 503, not 401." |
| live receipt does not contain a loading capture | `corpus/knowledge/llamacpp-loading-lifecycle.md:103-106` — `loading_observed` false; tiny model ~8 ms; an earlier unreceipted L1 smoke did see `/v1/models` 503; `:122` — "the harness probes only after `/health` is 200". |
| pinned provenance | kama `corpus/SOURCES.md:47-48` (S035 README §GET `/health` lines 479-490, sha256 `714c067b…`; S036 `server-http.cpp` lines 307-328, sha256 `24ede172…`, commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` = b11755); local copies under `.ufo/waves/round-16/sources/llama.cpp-704366d/`. |
| the 503 body is older than b11755 | kama `corpus/knowledge/runtime-health-surface-matrix.md:14` records the same 503 `Loading model` body at README `c0fd7862`. |

## Drafted handoff note (verbatim; kama reports, kagi owns any edit)

````text
DRAFT — kama-shokunin round 16 handoff to kagi-shokunin. Read-only: kama changed no kagi file.

Finding. A single-model llama.cpp server answers GET /health with 503 and
{"error":{"message":"Loading model","type":"unavailable_error","code":503}} while the model
loads; 200 {"status":"ok"} only after load. The same gate covers /v1/models, and the gate runs
before the API-key check (a keyed loading server therefore answers 503, not 401). This is
source-pinned at llama.cpp commit 704366d76 (kama S035/S036) and tested by 17 stub rows; it is
not a claim of runtime identity or of the served model.

Why your row is affected. SKILL.md:43 and corpus/knowledge/op-cli-surface.md:88-91 say
`curl -fsS <endpoint-minus-/v1>/health` -> `{"status":"ok"}`, and "a foreign listener 404s or
closes". A loading llama-server is a third state. Measured on a throwaway 503 stub:
  curl -fsS              -> exit 22, 0 stdout bytes (the body is discarded)
  curl -sS -w ...        -> exit 0, exact body + HTTP=503
  curl --fail-with-body  -> exit 22, exact body on stdout
So the literal current command loses exactly the bytes that separate loading from a foreign 503.

Proposed patch (kagi owns wording, line refs, and whether to land it):
1) SKILL.md:43 — capture status and body, and classify:
     curl -sS --max-time 2 -w '\nHTTP %{http_code}\n' <endpoint-minus-/v1>/health
   - 200 + {"status":"ok"} = ready (liveness; identity still needs the /v1/models id check).
   - 503 + exact envelope = llama.cpp loading; retry; do not repair baseURL. Parse JSON:
     message exactly "Loading model", type exactly "unavailable_error", code an integer 503
     (not true/503.0/"503"); key order and extra top-level keys tolerated.
   - any other 503 (HTML, "no slot available", lowercase "loading model", string/float/bool code,
     missing error wrapper, plaintext) = not the loading branch; remains the foreign/maintenance
     question. kama's 8 Overbroad503 controls all answer FOREIGN_SERVICE.
   - 401/403 = auth. 404/close/refused = the original foreign/dead drift shape.
   Keep the row's existing Never (trusting `status`'s `endpoint` line — it prints config, never
   probes) and the 8080/34113 example. Add: `curl -f` here (drops the body); treating any 503
   as loading; treating 200 as model identity; treating 503 as auth.
2) op-cli-surface.md:88-91 — use the same status-preserving form and update the parenthetical to
   name the 503-loading state and say "retry", not "foreign".
3) Do NOT add MODEL_LOADING to the readiness-loop/auth-pending failure row (SKILL.md:314) or to
   `client.py health`. That loop probes 40961 /global/health, not the model endpoint
   (janitor-command-surface.md:52-54); a model 503 cannot cause it. If a prompt-time error is
   diagnosed, check the model endpoint before editing baseURL: a 503-loading is transient, while
   refused/404 is the drift shape [INFERENCE: opencode's request-time 503 log text was not
   observed on this host].
4) Ledger — both files are stamped (stamps.tsv:24,63). After reviewed edits:
     bash corpus/claim-ledger.sh stamp SKILL.md corpus/knowledge/op-cli-surface.md
     bash corpus/claim-ledger.sh verify   # expected exit 0 CLEAN
   The /health check cannot become a claim row: `curl` is a denied verb in claim commands
   (SKILL.md:299). If the replacement is treated as an external knowledge claim, kama's opened
   pins are available at SOURCES.md:47-48 and .ufo/waves/round-16/sources/llama.cpp-704366d/
   (README sha256 714c067b..., server-http.cpp sha256 24ede172...); kagi decides whether a
   SOURCES row is required.
5) Do not rewrite the Round-3 falsification bullet (SKILL.md:566); it is historical. The current
   decision table is :43.

Boundary. The janitor substrate is declared absent (PROVINCE.md:10-15), so this is a documentation
correction, not a live gate: do not install or start anything for it. kama does not ask kagi to
probe 8080/34113, add credentials, or run a model server. MODEL_LOADING is kama's exit-2 drift
grade and does not prove the runtime; kagi's /health 200 does not either — keep the /v1/models
id check (op-cli-surface.md:76).
````

## Risks and limits

- **No receipted live loading capture.** The branch rests on pinned source, 17 stub rows, and an earlier unreceipted L1 smoke that saw `/v1/models` 503; the round-16 receipt says `loading_observed: false`. Do not upgrade this to "observed live" in the round record.
- **Body-shape matching is spoofable.** The exact envelope is consistent with llama.cpp loading but does not prove the runtime, the model, or readiness. The note says so; kagi must not turn it into an identity claim.
- **`--fail-with-body` is not a substitute for status.** It still exits 22 for 404 and 503, so a script checking only the exit code stays ambiguous; `%{http_code}` is required.
- **Over-application risk.** Adding MODEL_LOADING to kagi's 40961 readiness/auth-pending row would conflate two health surfaces and misdiagnose auth; the note explicitly forbids it.
- **Substrate absence.** kagi cannot run the rule today (`the-janitor` absent); this is a doc correction. kagi's stamps and claim-ledger verification are kagi's to run, not kama's.
- **Line refs.** kagi refs were read at the clean working tree on 2026-10-20 (`git status --porcelain` empty); a later edit can shift them, so the note names row titles as well as numbers.
- **No SOURCES row added.** kagi's sourcing rule decides whether one is needed; kama only supplies the pinned lead.

## Verification for L1

1. `git -C /home/vgpnk/Projects/shokunin/kagi-shokunin status --porcelain` → empty (already measured; this seat writes nothing there).
2. If L1 forwards the note, kagi's acceptance gate is `bash corpus/claim-ledger.sh verify` → exit 0 `CLAIM_LEDGER: CLEAN`; kagi runs it after its own reviewed edit, not kama.
3. Kama's matrix remains the falsifier for the verdict itself:
   `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py --probe /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh --json` → exit 0, `passes: 72`, `failures: 0`.
4. Optional curl repro of the `-f` loss: serve the exact 503 envelope on `127.0.0.1:0`, then compare `curl -fsS` (rc 22, 0 bytes) with `curl -sS -w '%{http_code}'` (rc 0, body + 503). The stub used here was scratch under `/tmp/kama-r16-ConnectKagiHealthBranch/` and has been removed.
