# E01CompletionRepeat — C1 live request-plane repeat (round 62, w1)

Seat: E01CompletionRepeat (advisory leaf, axis: operability). No commit, no lane-source edit,
no claim verdict. Everything below is a measurement taken in this session.

Repo: `/home/vgpnk/Projects/shokunin/kama-shokunin`
Tip measured: `git rev-parse master` = `65d7cad0fce90e34de37527cde22e97b63b118bf`
Scratch: `/fast/scratch/hyaku/kama-r62/w/E01CompletionRepeat/` (created with `mkdir -p`, passed
explicitly as `--work` on every run, `TMPDIR` pinned inside it for run1; deleted before yield).
Artifacts copied to `.ufo/waves/round-62/w1/out/E01CompletionRepeat/`.

## 1. Instrument byte check before running

| path | working tree sha256 | `master:<path>` sha256 | same? |
|---|---|---|---|
| `tools/kama-completion-live.py` | `71ac4f2c45570a79cb1e80db91e85268609f28bf4dd421d628ffb9d10243771f` | `71ac4f2c45570a79cb1e80db91e85268609f28bf4dd421d628ffb9d10243771f` | **yes** |
| `tools/round62-c1-counter.py` | `a3498308938ed4715cfdf1ce5c9a2e4ddf9cb5f9befbba29857980721fe8c415` | `275610b51eb1be219cdaa3c3e15e3568b590f35e7a1b3ceb42ab0374243f4d8d` | **no** |

The live tool is byte-identical to the tip; the counter is **not**. The executed instrument
(`python3 tools/round62-c1-counter.py` resolves to the working-tree file) carries an uncommitted
3-line delta against the frozen tip bytes:

```
130  u = cj.get('usage') or {}          ->  u = (cj or {}).get('usage') or {}
139  t = cj.get('timings') or {}        ->  t = (cj or {}).get('timings') or {}
165  if 'hold' in (receipt.get('checks') or {}):  ->  if 'hold_released' in (receipt.get('checks') or {}):
```

`git log --all -- tools/round62-c1-counter.py` shows the blob unchanged from `6c25a77e` through
`65d7cad0` (`275610b5…` in both commits), so the delta is worktree-only at measurement time.

## 2. Assigned runs — two fresh-scratch repeats

Command (cwd = lane, fresh `--work` per run, no inherited TMPDIR):

```
python3 tools/round62-c1-counter.py --repo . --tip master --work <fresh-scratch>/w
```

### Run 1 — `run1/`, exit 0, wall 0.890s

```
tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=8/8 log_rejected=1/1 predead_rejected=1/1 sigterm_rejected=1/1 hold_rejected=1/1 outside_rejected=1/1 errors=0 met=True
```

### Run 2 — `run2/`, exit 0, wall 0.357s

```
tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=8/8 log_rejected=1/1 predead_rejected=1/1 sigterm_rejected=1/1 hold_rejected=1/1 outside_rejected=1/1 errors=0 met=True
```

Both lines are byte-identical: 16/16 control families rejected, `errors=0`, `met=True`.

### Receipt verdict blocks (copied to `out/E01CompletionRepeat/receipts/`)

| leg | receipt sha256[:16] | verdict | nonce | port | child pid | checks | hold.released | teardown |
|---|---|---|---|---|---|---|---|---|
| run1 | `781816ef69de5b26` | REQUEST_OK | `r62-3a5c27cbbc` | 34777 | 713428 | 17/17 true | true | rc=0, pre_dead=false, port_closed=true, sigterm=true, waited 7 ms |
| run2 | `e91c5675e2245aee` | REQUEST_OK | `r62-55166c7a61` | 37937 | 743106 | 17/17 true | true | rc=0, pre_dead=false, port_closed=true, sigterm=true, waited 3 ms |

Shared observed values in both receipts: `model.sha256` = `270cba1bd510…9256d` (pinned fixture),
`server.sha256` = `b6a31a8e9761…cd804` (realpath `/home/vgpnk/.local/opt/llama-b11755/llama-server`),
`system_fingerprint` = `b11755-704366d76`, completion text `" ground. She liked"`,
usage `prompt 8 / completion 8 / total 16`, `bad_request` status 400. The 17 graded checks in each
receipt (all `passed=true, evaluated=true`): bad_request_graded, completion_deterministic,
completion_envelope, completion_fingerprint, completion_finish_reason, completion_model_id,
completion_timings, completion_usage, health_ready, hold_released, listener_owned, model_digest,
models_alias_id, props_alias, server_digest, teardown_clean, teardown_port_closed.

