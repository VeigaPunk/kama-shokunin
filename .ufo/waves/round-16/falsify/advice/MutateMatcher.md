VERDICT: confirm — the round-16 matrix kills all eight assigned weak-matcher / classifier-order mutants.

# MutateMatcher — isolated falsification probe

## Axes and scope

- Calibration: sensitivity to the eight named matcher/order defects.
- Isolation / no harm: one semantic change per scratch subject, unchanged lane inputs, exact restoration, and the same detector on pristine, mutated and restored bytes.
- Attacked criterion: `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md:109` (KQ19). Quote (12 words): “The verdict is widened to any 503, any `unavailable_error` or a substring”.
- Result is limited to these eight mutants: **8 killed, 0 survived, 0 inconclusive**. This is not a whole-round admission judgment or proof against all weak matchers.

## Method and exact detector

Copied the entire `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/` directory with `shutil.copytree` into nine independent scratch trees under `/tmp/kama-r16-MutateMatcher/`: one shared pristine baseline and eight subjects. Every initial copy had the same four file hashes as the source. Only each subject’s `tools/kama-probe.sh` was mutated. Single-line/predicate edits and the six-line branch move used the surgical edit tool; inverse edits restored the original bytes.

Executed exactly **17** full-matrix invocations: one pristine, eight mutated, eight restored. Independent subjects ran concurrently with eight worker slots. Every invocation had a 360-second outer bound; the unchanged harness applies a 30-second bound to each probe call. No `--only`, altered fixture, alternate detector, or retry of a failed detector was used.

Each invocation used this argv, with the absolute probe path listed below substituted literally:

```text
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py --probe PROBE --json
```

Only these environment overrides were supplied (the rest of the environment was inherited, not printed):

```text
KAMA_PROBE_TMPDIR=/tmp/kama-r16-MutateMatcher/runtime
TMPDIR=/tmp/kama-r16-MutateMatcher/runtime
PYTHONDONTWRITEBYTECODE=1
```

Captured stdout JSON and stderr through file handles under `/tmp/kama-r16-MutateMatcher/runs/`, using `<run-label>.json` and `<run-label>.stderr.txt`. Raw scratch captures were removed after their results, names, hashes and excerpts were retained in this report. Those removed paths are not durable evidence pointers.

Expected detector: pristine/restored runs exit **0** with `tests=72 passes=72 failures=0`; an invalid classifier returns suite exit **1** because at least one graded verdict/reason differs. The failing probe calls themselves still exit **2** with `drift=true`; these are behavioral kills, not crashes, parse faults or timeout kills.

### Commands, exits and actual output excerpts

For every row, the command is the exact argv above with the table’s absolute `PROBE`. Mutant rows were executed once as mutated and once again, at the same path, after exact restoration.

