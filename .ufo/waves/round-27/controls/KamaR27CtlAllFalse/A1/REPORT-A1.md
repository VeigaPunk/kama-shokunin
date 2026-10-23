# KamaR27CtlAllFalse — A1 re-score

- Best score, registered/counted: **40/0**.
- Meets target: **no** (`0 < 15`).
- Mutant verdict: **killed**. The eight source-misattribution rows that counted under A0 now fail clause **(d)**; all 40 all-false rows are rejected.
- Fresh sandbox: `/fast/scratch/hyaku/kama-r27/KamaR27CtlAllFalse-A1`.
- Measured amendment commit: `6020243e74a470507b9d6d89cd7904b8a878d39b`.
- Unmodified counter SHA-256, checked before each stage: `780c915672177f7d673eecec1bf2204aaf39c3c4ca837f23335c2995513885a6`.
- No new uniqueness-surviving source-misattribution row was constructed in the bounded search below. This is not a proof against every dynamic-message construction.

## Control shape

Replayed the exact A0 40-row registry, including all eight previously counted shared-word/different-raising-site cases and the 32 healthy/wrong-endpoint/nonmatching-error cases. The registry hash remains `6dbfe1cf3b86f2cd4cd5b73ed642efcc80f25c493edc4febdb0a42e5129d40c3`.

Only the SKILL table header was adapted relative to the A0 control:

```text
| id | signature | trigger | meaning | next action | source |
```

The data rows, requests, controls, signatures, source citations, meaning and next-action prose were otherwise unchanged. The original rows already had six cells and meaning/action cells exceeding six words. The 40 S900–S939 source rows were replayed unchanged. There are 35 entire decoded source literals and five source-literal substring probes.

Axes: depth challenged through source attribution; calibration by distinguishing the observed rejection from an unproven global safety claim; operability by pristine/mutated/restored runs and exact restoration.

## Additional misattribution search

Searched the 16 files in the counter's pinned snapshot, not unpinned neighboring source files. Compared 299 direct `throw`/`format_error_response` string literals of at least 20 bytes against joined literals from eight multiline raising expressions. Matching blocks of at least 20 bytes were screened for newline/pipe exclusions and per-line uniqueness across all pinned files. This specifically tested the possibility that another error builds an otherwise unique literal fragment across multiple source lines. **No candidate passed that search.**

Also opened the dynamic `throw`/`string_format`/error-response expressions, request wrappers, chat type/tool parsers and GCP compatibility dispatch. No additional wrong-site request was constructed that passed uniqueness. No fabricated or merely genuine-trigger rows were substituted to increase the score. No extra runtime rows were added. `uniqueness-search.json` records the observed search output and its bounded scope.

## Detector and actual outputs

All stages used the same frozen bounded command from the fresh sandbox; only the output receipt filename changed:

```sh
flock /fast/scratch/hyaku/kama-r27/counter.lock timeout 900 python3 .ufo/waves/round-27/count-c1.py --lane . --repo . --out <stage-receipt.json>
```

`run-counter.py` captures exact stdout/stderr/exit status and before/after hashes, with a 16-GiB address-space cap, no core dumps and a 1024 descriptor cap. The counter itself re-executes under `python3 -I -S` as required by A1. No counter file, pinned source file, runtime binary or fixture model was modified. No manual llama-server was launched; the counter owns server creation and process-group cleanup. Its successful populated run enforces process identity, model identity and server-port closure. Registered consumer ports were not touched.

| Stage | Exit | Registered | Counted | Target met | Recorded seconds |
|---|---:|---:|---:|---|---:|
| pristine | 0 | 0 | 0 | false | 0.113 |
| replay40 | 0 | 40 | 0 | false | 5.596 |
| restored | 0 | 0 | 0 | false | 0.096 |

Pristine and restored stdout, verbatim:

```text
registered 0 counted 0 target 15 met False not-counted []
```

Mutated stdout, verbatim:

```text
registered 40 counted 0 target 15 met False not-counted ['E27-00', 'E27-01', 'E27-02', 'E27-03', 'E27-04', 'E27-05', 'E27-06', 'E27-07', 'E27-08', 'E27-09', 'E27-10', 'E27-11', 'E27-12', 'E27-13', 'E27-14', 'E27-15', 'E27-16', 'E27-17', 'E27-18', 'E27-19', 'E27-20', 'E27-21', 'E27-22', 'E27-23', 'E27-24', 'E27-25', 'E27-26', 'E27-27', 'E27-28', 'E27-29', 'E27-30', 'E27-31', 'E27-32', 'E27-33', 'E27-34', 'E27-35', 'E27-36', 'E27-37', 'E27-38', 'E27-39']
```

