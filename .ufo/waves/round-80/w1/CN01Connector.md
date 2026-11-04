# CN01 — sibling-overlap scan for the three round-80 surfaces

Seat `CN01Connector`, kama round 80 wave 1. Read-only across the lane and 21 sibling lane dirs
under `/home/vgpnk/Projects/shokunin`. No sibling file, no lane file outside this seat dir and no
scratch tree was written; no git write, no counter run, no pre-report gate.
Receipts: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/CN01Connector/scan.out`.

Lane tip while scanning: `fe7b978013bd1aa6d67a7e0fbf6369b8d7a9b023` (`git -C
/home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master`). Base `c45fc7d1`, sealed
`a9b4543f` are read from `git show`, never re-derived here — C1 grading is `EX01C1Rederive`'s and
`R79RevC1`'s seat, not this one.

**Landed mid-scan** (reviewed as found, not graded): `registry/engine-pin-relations.tsv`,
`registry/unregistered-class-engines.tsv`, `corpus/lessons/round-80.md`,
`tools/round80-engine-pin-relations.py`, `tools/round80-ollama-census.py`, plus
`.ufo/waves/round-80/measured/after/`. They were absent at my start; two findings below are
against the landed bytes and are labelled so.

Sibling set screened: audio, chousa, game-dev-2d, game-dev-3d, kagi, kaidoku, kake, kasegi,
kengaku, kotoba, kotodama, kumitate (`kumitate-shokunin`; `kumitate-shokinin` is a nested misroot
holding only a duplicate dir and no matching file), lore, mado, mori, revenger, souji, tabi,
tameshi, tsukuroi. `tsunagu` does not exist. Fleet `tools/` is empty; fleet `scripts/` carries no
pin watcher.

---

## Surface 1 — the llama.cpp pin relation (`b11755` / `39febd2a` / `b7200`)

**Verdict: complementary. One cross-lane object (`b7200`), no sibling relation row, no duplicate
register.** The only other lane that holds any of the three refs is kengaku, and it holds one of
them, as a source row.

| file:line | ref | class | owning lane |
|---|---|---|---|
| `kama-shokunin/registry/engine-pins.tsv:4` | `b11755` (tag) | own register row the C2 counter consumes; unique fleet-wide | kama |
| `kama-shokunin/corpus/SOURCES.md:308` (S553) | `39febd2a…` (commit) | own source row; the "reference cited from another row" the predicate names | kama |
| `kengaku-shokunin/corpus/SOURCES.md:193` (S178) | `b7200` (tag) | **complementary** — a source row with a tag pin and a *date-based* `recheck 90d`, not a newest/newer relation | kengaku |
| `kengaku-shokunin/corpus/knowledge/served-endpoint-identity-pin.md:1,10` | `b7200` | kengaku knowledge that rests on S178 | kengaku |
| `kengaku-shokunin/LOG.md:1591`, `corpus/lessons/round-51.md:18`, `corpus/lessons/round-51-verifier-spotcheck.md:111,113` | `b7200` | kengaku's own record of the same admit; same ground as S178, not a second source | kengaku |
| `kaidoku-shokunin/corpus/evidence/round-41/c1/V4/oracle.tsv:686,815` and three `tools/round-50/oracle/*.tsv` | — | **false positives**: substring `…e613b720071a6f` in a sha256 column, not a pin | — |

Searches: `grep -rlnE 'b11755|39febd2a|b7200' */` over every `.md/.tsv/.py/.sh` outside `.ufo/`,
excluding kama → 9 files, all kengaku or the kaidoku hash collision; exit 0.

**Sharpest non-overlap (landed bytes, `registry/engine-pin-relations.tsv:4`).** The register's
`b7200` row reads `behind newer=3395 newest=b12103`. That is the fleet's only relation statement
about a kengaku row. Kengaku's own S178 carries a *date* recheck (`90d`, opened 2026-10-28) and no
tag relation, so kama's `behind` is a signal the owning lane does not carry. C2's scope ruling
("records relations, not knowledge") is what keeps that admissible: it is a recheck trigger, not a
verdict on S178. A seat that restates it as "kengaku's source is stale" would be over-claiming
kengaku's ground, because S178's bytes still describe b7200.

Second-order note: `b7200` and `b11755` are both matched by the register's own `b(\d+)` rule, so
`b7200 < b11755` is decided by the same numeric key that decides `behind` — the row and the kama
install pin are consistent, not contradictory.

---

## Surface 2 — the Ollama `/api/tags` census class and Ollama engine fixtures

**Verdict: clear on the sibling axis; the owner is kama, corroborated by a sibling refusal. The
adjacent duplicate ground is inside the lane (rounds 60/61), not in a sibling.**

| file:line | what it holds | class | owning lane |
|---|---|---|---|
| `kama-shokunin/corpus/SOURCES.md:21-25` (S009–S013), `:43` (S031), `:272-277` (S519–S525) | Ollama docs surface rows, incl. `/api/tags` (S011, S031) and the v0.40.11 rows | own | kama |
| `kama-shokunin/registry/ollama-live-pin.tsv:1-10` | pinned Ollama **v0.40.11** child (archive/bin/model sha256, scratch HOME) | own | kama |
| `kama-shokunin/registry/ollama-live-claims-r61.tsv:1-12` | r61 live OLLAMA claims (version, tags/ps join, v1 surfaces) | own, prior round | kama |
| `kama-shokunin/tools/kama-probe.sh:768,787` | the `registered` column and JSON key; added by `5ac1a8dd` (round 79) — the only implementation fleet-wide | own | kama |
| `kama-shokunin/tools/round79-unregistered-census.py` | round-79 census counter for the class | own, prior round | kama |
| `kake-shokunin/PROVINCE.md:47` | "`kama` owns local model-serving endpoints; kake owns remote web properties" | **complementary** — sibling boundary naming kama as owner | kake |
| `kake-shokunin/corpus/lessons/round-48.md:81-85`, `round-49.md:17`, `round-50.md:20`, `round-57.md:54-56`, `round-48-verifier-spotcheck.md:75` | four consecutive refusals of the staged Ollama OpenAPI entry as out of province | **complementary** — ownership corroboration, no graded fixture | kake |

Searches: `grep -rlnE 'registered=(no|yes)|class_missing' */` outside kama → 0 files, exit 1: no
sibling holds the class. `grep -rIl -i 'ollama' */` outside kama → 15 files, of which 11 are kake
lessons/verifier rows (the refusals above), 3 souji census copies of a round-29 connector report,
1 kengaku eval-design note; none is a fixture or a census.

**In-lane duplicate-observation boundary (matters for C3's wording).**
`.ufo/waves/round-60/w1/out/P04ProbeVersusOllama/evidence/probe-qualified.json` already ran
`kama-probe.sh listeners` against the Ollama child, but its listener row keys are
`bind/evidence/owner/port/reason/served_model/verdict` — **no `registered` key** (measured: `python3 -c
"…'registered' in json.dumps(d)"` → `False`). And `SCORECARD.md:59` already names the step
("Operability: exercise the `registered` class against a second engine fixture (Ollama's
`/api/tags`)…"). So the Ollama *fixture* and the `listeners` *observation* are prior ground
(r60/r61, SCORECARD:59); only *the class read on that engine* is new. The plan's "Before" says so;
a seat that restates it as a first Ollama fixture would over-claim rounds 60/61.

---

## Surface 3 — engine-pin watch and relation registers

**Verdict: no sibling register exists; the lane's own register is unique. One cross-lane
provenance defect sits in the lane's own prose, and one predicate-vs-register contradiction sits
in the landed C2 bytes.**

| file:line | what it holds | class | owning lane |
|---|---|---|---|
| `kama-shokunin/registry/engine-pins.tsv:2-4` | sglang v0.5.22, vllm v0.32.0, llama.cpp b11755 | own population (3) | kama |
| `kama-shokunin/tools/pin-watch.py:1-40` | `newest`/`newer`/`status` computation, peeled-line and numeric-order rules | own | kama |
| `kama-shokunin/corpus/knowledge/engine-pin-watch.md:1-3,44-49,60-70` | the method entry, the 2026-10-25 status table, and the scope clause | own | kama |
| `kama-shokunin/registry/release-recheck-b11889.tsv`, `-b11906.tsv`, `recheck-r45.tsv` | release/recheck ledgers of a different kind (row rechecks, not relation rows) | own, prior | kama |
| `tameshi-shokunin/tools/pin-disposition.py:1-40`, `tools/executor-source-pin.py:1-18` | **content-blob** pins (mutation-ledger legs, declared executor source blobs) | different subject — do not call it "reuse of tameshi's pin gate" | tameshi |
| `chousa-shokunin/PROVINCE.md` (880 bytes, 3 commits) | question framing, source hierarchy, citation chaining, claim-vs-source verification — **no tag/release clause** | no register; `git -C chousa-shokunin log -S 'tag' -- PROVINCE.md` prints no commit | chousa |

Searches: `grep -rln 'engine-pins\|pin-watch' */` outside kama → 0 files, exit 1. Fleet `tools/`
empty; `scripts/` holds `fixtures/`, `hyaku/`, `shokunin-watchdog.sh`, `sources-census.sh` only.

### 3a. The sibling-boundary citation is kama's own assertion (contested by omission)

`corpus/knowledge/engine-pin-watch.md:70-71` says "the generic method of pinning and tracking any
repository tag is chousa's ground (`PROVINCE.md`, round-38 note)". The parenthetical most plausibly
names **kama's** round-38 note (`PROVINCE.md:164-170`), which asserts that division — chousa's
`PROVINCE.md` does not carry it, and kama's own `PROVINCE.md:180` already records the absence:
"no chousa document names it, checked 2026-10-25". So the division is one-sided: the citation is
ambiguous about whose `PROVINCE.md` it names, and either reading leaves the chousa side
undocumented. Owner of the fix is kama (a supersession in the entry), never chousa.

### 3b. Predicate vs register: the `39febd2a` commit row

Frozen C2 predicate: "a commit row's 40-hex anchor is not any upstream tag's peeled oid." The
landed `registry/engine-pin-relations.tsv:3` row is
`llama.cpp 39febd2a… commit source-row S553 tag:b11963 110 b12103 …`.

- `b11963` is a **lightweight** tag: the committed tag list
  (`.ufo/waves/round-80/measured/after/c2-tags/llama.cpp.txt`) has one `refs/tags/b11963` line and
  no `refs/tags/b11963^{}` line, while the same file carries 25 `^{}` lines for annotated tags. A
  lightweight tag emits no peeled oid, so the predicate's literal sentence is satisfied.
- The counter (`tools/round80-engine-pin-relations.py:185-205`) applies `anchor-is-tag-tip` only to
  rows labelled `not-a-release-tag`; a `tag:<name>`-labelled commit row is checked by label
  re-derivation instead (`:193-205`). Its docstring states the stricter reading at `:18-21`.
- The contradiction is therefore a *reading* one, and it is the exact class the round mined as F4:
  a verifier holding the plan's sentence will read `anchor-is-tag-tip`, the implementation will not.
  Neither is red today; the register discloses the label, so this is an exposure, not a defect. It
  is named here because no sibling gate can see it and the C2 critic seat must.

Consequence for the lane's own row: S553's anchor is tag `b11963`, 110 releases below `b12103`.
S553's `recheck: on-release` covers it; the relation row is the recheck trigger, not a stale-fact
finding.

---

## Over-claim matrix (if sibling ground were absorbed)

| Claim | Clean? | Over-claims if… |
|---|---|---|
| **C1** calibration | **clean** | …a seat greps the *phrase* instead of the *block shape*. The full shape `corrected F<n> old=… new=… at=<40hex> date=…` occurs fleet-wide only in kama's own round-80 files (`corpus/lessons/round-80.md`, `.ufo/waves/round-80/w1/SC01Lesson/round-80.md`, the spec/dispatch) and the round-79 draft under `.ufo/waves/round-79/w1/SC03Lesson/`; no sibling lane holds it. But the bare phrase "corrected F<n>" occurs as prose in `kasegi-shokunin/LOG.md:2016`, `kasegi-shokunin/corpus/instruments/r47-counters-selftest.py:204`, `kengaku-shokunin/corpus/lessons/round-26.md:71`, `kotodama-shokunin/reports/round-20/readme/gaps.md:358` — and round 79's *committed* lesson (`corpus/lessons/round-79.md:115,120`) carries `corrected F5/F6` blocks for a **different fact set** (round 79 graded round 78). Copying those answers nothing. |
| **C2** freshness | **clean on its predicate; not clean on its title** | (i) a seat restates kengaku's `b7200` relation as a verdict on S178; (ii) a seat repeats the chousa-method citation as a documented sibling boundary; (iii) **independently of siblings**, the claim text "every pin the lane holds on a serving engine carries a dated, re-derivable relation row" is already false against the lane's own `registry/ollama-live-pin.tsv:6` (Ollama **v0.40.11**, own-work row S523, `tools/kama-ollama-live.py`) — Ollama is absent from `engine-pins.tsv` and therefore from the register — while `PROVINCE.md:180` says "the lane owns the watch of its own pinned serving engines". The predicate is honest ("every engine in `registry/engine-pins.tsv`"); the title is not. |
| **C3** operability | **clean** | …a seat presents the Ollama fixture or the `listeners` observation as new. Both predate round 79: r60's `P04ProbeVersusOllama` ran the probe against the Ollama child without a `registered` key, and `SCORECARD.md:59` already names the second-engine step. The new object is the class-on-Ollama plus the engine register; the fixture, the pin (`registry/ollama-live-pin.tsv`) and the probe are held ground. |

No claim is over-claimed by any *sibling's* bytes today: C1's grammar, C2's register and C3's class
each have exactly one implementation, and it is kama's.

---

## Proposed move (one, bounded)

**Append one dated section to `corpus/knowledge/engine-pin-watch.md`** — the entry that defines the
register's population — that (1) states that the C2 relation register's population is exactly
`registry/engine-pins.tsv`'s three engines plus the two named cross-refs (S553's commit anchor,
kengaku's S178 tag), (2) records the Ollama **v0.40.11** pin (`registry/ollama-live-pin.tsv:6`) as
a held serving-engine pin *outside* that population — a routed frontier line, explicitly **not** a
fourth `engine-pins.tsv` row, because a fourth row makes the frozen `engines=3` target unreachable
— and (3) supersedes the ambiguous `(PROVINCE.md, round-38 note)` clause at `:70-71` with the
lane's own wording at `PROVINCE.md:168-170,180`, which is where the one-sided division is actually
recorded.

**Affected axes.** calibration (primary — claim text matches the counter's population; a dead
one-sided citation is retired) and freshness (secondary — an unwatched held pin is named, not
silently omitted). Operability and coverage untouched.

**Why this and not a fourth register row.** The frozen target counts `engines=3`; adding Ollama to
`engine-pins.tsv` would kill C2 by construction. Disclosing the same fact in the knowledge entry
costs no counter change and cannot harm a clean claim.

**Risks.**
- Append-only discipline: the entry already carries a `## Correction — round 44` section; the new
  section must *name* the superseded lines rather than rewrite them, or the pre-report gate's
  append-only arms see a deletion event.
