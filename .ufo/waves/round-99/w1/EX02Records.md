# EX02Records — independent attack on C2 (`tools/round99-record-audit.py`, 12 checks)

Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`
Base `439fdb3d41b55e5b9e6d7c480d17f2c428bae978`; freeze commit `f6e7ccc285e0c1207378f73c394acbfda58bff23`
(the commit that adds `plans/round-99-claims.md` and the three instruments).
Graded counter bytes at freeze: `git show f6e7ccc2:tools/round99-record-audit.py`, sha256
`5e2be1391e199aa60adf5045d3cef87cc83115f951e13824ec984e7b87ed08f6` (261 lines; copied to
`out/EX02Records/receipts/counter-freeze.py.txt`).
Working tree currently carries an **uncommitted** change to the same file (it deletes the 3-line
`--tree` branch of `read_bytes_at` and adds 2 comment lines), sha256
`59f22d5e…a138ed` (`git diff -U3 -- tools/round99-record-audit.py`, receipt
`receipts/counter-freeze-vs-working.diff`).
Unless stated, runs below use the **freeze bytes**.

Verdict summary: the predicate is reachable — at a synthetic M2 carrying the working-tree corrections the
frozen counter prints `RECORD_AUDIT99 checks=12 mismatches=0 met=True rev=…` and exits 0 — and the
do-nothing control is real (10 mismatches at base). But the record checks are token-presence/union checks
that accept flat contradictions (3–6, 9–11), check 7 does not bind the two revision hashes (the exact class of the M2
mislabel it exists to correct), the union-of-both-blocks shape lets one file satisfy the other file's
propositions, and the freeze-committed `--tree` mode cannot run the forged control at all.

## 1. Base run at the freeze bytes (`--rev 439fdb3d`)

Command (receipt `receipts/base-run-frozen.txt`):

```
python3 /fast/scratch/hyaku/kama-r99/EX02Records/frozen/round99-record-audit.freeze.py \
  --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev 439fdb3d \
  --work /fast/scratch/hyaku/kama-r99/EX02Records/work
