# RerunC1FullMutants — C1 supporting evidence (full isolation mutant run) re-executed at the lane tip

**Verdict: holds.** The C1 supporting full run reproduces exactly at
`fa3b62ae6475d111eb466d79af616aeebb08bbb9`: exit 0, pristine passed,
28 mutants, 26 killed, survivors `M17-ref-shadow` and `M20-log-sha-shape`,
and the produced JSON is byte-identical (sha256
`75ad1e03dff31571dcfe85eca26d7154e509daa60ca092238d6942459c56eda1`) to the
committed `.ufo/waves/round-25/final/c1/c1-tip-mutants.json`. Zero
differences in the killed set, the surviving set, the retired set, the
per-mutant `grid_exit`, the per-mutant `failed_rows` and the `error` field.
No defect found in this evidence.

Scope: this seat attacked only the C1 supporting evidence (the full mutant
run). It did not judge the C1 axis fit, which the L1 already filed as
contested (`SCORECARD.md:1267-1276`, answered at `SCORECARD.md:1278-1290`),
and it wrote no lane production file.

## 1. What was run, where, and with which bytes

Per the lane contract a git-writing check runs only in a private clone.

```
git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin \
    /fast/scratch/hyaku/kama-r25a2w2/RerunC1FullMutants/clone
```
exit code 0.

```
cd /fast/scratch/hyaku/kama-r25a2w2/RerunC1FullMutants/clone
git checkout fa3b62ae6475d111eb466d79af616aeebb08bbb9
```
exit code 0. `git log -1` → `fa3b62ae6475d111eb466d79af616aeebb08bbb9
2026-10-22 06:54:34 -0300 round-25: context-capacity entry, S106-S113, SKILL
rows and routed wording fixes, KQ36, lesson, SCORECARD, LOG, errata, C1
full-run evidence and the attempt-2 build wave record`.

The clone's `tests/report-audit/isolation-mutants.py` resolves its lane
paths from `Path(__file__).resolve().parents[2]`
(`tests/report-audit/isolation-mutants.py:55-57`), so the whole run — the
auditor and the grid — executed inside the clone. No lane file was mutated
and no lane index, worktree or ref was touched. No llama-server child was
started (this seat has no port range).

Environment: python 3.14.8, git 2.56.0.

### Byte identity of the measured inputs across the two runs

The committed evidence was produced at `1fc41e34`
(`SCORECARD.md:1260`, `corpus/lessons/round-25.md` §C1 result); this
re-run is at `fa3b62ae`. The measured inputs are the same bytes:

```
git diff --numstat 1fc41e346853afd98cbd7010af5db4e54dc877f7 \
    fa3b62ae6475d111eb466d79af616aeebb08bbb9 \
    -- tools/report-landing-audit.py tests/report-audit/repo-state-grid.py
```
exit code 0, **empty output** — the auditor and the grid are byte-identical
between the two commits.

```
git show <commit>:tools/report-landing-audit.py | sha256sum
  1fc41e34: b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f
  fa3b62ae: b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f
git show <commit>:tests/report-audit/repo-state-grid.py | sha256sum
  1fc41e34: 994186952c5d720bd8494a00b930fd6edcec4951ba1e942ed409c510fc23d604
  fa3b62ae: 994186952c5d720bd8494a00b930fd6edcec4951ba1e942ed409c510fc23d604
```

The instrument itself differs between the two commits by **7 docstring lines
only** (`git diff 1fc41e34 fa3b62ae -- tests/report-audit/isolation-mutants.py`:
one `+` hunk, no `-` lines, inside the module docstring at
`tests/report-audit/isolation-mutants.py:33-39`). The `MUTANTS` list
(`:59-138`), the `RETIRED` list (`:140-162`) and `main()` (`:178-237`) are
unchanged. Instrument sha256: `bdd4250a…` at `1fc41e34`,
`67f57f1a…` at `fa3b62ae` (docstring only).

So the re-run is a true re-measurement of the same instrument on the same
auditor and the same grid, and the expected outcome is bit-for-bit equality.

## 2. The run

