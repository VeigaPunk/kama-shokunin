VERDICT: n/a — census question: 5 live doc files need an appended v2 note; 2 code files need v2 branches; all historical sites stay untouched.

# Receipt-schema consumers: `kama-llamacpp-live/v1`, `health_ready`, `teardown_exited`, `loading_envelope_exact`

## Scope and method

Literal census from the lane root with the mandated exclusions
(`grep -rn --exclude-dir=interactive-sessions --exclude-dir=.git --exclude-dir=.jj`),
one pass per literal, plus targeted count-claim greps (`10 checks`, `10/10`) for
consumers that cite the schema without naming it. Files matched per literal:
`kama-llamacpp-live/v1` 31 files (19 under `.ufo/waves/round-16`, 7 under
`.ufo/waves/round-17`, 1 `tools/`, 1 `tests/`, 1 `corpus/knowledge`, 1
`corpus/SOURCES.md`, 1 `SHONEN.md`); `teardown_exited` 40 (24 round-16, 11
round-17, 2 lessons, 1 each `tools/`, `tests/`, `corpus/knowledge`);
`health_ready` 35; `loading_envelope_exact` 33 (same shape for both, plus
`SCORECARD.md`).

Outside `.ufo`, the schema/check literals appear only in the producer, the gate,
the corpus/knowledge and corpus/SOURCES files, and SHONEN; the count form
(`10 checks`/`10/10`) additionally reaches `SKILL.md`, `SCORECARD.md` and
`LOG.md`. No other executable consumer exists: greps for
`REQUIRED_CHECKS|receipt.json|check-receipt` over non-`.ufo` `*.py`/`*.sh`
(and `registry/`) returned no other file.

No `lsp` device is mounted in this seat's inventory, so these Python constants
and Markdown prose were resolved by literal grep plus direct reads; the v2 spec
in `.ufo/waves/round-17/build/make_spec.py:72-90` is the authority. String
constants and prose are fully determinate here, so no semantic server was
required. [INFERENCE]

A v2 receipt is defined as schema `kama-llamacpp-live/v2` with 11 check ids:
`health_ready, models_alias_id, models_owned_by_llamacpp, metrics_not_enabled,
props_alias, probe_model_ok, probe_mismatch, teardown_graceful,
teardown_port_closed, loading_envelope_graded, model_unchanged`
(`.ufo/waves/round-17/build/make_spec.py:85`).

## A. Live consumers that need an appended v2 note

These are the only non-historical prose sites whose present tense would become
wrong or incomplete when v2 lands. All are append-style: none requires rewriting
an existing claim.

