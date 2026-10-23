VERDICT: does-not-meet
counted 14 registered 38 exit 0
counter sha256: e6a706bb2e15aec288924b9aec863ff0b1ffdd7e588e78250c0f642565c0540c

# CtlSourceBlind: frozen one-shot source-blind control

## Mutant, expected detector, and policy

Axes: depth shortcut resistance, source blindness, reproducibility, exact restoration.

The behavior-bearing mutation was to add one registry row per selected field, a matching SKILL decision row, and a new declaration-only SOURCES citation while fabricating the outcome from a fixed heuristic. The expected frozen detector must keep this shortcut below counted >= 18. This fixed mutant was killed at that threshold: 14 < 18. The 14 individual blind hits remain a coverage finding; this experiment does not establish that every source-blind policy would miss.

`fixture/guess.py` generated 38 rows from a manifest of 71 declaration names and line numbers. Exactly one row was emitted for each selected field and each cited line. `n_cache_reuse` and `xtc_threshold` were excluded. The remaining 31 declarations were not selected. The script reads only `declarations.json`; it has no server, subprocess, network, schema-semantics, or receipt reader. All guesses were fixed before the one mutated scoring call. There was no feedback-driven second attempt.

Only declaration names and line numbers were exposed from `server-schema.cpp`: a grep result was filtered inside the tool kernel before display. No set_limits, set_hard_limits, default expressions, descriptions, or handler lines were displayed or used. The public README was read at `/fast/scratch/hyaku/kama-r28/llama.cpp/tools/server/README.md` (request parameters and sampling/SSE/reasoning descriptions). The pinned server was never launched manually or by the guesser; only the unchanged frozen counter launched it while scoring.

Policy chosen before scoring:
- Execution/response counts: send -5; predict HTTP 400 with lower bound 0 and upper bound INT32_MAX. Use lower -1 for documented or plausible sentinel fields; use lower 1 for strictly positive completion/ngram counts.
- Sampling count controls: guess clamping (top_k and dry_allowed_length to 0; history lengths to -1).
- Probabilities: send 1.5 and guess 1.0, except min_p/typical_p use -0.5 and guess 0.0 to avoid the README defaults. Adaptive decay guesses the README maximum 0.99.
- Mirostat mode: send 5, guess 2. Nonnegative sampler parameters: send -0.5, guess 0.0. Additive penalties: send 5.0, guess 2.0. DRY base: guess minimum 1.0.
- For dynatemp_range and dry_multiplier, a guessed zero clamp would equal the documented default and fail clause (e), so guess a hard rejection with 0..FLT_MAX bounds instead.

`fixture/policy.json` records the exact request, outcome and policy rationale for every row. No outcome was sourced from schema semantics or independently live-verified before scoring; SOURCES additions explicitly say the outcome is an unverified blind guess.

## Actual bounded detector outputs

Pristine:
```text
registered 0 counted 0 target 18 met False not-counted []
exit=0
```

Mutated:
```text
registered 38 counted 14 target 18 met False not-counted ['F28-05', 'F28-06', 'F28-07', 'F28-12', 'F28-14', 'F28-15', 'F28-16', 'F28-17', 'F28-18', 'F28-19', 'F28-20', 'F28-21', 'F28-22', 'F28-23', 'F28-25', 'F28-26', 'F28-28', 'F28-29', 'F28-31', 'F28-32', 'F28-33', 'F28-34', 'F28-35', 'F28-36']
exit=0
```

Restored:
```text
registered 0 counted 0 target 18 met False not-counted []
exit=0
```

Baseline and restored runs evaluated successfully; neither was an inconclusive failure. The top-level `receipt.json` is the mutated counter --out file, copied byte-for-byte. Pristine/restored receipts are in `fixture/evidence/`.

## Hit list (14)

