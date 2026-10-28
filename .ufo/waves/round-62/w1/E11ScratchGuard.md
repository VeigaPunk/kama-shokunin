# E11ScratchGuard — round 62, kama (operability / calibration)

Assignment: verify no committed tool hardcodes `/tmp`; run each round-62 counter with `TMPDIR`
pointed at this seat's scratch and confirm nothing writes outside that scratch (`strace -f
-e trace=file`, corroborated by a newer-mtime scan of `/tmp`). Advisory leaf: findings and
receipts only, no verdict, no commit, no lane edit outside this report and my out dir.

- Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`
- Tip measured: `65d7cad0fce90e34de37527cde22e97b63b118bf` (`git rev-parse master`)
- Freeze base (do-nothing): `a959fd9022b1ac1f3cb4dc2475d9cded8b2b01c3`
- Scratch root used and given explicitly to every run: `/fast/scratch/hyaku/kama-r62/w/E11ScratchGuard`
  (`tmp/` as `TMPDIR`, `work-c1*`, `work-c2`, `traces/`); no inherited `TMPDIR`, `/tmp` never used for
  anything cited here. Scratch removed after receipts were copied to
  `.ufo/waves/round-62/w1/out/E11ScratchGuard/`.
- Tooling record: **no installs or upgrades** in this seat. `strace` was already present at
  `/usr/bin/strace` (smoke-tested); pacman untouched (paused host-wide); no `uv`/`npx`/binary installs.

## F1 — `/tmp` literals in committed tools: 7 hits, 0 hardcoded write targets

`git grep -n '/tmp' <tip> -- tools/` over all 90 tracked files under `tools/` (receipt
`tmp-literals.txt`):

| file:line | hit | class |
|---|---|---|
| `tools/kama-probe.sh:1128` | `mktemp -d "${KAMA_PROBE_TMPDIR:-${TMPDIR:-/tmp}}/kama-probe.XXXXXX"` | last-resort **fallback** (two overrides above it) |
| `tools/test-snapshot.sh:13` | `mktemp -d "${TMPDIR:-/tmp}/kama-snapshot-test.XXXXXX"` | last-resort **fallback** |
| `tools/test-snapshot.sh:45` | `"id": "/tmp/private/fixture-model.gguf"` | fixture **data string** (never opened) |
| `tools/test-snapshot.sh:113` | `"/tmp/private"` in a forbidden-token tuple | fixture **data string** |
| `tools/kama-live-replay.py:48` | `TMPDIR set to <work>/tmp` | docstring; `<work>/tmp` is work-subdir, not `/tmp` |
| `tools/round58-c1-counter.py:16` | "…else `$HYAKU_SCRATCH/kama-r58` (never /tmp…)" | docstring stating the opposite |
| `tools/seat-report-immutability.py:54` | "a hardcoded /tmp" | docstring describing what it avoids |

No committed tool contains a `/tmp` write target: no `open("/tmp…")`, no `Path("/tmp")`, no
`dir="/tmp"`, no `mkdtemp(dir="/tmp")`. Every temp-writing tool uses `tempfile.mkdtemp/mkstemp/
TemporaryDirectory()` (honours `TMPDIR`) or an explicit `--work`/`--scratch`/`--out` path; the only
literal-`/tmp` readers are the two `${TMPDIR:-/tmp}` fallbacks above, reachable only when `TMPDIR`
is unset. Repo-wide (`git grep HEAD`, `:(exclude).ufo` `:(exclude)corpus`) the remaining hits are
`LOG.md`/`SCORECARD.md`/`PROVINCE.md`/`SKILL.md` prose, `registry/error-signatures-r26.json` data,
and `tests/llamacpp-live/check-receipt.py:1835` fixture JSON — none are executed paths.

## F2 — C1 counter loses nothing outside its scratch

Three traced runs, all with `--repo <lane> --tip 65d7cad…`, `PYTHONDONTWRITEBYTECODE=1`, cwd inside
my scratch (receipts `c1.out/.err`, `c1-notmp.out/.err`, `c1tip.out/.err`):

| run | counter bytes | `TMPDIR` | result |
|---|---|---|---|
| A | working-tree `tools/round62-c1-counter.py` (sha256 `a3498308…`) | `$S/tmp` | rc 0, `met=True` |
| B | same working-tree file | **unset** (`env -u TMPDIR`) | rc 0, `met=True` |
| C | **tip blob** `65d7cad:tools/round62-c1-counter.py` (sha256 `275610b5…`) | `$S/tmp` | rc 1, **crash** (see F5) |

