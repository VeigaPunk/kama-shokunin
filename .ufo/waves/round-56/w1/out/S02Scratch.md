# S02Scratch — hardcoded `/tmp` scratch root in the committed counter, harness and spec

Seat: S02Scratch (operability, round-56 falsification). Read-only audit of the lane tree; no
lane file was written except this report and `out/S02Scratch/` receipts. No tools installed.

## Verdict

**No literal `/tmp` string exists in any committed round-56 counter, harness, or spec artifact.**
`grep -n "/tmp" tools/round56*.py` → **zero matches**. `grep -c "/tmp" preregistration.json` → 0.

**But the frozen counter has an *effective* `/tmp` scratch root**, reached by default and
silently: `tools/round56-replay-code-audit.py:886` resolves the scratch root as
`a.scratch or tempfile.gettempdir()`, and `tempfile.gettempdir()` returns `/tmp` when `TMPDIR`
is unset **or names a directory that does not exist** (verified below). This is a default,
not a hardcode — severity MEDIUM, operability only. It does not falsify C1 or C2: the C1
harness path (`tools/round56-env-leg-test.py` → `env_leg`) never touches scratch.

The only *hardcoded absolute* scratch root in the committed surfaces is **not** `/tmp`:
`tools/round56-env-leg-battery.py:37` → `/fast/scratch/hyaku/kama-r56/l1-battery`.

Frozen artifacts audited are the frozen bytes (working tree == freeze tip == frozen hashes):

```
tools/round56-replay-code-audit.py  fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f  (== frozen)
tools/round56-prereg-check.py       c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853  (== frozen)
tools/round56-env-leg-battery.py    79b19596c475863dbd5fe5c03511996b050a69d500f2671385069c02d17c335c
tools/round56-env-leg-test.py       ec7a2519f6d4b2e1bd08a7ead042a53c7b60e2f58af8e4db008dfd661acf82ac
```
(blob digests via `git -C lane cat-file -p efc6b3ec6fb6ea308c15855e9b8b62856f4255b7:<file> | sha256sum`,
identical to the working-tree `sha256sum`.)

## Exact locations

| # | Surface | Location | What it is | `/tmp`? |
|---|---|---|---|---|
| 1 | counter | `tools/round56-replay-code-audit.py:881` | `--scratch` default `None` | indirect |
| 2 | counter | `tools/round56-replay-code-audit.py:886` | `root = a.scratch or tempfile.gettempdir()` — **the effective `/tmp` root** | **yes (fallback)** |
| 3 | counter | `tools/round56-replay-code-audit.py:888` | `S = tempfile.mkdtemp(prefix="r53c1-", dir=root)` — archive (~75 MB), model, extracted `llama.cpp` tree and 3 receipt work dirs land here | inherits #2 |
| 4 | counter | `tools/round56-replay-code-audit.py:969` | `shutil.rmtree(S, ignore_errors=True)` — cleanup only on normal `finally` (SIGKILL leaves `r53c1-*`) | — |
| 5 | counter doc | `tools/round56-replay-code-audit.py:99` | "everything else lives under `--scratch` (default TMPDIR)" — documents the fallback, no warning | — |
| 6 | counter | `tools/round56-replay-code-audit.py:617` | child env `TMPDIR = S/tmp-<tag>` (correct: replay scratch is inside `S`, never `/tmp`) | no |
| 7 | harness (test) | `tools/round56-env-leg-test.py` (36 lines, imports at `:5-9`) | no `tempfile`, no `TMPDIR`, no scratch at all; child `sleep` inherits the parent env | **no** |
| 8 | harness (battery) | `tools/round56-env-leg-battery.py:37` | `scratch = pathlib.Path("/fast/scratch/hyaku/kama-r56/l1-battery")` — hardcoded absolute scratch root, **ignores `TMPDIR`, no `--scratch` flag** | no (`/fast`) |
| 9 | harness (battery) | `tools/round56-env-leg-battery.py:10-14, 36, 26` | receipts `OUT = LANE/.ufo/waves/round-56/measured`, `out.write_text(...)` — battery writes the lane (not a scratch root, but see F2) | no |
| 10 | spec | `.ufo/waves/round-56/w1/spec.json:9`; `.ufo/waves/round-56/build_spec.py:23` | prose only: "Per-seat scratch is `/fast/scratch/hyaku/kama-r56/<SeatName>/`; create it, set TMPDIR explicitly… Never use /tmp for evidence or large scratch." Correct instruction, **but no seat command names `--scratch`** (`grep -c -- '--scratch' spec.json` → 0) | **no** |
| 11 | spec | `.ufo/waves/round-56/w1/spec.json:339` (item text), `build_spec.py:76` | this seat's own text mentions `/tmp` — self-reference, not a scratch root | no |
| 12 | spec/prereg | `.ufo/waves/round-56/preregistration.json` | `grep -nE "scratch|tmp|command"` → **no matches** | **no** |
| 13 | copies | `w1/dispatch.json:384,713,883`, `w1/validate.out:384,713,883`, `w1/out/swarm-registry.json:366` | verbatim copies of #10/#11 prose | no |
| 14 | sources | `.ufo/waves/round-56/sources/ld.so.8.html:538` | upstream `ld.so(8)` text "the default is `/var/tmp`" — substring match on `/tmp`, not a scratch root | no |

