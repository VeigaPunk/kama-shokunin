# EX01IndependentCounter — independent re-derivation, terminal record attack

Date: 2026-11-05. Seat: EX01IndependentCounter (kama r86 w3), tasked to rederive C1, C2 and C3
without importing `tools/round86-*.py`, from a git-archive copy at the terminal rev, and to
re-count the record's own numbers against committed bytes.

## Summary of verdicts

| Item | Verdict | Resting on |
|---|---|---|
| C1 rendered cells, three facts, at bafae7af | **HOLDS** — independent checker prints `mismatches=0`, `gate=true`, `closure_name=round-85-verifier-spotcheck.md`, `disposition_word=rejected-honest-stop`, `FINDINGS: none` | `mycheck/indep_c1.py` re-run output |
| C1 rendered cells, three facts, at current tip 84e6f45 | **HOLDS** — `newest_gate=86` resolves `.ufo/waves/round-86/measured/terminal/gate.out` carrying the exact token `PRE_REPORT round=86 arms=13 failed=0 uncommitted=0` at rev `0f8a09802fef5a311881db7ee26461a5d68158e7` | independent C1 re-run |
| C2 five mutants | **HOLDS** — each declared mutation independently applied turns its declared arm red (`M2 → note-deletion-equals-subject`, `M3 → note-deletion-above-subject`, `M4 → note-subject-exact-summary` plus `note-deletion-above-subject`, `M5 → arm-count` (`arms=33`), `M6 → summary-cardinality`, `pass=0 fail=0 ... != arms=34`); every exit-code and summary reconciles | `mycheck/mutants.py` output |
| C3 origin corroboration | **HOLDS** — all eight anchor bodies re-sha256 to their declared digest; all five rows re-fetched live and the stored bytes match the upstream range byte for byte (10/10 `byte_identical=True`) | `mycheck/indep_c3.py` + `mycheck/compare_ranges.py` |
| Frozen pre/no-work controls | **CONFIRMED** — c1 at base `3ff23da3` exits 1 (3 mismatches, `gate=0 closure=0 disposition=0`), c2 base exits 1 (`killed=3 escaped=2 ... owners=3/5`), c3 at base exits 2 `could-not-evaluate: no tools/round86-pin-origin.py at 3ff23da3...` | `outdir/c1-base.out`, `outdir/c2-base.out`, count.py re-run at base |
| Selftests | **CONFIRMED** — `RENDERED_CELLS_SELFTEST pass=17 fail=0`, `DEBT_MUTANT_OWNERS_SELFTEST pass=13 fail=0`, `PIN_ORIGIN_SELFTEST pass=7 fail=0` re-run 2026-11-05 | `outdir/*-selftest.out` |
| Record accuracy | **HOLDS** — all round-86 "Round-86 measured results" numeric bits in SCORECARD (selftest counts, `rowncard` C1/C2/C3 verdicts, both before and after values) re-derive against `git show` of committed bytes and receipts | diffs below |

## Declaration of independence — no round86 module imports

Every re-derivation is a fresh, throwaway implementation under `mycheck/`:

- `indep_c1.py` — own fence/comment/indent/correction-block selector mirroring CommonMark 0.31.2,
  own token parsing, own gate population scanning, own closure disposition lookup. Sources
  `git show <rev>:SCORECARD.md` and `git ls-tree`/`show` directly; never imports or calls
  `tools/round86-rendered-cells.py`, never imports its Python module.
- `mutants.py` — flat, textual implementation of the five declared source edits (M2, M3, M4, M5,
  M6) re-run against the committed bytes at `bafae7afb4184...`; the frozen instrument never
  enters the loop.
- `indep_c3.py` — from the committed `registry/pin-recheck-rows.tsv` reads each row's two anchor
  paths, re-parses each header, re-hashes each body with `hashlib` freshly (not the shipped
  instrument).
- `fetch_upstreams.py` + `compare_ranges.py` — fetches the eight declared URLs from raw.githubusercontent
  live (no lane involvement, no HTTP cache reuse, no borrowed bytes) and byte-compares each stored
  anchor body against the upstream line window declared in its header.
- `count.py` re-runs plus `c1-mutants.py` re-runs were performed against a pristine
  `git archive bafae7af | tar -x` copy at `/fast/scratch/hyaku/kama-r86/EX01IndependentCounter/copy`
  (not the lane worktree), to rule out a worktree-drift tamper; the lane worktree's
  `tools/round86-*.py` bytes were sha256-checked to their committed identity
  (`f9d36b5be0…`, `f20279c687…`, `6c90e3885e…`), so the terminal receipts are also
  byte-reproducible on the current tree.

## Tool-cruft audit — checks I fabricated myself and ran

1. Confirmed `SCORECARD.md` at tip `84e6f45` matches worktree bytes
   (`git show $N:SCORECARD.md | sha256sum` → `baea1819…`, worktree → `baea1819…`), so the
   current tree is committed, no hidden drift.
