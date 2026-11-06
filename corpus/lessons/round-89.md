# Round 89 — lesson (kama)

Base `56174a1fa6a27faa91d3664ef4730b48dd3149c0`; freeze `4eb75c62f6deb1a586a291d611b71775049b34a6`
(`plans/round-89-claims.md`); C1 measured commit `4f9eacf720aa59ed806b31b758571e364658179b`. Read first: the
round-86, round-87 and round-88 verifier spot-checks (all `rejected-honest-stop`; the lane's last six closures
are rejected). Protocol re-read: `MISSION.md`, `AXES.md`, `LEARNING.md`, `CORPUS.md` §SOURCES.md, the round
prompt §6 (run-15 amendments through 46).

## Claims

- **C1 operability (sourced S583/S584/S585):** a router entry whose model file cannot load was graded
  `MODEL_OK router-unloaded-autoload`; the router answers a real request with `500 model name=<id> failed to
  load`. Counter `tools/round89-unloadable-cells.py` (11 live cells, oracle = the real completion; no canned
  expectation). Base `mismatches=5 positive_mismatches=0`; forgeries F1 (round-88 measured probe) 3/3, F2
  (pre-router probe) 7/2; M `mismatches=0 positive_mismatches=0` (`.ufo/waves/round-89/measured/c1.out`).
- **C2 depth (lowest axis, 7):** SKILL §"Router error signatures (llama.cpp router mode)", eight rows each bound
  to a captured b12177 wire answer. Counter `tools/round89-signature-rows.py`; base `rows=0`; forgery battery
  `bound=1 unbound=5 duplicates=1` (`controls/c2-forgeries.out`).

## Gate

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S583 llama.cpp `tools/server/server-models.cpp` @ 6c01da6 (b12177) | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/6c01da6278ab6c69ed67d9124806b50d2b299ba7/tools/server/server-models.cpp — 2026-11-06, sha256 `cab14969b9e5adf08a057c622d1abfc30fd8a17484de5b35942632d739a71108` | `throw std::runtime_error("model name=" + name + " failed to load");` (line 1641) | Source of the frozen oracle mapping (1641, 1956, 1962) at the exact commit of the binary the counter pins; every mapped answer re-observed live (`measured/router-signatures.jsonl`). |
| S584 `ggml/src/gguf.cpp` @ 6c01da6 (b12177) | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/6c01da6278ab6c69ed67d9124806b50d2b299ba7/ggml/src/gguf.cpp — 2026-11-06, sha256 `51bd966ab0494aa20d4087975f17d8b9b8ed9c4b63d7cbffe9315ed45de5dd78` | `GGUFv1 is no longer supported, please use a more up-to-date version` (line 512) | The loader's own checks, so the probe's pre-load rule mirrors what actually rejects a file, not the format's ideal. |
| S585 `gguf-py/gguf/constants.py` @ 6c01da6 (b12177) | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/6c01da6278ab6c69ed67d9124806b50d2b299ba7/gguf-py/gguf/constants.py — 2026-11-06, sha256 `53e6dfa95083d5e81d1da316beb9ea1d4f943cec9dd450db54d849023c01df6c` | `GGML_QUANT_SIZES: dict[GGMLQuantizationType, tuple[int, int]] = {` (line 7035) | Upstream's own block/type-size table; the probe's `QSIZES` was generated from it (36 types, QK_K = 256), not hand-typed. |
| S586 ggml `docs/gguf.md` @ 57e2c2c | **reject** | https://raw.githubusercontent.com/ggml-org/ggml/57e2c2ca2a7cae756b1c4dfafa0cdfef9051d234/docs/gguf.md — 2026-11-06, sha256 `1dead27b6a522709f0127d194e58c21dbbbf00ba1c64fe37c54d1a9048b05020` | "Must be `3` for version described in this spec, which introduces big-endian support." (line 285) | The spec is the format, not the b12177 loader: the loader also loads v2 and requires exact tensor contiguity where the spec only asks for padding. A rule built from it would false-red v2 files. Flip: the loader enforces exactly the spec. |
| `corpus/knowledge/router-unloadable-model.md` | **admit** | cites S583–S585 + own receipts | — | Own-corpus sweep first (KQ143): `grep -ril -E "failed to load\|gguf.*header\|truncat" corpus/knowledge SKILL.md` at base → 7 knowledge files + SKILL. Topical hits: `gguf-declared-identity.md` (a header reader is not loader validation), SKILL E26-15/E26-16 (single-model startup log for a missing / non-GGUF `-m`); the others match "truncat" in unrelated senses (body truncation, untruncated remotes). Plus `grep -n failed corpus/knowledge/router-mode-readiness.md` → the `failed: true` status after a failed load. All three are cited as prior art in the entry. New ground: the pre-attempt state is indistinguishable in the listing, the path is exposed in `status.args`, and a header-only loader-check verdict with live oracle receipts. |
| S582 (README @ 954de24, rejected r88) | **unchanged** (stays rejected) | re-opened 2026-11-06 at b12177 commit 6c01da6: sha256 `eafc1b53…` — identical bytes to S582 | "The `status` object can be:" (unchanged status block, diff vs S581 empty) | Its flip condition (pinned build past b11755) now holds for C1, but no admitted entry cites the README this round (CORPUS rule 4), so the row is not flipped. Recorded, not changed. |

