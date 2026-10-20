VERDICT: confirm — all six named mutants survive the frozen detector; each has a distinguishing fault rejected by pristine/restored current check.py.

# Scope and axes

Seat: `KamaR18.MutBaselineH-2`. **Calibration** is the primary axis: measure the frozen detector's actual sensitivity to the six named grading weakenings. **Operability** is the safety axis: bounded executable probes, loopback/protected-port isolation, exact restoration, and teardown. Coverage distinctions tested are reason case, verdict whitespace, HTTP method, ID normalization, zero requests, and first-versus-last output-row selection. This is C2 before-evidence/advice, not round admission, an official measurement, integration, or a runtime judgment.

The lane's `master` read `e75cf680b53484a61709ee1b2787d8dbc6419f74`. I cloned it into `/tmp/kama-r18-KamaR18.MutBaselineH-2`, created branch `seat/KamaR18.MutBaselineH-2` there, and copied the lane's CURRENT `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py` into the clone. That current file and the clone's saved pristine bytes both hashed to `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099`. All checker citations below describe this captured snapshot; they do not claim to measure later integrated bytes.

Read context: `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md:275-279`, quote: “all survive both detectors”; `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17-verifier-spotcheck.md:14-15`, quote: “the H1–H3 and H5–H7 mutants still survive.” The actual new observations below confirm that bound against the assigned frozen detector.

# Fixed detector and actual results

The exact detector was `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_probe-verdicts_fault-controls.py`, SHA-256 `d3eaadeb8a061b4e322868d569df77afbd7331089d06b06c86a2063fdc31b312`, unchanged throughout. Its contract is at lines 15-24, quote: “Exit codes: 0 no accepted faults | 1 at least one accepted | 2 own fault.” Its positive-control gate is at lines 762-767, quote: “suite INVALID — positive control”.

Each detector invocation actually used this argv (with the same path reused for one isolated mutation at a time):

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/kama-r18-KamaR18.MutBaselineH-2/guard TMPDIR=/tmp/kama-r18-KamaR18.MutBaselineH-2/tmp python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_probe-verdicts_fault-controls.py --check /tmp/kama-r18-KamaR18.MutBaselineH-2/tests/probe-verdicts/check.py --probe /tmp/kama-r18-KamaR18.MutBaselineH-2/tools/kama-probe.sh --matrix-dir /tmp/kama-r18-KamaR18.MutBaselineH-2/tests/probe-verdicts --json
```

The explicit `--probe` and `--matrix-dir` are necessary because the frozen script's defaults are relative to its own relocated path (lines 60-64). The script itself copies the check and nine matrix files into disposable scratch (lines 9-13, quote: “byte copies of the nine sibling matrix”). All such temporary files stayed below this seat's `/tmp` clone through `TMPDIR`.

All F0–F8 ran, including the full slow F7 and all six F8 variants; no `--skip-slow` or `--only-fault` filtering was used. Every invocation reported the pinned matrix set: 9 files, 72 tests, SHA-256 `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32`. The real probe copy hashed to `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`.

Cell notation below is **detector exit / detected faults / accepted faults**. “Accepted” here counts registered F1–F8 faults, not mutants. A mutant survives when the detector still reports its healthy baseline despite the injected weakening.

| Mutant | Pristine | Mutated | Restored | Mutant verdict |
|---|---|---|---|---|
| H1 reason casefold | 0 / 8 / 0 | 0 / 8 / 0 | 0 / 8 / 0 | **SURVIVED** |
| H2 verdict strip | 0 / 8 / 0 | 0 / 8 / 0 | 0 / 8 / 0 | **SURVIVED** |
| H3 route ignores method | 0 / 8 / 0 | 0 / 8 / 0 | 0 / 8 / 0 | **SURVIVED** |
| H5 normalized served IDs | 0 / 8 / 0 | 0 / 8 / 0 | 0 / 8 / 0 | **SURVIVED** |
| H6 zero-request branch passes | 0 / 8 / 0 | 0 / 8 / 0 | 0 / 8 / 0 | **SURVIVED** |
| H7 grade last row | 0 / 8 / 0 | 0 / 8 / 0 | 0 / 8 / 0 | **SURVIVED** |

**Total: 0 killed, 6 survived, 0 inconclusive.** Pristine F0 was healthy, so no baseline failure was counted as a kill. There were 13 completed full-detector invocations: one initial pristine, six mutant, six restored. Each restored run also supplies the unchanged pristine baseline immediately preceding the next mutation. Mutants never overlapped. Full `positive_control` and `faults` JSON objects, including their explanations, compared equal across every invocation; this is stronger than an accepted-count-only comparison. Only metadata such as checker hash, paths and elapsed time was excluded from that comparison.

The common actual output projection was:

```json
{
  "detected": 8,
  "accepted": 0,
  "F0": {"check_exit": 0, "detected": true},
  "fault_check_exits": {
    "F1": 1, "F2": 1, "F3": 1, "F4": 1, "F5": 1,
    "F6": [1, 1, 1, 1], "F7": 1, "F8": [1, 1, 1, 1, 1, 1]
  }
}
```

`fault_check_exits` is this report's extraction, not an original top-level field. Every F1–F8 `detected` was true. F0's literal explanation was “check exited 0 with JSON; all 5 rows passed (positive control healthy)”. No outer timeout, traceback, parse failure or failed detector invocation occurred in these 13 runs.

# Exact mutations, expected detector, and coverage gap

I used the exact edits from `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/falsify/advice/MutC1Preregistered.md:24-83` and `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/falsify/advice/MutC1Preregistered2.md:22-56`. The resulting mutant hashes also exactly reproduce those reports' hashes.

## H1 — case-insensitive reason

Checker site: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:475`, quote: `and record["reason"] == expected["reason"]`. Sole replacement:

