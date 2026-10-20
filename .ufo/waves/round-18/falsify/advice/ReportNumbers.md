VERDICT: partial — raw before→after improvements are retained, but both official counters exit 2; the delivered counter revisions have no corrected official run in the inspected runs directory.

# ReportNumbers — evidence draft, not admission

## Scope, axes and provenance

- Axes: C1 operability **8→8**; C2 calibration **7→7**, the lowest assigned axis. These are declared score assignments, not numerical increases inferred from test results (`/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:744–760`). Reporting axes: numerical fidelity, denominator visibility, provenance, and no new execution/exposure.
- Assignment: draft Before→after tables from existing raw c1/c2 outputs, recorded commands and input hashes. No product changes, runtime, gate reruns, mutations, judge, admission, commit, push or publication were performed by this seat.
- Authoritative assignment target: `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`. Official `commands.json:2` instead names measured revision `c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d`. The raw results below belong to that recorded measurement, not an unexecuted claim about revised counters.
- Read scope included the round-18 lesson, SCORECARD Round 18, `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md:125–133`, the official runs directory, and raw JSON/stdout/stderr. The initially supplied root `QUALITY.md` path does not exist; file discovery located `corpus/QUALITY.md`.
- KQ23 requires necessary conditions to remain necessary; no SIGTERM sufficiency claim is added here. KQ24 distinguishes missing observation from observed failure and forbids treating every nonzero as one class. Counting-tool exit 2 below is an unsuccessful evaluation of the counter, not automatically a C1 subject failure or a mutant kill.
- This is own-wave reporting advice. L1 owns integration/admission. It is not an outside non-author judgment.

## Evidence identity

All evidence paths in this report's tables are under the absolute directory `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/` unless an absolute path is given. JSON paths identify nested evidence without conflating it with a newly executed command.

The following hashes were observed directly with the read-only `sha256sum` command recorded below. The JSON/stdout pairs are byte-identical by SHA-256, and the stdout/stderr hashes match their corresponding command-manifest entries.

| Evidence | SHA-256 |
|---|---|
| commands.json | `ce7dc79c9523b92c33e0cbb141299db6196b2aa64b3c307779eee1842b51b84a` |
| c1-measure.json and c1-measure.stdout | `3ad738fc1a5035fd678dd4207b381f7491fb74887a894234a4d60274dfc098a4` |
| c1-measure.stderr | `62554bae491765a71855c98923e6c08e59c063d67a66f606f78ce79aef5549dc` |
| c1-self-mutants.json | `70a12d50e5b9d77bc6fce38e49bbc9ef3cf0e59a95dd1ba9966a48fdc3f23337` |
| c2-survivors.json and c2-survivors.stdout | `bd217de0030d1b69f07c0ac3cc334ccdac192896441a177bb13eb3c308509829` |
| c2-survivors.stderr | `9da3990cc432a14257f7e85d4f0cb30b709b9ee6e433967897e7315be30a21ec` |

## Exact official commands — recorded, NOT rerun

Recorded cwd: `/home/vgpnk/Projects/shokunin/kama-shokunin`. Recorded Python: `3.14.8 (main, Oct  2 2026, 10:23:31) [GCC 16.2.1 20260810]`.

### C1 measure

```sh
/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/c1/measure.py --controls /home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/controls.py --frozen-tool /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py --frozen-gate /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py --tool /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py --gate /home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py --probe /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh --json --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/c1-measure.json
```

`commands.json:170–198`: started `2026-10-20T22:36:27.079115+00:00`; elapsed 40.355 seconds; exit **2**, expected 0, `as_expected:false`. Stdout is the JSON above. Stderr, verbatim (`c1-measure.stderr:1`):

```text
c1-measure: fault: before: misclassified=1 but 0 row(s) classified misclassified
```

### C1 controls-self mutants

Exact argv is the C1 command above with `--self-mutants --baseline-runs 1` inserted after `--json`, and `--out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/c1-self-mutants.json` replacing its output argument. Started `2026-10-20T22:37:07.434893+00:00`; 101.303 seconds; exit **0**, expected 0; stderr empty. This is a distinct artifact/experiment, not a successful replacement for C1 measure.

### C2 named survivors

```sh
/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/c2/survivors.py --json --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/c2-survivors.json
```