`status` / `recheck` / `used-by` changes on existing rows: none.

## Mistakes

**M1 — a readiness branch generalized from one healthy asset.** Class: verdict rule validated only on inputs
where the asset is good. Evidence: round-88 decision row "`unloaded` (not failed) + autoload → `MODEL_OK`, a
request loads it" (`corpus/knowledge/router-mode-readiness.md`, SKILL §Round-88); its oracle cells used one
valid `stories260K` copy; `controls/c1-base.out` shows the same branch false-green on 5 of 5 unloadable files.
Captured-by: none — KQ141 asks for an oracle cell per documented *configuration*, not per input the branch
silently assumes (here: that the listed file loads). Fix: C1 (`4f9eacf7`) and KQ144 (oracle cells include a
failing variant of every asset the branch assumes). Shown able to fail: `controls/c1-base.out` (red, 5) and
`controls/c1-f1.out`/`c1-f2.out`.

**M2 — a mutating git command in the lane.** Class: write-scope breach. Evidence: L1 ran `git worktree add` from
the lane to get a clean checkout of M for the harm suites; `git worktree list` showed
`/fast/scratch/hyaku/kama-r89/L1/m/wt` registered in the lane's `.git/worktrees`. Captured-by: round prompt §6
item 4 ("Never … a mutating git/jj command"); the L1 did not apply it to `worktree`. Fix: removed with
`git worktree remove --force` (list back to one entry, `jj-lane.sh state` tracked=0); clean checkouts use
`git clone --shared <lane> <scratch>` thereafter. Shown able to fail: `git worktree list` printed two entries
before removal.

