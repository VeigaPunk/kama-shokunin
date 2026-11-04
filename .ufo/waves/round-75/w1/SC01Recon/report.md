# SC01Recon — recon report (kama round 75, wave 1)

Read-only seat. Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`.
Frozen base `dc58e51315e79d36df5fc530c95fbd3aecbf7593`; freeze commit `0908bab5cbf0ab6b435144fc525a3e18443dc08f`.
`sha256sum plans/round-75-claims.md` = `7e3e913cf8ee87843ca108f34e3cbcdff5f75cd72b4ff5377da9a3ed451eecda`,
equal to `controls/freeze.txt` `plan_sha256` — the claims file I read is the frozen one.
No production edit. Receipts: `receipts/` (audit JSON at base and tip, re-derivation tables, commands).
Scratch `/fast/scratch/hyaku/kama-r75/SC01Recon` deleted at exit.

**The tip moved while this seat ran** (§5): `0908bab5` → `10f37171` → `b8ed2568`. §1–§4 are
measured at the frozen base (`--json` run reports `to=0908bab5…`); §5 re-measures at the tip.

---

## 1. Source check — S547 (`gitattributes`): the page did not change

| check | value |
|---|---|
| `curl -sS -L --max-time 60 -o gitattributes.live.html -w '%{http_code} %{size_download}' https://git-scm.com/docs/gitattributes` | `200 131174`, exit 0 |
| `sha256sum` live | `ceb3351f931ae86283f51416cf0042fd78265eda59e5af7d09e17581ec0f77f7` |
| `sha256sum .ufo/waves/round-75/w1/sources/gitattributes.html` | identical |
| `cmp -s` live vs retained | exit 0 (**byte-identical**) |
| response headers | `last-modified: Mon, 02 Nov 2026 06:50:50 GMT`, `etag: W/"6ae832ca-20066"` (0x20066 = 131174), access 2026-11-04 |

The retained copy was committed at the freeze commit (`git log -1 -- .ufo/waves/round-75/w1/sources/gitattributes.html`
→ `0908bab5`). **Verdict: unchanged; SCR01's fetch will reproduce the mirror byte for byte.**

**Located quote.** `Line endings are normalized to LF in the index every time the file is checked in`
— **16 words** (≤25), occurring **exactly once** in the whitespace-normalized page (110692 chars), inside the
`<dd>` of the `Set` term in the `text` attribute definition list.

- Nearest element anchor: `#Documentation/gitattributes.txt-Set-1` (`<dt class="hdlist1" id="Documentation/gitattributes.txt-Set-1">Set</dt>`).
- Containing section anchor: `#_text` — `<h4 id="_text"><code>text</code></h4>` under `#_checking_out_and_checking_in` (EFFECTS).
- The quote's `<p>` carries no id of its own; `#_text` or `#Documentation/gitattributes.txt-Set-1` is the correct anchor, **not** the enclosing `#_effects`.
- Near-miss to avoid: the first paragraph of `#_text` also contains `…line endings are normalized to LF in the index.` (lower-case `line endings`, sentence ends at `index.`). The planned fragment's capital `Line endings … checked in` matches only the `Set` paragraph. Confidence: high (digest + byte compare + unique occurrence).

Grounding check for the frontier claim: the largest accepted-history event **is** a pure line-ending
rewrite of `corpus/SOURCES.md` (§3), so the rule quoted does explain that class. It explains the cause,
not harmlessness: the audit's restore measure is raw-byte exact, so those 362 graded lines stay
`undisclosed` by design (§2, note a).

---

## 2. The audit's undisclosed set, re-derived independently — zero instrument disagreement

Commands (all read-only; `receipts/commands.txt`, `receipts/checks.txt`):

```
python3 tools/append-only-audit.py --repo . --json      # exit 1, to=0908bab5…
  summary commits=576 files=143 events=223 restored=87 partial=0 unrestored=53 ungraded=78
          disclosed=5 permitted_lines=633 disclosed_lines=10 bad_disclosures=0
          ungraded_lines=330 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=5
```

Independent reconstruction (own hunk parser over `git diff -U0`, own `numstat`, own multiset algebra;
no call into the audit module for these numbers):