`commands.json:674–690`: started `2026-10-20T22:40:05.489261+00:00`; elapsed 1577.225 seconds; exit **2**, expected 0, `as_expected:false`. The report's internal elapsed time is 1577.1 seconds; do not substitute that for the outer command duration. Stderr ends, verbatim (`c2-survivors.stderr:22–23`):

```text
named items not killed/handled/correct: before 15 -> after 2 (of 15 named)
exit 2
```

## Before→after draft: C1 raw subject/control cells

Evidence: `c1-measure.json:380–427`, `.runs.before/.runs.after.doc`, `.summary.rows`, and the artifact hash above. One frozen-subject arm and one current-subject arm used the **same current controls file**, with K0–K22 selected in each arm (**23 rows per arm**). This is not a random sample or a fresh-mutant denominator.

| Metric | Before | After | Denominator / exact interpretation |
|---|---:|---:|---|
| accepted_bad | 5 | 0 | Bad rows K18–K22; before: K18 escaped without receipt, K19–K22 gate accepted. This is not five tool-exit-zero passes. |
| good_rejected | 1 | 0 | K17 ownership positive control; K0 and K17 are the two expected accepted rows. |
| misclassified | 1 | 0 | K16 no-loading observation; before row bucket is `misclassified`, while its classification token is `rejected-targeted`. Counter rejected this representation mismatch. |
| uncontrolled_checks | 0 | 0 | Ten governed graded check IDs have control coverage in each arm under the new controls suite. `model_unchanged` is separately listed as input integrity, not an eleventh controlled subject check. |
| gate_flip_arms | 16 | 17 | Number of recorded gate-flip arms, not total rows. |
| gate_flip_bad | 0 | 0 | Zero among 16 before / 17 after recorded flip arms; do not call either a 23-arm result. |
| good_ok | true | true | Boolean positive-control result; not an overall pass rate. |
| inconclusive (raw subject summary) | 0 | 0 | Does not erase the counter's own exit 2 / unusable frozen measurement baseline. |
| subject controls subprocess exit | 1 | 0 | Before reflects detected subject defects; after arm is green. Outer counter nevertheless exits 2. |

Cross-check of the 23 row buckets: before **16 ok + 5 accepted_bad + 1 good_rejected + 1 misclassified = 23**; after **23 ok = 23**. These are row-bucket tallies, not validated overall counter admission.

Classification tokens are a different distribution: before **6 accepted + 16 rejected-targeted + 1 rejected-untargeted = 23**; after **2 accepted + 19 rejected-targeted + 1 rejected-untargeted + 1 not-evaluated = 23**. In particular, `ok` includes the expected not-evaluated K16 and must not be rewritten as 23 subject passes.

### C1 named transitions and denominators

| Row(s) | Before raw observation | After raw observation |
|---|---|---|
| K9–K14, six retained check controls | Targeted rejection in all six | Targeted rejection in all six; checks are models_alias_id, models_owned_by_llamacpp, metrics_not_enabled, props_alias, probe_model_ok, probe_mismatch |
| K16, zero-loading | tool 1 / gate 1, rejected-targeted, misclassified bucket | tool 2 / gate 3, not-evaluated; no failed checks |
| K17, ownership positive | tool 2 / gate 1; rejected, good_rejected bucket | tool 0 / gate 0; accepted |
| K18, injected KeyboardInterrupt | tool 4; no receipt; gate not run; accepted_bad | tool 2 / gate 1; receipt written; `internal:KeyboardInterrupt`; targeted teardown failure |
| K19, schema | gate 0 | gate 1, targeted schema rejection |
| K20 and K22, argv | gate 0 on each | gate 1 on each, targeted argv rejection |
| K21, loading transition | gate 0 | gate 1, targeted transition rejection |

The six retained controls are not the same denominator as all ten controlled graded check IDs. The **0→0** uncontrolled-check result measures the new suite against both subjects; it does not establish that six v2 checks were absent. The supplied lesson already makes this limitation explicit (`corpus/lessons/round-18.md:169–176`).

## Before→after draft: C2 fixed named universe

Evidence: `c2-survivors.stderr:2–23`, `.counts`, `.results`, `.frozen_witness_validation`, hash above. The denominator is **15 heterogeneous named items**: **11 mutants + 1 provenance-count witness + 3 escaped fault paths**, not 15 mutants. Frozen-witness validation records all 15 expected labels matching, with no mismatches. Before labels: 11 survived, 1 miscount, 3 accepted. After labels: **9 killed, 2 inconclusive, 1 correct, 3 handled**.