```
cd /fast/scratch/hyaku/kama-r25a2w2/RerunC1FullMutants/clone
python3 tests/report-audit/isolation-mutants.py --json \
    > /fast/scratch/hyaku/kama-r25a2w2/RerunC1FullMutants/run.json \
    2> /fast/scratch/hyaku/kama-r25a2w2/RerunC1FullMutants/run.err
```
**exit code 0**. Wall time 983.45 s (16 min 23 s). `run.json` 5959 bytes,
`run.err` 0 bytes (the instrument prints `could-not-evaluate` to stderr and
exits 2 on any failure; an empty stderr with exit 0 is the pass path,
`tests/report-audit/isolation-mutants.py:237`).

Summary printed by the produced JSON:

| field | value |
|---|---|
| `pristine` | `passed` |
| `mutants` | 28 |
| `killed` | 26 |
| `surviving` | `['M17-ref-shadow', 'M20-log-sha-shape']` |
| `retired` | `['M14-promisor-config', 'M22-promisor-pack', 'M27-promisor-boolean', 'M29-promisor-pack-pairing']` |

Clone state after the run: `git status --porcelain=v1` → exit 0, empty
output. The instrument mutates only temporary copies
(`tests/report-audit/isolation-mutants.py:211-212`), so the clone tree is
unchanged.

## 3. Diff table versus the committed run

Committed file: `.ufo/waves/round-25/final/c1/c1-tip-mutants.json`
(sha256 `75ad1e03dff31571dcfe85eca26d7154e509daa60ca092238d6942459c56eda1`).
Re-run file: `out/RerunC1FullMutants/c1-tip-mutants-rerun-fa3b62ae.json`
(sha256 `75ad1e03dff31571dcfe85eca26d7154e509daa60ca092238d6942459c56eda1`).

```
cmp <re-run> <committed>   -> exit code 0 (byte identical)
python3 compare.py <re-run> <committed>   -> exit code 0, "differences: 0"
```

### Summary rows

| item | committed | re-run at fa3b62ae | same |
|---|---|---|---|
| pristine | passed | passed | yes |
| mutants | 28 | 28 | yes |
| killed | 26 | 26 | yes |
| surviving | `['M17-ref-shadow', 'M20-log-sha-shape']` | `['M17-ref-shadow', 'M20-log-sha-shape']` | yes |
| retired | `['M14-promisor-config', 'M22-promisor-pack', 'M27-promisor-boolean', 'M29-promisor-pack-pairing']` | same four, same order | yes |
| retired_detail | 4 entries (id, literal, replaced_by, why) | identical, field for field | yes |

### Per-mutant rows (all 28)

