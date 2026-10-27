# V04LateOutputs — round-56 w1 (lane kama): inherited round-55 late seat outputs

Scope: inventory the round-55 w1 late seat output files inherited by round 56, compare them
with the preserved artifacts that do exist, and report whether any remain uncommitted.
Read-only over the lane; no lane file, jj change or git index was written by this seat.

## Verdict

**Yes — they remain uncommitted.** At lane `HEAD` `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7`
(`round-56: freeze LD_AUDIT env leg and prereg roster controls`) the round-55 wave carries:

```
$ git status --porcelain=v1 -uall .ufo/waves/round-55 | wc -l
305
$ git status --porcelain=v1 .ufo/waves/round-55 | wc -l          # collapsed / default form
41
```

305 file entries = **303 untracked files (3,413,476 B) + 2 modified tracked files (56,461 B)**
= 3,469,937 B total. Collapsed to 41 porcelain lines = 38 `??` + 2 ` M` + 1 `??` at `w1/`
level (collapsed form also prints the two J2RowCap files separately). Nothing is staged
(`git diff --cached --name-only .ufo/waves/round-55 | wc -l` → `0`), and nothing is ignored —
`git check-ignore -v` over `w1-results.json`, `out/M6Anon.md`, `w1.ready.dispatched` and
`round-56/w1.ready` exits `1` with no output; `.gitignore` holds only
`.ufo/interactive-sessions/`, `.ufo/state/`, `__pycache__/`. These files were never `git add`ed,
not merely filtered.

Receipts written by this seat (both under `.ufo/waves/round-56/w1/out/V04LateOutputs/`):
`git-status-r55.txt` (307 lines, raw `-uall` porcelain at the HEAD above),
`r55-uncommitted-manifest.json` (every path + bytes + sha256),
`seat-table.tsv` (per-seat class/count/bytes/mtimes).

## What "late" means, and the cut used

The round-55 integration commit `c2c05e30` (`2026-10-27T11:13:18-03:00`, "… 44 seat reports")
is the last commit that added seat outputs; `e10b6d39` (11:31:52) added only
`corpus/lessons/round-55-verifier-spotcheck.md`, and `bf336baa` touched only `SCORECARD.md`.
Measured against `c2c05e30`:

```
$ git show --name-only --format='' c2c05e30 | grep -c 'round-55/w1/out/'
625
$ git show --name-only --format='' c2c05e30 | grep -cE 'round-55/w1/out/[^/]+\.md$'
49
```

49 seat reports + 3 seat directories without a report (`J2RowCap`, `V2C2Delta`,
`X7BatteryReplay`) = 52 seats touched; 12 seats untouched. On disk there are 63 seat reports
for 64 seats (`Cn2` has none), so 49 committed + **14 uncommitted reports** = 63 — the
arithmetic closes exactly. (The commit message's "44 seat reports" understates the 49 the
commit actually contains; an observed divergence, not a count this seat can reconcile.)

Late files are therefore of two kinds:

* **never-integrated seats** — no file of the seat exists in `c2c05e30`;
* **late additions** — the seat directory landed, but its report (and for J2RowCap a
  post-integration rewrite plus the proposed diff) arrived afterwards.

