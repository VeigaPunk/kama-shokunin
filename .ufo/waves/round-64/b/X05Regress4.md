# X05Regress4 - round 64 wave b, C2 sensitivity part 4 (advisory)

Deliverable: `.ufo/waves/round-64/b/out/X05Regress4/capability-regress-r64.part4.tsv` (3 rows, TAB-separated cap/tool_path/find/replace, no header, 4 cells per row, no tabs in cells). Receipts: `out/X05Regress4/receipts/`.

Method: %T = `git archive f6a4ea9a` tree (the tip tree); mutated copy = hardlink copy with only the bound tool rewritten (one `str.replace`, count asserted == 1, `ast.parse` OK so the file stays importable). Run template executed through `bash -c` in an `env -i PATH HOME LANG TMPDIR` environment, cwd = tree, same placeholders as the r63 counter (%S = fresh scratch). Verdict = pattern in stdout+stderr and exit 0 (r63 `verdict_fn`). No lane file edited; no lane git use beyond read-only `git archive/show`.

## Per-row evidence

| cap | find (occurrences in tip blob: find / replace) | unmutated | mutated | verdict |
|---|---|---|---|---|
| append-only-audit | `if not wild and fnmatch.fnmatchcase(decl_path, pattern):` -> `if wild and ...` in `binds()` (1 / 0) | `AOA_SELFTEST pass=51 fail=0`, rc 0 | `AOA_SELFTEST pass=50 fail=1` (FAIL binding-v4), rc 1 | pattern `AOA_SELFTEST pass=` still PRESENT but exit 0 -> 1: flips on exit code (the pattern alone cannot flip it) |
| live-receipt-replay | `if rerun.get("outcome") != orig.get("outcome"):` -> `==` in `compare()` (1 / 0) | `KLR_SELFTEST pass=48 fail=0`, rc 0 | `KLR_SELFTEST pass=42 fail=6`, rc 1 | pattern absent AND exit 1 |
| live-ollama-lifecycle | `check('running-exe-digest', exe_sha == pin['bin_sha256'],` -> `!=` (1 / 0) | `"verdict": "MODEL_OK"`, rc 0 (real pinned Ollama v0.40.11, nonce ctrun0001) | `"verdict": "FAIL"`, only failing check `running-exe-digest`, rc 1 | pattern absent AND exit 1 |

All three live in the real run template (`kama-ollama-live.py --work %S/ollama --nonce ctrun0001` ran live, ~8 s, ports free-picked, torn down by the tool).

## Survivors / observations (data, not claims)
- Candidate `MUTABLE_COLS = (7, 9, 10)` -> `(7, 9)` in append-only-audit: SURVIVED (`pass=51 fail=0`, rc 0): the selftest battery does not exercise the used-by column as mutable. Not used for the row. It is a coverage gap, not a defect finding on the claim.
- A mutation of only the final `return 0 if fails == 0 else 1` was not used (it would test the exit line, not behavior).
- append-only-audit's pattern `AOA_SELFTEST pass=` is non-discriminating by itself (prints whatever the count); sensitivity of the r64 row rests entirely on the exit code, so the counter's verdict function MUST keep `rc == 0`. A printer for that row only needs to echo `AOA_SELFTEST pass=` - the counter's printer control must run the printer with exit 0 and still reject it by the regress flip, not by pattern.
- No flake observed; each mutant run once, unmutated baseline run once (all three outputs in receipts/).
- Tools installed: none.

Counter line for the three rows: regress_flipped(part4)=3/3 (aoa rc1, klr pass=42 fail=6 rc1, ollama FAIL rc1); no row reported as unflippable.
