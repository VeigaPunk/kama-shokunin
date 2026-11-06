# MT01ProbeMutants — C1 mutation probe (kama round 90, wave 1)

## Scope

Mutation-test the landed C1 rule in `tools/kama-probe.sh` against its frozen counter
`tools/round90-hostile-answers.py` (13 cells H1–H8, P1–P5). Probe under test is the C1 measured
revision M=`f968fb19bb2a0c2afe271bfe606f11b52d10823f`, sha256
`c197912f8b3b5567e3ffd38178cb3a6e87187d7fb13136308c9a461ba8d2ef97` (identical to the lane file on
disk and to `git show M:tools/kama-probe.sh`). Counter bytes at HEAD == freeze
(`6f6d7873…`): sha256 `345b12b386bfa8258e9cd7f75c8838107da3c809781069e99f3b721bd741dde5`.
13 one-change reverts (M1–M13), each applied to a scratch copy only; nothing tracked was edited.
All runs: `--probe-file` (prints `probe=override`), `--rev M`, private `--work`, host curl 8.23.0,
python 3.14, no model server, no 1234 traffic.

Baselines: `probe=rev` at M → `cells=13 mismatches=0 positive_mismatches=0`, rc 0
(`results/predicate-cleanpath.out`). Base probe C (`c15ffca8…`, rev `99cdb4d6`) → `mismatches=8
positive_mismatches=0`, rc 1 (`results/base-F.out`), matching the frozen do-nothing control.

## Commands and outputs (true exit codes)

- `python3 tools/round90-hostile-answers.py --repo <lane> --rev f968fb19… --work <w> --probe-file mutants/MN.sh`
  for M1–M13, 3 concurrent, each with its own `--work`; per-run stdout `results/MN.out`
  (all rc inside those files: killed = 1, escaped = 0).
- Auxiliary (NOT the frozen counter, clearly fenced): same command with
  `PATH=<scratch>/shim:$PATH`, where `harness/curl-shim` deletes `--max-filesize <n>` and execs the
  real curl (`--max-filesize` inert for *all* bodies — stronger than curl < 8.4.0, which still
  enforces it for Content-Length answers). Runs: `results/A-M-shim.out`, `A-M2-shim.out`,
  `A-M5-shim.out`.
- Reachability demos (`harness/demo.py`, lane-owned stub on a free port):
  operator `--expect $'a\x01b'` + `--json` → M parses (rc 2 drift), M11 dies rc 1 with unparseable
  JSON; listener `Content-Type: …; x=1\x1b[2J` → M strips, M7 leaks raw ESC; wildcard against a
  router listing whose only id carries ESC → M `MODEL_OK/expected-wildcard` rc 0, M9
  `MODEL_UNLOADED/router-unloaded` rc 2, no ESC bytes in either.
- Restoration: lane `tools/kama-probe.sh` sha256 unchanged (`c197912f…`), `git status --porcelain`
  empty for `tools/kama-probe.sh tools/round90-hostile-answers.py`, predicate re-run after all
  mutants → 13/0/0 rc 0. Scratch removed.

## Mutation table

| mutant | one-change revert | verdict | failing cells |
|---|---|---|---|
| M1 | drop `--max-filesize` in `fetch` | KILLED | H1, H2 |
| M2 | drop `wc -c` re-check in `fetch` | ESCAPED | — |
| M3 | M1+M2 | KILLED | H1, H2 (verdicts MODEL_OK) |
| M4 | drop `--max-filesize` in `router_autoload` | KILLED | H3 |
| M5 | drop `router_autoload` size check | ESCAPED | — |
| M6 | drop `strip_ctl` on `F_SERVER` | KILLED | H7 |
| M7 | drop `strip_ctl` on `F_CT` | ESCAPED | — |
| M8 | drop `clean()` in `served_ids` | KILLED | H4, H5, H6 |
| M9 | old `router_entries` id filter (`\t\r\n` only) | ESCAPED | — |
| M10 | old status-value filter | KILLED | H8 |
| M11 | drop `jstr` control loop | ESCAPED | — |
| M12 | `MAX_BODY=67108864` | KILLED | H1, H2, H3 |
| M13 | rc 63 → `MODEL_OK` | KILLED | H1, H2 |

8 killed / 5 escaped; `positive_mismatches=0` in all 16 runs (no harm signal; P1–P5 pass under
every revert). Every killed mutant failed exactly the cells that own its rule; no collateral cell.

## Findings

