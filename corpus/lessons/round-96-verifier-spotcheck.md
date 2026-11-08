# Round 96 — verifier spot-check (non-author)

author: hyaku closure (non-author integrator, @m_zfl)

Lane `kama`, round 96. Lane HEAD after round: `49ef853f8480b445921123fcfc01d9357f54b5c0`. Base
`5d43528badc31ad6c0ca1848c00561f531924e4d`. Freeze `58001b71`. Verdict: status `ok`, **not admitted**
(`rejected-honest-stop`): C1 (operability) and C2 (depth) verify; C3 (calibration) is **not verified** —
its stated sentence ("every disclosure the lane repeats … matches the bytes beside it") is falsified by
the round's own probe ceiling comment and by S618's `teaches` cell, while the frozen C3 counter stays green
because it *requires* the falsified string.

## Step-1 conformance

- Report committed in the fleet repo by lane identity: `git log --format='%an %H' -- .ufo/reports/round-96/kama.md`
  → `kama-shokunin 491748d7e3c1a0f76a0ca29cfcd745e1a4539ad4` (correction, committer 07:31:13) and
  `kama-shokunin 8956d193d8a8991f6087ddf5a99263aa6029370d` (filing, committer 07:29:46). Committer time of
  the last report commit (07:31:13) is after the lane tip `49ef853f` (07:31:04): report lands last. ✓
- `## SHONEN` heading present with four `[~]` lines and pointers. ✓ — but the four lines are **not** the
  four `SHONEN.md` boxes (see defects).
- Every cited lane commit exists as a git object and is an ancestor of `master`: `58001b71`, `e2fed9f5`,
  `bbdfc930`, `fb5cd3cd`, `4a0f6a35`, `b3289c18`, `20317286`, `bb4a997a`, `f175a902`, `f3fd922e`,
  `f6122036`, `49ef853f` plus base `5d43528b` — `git -C kama-shokunin merge-base --is-ancestor <h> master`
  → OK 13/13. ✓
- Lane repo clean and pushed: `scripts/hyaku/jj-lane.sh state kama-shokunin` →
  `branch=master local=49ef853f remote=49ef853f ahead=0 behind=0 head=attached tracked=0 untracked=0`;
  `git status --porcelain` → empty. ✓
- Report is real work (127 tracked files under `.ufo/waves/round-96/`, three counters, six amendments,
  12-seat wave), not a marker. ✓
- Dispatched prompt `/home/vgpnk/Projects/shokunin/.ufo/prompts/kama-round-96.md` (989 lines) carries the
  template contract: claims/axes binding (line 11), L2 floor "at least 8 … in ONE batched AgentSwarm call"
  (lines 80–83, matching `MISSION.md` §L2), report path and required sections (lines 100–120), commit-then-
  push and push scope (lines 131–137), L0 side channel (line 138), report lands last and cites the pushed
  lane hash (line 516), write scope (line 448), plus the hyaku addendum §6. ✓
- Driver digest (copied from `.ufo/watchdog.log`, mutable):
  `2026-11-08T03:31:09-03:00 launch kama round=96 pgid=3180701 driver=hyaku-inline attempt=1`;
  `2026-11-08T07:31:25-03:00 complete kama round=96; hyaku-inline attempt=1`.

Conformance defects (status-neutral; none is the admission failure):
1. **`SHONEN` lines are not the boxes.** `SHONEN.md` has four boxes (decision tables/error patterns/
   checklists/cited sources; one end-to-end task logged; executable without oral context; no cross-domain
   bleed). The report's four lines instead assert counting-command discipline, wave floor, frontier step and
   "verification pending" — no line assesses a box. Protocol consequence: a conformance defect **and** the
   assessment is disqualified as evidence in the promotion review; it must be re-filed under the heading in
   the round-97 report.
2. **Filed report bytes were rewritten in place.** `git show 491748d -- .ufo/reports/round-96/kama.md` is a
   3-insertion/2-deletion edit of the filed header and Landed table. The protocol requires a correction to a
   filed report to land as an erratum appended after the filed bytes, never a rewrite.
3. **Seat enumeration is 11 of 12.** `w1-results.json` has 12 seats (RV01, RV02, CR01, CR02, MT01, SN01,
   SC01, SC02, EX01, EX02, CN01, SB01); the report's "5 attack (RV01, CR01, CR02, MT01, SN01), 1 connector,
   2 scouts, 2 executors, 1 scribe" omits RV02, and LOG.md repeats the same 11-name enumeration.
4. **LOG entry naming.** `LOG.md` carries one `## round 96` section whose heading still says "frozen;
   evidence pending measurement" though measurements landed in `f6122036`; the report's Landed-changes
   "LOG.md entry" column names three distinct entries (freeze / wave-findings / measurements) that do not
   exist as sections.