| Family / named items | Denominator | Before | After | Bounded reading |
|---|---:|---|---|---|
| a: H1,H2,H3,H5,H6,H7 | 6 mutants | 6 survived | 6 raw killed | Current pristine detector exit 0; each mutated checker causes detector exit 1; distinguishing controls F9,F10,F11,F12,F13,F14 respectively. H4 is not part of this named set. |
| b: FC-target, FC-f6cache, FC-f0gate | 3 mutants | 3 survived | 1 raw killed, 2 inconclusive | All three selftests red. FC-target/cache main arms exit 2 own-fault, so their composite rows remain inconclusive. FC-f0gate main survives, selftest rejects. |
| c: AO-opened, AO-blank | 2 mutants | 2 survived | 2 raw killed | Pristine selftests 14/14 frozen and 42/42 current. Current mutants exit 1: opened 15/42, blank 36/42, including targeted failing assertions. |
| d: refused-count | 1 input witness | miscount: 0 refused | correct: 82 refused | Same pinned refused-result bytes; spawned remains 0→0. This is one count witness, not 82 mutant kills or 82 successful task launches. |
| e: nested-json, bigint, escaped-sleep | 3 fault paths | 3 accepted | 3 handled | Malformed outputs become row failures without traceback; same-group timed-out child absent after current checker exit. These are fault-path outcomes, not mutant kills. |
| Combined unresolved named items | 15 items | 15 | 2 | Raw 15→2 means unresolved count; **not** 15→0 or 15 kills. Two residuals are inconclusive, not observed surviving current mutants. |

### Visible individual outcomes

| ID | Before→after raw label | Current mutant/payload SHA-256 (where supplied) |
|---|---|---|
| H1 | survived→killed | `4d3793d88e446fc22c640d8c6e36aed1dffb811bc559c2c7f681b064e5f66c32` |
| H2 | survived→killed | `85d20653a8d4899f77f51eacd9e3442640face4fbdb931a902cea78e9060d06b` |
| H3 | survived→killed | `6dafb748996dfc579e5651d06590d28737fd2cc3afdd852f8e46491d278dceaa` |
| H5 | survived→killed | `e672d93df90bd8d3e7c0235d147eb328dcb9be4c929773b6d0c95ed7ed22ad54` |
| H6 | survived→killed | `280111b9249dc217c8b501bbdc8d039c662213d063e1dbaac4484df0be8154fc` |
| H7 | survived→killed | `ee26337584752162014f758f5b62e6617cad99b6dde8211b7ef6e3ec983fa3dd` |
| FC-target | survived→inconclusive | `087b7ab4d35f3babc98928b1548b1fa768905862c333c9aec5cb7e300f6af6f4` |
| FC-f6cache | survived→inconclusive | `83ca502a06b57a560789596972cabb1af88e4f694f75742bfd5a99c93ee34d97` |
| FC-f0gate | survived→killed | `7543540b72b7e7f90bf5991d288c039f58049a1174f4b6872836b38f16d9df59` |
| AO-opened | survived→killed | `caff9a2e915423ea26ce3fc52b40bcf848f1f6886ff266aa46a2097d8e65abd5` |
| AO-blank | survived→killed | `8ebea191c992947973f3e1aea44ab05d51421334d9383b2f6feac6d3f530e3b3` |
| refused-count | miscount→correct | input `7167991932f619a6b805346338799bf6500d0a86387269e95b4c09e208041a5c` |
| nested-json | accepted→handled | payload `c706f5dbc35a287ab4f1e293002e8ea6a8c15c3ab5e7905c6ffad1c812123656` |
| bigint | accepted→handled | payload `ff27f74ea668652554e44089b1bc5cd6b0a4c20dae2bae684801ef61541e3fc6` |
| escaped-sleep | accepted→handled | payload hash explicitly null; do not invent it |

`accepted` in family e means the escaped fault remained, **not checker success**: frozen nested-json/bigint both exited 1 with traceback and non-JSON stdout; frozen escaped-sleep exited 1 with a live child. Current versions also exit 1, but return a failed JSON row; escaped-sleep current `escaped_pids:[]` versus the frozen live child, subsequently cleaned by the official harness. The intended 30-second probe timeout is the injected fault, not a harness timeout to credit as a kill. Deliberately detached sessions are outside the stated boundary.

### Composite-arm conflicts, verbatim

Source: `.results.b.items[].current`, corroborated by `c2-survivors.stderr:10–12`; C2 evidence hash above.

