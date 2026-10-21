# MistakeSweep (KamaR21.MistakeSweep-6) — executed command ledger

Lane pin: `a29bb84abbb8b4d328f5970a89e448330a3a42ac`, read from a scratch clone
`/tmp/kama-r21-MistakeSweep/lane` (checked out at that commit; deleted at the end).
Scratch guard copies: `/tmp/kama-r21-MistakeSweep/mut/` (`base.py`, `mutA_exit0.py`,
`mutB_casefold.py`, `mutC_opened_skip.py`; each mutant is one edit of `base.py`
via the edit tool). `OUT` = this directory. Host python3 = 3.14.8.
No tool installed or updated. No lane tracked file written.

| ID | Command (abridged) | Exit | Observed |
|---|---|---|---|
| R01 | `git clone -q …/kama-shokunin <scratch>/lane && git -C <scratch>/lane checkout -q a29bb84…` | 0 | HEAD a29bb84 |
| R02 | `python3 mut/base.py --selftest` | 0 | `42/42 selftest cases passed` |
| R03 | `python3 mut/mutA_exit0.py --selftest` (run_check returns 0) | 0 | `42/42` — survives |
| R04 | `python3 mut/mutB_casefold.py --selftest` (casefold compare) | 0 | `42/42` — survives |
| R05 | `python3 mut/mutC_opened_skip.py --selftest` (opened not compared) | 1 | `40/42`, 2 FAIL lines — killed |
| R06 | `python3 mut/base.py --repo <lane> --from b8e485c --to ccc4bb3` | 1 | `VIOLATION S041: cell anchor changed in place` |
| R07 | `python3 mut/mutA_exit0.py --repo <lane> --from b8e485c --to ccc4bb3` | 0 | same VIOLATION line printed, exit 0 |
| R08 | `python3 tools/citation-provenance.py` (scratch lane, no flags) | 0 | `required=17 docs_unreadable=0 found=17 verified=17 missing=0 mismatch=0 off_ref=0` |
| R09 | `git show --numstat --format='%h %s' 30ed378 -- corpus/lessons/round-18.md` | 0 | `1 1` (one line rewritten) |
| R10 | `git show --numstat --format='%h %s' 33a6777 -- corpus/lessons/round-18.md` | 0 | `57 0` (append only) |
| R11 | `grep -rniE "reread\|load order\|protocol-load\|load receipt" tools tests` | 1 | no match |
| R12 | `grep -rln "interactive-sessions" tools tests SKILL.md AGENTS.md corpus/QUALITY.md corpus/README.md` | 1 | no match |
| R13 | `git show a29bb84:corpus/SOURCES.md \| sed -n '216,224p'` | 0 | S051 clarification at lines 218–223; "records footer-only live-page drift" on 223 |
| R14 | `python3 $OUT/bound_scan.py $OUT/fixtures/bound_positive.txt` | 1 | 4 violations (interactive-sessions; ~/.omp + ~/.config; measure.py; check-receipt --selftest) |
| R15 | `python3 $OUT/bound_scan.py $OUT/fixtures/bound_negative.txt` | 0 | 3 commands, 0 violations |
| R16 | `python3 $OUT/kq22_killer.py mut/base.py` | 0 | `3/3 killer cases passed` |
| R17 | `python3 $OUT/kq22_killer.py mut/mutA_exit0.py` | 1 | `1/3` (case-only and real edits exit 0) |
| R18 | `python3 $OUT/kq22_killer.py mut/mutB_casefold.py` | 1 | `2/3` (case-only edit exits 0) |
| R19 | `python3 $OUT/kq22_killer.py mut/mutC_opened_skip.py` | 0 | `3/3` (not targeted by killer; killed by R05) |
| R20 | `python3 $OUT/append_only_lines.py --repo <lane> --from '30ed378^' --to 30ed378 --path corpus/lessons/round-18.md` | 1 | `VIOLATION … 1 line(s) deleted or rewritten (+1)` |
| R21 | `python3 $OUT/append_only_lines.py --repo <lane> --from '33a6777^' --to 33a6777 --path corpus/lessons/round-18.md` | 0 | `ok … +57 -0` |
| R22 | `python3 $OUT/pointer_check.py --repo <lane> --rev a29bb84 --file corpus/SOURCES.md --range 210-215 --anchor 'records footer-only live-page drift'` | 1 | `STALE` |
| R23 | same, `--range 217-222` | 1 | `STALE` (line 223 outside range) |
| R24 | same, `--range 218-223` | 0 | `ok` |
| R25 | `--range 217-222 --anchor 'S051 identity-label clarification'` | 0 | `ok` (heading-only anchor passes) |
| R26 | `python3 $OUT/count_sweep.py --repo <lane> $OUT/fixtures/count_fixture.md` | 1 | `4 count token(s), 2 violation(s)` (line 2 unbound; line 4 `required=3@a29bb84` vs 17) |
| R27 | `python3 $OUT/count_sweep.py --repo <lane> corpus/lessons/round-19.md corpus/lessons/round-19-verifier-spotcheck.md SCORECARD.md LOG.md` (cwd scratch lane) | 1 | `11 count token(s), 11 violation(s)` — all unbound on their own line |
| R28 | `git show 028235e:registry/required-citations.json \| python3 -c 'import json,sys;print(len(json.load(sys.stdin)))'` | 0 | `4` |
| R29 | same at `a29bb84` | 0 | `17` |
| R30 | `timeout 5 python3 $OUT/hang_stub.py` | 124 | stub bound; `shutdown()` never returns |
| R31 | `timeout 10 python3 $OUT/hang_bounded.py` | 2 | `VIOLATION: stub never served; shutdown() still blocked after 3 s` |
| R32 | `timeout 10 python3 $OUT/hang_bounded.py --serve` (control) | 0 | `shutdown returned within 3 s` |
| R33 | `python3 $OUT/residue_gate.py --glob 'kama-r*'` | 1 | `48 residue entries` (other seats' live scratch at run time) |
| R34 | `python3 $OUT/residue_gate.py --root <empty dir>` | 0 | `0 residue entries` |
| R35 | `pgrep -af 'hang_stub\|hang_bounded'` | 1 | none running after R30–R32 |
| R36 | `grep -nE "models_cap_status != 200\|version < minimum\|isinstance\(evaluated, bool\)" tests/llamacpp-live/check-receipt.py` (scratch, a29bb84) | 0 | lines 919, 1030, 1056, 2347 (pristine survivor sites) |
| R37 | `grep -c '201' tests/llamacpp-live/check-receipt.py` (scratch) | 1 | count 0 — no 201 status case in the gate selftest |
| R38 | `grep -nE "reversed\\(entries\\)\|all\\(isinstance" .ufo/waves/round-18/dispatch-provenance.py` (scratch) | 0 | lines 362, 430 (pristine) |
| R39 | python: `json.load` of `.ufo/waves/round-18/runs/c2-survivors.json` vs `.stdout`; compare `results` | 0 | top-level keys equal; `results` lengths 5/5; `results equal: False` |
| R40 | `python3 --version` | 0 | `Python 3.14.8` |
| R41 | `git -C <lane> diff --name-only` (read-only, the lane tree, not the scratch clone) | 0 | lists `tools/kama-llamacpp-live.py` — a concurrent round-21 change not made by this seat; not analysed |
| R42 | `sha256sum .ufo/waves/round-18/runs/c2-survivors.json .ufo/waves/round-18/runs/c2-survivors.stdout` (scratch) | 0 | `8cc59a65…2f13`, `ea2e3e02…f272` |
| R43 | `grep -n serve_forever tests/probe-verdicts/check.py` (scratch) | 0 | lines 459, 461 (root-cause patch present) |

Not run (stated so): no lane gate or official counter; no `--selftest` of
`tools/citation-provenance.py` (it writes only inside its selftest temp dirs);
no live llama-server, probe or download. Round-18 falsify seat reports were read
(not re-run): `.ufo/waves/round-18/falsify/advice/{AppendCells,FreshAppend,FreshGate}.md`.