```

Output (full):

```
RECORD_AUDIT99_MISMATCH 1 SCORECARD block states 12 reported, 0 dead after the stale line
RECORD_AUDIT99_MISMATCH 2 LOG block states 12 reported, 0 dead after the stale line
RECORD_AUDIT99_MISMATCH 3 both stale pointers named
RECORD_AUDIT99_MISMATCH 4 7 attack ['CR01Boundary', 'CR02Wording', 'MT01Forgeries', 'RV01SelfAssess', 'RV02BudgetCells', 'RV03Intent', 'SN01StepFlips'] / 5 non-attack ['CN01Overlap', 'EX01SelfAssessControl', 'EX02BudgetControl', 'SC01SiblingScan', 'SC02SourceReopen']
RECORD_AUDIT99_MISMATCH 5 EX02BudgetControl named against SB01-equivalent
RECORD_AUDIT99_MISMATCH 6 RV03Intent named
RECORD_AUDIT99_MISMATCH 7 lesson carries the base/tip census correction
RECORD_AUDIT99_MISMATCH 9 gate failed arms ['newest-closure', 'round-clean', 'round-scope', 'round75-instruments', 'round78-instruments', 'selfdesc']
RECORD_AUDIT99_MISMATCH 10 carried M3 sampling record inside ## Mistakes
RECORD_AUDIT99_MISMATCH 11 seats=12 results=12 dead=[]
RECORD_AUDIT99 checks=12 mismatches=10 met=False rev=439fdb3d41b55e5b9e6d7c480d17f2c428bae978
```

Exit **1**. Mismatch ids: **1,2,3,4,5,6,7,9,10,11** (8 and 12 are green at base).
This reproduces the committed `controls/c2-base.out` byte-for-byte over the `RECORD`/`exit` lines
(`diff` → IDENTICAL; receipt `receipts/base-run-frozen.txt`), and the working-tree counter produces the
identical rev-mode output (`receipts/base-run-current.txt`), as expected: the only byte difference sits in
the `--tree` branch, which rev mode never takes.

Record inconsistency found here: `tools/round99-record-audit.py:10` says the base control prints
`mismatches=9`; the actual output, `plans/round-99-claims.md` §C2, `claims.json` C2.before and
`controls/c2-base.out` all say **10**. The frozen docstring is the lone outlier.

## 2. Hand re-derivation of every proposition the claim freezes

### 2.1 Wave population: 12 seats / 12 results / 0 dead, 7 attack / 5 non-attack

From `git show 439fdb3d:.ufo/waves/round-98/w1-results.json` (independent Python, not the counter):

```
seats field: 12 len: 12
dead(empty output): []
counts: 7 5
attack: ['CR01Boundary', 'CR02Wording', 'MT01Forgeries', 'RV01SelfAssess', 'RV02BudgetCells', 'RV03Intent', 'SN01StepFlips']
non:    ['CN01Overlap', 'EX01SelfAssessControl', 'EX02BudgetControl', 'SC01SiblingScan', 'SC02SourceReopen']
```

`RV01SelfAssess`/`RV02BudgetCells` (reviewer), `CR01Boundary`/`CR02Wording` (critic), `MT01Forgeries`
(mutation-tester), `SN01StepFlips` (sentinel), `RV03Intent` (revenger) = 7; `SC01SiblingScan`,
`SC02SourceReopen` (scout), `EX01SelfAssessControl`, `EX02BudgetControl` (executor), `CN01Overlap`
(connector) = 5. Every `output` is non-empty (shortest 636 bytes). All five committed record files are
byte-identical between `439fdb3d` and `f6e7ccc2` (`git diff --stat` for `SCORECARD.md LOG.md
corpus/lessons/round-98.md .ufo/waves/round-98/w1-results.json
.ufo/waves/round-98/measured/pre-report-gate.out` is empty); `corpus/lessons/round-99.md` is in neither
commit. The tree copies' provenance is clean.

### 2.2 Census groups at the two frozen historical revisions

`git show <rev>:corpus/SOURCES.md` → scratch file, then
`bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --file <file>` (receipts
`receipts/census-base.tsv`, `receipts/census-tip.tsv`; `rc=0` both, empty stderr):

| revision | rows | A | B | C | mined | queued | rejected |
|---|---|---|---|---|---|---|---|
| base `681c80a4e3c745c22559f74b2c2a1917bdc66fc6` | 361 | 344 | 11 | 6 | 324 | 8 | 29 |
| r98 tip `649bb2e94501ee8aa2d4ceaeae52f7a1fb8d1ce9` | 363 | 345 | 11 | 7 | 325 | 8 | 30 |

These match `EXPECT_BASE`/`EXPECT_TIP` in the counter and the plan exactly. The census generator is a
**fleet-repo** file (`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh`, sha256
`3fb7261569f46423dd80ecc23e0a23789a7926f667c7a3fc559d2439d4a64e30`); it is not in the lane repo and the
lane has no `scripts/` directory, so the plan's relative `scripts/sources-census.sh` does not resolve from
the lane root. Absolute-path use is an existing lane pattern (`tools/round42-capacity-audit.py:76`,
`tools/round43-health-audit.py:88`), but the plan's "the frozen census generator" is not byte-pinned by
anything committed in the lane — see §6 F8.

### 2.3 Gate receipt: verdict line and the six failed arms

`git show 439fdb3d:.ufo/waves/round-98/measured/pre-report-gate.out` (sha256 `3e2ecc31…`), 14
`PRE_REPORT_ARM` lines, verdict at line 15:

```
PRE_REPORT round=98 arms=14 failed=6 uncommitted=1
```

Six arms print `FAIL`:

| arm | exit | note |
|---|---|---|
| `selfdesc` | 1 | closure_ptr red |
| `newest-closure` | 2 | COULD_NOT_EVALUATE |
| `round-scope` | 1 | stray untracked receipt |
| `round-clean` | **0** | prints FAIL (the round-98 erratum omitted this arm) |
| `round75-instruments` | 1 | APPEND_DEBT bad_rows=19 |
| `round78-instruments` | 1 | LIVE_RECONCILE_SELFTEST fail=3 |

The counter's regex `^PRE_REPORT_ARM (\S+) exit=\d+ FAIL` correctly catches `round-clean exit=0 FAIL`;
the sorted re-derivation equals the hardcoded list exactly.

### 2.4 The stale surfaces the corrections answer

- `SCORECARD.md:6431` “12 dispatched seats, 10 reported, 2 dead — `RV03Intent-2` and
  `EX02BudgetControl-2`…”; `LOG.md:4040` the same claim. The pointers the corrections name are the real
  stale lines; `LOG.md:4044` is the real “SB01-equivalent prose” misattribution.
- `corpus/lessons/round-98.md:28` “tiers measured with the census at HEAD (361 rows: A 344, B 11, C 6…)”
  — the base figures labelled HEAD; the same paragraph then prints base = 361 identical. Defect confirmed.
- Round-98 M3 sits at `corpus/lessons/round-98.md:83`, under `## Spot-check` (line 74); `## Mistakes` is
  lines 37–63. Defect confirmed. M3 itself says both `RV03Intent` and `EX02BudgetControl` settled — the
  evidence that contradicts “2 dead”.

