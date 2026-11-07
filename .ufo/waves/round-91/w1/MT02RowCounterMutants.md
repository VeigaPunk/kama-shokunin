# MT02 — mutation test of the frozen C2 counter (kama r91 w1)

## Scope

- Counter under test: `tools/round91-threshold-rows.py`, sha256 `fc304abd51135d464c402672c4c894bcff9b1bbe6b7c1565e7d6cf833f109661`.
  Identical bytes at freeze F=`9a41912a598cad00f7ff08391586a0ef3732bbed` and at measured M2=`3f317ecd211e80929c673e306e3230be287fdf20`
  (`sha256sum` of the working file and of `git show <F>:tools/round91-threshold-rows.py` agree; receipt `.ufo/waves/round-91/measured/c2.out`).
- 22 single-point mutants: the 11 named by the seat plus 11 more; each differs by exactly one hunk
  (`mutants/mutants.diff`; programmatic check `ALL_SINGLE_POINT True`).
- Detector A — the frozen forgery battery `controls/c2-forgeries.py`, fixture construction and variant rows copied
  verbatim, its printed expectations turned into assertions (`harness.py battery`: exit 0 = counter KILLED, 1 = SURVIVED).
  Faithfulness: re-running the frozen control script reproduced `controls/c2-forgeries.out` byte-for-byte ignoring
  `rev=` (`battery/frozen-control-rerun.out`, `DIFF_IDENTICAL_IGNORING_REV`).
- Detector B — the frozen predicate itself at M2 (`harness.py m2`: exit 0 = met, 1 = not met).
- 13 survivor witnesses (`witness.py`): each is validated first (pristine counter returns the documented negative
  verdict on the fixture), then the mutant is run on the same bytes.
- Host load 19.0–23.2 (32 cores) at run time; fetch latency ~27 ms (a local HTTP cache fronts raw.githubusercontent.com),
  `fetch_failures=0` in every run. No tool installed; no lane file touched; every fixture lived under scratch and was removed.

## Commands and outputs (exit codes)

1. `python3 OUT/make-mutants.py --counter OUT/pristine.py --out OUT/mutants` → exit 0; `pristine_sha256=fc304ab…`, 22 mutants.
2. `sha256sum tools/round91-threshold-rows.py`; `git show 9a41912a…:tools/round91-threshold-rows.py | sha256sum` → both `fc304ab…`.
3. `python3 OUT/harness.py battery --lane LANE --scratch SCR --counter OUT/pristine.py` → exit 1
   (`BATTERY_VERDICT alive`): the battery does not flag the pristine counter (`battery/baseline.out`).
4. `python3 OUT/harness.py m2 --lane LANE --rev 3f317ecd… --counter OUT/pristine.py` → exit 0,
   `M2 killed=0 rows=14 bound=14 unbound=0 duplicates=0 engines=3 fetch_failures=0` (`m2/baseline.out`; equals the frozen receipt).
5. `xargs -P 6` over the 22 mutants × both detectors → xargs exit 0; `battery/M*.out`, `m2/M*.out`; matrix `summary.tsv`
   = **9 KILLED / 13 SURVIVED**.
6. 13 × `python3 OUT/witness.py --case C --counters OUT/pristine.py,OUT/mutants/Mxx.py` → exit 0 each; `witness/*.out`.
7. `python3 LANE/.ufo/waves/round-91/controls/c2-forgeries.py --lane LANE --scratch SCR` → exit 0; diff vs frozen receipt
   identical ignoring `rev=`.

## Findings

DEFECT-1 (systemic, battery): **B7 masks every earlier rule.** All of V3's targeted rows T02–T08/T10 carry prose threshold
cells with no backticked parameter, so they fail B7 as well; removing B1/B2/B3/B4/B5 then changes only the printed `why=`,
while the battery asserts counts. 8 of 22 mutants survive exactly this way (M01–M05, M15, M16, M22). Evidence:
`battery/M01.out` V3 → T03 `bound=0 why=name-not-in-literal` (was `value-not-in-literal`), summary still
`rows=11 bound=1 unbound=9 duplicates=1`; `battery/M04.out` → T07 `literal-not-at-line` (S587 line 31 does not hold `8.4.0`);
`battery/M05.out` → T05 `name-not-in-literal`. Fixture rows that would kill them (each proven by `witness/`): a B7-satisfying
T03, e.g. ``| T01 | curl curl-8_23_0 | `threshold` prose | 9.9 | S587 | 35 | `threshold during` | x |`` (M01); the same shape
with a backticked token for T05/T08/T10 and for T02/T04/T06/T07: ``| T01 | curl master | `Starting` marker | 8.4.0 | S9001 | 34 | `Starting with curl 8.4.0` | x |``
(M02; S9001 = the master URL, whose live sha is today `4bbc00ec…`), ``| T01 | curl curl-8_3_0 | `Starting` marker | …`` (M03),
``| T01 | vllm curl-8_23_0 | `Starting` marker | …`` (M04), S9002 (M05), S9003 (M16), decision `-` (M15), empty decision cell (M22).

