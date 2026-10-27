# QUALITY rows — round 53, seat W2Quality

**Verdict:** the lane's working tree already carries the round-53 QUALITY section (`KQ94`-`KQ96`,
uncommitted, `corpus/QUALITY.md` sha256 `ed46d4b461da1346c5169b90009107e5f60a95b7ebe5544c7f85c9c57c77eb94`,
476 lines), so this seat reviews it against the build instead of landing a duplicate set: the three
criteria are correctly captured, but **two rows state more than the mechanism does or cite a lesson
section that does not exist**. The minimal cell edits are in `quality.proposed.diff`; the seat's own
independently drafted rows (which avoid both defects) are kept in `quality-draft-rows.md`.

Seat assignment: (a) C1 code-in-memory rule, (b) C2 cited-path disclosure rule, (c) R1 SOURCES
anchor rule. All three are present in the working tree at `corpus/QUALITY.md:468-476`.

---

## 1. What was checked, and how

| Item | Command / source | Result |
|---|---|---|
| the in-tree section | `sed -n '467,476p' corpus/QUALITY.md`; `git diff corpus/QUALITY.md` (10 added lines, `@@ -464,3 +464,13 @@`) | 3 rows, 4 cells each, section heading `## Criteria added — round 53 (each cites corpus/lessons/round-53.md)` |
| C1 counter, my own run | `python3 tools/round53-replay-code-audit.py --repo $S/lane --tip c22602bd… --scratch $S/c1` | exit 0, `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True`; `c1-build.out` |
| C2 counter, my own run | `python3 tools/round53-cited-path-check.py --repo $S/lane --tip c22602bd… --scratch $S/c2` | exit 0, `fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True`; `c2-build.out` |
| base controls | `.ufo/waves/round-53/controls/base.{c1,c2}.out` | `code=0 coderuns=0/3`; `lane=0 unresolved=16 undisclosed=16` — both `met=False` |
| S505 / S509 anchor | `sources-anchor-check.py --row S506 --row S507 --row S508 --row S509 --copy S509=…` | exit 0 `anchors=4 ok=4 na=3 covered_copy=1 copy_mismatch=0`; S509 located at 401 / 480 / 488-489 / **491**, fetched sha256 `1436b46b…7fe` = committed copy (`anchor-round53.out`) |
| S505 as control | same tool, `--row S505` | exit 1, `fail`, `want=422-439 got=[480, 578, 579]` (`anchor-controls.out`) |
| lesson sections | `grep -n '^## ' corpus/lessons/round-53.md` | `9:## Claims`, `14:## Gate` — **no** `Mistakes` section |
| memfd enumeration | `git show c22602bd:tools/kama-llamacpp-live.py \| sed -n '793p'`; `…round53-replay-code-audit.py \| sed -n '413p'` | both: a mapping whose pathname starts `/memfd:` is skipped (`continue`) |
| the only memfd examined | `round53-replay-code-audit.py:464-486` (`sealed_exe`), `kama-live-replay.py:505-517` | `/proc/<pid>/exe` link `/memfd:…`, seals, dev+inode — the server image only |
| J8AllNever's ablation (cited by KQ95) | `.ufo/waves/round-53/w1/out/J8AllNever/c2-abl-never.out` | `bad=2 stale=1 undisclosed=2 disclosed=12 met=False` — the row's `bad=2` is accurate |

## 2. Clause-by-clause review of the in-tree rows

**KQ94 (`corpus/QUALITY.md:474`, "extends KQ91") — confirmed except its memfd quantifier.**
Confirmed: `code_mappings` records path/dev/inode/uid and a digest only while the path is the mapped
inode (`tools/kama-llamacpp-live.py:774-838`); the counter reads each executable range from
`/proc/<pid>/mem` and compares it with its own download (`tools/round53-replay-code-audit.py:405`,
`:424-433`); host files must be root-owned, same inode, unwritable (`:447`); the replay's `own_code`
hashes members from the archive stream (`tools/kama-live-replay.py:290-303`, `:305-338`); S508 is
the rejected means, as the reject cell says. **Not confirmed:** "every executable file mapping" and
"admits no executable memfd but its own sealed server". Both enumerations skip every `/memfd:`
mapping (`kama-llamacpp-live.py:793`, `round53-replay-code-audit.py:413`), and the only memfd read is
the running image through `/proc/<pid>/exe` (`:464-486`). The build's own receipt shows the filter at
work: `code_mappings` has no `/memfd:` entry while `server_exe` is `/memfd:llama-server (deleted)`.
The reject cell's own `a path-less or second-memfd mapping admitted (wave seats V1Review,
V3Review)` is the accurate half — seat V3Review reported the skip at
`.ufo/waves/round-53/w1/out/V3Review.md:10`; the admit cell contradicts it.

**KQ95 (`:475`) — confirmed; one dead lesson section.**
Classes, surfaces and limbs match the frozen counter (`tools/round53-cited-path-check.py:28-37`,
`:41-58`, `:59-73`, `:107`); the `dropped` limb exists (`:69-72`); `bad=2` for a blanket `never`
ledger is J8AllNever's measured ablation; the prototype figure matches the lesson ("counted 51
`.ufo/` misses … called 50 pre-existing", `corpus/lessons/round-53.md:12`). **Not correct:**
`corpus/lessons/round-53.md` has no `Mistakes` section (`## Claims` at :9, `## Gate` at :14), so the
row's fourth cell cites a section that does not exist — the defect class round-52 closure D7
recorded. The motivating mistake it means is `corpus/lessons/round-52.md` Mistakes #4.

