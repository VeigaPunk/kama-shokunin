# CR01AnswerTimeCounter — kama r91 w1a2

## Scope
Attacked the frozen C1 counter `tools/round91-answer-time.py` (bytes at F `9a41912a`, sha256
`5d0fe009cd44…ef9e72`) and the C1 predicate: can a probe that is NOT linear-time or that breaks
`normalize_id`'s rule pass all 12 cells? Built eight forgery probes (F3–F10) from base `b71c309a…`
and measured `0aa43573…` bytes, scored each through the frozen counter with `--probe-file`, and
tested eight held-out answers (match not last, >250 000 ids under the cap, `models[]` keys, literal-grep
boundaries). Re-ran `controls/c1-forgeries.sh` and re-ran the counter at M. The lane was read-only.

## Commands and outputs (exit codes)
- `bash <clone>/.ufo/waves/round-91/controls/c1-forgeries.sh <scratch-clone> c06838c5… forg` → exit 0;
  rebuilt `base.sh b71c309a…`, `f1-count-cap.sh 71ab0910…`, `f2-exact-match.sh d25c913b…` — byte-identical
  to the `probe_sha256` in `controls/c1-base.out`, `c1-f1-count-cap.out`, `c1-f2-exact-match.out`.
  Counter bytes identical at F, M and M2 (`5d0fe009…`): K3 holds. `measured/c1.out` `probe_sha256`
  = `git show 3decfa36:tools/kama-probe.sh` (`0aa43573…`) ✓.
- `python3 wt/tools/round91-answer-time.py --repo wt --rev 3decfa36… --work run/m` → exit 0,
  `cells=12 mismatches=0 positive_mismatches=0 probe=rev`, max cell T5 3.16 s, total 17.3 s,
  load 39.91→41.14 (receipt `measured/c1.out`: 2.05 s, load not recorded) — `receipts/c1-M-rerun.out`.
- Forgery scoring, all `--probe-file`, all exit 0, all print
  `cells=12 mismatches=0 positive_mismatches=0 probe=override`: f3-tail `41cf9818`, f4-prefix
  `2c2f3da3`, f5-cap250k `b609603c`, f6-grep `f5fb79d8`, f7-substr `7d8bdc26`, f8-served-blank
  `d9187735`, f9-router-tail `63eb9427`; large cells 1.1–3.5 s (load 42–47). Receipts in `receipts/`.
  f10-naive-substring (`fc7f36c7`, one `grep -qF` on the served list) → exit 1, only P3 fails
  (`mismatches=1 positive_mismatches=1`) — the one cell that punishes a plain substring test.
- Committed-forgery run in my scratch clone only: f3 as commit `de5bd5a75423…` → `--rev de5bd5a7…`
  prints `ANSWER_TIME cells=12 mismatches=0 positive_mismatches=0 probe=rev probe_sha256=41cf9818… rev=de5bd5a7…`,
  exit 0 (`receipts/f3-rev.out`): the frozen predicate line, character for character, for a probe that
  normalizes only the LAST served id.
- `PATH=<shim without python3> /usr/bin/python3 wt/tools/round91-answer-time.py --repo wt --rev 3decfa36…`
  → exit 1, `mismatches=2 positive_mismatches=2` (P4, P5), `probe_sha256=0aa43573…` = M (`receipts/m-nopy.out`).
- Held-out answers (stub listener, `probes/stubrun.py`; load 37–47): 200 001 ids with `good` at index
  100 000 → M `MODEL_OK matched` 1.55 s, f3 `MODEL_MISMATCH`, f4 `MODEL_MISMATCH`; 260 001 short ids
  (3.64 MB, under cap) → M `MODEL_OK` 1.66 s, f5 `MODEL_MISMATCH`; `models[]` 200 000 ids + good →
  M `MODEL_OK` 1.43 s; `models[{"name":"good"}]` → M `MODEL_OK`; `/a/goodness` vs `good` → M
  `MODEL_MISMATCH` (rule-correct), f6 `MODEL_OK` (false green); `x/good.gguf.gguf` vs `good` → M
  `MODEL_MISMATCH`, f6 `MODEL_OK`; wildcard `*` on a 3.4 MB body → M `MODEL_OK` 3.44 s; python-free
  M on the 3.4 MB mid-match body → `MODEL_OK` 1.09 s.

## Findings

**1. BLOCKER — the 12 cells do not own the rule: "last served id only" passes.**
`f3-tail.sh` replaces `model_matches` with "normalize `tail -n 1` of the served list"; everything else
is M. All 12 cells pass, 1.1–3.0 s. Every large cell puts the match last (T1/T3) or has a 1–2 id list
(T4/T5), so no cell can see the difference. Held-out: 200 001 ids with `good` at index 100 000 →
M MODEL_OK, f3 MODEL_MISMATCH (harm shape the cells cannot produce). Evidence:
`receipts/f3-tail.out`, `receipts/f3-rev.out`, `probes/f3-tail.sh:41cf9818`.

**2. BLOCKER — the counter line is reproducible for arbitrary probe bytes at any rev.**
The counter fetches `git show <rev>:tools/kama-probe.sh` and has no allowlist; `probe=rev` is printed for
*any* commit. The only thing that pins the real fix is the M hash in `plans/round-91-claims.md`, which is
a human out-of-band comparison, not a check in the counter. So the frozen predicate's `rev=` token is the
sole defence; the counter itself cannot tell M from a forgery M. Evidence: `receipts/f3-rev.out` (predicate
line, exit 0, probe not the C1 fix), `tools/round91-answer-time.py` `main()` (`git show …`, no hash check).

