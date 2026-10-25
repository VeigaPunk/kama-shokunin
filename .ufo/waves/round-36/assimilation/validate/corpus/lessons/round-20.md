# Round 20 — errors are not kills; GGUF declared identity

Round 20 attempt 1. Base `37bd4c5bd456a2f8a54d3312c28495c321715856`
(branch master, clean and pushed). Round 19 admitted by the outside review at
`round-19-verifier-spotcheck.md`. Assigned axes operability 8 and calibration 7;
calibration is below saturation 8, so no stagnation waiver. Last capability was
round 16; the four-round window motivates C2, without waiving calibration.

## Declared claims

- **C1 calibration, 7 → 7:** finite named error-versus-kill regression repair.
  The grid's error children must not earn rejection credit, and the C2
  selftest-kill arm must not earn a kill from an unfinished selftest. The exact
  cells and controls are in `registry/error-injection-cells.json`; the frozen
  arm reads instrument bytes at the base revision. This is not a census or a
  universal guarantee about every historical counter. S061/S062/S064 ground
  status ambiguity and the distinction; S063 is an explicit counterexample
  to a universal mutation-testing convention.
- **C2 operability, capability acquisition, 8 → 8:** bounded offline GGUF
  header/metadata identity inspection and comparison with an existing live
  receipt, `tools/gguf-identity.py`. Sources S058/S060 ground declared training
  context versus effective per-slot context. Reference oracle: official PyPI
  `gguf==0.19.0`, independently reading the real 1,185,376-byte stories260K file
  (S039). This launches no server, loads no weights, and claims no quality or
  authenticated execution.

Separation: C1 reads grid/counter code and injected errors; C2 reads the GGUF
file and captured receipt. Neither depends on the other's changed code. Record
repairs below do not move either claim's number.

## Scope correction from build criticism

`build/advice/CritC1Wording.md` refutes an exhaustive reading of the initial
"errors are not verdicts" wording. Accepted: this round claims only the frozen
named regression set plus real-verdict controls. Gates may still fail closed
when their subject crashes (`ProbeCheckCrash.md`); that is distinct from a
mutation counter claiming it observed a targeted rejection. The entire lane's
historical kill convention is not changed. Missing git executables/documents
already give citation checker exit 2 at the base (`CitationExitFix.md`); a
nonexistent cited revision is a legitimate bad-citation verdict, not a broken
Git installation. No improvement is claimed for already-correct exit paths.

## Gate

All sources opened 2026-10-21 by named build seats and/or L1. Quotes below are
located and no longer than 25 words. Advice paths are lane-relative under
`.ufo/waves/round-20/build/advice/`.

| Candidate | Decision | URL, revision, location and quote |
|---|---|---|
| GGUF header fields declare inspectable metadata | admit S058 | https://raw.githubusercontent.com/ggml-org/ggml/da8e2a54b919557b816b1c2beb432ccb766f7ce0/docs/gguf.md §File Structure line 279: "Must be `GGUF` at the byte level: `0x47` `0x47` `0x55` `0x46`." (`SrcGgufSpec.md`) |
| Reference reader version subset is explicit | queue S059 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/gguf-py/gguf/gguf_reader.py:41: `READER_SUPPORTED_VERSIONS = [2, GGUF_VERSION]`; reader behavior, not proof every loader accepts these versions |
| Per-slot served context differs from training context | admit S060 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp:4654: "context size of a single slot, capped by --kv-unified-per-slot and by the training context of the model" (`SrcServerNctx.md`) |
| Status 1 uniquely identifies a gate failure verdict | reject; admit narrower S061 | https://docs.python.org/3.14/library/sys.html#sys.exit, Python 3.14.8 §sys.exit: "any other object is printed to stderr and results in an exit code of 1." (`SrcPySysExit.md`) |
| Failed tests and runtime errors are distinct in Stryker | admit S062, precedent only | https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/ §Runtime error; source a56f265c77c1cc811b10f0bae73ec1b0083d52a9: "The running of the tests resulted in an error (rather than a failed test)." (`SrcStrykerStates.md`) |
| All mutation tools exclude runtime errors from detected counts | reject S063 as that claim's basis | https://github.com/hcoles/pitest/blob/f7fe5adfa5fb6e727c12d2403a48f5e4e9dd2fc6/pitest/src/main/java/org/pitest/mutationtest/DetectionStatus.java:63: `RUN_ERROR(true)`; ScorePrecursor.java:34–46 filters isDetected (`SrcPitStatuses.md`) |
| A signal exit is an emitted subject verdict | reject; admit S064 signal meaning | https://docs.python.org/3.14/library/subprocess.html §CompletedProcess.returncode: "A negative value -N indicates that the child was terminated by signal N (POSIX only)." (`SrcPySubprocess.md`) |

