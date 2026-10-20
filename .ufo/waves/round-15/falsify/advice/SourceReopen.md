# SourceReopen — S012 `/api/ps` re-open (round 15)

Read-only source reopen. No checks, tests, builds, installs, or runtime sampling were
run. No writes outside this report.

## Opened source

- S012: https://docs.ollama.com/api/ps — opened 2026-10-20 (this round), rendered from
  `https://docs.ollama.com/api/ps.md` (alternate-markdown fetch; 248 words).
- Document metadata on the page: OpenAPI 3.1.0, `info.version 0.1.0`, server
  `http://localhost:11434`, `GET /api/ps`, `operationId: ps`.
- Summary: "Retrieve a list of models that are currently running".

## Quote (<=25 words) with location

> "Models currently loaded into memory"

— 5 words; location `GET /api/ps`, `responses.'200'.description`; raw alternate-markdown
page line 35. Supporting adjacent wording, each also under 25 words: the summary line 7
"Retrieve a list of models that are currently running" (10 words) and the `Ps.expires_at`
description line 93 "Time when the model will be unloaded" (7 words).

## Observed source facts

1. The only 200-response description is the loaded-memory statement quoted above.
2. The documented `Ps` fields are `name`, `model`, `size`, `digest`, `details`,
   `expires_at`, `size_vram`, `context_length` — all inventory/metadata descriptions
   (lines 63–99 of the fetched page). No documented field is a readiness, health,
   liveness, or serving-success flag.
3. A literal case-insensitive scan of the fetched alternate-markdown page for
   `ready`, `health`, `duplicate`, `unique`, `preflight`, and `child` returned zero
   matches.
4. The page defines no predicate that maps a `Ps` entry, or its `expires_at`, to
   "weights resident and ready to execute"; `expires_at` is described only as an unload
   time.

## Readiness inference — rejected

- `/api/ps` documents a running-model list, not an inference-readiness guarantee. The
  page supplies no readiness semantics, so a `Ps` entry cannot support a claim that
  inference is available now; a green guard/check result likewise cannot (the guard is a
  finite measurement contract, and no guard execution was performed here).
- The bounded negative claim is that the source **does not establish** readiness; it is
  not a vendor denial that a listed model can serve. Readiness therefore remains
  `unknown` unless separately sampled; nothing on this page upgrades it.
- This confirms the round-15 lesson gate wording (`.ufo/waves/round-15/frozen` context,
  `corpus/lessons/round-15.md` gate row "Loaded metadata or green replay/guard tests
  prove present inference readiness → reject") at the source level.

## Guard attribution — not vendor policy

- S012 contains no duplicate-corpus content: no fixture-name uniqueness rule, no minimum
  cardinality, no preflight, no Python, and no child-process ordering. The
  duplicate-declared-name guard and the sixteen-unique-name floor are lane policy, not
  vendor requirements.
- `SKILL.md`'s sentence "S012's loaded-memory documentation remains a limit, never
  readiness evidence" is a scope limit for S012. It must not be read as S012 endorsing
  or sourcing the duplicate guard. `corpus/SOURCES.md` row S012 ("Separates running
  models from the available-model list and exposes digest, context length, VRAM use, and
  expiry") is consistent with the page; it likewise does not source guard policy.

## Remaining unknowns

- The docs page is undated; the registry keeps its 2026-10-19 `opened` value and this
  reopen date is 2026-10-20. Server-version correspondence to `info.version 0.1.0` was
  not sampled.
- No live `/api/ps` response or inference request was made, so runtime behavior and
  present readiness remain unknown (unknown, not disproven).
- Whether a "loaded into memory" entry is always able to serve is not documented on this
  page; no other page was re-opened for this bounded task.

## Confidence

- Documented quote, field inventory, and absence of readiness/guard terms: **high**
  (direct page observation, exact locations above).
- Rejection of readiness inference from S012: **high** (the page defines no readiness
  predicate; absence of a readiness field is not a serving denial).
- Rejection of S012 as guard-policy authority: **high** (zero duplicate/unique/preflight/
  child terms on the page; guard remains own-work lane policy).

No tool installs or upgrades were performed; no pacman transaction was attempted.
