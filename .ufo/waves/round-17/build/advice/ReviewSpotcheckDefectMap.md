VERDICT: partial — every routed defect has a round-17 owner except defect 2's appended note, defect 1(c)'s 0→79 demonstration, and defect 4's S036-cell / 319–320 halves, which the plan leaves unowned or mis-specified.

## Scope and method

Read-only. I read `corpus/lessons/round-16-verifier-spotcheck.md` (189 lines), `corpus/lessons/round-16.md`, the round-17 spec (`build/spec.json`, 82 items), `build/make_spec.py`, `build/validation.json`, `build/attempts.json`, `build/dispatch.json`, the landed `build/drafts/` and `build/advice/` files, and the frozen manifest. I ran no lane gate, probe, `measure.py`, `mutants.py`, `controls.py`, `check.py` or `check-receipt.py`, started no server and bound no port. Lane tip `cff9e62`. Frozen copies still equal the working tree for all four target files — `tests/probe-verdicts/check.py` sha256 `b853576e…`, `tools/kama-probe.sh` `36b64978…`, `tools/kama-llamacpp-live.py` `b8c5e8d4…`, `tests/llamacpp-live/check-receipt.py` `6b9576a1…` — so none of the four has been changed yet at the time of reading. The wave was still landing advice files; re-check citations below against the integrated tree.

Quote discipline: every quote in this report is ≤25 words. `[INFERENCE]` marks anything not directly observed.

## Coverage matrix

