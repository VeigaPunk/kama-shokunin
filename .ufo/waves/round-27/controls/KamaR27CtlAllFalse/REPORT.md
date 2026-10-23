# KamaR27CtlAllFalse — all-false control

- Best score, registered/counted: **40/8**.
- Meets target: **no** (`8 < 15`).
- Mutant verdict: **survived partially** — eight false cited-fault attributions counted; the other 32 were rejected.
- Frozen lane commit: `530eaa998735d226ec90cea9b0cf4242a6b9cb01`.
- Frozen counter SHA-256, before every scoring command and unchanged afterward: `382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6`.
- This is a coverage finding, not a claim-admission judgment or permission to alter the predicate. No counter bytes, source snapshot, runtime binary, fixture model, lane history or fleet history were changed.

## Control shape and what was tried

Axes: C1 **depth**, challenged by false causal attribution; **calibration**, by reporting literal matching separately from genuine fault knowledge; **operability**, by running the identical bounded counter on pristine, mutated and restored inputs.

One isolated sandbox was cloned from the lane and checked out at the frozen commit: `/fast/scratch/hyaku/kama-r27/KamaR27CtlAllFalse`. Git environment overrides were cleared. Only a new registry and appended SKILL/SOURCES sections changed in that sandbox.

The registry has 40 rows, each citing an opened `throw` or `format_error_response` line in the pinned 704366d snapshot, a new S900–S939 row, and a six-cell SKILL row with a distinct actionable next-action cell. **35 signatures are entire decoded source literals**; five are deliberately selected literal substrings of at least 20 UTF-8 bytes. This exceeds the requested 20 genuine literals without counting the substring probes toward that floor.

Eight rows deliberately cite one error branch while inducing a different error containing the same words. The remaining 32 use healthy requests, wrong endpoints, or nonmatching errors. The strongest candidates were placed first so ordinary negatives could not consume the one-fault/one-row allowance. All 40 per-row controls returned 200. All 32 rejected rows have exactly `why: ["e:not-shown"]`; no malformed source/table row prevented their evaluation.

Expected semantic detector: reject every request that does not reach its claimed cited fault. The frozen literal predicate actually accepts the eight overlap cases below. This is **not** an implementation/predicate mismatch: clauses (d) and (e) require literal membership and live substring occurrence independently, not proof that the cited raising site ran.

## Same bounded detector, actual outputs

Each stage used this command from the sandbox, with only its receipt filename differing:

```sh
flock /fast/scratch/hyaku/kama-r27/counter.lock timeout 900 python3 .ufo/waves/round-27/count-c1.py --lane . --repo . --out <stage-receipt.json>
```

`run-counter.py` records stdout, stderr, exit code, elapsed time and before/after hashes. It applies a 16-GiB address-space cap, disables core dumps, caps descriptors at 1024, and bounds lock-plus-command time. No manual llama-server was launched. The unmodified counter owns loopback server argv/ports and closes each server process group via `Server.stop()` before successful completion; its source fixes ports 47600–47619. No registered consumer port was touched.

| Stage | Exit | Registered | Counted | Target met | Recorded elapsed seconds |
|---|---:|---:|---:|---|---:|
| pristine | 0 | 0 | 0 | false | 0.063 |
| all-false | 0 | 40 | 8 | false | 70.742 |
| restored | 0 | 0 | 0 | false | 3.533 |

Pristine and restored output, verbatim:

```text
registered 0 counted 0 target 15 met False not-counted []
```

Mutated output, verbatim:

```text
registered 40 counted 8 target 15 met False not-counted ['E27-08', 'E27-09', 'E27-10', 'E27-11', 'E27-12', 'E27-13', 'E27-14', 'E27-15', 'E27-16', 'E27-17', 'E27-18', 'E27-19', 'E27-20', 'E27-21', 'E27-22', 'E27-23', 'E27-24', 'E27-25', 'E27-26', 'E27-27', 'E27-28', 'E27-29', 'E27-30', 'E27-31', 'E27-32', 'E27-33', 'E27-34', 'E27-35', 'E27-36', 'E27-37', 'E27-38', 'E27-39']
```

All three stderr files are empty. No stage reported `could_not_evaluate`. The empty-registry pristine/restored paths validate pins and return before launching HTTP baselines; the populated mutated run executes the counter's healthy baseline and all row/control pairs.

## Counted rows and why they counted

