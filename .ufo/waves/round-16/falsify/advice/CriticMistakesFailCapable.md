VERDICT: partial — `corpus/lessons/round-16.md` §Mistakes (M1–M5): fail-capability of each fix, M1 "captured-by none", and whether M2–M5 are honest and complete against the build advice

Seat `KamaR16.CriticMistakesFailCapable` (critic, leaf). Read-only toward the lane: I wrote only this report, plus scratch under `/tmp/kama-r16-CriticMistakesFailCapable/`, which I removed afterwards. I did not run `measure.py`, did not start llama-server, and did not touch 8080/34113.

## Summary per row

| Row | Fix shown able to fail? | Honest? | Complete vs advice? | Verdict |
|---|---|---|---|---|
| M1 | **Yes.** Re-run: frozen 55/17, current 72/72, changed set == the 17 expected-loading rows | Yes. One overstatement in the evidence pointer (see M1-b) | n/a | confirm (one wording fix) |
| M2 | **Partly.** The rebound gate rejects old-spelling receipts (shown below). The class guard is still a hand-written selftest literal with no binding to the producer | Yes | Omits that a reviewer certified the drifted selftest as "no defect" | partial |
| M3 | **No, for the failure it names.** The zero-request guard cannot catch the M3 hang: a mutant without the serving thread still hangs (exit 124). The "timing smoke" has no receipt | Evidence pointer does not resolve to any artifact | Omits the real mechanical backstop (`measure.py` 600 s timeout) | refute (fix column) |
| M4 | **Partly.** The fleet sweep can see in-repo misroots but is blind to sibling lanes (`*-shokunin/` ignored) and has no baseline. No receipt shows it was run | "its own disclosure" resolves to no lane file | Repeats round 11 (`LOG.md:573`); the lesson does not say so | partial |
| M5 | **No fix.** "Disclosed and kept as incidents" cannot fail | Understates | **Materially incomplete:** names 2 seats; at least 6 more went beyond their bound, one of them ran a lane test | refute (completeness) |

## Evidence

### M1 — confirmed

- `python3 tests/probe-verdicts/check.py --probe .ufo/waves/round-16/frozen/kama-probe-before.sh --json > /tmp/…/frozen.json` → **exit 1**, `tests=72 passes=55 failures=17`, `probe_sha256 93ee4302…a2cd64` (equals the `frozen/manifest.json` sha256).
- `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json > /tmp/…/current.json` → **exit 0**, `tests=72 passes=72 failures=0`, `probe_sha256 6edd3c4c…72fa50`.
- I compared the two JSON files in Python. The frozen failure set (17) equals the set of `expected.verdict == MODEL_LOADING` rows (17): `equal True`. The set of changed verdicts equals the same set: `changed==exp True`. The before-red/after-green obligation in KQ19 (`corpus/QUALITY.md:109`) can fail, and it was shown failing.
- **M1-a — "Captured-by: none" holds.** `git grep -i -E "503|loading|not.ready|readiness" 20e392e -- corpus/lessons LOG.md SKILL.md corpus/QUALITY.md SCORECARD.md`, filtered for probe/verdict context, finds no record that compared a loading state with the probe. KQ13 (`QUALITY.md:40` at 20e392e: "inference readiness are separate propositions") covers documentation claims, not probe verdicts. `RevengerPlannerWalk.md:17-18` reports no 503/loading tokens in the round-1 tree.
- **M1-b — evidence pointer overstates (fixable wording).** M1 says "the body was already documented at `runtime-health-surface-matrix.md:14`". At 20e392e that row documents the 503 "Loading model" body only on **`GET /health`** (liveness column; README-sourced, S001). The identity route `/v1/models` is listed separately and gets no 503. The lesson's own Gate row 45 rejects "README alone supports the `/v1/models` 503". So the old knowledge could not have flagged the `/v1/models` grading without the S036 source read. **Smallest correction:** say "documented for `/health` (not `/v1/models`) at `runtime-health-surface-matrix.md:14`".
- **M1-c — counting caveat (not an M1 defect, but an unrecorded mistake).** The 72 rows hold only **69 behaviourally distinct tests**. I hashed `routes/default_route/port_mode/expect/expected` per test. Duplicates: `EnvelopeShapes.CodeAsString ≡ Overbroad503.code-string`, `ForeignControls.busy-unavailable-error ≡ Overbroad503.no-slot-available`, `ForeignControls.loading-message-wrong-type ≡ Overbroad503.server-error-type`. `SimplifierHarness.md:94-104` (D3) flagged this; it was not acted on or recorded. None of the three is a loading row, so 17/17 stands. But "72 rows" over-reports the denominator, which is the round-15 counting class.
- **M1-d — prior exposure is undeclared in the frozen manifest.** `frozen/manifest.json` has no prior-exposure field (keys: snapshot, sha256, source_commit, source_path, source_blob, capture, bytes). `ConnectTameshi.md:53` marked this **partial**. `RevengerPlannerWalk.md:41` shows the stub families landed (10:26) after the tree already carried `MODEL_LOADING`. The red/green is still literal and fail-capable, but it was not pre-registered blind. `LOG.md:930` discloses the 10:17 smoke in prose only.

