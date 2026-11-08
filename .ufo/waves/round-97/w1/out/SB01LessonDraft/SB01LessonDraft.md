# SB01LessonDraft — round-97 prose draft (lesson §Gate / §Mistakes, report §Sources & frontier, §Before → after)

Seat: `SB01LessonDraft` (scribe, read-only; no tracked lane file touched, nothing committed).
Lane: `kama-shokunin`, repo `/home/vgpnk/Projects/shokunin/kama-shokunin`.
Base `40763bd2ca1e3f99881247eaa9f5e3ef3b596653` (round-96 closure `rejected-honest-stop`); freeze `9e605d41`;
amendment 1 `e057166e` (C2 host-speed parameter `--slow-files 72`).

**Status.** This is a **draft of prose**, not a claim. Every number below was measured by this seat
against the named bytes; every figure the L1 has not measured yet is left as a `<<measured:…>>`
placeholder. The L1 integrates; the L1's own receipts, not mine, are the evidence of record.

**Sources read (committed bytes only):** `plans/round-97-claims.md`,
`plans/round-97-amendment-1.md`, `corpus/lessons/round-97.md` (the L1's current draft),
`corpus/lessons/round-96-verifier-spotcheck.md`, `corpus/SOURCES.md`, `corpus/QUALITY.md`,
`SKILL.md`, `SCORECARD.md`, `tools/kama-probe.sh`, the three round-97 counters,
`.ufo/waves/round-97/controls/*.out`, `.ufo/waves/round-97/measured/*.out`,
`.ufo/waves/round-97/claims.json`, and the fleet report skeleton
`/home/vgpnk/Projects/shokunin/.ufo/reports/round-97/kama.md` (read-only).

---

## 0. Findings the L1 must weigh before integrating this draft

These are the places where the committed bytes disagree with each other or with a frozen sentence.
Each names the file:line and the command that shows it. None is a change this seat can make — the
plan and its counters are frozen, and the lesson is the L1's to land.

### F1 — the frozen C2 predicate says "three new cells"; the counter grades four.

`plans/round-97-claims.md:76-77` states the control receipts print `caught=1` "for the three new
cells, one per mutant", and `plans/round-97-claims.md:70` names C2 as "four probe forgeries".
The counter's own cell table has **four** new cells:

```
$ grep -n "NEW_CELLS" tools/round97-router-budget.py
146:NEW_CELLS = {"W14-900k-nd1", "W15-700k-nd4", "W16-maxmeta", "W17-833333-nd1"}
```

and the committed control receipt prints `cells=4` for every new-cell block
(`.ufo/waves/round-97/controls/c2-new-mutants.out:6,13,20,27,34`). The counter's own docstring
says "Round 97 adds **three** cells past that:" and then lists four (`tools/round97-router-budget.py:13-26`).
`CELLS = 17` (`tools/round97-router-budget.py:142`) is consistent with 13 + 4.

So "three" in the frozen predicate sentence and in the counter docstring is a **stale count**; the
substance (17 cells, four new cells, four mutants each caught once) is what the receipts show.
The plan is frozen and this seat cannot edit it; the L1's report prose must use the measured
numbers (17 / four / four) and the lesson must not repeat "three". Note the C1 counter does **not**
grade the plan or the counter docstring, so no frozen instrument catches this drift — it is exactly
the "disclosed constant disagrees with the code" class the round's own C1 claim names.

### F2 — `SKILL.md` §Round 97 correction names three graded forgeries; the counter grades four.

```
$ grep -n "three probe variants\|grades each with W14" SKILL.md
2463:receipt does not prove this arithmetic is enforced: three probe variants survive all 13 of its
2467:round-97 counter `tools/round97-router-budget.py` grades each with W14, W15 and W16
```

`SKILL.md:2463-2467` lists three variants (per-header charging stopped, constant 6 steps/header,
`MAX_META` 100 MiB) and maps them to W14/W15/W16. The counter's fourth mutant — `nopreamble`
(`tools/round97-router-budget.py:174-175`), caught by W17 — is not mentioned. The C3 counter grades
only the six boundary rows and the C1 counter only the 14 named surfaces, so neither grades this
sentence. The section is otherwise correct (I re-derived all six rows; see §3 below).

### F3 — the lesson's M2 evidence points at a byte string that exists nowhere in the tree.

`corpus/lessons/round-97.md:44` cites "the first `maxmeta.gguf` wrote the KV value as
`struct.pack("<II", 8, 0)`". That literal appears nowhere in the lane except in the lesson itself:

```
$ grep -rn 'pack("<II", 8, 0)' . | grep -v '^\./\.git'
./corpus/lessons/round-97.md:44
```

The counter's *committed* fixture writes `struct.pack("<I", 8)` for the value type and then
`struct.pack("<Q", payload_len)` for the length (`tools/round97-router-budget.py:253-254`) — i.e.
the tree already carries the **fixed** bytes. There is no committed receipt showing the pre-fix
`caught=0` state either; the only `caught=0` receipts in the tree are the legacy-set survivals and
the real-probe survival (`controls/c2-legacy-mutants.out:15,31,47,63`,
`controls/c2-new-mutants.out:6`). M2's "shown able to fail" therefore has no committed red side.
That does not falsify the defect — the L1 found it while authoring the counter, before the freeze —
but the lesson cannot cite a byte string the tree does not contain as its evidence pointer. The
committed, citable statement of the same defect is the **fixture's own comment**
(`tools/round97-router-budget.py:244-249`) and the mutant control's current behaviour
(`controls/c2-new-mutants.out:27`, `mutant=maxmeta … caught=1`).

### F4 — the lesson's M3 fix names a file that does not exist yet.

`corpus/lessons/round-97.md:51-56` says "this round's `claim-falsification.tsv` names, for every
attack seat, the claim(s) its artifact attacks". That file is absent:

```
$ ls .ufo/waves/round-97/claim-falsification.tsv
ls: cannot access '...': No such file or directory
$ python3 /home/vgpnk/Projects/shokunin/scripts/hyaku/prefile-falsification.py --lane kama --round 97
FINDING wave-missing .../.ufo/waves/round-97/w1-results.json
FINDING ledger-missing .../.ufo/waves/round-97/claim-falsification.tsv
PREFILE-FALSIFICATION: SETUP findings=2      # exit 2
```

Both the ledger and the wave results file are still to be written by the L1. The lesson's M3 must
be written as a fix **to be landed**, and the lesson cannot yet claim the file exists.

### F5 — `## Mistakes` M4's "captured-by" pointer is a plan reference, not a wave seat.

`corpus/lessons/round-97.md:58-62` names "the round-96 closure step 1 (report contract)" as the
capturing party for M4. That is true of the *defect's origin* (the round-96 spot-check's
conformance defect 1, `corpus/lessons/round-96-verifier-spotcheck.md:39-44`), but the round-97
lesson's M4 is a **restatement of a routed defect**, not a defect this round's wave caught. The
routed-defect section of the lesson already carries it (`corpus/lessons/round-97.md:68-76`). As
drafted, M4 duplicates that section and reads as if wave-1 caught it. The plan is explicit that
round 97 closes routed defects 1, 2, 3, 6 and keeps 4/5/7 disclosed
(`plans/round-97-claims.md:11-14`). Recommend M4 be dropped from `## Mistakes` and kept only
in `## Routed-defect answers`, so the Mistakes list holds only what this round's own work caught.