## 3. Materialized tree (`--tree`), the forged control, and three required forgeries

Tree provenance: `SCORECARD.md`, `LOG.md`, `corpus/lessons/round-98.md`, `corpus/lessons/round-99.md`,
`.ufo/waves/round-98/w1-results.json`, `.ufo/waves/round-98/measured/pre-report-gate.out`. All committed
files in that list are byte-identical at base/HEAD; `round-99.md` is the **untracked M2 lesson in the
working tree**. The materialized tree is therefore “M2 records in flight”, not a revision — stated
explicitly because the counter prints `rev=tree:<path>`.

### 3.1 The freeze counter cannot run its own forged control

| run | tree contents | result |
|---|---|---|
| freeze bytes, `--tree`, no `corpus/SOURCES.md` | the assignment's six files | `RECORD_AUDIT99 could-not-evaluate: census revision bytes unavailable`, **exit 2** |
| freeze bytes, `--tree`, `corpus/SOURCES.md` = r98 tip | six files + SOURCES.md | MISMATCH 8 (both groups read the same tip bytes: `base={'rows':'363',…}` vs `EXPECT_BASE`), `mismatches=1`, exit 1 |
| working bytes, `--tree`, no SOURCES.md | six files | `checks=12 mismatches=0 met=True`, exit 0 |

Cause: freeze `read_bytes_at` (`git show f6e7ccc2:tools/round99-record-audit.py:252-256`) prefers
`tree/path` for the two **historical** census revisions, so `--tree` either finds nothing (exit 2) or
compares tip bytes against the base constants. There is no tree that makes the freeze counter grade checks
1–11 while keeping check 8 green. Consequences:

- The on-disk, untracked measurement-time `controls/c2-forged.out` — `rev=tree:/fast/scratch/hyaku/kama-r99/forge`,
  `mismatches=2`, exit 1 — **cannot have been produced by the freeze bytes**. It matches the working-tree
  counter's `--tree` run on the same forgery exactly.
- The working tree's uncommitted fix is a change to graded counter bytes after the freeze commit. On a
  plain reading of C2 K1 (“the graded counter/grader bytes change after the freeze commit”) committing it
  at M2 kills the claim; leaving it uncommitted leaves the committed forged control irreproducible from
  frozen bytes. **L1 decision required.** A freeze-compliance-preserving alternative exists and is
  demonstrated in §3.3: forge a commit in a scratch clone and replay the same forgery through `--rev`,
  which uses only frozen bytes.

### 3.2 Forgery matrix (working counter `--tree`; each variant is one row; full outputs in `out/EX02Records/receipts/forge-*.out`)