Existing S001–S057 cells are unchanged this round. Round-19's S057 used-by
change lacked an old→new log: `corpus/lessons/round-19.md,
registry/required-citations.json` → `corpus/lessons/round-19.md, SCORECARD.md`
(`SourcesGuardR19.md`); this paragraph supplies that missing history rather
than rewriting the old lesson. New rows S058–S064 are 7 tier-A scoped sources:
5 mined, 1 queued, 1 rejected. Search question: distinguish errors from credited
kills and decode model declarations without loading weights. Screened 7 source
candidates for these rows, included 7 (one retained rejected). Other opened
build candidates (mutmut, Ollama, context-warning details) remain in advice,
not registry evidence; no row quota. Stop: both claims have primary support and
a deliberate counterexample; no broader mutation policy or model evaluation.

## Mistakes

| ID | Class | Evidence | Captured-by | Fix / fail-capable evidence |
|---|---|---|---|---|
| M1 | Error credited as targeted rejection | grid exit1 rule at base; `build/advice/MutGridRedBefore.md` (3/3 crash gates called rejected) | KQ20 failed to cover counter outcome taxonomy | C1 explicit verdict plus non-passing error class; genuine-verdict control prevents always-error laundering |
| M2 | Partial selftest credited as kill | `build/advice/SurvivorsArmEnum.md`, target FAIL literal before abort | KQ20, missing enumeration obligation | require selftest completion evidence; early-abort and completed-target-failure controls |
| M3 | Registry expanded but copied counts stale | round-19 outside routed item 2; `build/advice/StaleCountSweep.md` | KQ20 numeric provenance | appended corrections name 4 rows and measured selftest revision; no old line rewritten |
| M4 | Filed lesson line rewritten | `30ed378`, round-18 line 42; `Lesson18Line42.md` | PROTOCOL append-only correction rule | named appendix records old and superseding text; history retained |
| M5 | Non-spawned falsify wave attributed criticism | round-19 falsify 0/66; `FalsifyLabelFix.md` | disclosure rule | append corrections: critics were build seats, not outside reviewers |
| M6 | Seat outlived round and retained scratch | `evidence/r19-scratch-removal.txt`; `LessonMistakes.md` | seat cleanup rule | L1 stopped orphan strace/survivors process tree and removed authorized r19 scratch; 24:31 total elapsed, about 13 minutes after round completion, not 24 minutes after completion |
| M7 | Whole-output agreement inferred from equal survivor summaries | R19 route 7d; R18 `c2-survivors.json` versus `c2-survivors.stdout`: counts equal, full `results` unequal, tool hashes `87cad1cad4565be01ce06e7f92c578c2f449c951894a880166040c3f118dc3ac` versus `ac934794af1eee8067ea11f7f8cc31702ea7dfad257fec2649f2d638477bac75` | KQ14 content review and KQ17 verdict/count separation | R18 lesson `:474-480` limits agreement to 15 item outcomes, counts, frozen witnesses and 42 run-status tuples; R20 did not rerun the full 42-run counter. The result inequality falsifies whole-document equality. |
| M8 | S051 source range omitted a sentence and shifted after S057 | `.ufo/waves/round-20/build/out/S051AnchorShift/qualification-drafts.md:29-31`; current source text `corpus/SOURCES.md:210-215` | KQ7 append-only stale-anchor rule | R18 lesson `:447-451` appends the revision-qualified correction and stable heading; source row cells remain unchanged. |

## Recovery and author boundaries

No earlier round-20 attempt inherited. L1 learned during the build that the
source-only broad C1 description overreached; the corrected finite scope above
is explicit, not a silent change to a denominator. The remaining historical
counter leaves (`MutantsGridCrash`, `GateSelftestCrash`, `KillCensus`), symlinked
sonames and endpoint restoration remain named limits, not claimed closed.
No operator-owned config, service, routing or system package was changed.

## Execution conformance disclosures

- The reused L1 had canonical protocol/AXES/CORPUS/LEARNING loaded from its
  earlier closure, but did not complete their fresh round-20 reread (or tower
  load) before the build dispatch. The late reread found no changed rule and
  does not satisfy the prescribed start-of-round load order retrospectively.
- Main authorized r19 scratch deletion after checking references. Core
  documents and the fleet report did not cite the scratch as outcome evidence;
  historical build advice did retain `/tmp/kama-r19-*` command paths. L1 deleted
  those directories anyway after preserving the size/path receipt and stopping
  the orphan process. Thus a literal "nothing cites it" condition was not met;
  this is a cleanup conformance defect, not an assertion that no such reference
  existed. Committed outcome receipts remain intact.