| Run | Absolute PROBE | Suite exit | Actual stderr summary |
|---|---|---:|---|
| baseline | `/tmp/kama-r16-MutateMatcher/baseline/tools/kama-probe.sh` | 0 | `tests=72 passes=72 failures=0` |
| m01-drop-type | `/tmp/kama-r16-MutateMatcher/m01-drop-type/tools/kama-probe.sh` | 1 | `tests=72 passes=70 failures=2` |
| m02-drop-message | `/tmp/kama-r16-MutateMatcher/m02-drop-message/tools/kama-probe.sh` | 1 | `tests=72 passes=65 failures=7` |
| m03-substring-loading | `/tmp/kama-r16-MutateMatcher/m03-substring-loading/tools/kama-probe.sh` | 1 | `tests=72 passes=70 failures=2` |
| m04-case-insensitive | `/tmp/kama-r16-MutateMatcher/m04-case-insensitive/tools/kama-probe.sh` | 1 | `tests=72 passes=71 failures=1` |
| m05-accept-float | `/tmp/kama-r16-MutateMatcher/m05-accept-float/tools/kama-probe.sh` | 1 | `tests=72 passes=71 failures=1` |
| m06-drop-http-503 | `/tmp/kama-r16-MutateMatcher/m06-drop-http-503/tools/kama-probe.sh` | 1 | `tests=72 passes=65 failures=7` |
| m07-loading-after-html | `/tmp/kama-r16-MutateMatcher/m07-loading-after-html/tools/kama-probe.sh` | 1 | `tests=72 passes=71 failures=1` |
| m08-any-error-dict | `/tmp/kama-r16-MutateMatcher/m08-any-error-dict/tools/kama-probe.sh` | 1 | `tests=72 passes=58 failures=14` |
| restored-m01-drop-type | `/tmp/kama-r16-MutateMatcher/m01-drop-type/tools/kama-probe.sh` | 0 | `tests=72 passes=72 failures=0` |
| restored-m02-drop-message | `/tmp/kama-r16-MutateMatcher/m02-drop-message/tools/kama-probe.sh` | 0 | `tests=72 passes=72 failures=0` |
| restored-m03-substring-loading | `/tmp/kama-r16-MutateMatcher/m03-substring-loading/tools/kama-probe.sh` | 0 | `tests=72 passes=72 failures=0` |
| restored-m04-case-insensitive | `/tmp/kama-r16-MutateMatcher/m04-case-insensitive/tools/kama-probe.sh` | 0 | `tests=72 passes=72 failures=0` |
| restored-m05-accept-float | `/tmp/kama-r16-MutateMatcher/m05-accept-float/tools/kama-probe.sh` | 0 | `tests=72 passes=72 failures=0` |
| restored-m06-drop-http-503 | `/tmp/kama-r16-MutateMatcher/m06-drop-http-503/tools/kama-probe.sh` | 0 | `tests=72 passes=72 failures=0` |
| restored-m07-loading-after-html | `/tmp/kama-r16-MutateMatcher/m07-loading-after-html/tools/kama-probe.sh` | 0 | `tests=72 passes=72 failures=0` |
| restored-m08-any-error-dict | `/tmp/kama-r16-MutateMatcher/m08-any-error-dict/tools/kama-probe.sh` | 0 | `tests=72 passes=72 failures=0` |

Other subprocess commands: `python3 --version` exited **0**, output `Python 3.14.8`; `rm -rf -- /tmp/kama-r16-MutateMatcher` exited **0**, no output. The scratch path was subsequently observed absent. Copying, hashing and result aggregation ran in the tool’s Python evaluator rather than additional shell commands.

## Mutants, expected detector and all killing tests

For m01–m06 and m08, every listed killing row actually produced `MODEL_LOADING / llamacpp-loading`, probe exit `2`, `drift=true`, `error=null`, where the fixture expected `FOREIGN_SERVICE`. Unless stated otherwise, the expected reason was `non-2xx-non-model-http`. For m07 the mismatch is reversed as detailed below. Every listed test passed in the shared pristine arm and every restored arm.

### m01-drop-type

- Mutation point: `body_is_llamacpp_loading(), original line 442` in `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh` (line numbers refer to the pristine source).
- Single semantic change: Remove and err.get("type") == "unavailable_error"; retain exact message, integer code and HTTP 503 guards.
- Actual matrix output: `tests=72 passes=70 failures=2`; suite exit **1**; verdict **killed**.
- All killing tests:
  - `ForeignControls.loading-message-wrong-type`.
  - `Overbroad503.server-error-type`.

### m02-drop-message

- Mutation point: `body_is_llamacpp_loading(), original line 442` in `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh` (line numbers refer to the pristine source).
- Single semantic change: Remove the exact message predicate; retain type, integer code and HTTP 503 guards.
- Actual matrix output: `tests=72 passes=65 failures=7`; suite exit **1**; verdict **killed**.
- All killing tests:
  - `ForeignControls.busy-unavailable-error`.
  - `LoadingRace.HealthOkNonLoading503`.
  - `NearMissTriple.message-trailing-period`.
  - `NearMissTriple.message-surrounding-space`.
  - `NearMissTriple.router-stream-owner-loading`.
  - `Overbroad503.no-slot-available`.
  - `Overbroad503.lowercase-loading`.

### m03-substring-loading

- Mutation point: `body_is_llamacpp_loading(), original line 442` in `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh` (line numbers refer to the pristine source).
- Single semantic change: Replace exact message equality with a case-sensitive string substring test for Loading.
- Replacement predicate: `(isinstance(err.get("message"), str) and "Loading" in err["message"])`.
- Actual matrix output: `tests=72 passes=70 failures=2`; suite exit **1**; verdict **killed**.
- All killing tests:
  - `NearMissTriple.message-trailing-period`.
  - `NearMissTriple.message-surrounding-space`.

