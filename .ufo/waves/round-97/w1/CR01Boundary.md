# CR01Boundary — round-97 C3 (depth) boundary review

Seat: CR01Boundary, wave 1, leaf (no dispatch). Lane `kama-shokunin` at `e057166e` (HEAD).
Reviewed: `plans/round-97-claims.md` §C3, `SKILL.md:2443-2470` (§Round 97 correction),
`tools/kama-probe.sh` ROUTER_PY (`:551-805`), `tools/round97-depth-boundary-audit.py`.
C3's inputs are byte-identical to the freeze commit `9e605d41`:
`git diff 9e605d41 HEAD -- SKILL.md tools/round97-depth-boundary-audit.py tools/kama-probe.sh`
prints nothing (HEAD's only change, `e057166e`, touched C2 receipts/plan only). K1 holds.

## Bottom line

- **C3's predicate holds.** Audit at base `40763bd2` → `rows=0 mismatches=1 met=False`, exit 1;
  at freeze `9e605d41`, at `e057166e` and at `HEAD` → `rows=6 checks=8 mismatches=0 met=True`,
  exit 0.
- **All six rows recompute exactly** from `MAX_STEPS = 5,000,000` and `steps = 4 + T x (5 + nd)`.
  There is **no numeric disagreement** with the round-96 ceiling table, and rank 0 (stated in
  round 96 at `SKILL.md:2435`) extends consistently even though round 97 omits it.
- **But the section's file-level sentence is false in two classes, and two of the six named rows
  are falsified by legal GGUF metadata.** `SKILL.md:2446-2448` says "A file pays
  `4 + T x (5 + nd)` steps … `MAX_STEPS = 5,000,000` decides it (`invalid`) when that sum fits".
  The parser also charges KV work (≥4 steps per KV, 5 for a string value, `probe:733-744`) and
  refuses rank > 4 as `invalid` before pricing a header (`probe:748-750`). Demonstrated below:
  - `(T=833,332, nd=1)` + one `general.architecture`-shaped KV → **`-`**, not `invalid`
    (4,999,996 + 5 = 5,000,001); the row has only 4 steps of headroom.
  - `(T=555,555, nd=4)` + **one** KV (17 bytes) → **`-`**, not `invalid`
    (4,999,999 + 4 = 5,000,003); 1 step of headroom.
  - `(T=600,000, nd=5)`: the rule prices 6,000,004 → `-`; the probe returns **`invalid`** at
    the third header, after 7 steps.
- **The counter is blind to both.** It takes `MAX_STEPS` from the probe but hardcodes
  `PREAMBLE = 4` and `5 + nd` (`audit:35,103`), and it grades only the six `(T, nd)` rows.
  A probe patched to charge one extra step per header (6 + nd) keeps the counter green
  (`rows=6 checks=8 mismatches=0 met=True`) while turning the table's first row class into
  `-`. C3 has no mutation receipt (its only control is base-absence), unlike C1/C2.
- Verdict on the seat question: **the rows recompute from the probe's `MAX_STEPS`; the green
  does not certify the rows against the parser's price.** C3's sentence holds for the exact
  class the counter's fixtures use — KV-free header bombs at ranks 0–4 — and fails outside it.
  None of this requires abandoning the frozen predicate; all three are routed corrections.

## 1. Independent derivation from the parser (not from the plan)

`need(n)` (`probe:647-655`) adds one step per call and raises `Unknown` (→ state `-`) when
`steps > MAX_STEPS`; exactly 5,000,000 is decidable. `MAX_META` (`probe:562`) raises `Unknown`
when the header position exceeds 512 MiB (`probe:652-653`).

**Preamble = 4 steps** (one `need` per read, `probe:719,721,724`):
`rd(4)` magic 1, `u32()` version 1, `u64()` `n_tensors` 1, `u64()` `n_kv` 1.

**Per tensor header = `5 + nd` steps** (`probe:746-752`):
`skip(u64())` name length + skip = 2 (the `u64()` is one `need`, `skip` a second), `nd = u32()`
= 1, `ne = [u64() for _ in range(nd)]` = `nd`, `tt, off = u32(), u64()` = 2.

**Per KV = at least 4 steps** (`probe:733-744`): `klen = u64()` 1, key `rd`/`skip` 1,
`t = u32()` 1, `skip_value(t)` ≥ 1 (scalar = 1; `t = 8` string = `skip(u64())` + `skip` = 2;
`general.alignment` = `align = u32()` = 1). So a 17-byte u32 KV costs 4 and a
`general.architecture` string KV costs 5.

Short-circuits that pre-empt pricing: `n_kv*13 + n_tensors*24 > size` → `invalid`
(`probe:728-729`); `n_kv > MAX_KV or n_tensors > MAX_TENSORS` → `-` (`probe:730-731`);
`nd > 4` → `invalid` (`probe:749-750`); unknown tensor type → `-` (`probe:753-754`);
position > `MAX_META` at any `need` → `-`.

Therefore the parser's cost is

    steps = 4 + KVwork(>= 4 per KV) + T x (5 + nd)     and    MAX_STEPS = 5,000,000

and the section's formula is exact only for `n_kv = 0`, rank 0–4, header position ≤ 512 MiB.
The per-rank ceiling `floor((5,000,000 - 4) / (5 + nd))` is correct on that subdomain.

## 2. All six rows recomputed

`4 + T x (5 + nd)`:

| T | nd | stated | recomputed | stated comp | `<`/`>` correct? | stated verdict | budget verdict |
|---|---|---|---|---|---|---|---|
| 833,332 | 1 | 4,999,996 | 4,999,996 | `<=` | yes | invalid | decidable |
| 833,333 | 1 | 5,000,002 | 5,000,002 | `>` | yes | - | undecidable |
| 900,000 | 1 | 5,400,004 | 5,400,004 | `>` | yes | - | undecidable |
| 700,000 | 4 | 6,300,004 | 6,300,004 | `>` | yes | - | undecidable |
| 555,555 | 4 | 4,999,999 | 4,999,999 | `<=` | yes | invalid | decidable |
| 555,556 | 4 | 5,000,008 | 5,000,008 | `>` | yes | - | undecidable |

The six required pairs are present; `checks=8` = 6 rows + the S620/S621 citation check
(`SKILL.md:2468-2469`) + the literal `5,000,000` check. All rows parse under the audit's
`ROW` regex (`audit:39-41`), including the `nd=(\d)` single-digit rank.

### Audit runs (pasted)

```
$ python3 tools/round97-depth-boundary-audit.py --repo . --rev 40763bd2ca1e3f99881247eaa9f5e3ef3b596653
DEPTH_BOUNDARY97 rows=0 mismatches=1 met=False
exit=1
$ python3 tools/round97-depth-boundary-audit.py --repo . --rev 9e605d41
DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=0 met=True
exit=0
$ python3 tools/round97-depth-boundary-audit.py --repo . --rev e057166e
DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=0 met=True
exit=0
$ python3 tools/round97-depth-boundary-audit.py --repo . --rev HEAD
DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=0 met=True
exit=0
```

`controls/c3-base.out` (`rows=0 mismatches=1 met=False`, `c3_base_exit=1`) and
`measured/c3.out` (`rows=6 checks=8 mismatches=0 met=True`, `c3_exit=0`) match these bytes.

## 3. Round-96 table vs round-97 table

**Numbers agree.** `floor((5,000,000 - 4) / (5 + nd))` for the round-96 rows at
`SKILL.md:2435-2439`:

| nd | steps/header | round-96 ceiling | recomputed | agree? |
|---|---|---|---|---|
| 0 | 5 | 999,999 | 999,999 (999,999 x 5 + 4 = 4,999,999) | yes |
| 1 | 6 | 833,332 | 833,332 | yes |
| 2 | 7 | 714,285 | 714,285 (714,286 x 7 + 4 = 5,000,006) | yes |
| 3 | 8 | 624,999 | 624,999 (625,000 x 8 + 4 = 5,000,004) | yes |
| 4 | 9 | 555,555 | 555,555 (555,556 x 9 + 4 = 5,000,008) | yes |

Rank 0 is stated in round 96 (`SKILL.md:2435`) and omitted in round 97, but the round-97 rule
extends to it without contradiction: at `T = 1,000,000, nd = 0` the formula gives
4 + 5,000,000 = 5,000,004 → `-`, and the probe agrees (the `MAX_TENSORS = 1,000,000` cap is
`>` so it does not fire; the budget does). **No listed round-96 ceiling disagrees with the
round-97 derivation.**

**The prose does disagree about the total.** Round 96 (`SKILL.md:2441`) ends: "KV and
string-array work also charges steps." The probe comment C1 grades (`probe:581-582`) says the
same: "KV and string-array work also charges steps, so the effective tensor ceiling is slightly
lower." Round 97 (`SKILL.md:2446-2448`) presents `4 + T x (5 + nd)` as what **a file** pays and
calls the fit/miss the verdict rule. The missing term is decisive exactly at the two
within-budget rows: row 1 has 4 steps of headroom, row 5 has **1**. The choice of the tightest
boundary pair in each rank class makes the omitted KV cost flip the boundary itself, not a
distant case. The round-97 disclosed limit ("not a proof over all `(T, nd)` pairs") does not
cover this: the falsified rows are the six **named** classes, with a legal third variable the
limit never mentions.

## 4. Counterexamples (real parser runs)

All fixtures are GGUF v3, `n_kv` as stated, `T` headers of rank `nd`, zero-length names,
one dim of size 1, type F32 (0), offset 0, no data section. Bytes:
preamble 24; header `24 + 8*nd`; u32 KV 17 bytes (4 steps), string KV 43 bytes (5 steps).
Driver is the probe's own `router_file_states` invocation:
`python3 -c "$ROUTER_PY" "$body" files 0` with the body entry
`{"status":{"value":"unloaded","args":[<abs path>, "-m", <abs path>]}}`; the state printed is
`file_state`'s (`probe:790-805`), which maps parser `ok`/`-` to `-` and parser `invalid` to
`invalid`. The ROUTER_PY was extracted read-only from `git show HEAD:tools/kama-probe.sh`
(extraction asserts the heredoc markers; 12,198 bytes).

### B1 — the KV term flips both `invalid` rows

```
t833332-nd1-kv0.gguf    26,666,648 B, n_kv=0  ->  0  invalid   (table row 1, holds)
t833332-nd1-kv2.gguf    26,666,682 B, n_kv=2  ->  0  -         (row 1 false: 4,999,996 + 8 = 5,000,004)
t833332-nd1-kv1arch.gguf 26,666,691 B, n_kv=1 ->  0  -         (one general.architecture string KV: 5,000,001)
t555555-nd4-kv0.gguf    31,111,104 B, n_kv=0  ->  0  invalid   (table row 5, holds)
t555555-nd4-kv1.gguf    31,111,121 B, n_kv=1  ->  0  -         (row 5 false: 4,999,999 + 4 = 5,000,003)
```

Row 1 needs **two** 17-byte KVs to flip; row 5 flips with **one** KV of any shape (4-step
minimum). A string-valued KV of the shape every model carries (`general.architecture`, a
5-step value) flips row 1 with one entry. The rows are true only for `n_kv = 0`; they are
false for the same `(T, nd)` with metadata.

### B2 — rank > 4 is decided `invalid`, the rule says `-`

```
t600000-nd5.gguf  14,400,100 B, T=600,000, first header nd=5  ->  0  invalid
```

The probe reads magic/version/counts (4 steps), the name length + skip (2), `nd` (1), and
returns `invalid` at `probe:749-750`: 7 steps total, independent of `T`. The table's formula
prices 10 steps/header → 4 + 600,000 x 10 = 6,000,004 > 5,000,000 → `-`. The rule misleads a
reader for every rank above the round-96 table's last row (4). (The `n_kv*13 + n_tensors*24 >
size` check passes: 14,400,000 ≤ 14,400,100.)

### B3 — the counter is green while the table is false against the parser

A scratch fixture repo (own `git init`, `rev-parse --show-toplevel` asserted equal to the temp
dir) committed HEAD's `SKILL.md` unchanged and a probe whose only patch is `need(0)` inserted
after the name skip in the tensor loop — one extra step per header, `6 + nd`:

```
AUDIT ON +1/PROBE REPO: DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=0 met=True   exit 0
real   t833332-nd1-kv0.gguf  ->  0  invalid
plus1  t833332-nd1-kv0.gguf  ->  0  -          (4 + 833,332 x 7 = 5,833,328 > MAX_STEPS)
real   t700000-nd1-kv0.gguf  ->  0  invalid
plus1  t700000-nd1-kv0.gguf  ->  0  invalid    (4 + 700,000 x 7 = 4,900,004 <= MAX_STEPS)
```

The audit reads only `MAX_STEPS` from the probe (`audit:69`) and recomputes with its own
`PREAMBLE = 4` and `5 + nd` (`audit:35,103`); the section's numbers match that copy, so the
green survives a parser whose price is one step/header higher. The same +1 probe also keeps
every C2 price expectation: W14 900,000 x 7 + 4 = 6,300,004 `-`; W15 700,000 x 10 + 4 =
7,000,004 `-`; W17 833,333 x 7 + 4 = 5,833,335 `-`; the `slow_*`/`mid` classes 4,200,004 and
4,900,004 `invalid`; `strbig`/`budgetkill` are dominated by the 6,000,000-element array and
`big` by `MAX_TENSORS`. W11 and the two boundary classes were executed above; the remaining
expectations are arithmetic over the frozen fixture list [INFERENCE: not executed through the
C2 harness]. C2's disclosed limit (a) covers wrong per-header charges; **C3's claim carries no
such limit**, and its sentence "every row recomputes from the probe's `MAX_STEPS`" is true only
for the budget side of the recomputation.

## 5. Per-row verdict

| row | arithmetic | verdict against the parser |
|---|---|---|
| 833,332, nd=1, `invalid` | true | **holds only for `n_kv = 0`**; `-` with 2 u32 KVs or 1 string KV (B1) |
| 833,333, nd=1, `-` | true | holds for every `n_kv >= 0` (KV only adds steps) |
| 900,000, nd=1, `-` | true | holds |
| 700,000, nd=4, `-` | true | holds |
| 555,555, nd=4, `invalid` | true | **holds only for `n_kv = 0`**; `-` with 1 KV (B1) |
| 555,556, nd=4, `-` | true | holds |

Unlisted classes: rank 0 extends consistently (no defect); ranks 5+ are the B2 mislead;
`MAX_META` (512 MiB header position, `probe:652-653`) is a third unstated term — a
833,332-header file with ~640-byte names crosses 512 MiB before 5,000,000 steps and returns
`-`, not `invalid` [INFERENCE from the code path; not built].

## 6. Does C3's sentence hold?

Split the two sentences the claim owns.

1. **Predicate** (`plans/round-97-claims.md` §C3): audit at M3 prints
   `DEPTH_BOUNDARY97 rows=6 checks=<c> mismatches=0 met=True` and exits 0. **Holds** at
   `9e605d41`/`e057166e`/HEAD; base is red; the counter's bytes are frozen (K1). The
   `rows=<n>`/`checks=<c>` parts are receipt-level, not audit-enforced (`rows` is whatever the
   section holds), but at the frozen bytes they are 6 and 8.
2. **Section sentence** (`SKILL.md:2446-2448`): "A file pays `4 + T x (5 + nd)` steps …
   decides it (`invalid`) when that sum fits and leaves it `-` … when it does not." **Fails as
   a file-level statement**: the KV term (B1) and the rank domain (B2) both decide the verdict
   for files of the named `(T, nd)` classes. It also conflates "decided" with "invalid": a
   well-formed file within budget returns `ok` at the parser (`probe:768`) and `-` at
   `file_state` (`probe:801-805`), so `invalid` is the header-bomb outcome, not a property of
   the size class.

The C3 claim's disclosed limit ("not a proof over all `(T, nd)` pairs") is accurate about
`(T, nd)` breadth but does not disclose the `n_kv`/rank-domain preconditions on the six
**named** rows, which is where the demonstrations land.

## 7. Impacted axes and smallest safe corrections (routed; this wave edits no tracked file)

- **depth** — E1: make the total a lower bound, not an equality. Replace "A file pays
  `4 + T x (5 + nd)` steps" with "the tensor headers pay `4 + T x (5 + nd)`; every KV costs at
  least 4 more steps (string values 5), and the tensor ceiling falls accordingly", and mark
  rows 1 and 5 `n_kv = 0` (or add the KV cost). Citations: `probe:733-744`, `probe:581-582`,
  `SKILL.md:2441`. This is one sentence plus two cell qualifiers.
- **depth** — E2: state the rank domain. "The formula is for ranks 0–4; `nd > 4` is refused
  `invalid` at `probe:748-750` before any header is priced." Drop the impression that
  `(5,000,000 - 4) / (5 + nd)` governs every rank (B2). Optionally add a rank-5 row whose
  verdict is `invalid` with steps "n/a (refused at the rank field)".
- **calibration** — E3: give C3 a price authority it can test. Either derive the per-header
  cost from the probe's tensor loop (count the `need()`-charging sites) in the counter, or add
  a control receipt that patches the probe to `6 + nd` and requires `mismatches > 0`. Until
  then disclose that the six rows are graded against a frozen copy of `4` and `5 + nd`
  (`audit:35,103`) and that `MAX_STEPS` is the only value read from the probe (`audit:69`).
  Also `audit:106` (`want_verdict = "invalid" if within`) encodes the section's conflation;
  the correct predicate is "decidable iff within budget; a bomb decides `invalid`; `nd > 4`
  decides `invalid` regardless of the budget".
- **operability** (one line, no action here): the missing KV term errs toward `-`, i.e. the
  round-89 loadable direction, so a realistic header bomb at the exact stated ceiling is graded
  loadable while the section says `invalid`. The probe still refuses every malformed file it
  decides; only the disclosure overstates the decided set. C2's fixtures are KV-free, so its
  cells and its disclosed limits are unaffected.

Fixability: E1 and E2 are disclosure edits to one sentence and two table cells; E3 is a
counter-breadth addition. None touches the frozen predicate, the counter bytes, or the probe.
If the canonical judge holds C3 to its predicate alone, the claim passes; if it holds the
section's sentence to the probe's priced behavior, E1 alone rejects it, and E1+E2 reject the
"boundary decision a reader can apply without re-parsing `tools/kama-probe.sh`" promise
(`SKILL.md:2445-2446`).

## 8. Receipts, environment, cleanup

- Parser runs: extracted ROUTER_PY (verbatim heredoc of `HEAD:tools/kama-probe.sh`, saved as
  `out/CR01Boundary/router-extracted.py`), invoked as the probe's `router_file_states` does.
  Fixture builder and exact byte sizes are in `out/CR01Boundary/README-receipts.txt`.
- Fixture repo for B3: temp dir under scratch, own `git init`, toplevel asserted; no lane,
  fleet or sibling repo touched; no `git add/commit` outside that fixture repo.
- Scratch `/fast/scratch/hyaku/kama-r97/CR01Boundary` deleted before yield; receipts copied to
  `.ufo/waves/round-97/w1/out/CR01Boundary/` first.
- Tools installed/upgraded: none (python3/git/struct only); no pacman, no sysctls, no
  process kills, no host services.
- Tracked lane files: none modified (`git diff 9e605d41..HEAD` over the C3 inputs is empty);
  no jj command run.