5. **Stale identity wording after amendment 6.** Amendment 5 binds C1's counter bytes to `b3289c18`
   ("unchanged by 4 and 5"); amendment 6 (`f175a902`) then changed the counter and restated only the
   predicate, not the identity revision. The counter docstrings still say "the counter's bytes identical to
   this freeze commit" (`tools/round96-router-budget.py:7-8`, `round96-disclosure-audit.py:8`).
6. **Prefile ledger coverage.** The ledger is structurally green (below) but files no row for the C3 × RV01
   F2 wording falsification it could have filed; coverage is per claim, not per claim-finding pair, so the
   gap passes the gate.

## Prefile falsification (step 2b)

`python3 /home/vgpnk/Projects/shokunin/scripts/hyaku/prefile-falsification.py --lane kama --round 96` →
`PREFILE-FALSIFICATION: pass claims=3 rows=11 attack_seats=7 findings=0`, exit 0. Ledger covers C1, C2, C3;
reads all seven attack-role seats (RV01, RV02, CR01, CR02, MT01, SN01, CN01); every `falsifies-wording` row
names a resolving narrowing (`plans/round-96-amendment-{2,3,4,5,6}.md`). No failing row to adjudicate.
Adjudication of the falsification the ledger does **not** file: **real and unreconciled** — see C3.

## Claims (step 2)

### C1 — operability: the step budget decides 700 000-tensor files; the instrument cannot pass without load evidence or without the cap being load-bearing

**Verified (evidence-verified; not re-executed).** I did not run the 13-cell counter: it needs 96 slow
fixtures, a private scratch and two host-load passes (the host incident in the prompt records leaked
burners from exactly this counter), and `PROTOCOL.md` §Gate standard tells the integrator to verify committed
evidence rather than execute a sibling instrument. Re-derived independently:

- `git show 5d43528b:tools/kama-probe.sh | grep -n 'MAX_STEPS = '` → `575:MAX_STEPS = 4_000_000`;
  `git show 49ef853f:tools/kama-probe.sh | grep -n 'MAX_STEPS = '` → `581:MAX_STEPS = 5_000_000`. Probe
  digests: base `sha256 b49d961a0548…` (`git show 5d43528b:tools/kama-probe.sh | sha256sum`), tip
  `11e5b01b8d01…` — both quoted in the receipts' `probe_sha256=` field, so each receipt is bound to the
  revision it claims.
- Receipt `.ufo/waves/round-96/measured/c1.out` (27 lines, tail): `ROUTER_BUDGET96 cells=13 mismatches=0
  positive_mismatches=0 load_cells=13 load_stable=1 budget=work probe=rev probe_sha256=11e5b01b… rev=f175a902
  w03_seconds=161.4 load1_nat=9.44`; W13-budget-kill `ok=1` on both passes.
- Control `.ufo/waves/round-96/controls/c1-base.out` (27 lines, tail): `cells=13 mismatches=1
  positive_mismatches=1 load_cells=13 load_stable=1 probe_sha256=b49d961a… rev=5d43528b w03_seconds=46.3`;
  W11-700k `ok=0` with `MODEL_OK/router-unloaded-autoload` on both passes — the false green is in the
  committed bytes, and it is the only mismatched cell.
- Counter bytes at the measured revision equal the tip: `git show f175a902:tools/round96-router-budget.py |
  sha256sum` = `sha256sum tools/round96-router-budget.py` = `6c5579a999fad82c…` (identity to `f175a902`).
- Load-evidence guard is structural: `--skip-load` prints `… load_skipped=true load_cells=0 load_stable=0
  (no second pass ran; predicate unreachable)` and `return 1` (`round96-router-budget.py:472-477`); the pass
  requires `mismatches == 0 and load_stable == 1 and len(cids) == CELLS` (:508).
- Cap-load-bearing: the W13 cell and its fixture exist in the counter (`:187-216`, `:325-333`, `:367`) and
  grade green only with the cap in place; amendment 6 records the capped `MODEL_OK` vs uncapped
  `MODEL_UNLOADED` measurement, and MT01's mutant runs are committed under `w1/out/MT01ProbeMutants/`.
- Arithmetic: `4 + 6 × 700 000 = 4 200 004` steps — ≤ 5 000 000 (decides at the tip) and > 4 000 000
  (undecidable → `-` → loadable at base). Matches the control and the receipt.

