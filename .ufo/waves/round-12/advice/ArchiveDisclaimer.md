# Round 12 — ArchiveDisclaimer: D5 banner for `.ufo/round-10/SEAT-PROTOCOL.md`

Scope: the single assigned file plus this report. No other file written, no commit, no build/test/lint/smoke run, no endpoint call, no host/config inspection. Tools installed or updated: none.

## What changed

Prepended an archival override banner (now lines 1–31) to `.ufo/round-10/SEAT-PROTOCOL.md`. The original 4413-byte round-10 file is retained byte-for-byte as the file's contiguous suffix (now lines 32–87), separated by a `---` rule at line 30. Nothing in the original was edited, deleted, or reordered.

Placement deviates from the ticket's literal `append` / `preserve original prefix` wording and follows the L1 override issued during the wave: "Authorize PREPENDED unmistakable historical/nonexecuted banner ... preserve all original bytes as suffix (not prefix)". The banner is therefore the first screen; the original title remains at line 32, unaltered, and is explicitly named as overridden by the banner's first bold sentence.

## Precise anchors

| Element | Location |
|---|---|
| Banner heading (`# ARCHIVAL — ... HISTORICAL, UNDELIVERED AND NONEXECUTED (round-12 notice, 2026-10-20)`) | line 1, byte 1 |
| Override sentence quoting `(L1-issued, binding on all 64 seats)` | line 3 |
| Per-directive void list | lines 11–22 |
| Sibling-template scope note (rounds 6–9) | line 24 |
| Byte-integrity statement + verification command | line 26 |
| Separator rule | line 30 |
| Original round-10 title (preserved, now overridden) | line 32 |
| Preserved suffix | lines 32–87 = 4413 bytes starting at 1-based byte 4616 (0-based offset 4615), i.e. `tail -c 4413` |

## Voided original directives (original numbering, quoted in banner)

- Original L1 — `(L1-issued, binding on all 64 seats)`; the 64-seat scheme and its 20/12/32 classes.
- Original L13 (hard rule 1) — AUDIT write grant to an assigned file plus `.ufo/round-10/audit/`.
- Original L16 (hard rule 4) — "a failed task ... is a success as a measurement seat".
- Original L17 (hard rule 5) — read-only inspection of `~/.config`, `~/.omp`, systemd units, sibling repos; also the short "never write" list as a boundary.
- Original L22–L23 — `$UFO_SRC` expansion and the `~/Projects/ufo-fsd-alpha`, `~/Projects/origin-work/ufo-fsd-alpha` fallbacks; loopback `runtime-surface` handling; `git cat-file -e` hash bookkeeping.
- Original L27–L29 — the back-dated `*[correction 2026-10-18 (round 10): ...]*` template.
- Original L35 — "run exactly the commands in your scope" and full-stream capture into committed JSON.
- Original L35/L39–L41 — capture targets under `.ufo/round-10/{gates,audit,tps-probes}/`.
- Original L43–L54 — the `SEAT-TELEMETRY` block.
- `plan.json:7` — pinned route/model `opencode-go/deepseek-v4.1-flash-free`; `plan.json:11` — `carried verbatim modulo round number` (no copy-forward/renumber/re-date).

The banner also states the notice covers only this file, and that the same binding-header template is tracked at `.ufo/round-6/SEAT-PROTOCOL.md` through `.ufo/round-9/SEAT-PROTOCOL.md` and needs its own label.

## Retained evidence (commands actually run, with observed output)

