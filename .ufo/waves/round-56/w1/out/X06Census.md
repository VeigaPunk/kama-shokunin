# X06Census — sources-census start receipt re-run (round-56, lane kama)

**Verdict: the census start receipt is reproducible.** At the base registry horizon (`e10b6d39`) the receipt-producing command reproduces all 98 warning lines of `.ufo/waves/round-56/census/start.out` exactly, with exit 0. Against the current (freeze-tip) registry the same command emits **one additional warning line** (`S513 duplicate url man7.org/.../ld.so.8.html`) and still **exits 0**. No error (`E*`) or overdue lines appear in either run. Two defects of provenance are reported below: the start receipt is **not committed** (it is untracked in both git and jj), and it is **stale by one committed registry row**.

Axes: **operability** — the census gate is unchanged and green at the live registry (exit 0, 0 errors, `missing 0`); no serving behavior is touched. **calibration** — the receipt->command->registry binding is now established by exact reproduction, and the single live delta is fully explained by the committed registry addition; the receipt's uncommitted state and one-row lag are calibration defects, not claim changes. No score movement is claimed by this seat; C1/C2 predicates in `preregistration.json` do not read the census.

## Exact commands, outputs, exits

Tool: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh`, sha256 `3fb7261569f46423dd80ecc23e0a23789a7926f667c7a3fc559d2439d4a64e30`, mtime `2026-10-19 21:22:45 -03` (unchanged since before the wave; no tool drift). Host: GNU bash 5.3.20(1), GNU Awk 5.4.1. Tip: `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7`. Worktree `corpus/SOURCES.md` blob `421b02b5de1f83d32db1685f52ee25c6e595fcf2` equals `HEAD:corpus/SOURCES.md`, i.e. no local registry edit confounds the rerun. All runs used `TMPDIR=/fast/scratch/hyaku/kama-r56/X06Census`.

1. **Live re-run (exact start-receipt mode):**
   `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
   → **exit 0**, 100 stdout lines (98 `W04`, 1 `W01`, 1 `kama ok .../corpus/SOURCES.md`), 0 stderr bytes, sha256 `3eeea0f4be9d942913d0458d1ec47f5e2d963b2790b95afbfc44abc7fe9a267d`. A second identical run produced the same sha256 (`rerun-validate2.out`), so the rerun is deterministic.
2. **Committed receipt for comparison:** `.ufo/waves/round-56/census/start.out`, 99 lines (97 `W04`, 1 `W01` `S481`, 1 `ok`), sha256 `bdc5c03c0073c7031c7294c3c2cf5c4bea17725461d5ace672f6a29617ef43e1`, mtime `2026-10-27 13:00:35 -03`.
3. **Diff live vs receipt (`start-vs-live.diff`):** one added line, no deletions, no reordering:
   `kama	W04	S513 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes`
   inserted immediately before the final `kama	ok` line.
4. **Base-horizon reproduction:** the lane is read-only, so a lane-rooted scratch root was built at `/fast/scratch/hyaku/kama-r56/X06Census/root/kama-shokunin` with every lane entry symlinked, except `corpus/SOURCES.md` replaced by `git show e10b6d39af450e8d652be9ac2986768b531fe13f:corpus/SOURCES.md` (611 lines, no S512/S513), plus the fleet `shokunin.conf`.
   `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /fast/scratch/hyaku/kama-r56/X06Census/root kama`
   → **exit 0**, 99 lines, sha256 `8b52003f7ec17b474a5844a84613298c00a1bffa83fae514e6429246891545d8`. Diff of warning lines (excluding the `ok` path line, which names the scratch root) against `start.out` is **empty** (`start-vs-base-root-warnings.diff`, diff exit 0). This identifies the start receipt's producing command and horizon: it is the `validate` mode at lane granularity against the base registry, and its unrecorded exit is 0.
5. **Census mode, same two horizons:**
   `... sources-census.sh census --root /fast/scratch/hyaku/kama-r56/X06Census/root kama` → exit 0; `rows 252, tier.A 239, tier.B 9, tier.C 4, mined 228, queued 8, rejected 16, missing 0`.
   `... sources-census.sh census --root /home/vgpnk/Projects/shokunin kama` → exit 0; `rows 254, tier.A 241, tier.B 9, tier.C 4, mined 229, queued 8, rejected 17, missing 0`.
   Delta is exactly the two committed rows: +1 tier-A mined (S512), +1 tier-A rejected (S513).