### F6 — the fleet report skeleton still carries the two placeholders this draft fills.

`/home/vgpnk/Projects/shokunin/.ufo/reports/round-97/kama.md:43` is `<<measurements>>` and
`:75` is `<<shonen>>`; the report also has `<<freeze>>`, `<<wavecommit>>`, `<<seats>>`,
`<<measurecommit>>` unfilled. §2 and §3 below are written to drop into `<<measurements>>` and to
supply the two Sources & frontier facts.

### F7 — the plan's §2b counts the lesson's Gate as three rows; the lesson's Gate has four.

`plans/round-97-claims.md:138-139` says the lesson carries "`## Gate` (one admit, two rejects,
every new row's URL/access date/quote)". The committed lesson's Gate table
(`corpus/lessons/round-97.md:15-18`) has **four** rows: two admits (S620, S621), one registry
reject (S619) and one path-absent reject (`llama.cpp` `docs/gguf.md` @ b12177, HTTP 404 — no
registry row). Under the plan's own reading of the registry delta ("S619 rejected, S620 admitted,
S621 correction of S618", `plans/round-97-claims.md:137`) the four rows are one admit, one
append-only correction, and two rejects — the same four rows, counted differently. The §Gate table
this draft proposes keeps all four rows and labels S621 as an admit of a **correction** row, so the
lesson states four rows where the plan says three. The L1 should either amend the plan's count or
word the lesson so the two agree; this seat cannot edit the frozen plan.