```text
FC-target: selftest killed (targeted selftest assertion failed: target-conjunct attribution); main inconclusive (fault-controls exit 2 (own fault), not a kill)
fault-controls: own fault: F1: fault declares no target conjunct; a row failure cannot be attributed to it
FC-f6cache: selftest killed (targeted selftest assertion failed: F6: replay run shares one cache); main inconclusive (fault-controls exit 2 (own fault), not a kill)
fault-controls: own fault: F6: a cached replay must target exactly one row (per-row cache), got 4
FC-f0gate: selftest killed (targeted selftest assertion failed: F0 gate: a reject-everything); main survived (main-run decision identical to the unmutated tool's)
```

There are no `equivalent` or `site_missing` outcome rows in this recorded named set; applicable mutant sites are recorded once each. That does not claim such outcomes cannot occur elsewhere. `.fresh_wave2` explicitly says `included:false, mutants:0`: this is exclusion from this report's universe, not evidence of zero fresh survivors. Fresh mutants need their own denominator and cannot be merged into these 15.

## Separate C1 controls-self experiment

`c1-self-mutants.json` records three `killed` labels, on **one** usable current-subject baseline run and a green controls selftest (`70 cases, 0 failure(s)`). The frozen-subject baseline is explicitly **usable:false / stable:false** with the same misclassified mismatch; it cannot substantiate before/after numeric kill comparisons.

| Named mutant | Raw selftest result | Current numeric arm | Mutant SHA-256 |
|---|---|---|---|
| drop-gate-flip-arm | exit 1, `ControlsFault: k1: gate-flip arm owed but not run` | exit 2 own-fault / non-JSON; not an additional targeted kill | `eaef487943e91ade3624fbe0cf99e9f11675feadf044e5f7e7fd504121d821d0` |
| loosen-k0-exit | exit 1, 2 failures about accepting -15 | exit 0, numeric signature unchanged | `dafae3e4620322f854365c3f63d38025562b9ad615081f72d863cb4a0e5810af` |
| k6-any-nonzero | exit 1, 5 failures including K6's exit-2 contract | exit 0, numeric signature unchanged | `f15866d40ad1d2facdb4edcd12191afbfd9f95189b3d61f70e18d09a887c47f9` |

Additional raw conflict, preserved verbatim from `.mutants[name=drop-gate-flip-arm].numbers.current`: `credited:true`, `differs:true`, and diff:

```text
run-fault: controls exit 2 (0|1 expected; 2 is its own fault); stdout is not JSON (JSONDecodeError: Expecting value: line 1 column 1 (char 0))
```

Its raw `killed_by` also includes `numbers:current (run-fault: controls exit 2 (0|1 expected; 2 is its own fault); stdout is not JSON (JSONDecodeError: Expecting value: line 1 column 1 (char 0)))`. That numeric credit conflicts with this assignment's own-fault-is-INCONCLUSIVE rule; the independent targeted selftest red remains separate evidence. Source hash is the full C1 self-mutants hash above. This seat does not resolve the conflict by upgrading the numeric arm to a kill.

These **3 raw labels are separate from C2's 15-item universe**. Neither this JSON nor C2's JSON contains explicit restoration-named fields in the inspected scalar paths. They preserve pristine/mutant input hashes and isolated scratch paths, but this seat did not independently observe byte-exact restoration. Consequently these are faithfully quoted historical outcome labels, **not newly admitted targeted mutation kills under this assignment's green/red/restoration requirement**. No denominator is silently strengthened on that basis.

## Official gates and totals

From `commands.json` directly: **32 commands**, **30 `as_expected:true`**, **2 `as_expected:false`** (C1 measure and C2 survivors). This is not “32 passed.”

- Ten selftest-named commands recorded exit 0: tool, gate, controls, checker, fault-controls, append-only, provenance, c1-counter, c2-counter, source-pins. They are commands, not a common number of test cases.
- Three live tool commands and their three gate commands recorded exit 0: **three pairs**, not six independent fixtures or a before→after experiment.
- Ten legacy commands are **five frozen/current pairs**, not ten different historical receipts. Wrong-probe-pin rejection is a separately expected negative result, not a failed no-harm check. Snapshot-clone and round-16-measure-clone are also distinct commands.
- These command counts account for the manifest as 10 selftests + 3 counting/self-mutant commands + 6 live commands + 10 legacy commands + 1 wrong-pin command + 2 clone commands = 32.
- Historical execution is not promoted to this seat's fresh runtime evidence. No missing real-fixture before arm is filled by inference; registered consumers, other runtimes, model quality, and repeated-trial statistics are out of scope.