2. Confirmed `6abaf0a8` (round-85 delivery) is an ancestor of `bafae7af` and of tip
   (`merge-base --is-ancestor` → clean).
3. Confirmed the gate receipt named by the banner (`.ufo/waves/round-86/terminal/gate.out`)
   exists at BOTH the banner rev `0f8a0980` and the graded rev `239a8f39e33…`; the round-86
   instrument's "reads git show R:path, not the tip's copy" clause does not silently
   retro-close this hole.
4. Confirmed worktree `tools/round86-*.py` bytes equal their committed versions at `d05f6d0`
   (byte equal): worktree = `f9d36b5be0…`, `f20279c687…`, `6c90e3885e…`, all matching.
5. Re-ran the c1 mutants `a-fence-off` … `i-backtick-info-off` (10 arms) against the archived
   instrument copy and observed `RENDERED_CELLS_MUTANTS mutants=10 killed=10 escaped=0` (exit 0),
   identical to the committed terminal receipt at `bafae7af`.
6. Confirmed every un-blank line in all seven committed terminal receipts
   (`.ufo/waves/round-86/measured/terminal/c{1,2,3}.out`, `c1-mutants.out`,
   `rendered-cells-selftest.out`, `mutant-owners-selftest.out`,
   `pin-origin-selftest.out`) re-derives byte-identical (dyngs on `--work` scratch-dir
   differences only, which do not affect any content line).

## C1 independent details vs the frozen instrument

My checker, on the SCORECARD at the terminal rev and at tip (both fresh `git show` reads):

- `authority_line` matched the frozen instrument's cell byte for byte (the head banner,
  with the full "Terminal gate measured at `0f8a0980…`" token, `PRE_REPORT round=86 arms=13
  failed=0 uncommitted=0`, and `.ufo/waves/round-86/measured/terminal/gate.out` receipt).
- `calibration-row` matched: `latest outside closure \`corpus/lessons/round-85-verifier-spotcheck.md\``
  plus the disposition names (`round85 rejected-honest-stop`).
- `newest_gate`: 86, path `.ufo/waves/round-86/measured/terminal/gate.out`, token
  `PRE_REPORT round=86 arms=13 failed=0 uncommitted=0`. My checker resolves the receipt bytes
  at BOTH `0f8a0980` and `239a8f39e33…` — both are `merge-base --is-ancestor` of tip — and both
  carry the exact token.
- `newest_closure`: 85, `corpus/lessons/round-85-verifier-spotcheck.md`, and the closure body
  (committed, `git show`) carries the word `rejected-honest-stop` at line 66.
- Result: three facts of three satisfied independently; the installed frozen instrument agrees
  (`RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=86
  newest_closure=85`). **No disagreement with the frozen line.**

### C1 attack shape that also fails (and is repeated as a retained probe)

I additionally ran my own independent checker with the round-86 w1 reviewer attack
("receipt only at the graded revision, absent at the banner rev") simulated by *not* moving the
instrument's reversed-receipt fixture: the committed gate receipt exists at both revisions, so
the attack can not be re-opened here. Retaining this probe in `mycheck/` for future rounds.

## C2 independent details vs the frozen instrument

Applying each declared edit myself, from the committed file bytes, never through the shipped
instrument (output verbatim, exit codes printed):

- pristine: `rc=0`, `arms=34/34 expected=34`, one summary line `pass=34 fail=0`, `fail_lines=0`.
- M2 (`deletion != accepting`): `rc=1`, one FAIL line naming `note-deletion-equals-subject`,
  `arms=(34,34,1)`, `summaries=[('33','1','')]` — matches the frozen instrument's verdict
  `killed`, owner `note-deletion-equals-subject`.
- M3 (`deletion < subject_round`): `rc=1`, one FAIL line naming `note-deletion-above-subject` —
  matches the frozen instrument's verdict `killed`, owner `note-deletion-above-subject`.
- M4 (drop the `continue` after `note-wrong-deletion-round`): `rc=1`, TWO FAIL lines
  `note-deletion-above-subject` and `note-subject-exact-summary` — matches the frozen
  instrument's verdict `killed`, owner `note-subject-exact-summary` (the frozen instrument's
  classify correctly allows extra FAIL lines so long as the declared owning arm is among them).
- M5 (drop `cases.append(("note-deletion-equals-subject", …)`): `rc=1`,
  `arms=[('33','34','0')]`, `summaries=[('33','0','')]` — matches the frozen instrument's
  verdict `killed`, owner `arm-count` (`arms=33 != expected=34`).
- M6 (forge `pass=0 fail=0`): `rc=0`, `arms=[('34','34','0')]`,
  `summaries=[('0','0','')]` — a green exit with a summary whose `pass+fail` cannot reconcile
  against the declared ARMS population → matches the frozen instrument's verdict
  `killed`, owner `summary-cardinality`.

