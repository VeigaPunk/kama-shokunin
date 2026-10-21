VERDICT: partial - official C2 argv is `--json` only and matches commands.json, run.py and the measured row; the `--out PATH` declaration row (SCORECARD.md:755) is still in place, and the erratum's "pre-official corrected run ... the two agree" needs qualifying.

# ScorecardErratum — round-19 advice

Scope: SCORECARD.md C2 declaration (:753-760), measured row (:782), erratum (:809-813); `runs/commands.json` `c2-survivors`. Work copy: `/tmp/kama-r19-ScorecardErratum` (lane untouched; copy SCORECARD.md `cmp` lane SCORECARD.md, exit 0). Receipts: `/tmp/kama-r19-ScorecardErratum/out/` (`RECEIPT.md` lists each command with its exit). Installs/updates: none.

## Confirmed
1. Official argv: `["/usr/bin/python3", ".../round-18/c2/survivors.py", "--json"]`, cwd lane, expected 0, observed 0, `as_expected` true (`commands.json` `c2-survivors`, measured_commit eb78788b). `run.py:88` is the same argv; its comment (:86-87) says `--out` is exclusive-create by design. Measured row :782 and erratum :810 state the same argv.
2. Digests: stdout `ea2e3e02…` = `runs/c2-survivors.stdout` (sha256sum, exit 0); stderr `9c6269b6…` = `c2-survivors.stderr`. `git show 1b85a24:.ufo/waves/round-18/runs/c2-survivors.stdout | sha256sum` = `ea2e3e02…` (exit 0), so the cite at round-18.md:421 and registry row `c2-official-stdout` resolve.
3. Official document (python, exit 0): 15 named (a6 b3 c2 d1 e3); before survived 11 / miscount 1 / accepted 3 → after killed 11 / correct 1 / handled 3; inconclusive 0/0; own_faults []; 15/15 witnesses matched; 22/22 recorded input hashes equal the copy's bytes; tool `ac934794…` = HEAD blob (`git show HEAD:…survivors.py | sha256sum`, exit 0).
4. `--out` is optional and never clobbers. Refusal happens before measurement (`survivors.py:1528-1535`); writes are `mkstemp` + `os.link` (:453-460). Probes, each exit 2 in 0 s: `--json --out <existing file>` leaves the file's sha unchanged; `--json --out out/no-such-dir/x.json` creates nothing.

## Remaining `--out` claims
| # | Where | Claim | Status |
|---|---|---|---|
| 1 | SCORECARD.md:755 | C2 declaration: `survivors.py --json --out PATH` | Wrong argv still in place. Erratum :811 supersedes it, but the row is not struck. |
| 2 | SCORECARD.md:782 | "the counter's exclusive `--out` is never clobbered" | Accurate (probes, item 4). Argv shown is correct. |
| 3 | corpus/lessons/round-18.md:377, 405-406, 420 | exclusive `--out`; `--out PATH` superseded; cite the stdout | Accurate. |
| 4 | round-18.md:407-408; SCORECARD.md:812-813 | `runs/c2-survivors.json` "is a pre-official corrected run … the two agree" | Partly unsupported; see F1-F2. |
| 5 | `runs/corrected.py:17` | runs `survivors.py --json --out R/c2-survivors-corrected.json` | Stale. Its outputs (`c2-survivors-corrected.json`, `corrected-commands.json`) are absent, it is not in commands.json, and it did not produce `c2-survivors.json`. |
| 6 | residual/advice/ResidCounterC2.md:3, 10, 12 | family-b rerun with `--out`; item 5 calls tool `87cad1ca` the "official artifact" | Evidence pointer for SCORECARD.md:782; see F3. |
| 7 | SCORECARD.md:781 (C1, non-C2) | argv shown without `--out`; commands.json `c1-measure` includes `--out c1-measure.json` | Not wrong (defers to commands.json); mirror image of #1. Not verified in depth. |
| 8 | SCORECARD.md:661, SKILL.md:572, corpus/lessons/round-17.md:160 | round-17 C1 `mutants.py --grid --out PATH` | Not C2; matches `round-17/c1/mutants.py:67`. No action. |

## Findings
- **F1 (medium) "They agree" holds for outcomes; the two runs are different builds.** `runs/c2-survivors.json` (started 04:08:39Z) records tool `87cad1ca…`, the committed blob at 1c325b2; the official run records `ac934794…` (0c75c61, HEAD). Comparing the two documents with volatile keys removed (times, tmp dirs, pids, ports, stdout hashes/tails, probe_sha256, tool, bind_guard) gives 0 differing paths over all 15 per-item outcomes, counts, witnesses and families; top-level schema, exit, counts, own_faults, named_universe, frozen_witness_validation, inputs, teardown are equal. The 1c325b2→0c75c61 diff (`out/survivors-1c325b2-to-0c75c61.diff`) is docstrings plus one guard: `combine_arms` returns "inconclusive" for an empty arms list, where 1c325b2 returned "survived" (`all()` over an empty list). `selftest_arm` and `main_arm` are byte-identical in both. The agreement is therefore expected from identical decision code, not a same-bytes reproduction. The erratum should say so.
- **F2 (medium) The pre-official run's invocation is unrecorded.** The JSON carries no argv; `commands.json` has no 04:08 entry; `LOG.md` has no match for `survivors`. File mode 0600 fits `--out` (`mkstemp`), [INFERENCE]. "Corrected" matches commit 1c325b2's message ("repair counter classification seams"), but no record defines the label. Name the commit and invocation, or label the run "unrecorded".
- **F3 (low) The family-b evidence pointer covers the 1c325b2 build.** `ResidCounterC2.md` was written 01:49:09 -0300, before `survivors.py` changed (01:50:36) and before 0c75c61 (01:58). Its item 5 calls the 04:08Z JSON's tool the "official artifact" (the official stdout says `ac934794…`), and its item 1 flags a docstring that the official build fixed. Family-b decision code is unchanged (F1), so the result probably carries over [INFERENCE]. Either state the sha, or rerun family b on `ac934794…` (`--family b --json --out <absent path>`, about 8 min; not run here).
- **F4 (low) `runs/corrected.py` is a tracked `--out` invocation in the official runs directory** with no record (#5). Remove or document; the lane owner decides.

## Official re-run (this seat)
`/usr/bin/python3 .ufo/waves/round-18/c2/survivors.py --json` in the copy, cwd copy root, no `--out`, started 06:32:51Z (detached). RESULT: PENDING.

## Hygiene
No listeners started by me. The counter's own fakes are gone (official doc `bind_guard.listening_after.owned` = []; my child tree had none at 06:35Z). Listeners on 127.0.0.1:8787-8796 belong to user shims (`~/.local/share/*-shim/shim.py`, pids 1511-1518); untouched. Lane changes: none except this file. Installs: none.

## For the main agent
1. Strike or annotate SCORECARD.md:755 (append-only policy decides how).
2. Reword erratum :812-813 per F1-F2.
3. Re-anchor SCORECARD.md:782's family-b pointer per F3.
4. Remove or document `runs/corrected.py` (F4).
