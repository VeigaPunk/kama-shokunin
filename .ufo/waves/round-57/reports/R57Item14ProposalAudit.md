# R57Item14ProposalAudit — considerthese 2026-10-26 proposal 3: relevance to the frozen claims and exact prior disposition

Seat: R57Item14ProposalAudit (scribe, leaf; no subagent dispatch). Lane: kama, round 57.
Assigned axes: calibration, operability (per `shokunin.conf`; `MISSION.md:29` conflict not resolved).
Write scope used: this report plus `R57Item14ProposalAudit.receipts/` and the separate case file
`R57Item14ProposalAudit-case35.md`, all under `.ufo/waves/round-57/reports/`. No shared file was edited;
nothing was committed, pushed, or run outside read-only tooling.

Revisions read (all pinned; the wave is live and the tip moved under this seat):

| Role | Commit | Subject |
|---|---|---|
| Frozen base (no-op/base receipts) | `b89bdab2cc114735ec5d331c6c610134258f7864` | round-56 verifier spot-check |
| Pre-data claim correction | `7c873d7b4e3839489a93d6334cdf93fe5d34d19f` | round-57: correct frozen claim targets before data |
| Executor commit (mid-seat) | `7b74e2f2` | round-57: bind prereg roster to executed calls |
| Tip at evidence capture | `8640e34cad02adcd247ba0862da63f6fb2aab0df` | round-57: record measured counter outcomes |

Receipts: `.ufo/waves/round-57/reports/R57Item14ProposalAudit.receipts/` (every command below writes
there; `<S>` = `/fast/scratch/hyaku/kama-r57/R57Item14ProposalAudit`, removed after copy-out).

## 1. The proposal, verbatim

`considerthese/2026-10-26.md:33` (file added in `221525bc`, `git log --oneline -- considerthese/2026-10-26.md` → one commit; never edited):

> 3. **Keep a running count of counters that a shortcut can satisfy:** each SCORECARD section now has a "What `met=True` does not show" paragraph, but nothing trends it. I could tally, per round, the shortcut controls that met the frozen counter, the mutants that survived, and whether the falsify wave ran, so João can see whether counter design is actually getting harder to fool or just better disclosed.

It asks for three per-round fields (shortcut controls that met the frozen counter; mutants survived;
falsify wave ran), a trend across rounds, and a read on whether counter design is getting harder to
fool or only better disclosed. It is a read-only instrument request, not a claim.

## 2. Exact prior disposition

| When | Artifact | What it says |
|---|---|---|
| Round 46 | closure defect D3 (cited at `corpus/lessons/round-47.md:14`) | D3 routs to "Mistakes row 1 (sufficiency family, with the shortcut tally as its fail-capable check; considerthese/2026-10-26.md proposal 3)" |
| Round 47 | `.ufo/waves/round-47/w1/out/X9Tally/shortcut-tally.py` | first implementation, the "draft" (v1); its header calls itself "round-47 X9Tally" and its own run needed `check-fail.out`, `check-pass.out`, `determinism.diff`, `unreadable-*.out` |
| Round 47 | `corpus/lessons/round-47.md:37` | "proposal 3 (running count of counters a shortcut can satisfy) → Mistakes row 1's check (seat X9Tally)" |
| Round 47 | `.ufo/waves/round-47/w1/out/S8Proposals/table.md:29` | row 19: "r47, mined as a lesson row/script … | pending — round-47 closure absent" |
| Round 48 | `tools/shortcut-tally.py` (975 lines added in integration commit `c4b2175d`) | v2 promoted to `tools/`; its docstring says "v2 (round 48) promotes the round-47 draft … to a lane tool"; adds committed-bytes reads, `--check N`, `--selftest` with a case that must fail |
| Round 48 | `SKILL.md:1476` | registry row "Round-48 shortcut tally … `selftest pass=7 fail=0`; considerthese/2026-10-26.md proposal 3, promoted from `.ufo/waves/round-47/w1/out/X9Tally/`" |
| Round 48 | `.ufo/waves/round-48/measured/tally.out` (commit `1541a0dd`) | the "standing run": 6 lines — the invocation line, four `detail: round 47: …` lines, `exit=0`. It contains **no table**, so the receipt does not show which rounds were tallied |
| Round 49 | `SCORECARD.md:2876` | regression line: "`shortcut-tally.py` exit 0 over rounds 40–47" — the only cited window is the default one |
| Round 55 | `corpus/lessons/round-55.md:161-166` | "**taken up round 47** … and **promoted to the lane tool `tools/shortcut-tally.py` v2 in round 48** … `.ufo/waves/round-48/measured/tally.out`, committed `1541a0dd`, is its standing run … no outside closure verdict on the tally itself exists yet" |
| Round 55 | `corpus/lessons/round-55.md:218` and `:278` (recovered/historical text blocks) | "Proposal 3 … — partially served by this round's battery receipts (each names its killed leg); a standing tally is still pending, not deferred silently" — contradicts the `:161` disposition, which records the standing tool as landed in round 48 |
| Round 57 | `corpus/lessons/round-57.md:16` | "proposal 3 (counter-shortcut tally) was opened; this round addresses a concrete counter no-op defect but does not implement a multi-round tally" |
| — | `corpus/lessons/*verifier-spotcheck.md`, `corpus/QUALITY.md` | `grep -rln "shortcut-tally\|shortcut tally"` → no match: no outside closure and no KQ criterion covers the tally |

