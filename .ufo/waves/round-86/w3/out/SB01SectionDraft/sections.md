# SB01SectionDraft — draft report sections (kama r86, terminal record)

Pinned revision: `bafae7afb41843564ac2468d28beb8e0bb98e8e6` (read via `git show <rev>:<path>`, never the worktree).
Every number below is either quoted from a committed receipt (path given) or re-derived by this seat at
`bafae7af` (command given). Tags: **RE** = re-derived here at `bafae7af`; **RCPT** = read from the committed
receipt only; **NOT-RE-DERIVABLE** = reason given. Base revision `3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d` per
`plans/round-86-claims.md` (the frozen before-state).

Counting-command convention: `<lane>` = `/home/vgpnk/Projects/shokunin/kama-shokunin`. The frozen counter runs the
instrument bytes from the **worktree** (`count.py` `command = [... repo/script ...]`); at this seat the worktree
bytes of all five instruments and `count.py` hash-equal `bafae7af` (`git show <rev>:<f> | sha256sum` vs
`sha256sum <f>`), so the worktree-executed run equals the committed-bytes run.

---

## (A) Before -> after measurements

### C1 — calibration: rendered-cell identity of the live self-assessment cells

- **Before** (base `3ff23da3`, receipt `.ufo/waves/round-86/measured/before/c1.out`, RCPT):
  `RENDERED_CELLS facts=3 mismatches=3 gate=0 closure=0 disposition=0 newest_gate=85 newest_closure=85`, then
  three `RENDERED_CELLS_FINDING` lines and `exit=1` (last line of the receipt).
  Revision: base named by the plan (`plans/round-86-claims.md`, "Before / no-work control"); the receipt itself
  carries no revision line (RCPT, no 40-hex in `before/c1.out`).
- **After** (receipt `.ufo/waves/round-86/measured/after/c1.out`, RCPT):
  `RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=85 newest_closure=85`.
  RE at `bafae7af`: same line, exit 0 (see command below).
  Revision: **NOT-RE-DERIVABLE from the receipt** — `after/c1.out` has no revision and no `exit=` line; the
  SCORECARD table writes `--rev <measured>` as a placeholder (`SCORECARD.md` line 5271). The revision RE-derived
  here is `bafae7af`.
- **Counting command** (paste in `<lane>`; `<dir>` = any empty scratch dir):
  `python3 .ufo/waves/round-86/count.py c1 --repo . --rev bafae7afb41843564ac2468d28beb8e0bb98e8e6 --work <dir>`
  RE output: `RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=85 newest_closure=85`, exit 0.
- **Selftest:** before `.ufo/waves/round-86/measured/before/c1-selftest.out` → `RENDERED_CELLS_SELFTEST pass=11 fail=0`
  (RCPT, 11 PASS lines). After `.ufo/waves/round-86/measured/after/c1-selftest.out` → 17 PASS lines (RCPT);
  RE: `python3 tools/round86-rendered-cells.py --selftest` (run from a `git archive bafae7af` copy) →
  `RENDERED_CELLS_SELFTEST pass=17 fail=0`, exit 0.
- **Mutants:** `.ufo/waves/round-86/measured/after/c1-mutants.out` → `RENDERED_CELLS_MUTANTS mutants=10 killed=10 escaped=0`
  (RCPT; RE at `bafae7af` with `python3 .ufo/waves/round-86/measured/after/c1-mutants.py <copy>` → same line, exit 0).
  The lesson's M3 sentence reads `7/7 ... mutants=7 killed=7` (`corpus/lessons/round-86.md:59`) — **stale**, see report F8.

### C2 — operability: every mutant maps to a declared owning arm; summary reconciles