```python
            and record["reason"].casefold() == expected["reason"].casefold()
```

Expected existing detector: F1. Actual F1 still exits 1 and detects its reason fault on all three rows, while the overall detector exits 0, accepted 0. The missing distinction is case-only corruption: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_probe-verdicts_fault-controls.py:283-284`, quote: `row["reason"] = str(row.get("reason")) + "-forged"`.

## H2 — whitespace-normalized verdict

Checker site: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:474`, quote: `record["verdict"] == expected["verdict"]`. Sole replacement:

```python
            record["verdict"].strip() == expected["verdict"].strip()
```

Expected existing detector: F4. Actual F4 still exits 1 and detects its verdict fault on all three rows; overall exit 0, accepted 0. It tests lowercasing, not surrounding whitespace: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_probe-verdicts_fault-controls.py:285-289`, quote: `row["verdict"] = v.lower()`.

## H3 — route method ignored

Checker site: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:374-376`, quote: `return any(r.get("method") == "GET"`. Replace the three-line return with exactly:

```python
    return any(r.get("path", "").split("?", 1)[0] == "/v1/models"
               for r in requests)
```

Expected existing detector: F6. Actual F6 still exits `[1,1,1,1]`; overall exit 0, accepted 0. It changes the path, not the method on the right path: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_probe-verdicts_fault-controls.py:242-243`, quote: `hit("/health")`.

## H5 — normalized served IDs

Checker site: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:470-471`, quote: `record["served_model"] == record["served_model_expected"]`. Replace only that assignment with:

```python
        record["served_model_ok"] = (
            [sid.lower().removesuffix(".gguf")
             for sid in (record["served_model"] or "").split(",")]
            == [sid.lower().removesuffix(".gguf")
                for sid in record["served_model_expected"].split(",")])
```

Expected existing detector: F5. Actual F5 still exits 1 and detects its served-ID fault on all three rows; overall exit 0, accepted 0. The frozen fault is an unrelated ID, not a normalized variant: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_probe-verdicts_fault-controls.py:292-293`, quote: `row["served_model"] = "kama-forged-id"`.

## H6 — zero requests still passes

Checker site: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:454-459`, quote: “stub accepted no requests; probe never”. Insert only this line after the error assignment and before the early return:

