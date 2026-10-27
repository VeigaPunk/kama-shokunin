# X11ScratchHygiene — Round 59 C1/C2 scratch-hygiene falsification

Axes: operability (8), calibration (lowest assigned: 7). Attacked clauses: frozen C1 predicate (`round59-c1-counter.py` operand at the measured tip) and frozen C2 predicate (`round59-c2-counter.py` derives closure metadata from named repo/ref inputs and fails closed). Seat work is a falsification, not the judge; all results advisory.

Inputs: lane `/home/vgpnk/Projects/shokunin/kama-shokunin`; C1 tip `aca8d0067ea25627c5015c2193c843965148bc8e`; C2 tip `2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35`. Scratch `S=/fast/scratch/hyaku/kama-r59/X11ScratchHygiene`, created with `mkdir -p`, `TMPDIR=$S` on every counter invocation, `HYAKU_SCRATCH` unset (`env -u HYAKU_SCRATCH`; pre-run `env | grep -i hyaku` empty). No installs, no `npx`/`uv`/`pacman` use. Toolchain as present: Python 3.14.8, git 2.56.0, `/usr/bin/strace`.

Fleet-repo observation, before any verdict: the assignment states fleet HEAD `3f3dd97345ef1aedfdaec818c9e58675d4f41e3f`, but `git -C /home/vgpnk/Projects/shokunin rev-parse HEAD` returned `0f99f606120d0c884656c6e7a290f0e8f33c2181` ("rounds ledger: tabi r40 closure"). `3f3dd973` is an ancestor; `MANIFEST.json` differs only by +41 lines (tabi r40 closure), blobs `73fe5893` → `c2d7e4c2`; kama closure rows are identical at both revisions and end at round 57 (`rejected-honest-stop`); no kama r58/r59 closure row exists. Counters were run with the live `HEAD` as the frozen C2 command specifies (`--fleet-ref HEAD`); the assignment's literal `3f3dd973` was also probed (below).

## C1 — operability + scratch isolation

Command (exit 0):
```sh
cd $S && env -u HYAKU_SCRATCH TMPDIR=$S strace -f -qq -y \
  -e trace=openat,open,creat,mkdir,mkdirat,rename,renameat,renameat2,unlink,unlinkat,rmdir,link,linkat,symlink,symlinkat \
  -o $S/strace-c1.log \
  python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-c1-counter.py \
  --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --tip aca8d0067ea25627c5015c2193c843965148bc8e --out $S/c1.out
```
Output: `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`; 20 detail lines: `genuine accept exit=0`, `B1/B2/B3 accept exit=0`, `N01`–`N16` `reject exit=1`. C1 predicate holds at this tip for this enumerated battery (bounded to the frozen fixture set; not S517/S518 discernment progress).

Scratch evidence (strace, exact):
- Work root created under the supplied TMPDIR, not a default: `mkdirat(... "/fast/scratch/hyaku/kama-r59/X11ScratchHygiene/r59-c1-ojkmkhc6")`; fixtures and checker written beneath it (`.../r59-c1-ojkmkhc6/genuine`, `.../outcome-checker.py`); the checker's own nested scratch dirs were created inside that root (`.../r59-c1-ojkmkhc6/r59-c1-9qyhqevh`, etc.).
- Cleanup completed: all fixture bytes unlinked (`unlinkat(...genuine/.git/hooks, "update.sample", 0) = 0`, `unlinkat(...genuine, ".git", AT_REMOVEDIR) = 0`, `unlinkat(...r59-c1-ojkmkhc6, "genuine", AT_REMOVEDIR) = 0`) then `rmdir("/fast/scratch/hyaku/kama-r59/X11ScratchHygiene/r59-c1-ojkmkhc6") = 0`. Post-run `find $S -maxdepth 1 -name 'r59-c1-*'` and `find /tmp -maxdepth 1 -name 'r59-c1-*'` returned nothing.
- `/tmp` writes: 0. Across all traces, mutating syscalls rooted at `/tmp` = 0 (`strace-c1.log total=6180 underS=6180 projects=0 tmpdir=0`). A raw `grep '/tmp'` on the log yields 1752 hits, all git object filenames `".git/objects/<xx>/tmp_obj_*"` inside the scratch fixture — not the `/tmp` directory.
- Write scope: every mutating syscall (create/write/mkdir/unlink/rmdir/rename) in the trace lies under `$S`; 0 touch `/home/vgpnk/Projects/...`; the only non-`$S` mutation is `openat(AT_FDCWD<S>, "/dev/null", O_RDWR)` from subprocess capture. Lane `git status --porcelain` shows no tracked modification.
- Error paths leave no tree: tip `5d957d24` (pre-fixture; `blob()` raises) → exit 2, `could-not-evaluate: missing committed blob tools/round59-battery-outcome-check.py`; work root `r59-c1-wgv0z338` was created and `rmdir(...) = 0`'d; `--checker /dev/null` → exit 2 `could-not-evaluate: checker file absent`, no `r59-c1-*` left; invalid tip → exit 2 `could-not-evaluate: invalid tip` before any mkdtemp.
- GIT_* hardening: C1 strips `GIT_*` (`round59-c1-counter.py:28`); hostile `GIT_DIR=<lane>/.git` with `--repo <empty dir>` → exit 2 (correct refusal), no leak.

Residual operability nit (not a frozen-control failure): `TMPDIR=/proc/nope` yields an uncaught `FileNotFoundError` traceback from `root_for`/`os.makedirs`, exit 1. It fails closed (non-zero, no fixture evaluation) but unstructured, and it is a crash rather than `could-not-evaluate`.

