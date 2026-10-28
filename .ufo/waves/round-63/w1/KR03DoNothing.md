# KR03DoNothing — attack: do-nothing and shortcut controls (round 63, kama)

Seat: KR03DoNothing (leaf, advisory). Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09`.
Method: a clone of the tip in scratch; every mutant is one commit on top of the tip in its own clone;
each counter is run from the clone's `tools/` with `--repo <clone> --tip <commit>`.
Evidence (kept): `.ufo/waves/round-63/w1/out/KR03DoNothing/` — counter stdout/stderr for every run,
receipts (`receipts/`), patches (`patches/`), the replay and fake-server inputs, the runner, and the
head-only mutant script. Scratch deleted before yield.
Installs: none. Nothing in `~/.local/bin` or any PATH directory touched. No pacman. No commits, no lane
edits, no lane index or jj state touched. No verdict on the C1 or C2 claims: every result below is a fact
about a counter or control set.

## Summary

**SURVIVED (met=True with the defect present):** S1 `c2-reconcile-lie`, S2 `c2-head-only`, S6 `c1-replay`,
S7 `c1-fake-child`. **Row-level SURVIVED (row facts byte-identical to base; met still blocked by the
reconciler):** S3 `c2-echo-pattern`, S4 `c2-capacity-refuse`. **SURVIVED (accepted by the predicate as
frozen):** weak substring patterns (W1, W2). **REJECTED:** S5 `c2-all-hostbusy`.

The committed controls reject records that are wrong or missing. None of them checks that an accepted
result was produced by the run it claims. Every shortcut that passes is a provenance shortcut.

## 1. Baseline at the tip

C1 (`round63-c1-counter.py`):
```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
C2 (`round63-c2-counter.py`):
```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False
```
At the tip, C2 fails only `selfdesc_mismatches=8`. The reconciler's eight details: r41 coverage run gives 38
against the stated 36; head banner says round 61; no `### Planned (round 64)`; head lacks "12 capabilities";
Saturation lacks the first-working list; the head table lacks `live-ollama-lifecycle`; PROVINCE.md lacks
`registry/ollama-live-claims-r61.tsv`. So any shortcut that moves that number flips C2 to met.

## 2. Shortcut results

| # | Mutant (commit on tip) | What is skipped | Counter output (verbatim, one line) | Verdict |
|---|---|---|---|---|
| S1 | `c2-reconcile-lie`: `round42-selfdesc-reconcile.py:269` `mism = sum(c.values())` → `mism = 0` (one line) | the self-description reconciliation | `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=0 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=True` | **SURVIVED / ACCEPTED** |
| S2 | `c2-head-only`: SCORECARD text only, canonical list untouched: banner "round 63"; `### Planned (round 64)` stub; "12 capabilities"; first-working sentence in Saturation; `live-ollama-lifecycle` row added to the head mirror table; Axes coverage row restated 36→38 and PROVINCE sha/line count restated; plus one appended pointer line in PROVINCE.md. Reconciler (alone) prints `mismatches=0 met=True`. | the SCORECARD head re-derivation the freeze reserves for L1 | `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=0 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=True` | **SURVIVED / ACCEPTED** |
| S3 | `c2-echo-pattern`: `sources-append-only.py` `--selftest` prints `45/45 selftest cases passed` and returns 0 without running any case | the selftest itself | `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False` | **row-level SURVIVED** (line identical to base; met blocked only by reconciler 8) |
| S4 | `c2-capacity-refuse`: `kama-context-capacity.py` raises `SetupError('host-not-idle-before-K1')` as the first statement in `main`'s try block, before any probe | the K1 cell and the host-idle probe | identical to S3 (`host_busy=1 mismatches=0 ... selfdesc_mismatches=8 ... met=False`) | **row-level SURVIVED** |
| S5 | `c2-all-hostbusy`: all 12 registry verdict cells rewritten to `host-busy` | — | `population=12 rows=12 covered=1/12 bound=1 eval_lines=1 sensitive=1/1 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=0/12 errors=11 met=False` | **REJECTED** (`hostbusy-not-declared` ×11) |
| S6 | `c1-replay`: `kama-completion-live.py`. The seven request-plane captures are replayed from the genuine tip receipt of an earlier run (`bad_request`, `completion`, `completion2`, `health`, `models`, `props`, `tokenize`; byte-identical to that run). The real llama-server is still spawned, ownership-gated, held, witnessed and torn down. nonce, child pid, port, hold and teardown are this run's. | every live request in the request plane | `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[...same as baseline...]` | **SURVIVED / ACCEPTED** |
| S7 | `c1-fake-child`: `Popen` argv replaced by a 90-line stdlib HTTP fake (`receipts/fake_llama.py`). The receipt still names the real llama-server path and sha. The fake's `server.log` is 0 bytes with no llama banner. | the llama.cpp process entirely | `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[...same...]` | **SURVIVED / ACCEPTED** |
| W1 | no mutant: `verdict_fn` applied directly to `IA_SELFTEST pass=0 fail=45` for pattern `IA_SELFTEST pass=` | the instrument's pass/fail semantics | verdict True, sensitive True | **SURVIVED** (accepted as frozen) |
| W2 | no mutant: `verdict_fn` applied to `scan: unknown=01 references=7` for pattern `unknown=0` | the count semantics | verdict True, sensitive True | **SURVIVED** (accepted as frozen) |

