VERDICT: partial — targeted runtime faults are contained, but one finalizer operation still escapes without a receipt.

# Round-18 ToolFaultPaths — bounded falsification

## Scope and evidence

Reviewed the pushed `1c325b2e58fcfdc6761f645b44cedfb1d65243e6` version of `tools/kama-llamacpp-live.py` in the required seat clone. I preserved that exact source at `/tmp/kama-r18-falsify-ToolFaultPaths/exp/pristine.py` (SHA-256 `dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b`), then copied only the parent’s newer uncommitted `tools/kama-llamacpp-live.py` into the clone for the requested atomic-publish residual check (SHA-256 `ec7a756712f10e628e7b02c45614fa29f106c096b5b2f016da95d09104cc69da`). No lane file was edited by this seat.

Runtime: Python 3.14.8. Server: `/home/vgpnk/.local/opt/llama-b11755/llama-server`, SHA-256 `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`. Model: `stories260K.gguf`, SHA-256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`. Probe: `tools/kama-probe.sh`, SHA-256 `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`.

The unfaulted run from the preserved pushed source exited 0, reported `pass`, and had 11/11 checks true (receipt SHA-256 `3c976eff25e9dde128b4c1239091ac1610fe3131627c55f0fa2fd0ea5c946b3a2`). Official retained `live-1` also records exit 0. No tools were installed or updated.

## Findings by severity

### P2 — unguarded `tuple(old_handlers)` can abort the finalizer before teardown and receipt emission

**Location:** `tools/kama-llamacpp-live.py:1403-1408` at the pushed revision. At line 1404, `tuple(old_handlers)` is evaluated before entering the per-handler `try` at line 1405. A `BaseException` from that expression therefore escapes the `finally` block before the subsequent teardown, safety-net kill, and `_emit` paths.

**Exact injection:** loaded the preserved pushed module, replaced its global `tuple` with a function that raises `RuntimeError`, set ordinary valid `--server`, `--model`, `--model-sha256`, and a writable `--out`, and called `main()`:

```python
import importlib.util, sys
spec = importlib.util.spec_from_file_location(
    "tool", "/tmp/kama-r18-falsify-ToolFaultPaths/exp/tools/pristine-copy.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
def fail(values):
    raise RuntimeError("injected at finally tuple(old_handlers)")
m.tuple = fail
sys.argv = [
    "kama-live",
    "--server", "/home/vgpnk/.local/opt/llama-b11755/llama-server",
    "--model", "/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf",
    "--model-sha256",
    "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d",
    "--out", "/tmp/kama-r18-falsify-ToolFaultPaths/scratch/rec-unguarded-epilogue.json",
]
m.main()
```

**Observed:** process exit 1; stderr traceback identifies `main`, `line 1404`, `for sig in tuple(old_handlers):`, ending `RuntimeError: injected at finally tuple(old_handlers)`; `receipt_exists=False`. The output path was already parsed and writable. The hook is synthetic; the normal built-in operation is materializing a tuple from the ordinary signal-handler dict, for which allocation failure (`MemoryError`) is a realistic `BaseException` route. The injection demonstrates the unguarded boundary, not a naturally induced `MemoryError`. Since the failure interrupts the finalizer before `teardown`, explicit harness cleanup and the receipt do not run; the separately configured child parent-death signal is not a substitute for this cleanup/receipt contract.

### P3 — interrupted atomic receipt publish leaked a sibling temporary in the pushed version; parent’s newer working-tree copy fixes this tested case

**Pushed location:** `tools/kama-llamacpp-live.py:1117-1126` at the assigned revision. The cleanup around the temporary file caught only `OSError`, so a `KeyboardInterrupt` from `os.replace` escaped without unlinking the already-written sibling temporary.

**Exact fault:** patch `os.replace` to raise `KeyboardInterrupt('injected at os.replace during _emit')` on its first call and delegate to the real `os.replace` on its second call; run the real pinned server/model with writable `--out` in a fresh directory. On the pushed bytes: `exit: 2`, `replace_calls: 2`; the final receipt was `setup-error` with `setup_error` and `internal_fault` both `internal:KeyboardInterrupt`, and teardown recorded `sigterm_sent=true`, `returncode=0`, `port_refuses=true`. The output directory contained `receipt.json` **and** leaked `.kama-live-ugdnznad` (first-attempt receipt SHA-256 `2146dc72c2a1d91445eee3d8ca03ad1476e3f82248ed0a0697d1b13f99d3c65b`).

The parent’s newer uncommitted copy changes the cleanup handler to `except BaseException` and adds an atomic-publish selftest. I copied only that file into the seat clone and reran the same `os.replace` first-call injection (no full matrix rerun): `exit: 2`, `replace_calls: 2`; receipt outcome `setup-error`, both fault fields `internal:KeyboardInterrupt`; teardown `sigterm_sent=true`, `returncode=0`, `port_refuses=true`; directory contained only `receipt.json`, no `.kama-live-*` temporary (receipt SHA-256 `1fe5b074b289542ee54fea58edacc036338f532b2afc41e699b7b4392ad3ba16`). New copied-tool SHA-256: `ec7a756712f10e628e7b02c45614fa29f106c096b5b2f016da95d09104cc69da`. This is a passing residual check of that newer copy, not evidence that the pushed hash itself had the fix.

## Targeted runtime matrix — pushed source

The fault hook was inserted at the first executable statement of `readiness_loop`, `teardown`, or `_emit`; rehash faults were raised by a `sha256_file` wrapper armed only after teardown returned. For each target site, the selected exception was `KeyboardInterrupt`, `SystemExit`, or `RuntimeError`.

| Injected site | Observed result for each of KI / SE / RE |
|---|---|
| `readiness_loop` | exit 2; receipt `outcome=setup-error`, `setup_error=internal:<type>`, `internal_fault=internal:<type>`; `sigterm_sent=true`, `port_refuses=true`; child return code `-15`. |
| `teardown` entry | exit 2; same internal receipt token; teardown catch followed by safety-net `SIGKILL`, `returncode=-9`, `port_refuses=true`. |
| post-teardown model rehash | exit 2; same internal receipt token; teardown had already completed. |
| first `_emit` call | with both stdout and writable `--out`, exit 2 and a valid re-emitted receipt with the same internal token when the second emit was allowed to complete. |

Representative retained receipt hashes: readiness KI `623ba8541956fabf78802da854cfd9979112289dd971ad7664e2597de81a6df4`; teardown KI `c5696f45c953e0e400771f48587bcb4e9b02dc65a954a620db96259490eb8e24`; rehash KI `fae12fefbe2054ba866eb1205087643312cfbe1c68c3c54e8992f2e06cafa4c0`.

An `OSError` injected only at the post-teardown model rehash is intentionally graded as an evaluated failure instead: receipt `model_sha256_post=rehash-error:[Errno 13] ...`, `model_unchanged=false`, outcome `fail`, exit 1. This is distinct from non-`OSError` internal `BaseException` faults and was not misreported as setup-error.

**First-timestamp pre-check:** patched `_utc_now()` to raise `RuntimeError('injected at _utc_now (started_utc)')` on its first invocation. It is called inside the outer `try` at line 1195, after receipt construction; result was exit 2 with a receipt carrying `setup_error=internal:RuntimeError` and `internal_fault=internal:RuntimeError` (receipt SHA-256 `edfe021cb13bf8574a9fb437bc81ef183e148d539618635c2e7df2f073feef3e`). No child had yet launched. A separate fault on the second `_utc_now()` call (`ended_utc`, line 1540) also produced exit 2 and an internal RuntimeError receipt (SHA-256 `8b7324e9238ac2c22934ba2facf624df125f298aeed049e14e19511c4a963797`).

**Mutation control:** a fresh targeted mutant changed only the outer handler at original line 1402 from `_record_internal(receipt, exc)` to `raise`; the one-line source diff was the only change from preserved source after accounting for the readiness injection hook. Same readiness `RuntimeError` was green on pristine (exit 2, `setup-error`, `internal:RuntimeError`; receipt SHA-256 `ca070f29c77123009efdea281ec07f7af12a9204e6d0023c296cf56ed63bd391`) and red on the mutant (exit 1; receipt `outcome=fail` with no setup/internal token; receipt SHA-256 `4be9a7525c2483571a2729063580821d6612f4d17a803341a51105133e5e671c`). Mutant source SHA-256 `003420f140c1f4961d38f7fbc41eb23846e784b5da76139b6140005ba95f80ff`. The pushed source copy remained byte-identical at `dc036d7d…b811a04b`; no in-place source mutation required restoration. This is a fresh targeted control, not an addition to the named round-17 denominator.

## Signal and CLI behavior

A loopback-only fake server on ephemeral port 51065 accepted connections without replying and ignored SIGTERM. Sending SIGINT to the harness during readiness produced a receipt with `setup_error=terminated:signal 2`, exit 2, then teardown `sigterm_sent=true`, `sigkill_sent=true`, `returncode=-9`, `port_refuses=true`. End-to-end exit followed the configured `TERM_GRACE=10s` escalation and took about 10.03 seconds; the signal was not converted to a pass or swallowed. The bounded delay is the expected teardown grace for this deliberately TERM-immune child, not a fast-exit guarantee.

No blanket help/usage conversion was observed on pushed bytes: `--help` exited 0 with argparse usage; an unknown flag and missing required model arguments each exited 2 with argparse’s own error text, before receipt creation. Per the parent’s stated boundary, parser/build-parser failures before arguments and `--out` are parsed are not treated as a promised receipt-file path. I did additionally inject `RuntimeError` from `build_parser()` at `main` line 1132: exit 1, traceback to the injected exception, no receipt. This is pre-parse and distinct from the caught first `_utc_now()` fault above.

## Exact fault-hook source

The readiness/teardown/emit hook used for the matrix was inserted inside each function body, not at module definition time:

```python
spec = open('pristine.py').read()
lines = spec.split('\n')
targets = {'readiness_loop': 'readiness', 'teardown': 'teardown', '_emit': 'emit'}
out = []
for ln in lines:
    out.append(ln)
    for name, where in targets.items():
        if ln.startswith(f'def {name}('):
            out.append(f"    import fault_shim; fault_shim.maybe('{where}')")
open('tools/injected.py', 'w').write('\n'.join(out))
```

For readiness and teardown, `tools/fault_shim.py` was:

```python
import os
def maybe(where):
    fault = os.environ.get('FAULT') or ''
    parts = fault.split(':')
    if parts and parts[0].lower() == where:
        exc = parts[1] if len(parts) > 1 else 'RuntimeError'
        raise {'KeyboardInterrupt': KeyboardInterrupt,
               'SystemExit': SystemExit,
               'RuntimeError': RuntimeError}[exc](f'fault-injected at {where}')
```

For the emission call-count control, the emit hook counted calls and raised only on selected `FAULT_NTHS` values; this permitted the first publish fault to be followed by one successful retry, and separately confirmed that two consecutive injected failures can prevent output. As directed by the parent, repeated output failure is treated as an unavailable-output boundary, not a receipt-pass claim.

## Residual risk and verification gaps

- The actionable open gap is the unguarded finalizer tuple materialization at pushed line 1404. It can bypass explicit cleanup and receipt emission; parser/help boundaries are separate.
- The interrupted-temp-file defect is present in the pushed hash but passes the exact requested recheck in the parent’s newer uncommitted file copy. Main must preserve that updated implementation when integrating.
- The `tuple(old_handlers)` injection replaces a module global to force the exact expression to raise; no natural `MemoryError` was induced. The six named subject controls and official counters were not rerun.
- No LSP device/server was mounted in this seat, so LSP status/references/definition/diagnostics were unavailable; the citations above are from opened source lines and exercised behavior, not grep-as-semantic-proof.
- No package/tool installs. Final checks showed no matching seat `llama-server`/fake-server process or listener and no listeners on ports 8080 or 34113. All launched listeners used ephemeral loopback ports. No official counting command was run by this seat.