**M3 — the round-88 "reasons are ungraded" counter defect repeated in the round-89 counter.** Class: frozen
instrument grades the verdict column only. Evidence: r88 `w1/MT01RouterMutants.md` (DEFECT "reasons are
ungraded by the counter", M01 escaped); round-89 `tools/round89-unloadable-cells.py` compares `oracle == probe`
verdicts only, and wave-1 `w1/MT01ProbeMutants.md` M23 drops both `router-model-*` reasons yet prints
`mismatches=0` (23/31 single-point mutants escape the frozen counter). Captured-by: the r88 MT01 finding itself
(routed in r88 R1 as "held-out cells", not as "grade the reason"); no QUALITY criterion. Fix: the claim stays on
its frozen verdict predicate (the oracle answers with an HTTP code, which cannot grade a reason); the reason
column is graded by the harm harness instead — `tests/probe-verdicts/RouterUnloaded.json` (R5 integration)
grades verdict, reason and exit and fails the three `router-model-*` rows on base
(`.ufo/waves/round-89/measured/harness-r5.out`, `tests=77 passes=74`). Shown able to fail: that base run.

**M4 — a measured commit that was correct but 10x slower and stallable.** Class: cost/robustness harm not in
the frozen kill rules. Evidence: `w1/EX02HarmSweep.md` (+1.3–1.4 s per live check at `4f9eacf7`, every unloaded
entry's file parsed whether it matched or not), `w1/SN01ProbeSafety.md` F1 (a 219-byte answer stalled the
probe 41.4 s), F2 (`/proc/self/environ` opened through a listener-chosen path), F5 (stat/open race onto a
FIFO). Captured-by: none — K2 named verdict suites, not latency or bounded work. Fix: repair `5b1e0fb3`
(matching autoload candidates only; 4 s deadline and 4 M-read budget → undecidable; `O_NONBLOCK` open +
`fstat`; nothing under `/proc`, `/sys`, `/dev`; chunked vocab skip). Re-measured: C1 counter unchanged green
(`measured/c1-final.out`), harm suites unchanged (`measured/harm-final.out`), operator-router median latency
0.136 → 0.251 s (single id) instead of +1.3 s, the SN01 CPU/memory bombs end in ≤1.6 s as undecidable (`measured/sn01-bombs-Mprime.out`), held-out
cells unchanged (`measured/heldout-Mprime.out`). Shown able to fail: EX02/SN01 receipts at `4f9eacf7`.

## Corrections (appended)

- Gate row 5's sweep command is written inside a table, so its `\|` is literal in the cell (RV02 DEFECT). The
  command that was run is: `grep -ril -E "failed to load|gguf.*header|truncat" corpus/knowledge SKILL.md`.
- Gate row 5 also omitted `served-identity-crosswalk.md` and `unregistered-listener-census.md` as router prior art;
  both are cited by `router-mode-readiness.md`, which the new entry cites.

## Wave-1 dispositions (13 seats; answering models `.ufo/waves/round-89/w1-seat-models.txt`, r88 R6)

| Seat | Finding | Disposition |
|---|---|---|
| RV01 | diff matches the loader's header-check set; QSIZES regenerated identical | agree; no change |
| RV02 | S583–S586 re-open clean; S586 reject confirmed; KQ143 grep `\|` DEFECT | Corrections above |
| CR01 | frozen counter reproduces; a name-keyed forgery passes the 11 cells (necessary, not sufficient) | reported as a limit; held-out cells (EX01) and the R5 harness are the extra discriminators |
| CR02 | C2 reproduces 8/8; receipt recaptured byte-identical; row 2 Action wrong after failure; counter binds 3 of 6 columns; `<id>` with empty model binds | SKILL row 2 and decision table fixed (`router-unloaded-failed`); binding limits reported |
| MT01 | 23/31 mutants escape the frozen counter | M3; R5 harness grades reasons |
| EX01 | 13 held-out cells: 6 FIX, 3 AGREE, 3 LIMIT, 1 INDETERMINATE, 0 HARM | re-run at `5b1e0fb3`: identical classes |
| EX02 | latency +1.3–1.4 s at M | M4, repaired `5b1e0fb3` |
| EX03 | R5 reproduced; patched harness 77/77, new rows fail on base | integrated with the fault-control pin update |
| EX04 | R4 cause: the audit's exempt-head eligibility is monotone in `<to>`; register-only fix would delete 19 late rows | not applied (deleting rows from an append-only register is an operator decision); L0 question filed |
| SN01 | F1 CPU stall, F2 listener-chosen opens, F3 unbounded body (pre-existing fetch), F4 unsanitised ids (pre-existing), F5 TOCTOU | F1/F2/F5 repaired `5b1e0fb3`; F3/F4 routed to round 90 |
| SC01 | router aliases give a false `MODEL_MISMATCH` (pre-existing at base) | frontier, routed to round 90 |
| CN01 | no sibling contests the ground; kengaku `PROVINCE.md:26-27` stale | reported, not edited |
| SB01 | SCORECARD round-89 draft, capability rows, R2 pointer | integrated after re-checking each number |