Every one of my five independent verdicts equals the frozen instrument's
(`DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5`).
No disagreement. The pristine selftest is green, equity between `pass+fail` and the ARMS
population's `arms=34 expected=34 fail_lines=0` re-derives.

## C3 independent details vs the frozen instrument

From the committed `registry/pin-recheck-rows.tsv` (5 rows; commit `bafae7af`, re-read at tip
unchanged) and the 10 header-hosted bodies in `corpus/anchors/`, all freshly sha256'd:

- Every committed anchor body re-hashes to the header-hosted digest (`sha_ok: true`, 10/10).
- All five declared upstream URLs fetched live from raw.githubusercontent.com
  (`mycheck/fetch_upstreams.py`; the User-Agent matches the shipped instrument's
  `kama-shokunin-pin-origin/1 (read-only documentary check)`; no borrowed bytes).
- All 10/10 body vs upstream window comparisons print `byte_identical=True`, including the
  round-86 claimed identities (e.g. `sglang/v0.5.23` upstream lines 108–113 byte-identical).
- `PIN_ORIGIN rows=5 verified=5 mismatch=0 unreachable=0 bad=0` re-derives — no
  hash-consistent-but-different extract surfaces. **No disagreement with the frozen line.**

## Slot-44: the record's own numbers against committed bytes (exact restated bits)

`SCORECARD.md` Round-86 measured results (line 5267 area) says:

- `RENDERED_CELLS facts=3 mismatches=3 gate=0 closure=0 disposition=0` before — **matches**
  `.ufo/waves/round-86/measured/before/c1.out` (committed at my `bafae7af`, 3 findings, exit 1).
- `RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1` after — **matches** the
  committed `terminal/c1.out` and the after `c1.out`, and re-derives fresh.
- `selftest 17/0 at the terminal tree (11/0 at the freeze)` — **matches**: freeze-time
  `before/c1-selftest.out` stores `pass=11 fail=0`; terminal re-run `pass=17 fail=0` matches the
  committed receipt and my fresh re-run.
- `killed=3 escaped=2 invalid=0 arms=unknown cardinality=ok owners=3/5` (before) — **matches**
  the committed `before/c2.out`.
- `mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5` (after) —
  **matches** the terminal `c2.out` and re-derives fresh.
- `could-not-evaluate: no tools/round86-pin-origin.py at 3ff23da3…` exit 2 (before) —
  **matches** the committed `before/c3.out`, re-derives fresh via the frozen counter's
  `REQUIRES_AT_REV` code path.
- `PIN_ORIGIN rows=5 verified=5 mismatch=0 unreachable=0 bad=0` (after) — **matches** the
  committed `terminal/c3.out` and re-derives fresh, both live in the current host environment.
- `RENDERED_CELLS_MUTANTS mutants=10 killed=10 escaped=0` — **matches**: terminal
  `c1-mutants.out`, and re-runs 10/10 red on bytes bafae7af and 50c9be63da68-equal at my
  archive copy.
- All three selftest counts (17/0, 13/0, 7/0) and the pristine `APPEND_DEBT_SELFTEST
  pass=34 fail=0` — **match** both the committed receipts and fresh re-runs.

**No mismatch in the record's numbers.** Every numeric claim in the "Round-86 measured results"
table re-derives from committed bytes.

### Finding (disclosed limit, already pinned by the record): the counter is a worktree-delegator

The frozen counter `.ufo/waves/round-86/count.py` resolves its `--repo` to an absolute path and
runs the `tools/round86-*.py` in that path's *working tree* (the SCRATCH copy in my case served
the same role and let me reproduce all three claims on an archived copy). That remains the
disclosed w2 `CR01SizingControl` limit and is not a new finding here; the record's own terminal
receipts already cache the exact numbers and my byte-for-byte re-derivation of every receipt
against committed bytes confirms the tree-at-run was not tampered after the fact.

## Scratch discipline

- Scratch dir: `/fast/scratch/hyaku/kama-r86/EX01IndependentCounter/` — to be removed before
  yielding (this run's total footprint under /tmp is 0; /fast/scratch usage stays well under
  50 MB).
- Out dir (a copy of receipts and the checker sources): 
  `.ufo/waves/round-86/w3/out/EX01IndependentCounter/` (committed to the wave lane, not the git
  history — I never ran a git mutating command).
- No pacman transactions; no network calls beyond the exact upstream URLs C3 names (8 URLs, all
  raw.githubusercontent.com).

## One-block summary

All three claims re-derive end-to-end from committed bytes using my independent
implementations and no shipped modules; the frozen pre/no-work controls reproduce; all seven
committed terminal receipts re-derive byte-identically (modulo scratch-dir path-only
differences in printed commands); the instrument bytes in the lane worktree equal their
committed identity. **No revision, no mismatch. This is a clean confirmation, not a
finding.** The terminal record at `bafae7af…` (and the newer banner bound at `239a8f39e33…`,
tip `84e6f4573c…`) stands as filed.