```python
            record["passed"] = True
```

Expected existing detector: route/error controls F6–F8. Actual F6, F7 and all F8 variants remain detected; overall exit 0, accepted 0. F6 makes a `/health` request (frozen detector lines 242-243, quote: `hit("/health")`), malformed modes run the real probe first (lines 253-259, quote: “The real probe still runs”), and F7 returns through the earlier timeout branch (checker lines 447-451, quote: `return record`). None of those exercises this normal-return/no-request branch.

## H7 — grade last rather than first row

Checker site: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:397`, quote: `row = rows[0]`. Sole replacement:

```python
    row = rows[-1]
```

Expected existing detector: malformed-output F8. All six F8 variants remain detected; overall exit 0, accepted 0. Its input list has no contrasting valid first/last object pair: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_probe-verdicts_fault-controls.py:170-187`, quote: `"body_b64": base64.b64encode(b'{"rows":[null]}').decode(),`. First-row grading is the documented current contract, not a new exact-one-row requirement: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:382-384`, quote: “first element is an object”.

# Minimal distinguishing faults — actually run

These proposals were exercised, not merely inferred. Each single-row check printed parseable JSON. Columns give **checker exit / passes / failures**, not detector exits. All six faults are rejected by the unmutated current checker and accepted by their corresponding mutant; the final restored checker rejects all six again. A positive seed/cache run before each complete pristine/restored fault set exited 0 with 1 pass and 0 failures.

| Mutant | Minimal fault and selected matrix row | Pristine current | Corresponding mutant | Final restored current | Deciding observed field |
|---|---|---|---|---|---|
| H1 | On `ReadyControls.expect-exact-id`, change only reason `matched` → `Matched` | 1 / 0 / 1 | 0 / 1 / 0 | 1 / 0 / 1 | reason differs only by initial-case byte |
| H2 | On `LoadingEnvelope.canonical-alias`, append one ASCII space: `MODEL_LOADING `; preserve reason, drift and probe exit 2 | 1 / 0 / 1 | 0 / 1 / 0 | 1 / 0 / 1 | verdict has one trailing space; route and served-ID checks stay true |
| H3 | Replay cached correct ready-row stdout/exit; make only POST `/v1/models`, never GET | 1 / 0 / 1 | 0 / 1 / 0 | 1 / 0 / 1 | identical requests `[POST /v1/models]`; `route_ok` false → true → false |
| H5 | On `ReadyControls.expect-exact-id`, change only served ID `kama-ready` → `kama-ready.gguf` | 1 / 0 / 1 | 0 / 1 / 0 | 1 / 0 / 1 | expected stays `kama-ready`; `served_model_ok` false → true → false |
| H6 | Replay cached correct ready-row stdout/exit without making any request | 1 / 0 / 1 | 0 / 1 / 0 | 1 / 0 / 1 | requests stay `[]`; error stays populated; only mutant reports passed true |
| H7 | Run real ready probe, then emit `[bad_first, original_last]`; bad first differs only by reason `matched-forged` | 1 / 0 / 1 | 0 / 1 / 0 | 1 / 0 / 1 | pristine/restored grade `matched-forged`; mutant grades last row's `matched` |

H3 and H6 necessarily inject **request behavior plus cached output**, not just a JSON-field fault: their mutated sites depend on the stub's actual request log. The seed was obtained by the real unchanged probe on that same literal matrix row, not by guessing an expected output. All other faults run the real probe and preserve its exit. H1/H3/H5/H6/H7 have probe exit 0; H2 has probe exit 2. H2 deliberately uses a non-`MODEL_OK` row so raw-verdict drift and served-ID guards do not independently reject the padded verdict.

Matrix anchors: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/ReadyControls.json:42-43`, quote: `"expected": {"verdict": "MODEL_OK", "reason": "matched", "exit": 0}`; `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/LoadingEnvelope.json:24-25`, quote: `"expected": {"verdict": "MODEL_LOADING", "reason": "llamacpp-loading", "exit": 2}`. Each fault tests the same checker site cited in its H-section above.

