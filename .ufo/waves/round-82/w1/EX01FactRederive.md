# EX01FactRederive — independent re-derivation of the six round-81 facts (kama r82 w1)

Leaf executor. No production file touched, no commit, no scored gate run. Sealed revision
`1b64f66ddea89c57b71165eacd14b0e1d6f24e11`; lane tip at final run `384ef1d5bcbf737183571398ecb0955ea5074609`
(`git -C … rev-parse master`). Counter `tools/round82-selfrecord-round81.py` was not opened until
`EX01.json` existed (independence order held).

## The six values (declared vs observed; receipt = `git show <tip>:<path>`)

| id | declared token (sealed bytes) | observed | stale |
|---|---|---|---|
| F1 | `sc81c2-pending=1` — `SCORECARD.md:4901` C2 row, `-> exit 0` cell | `pending=4` — `.ufo/waves/round-81/measured/after/debt-green.out` | yes |
| F2 | `log81-frontier-rows=301` — `LOG.md:3376` `Frontier: registry 297 → 301 rows` | 302 — S-row count of `corpus/SOURCES.md` (`^ {0,3}\| *S[0-9]+ *\|`) at sealed and at base | yes |
| F3 | `skill81-gate-arms=10` — `SKILL.md:309` `(ten arms, …)` | `arms=11` — `.ufo/waves/round-81/measured/after/gate.out` | yes |
| F4 | `calib81-newest-closure=round-80-verifier-spotcheck.md` — `SCORECARD.md:18` | `round-81-verifier-spotcheck.md` — newest `round-*-verifier-spotcheck.md` at tip | yes |
| F5 | `logcorr81-c2-pending=1` — `LOG.md:3388` `pending=0 -> pending=1` | `pending=4` — same `debt-green.out` | yes |
| F6 | `sc81c1-selftest=13` — `SCORECARD.md:4900` C1 row | `pass=13 fail=0` — `.ufo/waves/round-81/measured/after/c1-selftest.out` | **no** |

Verdict `stale=5 holding=1`, identical to the frozen plan's enumeration and its five correction blocks.

## Counter agreement — 6/6, green

`python3 tools/round82-selfrecord-round81.py --repo .` at `384ef1d5` (counter sha256
`381e8639b4d976f803462441de95b340a1bbf872d5bbb0b875c722fe1975c526`, worktree bytes == HEAD blob):
`SELFRECORD_R81 claims=6 mismatches=0 corrected=5 unbacked=0`, **exit 0**. Its per-fact lines agree with
the table fact for fact: F1–F5 `corrected` with exactly the declared/witness pairs above, F6 `holds`.
**No disagreement** — the headline is agreement, not a counter defect.

Controls observed at the same tip: `--selftest` → `SELFRECORD_R81_SELFTEST pass=19 fail=0`, exit 0;
`--no-corrections` → `SELFRECORD_R81 claims=6 mismatches=5 corrected=0 unbacked=0`, exit 1 (the target is
unreachable without the five blocks); `--enumerate` → `SELFRECORD_R81_ENUM claims=6 stale=5 corrected=0`,
exit 1 (enumeration ignores corrections by construction — counter lines 373-374).

## Seventh-fact scan

Full table: `EX01FactRederive/seventh-scan-full.md`. No seventh *receipt-stale, uncorrected* numeric fact
exists in §Round 81. Everything else re-derives green (`stale=6`, `corrected=6`, `mismatches=6`,
`pass=13`, `pass=26`, `arms=11`, `events=63`, `accepted=53`, `late=10`, `bad_*=0`, `88 rows`,
`ten events` = 10 distinct (commit,file) pairs, `14 seats` = `w1-results.json`, `08eb6949`), or is a
superseded value already answered by a committed correction (`LOG.md:3410` `pass=16 -> pass=22`;
`LOG.md:3388` `pending=0 -> pending=1`, whose new value is F5 itself).