### M2 — partial

- `python3 tests/llamacpp-live/check-receipt.py --selftest` → **exit 0**, `selftest: 16 mutations + unreadable case all rejected; valid receipt accepted` (the "16" matches the lesson).
- `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-16/live/receipt.json --expect-model-sha256 270cba1b…256d` → **exit 0**, `VALID`.
- **The rebinding can fail (my mutation controls).** I copied the real receipt to `/tmp` and restored each pre-fix spelling the lesson names:
  - `started_utc → started` → **exit 1**, `started_utc None is not a parseable ISO timestamp`.
  - `teardown.port_refuses → port_closed` → **exit 1**, `teardown_port_closed: teardown.port_refuses is None, want true`.
  - `probes[*].result → json` → **exit 1**, `probe ok: result is not a parsed kama-probe JSON object`.
- **The class guard is not fixed.** The selftest still validates a hand-written literal: `check-receipt.py:754 def _selftest_receipt()`, `:758 "started_utc": …`. The file imports nothing from `tools/kama-llamacpp-live.py`; `grep -n "import "` shows only stdlib. I diffed key paths between the literal and the real receipt: 85 real-only paths and 9 literal-only paths. The literal-only paths are the whole `loading_503` subtree and `server/install_tree/libllama.so`.
- The real receipt has `loading_observed: false` and `loading_503: null`, and `LiveHarness.md:31` says "loading-503 verbatim + envelope paths unexercised". So the gate's `loading_503` branch (`check-receipt.py:340-361`) has been checked only against the gate author's own literal. That is the M2 mechanism, still open on an unexercised branch. By static read its keys currently match the producer (`kama-llamacpp-live.py:426-433`; `_header_subset` lowercases `server`/`content-type`). Nothing mechanical keeps them matched.
- **Omitted consequence.** `ReviewSkillPlacement.md:6-8` ran the drifted selftest, and `:156-157` lists it under "Positive verifications (no defect)" ("10 mutations + unreadable case all rejected; valid receipt accepted"). That is a reviewer seat treating self-test green as verification, contrary to `PROTOCOL.md:390` ("Self-test green is capability, not a measurement"). M2's captured-by column should record that one review seat certified the drift and two others caught it.
- **Smallest correction:** derive the selftest base from the committed real receipt (load `receipt.json` and mutate it), or add a producer-bound test. Also record that the `loading_503` branch is validated only against the literal until a live loading observation exists.

### M3 — refuted (fix column)

- Baseline: `timeout 40 python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --only ReadyControls.expect-exact-id --json` → **exit 0**, 587 ms. This matches the lesson's "0.6 s".
- **Mutant 1 = the exact M3 defect.** In a `/tmp` copy of `check.py` I replaced `threading.Thread(target=server.serve_forever, daemon=True).start()` (`check.py:314-315`) with `pass`. The same `--only` run under `timeout 40` → **exit 124 after 40 003 ms, no output**. The zero-request guard (`check.py:323-328`) returns a record, but the `finally` then calls `server.shutdown()` (`:354`), which blocks forever when `serve_forever` never ran. That is the mechanism `ReviewSchemaAmbiguity.md:28-31` describes. **The guard cannot detect the failure M3 names.**
- **Mutant 2 (guard is live code).** Probing `port + 1` instead of `port` → **exit 1**, `error=stub accepted no requests; probe never reached a listening socket`. The guard catches a wrong-port fault, not a non-serving stub. It also grades that harness fault as exit 1 (test failure), not exit 2, which conflicts with the H2 separation (`ReviewSchemaAmbiguity.md:36-39`).
- **The mechanical backstop is not cited.** `measure.py:53 DEFAULT_TIMEOUT_SECONDS = 600` and `:152-159` (`subprocess.run(..., timeout=timeout)` → `measure: killed after {timeout}s`) bound the hang at 600 s. The lesson credits neither.
- **Unresolvable pointers.** "L1 started `measure.py` … hung and was killed (bg job cancelled)" and "L1 now runs a single-test timing smoke" cite no artifact. `ReviewSchemaAmbiguity.md` H1 proves the code defect, not that L1 started a measurement on it. I grepped `.ufo/waves/round-16/{measure-stdout.txt,run-check-selftest.txt,measure.py,…}`, `LOG.md` and `SKILL.md` for `smoke|--only|0.6 s|hung` and found no smoke receipt. This conflicts with `PROTOCOL.md:356` (a pointer must resolve at closure).
- **Smallest correction:** in the fix column, name the `measure.py` 600 s subprocess timeout as the mechanical bound, and either bound `shutdown()` (call it only when the serve thread started, or join it with a timeout) or drop the claim that the guard addresses M3. Commit the smoke's command, exit and elapsed time as a file, or drop "L1 now runs".

