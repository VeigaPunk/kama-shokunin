# Round 90 — frozen claims (kama)

Base revision `99cdb4d6270455494dd27901efe84a0f3b342062` (lane `master` at round start; `jj-lane.sh state`
ahead=0 behind=0, tree clean). L1 `KamaR90` (holds the §3 planner seat). Frozen in the commit that adds this
file; nothing below changes after that commit. Every control named here was executed before this file was
committed; its receipt is committed with it under `.ufo/waves/round-90/controls/`.

Closure history read before declaring: `corpus/lessons/round-89-verifier-spotcheck.md` (r89 **admitted**; routed
R1–R5) and `round-88-verifier-spotcheck.md` (r88 rejected-honest-stop: a frozen expectation written from lane
prose). Both claims below therefore grade by observable output of real runs, never by canned expectations
copied from lane text. Routed R4 (r89 SN01 F3/F4, SCORECARD §Planned (round 90) item 1) is C1.

Axes (SCORECARD `## Axes`): operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7.
Lowest non-retired: depth / calibration / adjacency (7). C2 works depth.

## C1 — operability (sourced: S587, S588): hostile listener answers stay bounded and cannot break output

**Predicate (one sentence, same in counter docstring and receipt label):**
`python3 tools/round90-hostile-answers.py --repo . --rev <M> --work <scratch>` prints
`HOSTILE_ANSWERS cells=13 mismatches=0 positive_mismatches=0 probe=rev …` and exits 0 at the measured commit M,
the counter's bytes being identical to this freeze commit.

- Cells (13, lane-owned stub HTTP servers on free loopback ports, one per cell, in the counter's process; each
  pass condition is in the counter docstring): H1 64 MiB `/v1/models` with Content-Length, H2 the same
  close-delimited, H3 64 MiB `/props` behind a router-shaped listing, H4 an id carrying `\n` and tabs (table
  column forging), H5 an id carrying U+0001 (`--json`), H6 an id carrying ESC (table), H7 a `Server:` header
  carrying ESC, H8 a router status value carrying ESC; positives P1 plain match, P2 a legitimate 1 MiB listing,
  P3 a non-ASCII id kept verbatim, P4 an id with `"` and `\` round-tripped, P5 wildcard. `positive_mismatches`
  counts P1–P5 (harm).
- Do-nothing control (base probe `c15ffca8…`): `mismatches=8 positive_mismatches=0`, exit 1 —
  `controls/c1-base.out` (H1–H3 accept all 64 MiB and grade `MODEL_OK`; H4 widens the header to 9 columns; H5,
  H7, H8 `--json` exit 1 unparsed; H6–H8 table carries raw ESC).
- Forgery controls (`--probe-file`, so they print `probe=override` and can never meet the predicate):
  F1 blanket refusal `controls/f1-blanket-refusal.sh`: `mismatches=6 positive_mismatches=5`;
  F2 over-sanitizer (base + non-ASCII stripped from ids) `controls/f2-over-sanitizer.sh`: `9 / 1` (P3);
  F3 over-tight cap (base + `--max-filesize 65536`) `controls/f3-tiny-cap.sh`: `7 / 1` (P2). All exit 1
  (`controls/c1-f1-blanket-refusal.out`, `c1-f2-over-sanitizer.out`, `c1-f3-tiny-cap.out`).
- Rule to implement (intent; the claim is judged only by the counter): `curl --max-filesize` on the
  `/v1/models` and `/props` fetches (S587: since curl 8.4.0 it also aborts a transfer of unknown size at the
  threshold; exit 63) plus a size check of the written body for older curl; an oversize model answer is never
  `MODEL_OK`; ids, router status values and the `Server:` header lose or escape U+0000–U+001F/U+007F before they
  reach table or JSON output, and `jstr` escapes every control character (S588 RFC 8259 §7: control
  characters U+0000–U+001F MUST be escaped).
- Kill rules (any one → C1 not verified): K1 `positive_mismatches>0` at M; K2 a harm suite regresses against its
  base receipt at M: `tests/probe-verdicts/check.py` `tests=77 passes=77` (`controls/harm-base-probe-verdicts.out`),
  `tools/test-snapshot.sh` `RESULT pass=30 fail=0` (`controls/harm-base-test-snapshot.out`), round-89
  `tools/round89-unloadable-cells.py` `cells=11 mismatches=0 positive_mismatches=0`
  (`controls/harm-base-r89-cells.out`), operator router 127.0.0.1:1234 (GET only) `MODEL_OK
  router-unloaded-autoload` (`controls/harm-base-operator-1234.out`); K3 the counter changes after this commit.
- Held-out (not in the predicate): wave seats build unseen hostile answers after M (gzip bombs, slow-drip
  bodies, C1 controls in other fields, very long ids, DEL/U+0085/U+2028, JSON with BOM). Each is reported with
  base and M verdicts; a held-out cell where base is right and M wrong is reported as harm.

## C2 — depth (lowest axis, 7): the probe's reason codes, each bound to a captured probe answer

**Predicate:** `python3 tools/round90-reason-rows.py --repo . --rev <M2>` prints
`REASON_ROWS population=23 documented=23 … unbound=0 missing=0 duplicates=0` and exits 0 at the measured commit
M2, counter bytes identical to this freeze commit.

- Population (frozen in the counter): the 23 reason codes the base probe can print (`C_REASON=`/`RT_REASON=`
  assignments, base lines 770–911); `dns-failure` is excluded with its reason (fetch always targets the literal
  127.0.0.1). Rows live in `SKILL.md` under `## Probe reason codes`; a row binds only to a line of
  `.ufo/waves/round-90/measured/reason-cells.jsonl` at M2 with the same cell, reason and verdict, and only
  when every receipt line names the sha256 of `tools/kama-probe.sh` at M2 (a stale receipt binds nothing).
