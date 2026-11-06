# MT02RowCounterMutants — kama round 91, wave w1a2

## Scope
Mutation-tested the frozen C2 counter `tools/round91-threshold-rows.py` (sha256
`fc304abd51135d464c402672c4c894bcff9b1bbe6b7c1565e7d6cf833f109661`, bytes at M2
`3f317ecd211e80929c673e306e3230be287fdf20`). 19 single-point mutants: the 11 named in the seat
(B2, B4 moving-ref, pin, engine, sha, line off-by-one, comment strip, fence, duplicate, B7,
MIN_ENGINES 3->1) plus 8 extra (MIN_ROWS 10->0, ROW_RE indent, heading prefix, SRC_RE indent,
duplicate pair-check, URL rstrip, tier check, empty-cell). Detector: the frozen forgery battery
V1–V4, adapted to take `--counter` (only change; `results/battery-adapt.diff`), plus the counter's
own predicate on M2. Fixtures are a scratch git repo built exactly like the frozen battery
(`git init`, verified toplevel, throwaway identity, no fixed date). Lane repo read-only throughout;
no tracked lane file touched.

## Commands and outputs (true exit codes)
1. `git clone --shared .../kama-shokunin /fast/scratch/hyaku/kama-r91/MT02RowCounterMutants/wt` &&
   `git -C wt checkout --detach 3f317ecd…` — exit 0; `git -C wt rev-parse HEAD` =
   `3f317ecd211e80929c673e306e3230be287fdf20`; counter sha256 lane == checkout == `fc304abd…`
   exit 0.
2. `python3 tools/round91-threshold-rows.py --repo . --rev 3f317ecd…` at M2 — exit 0;
   `THRESHOLD_ROWS rows=14 bound=14 unbound=0 duplicates=0 engines=3 fetch_failures=0
   rev=3f317ecd211e80929c673e306e3230be287fdf20` (matches `measured/c2.out`; load avg 21 at
   20:26, 33–40 at 20:28–20:30).
3. `python3 c2-forgeries-path.py --lane … --counter <frozen> --scratch …` (V1–V4) — pristine
   reproduces `controls/c2-forgeries.out` with `rev=<hex>` normalized: `diff` exit 0
   (`results/battery-reproduces-frozen.diff` empty; 4 variants, 4 final lines).
4. `python3 mt02-mutants.py --counter <frozen> --out mutants` — exit 0, 19 files, each `(old,new)`
   asserted to occur exactly once, `mutants/MUTANTS.sha256`.
5. `python3 mt02-run.py --frozen <frozen> --lane <lane> --rev 3f317ecd… --battery ./c2-forgeries-path.py
   --mutants mutants --scratch … --out results --jobs 4` — exit 0, 19/19 classified
   (`results/run.log`, `results/VERDICTS.tsv`, `results/summary.json`). Every mutant's M2 run is
   `rows=14 bound=14 unbound=0 engines=3 fetch_failures=0`, exit 0, except M06 (see Findings).
6. `python3 mt02-killers.py --lane <lane> --frozen <frozen> --mutants mutants --scratch …` —
   exit 0, `all_killer_fixtures_flip=yes`; 11/11 killer fixtures change the final `THRESHOLD_ROWS`
   numbers or the exit code (`results/killers.out`).

## Findings
- **DEFECT (battery coverage, 5/19 survived the frozen battery; each has a proven killing fixture):**
  - `M12-MIN_ROWS-10-to-0` — V1's expected exit 1 is over-determined: V1 also has `engines=1<3`.
    Killer fixture K01: three genuinely bound rows from three engines (curl S587, llama.cpp S593
    L634, ollama S594 L130) → pristine `rows=3 bound=3 engines=3` exit 1, mutant exit **0**.
  - `M14-heading-prefix-match` — no near-miss heading in the battery. K02: heading
    `## Serving timeout and limit thresholds (draft)` → pristine `rows=0`, mutant `rows=1 bound=1`.
  - `M15-src-re-any-indent` — no indented SOURCES row. K03: a 4-space-indented `S9101` row →
    pristine `source-absent`, mutant `bound=1`.
  - `M17-url-rstrip-dropped` — every battery URL is followed by a space. K04: `S9103` URL inside
    parentheses → pristine `bound=1`, mutant `fetch-failed` (`fetch_failures=1`).
  - `M18-tier-check-dropped` — all battery sources are tier A. K05: mined tier-C `S9102` →
    pristine `source-status=mined/tier=C`, mutant `bound=1`.