## Recorded input pins

These are **recorded measurement input hashes**, not an assertion that all delivered files still have those bytes. Production/frozen paths are absolute via the bases below.

C1 bases: production `/home/vgpnk/Projects/shokunin/kama-shokunin/`; frozen `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/`.

| C1 input | Bytes | SHA-256 |
|---|---:|---|
| controls: production tests/llamacpp-live/controls.py | 82837 | `106dd98b60e066a190ee8fea609e5be99c6b2065b9c5a404e14394ce59b6ffc8` |
| frozen tool: tools_kama-llamacpp-live.py | 57556 | `0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac` |
| frozen gate: tests_llamacpp-live_check-receipt.py | 60756 | `ad6801791f2ada896a7ee188609391aac86185c47320dbf415331869ca9cd2a5` |
| current tool: production tools/kama-llamacpp-live.py | 63370 | `dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b` |
| current gate: production tests/llamacpp-live/check-receipt.py | 93515 | `c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335` |
| counter: production .ufo/waves/round-18/c1/measure.py | 69785 | `55b26b3b47e316f6b013fae980550073bad3972009c7dcee75d8d0da9e568c17` |
| shared probe: production tools/kama-probe.sh | 49744 | `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3` |
| shared registry: production registry/endpoint-consumers.tsv | 3450 | `bf343625188d9f486a6f6d13c60c946e23c21d05ee1bef881204dfa14c62bc6c` |

Frozen C1 tool/gate pins record verified comparisons to revision `e75cf680b53484a61709ee1b2787d8dbc6419f74`. `current_clean:null` is unknown, not true; `identical_pairs:false` must not be rewritten as a byte-identical before/after subject pair.

| C2 input | Frozen SHA-256 | Current SHA-256 |
|---|---|---|
| tests/probe-verdicts/check.py | `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099` | `12367de62efafa02641c4acb497e50f1be5019b54879a9ac6da13efd5f8071a5` |
| tests/probe-verdicts/fault-controls.py | `d3eaadeb8a061b4e322868d569df77afbd7331089d06b06c86a2063fdc31b312` | `58dac1f71346734532bddc60a2d20f95f640406e924b1aec00a0b750feed072a` |
| tools/sources-append-only.py | `c477a172cd5ae1512a9f75456da216a7df8cfde1df7c28fd09e60b76054b1e05` | `4d7868564226b6caa5957e9d7f4f8910a1c459ec26462a52d42e802be6079c2d` |
| round-17 frozen / round-18 current dispatch-provenance.py | `11ebb2c02f4c9160a4f20fba8d107b14be648ce6a3b1722dbbd112961b8d96df` | `93705f17a2b2dfeab1e80c886bcb53ae5a8e43b0c6e86e91b73a65ad5c1ea72f` |

Other recorded C2 pins:

- counter `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/c2/survivors.py`: `2af03fed6ccb0b09e30061828843372cb503d5d5e3afae846bc3f5473ced411d`.
- frozen manifest `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/SHA256SUMS`: `696211fb8005743e66c61286c028465eec199c5f5815ce868e0edd57ea32ba8c`.
- refused result `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/refused-result-1.json`: 9427 bytes, `7167991932f619a6b805346338799bf6500d0a86387269e95b4c09e208041a5c`.
- corroborating attempts `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/attempts.json`: 993 bytes, `85e4ba72793a4e76478fd227dbe27d8ff28fcff9f8cdd1639ef4814f313bd0c1`.
- nine-file matrix set: `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32`, `pinned_ok:true`; shared probe and registry hashes equal the C1 pins above. Per-member before/after hashes and `same:true` are retained in `probe-matrix-identity.json:2–50`; no matrix-byte mutation is inferred.
- provenance runtime's recorded policy input `/home/vgpnk/Projects/shokunin/scripts/hyaku/ufo-wave-policy-v2.json`: same frozen/current hash `70418a0f0b89288b6b481d682fb91a884de18001ecf87d06469955ffa64f59f9`. This is a reported input, not a policy edit or a command this seat executed.
- Upstream advice-source hashes remain enumerated in `.inputs["advice/..."]`; they are provenance, not additional trials or fresh denominators.

