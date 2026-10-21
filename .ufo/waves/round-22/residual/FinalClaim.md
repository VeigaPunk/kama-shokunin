# FinalClaim — round-22 C1 admissibility and no-axis-harm critique

Seat: KamaR22.FinalClaim (critic). Pinned `master=971d4549dff78e93327fbebaf1498e1c47db6661`
in a scratch `git clone --shared` under `residual/FinalClaim/clone`, which was
removed after review. There were no production edits, no installs, no delegation,
no server or service launch, and no network calls. Receipts are in
`.ufo/waves/round-22/residual/FinalClaim/FinalClaim/receipts.json` with
stdout/stderr, SHA-256 digests and exits.

## Verdict

**No blocking issue was found.** At 971d454, C1 ("calibration 7→7: the
`install_tree` helper separates errors from identity") is admissible on every
attacked axis, **pending the official clean committed-tree recipe run**. At this
commit the claim is declared but not yet measured: the lesson and SCORECARD
defer counts to an appended run, and no `runs/` exists. The reruns below found
no harm on any axis. There are four non-blocking corrections (N1–N4).

Axes attacked: helper versus producer level; diagnostic specificity and
exception categories; compatibility of successful digests; null historical
schema; race and external-loader caveats; correct lowest axis and score
7→7; no capability claimed.

## Evidence (each executed once, Python 3.14.8, euid 1000)

Pinned source digests:

| File | SHA-256 |
|---|---|
| producer (current) | `8c0dbb2b…62f3` |
| producer (frozen, 10271460) | `cec67949…e023` (matches the matrix `FROZEN_SHA`) |
| `install-io-grid.py` | `c10de62f…06dc` |
| population | `5b38422c…833d` |

| Command | Exit | Result |
|---|---|---|
| `install-io-grid.py --arm both --json` | 1 (expected) | frozen: 0/18 refused, **3 null + 15 partial digests**, 18/18 paired install_links refusals, controls 14/14. current: 18/18 refused, 0 null, 0 partial, `cause_is_fault` on all 18, controls 14/14 (six TypeError/interrupt propagation controls included) |
| `FinalClaim/probe.py`: frozen vs current on real trees, no mocks | 0 | success differential **13/13 identical**. Cases: regular, symlink, dangling link, directory, FIFO, hardlink, Unicode/space/colon name, newline name, 3 MiB multi-chunk file, 202 members, the lane `tools/` dir, and non-UTF-8 name (both arms raise `UnicodeEncodeError`, pre-existing). Five real-errno cases (listdir EACCES, lstat EACCES via a dir with no x bit, read EACCES ×3 including colon and non-UTF-8 names): the frozen helper **returned** in 5/5 (null, `e3b0…` empty digest, partial); the current helper refused in 5/5 with `__cause__` errno 13; the frozen producer setup block (install_tree→install_links→SetupError, emulated, no launch) **already refused in 5/5** |
| `FinalClaim/realtree.py` (read-only `~/.local/opt/llama-b11755`) | 0 | 51 members; frozen = current = `6c216313…5a2c`, equal to the R18 receipt pin; install_links problems [] |
| detail-erased mutant via `--current-source` | **0, `clean`** | replacing `(exc.strerror or type(exc).__name__)` with `''` in all three handlers passes all 32 rows. Patch and digest are retained |

I also used the peer receipts from FinalMutations, which existed before this
report. Its pristine run was clean on the same population digest, and all five
production mutants (three refusals deleted; catches broadened to Exception and
to BaseException) were killed with exit 1. This agrees with my current-arm
result.

## Findings per axis

- **Helper versus producer level: holds.** LOG, lesson, knowledge, QUALITY KQ30
  and README all say the claim is function-level with "no producer-level
  red-before". The probe shows the frozen producer block refused every real
  case, so that disclaimer is necessary and accurate. Producer acceptance is
  monotone non-increasing: the success path is byte-identical, and every
  changed branch now raises. So every current acceptance is also a frozen
  acceptance. The only new producer refusal is a vanished-member race, which
  is more conservative. The matrix `paired_problems` exposes the backstop
  (frozen 18/18) and does not take credit for it.
- **Diagnostic specificity and exception categories: holds, with N1/N2.** Only
  OSError is caught. TypeError and KeyboardInterrupt propagate (six controls).
  Broad-catch mutants die. The cause is chained (`from exc`, oracle-checked).
  Stage and `repr(member)` are oracle-checked. Real errors carry strerror
  ("Permission denied"). The matrix fixtures use single-argument exceptions,
  so they only ever produce the type-name fallback ("PermissionError").
- **Successful digest compatibility: holds.** Statically, the diff touches only
  the except clauses and docstrings. Dynamically, the 13/13 differential and
  the real-tree pin both match.
- **Null historical schema: holds.** `check-receipt.py` changes only a comment.
  `allow_none` is unchanged. Null is still INVALID under
  `--expect-install-tree-sha256` (selftest `tree-sha-absent-expect`). The
  comment "Legacy producers used null on listing failure" is accurate: the
  R18 producer `0c75c61` recorded `install_tree` with no install_links
  backstop. Knowledge correctly says the gate cannot infer omitted historical
  members.
- **Race and external-loader caveats: holds.** The knowledge section and lesson
  name these as out of scope: lstat→open swap (blocking FIFO), in-place
  rewrite, replacement after hashing or after launch, unpinned subdirectories,
  external system libraries and loader config. None is credited. The FIFO
  control only covers a FIFO that lstat sees, and is described that way.
- **Calibration lowest axis and 7→7: holds.** `shokunin.conf:52` assigns
  operability + calibration, and the scores are 8 and 7. Saturation is 8, so
  there is no waiver. The score is not inflated. Precedent is R16–R21.
- **No capability: holds.** No SCORECARD capability row is added and
  `registry/` is unchanged. The SKILL row is a gate entry in R21's existing
  style. The window "2 of 4 since round 20" is correct (R20 row, R21 = 1/4).

## Non-blocking corrections (smallest safe fix)

- **N1. Error-detail suffix is unmeasured.** The detail-erased mutant is
  `clean`. Stage, member and in-process cause are measured. The receipt keeps
  only `exc.code`, so the error category there depends on that unmeasured
  suffix. Fix: say in the knowledge/lesson text that `<error detail>` is
  informational and not matrix-measured. Changing the population is not the
  smaller fix, because it moves `population_sha256`.
- **N2. Producer `setup_error` wording changed without being stated.** For
  stat/read faults it was `X:unreadable` / `X:not-hashed` /
  `a:EACCES;b:EACCES`. It is now `read:'X':Permission denied`, naming only
  the first failing member. The `install-tree-unpinnable:` prefix is stable,
  and e2e's `startswith` is the only consumer of the text. Fix: one sentence
  in the results section.
- **N3. The "lowest assigned" wording hides a tie.** Unassigned depth and
  adjacency are also 7. The AXES rule ("lowest-scoring non-retired") is still
  met by working calibration. Optional fix: note the tie.
- **N4. Precondition for admission.** During review the production lane was
  dirty: L1's uncommitted `corpus/SOURCES.md` and lesson edits (S087/S088),
  plus untracked residual output, including peers' nested scratch clones.
  `run.py` refuses a dirty tree. Fix: remove scaffold clones (don't commit
  them as embedded repos), commit, then measure. This verdict covers the
  971d454 bytes only.

Not raised, as scope expansion: the non-UTF-8 name `UnicodeEncodeError`
boundary (pre-existing, identical in both arms, fails closed as an
internal_fault), scandir or atomic snapshots, and receipt-schema tightening.