## Evidence (commands run, exact output)

Environment this seat runs in — no `TMPDIR` at all:

```
$ env | grep -iE '^(TMPDIR|TMP|TEMP)='   →  NO TMP* ENV SET
$ env -u TMPDIR python3 -c 'import tempfile;print(tempfile.gettempdir())'
/tmp
$ stat -c '%A %U:%G %n' /tmp
drwxrwxrwt root:root /tmp          # shared, 1777; xfs, 125G avail
```

E1 — real counter, `TMPDIR` unset (`/tmp` is used):

```
$ env -u TMPDIR strace -f -e trace=mkdir,mkdirat \
    python3 tools/round56-replay-code-audit.py --repo /nonexistent-repo --tip HEAD
counter_exit=2
mkdir("/tmp", 0777)             = -1 EEXIST (File exists)
mkdir("/tmp/r53c1-uaepock3", 0700) = 0
```
receipt: `out/S02Scratch/mkdir2.trace.txt`; stdout `could-not-evaluate: git rev-parse --verify HEAD^{commit}: fatal: cannot change to '/nonexistent-repo'` (exit 2 before any download). After the run `ls -d /tmp/r53c1-*` → none: `finally` cleanup (#4) works.

E2 — `TMPDIR` set to a **non-existent** directory: silent fallback to `/tmp`, the named dir is never even created:

```
$ TMPDIR=/fast/scratch/hyaku/kama-r56/DOES-NOT-EXIST strace -f -e trace=mkdir,mkdirat \
    python3 tools/round56-replay-code-audit.py --repo /nonexistent-repo --tip HEAD
counter_exit=2
mkdir("/tmp", 0777)                = -1 EEXIST (File exists)
mkdir("/tmp/r53c1-wl3kdy9u", 0700) = 0
$ ls -d /fast/scratch/hyaku/kama-r56/DOES-NOT-EXIST
ls: cannot access ...: No such file or directory
```
receipt: `out/S02Scratch/mkdir3.trace.txt`. **No warning, no error**: the operator believes `TMPDIR` was honoured; evidence landed in shared `/tmp`.

E3 — `TMPDIR` that exists is honoured:

```
$ TMPDIR=/fast/scratch/hyaku/kama-r56/S02Scratch python3 -c 'import tempfile;print(tempfile.gettempdir())'
/fast/scratch/hyaku/kama-r56/S02Scratch
```

E4 — `--scratch` works and touches no `/tmp`:

```
$ env -u TMPDIR strace -f -e trace=mkdir,mkdirat python3 tools/round56-replay-code-audit.py \
    --repo /nonexistent-repo --tip HEAD --scratch /fast/scratch/hyaku/kama-r56/S02Scratch/proof
counter_exit=2
mkdir("/fast/scratch/hyaku/kama-r56/S02Scratch/proof/r53c1-eq7v4trl", 0700) = 0
```
receipt: `out/S02Scratch/mkdir4.trace.txt`; no `/tmp` line; scratch cleaned (`ls -A proof` → empty).

E5 — no `/tmp` literal anywhere in the tools:

```
$ grep -n "/tmp" tools/round56*.py          →  NONE
$ grep -c "TMPDIR" tools/round56*.py        →  battery 0, test 0, prereg-check 0, replay-audit 4
   (replay-audit's 4 are docstring :19, :99, child-env :617, help :881 — none sets its own root)
```

## Impact and exploit path (operability)

- **F1 (MEDIUM, counter default).** A seat or verifier that runs the counter as the docstring
  prescribes (`--repo`/`--tip` only, `:99`) with `TMPDIR` unset — the state of this seat's
  environment — writes the counter's whole working set to shared `/tmp`: own archive download
  (`ARCHIVE_URL`, docstring `:152` "the replay downloads ~75 MB first"), model file, extracted
  `llama.cpp` tree and three receipt work dirs, all inside one 0700 `r53c1-*` dir. Two ways to
  lose the evidence: (a) `SIGKILL`/OOM/crash skips `:969`, leaving `r53c1-*` under `/tmp`
  (host-wide, shared with 64 seats); (b) `TMPDIR` pointing at a not-yet-created or misspelled
  dir silently resolves to `/tmp` (E2) while the run's own receipts look normal — a
  scratch-location/provenance claim the operator cannot see is wrong. Violates the wave rule
  (spec `:9`) "Never use /tmp for evidence or large scratch". No privilege boundary is crossed:
  `S` is 0700 under sticky 1777 `/tmp`.
- **F2 (MEDIUM, battery write bounds).** `tools/round56-env-leg-battery.py` hardcodes its scratch
  at `:37` (ignores `TMPDIR`, no `--scratch` → on a host without a writable `/fast`,
  `scratch.mkdir(parents=True)` at `:38` fails against `/`, not a `/tmp` fallback) **and** writes
  its three receipts over the lane's frozen measured files (`:11`, `:26`), i.e.
  `measured/base-c1.out`, `build-c1.out`, `m-drop-ldaudit.out`. The lane is READ-ONLY for seats,
  so a seat following the spec and running the battery silently overwrites the L1's C1
  falsification receipts (no `out.exists()` guard, no digest check).
- `tools/round56-prereg-check.py`: no scratch, no `TMPDIR`, writes only `--out` — clean.
- `tools/round56-env-leg-test.py`: no scratch at all — clean.

C1/C2 status from this seat: **not falsified by this finding.** C1's path never resolves a
scratch root (harness has none; `env_leg` reads `/proc/<pid>/environ` only), and C2 reads
committed blobs via `git show`. The frozen counter hash still matches, so the audited bytes are
the scored bytes.

## Smallest remediation

1. Counter (next freeze only — do not touch the frozen file this round):
   `root = a.scratch or os.environ.get("TMPDIR")`; if `root is None`, exit with
   "no scratch root: pass --scratch or set TMPDIR"; then `os.makedirs(root)` and verify
   `os.access(root, os.W_OK)`; optionally refuse `root == "/tmp"`. Removes the silent
   `gettempdir()` fallback (E2) and the `/tmp` default (E1) in three lines.
2. This round, procedurally: every counter invocation in the wave must pass an explicit
   `--scratch /fast/scratch/hyaku/kama-r56/<SeatName>/counter` (spec `:9` currently names only
   `TMPDIR`; the round-29 lesson records the same defect class — "prereg-time-check items omitted
   `--scratch`").
3. Battery: replace `:37` with `pathlib.Path(os.environ.get("TMPDIR") or tempfile.gettempdir())`
   plus a `--scratch`/`--out` flag, take `OUT` from `--out` instead of the lane `:11`, and refuse
   to overwrite an existing receipt (`if out.exists(): raise SystemExit(...)`).
4. No change needed in `w1/spec.json` beyond naming `--scratch` in the counter commands; its
   scratch root is `/fast/scratch/hyaku/kama-r56/<SeatName>/`, not `/tmp`, and
   `preregistration.json` references no scratch path.

## Receipts in this output directory

- `out/S02Scratch/mkdir2.trace.txt` — E1, `/tmp` used with `TMPDIR` unset.
- `out/S02Scratch/mkdir3.trace.txt` — E2, `TMPDIR` missing dir → silent `/tmp`.
- `out/S02Scratch/mkdir4.trace.txt` — E4, `--scratch` → no `/tmp`.
