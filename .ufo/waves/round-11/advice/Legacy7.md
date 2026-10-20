# Legacy7 — round 11 provenance supplement, `corpus/knowledge/listener-census.md`

Seat: Legacy7 (leaf executor). Target (sole owned file): `corpus/knowledge/listener-census.md`.
Report output: this file. No delegation, no commits, no builds/lints/tests/formatters, no network or
host/service commands executed. No tool installs or upgrades were needed (nothing installed this seat).

## What changed

Appended — never prepended, never rewriting prior lines — at end of file:

```
## Provenance supplement — round 11 (2026-10-19)
source: retained historical evidence — this file's own measurement header (live on-box probes, 2026-09-28 ~22:47–22:52 -0300, host `plazir27`) and its §5 command ledger C1–C19 plus the §7.1 same-session re-check, retained as committed bytes at `c6199a2542440db77d69918599e5a378ee116337` (2026-09-28, round-1) and `ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21` (2026-10-14, round-3 re-census); corroborating retained records: `LOG.md:72` (`KamaScoutListeners` 23-listener census, landed by that peer before it died) and `LOG.md:164-167` (a later refresh observed 20 listeners — ephemeral socket churn); no host path, config, or endpoint was re-opened for this supplement, so the source is the retained record, not current host state
verified-at: 2026-10-20 (actual UTC review date; the heading's 2026-10-19 is the steered round label) — metadata-only review: the retained bytes were re-read in-repo and hash-matched to the round-11 baseline (`sha256 9366a759cbaecb9d8227cb50ce4082e507d824aa6f9b6c3b73b31e5836504996`, 34489 bytes); the observations themselves are historical — the census was measured live 2026-09-28 ~22:47–22:52 -0300 on host `plazir27` with a same-session §7.1 re-check, and the last in-file re-measurements are dated 2026-10-14; no live revalidation, no listener/endpoint probe, and no host config or environment read in this review
recheck: on-authorization — round 11's declared scope forbids endpoint census (KQ10; round-10 mistake 25), so revalidation requires a future L1-declared census scope; then re-derive with `bash tools/kama-probe.sh listeners` (repo tool, loopback `ss -ltnpH`, unprivileged, no drift gate) and, for the 5 ownerless §0 rows, the privileged §7 one-liner `sudo -n ss -ltnp | awk '$4 ~ /127\.0\.0\.1|0\.0\.0\.0/ {print $4, $NF}'`; compare `stable` rows by bind addr:port and `churn` rows by owner (`omp` pid ↔ `/proc/<pid>/cmdline`), never by port number
```

The three field lines sit at column zero (verified by raw read of lines 382–387). Section adds 1971 bytes.

## Retained-bytes evidence (measured, not asserted)

| Measurement | Command | Result |
|---|---|---|
| Baseline before edit | `sha256sum corpus/knowledge/listener-census.md` | `9366a759cbaecb9d8227cb50ce4082e507d824aa6f9b6c3b73b31e5836504996`, 34489 bytes — byte-identical to `.ufo/waves/round-11/legacy-baseline.json` |
| Original prefix after edit | `dd if=corpus/knowledge/listener-census.md bs=1 count=34489 status=none \| sha256sum` | `9366a759cbaecb9d8227cb50ce4082e507d824aa6f9b6c3b73b31e5836504996` — exact match; every original byte retained in place as the file prefix |
| New totals | `wc -c` / `wc -l` | 36460 bytes / 387 newline-terminated lines (was 34489 / 381 `wc -l`; the reader counted 382 display lines because the original last line had no trailing newline) |
| New full-file hash | `sha256sum` | `9e4a36c917af8f4aede1297c6d179ee250026eb91090b69eed647fae21e09491` |
| Original final line text | raw read, line 382 | `stale port outnumber connections to the real model ~5:1 in TIME-WAIT churn (62:12, then 26:6).**` — unchanged text; append added only the terminating `\n` after that last byte (same append-exception class LOG.md:523 already records for three files that "lacked a final newline") |
| Repo history of the file | `git log --follow --format='%H %ad %s' --date=short -- corpus/knowledge/listener-census.md` | `c6199a2542440db77d69918599e5a378ee116337` 2026-09-28 "round-1: operability axis — runnable endpoint-identity gate for local model serving"; `ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21` 2026-10-14 "round-3: re-census — derived --ufo-src, registry cut to live rows, corpus errata" |
| Actual UTC review time | `date -u '+%Y-%m-%dT%H:%M:%SZ'` | `2026-10-20T02:14:42Z` |

