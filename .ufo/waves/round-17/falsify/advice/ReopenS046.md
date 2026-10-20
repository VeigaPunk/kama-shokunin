VERDICT: partial — S046's receipt-derived cells hold, but the anchor's "model, server, probe and tool pins" is absent from the cited gate record and the lesson Gate quote is a filtered projection, not verbatim.

# ReopenS046 — round-17 FALSIFY, S046 cell-by-cell

Seat: `KamaR17.ReopenS046` (scout, leaf). Target: `corpus/SOURCES.md:58` (S046) and
`corpus/lessons/round-17.md:70`, at lane commit
`54a29268e2083caa2b1e0d54ee1e7d90961302f3`. Every check ran in
`/tmp/ReopenS046-clone` (clone + checkout of that commit); the lane tree was read
only, never written.

## What I attacked

The S046 row's cells against its three receipts, the gate record and the gate
itself; the lesson `## Gate` quote against the receipt bytes. I also tried to make
`VALID` mean more than it does: a consistent other-build receipt passed the gate with
no pins, proving the pin arguments — not the word `VALID` — bind build and model.

## Cell-by-cell

| Cell | Verdict | Evidence |
|---|---|---|
| `id` | agree | `corpus/SOURCES.md:58`; exactly one `S046` registry row (counted); the append-only guard reports `S042`–`S046` added, `violations: []`. |
| `source` | agree | `tools/kama-llamacpp-live.py` exists; its sha256 `0efd1723…c46ac` equals `tool.sha256` in all three receipts (`receipt-1.json:529`); all three evidence paths exist. |
| `kind` (`own-work`) | agree | Lane-authored receipts, same kind as `S034`/`S041`; the fleet round-10 accounting lists "A=27 (docs/spec/code/own-work)" (`/home/vgpnk/Projects/shokunin/.ufo/reports/round-10/kama.md:65`). |
| `tier` (`A`, for `scope`) | agree | Scope is the lane's own primary observation (three runs); tier `A` is scoped to that observation, not a global trust claim, and matches the own-work precedent rows. |
| `scope` | agree | Three runs: distinct sha256, child pids 1677834/1677955/1678081, ports 40089/43091/38545, `started_utc` .932/.131/.328Z. `b11755`: `server.realpath` `…/llama-b11755/llama-server`, `props_alias.build_info` `b11755-704366d76` in all three. Unregistered: `grep` of `registry/endpoint-consumers.tsv` finds none of the three ports (only 8080/34113). Ownership: `port_listener_ownership` `"child"` (`receipt-1.json:259`). Fail-capable: `runs/controls-current.json` `accepted_bad 0`, `gate_flip_bad 0`, `inconclusive 0`, `good_ok true`, with `tool_sha256 0efd1723…` and `gate_sha256 ad680179…` equal to the landed tool/gate files. |
| `anchor` | **partial** | Schema `kama-llamacpp-live/v2` (`receipt-1.json:375`); span starts `15:57:44.932Z` (`:509`) and ends `15:57:45.445Z`; ports and tool pin resolve; 11 checks each, ids exactly `REQUIRED_CHECKS_V2` (`tests/llamacpp-live/check-receipt.py:80-92`), all `passed: true`. Gate `VALID` and exit 0 are recorded (`live/gate.txt:1-6`) and reproduce. **The four-pin clause does not resolve from the cited artifact**: `live/gate.txt:7` records only `probe=36b64978… tool=0efd1723…`; no model or server pin argument appears in any round-17 evidence artifact (`live/`, `runs/`, `c2/`), and the only `--expect-server-sha256` records are build-wave advice drafts. Re-running the landed gate with all four pins returns `VALID` 3/3, so the claim is true under that invocation — but `gate.txt` alone cannot prove it (see F1). |
| `teaches` | agree | Ready `/health` raw body is `{"status":"ok"}`, `Content-Length: 15`, sha256 `a29ee2b1…d288` (`receipt-1.json:21-30`). Loading totals `42/45/45` (`receipt-1.json:204`; receipt-2/3 same line `45`), one distinct envelope body, `bodies_dropped: 0`; I recounted `transitions` independently (`repeats + 1` per row) → 42/45/45 and the same distinct body. Teardown `alive true, sigterm true, sigkill false, rc 0, term_wait_ms 3, port_refuses true, ownership child` in all three. The word "one" SIGTERM is code-derived, not receipt-counted (see note N2). |
| `status` (`mined`) | agree | Both used-by paths exist and cite S046 (below). |
| `opened` (`2026-10-20`) | agree | Receipt timestamps are 2026-10-20T15:57:44.932Z–15:57:45.445Z; today's re-open is 2026-10-20. |
| `recheck` (`every round`) | agree | Matches the own-work precedent `S034`/`S041`; no in-lane enumeration contradicts it (see L2). |
| `used-by` | agree | Both paths exist: `corpus/knowledge/llamacpp-loading-lifecycle.md:155,186` ("Observed (S046)") and `corpus/lessons/round-17.md:61,70,74,172`. |
| row shape | agree | 13 pipe-delimited fields (the append-only guard parses the table without a width error); one `S046` row. |