So the exact disposition is: **proposed 2026-10-26; drafted round 47 (seat X9Tally); promoted to a
lane tool in round 48 (v2, `tools/shortcut-tally.py`, `--check`, `--selftest`); cited as a round-49
build regression over rounds 40–47 only; no outside closure exists; round 57 records it as "opened"
and says the round does not implement a multi-round tally, while the tool has existed since round 48.**
The round-57 lesson's phrasing is incomplete, not false (round 57 adds no tally work).

## 3. Relevance to the two frozen claims

Proposal 3 is directly relevant to **both** claim orderings this wave carries, because its subject is
exactly "counters a shortcut can satisfy":

- Operability claim (`round56-prereg-check.py` no-op): the round-56 defect is a shortcut
  (matching roster literal, `main(): return 0`) that satisfied a frozen counter. Proposal 3's first
  field is "the shortcut controls that met the frozen counter". Relevance is one-to-one.
- Calibration claim (`round42-selfdesc-reconcile.py` stale count): proposal 3's second purpose — "harder
  to fool or just better disclosed" — is the same question, and the selfdesc counter's own failure is a
  stale literal (expected 42, observed 43). Relevance is thematic: the tally does **not** read the
  selfdesc counter's output, so it cannot measure that claim.

Measured relevance of the instrument as it stands (commands and exits in §4):

1. **The tally covers rounds 40–47 by default.** `--rounds` defaults to `"40-47"`
   (`tools/shortcut-tally.py:895`); `SKILL.md:1476` documents the flag without stating the default.
   At `7c873d7b` and at `8640e34c`, the default run ends `latest=47 shortcuts=4 limit=5 result=PASS`,
   exit 0. A reader of that PASS sees a green trend line that stops at round 47 while the wave writes
   round 57.
2. **Extended to the current rounds it cannot certify them.** `--rounds 40-56` (rev `7c873d7b`) and
   `--rounds 40-57` (rev `8640e34c`) both end
   `latest=56/57 shortcuts=- limit=5 result=FAIL (unreadable rounds [48, 49, 50, 51, 52, 53, 54])`,
   exit 1. Per-round status in that window: 48–53 `unreadable:mutation-report`, 54
   `unreadable:no-section`, 40/41/45/56/57 `no-disclosure`, 55 `ok` but `shortcuts=-`
   (frozen id family matched none; `wide` names `K2Predicate,K4Sizing`). Only rounds 42 (5), 43 (2),
   44 (2), 46 (8) and 47 (4) carry a numeric shortcut count. The "running count" is therefore a
   frozen-window count.
