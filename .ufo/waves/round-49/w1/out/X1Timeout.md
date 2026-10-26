# Round 49 seat X1Timeout — witness-timeout path (operability, lane kama)

**Verdict: the timeout path is sound and bounded — a witnessed replay whose `release` never appears tears the server down ~5.0 s after `ready.json`, records `witness.released=false` with `waited_ms=5008`, still reports `match=true exit=0` (by contract, and C1 does not accept that receipt: it requires `released=true` *plus* its own observation), and leaves no process or listener. Six argument-error runs all exit 2 with no side effect. Two side defects found, both outside the timeout bound itself: a stale `release` in the witness directory yields `released=true, waited_ms=0` with no observation window (`tools/kama-llamacpp-live.py:280-300`), and a harness that fails mid-witness is reported as a comparison *difference* (exit 1) instead of a refusal (exit 2) (`tools/kama-live-replay.py:283-291`).**

Tested against a private clone at `/fast/scratch/hyaku/kama-r49/X1Timeout/lane` (HEAD `122c4ee9`; `git -C … diff --stat 74558c71c38ceaeace15fd4cf8aa9d84977584b1 122c4ee9` lists only
`.ufo/waves/round-49/{freeze/prereg-time-check.out,w1/{build_spec.py,dispatch.json,spec.json}}`, so both tools are byte-identical to the build commit). Receipt under test: `.ufo/waves/round-48/c2/live/receipt-2.json` (schema `kama-llamacpp-live/v5`, outcome `pass`, 11 checks). All runs used the documented harness:

```
S=/fast/scratch/hyaku/kama-r49/X1Timeout; export TMPDIR="$S"
python3 $S/lane/tools/kama-live-replay.py --receipt $S/lane/.ufo/waves/round-48/c2/live/receipt-2.json \
  --work $S/work --out $S/replay-out.json --witness-dir $S/wit --witness-timeout 5
```

`$S/wit` existed and empty; `release` was never created. Three independent runs (method scripts
`method-watch-run{1,2,3}.sh`, which start the replay and sample the announced pid from the same
shell).

## 1. Does the live tool tear down after ~5 s? Yes.

| run | `witness.waited_ms` | replay wall time | server alive at ready | gone after exit |
|---|---|---|---|---|
| 1 | 5008 | 7476 ms | yes (`/proc/256565/exe` → `…/work/server/llama-b11909/llama-server`) | yes |
| 2 | 5008 | 7469 ms (hold after ready = **5026 ms**) | yes, `LISTEN 127.0.0.1:37283 users:(("llama-server",pid=338555,fd=3))`, `GET /health` → `{"status":"ok"} status=200`, `POST /tokenize` → pieces | yes |
| 3 | 5008 | 7451 ms; last alive sample **4829 ms** after ready, exit at **5030 ms** | yes, 25 consecutive 200 ms samples alive across the window | yes |

Run 3's sample log shows one continuous liveness plateau and a single transition
(`timeline-run3.log`: first `alive t_since_ready_ms=0`, last `4829`, then
`replay_exit=0 … t_since_ready_ms=5030`), i.e. the hold ran for the whole bound and the child
died inside the last 200 ms sampling gap — the 8 ms above 5000 is the loop's `time.sleep(0.05)`
granularity plus the 50 ms poll (`tools/kama-llamacpp-live.py:295-298`).

## 2. `witness.released` false, `waited_ms` ~5000? Yes, in all three rerun receipts.

`rerun-receipt-run1.json` (identical key set in runs 2 and 3):

```json
"witness": {"dir": "/fast/scratch/hyaku/kama-r49/X1Timeout/wit", "pid": 256565,
            "port": 34407, "released": false, "schema": "kama-live-witness/v1",
            "waited_ms": 5008}
"teardown": {"returncode": 0, "sigterm_sent": true, "sigkill_sent": false,
             "port_refuses": true, "term_wait_ms": 3, "alive_at_teardown_start": true}
"outcome": "pass"   # checks: health_ready … model_unchanged, 11/11 true
```

So expiry is not a failure of the harness: teardown is graceful (SIGTERM, no SIGKILL, child
exit 0, port refuses afterwards), and the same 11 checks pass as in an unwitnessed replay.

## 3. Does the replay still exit 0 with `match=true`? Yes — and that is the documented contract, not an oversight.

```
replay match=True refused=None mismatches=0 exit=0
```

