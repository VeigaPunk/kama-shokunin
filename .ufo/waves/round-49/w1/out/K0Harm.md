# K0Harm — round-49 no-harm attack (lane kama, v2 wave; leaf seat)

Verdict: **PASS — no harm to any of the six axes from this round's build was found.** All
reds observed at 74558c71 are either the known integration-cleared items (unregistered
round-49 counters) or pre-existing findings already present at the round-48 closure base
438127bc (stale SCORECARD calibration fact; two unknown fleet OIDs in the round-48 verifier
lesson). No check failed *because of* the round-49 build.

Evaluated on a scratch clone of the lane at `74558c71c38ceaeace15fd4cf8aa9d84977584b1`
(base `438127bc01ff3b99f98468549d58046f932490ef`). No tools were installed; no lane files
were mutated; no services started/stopped (the live-tool selftest opened and closed its own
loopback listeners; no leftover `llama-server` from this seat — `pgrep` shows only sibling
seats' processes).

## Commands run (evidence: `.ufo/waves/round-49/w1/out/K0Harm/commands.txt`)

| # | Command | Result | RC |
|---|---------|--------|----|
| 1 | `python3 tools/gate-registry-check.py` | `registered 42 unregistered 2 defective 0` (round49-append-audit-v4-check.py, round49-replay-witness-audit.py) | 1 |
| 2 | `python3 tools/capability-repertoire-audit.py` | `listed 11 observed 11 missing 0 unsubstantiated 0 met True` | 0 |
| 3 | `python3 tools/round41-scorecard-reconcile.py` | `axes=6 facts=36 run_bad=1 mismatches=1 met=False` — calibration run expects `34` verifier-spotcheck blobs | 1 |
| 4 | `python3 tools/round42-selfdesc-reconcile.py` | `r41=1 … mismatches=1 met=False` — same calibration fact | 1 |
| 5 | `python3 tools/round43-registry-audit.py` | `unreg=2 selftest=1 spot=1 mismatches=4 met=False` | 1 |
| 6 | `python3 tools/planned-pointer-check.py SCORECARD.md` | `pointer: ok … measured: ok … met=True` | 0 |
| 7 | `python3 tools/digest-ledger.py scan --repo . --rev 74558c71…` | `tokens=127 blob=111 external_ok=9 external_absent=1 unverifiable=5 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0` | 0 |
| 8 | `python3 tools/hexrun-census.py scan --repo . --rev 74558c71…` | `tokens=1833 … upstream_ok=92 wrong_flagged=2 ledger_bad=0 unknown=2` | 1 |
| 9 | `python3 tools/sources-append-only.py --from 438127bc… --to 74558c71…` | `added S494 (allowed) / added S495 (allowed) / no append-only violations` | 0 |
| 10 | `python3 tests/llamacpp-live/check-receipt.py --selftest` | `16 VALID and 1 NOT-EVALUATED receipts accepted; 107 mutations + unreadable case rejected` | 0 |
| 11 | `python3 tools/gguf-identity.py --selftest` | `status passed, 30/30 cases` | 0 |
| + | `python3 tools/gate-registry-check.py --selftest` | `PASS … ×5, FAIL lane-tip 122c4ee95701: exit=1 line='registered 42 unregistered 2 defective 0'` → `GATE_SELFTEST pass=5 fail=1` | 1 |
| + | `python3 tools/kama-llamacpp-live.py --selftest` | `selftest: ok; closed tcp6 listeners …` | 0 |
| + | `python3 tools/append-only-audit.py --selftest` | `AOA_SELFTEST pass=30 fail=0` (incl. new `launder-through-head`, `binding-v4`) | 0 |

## Axis-by-axis no-harm analysis

### Operability — PASS
- Witness machinery is fully opt-in: `--witness-dir` defaults `None` in both
  `kama-live-replay.py` (line 481 ff., insertion at lines 275–280) and
  `kama-llamacpp-live.py` (line 1581); an unwitnessed replay builds exactly the same
  argv as before, so round-47/48 v4/v5 replay callers are unaffected. `argv[-2:-2]`
  insertion lands both `--server-archive` (v5) and witness args before the terminal
  `--out <rerun>` pair, so no arg is misplaced.
- The replay subprocess timeout grows by the witness timeout (line 281), so a witnessed
  hold cannot be cut off by the caller's own deadline.
- New archive bounds are generous vs. real assets: 1 GiB / 4096 entries vs. ~70 MB /
  ~60 entries for b11909 (lines 208–210); `verify_archive_member` reads the member
  only after size/sparse checks (lines 233–279). `--server` is the extracted member, so
  the new `size == member.size` check is trivially satisfied for legit replays.
- `check-receipt.py --selftest`, `kama-llamacpp-live.py --selftest` pass; listener
  cleanup verified (no leftover servers from this seat).
- Only operability red is gate-registry-check #1, which is the known integration item
  (counters not yet in SKILL.md's instrument registry) — see F1.

### Freshness — PASS
- `sources-append-only.py` base→tip: only additions S494/S495 (`corpus/SOURCES.md`
  lines 245–246), no append-only violations.
- `digest-ledger.py` scan exits 0. Its two flagged tokens are pre-existing and unrelated
  to round 49: `external_absent bcc55c92…` points at round-35/36 wave artifacts
  (`.ufo/waves/round-36/…` references to `ScribeGate/fetch/dockerfile.html`), and
  `wrong_flagged 5585f602…` is the round-40 sglang amendment superseded-digest record
  (`.ufo/waves/round-40/preregistration.json:15`). Neither touches changed files.

### Depth — PASS
- `capability-repertoire-audit.py` lists/observes 11 capabilities, 0 missing, 0
  unsubstantiated, `met True`. The round's changes deepen the existing
  `live-receipt-replay` capability (execution witness, bounded archive verification)
  rather than adding a new capability row; no repertoire regression.

### Coverage — PASS (with pre-existing D1)
- `planned-pointer-check.py SCORECARD.md` passes: `### Planned (round 49)` heading and
  all measured heads resolve (`met=True`).
- `round41-scorecard-reconcile.py` fails only on the stale calibration fact (D1),
  which fails identically at the base commit (evidence: `base-comparison.txt`) — not
  caused this round. Expected missing round-49 SCORECARD/LOG/lesson/QUALITY/README
  sections are scribe integration items and are not flagged by any of the run commands.

### Calibration — PASS (with pre-existing D1 and integration-cleared F1)
- `append-only-audit.py` v4 self-test passes 30/30, including the two new v4 cases
  (`launder-through-head` — origin carve-out; `binding-v4` — whole-word token,
  negation window, no wildcard self-declaration). Output shape is backward compatible:
  schema string unchanged `append-only-audit/v3`, additive `"definition": "v4"` key
  (`tools/append-only-audit.py:504`), so consumers of the v3 JSON still parse.
- The v4 semantics only tighten the carve-out (grading more lines), which is the
  instrument correction the claim promises; no other lane document is affected.
- `round42-selfdesc-reconcile.py` / `round43-registry-audit.py` reds decompose into
  D1 (pre-existing fact) + F1 (unregistered counters) + the gate selftest lane-tip
  case (same F1 root cause: `tools/gate-registry-check.py` lines 338–349 evaluate the
  repo tip and require zero unregistered counters; SKILL.md:1330 documents
  `GATE_SELFTEST pass=6 fail=0`, run prints `pass=5 fail=1` only because of F1).

### Adjacency — PASS (with pre-existing D2)
- `planned-pointer-check.py` passes; changed tools' public interfaces are additive
  (opt-in flags, additive JSON key), so nothing else in the lane consumes a changed
  shape.
- `hexrun-census.py` exits 1 for `unknown=2`: both tokens are fleet-repo commit OIDs
  cited in `corpus/lessons/round-48-verifier-spotcheck.md:21`
  (`15710a2a8286bf12d55d943f17028178fe8d421a`, `dcc079e7e56d3312ec70e0bd5b3c7f885b1242e8`).
  Identical counts at base (evidence: `base-comparison.txt`), so pre-existing and not
  round-49-caused. The two `wrong_flagged` tokens are informational (they resolve by
  prefix to known classes).

## Findings

- **F1 (integration-cleared, not a defect of the build):** round-49 counters
  `tools/round49-replay-witness-audit.py` and `tools/round49-append-audit-v4-check.py`
  are not yet in the SKILL.md instrument registry (`gate-registry-check.py`:
  `unregistered` ×2; `round43-registry-audit.py` `unreg=2`). This is also the sole
  reason `gate-registry-check.py --selftest` lane-tip fails (documented
  `GATE_SELFTEST pass=6 fail=0` vs run `pass=5 fail=1`) and for the `selftest=1`
  mismatch in `round43-registry-audit.py`. Clears when the round-49 instrument rows land
  at integration.
- **D1 (pre-existing, carried from the round-48 closure):** `SCORECARD.md:18`
  calibration fact states `34` verifier-spotcheck blobs, but the tree holds 35
  (`corpus/lessons/round-48-verifier-spotcheck.md` was added at the closure). This is
  the single `run_bad=1` that fails `round41-scorecard-reconcile.py` and
  `round42-selfdesc-reconcile.py`, and the `spot=1` in `round43-registry-audit.py`;
  all fail identically at base 438127bc (evidence: `base-comparison.txt`). Smallest
  safe correction: at round-49 integration (when the scorecard's round-49 section is
  written), re-anchor the calibration fact to the actual blob count (35 now; 36 once
  the round-49 lesson lands).
- **D2 (pre-existing):** `hexrun-census.py` exits 1 because two fleet OIDs cited in
  `corpus/lessons/round-48-verifier-spotcheck.md:21` are unknown to the census
  (neither lane OID nor upstream ledger row). Smallest safe correction: add the two
  fleet commits as `upstream` ledger rows in `registry/hexrun-ledger.tsv` (or annotate
  the lesson), at integration or closure — not round-49 build scope.

## No harm confirmed (the six "ways it could harm")
1. **Operability:** witness/archive-bound machinery cannot affect unwitnessed replays
   (opt-in defaults; same argv; timeout grows by witness timeout; size caps above real
   assets).
2. **Freshness:** SOURCES append-only clean; ledger scan exits 0; flagged tokens are
   historical.
3. **Depth:** repertoire audit met, no capability row disturbed.
4. **Coverage:** planned/measured pointers intact; only D1 (pre-existing) and expected
   missing round-49 sections.
5. **Calibration:** v4 self-tests pass; JSON shape backward-compatible; reds are D1 +
   F1.
6. **Adjacency:** public interfaces additive; hexrun red is D2 (pre-existing).
