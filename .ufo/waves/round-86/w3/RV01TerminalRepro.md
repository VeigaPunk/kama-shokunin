# RV01TerminalRepro — independent reproduction of the three frozen claim measurements at bafae7af

Seat: RV01TerminalRepro (kama r86 wave w3, terminal falsification). No `ask` available; no pacman
transactions run; **no tools installed or upgraded** (host tooling sufficed: stock python3, git, uv
cache untouched). Scratch: `/fast/scratch/hyaku/kama-r86/RV01TerminalRepro/` (incl. a `git clone`
of the lane at the terminal tip; removed on yield).

## What I ran (exact commands, full stdout/stderr/exit captured in this directory)

```text
git -C /home/vgpnk/Projects/shokunin/kama-shokunin archive bafae7afb41843564ac2468d28beb8e0bb98e8e6   # first copy attempt
git -C ... clone (fresh clone at bafae7af, detached HEAD verified by rev-parse == bafae7af...)
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-86/count.py {c1,c2,c3} --repo copy --rev bafae7afb41843564ac2468d28beb8e0bb98e8e6 --work w1
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round86-rendered-cells.py --selftest      # exit 0
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round86-mutant-owners.py --selftest       # exit 0
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round86-pin-origin.py --selftest          # exit 0
diffs of my c1/c2/c3 stdout against measured/after/{c1,c2,c3}.out and measured/terminal/{c1,c2,c3}.out
```

Captures: `c1.out/c1.err`, `c2.out/c2.err`, `c3.out/c3.err`, `*-selftest.out/*-selftest.err`,
`full-stdout-combined.txt`. All counters exited 0; all selftests exited 0 with `pass=… fail=0`.

## Verdicts

### C1 calibration — VERDICT: **tree reproduces; receipt with a disclosed defect**

My stdout (first line, byte-identical to `measured/after/c1.out` and
`measured/terminal/c1.out`, and to the no-work/`newest_gate=85` shape demanded by the frozen plan):

```
RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=85 newest_closure=85
```

Selftest 17/0 (`RENDERED_CELLS_SELFTEST pass=17 fail=0`), all red controls still red, round-85
false-green control (`fenced-shadow` with stale live cells → mismatches=3, gate=0) red.
**No-work control**: `measured/before/c1.out` still shows `mismatches=3 gate=0 closure=0
disposition=0`, exit 1 — a do-nothing tree cannot reach mismatches=0 at base `3ff23da3`.
Falsification attempts: I re-ran with `env -i … python3 … --selftest`, three repeat runs for each
selftest, and an env-scrubbed counter rerun (live `/home/vgpnk/Projects/shokunin/kama-shokunin/tools`)
— all green, all stable, no env-var or cwd sensitivity. Divergence found:

- **F1 (finding, defect-level zero but not inherent):** the reasoned synthetic fixture explicitly
  present in the frozen plan (work Sanitizer-armed bytes, fictional illus. `beef…678a`) did **not**
  print the target line for me. With live tip instrument bytes unchanged the pristine debt selftest
  tail was and is
  `APPEND_DEBT_SELFTEST_ARMS arms=34 expected=34 fail_lines=0\nAPPEND_DEBT_SELFTEST pass=34 fail=0\n`
  (attempted sum of my three explicit repro `w1/…` `cat` + `cmp` showed identical bytes; only the
  `arms=34` display line is Historied-receipt-old). Post-`c5a32443` bytes do **not** print
  `arms=34`; the plan's earlier "printed `arms=34`" reading was a summary-line钉 historical artifact.
  **Pointer:** run-c2.out line 1 byte-diff — `/tmp/out_73668b4e58d8c0de290ec697e2797178.txt`
  synthetic print line printed `…pass=34 fail=0 arms=34` and my clean `w1/targ` run line printed
  `…pass=34 fail=0` (no arms field) — see F1 in Finding file "The correct reading" below.

### C2 operability —_VERDICT: **target line reproduces at terminal tip; after-receipt mismatch found and disclosed**

My stdout (byte-identical to `measured/terminal/c2.out` line-for-line, incl. exit 0):

```
DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5
DEBT_MUTANT_OWNER M2 owner=note-deletion-equals-subject verdict=killed owning failure line present (1 FAIL lines)
DEBT_MUTANT_OWNER M3 owner=note-deletion-above-subject verdict=killed owning failure line present (1 FAIL lines)
DEBT_MUTANT_OWNER M4 owner=note-subject-exact-summary verdict=killed owning failure line present (2 FAIL lines)
DEBT_MUTANT_OWNER M5 owner=arm-count verdict=killed arms=33 != expected=34
DEBT_MUTANT_OWNER M6 owner=summary-cardinality verdict=killed summary pass+fail=0 != arms=34
DEBT_MUTANT_OWNER_PRISTINE APPEND_DEBT_SELFTEST pass=34 fail=0
```

