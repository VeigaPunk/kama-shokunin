VERDICT: holds — `ulimit -f` fails the self-appending runaway: at `ulimit -f 2048` the fixture stops at exactly 2,097,152 bytes (exit 153 = SIGXFSZ with SIGXFSZ at its default action, exit 1 = uncaught OSError EFBIG under bash's inherited SIG_IGN) while the same loop at `ulimit -f 20480` grows past 2 MiB and stops at exactly 20,971,520 bytes, though the cap bounds the file rather than terminating a loop that ignores or swallows the error (timeout still owns that), and this is a capability demo on a generic self-append writer, not a reconstruction of the incident's exact writer or MARKER alias.

# ExecFixtureBoundDemo — file-size cap vs. a runaway fixture

Seat: `KamaR27A3.ExecFixtureBoundDemo` (leaf, lane kama round 27 attempt 3).
Claim served: mined mistake fix, `corpus/lessons/round-27.md:92` (Mistakes row 1) — "every round-27 wave context requires `ulimit -f` on fixture-writing commands; **shown able to fail** only if this round's FixtureBoundDemo seat receipt shows the cap stopping a self-append".
Incident pointer: `.ufo/waves/round-27/a3/mistake-runaway/REMOVED-RUNAWAY.txt:1` — `sitecustomize.py` at 262,699,483,136 bytes, /fast full; first 4096 bytes kept as `sitecustomize.py.head4k` (4096 bytes, `stat`).
Retained receipt: `.ufo/waves/round-27/w1a3/out/ExecFixtureBoundDemo/receipt.json`; console log `…/receipt.log` (162 lines, sha256 `655a2ca3…abe3b1`).

## Method

Fixture (`fixture.template.py`, sha256 `93af1869…3df8e4`, 8385 bytes): a two-line `MARKER-A3-FIXTURE-BOUND-DEMO` snippet at the head, then

```python
_P = os.path.abspath(__file__)
_BLOB = open(_P, "rb").read()          # own content
while True:
    with open(_P, "ab") as f:          # self-append: the runaway
        f.write(_BLOB)
```

with MiB crossings written to `$PROGRESS_LOG` — a separate file that Python never imports and never reads back; the fixture itself is on no `sys.path`, and nothing appends to it except the loop. Two env switches change only what their names say: `A3_SIG_DFL=1` restores the SIGXFSZ default action before the loop; `A3_SWALLOW=1` wraps the append in `except OSError` and continues. The loop body is byte-identical across runs.

Guard on every command that writes: `ulimit -f 1048576` (1 GiB/file), `ulimit -c 0`, inside `timeout` (harnesses 300 s/120 s; the fixture runs inside their own `timeout 60`/`5`/`3`). `df -h /fast`: 804G, 581G used, 224G avail before; 223G avail after (`receipt.log:6`, `:111`, `:143`).

Commands per run (run_py in `run-demo.sh`), each preceded by `cp fixture.template.py fixture.py`:

```sh
( ulimit -f 2048;  export PROGRESS_LOG=A0.log A3_SIG_DFL=0; exec timeout 60 python3 fixture.py )   # A0
( ulimit -f 2048;  export PROGRESS_LOG=A1.log A3_SIG_DFL=1; exec timeout 60 python3 fixture.py )   # A1
( ulimit -f 20480; export PROGRESS_LOG=B1.log A3_SIG_DFL=1; exec timeout 5  python3 fixture.py )   # B1
( ulimit -f 2048;  export PROGRESS_LOG=C0.log A3_SIG_DFL=1; exec timeout 5  python3 fixture.py )   # C0
```

Units check (`receipt.log:16`): `( ulimit -f 2048; python3 -c '…RLIMIT_FSIZE…' )` → `RLIMIT_FSIZE soft=2097152 hard=2097152`; bash's `-f` unit is 1024-byte blocks, as the assignment assumes.

## (a) and (b), as assigned

| run | cap | timeout | exit | meaning | final size | ≤2 MiB | wall | max MiB crossed | log |
|---|---|---|---|---|---|---|---|---|---|
| A0 — (a) literal writer | 2048 (2 MiB) | 60 s | **1** | uncaught `OSError [Errno 27] File too large` | **2,097,152** | YES | 28 ms | 1 | `:19-28` |
| A1 — (a) death path | 2048 (2 MiB) | 60 s | **153** | 128+25 SIGXFSZ | **2,097,152** | YES | 57 ms | 1 | `:32-41` |
| B1 — (b) same loop | 20480 (20 MiB) | 5 s | **153** | SIGXFSZ at the 20 MiB bound | **20,971,520** | **NO** | 58 ms | 19 | `:46-56` |
| C0 — identical-timeout control | 2048 (2 MiB) | 5 s | **153** | SIGXFSZ | **2,097,152** | YES | 44 ms | 1 | `:60-69` |

- B1's progress log ends `crossed mib=19 size=19931145` (`:53`): the loop demonstrably passed 2 MiB, so (a)'s stop was the cap, not the loop ending or the clock.
- The final size equals the cap exactly in every capped run — the kernel clamps the crossing write to the limit; no overshoot.
- `pgrep -fc 'fixture\.py'` was 0 after every run (each run's `*_leftover_writer=0`); the writers are dead before their timeout except E2/D3.
- **Identical-timeout control** (critic request): C0 vs B1 hold `timeout 5` constant; the only difference is the cap, and the outcomes are 2,097,152 vs 20,971,520. The assigned (a) timeout 60 is therefore not a confound.
- No uncapped arm was run: the uncapped behavior is the incident itself. The 20 MiB row is the red arm under an outer safety bound, and A1→B1 differ only in `ulimit -f` (same fixture bytes, same loop, same SIG_DFL).
- **The printed detector is not a gate detector.** `detector()` at `run-demo.sh:42-43` only echoes `<label>_size<=<bound>=YES/NO` and always exits 0 (`receipt.log:28`, `:41`, `:55-56`, `:69`). The line `B1_size<=2097152=NO` is a reporting aid, **not** the fleet `CORPUS.md:179-183` red-before artifact ("the same command exits non-clean for the named reason"). Do not score it as one; the gate-shaped pair is §Strict red-before pair.

## Signal disposition: why (a) exits 153 only in one shape

`receipt.log:9-13`:

```
bash self:  SigBlk: 0000000000000000  SigIgn: 0000000001000000
python inherits SIGXFSZ handler=<Handlers.SIG_IGN: 1>
trap - SIGXFSZ  -> SigIgn: 0000000001000000 ; child python handler=<Handlers.SIG_IGN: 1>
```

Bit 24 = signal 25 = SIGXFSZ: bash 5.3.20 starts children with SIGXFSZ ignored, and `trap - SIGXFSZ` does not undo it. So the literal assignment command (A0) does not die by SIGXFSZ — Python gets `OSError(EFBIG, errno 27)` and exits 1, and the traceback points at the `with open(...)` line because the bytes after the kernel's clamp stayed buffered: the error surfaces from the file's close on `with` exit, not from the `f.write` call (`receipt.log:23`). Restoring `SIG_DFL` in the writer (A1/B1/C0/E) produces 153. Both paths stop the runaway and pin the file at the cap; only the exit code differs. [INFERENCE] The same inherited ignore applies to any writer a seat launches from bash, not just Python; I measured Python and `cat` (D3), not every writer.

Retained probe `probe-efbig-site.log` (command `bash probe-efbig-site.sh` under the same guard) pins the failure site: `open('ab')` on a file already at exactly 2,097,152 exits 0 with the size unchanged; `write(b'y'*10); close()` exits 1 with the OSError raised **from `close()`**; a no-close variant exits 0 and drops the error as `Exception ignored while finalizing file`; a single `write(b'z'*(2097152+100))` is clamped to exactly 2,097,152 and the remainder raises at close. So the cap clamps the crossing write to the limit and the first EFBIG may appear one flush later than the write that caused it — the file is bounded either way, and an unflushed failure can even be silently dropped at interpreter exit.

## Supplementary shapes (same guard, all cleaned up)

| row | shape | exit | final size | observation | log |
|---|---|---|---|---|---|
| D | `while :; do cat grow.txt >> grow.txt; done`, 2 MiB, 3 s | 124 | 60 | GNU cat refuses `f >> f` ("input file is output file"), 7,567 iterations; tests nothing about the cap | `:72-76` |
| D2 | `cat seed.txt >> grow.txt`, 60-byte seed, 2 MiB, 3 s | 124 | 486,960 | loop too slow to reach the cap in 3 s (205,740 on the discovery run); not cap evidence | `:115-121` |
| D3 | `cat seed8.txt >> grow3.txt`, 7,980-byte seed, 2 MiB, 3 s | 124 | **2,097,152** | 6,919 × `cat: write error: File too large`; file pinned at the cap while the loop spins to timeout | `:146-151` |
| E | swallowing writer, SIG_DFL, 2 MiB, 3 s | 153 | 2,097,152 | signal kills during the write, so the `except` never runs (0 swallowed lines) | `:80-90` |
| E2 | swallowing writer, bash's SIG_IGN, 2 MiB, 3 s | 124 | **2,097,152** | 889,000 EFBIG errors swallowed in 3 s (`swallowed errno=27 count=889000 size=2097152`); writer alive, file pinned at the cap | `:124-130` |

These delimit the guarantee: `ulimit -f` bounds the **file** unconditionally; it terminates the **process** only when SIGXFSZ has its default action. A shell loop (D3) or a swallowing writer (E2) keeps running, so the wave contexts' `timeout` remains required alongside the cap. [INFERENCE] A fixture that both swallows the error and logs each iteration will keep writing to its separate log until that log hits its own cap; here the log stayed tiny (892 lines).

## Strict red-before pair (gate shape, `CORPUS.md:179-183`)

`redbefore-cap.sh` (retained, sha256 `81729394…c53a8`; log `redbefore-cap.log`, `c8f2a763…09a423`) is one detector command, the same fixture bytes (`93af1869…3df8e4`) and the same `timeout 5` in both arms, with **only `ulimit -f` as the fix delta**:

```
## red-before: cap 20480 (20 MiB), 2 MiB bound absent
detector cap_blocks=20480 writer_exit=153 writer_exit_is_sigxfsz=YES final_size=20971520 bound=2097152 writer_stderr_first=[timeout: the monitored command dumped core]
detector cap_blocks=20480 RESULT=NON-CLEAN reason=file_exceeded_2MiB_bound size=20971520 bound=2097152
RED_EXIT=3
## fixed: cap 2048 (2 MiB), same detector command, only the cap changed
detector cap_blocks=2048 writer_exit=153 writer_exit_is_sigxfsz=YES final_size=2097152 bound=2097152 writer_stderr_first=[timeout: the monitored command dumped core]
detector cap_blocks=2048 RESULT=clean
FIX_EXIT=0
pair_verdict=RED_NONCLEAN_FIX_CLEAN
```

The detector parses the fixture's final size and exits 3 with the named reason string when it exceeds 2 MiB, 0 when it does not. The writer's own exit is 153 (SIGXFSZ) in both arms and is recorded, not scored — the cap is the fix under test, not the writer's signal path. The repair claim therefore has a red-before state in which the same command is non-clean for the named reason, with the fix as the only delta and the observed failure text committed.

Still **not** covered by a red-before pair: the MARKER-separation half of the lesson's fix ("a MARKER file separate from any file Python imports"). Building that red state means reproducing the incident's import-time self-append, which the critic and I both scoped out; it remains inference from `REMOVED-RUNAWAY.txt:1` ("MARKER evidently pointed back at this file").

## Deletions

`rm -f fixture.py grow.txt seed.txt seed8.txt grow3.txt cap.bin cap2.bin rb-fixture.py rb.log rb.stderr` plus every per-run `.log/.stdout/.stderr` (the harnesses remove them at exit). Post-cleanup `ls -la` of `/fast/scratch/hyaku/kama-r27c/ExecFixtureBoundDemo/` shows only harness scripts, no fixture or log from a run: `capture.sh`, `fixture.template.py`, `run-demo.sh`, `run-extra.sh`, `run-d3.sh` (`receipt.log:101-110`, at the canonical capture), plus `probe-efbig-site.sh` and `redbefore-cap.sh` added later; `du=40K` at the end. `core_files=none` (RLIMIT_CORE=0; `core_pattern` pipes to systemd-coredump but no dump was written), `leftover_writers=none` (`:94-98`). No llama-server was started by this seat; none was needed (the three visible in global `pgrep` started 05:53–06:15Z on ports 47636/47637/47644, before this seat's first command at 07:09:45Z, and are other seats').

## Scope limits and risks

- This shows **RLIMIT_FSIZE effectiveness on a generic linear self-append writer**. It does not reconstruct the incident writer's exact append shape or prove the MARKER alias (the critic `KamaR27A3.CriticMistakeRow` asked that this be stated; agreed — the alias remains inference, `REMOVED-RUNAWAY.txt:1` says "evidently").
- Soft and hard limits were equal, so the child could not raise the soft limit. A fixture that calls `resource.setrlimit` cannot exceed the hard cap; if a wave context sets only the soft limit while the hard limit stays unlimited, a child could raise it. The wave contexts' `ulimit -f N` in bash lowers both only if the hard limit allows; here the guard set `-f 1048576` first, and each harness lowered soft and hard together (bash's `ulimit -f` without `-S`/`-H` sets both). [INFERENCE] A context that sets `ulimit -S -f` alone would not be safe against a writer that raises it.
- Exit 153 is not what the literal bash-launched command yields (A0 → 1). If a receipt elsewhere expects 153 without restoring SIG_DFL, that expectation is wrong on this host.
- Harness v1 aborted after A0 (exit-153 gate); its logs were deleted. The canonical record is the 07:13:43Z capture; the 07:12:02Z discovery run agreed on every primary row (receipt `determinism`).

## Retained evidence

`out/ExecFixtureBoundDemo/`: `receipt.json`, `receipt.log` (7,092 B, sha256 `655a2ca3…abe3b1`), `fixture.template.py` (8,385 B, `93af1869…3df8e4`), `run-demo.sh` (5,912 B, `ad1771c5…284a01`), `run-extra.sh` (2,441 B, `b68cee60…85c40`), `run-d3.sh` (1,160 B, `0022f787…95edc`), `capture.sh` (694 B, `1d6cc658…66d8a`), `probe-efbig-site.sh` (1,482 B, `7ae3e55b…18f8`), `probe-efbig-site.log` (1,540 B, `a218d11e…509a7`), `redbefore-cap.sh` (2,165 B, `81729394…c53a8`), `redbefore-cap.log` (1,644 B, `c8f2a763…09a423`).