| check | result |
|---|---|
| event set: every `(commit, file)` with `numstat ≥ 1` over the contract's 143 files | `223` pairs, **identical set** to the JSON's 223 events; 0 missing, 0 extra |
| deletion count per event: JSON `deleted` vs `git diff --numstat` vs independent hunk count | **53/53** undisclosed events agree on all three |
| `git log -1 --name-status <commit> -- <file>` | `M` for 53/53; every event commit has exactly **1 parent** (no merges); all are ancestors of `HEAD` |
| every `undisclosed[].line_sha256` is the sha256 of a line the commit really deleted, with `count` ≤ observed multiplicity | **389/389** entries hold |
| accounting `graded + ungraded + permitted == deleted` | 53/53 |
| full-window replication of `restored_max`, `restored_best`/`restored_by`, `held_at_to` on the 80 events whose file region is `*` and `permitted==0` | **0 mismatches** (54 restored, 5 disclosed, 21 unrestored) |
| SCORECARD carve-outs: deleted **position** of each non-graded line | all 47 sit inside `## Axes`/`## Planned`/`## Retired`/`## Saturation`/`## Capabilities`; **0 outside** |
| SOURCES permitted lines | 277 = the A-row rows whose id survives with immutable cells equal (§3) |
| ledger premise: `git log --diff-filter=A -- registry/append-only-disclosures.tsv` | introduced `b6bed925b032` (round 51, 2026-10-27); **all 42 event commits are at/after it**, so a disclosure row naming them is rejected by the tool's own "names a commit at or after the ledger's introduction" rule — C3's premise is confirmed |

**Totals: 53 events, 42 distinct commits, 787 deleted lines, 463 graded, 277 permitted, 47 carved by
region; 463 undisclosed lines carried in 389 hash entries.**

### Disagreements: none
No event, no count, no hash and no window statistic disagrees with git history. Three model
subtleties *look* like disagreements and are not — recorded so no later seat re-litigates them:

- **(a) Raw-byte restore vs CR-normalized origin.** `key()` (CR strip) feeds origins and the reported
  hash, but `held_at_to`/`restored_max` compare **raw** lines (`Mto[l] - K[l]`). A CRLF→LF rewrite
  therefore reads `unrestored` even though the text is identical. This is the entire round-65 event.
  A naive key-normalized replication shows 288 false "still held" hits on that event.
- **(b) Exempt regions carve by birth section.** SCORECARD's 47 non-graded lines are exempt-section
  lines; e.g. `2bc9308a0f64` deletes 17 and grades 1 because 16 have their deleted position inside a
  head title.
- **(c) `permitted_edits` (A-row).** 277 SOURCES lines are removed from grading because the row id
  survives with every immutable cell byte-equal.

Freeze-receipt delta: `measured/before/c3-audit.out` says `commits=575`; today `576`. The only
difference — the before-receipt predates the freeze commit itself. Every other field identical.

---

## 3. Class census (53 events)

| file | events | deleted | graded | undisclosed lines |
|---|---:|---:|---:|---:|
| `corpus/SOURCES.md` | 2 | 640 | 363 | 363 |
| `SCORECARD.md` | 31 | 108 | 61 | 61 |
| `corpus/lessons/round-74.md` | 3 | 12 | 12 | 12 |
| `corpus/lessons/round-72.md` | 5 | 8 | 8 | 8 |
| `corpus/lessons/round-62.md` | 2 | 7 | 7 | 7 |
| `LOG.md` | 4 | 6 | 6 | 6 |
| `corpus/lessons/round-57.md` | 2 | 2 | 2 | 2 |
| `corpus/lessons/round-71.md` | 2 | 2 | 2 | 2 |
| `corpus/lessons/round-64.md` | 1 | 1 | 1 | 1 |
| `corpus/lessons/round-69.md` | 1 | 1 | 1 | 1 |
| **total** | **53** | **787** | **463** | **463** |

**Era** (round taken from the commit subject): pre-round-60 = **10 events / 20 deleted / 14 undisclosed**;
round 60+ = **43 events / 767 deleted / 449 undisclosed**. Rounds present: 53, 55, 57(6), 58, 59, 60(2),
61, 62(4), 63, 64(3), 65, 67(2), 68(2), 69(2), 71(4), 72(9), 73, 74(11).

**Mechanical class**: all **389/389 entries are `in-place-edit`**; zero `removal`, zero `revert`
(every undisclosed line was deleted in a hunk that also added a replacement line). Date range
2026-10-27 → 2026-11-04.

**Top three** — by events: `SCORECARD.md` (31), `corpus/lessons/round-72.md` (5), `LOG.md` (4).
By undisclosed lines: `corpus/SOURCES.md` (363), `SCORECARD.md` (61), `corpus/lessons/round-74.md` (12).