## Why each field is honest

- **`source:`** cites only evidence that is retained inside this repo and re-checkable offline: the
  file's own preamble measurement header and §5 command ledger (C1–C19, §7.1), the two commits that
  retain those bytes, and two `LOG.md` records about the census's producer and later count variance.
  No host path, config, endpoint or service was re-opened, so the line cannot smuggle a current-state
  claim — it says explicitly that the source is the retained record, not current host state. It is not
  "none — historical record" because retained evidence genuinely exists (unlike a fabricated receipt,
  every citation here resolves to bytes already in the working tree).
- **`verified-at:`** separates three dates instead of merging them: original live observation
  2026-09-28 ~22:47–22:52 -0300 (`plazir27`, same-session §7.1 re-check), last in-file re-measurements
  2026-10-14, and the actual review date 2026-10-20 (from `date -u`, per parent's UTC erratum). It
  labels the heading's 2026-10-19 as the steered round label rather than inventing an Oct-19 access,
  and states the review was metadata-only — no live revalidation, no probe, no host read. What was
  actually done to earn the line: re-read of retained bytes and sha256 comparison against the
  round-11 baseline value.
- **`recheck:`** is a real path, not a placeholder: `bash tools/kama-probe.sh listeners` exists in-repo
  (`tools/kama-probe.sh:15-16,667,1085` — "listeners   enumerate loopback TCP listeners (ss -ltn) and
  classify each"; implementation loads `ss -ltnpH 2>/dev/null || ss -ltnH`), and the privileged
  §7 one-liner plus owner-based churn comparison come from the file's own freshness contract. It names
  the authorization precondition (KQ10; round-10 mistake 25: out-of-scope census commands) so a future
  seat cannot read it as a standing instruction to probe now. The commands were deliberately not
  executed by this seat.

## Corroborating retained evidence (quotes ≤25 words, with location)

- `LOG.md:72` — "`KamaScoutListeners` 23-listener census (died after landing its artifact — Devin quota)" (producer provenance).
- `LOG.md:165-166` — "the round-1 23-listener census refreshed to 20 due ephemeral socket churn" (count is not an invariant).
- `LOG.md:523` — "`SKILL.md`, `corpus/README.md` and `consumer-registry.md` lacked a final newline, so each append rewrites that last line's bytes (text identical)" (precedent for this file's unterminated last line).
- File preamble — "Measured: 2026-09-28 ~22:47–22:52 -0300, host `plazir27`, live on-box probes."
- File §7.1 — the same-session re-check observed 23 → 24 listeners and two churn-port turnovers.

## Limits, defects, risks

- The heading keeps the steered date `2026-10-19` per parent instruction while `verified-at:` states the
  actual 2026-10-20 UTC review — a deliberate, disclosed discrepancy (parent owns the integration note).
- The supplement is a calibration artifact only: it adds dates/confidence/recheck limits. It asserts no
  freshness refresh, no endpoint health, and no runtime recovery (aligned with `.ufo/waves/round-11/claims.json`
  C1: "metadata review is not present endpoint revalidation or runtime recovery").
- `kama-probe.sh listeners` is unprivileged and cannot attribute the 5 ownerless rows of §0; the
  recheck line therefore pairs it with the privileged §7 one-liner. Both commands remain unexecuted here.
- Churn rows are not reproducible by port; the recheck line states the owner-based comparison rule.
  Count variance (23 → 20 in LOG, → 24 in §7.1) is retained history, not a contradiction.
- No endpoint, host config, environment, or credential read; no network command. Commands used were
  repo-local only: `sha256sum`, `wc`, `dd|sha256sum` (prefix proof), `git log --follow`, `git status`,
  `date -u`, plus read/grep/glob over repo files.