- The build's proposed host-wide GGUF census is not used as the C2 population.
  `GgufHostCensus.md` cannot establish round-start filesystem state, and
  `ConnectKagi.md` discloses count-only traversal of no-enumerate roots. No
  private config contents or credential values were read, but those traversal
  probes were out of bounds. The finite capability population is the explicitly
  named pre-existing SHA-pinned stories260K file plus independent committed
  synthetic fixtures, not all models on the host. Historical receipt bodies
  remain self-report; response-header minimization is routed as existing debt,
  not quietly folded into either claim.


## Selftest-arm boundary after integration

The arm-only regression retains AO-blank's completed failure (36 passing +
6 FAIL case lines = 42) as a kill, while a same-target early abort and
1/42 + one FAIL are inconclusive. JSON completion compares the emitted
baseline case-count fields and gate/escape key sets. This stricter policy
also makes the retained FC-f6cache selftest arm inconclusive (wrapper_checks
32 versus baseline35); historical round-18 11-kill output remains evidence
about its measured code, not a promise of the new counter's full-run tally.
`SurvivorsArmEnum.md` and `arm-regression-transcript-final.txt` record this.
No full 42-run survivor measurement was rerun in round20.


## Official measurement — committed 0957ce61

Work/population landed `33a6777866d0f63d894ef21bc863486bcb35b56c`; complete
measured tree `0957ce619789d13bb5779606078fa1498114d2c7`.
`python3 .ufo/waves/round-20/run.py --recipe .ufo/waves/round-20/recipe.json
--out .ufo/waves/round-20/runs/0957ce61` exits0: **21/21** declared exits met.
`commands.json` retains argv, measured revision, raw-stream digests and exits.

- C1: `tools/error-verdict-census.py --arm frozen --json` exit1 (6 false
  classes/15); `--arm current --json` exit0 (0/15); pair exit0, frozen witness
  mismatches0, red-vector mismatches0, unrun `[]`. Synthetic emitted-verdict
  positives and genuine complete target failure remain; no all-error shortcut.
  The timeout cell uses a pinned immediate TimeoutExpired shim (not a real
  long hang); the grid's own selftest also exercises a bounded actual timeout.
- C2: `c2/measure.py --json` exit0, fixtures23/23, no mismatches/tampered/
  unavailable inputs, oracle validated, model parser actually observed.
  Base reports `capability_absent`, not a fabricated parser failure.
  Real file: GGUFv3/tensors48/KV19, llama context2048, blocks5, embedding64;
  captured meta.n_ctx_train2048, n_embd64, n_vocab512 agree. Props256/slots4
  remain informational with no division. Scope is receipt self-report.
- Citation count17/17 (4 +13 reconstructed instances), selftest24 cases;
  GGUF selftest30/30, aggregate measure selftest7/7; survivor pure checks49/49.
  Gate6 VALID +1 NOT-EVALUATED, mutations77 plus unreadable rejected. Actual
  old receipt grid0/3 without tree pin (exit1), 3/3 with pin (exit0).
- Census command `scripts/sources-census.sh validate --root
  /home/vgpnk/Projects/shokunin kama` exit0 with W04 for S031/S043/S056/S060/
  S064; `census` exit0: rows57→64, A54→61/C3, mined46→51, queued5→6,
  rejected6→7. No existing immutable source cell changed.

### Build-wave disposition

72 seats, roles scout16/reviewer13/executor12/critic6/mutation-tester2/
revenger2/sentinel2/connector6/scribe12/simplifier1; planner is L1.
First entire72 call refused, second unchanged call spawned72 after ~3 minutes.
Original70 completed/2 dead: CellDesign and SrcGateStandard (Zai 429 type1302,
retry budget exhausted after5). SrcGateStandard left an artifact; CellDesign
did not. Same-seat integration continuations were author-side; StaleCountSweep
continuation failed on Haiku429 with retry-after8231000ms, its original report
retained. No dead seat replaced. Native result/refusal, registry and accounting
are under `build/`; counts script41 confirm/27 partial/2 refute/1
format-nonconformant (KnowGguf), files71. Out-only reports copied byte-exact;
two scout finals are explicitly L1 transcriptions.

CritC1Wording's scope refute accepted. ProbeCheckCrash's refute describes
fail-closed subject-row failure, not a mutation kill and not a repaired cell.
Other partials are bounded by the delivered artifacts and limits above.
The three ordinary fixes after delivery were typed input/alias/Unicode
handling, strict error aggregate exits, and explicit survivor observation
evidence; the official results, not draft selftest labels, are authoritative.
The production aggregate runner omits the worker's redundant fixture-only
mode; original worker sources/transcripts remain versioned advice.