---

## 1. `corpus/lessons/round-97.md` §Gate — rewritten table

Every row was opened this round (2026-11-08) and re-fetched by this seat; the digests below were
recomputed from the fetched bytes and match `controls/sources-opened.out` exactly
(receipt `receipts/sources-opened-recheck.txt`). Quotes are located in the fetched bytes and are
≤25 words each.

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S620 GGUF specification `docs/gguf.md` @ ggml `57e2c2ca` | **admit** (A, spec, mined) | https://raw.githubusercontent.com/ggml-org/ggml/57e2c2ca2a7cae756b1c4dfafa0cdfef9051d234/docs/gguf.md — 2026-11-08, sha256 `1dead27b6a522709f0127d194e58c21dbbbf00ba1c64fe37c54d1a9048b05020` (43 175 B) | "uint64_t dimensions[n_dimensions];" (line 313; "Currently at most 4" line 310) | The tensor-info struct is five fields — `name`, `n_dimensions`, `dimensions[n_dimensions]`, `type`, `offset` (lines 305-325) — with one dimension entry per rank, which is why a header costs `5 + nd` reads and why the ceiling is per rank, not a constant. |
| S621 `ggml/include/ggml.h` @ b12177, corrected reading of S618 | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/ggml/include/ggml.h — 2026-11-08, sha256 `590e00a522b8791235353a8c7388d67ff2fe929554f1834c58528b82afd67392` (119 369 B) | "nb[0] = ggml_type_size(type)" (line 697; "int64_t ne[GGML_MAX_DIMS];" line 695) | Supersedes S618's `teaches` cell, which stated "6 read/seek steps per header": `ne` is one element count per rank, so the cost is `5 + nd`. S618's anchor "line 690" was the struct header (`struct ggml_tensor {`); the fields are at 695-697. |
| S619 `gguf-py/README.md` @ b12177 | **reject** (docs, C-class lead only) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/gguf-py/README.md — 2026-11-08, sha256 `f759ed01b8899c392cee7f1bc9012356090dd46014898c2cface1cca5f1e18af` (3 339 B) | "This is a Python package for writing binary files in the [GGUF](https://github.com/ggml-org/ggml/pull/302)" (lines 3-4) | The page documents the Python writer, not the file layout the probe parses; it grounds no step cost. Flip: the page states the header field order and widths. |
| `llama.cpp` `docs/gguf.md` @ b12177 | **reject** (path absent) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/docs/gguf.md — 2026-11-08 | HTTP 404 (14 B body, sha256 `d5558cd419c8d46bdc958064cb97f963d1ea793866414c025906ec15033512ed`) | The spec moved to the ggml repository; S620 is the live location. Flip: a llama.cpp `docs/gguf.md` appears at a pinned tag. |