## Findings for the canonical judge

1. **Official C1 table is useful raw evidence but not a successful counter result.** `c1-measure.stderr:1`, `c1-measure.json:425–427`, and `commands.json:193–195` establish exit 2 with the verbatim mismatch above. The before K16 row actually has `bucket:misclassified` / `classification:rejected-targeted` (`c1-measure.json:3541–3543,4054–4058`). Preserve 5→0, 1→0, 1→0 and 0→0 as raw cells; do not call the counting command green. Evidence hash: C1 measure `3ad738fc...c098a4` (full hash above). Limit: no corrected official run observed; no fresh execution by this seat.
2. **C2 retains two explicitly inconclusive composites.** `c2-survivors.stderr:10–12,22–23` plus the recorded command exit 2 and `.results.b` conflicts above establish FC-target/cache main own-faults. A targeted selftest red does not change the official after residual from 2 to 0. Evidence hash: C2 `bd217de0...509829` (full above). Limit: raw historical labels only; no new kill admission or byte-restoration observation.
3. **Measured and delivered counters are different surfaces.** `commands.json:2` identifies c6dc46f, not the assigned 1c325b2. The read-only exact Git command below returned only counter changes among all explicitly scoped C1/C2 surfaces: measure.py 117 changed lines, survivors.py 26; total 2 files, 114 insertions, 29 deletions. These are diff statistics, not test counts. The inspected runs-directory listing and command manifest contain only the original official measurements, not corrected reruns. Evidence hash: commands `ce7dc79c...51b84a` plus the recorded raw counter pins. Limit: this does not prove no later evidence exists anywhere; none was present in the assigned official raw-runs location inspected.
4. **Denominators must stay disjoint.** C1 has 23 subject/control rows per arm, six highlighted retained controls, ten governed graded check IDs, and separate three controls-self mutants. C2 has 15 mixed named items, of which 11 are mutants; fresh-wave mutants are explicitly excluded (`c2-survivors.json:22–26`). No real before live-fixture arm or general-immunity denominator is recorded in these tables. Evidence: the two raw JSON hashes above, `.runs.*.doc`, `.counts`, `.fresh_wave2`, and the separate C1 self-mutants artifact hash. Limit: report labels are not interchangeable pass/kill rates.

## Read-only audit commands actually executed by this seat

These commands are evidence inspection only; neither invoked a subject runtime or official counting script. Both returned exit 0. Specialized read/grep/glob tools were used for all content inspection and JSON projections.

```sh
sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/commands.json /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/c1-measure.json /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/c1-measure.stdout /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/c1-measure.stderr /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/c1-self-mutants.json /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/c2-survivors.json /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/c2-survivors.stdout /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/c2-survivors.stderr

git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --stat c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d 1c325b2e58fcfdc6761f645b44cedfb1d65243e6 -- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/c1/measure.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/c2/survivors.py /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py /home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live /home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts /home/vgpnk/Projects/shokunin/kama-shokunin/tools/sources-append-only.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/dispatch-provenance.py
```

Git stdout, verbatim:

```text
 .ufo/waves/round-18/c1/measure.py   | 117 +++++++++++++++++++++++++++++-------
 .ufo/waves/round-18/c2/survivors.py |  26 +++++---
 2 files changed, 114 insertions(+), 29 deletions(-)
```

No experiment source was created because no experiment was executed. No tools were installed or updated. No scratch directory, clone, server, listener or long-lived process was created by this seat, so there is no seat-owned runtime to tear down; this is not a claim of a freshly executed system-wide listener scan. The official C2 artifact separately records its historical teardown `scratch_removed:true`, no marked stragglers, and `listening_after.owned:[]`; those are not this seat's observations of current host state.

## Touched surfaces, limits and artifact

- Only write: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/falsify/advice/ReportNumbers.md`.
- Production, fleet, sibling repositories, frozen evidence, old lessons and lane state were not edited. No git writes or jj commands were issued. No prohibited session, configuration or credential stores were read. No environment values were dumped.
- Missing prerequisites for any stronger numerical admission: corrected official output at delivered counter hashes; explicit admissible restoration evidence if historical mutation labels are to become newly credited targeted kills. This report intentionally does not manufacture either.
- Final behavior: retain raw before→after improvements and all contradictory/gate evidence; keep absent denominators absent. No score increase or universal detector adequacy claim.

Report: .ufo/waves/round-18/falsify/advice/ReportNumbers.md
