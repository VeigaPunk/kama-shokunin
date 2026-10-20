# Legacy9 — provenance supplement for `corpus/knowledge/snapshot-history.md`

## Change

Appended, at end of file only:

- `## Provenance supplement — round 11 (2026-10-19)` (steered round label retained per parent IRC)
- one `source:` line, one `verified-at:` line, one `recheck:` line, all at column zero

Nothing prepended, nothing rewritten, no existing line touched.

## Retention measurement (acceptance criterion)

- `head -c 6067 corpus/knowledge/snapshot-history.md | sha256sum`
  → `93b2c6f2a6db619751d1d65e1d5c9590c610d594525242f08c24725ee27bb4f5`
  — identical to the baseline sha256 for 6067 original bytes in
  `.ufo/waves/round-11/legacy-baseline.json`; prefix preserved exactly.
- New size `wc -c` = 8316 bytes (original 6067 + 2249 appended).
- `grep -cE '^(source|verified-at|recheck):'` = 3 (exactly one of each field).
- `git status --porcelain` → only ` M corpus/knowledge/snapshot-history.md`.

## Why each field is honest

**source:** cites only artifacts that exist in the repository now — `tools/kama-probe.sh`
(anchors re-derived read-only today), `tools/test-snapshot.sh` (harness exists; its
`RESULT pass=24 fail=0` is explicitly labeled the dated round-2 measurement, not a round-11
run), tracked `registry/history/latest.tsv` and `registry/history/DELTA.md`,
`corpus/lessons/round-2.md`, and commits `83bee7f`/`1e41928`. It states what is *not*
retained: the round-2 dated snapshots `20260929T043044Z`/`20260929T043052Z` exist only as
local run evidence (`registry/history/.gitignore`: "Dated snapshots are local run evidence";
glob with gitignore disabled shows only `20261014T124232Z.json` and `20261014T124525Z.json`;
no `.ufo/round-2` directory). The round-2 summary strings are therefore not offered as
retained evidence.

**verified-at:** actual review date taken from `date -u` = `2026-10-20T02:14:44Z` (parent
noted wave timestamps are 2026-10-20 UTC although the round label is 2026-10-19; heading
keeps the steered label, the field states the real date). It separates original observation
dates (2026-09-29 round-2 live; 2026-10-14 tracked drift/rebaseline) from today's metadata
review, and explicitly disclaims live revalidation: no probe, no `snapshot` run, no endpoint
claim refreshed.

**recheck:** three precise, safe commands, no placeholder: the hermetic fixture harness
(`bash tools/test-snapshot.sh`, loopback fixtures only), the authorized live re-sample
(`bash tools/kama-probe.sh snapshot`, with `--history DIR` for an isolated root; touches only
the registry's declared loopback consumers), and anchor re-derivation with the repo's own
`nl -ba … | sed -n` convention over the exact ranges verified today.

## Anchors re-derived read-only 2026-10-20 (content observed)

- `tools/kama-probe.sh:110-111` — verdict vocabulary and `exit: 0 reconciled | 2 drift | 1 probe error`
- `tools/kama-probe.sh:157-159` — `snapshot refuses --port: a matrix probe has no registry baseline to persist`
- `tools/kama-probe.sh:608-612` — credential-strip block (`url=${url%%\?*}; url=${url%%\#*}` plus userinfo removal)
- `tools/kama-probe.sh:845-848` — check JSON `exit_codes` emission and `return "$exit_code"`
- `tools/kama-probe.sh:919-943` — `row-added`, per-field transitions, sorted `row-absent` emission
- `tools/kama-probe.sh:959-970` — `served_persist` normalised basenames
- `tools/kama-probe.sh:987-1003` — symlink refusals, `flock -w 10 9`, `diff_baseline` call
- `tools/kama-probe.sh:1040-1054` — tmp+mv atomic `latest.tsv` replacement

## Exact retained evidence quotes

- `registry/history/DELTA.md:1` — "- 2026-09-29T04:30:44Z baseline recorded (11 rows); transitions begin with the next snapshot"
- `registry/history/latest.tsv:1` — "#@snapshot_id 20261014T124232Z # columns: id verdict reason served_model port file_match"
- `registry/history/.gitignore:1` — "# Dated snapshots are local run evidence; the normalized baseline and ledger are tracked."
- `git log` — `83bee7f 2026-09-29 round-2`; `1e41928 2026-10-19 round-10: … 50 stale anchors re-anchored by appended corrections; KQ6-KQ10`

## Limits and risks

- The quoted round-2 measurement strings cannot be independently re-verified from retained
  bytes: their dated JSON is untracked and absent. Only the baseline timestamp and 11-row
  count are corroborated (`DELTA.md:1`); the supplement says so.
- Body anchors at lines 15/21/36/51/53/55 remain as dated history with their round-10
  corrections intact (KQ7); the supplement adds the current set without rewriting them.
- `bash tools/test-snapshot.sh` was **not** executed (parent owns post-integration gates) and
  no endpoint probe was run; `verified-at` claims no revalidation.
- Commands executed: `date -u`, `git log --format`, `nl -ba … | sed -n`, `head -c | sha256sum`,
  `wc -c`, `grep -c`, `git status --porcelain`. No network or host-probing commands.
- Tool installs/upgrades: none — no necessity arose.

## Blocker

None.
