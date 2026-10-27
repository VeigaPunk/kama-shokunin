# S02ScratchAndSecrets — round-58 scratch / credential / private-URL / op:// sweep

**Clean on the three named leak classes:** zero credential values, zero `op://` references, zero private
URLs, zero hardcoded `/tmp` in code. **Not clean on scratch/portability:** one executed failure mode in the
C2 counter (F1) and hardcoded host paths in 21 committed files (F2).

Scope: the 42 paths added/changed `2f53614..e4891d8` (15 `tests/round58-battery-variants/*.py`, `tools/round58-{battery-exec-check,c1-counter,c2-counter}.py`, `.ufo/waves/round-58/{controls,census}/`, SCORECARD hunk) plus the 54 untracked `.ufo/waves/round-58/**` files. Committed bytes read via `git show e4891d8:…`.

## F1 — `round58-c2-counter.py` exits **1** on a missing scratch root (attacks the C2 kill rule)

`tools/round58-c2-counter.py:109-111` hands `dir=$TMPDIR` straight to `tempfile.TemporaryDirectory` and never
creates the root; `round58-c1-counter.py:57-61` and `round58-battery-exec-check.py:183-186` both `os.makedirs`.
Receipts (exit codes):

- `env -u TMPDIR HYAKU_SCRATCH=$S/no-such-base python3 tools/round58-c2-counter.py --repo … --tip e4891d8… --manifest-rev 941acf7…`
  → `FileNotFoundError: …/no-such-base/kama-r58/c2-pu86e0gw`, **exit 1**, no predicate line (`p1-c2-missing-scratch-base.out`).
- `TMPDIR=/dev/null python3 tools/round58-c2-counter.py …` → `NotADirectoryError: '/dev/null/c2-8yttkgod'`, **exit 1** (`p2-c2-bad-tmpdir.out`).
- Control: `TMPDIR=$S/missing-c1 python3 tools/round58-c1-counter.py … --checker tools/round58-battery-exec-check.py`
  → root created, `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True`, **exit 0** (`p3-c1-missing-tmpdir.out`).

Why it matters: the frozen kill rule is “any nonzero counter at the measured tip → C2 not met”, and the tool’s own
docstring (`:12-17`) maps exit 1 to “predicate not met”. A scratch-path typo therefore records a **silent false
C2 failure** instead of the `could-not-evaluate` (exit 2) its siblings reserve for infrastructure faults; `--out`
is not written either. Smallest fix: `os.makedirs(root, exist_ok=True)` before `TemporaryDirectory`, exit 2 on
`OSError`. Found by running the tool with the wave’s own prescribed `TMPDIR` shape.

## F2 — hardcoded absolute host paths, 21 committed files / 36 occurrences

| file | line(s) | literal |
|---|---|---|
| `tests/round58-battery-variants/*.py` (all 15, incl. `genuine.py`) | 10 | `LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin")` |
| same 15 (`genuine:66 B1:67 B2:70 B3:66 N01:66 N02:66 N03:66 N04:66 N05:66 N06:68 N07:67 N08:66 N09:66 N10:69 N11:66`) | left | `pathlib.Path("/fast/scratch/hyaku/kama-r56/l1-battery")` |
| `.ufo/waves/round-58/controls/checkers/hash-only.py` | 5 | lane path as `git -C` target (do-nothing control; deliberate) |
| `tools/round58-c2-counter.py` | 67 / 111 | `--fleet-repo` default `/home/vgpnk/Projects/shokunin`; `HYAKU_SCRATCH` default `/fast/scratch/hyaku` |
| `tools/round58-battery-exec-check.py`, `round58-c1-counter.py` | 184 / 59 | `HYAKU_SCRATCH` default `/fast/scratch/hyaku` |
| `.ufo/waves/round-58/census/start.out` (untracked `w1.ready:1` likewise) | 102 | absolute lane / dispatch paths in committed evidence |

Inert under the sanctioned entry point: the harness patches `Path.mkdir/write_text/write_bytes` and `TemporaryDirectory`, so the variants never dereference these paths (proved below). They are inherited from `tools/round56-env-leg-battery.py:10,66`, and the frozen variants must stay behaviour-preserving — remediate by documentation/parameter, not by editing the frozen bytes.

## F3 — the variant write target is live outside the harness (observed, not mine)

An unharnessed battery run at `2026-10-27 16:51:52` rewrote 5 files under `.ufo/waves/round-56/measured/`
(4 changed bytes, only `pid=`; `comparator-selftest.out` byte-identical) and created `/fast/scratch/hyaku/kama-r56/l1-battery`.
`git status --porcelain -- .ufo/waves/round-56/measured` → 4 `M` (`lane-dirty.txt`). Attribution is [INFERENCE]:
I ran nothing in the lane before 16:54. Concrete cost of `OUT = LANE/".ufo/waves/round-56/measured"`.

Harness guard verified: `TMPDIR=$S/tmp2 … round58-c1-counter.py --checker tools/round58-battery-exec-check.py`
→ `met=True`, exit 0, and `diff` of the measured-dir mtimes before/after is **identical** (`MTIME-IDENTICAL`).

## Clean checks (exit 0)
- `git grep -c -E 'op://|AKIA|ghp_|sk-|xox[baprs]-|BEGIN .*PRIVATE KEY|password|passwd|secret|api_key|apikey|Authorization:|Bearer '` over the round-58 scope → **0** per pattern; only `token=` (3) = verdict tokens in `c2-counter.py:125` and `controls/c2-*.out`.
- URLs: one public docstring link, `tools/round58-battery-exec-check.py:13 https://docs.python.org/3/library/sys.html#sys.setprofile`. Untracked `w1/out` hits are `docs.python.org` / `man7.org` only.
- Literal `/tmp` in code: **none**. Only prose in `build_spec.py:87,130`, `w1-dispatch.json`, `w1-spec.json`, `w1/out/swarm-registry.json` (task text) and the concession at `round58-c1-counter.py:16` (“never /tmp unless the operator sets it”).

## Limits
- `$TMPDIR` is used **verbatim** as `dir=` (proved by the `/dev/null` probe), so `TMPDIR=/tmp` puts scratch under `/tmp`; not executed here (writing `/tmp` is barred). `c1`/`exec-check` offer `--work`; `round58-c2-counter.py` has **no** `--work` flag (`:65-70`), so env is its only lever.
- `clean_env()` forwards the whole ambient environment (minus `GIT_*`) to child processes; no round-58 file reads or prints it.
- No production file edited, no tools installed. Scratch `$S` removed after copying receipts.

Receipts: `c1-counter.out`, `c2-counter.out`, `p1-*`, `p2-*`, `p3-*`, `lane-dirty.txt`, `measured-mtimes.txt`.
