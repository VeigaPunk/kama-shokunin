# Round 12 — AttackHistory: append-only and historical-receipt attack

Critic seat, static only. I compared bytes read-only with `git show HEAD:<path>` against the
working tree and inspected `fidelity.py` and `reproduce.py`. I ran no gate, runner, test or
census. The tree was mid-integration when I read it; each finding below states the state it
saw. Tools installed or updated: none.

Axes: **history integrity** (prior bytes stay put), **receipt reproducibility** (round-11
`reproduce.py` stays green), **report non-overwrite**, **D1–D5 conformance**.

## What holds (observed)

| Path | Observation |
|---|---|
| `.ufo/waves/round-11/frozen/before/corpus/SOURCES.md` | Byte-identical to HEAD; sha256 `52665cf2…42fa1`, equal to the pin at `round-11/frozen/expected.json:15` |
| `round-11/frozen/expected.json`, `reproduce.py`, `measure.py`, `legacy-baseline.json`, `acceptance.json` | Byte-identical to HEAD |
| `corpus/lessons/round-11-verifier-spotcheck.md`, `corpus/lessons/round-11.md` | Byte-identical to HEAD; verifier file not touched |
| Nine legacy knowledge files (round-11 provenance denominator) | Not modified (`git status`) |
| `LOG.md`, `SCORECARD.md`, `corpus/README.md`, `corpus/QUALITY.md`, `served-identity-crosswalk.md`, `SKILL.md` | The HEAD bytes are an exact prefix of the working file, so these are pure appends |
| `corpus/SOURCES.md` | Not a byte-prefix append: the S032 row was added at :44 and a search-log bullet at :59, inside their sections. `git diff` shows `+` lines only, so every existing line and cell is unchanged. This fits the row-level SOURCES contract. The D2/D4 prose is at EOF |
| Source vs old snapshot | Source sha256 `9dc40d25…2093a`. The old copy has 63 lines; the source has 60 plus a trailing newline. Old line 55 is cut to 768 bytes ending `St…`; there is a blank line 62 and a marker line 63, `[Some lines truncated … artifact://1157:raw:55-55 …]`, with no final newline |
| `fidelity.py` | Persistent writes happen only inside the selftest tempdir. The source anchor is a code constant at `:38-39`. Round-11 files are never opened for writing |
| New snapshot path | `round-12/frozen/corpus/SOURCES.md` is a different path from the round-11 copy, so it cannot overwrite it. It had not been generated yet when I read the tree |

**Round-11 receipt non-regression ([INFERENCE], not run).** Round-11 `reproduce.py:41-55`
measures the live tree in its "after" run. `measure.py:350` counts column-zero
`source:`/`verified-at:`/`recheck:` lines over the **whole** crosswalk file and fails if any
appears more than once. The appended D4 note (crosswalk :86-121) has no column-zero field
lines; the only ones are still lines 1–3. The nine legacy files are unchanged. So round-11
`reproduce.py` should still exit 0 at the integrated tree.

## Counterexamples (sustained)

### H1 — SEAT-PROTOCOL banner was prepended, not appended (contract defect; L1 decision)
- **Evidence:** `.ufo/round-10/SEAT-PROTOCOL.md`: `prefix_ok False`, `suffix_ok True`.
  `git diff` gives `@@ -1 +1,27`: 26 banner lines sit before the original line 1. The
  original 4413 bytes (sha256 `e9fbaa02…49c0a`, blob from `3285cdf`) survive only as a suffix.
- **Rules it breaks:**
  - The round contract: "do not edit immutable prior round evidence except **appending**".
  - The owner's own target: "append … Preserve original prefix".
  - The `head -n 56` prefix check that SafetyArchive specified.
- **Why the reviewer's check misses it:** ReviewArchive's check, "`git diff` shows only `+`
  lines", passes on a prepend. So it does not prove append-only. Only a byte-prefix hash does.
- **The banner contradicts itself.** It says "Verify with `tail -c 4413 … | sha256sum`; append
  only". The next append to the file breaks that tail check.