| Routed item | Round-17 action (owner artifact) | How the fix can be shown able to fail | Status |
|---|---|---|---|
| **D1a** policy identity in every validation; falsify `validation.json` (`spotcheck:182`) | `ProvenanceV2` → `.ufo/waves/round-17/dispatch-provenance.py` `--write-validation` (`make_spec.py:120-124`) | `--selftest` fixture: policy note `hyaku campaign policy v2` → `"v2"`; absent note → `null`; policy bytes hash recorded. No detector rejects a validation file that omits the block | **partial** — recorder, not detector; falsify wave not planned in this spec |
| **D1b** one `taskCall` canonicalization (`spotcheck:182`) | same item, part (b) | Recompute a known digest both ways. I did: this wave's `build/dispatch.json` `.taskCall` → `70e994a0…` with `ensure_ascii=False` (recorded `validation.json:18`); round-16 build `cdf02ba7…` reproduces **only** with `ensure_ascii=True` | **covered** (verified) |
| **D1c** count async `pending` spawns, `spawned:0` for 79 (`spotcheck:182`) | same item, part (c); `ScoutR16DispatchProvenanceBug` | Run `--attempt-result` on `.ufo/waves/round-16/falsify/spawn-result.json`; new tool must print 79 where the round-16 ledger printed 0 | **gap** — no item may run it; see F2 |
| **D2a** correct `verdict_first_lines` by an appended note (`spotcheck:183`) | none directly; only `ScribeLessonDefects` drafts dispositions (`make_spec.py:243`) | Note exists with both numbers (36/41/2 recorded, first-line truth) | **gap** — no owner artifact; the round-16 receipt stays wrong; see F3 |
| **D2b** enforce `VERDICT` first line or report non-conformant (`spotcheck:183`) | `VerdictCounter` → `.ufo/waves/round-17/count-verdicts.py` (`make_spec.py:116-118`) + contract line in every item | Run on `.ufo/waves/round-16/falsify/advice`: must list the 5 nonconformant files | **covered but mis-specified** — the prompt's expected totals cannot come from its own rule; see F1 |
| **D3** append-only SOURCES / S041 (`spotcheck:184`) | `SourcesAppendOnly` → `tools/sources-append-only.py` (`make_spec.py:110-112`); `RevengerS041Edit`; `ReviewSourcesHistoryRule2`; KQ22 draft | Item explicitly allows `--from b8e485c --to ccc4bb3` (must exit 1, flag S041) and `--from ccc4bb3 --to master` (exit 0) | **covered** — the only routed defect with an assigned, permitted before/after |
| **D4a** narrow "every non-frontend path", exclude OPTIONS (`spotcheck:185`) | `ScribeOptionsCorrections` (`make_spec.py:242`), `ScoutOptionsWording` | Append corrections, then a grep gate over lane docs returns no uncorrected statement. No such gate is planned | **partial** — drafts A–D cover the four docs; S036 cell omitted from the prompt; see F4 |
| **D4b** cite/quote 319–320 alongside 318 (`spotcheck:185`, nit `:144`) | same drafts (Appends A–E cite `:319-320`) | The subject cell `corpus/lessons/round-16.md:46` is an old lesson and cannot be edited; a round-17 note must carry it | **partial** — no artifact is assigned the lesson-level correction; see F4 |
| **D5** install disclosure (`spotcheck:186`) + nits `:122`,`:123` | `ScribeInstallDisclosure` (`make_spec.py:244`), `ScoutInstallFootprint` | Pasted `command -v -a llama-server`, `ls -l /usr/bin/llama-server`, archive sha256 — a fact check, not a predicate | **draft-only** — adoption into the fleet report/L0 is outside lane writes; see F6 |
| **D6a** five `check.py` mutants survive (`spotcheck:187`) | `C1HarnessGrading` (`make_spec.py:45`), `MutBaselineCheckPy` (before), `C1MutantRunner` (`:64-66`), `C1FaultControls` (`:56-58`) | `mutants.py --check FROZEN --detector pair` must reproduce 5 survivors; `--check CURRENT --detector full` must kill them | **covered** with two risks: confounded detector, `site_missing`; see F7 |
| **D6b** `served_model` ungraded; no route-match (`spotcheck:187`) | `C1HarnessGrading` items 1–2; `ProbeServedModel` independent evidence; `CriticC1Invariants` attacks circularity | F5 forged `served_model`, F6 route skip, M6/M7 mutants | **covered** |
| **D6c** live checks weak/unconsumed (`spotcheck:187`) | `C2LiveTool` (`:70-72`), `C2ReceiptGate` (`:83-85`), `C2Controls` (`:89-91`), `MutBaselineReceiptGate` (before) | K1 health-degraded, K3 self-exit, K4 SIGKILL, K5 rc 1, K2 non-exact loading must be rejected; gate keeps 26 v1 + `>=10` v2 mutations | **covered** |
| **D6d** exception in `finally`/teardown escapes (`spotcheck:187`) | `C2LiveTool` internal faults; `C2Controls` K6 monkeypatched teardown raise | K6 must produce a receipt and exit 2, never an escaped traceback | **covered** |
| **D6e** M3 hang design remains open (`spotcheck:187`) | `ScoutPythonServerShutdown` grounds the docs; `C1FaultControls` F7 exercises check.py's 30 s backstop (`check.py:50`) | F7 must be recorded as a failed row, not a hang | **partial** — no item closes the design gap; the plan does not say it is carried; see F8 |
| **D6f** M7 session-store traversal (`spotcheck:187`) | Contract clause with exact exclusions in the shared context (`make_spec.py:27`) | None mechanical; lesson says none exists (`round-16.md:170`) | **covered as prescribed**, residual risk only |

## Findings, by severity

### F1 (high) — `VerdictCounter`'s expected totals contradict its own counting rule

The item says to "read the first non-empty line" (`make_spec.py:118`, item `VerdictCounter`) and separately asserts "expected 36/43/0 + 5 nonconformant" (same line). Those cannot both hold: 36+43+5 = 84 > 79 seats.