**KQ96 (`:476`) — the locate rule is right; its copy clause is weaker than R1 and its citation is dead.**
Confirmed: an anchor must be located at the declared lines; S505 is the negative case (`lines
422–439` for a symbol first occurring at 480, quote at 491, "21 words" for 7). **Two corrections:**
(i) "(the copy committed beside the round)" makes the committed copy the reference, so a copy that
is *not* the fetch passes — R1 says "located … in the fetched copy"; the fetch must be the
reference and the copy admitted only on sha256 equality, which holds for S509
(`1436b46b…7fe`, mine and the build's). (ii) the fourth cell cites `corpus/lessons/round-53.md`
`Mistakes` (no such section); the round's own evidence is `corpus/lessons/round-53.md` Gate S509.

## 3. Proposed fix

Route A (preferred — the rows are uncommitted): apply `quality.proposed.diff` to
`corpus/QUALITY.md` before the section lands. It touches three lines, changes six spans, and leaves
every other byte and every row's 4-cell shape intact (verified: `cells=4` on lines 474-476 after the
patch). Its three substantive edits are:

1. `:474` admit — "every executable file mapping of its running server **whose maps pathname is
   absolute and not `/memfd:`** (`tools/kama-llamacpp-live.py:793`, `tools/round53-replay-code-audit.py:413`)";
   and ", and admits no executable memfd but its own sealed server" → "while the only memfd it
   examines is the running image through `/proc/<pid>/exe` (`…:464-486`) — an executable memfd
   mapping besides it is not enumerated"; and the reject cell's "a path-less or second-memfd mapping
   admitted (wave seats V1Review, V3Review)" → "a second-memfd mapping **counted as covered** when
   the enumeration skips it (seat V3Review's finding at `…:413`; the gap the admit cell now states)".
2. `:475` fourth cell — "`corpus/lessons/round-53.md` Claims C2 and Mistakes" → "`corpus/lessons/round-53.md`
   Claims C2; `corpus/lessons/round-52.md` Mistakes #4".
3. `:476` admit — "(the copy committed beside the round)" → "(the fetch is the reference: the
   round's committed text copy is admitted only once its sha256 equals the fetch's — held for S509's
   copy, `1436b46b…7fe`, `.ufo/waves/round-53/w1/out/W2Quality/anchor-round53.out`)"; and the fourth
   cell → "`corpus/lessons/round-53.md` Gate (S509 supersedes S505);
   `corpus/lessons/round-52-verifier-spotcheck.md` R1".

Route B (if the section has already landed): `corpus/QUALITY.md` is A-corr, so append instead —
three narrowing rows, next free ids after whatever the L1 has landed:

| ID | Admit only when | Reject or limit when | Motivating lesson |
|---|---|---|---|
| KQ97 (narrows KQ94) | A replay's code claim covers exactly the executable mappings whose maps pathname is absolute and not `/memfd:` — both enumerations skip `/memfd:` (`tools/kama-llamacpp-live.py:793`, `tools/round53-replay-code-audit.py:413`) and the only memfd read is the running image through `/proc/<pid>/exe` (`:464-486`) | a memfd mapping counted as covered, or a row inferring "no executable memfd but the image" from an enumeration that filters them (the build's `code_mappings` carries no `/memfd:` entry while `server_exe` is one) | `corpus/lessons/round-53.md` Claims C1; seat V3Review (`.ufo/waves/round-53/w1/out/V3Review.md:10`) |
| KQ98 (supersedes KQ95's fourth cell) | KQ95's admission and reject cells stand as written at `corpus/QUALITY.md:475` | a fourth cell citing a lesson section that does not exist: the right citation is `corpus/lessons/round-52.md` Mistakes #4, the round-53 lesson carrying only `## Claims` (:9) and `## Gate` (:14) | `corpus/lessons/round-52.md` Mistakes #4; `corpus/lessons/round-53.md` Claims C2 |
| KQ99 (supersedes KQ96) | A SOURCES anchor that names line numbers is admitted only after the quote is located at those lines in the copy fetched for that row, the round's committed text copy being admitted only once its sha256 equals the fetch's (held for S509: `1436b46b…7fe`), and the quote's word count re-counted from that copy | a committed copy accepted as the fetch (a stale copy locates any line); an anchor carried from a seat's summary (S505 `lines 422–439`, lesson `line 431`; quote at 491; "21 words" for 7) | `corpus/lessons/round-52-verifier-spotcheck.md` R1; `corpus/lessons/round-53.md` Gate S509 |

## 4. The seat's own frames, if the L1 prefers them

`quality-draft-rows.md` holds this seat's independently drafted `KQ94`-`KQ96` with the same three
criteria. They state the memfd filter honestly, require fetch/copy equality and cite only lesson
sections that exist; their limits cells also add two the in-tree rows leave implicit — a mapping's
bytes past the member's end are compared as zero fill (`tools/round53-replay-code-audit.py:424-425`)
and memory is read once while the server is held, so a library rewritten afterwards is unseen
(`:405`). They are **not** to be landed beside the in-tree rows: two row sets for one criterion
would double-count the claim.

## 5. Integration notes

- Whichever route: one row per criterion, no duplication; the section heading and 4-column shape
  stay as the in-tree text has them.
- The two dead `Mistakes` citations are the same defect class as round-52 closure D7; if the lesson
  gains a `## Mistakes` section later, the citation becomes true but the row still needs the
  correction row (a citation is graded at its writing instant).
- `sources-anchor-check.py` (in this directory) is the demonstration of KQ96/KQ99's locate rule; it
  reads three anchor forms and reports the rest `n/a`, so it does not sweep the 97 line-anchored
  SOURCES rows at the build — a round-54 instrument item, not this seat's.