All rows below have observed `why: []`, control status 200, and an observed error message containing the selected signature. Source-path attribution is **[INFERENCE] from the opened pinned guards**, not an instrumented execution trace. The counter receipt contains the exact HTTP messages and response hashes.

| Row | Cited source / signature | Observed status and message | Why the cited fault is false despite counting |
|---|---|---|---|
| E27-00 | chat.cpp L857 / `Unknown reasoning format` | 500: `Unknown reasoning format: all-false-unknown` | Cites enum-to-name formatting, but invalid request text follows the string-to-enum rejection at L874. The entire L857 literal is a prefix of L874's message. |
| E27-01 | sampling.cpp L279 / `failed to parse grammar` | 400: `Failed to initialize samplers: failed to parse grammar: llguidance is not enabled` | Cites ordinary GBNF initialization failure. `%llguidance` instead selects the unavailable-backend branch at L221 and throws before L279. |
| E27-02 | json-schema-to-grammar.cpp L492 / `unbalanced parentheses` | 400: `Field 'json_schema': "json_schema": JSON schema conversion failed:\nInvalid pattern ^($: unbalanced parentheses` | Cites an excess closing parenthesis/depth underflow. The pattern has an unmatched opening parenthesis and reaches the final-depth check at L627, not L492. The advised removal of an excess closing parenthesis is wrong. |
| E27-03 | chat.cpp L347 / `Expected 'messages' to be an array` | 400: `Expected 'messages' to be an array` | Cites the lower-level parser, whose full literal continues `, got `. The earlier server-common.cpp L1390 guard emits the selected prefix without reaching that parser. |
| E27-04 | server-common.cpp L1343 / `param requires --jinja flag` | 500: `tool_choice param requires --jinja flag` | No tools array exists. `tool_choice=required` under `no-jinja` reaches L1346, not L1343's nonempty-tools condition. |
| E27-05 | arg.cpp L2101 / `must be finite and greater than 0` | 400: `Failed to initialize samplers: penalty_repeat must be finite and greater than 0` | Cites CLI startup argument parsing, but the row controls no argv. Request `repeat_penalty=0` instead fails sampling.cpp L197. |
| E27-06 | chat.cpp L607 / `d continue_final_message` | 400: `Cannot set both add_generation_prompt and continue_final_message to true.` | Cites invalid continuation type/spelling, yet sends a valid boolean. The mutual-exclusion guard at server-common.cpp L1440 emits the selected substring. Including the preceding `d ` avoids treating the request key alone as an echoed signature. |
| E27-07 | chat.cpp L1037 / `Failed to parse tool` | 500: `Failed to parse tools: Expected 'tools' to be an array, got {"not":"an-array"}; tools = {\n  "not": "an-array"\n}` | Cites returned tool-call argument JSON parsing, but sends no tool-call arguments. The malformed request tools container fails L562 and is wrapped at L585; its prefix matches the source substring. |

## Weaknesses found, by clause

- **(d) + (e), E27-05:** valid source-literal citation and a matching live message do not bind the request to the cited source site. A startup-only CLI error can receive request-validation credit through a shared sampler-error suffix. E27-00–07 provide eight distinct examples; E27-07 even crosses model-output parsing and request-container validation.
- **(a), E27-02:** table shape and six-word next action do not establish that the meaning/remedy applies. The counted row says to remove an excess closing parenthesis although the live pattern is missing one. E27-04 also recommends removing tools that are absent.
- The literal uniqueness checks in **(h)** did not reject these eight distinct signatures/messages/source locations. This run does not establish a same-fault duplication bypass of (h), nor does it establish a target-meeting all-false control.

No repair was attempted. Healthy and genuinely nonmatching full literals were correctly rejected by (e).

## Every row's observed `why`

`[]` means counted. All controls returned 200. A 200 request has no JSON error message; a 400/500 rejection below returned a different error that lacked that row's full signature.

