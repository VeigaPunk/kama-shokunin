# CN01 — sibling-overlap scan for the three round-79 claims

Seat `CN01Connector`, kama round 79 wave 1. Read-only. Full evidence table and receipt block:
`.ufo/waves/round-79/w1/CN01Connector/overlap.md`. This file is the scoped finding.

Lane tip seen while scanning: `f7442dea53bd8f474293a2252437b5d869801f49` (past the round base
`ee53f1a2…`); base-state evidence is read from `git show ee53f1a2:…`, never the worktree.

---

## C1 — calibration (six round-78 facts re-derive at `7a3cd982`)

**Who owns adjacent ground.** Four lanes hold a claim-vs-tree or revision-token mechanism:

- **chousa** — `tools/claims-audit-v2.py:1-12` audits self-assessment statements in a claims
  file against committed files (seven rule classes, ten selftest cases, `--selftest-fault`);
  `tools/freeze-check.py` adds claims/context digest checks (`DIGEST_STRAY`). Rows:
  `chousa-shokunin/SKILL.md:156`, `:151`.
- **kengaku** — `plans/anchor_digest_check.py:1-12` binds every `sha256 <hex>` claim in
  `corpus/SOURCES.md` to the capture *that row names*.
- **tameshi** — `tools/receipt-revision-gate.py:25-31` named revision refusals; `:43`
  `REV_RE = re.compile(r'\brev=([0-9a-f]{7,40})\b')`; row `tameshi-shokunin/SKILL.md:1547`.
- **tsukuroi** — the `--revision <REV>` re-derivation idiom, including a gate literally named
  `source-scope-correction` (`tsukuroi-shokunin/SKILL.md:1778, 1897, 1899`).

**Does our change take any of it?** No. None reads a round record's declared facts at a sealed
revision, and none carries the correction grammar. `grep -rln "old=[^ ]* *new=.*at="` over
non-`.ufo/`, non-kama files → 0 files, exit 1: the block grammar is unoccupied.

**Sharpest non-overlap (state it, do not paper over it).** tameshi's revision token accepts
**7-40** hex (`receipt-revision-gate.py:43`); C1's `at` requires exactly **40** and a
41-character token answers nothing. C1 re-implements a *stricter* rule; it does not adopt
tameshi's gate, and calling it "reuse of the fleet revision gate" would be false.

**Nearest semantic twin** is kengaku's digest binding vs fact **F2**
(`skill:a50f6f74/1736, province:6b8c604f/331`): same shape (digest claim bound to named
content), different source of truth (kengaku's `corpus/evidence/` vs `git show <sealed>:path`)
and different lane. No shared file.

---

## C2 — operability (tenth arm composes the three round-78 instruments)

**Who owns adjacent ground.**

- **chousa** — `tools/lane-preflight.py:5-20`, summary print `:327`: one command runs the
  lane's eight committed gates one `GATE <id> <name> PASS|FAIL|ENV` line each, then
  `PREFLIGHT=<passed>/<run> FAILED= ENV= SKIPPED=`, exit 0 only when at least one gate ran and
  all that ran passed — and it composes the lane's *instrument selftests* (freeze-check,
  assimilate-rows, research-gate). Row `chousa-shokunin/SKILL.md:154`. This is the closest
  structural prior art to arm 10.
- **kumitate** — `scripts/round-gate.mjs:8-19` lane-local round-close pre-check with
  `--selftest`, explicitly "NOT a fleet report-conformance authority"; row
  `kumitate-shokunin/SKILL.md:609`.
- **souji** — `tools/souji-pre-report-gate.sh:23-24,76`: five artifact checks
  (`tip/report/shonen/clean/prereg`), `check-<name>=PASS|FAIL`, exit 1 on any FAIL, no arms,
  no selftest; row `souji-shokunin/SKILL.md:256`. Name overlap only.
- **tameshi** — literal counted gate selftest cases and a fixture dir per gate
  (`tameshi-shokunin/SKILL.md:1547`); precedent for `pass=22 → pass=26` meaning four real
  cases, not a restated tally.

**Does our change take any of it?** No shared code, no shared registry, no shared module.