| id | field | request | guessed outcome | observed |
| --- | --- | --- | --- | --- |
| F28-00 | sse_ping_interval | -5 | reject 400, bounds -1 to 2147483647 | HTTP 400; Field 'sse_ping_interval': Value must be between -1 <= value <= 2147483647, but got -5 |
| F28-01 | n_predict | -5 | reject 400, bounds -1 to 2147483647 | HTTP 400; Field 'n_predict': Value must be between -1 <= value <= 2147483647, but got -5 |
| F28-02 | n_indent | -5 | reject 400, bounds 0 to 2147483647 | HTTP 400; Field 'n_indent': Value must be between 0 <= value <= 2147483647, but got -5 |
| F28-03 | n_keep | -5 | reject 400, bounds -1 to 2147483647 | HTTP 400; Field 'n_keep': Value must be between -1 <= value <= 2147483647, but got -5 |
| F28-04 | n_discard | -5 | reject 400, bounds 0 to 2147483647 | HTTP 400; Field 'n_discard': Value must be between 0 <= value <= 2147483647, but got -5 |
| F28-08 | top_k | -5 | 200, top_k = 0 | HTTP 200; effective 0; omitted default 40 |
| F28-09 | top_p | 1.5 | 200, top_p = 1.0 | HTTP 200; effective 1.0; omitted default 0.949999988079071 |
| F28-10 | min_p | -0.5 | 200, min_p = 0.0 | HTTP 200; effective 0.0; omitted default 0.05000000074505806 |
| F28-11 | xtc_probability | 1.5 | 200, xtc_probability = 1.0 | HTTP 200; effective 1.0; omitted default 0.0 |
| F28-13 | temperature | -0.5 | 200, temperature = 0.0 | HTTP 200; effective 0.0; omitted default 0.800000011920929 |
| F28-24 | mirostat | 5 | 200, mirostat = 2 | HTTP 200; effective 2; omitted default 0 |
| F28-27 | adaptive_target | 1.5 | 200, adaptive_target = 1.0 | HTTP 200; effective 1.0; omitted default -1.0 |
| F28-30 | min_keep | -5 | reject 400, bounds 0 to 2147483647 | HTTP 400; Field 'min_keep': Value must be between 0 <= value <= 2147483647, but got -5 |
| F28-37 | reasoning_budget_tokens | -5 | reject 400, bounds -1 to 2147483647 | HTTP 400; Field 'reasoning_budget_tokens': Value must be between -1 <= value <= 2147483647, but got -5 |

## Refused rows and predicate clauses (24)

All 38 rows passed the static table/declaration/source checks (a), (b), and (c): no corresponding refusal appears in the receipt. All 24 misses below were refused by clause (d), exactly `d:not-shown`, because the observed status, bounds or effective value did not match the guess. No row was refused by clause (e); the seven counted effective outcomes differed from both their request value and the counter's field-omitted value. Reject rows do not use clause (e).

