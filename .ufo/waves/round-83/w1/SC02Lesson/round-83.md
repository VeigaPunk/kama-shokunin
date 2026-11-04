# kama round 83 — the caller path binds, three stale facts are corrected, and the pin gap becomes a graded register

Frozen plan `plans/round-83-claims.md` (freeze `743c1060`; base `30d8eac394a8714fad3dc792b74a45a25b4366a2`,
the round-82 non-author closure tip; sealed revision C2 grades `b1ba614b51255a3dcfe3e0946f32f8e31bd65c09`,
the round-82 lane tip its report cites). Three claims, three axes, one receipt each, and no axis claimed
to move in score:

- **C1 operability** — the late register read from a caller-supplied path binds to that path's commit
  identity per row, round 82's eight `pending` events are repaid at the round-83 base, and the pending
  count falls instead of growing.
- **C2 calibration** (the lowest assigned axis, 7) — the round-82 record's six declared facts re-derive
  at the sealed revision or are answered by exactly one dated, value-bound correction each, with the
  three facts that hold left uncorrected as the direction test.
- **C3 freshness** — every relation row of `registry/engine-pin-relations.tsv` carries a recheck row
  whose verdict the counter re-derives by byte comparison of two committed anchor extracts.

## Gate

Six sources opened this round with `curl -sS` on 2026-11-04; status, bytes, sha256 and line numbers are
the fetched facts in `.ufo/waves/round-83/w1/SK01SourceOpen/sources.json`, re-fetched by this seat to
the same sha256. Each quote is located at the line named and is at most 25 words.

| id | URL | status | bytes | anchor line | ≤25-word located quote | verdict | reason / flip | date |
|---|---|---|---|---|---|---|---|---|
| S566 | `https://raw.githubusercontent.com/ggml-org/llama.cpp/b12110/tools/server/README.md` | 200 | 136429 | 480–482 | "This endpoint is public (no API key check). `/v1/health` also works." | admit | newest-tag side of relation 1; sha256 `eafc1b53…a137` is byte-identical to round-82's b12103 read, so the release gap is the trigger and no statement moved | 2026-11-04 |
| S567 | `https://raw.githubusercontent.com/sgl-project/sglang/v0.5.23/docs/docs/basic_usage/native_api.mdx` | 200 | 18295 | 108–111 | "`/ready`: Returns 200 when the server accepts new requests; 503 while starting, paused, unhealthy, or shutting down." | admit | newest side of relation 4; v0.5.23 adds `/ready` and `/ping` over the pin (+936 B) and leaves every held sentence byte-identical | 2026-11-04 |
| S568 | `https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx` | 200 | 17359 | 108–109 | "`/health`: Check the health of the server." | admit | the pinned side; the held route sentence sits at the lane's own pin (line 109), so the recheck compares like with like; the pin has no `/ready` | 2026-11-04 |
| S569 | `https://raw.githubusercontent.com/vllm-project/vllm/v0.33.0/docs/design/prefix_caching.md` | 200 | 13916 | 3 | "Prefix caching kv-cache blocks is a popular optimization in LLM inference to avoid redundant prompt computations." | admit | newest side of relation 5; byte-identical to S570 (sha256 `67ee4e2b…3a61`), so this relation's verdict is a byte fact and never a declared word | 2026-11-04 |
| S570 | `https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/docs/design/prefix_caching.md` | 200 | 13916 | 3 | "Prefix caching kv-cache blocks is a popular optimization in LLM inference to avoid redundant prompt computations." | admit | the pinned side, byte-identical to S569; a `drifted` declaration over these bytes is the counter's `bad` control fixture, which is why relation 5 is graded by comparison | 2026-11-04 |
| S571 | `https://git-scm.com/docs/git-blame` | 200 | 82763 | 2143–2146 | "Annotates each line in the given file with information from the revision which last modified the line." | admit | C1's per-row introduction rule's ground; the DESCRIPTION sentence wraps after "which" (2146→2147), so a strict byte recheck must not read the wrap as absence; S571b, `--line-porcelain` at 2579, is the same ref's machine-readable anchor | 2026-11-04 |