- **Line numbers moved.** Every original line is now 26 lower, so old citations are stale:
  round-11 `advice/AttackAdmission.md:76` ("SEAT-PROTOCOL line 1") and round-12 MistakeScribe
  `SEAT-PROTOCOL.md:1`.
- **Not disclosed.** The LOG round-12 entry says only "receives an unmistakable in-file
  archival disclaimer". It does not record this as an append-only exception, unlike the
  lane's own precedent at `LOG.md:523`.
- **Axes:** history integrity −, D5 visibility +.
- **Smallest safe correction (preferred):**
  1. Restore the exact HEAD bytes.
  2. Append the same banner at EOF, under a greppable `ARCHIVAL DISCLAIMER — NEVER EXECUTED`
     heading.
  3. Change its verifier to `head -c 4413 … | sha256sum` = `e9fbaa02…`. That check stays
     stable under later appends.
  4. Keep the LOG/README wording that cites the file only together with "historical, void".
- **Alternative if L1 decides top-of-file visibility outweighs the rule:** record it as an
  explicit append-only exception in LOG and the report. Give the suffix hash and the shifted
  line offset (+26). The judge should treat an undisclosed prepend as a reject.
- **Residual:** `.ufo/round-{6..9}/SEAT-PROTOCOL.md` carry the same "binding" template with
  no disclaimer. That is outside D5; name it as a residual in the report, not a fix this round.

### H2 — `reproduce.py --output` can silently overwrite any lane file, including round-11 receipts
- **Evidence:** `round-12/reproduce.py:641-655` checks only that the path is under the lane
  root. `write_receipt` (`:616-638`) then calls `os.replace`, which atomically clobbers an
  existing file.
- **Counterexamples:** each of these overwrites a protected file with a round-12 receipt:
  - `--output .ufo/waves/round-11/acceptance.json`
  - `--output .ufo/waves/round-11/frozen/before/corpus/SOURCES.md`, which also makes round-11
    `reproduce.py` fail closed with `snapshot_tampered`
  - `--output corpus/lessons/round-11-verifier-spotcheck.md`
- A repeat run also overwrites a prior round-12 receipt without warning.
- **Axes:** report non-overwrite −, history integrity −.
- **Smallest correction:**
  - Refuse any resolved path that already exists.
  - Restrict output to `.ufo/waves/round-12/`.
  - Make the write no-clobber: replace `os.replace` with `os.link(temp, path)` and then unlink
    the temp file. That raises `FileExistsError` atomically.
  - Exit 2 with a stable error, e.g. `output_exists`.

### H3 — the D1 erratum does not name the old artifact
- **What D1 asks:** "Append an erratum naming the old truncated snapshot … carry the
  actual-before versus frozen hashes."
- **What each new file covers:**
  - `round-12/frozen/README.md:3-5` says the round-11 receipt is "left byte-identical" but
    gives neither the old path nor the hashes.
  - The lesson (`round-12.md:25`) has the hashes but not the path.
  - The LOG says only "old round-11 frozen bytes, manifest and receipt remain untouched".