- **DEFECT (aggregate-blind, 6/19 killed only via the printed per-row `why`):** the battery's named
  forgery rows are each rejected by a second rule, so the final line is unchanged when the intended
  rule is removed: M01 (B2: V3 T03 also fails B7), M02 (moving-ref: T04 also fails B7), M03 (pin:
  T06 also fails B7), M04 (engine: T07 also fails B6), M05 (sha: T05 also fails B7), M19
  (empty-cell: T10 also fails B2/B7). A reader who checks only `THRESHOLD_ROWS`/exit cannot see
  these rules exercised. K06–K11 give the aggregate-level fixtures: e.g. K06 T01 value `9.9`,
  S587 line 35 `` `threshold during transfer.` ``, name `` `threshold` `` → pristine
  `value-not-in-literal`, M01 `bound=1`; K10 S9002 all-zero digest → pristine `sha-mismatch`, M05
  `bound=1`.
- **NOTE:** `M11-MIN_ENGINES-3-to-1` is visible only in V4's exit code (1→**0**); its aggregate
  numbers are identical (`10/10/0/0/1`). Any receipt that stores numbers but not exit misses it.
- **NOTE:** `M06-line-off-by-one` is the only mutant the measured run itself kills:
  M2 `14/14/0/0/3` → `0/14/0/0/0`, exit 1 (`results/M06-line-off-by-one.m2.out`). All other rules
  are exercised only by the battery because M2's rows are all legit.
- **POSITIVE:** every one of the 19 mutants has a demonstrated fixture that flips the final
  predicate (V1–V4 or K01–K11); no rule in the frozen counter is redundant or untestable against
  the C2 predicate, and the frozen counter is not vacuous. The gaps above are control-set coverage,
  not counter defects; C2's measured predicate is unaffected (14/14/0/0/3, exit 0).
- **NOTE (environment):** the scratch checkout (`…/MT02RowCounterMutants/wt/`) and the battery work
  dir vanished between 20:28:14 and 20:29:52; only `kill/` remained. No lane write occurred. All
  detectors were re-executed against the lane read-only (`git show` at M2 + `corpus/SOURCES.md`
  read); verdicts, M2 numbers and the battery reproduction were identical before/after.
- **NOTE:** K07's mutant leg needs live `master` bytes equal to the tag digest; at 20:31:31 both
  sha256 `4bbc00ec37d8cab75479a7803a80552019e0bca6d83f68ecddf9feb893ea038f`
  (`results/master-vs-tag.txt`). If master moves, that leg stops binding; the pristine moving-ref
  rejection is unaffected.
- **NOTE:** fixture commit hashes vary per run (no fixed committer date), so the detector normalizes
  `rev=<hex>`; only revs were normalized, all other bytes compared.

## Deliverables
Out dir `.ufo/waves/round-91/w1a2/out/MT02RowCounterMutants/`:
`c2-forgeries-path.py` (battery + `--counter`), `mt02-mutants.py`, `mt02-run.py`,
`mt02-killers.py`, `mutants/` (19 mutants + `MUTANTS.sha256`), and `results/`: `run.log`,
`killers.out`, `killers.log`, `VERDICTS.tsv`, `summary.json`, `pristine.{battery,m2}.{out,err}`,
`M*.<battery,m2>.{out,err}`, `battery-adapt.diff`, `battery-reproduces-frozen.diff`,
`master-vs-tag.txt`, `tool-hashes.txt`, `MANIFEST.txt`.

VERDICT: partial — C2's predicate holds at M2 (14/14/0/0/3, exit 0) and every mutant has a fatal fixture, but the frozen forgery battery misses 5/19 single-point rule removals entirely and 6 more only through printed per-row reasons, not the final line.
