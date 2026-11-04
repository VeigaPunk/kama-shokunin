# SCR02SourceRow — round 71 v1 wave (scribe, freshness axis)

Seat: source row `git-status` + S052 re-open. Lane tip at round start: f3ee44f4; freeze b43e71a8.
Frozen claims read in full first: `plans/round-71-claims.md` (C1/C2/C3 predicates, counters, kill
rules, populations). No claim rule was edited, re-scored or reinterpreted; the freeze file was not written.

## 1. Live source fetch (frontier item 1)

Commands (cwd = lane root; scratch `S=/fast/scratch/hyaku/kama-r71/scr02-source-row`):

```
mkdir -p .ufo/waves/round-71/w1/SCR02SourceRow/source
curl -sSL --tlsv1.2 --fail-with-body \
  -o .ufo/waves/round-71/w1/SCR02SourceRow/source/git-status.html \
  -w 'HTTP=%{http_code} SIZE=%{size_download} URL=%{url_effective}\n' \
  https://git-scm.com/docs/git-status
```
Output: `HTTP=200 SIZE=100062 URL=https://git-scm.com/docs/git-status` — curl exit 0, TLS verified, direct
connect (no proxy variable set in this shell).

Retained bytes and hash:
```
sha256sum .ufo/waves/round-71/w1/SCR02SourceRow/source/git-status.html
22ff28ff73f83696c4a503e9c92e7a15f4ded2f91d96cc5668ee79db0a1b0180  git-status.html
```
Hash also stored as `git-status.html.sha256`. Access date **2026-11-03** (local America/Argentina -03;
UTC read 2026-11-04T00:38Z). Quote extraction receipt: `…/SCR02SourceRow/source/quote-extract.txt`.

### Anchor, version, exact quote

- Section anchor: `<h3 id="_porcelain_format_version_1">` → `https://git-scm.com/docs/git-status#_porcelain_format_version_1`,
  a subsection of `§OUTPUT`. Page is the "Latest version" build.
- Git version named on the page: the version panel reads `git-status last updated in 2.53.0` and lists
  `2.54.0 → 2.56.0 no changes`; the latest release covered by the served page is therefore **Git 2.56.0**
  (page-level statement; no separate release string is printed in the body or footer).
- Exact page wording of the sentence (verbatim, extracted from the retained HTML):
  "Version 1 porcelain format is similar to the short format, but is guaranteed not to change in a
  backwards-incompatible way between Git versions or based on user configuration. This makes it ideal
  for parsing by scripts."
- Located quote used in the row (17 words, ≤25, no `|`):
  `is guaranteed not to change in a backwards-incompatible way between Git versions or based on user configuration`
  (+ the following clause "This makes it ideal for parsing by scripts" is named in the anchor cell).

## 2. Id derivation from registry content (not a counter)

```
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md | grep -oE 'S[0-9]+' | sort -u   # 281 ids
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' /home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md \
  | grep -oE 'S[0-9]+' | sort -u                                                              # 142 ids
```
Lists (full, comma-joined; also retained verbatim at `.ufo/waves/round-71/w1/SCR02SourceRow/receipts/ids_*.txt`):