- **Old claims still read as exact:** `LOG.md:547` ("frozen source bytes … are in
  `.ufo/waves/round-11/frozen/`") and `round-11.md:206-208` ("frozen original source
  registry") carry no pointer to D1.
- **Correction (no round-11 byte change):** Fidelity appends an `Erratum` line to
  `round-12/frozen/README.md`. It should name:
  - the path `.ufo/waves/round-11/frozen/before/corpus/SOURCES.md`;
  - frozen `52665cf2…` versus actual `9dc40d25…`;
  - line 55 cut at 768 bytes and the appended `artifact://1157` marker at line 63;
  - that census rows are unaffected, per the closure.
  
  Optionally, also append a one-line pointer at EOF of `corpus/lessons/round-11.md`.
- **Never** append the erratum to the round-11 frozen `SOURCES.md` or `expected.json`.
  - SOURCES: its pin at `expected.json:15` makes round-11 `reproduce.py:33-37` exit 2.
  - `expected.json`: appending text after the JSON breaks `json.loads` (`:29`), and editing
    a pin rewrites history.

### H4 — wording invites in-place regeneration later (minor)
`round-12/frozen/README.md:13-14` says "Regenerating the snapshot requires regenerating the
pin". A future round could read that as permission to rewrite round-12's frozen pair in place.
**Correction:** replace it with "Never regenerate in place; any later correction gets a new
round directory and manifest."

### H5 — SKILL.md still has no final newline (cosmetic; false-alarm risk)
The HEAD bytes are a true prefix of the new file. But because HEAD had no final newline,
`git diff` shows one `-`/`+` pair at :374, and the new block again ends without a newline.
A reviewer counting "no deletions" (as the round-11 closure did for SCORECARD) would flag a
false violation, and the next round will hit the same thing. **Correction:** end the appended
block with `\n`, and judge append-only with byte-prefix hashes, not `git diff` deletion counts.

## Not sustained

- SOURCES row and search-log insertion: the edits are in-section, `+` lines only, and leave
  all S001–S031 cells intact. The D2 paragraph's "lines 6–7" and the crosswalk's
  `SOURCES.md:23,43` still point to the right lines, because the insertion is at :44 and later.
- Report overwrite in the lane: `corpus/lessons/round-12.md` and `.ufo/waves/round-12/advice/`
  are new paths. The fleet `.ufo/reports/round-12/kama.md` is a new round path that L1 writes
  after the lane push. Do not create `corpus/lessons/round-12-verifier-spotcheck.md`; that
  path belongs to the non-author closure.

## Checks for L1 (not run here)

1. Byte-prefix check on every modified tracked file: `cmp -n $(git cat-file -s HEAD:<f>) <(git show HEAD:<f>) <f>`. Expect a pass everywhere except SOURCES.md (row-level) and SEAT-PROTOCOL until H1 is fixed.
2. `git show HEAD:.ufo/round-10/SEAT-PROTOCOL.md | sha256sum` gives `e9fbaa02…`. After H1, `head -c 4413 .ufo/round-10/SEAT-PROTOCOL.md | sha256sum` should give the same.
3. `git diff --quiet HEAD -- .ufo/waves/round-11 corpus/lessons/round-11*.md` should exit 0.
4. `python3 .ufo/waves/round-11/reproduce.py` should still exit 0 (non-regression of the round-11 receipt on the live tree).
5. After H2, `reproduce.py --output .ufo/waves/round-11/acceptance.json` should exit 2 and leave that file's sha256 unchanged.
6. In the crosswalk, count column-zero `^(source|verified-at|recheck):` lines; each should still occur exactly once.

## Status update (re-read after Fidelity's message)

- **H3 resolved.** The erratum now has durable homes:
  - `corpus/lessons/round-12.md:145-156` names the old snapshot path, the old pin and
    receipt paths, the truncation and the `artifact://1157` marker.
  - `LOG.md:650-653` carries both SHA-256 values.
  - `advice/Fidelity.md:42-53` gives the byte counts 18793 vs 18898.
  - `git status` shows nothing modified under `.ufo/waves/round-11`.
- **H4 resolved.** `round-12/frozen/README.md` was removed. `Fidelity.md:52-53` and the lesson
  (`:155-156`) both say a later correction gets a new round directory and manifest, never an
  in-place regeneration. The frozen directory now holds only `corpus/SOURCES.md` and
  `expected.json`.
- **H1 is now a disclosed exception.** `round-12.md:139-141` says L1 authorized the prepend
  and that the original bytes survive as a suffix. That removes the "undisclosed" part. Still
  open:
  - The banner tells readers to verify with `tail -c 4413` and also says "append only". The
    next append breaks that check.
  - Neither the banner nor the lesson records the +26 line shift for old citations.
  - The round contract allows only *appending* to prior evidence. Whether a disclosed prepend
    is admissible is for the judge to decide.
  
  Smallest residual fix: change the banner's verifier to a check that survives appends, e.g.
  "the bytes between this banner's closing `---` line and EOF begin with the original 4413
  bytes". Also add one line saying original line N is now line N+26.
- **H2 still open:** I have not observed any change to the `--output` no-clobber behavior.
