# R57Item12CounterSemantics — round 57 seat report

Seat: `R57Item12CounterSemantics` (role: connector, leaf; no subagent dispatch). Item: `round57/CounterSemantics/12`. Axes judged: calibration, operability. Lane: kama (`kama-shokunin`). Scope: trace counter section-selection and maxN from source for `tools/round42-selfdesc-reconcile.py`; report semantic gaps. No shared-file edits, no commits, no pushes, no installs (none performed). Case-33 independent evidence is a separate file: `.ufo/waves/round-57/reports/R57Item12CounterSemantics-case33.md`.

Report path note: the seat spec names no `Report:` trailer path for this seat; this file is the path chosen. Receipts: `.ufo/waves/round-57/measured/R57Item12/`.

## Pinned tips (the lane tip moved during the seat)

`HEAD` advanced during the run: `7c873d7b` (claim freeze) → `7b74e2f2` → `8640e34c` (round-57 measured-outcomes commit, which also adds a `## Round 57` section). All counter runs below are pinned to a SHA via `--tip`:

- `b89bdab2cc114735ec5d331c6c610134258f7864` — frozen base named in `controls/freeze.txt`.
- `7c873d7b` (claim-freeze tip, abbreviated as given in `git log`; same counter output as base).
- `8640e34cad02adcd247ba0862da63f6fb2aab0df` — tip at measurement time (pinned tip).

Runs used a scratch clone of the lane repo at `/fast/scratch/hyaku/kama-r57/R57Item12CounterSemantics/clone` (guard asserted: `git rev-parse --show-toplevel` = clone path before every mutation). The lane tree was not written; `PYTHONDONTWRITEBYTECODE=1` was set. Scratch is removed at the end of the seat; all receipts are copied to the wave path.

## Answers

**1. maxN is the greatest `## Round N` heading in SCORECARD, not any canonical or calibration figure.**
Source: `tools/round42-selfdesc-reconcile.py:167-168` — `rounds = [int(m.group(1)) for l in lines for m in [re.match(r"^## Round (\d+)", l)] if m]; maxn = max(rounds)`. It scans the whole file, including appended historical sections, and it is position-agnostic.

Consequence for the claim "counter reports maxN=56 instead of expected 46":

- At the frozen base `b89bdab2` the counter prints `maxN=56`, which equals the SCORECARD banner `Latest measured round: 56` (banner check passes, `banner=0`). Under the counter's own contract 56 is the correct value. Receipt: `measured/R57Item12/B-b89bdab2-frozen-claim-base.out`, exit 1:
  ```
  tip=b89bdab2cc114735ec5d331c6c610134258f7864
  r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False
  detail: r41 calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '42' (exit 0)
  ```
- **No derivation in the tree yields 46 at any tip checked.** Candidate counts tried: distinct round headings ≤46 (40), all `## Round` headings ≤46 (48), canonical rows with first-working ≤46 (10), canonical round (49, 11 rows). The only literal `maxN=46` in the wave is the hard-coded print in the no-op controls (`controls/c1-noop.py:3`, `noop-c1.out`, `noop-c2.out`).
- **Provenance of 46:** it is the stale output of round 46. `git grep maxN=46 8640e34c` hits `.ufo/waves/round-46/measured/r42-final.out` (`maxN=46 met=True`), `r42-tip.out`, `r42-fix.out`. Using 46 as the "expected" value would reintroduce a stale round-46 literal, the defect class the round-56 outside review routed as must-fail (no-op/literal harness).
- The real mismatch at the base was not maxN. It was the r41 calibration literal: SCORECARD's calibration row said `→ \`42\`` while the committed count is 43 (`ls corpus/lessons/*verifier-spotcheck.md | wc -l` → 43). That row was changed `42 → 43` in commit `7b74e2f2` (`git diff 7c873d7b HEAD -- SCORECARD.md`, one line). The counter tool itself was not changed. The amendment (`controls/freeze-amendment.txt`) specifies exactly this: "update only the stale self-description count and require `mismatches=0`."

