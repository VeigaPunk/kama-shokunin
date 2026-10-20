# SourceCurator — round 11 evidence report

Scope: `corpus/SOURCES.md` only (this seat's sole owned file). No tool installs/upgrades (none
needed). No builds/lint/tests run per lane. Documentation-only reads; no runtime integration,
service, config, or endpoint action; no outside non-author verification claimed by this seat.

## Cells changed (exact old -> new; all other row bytes preserved)

1. **S001 used-by** — old: `corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/serving-metrics-crosswalk.md`
   new: `corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/serving-metrics-crosswalk.md, corpus/knowledge/served-identity-crosswalk.md`
2. **S010 used-by** — old: `corpus/knowledge/runtime-health-surface-matrix.md`
   new: `corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/served-identity-crosswalk.md`
3. **S011 status+used-by** — old: `queued | 2026-10-19 | 90d | —`
   new: `mined | 2026-10-19 | 90d | corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/served-identity-crosswalk.md`
   (matrix added on parent instruction; crosswalk per mandate)
4. **S012 status+used-by** — old: `queued | 2026-10-19 | 90d | —`
   new: `mined | 2026-10-19 | 90d | corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/served-identity-crosswalk.md`
5. **S016 status+used-by** — old: `queued | 2026-10-19 | 90d | —`
   new: `mined | 2026-10-19 | 90d | corpus/knowledge/served-identity-crosswalk.md`
6. **Header** — historical sentence kept verbatim; clarification appended:
   `Round 11 (actual review 2026-10-20 UTC; steered round label 2026-10-19) reopened five rows —
   S001, S010, S011, S012, S016 — for the served-identity crosswalk and appended S031 (same
   /api/tags page, remote-entry caveat superseding S011's local-residency implication); opened
   cells keep the round-10 access date, no other historical bytes were rewritten, and the
   round-11 review is recorded in §Search log.`
7. **New row S031 appended after S030** (full row bytes):
   `| S031 | Ollama List models (remote entries) — https://docs.ollama.com/api/tags | docs | A | Ollama `/api/tags` remote inventory caveat: available-model membership is not proof of local residency | OpenAPI 3.1.0, info.version 0.1.0; GET /api/tags; ModelSummary `remote_model` and `remote_host` descriptions | supersedes S011 — available inventory may include `remote_model`/`remote_host`; list membership does not prove local residency; `remote_model` names the upstream model and `remote_host` the upstream Ollama URL. | mined | 2026-10-20 | 90d | corpus/knowledge/served-identity-crosswalk.md |`
8. **Search-log bullet appended** (2026-10-20 UTC): five opened URLs, include/exclude/stop
   rationale, S031 addendum, S011/S012 matrix used-by note (bullet later amended in place to
   record the S031 addendum and the matrix addition; no historical bullet bytes touched).

Not changed: S001/S010 status/opened/recheck; S011/S012/S016 `opened` cells (2026-10-19,
round-10 access, per parent); S012/S016 recheck (90d, no change mandated); all
scope/anchor/teaches fields; S009/S010 matrix used-by retained (parent: still support base-URL
and subset claims); §Paths, §Leads and all other rows byte-identical.

## Recheck quotes (all five pages opened 2026-10-20T02:14:55Z UTC; located; <=25 words each)

- **S001** https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md — §GET `/health`:
  "the model is still being loaded" / "the model is successfully loaded and the server is ready"
  (19 words). Also §GET `/metrics`: "This endpoint is only accessible if `--metrics` is set.";
  §GET `/v1/models`: "model `id` field is the path to model file, specified via `-m`. You can set a
  custom value ... via `--alias`" (20 words).
- **S010** https://docs.ollama.com/api/openai-compatibility — §Endpoints `/v1/models` Notes:
  "`created` corresponds to when the model was last modified"; "`owned_by` corresponds to the
  ollama username, defaulting to `\"library\"`" (18 words). Full-page grep of the fetched text for
  `health`/`Health`: no matches (negative retained).
- **S011** https://docs.ollama.com/api/tags — GET /api/tags: "Fetch a list of models and their
  details" / "Summary information for a locally available model" (16 words).
- **S012** https://docs.ollama.com/api/ps — GET /api/ps: "Models currently loaded into memory" /
  "expires_at: Time when the model will be unloaded" (13 words).
- **S016** https://developers.openai.com/api/reference/resources/models/methods/list — GET /models:
  "Lists the currently available models, and provides basic information about each one such as the
  owner and availability." (18 words).
- **S031** same URL as S011 — ModelSummary: "Name of the upstream model, if the model is remote"
  (10 words; `remote_model`), "URL of the upstream Ollama host, if the model is remote" (`remote_host`).

## Calibration notes (C1 axis per parent erratum)

- New verification date: 2026-10-20 (actual UTC, from `date -u` = 2026-10-20T02:14:55Z); historical
  `opened` 2026-10-19 preserved on all pre-existing rows; S031 `opened` = 2026-10-20.
- Recheck limits: S031 90d; S011/S012/S016 kept 90d; S001/S010 kept on-release. No recheck change
  was mandated; values were not refreshed.
- Confidence limit: page-level revision pins (llama.cpp file commit, OpenAI OpenAPI
  commit/metadata version, Ollama source commits) were NOT re-derived from these renders; rows
  keep their round-10 pins; the search-log bullet records this explicitly.
- Re-read channels: raw.githubusercontent.com `master` (S001); docs.ollama.com markdown alternates
  (S010/S011/S012); developers.openai.com `index.md` alternate (S016).

## Defects / limits

- `corpus/knowledge/served-identity-crosswalk.md` does not exist yet (glob check 2026-10-20);
  rows point at the path per mandate. Creating it is outside this seat's write boundary.
- S011's "locally available" wording is superseded for local-residency implications by S031;
  S011 non-status fields intentionally unchanged per parent instruction.
- S011/S012/S016 statuses were `queued` since round 10 while their pages were already opened;
  the round-11 reopen is what moved them to `mined` (same-day as the round-10 access).
