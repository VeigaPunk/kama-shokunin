# ExecCountC2Fix — round-28 repair of `.ufo/waves/round-25/count-c2.py`

Routed defect 1 of `corpus/lessons/round-27-verifier-spotcheck.md:258-287`
(open since round-25 defect 5 and round-26 defect 8): the round-25 C2
counting command read every per-cell value from the receipt and used the
receipt's `raw` hashes only as a receipt-level binding. This directory holds
the patched counter, its diff, the forged fixtures and the demonstrated
before/after evidence. The lane file was not edited.

## Files

| file | sha256 | role |
|---|---|---|
| `count-c2.py` | `5aa64a370196f352435bdf2cee2526019a3eac2737eb194496c5126d5759fa2a` | patched counter (place at `.ufo/waves/round-25/count-c2.py`) |
| `count-c2.diff` | `f75468c8e219ceb27b8e8b21e8b41c151958b7519dba919146dea18b51cd6872` | unified diff against the lane file (`2f952dca…760b`) |
| `make-fixtures.py` | `99c8b30eec0d6e69d91574b4997847d1bf492fe18934be27ba1a2954537ee0b2` | builds the forged fixtures from the committed receipt |
| `run-demo.sh` | `928d842cdf2899a9b637c68bdd319063f722633e5b974e5ceaae2ecc71a503b3` | reproduces every demonstration below in `/fast` scratch |
| `forged-cells.receipt.json` | `8007fb2475f0b295c7d0ccf927d97c241a0da564d02d32957257c53774445a03` | receipt cell fields edited (K2 value/pool, K4 slot count, L1 outcomes); raw files untouched |
| `forged-raw-receipt.json` | `59e770eaae5e345736149664d7156128b2e505f61eff6282b4daa260ccece07f` | committed receipt with K3 `raw_props` rebound to the forged props bytes |
| `forged-K3.props.body` | `5e03cd808ae784d4e3eca0a4d12ffee3148fd9e008b71af85468deaf75ec6311` | raw `/props` body with `default_generation_settings.n_ctx` 2048 → 512 |
| `demo-run-all.out` | — | the full reproduction transcript |
| `demo-b-forged-cells.out`, `demo-c-forged-raw.out`, `demo-parity.out` | — | earlier separated runs, same results |

## What changes

Every per-cell value the counter validates is recomputed from the raw bytes
the cell's `raw` object hashes bind, never read from the receipt's cell
fields:

- `props_n_ctx`, `total_slots` ← `<id>.props.body`
  `default_generation_settings.n_ctx`, `total_slots`
- `slots_n_ctx` ← every `<id>.slots.body` entry `n_ctx`
- `models_n_ctx_train` ← `<id>.models.body` `data[0].meta.n_ctx_train`
- `kv_pool_candidates`, `kv_pool_n_ctx` ← every `llama_context: n_ctx = N`
  line of `<id>.server.log`, last one wins
- `log_lines` ← the claim-named line set extracted from `<id>.server.log`
- load-request outcomes ← the same log: `new prompt … task.n_tokens = N`
  (prompt tokens, start order), `srv send_error: task id = N` (HTTP 500 with
  that message), `slot release … n_tokens = M, truncated = F` (HTTP 200,
  truncation flag); concurrent mode iff the second request starts before the
  first ends

A cell is observed only when its `raw` hashes still match the files, every
derived value equals the receipt cell, and the existing structural checks
pass. `bound` additionally requires every cell to agree with its raw bytes.
The output line is unchanged: `registered N observed M bound B missing [...]`.

## Reproduce

```bash
bash /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/ExecCountC2Fix/run-demo.sh
```

The script copies the committed `.ufo/waves/round-25/final` tree to
`/fast/scratch/hyaku/kama-r28/w1/ExecCountC2Fix-demo`, places the lane
counter as `count-c2-before.py` and the patched file as `count-c2-after.py`
at `.ufo/waves/round-25/`, and runs the four cases.

> The patched file resolves its raw directory relative to its own location
> (`<script dir>/final/raw`). Running the copy that sits in this out
> directory therefore has no raw bytes and prints `observed 0`: that is the
> intended fail-closed behaviour, not a working run. Place it at
> `.ufo/waves/round-25/count-c2.py` in a tree that holds `final/raw`, as
> `run-demo.sh` does.

## Results (from `demo-run-all.out`)

```
lane counter sha256: 2f952dca58a4ff2efe55cbb9f2afcae1b8ae4efd41a3ee8461522699d77d760b
patched counter sha256: 5aa64a370196f352435bdf2cee2526019a3eac2737eb194496c5126d5759fa2a
committed receipt sha256: 78c51385991b1261359503e604adaf09113476d82ef7691f999d18abc673b98c
=== (a) unchanged committed receipt ===
before: registered 14 observed 14 bound True missing []
after:  registered 14 observed 14 bound True missing []
=== (b) forged receipt cell fields, raw files untouched ===
before: registered 14 observed 14 bound True missing []
after:  registered 14 observed 11 bound False missing ['K2', 'K4', 'L1']
=== (c1) forged raw file, committed receipt, hash not rebound ===
before: registered 14 observed 14 bound False missing []
after:  registered 14 observed 13 bound False missing ['K3']
=== (c2) forged raw file AND receipt raw hash rebound to it ===
before: registered 14 observed 14 bound True missing []
after:  registered 14 observed 13 bound False missing ['K3']
```

Parity extras (`demo-parity.out`): a duplicate `K1` id still yields
`observed 13 missing ['K1']` on both counters; an extra unregistered cell
with bogus hashes yields `bound False` on both; a tree with no `final/raw`
now yields `observed 0` (before: `observed 14 bound False`).

## Boundary

The counter binds receipt to raw bytes; it cannot bind raw bytes to the
server that produced them. A forgery that rewrites a raw file, updates its
receipt hash **and** rewrites the matching cell fields together is
indistinguishable from genuine data without an external anchor (the lane's
git history). Absolute request timestamps and the launch argv are not
recoverable from the committed bytes; they stay receipt-internal
consistency checks, and both requests' overlap must equal the raw-derived
mode. `n_predict` is the registered request constant from the claim, not a
receipt measurement.
