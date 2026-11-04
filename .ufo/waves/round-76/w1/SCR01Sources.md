# rev=1a85a991fce5b76b60f88a5cab3df98d253b1a4a
# SCR01Sources — round 76, wave 1

## Behavior and axes

Axes: expansion and depth (seat); C1 operability (claim). Opened one authoritative
source live, retained its exact bytes, appended S548 as tier A / mined, and wrote
`corpus/knowledge/fenced-quotation-scope.md`. No product code or frozen rule changed.

The entry separates CommonMark's literal-content and closing-fence semantics from
the lane's citation policy. In particular CommonMark permits an unclosed fence;
frozen C1 instead refuses evaluation. Quoted non-receipts remain counted and shown,
not silently discarded; live non-receipts remain findings. Append-only historical
bytes stay preserved. None of these statements asserts that the C1 counter ran.

## Provenance and gates

Read `plans/round-76-claims.md` in full before item work, including Frontier and
duties. Read fleet `CORPUS.md` rule 1 at lines 112–115 and contract-v1 shape at
86–108; the attempted lane-root CORPUS.md read failed because that path is absent.
Read the registry and an existing knowledge entry for established conventions.

Base supplied by assignment: b06cc612711560c53eef3ec21484c6963601262f.
Observed HEAD at source opening: 1a85a991fce5b76b60f88a5cab3df98d253b1a4a,
matching the supplied freeze. Access date: 2026-11-04.

Exact successful shell command (lane cwd):

```sh
mkdir -p /fast/scratch/hyaku/kama-r76/SCR01Sources /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-76/w1/SCR01Sources && curl -fsSL --max-time 60 -o /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-76/w1/SCR01Sources/commonmark-0.31.2.html 'https://spec.commonmark.org/0.31.2/#fenced-code-blocks' && sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-76/w1/SCR01Sources/commonmark-0.31.2.html && git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD
```

Outcome: successful (exit 0). Exact output after the required revision header:
`SCR01Sources/source-open.out`. SHA256:
`c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d`.
No fallback source needed. The retained HTML is raw source material, not a
revision-prefixed receipt: prepending a header would alter fetched bytes.

Source: https://spec.commonmark.org/0.31.2/#fenced-code-blocks
Section heading: **4.5 Fenced code blocks**, retained HTML lines 2726–2728.
Located quote at lines 2760–2761:
“The content of a code fence is treated as literal text, not parsed as inlines.”
Closing-fence rule: lines 2741–2750; unclosed-fence rule: lines 2750–2757.
This URL/date/quote is also in the knowledge entry's Gate for the lesson owner's
round-local Gate; this seat does not own or edit the lesson.

## Pre-append identifier census

Executed once in the Python Eval tool, before appending, with this computation:

```python
import re
from pathlib import Path
root = Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
registry = (root/'corpus/SOURCES.md').read_text()
ids = re.findall(r'^ {0,3}\| (S[0-9]+) \|', registry, re.M)
chosen = f'S{max(int(x[1:]) for x in ids)+1:03d}'
print('existing_ids=' + ','.join(ids))
print('existing_max_id=' + max(ids, key=lambda x: int(x[1:])))
print('chosen_ids=' + chosen)
print('chosen_existing_matches=' + str(ids.count(chosen)))
```

Outcome: completed without exception; the chosen id had zero existing matches.
Both lists, pasted from that computation (also in `SCR01Sources/id-census.out`):

