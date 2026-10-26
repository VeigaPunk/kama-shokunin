### Round-46 append-only audit

The lane treats five files as append-only — `SCORECARD.md`, `LOG.md`,
`corpus/QUALITY.md`, `corpus/README.md`, `corpus/SOURCES.md`; earlier outside
closures read a round's SCORECARD diff as `+65/−0` / "0 removed lines" and called
that append-only (`corpus/lessons/round-29-verifier-spotcheck.md:32`,
`corpus/lessons/round-30-verifier-spotcheck.md:41`). `python3
tools/append-only-audit.py --repo <lane> --to 4a2a4d55` sets that description
against 294 commits and exits **1**:

```
event dd9f5dc6c0e6 SCORECARD.md deleted=31 restored_at_tip=24 status=partial restored_by=-
event 0718b6abbda6 SCORECARD.md deleted=2417 restored_at_tip=2416 status=partial restored_by=-
event 0718b6abbda6 LOG.md deleted=2290 restored_at_tip=2290 status=restored restored_by=82b5e9d33a19
event 0718b6abbda6 corpus/QUALITY.md deleted=375 restored_at_tip=375 status=restored restored_by=82b5e9d33a19
event 0718b6abbda6 corpus/README.md deleted=663 restored_at_tip=663 status=restored restored_by=82b5e9d33a19
summary commits=294 events=5 restored=3 partial=2 unrestored=0
```

The same command at `0163fea2` (292 commits) and at the tip as read (`96d32918`,
295 commits) reports the same five events, so the picture is not an artifact of one
revision. Five is the count **above the frozen threshold**: `--threshold 1` on
the same tree reports 66 events (SCORECARD 23, SOURCES 20, LOG 13, README 8,
QUALITY 2; 11 restored, 6 partial, 49 unrestored) and exits 1. "Append-only"
here is a statement about deletions of >= 20 lines in one commit, not a
byte-level property of the five files.