DEFECT-2 (worst false green): **M14 "fetch failure counts as bound" survives both detectors** — the battery has no
unfetchable URL. `witness/M14-fetch.out`: pristine `T01 bound=0 why=fetch-failed … fetch_failures=1`; M14
`T01 bound=1 why=bound-unfetched … fetch_failures=0`. B5's "a fetch error … leaves the row unbound" is unprotected: a counter
could bind rows without fetching a byte and M2 would still print `rows=14 bound=14`.

DEFECT-3: **M05 (sha256 compare removed) survives**; witness binds a source whose live bytes do not match the declared digest.
Only moving-ref/pin/engine remain between a changed upstream and `bound=1`.

DEFECT-4: **M12 (MIN_ROWS 10→1) survives both detectors**; no variant is "few rows, all bound, ≥3 engines".
`witness/M12-min-rows.out` (LEGIT curl + lane-M2 llama.cpp T01 + lane-M2 ollama T08): pristine
`rows=3 bound=3 engines=3 exit=1`; M12 `exit=0`. The `rows>=10` half of the frozen predicate is owned by no control.

DEFECT-5: **duplicate-by-id is unowned (M18)**; T09 repeats both the id and the (S,line) pair, so the pair half alone kills the
full rule (M09 and M19 are killed) but dropping the id half survives. `witness/M18-dup-id.out` (T01 at S587:34 and T01 at
S587:30): pristine `duplicates=1 bound=1`; M18 `duplicates=0 bound=2`.

DEFECT-6: **section population by exact `## ` heading is unowned (M17)**. Witness adds
`## Serving timeout and limit thresholds (extended)` with one bound row: pristine `rows=1`; M17 `rows=2 bound=2`.

DEFECT-7: **the 8-cell arity check is unowned (M13)**. A 9-cell row: pristine prints a clean `why=cells=9` unbound, M13 crashes
(`ValueError: too many values to unpack (expected 8, got 9)`, exit 1, no `THRESHOLD_ROWS` line). Not a false green; the
predicate becomes unevaluable instead of false.

NOTE-1: what the battery does own — 9/22 killed: B6 line check and exit code (M06, M21), comment/fence population
(M07, M08 → `rows=12`), the duplicate rule as a whole (M09, M19), B7 (M10 → T14 binds), MIN_ENGINES (M11 → V4 exits 0),
backtick stripping (M20 → V1 unbound).

NOTE-2: the M2 detector is one-sided. 13/22 mutants pass it; it catches only over-strictness (M06, M20) because all 14 real
rows are valid. Under-strictness detection rests entirely on the battery, which is why DEFECT-1…7 matter.

NOTE-3: no harm to the frozen C2 measurement. Every surviving mutant still prints `rows=14 bound=14 unbound=0 duplicates=0
engines=3 fetch_failures=0` and exits 0 at M2 (`m2/M*.out`). These are control-coverage gaps, not a false C2 claim.

NOTE-4: M2 reproduced today line-for-line against `.ufo/waves/round-91/measured/c2.out` (`m2/baseline.out`).

No BLOCKER.

## Deliverables

- `OUT/pristine.py` (counter bytes under test), `OUT/mutants/` (M01–M22.py, `index.tsv`, `mutants.diff`), `OUT/make-mutants.py`
- `OUT/harness.py`, `OUT/battery/` (`baseline.out`, `M*.out`, `frozen-control-rerun.out`), `OUT/m2/` (`baseline.out`, `M*.out`)
- `OUT/witness.py`, `OUT/witness/` (13 cases), `OUT/summary.tsv` (full matrix)
- `OUT` = `.ufo/waves/round-91/w1/out/MT02RowCounterMutants/`; scratch `/fast/scratch/hyaku/kama-r91/MT02RowCounterMutants/` removed.

VERDICT: partial — C2's measured output holds and the counter is not falsified at M2, but the frozen forgery battery owns only 9 of 22 single-point rules: 13 mutants survive it, 12 as demonstrated row-level false greens (a row the pristine counter rejects is graded bound) and one as a crash.
