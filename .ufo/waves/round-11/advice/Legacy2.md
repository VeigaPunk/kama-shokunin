# Legacy2 — round-11 provenance supplement: corpus/knowledge/consumer-registry.md

Seat: Legacy2 (executor, leaf). Lane: kama-shokunin. Bounded slice: append-only provenance
supplement to the one owned file. Actual UTC review date: **2026-10-20** (`date -u` →
`2026-10-20T02:14:49Z`); the steered round label 2026-10-19 is retained in the heading per
spec. Axis note: the parent erratum (`.ufo/waves/round-11/claims.json`) re-assigns C1 to
**calibration** (provenance dates / confidence / recheck limits). The appended fields carry
exactly that: provenance, original-observation vs metadata-review separation, and bounded
rechecks. No freshness refresh, endpoint revalidation or runtime recovery is claimed.

## Files changed

- `corpus/knowledge/consumer-registry.md` — append only, lines 391–395: one blank line, then
  `## Provenance supplement — round 11 (2026-10-19)`, then `source:`, `verified-at:`,
  `recheck:` at column zero. Nothing else in the file was touched; no other file was edited.

## Behavior

Appended section (verbatim fields, see file for the full lines):

- `source: retained historical evidence only — …` (in-repo round-1 record; 2026-10-14
  re-census/teardown; 2026-10-15 teardown sample; 2026-10-19 corrections).
- `verified-at: 2026-10-20 (actual UTC review date, date -u 2026-10-20T02:14Z; heading keeps
  the steered round label 2026-10-19) — metadata-only review … no endpoint contacted, no live
  revalidation claimed. Original observations: 2026-09-28 … 2026-10-14 … 2026-10-15 … 2026-10-19`.
- `recheck: next authorized probe round — run bash tools/kama-probe.sh check … and bash
  tools/kama-probe.sh snapshot …; re-open every §Consumer table row's cited host anchor
  shape-only (test -e, wc -l) before reusing any verdict; endpoint contact only under an
  authorized probe scope.`

## Exact retained evidence (commands + outputs, this seat)

- Prefix preservation — `head -c 39951 corpus/knowledge/consumer-registry.md | sha256sum`
  → `ee2c399226ede70d2e217044a0f17ad70002846cc19da090f48f35065d182972`; identical to
  `.ufo/waves/round-11/legacy-baseline.json` sha256 and to
  `.ufo/waves/round-11/frozen/before/corpus/knowledge/consumer-registry.md` (sha256sum of both
  files equal, verified in one run). New file: 41760 B, 395 lines, sha256
  `6ca37b7747c987008c8d47ed5665b7baaf90c53ecbe017aff233b2a8df4abd28`.
- Field count — `grep -c '^source:'` = 1, `'^verified-at:'` = 1, `'^recheck:'` = 1 (baseline
  listed all three as `missing`; before this append the file had 0).
- Every anchor cited in the supplement was re-opened read-only this seat:
  - `corpus/lessons/round-1.md:3-4` — "Every rule below is grounded in a command run on
    2026-09-28" (round-1 commands date).
  - `corpus/lessons/round-1-citations.md:7-18` — frozen-fact audit table F1 (line 7) through
    F12 (line 18).
  - `corpus/lessons/round-4-recensus.md:26-27` — "`qwen-coder.service` gone; `34113` and
    `8080` refuse. Unblock: operator restores a serving unit."
  - `registry/history/DELTA.md:6-22` — line 6 baseline "2026-09-29T04:30:44Z … (11 rows)";
    lines 9–22 "2026-10-14T12:42:32Z … verdict MODEL_OK -> DEAD" and "row-absent" entries.
  - `registry/history/latest.tsv` — snapshot `20261014T124232Z`, 3 rows all
    `DEAD connection-refused`.
  - `corpus/lessons/round-1-relaunch-freshness.md:10-16` — "Live authority, one
    parent-authorized run 2026-10-15"; "registry_rows_evaluated=3 model_ok=0 drift=3 exit=2";
    "all three registry rows `DEAD` (connection-refused)".
  - `.ufo/round-10/audit/stale-anchors.tsv` — rows A19–A24 and A51 name this file (the
    round-10 correction provenance).
  - `.ufo/round-10/gates/check.json` — `sampled_utc` 2026-10-19T21:35:49Z, exit 2, rows DEAD.
  - `.ufo/waves/round-11/legacy-baseline.json` — pre-state sha256/bytes used above.
- No endpoint, service, config, environment or credential was contacted or read; no network
  command ran. Reads were repo-local plus the two policy files the seat contract directs
  (`~/.omp/agent/RULES.md`, `~/.agents/AGENTS.md`).

## Why each field is honest

- **source** — cites only retained artifacts whose cited lines were re-opened this seat; it
  does not use the "none — historical record" fallback because retained evidence exists. It
  explicitly labels the host-side row targets (#1–#16, #35; relocated/deleted trees) as
  historical record only, so it cannot be read as a live-file claim. The one contested item
  (`.ufo/round-10/gates/check.json`, rejected as S030 authority in round 10) is carried with
  that caveat and is not offered as admitted authority.
- **verified-at** — states the actual review date 2026-10-20 (from `date -u`) separately from
  the steered heading label, and lists the original observation dates (2026-09-28 round-1
  commands, 2026-10-14 re-census, 2026-10-15 relaunch check, 2026-10-19 round-10 corrections).
  The only thing "verified" today is byte metadata (prefix sha256/bytes) and anchor re-opening
  — stated as metadata-only; it explicitly disclaims endpoint contact and live revalidation,
  matching the C1 limit "metadata review is not present endpoint revalidation".
- **recheck** — names the lane's own executable surfaces (`bash tools/kama-probe.sh check`,
  `bash tools/kama-probe.sh snapshot`) and a shape-only anchor re-open, with the endpoint
  contact restricted to an authorized probe scope; no placeholder, no promise of monitoring,
  restoration or runtime recovery.

## Limits and risks

- This seat makes no endpoint-health claim and ran no probe; current-state truth remains the
  round-10-corrected text plus the retained samples cited above.
- The supplement is append-only; §Errata and the round-10 corrections keep their original
  bytes, so the file still contains stale-claim text superseded by its own errata — that is
  the corpus convention (KQ3/KQ7), not a defect of this append.
- Heading carries the steered date 2026-10-19 while `verified-at` carries the actual 2026-10-20
  review date; both are explicit, per the parent's execution-date erratum.
- Prefix preservation is verified by byte count + sha256 above; the parent's checker remains
  authoritative.

## Installs / updates

None — no tool was needed or installed for this read/append slice.

## Blockers

None.
