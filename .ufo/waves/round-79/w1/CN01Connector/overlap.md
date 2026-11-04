# CN01 — sibling-overlap scan, kama round 79 (connector)

Seat `CN01Connector`, wave `round-79/w1`. Read-only scan of the fleet's sibling trees
against the three frozen claims in `plans/round-79-claims.md`. Nothing outside this seat
directory was written; no tenant of another lane was modified, cloned or executed.

Lane state observed (read-only): `git -C kama-shokunin rev-parse master` →
`f7442dea53bd8f474293a2252437b5d869801f49` (the lane has moved past the round base
`ee53f1a2…` while seats run). Base evidence below is read from
`git show ee53f1a25eab93a8ab55bbb877e49e2e731df535:…`, never from the moving worktree.
Sealed revision `7a3cd98243b69fcbee0cc9e31878782bd8459320` resolves (`git cat-file -e`, rc 0).

Claim vocabulary used here is the plan's: C1 calibration (self-record facts re-derive or are
answered by one dated value-bound correction), C2 operability (gate composes three round-78
instruments as arm 10), C3 coverage (unregistered serving listener as its own census class).

---

## C1 — calibration: six round-78 facts re-derive at the sealed revision

Adjacent sibling ground is *claim-vs-tree auditing* and *revision-token binding*. Four lanes
hold a mechanism in that family; none holds the object C1 grades (a record's own declared
facts at a sealed revision, graded against a correction container).

| Sibling | Adjacent mechanism | Evidence | Does C1 take it? |
|---|---|---|---|
| chousa | claim text vs committed files: seven rule classes, ten selftest cases, frozen v1 bytes; separate claims/context digest checker with `CLAIMS_NONEMPTY`/`CONTEXT_DIGEST`/`DIGEST_STRAY` | `chousa-shokunin/tools/claims-audit-v2.py:1-12` (rule classes, `--selftest` ten cases, `--selftest-fault`); registry row `chousa-shokunin/SKILL.md:156`; `chousa-shokunin/tools/freeze-check.py` row at `chousa-shokunin/SKILL.md:151` | No. chousa audits a *claims file* against an audit TSV of rules and a source tree it names; it has no fact table, no `old=/new=/at=/date=` block grammar, and no sealed-revision record reading. No shared module, rule file, or output line. |
| kengaku | `sha256 <hex>` claims in `corpus/SOURCES.md` must resolve to the capture *the row itself names* (round-39 fix of a global-set membership hole) | `kengaku-shokunin/plans/anchor_digest_check.py:1-12` | No, but this is the nearest *semantic* twin of **F2** (`skill:a50f6f74/1736, province:6b8c604f/331`). kengaku binds a digest token to evidence paths under its own `corpus/evidence/`; F2 derives a blob sha prefix and a newline count from `git show <sealed>:path`. Different source of truth, different grammar, different lane. |
| tameshi | receipt `rev=` token must resolve and equal the certified revision; named refusals for ambiguous/unresolvable/mismatched revisions; 19 literal selftest cases | `tameshi-shokunin/tools/receipt-revision-gate.py:25-31` (code list), `:43` (`REV_RE = re.compile(r'\brev=([0-9a-f]{7,40})\b')`), `tameshi-shokunin/SKILL.md:1547` | No, and the grammars differ on purpose: tameshi accepts **7-40** hex; C1's correction block requires exactly **40** hex and a 41-character `at` token answers nothing. C1 therefore re-implements a *stricter* token rule rather than reusing the fleet's revision gate. |
| tsukuroi | the `--revision <REV>` re-derivation idiom across many gates (`check-source-scope-correction.py`, `check-boot-chain.py`, `check-freshness-r17.py`), several of them literally named "correction" | `tsukuroi-shokunin/SKILL.md:1778, 1897, 1899` | No. tsukuroi's "corrections" are document-scope corrections re-derived at a revision; C1's corrections are *fact value* corrections in a lesson container. Same idiom, disjoint objects, no shared code. |
| kumitate | repeat-run stability of a frozen counter's own summary line; byte-pin registry for frozen counters (`COUNTER_PINS: CLEAN` / `DRIFT` / `FAIL-CLOSED`) | `kumitate-shokunin/scripts/counter-rerun.mjs:3-14`; `kumitate-shokunin/scripts/counter-pins.mjs:3-16`; row `kumitate-shokunin/SKILL.md:625` | No. Those instruments police a counter's *bytes* and *stability*; C1 re-derives *facts* from tree bytes. Neither reads another lane's record. |