No row was refused this round: each of the six carries the statement it is cited for, and the one
quoting hazard (S571's wrapped sentence) is named rather than hidden.

## Corrections

The three stale facts of the round-82 record, each answered by the value its own committed receipt
prints; F4, F5 and F6 hold and are not corrected — the direction test.

```
corrected F1 old=log82-c1-selftest=18 new=log82-c1-selftest=23 at=b1ba614b51255a3dcfe3e0946f32f8e31bd65c09 date=2026-11-04 fix=LOG.md
corrected F2 old=sc82c1-selftest=22 new=sc82c1-selftest=23 at=b1ba614b51255a3dcfe3e0946f32f8e31bd65c09 date=2026-11-04 fix=SCORECARD.md
corrected F3 old=calib82-selftest=22 new=calib82-selftest=23 at=b1ba614b51255a3dcfe3e0946f32f8e31bd65c09 date=2026-11-04 fix=SCORECARD.md
```

- **F1** `LOG.md` §Round 82 C1 bullet (sealed line 3432) declares `log82-c1-selftest=18`;
  `python3 tools/round82-selfrecord-round81.py --selftest` prints `SELFRECORD_R81_SELFTEST pass=23
  fail=0` at `45c4926e`, committed as `.ufo/waves/round-82/measured/after/c1-selftest.out` (`EXIT=0`).
- **F2** `SCORECARD.md` §Round 82 C1 row (sealed line 4970) declares `sc82c1-selftest=22`; the same
  command and receipt print `pass=23` (the row cites that very receipt file beside its stale token).
- **F3** `SCORECARD.md` `## Axes` calibration row (sealed line 18) declares `calib82-selftest=22`
  through the same `--selftest` tally; the same receipt prints `pass=23`.

The fix leg binds the token, not the container: the predicate reads each `fix` path's tip bytes outside
`LOG-CORRECTION` lines and `#### round-<N> correction` blocks, so the plan's two named containers alone
leave all three corrections `unbacked` — measured, `SELFRECORD_R82 claims=6 mismatches=3 corrected=0
unbacked=3` exit 1 (`.ufo/waves/round-83/w1/EX03SelfRecord/final-records-only.out`) — and a receipt
binding line outside those regions turns the same run green
(`.ufo/waves/round-83/w1/EX03SelfRecord/final-honest.out`, `mismatches=0 corrected=3 unbacked=0`).

## Mistakes

| class | evidence pointer | captured-by | fix |
|---|---|---|---|
| `caller-path-unbound` — a leg that accepts an input it cannot bind grades per row instead of refusing the input: `--late FILE` read a register from disk but resolved no introduction for that path, so every row came back `unbound-register` and a 103-row attempt booked `late=0 unaccepted=23 bad_rows=103` | `.ufo/waves/round-82/measured/defects/` (`c2-debt-register-level-before.out`) and round-82 freeze divergence 1; reproduced in `.ufo/waves/round-82/w1/EX04GateArm/commands.txt` Part 1 D (an out-of-tree one-row register → `unbound-register late line 2`) | `none` — the round-82 control suite exercised only the default register path, so no criterion could see the caller path | the round-83 path binding plus `late-path-outside-repo` / `late-path-untracked` / `late-path-bound`; EX01 delivered them as `implemented-not-run` (`EX01LateBinding/EX01.json`), so this seat ran the draft module (sha256 `3868a3ee…`) in a scratch clone: `APPEND_DEBT_SELFTEST pass=28 fail=0` green, and `pass=25 fail=3` after `load_late` is reverted to the unbound path, the three failures naming exactly those arms (`SC02Lesson/probe-selftest-green.out`, `probe-selftest-unbound-mutant.out`) |

## Frontier

The pin-gap surface moved from a per-engine newest-tag line to a per-relation recheck register:
`registry/engine-pin-relations.tsv` holds five relation rows and the round's row register carries one
recheck each. Four are graded `holds` by byte comparison — relations 1, 2, 4 and 5; relations 1, 4 and
5 were re-confirmed first-hand this round (S566 identical bytes at b12110, S568→S567 adds `/ready` and
`/ping` without moving a held sentence, S569 and S570 byte-identical), while relation 2 rests on the
round-82 S555 read the lane already holds. Relation 3 (`llama.cpp b7200`, the cross-lane kengaku role)
is `ungraded` because the lane holds no document at that ref, and `ungraded` never counts as graded.

What stays frontier: other engines' documents (the relation register names only llama.cpp, SGLang and
vLLM) and a live serving runtime (every recheck reads a committed document, never a running server).
`Assimilation: none` — the three claims repair lane instruments and the round's source budget is spent
on C3's anchors; the `shokuknow` package theme is not adopted this round.