* `tools/kama-live-replay.py:45`: "A witnessed replay matches exactly as an unwitnessed one: the witness is not compared." The projection (`:168-195`) and `compare()` (`:198-227`) carry no `witness` key, so run 1 matching the *unwitnessed* round-48 original is direct evidence the block is inert for the verdict.
* `tools/kama-llamacpp-live.py:285-286` (docstring of `hold_for_witness`): "this tool records only that it waited, never what the observer saw." `tools/kama-llamacpp-live.py:1860-1863` adds no check for the witness; the receipt keeps exactly the 11 checks of an unwitnessed run.
* **Should it?** For the replay tool's own question — "does this server reproduce the recorded contract?" — yes: the rerun server did start, serve, pass all 11 checks and tear down; the observer's punctuality is not part of that contract, and making it part would let a slow observer flip a valid run to non-match.
* The claim is not weakened because C1 does not read the receipt as proof of observation: `tools/round49-replay-witness-audit.py:324-326` additionally requires `rr["witness"]["released"] is True`, and `witness_one()` (`:292-341`) does its own exe-digest / LISTEN-inode / `-m`-digest / nonce round-trip *before* it writes `release` and returns `not probs`. An expired witness is therefore `witness=0` for C1, which the timeout path cannot produce as a pass.

## 4. Is the server gone? Yes.

Run 3/2 after exit: `/proc/<pid>` absent (`alive_after=no`); `ss -ltn | grep :<port>` empty for all
three ports used (34407, 37283, 34565); `curl` to the port `rc=7` (connection refused) — matching
receipt `port_refuses: true`; `pgrep -af X1Timeout` → nothing. No llama-server I started survives
(the only llama-server processes visible belong to peer seat `X1Kill`'s `/fast/scratch/…/X1Kill/`
work dirs — not mine).

## 5. Argument errors (`--witness-dir` missing / a file)

| # | tool | argument | stderr | exit |
|---|---|---|---|---|
| R1 | `kama-live-replay.py` | `--witness-dir <missing>` | `error: --witness-dir must be an existing directory` | 2 |
| R2 | `kama-live-replay.py` | `--witness-dir <regular file>` | same | 2 |
| R3 | `kama-llamacpp-live.py` | `--witness-dir <missing>` | same | 2 |
| R4 | `kama-llamacpp-live.py` | `--witness-dir <regular file>` | same | 2 |
| R5 | `kama-llamacpp-live.py` | `--witness-timeout 0` | `error: --witness-timeout must be > 0` | 2 |
| R6 | `kama-llamacpp-live.py` | `--witness-timeout -3` | same | 2 |

Full transcripts: `argument-errors.txt`. Both counters are guarded at
`tools/kama-llamacpp-live.py:1581-1584` and `tools/kama-live-replay.py:481-482`; no `--work`
directory and no receipt was created by any refused run (`ls -d $S/neg*` → none), and no server
was started, so the refusal is free of side effects. (R3–R6 use `--server /bin/true --model
/nonexistent.gguf`, which is irrelevant: `parser.error` fires before any file is touched.)

## 6. Defects (found in addition to the timeout-bound behaviour)

### D1 — a stale `release` file makes `released=true, waited_ms=0` with no observation window
`tools/kama-llamacpp-live.py:293-297`: `hold_for_witness()` never checks that the witness
directory is fresh (`release` is only *defined* at `:293` and tested at `:295`), so a `release` left
by an earlier run ends the hold immediately, while `ready.json` from that earlier run is
overwritten only afterwards.

```
mkdir -p $S/wit-stale; echo leftover > $S/wit-stale/release
python3 $S/lane/tools/kama-live-replay.py --receipt $S/lane/.ufo/waves/round-48/c2/live/receipt-2.json \
  --work $S/work-stale --out $S/replay-stale.json --witness-dir $S/wit-stale --witness-timeout 5
# replay match=True refused=None mismatches=0 exit=0
# witness: {"released": true, "waited_ms": 0, "pid": 312477, "port": 36411, …}
```

Impact: the receipt-side signal C1 checks (`released is True`,
`tools/round49-replay-witness-audit.py:324-326`) is obtainable with a zero-length window. C1
itself is *not* defeated — it observes the pid/port/exe/model/nonce on its own and only then writes
`release` (`:298-328`) — but the pair (`released`, `waited_ms`) proves nothing on its own and a
reused directory silently produces a witness-shaped receipt. Adjacent, not duplicate: K1Cheat and
K1Design reported the counter-side reliance on `released` without pid continuity; this is the
tool-side acceptance of a foreign `release`, measured. Fix in `proposed-fixes.diff` (guard for a
stale `ready.json`/`release`, `SetupError('witness-dir-not-fresh:<name>')`, exit 2). C1 creates each
witness dir with `os.makedirs` (`:293`), so the guard cannot disturb the counter.