| mutant | killed (committed → re-run) | grid_exit (committed → re-run) | failed_rows (committed → re-run) | same |
|---|---|---|---|---|
| M01-replace-objects | True → True | 1 → 1 | F03-replace-hides-omission, F04-replace-fabricated-citation, F05-replace-fleet-report | yes |
| M02-lazy-fetch | True → True | 1 → 1 | F06-lazy-fetch-command, F27-filter-only-promisor-remote | yes |
| M03-log-encoding | True → True | 1 → 1 | F22-utf16-log-cutoff | yes |
| M04-log-follow | True → True | 1 → 1 | F07-log-follow-cutoff | yes |
| M05-log-showroot | True → True | 1 → 1 | F08-log-showroot-cutoff | yes |
| M06-log-signature | True → True | 1 → 1 | F09-signature-program | yes |
| M07-log-mailmap | True → True | 1 → 1 | F14-mailmap-fifo | yes |
| M09-strict-default | True → True | 1 → 1 | F02-report-invalid-utf8, F16-errata-invalid-utf8 | yes |
| M10-log-surrogates | True → True | 1 → 1 | F18-bad-byte-unrelated-subject, F19-bad-byte-round-subject | yes |
| M11-listing-surrogates | True → True | 1 → 1 | F20-quotepath-open-range | yes |
| M12-shallow-check | True → True | 1 → 1 | F10-shallow-lane, F28-shallow-fleet | yes |
| M13-grafts-check | True → True | 1 → 1 | F11-grafts-lane | yes |
| M15-object-format | True → True | 1 → 1 | F15-sha256-lane | yes |
| M16-top-level | True → True | 1 → 1 | F21-nested-subdirectory-lane | yes |
| **M17-ref-shadow** | False → False | 0 → 0 | `[]` → `[]` | yes |
| M18-branch-heads | True → True | 1 → 1 | F12-tag-shadows-branch, F29-broken-branch-same-named-tag | yes |
| M19-errata-hex | True → True | 1 → 1 | F17-errata-revision-correction | yes |
| **M20-log-sha-shape** | False → False | 0 → 0 | `[]` → `[]` | yes |
| M21-newlines | True → True | 1 → 1 | C08-cr-only-report | yes |
| M23-strict-decode-catch | True → True | 1 → 1 | F02-report-invalid-utf8, F16-errata-invalid-utf8 | yes |
| M24-catch-all | True → True | 1 → 1 | F24-huge-round-number | yes |
| M25-timestamp-shape | True → True | 1 → 1 | F26-huge-author-timestamp | yes |
| M26-record-separators | True → True | 1 → 1 | F25-subject-record-injection | yes |
| M28-correction-casefold | True → True | 1 → 1 | C11-uppercase-errata-correction | yes |
| M30-fleet-history-check | True → True | 1 → 1 | F28-shallow-fleet | yes |
| M31-git-timeout | True → True | 1 → 1 | F30-config-include-fifo | yes |
| M32-grafts-content | True → True | 1 → 1 | C13-comment-only-grafts | yes |
| M33-ref-shadow-bare-objects | True → True | 1 → 1 | F13-ref-named-abbreviation | yes |

Every row also has `error: null` in both files. Full table with the
raw fields is in `out/RerunC1FullMutants/diff-table-fa3b62ae-vs-committed.md`.

**Difference count: 0.**

## 4. Supplementary checks (same target, no extra claim)

1. **The C1 claim value itself, re-measured at the tip.** The registered
   command (`preregistration.json` `C1.command`) in the clone at
   `fa3b62ae`:

   ```
   python3 -c "import importlib.util as u;s=u.spec_from_file_location('m','tests/report-audit/isolation-mutants.py');m=u.module_from_spec(s);s.loader.exec_module(m);src=m.AUDIT.read_text();bad=[n for n,o,_ in m.MUTANTS if src.count(o)!=1];print('registered',len(m.MUTANTS),'stale',len(bad),bad)"
   ```
   output `registered 28 stale 0 []`, exit code 0. This matches the value
   recorded in `SCORECARD.md:1260` and `corpus/lessons/round-25.md` §C1
   result for `1fc41e34`, and it holds at the tip.

2. **Third independent run exists.** The wave-1 seat
   `KamaR25a2.ReviewerC1Patch` already ran the same instrument at
   `1fc41e34` and committed
   `.ufo/waves/round-25/a2-build/out/ReviewerC1Patch/full-mutants.json`;
   its summary is `pristine passed, mutants 28, killed 26, surviving
   ['M17-ref-shadow','M20-log-sha-shape']`, `retired` the same four ids.
   Two prior runs and this one agree. (Read only; that file is modified in
   the lane working tree by its owner and I did not touch it.)

3. **The two survivors are stable, not flaky.** `M17-ref-shadow` survives
   with `grid_exit 0` and no failed row in every run; `M20-log-sha-shape`
   likewise. `M33-ref-shadow-bare-objects` is killed by `F13-ref-named-abbreviation`
   in every run, which is the round-25 change (the second call site of the
   M17 element is now registered under a new id, no id reused or retired).

## 5. Risks, limits and what this does not establish

- **The axis fit is not settled by this seat.** This run only shows that the
  C1 supporting evidence is reproducible. The dispute filed by
  `KamaR25a2.CriticC1Calibration` (`SCORECARD.md:1267-1276`) — that the
  registered command counts instrument-to-auditor anchor mismatches rather
  than demonstrated SCORECARD/SHONEN self-assessment mismatches — is
  untouched by this evidence. It has since been answered in this same
  falsify wave by `KamaR25a2.CriticC1AxisFit`, whose correction is filed at
  `SCORECARD.md:1278-1290`: "**C1's axis fit to calibration is not
  established**", while "the measured value stands as repair evidence". My
  re-run neither supports nor weakens that finding; it only confirms the
  measured value is reproducible.