**Line-ending noise — exactly one event.** `ea33a78f2b0b` (round 65, `round-65: S537 byte-exact re-land (LF)`),
`corpus/SOURCES.md`, `deleted=639`, `graded=362`, `permitted=277`:

```
$ git show ea33a78f2b0b^:corpus/SOURCES.md | tr -d '\r' | cmp - <(git show ea33a78f2b0b:corpus/SOURCES.md)
cmp exit=0   # 639 lines each side; 639/639 deleted lines carry a trailing CR, 75 of them are bare-CR blank lines
```

Zero content change; the file was CRLF and became LF, exactly the rule S547 quotes. Its 362 graded
lines are `undisclosed` only because the audit restores on raw bytes (§2a). Register artefact to know:
75 of them are blank lines, so one register row is `sha256("") = e3b0c442…` with `count=75` — 288
entries in this event (287 distinct lines + that one).

**Content edits — the other 52 events**: 148 deleted lines, 101 undisclosed lines.

**The one event that most needs a human reason: `16efcf5eedf4` (round 57, `LOG.md`).** The deleted
line is a historical claim, replaced in place by a different claim, with no correction reason in the
subject:

```
- Reopened S515 source this round; no SOURCES registry cell changed.
+ Opened S516 from the round-56 battery's committed call sites; append-only row added and cited by
+ C1/lesson. S515 was also reopened from its authoritative Git manual; no existing row cell changed.
```

`LOG.md` is the contract's own append-only round log ("corrections land as new entries"); this is the
class where a human has to say why the entry was rewritten rather than superseded. Runners-up:
`2bc9308a0f64` (round 74) deletes the `live-receipt-replay` capability row from the head canonical
mirror — the subject explains the mirror, not the row's removal; `590037f4c63a` (round 74) is the same
class but states its reason in the subject ("correct the EX02 record").

---

## 4. Contract cross-check — every row, `declared_at`, and whether it binds today (at the frozen base)

| # | row | `declared_at` | region | binds at `0908bab5` |
|---|---|---|---|---|
| 1 | `LOG.md` | `README.md:16` | `*` | **yes** |
| 2 | `SCORECARD.md` | `corpus/README.md:761` | `exempt=…@SCORECARD.md:6` | **no** |
| 3 | `corpus/QUALITY.md` | `corpus/README.md:761` | `*` | **no** |
| 4 | `corpus/README.md` | `corpus/README.md:761` | `*` | **no** |
| 5 | `corpus/SOURCES.md` | `SKILL.md:578` | `*` | **no** |
| 6 | `corpus/lessons/*.md` | `corpus/README.md:1239` | `*` | **no** |
| 7 | `registry/history/DELTA.md` | `registry/history/DELTA.md:3` | `*` | yes |
| 8 | `registry/report-landing-errata.tsv` | `registry/report-landing-errata.tsv:1` | `*` | yes |
| 9 | `corpus/knowledge/consumer-registry.md` | `corpus/knowledge/consumer-registry.md:30` | `only=## Errata…` | yes |
| 10 | `corpus/knowledge/error-is-not-a-verdict.md` | `corpus/knowledge/error-is-not-a-verdict.md:173` | `only=## Round24…` | yes |

`bad_declarations=5` = rows 2–6. **All five bound when their pointer was written and drifted since** —
they are stale pointers, not never-true assertions:

| pointer | line today | last revision where it bound | first revision where it broke |
|---|---|---|---|
| `corpus/README.md:761` (rows 2,3,4) | `  context-capacity rows' scope already excludes.` | `c2c05e30` (round 55, 2026-10-27) — then read `append-only (SCORECARD.md, LOG.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md)` | `750e76b9` (round 56) |
| `SKILL.md:578` (row 5) | the `Live llama.cpp lifecycle` table row (782 bytes, zero occurrences of `append`) | `c2c05e30` — then read `\| SOURCES append-only guard \| gate: …` | `dc48ee2e` (round 60) |
| `corpus/README.md:1239` (row 6) | `- Carried over unchanged and not re-measured here: the b11906 ledger population at` | `c2c05e30` — then read ``Lesson files under `corpus/lessons/` are append-only…`` | `750e76b9` (round 56) |

The sentence that used to sit at `761` is still in the file, now at **`corpus/README.md:768`** (7 insertions above it).