3. **The current defect class is invisible to it.** `What met=True does not show` occurs **0 times** in
   the SCORECARD §Round 56 block (`SCORECARD.md:3121-3148`); round 56 is `no-disclosure`, and round 57
   (the section this wave is writing) adds no disclosure block either. So the round-56 no-op that the
   operability claim repairs is not a record the tally can see, and round 57 cannot certify a count at
   all. Proposal 3's instrument would have to be extended (disclosure block per round, window advanced,
   mutation-report parsers repaired) before it can trend this wave's repair.
4. **The instrument itself is shortcut-satisfiable in its falsify field and in its count.** See the
   separate case file: a placeholder `K9Cheat.md` under a wave `out/` with no disclosure yields
   `shortcuts=1`, `falsify=yes(w1,folded)`, and `--check 1` exit 0; and a single benign id
   (`X9SourcesGuard`) passes `--check 1` while the same disclosure text admits "two unnamed shortcut
   controls also met the counter". Its docstring admits the id-family undercount (`:43`, `:89`), but the
   `--check` gate inherits it: the gate grades the round's own disclosure, not the round's shortcuts.

Calibration observation on the frozen claim wording (not resolved here): the frozen base receipt prints
`mismatches=1 maxN=56 met=False`, and the tool defines `maxN` as "greatest N over SCORECARD lines
matching `^## Round (\\d+)`" (`tools/round42-selfdesc-reconcile.py:13`), not a capability-row count; the
highest canonical capability list at the tip (`SCORECARD.md:2844`) has 11 rows. The one mismatch is the
imported r41 calibration needle expecting `42` where 43 `corpus/lessons/*verifier-spotcheck.md` files
exist. The assignment phrase "maxN=56 instead of expected 46" is therefore not reproducible from the
counter's own terms (see §8 for the verbatim conflict).

## 4. Commands, exact output, exits

All read-only; `--rev` pinned; `--out`/`--scratch` under `<S>`. Receipts copied verbatim to
`R57Item14ProposalAudit.receipts/`.

1. `python3 tools/shortcut-tally.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev 7c873d7b4e3839489a93d6334cdf93fe5d34d19f`
   → exit 0; 29 lines; header `repo=… rev=7c873d7b… rounds=40-47`; rows for 40–47 only.
   Receipt `tally.stdout`, `tally.exit`.
2. Same, `--rounds 40-56` → exit 0 (table contaminated with `unreadable` statuses); rows 48–54
   `unreadable`, 55 `ok`/`-`, 56 `no-disclosure`. Receipt `tally-40-56.stdout`, `.exit`.
3. Same, `--check 5` (default window) → exit 0; last line
   `latest=47 shortcuts=4 limit=5 result=PASS`. Receipt `check-default.stdout`, `.exit`.
4. Same, `--rounds 40-56 --check 5` → exit 1; last line
   `latest=56 shortcuts=- limit=5 result=FAIL (unreadable rounds [48, 49, 50, 51, 52, 53, 54])`.
   Receipt `check-40-56.stdout`, `.exit`.
5. `python3 tools/shortcut-tally.py --selftest --scratch <S>/selftest` → exit 0;
   `selftest pass=7 fail=0` (cases readable-round, check-fails, committed-bytes, bad-rev,
   unreadable-round, split-slash-uppercase-kill, contradictory-report).
   Receipt `selftest.stdout`, `.exit`.
6. At tip `8640e34c`: `--rounds 40-57 --check 5` → exit 1, same unreadable list, `latest=57 … result=FAIL`;
   default `--check 5` → exit 0, `latest=47 shortcuts=4 limit=5 result=PASS`.
   Receipts `head-tally-40-57.*`, `head-check-default.*`.
7. `python3 tools/round42-selfdesc-reconcile.py --repo … --tip 7c873d7b… --out <S>/selfdesc-tip.out`
   → exit 1; `r41=1 … mismatches=1 maxN=56 met=False`; detail line names the calibration run
   `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` with
   "no stdout line == '42' (exit 0)". Receipt `selfdesc-tip.out`, `.exit`.
