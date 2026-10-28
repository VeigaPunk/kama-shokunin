# A03C1WitnessSpoof — C1 live-witness field spoof probes

## Setup and evidence

Used pinned master bytes at `65d7cad0fce90e34de37527cde22e97b63b118bf` for `tools/round62-c1-counter.py`, `tools/kama-completion-live.py`, and `tools/kama-llamacpp-live.py` (SHA-256 respectively `275610b51eb1be219cdaa3c3e15e3568b590f35e7a1b3ceb42ab0374243f4d8d`, `71ac4f2c45570a79cb1e80db91e85268609f28bf4dd421d628ffb9d10243771f`, `98d2e6bb48a90e60797df0d2bee895eac4a6cdd9859af2dc47b64bdb4a36fbe9`). The model and server hashes matched the pinned values. The counter's `witness_run()` launched the pinned tool, made its own outside request during hold on an unregistered loopback port, and returned a genuine witness (port `35295`, child PID `891292`, nonce `r62-6501cbb56b`). No dependencies were installed or updated.

Exact probe command:

```sh
cd /fast/scratch/hyaku/kama-r62/w/A03C1WitnessSpoof && TMPDIR=/fast/scratch/hyaku/kama-r62/w/A03C1WitnessSpoof python3 probe.py
```

The command output is preserved verbatim in `out/A03C1WitnessSpoof/probe-results.json`; the receipt and runnable probe are also preserved alongside it.

## Results

For each case, only the named witness field was changed from the genuine witness. I classify acceptance by `score()['live']`, the witness-specific predicate; `score()['met']` was false in the baseline and all probes because `score()['inconsistent']` contained `unexpected-checks` (see caveat below).

| Forgery | Result (`live`) | Observed score details |
|---|---|---|
| `server_sha256 = '0'*64` | REJECTED | `live=false`; pinned server digest check fails. |
| `model_sha256 = '0'*64` | REJECTED | `live=false`; pinned model digest check fails. |
| `pid = -1` | REJECTED | `live=false`; no longer equals receipt child PID. |
| `text = 'text from different model'` | **ACCEPTED** | `live=true`; arbitrary replacement string is accepted. |

The text result is the counterexample: `score()` checks only `isinstance(witness.get('text'), str)` and never binds that text to the completion body captured in the receipt or to the outside response bytes. A forged different-model text therefore passes the witness subpredicate, although it does not change the independent `met` result in this run.

## Baseline caveat

The captured genuine receipt had verdict `REQUEST_OK`, `alltrue=true`, and a real live witness, but `score()` returned `met=false`, `inconsistent=['unexpected-checks']`. The captured checks included `hold_released`, while the pinned counter's `grade()` recomputation in the saved receipt comparison did not include that key; strict key-set matching marked the baseline inconsistent. This is independent of the text-forgery acceptance and means this probe did not establish an end-to-end `met=true` forged receipt. Do not interpret the `live=true` result as an accepted C1 claim; it demonstrates the witness subpredicate's missing content binding.

Smallest safe correction: bind the outside witness's text to an independently captured/validated response body (or carry and hash the exact outside response bytes and recompute its parsed text), rather than accepting any string. Separately reconcile the `hold_released` check name with the grader's required check set so a genuine receipt can reach a clean baseline score.

Counter/tally: accepted witness-field forgeries `1/4` (`text`); rejected `3/4` (`server_sha256`, `model_sha256`, `pid`).