Actual H6 mutation observation, projected from checker stdout:

```json
{"tests":1,"passes":1,"failures":0,"probe_exit":0,"requests":[],"route_ok":false,"verdict":null,"reason":null,"served_model":null,"error":"stub accepted no requests; probe never reached a listening socket","passed":true}
```

Pristine and restored report the same requests, error, null fields and probe exit, but `passed:false`, totals `passes:0, failures:1`, and checker exit 1. This is not a wrapper failure being mistaken for a field-fault kill.

## Reproduction of the distinguishing inputs

The following is the actual scratch `/tmp/kama-r18-KamaR18.MutBaselineH-2/holdout.sh` body, retained here because scratch was removed. It is a reproduction recipe, not a surviving `/tmp` evidence dependency:

```sh
#!/usr/bin/env bash
exec python3 - "$@" <<'HOLDOUT_EOF'
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.request

root = Path('/tmp/kama-r18-KamaR18.MutBaselineH-2')
args = sys.argv[1:]
mode = os.environ['HOLDOUT_MODE']
cache = root / 'ready-output.cache'

def opt(flag):
    return args[args.index(flag) + 1]

if mode in ('H3', 'H6'):
    if mode == 'H3':
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        request = urllib.request.Request(
            'http://127.0.0.1:' + opt('--port') + '/v1/models', method='POST')
        with opener.open(request, timeout=3) as response:
            response.read()
    sys.stdout.write(cache.read_text())
    sys.exit(int((root / 'ready-output.rc').read_text()))

result = subprocess.run(['bash', str(root / 'tools/kama-probe.sh'), *args],
                        capture_output=True)
if mode == 'seed':
    cache.write_bytes(result.stdout)
    (root / 'ready-output.rc').write_text(str(result.returncode))
    sys.stdout.buffer.write(result.stdout)
else:
    doc = json.loads(result.stdout)
    row = doc['rows'][0]
    if mode == 'H1':
        row['reason'] = row['reason'][0].upper() + row['reason'][1:]
    elif mode == 'H2':
        row['verdict'] += ' '
    elif mode == 'H5':
        row['served_model'] += '.gguf'
    elif mode == 'H7':
        doc['rows'].insert(0, dict(row, reason=row['reason'] + '-forged'))
    else:
        raise ValueError('unknown holdout mode ' + mode)
    print(json.dumps(doc))
sys.stderr.buffer.write(result.stderr)
sys.exit(result.returncode)
HOLDOUT_EOF
```

The actual child argv was `python3 /tmp/kama-r18-KamaR18.MutBaselineH-2/tests/probe-verdicts/check.py --probe /tmp/kama-r18-KamaR18.MutBaselineH-2/holdout.sh --only ReadyControls.expect-exact-id --json`, with `HOLDOUT_MODE` set to `seed`, `H1`, `H3`, `H5`, `H6`, or `H7`. H2 used the same argv except `--only LoadingEnvelope.canonical-alias` and `HOLDOUT_MODE=H2`. The environment also carried the identical guard/TMPDIR/PYTHONDONTWRITEBYTECODE settings shown for the fixed detector. These ran on initial pristine bytes, on each corresponding mutant, and on final restored bytes; the positive seed was run on pristine and final-restored bytes.

# Before / mutation / exact-restoration hashes

Let **P** denote `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099`, the actual saved pristine checker SHA-256. Each restoration reversed only that mutation. Before every restored detector invocation, `cmp -s /tmp/kama-r18-KamaR18.MutBaselineH-2/check.pristine /tmp/kama-r18-KamaR18.MutBaselineH-2/tests/probe-verdicts/check.py` exited 0. The recorder also hashed the checker before and after each detector run; each run's two hashes were identical.