Every late mtime is later than 11:13:18 except `M1C1Mut`'s earliest file
(`2026-10-27T10:13:09`), which is an inherited `cp -p` receipt copied from the seat's clone —
its directory's last write is 11:26:00. This is consistent with the disclosed defect 8 of the
round-55 verifier lesson ("the wave filed at 44/64 without WAVE-DONE (budget-forced wrap-up) …
the late outputs are the defect-7 files", `corpus/lessons/round-55-verifier-spotcheck.md:132-137`).

## Inventory

Per seat, from `git status -uall` (untracked + modified; bytes are working-tree sizes):

| seat | class | files | bytes | modified | first..last mtime (local) |
|---|---|---:|---:|---:|---|
| V2C2Delta | late additions (report only) | 1 | 10,213 | 0 | 11:13:39..11:13:39 |
| M2C2Mut | never integrated | 66 | 673,938 | 0 | 11:15:28..11:18:07 |
| V4Receipts | never integrated | 20 | 82,433 | 0 | 11:14:29..11:20:35 |
| J2RowCap | late additions (+2 modified) | 4 | 77,757 | 2 | 11:22:19..11:25:30 |
| V7Hashes | never integrated | 4 | 50,833 | 0 | 11:21:28..11:25:48 |
| X7BatteryReplay | late additions | 23 | 96,270 | 0 | 11:17:21..11:25:51 |
| M1C1Mut | never integrated | 62 | 920,323 | 0 | 10:13:09..11:26:00 |
| J5EnvNames | never integrated | 23 | 147,536 | 0 | 11:24:08..11:26:31 |
| J6Timing | never integrated | 20 | 129,463 | 0 | 11:28:32..11:31:37 |
| J4ArchiveImmut | never integrated | 36 | 111,550 | 0 | 11:17:41..11:37:20 |
| D1 | never integrated | 2 | 47,290 | 0 | 11:36:17..11:38:12 |
| J1Twopass | never integrated | 10 | 307,846 | 0 | 11:38:07..11:40:33 |
| J3SecondMemfd | never integrated | 7 | 16,427 | 0 | 11:37:31..11:42:11 |
| M6Anon | never integrated | 26 | 473,927 | 0 | 11:42:34..11:43:53 |
| `w1/w1-results.json` | collection file | 1 | 324,131 | 0 | 11:44:20..11:44:20 |

Detail on the two special cases:

* **J2RowCap** — the directory is committed (harness JSON/PY), but the working tree has
  `+72/−9` in `j2-rowcap-unit-harness.json` and `+258/−4` in `j2-rowcap-unit-harness.py`
  (`git diff --numstat`), plus untracked `J2RowCap.md` and `J2RowCap-proposed-fix.diff`.
  So the committed copy is the pre-final harness; the verdict-bearing report was never added.
* **X7BatteryReplay** — 10 receipts committed (`control.out`, four mutant receipts,
  `replay-summary.txt`, …), 23 later files untracked: the report, `divergence-report.txt`,
  `elf-offset-analysis.txt`, `evidence-identity.txt`, `fixed-run-battery.py`,
  `proposed-run-battery.patch`, the `l1-receipts-cited/` copies and `scripts/` (7 files).
* **V2C2Delta** — 7 receipt files committed (including `receipt-forge-570f2f4.txt`);
  only its report `V2C2Delta.md` is untracked.
* **Cn2** — *no artifact at all in the lane*: `.ufo/waves/round-55/w1/out/Cn2/` is an empty
  directory (0 entries) and no `Cn2.md` exists, so git lists nothing for it. Its only surviving
  output is (a) the yield inside the untracked `w1-results.json`, and (b) three receipts left in
  `/fast/scratch/hyaku/kama-r55/w1/Cn2/` (`round50-append-audit-v5-check.py.out` 6,483 B,
  `round51-append-audit-v6-check.py.out` 1,536 B, `round52-append-restore-check.py.out` 1,224 B)
  plus a lane clone there. Scratch is transient by the wave contract, so Cn2's evidence is at
  risk of disappearing entirely.

## Comparison against the preserved artifacts

Four preserved surfaces exist; only one carries late-seat content, and it is itself untracked.

1. **`w1/w1-results.json` (untracked, 324,131 B, 64 seat entries).** Holds each late seat's
   terminal yield JSON (`seat`, `verdict`, `findings`, receipts). Cross-checked 14/14 late
   seats: every one has an entry, every `output` string parses as JSON, and each verdict is a
   *restatement* of the corresponding `.md`, not a copy — 2/14 verdict sentences appear
   verbatim in the report (D1, J1Twopass), the other 12 differ in wording while agreeing on the
   headline claim (checked pair by pair: e.g. X7 yield "zero receipt divergence …" vs
   `X7BatteryReplay.md` verdict "Zero receipt divergence — the control and all four mutants
   reproduce …"; M6Anon yield "… m1-anon-append, m2-memfd-name, m3-kernel-maps, m5-nopath-skip
   SURVIVED …" vs report "4 of 5 weakening mutants survive … the 5th … is killed"). No
   contradiction found between the two forms; the JSON is the summary, the `.md` the evidence
   narrative. **This means deleting the untracked files would lose the evidence, not just the
   summary** — and `w1-results.json` alone would leave 14 reports as one-line verdicts.
2. **Committed wave metadata** — `w1/dispatch.json`, `w1/spec.json`, `w1/validate.out`,
   `w1/out/swarm-registry.json`, `build_spec.py`, `w1.ready.dispatched` all reference the late
   seat *names* (`git grep -l -w M6Anon HEAD` → those 6 files + `Sen3/05-dispatcher-kama.out`)
   but contain none of their output.
3. **Committed narrative** — `LOG.md`, `SCORECARD.md` §Round 55 (incl. "Kill-rule disposition"
   and "What `met=True` does not show"), and `corpus/` contain no reference to any late seat by
   name (`git grep -n "M6Anon\|J1Twopass\|M1C1Mut\|M2C2Mut" HEAD -- LOG.md SCORECARD.md
   corpus .ufo/waves/round-56` → no output). Round 56's `preregistration.json` cites the
   round-55 spotcheck's routed defects generically ("defects 1, 2, 4, 5, 6, 7, 9, 10") and
   sources LD_AUDIT to S512 + rtld-audit(7); it never cites the uncommitted J5EnvNames evidence.
4. **Duplicates elsewhere** — none. `git ls-tree -r HEAD --name-only | grep -c '/<Seat>.md$'`
   is 0 for D1/J1Twopass/J3SecondMemfd/M6Anon/X7BatteryReplay, and a bounded `find` over
   `/home/vgpnk/Projects/shokunin` and `/fast/scratch/hyaku` for `M6Anon.md`, `D1.md`,
   `w1-results.json` outside the round-55 out dir returns only other lanes' homonyms
   (`kaidoku-*`, `lore-*`, `revenger-*`, `kengaku-*`). The late reports have no second home.

**Defect-7 count drift.** The committed round-55 spotcheck records "2 modified + 10 untracked
under `.ufo/waves/round-55/w1/out/`". Measured now: 2 modified + 302 untracked files under
`out/` (38 collapsed `??` entries). Even restricted to files that already existed at the
lesson's own commit time (11:31:52), the count is **234 untracked files (2,167,236 B)**; 69
more arrived afterwards (D1 11:36–11:38, J1Twopass 11:38–11:40, J3SecondMemfd 11:37–11:42,
M6Anon 11:42–11:43, plus `w1-results.json` 11:44). So the lesson's figure is not a file count
of the tree at any time after 11:15 and cannot be reproduced from the tree.
[INFERENCE] it was a collapsed `git status` listing taken earlier in that seat's process
(a collapsed listing reaches 10 entries only around 11:23 by the mtime record). Either way the
committed defect record understates what is now in the tree by ~30× in files.

## Late content that exists only in these uncommitted files

Substantive claims, read from the reports (none of this is echoed in a committed file):

* **V2C2Delta (HIGH)** — C2's `superseded` clause never verifies the base citation *resolved*
  at base; the seat forged a real-tree tip that deletes a never-resolved base citation and still
  prints `met=True` exit 0. Its receipt `receipt-forge-570f2f4.txt` **is committed**; the
  report that explains it is not. (SCORECARD's "checks cited-at-base, not resolved-at-base"
  line, credited to K2Predicate/K4Sizing, covers the same gap without the forged receipt.)
* **V2C2Delta (MEDIUM)** — the fixture's forged-`superseded` arm is dead code: per-scenario
  `hit` is clobbered by `hit = bool(want(ok, c))` at line 810, so a killed clause-(b) still
  yields 15/15. Not recorded anywhere committed.
* **J2RowCap** — both ROW_CAP clauses are correctly implemented and both *can* fail on
  synthetic and real maps rows, but at the frozen configuration neither branch can fire, so the
  frozen C1 measurement carries no evidence for either; a guard-deleting mutant would still
  print `met=True`. This is a kill-battery coverage gap absent from the committed
  "What `met=True` does not show" list.
* **J1Twopass** — the frozen counter's sampling-window limit is right in kind and wrong in the
  two places it is written: a same-uid in-place `pwrite` rewrite restored between the two reads
  passed 10/10 while `/proc/<pid>/mem` showed the flipped byte; the same rewrite held across
  pass 2 was caught 10/10. The committed SCORECARD mentions "the sampling window (two passes +
  a post-exit re-hash)" but not the wording error or the 10/10 result.
* **J5EnvNames** — `BAD_ENV` is underinclusive: the live server carries exactly five env names
  (`HOME`, `LANG`, `LD_LIBRARY_PATH`, `PATH`, `TMPDIR`) and LD_AUDIT is a live glibc channel the
  leg never names. This is the direct evidence behind round 56's C1 choice, and it is
  uncommitted while round 56 scores C1.
* **M6Anon** — 4 of 5 anon-leg weakening mutants survive the honest-build detector at
  `9c60eae6` (`met=True`, expected); the 5th (x-filter drop) is killed by over-flagging; the
  synthetic-maps unit harness kills all 5. No counter defect.
* **J3SecondMemfd** — a second executable memfd is reachable as non-root without LD_PRELOAD;
  the frozen counter rejects it by dev+inode even when the live tool hides it (`met=False`,
  exit 1).
* **J4ArchiveImmut** — no falsification: in-place overwrite, rename, forged bytes and unlink of
  the archive change no member comparison; only a vanish *before* the reference read fails, and
  it fails closed (`met=False`, exit 1).
* **V7Hashes** — PASS (clean): every lane commit hash cited in the committed round-55
  artifacts resolves; counter sha256s match preregistration ↔ frozen blobs ↔ worktree.
* **V4Receipts** — every printed number in the 11 committed receipts re-derives; one disclosed
  freeze-contract defect (MEDIUM) and one stale-row issue.
* **J6Timing** — between-passes rewrite of the loaded `libggml-cpu` file is covered, not a
  practical bypass (`met=False` 10/10); the two-pass leg tripped 15/30 replays.
* **D1** — the wave's own dedup: 59 seat reports → 41 distinct findings, 1 claim-falsifying,
  8 integration-red, 21 conformance, 11 observation, with four seat conflicts quoted.
  Its input set predates the last five late seats, so this tally is now itself stale.
* **M2C2Mut** — 7 of 12 single mutants killed, 2 equivalent, 3 true survivors (coverage gaps,
  not counter defects).
* **M1C1Mut** — 15/15 mutants applied, 21 runs, 3 survivors each with a live killing case,
  4 killed, 8 equivalent, plus a preregistration-vs-battery freeze-consistency defect.

## Defects and proposed fixes (this seat's scope only)

1. **D1 — 303 untracked + 2 modified round-55 artifacts at round-56 HEAD.** Fix: one successor
   commit that adds every path in `r55-uncommitted-manifest.json` verbatim (sha256-recorded), or
   an explicit sweep commit whose message names each discarded path and why. Committing the
   14 `.md` reports plus `w1-results.json` is the minimum to make the wave auditable.
2. **D2 — the wave's only machine-readable result file is untracked.** Fix: commit
   `.ufo/waves/round-55/w1/w1-results.json` (or move it under a path the wave contract commits).
   Without it, 64 seats have no structured yield record at all.
3. **D3 — J2RowCap's committed harness is pre-final** (`+330/−13` against the working tree) while
   its verdict and proposed fix are untracked. Fix: commit the final harness and `J2RowCap.md`
   together so the committed harness matches the report that interprets it.
4. **D4 — Cn2 has no lane artifact and its receipts exist only in scratch.** Fix: copy the three
   `round5x-append-*-check.py.out` receipts (and a short `Cn2.md` stating what the seat concluded)
   into `out/Cn2/` before scratch is swept.
5. **D5 — the committed defect-7 figure ("2 modified + 10 untracked") is unreproducible** from
   the tree at its own commit time (234 untracked files then, 303 now). Fix: correct it in a
   successor lesson, or annotate it as a collapsed-entry count with the method named.
6. **D6 — round 56's C1 grounding is uncited to the seat that produced it.** Fix: cite
   `J5EnvNames` (or its committed successor) in the next freeze's `sourced` field; the seat
   currently quoted is S512 (rtld-audit(7)), which grounds the mechanism, not the host's
   five-name BAD_ENV gap.

## Method, limits, confidence

Commands run (all read-only over the lane; lane root
`/home/vgpnk/Projects/shokunin/kama-shokunin`, cwd never used for writes):
`git rev-parse HEAD`, `git log --format=%h %cI %s`, `git show --name-only|--stat|--numstat`
(`c2c05e30`, `e10b6d39`, `bf336baa`), `git ls-files --error-unmatch`, `git ls-tree -r HEAD`,
`git ls-files`, `git status --porcelain=v1 [-uall]`, `git diff --stat/--numstat/--cached`,
`git check-ignore -v`, `git grep -l/-n ... HEAD`, bounded `find` over
`/home/vgpnk/Projects/shokunin` and `/fast/scratch/hyaku`, plus Python reads of
`w1-results.json` and the reports. All exited 0 except the expected
`git ls-tree | grep -c` returning 0 matches (exit 1 from `grep -c`, printed `0`).

Also run, disclosed: `jj --no-pager status` and `jj --no-pager diff --summary -r @` as read-only
queries (jj snapshots the working copy on such reads). They show @ `221337955009` carrying a
large pre-existing deletion set under `.ufo/waves/round-36/assimilation/**` — unrelated to this
scope, already present before this seat, and not modified here. Git is the authority for every
count above.

Limits: counts are a point-in-time snapshot at `efc6b3ec` while other seats are live, so the
untracked set can grow (it grew 69 files after 11:31:52 during round 55 under the same
conditions). Content comparisons were made on the verdict/finding level, not by re-running any
seat's probes — nothing in this report claims a late seat's measurement was reproduced. The one
inference is marked `[INFERENCE]` above.

Tool installs: none. Scratch `/fast/scratch/hyaku/kama-r56/V04LateOutputs/` created with
`TMPDIR` set to it, used for nothing but the shell's temporary state, and removed before
yielding. No lane file, git index entry, jj change, or fleet-root tracked file was written.

**Confidence:** uncommitted status and all counts/hashes — high (direct `git status`/`ls-tree`
reads, manifest sha256s). "Late" classification — high for the 12 never-integrated seats
(absence from `c2c05e30` is a direct read); high for the 3 late-addition seats (mtimes + commit
contents). The cause of the lesson's defect-7 undercount — low, marked inference.
