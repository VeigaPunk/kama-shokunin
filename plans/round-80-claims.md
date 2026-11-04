# kama round 80 — frozen claims

Lane: kama. Round 80 (attempt 1). Base (lane tip at round start):
`c45fc7d1a8427e9c98a9dd7befa542c7b5caed38`. Assigned axes (`shokunin.conf` kama row):
operability + calibration. Sealed revision for claim C1 (the round-79 self-record):
`a9b4543f14625d0f37daa42ef664ee6f6ea975ea` (the lane tip the round-79 verifier spot-check
graded; the closure commit `c45fc7d1` is a later, non-author artifact and is not graded).

Three claims, three distinct axes; C1 works calibration (7), the lowest assigned axis,
which sits below the saturation line (8/10), so the stagnation nudge is inactive. This plan
is the freeze: the predicates, fact value strings, target lines, controls and kill rules
below are fixed before any seat or counter produces data, and are not rewritten afterwards.
Pre-freeze receipts sit under `.ufo/waves/round-80/measured/before/` and
`.ufo/waves/round-80/measured/control/`.

## C1 — calibration: the round-79 self-record's six declared facts re-derive, or are answered by dated value-bound corrections

PREDICATE (this sentence is the counter's docstring `PREDICATE`, its receipt label and the
claim text — one sentence in three places):

> `python3 tools/round80-selfrecord-round79.py --repo <lane>` prints one `SELFRECORD_R79
> claims=6 mismatches=0 corrected=3 unbacked=0` line and exits 0 only when each of the six
> facts the round-79 self-record declares re-derives from the tree at the sealed revision
> a9b4543f14625d0f37daa42ef664ee6f6ea975ea and matches the same fact re-derived at the tip,
> or is answered by exactly one committed `corrected F<n> old=<value> new=<value> at=<40-hex>
> date=<ISO>` block whose `old` is the sealed value, whose `at` is the sealed revision and
> whose `new` equals the fact's tip value; it exits 1 naming every unanswered fact otherwise.

The six facts, each declared by the record's own bytes at the sealed revision and each
derived from the tree at that same revision (value strings are the receipt labels):

| Fact | Declared by the record | Declared value string | Observed at sealed and at the tip |
|---|---|---|---|
| F1 lowest assigned axis | §Round 79: "the lowest assigned axis (calibration 7) carries C1" | `lowest-axis=calibration:7` | from the sealed `## Axes` table over the assigned pair, both revisions |
| F2 population | §Round 79: "sources registry 292 → 293 rows …; filtered knowledge entries 51 → 52" | `population=sources:293,knowledge:52` | source-row count and filtered knowledge-blob count at sealed and tip |
| F3 wave shape | §Round 79: "one v1 wave, 14 seats (4 executor, 3 scribe, 2 scout, 1 connector, 1 reviewer, 2 critic, 1 mutation-tester; attack 4/14 = 29 %)" | `wave=seats:14,executor:4,scribe:3,scout:2,connector:1,reviewer:1,critic:2,mutation-tester:1,attack:4/14` | `.ufo/waves/round-79/w1-spec.json` at sealed and tip |
| F4 C2 verdict | §Round 79 claim table: the C2 row ends `**verified**`; the banner reads "C2 operability verified" | `c2=verified` | the record's own cited receipt `.ufo/waves/round-79/measured/after/c2-gate.out` prints `PRE_REPORT round=79 arms=10 failed=1 uncommitted=0` → `c2=not-verified:failed=1` (stale) |
| F5 C2 before tally | §Round 79 claim table, C2 before cell: "`ARM_ORDER` 9 arms, `PRE_REPORT_SELFTEST pass=26 fail=0`" | `before-selftest=pass=26` | `.ufo/waves/round-79/measured/before/c2-gate-arms.out` prints `PRE_REPORT_SELFTEST pass=22 fail=0` → `before-selftest=pass=22` (stale) |
| F6 LOG verdict | LOG §Round 79: "Three claims, three distinct axes, all verified on their receipts" | `log=all-verified` | the C2 receipt is red, and the tip LOG carries the round-80 appended correction token `LOG-CORRECTION round=79 claim=C2 verdict=not-verified` → `log=c2-not-verified` (stale) |

Pre-freeze measurement (`measured/before/c1-enum.out`): `SELFRECORD_R79_ENUM claims=6
stale=3 corrected=0`, exit 1 — F4, F5 and F6 are the three stale facts, which fixes
`corrected=3` in the target before data. The three corrections are the round-79 closure's
routed defects R79V1 (F4, the SCORECARD verdict overstatement), R79V1b/R79V2 (F5 before-tally,
F6 the LOG "all verified" line).

- **Target:** exit 0 with `SELFRECORD_R79 claims=6 mismatches=0 corrected=3 unbacked=0` at
  the round-80 tip.