I counted round-16 falsify `*.md` (excluding `swarm-registry*`) with the item's rule. Result: **34 confirm / 40 partial / 0 refute / 5 nonconformant** = 79. The 5 are files whose first line is a `# Title` and whose `VERDICT:` sits on **line 3**, e.g. `.ufo/waves/round-16/falsify/advice/ConnectSiblingCollision.md:3` — "VERDICT: partial — untracked fleet-root files naming kama/round-16" — and `ScribeReportWaves.md:3` — "VERDICT: confirm — build-wave accounting". Scanning past line 1 is exactly what reproduces 34+2 / 40+3 = **36/43/0**, i.e. the outside check's number is a body-scan, not a first-line count.

Consequence: a seat that "reconciles" its tool to the advertised 36/43/0 must scan away from line 1, which deletes the detector for the very class defect 2 names ("5/79 deviated"). The tool then reports `nonconformant: 0` on the wave it is meant to police. Fix before integration: change the expectation to `34/40/0 + 5` for falsify (or state both rules explicitly), and add a `--selftest` fixture with a heading-then-VERDICT file required to classify `nonconformant` — the item currently requires no selftest at all (the C1/C2 tools at least require `--dry-run`, `--list` or `--selftest`).

### F2 (high) — defect 1(c)'s fail-capable demonstration is unassigned, and this wave's own ledger repeats the bug

`ProvenanceV2` acceptance limits the seat to `py_compile`/`--selftest`/`--help`, and the item says "Do NOT run it against a real spec (L1 does)" (`make_spec.py:124`). The single real input that proves the counting fix is not a spec — it is `.ufo/waves/round-16/falsify/spawn-result.json`, whose payload is text-only: `"text": "Spawned 79 background agents …"` (line 4). The round-16 tally could not see it because `tally_counts` only adds int keys or per-member status strings — "Anything else contributes nothing" (`.ufo/waves/round-16/dispatch-provenance.py:159-160`, code at `:162-176`) — hence the ledger entry `"spawned": 0` for label `spawned`. No item, and no L1 acceptance line, requires the new tool to be run on that file and the 0 → 79 contrast recorded.

Worse, the round-17 build ledger already shows the shape the tool is supposed to count: `.ufo/waves/round-17/build/attempts.json:30-35` records the successful task call as `"refused": 0` plus a `result_head` beginning `Spawned 82 background agents` — **no `spawned` field at all**. The first attempt (`:2-9`) does have `spawned: 0`. So defect 1(c) recurs in this very wave's ledger unless L1 runs the new tool and records the count; the plan does not say it will.

Recommendation: L1 runs `dispatch-provenance.py --attempt-result .ufo/waves/round-16/falsify/spawn-result.json` (fixture, not a spec) and pastes `spawned` / method into the lesson, then writes this wave's attempt count from `attempts.json`'s result text or from the tool.

### F3 (medium) — defect 2's appended note has no owner, and the round-16 summary remains wrong

The defect says: "Correct `verdict_first_lines` by an appended note: 36/41/2 recorded vs 36/43/0 committed" (`spotcheck:183`). The recorded value is still in the tree — `.ufo/waves/round-16/falsify/completion-summary.json:22-26`: `"confirm": 36, "partial": 41, "refute": 2`. But the contract forbids editing old receipts/lessons, so the note cannot go there. The only planned vehicles are `ScribeLessonDefects` (drafts dispositions 1-6) and `ScribeLogEntry`; neither prompt names the recorded-vs-committed numbers, and neither is checked. Combined with F1, the disposition could be written with the wrong numbers.

Recommendation: require the round-17 lesson disposition for defect 2 to carry all three figures with their rules — recorded 36/41/2; first-line-conformant 34/40/0 + 5 nonconformant; body-scan 36/43/0 — and quote `completion-summary.json:22-26`.

### F4 (medium) — defect 4's named targets omit the S036 cell, and the 319–320 nit has no writable owner

The defect names two subjects: "Narrow "every non-frontend path" (corpus README §Round-16 row, S036 cell)" and "Quote or cite 319–320 for type and code alongside 318" (`spotcheck:185`). `ScribeOptionsCorrections` names four targets — README, `endpoint-identity.md`, `runtime-health-surface-matrix.md`, `SKILL.md` (`make_spec.py:242`) — **not** `corpus/SOURCES.md:48`. The landed seat noticed and added it as "E (extra, not in the four named targets)" (`.ufo/waves/round-17/build/drafts/options-corrections.md:48`; advice line 19), so the prompt itself is the omission.