**Grade: improved.** Wording limit, named not claimed: "a 700 000-tensor file … decides at 5 000 000" is
true for the nd = 1 fixture only; at nd ≥ 3 it stays `-` (the round's own SKILL correction says so).

### C2 — depth: the step-cost table states the arithmetic the parser enforces

**Re-measured by this closure** (read-only over committed bytes; no probe run):

```
$ python3 tools/round96-depth-audit.py --repo . --rev 5d43528b
DEPTH_AUDIT checks=14 mismatches=14 met=False          # exit 1
$ python3 tools/round96-depth-audit.py --repo . --rev 20317286
DEPTH_AUDIT checks=14 mismatches=0 met=True            # exit 0
```

Counter identity: `git show 20317286:tools/round96-depth-audit.py | sha256sum` = tip =
`7929628ca37d29b7…`. Independent hand derivation from `tools/kama-probe.sh:748-758` (one `need()` per
bounded read/seek): name `u64` + `skip` = 2, `nd` `u32` = 1, `nd` × `u64` dims = nd, type `u32` + offset
`u64` = 2 → **5 + nd** steps/header; preamble (`:736-740`) = 4 steps. Ceilings `(5 000 000 − 4) // (5 + nd)`
= 999 999 / 833 332 / 714 285 / 624 999 / 555 555, byte-identical to the five rows of `SKILL.md` §Round 96
correction. **Grade: improved.**

### C3 — calibration: every disclosure the lane repeats matches the bytes beside it

**Not verified.** Re-ran the counter (it discriminates base from tip):

```
$ python3 tools/round96-disclosure-audit.py --repo . --rev 5d43528b
DISCLOSURE_AUDIT checks=6 mismatches=3 met=False       # exit 1
$ python3 tools/round96-disclosure-audit.py --repo . --rev 20317286
DISCLOSURE_AUDIT checks=6 mismatches=0 met=True        # exit 0
```

Counter identity: `git show 20317286:tools/round96-disclosure-audit.py | sha256sum` = tip =
`72bd4550df2630a3…`. Two of the three named items hold: the counter docstring states `20 + 25 * npaths`
(shell literal at `tools/kama-probe.sh:871`), and the `router-byte-decided` pointer `c810f51e` resolves and
precedes the tip.

The claim does not hold at its stated width. The audit's check (1) is
`if max_steps != 5_000_000 or "6 steps per tensor header" not in probe: mismatches += 1`
(`round96-disclosure-audit.py:57-60`) — the instrument is green **because** the falsified sentence is
present. At the closed tip:

- `tools/kama-probe.sh:575-577` states "The binding ceiling is 6 steps per tensor header … so MAX_STEPS =
  5 000 000 puts the ceiling at ~833 333 tensor headers."
- The parser prices `5 + nd` (above); at nd = 4 the ceiling is 555 555, 33 % lower.
- The round's own `SKILL.md` §Round 96 correction says "Six steps is the `nd = 1` case only" and lists the
  per-rank ceilings.
- `corpus/SOURCES.md` S618 (written this round, status mined) repeats it: "… so 6 read/seek steps per header
  is the budget against which MAX_STEPS is sized".

Wave artifact RV01 F2 states the falsification in the round's own ledger ("the per-header cost is `5 + nd`,
not a constant 6"); its narrowing, amendment 2, repaired `SKILL.md` and the depth counter and left the probe
comment and S618's `teaches` cell untouched. No amendment narrows C3 to exclude the probe's ceiling comment
(amendment 5 restates only the identity clause). A 700 000-header nd = 4 file is exactly the class the claim
says the comment now describes: it costs 6 300 004 steps, is undecidable → loadable, i.e. the false green C1
closed at nd = 1. **Grade: unchanged** (the instrument is real and discriminates literal presence; the
claimed universal is false).

### Per-axis verdicts

| Axis | Verdict | Evidence |
|---|---|---|
| operability | improved | C1: `measured/c1.out` `cells=13 mismatches=0` at `f175a902`; base control `mismatches=1` W11-700k false green; probe digest identity; `--skip-load` structurally unable to pass |
| depth | improved | C2: `DEPTH_AUDIT checks=14 mismatches=0 met=True` re-run at `20317286`; 14/14 at base; 5 + nd and all five ceilings re-derived by hand |
| calibration | unchanged | C3 not verified: probe ceiling comment and S618 `teaches` restate constant 6 while the parser prices 5 + nd; counter green because it requires that string |
| freshness | unchanged | no claim; `SCORECARD.md` axis table unchanged (`git diff 5d43528b 49ef853f -- SCORECARD.md` moves no score) |
| coverage | unchanged | no claim; no new governed surface (`corpus/README.md` untouched) |
| adjacency | unchanged | no claim; CN01's 20-lane scan is read-only and reports no new contested scope |

No owned axis is harmed: no score moves, and the two verified claims replace instruments that graded
outcomes without grading the mechanism.

## Discernment spot-check (LEARNING.md) — `corpus/lessons/round-96.md` `## Gate`

| Item | Decision | Re-opened source | Agree/disagree | Reason |
|---|---|---|---|---|
| S618 `ggml/include/ggml.h` @ b12177 | admit (A, code, mined) | `curl https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/ggml/include/ggml.h` | **agree** on the admit; **disagree** with the row's `teaches` arithmetic | Digest `sha256 590e00a5…67392` matches the row; line 697 is `// nb[0] = ggml_type_size(type)` verbatim and line 694 `int64_t ne[GGML_MAX_DIMS];` confirms the per-rank descriptor. But `teaches` says "6 read/seek steps per header", the constant this round's table corrects |
| S619 `gguf-py/README.md` @ b12177 | reject (docs, C-class lead) | `curl https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/gguf-py/README.md` | **agree** | Digest `f759ed01…18af` matches; the quoted sentence is verbatim but spans lines 3–4 (the row says "line 3"); the page is a Python writer's README and grounds no header cost — flip condition (states field order/widths) is the right one |
| `ggml/src/gguf.cpp` as a new row | reject (duplicate of S129) | `corpus/SOURCES.md` + census | **agree** | `scripts/sources-census.sh validate` prints `W04 S129 duplicate url … ggml/src/gguf.cpp`; S129 is the existing registry row for that URL |

Census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
→ `kama ok …` exit 0 (pre-existing W04 duplicate-URL warnings and W01 S481 only). Rows
357 → 358 (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` at `5d43528b` → 357, at
tip → 358); malformed rows `awk … NF!=13` → 0; duplicate ids → empty.

## Trends

- **expansion: unchanged** — one A/code row (S618) deepened a surface the probe already parses; no admitted
  `knowledge/` entry and no new covered surface. Matches the report.
- **quality: improved** — C1 replaced a budget that left 700 000-tensor files loadable and an instrument
  that could not be shown to require load evidence; C2 replaced a table that stated the `MAX_TENSORS`
  constant as the ceiling with the arithmetic the parser enforces. Both re-derived above; no entry found
  false and left unmarked on the claimed axes.
- **discernment: improved** — the gate decisions sampled above are 3/3 agree; the round's own wave found six
  filings and one instrument gap and the repairs are recorded with red controls (amendments 1–6, W13).

## Routed defects for round 97 (lane must answer next round)

1. **C3's named disclosure is false.** Correct `tools/kama-probe.sh:575-577` and S618's `teaches` cell to
   `5 + nd` (or qualify the sentence as the nd = 1 case and name the per-rank ceilings). Then remove the
   disclosure audit's requirement for the literal "6 steps per tensor header" (check 1) so the instrument
   grades the binding claim instead of the string — the round's own CR02 B2–B5 item.
2. **Re-file the `SHONEN` assessment** under `## SHONEN` with exactly one line per `SHONEN.md` box; the
   round-96 lines do not assess the boxes and are disqualified as promotion evidence (protocol
   consequence).
3. **Restate C1's identity revision.** Amendment 5 binds `round96-router-budget.py` to `b3289c18`, which
   amendment 6 invalidated; bind it to `f175a902`, and refresh the two counter docstrings that still say
   "identical to this freeze commit" after the counters were amended.
4. **Report-correction discipline.** Corrections to a filed report land as an appended erratum naming the
   superseded text; `491748d` rewrote filed bytes.
5. **Seat accounting and LOG naming.** Record 12 seats (RV02 missing from the report's and LOG's 11-name
   enumeration) and retitle or append the LOG round-96 entry so its heading no longer says "evidence
   pending measurement" after `f6122036` landed the measurements.
6. **Prefile ledger width.** When a wave artifact falsifies a claim's wording, file the row against every
   claim whose sentence it falsifies (here C3 × RV01 F2), not only the claim whose counter moved; coverage
   is currently per claim and misses this class.
7. **Carried, unchanged:** MT01 G2 (a cell between the 833 332-header ceiling and `MAX_TENSORS`), MT01
   G3/G4 (`MAX_META`, ctime), r94 SC02 F4 (slow `/props`), CR02 B2–B5, SC01's staged held-out listings,
   `round75-instruments` `APPEND_DEBT bad_rows=19`, and the non-lane Ollama listener on 127.0.0.1:8080.

## SHONEN note for the operator

Promotion is operator-owned and was not exercised. The lane's four `SHONEN.md` boxes remain `[~]`; as of
this closure boxes 1–3 have named non-author evidence available in this spot-check and the round records
(same-axis counters with red controls, an executed end-to-end probe task, commands that re-run from the
plan text), but no non-author has written `[x]` and I did not write one. The round-96 report's `SHONEN`
lines cannot carry a box mark: they do not address the boxes.