## C2 — calibration + scratch isolation

Command (exit 0):
```sh
cd $S && env -u HYAKU_SCRATCH TMPDIR=$S strace -f -qq -y \
  -e trace=openat,open,creat,mkdir,mkdirat,rename,renameat,unlink,unlinkat,rmdir -o $S/strace-c2.log \
  python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-c2-counter.py \
  --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --tip 2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35 --fleet-ref HEAD --out $S/c2.out
```
Output: `tip=2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35 fleet=0f99f606120d0c884656c6e7a290f0e8f33c2181 maxN=57 manifest=rejected-honest-stop`, `rows=44 mismatches=0 met=True`, every field 0. Genuine frozen control passes and binds the exact lane tip bytes plus a freshly resolved live fleet revision.

Extra ref probe (not a score claim): `--fleet-ref 3f3dd97345ef1aedfdaec818c9e58675d4f41e3f` → exit 0, `fleet=3f3dd973...`, same `maxN=57 manifest=rejected-honest-stop`, mismatches=0.

Scratch evidence: C2 creates no temp tree (`import tempfile` is unused; no `mkdtemp`); trace contains 7 mutating syscalls, all `/dev/null` captures, `tmpdir=0`, `projects=0`, and nothing left in `$S`.

Row/derivation evidence at `2c7443ab`:
- Calibration row has no 40-hex literal (`grep -oE '[0-9a-f]{40}'` → empty) and no literal `N (outside closures on record)` pattern; it names `tools/round59-c2-counter.py ... --fleet-ref HEAD` and states pointer `corpus/lessons/round-57-verifier-spotcheck.md` (`rejected-honest-stop`), `including round 57`.
- Committed spotcheck files at tip: 44, max round 57, and MANIFEST kama round 57 closure is `rejected-honest-stop`; no round 58 closure. Pointer/round/verdict agree with derived inputs.

Single-field controls, run in a scratch clone (`S/c2fix`, `git rev-parse --show-toplevel` asserted equal to `$D` before every commit; commits made with inline `-c user.name=kama-r59-control -c user.email=kama-r59@invalid`, never outside `$D`; each mutation applied to real `2c7443ab` SCORECARD bytes and committed):
| mutant | counter exit | observed |
|---|---|---|
| pointer round 57→56 | 1 | `mismatches=1 met=False pointer_round=1` |
| insert pinned 40-hex `8f7f58cd…` into row | 1 | `mismatches=1 met=False pinned_fleet_revision=1` |
| replace `round59-c2-counter.py` with `round58-c2-counter.py` | 1 | `mismatches=1 met=False count_command=1` |
| pointer verdict `(rejected-honest-stop)`→`(admitted)` | 1 | `mismatches=1 met=False pointer_verdict=1` |
| `including round 57`→`including round 56` | 1 | `mismatches=1 met=False including_round=1` |

Derivation (not pinned) probes on the same clone: add `corpus/lessons/round-58-verifier-spotcheck.md` → `rows=45 maxN=58 manifest=None`, exit 1 (3 mismatches: pointer_round, pointer_verdict, including_round) — correctly refuses when no current external verdict exists; remove round-57 and round-58 spotchecks → `rows=43 maxN=56`, exit 1 (`pointer_round=1 including_round=1`). Count and max round move with committed bytes.

Fail-closed probes: bogus `--fleet-ref 0000…` and bogus `--tip 1111…` → exit 2 `could-not-evaluate: unresolvable lane tip or fleet ref`.

Calibration risk (advisory; frozen predicate still passes under a clean env, which is how the official runs above were made; do not mutate frozen counters now): C2's `git()` does not scrub `GIT_*` while C1's does (`round59-c1-counter.py:28`; C2 has no equivalent). Reproduced in scratch: with `GIT_DIR=$S/c2fix/.git` and `--repo $S/emptyrepo` (a non-repo empty dir), C2 printed `met=True`, `fleet=acad1de18983a8fef529e5ae38c784199e33a393` (a fixture commit), while the named fleet HEAD is `0f99f606…`; the same command without `GIT_DIR` exits 2. So printed revisions can be redirected by inherited environment even though the named `--repo` is not the tree read. Recommend C2 mirror C1's env scrub in a future freeze (not this one).

## Verdicts

- Operability (8): no falsifying counterexample found. Both counters run under `TMPDIR=$S` with `HYAKU_SCRATCH` unset, write nothing rooted at `/tmp`, create no file outside their scratch root, and remove every tree on success and on the exercised error paths (`missing blob`, `checker absent`, `invalid tip`). C1: `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True` at `aca8d006`.
- Calibration (7): C2 frozen predicate holds at `2c7443ab` against live fleet `HEAD` (`mismatches=0`, `maxN=57`, `rejected-honest-stop`, `rows=44`), passes identically against literal `3f3dd973`, rejects each of five single-field row mutations, re-derives count/max-round from committed bytes, and fails closed on unreadable refs. Residual risks: the assignment's fleet HEAD was stale by one commit (tabi-only MANIFEST delta), and C2 inherits `GIT_*` environment (demonstrated misbinding). No external S517/S518 spot-check is recorded here, so no discernment progress is claimed.

Scratch hygiene of this seat: `S` (including the 566M clone and all traces) removed after gathering this evidence; no lane/fleet source edits, no commits, no peer/fleet writes. Observation only (not mine, not evaluated): live peer scratch existed at `…/kama-r59/R16CheckerTamper/r59-c1-*` during inspection.