**Registry changes:** S619 (rejected row, replacing round 96's prose-only rejection), S620 (admit),
S621 (append-only correction of S618). No existing row's `status`/`recheck`/`used-by` changed; S618
stays `mined` as history and S621's `teaches` opens `supersedes S618 —` (CORPUS.md rule 2).
Measured: `git diff 40763bd2 HEAD -- corpus/SOURCES.md` is `3` insertions and `0` deletions, and the
S618 row is byte-identical between the two revisions (`diff` of the two `grep '^| S618'` extracts is
empty). The census reports the two new rows as W04 "duplicate url across scopes" warnings — S620
shares S586's URL, S621 shares S618's — which are warnings only; `validate` still exits 0.

**Census before → after: 358 → 361 rows.** Counting command:
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
→ `kama ok …`, **exit 0** at round start (`controls/census-start.out`) and at round end
(`controls/census-end.out`); tier counts measured with `census --root … kama` (361 rows: tier.A 344,
tier.B 11, tier.C 6; mined 324, queued 8, rejected 29) against the base blob (358 rows: tier.A 342,
tier.B 11, tier.C 5; mined 322, queued 8, rejected 28).

**Assimilation:** none — `considerthese/2026-11-07.md` proposal 3 (a file-identity memo is not frozen
without a mutation-control receipt) is mined as QUALITY KQ152 below, not as a package row; no
`merge/kama/` theme was adopted.

---

## 2. `corpus/lessons/round-97.md` §Mistakes — rewritten rows

Each row is `class · evidence · captured-by · fix · shown able to fail`, with the evidence pointer
resolved to a committed file:line by this seat. The **shown able to fail** column is the part that
must not be a promise; each pointer below is a receipt or a counter run that exists.

**M1 — the C3 counter required the false sentence it was supposed to catch.**
Class: `number-drift`. Evidence: `corpus/lessons/round-96-verifier-spotcheck.md:140-143` ("The
audit's check (1) is `if max_steps != 5_000_000 or "6 steps per tensor header" not in probe:
mismatches += 1` … the instrument is green **because** the falsified sentence is present") and
`tools/round96-disclosure-audit.py:51` — that literal is the string the counter *requires*, so the
green receipt is earned by the false disclosure. Captured-by: the round-96 closure spot-check
(non-author), not the round's own counter — the counter's check was written to agree with the
disclosure it was auditing. Fix: `tools/round97-self-assessment-audit.py` derives every ceiling
from `MAX_STEPS` and the rank (`:140-153`) and rejects the constant-6 sentence outright (`:143`).
Shown able to fail: at base `40763bd2` the counter prints `SELF_ASSESS97 checks=14 mismatches=9
met=False` and exits 1 (`controls/c1-base.out`; re-run by this seat, receipt
`receipts/counter-runs.txt`), and the nine mismatches are exactly the stale surfaces — depth-row
digest/line-count/section-count (`:100-109`), the capability pointer (`:129-137`), the probe's
`5 + nd` sentence (`:142-144`), the probe's per-rank ceilings (`:145-153`), SKILL's ceilings and
S620/S621 citations (`:156-164`), and the S621/S620 rows (`:169-184`); the base/head per-check
traces are `receipts/base_trace.txt` and `receipts/head_trace.txt`.

**M2 — a fixture that could not grade its own design, found by the mutant control.**
Class: `vacuous`. Evidence: the `maxmeta` fixture's committed writer
(`tools/round97-router-budget.py:243-260`) writes the GGUF string value as **type `u32` then `u64`
length** (`:253-254`); a GGUF string carries no element-type field, so a length read that lands one
field early reads the wrong offset, and the probe then grades the file at the size guard instead of
the position guard the cell is meant to grade — a cell whose expectation the fixture bytes cannot
reach. Captured-by: the counter's own `--control --expect caught` mutant run (it refused to
agree). Fix: the two-field KV encoding above; the mutant now prints `caught=1` and the real probe
prints `survived=1` on the same four cells (`controls/c2-new-mutants.out:6` and `:27`).
Shown able to fail: `controls/c2-new-mutants.out:27` — `mutant=maxmeta … caught=1`, `cells_ok=3`
— versus the same receipt's real-probe block at `:6`, `mutant=none … survived=1`, `cells_ok=4`;
the control's own exit-code rule (`tools/round97-router-budget.py:625-630`, `ok = survived if
expect == "survived" else caught`) turns `caught=0` into a non-zero exit, so a fixture that cannot
discriminate fails the control rather than passing it quietly.
**Note for the L1 (finding F3):** the pre-fix byte string `struct.pack("<II", 8, 0)` that the
current lesson text cites is **not in the tree**; cite the committed writer and the receipt pair
above instead, and do not assert a pre-fix red receipt that does not exist.

**M3 — the prefile ledger's coverage was per claim, not per claim-finding pair.**
Class: `vacuous`. Evidence: `corpus/lessons/round-96-verifier-spotcheck.md:59-61` — "the ledger is
structurally green (below) but files no row for the C3 × RV01 F2 wording falsification it could have
filed; coverage is per claim, not per claim-finding pair, so the gap passes the gate" — and the
gate's own rules (`/home/vgpnk/Projects/shokunin/scripts/hyaku/prefile-falsification.py:29-33`:
one row per (claim, artifact); `claim-uncovered`, `attack-seat-unread`, `narrowing-missing`).
Captured-by: the round-96 closure, step 2b. Fix: this round's `claim-falsification.tsv` names, for
every attack seat, the claim(s) its artifact attacks, and a `falsifies-wording` row carries a
resolving narrowing pointer. Shown able to fail: the gate refuses to run on a missing or thin
ledger — this seat ran it and got `FINDING wave-missing …/w1-results.json`,
`FINDING ledger-missing …/claim-falsification.tsv`, `PREFILE-FALSIFICATION: SETUP findings=2`,
exit 2 — and the same gate passed round 96 at `claims=3 rows=11 attack_seats=7 findings=0`
(`corpus/lessons/round-96-verifier-spotcheck.md:65-67`).
**Note for the L1 (finding F4):** neither file exists yet; write M3 as a fix to be landed, not as a
landed state.

**M4 — dropped from `## Mistakes` (see finding F5).** The `SHONEN` re-filing is a round-96 routed
defect, not a defect this round's wave caught; it is already answered in the lesson's
`## Routed-defect answers` (`corpus/lessons/round-97.md:68-76`). Keeping it in `## Mistakes` with
"captured-by: the round-96 closure" misattributes it to wave-1. The plan's own routing table lists
it as routed defect 2, to be closed *in the report* (`plans/round-97-claims.md:8-11`), which is
where this seat's §4 below belongs.

---

## 3. Report `## Before → after measurements` — draft for the `<<measurements>>` placeholder

Every number the L1 has measured is quoted from the receipt that carries it; every number it has
not measured yet is a `<<measured:…>>` placeholder. Nothing here is a guess.

### C1 — calibration

Counting command:
`python3 tools/round97-self-assessment-audit.py --repo . --rev <M1>`.

- **Before** (`controls/c1-base.out`, at base `40763bd2`): `SELF_ASSESS97 checks=14 mismatches=9
  met=False`, exit 1. Re-run by this seat at `40763bd2`: identical (`receipts/counter-runs.txt`).
  The nine mismatches are the nine stale surfaces listed under M1 above.
- **After** (`measured/c1.out`): `<<measured:SELF_ASSESS97 checks=14 mismatches=0 met=True>>`,
  exit `<<measured:exit>>`. The receipt at the time of this draft already carries
  `SELF_ASSESS97 checks=14 mismatches=0 met=True` / `c1_exit=0`
  (`.ufo/waves/round-97/measured/c1.out`, uncommitted) — re-quote it after the L1's measurement
  commit is fixed, since the counter grades a named `--rev`.
- The counter's red control is the base run above; the do-nothing reading is in the plan
  (`plans/round-97-claims.md:53-59`).

### C2 — operability

Counting command (amended, per `plans/round-97-amendment-1.md`):
`python3 tools/round97-router-budget.py --repo . --rev <M2> --work <scratch> --slow-files 72`.

- **Before** (`controls/c2-legacy-mutants.out`, the 13 round-96 cells): each of the four mutants
  survives the whole legacy set — `flat6` `:15`, `undercharge` `:31`, `maxmeta` `:47`,
  `nopreamble` `:63`, each `cells=13 cells_ok=13 survived=1 caught=0 ok=1`. The old set cannot
  discriminate any of the four.
- **The amended predicate's own red state** (`controls/c2-could-not-evaluate.out`, committed with
  amendment 1 `e057166e`): the frozen command at the freeze commit exited **2**, not 0/1, with
  `ROUTER_BUDGET97 could-not-evaluate: W03 natural pass 55.0s < 1.25 x 60s — the round-94 constant
  wrapper would not truncate this listing on this host, so no discriminator is claimed`. No cell was
  scored. Amendment 1 adds the declared host-speed parameter `--slow-files 72` and changes nothing
  else.
- **After** (`measured/c2.out`): `<<measured:ROUTER_BUDGET97 cells=17 mismatches=0
  positive_mismatches=0 load_cells=17 load_stable=1 budget=work …>>`, exit `<<measured:exit>>`.
  The receipt at the time of this draft is empty (the L1's run is in flight), so no number is
  claimed here.
- **The four mutant receipts that must hold** (`controls/c2-new-mutants.out`): the real probe
  survives all four new cells (`:6`, `mutant=none … cells=4 cells_ok=4 survived=1`), and each
  mutant is caught exactly once — `flat6` `:13` (`cells_ok=3`, caught by W15), `undercharge` `:20`
  (`cells_ok=1`), `maxmeta` `:27` (`cells_ok=3`, caught by W16), `nopreamble` `:34` (`cells_ok=1`).
  `caught=0` on any of these voids the counter for that mutant
  (`plans/round-97-claims.md:96-98`).
- **Cell count, stated from the code**: `CELLS = 17` (`tools/round97-router-budget.py:142`),
  `LEGACY_CELLS` = 13 (`:143-145`), `NEW_CELLS` = 4 (`:146`). The frozen predicate's "three new
  cells" wording (finding F1) must not be repeated in the report.

### C3 — depth

Counting command:
`python3 tools/round97-depth-boundary-audit.py --repo . --rev <M3>`.

- **Before** (`controls/c3-base.out`, at base `40763bd2`): `DEPTH_BOUNDARY97 rows=0 mismatches=1
  met=False`, exit 1 — the section is absent, so no row is graded. Re-run by this seat at `40763bd2`:
  identical (`receipts/counter-runs.txt`).
- **After** (`measured/c3.out`): `<<measured:DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=0 met=True>>`,
  exit `<<measured:exit>>`. The receipt at the time of this draft already carries
  `DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=0 met=True` / `c3_exit=0`
  (`.ufo/waves/round-97/measured/c3.out`, uncommitted).
- **Every row recomputes from the probe's `MAX_STEPS`** — this seat re-derived all six rows from
  `MAX_STEPS = 5_000_000` (`tools/kama-probe.sh:583`) with `steps = 4 + T x (5 + nd)`, verdict
  `invalid` iff `steps <= MAX_STEPS`:

  | T | nd | steps | vs 5 000 000 | verdict | recomputed |
  |---|---|---|---|---|---|
  | 833 332 | 1 | 4 999 996 | ≤ | invalid | 4 + 833 332 × 6 = 4 999 996 ✓ |
  | 833 333 | 1 | 5 000 002 | > | - | 4 + 833 333 × 6 = 5 000 002 ✓ |
  | 900 000 | 1 | 5 400 004 | > | - | 4 + 900 000 × 6 = 5 400 004 ✓ |
  | 700 000 | 4 | 6 300 004 | > | - | 4 + 700 000 × 9 = 6 300 004 ✓ |
  | 555 555 | 4 | 4 999 999 | ≤ | invalid | 4 + 555 555 × 9 = 4 999 999 ✓ |
  | 555 556 | 4 | 5 000 008 | > | - | 4 + 555 556 × 9 = 5 000 008 ✓ |

  The table rows sit at `SKILL.md:2453-2458`; the counter's required set and re-derivation are
  `tools/round97-depth-boundary-audit.py:37-38` and `:92-113`, and it rejects a row whose stated
  steps, comparison or verdict disagrees (`:107-108`).

---

## 4. Report `## Sources & frontier` — draft paragraph

`SOURCES.md` rows before → after: **358 → 361**. Counting command:
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
→ `kama ok …`, **exit 0** at round start (`controls/census-start.out`) and at round end
(`controls/census-end.out`); tier and status counts from the same script's `census` mode.

- Rows added by tier: **2** A-tier rows — S620 (spec, ggml `57e2c2ca`, sha256 `1dead27b…`, quote
  "uint64_t dimensions[n_dimensions];" line 313) and S621 (code, `ggml.h` @ b12177, sha256
  `590e00a5…`, quote "nb[0] = ggml_type_size(type)" line 697, `teaches` opens `supersedes S618 —`);
  **1** rejected row — S619 (`gguf-py/README.md` @ b12177, docs, grounds no header cost). The
  census counts move accordingly: tier.A 342 → 344, tier.C 5 → 6, mined 322 → 324, rejected
  28 → 29.
- Rows touched old → new: none (`status`/`recheck`/`used-by` unchanged; `git diff 40763bd2 HEAD --
  corpus/SOURCES.md` is 3 insertions / 0 deletions, and the S618 row is byte-identical between the
  two revisions). S618 stays `mined` as history and S621 is the append-only correction
  (`corpus/SOURCES.md:373` and `:376`).
- Frontier rows advanced: the step-budget boundary (round-89's `-` → loadable rule) now carries the
  two rank classes with the recomputed `4 + T x (5 + nd)` arithmetic, so a reader can decide
  "does this file decide?" for a named tensor count without re-parsing `tools/kama-probe.sh`; and
  the per-header cost is now stated on a spec row (S620) rather than on a code row alone.
- Assimilation: none taken; `considerthese/2026-11-07.md` proposal 3 mined as KQ152.

---

## 5. Report `## SHONEN` — draft for the `<<shonen>>` placeholder

The round-96 closure's conformance defect 1 (`corpus/lessons/round-96-verifier-spotcheck.md:39-44`)
is that the report's `## SHONEN` lines did not assess the `SHONEN.md` boxes. The four boxes are in
`SHONEN.md`; the report must carry one `[~]` line per box, in box order, each with its evidence
pointer. Draft:

- [~] **SKILL.md contains real decision tables, error patterns, checklists, cited sources.**
  `SKILL.md` §§Decision table, Error signatures, Checklist; the round-97 correction at
  `SKILL.md:2443-2470` adds the step-budget boundary table with six recomputed rows.
- [~] **At least one end-to-end domain task executed and logged in LOG.md.**
  `LOG.md` §§round 1–3 record the executed endpoint reconciliation and invocation history; the
  round-97 entries are the freeze, the wave and the measurement entries named in §Landed changes.
- [~] **Instructions executable by an agent without oral context.**
  `SKILL.md` §Checklist and `corpus/knowledge/snapshot-history.md` §Run it; each round-97 counter
  carries its predicate and exit map in its own docstring
  (`tools/round97-self-assessment-audit.py:2-38`, `tools/round97-router-budget.py:2-122`,
  `tools/round97-depth-boundary-audit.py:2-26`).
- [~] **No cross-domain bleed (PROVINCE.md still accurate).**
  `PROVINCE.md` §Write boundary and `corpus/knowledge/cross-lane-scope.md`; this round's sources are
  three read-only fetchable documents, and no sibling lane's scope was touched.
- [~] **Non-author verification is pending, as the protocol requires.**
  No `[x]`: this report is the author's; the closure judge and its spot-check own the admit/reject.
  The wave's own non-author reads are cited where they caught the author.

(The fourth `[~]` line is the round's own addition; the protocol asks for one line per **box**,
and there are four boxes. If the L1 prefers exactly four lines, fold the verification-pending
sentence into the third line rather than adding a fifth.)

---

## 6. Receipts this seat produced

All under `.ufo/waves/round-97/w1/out/SB01LessonDraft/receipts/` (copied out of
`/fast/scratch/hyaku/kama-r97/SB01LessonDraft/`, which this seat removed on exit):

| File | What it shows |
|---|---|
| `counter-runs.txt` | C1 and C3 counters at base `40763bd2` and at freeze `9e605d41`, with exit codes |
| `base_trace.txt` | per-check trace of C1 at base: 9 mismatches over 14 checks |
| `head_trace.txt` | per-check trace of C1 at freeze: 0 mismatches over 14 checks |
| `instr_c1.py` | the instrumented copy of `tools/round97-self-assessment-audit.py` that produced the two traces (prints the source line of each `checks += 1` / `mismatches += 1`); it changes no check |
| `sources-opened-recheck.txt` | this seat's re-fetch of the three round-97 sources: HTTP 200 + sha256 for each, matching `controls/sources-opened.out` |
| `source-digests.txt` | the three recomputed sha256 digests |
| `census-head.out` | `sources-census.sh validate --root … kama` at HEAD, exit 0 (with the two new W04 warnings) |
| `census-head-counts.out` | `census` mode tier/status counts at HEAD (361 rows) |
| `census-base-counts.out` | `census` mode tier/status counts at the base blob (358 rows) |

**Tools.** No package was installed, upgraded or removed; the seat used only the toolchain already
present (`git`, `python3`, `bash`, `curl`, `grep`, `sha256sum`) — no `uv tool install`, `npx`,
`cargo install` or release binary was needed, and `pacman` was not touched (it is paused host-wide
by the orchestrator ruling of 2026-10-20). No host service was restarted and no sysctl was written.

**Bounds.** No tracked lane file was edited; the only writes were this seat's out directory and its
scratch. No `git add/commit/stash/checkout/switch/reset/pull/push` and no mutating `jj` command was
run; the only git commands used were read-only (`show`, `log`, `diff`, `rev-parse`, `status`,
`ls-files`, `merge-base` via the counter). The fleet repo was read only
(`/home/vgpnk/Projects/shokunin/.ufo/reports/round-97/kama.md` and `scripts/sources-census.sh`,
`scripts/hyaku/prefile-falsification.py`); nothing under the fleet root was written.