| # | forgery in the scratch tree | rc | catches / escapes |
|---|---|---|---|
| A | both correction blocks restored to “10 reported, 2 dead” | 1 | **caught by 1,2** — same mismatch ids and count as `controls/c2-forged.out` (`mismatches=2`) |
| B | right total, wrong split tokens: `6 attack` / `6 non-attack` | 1 | **caught by 4** |
| B2 | `7 attack` / `5 non-attack` tokens kept, all 12 names kept, but `CN01Overlap` moved into the attack list and `RV03Intent` into non-attack | 0 | **escapes** — 4 and 6 are name-presence only; no attribution is bound |
| C | lesson census sentence: base and tip number groups swapped wholesale | 1 | **caught by 7** |
| C2 | swapped groups **plus** one later correct sentence | 0 | **escapes** — check 7 is a whole-file `re.search`, one true sentence rescues a false one |
| D | a second stale `## Round 99 correction` block appended **after** the correct block, stating “10 reported, 2 dead and 6 attack / 6 non-attack” | 0 | **escapes** — `correction_blocks()` concatenates all matching blocks; the correct token in any block satisfies checks 1/2 |
| D2 | the same stale block inserted **between** the stale wave line and the correct block | 0 | **escapes** — placement is anchored to the first 20 chars of the *first* matching block only |
| E | stale duplicate block inserted **before** the stale wave line; correct block still appended after it | 1 | **caught by 1,2 — as a false negative**: the first matching heading now precedes the stale line, so even a valid appended correction cannot pass |
| F | correct block physically moved before the stale wave line | 1 | **caught by 1,2** |
| G | stale block before the wave line headed `## Round 99 CORRECTION` (uppercase) | 0 | **escapes** — `BLOCK_RE` is case-sensitive except `[Rr]ound`; the block is invisible to the reader while remaining visible to a human |
| H | `SCORECARD.md:6431` removed from the SCORECARD block; LOG block still names both pointers | 0 | **escapes check 3** — checks 3–6,9,11 grade `both = s_block + l_block`, not each file |
| K | `## Mistakes` kept, the real M3 paragraph replaced by “**M3 — not carried.** … round-98.md … sampling.” | 0 | **escapes check 10** — three tokens, no semantics |
| K2 | M3 row left in place but `## Mistakes` renamed `## Retrospective` | 1 | **caught by 10** |
| L | an earlier `## Mistakes` heading inserted before `## Gate`, record stays in the later section | 1 | **caught by 10 — false negative**: `section()` returns only the first heading's slice |
| M | “the ‘SB01-equivalent prose’ seat above is **NOT** `EX02BudgetControl`” | 0 | **escapes check 5** — token presence only |
| N | “carries **NOT 12 seats** and **NOT 12 results**” | 0 | **escapes check 11** — substring presence only |
| J | the six failed arm names appended inside “were NOT failed; the receipt is wrong” | 0 | **escapes check 9** — arm names are presence-only; the receipt half still re-derives |
| V | `PRE_REPORT round=98 arms=14 failed=6 uncommitted=1` deleted from both correction blocks, arms kept | 0 | **escapes check 9** — the verdict regex runs over the gate receipt, never over `both`, although the docstring says “The correction names the round-98 gate verdict” |
| O | only the two revision hashes swapped in the lesson census sentence (`base 649bb2e9 → 361 …`, `tip 681c80a4 → 363 …`) | 0 | **escapes check 7** — the regex binds `base`/`tip` labels and the numbers, **not** `681c80a4`/`649bb2e9`; check 8 is independent of the lesson, so nothing catches the misattribution |
| P | SCORECARD correction reduced to “`SCORECARD.md:6431` … 12 reported, 0 dead; `LOG.md:4040` …” only; LOG block full | 0 | **escapes 4,5,6,9,11 per-file expectations** — union again |

Receipt slugs (`receipts/forge-<slug>.out`): A `a-oldcount`, B `b-splitcount`, B2 `b2-membership`,
C `c-swapcensus`, C2 `c2-swap-plus-right`, D `d-dup-after`, D2 `d2-dup-between`, E `e-dup-before`,
F `f-prestale`, G `g-upper`, H `h-union-pointers`, K `k-m3-denial`, K2 `i10-outside`,
L `l-dup-mistakes`, M `m-sb01-denial`, N `n-counts-negated`, J `j-gate-denial`, V `verdict-removed`,
O `revision-hashes-only`, P `scorecard-minimal`.

Direct answers to the three required forgeries:
(a) old “10 reported, 2 dead” → **caught by 1 and 2**;
(b) “right counts, wrong seat split” → wrong 7/5 **tokens** are caught by 4, but the same 7/5 tokens with
**swapped membership** (B2) escape all 12;
(c) “right tokens, census numbers swapped” → swapping the number groups is caught by 7, but swapping only
the **revision hashes** (the precise defect class M2 records: a census group bound to the wrong revision)
escapes.

### 3.3 Freeze-bytes replay of the forged control (`--rev`)

Scratch `git clone --shared --no-checkout` of the lane (6.7 MB, toplevel asserted), records committed with
plumbing only (no worktree checkout, no lane index touched): synthetic M2 `c2237869`; forged M2
`82f07e86` (old counts). Frozen counter, rev mode:

```
RECORD_AUDIT99_MISMATCH 1 SCORECARD block states 12 reported, 0 dead after the stale line
RECORD_AUDIT99_MISMATCH 2 LOG block states 12 reported, 0 dead after the stale line
RECORD_AUDIT99 checks=12 mismatches=2 met=False rev=82f07e866c1c0076f1948f2f8d2ca8d20183e9a9
exit=1
```

i.e. exactly the committed `c2-forged.out` verdict, produced without changing a frozen byte. And at the
unforged synthetic M2 (`c2237869`) both the frozen and working counters print the predicate line

```
RECORD_AUDIT99 checks=12 mismatches=0 met=True rev=c22378699074334d7ae1cd9fcbd5f9dc4d1fc035
```

exit 0 — so the C2 predicate itself is reachable with freeze bytes once the corrections are committed.

## 4. Block regex and `section()` reader

`BLOCK_RE = ^## .*[Rr]ound[- ]99.*(?:correction|corrections).*$` (line 65), `correction_blocks()` (68–75)
joins every match to the next `^## `; `section()` (78–84) takes the **first** `^## Mistakes` and slices to
the next `^## `.

| heading | `BLOCK_RE.match` |
|---|---|
| `## Round 99 correction` | True |
| `## Round 99 corrections` | True |
| `## round-99 correction` | True |
| `## Round 99 — record correction` | True |
| `## Round 99 CORRECTION` | **False** |
| `## Round 99 Correction` | **False** |
| `## ROUND 99 correction` | **False** |
| `## Correction for round 99` | **False** (word order) |

Answers to the two questions:

- **A duplicated/stale correction heading after the wave line passes.** D and D2: any matching block after
  the first stale token, correct or stale, makes checks 1/2 green as long as *one* matching block contains
  “12 reported, 0 dead”; the stale block's contradictory text is never compared. A component can therefore
  carry both the correction and a stale restatement, and the counter reports `met=True`.
- **A duplicate before the wave line does not pass — it poisons the check.** E: because placement is
  `score.find(s_block[:20]) > stale_s.start()` and `s_block` starts at the earliest matching heading,
  a stale-looking heading inserted before the wave line makes checks 1/2 red even when the correct
  correction is appended after it. That is a false negative an editor can trigger without lying.
- **A correction placed before the wave line does not pass** (F), and removing the stale text entirely
  makes `stale_s is None`, also red.
- **A case-variant heading is invisible**: G's `## Round 99 CORRECTION` stale block sits before the wave
  line and the counter never sees it (green).
- `section()` duplicate behavior: an earlier `## Mistakes` heading with no record makes check 10 red even
  when the record exists in the real later section (L); conversely three tokens in any sentence inside the
  first `## Mistakes` slice pass (K).

## 5. Check-by-check: what is bound, what gets caught, what escapes

| id | what the code actually binds (lines) | lie caught | lie that escapes |
|---|---|---|---|
| 1 | SCORECARD: a matching block with `12 reported, 0 dead`; first matching heading after the first `10 reported, 2 dead` (178–180) | A (old counts) | D/D2 contradictory duplicate; stale token need not be the wave line (only first occurrence); E false-negative |
| 2 | same for LOG (181–183) | A | D/D2, E |
| 3 | tokens `SCORECARD.md:6431` + `LOG.md:4040` in `s_block+l_block` (185) | none of the tested lies | H (one file carries both); contradicting sentence still passes |
| 4 | `\b7 attack\b`, `\b5 non-attack\b`, plus all 12 names present somewhere in the union (188–190) | B (wrong count tokens) | B2 (membership swapped), P (one file), negated phrasing |
| 5 | tokens `EX02BudgetControl` + `SB01-equivalent` (192) | none | M (“is NOT EX02BudgetControl”) |
| 6 | token `RV03Intent` (195) | none | any mention, no role binding |
| 7 | whole-file regex: `base … 361 … A 344 … B 11 … C 6 … mined 324 … queued 8 … rejected 29` and the tip analogue (197–203) | C (numbers swapped) | O (revision hashes unbound), C2 (a correct sentence anywhere rescues a false one) |
| 8 | census script output vs hardcoded `EXPECT_BASE`/`EXPECT_TIP` at the two historical revs (205–213) | a bad census expectation / missing bytes | **reads no correction**: every record lie above is invisible to it; depends on a non-frozen fleet script |
| 9 | verdict regex over the receipt + sorted six `FAIL` arms == hardcoded list + the six names in `both` (215–221) | a receipt with a different failed set; `round-clean` is caught (exit=0 FAIL) | J (denial), V (verdict line absent from the correction) |
| 10 | `M3`, `round-98.md`, `sampling` in the first `## Mistakes` slice (223–225) | K2 (record outside Mistakes) | K (denial), L (duplicate heading false-negative) |
| 11 | results-derived `seats==len==12`, no dead, 7/5, plus `12 seats` and `12 results` tokens (227–229) | wrong populations in the results file | N (negated tokens), B2 (identities not bound) |
| 12 | only the counter's own parse of the results file (231–232) | nothing record-side; green at base and in every variant | vacuous as a record check |

