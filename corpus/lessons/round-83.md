# kama round 83 — the caller path binds, three stale facts are corrected, and the pin gap becomes a graded register

Frozen plan `plans/round-83-claims.md` (freeze `743c1060`; base `30d8eac394a8714fad3dc792b74a45a25b4366a2`,
the round-82 non-author closure tip; sealed revision C2 grades `b1ba614b51255a3dcfe3e0946f32f8e31bd65c09`,
the round-82 lane tip its report cites). Three claims, three axes, one receipt each; no axis is claimed
to move in score:

- **C1 operability** — the late register read from a caller-supplied path binds to that path's committed
  identity per row, round 82's eight `pending` events are repaid at the round-83 base, and the pending
  count falls instead of growing.
- **C2 calibration** (the lowest assigned axis, 7) — the round-82 record's six declared facts re-derive
  at the sealed revision or are answered by exactly one dated, value-bound correction each, with the
  three facts that hold left uncorrected as the direction test.
- **C3 freshness** — every data row of `registry/engine-pin-relations.tsv` carries one recheck row whose
  verdict the counter re-derives by byte comparison of two committed anchor extracts.

## Gate

Six sources opened this round with `curl -sS` on 2026-11-04; bytes and sha256 are of the received body,
re-fetched by the L1 and by `SK01SourceOpen` to the same digest. Each quote is located at the line named
and is at most 25 words.

| id | URL | status | bytes | line | ≤25-word located quote | verdict | reason / flip |
|---|---|---|---|---|---|---|---|
| S566 | `https://raw.githubusercontent.com/ggml-org/llama.cpp/b12110/tools/server/README.md` | 200 | 136429 | 480 / 482 | "This endpoint is public (no API key check). `/v1/health` also works." | admit | newest-tag side of relation 1 (sha256 `eafc1b53…a137`, 2620 lines); byte-identical to round-82's b12103 read and to the 10:56 b12111 read, so the release gap is the trigger and no statement moved |
| S567 | `https://raw.githubusercontent.com/sgl-project/sglang/v0.5.23/docs/docs/basic_usage/native_api.mdx` | 200 | 18295 | 108 / 111 | "`/ready`: Returns 200 when the server accepts new requests; 503 while starting, paused, unhealthy, or shutting down." | admit | newest side of relation 4 (sha256 `3ed17118…7a3c`); v0.5.23 adds `/ready` (111) and `/ping` (112) and leaves `/health` (109) and `/health_generate` (110) byte-identical |
| S568 | `https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx` | 200 | 17359 | 108 / 109 | "`/health`: Check the health of the server." | admit | the pinned side (sha256 `209087c3…1eb`); the held route sentence sits at the lane's own pin, and the pin has no `/ready` |
| S569 | `https://raw.githubusercontent.com/vllm-project/vllm/v0.33.0/docs/design/prefix_caching.md` | 200 | 13916 | 3 | "Prefix caching kv-cache blocks is a popular optimization in LLM inference to avoid redundant prompt computations." | admit | newest side of relation 5 (sha256 `67ee4e2b…3a61`), byte-identical to S570, so the verdict is a byte fact and never a declared word |
| S570 | `https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/docs/design/prefix_caching.md` | 200 | 13916 | 3 | "Prefix caching kv-cache blocks is a popular optimization in LLM inference to avoid redundant prompt computations." | admit | the pinned side, same sha256 as S569; a `drifted` declaration over these bytes is exactly the counter's `bad` control |
| S571 | `https://git-scm.com/docs/git-blame` | 200 | 82763 | 2146–2147 | "Annotates each line in the given file with information from the revision which last modified the line." | admit | C1's per-row introduction rule's ground (sha256 `cc28e3b8…e187`, 2847 lines); the sentence wraps after "which", so a byte recheck must not read the wrap as absence |

No row was refused: each carries the statement it is cited for, and the one quoting hazard (S571's
wrapped sentence) is named rather than hidden. The newest llama.cpp tag moved twice today — b12103 at
the round-82 read, b12110 at 10:07, b12111 at 10:56 — and b12103/b12110/b12111 are byte-identical
(sha256 `eafc1b53…a137`), so the register's `newest=b12111` and S566's b12110 row attest the same bytes.

## Corrections

The three stale facts of the round-82 record, each answered by the value its own committed receipt
prints; F4, F5 and F6 hold and are not corrected — the direction test.

```
corrected F1 old=log82-c1-selftest=18 new=log82-c1-selftest=23 at=b1ba614b51255a3dcfe3e0946f32f8e31bd65c09 date=2026-11-04 fix=LOG.md
corrected F2 old=sc82c1-selftest=22 new=sc82c1-selftest=23 at=b1ba614b51255a3dcfe3e0946f32f8e31bd65c09 date=2026-11-04 fix=SCORECARD.md
corrected F3 old=calib82-selftest=22 new=calib82-selftest=23 at=b1ba614b51255a3dcfe3e0946f32f8e31bd65c09 date=2026-11-04 fix=SCORECARD.md
```