- **Control that skips the claimed work:** the same counter, same sealed tree, the tip's
  correction container with `--no-corrections` — `SELFRECORD_R79 claims=6 mismatches=3
  corrected=0 unbacked=0`, exit 1 (`measured/control/c1-score-nocorrections.out`, produced
  pre-freeze against the tip before the corrections land). A do-nothing round cannot print
  the target line.
- **Correction grading:** a block is `corrected F<n> old=<value> new=<value> at=<40-hex>
  date=<ISO>`; it answers a fact only when `old` equals that fact's sealed value, `at` is the
  sealed revision (40 hex, resolving to it) and `new` equals the fact re-derived at the tip.
  Two blocks for one fact answer nothing; a block whose `new` does not re-derive leaves the
  fact unbacked; a 41-character or unresolvable `at` token answers nothing (the round-78
  `unresolvable-cited-hash` class).
- **Scope ruling:** facts are read from `git show <sealed>:…` and `git show <tip>:…`, never
  from the worktree, so the round's own record commit cannot refute a fact (the round-78 F2
  defect). The correction container is `corpus/lessons/round-80.md` §Corrections, appended,
  never a rewrite of the round-79 record; the LOG correction is an appended entry, never an
  edit of the round-79 bytes.
- **Kill rule:** the claim fails if the frozen line is not printed at the tip, if the control
  reaches the target line, or if any correction's `new` value does not re-derive at the tip.

## C2 — freshness: every pin the lane holds on a serving engine carries a dated, re-derivable relation row

PREDICATE:

> `python3 tools/round80-engine-pin-relations.py --repo <lane>` prints one
> `PIN_RELATIONS engines=3 refs=5 unexplained=0` line and exits 0 only when
> `registry/engine-pin-relations.tsv` carries one dated row for every engine in
> `registry/engine-pins.tsv` and for the two llama.cpp references the lane cites from other
> rows (S553's commit anchor and kengaku's S178 tag b7200), each row's `newest`/`newer`/
> `relation` cells equal the live `git ls-remote --tags` computation over that engine's
> repository (or its committed tag list under `--tags-dir`), a tag row names a release tag
> that exists upstream, a commit row's 40-hex anchor is not any upstream tag's peeled oid,
> and every row's receipt path exists and is committed.