**DEFECT D1 (M2 + M5 escaped) — the older-curl `wc -c` re-checks are claimed but no frozen cell
owns them.** The C1 rule text (plans/round-90-claims.md:40) names "a size check of the written body
for older curl" for both the `/props` and `/v1/models` fetches; removing either check leaves 13/0/0
(`results/M2.out`, `results/M5.out`) because host curl 8.23.0 already aborts unknown-length bodies
at the cap. Under the inert-cap shim the loss is observable: M2 flips H1/H2 to `verdict=MODEL_OK`
on a 64 MiB answer (false green) and H3 to `MODEL_OK`; M5 flips H3's verdict from
`MODEL_UNLOADED` to `MODEL_OK` (`A-M2-shim.out`, `A-M5-shim.out`). Stronger: with the re-check
*intact* and only the curl option inert, H1–H3 still fail on `sent=67108864`
(`A-M-shim.out`) — so on curl < 8.4.0 the re-check preserves the verdict but cannot restore the
16 MiB byte bound the cells assert. The claim "caps every listener answer body" therefore holds
only on curl ≥ 8.4.0, and the fallback clause is unverifiable by the frozen counter.

**DEFECT D2 (M11 escaped) — `jstr`'s control loop is claimed but unowned.** The rule text
(plans/round-90-claims.md:42) says "`jstr` escapes every control character"; all 13 cells
pre-sanitize every field that reaches `jstr` (`strip_ctl` on F_SERVER/F_CT/F_ERRMSG/`probe_short`,
`clean()` on served ids), so deleting the loop changes no cell (`results/M11.out`). The loop is
still load-bearing on inputs no cell covers: operator `--expect`/registry text carrying U+0001
makes the landed probe emit parseable JSON (rc 2 drift) while M11 prints unparseable JSON and dies
rc 1 (`harness/demo.py` output in the session transcript). Coverage gap, not dead code.

**NOTE N1 (M7 escaped) — `strip_ctl` on the answered `Content-Type` is unowned.** No cell sends a
hostile CT. Demo: CT `application/json; x=1\x1b[2J` on a healthy answer leaks the raw ESC into the
table evidence at M7 and is stripped at M. CT is not named in the frozen rule text (only ids,
router status values and `Server:`), so this is outside C1 as frozen — but it is listener-controlled
text reaching the operator's terminal.

**NOTE N2 (M9 escaped) — the `router_entries` id filter is unowned and selection-only.** The old
filter keeps C0/ESC ids in router-entry *selection*; bytes never leak (the output path is owned by
`served_ids clean()`, M8 kills). Demo wildcard on a listing whose only id carries ESC: M gives
`MODEL_OK/expected-wildcard` (entry dropped), M9 gives `MODEL_UNLOADED/router-unloaded` with the
same `down` reason. A verdict difference no cell exercises; the landed behavior also grades a
garbage-only listing `MODEL_OK` under a wildcard, which is unfrozen, not a regression.

**NOTE N3 (H8 at M)** — H8 table mode exits 2 (drift) at M and the cell only asserts "no ESC", so
the cell owns the sanitization, not a verdict. Not a defect; recorded so a drift exit is not read
as a probe error.

**NOTE N4 (harness hygiene)** — my first predicate run inherited a `PATH` shim from an earlier
command in the persistent shell and printed `mismatches=3` (sent=64 MiB, correct verdicts); it is
kept only as `results/predicate-CONTAMINATED-shim-path.out` and must not be read as a C1 result.
It doubles as a check that the shim really makes `--max-filesize` inert; `predicate-cleanpath.out`
is the valid run.

## Deliverables

Out dir `.ufo/waves/round-90/w1/out/MT01ProbeMutants/`:
`harness/mutants.diff` (M1–M13 unified diffs vs the M probe), `harness/mutants.sha256`,
`harness/gen.py` (regenerates all 13 byte-exactly from `git show M:tools/kama-probe.sh`),
`harness/demo.py`, `harness/curl-shim`, `results/M1.out`…`M13.out`, `results/base-M.out`,
`results/base-F.out`, `results/A-M-shim.out`, `results/A-M2-shim.out`, `results/A-M5-shim.out`,
`results/predicate-cleanpath.out`, `results/predicate-CONTAMINATED-shim-path.out`.

VERDICT: partial — the C1 counter predicate holds at M (13/0/0, rc 0) and 8/13 one-change reverts die, but 5 escape: the two older-curl size re-checks and `jstr`'s control loop are claimed in the plan yet owned by no frozen cell, and the Content-Type strip and router-id filter are unfrozen.