| id | field | guessed outcome | observed | refusal |
| --- | --- | --- | --- | --- |
| F28-05 | n_cmpl | reject 400, bounds 1 to 2147483647 | HTTP 400; Field 'n_cmpl': Value must be between 1 <= value <= 4, but got -5 | d:not-shown |
| F28-06 | t_max_prompt_ms | reject 400, bounds 0 to 2147483647 | HTTP 200; no matching bounds error | d:not-shown |
| F28-07 | t_max_predict_ms | reject 400, bounds 0 to 2147483647 | HTTP 400; Field 't_max_predict_ms': Value must be between -1 <= value <= 9223372036854775807, but got -5 | d:not-shown |
| F28-12 | typical_p | 200, typical_p = 0.0 | HTTP 200; effective -0.5 | d:not-shown |
| F28-14 | dynatemp_range | reject 400, bounds 0.0 to 3.4028234663852886e+38 | HTTP 200; no matching bounds error | d:not-shown |
| F28-15 | dynatemp_exponent | 200, dynatemp_exponent = 0.0 | HTTP 200; effective -0.5 | d:not-shown |
| F28-16 | repeat_last_n | 200, repeat_last_n = -1 | HTTP 400; effective null | d:not-shown |
| F28-17 | repeat_penalty | 200, repeat_penalty = 0.0 | HTTP 400; effective null | d:not-shown |
| F28-18 | frequency_penalty | 200, frequency_penalty = 2.0 | HTTP 200; effective 5.0 | d:not-shown |
| F28-19 | presence_penalty | 200, presence_penalty = 2.0 | HTTP 200; effective 5.0 | d:not-shown |
| F28-20 | dry_multiplier | reject 400, bounds 0.0 to 3.4028234663852886e+38 | HTTP 200; no matching bounds error | d:not-shown |
| F28-21 | dry_base | 200, dry_base = 1.0 | HTTP 200; effective 1.75 | d:not-shown |
| F28-22 | dry_allowed_length | 200, dry_allowed_length = 0 | HTTP 400; effective null | d:not-shown |
| F28-23 | dry_penalty_last_n | 200, dry_penalty_last_n = -1 | HTTP 400; effective null | d:not-shown |
| F28-25 | mirostat_tau | 200, mirostat_tau = 0.0 | HTTP 200; effective -0.5 | d:not-shown |
| F28-26 | mirostat_eta | 200, mirostat_eta = 0.0 | HTTP 200; effective -0.5 | d:not-shown |
| F28-28 | adaptive_decay | 200, adaptive_decay = 0.99 | HTTP 400; effective null | d:not-shown |
| F28-29 | n_probs | reject 400, bounds 0 to 2147483647 | HTTP 200; no matching bounds error | d:not-shown |
| F28-31 | speculative.n_max | reject 400, bounds 0 to 2147483647 | HTTP 200; no matching bounds error | d:not-shown |
| F28-32 | speculative.n_min | reject 400, bounds 0 to 2147483647 | HTTP 200; no matching bounds error | d:not-shown |
| F28-33 | speculative.p_min | 200, speculative.p_min = 1.0 | HTTP 200; effective null | d:not-shown |
| F28-34 | speculative.ngram_size_n | reject 400, bounds 1 to 2147483647 | HTTP 200; no matching bounds error | d:not-shown |
| F28-35 | speculative.ngram_size_m | reject 400, bounds 1 to 2147483647 | HTTP 200; no matching bounds error | d:not-shown |
| F28-36 | speculative.ngram_min_hits | reject 400, bounds 1 to 2147483647 | HTTP 200; no matching bounds error | d:not-shown |

## Exact commands and tool operations

All shell commands were bounded. Clone/checkouts were confined to the isolated scratch tree with Git override variables unset. No git/jj write was made in the lane or fleet repository. The shell cwd was `/home/vgpnk/Projects/shokunin` except the generation/hash calls whose cwd was the scratch tree.

```sh
timeout 20 df -h /fast
timeout 180 env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree && timeout 30 env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE git -C /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree checkout -q d8bf1804ce52c30343f3e41cbae41c9640db9a64 && timeout 20 sha256sum /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree/.ufo/waves/round-28/count-c1.py
timeout 900 /usr/bin/python3 /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree/.ufo/waves/round-28/count-c1.py --lane /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree --repo /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree --out /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/pristine-receipt.json; echo exit=$?
timeout 30 /usr/bin/python3 /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree/.ufo/waves/round-28/control-fixture/CtlSourceBlind/guess.py --declarations /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree/.ufo/waves/round-28/control-fixture/CtlSourceBlind/declarations.json --out /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree/.ufo/waves/round-28/control-fixture/CtlSourceBlind
timeout 900 /usr/bin/python3 /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree/.ufo/waves/round-28/count-c1.py --lane /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree --repo /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree --out /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/receipt.json; echo exit=$?
timeout 900 /usr/bin/python3 /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree/.ufo/waves/round-28/count-c1.py --lane /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree --repo /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree --out /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/restored-receipt.json; echo exit=$?
```

