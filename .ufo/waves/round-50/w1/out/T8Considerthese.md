# T8Considerthese — round-50 proposal tracker (considerthese 2026-10-22 … 10-26)

**Verdict: the tracker's 20 proposals are unchanged in substance after round 50 — still 6 unimplemented, and for the first time
three *landed* instruments (pin-watch, seat-yield, shortcut-tally) are dark or frozen in the same round, while the lane again
records no machine-readable pointer to the proposal it mines.** Lane tip read `3b79eaddf38246c637cc7ba1a94ab363422876b6`;
round-50 build `97c864be…`, freeze `601c8889…`, base `26ecba64…`. Deliverables: `T8Considerthese/table.md` (updated table,
20 rows, every R50 cell with file:line) and `T8Considerthese/commands.txt` (commands + exit codes).

## 1. What round 50 takes up

| Check | Result |
|---|---|
| prereg proposal pointer | **absent** — `python3 -c "…list(json.load(open('.ufo/waves/round-50/preregistration.json')).keys())"` → `['lane','round','attempt','author','frozen_at_utc','base','authority','separability','claims','controls','limits']`, no `frontier`; rounds 46/47/48 have it (`.ufo/waves/round-46/preregistration.json:150`, `round-47:56`, `round-48:55`), rounds 49 and 50 do not (exit 0) |
| lesson proposal line | **absent and not requested** — `grep -cE "considerthese\|proposal" corpus/lessons/round-49.md` → 0 (exit 1); `.ufo/waves/round-50/build_spec.py:174-175` asks the lesson seat for `## Claims`/`## Gate`/`## Mistakes` only |
| LOG / SCORECARD round-50 sections | **absent** — `grep -n "^## Round 49\|^## Round 50" LOG.md` → `2331` only; `SCORECARD.md:2813` is still `## Round 49`, banner `SCORECARD.md:6` "Latest measured round: 49" |
| measured set | 20 `run` lines (`.ufo/waves/round-50/measured/measure.sh:20-39`); re-runs rows 13 (`:28-29`), 17 (`:30-32`), 19 (`:36`); **no pin-watch, no seat-yield** (`grep -c "pin-watch\|seat-yield" …` → 0, exit 1) |
| route of the two claims | the round-49 outside closure (`corpus/lessons/round-49-verifier-spotcheck.md`), not `considerthese/` — same non-author route as round 49, uptake zero and unrecorded |

## 2. Table, in brief (full version: `T8Considerthese/table.md:1`)

| Status class | Rows |
|---|---|
| landed lane artifact | 13 (digest/hexrun), 15 (`registry/staged-refusals.tsv`), 17 (`append-only-audit` v5, `tools/append-only-audit.py:2,4,573`) |
| landed but **regressed this round** | 14 (pin-watch: not run, no seat), 16 (seat-yield: not run, unrunnable → exit 2), 19 (tally: `rounds=40-47`, `tools/shortcut-tally.py:895`) |
| criterion only | 9 (KQ44), 12 (KQ47) |
| practice only | 1, 8 (reflection series; `considerthese/2026-10-26.md:5-13`) |
| wave artifact only | 18 (this seat), 20 (pin gap; not taken this round) |
| partial | 2 (relays frozen at `tools/round38-statement-audit.py`) |
| **unimplemented** | **3, 4, 5, 6, 7, 11** — §3 of `table.md` gives each one-round sketch |

