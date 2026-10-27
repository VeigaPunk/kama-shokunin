# M2C2Mut — round-55 C2 counter mutation test (seat report)

**Verdict: the frozen C2 counter's `superseded` check is real — 7 of 12 single mutants killed (m01 by the forged-superseded tree, m08 by an env attack, 5 by the counter's own fixture/lane legs), 2 provably equivalent, and 3 true survivors (m03 replacement-resolves, m04 base-cited, m09 served-bytes digest compare) are coverage gaps in the oracle set, not counter defects; the lane at 9c60eae6f7ed84f7da93d219a406aadc30958c6c was re-measured met=True and every byte I touched was restored.**

Scope: mutation test of `tools/round54-cited-path-check.py` (sha256 `d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c`, byte-identical to `counter_sha256` in `.ufo/waves/round-55/preregistration.json` before and after all runs). 12 single mutants, 20 counter invocations (cap 20), all receipts in `.ufo/waves/round-55/w1/out/M2C2Mut/runs/`.

## 1. Setup

- Scratch: `S=/fast/scratch/hyaku/kama-r55/w1/M2C2Mut` (`TMPDIR=$S`); one live clone `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`; `git -C $S/lane rev-parse --show-toplevel` printed `$S/lane` before any mutation.
- Baseline re-measurement (run r01) reproduced the frozen build measurement exactly:
  `python3 $S/pristine.py --repo $S/lane --tip 9c60eae6f7ed84f7da93d219a406aadc30958c6c --fleet /home/vgpnk/Projects/shokunin --fleet-rev 6c4aba34c2a22519152d8c6f32e1039eecb1381b --scratch $S/rs --out .../r01-baseline-tip.out` → exit 0, `fixture=1 lane=1 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True` — identical counters to `.ufo/waves/round-55/measured/c2-build.out` (network up; all upstream fetches succeeded).
- Forged-superseded tree, built once (commit `c54fa712d2cb978fb34fd4809ca8d1eeb7a759e0` in my clone, parent 9c60eae, author `fx <fx@invalid>`, diff = 1 line in `SCORECARD.md:18`, full diff in `out/M2C2Mut/forged-commit.diff`): the calibration row's "latest outside closure" now cites BOTH the superseded token `corpus/lessons/round-52-verifier-spotcheck.md` (still cited = the forgery) and the replacement `corpus/lessons/round-53-verifier-spotcheck.md`; the honest ledger row 46 (`SCORECARD.md → superseded → round-53-verifier-spotcheck.md`) unchanged. Both files resolve at the tip, the token is cited at BASE 0b75a84c, so the ONLY defect is the still-cited token.
- Killing-case validation (run r02): pristine counter on the forged tip → exit 1, `bad=1` (detail: "superseded token is still cited at tip"), `dropped=0 undisclosed=0` — the failure is attributable solely to the superseded still-cited clause. The killing case has teeth.

## 2. Mutants and verdicts

Every mutant is a single unique-anchor replacement (asserted count==1; table with exact old/new strings and sha256s in `out/M2C2Mut/mutation-table.json`; mutant sources in `out/M2C2Mut/mutants/`). Line numbers refer to the frozen counter.