The receipt nonce equals the counter's per-run generated nonce, i.e. the counter's own outside
`POST /v1/completions` during the hold window is bound to the same lifecycle (the counter-side
witness is in-memory only; see §6).

## 3. Flakiness probes (requested)

**Ready timeouts — none.** Server readiness from the child's own log (`tool-work/server.log`):

| leg | model loaded | listening on |
|---|---|---|
| run1 | `0.00.011.361` | `0.00.011.365` → 127.0.0.1:34777 |
| run2 | `0.00.010.607` | `0.00.010.611` → 127.0.0.1:37937 |
| par-r1 | `0.00.009.284` | `0.00.009.290` → 127.0.0.1:46327 |
| par-r2 | `0.00.008.602` | `0.00.008.606` → 127.0.0.1:40459 |
| par-r3 | `0.00.009.383` | `0.00.009.388` → 127.0.0.1:33959 |
| par-r4 | `0.00.009.514` | `0.00.009.521` → 127.0.0.1:39185 |
| tipblob | `0.00.009.327` | `0.00.009.329` → 127.0.0.1:46117 |

Readiness ≈ 8.6–11.4 ms against the tool's `--ready-timeout` default of 60 s and the counter's
120 s hold-detect window — roughly three orders of magnitude of margin. No `server not ready`
branch was taken in any leg (each server.log ends with `cleaning up before exit...`, rc=0).

**Port reuse — none.** Seven live legs used seven distinct ports
(33959, 34777, 37937, 39185, 40459, 46117, 46327); none appears in
`registry/endpoint-consumers.tsv` (`grep -w` per port → unregistered), and `ss -ltn` showed no
listener on any of them after teardown. Seven distinct child pids (713428, 743106, 759189,
813639, 813641, 813646, 813650); all were gone when re-checked. No collision was observed with a
*sibling* live run that was concurrently holding port 34969 with the same fixture/alias
(pid 965906, seen mid-wave, already exited and unlistened minutes later) — that is a peer's
lifecycle, not mine, and I did not signal it.

**Concurrency.** Four additional repeats launched simultaneously (separate `--work` dirs) all
returned `met=True`, exit 0, in 1.84 s wall for the whole batch — no ready timeout, no port
collision, no cross-talk.

**Output determinism across processes.** All seven independent children produced the identical
completion text `" ground. She liked"` and identical usage accounting, and the same
`system_fingerprint` — so the graded invariants (not text quality) reproduce bit-for-bit.

## 4. Frozen-instrument finding (measured, not judged)

The counter bytes **at tip master** do not produce a summary line on a live receipt. Running the
tip blob verbatim (`git show master:tools/round62-c1-counter.py` into scratch) with the same
arguments:

```
$ python3 <scratch>/round62-c1-counter.tip.py --repo . --tip master --work <fresh>
Traceback (most recent call last):
  File "…/round62-c1-counter.tip.py", line 501, in <module>
    sys.exit(main())
  File "…/round62-c1-counter.tip.py", line 440, in main
    s = score(ctl, witness)
  File "…/round62-c1-counter.tip.py", line 191, in score
    recomputed, inconsistent = grade(receipt)
  File "…/round62-c1-counter.tip.py", line 130, in grade
    u = cj.get('usage') or {}
AttributeError: 'NoneType' object has no attribute 'get'
```

exit=1, empty stdout. Reproduced **3/3** times (fresh scratch each), so it is deterministic, not
flaky. The live leg had already completed successfully in each of those runs — a valid
`REQUEST_OK` receipt with 17/17 checks, rc=0 teardown, `port_closed=true` was written before the
control phase crashed, so the crash strands nothing.

Localised by importing the tip module and grading the run1 receipt under the counter's own
control mutations:

| control mutation | tip `grade()` outcome |
|---|---|
| `stale` (nonce → `r60-deadbeef`) | graded; alltrue=False, inconsistent=`['unexpected-checks']` |
| `log` (health body tampered) | graded; alltrue=False, inconsistent=`['health_ready','unexpected-checks']` |
| `tamper[0]` (completion body `text_completion`→`chat.completion`, sha therefore stale) | **RAISES AttributeError** |

So the crash trigger is the first control that invalidates the completion capture's body digest:
`cap('completion')` → `None` → `cj = None` → `cj.get('usage')`.

Root cause of the third delta: the tip gates the hold check on `'hold' in checks`, but the tool
records the check as `hold_released`. A real receipt therefore gains an `unexpected-checks`
inconsistency on *every* live run. Verified with a derived copy carrying only the two `(cj or {})`
guards (third delta left as at tip):