The one live numeral contradicted by the tree is **correction prose**, not a graded fact: tip
`SCORECARD.md:4958` (inside the appended `#### round-82 correction` block that sits in the §Round 81
region, line 4952, before `## Round 82` at 4962) says *"the tip registry holds 302"*, but commit
`962bd251` — the same commit that writes the sentence — already carries **305** rows (parent `5fe3c58c`:
302; tip now 305). The round's own record names the correct numbers: `corpus/lessons/round-82.md:85-92`
(freeze divergence 5) `301 (declared) → 302 (base) → 305 (tip)`. The `new=log81-frontier-rows=302` token
is still right for the sealed/base witness and the counter binds F2 to the base revision
(`registry-base-bound` selftest arm), so the token grades green while the prose is wrong. Not a seventh
receipt-bound fact; reported as prose drift for the L1.

## Files written (all inside the seat dir; nothing else written)

- `EX01FactRederive/EX01.json` — per-fact declared/observed/stale, sealed/tip revisions, F2 count disclosure.
- `EX01FactRederive/EX01.md` — 30-line summary.
- `EX01FactRederive/rederive.py` — the independent derivation (git-show only; mechanically reproducible).
- Receipts: `rederive.{out,err}`, `EX01-counter-final.out`, `EX01-counter.out/.err`,
  `EX01-counter-enum.out/.err`, `EX01-counter-selftest.out`, `EX01-counter-nocorr.out`,
  `r81-debt-selftest.out`, `sealed-extracts.txt`, `seventh-scan.txt`, `seventh-scan-full.md`,
  `sealed-r81-plan.md` (frozen plan blob at sealed).

## Evidence (absolute paths · command · exit)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/EX01FactRederive/EX01-counter-final.out`
  · `python3 tools/round82-selfrecord-round81.py --repo .` (rev `384ef1d5`) · **exit 0**,
  `SELFRECORD_R81 claims=6 mismatches=0 corrected=5 unbacked=0`.
- `…/EX01FactRederive/EX01-counter-nocorr.out` · `… --no-corrections` · **exit 1**, `mismatches=5`.
- `…/EX01FactRederive/EX01-counter-selftest.out` · `… --selftest` · **exit 0**, `pass=19 fail=0`.
- `…/EX01FactRederive/EX01-counter-enum.out` · `… --enumerate` · **exit 1**, `stale=5 corrected=0`.
- `…/EX01FactRederive/rederive.out` / `rederive.err` · `python3 rederive.py` · **exit 0**,
  `EX01_REDERIVE claims=6 stale=5 holding=1`.
- `…/EX01FactRederive/r81-debt-selftest.out` · `python3 tools/round81-append-debt.py --selftest`
  (rev `384ef1d5`) · **exit 0**, `APPEND_DEBT_SELFTEST pass=25 fail=0` (evidence for the tip
  `pass=22 -> pass=25` correction).
- `…/EX01FactRederive/sealed-extracts.txt` · `git show 1b64f66d…:{SCORECARD,LOG,SKILL}.md` line extracts.
- `…/EX01FactRederive/seventh-scan-full.md` · numeric inventory + per-claim receipt verification.

## Risks / notes

- The lane moved during the seat (`bacae072` → `4beb4f2b` → `384ef1d5`); every receipt names the revision
  it graded, and the counter bytes were pinned by sha256. A later L1 commit can move the tip again, but
  the graded bytes (sealed record + round-81 receipts) are immutable.
- F2's witness revision is the one genuine freeze divergence: sealed/base 302, live tip 305. The counter
  reads the base (302), my derivation read the sealed (302); both agree, and neither reads the live tip.
  The correction prose at `SCORECARD.md:4958` says "tip … 302" and is the only place that conflates them.
- No blocker, no dead dependency seat; no labrat was needed. Scratch `$S` deleted after the copy.

Tool installs: none required.