- **Before:** `registry/engine-pin-relations.tsv` does not exist. The lane holds three
  llama.cpp references with no declared relation — the install pin `b11755`
  (`registry/engine-pins.tsv`), the round-79 source anchor `39febd2a…` (SOURCES S553) and
  kengaku's S178 tag `b7200` — and the live `python3 tools/pin-watch.py check --pins
  registry/engine-pins.tsv` run reports `pins=3 current=0 behind=3 missing=0 error=0`
  (`measured/before/c2-pinwatch.out`), so all three engine pins are behind upstream with no
  recorded relation to their upstream newest release.
- **Target:** exit 0 with `PIN_RELATIONS engines=3 refs=5 unexplained=0` at the round-80 tip.
- **Control that skips the claimed work:** a header-only register (no rows) scores
  `refs=0` and exits 1 (each `engine-pins.tsv` row lacks its relation row); a copied register
  whose `llama.cpp` install row claims `current` scores `unexplained=1` and exits 1
  (`measured/control/c2-empty-register.out`, `measured/control/c2-stale-relation.out`).
- **Scope ruling:** the register records relations, not knowledge: a `behind` row is a
  recheck trigger (the pinned docs still describe the pinned release) and never a claim that
  the lane's held knowledge is wrong. Tag lists are committed under
  `measured/after/c2-tags/<engine>.txt` so the counter re-runs offline at closure; the live
  leg is `git ls-remote --tags`, the mechanism `tools/pin-watch.py` already uses. No engine
  is installed or upgraded by this round.
- **Kill rule:** the claim fails if a relation cell does not re-derive from the committed tag
  list, if any engine or any of the two cross-references is missing a row, or if the counter's
  target line is reachable with an empty or stale register.

## C3 — operability: the `registered` census class is proven on a second engine fixture and its engine coverage is a register

PREDICATE:

> `python3 tools/round80-ollama-census.py --repo <lane>` prints one `OLLAMA_CENSUS
> port=<p> engine=ollama unregistered=1 governed=1 class_missing=0` line and exits 0 only
> when the lane-owned pinned Ollama child (v0.40.11, scratch HOME and model store, one model
> created from the lane fixture GGUF) serving on a free loopback port is reported by
> `bash tools/kama-probe.sh listeners` as `registered=no` under a registry that does not
> declare that port and as `registered=yes` under one that does, the summary's
> `unregistered`/`governed` counts move with the class, and the run writes the engine's
> receipt into the class-engine register; `--audit` then prints `CLASS_ENGINES engines=2
> verified=2 stale=0` only when every register row's receipt exists, carries `class_missing=0`
> and names the same engine.

- **Before:** the class is proven on one engine only (the llama.cpp fixture, round 79); the
  class-engine register `registry/unregistered-class-engines.tsv` does not exist
  (`measured/before/c3-engines-before.out` prints `CLASS_ENGINES engines=0`, exit 2), and no
  committed receipt names an Ollama listener's `registered` class.
- **Target:** the fixture leg's `OLLAMA_CENSUS … class_missing=0` line with exit 0, and
  `--audit` printing `CLASS_ENGINES engines=2 verified=2 stale=0`, exit 0, at the round-80
  tip.
- **Control that skips the claimed work:** the base probe copy (no `registered` class) scored
  by the same counter prints `class_missing=1`, exit 1 (`measured/control/c3-base-probe.out`);
  a register naming one engine scores `engines=1` and exits 1
  (`measured/control/c3-one-engine.out`); the counter's selftest carries `absent-probe`,
  `probe-error`, `class-missing` and `one-engine` arms.
- **Sourced claim:** rests on the round-80 `SOURCES.md` row for Ollama's `GET /api/tags`
  documentation at the pinned v0.40.11 release (URL opened this round; the Gate block carries
  the URL, access date and a located ≤25-word quote): a tags listing is an inventory of models
  available locally, not proof a model is loaded, so a second engine's model list is exactly
  what the census class needs and no more.
- **Scope ruling:** a census class and its engine register, not a verdict: the verdict
  vocabulary is unchanged, no registry consumer row is admitted (consumer pins are
  operator-owned), the Ollama child is lane-owned, runs under a scratch HOME/model store and
  is torn down in the run (the round-60/61 fixture boundary), and the live-host leg is
  informational and gates nothing.
- **Kill rule:** the claim fails if the class reads `unregistered` for a registered port, if
  the two registry legs return the same class, if the Ollama leg is satisfied by the
  llama.cpp fixture, or if the register audits green with one engine.

## Round scope and record allow-list

Paths this round may commit: `plans/round-80-claims.md`;
`tools/round80-selfrecord-round79.py`, `tools/round80-engine-pin-relations.py`,
`tools/round80-ollama-census.py`, `tools/round78-live-reconcile.py`,
`tools/pre-report-gate.py` (docstring/prose only); `registry/engine-pin-relations.tsv`,
`registry/unregistered-class-engines.tsv`; `SCORECARD.md`, `LOG.md`, `SKILL.md`,
`PROVINCE.md`; `corpus/SOURCES.md`, `corpus/QUALITY.md`, `corpus/README.md`,
`corpus/knowledge/*.md`, `corpus/lessons/round-80.md`; `.ufo/waves/round-80/**`;
`registry/*` only when a routed disposition requires a register row. Nothing outside this
list; no sibling lane and no operator-owned file is touched.

## Frontier step (§2b) and the round-79 routed defects

- **SOURCES:** one new row (Ollama `docs/api.md` at v0.40.11, URL opened this round, located
  quote), one supersession row replacing S553's region-label anchor with the heading it names
  (R79V6), one `REJECTED` row for `docs/preset.md` with its flip (R79V4); one admitted
  `corpus/knowledge/` entry on the second-engine class and one coverage-map row.
- **Mistake mined:** round 79 filed the C2 claim as `verified` in the SCORECARD banner, the
  claim table and the LOG while its own cited receipt printed `failed=1` — a self-record fact
  stated from the intent, not from the receipt (R79V1/V2). Captured by the new F4/F5/F6 facts;
  fix is the counter plus the KQ criterion it grounds.
- **Round-79 routed defects R79V1–R79V7:** V1 fixed by the appended SCORECARD correction and
  the head-section re-derivation; V2 by the appended LOG correction entry; V3 by the
  `round79-selfrecord-round78.py` docstring fact list; V4 by the `REJECTED` SOURCES row; V5 by
  re-documenting the C3 control from `git show <base>:tools/kama-probe.sh`; V6 by the
  supersession SOURCES row; V7 by the validate-warning inventory and the gate docstring's arm
  numbering. Round-79's own note routes one more: `round78-live-reconcile.py --selftest` must
  write under TMPDIR/`--scratch`, not into `.ufo/waves/round-78/measured/after/`.
- **Note on the inherited pre-report gate:** `round75-append-accepted.py` grades deletion
  events in append-only files against a register whose rows must predate the register's
  introduction; round-79's own commits `4af44f7` (SCORECARD.md, `corpus/lessons/round-79.md`)
  left unaccepted events that no post-introduction row can answer. Arm 8 is therefore red at
  the base and stays red at the tip; this round adds no append-only deletion of its own and
  reports the inherited red as debt, never as a green gate.