8. Same at tip `8640e34c` → exit 0; `r41=0 … mismatches=0 maxN=57 met=True` (observed counter output at
   that commit; this seat did not verify the claim). Receipt `selfdesc-head.out`, `.exit`.
9. `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` → `43`.

## 5. Non-author spot-check: SOURCES S515 reopen (advisory — this seat is a lane author)

- URL reopened this round: https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT
- `curl -L --fail --silent --show-error https://git-scm.com/docs/git-config -o <S>/s515/git-config.html`
  → exit 0; 830605 bytes; sha256 `706b1566467e9cd8c6cdda853a5fc82118a48fde3119777d18cefc014bcd3d5a`.
- The fetch is byte-identical to both committed snapshots:
  `.ufo/waves/round-56/sources/git-docs-git-config.html` and
  `.ufo/waves/round-57/sources/git-config-live-2026-10-27.html` (same sha256), so the row's snapshot is
  not stale.
- Location: HTML line 5850, section `GIT_CONFIG_COUNT`, anchor
  `Documentation/git-config.txt-GITCONFIGCOUNT`.
- **Located quote (18 words, ≤25):** "all environment pairs GIT_CONFIG_KEY_&lt;n&gt; and
  GIT_CONFIG_VALUE_&lt;n&gt; up to that number will be added to the process&#8217;s runtime
  configuration". Source uses U+2019 (`&#8217;`); `corpus/lessons/round-56.md:18` renders it ASCII
  (`process's`) — same words, same claim. `corpus/lessons/round-57.md:12` uses the typographic form.
- Revision marker: `last updated in 2.56.0` (matches the S515 anchor claim "git 2.56.0, page last
  updated in 2.56.0").
- Row consistency: `corpus/SOURCES.md:268` (S515) is tier B, status `mined`, recheck `2026-10-27`, 180d,
  `used-by corpus/lessons/round-56.md`, "supersedes S511 — … (18 words); the revision marker was
  available but omitted from S511's anchor". S511 exists at `corpus/SOURCES.md:264` and its anchor indeed
  carries no revision marker (`§GIT_CONFIG_COUNT (HTML copy .ufo/waves/round-55/sources/…); opened
  2026-10-27 by the L1`), so the supersession rationale is supported by the tree.
- Receipt: `s515-fetch.txt`.

## 6. Admit/reject decision spot-check (one decision; advisory)

Decision checked: **S515 ADMIT** (round-56 Gate, `corpus/lessons/round-56.md:18`) — supported: live
quote present at the stated anchor, 18 words, revision marker present, S511's anchor lacks it. I agree
with the admit on the evidence above.

Decision checked as the "reject" sample: **S513 REJECT** (`corpus/lessons/round-56.md:15`; row
`corpus/SOURCES.md:266`). The round-56 outside closure already **disagrees** with this reject
(`corpus/lessons/round-56-verifier-spotcheck.md:30`: S513 reject → `disagree`; routed defect at `:45`
"round-56 S513 is an outside discernment miss"). Round 57's Gate and lesson do not mention S513 at
all (`grep -n "S513" corpus/lessons/round-57.md` → no match), so the outside defect is not
lesson-addressed in the round-57 lesson as it stands. Advisory only: the round's claim set (counter
repair) may legitimately not owe S513 a row, but the assignment requires the round-56 outside defects to
be lesson-addressed; the L1/integration owner should record the disagreement rather than leave the
round-56 reject standing unqualified.

## 7. Findings (calibration / operability, no judgment filed)