- **Before** (`.ufo/waves/round-86/measured/before/c2.out`, RCPT): `DEBT_MUTANT_OWNERS mutants=5 killed=3 escaped=2 invalid=0 arms=unknown cardinality=ok owners=3/5`, `exit=1`.
- **After** (`.ufo/waves/round-86/measured/after/c2.out`, RCPT): `DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5`, then `DEBT_MUTANT_OWNER_PRISTINE APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34`. No `exit=` line in the receipt.
  RE at `bafae7af`: identical line, exit 0 (command below).
  Revision: **NOT-RE-DERIVABLE from the receipt** (no revision line; SCORECARD row 5272 uses `<measured>`). RE revision = `bafae7af`.
- **Counting command:** `python3 .ufo/waves/round-86/count.py c2 --repo . --rev bafae7afb41843564ac2468d28beb8e0bb98e8e6 --work <dir>`
  RE output: `DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5`, exit 0.
- **Selftest:** before `measured/before/c2-selftest.out` → `DEBT_MUTANT_OWNERS_SELFTEST pass=10 fail=0` (RCPT);
  after `measured/after/c2-selftest.out` → 13 PASS lines (RCPT); RE: `python3 tools/round86-mutant-owners.py --selftest`
  → `DEBT_MUTANT_OWNERS_SELFTEST pass=13 fail=0`, exit 0 (`probes/c2-selftest-rerun-at-tip.out`).
- **Debt selftest (subject):** RE `python3 tools/round81-append-debt.py --selftest` → `APPEND_DEBT_SELFTEST_ARMS arms=34 expected=34 fail_lines=0` and `APPEND_DEBT_SELFTEST pass=34 fail=0`, exit 0, stderr 0 bytes (`probes/debt-selftest-at-tip.out`). `EXPECTED_ARMS = 34` at `tools/round81-append-debt.py:483`.

### C3 — freshness: pin-recheck rows corroborated against live source bytes

- **Before** (`.ufo/waves/round-86/measured/before/c3.out`, RCPT): `could-not-evaluate: no tools/round86-pin-origin.py at 3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d`, `exit=2`. The revision is printed in the line itself (RCPT).
- **After** (`.ufo/waves/round-86/measured/after/c3.out`, RCPT): `PIN_ORIGIN rows=5 verified=5 mismatch=0 unreachable=0 bad=0` plus five `PIN_ORIGIN_ROW` lines (`anchors=2/2` each). No `exit=` line in the receipt.
  RE: **NOT-RE-DERIVABLE** in this seat — the live leg fetches five upstream URLs and the bounds of this item forbid network calls beyond the URLs it names. What *was* re-derived offline at `bafae7af`:
  all 10 anchor headers parse; each stored body's sha256 equals the header digest (`digest_ok=True` ×10); each stored
  body has exactly the header's `end-start+1` lines (`stored_newlines == declared`, 10 of 10; `probes/` script run in this seat).
  The exit status 0 is implied by the printed counts under `main()`'s return rule (`round86-pin-origin.py:302-303`), not observed.
- **Counting command:** `python3 .ufo/waves/round-86/count.py c3 --repo . --rev bafae7afb41843564ac2468d28beb8e0bb98e8e6 --work <dir>` (performs the live fetch; not run here).
- **Selftest:** before `measured/before/c3-selftest.out` → `PIN_ORIGIN_SELFTEST pass=7 fail=0`; after `measured/after/c3-selftest.out` → `PIN_ORIGIN_SELFTEST pass=7 fail=0`. RE (offline, injected fetcher): `PIN_ORIGIN_SELFTEST pass=7 fail=0`, exit 0.
- Revision of the after receipt: NOT-RE-DERIVABLE from the receipt (`c3.out` contains one 40-hex string, the upstream commit inside a URL, not a measurement revision).

---

## (B) Sources & frontier

Registry: `corpus/SOURCES.md`, `## Registry` table (11 cells per row). Counts parsed from committed bytes and
reproduced with the fleet census. The census is run through a scratch root whose `kama-shokunin` symlinks to a
`git archive` of each revision (`fleetB` = base, `fleetT` = tip) so the lane worktree does not stand in for the base.

