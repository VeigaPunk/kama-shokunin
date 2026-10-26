# S9Lesson — round-47 lesson skeleton (kama, w1)

**Verdict:** the round-47 lesson skeleton is written in the round-46 shape with
`## Claims` placeholders, four Gate row families with scoped admits and three
grounded rejects, and three `## Mistakes` rows (the sufficiency family, D2's
tip-relative restoration, D5's dead pointer), each carrying a fix this seat showed
able to fail. No frozen artifact was edited; no defect was found in the frozen
counters by this seat beyond those the wave seats report.

## What was read (contract and inputs)

- `.ufo/waves/round-47/preregistration.json` — claims, predicates, controls, routed map.
- `tools/round47-append-audit-v2-check.py:1-101` (docstring = contract) and
  `tools/round47-live-replay-audit.py:1-82` (docstring = contract).
- `corpus/lessons/round-46.md:87` (sweep finding 1) and
  `corpus/lessons/round-46-verifier-spotcheck.md:138-141` (D2, D3, D5).
- `.ufo/waves/round-47/c2/release-b11909.json`, `.ufo/waves/round-47/c2/live/install.txt`,
  the three v4 receipts, and the round-46 v3 receipts.
- `.ufo/waves/round-47/w1/out/K1Cheat.md:37,47,57` and `K2Cheat.md:29,39,45` (round-47 attacks).
- `https://git-scm.com/docs/git-diff` (`--numstat` definition; page last updated for 2.56.0, 2026-09-28).
- Considered but did not run: seat X9Tally's `shortcut-tally.py` — absent at
  `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X9Tally/`
  when checked (21:30Z). The sufficiency row therefore carries X9Tally's proposed
  `--check` contract plus a fail-capable row check this seat did run and ship.

## Evidence (run by this seat)

Scratch `S=/fast/scratch/hyaku/kama-r47/S9Lesson`; one `git clone --shared` of the
lane at `S/lane`; `TMPDIR=$S`. Lane tip at draft time `46a924e0`; build
`3a09a1d93dcc16799cf6c4b48786e6440af134c4`; base `172b8ad0`.

1. **C1 counter at the build tip** (frozen file, read-only run, no network):
   ```
   python3 tools/round47-append-audit-v2-check.py --repo $S/lane \
     --tip 3a09a1d93dcc16799cf6c4b48786e6440af134c4 --scratch $S/c1scratch --out $S/c1-counter.out
   ```
   → `selftest=1 contract=1 lane=1 fixture=1 stable=1 files=85 lane_events=5
   lane_mismatch=0 fixture_mismatch=0 met=True`, `tip=3a09a1d9… base=172b8ad0…`,
   **exit 0** (`out/S9Lesson/c1-counter.out`). Same result the L1 pre-wave dry run recorded.

2. **C2 counter at the build tip** (frozen file, read-only run, network used by the
   replay leg: ~23 MB github.com + 1.2 MB huggingface.co):
   ```
   python3 tools/round47-live-replay-audit.py --repo $S/lane \
     --tip 3a09a1d93dcc16799cf6c4b48786e6440af134c4 --scratch $S/c2scratch --out $S/c2-counter.out
   ```
   → `receipts=1 replay=1 tamper=1 newrow=0 rerun_checks=11 met=False`,
   `started=2026-10-26T21:28:16.120715+00:00`, detail
   `newrow: no registry row names b11909 and caa8191df159f764fb0160e3d2fc6be008948aee`,
   **exit 1** (`out/S9Lesson/c2-counter.out`). Matches the L1 dry run; the only
   failing leg is the registry row that lands at integration.

3. **Deleted counts equal numstat** (`out/S9Lesson/evidence-stability.txt`):
   v2 reports `0718b6ab` LOG 2292 / SCORECARD 2421 / QUALITY 375 / README 663 and
   `dd9f5dc6` SCORECARD 31; `git -C $S/lane diff --numstat --no-renames <commit>^1 <commit>`
   prints 2292, 2421, 375, 663 and 31 deletions respectively.

4. **D2 stability, v1 vs v2** (same file):
   - v1 (`git show 4a2a4d55:tools/append-only-audit.py`) at `0163fea2` →
     `0718b6ab SCORECARD deleted=2417 restored_at_tip=2416`; at `4340cf2f` →
     `deleted=2417 restored_at_tip=2409`. The measure falls 7 with no new loss.
   - v2 at `0163fea2`, `4340cf2f` and `3a09a1d9` → `deleted=2421 restored_max=2420
     restored_best=82b5e9d3 status=partial` at all three tips. The stable predicate
     `restored_max(tip) >= restored_max(base)` therefore fails v1 (2409 < 2416) and
     passes v2 (2420 == 2420).

5. **D5 dead pointer** (`out/S9Lesson/evidence-d5.txt`):
   the three round-46 v3 receipts record `/fast/scratch/hyaku/kama-r46/X1Live/…`
   and `os.path.exists` is `False` for all three; the three round-47 v4 receipts
   record `null`. Calling the counter's own `check_receipt`
   (`tools/round47-live-replay-audit.py:172-178`) on v4 receipt-1 returns `True`
   unmutated and `False` with exactly
   `teardown.log_path '/fast/scratch/hyaku/kama-r46/X1Live/kama-llamacpp-live-j7s5brv0.log'
   is not a committed repo-relative path` after setting that one field.

6. **Sufficiency row check** (`out/S9Lesson/evidence-row-check.txt`):
   ```
   python3 .ufo/waves/round-47/w1/out/S9Lesson/check-sufficiency-row.py corpus/lessons/round-46.md
   → row=0 file=corpus/lessons/round-46.md command=0   exit 1
   python3 …/check-sufficiency-row.py .ufo/waves/round-47/w1/out/S9Lesson/round-47.md
   → row=1 file=…/round-47.md command=1                exit 0
   ```
   The check fails on the lesson that lost the carrier and passes on the draft that
   carries it with a runnable command in the fix cell. The ongoing trend check is
   X9Tally's `shortcut-tally.py --check N`; the sufficiency row names the instance
   set (K1Cheat `:37,57`, K2Cheat `:29,39,45`) and requires `--check 0` to exit 1
   for any round containing one of them.

7. **Gate material** (read, not re-fetched):
   - b11909 release record: `target_commitish caa8191df159f764fb0160e3d2fc6be008948aee`,
     `published_at 2026-10-26T21:00:58Z`, `prerelease true`, asset
     `llama-b11909-bin-ubuntu-x64.tar.gz` 22475032 bytes
     `sha256:bf94332a…e695b` (`.ufo/waves/round-47/c2/release-b11909.json`).
   - `install.txt`: 22475032 bytes, same sha256, extracted `llama-server`
     `35ac50fb…7ff0`, `version: 0.7.0-dev (build 11909, commit caa8191df)`.
   - receipts 1–3: v4, pass, `evaluated=11 passed=11`,
     `captures.health.body {"status":"ok"}`, `build_info b11909-caa8191df`,
     `provenance.server.member llama-b11909/llama-server`, `teardown.log_path null`.
   - git-diff(1) `--numstat`: field 3 is "the number of deleted lines"; binary files
     "outputs two `-` instead of saying `0` `0`" — the definition C1's `deleted`
     must equal, not evidence the tool implements it.

## Findings

1. **Sequencing requirement, not a defect:** C2's `met` is `False` at the build tip
   solely because `corpus/SOURCES.md` has no b11909 row (`newrow=0`). If the
   integration commit does not add the row, the counter stays at exit 1 and C2 is an
   honest stop. The lesson skeleton's Gate lists the four rows to register
   (`<S488>`–`<S491>`, ids placeholders from the current tail `S487`).
2. **Reported by seat K2Cheat, not re-run here:** the C2 counter compares recorded
   digest fields between receipts but never hashes the rerun files at
   `server.realpath`/`model.path` (`tools/round47-live-replay-audit.py:273-284`), so a
   fabricated rerun with 0-byte placeholders met the frozen counter
   (`K2Cheat.md:39`, V3). Proposed fix (K2Cheat's fix 1, counter frozen): hash the two
   files inside the counter and require equality with the recorded sha256; require
   `J["inputs"]["archive"]` non-null and matching. This is filed as the instance set
   of the sufficiency row, not as an in-place edit.
3. **`install.txt` is host-bound:** it records `/home/vgpnk/.local/opt/llama-b11909/…`
   as the install location. The Gate rejects that path as the artifact locator
   (asset URL + archive member is the locator); the same file's byte count and
   sha256 remain usable evidence. Same class as D5.
4. **Placeholders left for the L1:** measured commit and receipts, `SCORECARD §Round-47
   measured results` values, Wave seat count/`seat-yield` output, r46-D4 disposition,
   the term-wait reject values, and the status/recheck/used-by line.

## Out-of-scope / not done

- No lane file was edited; the draft and all evidence live in
  `.ufo/waves/round-47/w1/out/S9Lesson/`. No counter, preregistration or control was
  modified.
- I did not rerun C1/C2 at an integration commit (none exists yet).
- I did not run X9Tally's tally (absent); the row states that and carries a runnable
  substitute check.
- Tooling: no installs or upgrades this seat (nothing needed; `git`, `python3` only).

## Absolute paths written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Lesson.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Lesson/round-47.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Lesson/check-sufficiency-row.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Lesson/c1-counter.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Lesson/c2-counter.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Lesson/evidence-stability.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Lesson/evidence-d5.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Lesson/evidence-row-check.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Lesson/c2/{receipt-1.json,receipt-2.json,receipt-3.json,install.txt,release-b11909.json}`