| # | mutant (mutated point) | @ honest tip 9c60eae | @ forged tip c54fa71 | verdict |
|---|---|---|---|---|
| m01 | superseded **still-cited** clause dropped (`:470-471`) | met=True exit 0 (survivor) | **met=True exit 0, bad=0** on a tree the honest counter fails with bad=1 → calls the forged row good (`runs/r-m01-still-cited-drop-forged.out`) | **KILLED** (forged tree) |
| m02 | superseded **replacement-cited** clause dropped (`:473-474`) | exit 1, uncaught `TypeError: 'NoneType' object is not iterable` at `if any(v != "ok" for _e, v in rep)` — the counter's own fixture scenario 15 forged tip (replacement never cited) hits the removed guard (`runs/r-m02-replacement-cited-drop-tip.stderr`) | not reachable (crash in fixture leg precedes the lane leg) | **KILLED** (fixture; loud crash, exit 1 = not-met code, no met line) |
| m03 | superseded **replacement-resolves** clause dropped (`:475-476`) | met=True (survivor) | met=False — rejects the forgery via the intact still-cited clause; did not call it good | **SURVIVOR** (coverage gap, §3.1) |
| m04 | superseded **base-cited** clause dropped (`:477-478`) | met=True (survivor) | met=False — token IS cited at base in the forged tree, clause unreachable there | **SURVIVOR** (coverage gap, §3.2) |
| m05 | **stale-exempt tuple** − `superseded` (`:637`) | exit 1, `fixture=0 (14/15)` + `stale=1` — the honest round-55 row itself becomes stale | — (fate sealed at tip) | **KILLED** |
| m06 | **dropped-exempt set** − `superseded` (`:646-647`) | exit 1, `fixture=0 (14/15)` + `dropped=1` (scenario 15 requires dropped==0) | — | **KILLED** |
| m07 | **disclosed exclusion** +`superseded` back into the disclosed gate (`:641`) | met=True, `disclosed=15` vs 14, all gate counts unchanged | provably unreachable: on the forged tree the row is bad → `elif why is not None` precedes the gate; skipped (run-cap triage, §4) | **EQUIVALENT** (only the informational `disclosed` count shifts) |
| m08 | **clean_env** passthrough of inherited `GIT_*` (`:200`) | met=True with a clean environment (survivor) | tree-independent, skipped (§4) | **SURVIVOR** of both assigned oracles — **KILLED by env attack** (§3.3) |
| m09 | **upstream digest compare** (full-digest branch) disabled (`:568`) | met=True, 15/15 (survivor) — fixture scenario 10 "upstream serving unpinned bytes (M11)" is still caught by the stated-digest-vs-frozen-pin clause (`:560-561`), not by the served-bytes compare | tree-independent, skipped (§4) | **SURVIVOR** (coverage gap, §3.4) |
| m10 | fixture **want-lambda** scenario 15 → `lambda ok, c: True` (`:774`) | met=True; output **byte-identical** to baseline r01 (`diff` clean, `runs/r-m10-want-lambda-vacuous-tip.out`) | algebraically identical for all inputs: `hit = bool(want(ok,c)) and ok and …` and `bool(want_unmutated) ≡ ok`, so the mutated want can never change `hit` | **EQUIVALENT** (the want is defense-in-depth behind the inline `ok`/`bad`/`dropped`/`ok2` guards) |
| m11 | `CLASSES` tuple − `superseded` (`:167`) | exit 1, `bad=1` ("unknown class 'superseded'"), `fixture=0 (14/15)` | — | **KILLED** |
| m12 | ledger parse swaps `superseded`→`fixed` (`read_ledger`) | exit 1, `bad=1` (fixed's stem-extension check: `round-53-…` does not extend `round-52-…`), `fixture=0 (14/15)` | — | **KILLED** |

Tally: **7 killed** (m01, m02, m05, m06, m08*, m11, m12), **3 survivors** (m03, m04, m09), **2 equivalent** (m07, m10). (*m08 survives both assigned oracles and is killed only by the environment attack below.)

## 3. Killing cases for survivors / attack legs

### 3.1 m03 (replacement-resolves) — killing case documented, not run
Needs a state the assigned forged tree cannot reach (there R resolves, so the clause never fires): a tree where the original token is NOT cited at tip (still-cited passes), the replacement IS cited at tip but does NOT resolve (e.g. line anchor past EOF), and the replacement's unresolvedness is disclosed by its own `eof` row (else `undisclosed=1` masks the mutant anyway). Unmutated → bad=1 ("replacement … does not resolve at tip"); mutant → all legs clean → met=True. Building it requires a second forged tree + 2 runs; the 20-run cap was spent on the assigned probes. The clause is otherwise live code — reached at the honest tip every run (R resolves, clause passes).

### 3.2 m04 (base-cited) — killing case documented, not run
A superseded row whose token is NOT cited in that surface at the BASE tree (fabricated history). Unmutated → bad=1 ("superseded token was not cited in this surface at the base"); mutant → met=True (token absent at tip ⇒ nothing dropped, replacement fine). The assigned tree must have the token cited at base to isolate still-cited, so the two kills need different trees — a coverage finding: no built-in fixture scenario exercises a superseded row with an uncited-at-base token (scenario 15's base cites `tools/live.py`).

### 3.3 m08 (clean_env) — KILLED by environment attack (demonstrated)
- r18 control: `GIT_DIR=/nonexistent-m2c2mut-poison GIT_WORK_TREE=… python3 pristine.py …` → exit 0 `met=True` — the frozen strip (`:200`) neutralizes inherited redirection, as claimed (Sen4Fixture).
- r19 mutant: same poison + m08 → exit 2 `could-not-evaluate: git rev-parse …: fatal: not a git repository: '/nonexistent-m2c2mut-poison'` — with the strip gone the predicate run is unevaluatable. So the leg is load-bearing; it is simply not exercised by the two assigned oracles (no `GIT_*` in a clean run environment).

### 3.4 m09 (served-bytes digest compare) — coverage finding
The only oracle that reaches a served-bytes mismatch would be upstream serving different bytes at the frozen pin `704366d7…` while the surface states the correct pin digest. The fixture's M11 scenario (scenario 10) states the WRONG digest (schema's), so it is killed by the stated-vs-pin clause at `:560-561`, not by the mutated comparator; the lane tree's bytes still match. Not demonstrable without a fetch-intercepting fixture (out of scope for the assigned probes). Note the trunc-digest branch (`:570-572`) was NOT mutated (single-mutant discipline); it is likewise unreached by any scenario.

## 4. Run ledger (20 invocations, cap 20 — respected)

All runs: `python3 <script> --repo $S/lane --tip <T|F> --fleet /home/vgpnk/Projects/shokunin --fleet-rev 6c4aba34c2a22519152d8c6f32e1039eecb1381b` (fleet rev pinned to the frozen receipts' value to remove HEAD-drift as a confound).

| run | script | tip | exit |
|---|---|---|---|
| r01 | pristine | 9c60eae | 0 (met=True — matches frozen receipt) |
| r02 | pristine | c54fa71 (forged) | 1 (met=False, bad=1 still-cited) |
| r03–r14 | m01…m12 | 9c60eae | m01:0 m02:1 m03:0 m04:0 m05:1 m06:1 m07:0 m08:0 m09:0 m10:0 m11:1 m12:1 |
| r15–r17 | m01, m03, m04 | c54fa71 | m01:**0 (kill)** m03:1 m04:1 |
| r18/r19 | pristine / m08 + `GIT_DIR` poison | 9c60eae | 0 / **2 (kill)** |

Triage disclosure: m07/m08/m09 had no forged-tip run. Justification: each mutated line is provably tree-independent for these trees — m07's disclosed gate is unreachable when the forged row is bad (`elif why is not None` at `:640` precedes it); m08's `clean_env` never reads tree state; m09's upstream branch is never entered (no upstream rows; fixture behavior unchanged, proven at the tip run). m02's forged run is unreachable (fixture-leg crash). 12 mutants × 2 = 24 > 20, so forged runs were spent on every mutant whose mutated clause branches on citation state (m01, m03, m04).

## 5. Findings for the lane (coverage, not defects — counters are frozen)

1. **The superseded still-cited clause (m01) is defended only by the lane leg against a live tree.** The built-in fixture's forged-superseded tip re-points in prose (token NOT cited), so it exercises replacement-cited, never still-cited; without an external forged tree, m01 ships met=True. Proposed fixture extension (unified diff, NOT applied): `out/M2C2Mut/proposed-fixes.md` Fix A — make scenario 15's forged tip cite the old token again, so `(not ok2) and c2["bad"] == 1` fails under m01 at any tip.
2. **No scenario exercises a superseded row whose token was uncited at base (m04), nor a resolving-but-unresolved replacement (m03).** Fixes B/C in the same file propose scenarios for both.
3. **m02's kill mode is an uncaught TypeError** — it exits 1 (the not-met code) without a met line. A pipeline reading only exit codes still sees failure, but the counter's contract (verdict or could-not-evaluate) is bypassed; recorded, not fixed (frozen).
4. m07/m10 are redundant-guard equivalents: harmless, but they mean the disclosed-exclusion gate and the scenario-15 want-lambda carry no unique detection weight.

## 6. Restoration evidence

- Fleet counter before all runs: `d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c`; after all runs: `d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c` — byte-identical; `git -C <lane> status --porcelain` for `tools/round54-cited-path-check.py registry/cited-path-corrections.tsv` → empty (0 lines).
- The lane repo was never written: all mutants ran from `$S/pristine.py`/`$S/mutants/`; the forged commit exists only in my `--shared` clone (`$S/lane`), deleted at cleanup.
- No llama-server was started by this seat (`pgrep -af llama-server` after runs shows only sibling seat J5EnvNames's processes under `/fast/scratch/hyaku/kama-r55/w1/J5EnvNames/` — left untouched); no tracer wrapped any counter; no services started/stopped.
- No tool installs were needed (python3 3.14.8, git 2.56.0 present); scratch removed at the end.