| | base `3ff23da3` | tip `bafae7af` |
|---|---|---|
| rows (`census … FLEET rows`) | 317 | 319 |
| tier A / B / C | 302 / 11 / 4 | 304 / 11 / 4 |
| status mined / queued / rejected | 284 / 8 / 25 | 286 / 8 / 25 |
| `validate` exit | **0** (`kama ok …/SOURCES.md`) | **0** (`kama ok …/SOURCES.md`) |
| W01 / W04 warnings | 1 / 113 | 1 / 115 |

Commands (RE):
- base: `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root <scratch>/fleetB kama` → last line `kama ok …/fleetB/kama-shokunin/corpus/SOURCES.md`, exit 0; `census --root <scratch>/fleetB kama` → the counts above.
- tip, run-start form on the lane: `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → `kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`, exit 0 (the lane's `corpus/SOURCES.md` worktree hash equals the tip blob hash, `6152adec91fb`, so this reads committed bytes).
- tip committed bytes: `validate --root <scratch>/fleetT kama` → exit 0; `census --root <scratch>/fleetT kama` → rows 319, tier A 304, mined 286.

Both exits: **0** and **0**. Warnings are not failures (census header: "warnings do not affect clean lanes").

**Rows added this round, by tier** (set difference of S-ids, `census.py`):
- tier A: 2 — S578 (`SOURCES.md:333`, CommonMark 0.31.2 §4.5 fenced code blocks, `status=mined`) and S579 (`SOURCES.md:334`, §4.4 indented code blocks, `status=mined`).
- tier B: 0. tier C: 0. No row removed.

**Rows whose cells changed, old -> new:** one row, one cell.
- S576 (`SOURCES.md:331`), cell 11 (`used-by`): `corpus/lessons/round-85.md` → `corpus/lessons/round-85.md, corpus/lessons/round-86.md`. All other 10 cells of S576 unchanged. Source: `git diff 3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d bafae7af -- corpus/SOURCES.md` (`@@ -328,8 +328,10 @@`, 3 insertions, 1 deletion).

**Frontier rows advanced:** 0 (RE).
- queued rows at base and tip are the same eight ids: `S021 S022 S023 S025 S029 S059 S074 S086` (awk over the `status` column of both committed files); no queued row changed status.
- `## Leads (unopened)` (`SOURCES.md`, tip line 369) is outside the round's only hunk (`@@ -328`), so it is unchanged.
- `registry/pin-recheck-rows.tsv` is not in `git diff --numstat` for the round: the five pin rows are unchanged.
- S578/S579 enter at `mined` (not `queued`), so they do not move a frontier row; the SCORECARD's word "admitted this round" (`SCORECARD.md` line 5299) is the lesson's decision column (`corpus/lessons/round-86.md` gate table), not a registry status.

**Quote check (committed receipt, not live):** the three lesson quotes appear verbatim in the committed fetch
receipts `.ufo/waves/round-86/w2/out/SC01SourcesCensus/receipts/commonmark-0.31.2.fetched.html` and
`.ufo/waves/round-86/w1/out/SC01SourcesRecon/receipts/commonmark-0.31.2.html` (tags stripped; RE with `grep -o`).
Section headings `4.4Indented code blocks` and `4.5Fenced code blocks` are in the same receipt. Live re-fetch: NOT-RE-DERIVABLE (no network beyond named URLs).

**Round-86 registry append (debt, RE):** `APPEND_DEBT round=86 base=3ff23da3f291 events=80 accepted=53 late=27 pending=3 unaccepted=0 bad_rows=0 bad_declarations=0 out_of_population=0`, exit 0 — run as `python3 tools/round81-append-debt.py --repo <clone> --round 86` on a `git clone --shared` checked out at `bafae7af`. `registry/append-only-late.tsv` gains 15 rows (`git diff --numstat`: `15 0`), naming four event commits: `3e93febb` (1), `65665250` (12), `c0d7fbd8` (1), `948dec78` (1). `pending=3` is printed by the counter and is not stated in the round-86 SCORECARD/LOG entries (grep of the round-86 sections finds no `pending=3`).