## F1 — `anchor`: the four-pin claim is reproducible, not recorded (partial)

`corpus/lessons/round-17.md:171-173` says the three runs were "gate `VALID` with
model, server, probe and tool pins (`.ufo/waves/round-17/live/gate.txt`)". The cited
record's pin line is:

`.ufo/waves/round-17/live/gate.txt:7`
`probe=36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 tool=0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac`

It contains two of the four named pins. Re-running the landed gate in the clone with
`--expect-model-sha256 270cba1b…256d --expect-server-sha256 b6a31a8e…d804
--expect-probe-sha256 36b64978…29d3 --expect-tool-sha256 0efd1723…c46ac` gives
`VALID` and exit 0 for all three receipts, so the row's claim is not false — it is
under-recorded. The gap is material: a copy of receipt-1 with a consistent other
server digest (`1111…`) and `build_info: b9999-0000000` passes `VALID`, exit 0, when
the gate is run without pins; the same file is rejected, exit 1, only when
`--expect-server-sha256 b6a31a8e…` is supplied. `VALID` alone therefore does not bind
"b11755" or the model.

Corroboration, independently reached: `.ufo/waves/round-17/falsify/advice/LiveRerun.md:44`
also notes that gate.txt lacks the model and server pins; my no-pins forgery acceptance
is the additional evidence that the omission is not cosmetic.

## F2 — Lesson `## Gate` quote: values true, quote not verbatim

`corpus/lessons/round-17.md:56` sets the rule: "Quotes are verbatim and at most 25
words." The S046 Gate row (`:70`) quotes:

`{"alive_at_teardown_start": true, "returncode": 0, "sigkill_sent": false, "sigterm_sent": true}`

- **Located:** agree. `receipt-1.json:175` is `"id": "teardown_graceful"`; its
  `observed` object is at `:176-184`.
- **<=25 words:** agree (8 whitespace-delimited tokens).
- **Verbatim:** **disagree.** The stored object is
  `{"alive_at_teardown_start": true, "error": null, "port_listener_ownership": "child", "returncode": 0, "sigkill_sent": false, "sigterm_sent": true}`
  (`receipt-1.json:176-184`). The quote elides `"error": null,` and
  `"port_listener_ownership": "child",`; it is not a contiguous substring of the
  receipt, of the check's `observed` serialization, or of the top-level `teardown`
  object. `grep -rF` across the lane finds the quoted string only in the lesson
  itself. The elided ownership field is load-bearing for the "harness-initiated"
  argument, though the separate `teardown_port_closed` check covers it.
- Consequence: the row's decision is supportable from the receipt, but the Gate's own
  verbatim rule is violated; L1 should either quote the object as stored or mark the
  projection explicitly.

