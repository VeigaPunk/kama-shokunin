# X1Hold — does holding change what is compared?

**Verdict: no.** Both replays of the round-48 receipt match the original and each other
(`compare match=True mismatches=0`, exit 0); holding adds exactly one receipt key, `witness`
(6 leaves), that `compare()` never reads, and every surface the replay does compare — 11
checks, the stable projection, the loading envelope, `returncode`, `term_wait_ms` — is
identical across original, unwitnessed and witnessed receipts. The hold lengthened the
instrumented run from 0.353 s to 3.465 s without moving any compared value.

Seat: executor on operability (lane kama, round 49, wave r49-w1), lane build commit
`74558c71c38ceaeace15fd4cf8aa9d84977584b1`.

## Setup and commands

- Lane clone: `git clone --shared <lane> $S/lane`; `git -C $S/lane checkout -q 74558c71…`;
  `rev-parse HEAD` = `74558c71c38ceaeace15fd4cf8aa9d84977584b1`. Tool digests in the clone equal
  the lane's (`sha256sum`): `kama-live-replay.py 636074f9628f8c61…`, `kama-llamacpp-live.py
  72e76079995c5ba8…`. The lane's `tools/` is unchanged between the build commit and the head
  `122c4ee9` (`git diff --stat 74558c71 122c4ee9 -- tools/` prints nothing).
- Receipt under replay: `.ufo/waves/round-48/c2/live/receipt-1.json` (v5, b11909,
  `stories260K.gguf`, ctx 256, threads 1).
- A, unwitnessed:
  `python3 $S/lane/tools/kama-live-replay.py --receipt <receipt-1.json> --work $S/work-a --out $S/replay-a.json --timeout 300`
  → `replay match=True refused=None mismatches=0 exit=0`, exit 0.
- B, witnessed:
  `… --work $S/work-b --out $S/replay-b.json --witness-dir $S/witness --witness-timeout 60 --timeout 300`
  → `replay match=True refused=None mismatches=0 exit=0`, exit 0. An external observer
  (`observe.sh`) created `witness/release` 3.037 s after `ready.json` appeared.
- CLI compares, exit codes as printed:
  - `--compare work-a/rerun-receipt.json work-b/rerun-receipt.json` → `compare match=True mismatches=0`, exit 0
  - `--compare <original> work-a/rerun-receipt.json` → `compare match=True mismatches=0`, exit 0
  - `--compare <original> work-b/rerun-receipt.json` → `compare match=True mismatches=0`, exit 0

### The hold really happened (`observe.log`)

```
ready_at=… pid=268031 port=39795 ready_json={"schema": "kama-live-witness/v1", "port": 39795, "pid": 268031, "written_utc": "2026-10-26T23:27:12.681Z"}
exe=/fast/scratch/hyaku/kama-r49/X1Hold/work-b/server/llama-b11909/llama-server
listen_inode=619144239
props_during_hold=200
release_at=… held_s=3.037
alive_at_release=yes
```

The witnessed receipt records `witness {schema kama-live-witness/v1, released true,
waited_ms 3105, pid 268031, port 39795}`; `witness.pid == child_pid` and `witness.port == port`
both hold. The hold is placed after every capture and check
(`tools/kama-llamacpp-live.py:1860-1864`), so compared captures are pre-hold by construction.

## What `compare()` reads — 60 leaves, none of them `witness.*`

Discovered mechanically (`compared-leaves.txt`): each leaf of rerun-a was perturbed and a
`compare()` mismatch recorded. The set is `schema`, `outcome`, `server.sha256`, `model.sha256`,
`checks[i].{id,evaluated,passed}`, the five v5 provenance leaves, and the projection
(`captures.props.fields.*`, `captures.slots.{element_count,body_sha256}`,
`captures.health.{status,body_sha256}`, `captures.models.body` (parsed),
`captures.metrics.status`, `loading_envelope_exact`, `loading_503.body_sha256`,
`teardown.{returncode,sigterm_sent,sigkill_sent,port_refuses}`,
`port_listener_ownership`). No `witness.*` leaf is read: compare(a, b) returns 0 mismatches
while their `witness` blocks differ (absent in a, present in b).

## Whole-receipt diff — 414 leaves, 38 differ, 1 is read

`diff_receipts.py` flattening of original / rerun-a / rerun-b (`diff.txt`,
`differing-leaves.tsv`): 376 leaves equal, 38 differ. All 38 are instance facts:

| class | leaves | read by `compare()` |
|---|---|---|
| paths (`argv`, `server.arg/realpath`, `model.arg/path`, `probe.path`, `tool.path`, `probes[i].argv`, `probes[i].result.registry`) | 10 | no |
| pids/ports (`child_pid`, `port`, `probes[i].result.rows[0].declared`) | 4 | no |
| timestamps (`started_utc`, `ended_utc`) | 2 | no |
| loading/transition envelope counts (`checks[9].observed.total_503_responses`, `loading_503.t_ms`, `loading_503_bodies[0].repeats`, `transitions[0..3].t_ms/repeats/body*)` | 10 | no |
| `/v1/models` body (`created` epoch, `models.body` + its digest + transition copy) | 4 | body is parsed only: projection strips `created` |
| `/props` body digest (random `media_marker`, see F1) and its `Content-Length` | 2 | no (`fields` are compared instead) |
| `tool.sha256` (round-48 tool vs round-49 tool) | 1 | no (a note) |
| `witness.*` (`dir`, `pid`, `port`, `released`, `schema`, `waited_ms`) | 6 | no |

### The seat's specific questions

- **Checks:** identical. 11 checks, all `evaluated=true, passed=true`, same ids in all three;
  the only differing check payload is `checks[9].observed.total_503_responses` (23 / 23 / 21),
  which `compare()` does not read (it reads only `id`, `evaluated`, `passed`).
- **Teardown:** identical. `returncode` 0 / 0 / 0, `sigterm_sent` true, `sigkill_sent` false,
  `port_refuses` true, `alive_at_teardown_start` true, and `term_wait_ms` **3 / 3 / 3 ms** —
  the server that had been up 3.1 s longer did not shut down any slower. `term_wait_ms` is not
  compared, so it cannot fail a replay in either direction.
- **Loading envelope:** identical. `loading_envelope_exact` true ×3, `loading_observed` true ×3,
  `loading_bodies_dropped` 0 ×3, `distinct_bodies` 1 ×3, and the loading body digest
  `baa09177700f64520a799fd2628bb3663c1486b25e17e4a507f2e6c81bef957c` ×3. The 503 envelope is
  captured during model load, before the hold.
- **Projection:** byte-identical JSON in all three (`diff.txt`):
  `{"health":[200,"a29ee2b1…"],"loading":[true,"baa09177…"],"metrics":501,
  "models":{"data":["kama-r48-live|llamacpp"],"models":["kama-r48-live"]},"ownership":"child",
  "props":{"build_info":"b11909-caa8191df","default_generation_settings.n_ctx":256,
  "is_sleeping":false,"model_alias":"kama-r48-live","total_slots":4},
  "slots":[4,"6d345b40…"],"teardown":[0,true,false,true]}`.
- **Time cost of the hold:** run span 370 ms (original) / 353 ms (rerun-a) / 3465 ms
  (rerun-b); `witness.waited_ms` 3105. `kama-live-replay.py:281` grows the child bound by
  `witness_timeout` (`timeout + witness_timeout`).

## Findings

**F1 — `/props` carries a random per-process `media_marker`; only 5 fields are comparable
(documentation gap, not a counter defect; counters are frozen, nothing edited).**
Two direct `llama-server` runs from the replay download with the same argv but ports
39021/39022 produced `/props` bodies of equal length (2079 bytes) differing in exactly one
leaf: `.media_marker` `'<__media_5ELZ6CYKwTTQe3QOkJpdqKjo0hVWHoOg__>'` vs
`'<__media_yLsvRWJccvncrdXfkevzTMz1SnaBmqSx__>'`. Within one process the body is
byte-identical across two reads 0.4 s apart (sha equal), and it is unaffected by
`/tokenize` traffic. Hence `captures.props.body_sha256` is unique per run — observed
`f6cb10aa…` (original) / `2d6b13c5…` (a) / `be4c32b6…` (b) — while the five recorded fields
are equal. That is why the projection compares `captures.props.fields`
(`tools/kama-live-replay.py:168-176`, built at `tools/kama-llamacpp-live.py:899-914`) and not
the body digest; anyone "tightening" the projection to the props digest would break every
replay, holding or not. The docstring's exclusion list
(`tools/kama-live-replay.py:18-19`) names ports, pids, times, paths, log text and `created`
but not `media_marker`. Proposed doc-only patch (not applied):
`props-marker-doc.diff` — add `media_marker` to that list and a comment at the fields build.

**F2 — the `witness` block is never compared (by contract).**
`kama-live-replay.py:45` states "the witness is not compared"; measured:
compare(a, b) = 0 mismatches with `witness` absent vs present. A witnessed rerun with
`released=false` would therefore still "match". The assurance for a witnessed replay comes
from the round-49 counter observing from outside, not from the receipt's own `witness` block;
a witnessed receipt is not self-evidence. No action (contract), but relevant when reading C1
evidence.

**F3 — the witness grows the replay's wall clock.**
The child bound is `timeout + witness_timeout` (`kama-live-replay.py:281`); with the default
120 s witness timeout a caller that budgets wall clock from `--timeout` alone is short by
120 s. Measured delta here: +3.1 s (3.465 s vs 0.353 s). Informational for wrappers.

**Ordering is load-bearing but benign.** The hold runs after `ready_captures` and all checks
(`kama-llamacpp-live.py:1860-1864`), so no compared capture can see it. Even had it run
earlier, the observer's own traffic does not move a compared surface: after POST `/tokenize`
(with_pieces, 200) the `/slots` body was byte-identical
(`6d345b4035d771f3…`, the same digest as all three receipts), `/health` unchanged, and the
`/props` fields unchanged (`tokenize-probe.txt`; the `/detokenize` with piece objects in that
probe returned 400 because I sent objects rather than ids — my input, not a tool defect).

## Limits

- One receipt, one model (`stories260K`, 512 vocab), one 3 s hold, one host. `term_wait_ms`
  equality is a single observation and is not compared anyway; nothing here says anything
  about holds long enough to hit server idle timeouts (none are configured by the tool).
- `captures.models.body` is "read" by compare only through parsing; its only difference is the
  per-process `created` epoch, which the projection drops (`kama-live-replay.py:168-183`).
- I did not run the round-49 counter; the C1 witness leg (counter-side observation) is measured
  by other seats.

## Artifacts (all in `.ufo/waves/round-49/w1/out/X1Hold/`)

`replay-a.json`, `replay-b.json` (replay results), `rerun-a-receipt.json`,
`rerun-b-receipt.json`, `original-receipt-1.json` (copies), `a.log`, `b.log`,
`observe.log`/`observe.sh`, `diff.txt`, `differing-leaves.tsv`, `compared-leaves.txt`,
`hold-verdict.json`, `tokenize-probe.txt`/`tokenize_probe.py`, `diff_receipts.py`,
`props-marker-doc.diff`.

No tools installed; python3 stdlib only. Every `llama-server` I started (replay downloads and
two direct `/props` probes) was torn down — `pgrep -af llama-server | grep X1Hold` empty after
each probe; scratch `/fast/scratch/hyaku/kama-r49/X1Hold` removed after copying receipts here.