```
tool_present=1 live_ok=0/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=8/8 log_rejected=1/1 predead_rejected=1/1 sigterm_rejected=1/1 hold_rejected=1/1 outside_rejected=1/1 errors=1 met=False
error: live: {"alltrue": true, "inconsistent": ["unexpected-checks"], "live": true, "met": false, "verdict_ok": true}
```

i.e. with the guards alone every recomputed check is true and the outside witness matched, yet the
gate still fails — the `hold_released` key fix is load-bearing, not cosmetic. All three deltas are
jointly required for the executed counter to reach `met=True`; the working-tree version
(`a3498308…`) does so in 6/6 live runs.

Consequence to record plainly: at tip `65d7cad0` the committed counter cannot reproduce a
`met=True`/`live_ok=1/1` line, and cannot grade its own 16-control battery to completion. The
`met=True` figures attributed to the tip at spec time are reproducible only with counter bytes
that are not at the tip. Artifacts of both sides are in the out dir
(`tip-counter-at-tip-master.py.txt`, `derived-only-cjguard.py.txt`, `tipblob.stderr.txt`,
`tipblob-repeat.stderr.txt`, `derived-2line.stdout.txt`/`.stderr.txt`).

## 5. Environment / tooling

- No tool was installed or upgraded for this seat: `python3` 3.14.8 (stdlib only), `git`,
  and the pinned `llama-server` (`/home/vgpnk/.local/bin/llama-server` →
  `/home/vgpnk/.local/opt/llama-b11755/llama-server`, version 0.7.0-dev build 11755 commit
  `704366d76`, sha256 `b6a31a8e…cd804`) plus the fixture
  `~/.cache/kama-shokunin/models/stories260K.gguf` (sha256 `270cba1b…9256d`) were already present
  at the pinned digests. Pacman was not invoked (host-wide pause); nothing required it.
- Read-only git only (`rev-parse`, `show`, `log`, `diff`, `status`). No commit, no push, no jj,
  no index write, no lane source edit; the only writes are this report, the out dir, and scratch.

## 6. Residual risks / open surfaces (advisory)

1. **Uncommitted instrument.** The passing counter is worktree-only. Any tip-blind rerun
   (clone / export of `65d7cad0`) reproduces the AttributeError instead of `met=True`. Until the
   L1 commits the 3-line delta, C1's "exit 0 iff met" is not reproducible from committed bytes.
2. **Hold grading is keyed on the receipt's own `checks` map.** `required = set(out) - {'nonce_match'}`
   and `hold_released` only enters `out` when the receipt already carries a `hold_released` entry.
   A receipt that simply omits that check would not be flagged as `missing-checks`, so the hold
   release would go ungraded. Controls are mutations of a real receipt (which always carries it),
   so the battery does not exercise this shape. [INFERENCE from the code path; not demonstrated.]
3. **Counter-side witness is in-memory only.** The outside hold-window contact is not persisted to
   disk; it is evidenced only by the printed `live_ok=1/1` plus receipt/nonce agreement. A third
   party re-deriving the claim from artifacts alone can confirm 17/17 graded checks and nonce
   binding, but cannot re-observe the witness request itself.
4. **Wall-clock speed.** A full graded lifecycle completes in 0.36–0.89 s (tiny fixture). Fast
   enough that a `met=True` line is not by itself evidence of a long-lived server; the graded
   `hold_released` + `listener_owned` + `teardown` checks are what carry that, and both were true.

## 7. Evidence inventory

`.ufo/waves/round-62/w1/out/E01CompletionRepeat/`
- `run1.stdout.txt`, `run2.stdout.txt` — the two assigned one-line outputs (identical).
- `receipts/run1.receipt.json`, `receipts/run2.receipt.json` — full receipts (verdict blocks, 17 checks, captures).
- `receipts/par-r{1..4}.receipt.json`, `par-r{1..4}.stdout.txt` — four concurrent repeats, all `met=True`.
- `tipblob.stdout.txt` (empty), `tipblob.stderr.txt`, `tipblob-repeat.stderr.txt` — frozen-tip counter traceback, 3/3.
- `tip-counter-at-tip-master.py.txt` — exact tip blob run (`275610b5…`).
- `derived-only-cjguard.py.txt`, `derived-2line.stdout.txt`, `derived-2line.stderr.txt` — two-guard-only variant proving the third delta load-bearing.

## 8. Tally

```
E01 live legs: 6/6 met=True (2 assigned + 4 concurrent, worktree counter a3498308) | tip-blob counter 275610b5: 0/3 summary lines (AttributeError, deterministic) | ready timeouts 0/7 | distinct ports 7/7 unregistered, 0 listeners after teardown | controls 16/16 rejected per leg, errors=0
```