Verification of S6/S7 (done, not inferred): the replay receipt has `verdict=REQUEST_OK`, a new `child_pid`
(94392 vs 2716799) and port (35895 vs 46437); its `server.log` is 1877 bytes with the llama.cpp banner; its
captures are byte-identical to the earlier genuine run, including `created` 1793227518. The replayed
`completion` request body is `{"prompt": "The cat sat on the", ...}` with no nonce. The fake-child receipt:
`verdict=REQUEST_OK`, `child_pid=97014`, `server.log` 0 bytes, `server.path=/home/vgpnk/.local/opt/llama-b11755/llama-server`.
The interpreter the fake ran under (`/usr/bin/python3`) does not hash to the pinned b6a31a8e….

Row-level equivalence (S3, S4): the counter lines for `c2-echo-pattern` and `c2-capacity-refuse` equal the
base line in every field the row facts use (`covered 12/12`, `bound 12`, `sensitive 12/12`, `mismatches 0`,
`host_busy 1`, `errors 0`). The only field that differs from a green counter is `selfdesc_mismatches=8`.

## 3. What the committed controls cover, and what they do not

Committed (`controls/`): `c1-base.txt` (absent tool, met=False), `c1-relabel.txt` (schema string changed to v2,
rejected by missing checks), `c2-base.txt` (absent counter/registry/canonical list, selfdesc 8),
`c2-shortcut.txt` (registry plus canonical list with no ledger repair: `mismatches=2 sensitive=11/12`, rejected).
Inside each counter, 44 C1 and 12 C2 control families mutate a recorded field or a canonical row, re-seal it,
and check that the named check (and only it, within the cap) is what rejects it.

Covered: any record that is wrong, relabelled, missing or duplicated. Not covered: any result that is
**accepted** while its source was never run. The controls never ask where an accepted value came from.

The shortcut the committed controls do not cover, named as the item asks: a result produced by a previous run
or by a tip-tree instrument, accepted while the claimed live work never happened. Instances:

- **Cheapest: S1 (one line).** The C2 counter takes `mismatches=` from the reconciler's stdout and
  ignores its exit status (`selfdesc_mismatches`). The reconciler is a tip-tree tool. No control touches it.
- **Most consequential: S6 (replay on a real hold server).** Every element the freeze lists as live is present
  except the request plane. The witness proves a server listens and answers the nonce prompt, but the
  witness never checks the captured completion, and no control asks whether the captures belong to this run.
- **S2 (SCORECARD head).** The reconciler is substring presence. No control exercises the head text.
- **S3, S4 (tool-body echo, unconditional refusal).** The sensitivity test checks dependence of the verdict on
  the output. It cannot see whether the tool produced the output, and the `hostbusy` control checks only the
  declared-alternative flag. The host-busy check is a pgrep before and after, which this host satisfies
  permanently (foreign llama-servers on 1234, 45669, 37323, 34885 and others). The honest K1 receipt
  (`receipts/base-c2-cc.json`) carries `host_idle: {ok: false, other_pids_seen: [11 pids], waited_s: 20.1}`.
  The refusal receipt (`receipts/c2-capacity-refuse-cc.json`) has no `host_idle` key at all.
- **S7 (fake child).** `server_digest` hashes the path the receipt names, not the executed process. The witness
  docstring says an outside observer can read `/proc/<pid>/exe`; the counter never does.

## 4. Counter defects and smallest corrections (not applied; for L1)