All stderr files are empty. No stage reported `could_not_evaluate`. The populated replay sent every row/control pair: all 40 controls returned 200. Empty-registry pristine/restored paths validate pins and return before the HTTP baseline; they did not fail evaluation.

Expected detector result: reject all 40 false fault claims. Observed result: all rejected. The prior eight rows still produced the matching live error strings, so their loss of credit is specifically the new source-literal uniqueness guard, not a healthy request, missing table row, failing control or unevaluated server.

## Every row's observed reason

No row counted. All controls returned 200. The receipt stores exact messages and response hashes. The source-site strings below are the counter's observed `why` values, not inferred execution traces.

| Row | Request status | why |
|---|---:|---|
| E27-00 | 500 | `["d:literal-not-unique:chat.cpp:874"]` |
| E27-01 | 400 | `["d:literal-not-unique:llama-grammar.cpp:1229"]` |
| E27-02 | 400 | `["d:literal-not-unique:json-schema-to-grammar.cpp:627"]` |
| E27-03 | 400 | `["d:literal-not-unique:server-common.cpp:1390"]` |
| E27-04 | 500 | `["d:literal-not-unique:server-common.cpp:1346"]` |
| E27-05 | 400 | `["d:literal-not-unique:sampling.cpp:197"]` |
| E27-06 | 400 | `["d:literal-not-unique:server-common.cpp:1440"]` |
| E27-07 | 500 | `["d:literal-not-unique:chat.cpp:585"]` |
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
| E27-23 | 200 | `["d:literal-not-unique:chat.cpp:347", "e:not-shown"]` |
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

## Weakness finding / boundary

No A1 numeric-counter bypass was found in this probe. Clause **(d)** kills all eight A0 **(d/e)** causal-misattribution examples; **(e)** continues to reject healthy or nonmatching requests. A1 explicitly excludes prose correctness from the counted predicate, so the previously identified wrong-remedy weakness of (a) is not presented as a new A1 counter failure. No contract repair or claim judgment was performed.

## Exact restoration

Removed only the two appended control sections and newly created registry. Restored stage hashes match pristine stage hashes exactly; the counter hash remained the A1 pin throughout.

| File | Pristine SHA-256 | Mutated SHA-256 | Restored SHA-256 |
|---|---|---|---|
| SKILL.md | `6127e49f1c7c38a05c5154c5e3f926c99ad7d6fe3ccb6c30d58b0aefa0fa7747` | `d58f710219c70bfae189dd30a6ba1998d9835923fc801218f86d504209a1398d` | `6127e49f1c7c38a05c5154c5e3f926c99ad7d6fe3ccb6c30d58b0aefa0fa7747` |
| corpus/SOURCES.md | `1e26818e85aa8e6d45fd0c6c2014f320a5b35f87a96a06e6f5d5ff47c64f8cf2` | `433badcf13d2455de8ef7bdcd455948b2a3724d2444d2c6011d41e9c509219ec` | `1e26818e85aa8e6d45fd0c6c2014f320a5b35f87a96a06e6f5d5ff47c64f8cf2` |
| registry/error-signatures-r27.json | absent | `6dbfe1cf3b86f2cd4cd5b73ed642efcc80f25c493edc4febdb0a42e5129d40c3` | absent |

No sandbox change was integrated, committed or shipped. All lane writes were restricted to this seat's evidence directory.

## Evidence

Within this `A1/` directory:

- `control-registry.json`: exact scored 40-row replay.
- `replay40-control.diff`: actual sandbox SKILL/SOURCES diff captured before scoring.
- `replay40-receipt.json`: score and all per-row live observations/reasons.
- `pristine-receipt.json`, `restored-receipt.json`: identical detector on pristine/restored input bytes.
- `*-run.json`: exact argv, hashes, stdout/stderr, exit codes and caps; `*-stdout.txt`, `*-stderr.txt`, `*-exit-code.txt`: standalone output copies.
- `uniqueness-search.json`: bounded additional-candidate search result.
- `run-counter.py`: recorder, not a modified counter copy. The original A0 control rationale and construction provenance remain in the parent evidence directory.

Tool installs/updates: **none**. No builds, linters or unrelated checks were run. Assigned A1 re-score complete.
