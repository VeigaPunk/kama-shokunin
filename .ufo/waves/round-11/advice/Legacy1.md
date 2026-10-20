# Legacy1 — round-11 provenance supplement: corpus/knowledge/alias-endpoint-normalization.md

Seat Legacy1 (executor, leaf). Lane kama-shokunin. Wave kama-round-11. Steered round label 2026-10-19; actual UTC review date **2026-10-20** (`date -u` → `2026-10-20T02:14:56Z`; parent erratum: the wave executed 2026-10-20 UTC, steered label retained only in the heading). Scope: the single assigned file. No network/host commands executed; only in-repo reads, `git` read-only commands, `date -u`, and the seat's Python `eval`.

## Files changed

| file | change |
|---|---|
| `corpus/knowledge/alias-endpoint-normalization.md` | appended `## Provenance supplement — round 11 (2026-10-19)` (+3323 bytes; the original 7595 bytes are preserved byte-for-byte as the file prefix) |
| `.ufo/waves/round-11/advice/Legacy1.md` | this report |

Nothing else written. No commit, push, test, lint, build or formatter. Zero subagent spawns. No host config/env/credential read, no endpoint census, no service change.

## Behavior (what changed)

Appended only, at end of file: heading `## Provenance supplement — round 11 (2026-10-19)`, blank line, then `source:`, `verified-at:`, `recheck:` at column zero, then a closing note (same phrasing convention as sibling supplements at `corpus/knowledge/cross-lane-scope.md:87` and `corpus/knowledge/free-tier-provider-limits.md:77`). Nothing prepended, no existing line rewritten, no sibling file touched.

## Appended fields (verbatim)