**Why each fails** (`binds()` in the byte-frozen tool): the pointer line must contain `append-only`/`append only`,
must not contain a negation, and must name the row's token as a whole word (the path-equals-declaring-file
shortcut applies only to non-wildcard rows). Line `761` today contains none of that; `SKILL.md:578` contains
no `append` at all; `1239` is unrelated prose.

**Second, masked defect (not visible in today's JSON).** The SCORECARD row also has a broken **region**
pointer: `SCORECARD.md:6` must contain `re-derived` and the names of all five exempt titles. It bound until
`2fc9ce1e` (round 70) and broke at **`e2b860c8907a` (round 71)**, whose rewrite of that line dropped all five
titles. `declaration()` returns on the `declared_at` failure first, so `bad_declarations` never shows it.
Demonstrated with the tool's own function on read-only data:

```
row = ("SCORECARD.md", "A-corr", "corpus/README.md:768", parse_region("exempt=…@SCORECARD.md:6"), …)
declaration(".", "HEAD", row)
  -> {'ok': False, 'reason': 'exempt pointer SCORECARD.md:6 does not name every title as re-derived'}
```

**Binding-shape facts for whoever repairs the pointers** (measured, not inferred):
`corpus/README.md:768` binds rows 2, 3, 4 and 5 (`SCORECARD`, `QUALITY`, `README`, `SOURCES` tokens present)
but **not** row 6 (wildcard → token `lessons` absent). A line containing `nothing is edited in place` still
binds; the four NEGATIONS (`not append-only`, `not append only`, `no longer append`, `never append-only`) and a
negation within three words before `append-only` do not.

---

## 5. Post-freeze drift (freshness note; not this seat's work)

While this seat ran, two commits landed: `10f37171` (02:25: pins, survivor probe, register, declaration repair)
and `b8ed2568` (02:26: `bind the SCORECARD exempt region to its own declaration line`). Re-measured at the tip:

```
python3 tools/append-only-audit.py --repo . --json    # exit 1, to=b8ed2568…
  summary commits=578 files=144 events=223 restored=87 partial=0 unrestored=53 ungraded=78
          disclosed=5 permitted_lines=633 disclosed_lines=10 bad_disclosures=0
          ungraded_lines=330 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=0
python3 tools/round75-append-accepted.py --repo .
  APPEND_ACCEPTED events=53 accepted=53 unaccepted=0 bad_rows=0 bad_declarations=0   exit=0
```

Cross-check of the landed `registry/append-only-accepted.tsv` against my independently derived set:
**389 rows, 0 malformed, 0 duplicates, 0 missing, 0 extra, 0 empty notes** — every
`(commit, file, line_sha256, count, class)` matches an audit `undisclosed` entry, including the
`count=75` blank-line row. The tip's undisclosed set is byte-identical to the base's (53 events, 389 entries),
and `unrestored=53` is unchanged, as C3's non-goal requires. The contract now has 11 rows
(`registry/append-only-accepted.tsv` added) and all 11 bind, including the SCORECARD row whose
`declared_at`→`registry/append-only-declarations.md:1` and region pointer→`…:7` close the §4 masked defect.
This is a read-only confirmation of the landed artefacts, not an endorsement of the counter's selftest.

---

## 6. Disagreements, dead ends, limits

- **No disagreement** between the audit's JSON and git history at the frozen base (event set, counts, hashes,
  window statistics all reproduced). No instrument defect found.
- Dead end: the current (v6) module refuses the historical v1/v2 contract headers, so pre-round-48 declarations
  cannot be graded with today's `parse_contract`; historical binding was checked with `binds()` on the
  pointer line plus the raw contract text.
- Limit: I did not re-implement the exempt **origin-birth** rule (`origins()`); for SCORECARD I verified that
  every carved line's deleted position lies inside an exempt title, which is the necessary condition and is
  sufficient here (47/47, 0 outside).
- Limit: `binds()` semantics were probed by calling the frozen module's own function, so those statements are
  about the shipped rule, not an independent reading of it.

## 7. Tooling / hygiene

No installs, no pacman transaction, no tool upgrade, no mutating git or `jj` call in the lane (only
`rev-parse`, `log`, `show`, `diff`, `merge-base`, `rev-list`, `ls-tree`, `cat-file`). Scratch
`/fast/scratch/hyaku/kama-r75/SC01Recon` removed after copying `receipts/` into this directory.