**2. At the pinned tip the counter is green, so "C1" as framed has no failing counter left to repair.**
Receipt `measured/R57Item12/B-pinned-tip.out`, exit 0:
```
tip=8640e34cad02adcd247ba0862da63f6fb2aab0df
r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=57 met=True
```
This is caused by SCORECARD content edits (the 42→43 count and the new `## Round 57` section with banner "round 57"), not by a counter change. `tools/round42-selfdesc-reconcile.py` and `tools/round41-scorecard-reconcile.py` are unchanged between `b89bdab2` and `8640e34c` (`git diff --stat b89bdab2 8640e34c -- tools/round42-selfdesc-reconcile.py tools/round41-scorecard-reconcile.py` prints nothing; checked after the runs).

**3. Semantic gaps in section selection and maxN (confirmed by mutation at the pinned tip).**

Mutation battery: `scratch mutants.py`, 12 mutants of the pinned SCORECARD, one commit each, counter run at each commit. Receipts: `measured/R57Item12/<label>.{diff,out}`, summary `measured/R57Item12/summary.tsv`. Oracle cross-check (independent re-derivation, see case-33 file): `measured/R57Item12/oracle.tsv`.

| Mutant | What it does | Tool verdict | Gap |
|---|---|---|---|
| M1 | append `## Round 58` heading, banner and plan untouched | met=False, mismatches=3 (banner, planned) | none: coupling works as designed |
| M2 | append `## Round57` (no space) heading | met=True, maxN=57 | **G1** heading regex requires a space; the file already has a `## Round24` heading (SCORECARD line 1245) that is silently excluded |
| M3 | newer canonical table (12 → 1 row decoy) with colon-form header `as of round 58:**` | met=True | **G2** canon regex requires `round N**`; colon-form canonical headers are invisible; the stale round-49 table stays canonical (the same colon form already exists at SCORECARD line 747) |
| M3b | same table, bold-closed header | met=False (caps, saturation) | detected; but retired passes by substring luck (see G4) |
| M4a | `### Planned (round 58)` heading moved from the Round 57 section to EOF | met=True | **G3** planned check accepts a plan heading anywhere in the file; section scope is not checked |
| M4b | as M4a, plus §Planned prose no longer backtick-names the heading | met=False, planned=1 | shows the check passes only because the §Planned prose contains the string "`### Planned (round 58)`" (SCORECARD line 53); the prose is a superseded pointer |
| M5a | second `## Retired` appended at EOF saying "16 axes and 111 capabilities ... both assigned axes are retired" | met=True | **G5** `sections(...)[:1]` reads only the first heading; duplicates are silently ignored |
| M5b | first Retired changed to "16 axes and 111 capabilities" | met=True | **G4** substring checks: `"6 axes" in` and `"11 capabilities" in` match inside "16 axes" and "111 capabilities" |
| M5c | first Retired gets the two forbidden phrases | met=False, retired=2 | detected (control) |
| M6 | fenced ```` ```text ```` block with a `## Retired` decoy placed before the real section, real section made false | met=True | **G6** `sections()` is fence-unaware; a fenced heading shadows the live section |
| M7a | missing `.ufo/...` receipt cited in the Round 56 section | met=True | **G7** receipts check runs only for headings naming round 40/41 (`RECEIPT_ROUNDS = (40, 41)`, line 75) |
| M7b | same missing receipt in the Round 41 section | met=False, receipts=1 | detected (control) |

Tally: 12 mutants, the tool detects 5 (M1, M3b, M4b, M5c, M7b), and 7 survive (M2, M3, M4a, M5a, M5b, M6, M7a). Survivors are all shortcut-satisfiable by prose, a literal, or a duplicate/fenced heading. This is the per-counter shortcut tally the `considerthese/2026-10-26.md` proposal 3 asks for.

Additional gaps, source-only, not mutated:

- **G8 hard-coded scope.** `NEEDLE`, `ASSIGNED`, `SAT_LINE = 8`, `RECEIPT_ROUNDS = (40, 41)` (lines 70-75) and the imported `round41-scorecard-reconcile.py` are literals, not derived from maxN. Scoping receipts to all rounds is not a one-line change: a scratch scan at the pinned tip finds 298 unique backticked `.ufo/` citations in SCORECARD, of which 48 do not resolve in the commit tree (`measured/R57Item12/ufo-cites-check.txt`; the independent oracle finds the same 48). Extending the check would need adjudication of historical citations; this seat does not decide that.
- **G9 first-table rule.** `table_rows()` takes the first table after a canonical header, wherever it is in the file, and `canon()` takes the maximum header over the whole file, although the Capabilities mirror text says "the counters resolve the highest-numbered canonical heading below this line". The "below this line" rule is not enforced (SCORECARD line 117 says so; line 2844 is the round-49 header).
- **G10 banner coupling.** The banner check compares head text to the maxN that the same file defines. The check is internally consistent, so it cannot detect a stale banner that happens to match a heading; it only detects a heading without a banner update (M1).
- **G11 live instance of G6.** The pinned tip already contains a fenced heading: SCORECARD line 2969 (`## Round 30 — self-assessment corrections (recall population)`) sits inside a five-backtick fence quoting a deleted section (`git show 8640e34c:SCORECARD.md | sed -n 2969p`). `sections()` and `maxN` read it as a real heading. It is harmless today (no assigned section precedes it; 30 < 57), so the fence gap is present now, not only in the mutant.

**4. Round-56 outside defects, lesson-addressed for this counter.** The round-56 spot-check routed "a roster literal/no-op harness must fail" and "bind actual executed entries." For the self-description counter the same class appears as G2-G7: the counter is satisfied by prose pointers, literal strings, duplicate headings, fenced text, and round-scoped receipts. Lesson text for L1 (not written here, shared file): cite M2-M7a as the counter's measured shortcut survivors at `8640e34c`.

**5. Claim-ordering conflict for L1 (reported, not resolved).** The dispatch and seat context frame C1 as calibration (stale maxN) and C2 as operability (canonical-row binding). `controls/freeze-amendment.txt` (committed "before any seat findings") says C1 is the round-56 prereg-check no-op (operability) and C2 is this counter's stale count (calibration), and that it "supersedes the earlier round-57 freeze's claim ordering only". Under the amendment, this counter's repair is C2 and it is already done in SCORECARD (`7b74e2f2`); under the dispatch it is C1 and the stated expected value (46) is not supported by the tree. L1 must choose the ordering; this seat did not.

**6. Recommendations (advice only; no edits made).**
- Do not set any expected maxN to 46. If maxN must be pinned, derive it as the greatest `## Round N` heading (already the behavior) and keep the banner check; add a red control that adds a `## Round N+1` heading without updating the banner (M1 already does this).
- Repair G1-G7 only with per-gap controls: colon/bold canon form in one regex; section-scoped Planned check; exact token counts for "N axes"/"N capabilities"; `sections()` that skips fenced blocks and rejects duplicate headings; receipts scope decided by maxN or by an explicit list, with the 48 unresolved citations adjudicated first.
- Keep `met=True` claims out of the lane narrative until a red control for each survivor exists.

## Verification ran (exact commands)

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/round42-selfdesc-reconcile.py --repo <scratch clone> --tip <sha>` for `b89bdab2…`, `7c873d7b`, `8640e34c…`, and each mutant commit → receipts above (exit 1, 1, 0).
- `python3 mutants.py 8640e34c… <wave path>` → `measured/R57Item12/summary.tsv`; battery wall time 144 s.
- `CL=<scratch clone> python3 oracle.py summary.tsv 8640e34c…` → `measured/R57Item12/oracle.tsv` (see case-33 file).
- `git show 8640e34c:SCORECARD.md | grep -o '`\.ufo/…`'` → `measured/R57Item12/ufo-cites-check.txt` (298 unique, 250 resolve, 48 do not).

Not run by this seat: lane gate, full test suite, other counters (per assignment). Not performed: source-URL re-open of S515 and admit/reject spot-check (owned by other seats; not in this item).

## Installs and versions

None. Tools used: `git`, `python3` (system interpreter). No package install, no update.

## Observed state (not caused by this seat)

At my last `git status --porcelain` the working tree showed ` D .ufo/waves/round-57/controls/noop-c2.out` (a tracked frozen control receipt missing from the working tree). This seat only read that file (`cat`) and never wrote to the lane tree. L1 should restore or explain it before the controls are cited.
