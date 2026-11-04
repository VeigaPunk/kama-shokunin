# kama round 80 — lesson

author: kama L1 (integration; drafted by SC01Lesson seat, landed by the L1)

Lane: kama. Round 80 is ONE v1 wave of **13 seats** (build + attack); base
`c45fc7d1a8427e9c98a9dd7befa542c7b5caed38`; the sealed revision C1 grades is
`a9b4543f14625d0f37daa42ef664ee6f6ea975ea` (round 79's tip). This file is the correction container
C1 reads at the tip: the three blocks under §Corrections are appended here and are never written
into the round-79 record's bytes.

## Gate

Every row is a source opened this round with `curl`; each receipt named in the last column lives
under `.ufo/waves/round-80/w1/SC01Lesson/gate/` and carries the command, the UTC access time, the
HTTP status, the byte count, the sha256 and the located lines quoted here.

| # | Source (URL) | Accessed · status · bytes · sha256 | Located quote (≤25 words) | Disposition · reason · flip | Receipt |
|---|---|---|---|---|---|
| 1 | Ollama `docs/api.md` at tag v0.40.11 — https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api.md | 2026-11-04T10:42:58Z · 200 · 54614 bytes · `96db03080e385dbabf5d70e75f298d41b75983bc30975cae56f7119f848dd0f5` | "List models that are available locally." — **6 words**, line 1358, under `## List Local Models` (line 1352) and `GET /api/tags` (line 1355) | **Admit.** C3's census class needs a second engine's *model-list* semantics; the pinned file names the listing endpoint and states in one sentence that the list is the local inventory, and the same file keeps loaded residency in a separate section (`## List Running Models` / `GET /api/ps`, lines 1763/1766, whose sentence at line 1769 reads "List models that are currently loaded into memory."). Scope: available-inventory versus loaded-residency only (KQ13); not served identity, not inference readiness, not this host's Ollama behaviour. **Flip:** a round that grades a loaded-model or readiness claim from `/api/tags` retracts this row, as does a revision whose `/api/tags` section claims more than a listing. | `.ufo/waves/round-80/w1/SC01Lesson/gate/ollama-api-tags.out` |
| 2 | llama.cpp server README @ `39febd2a` (S553, supersession of its anchor) — https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/tools/server/README.md | 2026-11-04T10:42:58Z · 200 · 135608 bytes · `8fd5abde2fb52de3b30f30a170631d4c0d92febecc8da44d0541e48b132b35c6` | "If a model is not running, it will be added or updated according to the source" — **16 words**, line 2227, note 1 (line 2224) of the heading at line 2197 | **Admit as a supersession of S553.** S553's region label `§Router mode` is not a heading in these bytes; the heading it names is ``### GET `/models`: List available models`` (line 2197 — the literal bytes carry backticks around `/models`), and the cited content is note 1, the `?reload=1` refresh note, second bullet at line 2227. S553's scope is unchanged: the router's model list is an inventory (each entry carries `status.value`, values including `unloaded`), never a served-identity normalisation and never a readiness claim. Bytes are identical to round-79's own receipt digest. **Flip:** a revision that renames the heading, renumbers the note, or moves the sentence out of note 1 makes this locator stale and needs another supersession row, never an edit of S553's bytes. | `.ufo/waves/round-80/w1/SC01Lesson/gate/s553-router-models.out` |
| 3 | llama.cpp `docs/preset.md` @ `39febd2a` — https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/docs/preset.md | 2026-11-04T10:42:58Z · 200 · 4090 bytes · `3e6643541e12ff3dfee2a23c23a57357403bf4500beced780f010eaebbbdfe13` | "INI preset files can be used to configure model-specific parameters" — **10 words**, fragment of line 9, `## Using Presets with the Server` (line 7); the full line is 28 words, and this fragment is its middle clause | **Reject.** No claim in this round parses a preset file: C1 grades record facts, C2 records pin relations from `git ls-remote --tags` or a committed tag list, C3 reads a model list. A row would scope a configuration format no instrument in this round reads — the defect would be ground, not tier. The bytes are identical to the copy round 79 rejected and to `master` at access time. **Flip:** a round that grades preset-inherited parameters on a lane-owned fixture (an INI preset's `[*]` defaults, `--models-preset` precedence, or a preset-driven reload) reopens it. | `.ufo/waves/round-80/w1/SC01Lesson/gate/preset-md.out` |

## Corrections

The three blocks below answer the three facts the round-80 C1 counter reports stale at the sealed
revision `a9b4543f14625d0f37daa42ef664ee6f6ea975ea`. In each, `old` is the value the round-79 record
declares at that revision, `new` is the value the counter re-derives at the round-80 tip, `at` is the
sealed revision and `date` is the date the correction is filed. Each fact is answered by exactly one
block; the round-79 record's bytes are not rewritten.

`corrected F4 old=c2=verified new=c2=not-verified:failed=1 at=a9b4543f14625d0f37daa42ef664ee6f6ea975ea date=2026-11-04`

`corrected F5 old=before-selftest=pass=26 new=before-selftest=pass=22 at=a9b4543f14625d0f37daa42ef664ee6f6ea975ea date=2026-11-04`

`corrected F6 old=log=all-verified new=log=c2-not-verified at=a9b4543f14625d0f37daa42ef664ee6f6ea975ea date=2026-11-04`

**F4 — the C2 verdict.** The round-79 record states C2 `verified` in three places at the sealed
revision: the SCORECARD banner ("C2 operability verified"), the §Round 79 claim table's C2 row, whose
verdict cell ends `**verified**`, and LOG §Round 79's sentence "Three claims, three distinct axes, all
verified on their receipts". The receipt that same row cites, `.ufo/waves/round-79/measured/after/c2-gate.out`,
prints `PRE_REPORT round=79 arms=10 failed=1 uncommitted=0` and `EXIT=1`, with arm 8
`round75-instruments` red (`APPEND_ACCEPTED events=58 accepted=53 unaccepted=5`). The record is not
concealing that red: its own §Gate reproduces the failing line (SCORECARD.md:4662 at the sealed
revision) and names the red arm and its cause, while the round's own frozen C2 predicate required "a
scored run at the tip must print `PRE_REPORT round=79 arms=10 failed=0 uncommitted=0`"
(`corpus/lessons/round-79.md` lines 18–20 at the same revision). The verdict cell and the banner still
read `verified` against a predicate the record itself prints as unmet.

**F5 — the C2 before tally.** The same claim table's before cell reads "`ARM_ORDER` 9 arms,
`PRE_REPORT_SELFTEST pass=26 fail=0`" and cites `.ufo/waves/round-79/measured/before/c2-gate-arms.out`.
The committed selftest receipt for that run, `.ufo/waves/round-79/measured/before/c2-gate-selftest.out`,
ends `PRE_REPORT_SELFTEST pass=22 fail=0` with `EXIT=0`, and the cited arms receipt carries only
`BASE_ARM_ORDER 9 [...]` and no selftest tally at all (3 lines, 300 bytes, at both the sealed revision
and the tip). The declared `pass=26` is in neither receipt: the run's own before tally is 22, and the
path the cell cites cannot support the cell.

**F6 — the LOG verdict.** LOG §Round 79 opens "Three claims, three distinct axes, all verified on their
receipts". The C2 receipt that sentence rests on is red (`failed=1`, `EXIT=1`), so the LOG's closing
verdict word does not hold for C2; the value the counter re-derives at the tip is `log=c2-not-verified`,
taken from that same C2 receipt rather than from the LOG's prose. The LOG-side disclosure is an
appended round-80 correction entry of the form `LOG-CORRECTION round=79 claim=C2 verdict=not-verified`,
appended at the end of the log — never an edit of the round-79 bytes.

## Mistakes

| Class | Evidence pointer | Captured-by | Fix |
|---|---|---|---|
| `verdict-stated-from-intent` — a record's verdict word is written from what the round meant to establish, not from the receipt it cites. | At the sealed revision `a9b4543f`, round 79 states C2 `verified` in three places — the SCORECARD banner, the §Round 79 claim table's C2 row (ending `**verified**`) and LOG §Round 79's "all verified on their receipts" — while the receipt that row cites, `.ufo/waves/round-79/measured/after/c2-gate.out`, prints `PRE_REPORT round=79 arms=10 failed=1 uncommitted=0` with `EXIT=1`, and §Gate reproduces the failing line at SCORECARD.md:4662 and names the red arm, even though the round's own frozen C2 predicate required `PRE_REPORT round=79 arms=10 failed=0 uncommitted=0` — the verdict word contradicts a number the record prints, not a number it omitted. The same record's before cell states `PRE_REPORT_SELFTEST pass=26 fail=0` while the committed selftest receipt prints `pass=22 fail=0`. Routed at round-79 closure as R79V1 (SCORECARD verdict overstatement), R79V1b (before tally) and R79V2 (LOG line). | The new C1 facts: **F4** compares the claim table's verdict cell with the exit code of the receipt that row cites, **F5** compares the before cell's tally with the committed selftest receipt, **F6** derives the LOG verdict from the same red receipt. At the round-79 base no rule tested a carried verdict against the exit code its own receipt prints; the round-79 spot-check found it by reading. | `tools/round80-selfrecord-round79.py` makes a future record's carried verdict re-derive from the tree or be answered by exactly one dated, value-bound correction block, so the counter turns red on the next intent-stated verdict; the criterion it grounds is the round's **KQ132** — a self-record fact is stated only in the form its receipt prints it, and a claim whose own cited receipt disagrees is unverified regardless of intent (drafted at `.ufo/waves/round-80/w1/SC02Sources/quality-criterion.md`, filed in `corpus/QUALITY.md`). |
