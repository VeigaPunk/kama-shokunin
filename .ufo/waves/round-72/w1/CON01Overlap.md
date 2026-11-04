# CON01Overlap — scoped findings (kama round 72, w1, connector, axis adjacency)

Read-only scan. kama record surfaces read at `HEAD = a3cc39f0`; siblings read from
`/home/vgpnk/Projects/shokunin/*-shokunin/{tools,SKILL.md}`; no sibling gate executed, no lane file
edited. Full evidence tables, exit maps and commands: `w1/CON01Overlap/overlap.md`.

## Prior art — receipt → revision / tip binding (C2)

| lane / path | one-line predicate |
|---|---|
| tameshi `tools/receipt-revision-gate.py` (`SKILL.md:1547`) | every receipt carries one distinct `rev=`, equal to `--certified` (or byte-identical over `--paths`); `control` tokens ancestor-or-equal; codes `RECEIPT_*`; exit `0`/`3`/`2`/`1` |
| tameshi `tools/receipt-commit-bind.py` (unregistered) | a commit message naming an evidence/`tools/` path must carry or resolve it in that commit's tree; empty population = exit 2, never green |
| tameshi `tools/receipt-window.py` (`SKILL.md:2196`) | receipt needs unique id + 64-hex instrument sha + aware interval; frozen-bytes receipts must end before the edit window starts; exit `0`/`1`/`2`/`64` |
| kotodama `tools/check-receipt-seq.py` (unregistered) | `stamped == evaluated == measured` rev, tree oid, counter sha; `--lands` reads committed bytes and prints `moved_past=True` as a **flag, never a verdict change**; exit `0`/`1`/`2` |
| souji `census/round-57/c2-counter.py` (`SKILL.md:765`) | every receipt binds a durable full-40 `rev=`, `EXIT=`, matching `instrument_sha256=`; `KEEP-ONLY` for `refs/jj`; selftest `FALSE-GREEN-REJECTED` |
| chousa `tools/receipt-pin.py` (`SKILL.md:159`) | header `REVISION=` equals `--revision` and `SHA256=` equals the blob at `REVISION:PATH`; exit `0`/`1`/`2` |
| tsukuroi `tools/check-cited-receipts-r62.py` (`SKILL.md:5371`) | every `.ufo/waves/round-N/…` path named by any tracked blob at REV exists as a blob at the **same** REV; exit `0`/`1`/`2` |
| mado `tools/mado-receipt-citecheck.py` (unregistered) | caller-named artifacts' citations resolve in `ls-tree -r <rev>`; top-anchored fail-closed grammar; exit `0`/`1`/`2` |
| kama `tools/round68-receipt-pointer-audit.py` (in-lane) | section-relative `measured/` pointers resolve at `--rev`, brace/glob expansions, append-only ledger; exit `0`/`1`/`2` |
| tsukuroi `tools/check-revision-binding.py` + `_revision.py` (`SKILL.md:1902`) | every gate's `--revision` binds identically (`E-REVISION-INVALID`/`NOT-LANDED`/`NOT-PUSHED`); exit `0`/`1`/`2` |

**Verdict for C2:** tameshi owns the *binding*; kotodama computes the *tip* question and refuses to
grade it; souji-r57 owns *durability*; no sibling makes `rev..tip` a verdict. C2's originality is the
instrument-input allow-list over the delta — that leg has no prior art and cannot be adopted.

## Prior art — pre-report aggregation (C1, aggregation half)

| lane / path | one-line predicate |
|---|---|
| souji `tools/souji-pre-report-gate.sh` (`SKILL.md:256`) | tip==remote, report non-empty, one `## SHONEN`, **whole-lane** porcelain clean, prereg present; `--contract` refuses vacuous success; exit `0`/`1`/`2` |
| kasegi `corpus/instruments/r46-landing-gate.py` (`SKILL.md:1163`) | pre: tree-clean/jj-state/remote-tip/placeholders; post: report-readable, cited hashes resolve, ancestor, **final-is-tip**, date order, SHONEN; exit `0`/`1` |
| tsukuroi `tools/check-seat-scope.py` (`SKILL.md:1901`) | seat `Scope:` trailers; non-`none` needs `EXEC-AUTHORIZED`; counts are declarations, never verified executions; exit `0`/`1`/`2` |
| souji `tools/souji-landing-gate.py` (`SKILL.md:229`) | registry scripts parse, pins match committed bytes, seat failures carried to the lesson; exit `0`/`1`/`2` |