The 319–320 nit's subject is `.ufo/waves/round-16`'s Gate cell at `corpus/lessons/round-16.md:46`, which reads "body literal at 318-320" while quoting only 318. That file is an old lesson and off-limits to writes; no item assigns a round-17 note to carry the 319–320 correction. The landed drafts do cite ":319-320" in Appends A–E, which repairs the substance in writable files, but nothing records that the old lesson cell stays as-is — the round-16 lesson's own correction convention (appended notes) is the precedent to follow.

Integration hazard: defect 4 says "Append the corrections", but the SOURCES cell must **not** be edited in place or the new defect-3 guard will exit 1 at round end. The draft says this explicitly at line 48; L1 must keep that distinction when integrating.

One further unowned statement: `tools/kama-probe.sh:423` — "# is_ready is false every non-frontend path returns 503 with the exact envelope". No item names `tools/kama-probe.sh` as an owned write target (I checked all 82 `Own ONLY` lines). The landed advice asserts "Owned by another seat" (`.ufo/waves/round-17/build/advice/ScribeOptionsCorrections.md:22`), which is false. Editing it would also change the after-probe digest that C1's pair detector pins, so the correct disposition is an explicit deferral in the lesson — not an edit.

Positive note: the OPTIONS correction for S036 already exists as a committed file-end note, `corpus/SOURCES.md:135` — "S036: "every non-frontend path" excludes `OPTIONS`". It does not carry 319–320. Adding a second note should be a deliberate superseding/append decision, not duplication.

### F5 (medium) — defect 1(a) has a recorder but no detector; the new schema is narrower than the file it will overwrite

`--write-validation` records the policy block, and this wave's hand-written `build/validation.json:38-59` already carries `policy{path, sha256, version:"v2", band}` plus the canonicalization string. But nothing in the plan fails if a future wave ships a `validation.json` with no policy block — which is precisely the round-16 defect (falsify has no file; build had none). A `--check-validation PATH` mode (exit 1 on missing `policy`, `canonicalization`, `recorded_at`, or a `taskCall_sha256` that does not recompute from the retained `dispatch.json` → `.taskCall`) would make the remedy fail-capable. No such item exists.

Also: the tool's specified output keys are `{argv, cwd, env_bindings, exit, stdout_sha256, taskCall_sha256, canonicalization, counts, policy, recorded_at}`. The current `build/validation.json` additionally carries `stdout_file`, `role_mix`, `tasks_with_model_key`, and a `note` (lines 16, 25-37, 61). If L1 regenerates the file with the new tool as the prompt says ("L1 does"), those fields disappear — including `tasks_with_model_key`, one of the facts the round-16 spot-check used. Require the tool to preserve/emit them or have L1 merge explicitly.

### F6 (low) — defect 5's disclosure is draft-only and cannot be verified in-lane