## Wave-2 integration corrections (appended)

- **S063 used-by, old → new:** `—` → `corpus/knowledge/error-is-not-a-verdict.md, corpus/lessons/round-20.md`. `SourceS063.md` verified both citations. Only the permitted `used-by` cell changed; S063 remains a rejected counterexample to a universal error-exclusion claim.
- **S065 correction row:** the S061 wording omitted the `sys.exit(None)` special case. S065, opened from Python 3.14.8 `sys.exit`, records “None is equivalent to passing zero” and supersedes only that scope; the knowledge entry has an appended qualification. Search note and row are at the end of `corpus/SOURCES.md`.
- **S051 line range:** M8 at line 82 incorrectly called 210–215 the current S051 text. The S051 clarification is currently at `corpus/SOURCES.md:217-222`; 210–215 is the S056 supplement. The R18 lesson's appended stable-heading correction at `:447-451` remains the durable pointer; no source row was rewritten.
- **C2 fixture boundary:** `v3-all-scalars` expected.json contains twelve `test.*` values, but `c2/measure.py:459-484` compares selected identity keys/types, arrays, header counts/version/endianness, size and digest, not those arbitrary scalar values. Thus 23/23 means all declared measurement predicates passed, not generic scalar-value recovery; the C2 claim remains limited to selected declared identity fields.
- **Grid signal/timeout probes:** deleting either explicit branch preserved the `error` class through the fallback but weakened reason detail (`MutGridSignal.md`, `MutGridTimeout.md`). No claim about diagnostic-reason equivalence is made; the C1 outcome-class boundary remains.

## Gate supplement — S065 `sys.exit(None)` exception (opened 2026-10-21)

| Candidate | Decision | URL, revision, location and quote |
|---|---|---|
| S061's non-`None` exit-1 rule also applies to `sys.exit(None)` | reject that broad reading; add S065 as a correction row | https://docs.python.org/3.14/library/sys.html#sys.exit, Python 3.14.8, §sys.exit optional-argument paragraph: “None is equivalent to passing zero.” |

The reopened paragraph distinguishes the `None` special case from “any other
object” printed to stderr with status 1. S065's `teaches` field supersedes only
that scope in S061; it does not change the error-versus-verdict claim. Search
log: one source candidate identified, screened and included as S065; excluded
zero; stop after the special-case wording was located. Existing S061 cells
remain unchanged.

### S051 range after the S065 append (appended)

M8's `SOURCES.md:210-215` pointer was already stale after earlier R20 rows
shifted the S051 clarification to `217-222`. Appending S065 after S064 moved the
current clarification to `218-223`. The LOG's pre-S065 range was time-bounded;
this note gives the current range. The stable heading and revision-qualified
R18 lesson correction remain the durable pointer.

## Trend verdicts and previous verifier disagreement

- **Expansion: improved.** The scorecard adds one first-working offline GGUF
  identity capability (`SCORECARD.md:909-918`); this is a capability surface,
  not a source-row-count argument.
- **Quality: improved, bounded.** C1's finite 15-cell misclassification count
  falls 6→0; C2 passes its declared 23-fixture predicates and oracle/receipt
  agreement. The preceding fixture note limits scalar-value coverage.
- **Discernment: unchanged for R20.** There was no independent non-author R20
  admit/reject sample. The prior R19 verifier reopened three decisions, agreed
  with two admits and one reject, and credited R19 discernment as improved after
  the author record was written (`round-19-verifier-spotcheck.md:160-172`).

That verifier disagreed with the R19 author trend: expansion was unchanged
because no knowledge/capability surface was added, despite the lane's
“improved (narrow)” wording. R20's expansion verdict is improved for the new
capability row, not for S-row growth. This preserves the historical R19 record
and makes the time boundary explicit.

## CellGridRealInvalidVerdict source binding

Its falsify seat report remains `partial` because it did not itself pin the
execution-time source bytes. The official `run.py` refuses a dirty tree
(`run.py:25-27`) and records `measured_commit`; `runs/0957ce61/commands.json`
records `0957ce619789d13bb5779606078fa1498114d2c7`. Read-only hashing of that
commit's `tests/llamacpp-live/install-tree-grid.py` gives
`d9689c0718a6001f808c00c7b5318327e0757713033e9df04994687a422650c5`.
This binds the measured classifier source at that revision; it does not claim
additional cells or broader detector coverage.

