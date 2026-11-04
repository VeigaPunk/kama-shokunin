# CR01 — falsification: round-82 claims, predicates, controls (kama, w1)

Tip `bacae072` (`git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master`). All runs in scratch clones under `$S=/fast/scratch/hyaku/kama-r82/CR01FalsifyClaims`, toplevel asserted per clone, `PYTHONDONTWRITEBYTECODE=1`; `$S` deleted. Lane read-only; no tool installs needed.

| claim | target line at tip | do-nothing control | verdict |
|---|---|---|---|
| C1 | `SELFRECORD_R81 claims=6 mismatches=0 corrected=5 unbacked=0` rc 0 | `--no-corrections` → `mismatches=5` rc 1; `--enumerate` → `stale=5` rc 1 | verified only under the recorded base-bound F2 reading; plan-literal reading **red** |
| C2.1 | `LATE_DELTA round=82 base=aaf974dbd3b6 population=103 carried=88 new=15 bad=0` rc 0 | base register → `carried=88 new=15 bad=15` rc 1 | verified; before receipt unreproducible |
| C2.2 | `APPEND_DEBT … late=15 pending=2 unaccepted=0 bad_rows=0 …` rc 0 | base → `late=10 unaccepted=5` rc 1; empty → `unaccepted=15` rc 1 | verified; repaired instrument, rule text byte-identical |

## 1 — do-nothing reachability
- C1 control: `python3 tools/round82-selfrecord-round81.py --repo . --no-corrections` → `mismatches=5 corrected=0 unbacked=0`, **rc 1**. Receipt `control/c1-no-corrections.out` prints `EXIT=0` — that is `tail`'s status, not Python's; `before/c1-enum.out` has the same pipeline artefact (real rc 1).
- C1 cheaper skip: revert SCORECARD+LOG to base and repoint the five `fix=` at the lesson itself → **exact target line, rc 0** (1.2 s). The target line does not evidence the SCORECARD/LOG appends; the frozen "fix path's tip bytes contain" admits self-reference, and admits `…=44` for `new=…=4`.
- C1 strongest: the predicate says the fact "matches the same fact re-derived at the graded tip" and the witness cell "the tip registry row count (302)". At tip the count is **305** (`grep -cE '^ {0,3}\|[ \t]*S[0-9]{3,}\b' corpus/SOURCES.md`). Only changing `read("BASE")`→`read("TIP")` yields `F2 unbacked-correction … witness=log81-frontier-rows=305`, `mismatches=1 unbacked=1`, rc 1.
- C2 controls: base register at `bfdd7a70` + tip instruments → leg1 `carried=88 new=15 bad=15` rc 1; leg2 `late=10 unaccepted=5 bad_rows=0` rc 1 (identical with the tree's own pre-repair module). Empty register → `unaccepted=15` rc 1. Target unreachable without the 15 rows.
- C2 control 4: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/measured/control/c2-gate-arm-freeze-tip.out` (`pre-report-gate.py --repo . --round 82 --tip HEAD`) is red (`PRE_REPORT round=82 arms=11 failed=3`, `EXIT=1`) and carries the debt leg's `unaccepted=5`; but the freeze tip has only **11 arms**, so it cannot exercise the round-82 arm — the red is arm 8's debt leg, and the plan's literal "the gate's round-82 instrument arm" is unrealizable there.
- C2.1 before receipt is unreproducible twice: `# rev: bfdd7a70` contains no round-82 tool (`git ls-tree bfdd7a70 tools/ | grep -c round82` → 0), and with the tip tool that rev prints `new=15`, not the receipt's `new=0`; at `b0064016` (the only committed rev with the tool) the rows are already present → `bad=0`.

## 2 — instruments the round modified
- C2.2 module: `tools/round81-append-debt.py` changed 70 lines at `5fe3c58c` → **not byte-intact**, contrary to the plan's "byte-frozen module" and "counter stay byte-intact". Rule text: bytes 1–32 `diff` empty, and `plans/round-81-claims.md:80` says "row whose introducing commit" → the repair aligns code to predicate, not predicate to code.
- Disclosed: docstring `ROW-INTRODUCTION REPAIR`, lesson §Freeze divergences 3, `LOG.md:3441`. Red-before reproduces at `b0064016`: `bad_rows=15 unaccepted=5`, 30 findings, rc 1.
- Independent of that module: `git blame` puts all 15 new rows at `b0064016`, and every introducing commit is a **strict descendant** of its event (15/15). Admissible only with this re-derivation — the repair is author-performed after the data and decisive (15→0).
- C1's F2 binding was changed after data (`a251cbab`, "freeze divergence 5"), disclosed in the lesson; but `SCORECARD.md:4958` still says "the tip registry holds 302" while the tip holds 305.

## 3 — axes harmed
- Append-only (operability): two **graded** deletions in SCORECARD's non-exempt surface → `pending=2` on the round's own line:
  `962bd251`: `-**Current authority (round 81):** …` (the four head rows in the same hunk are exempt).
  `a251cbab`: `-| C1 — the round-81 self-record's six declared facts … |` (round-82 claim row, dated section).
- The plan's "every edit to an append-only file is an append" is false, refuted by its own `pending=2`. Head rows/SKILL are exempt or not contract-covered; SKILL reads twelve arms where the plan's record-fix says "eleven" (execution divergence, no predicate impact).

## 4 — prediction for round 83
Round-82's C1 green cannot survive the next non-author closure: F4 is tip-bound, so at any tip carrying `corpus/lessons/round-83-verifier-spotcheck.md` the counter prints `F4 unbacked-correction … witness=calib81-newest-closure=round-83-verifier-spotcheck.md`, `mismatches=1`, rc 1. Refutation: clone, add that file, rerun the exact command; exit 0 refutes (1.7 s, ran: rc 1).

## Residual risks a closure must weigh
- C1: a correction outside `## Corrections` is ignored (`unbacked=0`) although the predicate calls it `unbacked` — latent (all five blocks are inside), but the selftest encodes the looser rule.
- C1: witnesses F1/F3/F5/F6 are read at the **tip** from mutable receipts; tip-only receipt edits move the witness and can zero the answer.
- C2: `--late FILE` is unbound (freeze divergence 1) — every row reports `unbound-register`; controls must use the default path.
- `registry/append-only-late-r82.tsv` is a byte-identical, unread duplicate (freeze divergence 2): two authorities, one checked.
- `after/c1-json.out` is truncated, invalid JSON (33 lines) and records a red state (`mismatches=1`) at `962bd251` under `after/`; re-derivable only by rerunning that rev.

## Receipts (absolute path; command; exit)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/measured/after/c1-green.out` — `python3 tools/round82-selfrecord-round81.py --repo .` @bacae072 → rc 0 (reproduced in lane).
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/measured/control/c1-no-corrections.out` — same `--no-corrections` → real rc 1 (receipt prints EXIT=0).
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/measured/before/c1-enum.out` — `--enumerate` → `stale=5`, rc 1.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/measured/defects/c2-debt-register-level-before.out` — `round81-append-debt.py --repo . --round 82` @b0064016 → `bad_rows=15`, rc 1 (reproduced).
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/measured/after/c2-late-delta.out` / `after/c2-debt.out` — @bacae072 → rc 0, `bad=0` / `pending=2` (reproduced).
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/measured/before/c2-late-delta-base.out` — not reproducible at its named rev (tool absent; `new=15` ≠ receipt `new=0`).
