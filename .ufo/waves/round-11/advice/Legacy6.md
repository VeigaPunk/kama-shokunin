# Legacy6 — round-11 C1 provenance supplement: free-tier-provider-limits.md

Seat: Legacy6 (executor, leaf). Owned file: `corpus/knowledge/free-tier-provider-limits.md`.
Scope: append-only provenance supplement; no runtime integration, no outside verification,
no endpoint/provider/dispatch contact, no network or host-config commands.

## Files changed

- `corpus/knowledge/free-tier-provider-limits.md` — appended at EOF (no byte above rewritten):
  heading `## Provenance supplement — round 11 (2026-10-19)` plus column-zero `source:`,
  `verified-at:`, `recheck:` lines and one short italic scope note.
- `.ufo/waves/round-11/advice/Legacy6.md` — this report (only other file written).

## Retained evidence (measured)

| Check | Value |
|---|---|
| Baseline (`.ufo/waves/round-11/legacy-baseline.json`) sha256 / bytes / missing | `5dd888709c3525965c4b487588c25d426dee06c2b6059b923b8a3bfa210caf7e` / 3914 / `[source, verified-at, recheck]` |
| Post-edit total bytes | 5760 |
| Post-edit sha256 of first 3914 bytes vs baseline | identical (`prefix_match True`) |
| Column-zero field counts post-edit | `source:` 1, `verified-at:` 1, `recheck:` 1 |
| Heading line | `## Provenance supplement — round 11 (2026-10-19)` (exact) |
| File ends with newline (pre-edit tail `]*\n`, od) | yes — append produced one blank line before the new heading |

Command used for the prefix proof (local, read-only):

```sh
python3 -c "import hashlib;d=open('corpus/knowledge/free-tier-provider-limits.md','rb').read();print(len(d),hashlib.sha256(d[:3914]).hexdigest())"
```

## Why each appended field is honest

- **source** — cites only retained artifacts, each re-opened read-only on 2026-10-20:
  `.ufo/round-6..9/telemetry.json` (lane root) and
  `/home/vgpnk/Projects/shokunin/.ufo/reports/round-6..9/kama.md` (fleet root). All eight
  exist; telemetry was read in full and its recorded values match the status board
  (r6 `2026-10-18T18:35:08Z` 64/0/64; r7 `18:38:06Z` 64/0/64; r8 `18:40:17Z` 0/0/0;
  r9 `18:42:06Z` 0/0/0). The A39 correction note is already in-file. No source is
  invented and none is cited that was not opened today.
- **verified-at** — states the actual review date `2026-10-20T02:14Z` (from `date -u`,
  per parent IRC: host wave runs 2026-10-20 UTC while the steered label date is
  2026-10-19), and separates it from the original observation window
  `2026-10-18T18:32–18:42Z`. It names the review as metadata-only and explicitly states
  that no endpoint, provider, dispatch catalog or wire id was contacted and the dated
  observations are not refreshed — so it makes no live-revalidation claim. Wording
  deliberately avoids any positive "live revalidated today" phrasing.
- **recheck** — supplies a concrete, tested, read-only command (run once by this seat
  before embedding; output below) that re-checks the retained metadata and fleet-report
  presence without network access, and separately states what a live revalidation would
  require (a new operator-authorized single-seat probe of the exact wire id
  `opencode-go/deepseek-v4.1-flash-free` plus a fresh dispatch-catalog listing for the
  `opencode-go/glm-5.3-flash-free` arm), flagged as dispatch-surface work outside a
  documentation round. No placeholder text.

Recheck-command validation output (this seat, local only):

```text
6 2026-10-18T18:35:08Z 64 0 64
round-6 fleet report present
7 2026-10-18T18:38:06Z 64 0 64
round-7 fleet report present
8 2026-10-18T18:40:17Z 0 0 0
round-8 fleet report present
9 2026-10-18T18:42:06Z 0 0 0
round-9 fleet report present
l0-questions present
```

## Grounded quotes (≤25 words)

- `.ufo/round-6/telemetry.json` (recorded 2026-10-18T18:35:08Z): `"400 Upstream request failed: Model is unavailable."` — field `failure_class_verbatim`.
- `.ufo/round-8/telemetry.json` (recorded 2026-10-18T18:40:17Z): `"rejected by the host runtime BEFORE any seat was created; zero spawn attempts; zero upstream contact"` — field `failure_stage`.
- `/home/vgpnk/Projects/shokunin/.ufo/reports/round-9/kama.md:1` (fleet report, 2026-10-18): `# kama — round 9 report (BLOCKED-WITH-DATA)`.

## Risks and limits

- The steered section heading says `(2026-10-19)` while `verified-at` records the actual
  2026-10-20 review date; this split is intentional per parent IRC, and the checker must
  read `verified-at` for the true date.
- The file's line 1 `(rounds 6–17)` remains stale prose; it is already corrected by the
  appended A39 note (round 10) and is not rewritten here — parent owns index/README rows.
- No provider availability claim is added or revalidated; a reader must not treat the
  supplement as evidence that either wire id is dispatchable now.
- The recheck command assumes `python3` and lane-root cwd; it fails loudly rather than
  passing vacuously if either is absent.

## Installs / updates

None by this seat. No tool needed installation; no `pacman`/`uv`/binary installs occurred.

## Blockers

None. Bounded slice complete; existing bytes preserved exactly (prefix sha256 identical),
three fields present once each at column zero.