## 6. Findings (ranked by calibration impact)

**F1 — check 7 does not bind the revision hashes (claim-central).** Plan §C2 check 7 states the correction
as `base 681c80a4 → 361 …` / `tip 649bb2e9 → 363 …`; the implemented regex (lines 197–203) binds only the
words `base`/`tip` and the numbers. Variant O binds the correct numbers to the **wrong revisions** and the
counter prints `mismatches=0 met=True`. The round-98 lesson's actual defect was “base census labelled
HEAD”; the check cannot catch the same misattribution one level down. Check 8 cannot cover it: it uses the
hardcoded revisions and never reads the lesson. Disclosed limit (a) covers only *omitted labels*, not
unbound revisions.

**F2 — the frozen `--tree` mode cannot execute the forged control; the working-tree fix is post-freeze.**
See §3.1. `controls/c2-forged.out` is irreproducible from freeze bytes. If M2 commits the uncommitted
`read_bytes_at` change, C2 K1 applies on its plain wording; if not, the receipt documents a run made by
different bytes. A compliant replay exists (§3.3, rev-mode forged commit), so L1 has a path that needs no
counter edit — but the committed receipt's command must be replaced by that replay.

**F3 — the union `both = s_block + l_block` weakens checks 3–6, 9 and 11.** The docstring says “Both blocks
name the stale pointers” (line 21); the code checks the concatenation. H and P: the SCORECARD block can be
reduced to a bare count sentence and the LOG block alone satisfies the split, pointers, seat-5/6 and arm
propositions. The plan’s check 3 (“both name …”) is likewise not implemented.

**F4 — presence-only semantics accept flat contradictions.** M, N, J, V, K, B2: “NOT EX02BudgetControl”,
“NOT 12 seats … NOT 12 results”, “were NOT failed”, a removed verdict line, and “M3 — not carried …
sampling” all print `met=True`. This is broader than plan limit (c), which only concedes “tokens beside an
unrelated true-sounding narrative”; the value-bearing propositions 9 and 11 are also token-bound.

**F5 — duplicate matching blocks after the wave line are invisible (D, D2).** `correction_blocks()` unions
all matches and never compares them: a stale restatement can coexist with the correction. The only
placement test anchors the first matching heading, so a duplicate *before* the wave line is a
denial-of-service on checks 1/2 (E), the opposite failure.

**F6 — the reader is case- and wording-fragile.** `## Round 99 CORRECTION`, `## Round 99 Correction`,
`## ROUND 99 correction`, `## Correction for round 99` are not blocks (G). A correction under any of them
is silently ignored; under an uppercase heading before the wave line it is silently accepted.

**F7 — `section()` binds the first `## Mistakes` heading; check 10 is semantic-free.** L (duplicate
heading) is a false negative; K (denial sentence) passes. The check also does not verify the M3 row is the
carried round-98 record, only its three tokens.

**F8 — two of the twelve checks cannot fail on a record lie; check 8 has a non-lane dependency.** Check 12
is a pure recomputation of the counter's own parse (green at base, green in every forge). Check 8 is a
data/expectation check, useful but record-independent. The census generator is outside the lane repo and
outside K1; its current sha256 is `3fb7261569…` — the plan calls it “frozen” but no lane artifact pins it.

