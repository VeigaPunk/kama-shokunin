# MT01ProbeMutants — mutation test of C1 (kama r91 w1)

## Scope
15 single-point mutants of the round-91 C1 code in `tools/kama-probe.sh`, applied in scratch clones at
M=`3decfa36b0eba7e5197c034dd1547146bca1568a` (probe sha256 `0aa43573be3a52fa22d9b419049814133324e423dcd22429f107ad28ee0a75da`).
Each mutant was (a) syntax-checked, (b) committed inside a scratch clone and graded with the frozen counter
`/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round91-answer-time.py` (bytes sha256
`5d0fe009cd44107a2155e5567b8e9409c4d294b7e94a9b738a9aa98303fd9e72`, unchanged from F), and (c) graded with
`tests/probe-verdicts/check.py` run from the clone (77 rows). Baseline pristine M was graded first and after
restoration, on the same detector pair. Survivors were then probed with discriminating stubs versus pristine
bytes (`diverge.py`, imports the frozen counter's `Stub`/`jbody` so stub behaviour is identical). Counter cell
list is frozen: no new cell was run against the counter; proposed cells below are prose only.

## Commands and outputs (exit codes)
- baseline: `python3 tools/round91-answer-time.py --repo <wt> --rev 3decfa36… --work <scratch>/w/wt` →
  `ANSWER_TIME cells=12 mismatches=0 positive_mismatches=0 probe=rev probe_sha256=0aa43573…` **exit 0**;
  `cd <wt> && python3 tests/probe-verdicts/check.py` → `tests=77 passes=77 failures=0` **exit 0**.
  (first baseline attempt exited 2 `unresolvable --rev` because the driver passed a relative `--repo`; fixed
  before any mutant ran — that run graded nothing and is not counted.)
- per mutant: `bash -n` **rc 0** for all 15; probe file sha256 recomputed independently from
  `pristine + one exact replacement` matched the recorded sha for every mutant (no cross-contamination, incl.
  the two commits a peer pilot left in `<wt>`: each mutant is rewritten whole from its own pristine copy).
- mutant grading: `python3 <lane>/tools/round91-answer-time.py --repo <clone> --rev <mutant-sha> --work <scratch>/w/<clone>`
  and `cd <clone> && python3 tests/probe-verdicts/check.py` — codes are the `counter_rc`/`check_rc` columns of
  `kill-matrix.tsv`.
- restoration: clone tree rewritten to pristine bytes (`sha256 0aa43573…`), then
  `--rev 3decfa36…` → `cells=12 mismatches=0 positive_mismatches=0` **exit 0** and `check.py` → `77/77`
  **exit 0** (`restored-run.out`).
- load: `uptime` captured per mutant (`receipts/<mid>/uptime.before|after`); load average 10.07 at the start,
  32–36 while the four workers ran. Max observed cell time over all mutant runs 3.62 s (mutant), 2.08 s
  (baseline) against the 20 s budget → **no cell was killed by time**; every failure is a verdict/reason
  mismatch (`grep ok=0` shows seconds 0.09–2.41).
- lane untouched: `git -C <lane> status --porcelain` shows only other seats' untracked `.ufo/waves/...` files;
  lane HEAD `3f317ecd` (M2). No tool installs.

## Findings
**Mutation score: 5/15 killed; 5/10 non-equivalent killed (50%).** Killed: m01, m02, m05, m06 (counter and/or
check), m07 (check only). Not killed: m03, m04, m08, m09, m10, m11, m12, m13, m14, m15.

- **DEFECT (coverage, verdict level, false green): the router id filter is unguarded by both detectors.**
  `m08-router-match-prints-all` (router_match `{print}` instead of the `s==e` filter) and
  `m14-router-refine-wildcard-inverted` (`[ "$wild" -eq 1 ]` → `-eq 0`) both pass 12/12 cells and 77/77 rows,
  yet flip a real verdict: `out/diverge/m08-…out:2-4` and `out/diverge/m14-…out:2-4` — body
  `[{other,loaded},{good,unloaded}]`, `--expect good`: M `MODEL_UNLOADED/router-unloaded exit 2`,
  mutant `MODEL_OK/matched exit 0`. Structural reason: T3 is the counter's only router cell and every one of
  its 80 000 entries is `loaded`, so any filter defect yields `ok=1` → MODEL_OK; no check.py row pairs a
  foreign *loaded* entry with an expected *unloaded* one. The whole `router_match` filter is therefore
  untested by the frozen set. Proposed cell (prose only): `T6-router-foreign-loaded` — `/v1/models` data
  `[{id:"other",status:{value:"loaded"}},{id:"good",status:{value:"unloaded"}}]`, expect `good` →
  MODEL_UNLOADED/router-unloaded/exit 2/≤20 s. Kills m08 and m14.
- **DEFECT (coverage, verdict level, false green): a space inside a router id.** `m11-router-match-default-fs`
  (drop `-F '\t'`) passes 12/12 and 77/77, but `out/diverge/m11-…out:2-10`: entry
  `{id:"My Model",status:{value:"unloaded"}}` (and `"/mnt/models/My Model.gguf"`, a plausible llama.cpp path
  id) with `--expect "My Model"` → M `MODEL_UNLOADED/router-unloaded exit 2`, mutant `MODEL_OK/matched exit 0`
  (default FS makes `$1` = `My`, the entry is dropped, `any_status` stays 0 and router_refine returns without
  rewriting the arm's MODEL_OK). Proposed cell: `P8-router-space-id` — one entry
  `{id:"My Model",status:{value:"unloaded"}}`, expect `My Model` → MODEL_UNLOADED.
- **NOTE (coverage, reason level): m03, m13 survive both detectors but change the reason.**
  `m13` (drop `if (s=="") next`) and `m03` (`L >= 5` → `L > 5`, the 5-byte id `.gguf`) both turn
  `MODEL_MISMATCH/unresolvable-id` into `MODEL_MISMATCH/served-id-mismatch` for ids that normalize to empty
  (`.gguf`, `a/`): `out/diverge/m13-…out:2-7`, `out/diverge/m03-…out:2-4`; verdict and exit are unchanged,
  which is why the counter (T2 pins verdict only) and check.py (no such row) are both blind. If reason pinning
  is wanted the counter's T2 would need `reason=served-id-mismatch` plus a `.gguf`-only cell; check.py needs a
  row with a normalize-to-empty served id.
- **NOTE (equivalent, defence in depth): m04 and m15 are individually inert.** Dropping norm's `return s ""`
  (m04) or the BEGIN `e = … ""` (m15) changes nothing while the other coercion stands: `s` is a plain string,
  so `s == e` is a string compare either way (verified: gawk 5.4.1 makes `ENVIRON["KAMA_EXP"]` a strnum —
  `KAMA_EXP=0123 awk 'BEGIN{print (ENVIRON["KAMA_EXP"]==123)}'` → `1`). Both removed together is observable:
  `out/diverge/double-m04+m15.out:2-7` — ids `["0123"]` expect `123`, and `["1000"]` expect `1e3` →
  M MODEL_MISMATCH, double mutant MODEL_OK. No cell or row uses a numeric id; the coercion pair is real but
  unexercised (low likelihood: needs a numeric-only id pair that differs as text).
- **NOTE (equivalent): m10 `paste -sd,` → `printf '%s' | tr '\n' ','` is byte-identical.** `$ids` is
  newline-*separated* (command substitution strips the trailing newline), so `tr '\n' ','` emits no trailing
  comma and `paste -sd,` emits none either: `out/diverge/m10-…out` (J1 two ids → `served_model:"a,b"`, J2 one
  id → `"good"`) is identical for all three cases, and 12/12 + 77/77 pass. So the load-bearing part of the C1
  fix is the removal of `${C_SERVED%,}` (the 38 s quadratic in a UTF-8 locale), not the paste swap; the two
  join forms are interchangeable and the detectors cannot tell them apart.
- **NOTE (equivalent): m09 (router_refine early-return removed) and m12 (`hit { next }` removed) are inert.**
  m09 only costs an extra `router_entries | router_match ""` fork when `--expect` normalizes to empty
  (verdicts identical in `out/diverge/m09-…out`); m12 is performance-only (all cells ≤2.39 s, T-cells pass).
- **NOTE: m07 (END exits 1↔2 swapped) is killed by check.py only.** The frozen counter passes 12/12 because
  T2 pins `MODEL_MISMATCH` but no reason: the swap degrades `served-id-mismatch` to `unresolvable-id` and T2 is
  satisfied. A reason-level regression in the mismatch path is invisible to the counter alone.
- **NOTE: m02 (strip all `.gguf`) is killed by counter P3 only** (`good.gguf.gguf`); check.py has no
  double-suffix row. Harm there is caught, but the suite is thinner than the counter on that axis.
- **NOTE: m01 (`no .gguf` strip) is double-killed** (counter T5, P2; check `ReadyControls.served-id-carries-gguf-suffix`)
  and **m05 (`-v` instead of ENVIRON) is killed as harm** — counter P5-json-specials, `positive_mismatches=1`,
  which is exactly the S592 POSIX claim's predicted failure (a `-v` assignment eats the backslash in `q"b\s`).
  This empirically corroborates C1's cited mechanism.

## Deliverables (all under `.ufo/waves/round-91/w1/out/MT01ProbeMutants/`)
`kill-matrix.tsv` (mutant, probe sha, rev, cells killed, check rows killed, divergent cases, killed_by);
`restored-run.out`; `receipts/<mid>/` (counter.out with per-cell lines, counter.rc, check.rc, check-summary.txt,
probe.sha256, probe.diff, rev, bash-n.rc, uptime.before/after) incl. `receipts/baseline/`;
`diverge/*.out` (M vs mutant verdict/reason/served_model/exit per case); `harness/` (muts.py, driver.sh,
diverge.py, summarize.py, cases-*.json) to reproduce.

VERDICT: holds — C1's predicate is intact at M (12/12, 0/0) and 5/15 mutants die, but 3 verdict-level survivor classes (router filter, space-bearing router id, empty-normalizing id) prove the frozen 12 cells cannot detect any defect in the router arm.