LANE (281, `receipts/ids_lane.txt`):
```
S001,S002,S003,S004,S005,S006,S007,S008,S009,S010,S011,S012,S013,S014,S015,S016,S017,S018,S019,S020,S021,S022,S023,S024,S025,S026,S027,S028,S029,S030,S031,S032,S033,S034,
S035,S036,S037,S038,S039,S040,S041,S042,S043,S044,S045,S046,S047,S048,S049,S050,S051,S052,S053,S054,S055,S056,S057,S058,S059,S060,S061,S062,S063,S064,S065,S066,S067,S068,
S069,S070,S071,S072,S073,S074,S075,S076,S077,S078,S079,S080,S081,S082,S083,S084,S085,S086,S087,S088,S089,S090,S091,S092,S093,S094,S095,S096,S097,S098,S099,S100,S101,S102,
S103,S104,S105,S106,S107,S108,S109,S110,S111,S112,S113,S114,S115,S116,S117,S118,S119,S120,S121,S122,S123,S124,S125,S126,S127,S128,S129,S130,S131,S132,S133,S134,S135,S136,
S137,S138,S139,S140,S141,S142,S143,S144,S145,S146,S147,S148,S149,S150,S151,S152,S153,S154,S155,S156,S157,S158,S159,S160,S161,S162,S163,S164,S165,S166,S167,S168,S169,S170,
S171,S172,S173,S174,S175,S176,S177,S178,S179,S180,S181,S182,S183,S184,S185,S186,S187,S188,S189,S190,S191,S192,S193,S194,S196,S205,S206,S209,S223,S324,S327,S328,S329,S330,
S333,S334,S335,S346,S347,S352,S353,S363,S472,S473,S474,S475,S476,S477,S478,S479,S480,S481,S482,S483,S484,S485,S486,S487,S488,S489,S490,S491,S492,S493,S494,S495,S496,S497,
S498,S499,S500,S501,S502,S503,S504,S505,S506,S507,S508,S509,S510,S511,S512,S513,S514,S515,S516,S517,S518,S519,S520,S521,S523,S524,S525,S526,S527,S528,S529,S530,S531,S532,
S533,S534,S535,S536,S537,S538,S539,S540,S541
```
MERGE (142, `receipts/ids_merge.txt`):
```
S330,S331,S332,S333,S334,S335,S336,S337,S338,S339,S340,S341,S342,S343,S344,S345,S346,S347,S348,S349,S350,S351,S352,S353,S354,S355,S356,S357,S358,S359,S360,S361,S362,S363,
S364,S365,S366,S367,S368,S369,S370,S371,S372,S373,S374,S375,S376,S377,S378,S379,S380,S381,S382,S383,S384,S385,S386,S387,S388,S389,S390,S391,S392,S393,S394,S395,S396,S397,
S398,S399,S400,S401,S402,S403,S404,S405,S406,S407,S408,S409,S410,S411,S412,S413,S414,S415,S416,S417,S418,S419,S420,S421,S422,S423,S424,S425,S426,S427,S428,S429,S430,S431,
S432,S433,S434,S435,S436,S437,S438,S439,S440,S441,S442,S443,S444,S445,S446,S447,S448,S449,S450,S451,S452,S453,S454,S455,S456,S457,S458,S459,S460,S461,S462,S463,S464,S465,
S466,S467,S468,S469,S470,S471
```

Counts and collision set:
- lane-only 272; merge-only 133; union 414.
- **collision set (id present in both files) = 9: S330, S333, S334, S335, S346, S347, S352, S353, S363.**
- union maximum = **S541**, so the next unused id (checked absent from both lists: `grep -c S542 ids_union.txt` → 0,
  exit 1) is **S542**. No counter file was read; the id comes from the set union, not from row count.

## 3. New row S542 (appended as the last registry row)

Inserted after S541 (registry table line 293), i.e. appended at the end of the `## Registry` table; no
mid-table insertion (the table is followed by blank lines then `## Paths`). Diff proof:
`git diff --numstat -- corpus/SOURCES.md` → `2  1  corpus/SOURCES.md` (one added row + one replaced S052 line).

Row (final bytes, line 294; 11 fields, 12 delimiters, 0 literal or escaped `|` in any cell):