Selftest 13/0 (`DEBT_MUTANT_OWNERS_SELFTEST pass=13 fail=0`), all 13 arms green.
**No-work control**: `measured/before/c2.out` at base still shows `killed=3 escaped=2
arms=unknown cardinality=ok owners=3/5`, exit 1 (M5/M6 escape at base bytes) — the base bytes are
real, not staged.

**F2 — the one materially divergent artifact (superseded-receipt defect, multi-seat corroborated).**
`measured/after/c2.out`'s last line is
`DEBT_MUTANT_OWNER_PRISTINE APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34`, but the committed bytes
at every revision carrying that file (bafae7af, 239a8f39, 84e6f457, HEAD) print (and my three runs
deterministically printed) `pass=34 fail=0` with **no** `arms=` suffix, because `c5a32443` (the
"keep the round-81 summary shape" commit) dropped the suffix so frozen gate arm 11's `fullmatch`
keeps working; arms moved to the `APPEND_DEBT_SELFTEST_ARMS arms=34 expected=34
fail_lines=0` line. Therefore `after/c2.out` is **not producible at the claim's terminal revision**
by the committed bytes — it is the pre-correction intermediate receipt saved at commit `c5d71b7a` /
staged in the L1 draft. This is a publication-hygiene defect (a superseded intermediate receipt
carrying a line the current bytes cannot print), not a wrong number of killed mutants, and the
instrument-side defect was already absorbed by the terminal receipt + a w1/w2 record check. Flagged
at the same time by w2 seats; the banner ("record at 239a8f39… selftest 13/0, pristine pass=34
fail=0") is correct for the terminal bytes.

### C3 freshness — VERDICT: **reproduces byte-for-byte against live upstreams**

My stdout byte-identical to `measured/after/c3.out` (and to `terminal/c3.out`'s payload):

```
PIN_ORIGIN rows=5 verified=5 mismatch=0 unreachable=0 bad=0
PIN_ORIGIN_ROW llama.cpp/b11755 verdict=verified anchors=2/2 corpus/anchors/llamacpp-b11755-health.txt: upstream 478-490 byte-identical; corpus/anchors/llamacpp-b12111-health.txt: upstream 479-491 byte-identical
PIN_ORIGIN_ROW llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a verdict=verified anchors=2/2 corpus/anchors/llamacpp-39febd2a-router.txt: upstream 2197-2204 byte-identical; corpus/anchors/llamacpp-b12111-router.txt: upstream 2199-2206 byte-identical
PIN_ORIGIN_ROW llama.cpp/b7200 verdict=verified anchors=2/2 corpus/anchors/llamacpp-b7200-health.txt: upstream 403-415 byte-identical; corpus/anchors/llamacpp-b12111-health.txt: upstream 479-491 byte-identical
PIN_ORIGIN_ROW sglang/v0.5.22 verdict=verified anchors=2/2 corpus/anchors/sglang-v0.5.22-health.txt: upstream 108-111 byte-identical; corpus/anchors/sglang-v0.5.23-health.txt: upstream 108-113 byte-identical
PIN_ORIGIN_ROW vllm/v0.32.0 verdict=verified anchors=2/2 corpus/anchors/vllm-v0.32.0-prefix-caching.txt: upstream 1-6 byte-identical; corpus/anchors/vllm-v0.33.0-prefix-caching.txt: upstream 1-6 byte-identical
```

All ten (5 rows × 2 anchors) live-upstream byte comparisons passed on this run against live
llama.cpp/SGLang/vLLM release bytes. Selftest 7/0 (`PIN_ORIGIN_SELFTEST pass=7 fail=0`), including
the fabricated-hash-consistent control grading `mismatch`, not `verified`.
**No-work control** intact: `measured/before/c3.out` = `could-not-evaluate: no
tools/round86-pin-origin.py at 3ff23da3…`, exit 2 — a do-nothing tree cannot print a green row.
The count.py `REQUIRES_AT_REV` presence-then-worktree-execute split is a known, plan-disclosed
limit and is covered by w3 seat findings (NOT re-attacked here; the instrument at the terminal
revision is what was graded).

## Instrument-bound checks

- **No published number is reachable by a no-work tree.** All three `before` receipts are
  committed and show the refused/red anchor state (exit 1/1/2 respectively). ✔
- **No receipt is bound to a revision that lacks the instrument it grades.** `count.py` c3's
  gate: `git cat-file -e <rev>:tools/round86-pin-origin.py` is required at `--rev` before grading —
  confirmed by reading `count.py` line 36 and by the fact that running with a non-git directory or
  removing the instrument at tip reliably flips c3 to `could-not-evaluate:`, exit 2. ✔
- All three instrument files are **unchanged** between freeze `c07e1f90` and bafae7af
  (md5-identified blobs identical for `tools/round86-{rendered-cells,mutant-owners,pin-origin}.py`
  and `tools/round81-append-debt.py`). The `after` measure vs `before` measure difference is
  entirely in the record/test artifacts, not the graded code. ✔

## Record bytes verified against the joint-diff

- `SCORECARD.md`, `LOG.md`, `corpus/lessons/round-86.md`, `corpus/SOURCES.md` at bafae7af
  differ from the HEAD worktree only in the w3 correction commits (`c5a32443`, `84e4f457`, HEAD).
  No closing truce entries or hidden truce pages found; diffs are pure correction/appends of the
  round-86 record.
- `SCORECARD.md` bafae7af "Current authority (round 86)" and "Round-86 measured results" tables
  name exactly `mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5`,
  `selftest 13/0`, `RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 …
  newest_gate=85 newest_closure=85`, `17/0`, `mutants=10 killed=10 escaped=0`,
  `PIN_ORIGIN rows=5 verified=5 mismatch=0 unreachable=0 bad=0` — every one of these exact
  strings appears in the trace-verified receipt stdout I reprinted above. ✔
- Record's axis/capability tables (`mutant-owning-arms`, `rendered-cell-identity`,
  `pin-origin-corroboration` first-working-round 86) match the tree's keys verbatim. ✔
- Lesson file `corpus/lessons/round-86.md` and `corpus/SOURCES.md` matches ("C1 10/10 source
  mutants each killed by a named arm") re-derivable from the small local `measured/after/
  c1-mutants.out` (10 mutants, each arm red at exit 1, including `h-container-off` matching
  `list-fence-shadow` and `i-backtick-info-off` matching `backtick-info-not-a-fence`). ✔

## The one materially divergent artifact, itemized (supersedes my first report's undecided F1 question)

1. `measured/after/c2.out`'s pristine line (from the committed blob `97b97c4a…`, and also at the
   frozen plan's freeze commit):

   ```
   DEBT_MUTANT_OWNER_PRISTINE APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34
   ```

   …cannot be printed by the committed bytes today. Reproduced fact from this seat's
   `w1/targ/out.txt` (a full-reasoned scratch rerun of the frozen counter at bafae7af), plus the
   L1's own `measured/terminal/c2.out` line 9, and a direct `python3 tools/round81-append-debt.py
   --selftest | tail -2` (exits 0, stdouts seen above):

   ```
   APPEND_DEBT_SELFTEST pass=34 fail=0
   ```

   `c5a32443` ("correct the terminal selftest and mutant counts in the record") is the commit
   that produced the split; the after-receipt predates it and was never re-stamped. This is the
   same finding w2 seat `MT02ForgeryArms` §3 and the `0fec2861` lesson already disclose; it is
   **not a hidden discrepancy** but it is a real, unproducible-instrument-state line still
   published as part of the round's number set.
2. The record's C2 banner (`pristine pass=34 fail=0`, SCORECARD line 6) is the **terminal**
   numbers and quotes the terminal receipt, not the stale intermediate: correct as published.

## Residual risks / what I did not attack

- `count.py` c3's presence gate reads at `--rev` but executes the **worktree** instrument
  (`tools/round86-pin-origin.py` from `--repo`'s checkout bytes, not from
  `git show <rev>:tools/round86-pin-origin.py`). A tampered worktree instrument at the run machine
  changes the verdict at any revision. Known to the plan (disclosed in w2 CR01 receipts), so not an
  admission-corridor failure, but worth routing to r87's plan item 2 (already there).
- Instruments exercised in this seat: `rendered-cells.py`, `mutant-owners.py`, `pin-origin.py`,
  `append-debt.py` (pristine), `count.py`. Not exercised: `pre-report-gate.py` arms 1–13
  independently, `sources-census.sh`, and the c3 anchors' upstream **timing** drift risk
  (byte-identical today, could legitimately flip on any later upstream change — by design).
- The selftest `muant-owners` "no-arms-line-disclosed-limit" arm grades `escaped` (not `invalid`):
  an attempt by the calibration to surface the arms-missing summary is present but framed as a
  disclosed limit, not a red failure. Verified visible in `st-mutant-owners.out` line
  `no-arms-line-disclosed-limit … verdict=escaped`.

## Bottom line

**C1 reproduces (exit 0, mismatches=0, selftest 17/0).**
**C2 reproduces at the terminal tip** (`killed=5 escaped=0 invalid=0 arms=34 cardinality=ok
owners=5/5`, exit 0; selftest 13/0) — with the single receipt-hygiene defect recorded above
(`measured/after/c2.out` is a non-producible intermediate, `arms=34` suffix line).
**C3 reproduces** (verified=5/mismatch=0 unreachable=0 bad=0, exit 0; selftest 7/0) — the
fabricated-hash-consistent control stays red, the instrument's live-origin leg works.

No published claim number is fabricated, no latent landing red arm was found beyond the two
already-recorded w3 findings, and record bytes match receipt bytes everywhere except the one
superseded-receipt defect honestly disclosed above. No new capabilities beyond
`rendered-cell-identity`, `mutant-owning-arms`, `pin-origin-corroboration` are implicitly claimed.

**Tools installed:** none (nothing needed beyond stock python3/git).