## Why the single delta exists

`git diff e10b6d39..efc6b3ec -- corpus/SOURCES.md` is 4 insertions, 0 deletions: `S512 rtld-audit(7)` and `S513 ld.so(8)` plus two blank lines (`registry-delta.diff`). S512's URL is unique in the registry, so it yields no `W04`; S513 repeats the already-catalogued `man7.org/linux/man-pages/man8/ld.so.8.html` (S67, S79) and therefore adds the one `W04` seen live. `W04` is a warning class that does not change lane status (`sources-census.sh:31-32`), which matches the observed exit 0 at both horizons. The start receipt was written at 13:00:35, two minutes before the freeze appended S512/S513, so it is a correct but pre-freeze snapshot.

## Defects / proposed fixes

1. **`start.out` is not committed** (calibration). `git ls-tree -r efc6b3ec -- .ufo/waves/round-56/` lists only `controls/base-c1.out`, `controls/base-c2.out`, `preregistration.json`, `sources/ld.so.8.html`, `sources/rtld-audit.7.html`; `git status` reports `?? .ufo/waves/round-56/census/`. The lane's jj is configured `snapshot.auto-track = "none()"`, so `jj file list -r @` also lacks it. The seat text calls it the "committed start output"; no committed bytes exist, so comparison is against worktree bytes `bdc5c03c...`, which any lane writer can rewrite without a record. Proposed fix: include `census/start.out` (and `measured/` mutant receipts) in the freeze commit, or record their sha256s in `preregistration.json`.
2. **Start receipt is stale by one committed row** (calibration). Because S512/S513 landed after the receipt, the live receipt-equivalent output is 100 lines/98 `W04`, not 99/97. `Q08CensusEnd` ("run the frozen sources-census command") has no recorded expected output; a final-tip seat will legitimately produce 100 lines and cannot tell growth from drift. Proposed fix: record the exact command and expected warning/row counts at freeze time, and regenerate the start receipt after the registry append.
3. **The census command itself is not frozen anywhere** (calibration). `grep` of `.ufo/waves/round-56/preregistration.json` finds no census entry (`build_spec.py:94,107` only name the seats). The command above is identified by exact reproduction, not by a written pin. Proposed fix: add the command line, tool sha256 and expected exit to the preregistration alongside the C1/C2 counters.

Not a defect, recorded to stop a false positive: `--file` mode is not a substitute for lane mode — it labels the row `file` and resolves used-by relative to `dirname(file)/..` (`sources-census.sh:497-505,538-568`), so it reports `E11` spam unless that directory is a populated lane root. The `--root` form was used here.

## Contradictions / limits

- This seat re-ran an untracked worktree receipt; it did not and cannot verify who created `start.out`, its chronology, or that its recorded bytes were produced at `e10b6d39`. The base-horizon reproduction shows the bytes are *consistent with* that command at that registry content, not that they were captured then. [INFERENCE] for the producing command and horizon; the byte-level matches themselves are measured.
- The receipt records no exit code; the reproduced exit 0 is the measured exit of the equivalent command, not a recorded field of `start.out`.
- Census covers the registry (`corpus/SOURCES.md`) only. It says nothing about the C1 env-leg or C2 roster claims, and no claim predicate consumes it.
- No lane, jj index, or git state was modified: all runs were read-only, the scratch root only symlinked lane paths, and scratch was removed after copying receipts. No tools were installed.

## Retained receipts (`.ufo/waves/round-56/w1/out/X06Census/`)

`rerun-validate.out` (`3eeea0f4...`), `rerun-validate2.out` (same sha256), `start-vs-live.diff`, `base-root-validate.out` (`8b52003f...`), `base-root-validate.err` (empty), `start-vs-base-root-warnings.diff` (empty), `base-census.out`, `census-now.out`, `registry-delta.diff`, `SOURCES-base.md` (`4962c9a0...`), `exits.txt`.

**Verification run:** commands 1, 4 and both census invocations above, all exit 0; diff 3 non-empty by exactly one added line; diff of base-horizon warnings empty. No build/lint/test suite was run for this read-only receipt comparison.