**The three restored events are one bug and one repair.** `0718b6ab` (round-45
integration, 2026-10-26 07:46) deleted 2,290 lines of `LOG.md`, 663 of
`corpus/README.md`, 375 of `corpus/QUALITY.md` and 2,417 of `SCORECARD.md` — 5752
deletions against 565 insertions in that commit. `82b5e9d3` (07:50, "restore
SCORECARD/LOG/QUALITY/README bodies truncated by the previous commit (append
bug)") put them back text-for-text: `LOG.md` 2290/2290, `corpus/README.md`
663/663, `corpus/QUALITY.md` 375/375, `SCORECARD.md` 2416/2417 (`git show
--numstat 82b5e9d3 -- SCORECARD.md` → `2428 0`, a pure addition). No body line of those four files was lost.

**The two partials are the SCORECARD head, which the file declares re-derived.**
The round-42 event `dd9f5dc6` removed 31 lines, and 24 are held again:

- 23 came back in the same commit as archived blocks under §Historical head
  sections — the round-5 banner (8 lines), the round-5 plan (9) and the round-3
  Retired block (6);
- 1 (`## Saturation`) is held only because the current head carries the same
  heading; its archived copy was retitled `### Saturation (round-10 text)`;
- the 7 not held are the six round-41 `## Axes` rows and the round-41 reconcile
  sentence. The rows survive only as re-anchored rows (`depth` in that diff:
  `SKILL.md` sha256 `151023b9…`, 1375 lines, `grep -c '^## '` → `30`; at the tip
  `3046955b…`, 1432 lines, `33` — `git show dd9f5dc6^1:SCORECARD.md | grep -c
  151023b99bec` → `1`, `grep -c 151023b99bec SCORECARD.md` → `0`), and the
  round-41 sentence survives only inside the tip line (`grep -c 'Reconciled in
  round 41 against the measured commit' SCORECARD.md` → `1`).

The round-45 event `0718b6ab` left exactly one line unrestored of its 2,417: the
pre-round-45 `depth` row (`SKILL.md` sha256 `91440eb8…`, 1420 lines, `32`
headings), replaced inside the repair commit by the re-anchored row
(`3046955b…`, 1432, `33`): `git show 82b5e9d3^1:SCORECARD.md | grep -c 3046955b`
→ `0`, `git show 82b5e9d3:SCORECARD.md | grep -c 3046955b` → `1`.

What that means for the claim "SCORECARD.md is append-only":

- For the record it holds. No round section, correction row, historical table
  or capability row is among the unrestored lines; `unrestored=0`, and the
  three mass deletions of body text were repaired text-for-text.
- For the head it does not, and the file itself says so: `SCORECARD.md:6`
  declares the `## Axes` table, §Planned, §Retired, §Saturation and
  §Capabilities re-derived from the tree by `tools/round42-selfdesc-reconcile.py`
  since round 42. Both partials are that carve-out exactly — 7 superseded head
  lines in round 42, 1 superseded head row in round 45.
- The head's own promise is wider than its practice. `SCORECARD.md:6` says "the
  round-5 banner and the head sections they replace are kept verbatim under
  §Historical head sections"; the round-5 banner, round-5 plan and round-3
  Retired block are (23 lines), but the `## Axes` rows it re-derives are not
  archived — the six round-41 rows and the round-45 `depth` row exist only in
  git history. Either those rows are appended under §Historical head sections,
  or the sentence is narrowed to the blocks that are.

**Limits of the instrument, read off its own output and source.**

- `restored_by=-` on a partial is definitional — no later commit holds *every*
  deleted line — and does not mean nothing was restored: `82b5e9d3` holds
  2416/2417 counted lines (1789/1790 unique) of the SCORECARD event.
- `restored_at_tip` is set membership, not position or identity: a deleted line
  that recurs as another line counts, which is how `## Saturation` is "held".
- The filter at `tools/append-only-audit.py:102` (`not x.startswith("---")`)
  drops deleted lines whose *text* begins `--`, as if each were the `---`
  header: four `--out …` lines in the SCORECARD event
  (`git show 0718b6ab^1:SCORECARD.md | grep -c '^--out '` → `4`; at the tip →
  `4`) and two (`--tip …`, `--rev …`) in the LOG event. A header-aware recount
  (`.ufo/waves/round-46/w1/out/S2Events/recount.py`) reads `2421`/`2420` for SCORECARD and
  `2292`/`2292` for LOG; no verdict class changes, and the counter
  `tools/round46-append-audit-check.py:115` carries the same filter, so tool and
  counter agree on the undercount.

**Verdict.** The five-file append-only self-description survives its own history
at mass-deletion scale: 0 unrestored, 3 repaired text-for-text after a real
truncation, 2 accounted head re-derivations, 0 lost record lines. It does not
survive as a literal whole-file claim; the honest form is that the record is
append-only while the head is re-derived, and the head's superseded rows are not
archived. The instrument is red at the tip (exit 1) and this section reports the
red, not a green.

---

## Seat notes — S2Events (not part of the section text above)

### Provenance of every figure

| Figure | Command | Exit | Receipt |
|---|---|---|---|
| 5 events / 3 restored / 2 partial / 0 unrestored at `4a2a4d55`, 294 commits | `python3 tools/append-only-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --to 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050` | 1 | `audit-at-4a2a4d55.out` |
| same 5 events at `0163fea2`, 292 commits | same with `--to 0163fea2dab3f282ebd70c71da9ab5de4cedf733` | 1 | `audit-at-0163fea2.out` |
| same 5 events at tip `96d32918`, 295 commits | same with `--to HEAD` | 1 | `audit-at-head.out` |
| 66 events (11/6/49) at threshold 1 | same with `--threshold 1 --json` | 1 | `audit-threshold1.json` |
| `AOA_SELFTEST pass=10 fail=0` | `python3 tools/append-only-audit.py --selftest` | 0 | `selftest.out` |
| header-aware 2421/2420, 2292/2292, 31/24, 663/663, 375/375 | `python3 <out>/S2Events/recount.py <lane> 4a2a4d55` | 0 | `recount.out` |
| C2 legs at `4a2a4d55`: `selftest=1 fixture=1 lane=1 table=0 lane_events=5 lane_partial=2 met=False` | `python3 tools/round46-append-audit-check.py --repo <lane> --tip 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050 --scratch <scratch>` | 1 | `c2-counter-at-4a2a4d55.out` |
| SCORECARD event breakdown 8/1/6/9/6/1 = 31 | `git diff --no-renames --no-color --no-ext-diff -U0 dd9f5dc6^1 dd9f5dc6 -- SCORECARD.md` | 0 | `recount.out`, this note |
| 2416/2417 held by `82b5e9d3`; `2428 0` numstat | `git show --numstat 82b5e9d3 -- SCORECARD.md` + counted intersection | 0 | `recount.out` |
| no round section/correction row among unrestored lines | `recount.out` `absent:` lines: six `## Axes` rows + one reconcile sentence | 0 | `recount.out` |

`table=0` at `4a2a4d55` is expected: the C2 counter's table leg needs the
capability row naming `append-only-audit` with last cell `46`, which is this
round's entry and lands with the measured commit. The measured result belongs to
§Round-46 measured results, not to this paragraph.

### Findings

**F1 (instrument, frozen) — the `---` filter also drops `--…` content lines.**
`tools/append-only-audit.py:102` and `tools/round46-append-audit-check.py:115`
both read `not x.startswith("---")`. After the diff marker is stripped, a
deleted content line that begins `--` (a wrapped `--out`, `--tip`, `--rev`) is
excluded as if it were the `---` header, contradicting the docstring ("the
`---` header excluded"). Evidence: `git show 0718b6ab^1:SCORECARD.md | grep -c
'^--out '` → `4`; the SCORECARD event reads `deleted=2417` where the
header-aware count is `2421` (LOG: `2290` vs `2292`). Verdict classes
unchanged. Proposed fix (not applied — both files are frozen; the counter
carries `counter_sha256 4dcfbe10…`):

```diff
-            dele = [x[1:] for x in d.split("\n") if x.startswith("-") and not x.startswith("---")]
+            body = d.split("\n")
+            dele = [x[1:] for i, x in enumerate(body) if x.startswith("-")
+                    and not (x.startswith("---") and i + 1 < len(body) and body[i + 1].startswith("+++"))]
```

Applied to the frozen tool, this changes two `deleted`/`restored_at_tip` pairs
and no `status`/`restored_by` value, so C2's `lane` leg still agrees if both
copies take the fix in the same round.

**F2 (self-description) — §Historical head sections covers less than
`SCORECARD.md:6` promises.** The sentence says "the round-5 banner and the head
sections they replace are kept verbatim under §Historical head sections". The
`## Axes` rows re-derived in rounds 42 and 45 are not archived: `grep -c
151023b99bec SCORECARD.md` → `0`, `grep -c 91440eb8 SCORECARD.md` → `0`, both
present in the pre-change files (`git show dd9f5dc6^1:SCORECARD.md`,
`git show 0718b6ab^1:SCORECARD.md`, each `1`). Proposed narrowing of the
sentence at `SCORECARD.md:6` (full proposed line text in
`proposed-scorecard-head-line6.txt`):

> … the round-5 banner, the round-5 plan and the round-3 Retired and round-10
> Capabilities blocks they replace are kept verbatim under §Historical head
> sections; the superseded `## Axes` rows are kept in git history only.

The alternative fix — appending each superseded row as a dated line under
§Historical head sections — is what would make the claim unqualified but adds
about seven lines per re-anchoring round.

**F3 (contract limit, disclosed, no fix).** `restored_by` is null for a partial
by definition, so the check cannot name the commit that restored the bulk of a
partially restored file (`82b5e9d3`, 2416/2417). That is the frozen contract,
not a defect; the paragraph states it so a reader does not read `-` as "nothing
came back".

### Out of scope / not done

- The capability-table row for `append-only-audit` (C2's `table` leg) is not
  added here; that is the round's capability entry.
- No counter, preregistration or control was edited; the F1 fix is proposed
  only, in this directory.
- No measured-commit receipt is filed: the measured commit does not exist yet;
  this paragraph reports `4a2a4d55`, `0163fea2` and `96d32918`.