The actual declaration search used the specialized grep tool (its raw return was retained only in the kernel, not displayed):
```json
{
 "pattern": "new field_[A-Za-z_]+\\(\"[^\"\\n]+\"",
 "path": "/fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree/.ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp",
 "case": true,
 "gitignore": false,
 "skip": null
}
```
Only this extraction was displayed and written to declarations.json:
```python
schema_declarations = [{'line': int(m.group(1)), 'field': m.group(2)} for m in re.finditer(r'^\s*\*?(\d+):[^\n]*?new field_[A-Za-z_]+\("([^"\n]+)"', schema_grep_result['text'], re.M)]
```

Tool application: write the generated registry to scratch `registry/request-field-outcomes-r28.json`; use edit CUT 1.=43 from generated SKILL.add.md and PUT after scratch SKILL.md line 1133; use edit CUT 1.=43 from generated SOURCES.add.md and PUT after scratch corpus/SOURCES.md line 371. Generated additions were then restored from their saved exact strings. Restoration replaced the two scratch documents with their saved original bytes and removed only the newly created registry. Reproduction is the original frozen tree plus the generated registry and the two appended addition files.

Hash/listener commands actually used:
```sh
timeout 20 sha256sum /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree/SKILL.md /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree/corpus/SOURCES.md /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree/.ufo/waves/round-28/count-c1.py && timeout 20 ss -ltnp
timeout 20 sha256sum /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree/SKILL.md /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree/corpus/SOURCES.md /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree/registry/request-field-outcomes-r28.json /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree/.ufo/waves/round-28/count-c1.py
timeout 20 sha256sum /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree/SKILL.md /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree/corpus/SOURCES.md /fast/scratch/hyaku/kama-r28/ctl/CtlSourceBlind/tree/.ufo/waves/round-28/count-c1.py && timeout 20 ss -ltnp
```

## Exact restoration evidence

| file | pristine sha256 | mutated sha256 | restored sha256 |
| --- | --- | --- | --- |
| SKILL.md | 6127e49f1c7c38a05c5154c5e3f926c99ad7d6fe3ccb6c30d58b0aefa0fa7747 | ab8a2ef0f9a1de3fe741523dc6c10737a3951e248e8ac7784a5ff6cd600fa25c | 6127e49f1c7c38a05c5154c5e3f926c99ad7d6fe3ccb6c30d58b0aefa0fa7747 |
| corpus/SOURCES.md | 01c713f31ba87189ccb2669cd0f1aade2be3d4a110946a85c02770893a6dd6ef | c53328c9e5916bbf21701ac768ec88b10f69f2bfbceccf874f450dcb14b626df | 01c713f31ba87189ccb2669cd0f1aade2be3d4a110946a85c02770893a6dd6ef |
| registry/request-field-outcomes-r28.json | ABSENT | 6a9b29979d9c38bca17049556ce3a4940c9b35639a5ef97482e8d1ab04189d02 | ABSENT |

Each restored document was also compared byte-for-byte with its saved original: true. The registry was absent before and absent after. The counter sha256 was verified before its first use and again at mutated/restored states; it remained `e6a706bb2e15aec288924b9aec863ff0b1ffdd7e588e78250c0f642565c0540c` throughout. Only the reproducible fixture remains in the scratch control-fixture directory.

The frozen counter terminates its launched process group in its finally block. After scoring, `timeout 20 ss -ltnp` showed no listener on any 47600–47619 counter port. No shim, fake server or manually launched llama-server was started. The pristine and restored empty-registry paths did not launch a server.

`df -h /fast` before cloning reported 804G size, 597G used, 207G available (75% used). Total published fixture content is 44966 bytes, below 1 MiB; every generated file is separately bounded below 1 MiB and no append loop is used.

Tool installs/updates: none. One edit-tool false positive about an intentionally emptied Markdown handoff file was reported via xd://report_issue; the handoff file was restored exactly and did not affect scoring.

Report: .ufo/waves/round-28/controls/CtlSourceBlind/REPORT.md