`strace -f -e trace=file` write-flag/`mkdir`/`unlink`/`rename`/`link`/`symlink`/`chmod` analysis of
each trace: **0** writes to `/tmp`, **0** writes anywhere under the lane, **0** non-scratch
`/fast/scratch` writes. Run A/B: 22 write events, all inside `$S/work-c1*`; the only other
absolute write targets are `/dev/null`. Run B (TMPDIR unset) also shows 0 `/tmp` opens, i.e. the
counter has no temp-dir fallback on this path and needs no `/tmp` at all. Full inside-scratch
inventory of run A (`writes-c1.txt`): `work-c1/` (mkdir), `hold/hold.json`, `hold/ready.json`,
`hold/ready.json.tmp.<pid>`, `hold/release`, `hold/.witness-write-probe.<pid>`, `receipt.json`,
`tip/tools/kama-completion-live.py`, `tip/tools/kama-llamacpp-live.py`,
`tip/registry/endpoint-consumers.tsv`, `tool-work/server.log`.

The lane server log is `work/server.log` (not `tempfile.mkstemp`), so the completion lifecycle
writes its child log inside `--work` too.

## F3 — C2 counter loses nothing outside its scratch (12.3M traced syscalls)

`tools/round62-c2-counter.py` at the tip is byte-identical to the working tree
(sha256 `15d11f1c…` both), so this run *is* the committed instrument:

```
python3 tools/round62-c2-counter.py --repo <lane> --tip 65d7cad… --work $S/work-c2
# env TMPDIR=$S/tmp PYTHONDONTWRITEBYTECODE=1 ; strace -f -e trace=file
```
output (receipt `c2.out`, 914.7 s, rc 1):
```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 mismatches=4 canonical=62 controls_rejected=8/8 errors=0 met=False
```
Write audit over 12,307,166 traced syscall lines (636 MiB trace):

- `/tmp` write-flag opens: **0** (`writes-c2-tmp.txt`).
- Absolute path under the lane `.git` opened for write: **0**; lane `.git` mutating calls: **0**.
  The lane Git index was therefore untouched by this run (its mtime moved to 09:44 during the
  window from other seats/`jj`, not from my pids — see F4 caveat).
- Other absolute write targets: `/dev/null` (1688 opens) and `/dev/tty` (14 `ENXIO` probes) only.
- Relative writes: 7,934 resolved (via per-pid `chdir`/fork inheritance) to `<scratch>`; **0**
  resolved to the lane. The remaining dirfd-relative writes (`mkdirat`/`unlinkat`/`utimensat`
  building the `.ufo/round-5`, `.ufo/round-10` fixture tree in a control) use dirfd 3, which trace
  line 18395 pins to `$S/work-c2/tip` (`openat(…, "…/work-c2/tip", O_RDONLY|O_DIRECTORY) = 3`) —
  inside my scratch.
- The 7 lane-referencing events are `symlinkat` whose *targets* are lane paths
  (`.ufo`, `SCORECARD.md`, `SKILL.md`, `corpus/knowledge`, `corpus/lessons`, `registry`, `tests`),
  created at dirfd 3 inside `work-c2/tip`; the lanes were only referenced, never written.
- `env['TMPDIR']` is forced to `<work>/run` for every bound row (counter line ~380) and
  `PYTHONPATH` is popped, so the bound 12 live/`selftest` executions ran with a scratch temp dir
  regardless of the caller's environment.

## F4 — `/tmp` newer-mtime scan (corroboration)

Marker touched at `09:27:56 -0300`, scan after all four runs (`tmp-delta.txt`): 50 new entries under
`/tmp` at depth ≤2, **none** matching `kama|llama|round62|completion`. They belong to other host
workstreams (`hyakki-*`, `tsukuroi-bootchain-selftest.*`, `playwright_*`, `ecc-metrics-*`,
`zcode-*`, `claude-tool-count-*`). Independent confirmation of F2/F3: these counters put nothing in
`/tmp` even indirectly.

Caveat, stated rather than glossed: `/tmp` and the lane are shared with ~100 live fleet seats, so a
mtime delta alone cannot prove absence. The strace deltas (per-pid, complete process tree) can, and
they agree.

Lane delta scan (`lane-delta.txt`) outside `.git`/`.jj`/`.ufo/waves/round-62`: `corpus/knowledge/
completion-request-plane.md`, `corpus/lessons/round-62.md`, `registry/digest-ledger.tsv`, `LOG.md`,
`SCORECARD.md`, `tools/__pycache__/kama-completion-live.cpython-314.pyc` — all sibling/L1 writes
(authored concurrently in this wave), **0** attributable to my pids.

## F5 — Operability blocker: the **committed** C1 counter crashes; only the uncommitted edit passes

The tip blob of `tools/round62-c1-counter.py` (sha256 `275610b5…`) exits 1 with an empty stdout and
this traceback (`c1tip.err`):

```
File "…/round62-c1-counter-tip.py", line 440, in main        s = score(ctl, witness)
File "…/round62-c1-counter-tip.py", line 191, in score       recomputed, inconsistent = grade(receipt)
File "…/round62-c1-counter-tip.py", line 130, in grade       u = cj.get('usage') or {}
AttributeError: 'NoneType' object has no attribute 'get'
```