### M4 — partial

- **Fail-capable in scope only.** `git -C /home/vgpnk/Projects/shokunin check-ignore -v` → `not ignored` for `.ufo/waves/round-16/build/advice/RevengerPlannerWalk.md`, `corpus/knowledge/x.md`, `tests/probe-verdicts/x.json`, `tools/x.py`. A misroot into the fleet repo would therefore show in `status --porcelain`.
- But `kama-shokunin/x -> .gitignore:1:*-shokunin/`. A misroot into any sibling lane directory, and any write outside the fleet tree, is invisible to the sweep.
- The fleet status is not quiet: `git status --porcelain | wc -l` → 14 lines (`.ufo/watchdog.log`, `.ufo/state/*.report-baseline`, `.ufo/waves/hyaku/jj-w1/`, `scripts/hyaku/*`). Without a pre-round baseline, attribution is manual. `/home/vgpnk/Projects/shokunin/.ufo/waves/round-16/` exists and holds 6 tracked fleet files (`before.md`, `dispatch.md`, `clobber/*`, `gate/*`), so a same-named misroot path sits next to legitimate fleet files.
- **Not shown run.** No file in `.ufo/waves/round-16/` records the sweep's output.
- **Unresolvable "own disclosure".** `RevengerPlannerWalk.md` has no misroot/moved/removed text (grep empty). A regex over `build/{spawn-result.json,advice/swarm-registry.json,completion-summary.json,record.stdout}` finds none either. [INFERENCE] The disclosure lives only in the seat's final message, which this seat may not read (session stores are forbidden).
- **Recurrence not stated.** `LOG.md:573` (round 11): "Three misrooted continuation reports were copied into this lane"; `round-12-verifier-spotcheck.md:153`: "round-11 misrooted-advisor cleanup remains with Main". The prior control (the absolute-path context clause) existed and failed again. M4 should say it repeats round 11.
- **Smallest correction:** record a fleet-status baseline at dispatch, plus the post-wave diff, as a file. Add `ls` checks of the sibling-lane paths the seat could misresolve. Cite the recurrence. Paste the disclosure text into the lesson or an advice file so the pointer resolves.

### M5 — refuted (completeness)

M5 names `ConnectKumitate` (two kumitate notes) and `ConnectTsukuroi` ("one `ls -la`"). The build contract (`build/spec.json` context) says: "bound every grep/glob to the paths your item names", and "run no lane gate, harness or test against the lane except what your item explicitly allows". Each Connect item reads "bounded to those files and its corpus/QUALITY.md". The seats' own reports show more:

| Seat | Beyond-bound action (its own words) | Item bound |
|---|---|---|
| ConnectTsukuroi | `ConnectTsukuroi.md:5` "tsukuroi `SKILL.md`, `PROVINCE.md`, `MINT.md`, `AGENTS.md`, `LOG.md:775-850`, … `corpus/knowledge/adjacency-handoffs-fleet-r1.md`, `tools/tsukuroi-census.sh`" | SKILL/PROVINCE/QUALITY. M5's "one `ls -la`" understates this |
| ConnectTameshi | `ConnectTameshi.md:4-5` "plus four corpus notes cited below" (e.g. `mutation-case-kagi-census.md:88-91`) | same class as ConnectKumitate; not listed |
| ConnectKake | `ConnectKake.md:10-11` "`kake-shokunin/corpus/knowledge/publish-queue.md`, `kake-shokunin/corpus/lessons/{round-9,round-10,round-1-aggregator-audit}.md`" | not listed |
| ConnectMori | `ConnectMori.md:118` "`tools/mori-census.sh`, `corpus/knowledge/observability-surfaces-r2.md` and `corpus/evidence/README.md` were read only to corroborate" | disclosed; not listed |
| ConnectKengaku | cites `kengaku/corpus/knowledge/consumer-registry.md:110` (`ConnectKengaku.md:49`) | not listed [INFERENCE: beyond bound by path] |
| RevengerPlannerWalk | item: "bounded to that file" plus LOG.md. Report `:18` ran `git grep 503\|5xx\|loading c6199a2 -- .` (whole tree) and `:117-118` "Searches bounded to … `corpus/`, `registry/`, `tests/`, `.ufo/waves/round-11`, `.ufo/waves/round-16`" | not listed |
| ReviewSkillPlacement | **ran a lane test:** `:6-8` "the only executions were `check-receipt.py --selftest`". Item: "Read … SKILL.md (all)", read-only | not listed. This is the "run no lane gate/test" clause, which is more serious than a read |

