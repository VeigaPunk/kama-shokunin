# SC02QuadraticSweep — kama round 91 wave 1

## Scope

Sweep `tools/kama-probe.sh` at the round-91 measured revisions for **other** bash constructs that are
quadratic or fork-per-item on listener-controlled data, beyond the C1 constructs the claims file names
(`model_matches` / `router_refine` per-id forks, the `${C_SERVED%,}` suffix removal). Candidates examined:
`${var%...}` / `${var#...}` / `${var//...}` on bodies, ids and headers; `while read` loops with `$(...)`
inside; `jstr` on a multi-MB served list; `strip_ctl` call sites. Plus the routed r90 item R3
(`router-?` reason vs SKILL §Probe reason codes).

Revisions measured (full hashes):
- **M** = `3f317ecd211e80929c673e306e3230be287fdf20` (current master, C2 commit), probe
  `tools/kama-probe.sh` sha256 `0aa43573be3a52fa22d9b419049814133324e423dcd22429f107ad28ee0a75da`.
- **C1-measured M** = `3decfa36b0eba7e5197c034dd1547146bca1568a` — `tools/kama-probe.sh` is **byte-identical**
  to M (`git diff --stat 3decfa36 3f317ecd -- tools/kama-probe.sh` → empty, exit 0), so all line numbers below
  apply to both.
- **BASE** = `c06838c5b94576971ea33ac465bf2c935e9037f9`, probe sha256
  `b71c309ad849c25db9c33a2e1bde4c691c766d68073ed0378b5fc96f1e4b48d7`.

Method: lane-owned stub HTTP servers on free 127.0.0.1 ports (never 1234; GET only), one held-out cell per
body shape; attribution by candidate copies of the probe with exactly one construct changed (candidates in my
scratch, never in the lane). Host: 32 cores, load 29–77 during these runs (`/proc/loadavg` printed per run);
every quadratic claim below rests on a **within-run doubling ratio** (N×2 → time ×4), not on an absolute
threshold, so it is load-insensitive; each M/base pair was measured twice and agreed. No tool was installed
or upgraded (none needed).

## Commands and outputs (exit codes)

| # | Command (cwd = my scratch) | Exit | Result |
|---|---|---|---|
| 1 | `git -C wt checkout --detach 3f317ecd211e80929c673e306e3230be287fdf20` | 0 | HEAD=3f317ecd |
| 2 | `git diff --stat 3decfa36 3f317ecd -- tools/kama-probe.sh` | 0 | empty (probe identical) |
| 3 | `python3 tools/round91-answer-time.py --repo <lane> --rev 3f317ecd… --work <scratch>` | 0 | `ANSWER_TIME cells=12 mismatches=0 positive_mismatches=0 probe=rev` (receipt: out dir `counter-at-M.out`) |
| 4 | `python3 tools/round90-reason-rows.py --repo <lane> --rev 3f317ecd…` | 0 | `population=23 documented=23 rows=24 bound=0 unbound=24 … receipt=stale` (receipt binds BASE probe sha) |
| 5 | micro-bench `bash -c` (1–4 MB strings, `LC_ALL=en_US.UTF-8` and `LC_ALL=C`) | 0 | see F1/F4 |
| 6 | stub cells vs probe at M and BASE (`driver.py`, `scale.py`, `curve.py`, `router2/3.py`, `dup_router.py`, `snap.py`, `snap2.py`) | 0 | see Findings |
| 7 | attribution probes `candA-nojstr.sh`, `candC-jstrC.sh`, `candB-nocand.sh`, `candD-noservedfork.sh` | 0 | see Findings |
| 8 | `python3 tools/round91-answer-time.py` re-run into out dir | 0 | `cells=12 mismatches=0 positive_mismatches=0` |

## Findings