## GGUF fixture default metadata correction

`FixtureKvCount2pow40.md` found that `expected.json` and its generator described
`--max-kv` as 1,000,000 while `tools/gguf-identity.py` sets both limit and
default to 100,000. The adjacent `tool_default_max_string_bytes` was also stale:
16,777,216 versus the parser's 1,048,576. The generator now records the actual
defaults and separates the upstream uint64 count fact from this parser default
in the fixture basis. Regeneration retained all 23 fixture hashes; the
`SHA256SUMS` file hash remains
`ab51c80f26ce1c155f5b5e8377a6363df9fa93ff6ac1669000a9aaf70d995812`. This is
manifest/test-description correction only: no parser behavior or fixture bytes
changed, and the 2^40 count still rejects as `kv_count_too_large`.

## Falsify wave-2 disposition

The 86-seat wave used roles reviewer60/mutation-tester17/scout6/critic2/
connector1. Attempt 1 was refused before spawning any seats by the host job cap;
after at least 180 seconds the unchanged payload spawned all 86. Seventy-three
completed with one report each; thirteen exhausted provider retries without
advice. No seat was replaced; the round total is 158 spawned seats across build
and falsify. The exact dead-seat names/errors, retry record, and advice counts
are in `falsify/{seat-failures.json,dispatch-attempts.json,verdict-count.json,
completion-summary.json}`.

Top-level advice verdicts: confirm66, partial7, refute0, nonconformant0. All
seventeen mutation probes produced results: fifteen killed their targeted
mutants, while signal and timeout-branch deletion preserved the `error` class
and only lost diagnostic detail. Integrated partial findings: S063 `used-by`
was corrected; S061's `None` case received S065; the S051 range was updated
after insertions; the fixture default-limit manifest was corrected; and the
grid classifier source was bound to its clean measured commit. The
v3-all-scalars comparison gap and timeout-reason detail remain explicit limits.
No extra ordinary residual-review task call was used.

## First post-manifest measurement failure and correction

The first official rerun at `c7311039` failed closed: both GGUF measurement
commands exited 2 because `c2/measure-reference.json` still pinned old
`expected.json` SHA-256 `1ffe884a523fb85866ac43775fee0a5be1f69398c09a3dae8b8832f39c9f7f9f`, while the corrected manifest hashes to
`714226dfb6ae578fb1718f6c19b76c1328cf9dfc74ced01e5f280b39bfeccd48`. The retained output
`.ufo/waves/round-20/runs/c7311039/gguf-measure.stdout` reports
`snapshot_tampered` for all 23 fixtures and `parser_attempted: false`; thus no
fixture result was credited by this run. The reference's fixture identities
remain the same; only `fixture_manifest.expected_json_sha256` was updated to
the exact new manifest digest. The failed run is retained as evidence, not
counted as final verification.

## Second post-manifest measurement failure and correction

The rerun at `04de7a87` advanced past the manifest pin but failed closed before
fixture evaluation because `c2/measure.py` still pinned the prior reference
file hash `fb367e9e2c91eaadf4fb48bddb7a984a2c0c0feda41a45a00d75bbed182c5bc6`,
while the updated reference file hashed to
`e3f0349ab13cf08c7934d43c71a6ec27c7283150e90e39f3dd2d63f9be9c7bcb`. The
retained `gguf-measure.stdout` contains only this reference-hash mismatch and
credits no fixture outcome. `REFERENCE_SHA256` is now updated to that exact
file digest; this failure is retained separately from the final rerun.

## Corrected final measurement — 9add96e4

The committed-tree runner
`python3 .ufo/waves/round-20/run.py --recipe .ufo/waves/round-20/recipe.json
--out .ufo/waves/round-20/runs/9add96e4` measured
`9add96e462e62dc5141cd02730b7a699268b3513`; all 21 commands met their declared
exits, harness exit0. C1 remains 15 cells, frozen misclassified6/current0,
witness mismatches0, red-vector mismatches0, unrun0. C2 is 23/23 declared
fixture predicates with mismatches0, snapshot tampering0, unavailable0, and
real-file oracle/receipt agreement. Its arbitrary scalar-value boundary stays
as stated above.

The source census after S065 is rows57→65 (A54→62/C3; mined46→52, queued5→6,
rejected6→7, missing0). `sources-validate` and `sources-census` both exit0;
W04 warnings are S031/S043/S056/S060/S064/S065. Exact stdout, stderr, argv and
exit records are in `.ufo/waves/round-20/runs/9add96e4/commands.json` and its
sidecars. The c731 and 04de fail-closed outputs remain retained, not credited.
