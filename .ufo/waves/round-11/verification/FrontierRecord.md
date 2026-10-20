# FrontierRecord — kama round 11 source-cell advisory (non-author, advisory only)

Seat: KamaR11.FrontierRecord (leaf). Scope: `kama-shokunin/corpus/SOURCES.md` before/after cells, the inherited SourceCurator advice, the before census JSON, and the S031 quote requirement. No implementation, corpus, or fleet file was edited. No census, validate, test, build, lint, or formatter was run. Outside non-author verification remains separate.

Observation time: 2026-10-20T03:44Z (`date -u`). Installs: none. Tool/version/channel records: none needed.

## Axes

- A1 Cell fidelity: each changed cell's before and after bytes.
- A2 Quote grounding: each reopened or new row's quote against its public page, read by this seat.
- A3 Census delta: before JSON against the registry as it now reads (counted by hand, not executed).
- A4 Used-by resolvability: every `mined` used-by path exists and cites its S-id.
- A5 Contract conformance: SOURCES-CONTRACT-v1 rules 1 and 2 (quote/access logging, old→new logging).

## Before source of truth

- Before bytes: `git show HEAD:corpus/SOURCES.md` (commit 1e41928, round-10). The working tree is modified (`git status`: ` M corpus/SOURCES.md`).
- Before census: `kama-shokunin/.ufo/waves/round-11/sources-census-before.json` → `kama 30 rows, tier.A 27, tier.C 3, mined 17, queued 8, rejected 5`; exit 0. `sources-validate-before.json` → `kama ok`, exit 0.

## A1 — exact cell changes (HEAD → working tree)

| Row | Cell | Before (HEAD) | After (working tree, read 03:44Z) |
|---|---|---|---|
| S001 | used-by | `corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/serving-metrics-crosswalk.md` | `… serving-metrics-crosswalk.md, corpus/knowledge/served-identity-crosswalk.md` |
| S010 | used-by | `corpus/knowledge/runtime-health-surface-matrix.md` | `corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/served-identity-crosswalk.md` |
| S011 | status | `queued` | `mined` |
| S011 | used-by | `—` | `corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/served-identity-crosswalk.md` |
| S012 | status | `queued` | `mined` |
| S012 | used-by | `—` | `corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/served-identity-crosswalk.md` |
| S016 | status | `queued` | `mined` |
| S016 | used-by | `—` | `corpus/knowledge/served-identity-crosswalk.md` |
| S031 | whole row | (absent) | new row, see A2/S031 below; appended after S030 |

Unchanged (verified identical in the read): S011/S012/S016 `opened` (2026-10-19) and `recheck` (90d); S001/S010 status, opened, recheck; all scope, anchor, teaches fields; §Paths; §Leads. Header sentence kept; clarification appended. The curator's old/new values match HEAD and the working tree exactly.

## S031 — exact row (working tree)

```
| S031 | Ollama List models (remote entries) — https://docs.ollama.com/api/tags | docs | A | Ollama `/api/tags` remote inventory caveat: available-model membership is not proof of local residency | OpenAPI 3.1.0, info.version 0.1.0; GET /api/tags; ModelSummary `remote_model` and `remote_host` descriptions | supersedes S011 — available inventory may include `remote_model`/`remote_host`; list membership does not prove local residency; `remote_model` names the upstream model and `remote_host` the upstream Ollama URL. | mined | 2026-10-20 | 90d | corpus/knowledge/served-identity-crosswalk.md |
```

11 cells, NF=13 under the census awk. The curator's proposed bytes match the file.

### S031 quote requirement (for the round-11 lesson `## Gate`, contract rule 1)

The `## Gate` must record, for S031: URL `https://docs.ollama.com/api/tags`; access date `2026-10-20` (UTC; this seat fetched the page at 2026-10-20T03:44Z, method alternate-markdown); and located quotes ≤25 words each:

1. `"Name of the upstream model, if the model is remote"` — OpenAPI `components/schemas/ModelSummary/properties/remote_model/description` (10 words). Grounds `remote_model`.
2. `"URL of the upstream Ollama host, if the model is remote"` — `ModelSummary/properties/remote_host/description` (11 words). Grounds `remote_host`.
3. Counter-quote, required so the supersession is visible: `"Summary information for a locally available model"` — `ModelSummary` schema `description` (7 words). This is the S011-side wording that S031 supersedes.

Teaches caveat: "list membership does not prove local residency" is NOT a quoted sentence on the page. It is an inference from quote 1 (an entry flagged "if the model is remote" is not local). The lesson should mark it `[INFERENCE]` or cite quote 1 as its ground. The row's `supersedes S011 —` opening matches contract rule 2.

Per rule 2, the lesson must also log old→new for every in-place change: S001 used-by, S010 used-by, S011/S012/S016 status and used-by (table above). Changes to `opened` do not occur.

## Quote verification this seat (public pages opened 2026-10-20 UTC)