**3. BLOCKER — the fix's own id-family independence is not tested; a prefix special-case passes.**
`f4-prefix.sh` keeps the pre-round-91 per-id `$(normalize_id …)` fork loop for every large list whose
first id does not start with `x`, `r` or `a`, and decides `x…/r…/a…` lists from the last id. All 12 cells
pass; T1/T2 start `x000000`, T3 `r00000`, T4/T5 `aaaa…`. Held-out `good`-in-middle (x ids) →
M MODEL_OK, f4 MODEL_MISMATCH (`receipts/f4-prefix.out`, `probes/f4-prefix.sh:2c2f3da3`).

**4. DEFECT — no count cap is owned above 200 001 ids.**
`f5-cap250k.sh` (`head -n 250000` on both the models and router streams) passes 12/12; the largest cell is
200 001 ids. Receipt F1 shows a 1 000 cap is caught (T1/T3 verdict), but any cap ≥ 200 001 is invisible.
Held-out 260 001 ids (3.64 MB, legal): M MODEL_OK 1.66 s, f5 MODEL_MISMATCH
(`receipts/f5-cap250k.out`).

**5. DEFECT — literal/substring matching passes; the rule is pinned only by P2/P3's two shapes.**
`f6-grep.sh` (four literal `grep -F` patterns, no per-id normalization) and `f7-substr-leftover.sh`
(substring test for bodies >1 MB) both pass 12/12. Held-out `/a/goodness` vs `good` and
`x/good.gguf.gguf` vs `good` → M MISMATCH, both forgeries MODEL_OK. P3 does kill a *plain* substring test:
f10 (one `grep -qF`) fails P3 only (`receipts/f10.out`); f6/f7 route around it with exact-line and `/id`
patterns while still never normalizing an id (`receipts/f6-grep.out`, `receipts/f7-substr-leftover.out`).

**6. DEFECT — the router half is unpinned: T3 only needs its last entry.**
`f9-router-tail.sh` filters `router_entries` with `tail -n 1` before `awk`, so only the final entry is
considered; T3 passes in 0.51 s and all 12 cells pass. Held-out: a router list whose only loaded matching
entry is not last would be misgraded. The 80 000-entry scan is therefore not what T3 tests — only the
verdict derived from the last line (`receipts/f9b.out`, `probes/f9-router-tail.sh:63eb9427`).

**7. DEFECT — row fields other than verdict/reason are unasserted.**
The counter parses `rows[0].verdict` and `.reason` only. `f8-served-blank.sh` replaces the
`paste -sd,` join with `C_SERVED='-'` (dropping the served list and the join entirely) and passes 12/12:
the C1 join change is time-covered but its output is not (`receipts/f8-served-blank.out`).

**8. NOTE — ambient PATH changes the verdicts of the same M bytes (pre-existing).**
With a PATH that has no `python3`, the identical counter at M prints `mismatches=2 positive_mismatches=2`
(P4 unicode, P5 JSON specials) and exits 1 — a false K1 trigger, probe hash `0aa43573…` = M. Base fails
P4 identically (`base`/`m` both MODEL_MISMATCH without python), so this is the probe's pre-existing
grep/sed fallback, not C1 harm; the counter never strips PATH and never exercises `HAVE_PY=0` (`receipts/m-nopy.out`).

**9. NOTE — 20 s budget at load; single size point.**
At load 39.9–41.1 M's slowest cell was 3.16 s (T5), ~1.5× the receipt's 2.05 s and 6.3× under budget;
under load 42–47 the forgeries' slowest cell was 3.53 s. All five large bodies are 3.40–3.90 MB
(81–93 % of the cap), so the counter measures one size point per shape, not a complexity slope.
No M or forgery cell came near 20 s in any run; load is not recorded by the counter.

**10. NOTE — properties the cells cannot own at all.**
`models[]` instead of `data[]`, `models[].name/model`, top-level `id`: no cell uses them (M is correct on
my held-outs: `models[]` 200 000 ids + good 1.43 s, `models[{"name":"good"}]` matched; the python-free
fallback drops `models[].name` — base-nopy and m-nopy both MODEL_MISMATCH on that 44-byte body, so
pre-existing). Wildcard on 200 000 router entries is *infeasible* under the 4 MiB cap: a loaded entry is
44 B, T3's 80 001 entries are already 3.52 MB, so 200 000 entries would be ≈8.8 MB; the feasible ceiling
is ≈95 000 entries.
`--probe-file` mode differs from `probe=rev` only by the printed token.

**11. NOTE — receipts verified.**
F1/F2/base probe hashes reproduce exactly; F1 fails T1/T3 by verdict and T4/T5 by time (T2 passes, it only
needs a MISMATCH); F2 fails P2 (positive_mismatches=1) and T1/T2/T4/T5 by time. So P2 pins the
dir/one-`.gguf` rule on the served side, P3 pins one-`.gguf` stripping, P6/T2 pin "not blanket MODEL_OK",
T1/T3 pin cap-below-the-match, T4/T5 pin single-huge-id time. Everything else is not pinned.
`measured/c1.out` omits the exit code (base/F1/F2 receipts carry `exit=1`); my rerun records `exit=0`.

## Deliverables
`out/CR01AnswerTimeCounter/probes/` (8 forgery probes + base/F1/F2 rebuild + build.py/mkbody.py/stubrun.py),
`out/CR01AnswerTimeCounter/receipts/` (counter and held-out runs), `hashes.txt` in the same dir.
Scratch `/fast/scratch/hyaku/kama-r91/CR01AnswerTimeCounter` removed after copying. No tool installed.

VERDICT: partial — C1 holds on the landed M (12/12 at load 41 plus eight held-out answers, max 3.5 s), but the frozen counter is satisfied by seven non-conforming probes (one printed as `probe=rev`), so it does not certify the claimed linear-time rule; predicate stays frozen.