### m04-case-insensitive

- Mutation point: `body_is_llamacpp_loading(), original line 442` in `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh` (line numbers refer to the pristine source).
- Single semantic change: Replace exact message equality with case-folded equality.
- Replacement predicate: `str(err.get("message")).casefold() == "loading model"`.
- Actual matrix output: `tests=72 passes=71 failures=1`; suite exit **1**; verdict **killed**.
- All killing tests:
  - `Overbroad503.lowercase-loading`.

### m05-accept-float

- Mutation point: `body_is_llamacpp_loading(), original line 443` in `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh` (line numbers refer to the pristine source).
- Single semantic change: Widen the integer type predicate to accept int or float; keep the bool exclusion and equality to 503.
- Replacement predicate: `isinstance(code, (int, float))`.
- Actual matrix output: `tests=72 passes=71 failures=1`; suite exit **1**; verdict **killed**.
- All killing tests:
  - `NearMissTriple.code-float-503.0`.

### m06-drop-http-503

- Mutation point: `classify(), original line 503` in `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh` (line numbers refer to the pristine source).
- Single semantic change: Remove only the HTTP status == 503 guard; retain nonempty-body and exact-envelope checks.
- Replacement predicate: `if [ -s "$FBODY" ] && body_is_llamacpp_loading "$FBODY"; then`.
- Actual matrix output: `tests=72 passes=65 failures=7`; suite exit **1**; verdict **killed**.
- All killing tests:
  - `NonLoadingStatuses.ok200-json-envelope`; expected reason `schema-unrecognized`.
  - `NonLoadingStatuses.ok200-plain-envelope`; expected reason `non-model-2xx`.
  - `NonLoadingStatuses.err500-envelope`.
  - `NonLoadingStatuses.err502-envelope`.
  - `NonLoadingStatuses.err504-envelope`.
  - `NonLoadingStatuses.err404-envelope`.
  - `NonLoadingStatuses.err429-envelope`.

### m07-loading-after-html

- Mutation point: `classify(), original lines 503–508 moved below original lines 549–554` in `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh` (line numbers refer to the pristine source).
- Single semantic change: Move the unchanged MODEL_LOADING branch after the HTML sniff/rejection path, giving html-non-model precedence. This means after the HTML early return, not merely after computing ishtml.
- Actual matrix output: `tests=72 passes=71 failures=1`; suite exit **1**; verdict **killed**.
- All killing tests:
  - `NearMissTriple.exact-envelope-labelled-html`; expected `MODEL_LOADING / llamacpp-loading`, observed `FOREIGN_SERVICE / html-non-model`, probe exit `2`, `drift=true`, `error=null`.

### m08-any-error-dict

- Mutation point: `body_is_llamacpp_loading(), original lines 442–443` in `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh` (line numbers refer to the pristine source).
- Single semantic change: Replace the final exact-triple predicate with acceptance of any dictionary error; the existing top-level/error dictionary guards and HTTP 503 guard remain.
- Replacement predicate: `if isinstance(err, dict):`.
- Actual matrix output: `tests=72 passes=58 failures=14`; suite exit **1**; verdict **killed**.
- All killing tests:
  - `EnvelopeShapes.MissingCode`.
  - `EnvelopeShapes.CodeAsString`.
  - `ForeignControls.busy-unavailable-error`.
  - `ForeignControls.loading-message-wrong-type`.
  - `LoadingRace.HealthOkNonLoading503`.
  - `NearMissTriple.code-float-503.0`.
  - `NearMissTriple.code-boolean-true`.
  - `NearMissTriple.message-trailing-period`.
  - `NearMissTriple.message-surrounding-space`.
  - `NearMissTriple.router-stream-owner-loading`.
  - `Overbroad503.no-slot-available`.
  - `Overbroad503.lowercase-loading`.
  - `Overbroad503.server-error-type`.
  - `Overbroad503.code-string`.

## Hashes and exact restoration