| Row | Request status | why |
|---|---:|---|
| E27-00 | 500 | `[]` — counted; shared prefix, details above |
| E27-01 | 400 | `[]` — counted; unavailable-backend/GBNF collision |
| E27-02 | 400 | `[]` — counted; opening/closing-parenthesis collision |
| E27-03 | 400 | `[]` — counted; early/lower-level guard collision |
| E27-04 | 500 | `[]` — counted; tools/tool_choice collision |
| E27-05 | 400 | `[]` — counted; CLI/sampler collision |
| E27-06 | 400 | `[]` — counted; invalid-value/mutual-exclusion collision |
| E27-07 | 500 | `[]` — counted; output-arguments/request-tools collision |
| E27-08 | 200 | `["e:not-shown"]` |
| E27-09 | 200 | `["e:not-shown"]` |
| E27-10 | 200 | `["e:not-shown"]` |
| E27-11 | 200 | `["e:not-shown"]` |
| E27-12 | 500 | `["e:not-shown"]` |
| E27-13 | 200 | `["e:not-shown"]` |
| E27-14 | 500 | `["e:not-shown"]` |
| E27-15 | 500 | `["e:not-shown"]` |
| E27-16 | 200 | `["e:not-shown"]` |
| E27-17 | 400 | `["e:not-shown"]` |
| E27-18 | 200 | `["e:not-shown"]` |
| E27-19 | 200 | `["e:not-shown"]` |
| E27-20 | 200 | `["e:not-shown"]` |
| E27-21 | 200 | `["e:not-shown"]` |
| E27-22 | 200 | `["e:not-shown"]` |
| E27-23 | 200 | `["e:not-shown"]` |
| E27-24 | 400 | `["e:not-shown"]` |
| E27-25 | 400 | `["e:not-shown"]` |
| E27-26 | 200 | `["e:not-shown"]` |
| E27-27 | 200 | `["e:not-shown"]` |
| E27-28 | 200 | `["e:not-shown"]` |
| E27-29 | 400 | `["e:not-shown"]` |
| E27-30 | 200 | `["e:not-shown"]` |
| E27-31 | 200 | `["e:not-shown"]` |
| E27-32 | 200 | `["e:not-shown"]` |
| E27-33 | 200 | `["e:not-shown"]` |
| E27-34 | 400 | `["e:not-shown"]` |
| E27-35 | 200 | `["e:not-shown"]` |
| E27-36 | 400 | `["e:not-shown"]` |
| E27-37 | 200 | `["e:not-shown"]` |
| E27-38 | 200 | `["e:not-shown"]` |
| E27-39 | 200 | `["e:not-shown"]` |

## Exact restoration evidence

The two appended sections and new registry were removed after scoring. The restored counter run records the original hashes again; the counter's own hash never changed. Probe-created Python import bytecode and its empty directory were removed. No sandbox changes were shipped or integrated.

| File | Pristine SHA-256 | Mutated SHA-256 | Restored SHA-256 |
|---|---|---|---|
| SKILL.md | `6127e49f1c7c38a05c5154c5e3f926c99ad7d6fe3ccb6c30d58b0aefa0fa7747` | `88a873d3a51cc9545c15f35a8e67687f615a3c06904788364c015cd2970a705c` | `6127e49f1c7c38a05c5154c5e3f926c99ad7d6fe3ccb6c30d58b0aefa0fa7747` |
| corpus/SOURCES.md | `1e26818e85aa8e6d45fd0c6c2014f320a5b35f87a96a06e6f5d5ff47c64f8cf2` | `433badcf13d2455de8ef7bdcd455948b2a3724d2444d2c6011d41e9c509219ec` | `1e26818e85aa8e6d45fd0c6c2014f320a5b35f87a96a06e6f5d5ff47c64f8cf2` |
| registry/error-signatures-r27.json | absent | `6dbfe1cf3b86f2cd4cd5b73ed642efcc80f25c493edc4febdb0a42e5129d40c3` | absent |

## Evidence files

All paths below are relative to this evidence directory:

- `control-registry.json`: scored 40-row registry; `control.diff`: actual sandbox `git diff -- SKILL.md corpus/SOURCES.md` captured before the mutated run.
- `row-intent.json`: source line text, complete-literal/subsequence distinction, false-fault rationale and request for each row.
- `all-false-receipt.json`: authoritative score, per-row HTTP status/message, response hashes and `why` arrays.
- `pristine-receipt.json`, `restored-receipt.json`: identical counter runs on original/restored input bytes.
- `pristine-run.json`, `all-false-run.json`, `restored-run.json`: exact argv, stdout, stderr, exit code and stage hashes; matching `*-stdout.txt`, `*-stderr.txt`, `*-exit-code.txt` are standalone copies.
- `restoration-evidence.json`: before/mutated/restored hash manifest.
- `SKILL.md`, `SOURCES.md`: exact pristine backup bytes. `build-control.py` and `run-counter.py`: construction/recording provenance, not modified counter copies.

Tool installs/updates: **none**. No builds, linters or unrelated tests were run. Assigned mutation probe complete.