**F9 — the frozen docstring contradicts the frozen control.** Line 10 says `mismatches=9` at base; actual
output, plan §C2, `claims.json` C2.before and `controls/c2-base.out` say 10. The counter's own provenance
paragraph is wrong even though the predicate is unaffected.

**F10 — check 9 does not require the verdict line in the correction, contrary to its docstring.** V passes
with `PRE_REPORT round=98 …` deleted from both correction blocks; only the receipt is searched for it.

**F11 — forged-control receipt hygiene.** `controls/c2-forged.out`'s `# command:` line is a placeholder
(`--tree <scratch mirror …>`) and its `rev=tree:/fast/scratch/hyaku/kama-r99/forge` is not a replayable
path; combined with F2 it cannot be re-run from the freeze bytes.

Minor: check 11's `in` tests would accept `112 seats`/`312 results` as containing `12 seats`/`12 results`;
the plan's `scripts/sources-census.sh` does not exist lane-relative; `SCORECARD.md:6431`/`LOG.md:4040` are
the correct stale lines at the working tree (append-only corrections do not shift them).

## 7. What the instrument does bind correctly (credit where due)

- The wave-population derivation is real: 12 seats / 12 results / 0 dead / 7 attack / 5 non-attack re-derived
  from `w1-results.json` and printed in mismatch detail; the stale “10 reported, 2 dead” is caught per file
  (A) and the committed base control is reproduced byte-for-byte.
- Check 8 re-derives both census groups exactly at `681c80a4` and `649bb2e9` via the frozen generator
  (`rc=0`, exact table in §2.2).
- Check 9's receipt half is exact: verdict line, 14 arms, six `FAIL` names including `round-clean exit=0
  FAIL`.
- Check 10 catches the real routed defect (record outside `## Mistakes`, K2).
- The do-nothing control discriminates: 10 mismatches / exit 1 at base, 0 at a synthetic M2 with the
  corrections committed. No forgery that *replaces* the correction stays green: every escape in §3.2 adds
  contradictory text or exploits an unbound token; the required lies (A, C) are caught.
- Exit-code contract works: 0 met, 1 not met, 2 could-not-evaluate (missing records/census/unresolvable
  rev), 64 usage.

## 8. Files changed / artifacts

No tracked lane file was modified. Written:

- this report `.ufo/waves/round-99/w1/EX02Records.md`;
- `.ufo/waves/round-99/w1/out/EX02Records/receipts/` — frozen counter copy, base runs (frozen/current),
  census TSVs + the two SOURCES.md revisions, gate/sha manifest, counter diff, tree runs (freeze with and
  without SOURCES.md, working baseline), synthetic-M2 (unforged/forged, frozen/current), and every
  forge-*.out + forge-summary-*.json.

Scratch `/fast/scratch/hyaku/kama-r99/EX02Records/` (clone, materialized tree, 22 forged variants, work
dir) was deleted after the receipts were copied. No tools installed; no pacman; no host service touched; no git
mutation in the lane or fleet repos (the only mutations were plumbing commits inside the scratch clone of
§3.3, whose toplevel was asserted before the first commit and which was deleted with the scratch).

## 9. Risks and blockers

- **R1 (wave decision, F2):** C2's measurement-time forged control cannot be produced by the freeze-committed
  counter. L1 must either (i) commit the `read_bytes_at` fix and accept/argue K1, or (ii) keep freeze bytes
  and replace the `--tree` receipt with the rev-mode forged-commit replay demonstrated in §3.3.
- **R2 (claim strength, F1):** check 7 as implemented does not grade the revision attribution that M2's
  defect was about. The plan's own check wording names the revisions, so this is an implementation gap
  against the frozen wording, not a limit the plan discloses. It is fixable only by touching the counter
  (K1) or by disclosing it in the M2 record/report and carrying it as a stated limit — L1's call.
- **R3 (record truth, F3/F4/F5):** the corrections as written pass, but the instrument would equally pass
  contradictory duplicates and negated propositions. If the calibration claim is to be read as “the records
  agree”, the disclosed limits should be widened to cover these shapes, or the checks tightened at a later
  round.
- **R4 (external substrate, F8):** check 8 depends on `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh`
  outside the lane's K1; its sha256 is recorded here for the round's receipt trail.
- No blocker prevented any requested step; all four assignment parts were executed.
