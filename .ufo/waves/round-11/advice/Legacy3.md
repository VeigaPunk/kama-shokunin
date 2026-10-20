# Legacy3 — C1 provenance supplement for `corpus/knowledge/cross-lane-scope.md`

Seat: Legacy3 (executor). Scope: append-only provenance supplement to
`corpus/knowledge/cross-lane-scope.md`. No other file written. No delegation. No
build/lint/test/formatter run. No network or host-config command executed. No tool
installed or upgraded (nothing needed).

## Files changed

| file | change | before | after |
|---|---|---|---|
| `corpus/knowledge/cross-lane-scope.md` | appended `## Provenance supplement — round 11 (2026-10-19)` (column-zero `source:` / `verified-at:` / `recheck:` + closing note); no byte above rewritten | 18448 B, sha256 `97c7a8138c792a8df6c9608b0933aa0cd5623a09afbf6a6fceb98f66357e02a0` | 22502 B, sha256 `31ee64b4a32816177f9bfb4fdf7bbd3ee354c88411dc154259732b5130992f84` |

## Exact retained evidence

- Prefix preservation (run from lane root):
  `head -c 18448 corpus/knowledge/cross-lane-scope.md | sha256sum` →
  `97c7a8138c792a8df6c9608b0933aa0cd5623a09afbf6a6fceb98f66357e02a0` (equals
  `.ufo/waves/round-11/legacy-baseline.json`); `cmp -n 18448` against
  `.ufo/waves/round-11/frozen/before/corpus/knowledge/cross-lane-scope.md` →
  `IDENTICAL_PREFIX` (exit 0, no output before the echo).
- Fields: `grep -nE '^(source|verified-at|recheck):'` returns exactly 3 lines at
  column zero (83, 84, 85); heading at line 81. No other line in the file matches
  the pattern.
- Actual review date: `date -u` → `2026-10-20T02:14:23Z` (host wave UTC date is
  2026-10-20; the steered label date 2026-10-19 is retained only in the heading,
  per parent steering).
- Retained sources re-opened read-only today: fleet reports
  `/home/vgpnk/Projects/shokunin/.ufo/reports/round-3/kagi.md` (whole file, 73
  lines; drift evidence at :23-28: "Endpoint drift discovered: `opencode.json`
  pins `127.0.0.1:8080/v1`, but 8080 is a **Jitsi videobridge**"), `round-4/kengaku.md`
  (:1-33; "Date: 2026-09-28", drift proof at :18-25), `round-1/kama.md` (grep
  slices; 34113 = llama-server pid 1299, active since 2026-09-28 02:55:28), and
  in-repo `corpus/lessons/round-1.md:1-73` ("grounded in a command run on
  2026-09-28").
- Pointer bounds re-measured: `wc -l` → consumer-registry.md 390, SKILL.md 344,
  PROVINCE.md 52, MINT.md 67 (all cited ranges in bounds).
- File history: `git log --follow` → `c6199a2` (round 1, 2026-09-28, 13089 B) and
  `1e41928` (round 10, 2026-10-19, 18448 B); 13 stale-anchor ledger rows A25–A37
  for this file (`.ufo/round-10/audit/stale-anchors.tsv:25-37`).
- `[L1-F<n>]` bundle search (full lane tree, `grep -rln "L1-F" --exclude-dir=.git .`):
  only `corpus/lessons/round-1-critic.md`, `round-1-safety.md`,
  `probe-mutation-matrix.md` (plus knowledge/frozen references) — no standalone
  bundle file in this repo; the supplement says so instead of implying retention.

## Why each field is honest

- **source** cites only files that exist and were actually opened read-only today
  (fleet reports + `corpus/lessons/round-1.md`), names the in-repo survival of the
  `[L1-F]` facts with exact files, states the standalone bundle is not retained,
  marks the host surfaces (`~/.config/opencode/...`, `~/.local/bin/the-janitor`,
  `qwen-coder.service`) as not retained and not re-read in round 11, and dates the
  in-file corrections and both commits. No claim rests on an unopened source.
- **verified-at** uses the actual UTC review date from `date -u` (2026-10-20),
  explicitly separates it from the steered label date, enumerates what was checked
  (bytes, sha256 vs baseline + frozen copy, pointer bounds) and states the
  confidence limit: presence/dates/bounds only, no endpoint/listener/probe/pin
  contacted, no live revalidation, no observation refreshed. Historic observation
  dates (2026-09-28 round-1/round-3/round-4; 2026-10-19 round-10 corrections) are
  named separately.
- **recheck** is a safe, no-network, pasteable check: prefix sha256 equality at
  `head -c 18448`, two `sed` re-opens of the retained drift evidence at the exact
  lines cited by the file, and a bounds re-check; current endpoint/consumer-state
  revalidation is routed to an operator-authorized probe round
  (`bash tools/kama-probe.sh check` + re-derivation against the round-10 current
  anchors), explicitly not run this round. No placeholder.

## Limits / risks

- The fleet reports and parent `AXES.md`/`MISSION.md` live outside the lane repo;
  the supplement cites them by absolute fleet path (same convention as sibling
  supplements) — they are retained but not lane-local.
- Parent erratum acknowledged (final C1 axis is calibration): this supplement is a
  dates/confidence/recheck-limits artifact, not a freshness refresh; no endpoint
  claim is strengthened.
- This seat is an author advisor; nothing here is a non-author verification.

## Blockers

None.