| Command | Observed |
|---|---|
| `wc -l -c .ufo/round-10/SEAT-PROTOCOL.md` before edit | `56 4413` |
| `sha256sum .ufo/round-10/SEAT-PROTOCOL.md` before edit | `e9fbaa02b4329ec415ac73eb0a6a5eaf4c91ae17f2889cc96232fb51f5d49c0a` |
| `git log --diff-filter=A --format='%H %ad %s' -- .ufo/round-10/SEAT-PROTOCOL.md` | `3285cdf7a50481694a36c4425cf32c915ab5e5f0 2026-10-20 00:56:15 -0300 round-11: calibrate historical provenance and extend identity coverage` |
| `git rev-parse 3285cdf:.ufo/round-10/SEAT-PROTOCOL.md` | `69659feb5f77a80a7c6020fbe95ba75c3d38ff72` |
| `tail -c 4413 .ufo/round-10/SEAT-PROTOCOL.md \| sha256sum` after edit | `e9fbaa02b4329ec415ac73eb0a6a5eaf4c91ae17f2889cc96232fb51f5d49c0a` |
| `git cat-file blob 69659feb... \| sha256sum` | `e9fbaa02...` (identical; suffix is the tracked blob) |
| `git diff --numstat -- .ufo/round-10/SEAT-PROTOCOL.md` | `31 0` (additions only, zero deletions) |
| `wc -l -c .ufo/round-10/SEAT-PROTOCOL.md` after final edit | `87 9028` |
| `git status --short -- .ufo/round-10/` | ` M .ufo/round-10/SEAT-PROTOCOL.md` only |
| `git diff --check -- .ufo/round-10/SEAT-PROTOCOL.md` | empty, exit 0 |
| `grep -n '^---$\|^# Round 10\|^# ARCHIVAL' ...` | `1:` ARCHIVAL, `30:` `---`, `32:` `# Round 10 ...` |

Status facts cited in the banner, each independently checked: `plan.json:6` `"dispatch_utc": null`; `plan.json:12` loop 1 `blocked-with-data`; `.ufo/round-10/tps-probes/` contains 0 entries; `git ls-files .ufo/round-10` lists 14 paths; the four sibling templates exist, are tracked, and each opens `# Round N — seat protocol (L1-issued, binding on all 64 seats)`.

## Static findings

- The opening-binding defect is now physically preceded by an unmissable H1 whose second sentence quotes the old binding phrase and voids it. A `head`/first-screen read can no longer see the binding title first.
- Original bytes remain recoverable and verifiable in place; no history rewrite and no new copy of the old text.
- The file is now dirty relative to `3285cdf`; L1 owns the pathspec-limited commit.
- `grep -n "binding on all 64"` returns exactly two lines by construction: banner line 3 (quoted override) and preserved original title line 32. This is expected under byte-preservation, not a duplicate authority.

## Not run (unrun is not pass)

- No runner, fidelity CLI, selftest, gate, census, build, lint, formatter, or smoke run.
- No endpoint/loopback call, no `$UFO_SRC` expansion, no host/config/systemd/sibling inspection, no `git cat-file -e` probes of round-10 hashes.
- No edits to `plan.json`, rounds 6–9 templates, verifier files, MANIFEST, fleet repo, `tools/`, `registry/`, corpus, or `LOG.md`.

## Risks and residual

1. Banner visibility assumes a reader reaches the top of the file or greps it; a tool that extracts only the second H1 (`# Round 10 ...`) still sees the old binding phrase in isolation. Mitigation inside write scope is exhausted; a later reader must treat the banner as authoritative per its explicit override sentence.
2. Round-6 through round-9 templates carry the same `binding on all 64 seats` header and remain unlabeled; this notice disclaims only the round-10 file and routes the rest to L1.
3. The banner cites original line numbers (L13/L16/L17/L22–L23/L27–L29/L35/L39–L41/L43–L54). Those numbers refer to the 56-line original, not current file offsets (current offsets are +31). The banner says "Original L…" for every citation.
4. This report is an author advisor artifact, not independent closure.

## Checks for L1

```sh
tail -c 4413 .ufo/round-10/SEAT-PROTOCOL.md | sha256sum          # e9fbaa02…5d49c0a
git cat-file blob 69659feb5f77a80a7c6020fbe95ba75c3d38ff72 | sha256sum
git diff --numstat -- .ufo/round-10/SEAT-PROTOCOL.md             # 31  0
git status --short -- .ufo/round-10/                              # only the assigned file
sed -n '1p;30p;32p' .ufo/round-10/SEAT-PROTOCOL.md                # banner H1, ---, original title
grep -c 'binding on all 64' .ufo/round-10/SEAT-PROTOCOL.md        # 2: override quote + preserved title
```