- The section must **not** assert a relation for Ollama (no Ollama tag list was fetched this round;
  absence of a row is the only claim). Asserting `behind`/`current` for it would be an unbacked
  freshness claim — the exact F4 class.
- It must not restate kengaku's `b7200` relation as knowledge about S178; the row is kama's
  relation, kengaku's row stays kengaku's.
- If the L1 prefers to narrow the claim title in `SCORECARD.md`/`LOG.md` instead, the two are
  compatible; do not do both in a way that states the population twice with different words.

**Verification (read-only, all reproducible before the append).**
- `grep -n 'chousa' /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/engine-pin-watch.md`
  → `:70-71` (today), plus the new section heading after.
- `git -C /home/vgpnk/Projects/shokunin/chousa-shokunin log -S 'tag' -- PROVINCE.md` → exit 0,
  **no commit lines**; `wc -c chousa-shokunin/PROVINCE.md` → 880.
- `awk -F'\t' 'NR>1{print $1}' kama-shokunin/registry/engine-pins.tsv` → `sglang`, `vllm`,
  `llama.cpp` (no `ollama`); `grep -n '^version' kama-shokunin/registry/ollama-live-pin.tsv` →
  `6:version 0.40.11`.
- `python3 tools/pin-watch.py check --pins registry/engine-pins.tsv` still reports `pins=3` (the
  append does not touch the register); the frozen line `PIN_RELATIONS engines=3 refs=5
  unexplained=0` stays reachable.

