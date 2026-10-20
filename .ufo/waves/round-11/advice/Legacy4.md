# Legacy4 — C1 provenance supplement for `corpus/knowledge/drift-timeline.md`

Seat: `Legacy4` (leaf executor, kama round 11). Owned file: `corpus/knowledge/drift-timeline.md` only.
No delegation, no commits, no builds/tests/formatters, no host-config/env reads, no endpoint census, no service changes.
Tool installs/upgrades: **none** (no necessity).

## Change

Appended at end of file (nothing prepended, rewritten, or reordered):

```
## Provenance supplement — round 11 (2026-10-19)
<blank>
source: …
verified-at: …
recheck: …
```

Three field lines at column zero, one blank line after the heading, appended after the existing round-10
correction block. The heading retains the steered round date `2026-10-19` per parent steer; the actual
review date is carried inside `verified-at`.

## Byte-preservation evidence (measured, not asserted)

- Baseline (`.ufo/waves/round-11/legacy-baseline.json`): `sha256 a161615286428054f834b0d9e9be9261ce0a52a631cd8fe11bde2d277d214df7`, `bytes 7428`, `missing: source, verified-at, recheck`.
- After the append: `head -c 7428 corpus/knowledge/drift-timeline.md | sha256sum` → `a161615286428054f834b0d9e9be9261ce0a52a631cd8fe11bde2d277d214df7  -` — **identical prefix hash**, so all 7428 original bytes (and the original trailing `\n`) are retained exactly.
- `wc -c` → `9818` (7428 + 2390 appended); `wc -l` → `34`. Fields present exactly once each, at column zero (`grep -n '^(## Provenance supplement|source:|verified-at:|recheck:)'` → lines 30, 32, 33, 34).

## Why each field is honest

**`source:` — no live source claimed, every pointer opened by me in this session.**
It says "retained historical record only (no live source)" and cites only in-repo copies I actually read:
`LOG.md:71-74` (round-1 peer ledger: "KamaRevengerTimeline drift timeline"), `LOG.md:159-163` (round 2: "34113 still serves the expected llama.cpp model"), `LOG.md:203-255` (round 3: "ports 34113 and 8080 both refuse connections" plus unit/backups gone), `registry/history/DELTA.md:14-22` (tracked snapshot `2026-10-14T12:42:32Z`: "systemd-qwen-coder row-absent (was verdict=MODEL_OK port=34113)"), `corpus/knowledge/consumer-registry.md:100,120-123` ("epoch 1788033391 = 2026-08-29 19:56 UTC … the fossil origin of the stale pin (L1-F9)"; archival rows 31–34), and `.ufo/waves/round-11/legacy-baseline.json`. All quotes are ≤25 words and were copied from the reads above. The line explicitly dates the record: original observations 2026-08-20 → 2026-09-28 (last row 2026-09-28), **distinct from** the 2026-10-20 UTC metadata review.

**`verified-at:` — actual review date, original dates separated, no live revalidation.**
It states `2026-10-20 02:14 UTC`, the real host-clock value read with `date -u` during this wave (parent steer: host wave timestamps are 2026-10-20 UTC while the steered round label is 2026-10-19). It distinguishes the observation window (2026-08-20 → 2026-09-28), the in-file round-10 correction date (2026-10-19), and today's metadata review; and it explicitly denies re-reading any endpoint, listener, systemd unit, docker container, or backup file. No row of the table is restated as current state, so nothing here can be read as endpoint-health evidence.

**`recheck:` — not a placeholder; states the limit and the current authorized surface.**
Per parent steer it does **not** recommend replaying the stale timeline shell/config bodies or the deleted janitor/backup paths. It states the historical table is not rerunnable (every per-row command targets a host artifact recorded gone, `LOG.md:245-255`) and names the current authorized read-only revalidation surface: `bash tools/kama-probe.sh check --json` from the repo root (the lane's own probe, evaluating the surviving `registry/endpoint-consumers.tsv` rows) plus `bash tools/kama-probe.sh snapshot` for invocation-to-invocation drift, with the expected reading `DEAD`/`connection-refused` documented from `registry/history/latest.tsv:2-4`. A reappearing host artifact is characterized as restored state to inspect read-only under operator authorization — not a re-run of these rows. No command was executed for this supplement (no endpoint census is permitted in this wave).

## Calibration framing (parent erratum, integration-side)

Per the erratum, C1's final axis is **calibration** (provenance dates / confidence / recheck limits), not freshness refresh. This supplement supplies exactly those three: dated evidence with the review date separated from observation dates; an explicit confidence boundary (metadata review only, zero live revalidation, no current-state claim); and a bounded recheck path with the historical table declared non-rerunnable. No content was rewritten in response to the erratum; the appended text already carried this framing.

## Limits / defects

- The host artifacts named in rows 7–20 were **not** re-opened (contract forbids host config reads); their state is cited only as recorded in retained repo evidence (`LOG.md:245-255`).
- `~/.config/llama/qwen-coder-godspeed.jinja` (row 11) and the Jitsi container (row 15) are not covered by the `LOG.md:245-255` deletion list; the supplement therefore makes no claim about their present existence, and the recheck line no longer names them.
- The round-10 correction block (line 26–28) and its `consumer-registry.md:62-65` anchor were left byte-identical and were not re-validated (out of this slice).
- Rows 7–20 remain historical observations; this seat makes no endpoint-health, listener, or served-model claim.

## Commands actually run

Repo-local reads (`read`/`grep`/`glob` on `corpus/`, `LOG.md`, `registry/history/`, `.ufo/waves/round-11/`),
one clock read `date -u` → `2026-10-20 02:14:36 UTC`, one byte check
`head -c 7428 … | sha256sum` + `wc -c`/`wc -l`. No network, no host-config read, no probe execution.