### D2 — a harness that dies mid-witness is scored as a behavioural difference (exit 1), not a refusal (exit 2)
`tools/kama-live-replay.py:285-288`: the rerun receipt is loaded and compared even when the live
tool exited with a setup error, so the replay reports `mismatches=['outcome:pass->setup-error',
'live-exit:2']` and exit 1, while the module contract (`:46-48`) reserves exit 2 for "unreadable or
refused".

```
mkdir -p $S/wit-ro; chmod 555 $S/wit-ro
python3 $S/lane/tools/kama-live-replay.py --receipt $S/lane/.ufo/waves/round-48/c2/live/receipt-2.json \
  --work $S/work-ro --out $S/replay-ro.json --witness-dir $S/wit-ro --witness-timeout 5
# replay match=False refused=None mismatches=2 exit=1
# rerun receipt: outcome setup-error, setup_error/internal_fault internal:PermissionError,
#                no "witness" key, teardown {returncode 0, sigterm true, sigkill false, port_refuses true}
```

No server leaked on this path either (checked: no process, no listener), and the fix is a one-line
`Refused` for `rr["outcome"] == "setup-error"` when the original was a completed run. Low severity:
C1 already treats any non-zero replay exit as a problem (`tools/round49-replay-witness-audit.py:319-321`).

## Not tested / out of scope
* `release` created *during* the hold → succeeded path (C1's own leg and seat K1Fresh cover it; K1Fresh measured `released=true waited_ms=27403`).
* SIGINT/SIGTERM to the harness while it holds (peer seat `X1Kill` owns signal handling); the `release`-after-expiry race; `--witness-timeout` values below one poll interval.

## Housekeeping
* Lane `/home/vgpnk/Projects/shokunin/kama-shokunin` read-only throughout: no `git`/`jj` mutation, no in-place edit; the only lane writes are this report and `.ufo/waves/round-49/w1/out/X1Timeout/`.
* Scratch `/fast/scratch/hyaku/kama-r49/X1Timeout` removed after copying the evidence below; no `/tmp` path is cited; `pgrep -af X1Timeout` empty, none of the three witness ports listening.
* No tool installs or upgrades (nothing was needed; no pacman).

## Evidence files (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X1Timeout/`)
| file | sha256 |
|---|---|
| `replay-timeout-5s-run1.json` | 45d09d074de2d2efcd5b0ba1b5b229bb958b8a55ba77f0da798272eb6d941fcd |
| `replay-timeout-5s-run2.json` | 680b73e25c7891e6ead8795e8c2968830802bd409fdeb7d74cd356e9f29b9f3d |
| `replay-timeout-5s-run3.json` | 78bc76aa6cfdf3dab2d68547a1e83c4b7a7037bb78ffbb2be68f5e89126a268d |
| `rerun-receipt-run1.json` | 8b0b412755d4468fc8775512cc3fc77f99a50620c71eaefa0724b5a6fadec66e |
| `rerun-receipt-run2.json` | c1b4faa80a5de2f6a132788f7a86ec7911e16e5e20e9bf0c1763827b8fa3e7c7 |
| `rerun-receipt-run3.json` | 71c2775a12f16b371a01bc8ba2ef41466de87a5c7d006613b147f49ade0bcba3 |
| `timeline-run1.log` / `-run2.log` / `-run3.log` | a79852cb… / 9a4cc7b6… / 465d19f9… |
| `replay-run1.log` (identical in all three) | 8116d78fdaf599bcea5d4f14ce6f0af634fde98a21637e783d3736732d284b73 |
| `replay-stale-release.json` | 1f51544febc7229b242840afc69c84e0ea90fe14e72ac54f24ebc74f2816247e |
| `rerun-receipt-stale-release.json` | 437f5997958ccecccf53f4aa85a8f6d175819dd01e8c5eda67dc572c8a4bb8b0 |
| `replay-unwritable-dir.json` | 8415d97c406613fdafc83a28c25653ae110cae6c5e4c03b60394c728bb0b9ebe |
| `rerun-receipt-unwritable-dir.json` | e620daa04e31881dbf9c14ea7d032227c77408365a75607ae3231fc829613709 |
| `argument-errors.txt`, `method-watch-run{1,2,3}.sh`, `proposed-fixes.diff` | transcripts, harnesses, proposed diffs |