## Prior art — round scope / cleanliness / ignored / whole-tree (C1, scope half)

| lane / path | one-line predicate |
|---|---|
| kaidoku `tools/round-42/prefile-gate.py` (`SKILL.md:1804`) | waves settled; `status -z` clean under **four** round scopes; no stray `*.err`; lesson pointers resolve at HEAD; `--ignored=matching` residue **advisory only**; exit `0`/`1`/`2`, but a non-work-tree root exits `1` "although nothing was evaluated" (do not copy that) |
| kaidoku `tools/round-29/prefile-check.sh` (`SKILL.md:1363`) | whole-tree `git status --porcelain` empty plus two freeze gates; known limit "cannot see a still-running seat"; exit `0`/`1`/`2` |
| kaidoku `tools/round-45/frozen-path-preflight.py` (`SKILL.md:1761`) | no commit in FREEZE..REV touches a frozen pathspec (`-m --diff-merges=first-parent`), plus restored/blob/dirty/pathspec arms; exit `0`/`1`/`2` |
| mori `tools/mori-unlanded-check.py` (`SKILL.md:973`) | round-scoped unlanded over wave dir + `corpus/` + `tools/` + top-level `*.md`; **`.scratch/` and git-ignored paths excluded on purpose**; exit `0`/`1`/`2` |
| mori `tools/mori-index-clean.sh` (`SKILL.md:904`) | staged/intent-to-add fail; refuses a verdict on porcelain v1/v2 disagreement; exit `0`/`1`/`2` |
| souji `tools/souji-fleet-root-census.py` (`SKILL.md:675`) | top-level kind/tracked/ignored via `check-ignore --no-index`, never a listing (would walk protected subtrees) |
| souji `souji-verify.sh` / `cand-*.sh` | `status --porcelain -uall --ignored=matching -- <target>` as destructive-op precondition |
| kama `tools/round67-worktree-landing-check.py` (`SKILL.md:1709`) | declared paths' worktree bytes equal HEAD blob; exit `0`/`1`/`2` (in-lane, do not duplicate) |

**Adopt / re-derive / do not duplicate:** adopt kaidoku-r42's multi-scope pathspec + `-z`, mori's v1/v2
refusal, souji's FALSE-GREEN fixture and "printed FAIL with exit 0" rule, kasegi's final-is-tip arm;
**re-derive** the *graded* ignored class (kaidoku detects it but exits neutral) and C2's allow-list;
do not duplicate kama's own arms 1-5/`round67`/`round68` or souji/tsukuroi granular gates.
Registry hygiene: kotodama `check-receipt-seq.py`, mado `mado-receipt-citecheck.py` and tameshi
`receipt-commit-bind.py` have no `SKILL.md` row — C1/C2 must register, including exit `2`.

## Inherited-defect disposition (one line each)

Round-71 spot-check §8:
1. C2 selftest tally false (`pass=8` / `pass=19` / "19 arms" vs true `pass=18`) — **OPEN**; no r72 seat owns it; `SKILL.md:310` still reads `pass=19 fail=0` at HEAD, and SCR03 rewrites that same row for item 2.
2. C2 registry row omits exit `2` — **CLOSED by r72 SCR03** (prompt names "round-71 routed defect 2").
3. `LOG.md` depth anchor stale (`0b61e118…` vs `7ff94d67…`) — **CLOSED by r72 SCR03** (appended correction, defect 3).
4. C1 receipt described as "at the report tip" (`4b284653` header) — **CLASS CLOSED by C2**; instance is historical in the fleet report (unwritable). C2 would grade r71 green: the later commits touch `.ufo/waves/**` + `corpus/lessons/**`, both record paths.
5. Coverage map has no `knowledge/pre-report-gate.md` row — **CLOSED by r72 SCR02(b)**; verified open at HEAD: `git show HEAD:corpus/README.md | grep -c pre-report-gate` → `0`.