`cj` is `None` whenever a control receipt carries no parseable `completion` body — i.e. it crashes
on the *control* families, the very inputs the predicate requires to be "rejected" rather than to
raise. The working-tree copy (uncommitted `git diff` of 3 lines: `(cj or {}).get(…)` twice plus
`'hold_released' in checks` instead of `'hold' in checks`) runs clean: `met=True`, `errors=0`.

Consequence for the wave: the spec-time statement "C1 met=True at tip `65d7cad…`" is reproducible
**only with the uncommitted working-tree counter**; the byte-committed instrument at that tip cannot
emit its line at all. `tools/kama-completion-live.py` itself is fine (it is the pinned tool the
counter grades), and the `/tmp` discipline is unaffected. This is a delta the L1 must commit before
C1's predicate can hold "at the tip" — behavior confirmed twice (rc 1, identical traceback, 0-byte
stdout). Advisory only: I made no edit.

## F6 — Adjacent scratch observations (not `/tmp`, same class)

- `tools/kama-context-capacity.py:61` `DEFAULT_SCRATCH = Path('/fast/scratch/hyaku/kama-context-capacity')`
  and `tools/round56-env-leg-battery.py:66` `scratch = Path('/fast/scratch/hyaku/kama-r56/l1-battery')`
  are fixed, host-wide scratch paths: a caller that omits `--work`/`--scratch` collides with any
  other concurrent seat and writes outside its own scratch. My C2 trace shows the bound row passes a
  scratch explicitly (no write to either path), so this is latent, not active.
- `tools/__pycache__/*.pyc` in the lane: `round62-c1-counter`, `round62-c2-counter` (09:26) and
  `kama-completion-live` (09:28) were byte-compiled by *other* seats' untraced runs. Ignored by
  `.gitignore:3` (`__pycache__/`), so no tracked write, but instruments invoked without
  `PYTHONDONTWRITEBYTECODE=1` still seed ignored files into the checkout. My four traced runs have
  **0** write-flag opens under the lane's `tools/__pycache__`.
- `tools/kama-llamacpp-live.py:2209` `tempfile.mkstemp(prefix='kama-llamacpp-live-', suffix='.log')`
  (no `dir=`) routes the standalone server log through `TMPDIR` and deletes it at teardown; with
  `TMPDIR` unset that is `/tmp` by default. Not a hardcode, but the one shipped tool whose temp
  artifact depends on the caller's `TMPDIR`; it never appeared in my traces because the C1/C2 paths
  use `kama-completion-live.py`'s work-dir log.

## F7 — Measured counter lines (evidence, not a verdict)

```
C1 (working tree, TMPDIR=$S/tmp):    tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=8/8 log_rejected=1/1 predead_rejected=1/1 sigterm_rejected=1/1 hold_rejected=1/1 outside_rejected=1/1 errors=0 met=True
C1 (TMPDIR unset):                   identical line, rc 0
C1 (tip blob):                       (no line) rc 1 AttributeError at line 130
C2 (tip blob == working tree):       population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 mismatches=4 canonical=62 controls_rejected=8/8 errors=0 met=False
```

The C2 `mismatches=4` is not explained by a scratch escape: 8/8 controls rejected, `errors=0`,
12/12 rows bound and evaluated, `dead=0`, and `TMPDIR` was forced to a scratch dir the run owned. It
is left for the L1/C2 seats; I did not re-run or grade it.

## Risks / blockers

1. **Blocking for C1-at-tip:** the committed counter crashes on control inputs (F5). Until the
   three-line fix is committed, no C1 receipt at the tip can be emitted by the frozen instrument.
2. **C2 unbound at measurement time:** `met=False`, `mismatches=4` with the tip-identical counter
   (F7). If the wave expects C2 to hold, the four mismatching capabilities need identification by
   the owning seats; my run rules out scratch/TMPDIR leakage as the cause.
3. **Latent collisions:** fixed absolute scratch defaults (F6) can silently redirect writes out of a
   seat's scratch when `--work` is omitted.
4. **No hardcoded `/tmp` risk found** for any committed tool, in writing or in execution.

## Retained evidence

`.ufo/waves/round-62/w1/out/E11ScratchGuard/`
`tmp-literals.txt` (tip-exact grep), `c1.out`, `c1.err`, `c1-notmp.out`, `c1-notmp.err`,
`c1tip.out`, `c1tip.err`, `c2.out`, `c2.err`, `writes-c1.txt`, `writes-c2-outside.txt`,
`writes-c2-tmp.txt`, `tmp-delta.txt`, `lane-delta.txt`, `trace-sizes.txt`
(traces themselves: `c1.trace` 2,786 lines, `c1-notmp.trace`, `c1tip.trace`, `c2.trace` 636 MiB /
12,307,166 lines — deleted with the scratch, analyses above derived from them are retained).

TALLY: tmp_literals=7 hardcoded_tmp_targets=0 fallbacks_used=0 counters_run=2 c1_tip_committed=CRASH rc=1 c1_worktree_met=True outside_writes=0 tmp_writes=0 lane_writes=0 lane_git_writes=0 met_c2=False(mismatches=4,errors=0)