Six remain unimplemented with one-round uptake sketches in `table.md` §3.1-§3.6: (3) `tools/anchor-drift-watch.py`
(`considerthese/2026-10-22.md:24`); (4) owner column on defect/Mistakes rows (`2026-10-22.md:26`); (5) `--classes` view of
the tally (`2026-10-23.md:29`); (6) seat-evidence-vs-amendment leg on `tools/prereg-time-check.py` (`2026-10-23.md:31`);
(7) `tools/unadmitted-census.py` (`2026-10-23.md:33`); (11) `registry/prepared-waves.tsv` (`2026-10-24.md:31`).
Round 50 now supplies free fixtures/inputs for 3 (three real drifts), 4 (a standing orchestrator-owned row), 6 (a clean
passing case plus round-28's failing ordering), and 11 (a second wave row, with a durability hazard).

## 3. Findings (defects: exact site, showing command, proposed fix)

**F1 — the preregistration dropped the proposal pointer for the second round running.**
Site: `.ufo/waves/round-50/preregistration.json` (whole file; keys at `:1-46`). Show:
`python3 -c "import json;d=json.load(open('.ufo/waves/round-50/preregistration.json'));print('frontier' in d)"` → `False`;
same loop over rounds 46-50 → `46 True / 47 True / 48 True / 49 False / 50 False`. Fix: `"frontier": {"considerthese":
"<day> proposal N (summary) — or none (reason)"}`, plus a `gate-registry-check.py` leg failing a round ≥ 50 prereg without it.

**F2 — the lesson-level proposal line is missing for two landed rounds and round 50's lesson seat cannot add it.**
Site: `corpus/lessons/round-48.md`, `corpus/lessons/round-49.md` (no line), and `.ufo/waves/round-50/build_spec.py:174-175`
(the seat's spec). Show: `grep -cE "considerthese|proposal" corpus/lessons/round-49.md` → 0 (exit 1), against
`corpus/lessons/round-47.md:37`, `round-46.md:11`, `round-45.md:21`. Fix: one sentence in the T4Lesson item — "end `## Claims`
with `considerthese: …` or `considerthese: none (reason)`".

**F3 — three landed instruments went dark or stale in one round, and the round-49 fix for this class was not built.**
Sites: `.ufo/waves/round-50/measured/measure.sh:20-39` (no pin-watch, no seat-yield), `.ufo/waves/round-50/build_spec.py:82`
(wave U-names `['U1Fresh']` — no `U2Pins` seat), `tools/shortcut-tally.py:895` (`default="40-47"`). Show:
`grep -c "pin-watch\|seat-yield" .ufo/waves/round-50/measured/measure.sh` → 0 (exit 1);
`python3 tools/seat-yield.py .ufo/waves/round-50/w1` → `could-not-evaluate: no *-results.json`, exit 2;
`W:measured/tally-build.out:2` → `rounds=40-47` (rows `:4-11`). Round 49's F7 proposed `registry/per-round-instruments.tsv`;
`ls registry/` → absent. Fix: add that TSV (`instrument, script, command, required_since_round`) and one gate leg failing when
a required instrument has no `run` line in the round's `measure.sh`.

**F4 — a committed build receipt carries a failure that a later build-fix repaired without a re-run.** Site:
`.ufo/waves/round-50/measured/sao-build.out:2` (`error: 97c864be…:corpus/SOURCES.md:251: unterminated table row`, `:3` `exit=2`)
against commit `3d42897b` (the fix) and the tip. Show, in a `git clone --shared` at `3b79eadd`:
`python3 tools/sources-append-only.py --from 26ecba64… --to <tip>` → `added S496 (allowed) / added S497 (allowed) /
added S498 (allowed) / no append-only violations`, exit 0. Fix: re-run `sao` at the measurement commit and overwrite the
receipt; the SCORECARD regression line must quote the tip re-run.

**F5 — `hexrun-census` is red at the tip on an id no lane commit can resolve, and neither receipt nor ledger names it.**
Sites: `.ufo/waves/round-50/measured/hexrun-build.out:2-3` (`unknown=1`, exit 1), `registry/hexrun-ledger.tsv` (no row).
Show: `python3 tools/hexrun-census.py scan --rev <tip> --details` → `detail: f8cdb853aaff29393faeb0b6d4c2a2296778b698 len=40
class=unknown`, exit 1; `git cat-file -t f8cdb853…` → `fatal: could not get object info`;
`grep -c f8cdb853 registry/hexrun-ledger.tsv` → 0. The id is the round-49 report commit in the fleet repo, cited at
`corpus/lessons/round-49-verifier-spotcheck.md:21`; a fleet-repo precedent row exists at `registry/hexrun-ledger.tsv:2`
(class `upstream`). Fix: add that ledger row; make the counter print the token without `--details`.

**F6 — no closure has ever ruled this tracker, including the one that admitted the round carrying it.** Sites:
`corpus/lessons/round-47-verifier-spotcheck.md`, `…round-48…`, `…round-49…`. Show: `grep -cE "proposal|considerthese|tally"`
→ 0 on all three (exit 1), while `corpus/lessons/round-49-verifier-spotcheck.md:11` reads `Verdict: **admitted**`. Fix: one
line per closure, `frontier seat: <name>: <verdict on its product>`.

**F7 — the round whose claim rests on a binary lost the only instrument that reports that binary's pin.** Sites:
`.ufo/waves/round-50/preregistration.json:16` (C1 on b11909), `registry/engine-pins.tsv:4` (llama.cpp `b11755 S038`). Show:
`grep -c b11909 registry/engine-pins.tsv` → 0 (exit 1); `grep -c "pin-watch" .ufo/waves/round-50/measured/measure.sh` → 0;
`grep -rn "pin-watch\|newest tag" .ufo/waves/round-50/measured/` → no match (exit 1). Fix: a pin row `llama.cpp b11909`
(source = the receipt that records it) and a pin line in `measure.sh`.

## 4. Out of scope / not re-reported

The round-50 known integration items were not re-verified beyond table needs: the two round-50 counters are unregistered
(`.ufo/waves/round-50/measured/gate-build.out:2-4`, `registered 44 unregistered 2 defective 0`, exit 1); SCORECARD/LOG/
QUALITY/README and the round-50 lesson are unwritten; S496-S498 `used-by` names a missing `corpus/lessons/round-50.md`
(`corpus/SOURCES.md:251`). Wave state at the snapshot: 66 seats (`spec.json` items: executor 22, reviewer 10, scribe 10,
critic 6, connector 5, mutation-tester 4, scout 4, sentinel 3, revenger 1, simplifier 1), 29 seat dirs, 3 report files, no
`w1-results.json`; `w1.ready`/`w1.ready.dispatched` untracked (`git status --porcelain`), unlike round 49's tracked pair.

## 5. Posture

Read-only on the lane. No counter was run and no server was started (`pgrep -f llama-server` → rc 1). Four read-only tool
runs happened inside one `git clone --shared` at `3b79eadd` (`sources-append-only.py`, `hexrun-census.py`,
`shortcut-tally.py`, `seat-yield.py`), exit codes in `commands.txt` §9. No tool was installed or upgraded. No lane file was
edited; every proposed change above is a proposal, not a patch.