```
| S542 | Git git-status — https://git-scm.com/docs/git-status | docs | A | the pre-report cleanliness arm's porcelain parsing: `git status --porcelain` version 1 records as a script-stable machine surface, so the arm may parse status bytes and a shape break is an upstream guarantee break, not a parser bug | §OUTPUT, subsection "Porcelain Format Version 1" (`#_porcelain_format_version_1`), sentence "is guaranteed not to change in a backwards-incompatible way between Git versions or based on user configuration", followed by "This makes it ideal for parsing by scripts"; page is the Latest-version build, "git-status last updated in 2.53.0", changes list "2.54.0 → 2.56.0 no changes" (Git 2.56.0); fetched bytes sha256 22ff28ff73f83696c4a503e9c92e7a15f4ded2f91d96cc5668ee79db0a1b0180 retained at `.ufo/waves/round-71/w1/SCR02SourceRow/source/git-status.html` (accessed 2026-11-03) | version 1 keeps one record shape across Git versions and user configuration, so the cleanliness arm's uncommitted-path parser is keyed to a guaranteed contract rather than a vendor habit | mined | 2026-11-03 | on-release | corpus/knowledge/pre-report-gate.md, corpus/lessons/round-71.md |
```

Fields: kind `docs`, tier `A`, scope = pre-report cleanliness arm's porcelain parsing, status `mined`,
opened `2026-11-03`, recheck `on-release` (cadence: re-read when Git changes the porcelain/status docs),
used-by `corpus/knowledge/pre-report-gate.md, corpus/lessons/round-71.md`.

### Scratch-mirror gate before the lane write

```
cp -a corpus "$S/mirror/corpus"                     # exact copy of corpus/
rsync -a --exclude .git --exclude .jj --exclude .ufo --exclude tests <lane>/ "$S/mirror-full"/
# used-by targets that do not exist yet, created only inside the mirror as zero-byte placeholders:
: > $S/mirror-full/corpus/knowledge/pre-report-gate.md
: > $S/mirror-full/corpus/lessons/round-71.md
./scripts/sources-census.sh validate --file $S/mirror-full/corpus/SOURCES.md
```
- `$S/mirror` (corpus only): exit 1, E11 on S525/S538/S539/S540/S541 — used-by paths such as
  `SCORECARD.md`/`registry/…` resolve against the mirror root, so a corpus-only mirror cannot pass.
- `$S/mirror-full` (lane tree minus `.git`/`.jj`/`.ufo` plus the two `.ufo`/`tests` used-by targets the
  registry names): **exit 0**, last line `file\tok\t…/mirror-full/corpus/SOURCES.md`, 282 rows, no `E`
  code, 105 warnings (identical count to the lane's before-state; the new row adds none).
- Re-validated with the final lane bytes after the anchor-cell tightening: `census-mirror-final.out`,
  **exit 0**, `file\tok`.
- Placeholder caveat: E11 for `corpus/knowledge/pre-report-gate.md` and `corpus/lessons/round-71.md` was
  satisfied with zero-byte mirror-only placeholders; those two files are sibling deliverables of this
  wave and did not exist in the lane at write time. Only then was the row applied to the lane file.

## 4. S052 in-place re-open (step 4)

Live fetch, same method:
```
curl -sSL --tlsv1.2 --fail-with-body -o .ufo/waves/round-71/w1/SCR02SourceRow/source/pytest-exit-codes.html \
  -w 'HTTP=%{http_code} SIZE=%{size_download}\n' https://docs.pytest.org/en/stable/reference/exit-codes.html
