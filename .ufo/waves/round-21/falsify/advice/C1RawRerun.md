VERDICT: confirm - both C1 counting commands re-run byte-identical at b76727f3 in a fresh clone; tool provably absent at round start 7a6bc911.
Attacks: C1 counting commands (exit/JSON) and the "tool absent at round start" claim.

# Method
- Fresh clone `git clone -q <lane> /tmp/kama-r21-C1RawRerun/lane`, `checkout -q b76727f31e522763ce24e43d6ec86d21b507a11f`; `rev-parse HEAD` = b76727f31e522763ce24e43d6ec86d21b507a11f; `status --porcelain | wc -l` = 0.
- Official argv taken from `.ufo/waves/round-21/runs/b76727f3/commands.json` (c1-audit-raw / c1-audit-ledger): `/usr/bin/python3 <lane>/tools/report-landing-audit.py --rounds 10-20 [--no-errata] --json`, cwd-independent (tool resolves repos from `__file__`/flags; read commands.json lines 38-73).
- One deviation, by necessity of the clone location: added `--fleet-repo /home/vgpnk/Projects/shokunin`. Tool default fleet = lane parent (`main()`: `--lane-repo` default `Path(__file__).resolve().parent.parent`, `--fleet-repo` default its parent); the official lane sat at `<fleet>/kama-shokunin` so the flag was implicit there. No other flag differs. Env scrubbed of `GIT_*` before exec (the tool also scrubs internally, tools/report-landing-audit.py:72-77).
- Interpreter `/usr/bin/python3` (3.14.8), same as official argv. No tool installs performed (git + python3 preexisting).

# Results (every line an executed observation)
- Raw rerun (`--rounds 10-20 --no-errata --json`): exit **1**; stderr empty; stdout sha256 `af2707adf5c2424ebe64b30505d33d94b0c5ca08f2d843cf6a27a4aa10651e24` — **byte-identical** to official `c1-audit-raw.stdout` (same digest also recorded in commands.json; reference file re-hashed = match).
- Ledger rerun (`--rounds 10-20 --json`): exit **0**; stderr empty; stdout sha256 `6e865bd73178441f9eceb51018cffe42a513dcf1ff52cd324cf7cc4e17e4259d` — **byte-identical** to official `c1-audit-ledger.stdout` (commands.json digest match).
- Assigned diff (minus clone paths): 0 diff lines for both; in fact equal even before normalization — the JSON embeds no lane path (only fleet-side `/home/vgpnk/Projects/shokunin/.ufo/reports/round-N/kama.md`). `json.loads(mine) == json.loads(ref)` asserted True for both.
- Breakdown (from rerun JSON, matches every claimed number): raw summary `defects=9`, `by_kind {landed-omitted: 8, unresolved-full-hash: 1}`, `required_commits=42`, `post_report_commits=4` (all 4 in r19 `post_report`), `reports=11`, rounds 10..20, `status="failed"`, `errata_rows=0`. Per round: r10 landed-omitted×1; r18 ×3; r20 landed-omitted×4 + unresolved-full-hash×1; r11-r17, r19 zero.
- Ledger run: `status="clean"`, `corrected=9`, `uncorrected=0`, `errata_rows=9`, `errata_unmatched=0`, `errata_invalid=0`; per-defect `corrected_by` present (e.g. r20 unresolved-full-hash token `0957ce619789d13d894ef21bc863486bcb35b56c` → corrected_by [3]).
- Absence at round start: `git -C <clone> cat-file -e 7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d:tools/report-landing-audit.py` → **exit 128**, stderr `fatal: path 'tools/report-landing-audit.py' exists on disk, but not in '7a6bc911…'` — matches official `c1-absent-at-base` (exit 128, same stderr text). Contrast: same command at b76727f3 → exit 0.
- Bonus: `--selftest` in the clone → exit 0 (`ok raw-fails … ok exact-defect-set`), matching official c1-audit-selftest exit 0.
- Side-effect scan of the tool (grep of clone copy): only git subprocess calls with scrubbed env; no writes outside `--selftest`'s tempdirs. The rerun mutated nothing.

# Residual risk / verification gaps
- Rerun happened minutes after the official run on the same host, so fleet report inputs are identical by construction; a much-later rerun could legitimately diverge if reports changed — inherent, not a defect found.
- [INFERENCE] None of the numbers above are inferred; all from executed commands. The only reasoning beyond observation is the fleet-flag equivalence (defaults vs explicit), which follows from the tool's own `main()` defaults.

# Artifacts (under .ufo/waves/round-21/falsify/out/C1RawRerun/)
`c1-audit-raw.rerun.stdout`, `c1-audit-ledger.rerun.stdout`, `c1-audit-*.rerun.stderr` (0 B), `diff-c1-audit-raw.txt`, `diff-c1-audit-ledger.txt` (0 lines), `EVIDENCE.md` (command log with exits). Scratch `/tmp/kama-r21-C1RawRerun` deleted at close.