Verified as quoted by the curator or verbatim in the page:

- S031 `docs.ollama.com/api/tags` — quotes 1–3 above. Verified.
- S011 same page — `"Fetch a list of models and their details"` (paths `/api/tags` description). Verified.
- S012 `docs.ollama.com/api/ps` — `"Models currently loaded into memory"` (200 description); `"Time when the model will be unloaded"` (`Ps.expires_at`). Verified.
- S010 `docs.ollama.com/api/openai-compatibility` — `` "`created` corresponds to when the model was last modified" ``; `` "`owned_by` corresponds to the ollama username, defaulting to `"library"`" ``. Verified. Grep of full fetched text for "health": no matches. Confirmed.
- S016 `developers.openai.com/.../methods/list` — `"Lists the currently available models, and provides basic information about each one such as the owner and availability."` Verified, exact.
- S001 — fetched `raw.githubusercontent.com` `master`, NOT the pinned commit c0fd786. Verified quotes: `"the model is still being loaded."` (§GET /health); `"the model is successfully loaded and the server is ready."`; `"This endpoint is only accessible if `--metrics` is set."` (§GET /metrics); `"Returns information about the loaded model."` (§GET /v1/models); `--alias` id sentence. Verified on master only.

## A3 — census delta (derived by counting the registry; NOT executed)

| Field | Before (JSON) | After (expected, counted) |
|---|---|---|
| kama rows | 30 | 31 |
| tier.A | 27 | 28 |
| tier.B | 0 | 0 |
| tier.C | 3 | 3 |
| status.mined | 17 | 21 (S001–S020 all mined = 20, plus S031) |
| status.queued | 8 | 5 (S021, S022, S023, S025, S029) |
| status.rejected | 5 | 5 |
| FLEET invalid / missing | 0 / 0 | 0 / 0 (expected) |

Before queued 8 = S011, S012, S016, S021, S022, S023, S025, S029. After queued 5 = the last five. The FLEET block mirrors kama because the run is scoped to `kama`. The parent must run the census once after integration to confirm; this seat has not.

## A4 — used-by resolvability

- Every `mined` used-by path in the working tree exists: `corpus/knowledge/runtime-health-surface-matrix.md`, `serving-metrics-crosswalk.md`, `gguf-runtime-compatibility-boundary.md`, `served-identity-crosswalk.md` (all found by `ls`).
- Each cited row appears in its citing file: S001/S010/S011/S012/S016/S031 in `served-identity-crosswalk.md`; S011/S012 in the matrix; S001 in the matrix. Grep confirmed.

## Defects and risks (ranked)

1. **Curator defect is stale.** SourceCurator.md §Defects says `corpus/knowledge/served-identity-crosswalk.md` does not exist. At its 02:14:55Z check that was true. The file's mtime is `2026-10-19 23:23:21 -0300` (= 02:23Z), and it exists now (`git status`: `??`). Do not carry the defect forward. Smallest repair: strike the defect line; the file is untracked, so the parent should stage/commit it with the round.
2. **SOURCES.md changed during this review.** mtime `2026-10-20 00:44:11 -0300` (= 03:44:11Z), within this seat's read window. Re-read the registry before integrating the cells above. Smallest repair: re-run the table check against the final bytes.
3. **Crosswalk overclaims the S001 pin.** `corpus/knowledge/served-identity-crosswalk.md` line 2 says the S001 sections (§GET `/v1/models`, §GET `/models`, §Sleeping on idle) were "verified at this pinned revision". Round-11 read master, not c0fd786; the curator says pins were not re-derived. Smallest repair: change the parenthetical to "verified on master 2026-10-20; pinned-commit text not re-derived". Quotes themselves are correct.
4. **S031 teaches residency claim is inference.** Covered above. Smallest repair: `[INFERENCE]` tag in the Gate, or rely on quote 1.
5. **Round-11 lesson missing.** `corpus/lessons/round-11.md` does not exist (latest is round-10). Contract rules 1–2 require its Gate to hold the S031 URL/date/quote and the old→new log. Parent writes it (per target).
6. **Census not run.** Expected after values in A3 are counted, not measured. The parent must run the census once and paste before/after output (round-11 lesson conformance item 2).

## Already correct

- Before-state of every changed cell matches HEAD exactly.
- S031 row is 11 cells, `supersedes S011 —` opener, tier A, status mined, recheck 90d, used-by resolves.
- All five reopened rows' quotes (S010, S011, S012, S016, S001-on-master) match the pages.
- The curator correctly left S011/S012/S016 `opened` and S001/S010 status/recheck unchanged, consistent with contract rule 2.

## Out of scope / not done

- No census, validate, build, test, lint, or formatter run; no install or upgrade; no commit, push, or config/endpoint probe.
- The pinned-revision claims for S001, S010, S011, S012, S016 were not re-derived against commits; only the quote text was checked.
