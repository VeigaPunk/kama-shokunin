VERDICT: confirm — 82/95-refusal counts, spawned75 header/rows and the label-distinct prose method all reproduce exactly on the raw inputs; no numeric job-cap-100 confusion exists; residual parser hazards are latent and unexercised by the named inputs.

# Round 18 FALSIFY — ProvenanceRefusal (leaf reviewer)

Target: `.ufo/waves/round-18/dispatch-provenance.py` (integrated) as delivered at lane master
`1c325b2e58fcfdc6761f645b44cedfb1d65243e6`. Attack scope: round-17 82-refusal and round-18
95-refusal raw inputs, spawned75 header/rows, mixed/duplicate labels, count method, and the
"never numeric job-cap100 as refusal count" requirement.

Environment: separate clone only — `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin
/tmp/kama-r18-falsify-ProvenanceRefusal && git -C <clone> switch -q -c seat/ProvenanceRefusal
1c325b2e…`. All commands below ran inside that clone with `cwd` = clone root. No ports opened,
no listeners, no background processes (short-lived `python3` invocations only); nothing copied
back except this report. No installs (stdlib python3 only). Scratch (clone + ledger temp files)
removed before finish.

## Script identity

- Integrated == delivered: sha256 `93705f17a2b2dfeab1e80c886bcb53ae5a8e43b0c6e86e91b73a65ad5c1ea72f`
  for both `.ufo/waves/round-18/dispatch-provenance.py` and
  `.ufo/waves/round-18/build/out/C2Provenance-2/dispatch-provenance.py` (`diff -q` empty).
- Frozen round-17 copy == round-17 working copy: sha256 `11ebb2c02f4c9160a4f20fba8d107b14be648ce6a3b1722dbbd112961b8d96df`
  for `.ufo/waves/round-18/frozen/round-17_dispatch-provenance.py` and
  `.ufo/waves/round-17/dispatch-provenance.py`.

## Raw-input hashes

| Input | sha256 |
|---|---|
| `.ufo/waves/round-17/build/refused-result-1.json` | `7167991932f619a6b805346338799bf6500d0a86387269e95b4c09e208041a5c` |
| `.ufo/waves/round-18/build/refused-result-1.json` | `83533c134a04ddab64771a02e3b7e41ab2fc89740dbc57ff219609e6e664d6cf` |
| `.ufo/waves/round-18/build/spawn-result.json` | `cb0e2b10223606ffaf1f4287a6304a0b320c8d361b3b1af202d2ceffc48f4898` |
| `.ufo/waves/round-18/build/dispatch-95.json` | `59ec84c1fa30c392f8de8b27277550dcad15d006585b4462086e479b92b36744` |
| `.ufo/waves/round-18/build/dispatch.json` | `470ae3ad6fd13e6142cf45143a34c9d99581ea339c606aa23756513c857434e4` |

## Claim verification (executed, clone)

1. **Round-17 82-refusal input.** `parse_attempt_result` on the raw bytes:
   `refused=82 spawned=0 method=None`; independent recount: 82 regex occurrences, 82 distinct
   labels, zero duplicate labels; the 82 `KamaR17.*` labels are exactly the 82 task labels of
   `.ufo/waves/round-17/build/dispatch.json` under the `KamaR17.` prefix (set equality after
   prefix strip). All 82 messages carry cap `(100)` — count is 82, never 100.
2. **Round-18 95-refusal input.** `refused=95 spawned=0`; 95 occurrences, 95 distinct, no
   duplicates; prefix-stripped set equals the 95 task labels of `dispatch-95.json`.
   `build/attempts.json` independently records `result: "refused", refused: 95, spawned: 0`
   at `19:55:45Z`.
3. **Frozen 0 → repaired 82 (M5).** Importing `.ufo/waves/round-18/frozen/round-17_dispatch-provenance.py`
   and calling `parse_attempt_result` on the same round-17 input returns
   `{'refused': 0, 'spawned': 0, 'spawned_method': None, 'spawned_methods': {}}` — the frozen
   prose-blind defect reproduces; the integrated script returns 82 on identical bytes.
   Builder advice `build/advice/C2Provenance.md:32` claims the same transition.
