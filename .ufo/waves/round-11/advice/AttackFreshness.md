# AttackFreshness — C1 falsification review (round 11)

Seat: critic (parent-dispatched author advisor, NOT an outside non-author verifier).
Review time: `date -u` → `2026-10-20T02:14:33Z` (host local −0300 is still 2026-10-19). Read-only; no network or host-config reads, no runtime probes, no checks run. No tools installed or updated.

Axes: **freshness** (the C1 claim), **calibration** (honest dates and limits), **operability** (recheck commands stay executable and in-province).

## Evidence base (observed)

- The baseline `.ufo/waves/round-11/legacy-baseline.json` lists 9 files × 3 missing fields = 27. For all 9 files, the working tree and `git show HEAD:<path>` match the baseline sha256 on its first 12 hex characters. HEAD is `2f7303c`. At review time, all 9 files had 0 column-zero `source:|verified-at:|recheck:` lines, and a case-insensitive search found no indented variants either.
- Fence lines (```` ``` ````) per file: 2, 10, 0, 0, 8, 0, 8, 8, 2. Every count is even, so the fences are balanced.
- Last byte of each file: `\n` for 8 files. `listener-census.md` ends in `*` with **no trailing newline**. Its tail is `…(62:12, then 26:6).**`.
- Read in full: `served-model-identity.md` (37 lines) and `drift-timeline.md` (28 lines).

## Counterexamples

### F1 — The count measures metadata, not freshness (premature saturation)
If all 9 files got `source: none — historical record`, a review-date `verified-at:` and `recheck: unavailable`, then 27 → 0 would pass. No content would be any fresher. Freshness is already 8 from round 10, and that score rested on resolving anchors (`SCORECARD.md:211`, `rows=50 resolved=48 terminal=2 unresolved=0`).
- **Impacted axes:** freshness, calibration.
- **Judge tradeoff, not a fixable defect:** name the claim "provenance completeness 27 → 0". Do not present it as content revalidation. Any freshness score change must say no observation was refreshed.

### F2 — The denominator silently shrank from 18 to 9
`SCORECARD.md:203` says: "provenance for the 18 pre-round-10 entries, appended, never invented". Round 11 measures only the 9 knowledge files. I counted the 9 pre-round-10 lessons in `corpus/lessons/` (all except `round-10.md` and the immutable `round-10-verifier-spotcheck.md`). Each has 0 column-zero fields, so 27 fields there are still missing.
- **Impacted axes:** freshness, calibration.
- **Fix:** state the denominator as "9 knowledge entries". Record the 9 lessons as out of scope, still 27 missing, so it is not read as "18 → 0".

### F3 — Date inflation through a single `verified-at` date
- **`served-model-identity.md`** has no date anywhere. A grep for `2026-|round 1|date` found nothing. The grounded date comes from outside the file:
  - `lessons/round-1.md:3-4`: "Every rule below is grounded in a command run on 2026-09-28".
  - Commit `c6199a2` is `2026-09-28 23:15:05 -0300`, which is 2026-09-29T02:15Z.
  - So the observation is "2026-09-28 local, no later than commit c6199a2". The commit date alone is an upper bound, not the sample time.
- **`drift-timeline.md`**:
  - The latest observation is `2026-09-28` (rows at lines 17–20).
  - Its only later date is the round-10 correction at line 28: "wc -l ~/.config/opencode/opencode.json => 5 … shape-only, no body read". That checked one anchor, not the table.
  - A bare `verified-at: 2026-10-19` or `2026-10-20` would make 2026-09 observations look current.
- **Fix:** `verified-at` has to carry two dates:
  - the original observation date(s), with timezone (−0300 vs UTC);
  - the actual review date `2026-10-20` UTC, explicitly "metadata review, no live revalidation".
  - The heading may keep the steered date `2026-10-19` (parent IRC).

### F4 — A stale recheck would revive retired authority (KQ3)
- **`served-model-identity.md:10,27`** is all `curl … http://127.0.0.1:34113/…`. Port 34113's unit has been deleted: `PROVINCE.md:10` ("is deleted; row-absent since snapshot `20261014T124232Z`"). A recheck that says "re-run the file's commands" presents a deleted unit as current executable authority. KQ3 rejects that.
  - **Fix:** recheck = registered surface `bash tools/kama-probe.sh check`, under operator authorization. Note that the original curl commands are historical and not repeatable against the retired port.
- **`drift-timeline.md`** evidence commands read `~/.config` backups and the deleted `janitor.md` (`PROVINCE.md:11` "file deleted"), and run `docker inspect`. A recheck of "re-run the table" would mean host-config reads plus a target that no longer exists.
  - **Fix:** mark the rows historical and not re-runnable. Name only the repo-local re-anchor (`corpus/knowledge/consumer-registry.md:62-65`, per line 28) or the registry `snapshot` surface.
- **Impacted axes:** operability, calibration.

### F5 — The no-newline append trap in `listener-census.md`
The file lacks a final `\n`. A naive append would glue `## Provenance supplement…` onto the closing `**` line. The heading would then not be at column zero, and the prefix sha check would still pass.
- **Impacted axis:** freshness (whether the section is well-formed).
- **Fix:** the appender emits `\n\n` first. The checker requires the supplement heading at column zero, located after the baseline byte length.

### F6 — Field location gaming
- **Field placement:** a checker that counts fields anywhere in the file would accept fields inside a fenced block, or in the original region (impossible without breaking the prefix, but a placement bug the checker could still miss).
  - **Fix:** count fields only in the suffix (bytes after baseline `bytes`), exactly once each, at column zero, outside fences.
- **Mutable baseline:** the baseline is an untracked, mutable JSON in `.ufo/waves/` (`git status`: `?? .ufo/waves/`). Editing its sha256 or byte count to match a mutated file would defeat the prefix check. That makes the baseline a duplicate authority.
  - **Fix:** record the source commit `2f7303c` in the baseline, or have the checker cross-check `git show 2f7303c:<path>`.

### F7 — Source/index mismatch for `served-model-identity.md` (stale prose, outside C1)
- `corpus/README.md:32` describes it as "served-model reconciliation (`/v1/models` vs `--alias` vs configured id) + the minimal proof procedure".
- The file is a 37-line fragment unchanged since `c6199a2`. It opens with two blank lines and `### Exact readiness-field probes`, and has only `/health`, `/props`, `/slots`, `/metrics` outputs.
- The supplement's `source:` must not claim the file holds identity reconciliation. Cite `lessons/round-1.md:3-4` and the F-rows in `endpoint-identity.md` instead.
- The README line needs an appended supersession; the parent owns that.
- Relevant to C2: this gap is why the crosswalk entry is needed, but it does not by itself show the crosswalk is honest.

## Minimal negative controls (named, not executed)

Run each on an isolated copy (`cp -a` to a tmp root, then `--root <tmp>`), never on the lane tree.

| ID | Mutation | Expected |
|---|---|---|
| NC1 missing-field | Delete the single `recheck:` line from one file's supplement | `missing_fields=1`, `missing_files=1`, exit 1 |
| NC2 altered-original | Change one byte inside the baseline prefix, e.g. `drift-timeline.md` line 1 `timeline` → `Timeline` | `prefix_violations=1`, exit 1 |

Optional controls, only if cheap:

| ID | Mutation | Expected |
|---|---|---|
| NC3 | Duplicate the `source:` line | exit 1 (exactly-once rule) |
| NC4 | Indent one field (` source:`) | counts as missing |
| NC5 | Tamper the baseline sha256 to match the mutated file from NC2 | Must still fail if anchored to `2f7303c`. Otherwise record it as a known limit. |

## Defects / limits of this review
- I read only two legacy files in full. F4 and F5 for the other files rest on PROVINCE/README pointers and byte checks.
- I did not inspect the host to confirm which `~/.config` backups still exist (out of contract). F4 therefore says "not re-runnable without host-config reads", not "deleted", except where `PROVINCE.md:11` records the deletion.
- When I listed `.ufo/waves/round-11/`, no `measure.py` existed yet, so I could not see whether F5 and F6 are handled.

## Addendum — axis erratum (Main IRC, after review; original text above retained)

Main reassigned the C1 axis to **calibration** (provenance dates, confidence and recheck limits; `../shokunin.conf:52`, per `.ufo/waves/round-11/claims.json`). That reassignment answers the F1 tradeoff: a 27 → 0 provenance count is not a freshness refresh. F2–F7 and NC1/NC2 stand unchanged and now bear on calibration: honest denominators (F2), dual observation/review dates (F3), non-retired recheck surfaces (F4), and measurement integrity (F5/F6). I did not verify the reassignment or read `shokunin.conf` myself.