- **F1** `LOG.md` §Round 82 C1 bullet (sealed line 3432) declares `pass=18 fail=0`;
  `.ufo/waves/round-82/measured/after/c1-selftest.out` prints `SELFRECORD_R81_SELFTEST pass=23 fail=0`
  (`EXIT=0`). The bullet quotes the pre-hardening tally.
- **F2** `SCORECARD.md` §Round 82 C1 row (sealed line 4970) declares `pass=22 fail=0` beside a citation
  of that very receipt, which prints 23.
- **F3** `SCORECARD.md` `## Axes` calibration row (sealed line 18) repeats `pass=22 fail=0` through the
  same `--selftest` tally.

The fix leg binds the token, not the container: the predicate reads each `fix` path's tip bytes outside
`LOG-CORRECTION` lines and `#### round-<N> correction` blocks. The plan's two named containers alone
leave all three corrections `unbacked` — measured, `SELFRECORD_R82 claims=6 mismatches=3 corrected=0
unbacked=3`, exit 1 (`.ufo/waves/round-83/w1/EX03SelfRecord/final-records-only.out`) — and ordinary
record lines outside those regions turn the same run green (`mismatches=0 corrected=3 unbacked=0`). The
tightened leg is therefore load-bearing, not decorative.

## Routed record correction (round 82, outside the C2 population)

The critic's sealed sweep found a fourth stale cell the six-fact population does not carry:
`SCORECARD.md:4971` (§Round 82 C2 row) states its cited before receipt prints `new=0 bad=15`, and
`.ufo/waves/round-82/measured/before/c2-late-delta-base.out` actually prints
`LATE_DELTA round=82 base=aaf974dbd3b6 population=103 carried=88 new=15 bad=15`, exit 1. The row's
`new=` cell is therefore stale by one value. It is recorded here as prose, not as a `corrected F<n>`
block, because C2's population was frozen at six facts and widening it after data would rewrite the
claim; the row's `bad=15` and its exit-1 verdict are correct and the correction is owed to round 84's
own counter population.

## Mistakes

| class | evidence pointer | captured-by | fix |
|---|---|---|---|
| `caller-path-unbound` — a leg that accepts an input it cannot bind grades per row instead of refusing the input: `--late FILE` read a register from disk but resolved no introduction for that path, so every row came back `unbound-register`; a whole-register attempt booked `late=0 unaccepted=23 bad_rows=103` | `.ufo/waves/round-83/measured/before/c1-debt-legB.out` (base `30d8eac3`); the same defect's first sighting at `.ufo/waves/round-82/measured/defects/c2-debt-register-level-before.out` and round-82 freeze divergence 1 | `none` — the round-82 control suite exercised only the default register path, so no criterion could see the caller path; `KQ135` now names it | `tools/round81-append-debt.py` gains `load_late()`: realpath inside `git rev-parse --show-toplevel`, `git cat-file -e <to>:<path>`, file and per-row blame at the audited revision, `exit 2` for an unbound path. Shown able to fail: `late-path-outside-repo` and `late-path-untracked` go red under the old code (both paths were graded, not refused), and the round's before receipt is the old code's own output (`bad_rows=103`, exit 1) |

## Freeze divergences (recorded after the first data run, before the report; the frozen text stands)

1. **The C1 target's `late=35` token is a row count written into an event counter.** The predicate's
   prose says "20 new rows … and the 15 carried round-82 rows" (35 rows), but `APPEND_DEBT`'s `late`
   counts EVENT keys (`late = len((late_covered - frozen_keys) & graded_keys)`,
   `tools/round81-append-debt.py:289-290`). The reachable value is `late=23` = the 15 carried events plus
   the 8 round-82 window events, with `unaccepted=0`; the row promise is measured separately and exactly
   by `LATE_DELTA round=83 base=30d8eac394a8 population=123 carried=103 new=20 bad=0`, exit 0. Both
   numbers are named here and in the report; the closure decides which sentence governs.
2. **The `pin-recheck-trigger.md` command-cell correction was already discharged.** Round 82 repaired it
   at `8a3e8af2`; the live line 5 reads `--pins`, and the command runs (exit 1, three `behind` rows).
   This round verifies the cell and records the superseded text instead of re-fixing it.

## Frontier

The pin-gap surface moved from a per-engine newest-tag line to a per-relation recheck register:
`registry/engine-pin-relations.tsv` holds five data rows and `registry/pin-recheck-rows.tsv` answers each
with one row. Four are graded `holds` by byte comparison — relations 1, 2, 4 and 5, from six committed
extracts under `corpus/anchors/`; relation 3 (`llama.cpp b7200`, the cross-lane kengaku role) is
`ungraded` because the lane holds no document at that ref, and `ungraded` never counts as graded.

What stays frontier: other engines' documents (the relation register names only llama.cpp, SGLang and
vLLM) and a live serving runtime (every recheck reads a committed document, never a running server).
The SGLang `/ready` and `/ping` routes enter the recorded health vocabulary as new ground for a later
entry; `runtime-health-surface-processes.md:20` already holds vLLM's readiness routes, so this is an
engine-side addition, not a new class.

`Assimilation: none` — the three claims repair lane instruments and the round's source budget is spent
on C3's anchors; the `shokuknow` package theme is not adopted this round.