```text
source: retained in-repo history only — the underlying host surface `~/.omp/agent/config.yml:21-44` is not retained in this repository and was not re-read in round 11; retained evidence: this file's own frozen 23-row alias table (host config read 2026-09-28; the loopback question re-measured 2026-10-14 at the relocated tree, same empty result, `/tmp/fleet-override.yml` gone), preserved byte-for-byte by this append; `LOG.md:77-80` (round-1 peer ledger: `KamaDistillerAliases` alias→endpoint normalization — no alias resolves to loopback; the `m_flash` route was caught stale); `corpus/lessons/round-1.md:3-4,70-72` and `corpus/lessons/round-1-citations.md:17,28` (F11 re-derivation: live line 24 is `charm-hyper/deepseek-v4.1-flash:max`); `corpus/lessons/round-4-recensus.md:79` (round-10 A48 re-anchor to this file's line 11); appended corrections A16–A18 with ledger `.ufo/round-10/audit/stale-anchors.tsv:16-18` (2026-10-19); file history commits `c6199a2` (round 1, 2026-09-28, table already 23 rows), `ea72c3e` (round 3 errata, 2026-10-14 — relocated the recorded grep paths from `~/Projects/origin-work/ufo-fsd-alpha` to `~/Projects/ufo-fsd-alpha`, dropped "today" from the answer sentence, added the errata line), `1e41928` (round 10, 2026-10-19 — appended A16–A18 only).
verified-at: 2026-10-20T02:14Z — actual review date (the round-11 wave executed 2026-10-20 UTC; this heading retains the steered round label date 2026-10-19). Metadata review only: this seat re-read this file's bytes and its in-repo pointers and confirmed the pre-append baseline sha256 `a441829c75fd6c7780c44411cf93f79ee863d7bebdbe8804229b93dabf08ff93` (7595 bytes, matching `.ufo/waves/round-11/legacy-baseline.json`); the host config was not re-read and no endpoint, listener, probe or dispatch surface was contacted, so no live revalidation is claimed and no observation here is refreshed. Original observation dates: 2026-09-28 (round-1 live alias census and loopback grep), 2026-10-14 (errata re-measure), 2026-10-19 (round-10 stale-anchor corrections A16–A18).
recheck: on the next authorized host-config read or alias-table correction round (metadata-only; no endpoint probe) — re-derive the table with `nl -ba ~/.omp/agent/config.yml | sed -n '21,44p'`; rerun the loopback grep exactly as recorded in §Loopback answer above: `grep -nE "(baseURL|baseUrl|endpoint):[[:space:]]*https?://(127\\.0\\.0\\.1|localhost)(:|/)" ~/.omp/agent/config.yml /tmp/fleet-override.yml ~/Projects/ufo-fsd-alpha/.omp/config.yml ~/Projects/ufo-fsd-alpha/config/*.yml 2>/dev/null` — expect no matching lines (grep exit 1; a match fails freshness review); re-confirm the three round-10 terminals: `test -e /tmp/fleet-override.yml` (expected missing — dead surface unless recreated), `wc -l ~/Projects/ufo-fsd-alpha/config/l1-max-context.yml` (was 20; a longer file re-opens A18's range), `nl -ba ../MISSION.md | sed -n '11,15p'` (fleet-root MISSION.md route semantics). Local serving readiness stays with `bash tools/kama-probe.sh check` — a separate registry claim, not a revalidation of this table.
```

Closing note: `*[provenance supplement appended 2026-10-20 (round-11 wave; steered label 2026-10-19): no byte above is rewritten and no observation above is refreshed by this supplement.]*`

## Exact retained evidence

- Baseline (`.ufo/waves/round-11/legacy-baseline.json`): `sha256 a441829c75fd6c7780c44411cf93f79ee863d7bebdbe8804229b93dabf08ff93`, 7595 bytes. `git show HEAD:corpus/knowledge/alias-endpoint-normalization.md | sha256sum` → same hash: the committed HEAD blob equals the baseline, and the working tree carries only the append (`git status --porcelain` → ` M corpus/knowledge/alias-endpoint-normalization.md`).
- Prefix preservation: `hashlib.sha256(b[:7595]).hexdigest() == baseline` → **True** (seat `eval`, 2026-10-20). Heading located at byte offset 7596: the baseline prefix is bytes 0–7594 (ending in the original final newline, byte 7594), followed by one added blank line (byte 7595), then `##` at 7596; file ends with `\n`.
- Post-append: `sha256 360395670fa2191b2b6920bd6aae681b7ef788915732086c32268c039c4a1fb1`, 10918 bytes (delta +3323).
- Field counts: `^source:`, `^verified-at:`, `^recheck:` each match exactly **1** line at column zero (`re.M`); no pre-existing field lines existed (baseline "missing" list for this file: all three).
- Reproduce: `python3 -c "import hashlib;b=open('corpus/knowledge/alias-endpoint-normalization.md','rb').read();print(hashlib.sha256(b[:7595]).hexdigest()=='a441829c75fd6c7780c44411cf93f79ee863d7bebdbe8804229b93dabf08ff93', len(b))"` → `True 10918`.
- Historical evidence re-opened read-only this round: `LOG.md:77-80`; `corpus/lessons/round-1.md:3-4,70-72`; `corpus/lessons/round-1-citations.md:17,28`; `corpus/lessons/round-4-recensus.md:79`; `corpus/lessons/round-10.md` (A16–A18 provenance); `.ufo/round-10/audit/stale-anchors.tsv:16-18`; `git log --follow -- corpus/knowledge/alias-endpoint-normalization.md` → `c6199a2` (2026-09-28), `ea72c3e` (2026-10-14), `1e41928` (2026-10-19); round-3 and round-10 `git diff` output (full text at `artifact://205`). Table row count checked at each revision: 23 rows at `c6199a2`, 23 at `ea72c3e`, 23 now (`grep -c '^| \`m_'` on `git show <rev>:<path>`).
- Corpus cross-refs confirming the file's position (read, not edited): `corpus/knowledge/consumer-registry.md:177-181`; `corpus/knowledge/listener-census.md:10-11,90-91`.

## Why each field is honest

- **`source:`** cites only retained in-repo evidence that was actually re-opened this round (LOG peer ledger, dated lessons, the round-10 ledger rows, commit hashes/diffs) plus the file's own frozen table. It states up front that the underlying host surface `~/.omp/agent/config.yml:21-44` is not retained in this repository and was not re-read, so no host-content claim is renewed. The commit characterizations are measured, not guessed: round 3 rewrote the recorded grep paths (`origin-work` → relocated tree), dropped "today" and added the errata line; round 10 only appended A16–A18.
- **`verified-at:`** states the actual review date (2026-10-20T02:14Z from `date -u`) and explicitly separates it from the steered heading date (2026-10-19); scopes today's work to metadata review (this file's bytes, in-repo pointers, baseline hash); names the three original observation dates (2026-09-28, 2026-10-14, 2026-10-19); and states that the host config was not re-read and no endpoint/listener/probe/dispatch surface was contacted — so it cannot and does not claim live revalidation or refreshed observations.
- **`recheck:`** gives a safe, precise, future-authorized path: the trigger (next authorized host-config read or alias-table correction round), the exact re-derivation command (`nl -ba ~/.omp/agent/config.yml | sed -n '21,44p'`), the exact recorded loopback grep with its file list and expected outcome (no matches, exit 1), and the three round-10 terminal re-checks with expected values (`/tmp/fleet-override.yml` missing; `l1-max-context.yml` 20 lines; `../MISSION.md:11-15`). It explicitly scopes local readiness to `tools/kama-probe.sh check` as a different claim. No placeholder; the only surface that needs operator authorization is named as such.

## Axis note (parent integration erratum)

Per the parent erratum, C1's axis is **calibration** (provenance dates/confidence/recheck limits), not a freshness refresh. The supplement records date provenance and recheck limits only: it claims no endpoint health, no runtime integration and no outside verification, and it does not raise an operability or freshness verdict.

## Risks, defects, limits

- The alias table's row values remain frozen history: they cannot be re-derived this round because `~/.omp/agent/config.yml` is a host surface (no host config reads; KQ5). A future correction round must re-read it before restating any row; the recheck line says so.
- The file's recorded loopback grep's file list is itself the round-3 (2026-10-14) revision (paths relocated), while the paragraph label stays `2026-09-28`; the source line records this so the label is not misread as covering the current path list.
- Host pins named inside the file (`~/.local/bin/the-janitor:16-19`, `~/.config/opencode/agents/distiller.md:5-8`) were not re-read this round (KQ3: historical).
- KQ compliance: KQ3 (append-only; old bytes preserved — proven by prefix hash), KQ5 (no config bodies, environment values or secrets; shape/pointer evidence only), KQ7 (appended at end of file; no mid-file insertion). KQ6/KQ8 not implicated (no vendor-doc claim, no blocked-command verdict).

## Installs

None — no tool was installed or updated by this seat.

## Not done

No endpoint/listener/probe run, no dispatch, no host config/env read, no commit/push, no sibling file touched, no build/lint/test/formatter.