**Scan limits.** No `git ls-remote`, no counter run, no sibling execution, no `pre-report-gate.py`;
all sibling statements are current-tree reads, not sibling green/red receipts. Sibling `PROVINCE`/
`SOURCES` reads are not certification of the siblings' own gates.

---

## Receipts

| path (absolute) | command | exit |
|---|---|---|
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/CN01Connector/scan.out` | scan transcript (write target) | 0 |
| — | `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master` → `fe7b978013bd1aa6d67a7e0fbf6369b8d7a9b023` | 0 |
| — | `grep -rlnE 'b11755\|39febd2a\|b7200' /home/vgpnk/Projects/shokunin/*/ --include='*.md' --include='*.tsv' --include='*.py' --include='*.sh' \| grep -v '/\.ufo/' \| grep -v '^…/kama-shokunin/'` → 9 files (5 kengaku, 4 kaidoku hash collisions) | 0 |
| — | `grep -rln 'engine-pins\|pin-watch' /home/vgpnk/Projects/shokunin/*/ …` (same filters) → no output | 1 |
| — | `grep -rlnE 'registered=(no\|yes)\|class_missing' /home/vgpnk/Projects/shokunin/*/ …` (same filters) → no output | 1 |
| — | `grep -rlnE 'corrected F[0-9]+ old=[^ ]+ new=[^ ]+ at=[0-9a-f]{40} date=' /home/vgpnk/Projects/shokunin` → 5 kama paths, 0 sibling | 0 |
| — | `git -C /home/vgpnk/Projects/shokunin/chousa-shokunin log -S 'tag' -- PROVINCE.md` → no commit lines | 0 |
| — | `python3 -c` on `.ufo/waves/round-60/…/probe-qualified.json` → `'registered' in dumps = False`; row keys `bind,evidence,owner,port,reason,served_model,verdict` | 0 |

No tool was installed or upgraded; no pacman transaction; no host service touched. Nothing was
written outside `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/CN01Connector*`.