- **D1 — C1 captures not bound to the run (S6).** Smallest correction: the tool already receives `--nonce`;
  have it put the nonce into its own completion prompt, and have the counter require
  `NONCE in captures.completion.request_body` (check `completion_nonce_bound`). Add a control family that
  replays earlier captures and expects that check to fail. The replay in S6 has no nonce in its request body, so
  this check would reject it.
- **D2 — C1 child identity (S7).** Smallest correction: during the hold, the witness reads `/proc/<pid>/exe`,
  sha256s it, and requires `SERVER_SHA` (`live_exe`). Control: a witness mutation that carries the interpreter's
  path and sha; expect `live_exe`. For S7 this check is decisive: `/usr/bin/python3` does not hash to the pin.
- **D3 — C1 dependency not pinned [code-read, not exercised].** `live_owned` calls the tip's
  `kama-llamacpp-live.py:port_owned_by`, the same function the tool's ownership gate uses. The counter copies
  whatever blob the tip holds for that file. A tip that edits `port_owned_by` would pass `live_owned` for any
  listener. Smallest correction: pin that file's sha256, or inline the 12-line ownership check in the counter.
- **D4 — C2 reconciler trusted (S1, S2).** `selfdesc_mismatches` returns the printed count whatever the return
  code. Smallest correction: pin the reconciler's sha256 (the freeze says "imported unchanged") and require
  `returncode == 0` alongside `mismatches=0`. Pinning alone does not stop S2, because S2 edits SCORECARD. S2
  needs the head checked against a fact the head cannot restate, such as the count it cites recomputed by the
  counter.
- **D5 — C2 host-busy unjustified (S4).** Smallest correction: require the K1 receipt written by `--out` to
  contain `host_idle` with `ok: false` and a non-empty `other_pids_seen` that is a subset of the counter's own
  pgrep set before the run. The honest receipt has it and the S4 receipt does not. Control: `hostbusy-unprobed`,
  expect `host_idle`.
- **D6 — C2 substring patterns (W1, W2).** `pat in out` accepts any output containing the pattern as a
  substring. Smallest correction: anchor each pattern to its tool's full line form (e.g. `IA_SELFTEST pass=\d+ fail=0`,
  `unknown=0\b`). This changes the frozen manifest, so it needs an amendment.
- **D7 — C2 tool bodies unpinned (S3).** The predicate says "verdict true (pattern emitted, exit 0)", which S3
  satisfies by definition. Smallest correction: freeze a per-row sha256 of each bound tool at the frozen tip.
  That is also a predicate change and needs an amendment. No check on the output alone can close this gap.

Suggested control families for the next counter revision (each would reject one of S1–S7 or W1/W2):
`replayed-captures` (D1), `witness-exe` (D2), `dep-pin` (D3), `reconciler-pin` (D4), `hostbusy-unprobed` (D5),
`weak-pattern` (D6), `tool-pin` (D7).

## 5. Notes and limits

- Counters ran from the clones' `tools/`, against commits holding the mutants. Baselines were run on a
  clone of the tip. Runs took about 40 s (C1) and 45 s (C2). The counters spawned and tore down their own
  llama-server children on unregistered loopback ports; no foreign process was signalled. Detached runs
  (`setsid`) were used after a subshell launch silently died; the outputs in `out/` are from the completed runs.
- S2's head restatements (coverage sha and line count) were computed from the PROVINCE.md I had just appended
  to. That is exactly the relabel-after-the-fact the freeze reserves for L1 to re-derive after measurement.
- Mutants were built two ways: hashline edits for short lines (S1, S3, S4, S6, S7) and an exact-substring
  script for the long SCORECARD lines (S2, `receipts/mk_headonly.py`, asserts one match per replacement). The
  S5 registry rewrite changed only the verdict column (12 cells). Patches are in `patches/`.
- Scratch (clones, fake, replay copy, work dirs) deleted before yield. Every receipt and output cited above is in `out/`.

## Tally

KR03DoNothing tally: SURVIVED met=True ACCEPTED 4 (S1 c2-reconcile-lie, S2 c2-head-only, S6 c1-replay, S7 c1-fake-child);
row-level SURVIVED 2 (S3 c2-echo-pattern, S4 c2-capacity-refuse); weak-pattern SURVIVED 2 (W1, W2);
REJECTED 1 (S5 c2-all-hostbusy). Baselines: C1 met=True 44/44 3/3; C2 met=False selfdesc 8 (all else green).
