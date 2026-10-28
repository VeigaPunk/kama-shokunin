# A02C1HoldTamper — C1 hold witness tamper

Axis: operability. Probe ran the frozen master bytes at `65d7cad0fce90e34de37527cde22e97b63b118bf`. No tools installed or updated.

## Counter-race probe

Exact command launched by the probe:

```sh
python3 /fast/scratch/hyaku/kama-r62/w/A02C1HoldTamper/source/round62-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip master --work /fast/scratch/hyaku/kama-r62/w/A02C1HoldTamper/counter-work
```

Before the counter created its release marker, the probe replaced `hold.json`'s `pid`, `port`, `alias`, and `model_sha256` with a fake pid, port 1, `tampered-alias`, and 64 zeroes. Probe output:

```text
COMMAND: python3 /fast/scratch/hyaku/kama-r62/w/A02C1HoldTamper/source/round62-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip master --work /fast/scratch/hyaku/kama-r62/w/A02C1HoldTamper/counter-work
TAMPERED hold.json fields pid,port,alias,model_sha256 before counter release
EXIT: 1
STDOUT:
STDERR: Traceback (most recent call last):
  File "/fast/scratch/hyaku/kama-r62/w/A02C1HoldTamper/source/round62-c1-counter.py", line 501, in <module>
    sys.exit(main())
  File "/fast/scratch/hyaku/kama-r62/w/A02C1HoldTamper/source/round62-c1-counter.py", line 440, in main
    s = score(ctl, witness)
  File "/fast/scratch/hyaku/kama-r62/w/A02C1HoldTamper/source/round62-c1-counter.py", line 191, in score
    recomputed, inconsistent = grade(receipt)
  File "/fast/scratch/hyaku/kama-r62/w/A02C1HoldTamper/source/round62-c1-counter.py", line 130, in grade
    u = cj.get('usage') or {}
AttributeError: 'NoneType' object has no attribute 'get'
```

Disposition: **REJECTED by process failure, not a valid completed counter verdict**. The live tool did produce a `REQUEST_OK` receipt and all six real endpoint captures; the receipt's completion response was valid JSON with the expected alias/fingerprint/usage. The counter then crashed while evaluating a synthetic control whose modified completion body did not parse as JSON. Thus this run does not produce the counter's promised 16/16/errors=0 result and cannot be treated as clean evidence that its witness binding detected tampering.

The binding itself is explicit in frozen counter code (`score`, lines 194–206): it requires observed `witness.pid == receipt.child_pid`, `witness.port == receipt.port`, expected alias, model/server digests, and `listener_owned is True`. The witness values are populated from `hold.json` in `witness_run` (lines 239–270), so changing the hold metadata should fail the live predicate; the counter does not separately authenticate the hold-file bytes. Given the counter's crash, this code-path conclusion is not a successful end-to-end tamper rejection.

## Isolated pid probe

An attempted second probe launched the tip-pinned live tool with `--hold-dir` and waited for its `hold.json`; no hold file appeared before the waiting script timed out, so no mutation or score was observed. Its command was:

```sh
python3 /fast/scratch/hyaku/kama-r62/w/A02C1HoldTamper/source/kama-completion-live.py --nonce r62-pidprobe --work /fast/scratch/hyaku/kama-r62/w/A02C1HoldTamper/pid-probe/work --model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --server-sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 --alias kama-completion-probe --hold-dir /fast/scratch/hyaku/kama-r62/w/A02C1HoldTamper/pid-probe/hold --hold-timeout 45 --out /fast/scratch/hyaku/kama-r62/w/A02C1HoldTamper/pid-probe/receipt.json
```

Output: `FileNotFoundError: .../pid-probe/hold/hold.json`. No standalone probe acceptance is claimed.

Smallest safe correction indicated by observed failure: make `grade` handle an unparseable/missing completion JSON as a failed recomputation rather than dereferencing `cj` at line 130; then rerun the live counter and tamper race. This is separate from the witness metadata binding. No source files were changed.
