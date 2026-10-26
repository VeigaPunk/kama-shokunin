# V1Ctr — code review of the frozen C1 counter (round47-append-audit-v2-check.py)

Verdict: the fixture leg's oracle is genuinely independent (by construction, fail-safe) and the D1 `--` blind spot is now caught three independent ways, but the stable leg is vacuous as run (base==tip passes; a tool that ignores `--to` passes without ever measuring the base), the contract leg accepts a declared_at line that merely contains the substring `append` (even one that negates the rule), and the `round47` guard is a literal-string tripwire that a 30-line glob-import shim defeats — so the lane leg's restored_* equality remains tool-vs-counter-reimplementation outside the fixture's shapes, exactly the round-46 shared-definition family, disclosed in the prereg `limits` but overstated in the counter's own docstring. All findings were reproduced with minimal fixtures; none flips the round-47 C1 verdict on the current lane bytes (baseline `met=True` reproduces; the real contract's declaring lines are genuine declarations).

Reviewed bytes: `tools/round47-append-audit-v2-check.py` sha256 `a180ab84cc642731a6bd5fca92e5218dfaa6c074279e2f001110b348d73755ed` — equals `claims[C1].counter_sha256` in `.ufo/waves/round-47/preregistration.json` (frozen bytes confirmed). Tool under review at tip: `git show 3a09a1d93dcc16799cf6c4b48786e6440af134c4:tools/append-only-audit.py` (500 lines). All line refs below are to the counter unless prefixed `tool:`.

Baseline (my own shared clone, build commit):
```
S=/fast/scratch/hyaku/kama-r47/V1Ctr
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
python3 tools/round47-append-audit-v2-check.py --repo $S/lane \
  --tip 3a09a1d93dcc16799cf6c4b48786e6440af134c4 --scratch $S   # exit 0
→ selftest=1 contract=1 lane=1 fixture=1 stable=1 files=85 lane_events=5
  lane_mismatch=0 fixture_mismatch=0 met=True        (out/V1Ctr/baseline.out)
```
Matches the L1 pre-wave dry run. Every fixture below is a fresh `git init` repo under my scratch whose toplevel is asserted before the first commit; no lane or fleet path was written except my out directory.

---

## F1 (medium, latent on this lane) — contract leg: any line containing `append` declares the rule; no binding to the row's path or rule

`round47-append-audit-v2-check.py:293`:
```python
if k < 1 or k > len(flines) or "append" not in flines[k - 1].lower():
```
Any substring occurrence passes. The leg never checks that the declared line mentions the row's path/pattern or states the rule, so the prereg's semantics ("each row pointing at the lane line that declares the rule", C1 statement) are not what is enforced.

Evidence (`python3 drive.py t1 t1b`, out/V1Ctr/drive.out):
- `AGENTS.md:2` = "Full revision history: see the appendix at the end of this file." → declared_at check passes (no complaint in detail).
- `AGENTS.md:2` = "If a clone is damaged, re-append the missing entries from the backup." → passes.
- `AGENTS.md:2` = "LOG.md is NOT append-only; rewrite and prune it freely during cleanup." → passes (a line negating the rule satisfies the check).
- Control line without `append` → correctly flagged: `contract line 2: AGENTS.md:2 does not hold a line containing 'append'`.
- T1b: with the appendix line as the only declaring line and a `*` pattern row covering the five REQUIRED files plus a lessons file, the full leg returns `ok=True detail=[]`.

Grounding: the real contract at 3a09a1d has genuine declaring lines — README.md:16 "`LOG.md` — append-only round log", corpus/README.md:86 "Appended rather than inserted…", corpus/README.md:521, corpus/QUALITY.md:24, SKILL.md:578, corpus/lessons/round-23.md:100 "are append-only.", registry/history/DELTA.md:3 "# Append-only" — so this defect is latent here; it caps what `contract=1` proves rather than falsifying this round's verdict.

Proposed fix (counter is frozen; next round): require the declared line to contain `append-only` (or the rule token for `A`/`A-row`/`A-corr` families) and to reference the row's path or pattern; keep the case-insensitive compare.

## F2 (medium) — stable leg is vacuous: base==tip passes, and a tool that ignores `--to` passes without ever measuring the base

The leg (`round47-append-audit-v2-check.py:555-580`) runs the tool twice (base, tip), requires base events non-empty (`:571`) and each base event present at tip with equal `deleted` and `restored_max(tip) >= restored_max(base)` (`:577`). Both runs are tool-vs-tool; the counter never recomputes the base itself. `restored_max` monotonicity is a theorem of the v2 window definition, so the only failure it can catch is a tool whose base-run and tip-run are mutually inconsistent — and nothing forces the base run to measure the base.

Evidence (`python3 drive.py t2 t2b`, out/V1Ctr/drive.out):
- T2, `--base == --tip` (same commit twice, one real unrestored event, genuine v2 tool): `selftest=1 contract=0 lane=1 fixture=1 stable=1 … met=False` — `stable=1` with the equalities holding by construction. There is no base≠tip or ancestry guard.
- T2b, tool that rewrites `--to X` to `--to HEAD` (prelude prepended to a faithful engine): asked `--to e454f378a420` (the base), it answered `"to": "332b00c311de…"` (the tip) — the base commit was never evaluated — and the counter printed `lane=1 … stable=1`.
- The non-empty guard does fire: a repo with no ≥20-line deletion gives `stable: no event at base` (observed in an intermediate run).

Proposed fix: cross-check the base run against the counter's own `recompute(repo, base, files)` (already implemented and cheap), and reject `base == tip` (or require `git merge-base --is-ancestor base tip`).

## F3 (medium-low; partially disclosed) — lane leg equality is tool-vs-reimplementation; the `round47` guard does not establish independence

`leg_lane` (`:365-391`) compares the tool's events with this counter's `recompute` (`:348` `compare`), and its only independence device is `:367` `if b"round47" in fh.read()`, backing the docstring claim (`:71-72`) "the tool's source at --tip must not contain the string `round47`, so it cannot load this counter's recomputation".

Evidence (`python3 drive.py t3a t3b`, out/V1Ctr/drive.out):
- T3a: a tool that is a verbatim copy of the counter's own `recompute`/`deleted_lines`/`numstat`/`contract_files` with a CLI shell (out/V1Ctr/clone_tool.py; asserted free of the literal `round47`) → `selftest=1 contract=0 lane=1 fixture=1 stable=1 lane_mismatch=0`. Definitionally identical tool, lane leg cannot tell.
- T3b: a 30-line shim (out/V1Ctr/shim_tool.py) that globs `*/tools/*append-audit-v2-check.py`, imports the frozen counter module via importlib and delegates `contract_files`+`recompute` to it → `lane=1 lane_mismatch=0`. The docstring's "cannot load this counter's recomputation" is falsified; the guard is a tripwire against the literal string only (also bypassable by `"round"+"47"`).

What does give the lane leg teeth — verified, not assumed:
- `deleted` is anchored to `git diff --numstat` inside `recompute` (`:196` parse, `:221-222` raise on disagreement). Positive control T4 (v1-style mutant: drop deleted lines whose text starts with `-`, numstat cross-check removed; out/V1Ctr/mutant_dashfilter.py) → `lane=0 lane_mismatch=2` (recompute 25 vs mutant 22 on a 25-line deletion containing three `--meta` lines), i.e. the exact round-46 D1 shape is caught at lane level.
- The fixture leg catches the same mutant by construction alone: `fixture=0 fixture_mismatch=2` (constructed 26 vs mutant 21), and the tool's own selftest also fails (`selftest=0`, `AOA_SELFTEST pass=14 fail=1`).

Residual risk (disclosed, but sharper than the disclosure): the prereg `limits` says "The counter's recomputation and the tool share the v2 definition by contract; ground truth independent of both is git numstat (deleted) and the fixture's construction (all fields)." True — and it means for any input shape outside the fixture's eight classes and outside numstat's anchoring (deleted counts only), `restored_max/restored_best/restored_by/status` on the lane are the tool agreeing with a re-implementation of the same definition. That is the round-46 blind-spot family reduced, not eliminated.

Proposed fix: report-only for the frozen counter — reword docstring lines 71-72 to "must not name this counter" (drop the "cannot load" inference). Next round: derive at least one lane restored_* value from a constructed (not recomputed) answer, as the fixture leg does.

## F4 (low-medium, undisclosed) — binary deletions are invisible to both sides

`numstat` skips any row whose deletions column is not a digit (`:196`), and `git diff --numstat` prints `-` for binary files; the tool has the same skip (`tool:165-173`). The docstring defines `deleted` via numstat with no binary exemption.

Evidence (`python3 drive.py f6`, out/V1Ctr/drive.out): a file with 30 NUL-containing lines wholly deleted → `git diff --numstat` = `-	-	data.bin`; `ctr.recompute(...)` → `[]` (no event). Text control with the same shape → the expected `deleted=30 unrestored` event. So a contract-declared file that flips to binary and loses ≥20 lines is silently unaudited by tool and counter alike.

Lane impact today: none — every declared file is `.md`/`.tsv` text. Proposed fix: state the binary exemption in the tool contract (docstring + selftest case), or make the tool emit an explicit skipped-binary marker instead of silence.

## F5 (no defect) — fixture oracle independence, answered directly (assigned question 1)

The fixture leg is sound by construction and fail-safe:
- The tool is compared against `exp` built in `build_fixture` (`:394-513`) from sampled indices and lengths (`k1 = rnd.randint(22, 30)`, `:454-456` where `len(must)=9` is disjoint from `plain_idx`, `r1 = len(back)`, the 21-line relocation, the 19-line non-event) — answers known before any tool runs, with the required adversarial shapes (`--`, `---`, CRLF vs LF copy, triplicated, no-final-newline, window-max survival, below-threshold, undeclared file).
- `recompute` appears only as a self-check that RAISES on disagreement with construction (`:523-526`), so a construction bug fails the leg (`fixture: build failed`) — it can never convert a construction bug into a pass.
- Empirical: the T4 mutant is caught by construction (`fixture_mismatch=2`) even though the mutant agrees with recompute's definition family — the oracle is not the recompute. Dozens of fresh randomized fixtures were built across my runs; every healthy-tool run gave `fixture=1 fixture_mismatch=0`.

## F6 (notes, no single defect)

- The selftest leg attests the tool's own claim (`:342`, `pass>=10 fail=0`): both T3 mutants printed a fake `AOA_SELFTEST pass=10 fail=0` and got `selftest=1`. Inherent to a selftest leg; worth one line in the prereg's `limits` next time.
- A `*`-pattern contract can declare itself: the expansion includes `registry/append-only-contract.tsv` and `AGENTS.md` (T1b output). Cosmetic today.
- If `recompute`'s own hunk parse ever disagrees with numstat (`:221-222`) the counter exits 2 (could-not-evaluate) rather than failing a leg — by design, but a novel git-diff shape suspends measurement instead of scoring the tool.

---

## Assigned questions, one line each

1. Fixture oracle independent? Yes — construction (`exp`), with `recompute` only as a raising self-check; proven by the T4 mutant being caught by construction alone (F5).
2. Stable leg vacuous? Yes — `base==tip` passes (T2) and a `--to`-ignoring tool passes with the base never measured (T2b); empty base events are guarded, equality is not (F2).
3. Contract leg 'append' substring? Yes — "appendix", "re-append", and a line negating the rule all pass; no path/rule binding (T1/T1b, F1); latent on this lane because the real declaring lines are genuine.
4. Lane leg shared-definition dependence? Structurally yes — clone (T3a) and glob-import shim (T3b) both get `lane=1`; mitigated by numstat anchoring and the fixture for the D1 shape (T4), residual for everything else; prereg discloses the shared definition, docstring overstates the guard (F3).
5. `round47` guard meaningful? As a literal-string tripwire only; bypassed in 30 lines without the string (T3b); docstring claim it enforces ("cannot load this counter's recomputation") is false as stated (F3).

Residual risk / verification gaps: I reviewed C1 only (not C2); mutant coverage is the D1 shape plus `--to` handling — a shared-definition bug in a shape absent from both the fixture classes and the lane's 5 events would still pass all five legs; T2b's demonstration runs the tool directly on the fixture repo (HEAD==tip), which is exactly how the counter invokes it. No tools were installed or upgraded (none needed); no pacman transactions; one shared read-only clone; scratch removed after artifact copy.

Artifacts: out/V1Ctr/{drive.py,drive.out,clone_tool.py,shim_tool.py,mutant_dashfilter.py,baseline.out} — `drive.py t1 t1b t2 t3a t3b t2b t4 f6` reproduces every run above from any cwd.