HTTP=200 SIZE=25787   # sha256 a403306a1d763fc8123749544905dd64e8e0cfa5ed46a416679001c3142e3977, access 2026-11-03
```
Claims still hold live: "Exit code 1: Tests were collected and run but some of the tests failed"; "Exit
code 5: No tests were collected". The page still names no pytest version (footer only copyright), so the
row's scope note "the `stable` alias, whose pytest version the page does not state" is unchanged.
Only the used-by cell was changed (KQ22 in-place change), all other cells byte-identical:

```
old: corpus/knowledge/llamacpp-loading-lifecycle.md, corpus/lessons/round-18.md, corpus/lessons/round-70.md
new: corpus/knowledge/llamacpp-loading-lifecycle.md, corpus/lessons/round-18.md, corpus/lessons/round-70.md, corpus/lessons/round-71.md
```
`git diff` shows exactly one removed/one added line for S052, no other change in that row.

## 5. Census before / after

Command both times:
```
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
```

BEFORE (receipt `receipts/census-before.out`): **exit 0**. 104 `W04` duplicate-url warnings + 1 `W01`
(S481 tier-C), final line `kama\tok\t/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`;
no `E` codes; registry rows 281 (matches the frozen population table).

AFTER (receipt `receipts/census-after.out`): **exit 1**, three `E11` findings, all of them the two
sibling deliverables that do not exist yet:
```
kama	E11	S052 missing used-by corpus/lessons/round-71.md
kama	E11	S542 missing used-by corpus/knowledge/pre-report-gate.md
kama	E11	S542 missing used-by corpus/lessons/round-71.md
```
Registry rows 282 (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`), matching the
frozen expectation "281 → 282". No other `E` code appears; the warning set is unchanged.
The same registry bytes pass validate with exit 0 when the two used-by targets exist (mirror evidence
above), so the E11 is target-existence, not row shape. Freeze reconciliation: the frozen
claims make both files round-71 deliverables (`pre-report-gate` knowledge entry, `lessons/round-71.md`);
their absence is a wave-ordering state, and I did not create them (not my seat, and stubbing them in the
lane would be fabricated corpus content).
Re-run before this seat closed, 2026-11-03T21:40-03 and again 2026-11-03T21:41-03 (receipt
`receipts/census-after-rerun.out`, last run overwrote it): **exit 1** both times, the same three E11
lines, both target files still absent. So the after-state recorded here is
`exit 1 / rows 282 / 3×E11`, and the green after-state depends on the sibling deliverables landing.

Diff against the freeze commit (proves the append-only claim and no collateral edit):
```
git diff --numstat b43e71a8 -- corpus/SOURCES.md        ->  2  1  corpus/SOURCES.md
git show b43e71a8:corpus/SOURCES.md | grep -c '^\| *S[0-9]{3,} *\|'   -> 281 (now 282)
S541 line sha256 at freeze = 454adfa82b9b9fc99477665aaa7aea540a6296d560a9734ebb8f351230e98da1
S541 line sha256 now       = 454adfa82b9b9fc99477665aaa7aea540a6296d560a9734ebb8f351230e98da1
```

## 6. Touched surfaces / provenance

| Path | Change |
|---|---|
| `corpus/SOURCES.md` | line 294 S542 row appended as last registry row; line 64 S052 used-by cell only |
| `.ufo/waves/round-71/w1/SCR02SourceRow/source/git-status.html` | retained fetched bytes (sha256 22ff28f…), hash beside it as `git-status.html.sha256` |
| `.ufo/waves/round-71/w1/SCR02SourceRow/source/pytest-exit-codes.html` | retained re-open bytes (sha256 a403306…) |
| `.ufo/waves/round-71/w1/SCR02SourceRow/source/quote-extract.txt` | sentence + quote + word count |
| `.ufo/waves/round-71/w1/SCR02SourceRow/receipts/` | census before/after/mirror outputs, ids_* lists |
| `.ufo/waves/round-71/w1/SCR02SourceRow.md` | this report |

Scratch `S` created, all fixtures under it; deleted at exit (receipts copied into the wave dir first).
No commit, push, or mutating git/jj command: only `git diff`, `git status`, `grep`, `ls`, `sha256sum`.
No write to `~/.config`, `~/.omp`, systemd, `.ufo/state`, `MANIFEST.json`, `SCORECARD.md`, `SKILL.md`.
No tool install or upgrade was needed (curl, coreutils, gawk, python3 present; no package command run).

## 7. Limits / what I could not verify

- The lane census at this instant exits 1 on E11 for `corpus/knowledge/pre-report-gate.md` and
  `corpus/lessons/round-71.md` because neither file exists yet; I cannot verify the final green state
  and did not manufacture the files. A re-run after the sibling scribe lands them is the check; the last
  re-run of this seat (receipt `receipts/census-after-rerun.out`) still showed the same three E11 lines.
- The `Git 2.56.0` attribution is page-level: the page prints "last updated in 2.53.0" and a change panel
  "2.54.0 → 2.56.0 no changes"; it does not print a `git version` line in the body.
- Round-mirror E11 for the two used-by paths was demonstrated only with mirror placeholders, not with
  real sibling content.
- I did not re-derive the source's byte content against a second mirror/CDN origin; one live fetch, one hash.
