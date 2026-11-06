## Round 90 — hostile listener answers stay bounded and the probe's reason codes get a wire-bound table (2026-11-06)

Round on the admitted round-89 base; the wave attacks work already landed and changes no frozen predicate.
Base `99cdb4d6270455494dd27901efe84a0f3b342062`; frozen plan `plans/round-90-claims.md`, counters
`tools/round90-hostile-answers.py` and `tools/round90-reason-rows.py`, frozen at
`6f6d7873dac936ba407398ce81b464d77d0fcf32`. Two claims on two axes, causally separable (C1's counter never
reads `SKILL.md`; C2's counter never runs the probe). **No canned expectation**: every C1 cell's expected
answer is the probe's own output on a lane-owned stub, and every C2 row binds to a captured probe answer on a
receipt whose every line names the probe's sha256.

Revisions: B `99cdb4d6270455494dd27901efe84a0f3b342062`; F `6f6d7873dac936ba407398ce81b464d77d0fcf32`;
M `f968fb19bb2a0c2afe271bfe606f11b52d10823f`; M2 `2ee0b55f4d3fd0cb3157d26b03280c1d21e27b2d`.

Predicates (frozen, from the plan):

- **C1** — `python3 tools/round90-hostile-answers.py --repo . --rev <M> --work <scratch>` prints
  `HOSTILE_ANSWERS cells=13 mismatches=0 positive_mismatches=0 probe=rev …` and exits 0 at the measured
  commit M, the counter's bytes being identical to this freeze commit.
- **C2** — `python3 tools/round90-reason-rows.py --repo . --rev <M2>` prints
  `REASON_ROWS population=23 documented=23 … unbound=0 missing=0 duplicates=0` and exits 0 at the measured
  commit M2, counter bytes identical to this freeze commit.

| Claim | Axis | Counting command | Before (base, committed receipt) | Target |
|---|---|---|---|---|
| C1 hostile listener answers (capability `hostile-answer-bounds`, sourced S587/S588) | operability | `python3 tools/round90-hostile-answers.py --repo . --rev <M> --work <scratch>` | `HOSTILE_ANSWERS cells=13 mismatches=8 positive_mismatches=0 probe=rev`, exit 1, probe `c15ffca8…`, rev `99cdb4d6…` (`controls/c1-base.out:14`); forgeries F1 `mismatches=6 positive_mismatches=5` (`controls/c1-f1-blanket-refusal.out:15`), F2 `9/1` (`c1-f2-over-sanitizer.out:15`), F3 `7/1` (`c1-f3-tiny-cap.out:15`), all `probe=override`, exit 1 | `cells=13 mismatches=0 positive_mismatches=0 probe=rev`, exit 0, probe `c197912f…`; counter bytes equal to freeze; the four harm receipts (`controls/harm-base-*`) unchanged at M |
| C2 probe reason-code table (capability `probe-reason-table`) | depth | `python3 tools/round90-reason-rows.py --repo . --rev <M2>` | `REASON_ROWS population=23 documented=0 rows=0 bound=0 unbound=0 missing=23 duplicates=0 additional=0 receipt=absent`, exit 1 (`controls/c2-base.out:24`); forgery battery `rows=5 bound=2 unbound=3 duplicates=1`, stale `bound=0 receipt=stale`, prose-only `documented=23 bound=0 unbound=23`, all exit 1 (`controls/c2-forgeries.out:7,10,13`) | `documented=23 rows=24 bound=24 unbound=0 missing=0 duplicates=0 additional=1`, exit 0; counter bytes equal to freeze |

Receipt summary lines, verbatim (`.ufo/waves/round-90/`):

- `controls/c1-base.out:14` — `HOSTILE_ANSWERS cells=13 mismatches=8 positive_mismatches=0 probe=rev probe_sha256=c15ffca8f6b4f07f19fe378d08b8495f2b345dd53face17b686c78ea5cc73238 rev=99cdb4d6270455494dd27901efe84a0f3b342062` (exit 1, line 15)
- `controls/c1-f1-blanket-refusal.out:15` — `HOSTILE_ANSWERS cells=13 mismatches=6 positive_mismatches=5 probe=override probe_sha256=9aaa15166256a485b01b35511ef963846b247c8f54f8f61bc3312e02d45a9730 rev=99cdb4d6270455494dd27901efe84a0f3b342062` (exit 1, line 16)
- `controls/c1-f2-over-sanitizer.out:15` — `HOSTILE_ANSWERS cells=13 mismatches=9 positive_mismatches=1 probe=override probe_sha256=a96879dd4d9fd44b0998543b174c3a4eacc351e9435b00d22d3d1052d2332aeb rev=99cdb4d6270455494dd27901efe84a0f3b342062` (exit 1, line 16)
- `controls/c1-f3-tiny-cap.out:15` — `HOSTILE_ANSWERS cells=13 mismatches=7 positive_mismatches=1 probe=override probe_sha256=6ddf9df58d95296682786de86329a3ec29fcf1a88a02025d76aae629020b355b rev=99cdb4d6270455494dd27901efe84a0f3b342062` (exit 1, line 16)
- `controls/c2-base.out:24` — `REASON_ROWS population=23 documented=0 rows=0 bound=0 unbound=0 missing=23 duplicates=0 additional=0 receipt=absent probe_sha256=c15ffca8f6b4f07f19fe378d08b8495f2b345dd53face17b686c78ea5cc73238 rev=99cdb4d6270455494dd27901efe84a0f3b342062` (exit 1, line 25)
- `controls/c2-forgeries.out:7` — `REASON_ROWS population=23 documented=4 rows=5 bound=2 unbound=3 missing=19 duplicates=1 additional=0 receipt=current probe_sha256=f80023623477bacb9a4a4cff1c7573ca029fd1ba20592906f48ad55278c5e330 rev=4928a9412911ed55344fb2a556a113478d5ac905` (exit 1, line 8); line 10 — `REASON_ROWS population=23 documented=1 rows=1 bound=0 unbound=1 missing=22 duplicates=0 additional=0 receipt=stale probe_sha256=75daa9b6d130cba9b3c363599ff210147404f689fd9a47248f03a9e9975932d0 rev=eb8598bf442e3ab66bd7cea5ee3031a5e87aa843` (exit 1, line 11); line 13 — `REASON_ROWS population=23 documented=23 rows=23 bound=0 unbound=23 missing=0 duplicates=0 additional=0 receipt=absent probe_sha256=75daa9b6d130cba9b3c363599ff210147404f689fd9a47248f03a9e9975932d0 rev=5ad2369b043118eab32559d1d5cfb15dc8c8e2c3` (exit 1, line 14)
- `measured/c1.out:14` — `HOSTILE_ANSWERS cells=13 mismatches=0 positive_mismatches=0 probe=rev probe_sha256=c197912f8b3b5567e3ffd38178cb3a6e87187d7fb13136308c9a461ba8d2ef97 rev=f968fb19bb2a0c2afe271bfe606f11b52d10823f` (exit 0, line 15; committed at M2, names M)
- `measured/harm-M.out:3` — `tests=77 passes=77 failures=0` (exit 0, line 4); line 6 `RESULT pass=30 fail=0` (exit 0, line 7); line 20 `ROUTER_UNLOADABLE cells=11 mismatches=0 positive_mismatches=0 probe=rev probe_sha256=c197912f8b3b5567e3ffd38178cb3a6e87187d7fb13136308c9a461ba8d2ef97 server_sha256=ba272ee3446d9b98c9150c79667e6a8b217f25ee58ce0c6156cc96d2b5b362b0 rev=f968fb19bb2a0c2afe271bfe606f11b52d10823f` (exit 0, line 21); lines 23-24 operator router GET `"verdict": "MODEL_OK"`, `"reason": "router-unloaded-autoload"` (exit 0)
- `measured/c2.out:26` — `REASON_ROWS population=23 documented=23 rows=24 bound=24 unbound=0 missing=0 duplicates=0 additional=1 receipt=current probe_sha256=c197912f8b3b5567e3ffd38178cb3a6e87187d7fb13136308c9a461ba8d2ef97 rev=2ee0b55f4d3fd0cb3157d26b03280c1d21e27b2d` (exit 0, line 27; **uncommitted at draft time** — the L1 commits it; the scribe re-derived the same line read-only at M2)
- `measured/reason-capture.out:25` — `REASON_CAPTURE cells=24 probe_sha256=c197912f8b3b5567e3ffd38178cb3a6e87187d7fb13136308c9a461ba8d2ef97 rev=f968fb19bb2a0c2afe271bfe606f11b52d10823f out=.ufo/waves/round-90/measured/reason-cells.jsonl`

### Round-90 measured results

| Claim | Measured commit | Counting command → output | Verdict (author) |
|---|---|---|---|
| C1 operability | `f968fb19bb2a0c2afe271bfe606f11b52d10823f` | `python3 tools/round90-hostile-answers.py --repo . --rev f968fb19… --work <scratch>` → `HOSTILE_ANSWERS cells=13 mismatches=0 positive_mismatches=0 probe=rev`, exit 0; counter sha256 `345b12b3…` at M equal to freeze (`measured/c1-counter-hash.out`); harm (`measured/harm-M.out`): `tests=77 passes=77 failures=0`, `RESULT pass=30 fail=0`, `ROUTER_UNLOADABLE cells=11 mismatches=0 positive_mismatches=0`, operator router GET `MODEL_OK router-unloaded-autoload` | Frozen predicate met at M: K1 `positive_mismatches=0`; K2 every harm receipt agrees with its base counterpart; K3 the counter's bytes are unchanged from the freeze. |
| C2 depth | `2ee0b55f4d3fd0cb3157d26b03280c1d21e27b2d` | `python3 tools/round90-reason-rows.py --repo . --rev 2ee0b55f…` → `REASON_ROWS population=23 documented=23 rows=24 bound=24 unbound=0 missing=0 duplicates=0 additional=1`, exit 0; counter sha256 `fa4c3177…` at M2 equal to freeze (`measured/c2.out:1`); receipt `measured/reason-cells.jsonl` 24 lines, every line `probe_sha256=c197912f…` = the probe at M2 | Frozen predicate met at M2; K1 counter bytes unchanged; K2 (trigger prose vs receipt cell) is a reviewer read, recorded by the L1 from the wave; K3 the receipt is current, not stale. |

Score deltas: none claimed — no axis score moves this round. Two capabilities enter the repertoire with
first-working round 90.

**Capabilities — canonical list as of round 90** (the round-89 rows carry unchanged; two rows added)

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| hostile-answer-bounds | Cap a listener's `/v1/models` and `/props` answer at 4 MiB on the wire (`curl --max-filesize`, rc 63, plus a written-size re-check for older curl), grade an oversize model answer `FOREIGN_SERVICE`/`body-too-large` and an oversize `/props` as not autoload, strip C0/DEL/C1 controls from router status values, `Server:`/`Content-Type` headers and curl error text, print ids with C0/DEL/C1 as `\uXXXX` text, and escape every U+0001–U+001F and DEL in generated JSON, keeping non-ASCII text verbatim | `tools/round90-hostile-answers.py` (`HOSTILE_ANSWERS cells=13 mismatches=0 positive_mismatches=0`, `.ufo/waves/round-90/measured/c1.out`) | 90 |
| probe-reason-table | Bind each row of `SKILL.md` §Probe reason codes — the 23 frozen reason codes plus `body-too-large` — to a captured probe answer (cell, reason, verdict) on a receipt whose every line names the probe's sha256 at the measured revision; a wrong verdict, fabricated reason, duplicate, cell mismatch or stale receipt leaves the row unbound | `tools/round90-reason-rows.py`, `tools/round90-reason-capture.py` (`REASON_ROWS population=23 documented=23 rows=24 bound=24 unbound=0 missing=0 duplicates=0 additional=1`, `.ufo/waves/round-90/measured/reason-cells.jsonl`) | 90 |

### Round-90 disclosed limits

- The 4 MiB cap is a transfer rule: it bounds the bytes curl writes, not the CPU the probe spends on a body at
  the cap. The router GGUF header checks on crafted files (r89 SN01 F1) are unchanged and no latency/step
  budget is pinned (r89 R3).
- The listener still chooses which local files the probe opens (r89 SN01 F2); C1 does not change that path set.
- `listeners` and `snapshot` share `classify` and `jstr` and inherit the fix, but the frozen cells run `check`
  only.
- An oversize `/props` has no distinct reason: it is read as "not autoload" (an `unloaded` entry then grades
  `router-unloaded`), the conservative direction; only `/v1/models` oversize gets `body-too-large`.
- C2's receipt is a writable file: the counter binds rows to its `probe_sha256` and the closure can re-run
  `tools/round90-reason-capture.py` and `cmp`. `dns-failure` is excluded (unreachable), and `router-<value>`
  statuses outside the vocabulary are an open set with `router-unloaded` as the representative.

### Planned (round 91)

1. Operability (carried r89 R1): the `round75-instruments` arm stays red (`bad_rows=19`); the register-only fix
   still waits for the L0 ruling. Keep it open until either the L0 answer lands or the audit's eligibility rule
   is fixed without an append-only rewrite.
2. Operability (carried r89 R3): pin a latency/step budget for the probe in a harm suite, so a future slowdown
   is caught by a frozen rule rather than by a wave seat.
3. Operability (C1 uncovered, F1 CPU budget): the cap bounds bytes, not CPU — a crafted 4 MiB answer of many
   small ids is still parsed, and the router GGUF header checks on crafted files (r89 SN01 F1) are unchanged.
   Pin a CPU/step budget and grade it with a failing-before control.
4. Operability (C1 uncovered, F2 path choice): the listener still chooses which local files the probe opens
   (r89 SN01 F2). Grade the path set the probe may open, with a cell per listener-chosen path.
5. Operability (C1 uncovered, listeners/snapshot modes): the 13 frozen cells run `check` only; `listeners` and
   `snapshot` share `classify`/`jstr` but no cell proves the inherited cap and sanitisation. Run the hostile
   cells through both modes.
6. Operability (carried r89 R5): the three held-out LIMIT cells (chmod-000, split model with a missing shard,
   relative missing path), the FIFO INDETERMINATE cell and SC01's alias-pin `MODEL_MISMATCH` remain false
   greens; grade each from a committed receipt that also records the base verdict.