| Mutant | Before SHA-256 | Mutation SHA-256 | Restored SHA-256 | Exact byte comparison |
|---|---|---|---|---|
| H1 | P | `036f2103aef304fb545ca65b2a0f206335b3c7c4e84fdd0626ead74eb04c3bd5` | P | true |
| H2 | P | `e78796341f17d274de93ed0df556c47265f8f615d81365afc9c698a7042ec6e6` | P | true |
| H3 | P | `7f67387a3958e138fe77bab39b77fe6280d54a1e4b8abb880dd0a41f6fd4692d` | P | true |
| H5 | P | `fab14d2da26568cce976747d10e2a8a5a1264621941b67e237330e85f9dba1e6` | P | true |
| H6 | P | `30623b53c544b6e2f6011375ab22aea81a07ef0a650c8ff942dcd0b68519004f` | P | true |
| H7 | P | `eb7b2ad5008fb6e6593055f444ec0cd46c183b57dd85337570250e18f9632d05` | P | true |

The final independent byte comparison returned `exact_bytes:true` and final SHA-256 P. The full fixed-detector F0/fault records also returned to their exact pristine values after each restoration.

# Bounds, teardown, limitations, installs

- Each full-detector subprocess had a 240-second outer cap and its own process session. The frozen detector retained its own 150-second per-check cap and full F7. Each holdout checker had a 90-second outer cap. All completed without an outer cap firing. Processes and observations were serialized where they shared checker bytes or served a stub; independent source reads/preparation ran concurrently. No two mutants or synthetic servers were deliberately run concurrently by this seat.
- A scratch-only `sitecustomize.py` uniformly replaced ephemeral socket allocation with randomly selected `127.0.0.1` ports in 49152–65535, rejected non-loopback/protected binds, and logged successful binds. This identical safety environment was used in pristine, mutant and restored phases; no grading logic was patched by that guard. The protected registry was read at `/home/vgpnk/Projects/shokunin/kama-shokunin/registry/endpoint-consumers.tsv:35-37` (quote: `http://127.0.0.1:34113`); protected ports were 8080 and 34113.
- Actual final listener audit, using logged owned PIDs and `ss -ltnp` (exit 0): `owned_bind_count=787`, `owned_process_count=293`, observed ports 49163–65526, `forbidden_binds=[]`, `owned_pids_still_listening=[]`. The count includes temporary bound-then-closed dead-port reservations, not just listening servers.
- Cleanup process-path sweep `pgrep -af '/tmp/kama-r18-KamaR18[.]MutBaselineH-2'` exited 1 with no output. `rm -rf /tmp/kama-r18-KamaR18.MutBaselineH-2 && test ! -e /tmp/kama-r18-KamaR18.MutBaselineH-2 && ss -ltnp` exited 0. The clone, generated wrappers, guard, caches, drivers and raw observation files were removed. Other host/concurrent-seat listeners remained and were not stopped.
- The first asynchronous pristine launch was refused before execution with “Background job limit reached (100).” Its synchronous retry produced the one recorded pristine run. This was not a detector baseline failure. No detector was rerun to erase a failing observation.
- No lane source, matrix, frozen byte, tracked lane file, index, jj state, manifest, old report/lesson, sibling source, operator model/runtime or host service was changed. No llama-server or model was launched. No official round-18 measure/survivor command, official lane-checkout gate, pair grid, broader suite, build, formatter or linter was run. The only lasting write is this scoped report.
- These are six bounded **coverage findings**, not permission to casefold reasons, strip verdicts, normalize IDs, ignore GET, pass empty-request branches, or change the first-row contract. The new faults were separate diagnostic probes; they were not added to the frozen detector and do not change its six SURVIVED results.
- **Installs/updates: none.** Existing `python3 --version` printed **Python 3.14.8**. No pacman transaction, runtime installation, service restart or downgrade occurred.