**F1 — DEFECT (operability, C1 intent): `jstr`'s global replacements are quadratic in the number of
backslashes/quotes in the served list; a legal 3.80 MB answer kills the probe.**
`tools/kama-probe.sh:204-222` — `s=${s//\\/\\\\}` (206) and `s=${s//\"/\\\"}` (207) run over the *whole*
`C_SERVED` string, which `jstr` receives at lines 1200/1254/1272/1315/1340. Bash's `${s//pat/repl}` costs
O(length) per match, so cost ≈ O(matches × length).
Probe at M, one served id of N backslashes (`check --port --expect nomatch --json`):
`N=80000 → 2.01 s`, `N=160000 → 6.97 s`, `N=320000 → 27.11 s`, `N=640000 → 129.04 s` (body 1.28 MB).
Held-out cell H1 (N=1 900 000, body **3.80 MB — under the 4 MiB cap**): **KILLED at 180.10 s** at M.
BASE at the same cells is *worse* (`N=80000 → 7.09 s`, `N=160000 → 32.76 s`), so this is a carried defect,
not an M regression; M is ~3.5× faster but still quadratic. Attribution at N=160000: probe `10.92 s` →
candidate with jstr's two global replacements removed `0.35 s` → candidate with `LC_ALL=C` inside jstr
`0.58 s` (same verdict MODEL_MISMATCH). The frozen C1 counter does not cover this shape (its only
quote/backslash id, P5, is one id with two specials), so the frozen predicate still passes — but the claim
text "a large answer under the 4 MiB cap is graded in linear time" is **not** true of this body.

**F2 — DEFECT (operability): `router_refine` accumulates `cand` by repeated string append → O(n²) in the
number of matching `unloaded` entries.** `tools/kama-probe.sh:817` `cand="$cand $idx"`.
Wildcard expectation (`--expect *`), router entries with `status.value=unloaded`, at M:
`N=8000 → 2.37 s`, `N=16000 → 9.61 s`, `N=32000 → 37.79 s`, `N=80000 → KILLED at 180.11 s`.
BASE: `N=8000 → 2.52 s`, `N=32000 → 37.40 s` (identical shape — carried, not an M regression).
Control at the same N=32000 with `status.value=weird` → `1.03 s` and `=loaded` → `0.95 s` (no accumulation).
Attribution N=32000: probe `40.27 s` → candidate with `cand=""` (no accumulation) `1.12 s`, same verdict
MODEL_UNLOADED. The wildcard is not required: 32 000 entries **all carrying the expected id**
(`id=good`, `status.value=unloaded`, `--expect good`) → `39.96 s` at M. A non-wildcard expectation with
distinct ids filters through `router_match` (467) and is fine (`H3`, 80 k unloaded entries → `2.28 s`).

**F3 — DEFECT (operability, snapshot path): `served_persist` forks twice per served id, and its
`normalize_id` call keeps the quadratic `${s##*/}`.** `tools/kama-probe.sh:1473`
`p=$(normalize_id "$(persist_clean "$p")")` inside the per-part loop of `served_persist` (1468).
`snapshot` against a stub serving N ids (registry row in my scratch): at M `N=2000 → 11.72 s`,
`N=8000 → 51.21 s`. Attribution N=8000: probe `51.21 s` → candidate with the per-id forks removed `1.50 s`.
Separately, `normalize_id` (438) does `${s##*/}`, which is quadratic in a UTF-8 locale when the id has no
slash: `N=200000 → 21.9 s` (UTF-8) vs `522 ms` at N=40000 in `LC_ALL=C`; reachable end-to-end through
`snapshot` with one no-slash id: `N=50000 → 5.6 s`, `N=100000 → 19.2 s`, `N=200000 → 61.5 s` at M. The C1
change removed this quadratic from `model_matches`/`router_match` but not from the snapshot persistence path.