In-lane note (not a sibling, boundary only): the plan's "unresolvable-cited-hash" class already
has a lane instrument — `kama-shokunin/tools/hexrun-census.py:6` classifies "over-long or
abbreviated runs". C1 does not reuse it, so a 41-char `at` token is refused by the counter's own
grammar, not by the hex census.

**Boundary call for the L1.** C1's novelty is the *correction container* (`corrected F<n>
old=… new=… at=<40-hex> date=<ISO>`) with `at` pinned to the sealed revision and `new`
re-derived at the tip. No sibling holds that grammar (`grep -rln "old=[^ ]* *new=.*at="` over
non-`.ufo/`, non-kama files → 0 files, rc 1). State it as lane-local, and do not cite tameshi's
gate as the mechanism: the token widths disagree.

---

## C2 — operability: the gate gains a tenth arm composing three round-78 instruments

This is the claim with the most sibling ground, because "a pre-report gate that runs other
tools' selftests" exists in three lanes under three names. The overlap is **structural pattern**,
never shared code; the sharpest finding is that the one fleet-adjacent *registry-row auditor*
cannot parse kama's registry table at all.

| Sibling | Adjacent mechanism | Evidence | Does C2 take it? |
|---|---|---|---|
| chousa | `lane-preflight.py`: one command runs the lane's committed self-checks, one `GATE <id> <name> PASS\|FAIL\|ENV` line each, then `PREFLIGHT=<passed>/<run> FAILED= ENV= SKIPPED=`, exit 0 only when at least one gate ran and all that ran passed — and it composes *instrument selftests* (freeze-check selftest, assimilate-rows selftest, research-gate selftest) as gates G01-G08 | `chousa-shokunin/tools/lane-preflight.py:5-20` (gates and summary contract), `:327` (summary print); registry row `chousa-shokunin/SKILL.md:154` | No shared code, but this is the **closest structural prior art** to arm 10. C2 must be worded "the gate composes *kama's* round-78 instruments as *its own* arm", not as a fleet-first composition. chousa's gates are `G01..G08` with an `ENV` (could-not-run) state and a skipped-gate rule; kama's arms derive from `ARM_ORDER`/`ARM_SPECS`. |
| kumitate | `round-gate.mjs` (`kumitate-round-gate-v1`): lane-local pre-check of the fleet round-close contract, `--selftest`, and an explicit disclaimer that it is "NOT a fleet report-conformance authority" | `kumitate-shokunin/scripts/round-gate.mjs:8-19`; row `kumitate-shokunin/SKILL.md:609` | No. Its object is report/SCORECARD/LOG/commit fields and index state, not instrument arms; it never executes another instrument's selftest. |
| mori | `mori-gate-registry.py`: audits **registry rows** in a SKILL.md against an eight-standard-cell table, including whether the row's tool really has a selftest argv branch; counters `registered= unregistered= no_selftest= duplicate= wrong_row=` | tool grammar `mori-shokunin/tools/mori-gate-registry.py:5-23` (eight cells, selftest detection, duplicate/wrong_row findings); counters `:42`; parser `:215` and the fail-closed `raise` at `:359`; eight-cell header `mori-shokunin/SKILL.md:162`; row `mori-shokunin/SKILL.md:184` | **No — and it cannot be borrowed.** mori's parser selects pipe tables whose header is exactly `name \| kind \| entry \| verdict map \| self-test \| pinned values \| write scope \| owner` (`:215`, `:359`). kama's gate table header is five columns: `Name \| Kind / entry command \| Exit map \| Self-test / pinned values \| Write scope` (`kama-shokunin/SKILL.md:303`). Run against kama, mori's auditor errors with "no registry table with the eight standard cells". So C2's second half (the SKILL row naming `round78-instruments` and the new tally) is graded by kama's own row discipline only; citing mori's auditor as the grader would be false. |
| souji | a tool literally named a pre-report gate: five checks (`tip`, `report`, `shonen`, `clean`, `prereg`), `check-<name>=PASS\|FAIL`, exit 1 on any FAIL, optional `--contract` predicate 6 | `souji-shokunin/tools/souji-pre-report-gate.sh:23-24` (fail counter and `check()`), `:76` (`exit "$fail"`); row `souji-shokunin/SKILL.md:256` | No. No arms, no arm count, no selftest, no instrument composition; it reads report artifacts and git refs. Name overlap only. |
| tameshi | gate selftests with literal counted cases and named refusal codes; a fixture directory per gate | `tameshi-shokunin/SKILL.md:1547` (19 literal selftest cases, `tools/fixtures/receipt-gate/`) | No. It is the precedent for "selftest cases are literal and counted", which is why C2's `pass=22 → pass=26` must come from four real cases; nothing of it is composed into kama's gate. |
| tsukuroi | `check-report-receipts.py`: revision-cited report gates must have committed receipts, `--selftest` | `tsukuroi-shokunin/tools/check-report-receipts.py:1-16` | No. Adjacent to the receipts half of the arm only; not an arm composer and not referenced by kama's gate. |

Kama base, for the non-overlap side of the ledger (read from the base revision, not the worktree):
`git show ee53f1a2:tools/pre-report-gate.py` → `ARM_SPECS` holds 5 names
(`selfdesc`, `newest-closure`, `receipt-audit`, `worktree-landing`, `round-scope`) at `:214`,
and `ARM_ORDER` appends `round-clean`, `round74-v2`, `round75-instruments`,
`round77-instruments` at `:223-224` — 9 arms, which is the plan's "Before". The registry row at
`SKILL.md:309` is the one C2 edits, and it already says "nine arms".

**Boundary call for the L1.** No sibling ships a gate arm that composes kama's instruments, and
no sibling's gate is named in kama's `SKILL.md` registry. The honest novelty sentence is:
"arm 10 is the first composition of the three round-78 instruments inside *this* lane's gate";
fleet-wide, chousa's `lane-preflight` already composes that lane's own instruments, and mori's
registry auditor already polices *its* registry rows with an incompatible grammar.

---

## C3 — coverage: an unregistered serving listener becomes a census class

The class token is unoccupied fleet-wide. The overlap that does exist is on the *source* side
(llama.cpp `/models` surface) and on the *token* side (`unregistered=` means something else in
two other lanes).

| Sibling | Adjacent ground | Evidence | Does C3 take it? |
|---|---|---|---|
| kengaku | the same live listener and the same upstream surface: a six-field served-endpoint identity pin, measured on this host, including `router http://127.0.0.1:1234` listing 5 model ids; upstream pin is llama.cpp server README @ tag **b7200** (`ab49f094…`) | `kengaku-shokunin/corpus/knowledge/served-endpoint-identity-pin.md:1` (source line S178), `:16-23` (six-field pin table), `:35` (router row); row `kengaku-shokunin/corpus/SOURCES.md:193`; index `kengaku-shokunin/corpus/README.md:584` ("a pin is host state, not a capability claim"); live-listener observation `kengaku-shokunin/SCORECARD.md:3434-3435` | No. kengaku reads the endpoint to bind an **eval identity** (what a capability number was taken under); C3 reads it to classify **governance** (does the registry declare that port). C3 asserts no loaded model and no readiness — the same line kengaku draws from the other side. Neither takes the other's object; the rule in kengaku's file is a useful quote for C3's scope ruling. |
| research tree (fleet root, not a lane) | `probe_shims.py`: discovers user systemd shim units, records unit state and whether a listener exists on `SHIM_PORT`, then cross-references each shim port to the config provider whose `base_url` points at it; writes `raw/shims.json` | `research/round-18-kimi-model-routing/census/scripts/probe_shims.py:1-14` | No. It is the closest fleet prior art for *port ↔ registry/consumer cross-reference*, but it enumerates systemd units, is a one-off census (no gate, no class column, no exit contract), and lives outside every lane's `tools/`. C3 classifies arbitrary serving listeners against a lane registry, with a two-registry negative leg. |
| tabi | loopback DevTools/fixture ports probed for teardown after each run (process discipline) | `tabi-shokunin/scripts/chrome-cdp-loopback-round59.mjs:63-64`, `:149` | No. Ports are fixture hygiene, not governance; no registry relation. |
| mado | `CHECK96: frozen= landed= added= removed= unregistered= verdict=OK\|NARROWED\|UNDECLARED` — "unregistered" counts *contract classes* absent from a frozen list | `mado-shokunin/quality/check-landed-contract.py:14` (line contract), `:88` (print) | No mechanism overlap, but a **vocabulary collision**: an `unregistered=` token with a different population. Any L1 sentence quoting both must name the population. |
| mori | `unregistered=<n>` in the registry-row counters (paths with no registry row) | `mori-shokunin/tools/mori-gate-registry.py:42` | No. Same vocabulary collision as mado, second instance. |
| kumitate | census *gates* over installation trees and waves (`kimi-census.mjs`, `omp-census.mjs`, `wave-census.mjs`) | `kumitate-shokunin/scripts/kimi-census.mjs:1-10` | No. "Census" name only; none reads sockets and none has a registry-port relation. |

