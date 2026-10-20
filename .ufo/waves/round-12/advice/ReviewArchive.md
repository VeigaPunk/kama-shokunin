# Round 12 — ReviewArchive: D5 disclaimer placement for `.ufo/round-10/SEAT-PROTOCOL.md`

Scope: read-only review of D5 (`corpus/lessons/round-11-verifier-spotcheck.md:226-230`) and the artifact. No edits made. Tools installed/updated: none.

## Current state (observed 2026-10-20, HEAD 79fa257)

- File: 56 lines, 4413 bytes, sha256 `e9fbaa02b4329ec415ac73eb0a6a5eaf4c91ae17f2889cc96232fb51f5d49c0a`, last byte `\n`. Unchanged from the hash recorded in `advice/AttackAdmission.md` line 75.
- Tracked: `git ls-files` lists it; `git log` shows its introduction in `3285cdf round-11: calibrate historical provenance...`; `git status --short -- .ufo/round-10/` is empty. The "untracked" findings in `verification/ReportConformance.md` R23/D2 and `ReviewContract.md` K4 are stale as of this HEAD.
- No archival disclaimer exists. `grep -n -i "archiv|historical|nonexecut|not current|disclaim"` matches only line 24 and line 26, both inside the classification rules for citations, not status prose.
- Line 1 is `# Round 10 — seat protocol (L1-issued, binding on all 64 seats)`. Line 13 `## Hard rules (every seat)` and line 7-9 class counts (20/12/32 seats) are present-tense instructions.
- D5 wording is `opens binding on all 64 seats without an in-file archival disclaimer`. Status evidence for the disclaimer text: `.ufo/round-10/plan.json` and `LOG.md:553-555` ("inherited undelivered planning artifacts ... old provider/route instructions are not executed"), `waves/round-11/inherited-state.json` disposition, `corpus/lessons/round-11.md:87`.

## Assessment of placement

1. **Append at end (the literal spec for executor D5): does not satisfy "unmistakable."** A reader opens at line 1 and reads "binding on all 64 seats" and "Hard rules (every seat)" before reaching any tail text. A tail block cannot "override opening binding wording" by position. It is append-only compliant but leaves title/body binding unchanged in the first screen. Adequate only as a secondary footer.

2. **Banner above line 1 (recommended).** Adds a block before the existing first line; no existing line is modified, so the original 56 lines survive as a contiguous suffix byte-for-byte. This is not strictly "append," so L1 must explicitly authorize it as the D5 exception; the spec's "preserve original prefix" is satisfied at byte level, not offset-0 level. Git keeps the pre-edit file at `3285cdf`.

3. **Sibling file / README only.** Does not meet D5's in-file requirement. Rejected.

4. **Editing line 1 or the body.** Violates append-only and the round-12 rule "do not edit immutable prior round evidence except appending explicit historical disclaimers/corrections." Rejected.

## Advice to owner (content of the banner)

The banner must name, not gesture at, the replay surfaces:
- Status: historical, undelivered, never executed; not current authorization; supersedes line 1 "binding" wording and all "L1-issued" authority from round 10.
- Disabled instructions by name: provider/route and model choice (plan.json, not this file, but any replay must not reuse it); `$UFO_SRC`, `~/Projects/ufo-fsd-alpha`, `~/Projects/origin-work/ufo-fsd-alpha` path probing (line 23); loopback runtime endpoints and "class as runtime-surface" (line 23); read-only inspection of `~/.config`, `~/.omp`, systemd units (line 5); provider/rate-limit telemetry requirements (lines 16, 52); seat-class counts and `.ufo/round-10/{gates,audit,tps-probes}` output directories (lines 7-9).
- Pointer to the current governing protocol (round-11 or later) rather than a successor design.

A short footer restating status is acceptable as a duplicate; the banner is the required one.

## Checks for L1 after the owner edit (not run here)

- `git diff 3285cdf -- .ufo/round-10/SEAT-PROTOCOL.md` must show only `+` lines and zero `-` lines.
- `git show 3285cdf:.ufo/round-10/SEAT-PROTOCOL.md | sha256sum` must equal `e9fbaa02…49c0a`.
- `tail -n 56 .ufo/round-10/SEAT-PROTOCOL.md | sha256sum` must equal the same hash (original body intact as suffix).
- `head -n <banner-length>` must show the disclaimer before the `# Round 10` line.
- `grep -n "binding on all 64" .ufo/round-10/SEAT-PROTOCOL.md` should match only inside the banner's quoted/struck text.

## Residual risk

- Owner identity for the D5 edit is ambiguous from the dispatch files (executor spec "Own ONLY ..."); confirm with L1 before writing so no sibling edits the same file.
- The executor's spec says "append"; the owner may apply the literal append (option 1) unless L1 approves option 2 explicitly.
- Any edit makes the file dirty relative to `3285cdf`; it needs a pathspec-limited commit by L1 to keep the round-11 disclaimer chain intact.