```text
existing_ids=S001,S002,S003,S004,S005,S006,S007,S008,S009,S010,S011,S012,S013,S014,S015,S016,S017,S018,S019,S020,S021,S022,S023,S024,S025,S026,S027,S028,S029,S030,S031,S032,S033,S034,S035,S036,S037,S038,S039,S040,S041,S042,S043,S044,S045,S046,S047,S048,S049,S050,S051,S052,S053,S054,S055,S056,S057,S058,S059,S060,S061,S062,S063,S064,S065,S066,S067,S068,S069,S070,S071,S072,S073,S074,S075,S076,S077,S078,S079,S080,S081,S082,S083,S084,S085,S086,S087,S088,S089,S090,S091,S092,S093,S094,S095,S096,S097,S098,S099,S100,S101,S102,S103,S104,S105,S106,S107,S108,S109,S110,S111,S112,S113,S114,S115,S116,S117,S118,S119,S120,S121,S122,S123,S124,S125,S126,S127,S128,S129,S130,S131,S132,S133,S134,S135,S136,S137,S138,S139,S140,S141,S142,S143,S144,S145,S146,S147,S148,S149,S150,S151,S152,S153,S154,S155,S156,S157,S158,S159,S160,S161,S162,S163,S164,S165,S166,S167,S168,S169,S170,S171,S172,S173,S174,S175,S176,S177,S178,S179,S180,S181,S182,S183,S184,S185,S186,S187,S188,S189,S190,S191,S192,S193,S194,S196,S205,S206,S209,S223,S324,S327,S328,S329,S330,S333,S334,S335,S346,S347,S363,S352,S353,S472,S474,S473,S475,S476,S477,S478,S479,S480,S481,S482,S483,S484,S485,S486,S487,S488,S489,S490,S491,S492,S493,S494,S495,S496,S497,S498,S499,S500,S501,S502,S503,S504,S505,S506,S507,S508,S509,S510,S511,S512,S513,S514,S515,S516,S517,S518,S519,S520,S521,S523,S524,S525,S526,S527,S528,S529,S530,S531,S532,S533,S534,S535,S536,S537,S538,S539,S540,S541,S542,S543,S544,S545,S546,S547
existing_max_id=S547
chosen_ids=S548
chosen_existing_matches=0
```

## Touched surfaces and artifacts

All paths below are relative to the lane repository:

- `corpus/SOURCES.md`: appended one registry row S548 after S547; no existing row edited.
- `corpus/knowledge/fenced-quotation-scope.md`: new sourced decision entry and Gate.
- `.ufo/waves/round-76/w1/SCR01Sources/commonmark-0.31.2.html`: exact live response bytes.
- `.ufo/waves/round-76/w1/SCR01Sources/source-open.out`: revision-prefixed command output.
- `.ufo/waves/round-76/w1/SCR01Sources/id-census.out`: revision-prefixed pre-append output.
- `.ufo/waves/round-76/w1/SCR01Sources.md`: this scoped report.

## Findings, limits, and out-of-scope work

- No disagreement with frozen C1. CommonMark alone does not establish evidence
  admissibility; the knowledge entry explicitly identifies that policy boundary.
- Two initial shell calls never started because their requested scratch cwd did
  not exist yet. No fetch, census, or mutation occurred in those failed launches;
  the later successful command created the directory from the lane cwd.
- The initial edit insertion was refused because its anchor row was truncated.
  Re-read the exact row, then successfully inserted without altering S547.
- No tests, counter selftests, census gate, mutation battery, or claim-scoring
  command ran. This is source-opening and documentation evidence only. Main owns
  the round census and C1 execution; their results are not inferred here.
- No installs or updates. No git/jj mutation, commit, push, judge, publication,
  service operation, or subagent dispatch. No writes to fleet, sibling lane,
  `.ufo/state`, `.scratch`, SCORECARD.md, LOG.md, README.md, or QUALITY.md.
- Scratch cleanup command: `rmdir /fast/scratch/hyaku/kama-r76/SCR01Sources`;
  successful (exit 0), no output. The directory was empty; all artifacts already
  lived under the authorized wave directory.

## Self-evaluation (not a gate)

Accuracy 4: live bytes and exact locations support the syntax; scanner execution
is intentionally unobserved. Completeness 4: scoped files and provenance are
written; the lesson Gate belongs to another seat. Clarity 4: policy versus spec
is explicit, but the raw HTML locator requires the retained file. Actionability 4:
Main can cite the entry and source receipt; no overall round verdict is supplied.
Conciseness 4: full identifier lists are long but required. Overall 4.0.
Improvement priorities: preserve these locators in the lesson Gate; keep final
claim execution evidence separate from this source-opening report. The user can
verify the scoped deliverables without treating this self-rating as acceptance.
