# Legacy8 — provenance supplement for corpus/knowledge/served-model-identity.md

Seat: Legacy8 (executor, leaf). Scope: append provenance only to
`corpus/knowledge/served-model-identity.md`. No delegation, no network/host
commands, no endpoint contact, no build/lint/test runs. Tool installs: none.

## Files changed

- `corpus/knowledge/served-model-identity.md` — appended only (no rewrite):
  `## Provenance supplement — round 11 (2026-10-19)` with `source:`,
  `verified-at:`, `recheck:` at column zero, plus one scope-note sentence.
  1221 → 2462 bytes.

## Behavior / exact retained evidence

- Baseline prefix preserved byte-for-byte:
  `head -c 1221 corpus/knowledge/served-model-identity.md | sha256sum` →
  `294e1192181837cfbc31480c07c005cc012cbd7de7852c6ca58bb1d36d4b630b`,
  identical to `.ufo/waves/round-11/legacy-baseline.json` and to
  `.ufo/waves/round-11/frozen/before/corpus/knowledge/served-model-identity.md`
  (`cmp` → IDENTICAL; frozen copy sha256 and 1221 bytes also equal the baseline).
- Pre-append worktree state: `git diff --quiet HEAD -- corpus/knowledge/served-model-identity.md`
  → exit 0 (file matched HEAD before the append); `git log` for the path shows
  exactly one commit, `c6199a2542440db77d69918599e5a378ee116337`, 2026-09-28T23:15:05-03:00,
  subject "round-1: operability axis — runnable endpoint-identity gate for local model serving".
- Appended text (three field lines at column zero, then a scope note):

```text
## Provenance supplement — round 11 (2026-10-19)
source: retained historical sample — round-1 command ledger `corpus/lessons/round-1.md:3-4` ("grounded in a command run on 2026-09-28") and `corpus/knowledge/listener-census.md` §5 C2 (measured 2026-09-28 ~22:47–22:52 -0300); bytes committed in `c6199a2` (2026-09-28T23:15:05-03:00, "round-1: operability axis") and unchanged at HEAD; no external source.
verified-at: 2026-10-20 (actual UTC metadata-review date: git history and corpus line anchors only; no endpoint contacted, no live revalidation claimed) — original samples observed 2026-09-28 against the then-live 127.0.0.1:34113 llama.cpp server, retired since the 2026-10-14T12:42:32Z snapshot (`registry/history/DELTA.md` systemd-qwen-coder row-absent).
recheck: on authorized revalidation — `bash tools/kama-probe.sh check; echo "CHECK_EXIT=$?"` (read-only registered-row reconciliation; exit 0/2/1; `SKILL.md` §Checklist item 1); do not replay the 34113 samples above as current — re-probe readiness fields only against an operator-authorized serving base URL.

Scope note: the retained bytes above are the readiness/metrics field fragment (health, props, slots, metrics), not the served-id reconciliation procedure.
```

## Why each field is honest

- **source** — cites only retained, in-repo historical evidence: the dated
  round-1 ledger line (`corpus/lessons/round-1.md:3-4`: "Every rule below is
  grounded in a command run on 2026-09-28"; ≤25 words) and the census C2 block
  (`corpus/knowledge/listener-census.md:191-193`, header "Measured: 2026-09-28
  ~22:47–22:52 -0300"). The file's own bytes carry no date, so the date is
  derived from those dated records and the single commit that created the file
  (c6199a2, 2026-09-28T23:15:05-03:00); no date is claimed from the file itself.
  It also states the scope honestly: the retained bytes are a readiness/metrics
  fragment, not the served-id reconciliation procedure (matches the round-11
  critic note). No external source exists for these local samples, so none is cited.
- **verified-at** — separates the two events the task requires: today's review
  (actual host UTC date 2026-10-20, `date -u` → 2026-10-20T02:14:50Z; metadata
  only: git history, corpus anchors, registry ledger) from the original
  observations (2026-09-28). It explicitly disclaims live revalidation and names
  why: the answering server was retired (`registry/history/DELTA.md`:
  "2026-10-14T12:42:32Z systemd-qwen-coder row-absent (was verdict=MODEL_OK
  port=34113)"; round-5 samples are `DEAD`/connection-refused). No endpoint was
  contacted by this seat.
- **recheck** — a precise, safe, authorized path instead of replaying retired
  commands: `bash tools/kama-probe.sh check; echo "CHECK_EXIT=$?"` (read-only,
  registered rows, documented in `SKILL.md` §Checklist item 1; exit 0/2/1).
  It states the limit explicitly: the 34113 samples must not be replayed as
  current, and readiness-field re-probing is gated on an operator-authorized
  serving base URL. No placeholder token; the only conditional is the
  authorization gate itself.
- **Scope note** — added so a future reader is not misled by the filename: the
  bytes are probes/outputs only.

## Axis fit (parent erratum 2026-10-20)

Final C1 axis is calibration (MISSION.md:29 historical; `../shokunin.conf:52`):
this supplement is dates + confidence limits + recheck limits, and makes no
freshness/liveness improvement claim. No claims beyond the appended provenance.

## Risks / limits

- The appended section relies on repo history and corpus anchors; if the round-1
  commit is ever rewritten the c6199a2 citation would need re-derivation.
- `verified-at` cites the DELTA ledger as evidence of retirement; that is a
  registry record, not a live observation this round.
- No endpoint, config, credential, service, or sibling report was touched.

## Checker-relevant summary

- Fields before: source/verified-at/recheck absent. After: all three present at
  column zero (one each), heading retained exactly
  `## Provenance supplement — round 11 (2026-10-19)`.
- Prefix: 1221 baseline bytes preserved (sha256 match), append-only growth to 2462 bytes.
