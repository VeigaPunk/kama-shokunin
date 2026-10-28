# A04C1SchemaFuzz — C1 receipt-plane adversarial probes

Axis: operability. Source under test: committed master bytes at `65d7cad0fce90e34de37527cde22e97b63b118bf`; the counter was loaded from that same commit via `git show` (working-tree copy was modified, so intentionally not used). No live endpoint was contacted; this item exercised only local `grade()` / `score()` receipt handling.

## Results

Exact command for all probes:

```sh
cd /fast/scratch/hyaku/kama-r62/w/A04C1SchemaFuzz && TMPDIR=/fast/scratch/hyaku/kama-r62/w/A04C1SchemaFuzz python3 fuzz.py
```

The script imports the master counter, sets `NONCE='r62-fuzz'`, and invokes both `grade(receipt)` and `score(receipt, None)` for each receipt.

| Probe | grade | score | Result |
|---|---|---|---|
| Empty receipt / missing captures | REJECTED: `AttributeError: 'NoneType' object has no attribute 'get'` at counter line 130 (`u = cj.get('usage')`) | REJECTED: same exception propagated through `score` | Crash |
| `captures` is a list | REJECTED: same `NoneType.get` exception at line 130; absent completion masks bad captures container | REJECTED: same propagated exception | Crash (missing completion path) |
| Captures mapping but missing `completion` | REJECTED: same `NoneType.get` exception at line 130 | REJECTED: same propagated exception | Crash |
| Completion capture body is integer `1` | REJECTED: `AttributeError: 'int' object has no attribute 'encode'` at line 96 | REJECTED: same propagated exception | Crash |
| `checks` is an empty list, with completion body `{}` and matching SHA-256 | ACCEPTED; false checks plus `['missing-checks', 'unexpected-checks']` | ACCEPTED; `met=False` | No exception; predicate fails |
| `checks.listener_owned` is a list | REJECTED: `AttributeError: 'list' object has no attribute 'get'` at line 160 | REJECTED: same propagated exception | Crash |
| Valid JSON completion body of 8 MiB with matching SHA-256 | ACCEPTED; false checks plus missing/unexpected checks | ACCEPTED; `met=False` | No exception observed at 8 MiB |

`ACCEPTED` means the grading function returned normally, not that the receipt met C1. Every probe scored `met=False`. Complete output with tracebacks is preserved at `.ufo/waves/round-62/w1/out/A04C1SchemaFuzz/probe-output.txt`; harness at `.ufo/waves/round-62/w1/out/A04C1SchemaFuzz/fuzz.py`.

Representative verbatim traceback for missing captures:

```text
Traceback (most recent call last):
  File "/fast/scratch/hyaku/kama-r62/w/A04C1SchemaFuzz/fuzz.py", line 11, in probe
    result=fn(receipt)
  File "/fast/scratch/hyaku/kama-r62/w/A04C1SchemaFuzz/round62-c1-counter.py", line 130, in grade
    u = cj.get('usage') or {}
        ^^^^^^
AttributeError: 'NoneType' object has no attribute 'get'
```

Representative verbatim traceback for integer body:

```text
Traceback (most recent call last):
  File "/fast/scratch/hyaku/kama-r62/w/A04C1SchemaFuzz/fuzz.py", line 11, in probe
    result=fn(receipt)
  File "/fast/scratch/hyaku/kama-r62/w/A04C1SchemaFuzz/round62-c1-counter.py", line 113, in grade
    c = cap('completion')
  File "/fast/scratch/hyaku/kama-r62/w/A04C1SchemaFuzz/round62-c1-counter.py", line 96, in cap
    if sha256_b(c.get('body', '').encode()) != c.get('body_sha256'):
                ^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'int' object has no attribute 'encode'
```

## Counterexample and smallest safe correction

`grade()` assumes JSON-shaped receipt structures without validating them. Missing completion data yields `cj=None`, but lines 130 and 139 dereference it unconditionally; a non-string capture body is `.encode()`d at line 96; non-mapping `checks` / check entries are `.get()`d at lines 160 and 178. Thus malformed receipts crash instead of becoming ordinary failed/incomplete evidence. Minimal correction: validate receipt/capture/check container and body types before dereferencing/hashing; treat invalid or absent inputs as unevaluable (`None`/false), so `score()` returns `met=False` rather than raising. The 8 MiB test returned normally; no oversized-body threshold was identified, so this probe alone does not establish a size-specific crash or saturation defect.

Tool installation: none.

Report: `.ufo/waves/round-62/w1/A04C1SchemaFuzz.md`