## Commands run

Clone cwd for the gate and append-only runs (`PYTHONDONTWRITEBYTECODE=1`); lane cwd
(read-only) for hashes, grep and `ss`.

```
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/ReopenS046-clone \
 && git -C /tmp/ReopenS046-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3      # 0
sha256sum .ufo/waves/round-17/live/receipt-*.json                                            # 0; three distinct digests
for i in 1 2 3; do python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-17/live/receipt-$i.json \
  --expect-model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d \
  --expect-server-sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 \
  --expect-probe-sha256 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 \
  --expect-tool-sha256 0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac; done  # VALID each, 0
python3 tests/llamacpp-live/check-receipt.py /tmp/ReopenS046-scratch/other-build2.json        # VALID, 0
python3 tests/llamacpp-live/check-receipt.py /tmp/ReopenS046-scratch/other-build2.json \
  --expect-server-sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804   # INVALID, 1
python3 tools/sources-append-only.py --from cff9e62 --to 54a29268e2083caa2b1e0d54ee1e7d90961302f3 \
  --repo /tmp/ReopenS046-clone --json                                                        # 0; added S042-S046, violations []
sha256sum tools/kama-llamacpp-live.py tests/llamacpp-live/check-receipt.py                     # 0; 0efd1723…, ad680179…
ss -ltnp | grep -E ':(40089|43091|38545)\b'                                                   # 1; none listening
grep -rF '{"alive_at_teardown_start": true, "returncode": 0, "sigkill_sent": false, "sigterm_sent": true}' \
  --exclude-dir=.git --exclude-dir=.jj --exclude-dir=interactive-sessions .                     # 0; only corpus/lessons/round-17.md:70
```
Python recounts (exit 0): each receipt has exactly the 11 `REQUIRED_CHECKS_V2` ids,
unique, all `passed: true`; `loading_503` totals recomputed from `transitions`
(`repeats + 1`) are 42/45/45 and the stored distinct body sha256 is
`baa09177…957c`.

## Limitations

- L1: I did not start `llama-server` or re-run the live tool; no port was bound by
  this seat (`ss` grep above is clean). The receipts and the landed gate are what I
  tested.
- L2: `SOURCES-CONTRACT-v1`'s kind/tier/recheck enumeration is not in this lane. The
  `kind`/`tier`/`recheck` verdicts rest on the in-lane precedent rows (`S034`,
  `S041`, `S030`) and the fleet round-10 accounting; `CORPUS.md`, cited by sibling
  `ReopenS045`, does not exist under the lane root (`ls` error). No contradiction
  found, but the frozen text itself was not re-read.
- L3: `gate.txt` records no gate sha256 or timestamp. The landed gate's hash equals
  `controls-current.json:gate_sha256`, so the controls graded this gate; the identity
  of the gate that produced the three `VALID` lines is [INFERENCE] from the
  successful four-pin re-run, not recorded.
- No tools installed or upgraded; no package-manager transaction was run.

## Non-falsifying notes

- N1: the three receipts are all 27262 bytes but not copies: sha256 differ
  (`f34afb54…`, `3df31ddb…`, `5e2c0511…`) and child pids, ports, log paths and 503
  counts differ. Equal size is coincidence of equal-width fields.
- N2: "one harness SIGTERM" is [INFERENCE] from tool code, not a receipt count:
  `tools/kama-llamacpp-live.py:782` issues one `killpg(proc.pid, SIGTERM)` and `:793`
  escalates to SIGKILL only after `TERM_GRACE` (10.0 s, `:73`); `term_wait_ms 3`
  proves no escalation occurred. The receipt stores booleans, not a signal count.
- N3: the gate's `loading_envelope_graded` re-derives exactness from the stored
  bodies (`tests/llamacpp-live/check-receipt.py:908-938`) but does not cross-check
  `observed.total_503_responses`; my transition recount closes that gap and agrees
  with 42/45/45.