Uniqueness checks (positive evidence that C3's class is not duplicated):

- `class_missing` as a token appears in **no** sibling `.py`/`.sh`/`.mjs`; the only non-wave hit
  is kama's own `.ufo/waves/round-79/build-spec.py` (in-lane, this round).
- No sibling ships an `ss -ltn` listener enumerator in `tools/` or `scripts/`: every non-kama
  `ss -ltn` hit is wave-dir scratch (`kaidoku-shokunin/.ufo/waves/round-22/`,
  `kengaku-shokunin/.ufo/waves/round-64|65/`) or `research/` (above), except
  `kengaku-shokunin/plans/round64_c1_kvstore_probe.py` and
  `kengaku-shokunin/plans/round65_c1_sqlite_probe.py` (probe fixtures for corpus claims, not
  listener governance).
- kama base confirms the missing class: `git show ee53f1a2:tools/kama-probe.sh:745,750` — the
  `listeners` JSON/plain summaries carry `probed, model_endpoints, foreign_service,
  unauthorized_service, dead, not_http, model_loading` and no `registered`/`governed` keys.

Two hazards this scan surfaces for C3's source leg (internal to kama, not sibling-owned):

1. **Three llama.cpp pins.** kengaku S178 pins the server README at **b7200** (`ab49f094…`);
   kama `registry/engine-pins.tsv:4` pins the llama.cpp line at **b11755** (`704366d76`);
   the plan's new row pins the router docs at **39febd2adb947b70da35e95f9351b3bf58ad170a**.
   `grep -rn 39febd2a kama-shokunin/registry kama-shokunin/corpus` → no match (rc 1): the new
   pin is not yet in any registry or corpus byte, so the SOURCES Gate block is the only place
   that records the divergence. If the L1 does not state it, `pin-watch.py`/`digest-ledger.py`
   will read three different llama.cpp revisions with no relation declared.
2. **The C3 surface is adjacent to kama's own S479/S037.** `corpus/SOURCES.md:232` (S479)
   already rows "llama.cpp router model listing" *code* — `server-models.cpp`,
   `get_router_models`, `context_length` — at `704366d76`; `corpus/SOURCES.md:49` (S037) rows
   router readiness semantics at the same commit. The new row must be worded as *router docs
   (`GET /models`) at a newer commit*, never as a new surface, or it reads as a re-row of an
   existing one. (This is the same shape the plan already rejects for S001/S526; kengaku's
   S178 is a third holding of the upstream README surface.)

---

## D — fleet-contract adjacency (operator/fleet root, not a lane; read-only)

The three claims are graded against kama's predicates, but four fleet-level clauses and two
kumitate mechanisms shape what the L1 may *say* about them. None of this is a lane's ground; it is
the standard every lane's row is measured against.

| Fleet artifact | What it fixes | Evidence | Consequence for round 79 |
|---|---|---|---|
| `PROTOCOL.md` §Gate standard | gate vs probe; verdict map over `clean\|failed\|could-not-evaluate`; self-test over isolated fixtures; **the registry row schema is eight fields** — "name, `gate\|probe`, entry command, verdict map (code → class), self-test command and spelling, pinned-value path, write scope, owner"; a lane's registry home is its own `SKILL.md`; the integrator verifies committed evidence and **does not execute a sibling's gate** | `PROTOCOL.md:375-416`, registry clause `:398-404` (row fields at `:401`), integrator clause `:415-416` | C2's requirement that the row live in `SKILL.md` is protocol-grounded. But kama's gate table is **five** columns (`kama-shokunin/SKILL.md:303`) against an **eight-field** schema, so mori's schema-implementing auditor (`mori-gate-registry.py:215,359`) cannot read it: do not claim §Gate-standard row conformance for the new row, only the plan's predicate (row names `round78-instruments` and the new tally). Fixing the table shape is out of C2's scope. |
| `PROTOCOL.md` §Gate standard, "Two evidences" | a verdict **names the revision it was measured against**; a gate over a mutable artifact also ships a run over a committed snapshot with its committed expected verdict | `PROTOCOL.md:390-395` | Supports C1's `at=<40-hex>` binding and the "read `git show <sealed>:…`, never the worktree" scope ruling (the round-78 F2 defect is the exact failure this clause names). C3's fixture census is the "committed snapshot" shape. |
| `PROTOCOL.md` §Evidence standard, corrections | a filed report is a record: "a correction to it lands in the correcting round's own report, or as an erratum appended after the filed bytes in a new commit and naming the text it supersedes — never a rewrite of the filed bytes"; append-only files take an appended correction entry pointing at the superseded text; a falsified claim stays on the routed-defect queue until it lands | `PROTOCOL.md:133-136`, `:366-367` | C1's container (`corpus/lessons/round-79.md` §Corrections, appended) is the lane instantiation of this form. The *block grammar* remains kama's own; the *form* is not novel and should not be claimed as such. |
| `PROTOCOL.md` "Corrections sweep every mention" | before the round's commit, grep every file the lane touches for the superseded claim — "a corrected fact left standing in a sibling file is still a defect" | `PROTOCOL.md:365-366` | Direct hit on C1: both superseded mentions stand in `SCORECARD.md` §Round 78 — F5 at `SCORECARD.md:4538` ("green at `rev=22cce544`") and F6's prose at `:4527-4528` ("the pre-correction tip run and the corrected tip run are both in the lesson"), inside the section that declares itself "recorded, not rewritten" (`:4510`). A third mention, `corpus/lessons/round-78-verifier-spotcheck.md:33`, is *not* in the round-79 allow-list and is a filed record. The disposition the L1 must state: an erratum **naming** `SCORECARD.md:4527-4538` as superseded (naming satisfies both the sweep clause and the never-rewrite clause), and the spot-check left as history with its reason. |
| kumitate `harm-matrix` | a **registry of lane gates run at BASE and at TIP** in separate sandbox clones, one row per gate with a transition (`HELD` / `REPAIRED` / `HARM` / `HARM_ABSENT` / `NEW_OK` / `NEW_RED` / `GONE` / `CARRIED`), fail-closed on a missing verdict line, signal death or timeout | `kumitate-shokunin/scripts/harm-matrix.mjs:3-16`; gate list `scripts/harm-matrix-gates.json:1-20` (includes `counter-pins-selftest`, `round-gate-selftest`, `sources-check-selftest`); row `kumitate-shokunin/SKILL.md:640` | Closest fleet mechanism to *both* the round's before/target structure *and* arm-style composition of other instruments' selftests. It takes nothing from kama and kama takes nothing from it — but a C2 sentence like "first gate to compose other instruments' selftests" is false fleet-wide; say "first in this lane". |
| kumitate `routed-ledger` | every routed defect item must have a ledger row bound by a located 3-25-word quote, and every closed row must bind its answer by `path:line` **plus a quote at that exact line** inside the root | `kumitate-shokunin/scripts/routed-ledger.mjs:3-18`; row `kumitate-shokunin/SKILL.md:639` | Adjacent to the plan's §Round-78 routed defects: the plan discharges V1-V7 "by dispositions recorded in `SCORECARD.md` §Round 79 and the round report", each naming an evidence pointer. kama has no routed-ledger file in its allow-list, so its dispositions are prose, weaker than kumitate's located-quote binding. Name the difference; do not import the ledger (out of allow-list). |

---

## Answers to the two explicit flags

**A sibling that already ships an equivalent gate arm.** None ships an arm that composes
kama's instruments, and none is registered in kama's registry. Nearest equivalents, in order of
distance: chousa `tools/lane-preflight.py` (composes that lane's own instrument selftests as
gates, `chousa-shokunin/SKILL.md:154`); kumitate `scripts/round-gate.mjs` (lane-local round
pre-check with `--selftest`, `kumitate-shokunin/SKILL.md:609`); souji
`tools/souji-pre-report-gate.sh` (five artifact checks, no arms, `souji-shokunin/SKILL.md:256`);
mori `tools/mori-gate-registry.py` (registry-row auditor, eight-cell grammar, inapplicable to
kama's five-column table, `mori-shokunin/SKILL.md:184`).

**A sibling that already ships an equivalent listener census class.** None. The unique-token
evidence is above; the nearest non-lane prior art is `research/`'s shim census, which is not a
lane gate and classifies nothing as `unregistered`.

---

## Risks to the L1 report wording

1. Do not call C2 "the first pre-report gate that composes instruments" — chousa's
   `lane-preflight` did that for chousa. Say "this lane's gate, for the first time, composes
   this lane's three round-78 instruments".
2. Do not cite `mori-gate-registry.py` as the validator of the new `SKILL.md` row; its grammar
   rejects kama's table (`mori-gate-registry.py:215, 359` vs `kama-shokunin/SKILL.md:303`).
3. Where `unregistered=` appears in a fleet-wide sentence, name the population: mado's contract
   classes (`check-landed-contract.py:14`), mori's registry rows (`mori-gate-registry.py:42`),
   kama's listeners (C3). Three meanings, one token.
4. C3's source leg needs one sentence separating it from kengaku S178 (server README, b7200,
   eval identity) and from kama S479/S037 (router code, 704366d76): the new row is router *docs*
   at 39febd2a, and the host pin divergence from `registry/engine-pins.tsv:4` (b11755) is stated
   in the Gate block or left to `pin-watch.py`.

---

## Receipts (all read-only; run from `/home/vgpnk/Projects/shokunin`)

| Command | Exit | Observed |
|---|---|---|
| `git -C kama-shokunin rev-parse master` | 0 | `f7442dea53bd8f474293a2252437b5d869801f49` |
| `git -C kama-shokunin cat-file -e 7a3cd98243b69fcbee0cc9e31878782bd8459320^{commit}` | 0 | sealed revision resolves |
| `grep -n "REV_RE = re.compile" tameshi-shokunin/tools/receipt-revision-gate.py` | 0 | `43:REV_RE = re.compile(r'\brev=([0-9a-f]{7,40})\b')` |
| `grep -n "PREFLIGHT=" chousa-shokunin/tools/lane-preflight.py` | 0 | lines 9, 12 (contract) and 327 (print) |
| `grep -n "^| Name | Kind / entry command | Exit map" kama-shokunin/SKILL.md` | 0 | first hit `303:` (five-column header); 23 such headers in the file |
| `grep -n "^| name | kind | entry" mori-shokunin/SKILL.md` | 0 | first hit `162:` (eight-cell header) |
| `grep -n "127.0.0.1:1234" kengaku-shokunin/corpus/knowledge/served-endpoint-identity-pin.md` | 0 | `35:` router row, `lfm3-server.service` |
| `grep -n "S479" kama-shokunin/corpus/SOURCES.md` | 0 | `232:` router model listing (code) @ 704366d76 |
| `grep -rn "39febd2a" kama-shokunin/registry kama-shokunin/corpus` | 1 | no match (pin absent from registry/corpus) |
| `grep -n "llama.cpp" kama-shokunin/registry/engine-pins.tsv` | 0 | `4:…b(\\d+)  b11755  S038` |
| `grep -rln "class_missing" . --include=*.py --include=*.mjs --include=*.sh` | 0 | one hit, kama's own round-79 build spec; no sibling |
| `grep -rln "old=[^ ]* *new=.*at="` over non-`.ufo/`, non-kama files | 1 | no match (correction grammar is unoccupied) |
| `git show ee53f1a2:tools/pre-report-gate.py` → `ARM_SPECS` names | 0 | 5 names at `:214`; `ARM_ORDER` +4 at `:223-224` = 9 arms |
| `git show ee53f1a2:tools/kama-probe.sh` → `grep -n "registered\|governed\|model_endpoints"` | 0 | `:745`, `:750` — summary keys without `registered`/`governed` |
| `grep -n "Row fields: name" PROTOCOL.md` | 0 | `401:` eight-field registry schema |
| `grep -n "does not execute a sibling" PROTOCOL.md` | 0 | `416:` integrator clause |
| `grep -n "^### Freeze divergences" kama-shokunin/SCORECARD.md` | 0 | `4510:` "recorded, not rewritten" |
| `grep -n "both in the lesson" kama-shokunin/SCORECARD.md` | 0 | `4528:` F6 prose (pre-correction run) |
| `grep -n "rev=22cce544" kama-shokunin/SCORECARD.md` | 0 | `4538:` F5 wording ("green at `rev=22cce544`") |
| `grep -n "22cce544" kama-shokunin/corpus/lessons/round-78-verifier-spotcheck.md` | 0 | `33:` third mention (outside allow-list); `22:` is a cited-hash list, not the tip claim |
| `grep -n "| harm-matrix |" kumitate-shokunin/SKILL.md` | 0 | `640:` gate-registry row (BASE/TIP transitions) |
| `grep -n "| routed-ledger |" kumitate-shokunin/SKILL.md` | 0 | `639:` routed-defect ledger row |


Scratch root `$S=/fast/scratch/hyaku/kama-r79/CN01Connector` was created for `TMPDIR` and
removed before yield; no clone or fixture was needed (this seat executed no git mutation and no
lane tool).

## Not checked

- Sibling rounds whose claims are in flight at scan time (their worktrees move); all evidence
  above is from committed/tracked bytes read at the moment named in the receipts.
- Any live network fetch of the three llama.cpp pins; the divergence is reported as recorded
  bytes, not re-resolved upstream.