**F4 — NOTE (mechanism, confirms the claims file's own number): the removed `${C_SERVED%,}` really was the
dominant cost, and bash's cost is locale-dependent.** Micro-benchmark, 1.60 MB comma-joined list:
`${s%,}` → `42.8 s` in `LC_ALL=en_US.UTF-8` vs `8.7 s` in `LC_ALL=C` (claims file says "38 s on a 1.6 MB list
in a UTF-8 locale" — same effect); `${s%zzz}` → `43.9 s`/`8.8 s`; `${s##*,}` → `23 ms`; `${s//x/xx}` →
`97–115 s`/`3.4 s`; the ctl-glob test `[[ $s == *[$'\x01'-$'\x1f'$'\x7f']* ]]` → `29–38 ms` (cheap, **not** a
cost). `strip_ctl` (228, `LC_ALL=C tr -d …`) is applied only to header/CT/err text — bounded, not quadratic
(no finding). `${s##*/}` with slashes present is fast (N=40000 → 1 ms); the cost is the *no-slash* case
(`N=40000 → 1348 ms` UTF-8 / `522 ms` C).

**F5 — NOTE (correctness, no regression): every held-out cell gives the same verdict at M and BASE.**
`H5` (router status value with a control char) → MODEL_UNLOADED/`router-?` at M (0.16 s) and BASE (0.11 s);
`H8` (3.9 MB id of 1.9 M `a/` pairs) → MODEL_OK/`matched` (4.19 s); `H4` (200 k ids, expected absent) →
MODEL_MISMATCH/`served-id-mismatch` (2.06 s); `H11` (40 k ids with a control char → 40 k `\u0001` escapes in
`C_SERVED`) → MODEL_MISMATCH (12.38 s); `H2` (200 k duplicate ids) → MODEL_OK/`matched` (3.45 s). No
held-out cell is a false green/red at M.

**F6 — NOTE (R3, r90 routed item, still open at M): the probe prints reason `router-?` for a router status
value with a control character, and `router-?` is still absent from SKILL §Probe reason codes.**
`tools/kama-probe.sh:759` collapses a `status.value` containing a control byte to `"?"`; `router_refine`
then sets `down="router-$val"` (818) → `RT_REASON=router-?` (841). Measured at M: `MODEL_UNLOADED`,
`reason=router-?` (H5). SKILL.md `## Probe reason codes` (line 1831) has **24** rows — the 23-code
population plus `body-too-large` — and contains **no** `router-?` (`grep -c 'router-?' SKILL.md` → 0); the
frozen population in `tools/round90-reason-rows.py:47-53` likewise lacks it. r90 lesson
`corpus/lessons/round-90-verifier-spotcheck.md:131` asks for it to be escaped as text or documented as a row:
still neither, at M. (Side effect of the same staleness: `round90-reason-rows.py` at M reports
`receipt=stale bound=0 unbound=24` because `.ufo/waves/round-90/measured/reason-cells.jsonl` binds the BASE
probe sha `b71c309a…`, not M's `0aa43573…`.)

**F7 — NOTE (scope): the frozen C1 predicate itself holds at M.** `round91-answer-time.py` at
`3f317ecd211e80929c673e306e3230be287fdf20` → `cells=12 mismatches=0 positive_mismatches=0 probe=rev`, exit 0
(receipt `counter-at-M.out`), and the counter's bytes are unchanged. F1–F3 are therefore **held-out defects
outside the frozen predicate**, not a falsification of the counter.

## Deliverables

- Report: `.ufo/waves/round-91/w1/SC02QuadraticSweep.md` (this file).
- Out dir `.ufo/waves/round-91/w1/out/SC02QuadraticSweep/`: `measurements.out` (every number quoted, with
  probe revs/shas and load context), `counter-at-M.out` (frozen C1 counter at M, exit 0), `escaped.out`,
  `router_scale.out`, `longcurve.out` (raw stub-cell output).
- No lane tracked file was modified; scratch `/fast/scratch/hyaku/kama-r91/SC02QuadraticSweep/` removed.

VERDICT: partial — the frozen C1 counter predicate holds at M (12/12, exit 0), but three quadratic or fork-per-item paths survive at M on listener-controlled data (jstr over a backslash-heavy served list kills a legal 3.80 MB answer at 180 s; `router_refine`'s `cand` append is O(n²) and reaches 180 s at 80 k unloaded entries; `snapshot`'s `served_persist` forks per id), and r90 R3 (`router-?`) is still printed and still undocumented in SKILL §Probe reason codes.