All SHA-256 values below were computed from actual bytes with `hashlib.sha256(Path(...).read_bytes()).hexdigest()`. The detector independently emitted the matching `probe_sha256` for every run.

Common pristine/restored probe SHA-256 (**P**):

```text
6edd3c4cfdf3f86c98202cef58859c29406d4a9cec17495454c514ac5972fa50
```

Each subject started at P. Mutated hash below was unchanged before/after its detector. After the inverse edit, both before/after hashes of every restored detector were P. All other copied tool files stayed at their original hashes. All nine full scratch tool trees matched the source’s four-file hash map before removal.

| Subject | Before mutation | Mutated SHA-256 (before = after detector) | After restoration | Restored detector |
|---|---|---|---|---|
| m01-drop-type | P | `376b5816fe0f8a6dea0d472833e1a6b0e50be87c0e2448b2bb7ff0ee25eabbca` | P | exit 0; 72/72 |
| m02-drop-message | P | `957a97e5425cd2a813f55836ce2fd32be3799846e50cb54201692c389e248f24` | P | exit 0; 72/72 |
| m03-substring-loading | P | `fc0419ed0580ec9b471aa9693d45d3f72933ffd6e32b23a276246a0e0613690a` | P | exit 0; 72/72 |
| m04-case-insensitive | P | `3abcad5347bcd7f1d5667571c791d3fbdec742fa3ba8d7301a85752803fe6716` | P | exit 0; 72/72 |
| m05-accept-float | P | `c1b08e7188f941b840d90c5df5f5d65db0226cff265c96d9511834808d905f61` | P | exit 0; 72/72 |
| m06-drop-http-503 | P | `f429b59e6933fa63541d3730192e32c47c5772e245636638024b1cf2ace8a2b6` | P | exit 0; 72/72 |
| m07-loading-after-html | P | `fb4967c638d22343e2fe3ae7b5ab89c77e3b0fe948533ec94ebf41342c982b79` | P | exit 0; 72/72 |
| m08-any-error-dict | P | `47848ad312398d971a5253d006bdd45ffe171d2379ea623ec05858ae6e2b5505` | P | exit 0; 72/72 |

### Lane tool hashes (before = after)

| Absolute path | SHA-256 |
|---|---|
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py` | `cf95f382032d9c510c5e59124c3fda3a50915c0800fdbcd27ddbd145a9ef39ea` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-evidence.py` | `38d1f5d216181bdb7693582027da83eace707f111f42dd32785d386ffe78fb02` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh` | `6edd3c4cfdf3f86c98202cef58859c29406d4a9cec17495454c514ac5972fa50` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/test-snapshot.sh` | `236c23c12964cf0b2f0a2f970187e216d3398dcf2b92ffb7e8606e0fdd029646` |

### Detector and fixture hashes (pinned during run = after all runs)

| Absolute path | SHA-256 |
|---|---|
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py` | `fd49ff7c0621bf3799c835b8e2baffbac61c35ce8e2c6e91b92fc495ce376140` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/AuthAndDead.json` | `670d539002ecf00579a1529d3a4b5ed0ab50ea645db853cc69cc8e61cf8e5b6a` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/EnvelopeShapes.json` | `c6fe95222039abdb1d21248a9278df9fd20f86a52f19b67973042d2a4e8c814e` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/ForeignControls.json` | `e5d8c201de3ace9d07c70aac49c54c63fa818cf32e6d33e22f230d8a6356e613` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/LoadingEnvelope.json` | `12bc261c595115446dbf592d1ff479c1351229f504a0016f5ef8c0ab05306f03` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/LoadingRace.json` | `5644e10ed47ad8521eeadc3b9137553d5303790447575085580e6570ad95c108` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/NearMissTriple.json` | `9b19301159bcadb03098edef2931998593b5c4c2f028f6ce0c0afb832e8b09db` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/NonLoadingStatuses.json` | `0136baa119aa1e6e74d1423318ddf9275755de0345210601af5765e84e3d922a` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/Overbroad503.json` | `680582e1b6585741cbf20513cc055077812f76e88a20d8e77c8faed9b84744b2` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/ReadyControls.json` | `ef572d186e699ccd1a10728b53e13742800963f2f0aedfd02a7f9f80c133f3ba` |