`ScribeInstallDisclosure` drafts both required facts — the retained archive `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` and "no `/usr/bin/llama-server` exists so the PATH link shadows nothing" (`make_spec.py:244`); the landed draft also has the L0 follow-up line. That covers nits `spotcheck:122-123` exactly. The L0 question is fleet-owned (`spotcheck:186` cites `.ufo/l0-questions.md`), and the lane contract forbids writing the fleet root, so no lane item can make the correction land. That is an honest boundary, but the plan should name the consumer (L1's report paragraph / fleet L0 edit) as the integration point, or the draft dies in `build/drafts/`.

### F7 (low) — C1's before/after changes the gate *and* the detector, and the mutant sites are not pinned

The claim's counting command is asymmetric: before = frozen `check.py` + `pair`; after = current `check.py` + `pair` + fault controls (`make_spec.py:64-66`). `ReviewMeasureDesignC1` is assigned the confound question, and `mutants.py` supports both detectors, so the 2×2 is computable — but no acceptance line requires it. Without `frozen-under-full` and `current-under-pair`, "5 survivors → 0" cannot distinguish gate hardening from detector enrichment.

Second risk: `mutants.py` edits by exact source string and reports `site_missing` rather than skipping. `C1HarnessGrading` rewrites the `passed = (...)` expression to add `served_model_ok` and `route_ok`; if it reformats the reason/exit/drift lines, M1–M3 sites vanish and the "after" count silently shrinks. The dry-run on the current file is only "allowed", not required. Require L1 to report `applicable` alongside `killed/survived`, and to treat `applicable < 5` (or `< 8` with M6/M7) as a failed measurement.

### F8 (low) — M3 and the unlimited debt list are not dispositioned

The plan tests the *backstop* for M3 (`C1FaultControls` F7; `check.py:50` `PROBE_TIMEOUT = 30`; `:320` records a timeout failure) and grounds the docs (`ScoutPythonServerShutdown`), but no item addresses the design gap. The round-16 lesson's own correction is explicit: "M3 stays open as a harness design gap" (`round-16.md:174`). That is acceptable, but the round-17 lesson must say it is carried, not closed.

Similarly, `spotcheck:187` summarizes only part of `round-16.md` §Kept as debt (`:151-163`). Unlisted and unowned: matrix `why` citations using frozen numbering (+36/+43); the `EnvelopeShapes.CodeAsString` / `Overbroad503.code-string` duplicate equivalence class; `ReadyControls` substring/id semantics; and "the frozen manifest lacks a prior-exposure field" (`round-16.md:163`). The first two are legitimately deferred by the byte-identical matrix constraint, but the plan never records that deferral — and the round-17 frozen manifest (`build/../frozen/manifest.json`, keys `captured_by`, `files`, `schema`, `source_commit`) still has no prior-exposure field.

## Nit map

| Nit | Owner | Demonstration |
|---|---|---|
| `spotcheck:122` PATH shadows nothing | `ScribeInstallDisclosure` (explicit in prompt) | `command -v -a llama-server`, `ls -l /usr/bin/llama-server` pasted; draft present |
| `spotcheck:123` retained tarball unnamed | same | archive path + sha256 `753bfa73…` in draft; L0 follow-up line drafted |
| `spotcheck:131` OPTIONS bypasses gate | `ScribeOptionsCorrections` + `ScoutOptionsWording`; already noted at `SOURCES.md:135` | pinned source `server-http.cpp:347-352`; Appends A–D |
| `spotcheck:144` S036 Gate cell quotes only 318 | **none writable** — target `round-16.md:46` is an old lesson | drafts cite `:319-320`; round-17 lesson must carry the note (not assigned) |

## Residual risk and verification gaps

- I did not execute any gate or measurement, so every "must fail/must pass" above is a design claim, not observed behaviour.
- The wave was in flight: the landed drafts/advice I cite (`options-corrections.md`, `ScribeOptionsCorrections.md`, `install-disclosure.md`) may be revised before L1 integrates; the `ScoutOptionsWording` report had not landed at read time, so the phrase sweep completeness is the scribe's four+two list, which my own grep confirmed.
- Advice files are untrusted inputs to integration; nothing here admits, judges or integrates them.
- `[INFERENCE]` The round-17 falsify wave will reuse `ProvenanceV2 --write-validation`; the spec I reviewed covers the build wave only, so defect 1(a)'s "give falsify a validation.json" cannot be demonstrated until that wave is planned.
- `[INFERENCE]` `attempts.json` is written by the orchestrator/driver, not by lane code (no lane file references it); the fix therefore depends on L1 running the new tool over the driver's result, not on the driver changing.

## Installs

None. No tool installed or updated; no package manager invoked. No ports bound, no servers started, no scratch left behind.