4. **spawned75 header/rows.** On `build/spawn-result.json` (at `2026-10-20T20:59:22Z`, matching
   the lesson's "20:59Z" dispatch): exactly one `Spawned 75 background agents` header;
   decoded-text member bullets 75, all distinct; `omp_progress_members`=75 and
   `omp_progress_pending`=75; resolved `spawned=75` via `omp_text_spawned_header` (documented
   precedence), `refused=0`, and no `Background job limit` text anywhere in the file.
   `dispatch.json` has exactly 75 tasks, no duplicate labels.
5. **taskCall digests.** Canonical sha256 (the script's single formula) of `dispatch.json`
   `taskCall` = `validation.json:taskCall_sha256` (`7390f6cbfa63a4f5…`), and of
   `dispatch-95.json` = `validation-95.json` (`fe887fc466de6d74…`). Receipt digests are honest.
6. **CLI end-to-end.** Three `--attempt-result … --label refused --out .scratch/ledger-*.json`
   runs exited 0 and recorded: r17ref `refused:82 spawned:0`, r18ref `refused:95 spawned:0`,
   r18spawn `refused:0 spawned:75 via omp_text_spawned_header`; result hashes match the input
   table above (`71679919…`, `83533c13…`, `cb0e2b10…`).
7. **Selftest.** `python3 .ufo/waves/round-18/dispatch-provenance.py --selftest` in the clone:
   exit 0, `selftest: 30/30 checks passed`; committed `runs/provenance-selftest.stdout` sha256
   `99118ced…` matches `runs/commands.json` `stdout_sha256`. The selftest's refused fixture
   (`dispatch-provenance.py:762-771`) uses duplicate `Seat-0/1/0` labels → 2 and cap `(100)`
   text → count 2, i.e. duplicate collapse and cap non-confusion are pinned by a check.

## Job-cap-100 non-confusion (targeted probes)

All 82+95 real refusal messages end `Background job limit reached (100)`; the regex
`REFUSED_TASK_RE` (`dispatch-provenance.py:178-179`) consumes `\(\d+\)` and captures only the
label. Crafted worst case: one label repeated 100× with `(100)` → `refused=1`. Mixed
refusal+spawn text (`…limit reached (100).\nSpawned 3 background agents…`) → refused and
spawned counted from disjoint evidence. No path returns 100 for a 95-refusal payload.

## Findings (latent; none exercised by the three named inputs)

- **LOW — prose false positive.** Guidance text counts as a refusal:
  `{"text": "Reminder: if a launch fails with: Background job limit reached (100), retry later."}`
  → `refused=1` (label "if a launch fails with"). Any result that *quotes or describes* the
  message inflates the refusal count. Real inputs are genuine per-task enumerations, so
  recorded 82/95 stand.
- **LOW — colon-in-label collapse (undercount).**
  `"TeamA: ops: Background job limit reached (100); TeamB: ops: Background job limit reached (100)"`
  → `refused=1`: the regex captures the last `[^;:\n]+` segment before the phrase, so distinct
  tasks sharing a post-colon segment dedupe into one label. Real OMP labels
  (`KamaR18.C1Controls`) contain no colon; the committed 82/95 are unaffected.
- **LOW — case-sensitivity.** Lowercase `background job limit reached (100)` → `refused=0`.
  A casing change in the OMP message would silently fall back to the legacy tally (0 on
  prose-only results).
- **LOW — non-`text` keys invisible when JSON parseable.** Refusal text under an `"error"` key
  → `refused=0`: `_iter_texts` reads only `text` keys and the raw-text fallback applies only
  when the file is unparseable (`parse_attempt_result`, `dispatch-provenance.py:484-502`).
- **LOW — stale/quoted spawn header cross-talk.**
  `"SeatC: Background job limit reached (100). Previous run: Spawned 75 background agents."`
  → `refused=1, spawned=75 via omp_text_spawned_header`: a quoted or stale header inside an
  all-refused result records spawned seats that never spawned. `spawned_methods` keeps only
  header evidence here, so the distortion is not self-revealing.
- **INFO — docstring literal claim inaccurate.** `dispatch-provenance.py:165-168` asserts the
  build wave's L1-recorded `validation.json` "uses this same literal" as `CANONICALIZATION`
  (`json.dumps(taskCall, sort_keys=True, …)`), but committed `build/validation.json:11` and
  `build/validation-95.json:11` record the short descriptive literal
  `"json sort_keys, separators (',',':'), ensure_ascii=False, utf-8"`. Semantically equivalent
  canonicalization (digest cross-check in claim 5 passes); the docstring's byte-level claim is
  false as written.
- **INFO — case-distinct labels counted separately** (`seatf` vs `SeatF` → 2): defensible for
  case-sensitive OMP ids; noted for completeness. Whitespace-only labels are correctly dropped
  (`" : Background …; Real: Background …"` → 1).

## Residual risk and verification gaps

- The method's correctness claim holds for the observed OMP text shape only; the LOW findings
  bound it there. A mutant weakening any of these behaviors would still pass the 30-check
  selftest (no fixture covers prose quotes, colon labels, casing, non-text keys, or stale
  headers) — they are fresh-attack territory, separate from the named round-17 denominator.
- Spawn bullets carry agent ids (`KamaR18.C1LiveTool-2`) while dispatch tasks are labeled
  `C1LiveTool`; I verified count agreement (75=75=75=75) and prefix/suffix shape, not a 1:1
  identity mapping bullet↔task — the tool itself never cross-checks identity.
- `runs/commands.json` retains no per-input attempt invocation for the three raw files (only
  the selftest); my CLI reproductions above supply that gap for this wave.
- Validator/`node` child behavior, capacity-check cadence and role mix are outside this seat's
  scope (L1/GateInternalFault et al.).