Round-71 lesson survivors:
- C1 S1 wrong `--round` vacuous green — **closed in kind by C1** (case `label`).
- C1 S2 round work outside the wave dir invisible — **closed in kind by C1** (case `stray`).
- C1 S3 git-ignored file inside the wave dir invisible — **closed in kind by C1** (case `ignored`).
- C2 `m7` (`waiver_keeps_not_evaluated` forced true, no isolating fixture) — **OPEN**.
- C3 `m6` (correction-date guard, no fixture) — **OPEN**.
- C3 `iv` (duplicated tag paragraph reads as a false red) — **OPEN**.
- C1 "Ceiling" (a child arm exiting 0 on an unevaluable state still reads green) — **not closed** by C1's predicate; remains a limit of the other five arms.

## Second-order findings the round must decide (details in `overlap.md` §5)

1. **Merge blindness.** `git log -1 --name-only <merge>` = 1 line (subject only); `git diff-tree -m --name-only --no-commit-id` = 8 and 2 lines on kama's two merges. C2's "every commit in `rev..tip`" arm needs `--diff-merges=first-parent` or it grades a merge vacuously (kaidoku routed this as `R45-CL6`).
2. **"git-ignored" disagrees by tool.** On a tracked path matching an ignore glob: `status --ignored=matching` and `check-ignore` (index-aware) say nothing; `check-ignore --no-index` reports it. The builder must declare which spelling answers C1 case C.
3. **Ignored finding count is mode-dependent.** `--ignored=matching` reports an ignored directory as one record; `--ignored=traditional` reports its files (3 vs 4 records in the fixture). `findings=<f>` therefore needs the mode stated.
4. **C2's before-control receipts are headerless** (`BINDING_CONTROL …`, `SCOPE_CONTROL base_rev=…`). Cited from `SCORECARD.md`'s round-72 section or `corpus/lessons/round-72.md`, they grade `unbound` — keep those citations in `plans/` (not a scanned surface) or declare the red line.
5. **`corpus/QUALITY.md` is in neither frozen list** (not a record path, not an instrument input) and SCR02(c) writes it → that commit is `shifted`. Likewise SCR01/SCR02/SCR03's `corpus/SOURCES.md` / `corpus/knowledge/**` / `SKILL.md` writes. Actionable sequencing: instrument inputs first, scored receipts next, record-path commits last (r71's receipts at `4b284653` were taken after its instrument commits).
6. **C1 case A is red at the stated base revision**: `git cat-file -e d30a8696:plans/round-72-claims.md` → rc 128; at `090a0b25` → rc 0. The arm was measured at ≥ the freeze commit; the report must say which.
7. **C1's "declared record allow-list" is unenumerated** (C2 enumerates both lists). Only the reading that *includes* `.ufo/waves/round-<N>/**` closes r71 defect (ii) without duplicating arm 5; case C stays absolute regardless.

## Sibling that owns a `receipt-tip`-shaped gate

**tameshi** (`tools/receipt-revision-gate.py`, `SKILL.md:1547`) owns receipt→revision binding;
**kotodama** (`check-receipt-seq.py`) computes the tip question and keeps it a flag; **kaidoku**
(`frozen-path-preflight.py`) owns the delta-sweep method; **souji** (`census/round-57/c2-counter.py`)
owns durability + instrument pins. Kama would be first to make the tip-delta a verdict. A
ready-to-paste replacement bullet for `corpus/knowledge/cross-lane-scope.md` §"Overlap rules —
round 71" is in `overlap.md` §4, for the L1 to apply (this seat wrote no lane file).

## Files written

- `.ufo/waves/round-72/w1/CON01Overlap/overlap.md` (full scan, tables, commands, limits)
- `.ufo/waves/round-72/w1/CON01Overlap.md` (this scoped summary)

Scratch `/fast/scratch/hyaku/kama-r72/CON01Overlap` removed before yield.
