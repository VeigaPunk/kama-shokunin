VERDICT: confirm — producer argv is fixed-form, but the gate does not enforce exact equality and its receipt fields do not authenticate execution.

## Findings

### High — argv validation accepts undeclared and duplicate flags

The frozen producer constructs one fixed ordered argv: `[server_real, "-m", args.model, "--alias", args.alias, "--host", "127.0.0.1", "--port", str(port), "-c", str(args.ctx), "-t", str(args.threads), "--no-webui", "--offline"]` (`.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py:1088-1098`; quote: “receipt['argv'] = server_argv”). The validator instead checks individual values using `argv_flag`, which returns the first match (`tests/llamacpp-live/check-receipt.py:169-176`; quote: “for i, a in enumerate(argv[:-1]):”), then checks only the last two entries (`:387-421`; quote: “tail != [\"--no-webui\", \"--offline\"]”). Thus an argv with an extra `--api-key X` before that tail, or a second `--host 0.0.0.0` after the expected first `--host 127.0.0.1`, satisfies these argv predicates. This is not an exact re-derivation; reject unless `argv == expected_argv` (after validating the receipt field types). The task’s required invalidation of every extra/duplicate flag is not currently met.

### Medium — current receipt schema lacks the exact model argv value

The producer records `model.path` as `os.path.realpath(args.model)` (`.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py:1054-1057`; quote: “'path': os.path.realpath(args.model)”), but puts the original `args.model` in the child argv (`:1088-1090`; quote: “'-m', args.model”). A gate deriving `-m` from `model.path` therefore rejects a legitimate run invoked with a relative or symlink model path; deriving it from the receipt’s existing `argv` would be circular. To support exact equality from receipt fields, either make the producer pass the canonical `model.path` to `llama-server`, or add a separately validated receipt field such as `model.argv_path` for the original CLI argument.

## Exact re-derivation contract

After checking types/ranges for all values, compare the whole argv list, in order, against:

```python
expected_argv = [
    receipt["server"]["realpath"],
    "-m", receipt["model"]["argv_path"],  # or model.path after producer normalization
    "--alias", receipt["alias"],
    "--host", "127.0.0.1",
    "--port", str(receipt["port"]),
    "-c", str(receipt["ctx"]),
    "-t", str(receipt["threads"]),
    "--no-webui", "--offline",
]
if receipt["argv"] != expected_argv:
    invalid("argv differs from exact producer argv")
```

The receipt inputs required are `server.realpath`, an exact model argv path (missing in the current schema; see finding above), `alias`, `port`, `ctx`, and `threads`. All remaining tokens/values and their ordering are constants. `server.realpath`, not `server.arg`, supplies argv[0] (`.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py:998-1004,1046-1053,1088-1091`).

There are no server-argv flags whose *presence* depends on these CLI options: `--ctx` and `--threads` always emit `-c` and `-t`, and `--port` always emits `--port` for either an explicit or selected port (`.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py:959-969,1033-1034,1088-1097`). `--server` changes argv[0] via resolved `server_real`; `--model`, `--alias`, `--port`, `--ctx`, and `--threads` supply the values above. `--ready-timeout` is not a server flag: it is passed to `readiness_loop` (`:961-962,1143-1144`). `--probe`, `--out`, and `--model-sha256` do not enter this server argv construction.

## Forgery / residual risk

Yes, a forged receipt can still be internally consistent with exact argv re-derivation: that comparison would prove only that its argv matches its own declared inputs, not that the process ran with them. The gate’s `--expect-model-sha256`, `--expect-server-sha256`, `--expect-probe-sha256`, and `--expect-tool-sha256` are optional (`tests/llamacpp-live/check-receipt.py:1358-1392`; quote: “ap.add_argument(\"--expect-model-sha256\"”), and digest fields are otherwise shape-checked rather than checked against an independently trusted source (`:273-277,319-322,339-342,350-363`). [INFERENCE] A self-authored receipt can claim mutually consistent inputs and observations; exact argv equality alone is not provenance or proof of launch. Trusted expected digests / an external authenticated record are needed if the gate must attest to a particular binary, model, or harness.

## Verification gaps and limitations

- No working-tree diff for `tools/kama-llamacpp-live.py` or `tests/llamacpp-live/check-receipt.py` was present at review time; this report analyzes the frozen producer and current gate.
- No `lsp` device is mounted (`read xd://lsp` returned “No such tool”); therefore no LSP status/references/definition/diagnostics were available. Static conclusions above are based on the cited source lines, not grep as semantic proof.
- No runtime test or lane gate was run; this was a read-only scoped review.
- Installs/updates: none.
