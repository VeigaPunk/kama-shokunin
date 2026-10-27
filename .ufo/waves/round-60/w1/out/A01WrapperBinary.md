# A01WrapperBinary — C1 fake-binary falsification

**Axis:** operability. **Scope:** `--ollama-bin` wrapper, symlink, and identical-copy variants; frozen C1 counter at the assigned tip. No lane source was changed.

## Results

All three lifecycle invocations used fresh nonces and distinct work dirs under `/fast/scratch/hyaku/kama-r60/A01WrapperBinary/`.

| Variant | Exact invocation | Observed output | Exit | Assessment |
|---|---|---|---:|---|
| Shell wrapper (`exec` of pinned binary) | `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-live.py --ollama-bin /fast/scratch/hyaku/kama-r60/A01WrapperBinary/variants/wrapper --work /fast/scratch/hyaku/kama-r60/A01WrapperBinary/work-wrapper --nonce wrap60a01` | JSON: `binary_sha256=79d6012d485d0f8ea107b051577ba0c9eef99925acf94876ff1c5aa22a63130d`, `binary-digest.passed=false`, `verdict=BINARY_DIGEST_MISMATCH` | 2 | Correctly rejected: the wrapper script itself is not byte-identical, even though it would exec the real binary if run. No server started. |
| Symlink to pinned binary | `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-live.py --ollama-bin /fast/scratch/hyaku/kama-r60/A01WrapperBinary/variants/symlink --work /fast/scratch/hyaku/kama-r60/A01WrapperBinary/work-symlink --nonce symb60a01` | JSON: pinned `binary_sha256=b0a4becfaf872e3ad5d2e9051244e0dfe55409f03d6e2cd9bd9c34400e201b4c`, `running-exe-digest.passed=true`, `listener-owned.passed=true`, `verdict=MODEL_OK` | 0 | Correctly accepted: resolving and hashing the symlink yields the pinned release, and the lifecycle completed. |
| Byte-identical copy in another directory | `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-live.py --ollama-bin /fast/scratch/hyaku/kama-r60/A01WrapperBinary/variants/copy --work /fast/scratch/hyaku/kama-r60/A01WrapperBinary/work-copy --nonce copy60a01` | JSON: pinned `binary_sha256`, `binary-digest.passed=true`, but generation returned HTTP 500 (`llama-server binary not found` in the copied binary's expected relative locations), checks `generate`, `ps-lists-loaded`, and `evidence-after-load` failed, `verdict=FAIL` | 1 | The binary-digest gate correctly accepts this byte-identical copy; the full lifecycle does **not** accept it as successful because the ancillary runtime files were not copied. |

Thus the wrapper is rejected; the symlink and identical copy are accepted by the binary identity check. Only the symlink achieved overall `MODEL_OK` in this test. No accepted variant ran a non-pinned server: the symlink's `/proc/<child pid>/exe` digest was pinned, and the copied executable has that same digest (though its lifecycle failed). The wrapper was rejected before launch. This tests identity of the executable bytes, not a different Ollama implementation masquerading as the pinned one.

## Frozen counter

Command:

`python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round60-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip e0b5b1ead9adb7a5a4744caca8837ec6496e1ca1 --work /fast/scratch/hyaku/kama-r60/A01WrapperBinary/counter`

Exact output:

`tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=3/3 log_rejected=1/1 errors=0 met=True predicate='C1-r60 fresh-nonce live run verifies independently and 7/7 controls are rejected, errors=0'`

Exit: **0** (`met=True`).

## Evidence

Full lifecycle JSON outputs and counter output are copied into this seat's output directory: `wrapper-receipt.json`, `symlink-receipt.json`, `identical-copy-receipt.json`, and `c1-counter.out`. The wrapper and copy verdicts are the tool's JSON verdicts; the corresponding process exits are 2 and 1 respectively, per the tool's `BINARY_DIGEST_MISMATCH` and `FAIL` return paths; symlink `MODEL_OK` returns 0. Counter returned 0.