- **F1 (calibration, the tally's window is a stale literal).** `--rounds` default `"40-47"`
  (`tools/shortcut-tally.py:895`) is the window of the round that landed the tool. The default run is
  green (`latest=47 … PASS`, exit 0) while rounds 48–56 are not counted; extending the window reds it
  permanently (`unreadable rounds [48, 49, 50, 51, 52, 53, 54]`, exit 1). This is the same
  stale-count family as the calibration claim under repair.
- **F2 (calibration, the tally cannot see the defect it exists to trend).** Round 56 has no
  `What met=True does not show` block (`SCORECARD.md:3121-3148`, 0 occurrences) and round 57 has none
  either, so the tally records both `no-disclosure`; the round-56 no-op shortcut is not a record the
  tally reads.
- **F3 (operability, the standing-run receipt does not show its window).**
  `.ufo/waves/round-48/measured/tally.out` (committed `1541a0dd`) is 6 lines of `detail:` for round 47
  plus `exit=0`; the table and the `rounds=` header are absent, so the receipt cited as the tool's
  standing run cannot demonstrate what it covered.
- **F4 (calibration, disposition records disagree).** `corpus/lessons/round-55.md:161` says the tally
  was promoted to `tools/` in round 48; the preserved text at `:218`/`:278` says "a standing tally is
  still pending". The later text is historical, but nothing in either block marks which one a reader
  should trust.
- **F5 (calibration, round-57 lesson wording).** `corpus/lessons/round-57.md:16` says the round "does
  not implement a multi-round tally" without noting the tally already exists since round 48
  (`tools/shortcut-tally.py`, `SKILL.md:1476`); the "opened" phrasing reads as first contact.
- **F6 (operability, instrument-level shortcut — op.)** The tally's `--check` passes a round with no
  disclosure block and a single placeholder `K9Cheat.md`: `shortcuts=1`, `falsify=yes(w1,folded)`,
  `status=no-disclosure`, `latest=12 shortcuts=1 limit=1 result=PASS`, exit 0. See the case file.
- **F7 (operability, instrument-level undercount — op.)** A disclosure naming one benign id
  (`X9SourcesGuard`) while stating "two unnamed shortcut controls also met the counter" passes
  `--check 1` with `shortcuts=1`; the gate grades disclosure, not shortcuts (docstring admits the
  family undercount at `:43`, `:89`).
- **F8 (calibration, claim phrasing).** "maxN=56 instead of expected 46" does not match the counter's
  definition of `maxN` (`tools/round42-selfdesc-reconcile.py:13`: greatest `## Round N`); at base
  `maxN=56` equals the highest measured round, and the canonical capability list has 11 rows. The
  counter's single mismatch is the 42-vs-43 spotcheck needle (43 observed). Flagged for the canonical
  judge, not resolved.

## 8. Conflicts, verbatim (not resolved here)

1. Assignment context: "C1 calibration—repair the stale canonical capability row count, counter
   currently reports maxN=56 instead of expected 46; before output mismatch=1. C2 operability—distinct,
   actual canonical-row execution/content binding; a no-op currently reports met=True exit 0."
2. `.ufo/waves/round-57/controls/freeze.txt`: "claims=C1 calibration stale canonical-table count;
   C2 operability canonical-row execution binding".
3. `.ufo/waves/round-57/controls/freeze-amendment.txt`: "C1 is the frozen round56-prereg-check no-op
   control defect, operability axis … C2 is the tools/round42-selfdesc-reconcile.py stale calibration
   count, calibration axis: its base output says the calibration run expects 42 but the actual
   committed outside verifier spotcheck count is 43; update only the stale self-description count and
   require `mismatches=0`."
4. `SCORECARD.md:3149`: "C1 is the frozen round-56 prereg checker no-op defect (operability); C2
   corrects the verifier-spotcheck count (calibration)."
5. `corpus/lessons/round-57.md:16` vs `tools/shortcut-tally.py`/`SKILL.md:1476` (F5).
6. `MISSION.md:29` (operability + freshness) vs `shokunin.conf`/SCORECARD (operability + calibration),
   the known open L0 question; not touched.

## 9. Scope statement

No claim was verified or refuted here, no counter or score changed, and no shared file was written. This
seat's product is the disposition, the relevance measurement, the two spot-checks, and the instrument
observations above. Installations: none (no package, tool or version was installed or updated this
seat). Scratch `/fast/scratch/hyaku/kama-r57/R57Item14ProposalAudit` was created explicitly, receipts
were copied to `R57Item14ProposalAudit.receipts/` first, and the scratch was removed.