- **M17 is a survivor with no reachable caller.** The re-run confirms the
  survival but does not explain it. The cause (no caller in this tree can
  make the `lookup()` guard fire, per
  `.ufo/waves/round-25/a2-build/advice/ReviewerC1Patch.md` F1) is another
  seat's finding; this seat did not re-derive it. No necessity or
  defensive-only claim is made or supported here.
- **The run is one machine, one git version.** git 2.56.0 and python
  3.14.8 on Arch Linux. The grid builds fresh fixtures per case
  (`tests/report-audit/repo-state-grid.py:104-120`) and pins git config and
  identities (`repo-state-grid.py:46-52`), so the outcome should be
  environment-independent for this surface, but that is a reading, not a
  measurement on other hosts.
- **The committed evidence has no source binding beyond this report.** The
  committed sidecar `.ufo/waves/round-25/final/c1/c1-tip-mutants.exit`
  holds `exit=0` and `.ufo/waves/round-25/final/c1/c1-tip-mutants.time`
  holds `real 16m25.987s`; this re-run took 983.45 s (16 m 23.45 s),
  2.5 seconds apart from the recorded figure. The grid carries 46 cases
  (`CASES` in `tests/report-audit/repo-state-grid.py`, counted by import:
  46), so each of the 28 mutants re-runs the whole case set, and a
  two-second spread over that work is the expected variance.
  [INFERENCE] the sidecars are consistent with the committed JSON having
  been produced by the same instrument at the same commit; I did not
  re-derive the committed run's timestamp from the filesystem.

## 6. Smallest correction

None required for this evidence. The C1 supporting evidence stands as
committed. If the L1 wants the reproduction recorded, the smallest
addition is one line in `corpus/lessons/round-25.md` §C1 result noting
that the full run was reproduced at `fa3b62ae` with an identical JSON
(sha256 `75ad1e03…`), exit 0 — a sentence, no new claim, no change to any
number.

## 7. Files I wrote

Under the lane (this seat's exclusive output directory and its advice
report only):

- `.ufo/waves/round-25/a2-falsify/advice/RerunC1FullMutants.md` — this report
- `.ufo/waves/round-25/a2-falsify/out/RerunC1FullMutants/c1-tip-mutants-rerun-fa3b62ae.json` — the re-run JSON (5959 bytes, sha256 `75ad1e03…`)
- `.ufo/waves/round-25/a2-falsify/out/RerunC1FullMutants/c1-tip-mutants-rerun-fa3b62ae.exit` — `exit=0`
- `.ufo/waves/round-25/a2-falsify/out/RerunC1FullMutants/c1-tip-mutants-rerun-fa3b62ae.err` — 0 bytes (empty stderr)
- `.ufo/waves/round-25/a2-falsify/out/RerunC1FullMutants/diff-table-fa3b62ae-vs-committed.md` — the full diff table
- `.ufo/waves/round-25/a2-falsify/out/RerunC1FullMutants/compare.py` — the comparison script used
- `.ufo/waves/round-25/a2-falsify/out/RerunC1FullMutants/run-record.txt` — commands, exit codes, environment

Heavy scratch (outside the lane):

- `/fast/scratch/hyaku/kama-r25a2w2/RerunC1FullMutants/clone/` — the private clone at `fa3b62ae`
- `/fast/scratch/hyaku/kama-r25a2w2/RerunC1FullMutants/run.json`, `run.err`, `exitcode.txt`, `compare.out`, `diff-table.md`, `compare.py`

No lane production file was modified. No commit, push, `git add`, checkout,
reset or stash was run in the lane; no `jj` command was run at the fleet
root or in the lane. No llama-server child was started.

## 8. Tool installs

None. The run needed only `python3` (3.14.8) and `git` (2.56.0), both
already present on the host. No pacman, uv, cargo or npm transaction was
made by this seat.