**Flag — the registry-row half has a sibling that looks applicable and is not.** mori's
`tools/mori-gate-registry.py:5-23` audits SKILL.md gate-registry rows (eight standard cells,
real `--self-test` argv detection, `duplicate`/`wrong_row`) and prints
`registered= unregistered= no_selftest= …` at `:42`; row `mori-shokunin/SKILL.md:184`. Its
parser selects only tables headed `name | kind | entry | verdict map | self-test | pinned
values | write scope | owner` (`:215`, fail-closed `raise` at `:359`; header seen at
`mori-shokunin/SKILL.md:162`). kama's gate table is five columns
(`kama-shokunin/SKILL.md:303`: `Name | Kind / entry command | Exit map | Self-test / pinned
values | Write scope`), so mori's auditor cannot grade kama's row — it errors. Do not cite it.

**Base ledger (sealed base bytes).** `git show ee53f1a2:tools/pre-report-gate.py`: `ARM_SPECS`
holds 5 names at `:214`; `ARM_ORDER` appends `round-clean`, `round74-v2`,
`round75-instruments`, `round77-instruments` at `:223-224` → 9 arms, matching the plan's
"Before". The row C2 edits is `SKILL.md:309` and already says "nine arms".

---

## C3 — coverage (unregistered serving listener as a census class)

**Who owns adjacent ground.**