| Site | Evidence | Why v2 forces a note |
|---|---|---|
| `SKILL.md:535` | "0 all 10 checks pass, 1 a check failed" | Capability row hard-codes ten checks; v2 has eleven and renames one. The operational exit map for agents becomes wrong. |
| `SKILL.md:536` | "10 check ids; checks re-derived from stored captures and probe output" | Gate row asserts a ten-id contract; v2 adds `teardown_graceful` + `loading_envelope_graded`. A superseding §Round-17 paragraph matches the file's own "superseded, not edited" precedent at `SKILL.md:509`. |
| `corpus/knowledge/llamacpp-loading-lifecycle.md:144-147` | "`health_ready` checks the status only, not the `{"status":"ok"}` body" … "`loading_envelope_exact` is recorded, not graded" | This paragraph is the exact debt list v2 closes. Append a dated round-17 correction stating v2 grades body, SIGTERM cause and the loading envelope; leave `:101`, `:121` and `:135` (`v1` receipt / `loading_envelope_exact` true / "all 10 checks") as historical text. |
| `corpus/README.md:220-221` | "Still open: live grading of a loading server by the receipt" | The named open item is closed by `loading_envelope_graded`; the frontier disposition must be corrected by appended prose (the file's own pattern at `:154` "Existing criterion/receipt bytes remain historical evidence"). |
| `corpus/SOURCES.md:53` (S041) | "receipt `kama-llamacpp-live/v1` … port 37527" | S041 anchors v1 evidence. Append-only rule 2 (only `status`/`recheck`/`used-by` change in place; `corpus/lessons/round-16-verifier-spotcheck.md:184`) plus the S041 amendment incident mean the v2 run needs a **new superseding row** and an appended round-17 note, never an anchor/teaches edit. `tools/sources-append-only.py` (this round) is the matching guard. |
| `SCORECARD.md:611` | "receipt 10/10 checks, `VALID`" | Round-16 measured row is historical and true; append a round-17 measured-results row, following "Measured values are appended below" (`SCORECARD.md:598-599`). Do not rewrite `:611`. |
| `SCORECARD.md:628` | "receipt gate re-derives every check" | Capability evidence pointer names only the round-16 receipt; append the superseding evidence pointer once a v2 receipt exists. |

`SCORECARD.md:592` ("receipt re-derived by `tests/llamacpp-live/check-receipt.py`")
and `:641-642` (planned: "make the live checks fail-capable") need no note: the
first stays true for v2, the second is the plan the round-17 section supersedes.

## B. Code consumers (edits, not notes)

| Site | Evidence | Required change |
|---|---|---|
| `tests/llamacpp-live/check-receipt.py:45` | `RECEIPT_SCHEMA = "kama-llamacpp-live/v1"` | Accept both schemas; v1 path unchanged. |
| `tests/llamacpp-live/check-receipt.py:174-175` | `if receipt.get("schema") != RECEIPT_SCHEMA:` → "schema is … want" | Hard equality rejects every v2 receipt before any check runs; branch on schema first. |
| `tests/llamacpp-live/check-receipt.py:53-64` | `REQUIRED_CHECKS = (` … `"teardown_exited",` | Ten-id tuple is v1-only; v2 needs its own eleven-id tuple (`teardown_graceful`, `loading_envelope_graded`), and `:618-619` "unexpected check id" must not reject them. |
| `tests/llamacpp-live/check-receipt.py:2`, `:1104` | "Independent validator for a `kama-llamacpp-live/v1` receipt." | Docstring and argparse description become stale; state both schemas. |
| `tools/kama-llamacpp-live.py:50` | `SCHEMA = 'kama-llamacpp-live/v1'` | Producer constant → `v2`. |
| `tools/kama-llamacpp-live.py:23`, `:725` | Receipt schema docstring; epilog "receipt." | Docstring/epilog must describe v2 fields and checks. |
| `tests/llamacpp-live/controls.py` (absent today; `ls` shows only `check-receipt.py`) | — | New counting command; imports nothing from the gate, so no schema coupling. |

Regression obligation, not a note: `.ufo/waves/round-16/live/receipt.json:340`
and `receipt-frozen-probe.json:340` both carry `"schema": "kama-llamacpp-live/v1"`
and must keep validating exactly as before (`make_spec.py:85`). The v1
`--selftest` mutations (`check-receipt.py:1004-1005` `mut("schema-id-changed", …)`)
must also stay meaningful.

## C. Live consumers that need no note

| Site | Evidence | Why none |
|---|---|---|
| `PROVINCE.md:55` | "Round-16 note — lane-owned live fixture (2026-10-20)." | Scope/port/teardown narrative; v2 changes grading strictness, not province or port policy. |
| `SHONEN.md:8` | "10/10 `kama-llamacpp-live/v1` checks" | Literal v1 claim stays true (v1 receipts remain valid). A round-17 sentence is optional, not required; box 2 is `[~]` author assertion. |
| `LOG.md:937-938`, `:966-967` | "C2 operability capability: `tools/kama-llamacpp-live.py`…"; "live tool exit 0, 10/10 checks" | Append-only log history; a new round-17 entry carries v2. No in-place note. |
| `corpus/lessons/round-16.md:160-161` | "live checks `health_ready` (status only), `teardown_exited` and" | Old lesson; contract forbids editing old lessons. Closure belongs in the round-17 lesson (not yet written at census time). |
| `corpus/lessons/round-16-verifier-spotcheck.md:100`, `:187` | "Live checks … `loading_envelope_exact` are weak or ungraded." | Same: historical verification, routed-defect record; append closure to the next lesson, not here. |
| `corpus/QUALITY.md:109` (KQ19) | Exact `MODEL_LOADING` envelope criterion | Calibration criterion for the probe verdict; says nothing about receipt checks or schema. |
| `corpus/knowledge/endpoint-identity.md:216` | "the round-16 live receipt in `corpus/knowledge/llamacpp-loading-lifecycle.md`" | Cross-reference only; target file carries the correction. |
| `corpus/README.md:206` | "one live lane-owned run" | Index row; no count or schema claim. |
| `tests/probe-verdicts/*.json` (9 matrix files) | only the string `"llamacpp-loading"` | Verdict-matrix fixtures, unrelated to the receipt; hard constraint keeps them byte-identical. |

## D. Historical / frozen sites — never edit

- `.ufo/waves/round-16/live/receipt.json:98,169,212,340` and
  `receipt-frozen-probe.json:98,169,212,340`: v1 artifacts (`health_ready`,
  `teardown_exited`, `loading_envelope_exact: true`), also the v1 regression
  fixtures. No note.
- `.ufo/waves/round-16/acceptance.json:55`: `"loading_envelope_exact": true`
  measurement; no edit.
- `.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md:45-59,69-98`
  (defect source: "yes — `teardown_exited`" cannot fail) and the other advice
  files (`ReviewReceiptGateCode.md:177`, `RerunReceiptGate.md:89-90`,
  `LiveReceiptGate.md:13`, `LiveHarness.md:13,22-25`,
  `build/drafts/skill-section.md:55`): historical seat advice, 18-24 files per
  literal under `.ufo/waves/round-16`. No edits, no notes.
- `.ufo/waves/round-16/build/{spec.json,dispatch.json,spawn-result.json,make_spec.py,drafts/}`:
  round-16 build provenance; no edit.
- `.ufo/waves/round-17/frozen/{tools_kama-llamacpp-live.py,tests_llamacpp-live_check-receipt.py,...}`:
  frozen pre-round copies (`SCHEMA` at :50, `RECEIPT_SCHEMA` at :45); never
  edit. They are inputs to the C2 before/after counting command.
- `.ufo/waves/round-17/build/{make_spec.py,spec.json,dispatch.json,...}`:
  the v2 specification and dispatch, not a consumer; no note. Wave-local
  `make_spec.py:74-76` defines `teardown_graceful` and
  `loading_envelope_graded`, matching section A.

## Residual unknowns

- Whether L1 places the `SKILL.md` correction as a new §Round-17 subsection or
  an added row: both are consistent with the file's precedent; a plain rewrite
  of `:535-536` would diverge from "superseded, not edited" (`:509`).
- Whether the round-17 measured run is committed as a new receipt under
  `.ufo/waves/round-17/live/` (assumed, not observed). [INFERENCE]
- `.ufo/waves/round-16/*/advice/*` was classified by grep matches and the named
  files only; I did not read every one of the 18-24 matching files, but they are
  historical seat output under a directory this seat must not edit.

## Installs

None.