Lower-severity executions that were disclosed: `ReviewMatcherExactness.md:147-148` ("an extracted-function unit run"), `ReviewSnapshotCoupling.md:12` (`bash -n tools/test-snapshot.sh`), `SimplifierHarness.md:23-27` (whole-tree `grep`, `llama-server --version/--help`).

- **"no session or credential store was read by any seat that reported"** — no seat discloses such a read. I cannot verify absence without reading forbidden stores. [INFERENCE] The claim rests on self-reports.
- **Fix column:** "disclosed and kept as incidents" is a disposition, not a fix. Nothing in it can fail. `ScribeLessonMistakes.md:20` already said "Compliance is not observed", and the lesson still has no mechanical check.
- **Smallest correction:** list every beyond-bound seat above, or state the sweep method and its count. Separate "read beyond bound" from "executed a lane test". Either name a fail-capable control (e.g. L1 greps each advice file's own read/exec disclosures against its item's named paths and records the count) or write "no fix; incident only".

## Other unrecorded build-wave mistakes (not in §Mistakes)

- **Stale line anchors in committed fixtures.** `tests/probe-verdicts/AuthAndDead.json` why: "curl rc=52 empty reply -> NOT_HTTP empty-reply (kama-probe.sh:436-440)". The current `tools/kama-probe.sh:436-440` is the new Python matcher (`if not isinstance(doc, dict): sys.exit(1)` …); `empty-reply` is now at `:474`. The anchor was right only for the frozen probe. `grep -o "kama-probe\.sh:[0-9-]*" tests/probe-verdicts/*.json` → 11 anchors, all past line 60, where the header insertion sits [INFERENCE: all shifted; I verified one]. Flagged by `SimplifierHarness.md:247-248` and `ReviewSchemaAmbiguity.md:232-234`. This is the KQ7 class (`QUALITY.md:29`: "a mid-file insertion shifts other files' line anchors").
- The three behavioural duplicates in the matrix (M1-c).

## Impacted axes

- Calibration: the M1 claim stands. M3, M4 and M5 overstate fixes and M5 undercounts incidents. Those are self-assessment defects in a round whose assigned lowest axis is calibration.
- Operability: unaffected by these findings. The receipt gate is VALID on the real receipt.

## Limitations

- I did not read the operator round-prompt template ("Frontier step — every round") because it is outside my named paths. "Fix shown able to fail" is judged against the lesson's own "Fix / failure obligation" column, KQ19, QUALITY.md:38 ("controls must fail before the repair counts") and PROTOCOL.md:138-140/356/390.
- The pre-fix `check-receipt.py` is not in git (only b8e485c). The M2 "before" state rests on the two advice reports.
- All mutation work used `/tmp` copies. I made no lane edits.
- `pgrep -x llama-server` → exit 1 (no process). I started no server.

## Commands run (exit codes)

1. `check.py --probe frozen --json` → 1 (55/17)
2. `check.py --probe tools/kama-probe.sh --json` → 0 (72/72)
3. `check-receipt.py --selftest` → 0
4. `check-receipt.py receipt.json --expect-model-sha256 …` → 0 VALID
5. Gate on 3 old-spelling `/tmp` copies → 1, 1, 1
6. `check.py --only ReadyControls.expect-exact-id` → 0 (587 ms)
7. Serving-thread-removed mutant under `timeout 40` → 124 (hang)
8. Wrong-port mutant → 1 (guard fires)
9. Fleet `git status --porcelain` (14 lines) and `check-ignore -v`
10. `git grep` at 20e392e for prior capture
11. Python set and duplicate analyses
12. `pgrep -x llama-server` → 1

## Installs

None.