- **kengaku** — same live listener, same upstream surface, different question.
  `corpus/knowledge/served-endpoint-identity-pin.md:1` (source S178), `:16-23` six-field pin,
  `:35` "router `http://127.0.0.1:1234` — `lfm3-server.service` … lists 5 model ids"; row
  `corpus/SOURCES.md:193`; index `corpus/README.md:584` ("a pin is host state, not a capability
  claim"); live observation `SCORECARD.md:3434-3435` (`llama-server` alive on `:1234`). kengaku
  binds an **eval identity**; C3 classifies **governance**. C3's "census class, not a verdict"
  scope ruling is the mirror of kengaku's rule and takes nothing.
- **research/** (fleet root, not a lane) — `round-18-kimi-model-routing/census/scripts/
  probe_shims.py:1-14` discovers systemd shim units, records whether a listener exists on
  `SHIM_PORT`, and cross-references each port to the config provider whose `base_url` points at
  it. Closest fleet prior art for port ↔ registry cross-reference; one-off census, no class
  column, no exit contract, outside every lane's `tools/`.
- **tabi** — `scripts/chrome-cdp-loopback-round59.mjs:63-64,149`: loopback DevTools/fixture
  ports probed for teardown. Hygiene, not governance.
- **mado / mori** — vocabulary only: `CHECK96: … unregistered= …`
  (`mado-shokunin/quality/check-landed-contract.py:14,88`) counts contract classes;
  `mori-shokunin/tools/mori-gate-registry.py:42` counts registry rows. Neither reads a socket.

**Does our change take any of it?** No. Positive uniqueness evidence: `class_missing` appears in
no sibling `.py`/`.sh`/`.mjs` (single non-wave hit is kama's own
`.ufo/waves/round-79/build-spec.py`); no sibling ships an `ss -ltn` enumerator in `tools/` or
`scripts/` (all such hits are wave scratch or the `research/` census); the base probe's
`listeners` summaries carry no `registered`/`governed` keys
(`git show ee53f1a2:tools/kama-probe.sh:745,750`).

**Two hazards for C3's source leg (in-lane, flagged because they touch the plan's allow-list).**

1. Three llama.cpp pins: kengaku S178 = **b7200** (`ab49f094…`); kama
   `registry/engine-pins.tsv:4` = **b11755** (`704366d76`); the plan's new row =
   **39febd2adb947b70da35e95f9351b3bf58ad170a**. `grep -rn 39febd2a kama-shokunin/registry
   kama-shokunin/corpus` → exit 1, no match: the pin exists nowhere but the plan. Either the
   Gate block states the divergence from the engine-pins line, or `pin-watch.py` reads three
   unrelated revisions.
2. The surface is adjacent to kama's own holdings: `corpus/SOURCES.md:232` (S479) already rows
   the router model listing *code* (`server-models.cpp`, `get_router_models`,
   `context_length`) at `704366d76`, and `:49` (S037) rows router readiness at the same commit.
   The new row must read as router *docs* (`GET /models`) at a newer commit, never as a new
   surface.

---

## D — fleet contract and protocol adjacency (not a lane; read-only)

Four fleet-level clauses and two kumitate mechanisms bound what round 79 may claim.

- **`PROTOCOL.md:375-416` §Gate standard.** Registry row schema is **eight fields** (name,
  `gate|probe`, entry command, verdict map, self-test command+spelling, pinned-value path, write
  scope, owner — `:398-404`, row fields at `:401`); registry home is the lane's own `SKILL.md`;
  the integrator does not execute a sibling's gate (`:415-416`). C2's row-in-SKILL.md requirement is
  protocol-grounded, but kama's gate table is five columns (`kama-shokunin/SKILL.md:303`), so the
  new row cannot be called §Gate-standard conformant and mori's schema-implementing auditor cannot
  read it. Fixing the table shape is not C2's scope.
- **`PROTOCOL.md:390-395` "Two evidences".** A verdict names the revision it was measured
  against. This is the clause the round-78 F2 defect (worktree read) violated; it supports C1's
  `at` binding and C3's committed-fixture shape.
- **`PROTOCOL.md:133-136`, `:366-367`.** A correction to a filed report lands in the correcting
  round's own record or as an erratum appended after the filed bytes, naming the text it
  supersedes — never a rewrite. C1's container form is not novel; only its block grammar is.
- **`PROTOCOL.md:365-366` "Corrections sweep every mention".** Both superseded mentions stand in
  `SCORECARD.md` §Round 78: F5 at `SCORECARD.md:4538` ("green at `rev=22cce544`") and F6's prose
  at `:4527-4528` ("the pre-correction tip run and the corrected tip run are both in the
  lesson"), inside the section that declares itself "recorded, not rewritten" (`:4510`). A third mention at `corpus/lessons/round-78-verifier-spotcheck.md:33` is outside the
  round-79 allow-list and is a filed record. The L1 must state the disposition: an erratum
  **naming** `SCORECARD.md:4527-4538` as superseded (satisfies the sweep clause without
  rewriting round-78 bytes), and the spot-check left as history with its reason.
- **kumitate `harm-matrix`** — a registry of the lane's gates run at BASE and TIP in separate
  sandbox clones, one row per gate with a transition (`HELD`/`REPAIRED`/`HARM`/`NEW_RED`/…),
  fail-closed on a missing verdict line or timeout: `kumitate-shokunin/scripts/harm-matrix.mjs:3-16`,
  gate list `scripts/harm-matrix-gates.json:1-20` (it composes `counter-pins-selftest`,
  `round-gate-selftest`, `sources-check-selftest`), row `kumitate-shokunin/SKILL.md:640`. Closest
  fleet mechanism to both the round's before/target structure and arm-style composition of other
  instruments' selftests — so C2's novelty must be lane-scoped.
- **kumitate `routed-ledger`** — a routed defect closes only when its row binds `path:line` plus a
  quote at that exact line: `kumitate-shokunin/scripts/routed-ledger.mjs:3-18`, row
  `kumitate-shokunin/SKILL.md:639`. kama's V1-V7 dispositions are prose in `SCORECARD.md` §Round 79
  and the report (no ledger file in the allow-list); name the gap, do not import the ledger.

---

## Boundary lines the L1 can lift into the report

1. C2 novelty, stated honestly: arm 10 is the first composition of the three round-78
   instruments inside *this* lane's gate; fleet-wide, chousa's `lane-preflight` already composes
   that lane's own instrument selftests.
2. C2's registry row is graded by kama's own five-column discipline; mori's eight-cell auditor
   cannot parse it (`mori-gate-registry.py:215,359` vs `kama-shokunin/SKILL.md:303`).
3. `unregistered=` carries three populations fleet-wide (mado contract classes, mori registry
   rows, kama listeners). Any cross-lane sentence must name the population.
4. C3's source leg needs one sentence separating it from kengaku S178 (server README, b7200,
   eval identity) and from kama S479/S037 (router code, 704366d76): the new row is router docs
   at 39febd2a, with the engine-pins divergence (b11755) either stated or left to `pin-watch.py`.
5. C1's revision token is not tameshi's: 40 hex here, 7-40 there
   (`receipt-revision-gate.py:43`).
6. C1's correction sweep: both superseded mentions stand in `SCORECARD.md` §Round 78
   (`:4527-4528` F6 prose, `:4538` F5 tip wording; the section declares itself
   "recorded, not rewritten" at `:4510`) and a third in
   `corpus/lessons/round-78-verifier-spotcheck.md:33` (outside the allow-list). Per
   `PROTOCOL.md:365-366` plus `:133-136`, the erratum must *name* the scorecard lines as
   superseded and leave the spot-check as filed history — state which, or the sweep clause
   reads as unmet.
7. C2's registry row is not §Gate-standard conformant (`PROTOCOL.md:398-404` eight fields vs
   `kama-shokunin/SKILL.md:303` five columns); claim only the plan's predicate.

## Receipts

All read-only, run from `/home/vgpnk/Projects/shokunin`; full table in
`.ufo/waves/round-79/w1/CN01Connector/overlap.md` §Receipts.

| Command | Exit | Observed |
|---|---|---|
| `git -C kama-shokunin rev-parse master` | 0 | `f7442dea53bd8f474293a2252437b5d869801f49` |
| `grep -n "REV_RE = re.compile" tameshi-shokunin/tools/receipt-revision-gate.py` | 0 | `43:REV_RE = re.compile(r'\brev=([0-9a-f]{7,40})\b')` |
| `grep -n "PREFLIGHT=" chousa-shokunin/tools/lane-preflight.py` | 0 | contract at `:9`, print at `:327` |
| `grep -n "^| Name | Kind / entry command | Exit map" kama-shokunin/SKILL.md` | 0 | `303:` five-column header |
| `grep -n "^| name | kind | entry" mori-shokunin/SKILL.md` | 0 | `162:` eight-cell header |
| `grep -n "127.0.0.1:1234" kengaku-shokunin/corpus/knowledge/served-endpoint-identity-pin.md` | 0 | `35:` router row |
| `grep -n "S479" kama-shokunin/corpus/SOURCES.md` | 0 | `232:` router listing code @ 704366d76 |
| `grep -rn "39febd2a" kama-shokunin/registry kama-shokunin/corpus` | 1 | no match |
| `grep -n "llama.cpp" kama-shokunin/registry/engine-pins.tsv` | 0 | `4:… b11755  S038` |
| `grep -rln "class_missing" . --include=*.py --include=*.mjs --include=*.sh` | 0 | kama's own build spec only |
| `grep -rln "old=[^ ]* *new=.*at="` (non-`.ufo/`, non-kama) | 1 | no match |
| `git show ee53f1a2:tools/pre-report-gate.py` arm census | 0 | 5 specs `:214` + 4 `:223-224` = 9 arms |
| `grep -n "Row fields: name" PROTOCOL.md` | 0 | `401:` eight-field registry schema |
| `grep -n "does not execute a sibling" PROTOCOL.md` | 0 | `416:` integrator clause |
| `grep -n "both in the lesson" kama-shokunin/SCORECARD.md` | 0 | `4528:` F6 prose |
| `grep -n "rev=22cce544" kama-shokunin/SCORECARD.md` | 0 | `4538:` F5 wording |
| `grep -n "22cce544" kama-shokunin/corpus/lessons/round-78-verifier-spotcheck.md` | 0 | `33:` third mention, outside allow-list |
| `grep -n "| harm-matrix |" kumitate-shokunin/SKILL.md` | 0 | `640:` |
| `grep -n "| routed-ledger |" kumitate-shokunin/SKILL.md` | 0 | `639:` |


No clone, fixture or lane tool was run; `$S=/fast/scratch/hyaku/kama-r79/CN01Connector`
existed only for `TMPDIR` and was removed before yield.