- Receipt producer (post-freeze work, not the counter): `tools/round90-reason-capture.py`, one stub cell per
  reason, run against the probe at the measured revision; the closure can re-run it and `cmp`.
- Do-nothing control: base `documented=0 rows=0 missing=23`, exit 1 (`controls/c2-base.out`). Forgery battery
  on a scratch fixture repo (`controls/c2-forgeries.sh` → `controls/c2-forgeries.out`): wrong verdict,
  fabricated reason, duplicate, cell mismatch → `rows=5 bound=2 unbound=3 duplicates=1`, exit 1 (fenced,
  indented, after-section and before-section rows not counted); a stale receipt → `bound=0 receipt=stale`,
  exit 1; a prose-only table of all 23 reasons with no receipt → `documented=23 missing=0 bound=0
  unbound=23`, exit 1. (The battery's printed expectation first said `bound=1 unbound=4`; I corrected it
  before freeze — the duplicate row binds like its original and fails through `duplicates=1`.)
- Kill rules: K1 counter changes after this commit; K2 a row's trigger text contradicts its receipt cell
  (reviewer read, reported); K3 C1's probe change makes the receipt stale and it is not re-captured at M2.

## Separability, sources, carried defects

- C1's counter never reads `SKILL.md`; C2's counter never runs the probe. C2 verifies on the base probe alone
  (capture against base bytes); C1 verifies with no SKILL edit. If C1 lands first, C2's receipt is captured at
  the post-C1 probe (any new C1 reason code may appear as an `additional` row).
- Sourced claim: C1 rests on S587 (curl `docs/cmdline-opts/max-filesize.md` @ `curl-8_23_0`, the host's curl
  8.23.0) and S588 (RFC 8259 §7), both opened this round before freeze.
- Carried from the r89 closure: R1 (`round75-instruments` `bad_rows=19`, L0 open) stays open, not claimed;
  R2 (`bc` missing in r89 `harm-final.out`) and R3 (latency budget) are wave items reported in the lesson; R5
  held-out LIMIT cells are not claimed this round.