### Captured stdout JSON identities

Digests identify the actual removed raw captures; the behavioral evidence and summaries are embedded above, not delegated to temporary paths.

| Run label | stdout JSON SHA-256 |
|---|---|
| baseline | `bd7201e7493bd6cf2969e39c3d560b9dbe7f3c0c4d3e091a608de50eaf04c515` |
| m01-drop-type | `d0eaef2ee6082b2aaf75e9710529b3540665bab23eee8745737184d4da5c16df` |
| m02-drop-message | `c216e8a11b83af851625759246e38c5826ed29f24fc92942b334da3b62210f52` |
| m03-substring-loading | `31b76f9fafe18581679fbce5a635c315f8f99e5903f465e34f5868ed308a1e05` |
| m04-case-insensitive | `2605c634c79e69e057fa00d824b4b28cd8404c5009a575872cb10b16efedc426` |
| m05-accept-float | `cc6d0c5d528a6d2f51a464261de604477215283dd0d5b0eec5277673c11f1569` |
| m06-drop-http-503 | `b79f2b1c883dddf947a8e30b40b75f2d256016fad0bea349d73c750c8a9bdd16` |
| m07-loading-after-html | `c0b316b5363f23b09056f0953cfa57157dfe3446f9e7a0436f30ac54f28f5867` |
| m08-any-error-dict | `6c597dba8bcb36d38a82a018e46b4c892d71c4b1b4365a1d7ff54d40fccddbb7` |
| restored-m01-drop-type | `ffbbc176d0f790a69604a0bcdfd299bb4c8442cb5fbcb113e5356b4d121e21b5` |
| restored-m02-drop-message | `fb1043b545dbc5dad231c3954eecdfded6ca3f34d6e4ebcfa7b7fb8ac059efe6` |
| restored-m03-substring-loading | `49993e5e71510e00943276191d31eaf38f108ede1b96cb5e1a33dd67be30ca09` |
| restored-m04-case-insensitive | `a57c802ae7180e4064ed8f0545bd90ca1751977f05bbccaada350dc7518cec87` |
| restored-m05-accept-float | `569d920044ad82948a44d5ca93fb09de30cef2076d3d3020ac7df67cd99787bd` |
| restored-m06-drop-http-503 | `8a73c2b41a84489413a8dcf7f545ce4d304bad63c0aaa5fd02f5cb1365647758` |
| restored-m07-loading-after-html | `1e4f2a100a0538824c7b22a54adcf9cbb345ddeac89af5698881eeadcdca55e6` |
| restored-m08-any-error-dict | `e33340cf617196225eec787e66e53ee1cb6ac7c46f5fc4bf6be6125e9b6feb9a` |

## Restoration, boundaries and limitations

- The pristine arm passed 72/72. Each mutated arm had genuine graded mismatches; each of the eight restored arms passed 72/72. No baseline failure was counted as a kill.
- All 17 detector invocations returned complete 72-row documents: 1,224 case observations across nine families; every `error` field was null. Every recorded port was checked against `{8080, 34113}` and their intersection was empty.
- The lane’s four tool hashes, the unchanged detector hash, and all nine fixture hashes matched after the experiment. No lane source, registry, L1 receipt, fleet state or sibling checkout was edited. The only retained write is this scoped report.
- No llama-server or other model runtime was started. Only the assigned harness’s disposable loopback stubs were used; the harness performs their shutdown/close in its cleanup path. No call to the receipt-rewriting measurement script was made.
- One inverse-edit attempt was refused because the edit anchor’s folded display omitted two moved lines. It applied no edits; refreshed anchors were read and the inverse edit then succeeded. This did not introduce an extra detector attempt.
- `/tmp/kama-r16-MutateMatcher/` was removed after all restores, hashes and restored-arm runs completed; its absence was observed. Raw captures were intentionally not retained elsewhere.
- [INFERENCE] These results support KQ19’s intended resistance to this specific family of weak matchers and ordering regressions. They do not establish mutation completeness, upstream runtime identity, readiness or coverage of a different defect.

## Installs

None. Existing Python 3.14.8 and the existing probe dependencies were sufficient. No package transaction, tool upgrade, service restart or host configuration change was performed.
