VERDICT: holds — Decoded-body visibility carries refusal of these 12 shortcut rows; extraction and reserialisation cover each other, while case and whitespace normalisation are not required by this fixture.

Axes: calibration (echo refusal and guard attribution); operability (bounded offline reproducibility and exact restoration). This is mutation evidence for X1, not a verdict on X1 or withdrawn C1.

Expected detector: `any(counter.occurs(signature, s) for s in counter.request_surfaces(request))` must flag all 12 round-26 shortcut rows. Exit 0 means 12/12; exit 1 means at least one missed echo. A mutant survives only at 12/12. Each scratch file was tested pristine, mutated alone, and restored using the same harness and registry bytes.

| Mutant | Exact change (original counter line) | Pristine | Mutated flagged/12 | Restored | Exit codes P/M/R | Verdict and covering guard |
|---|---|---:|---:|---:|---|---|
| M1 | Lines 369–371: replace `json_strings(body)` and both `json.dumps` surfaces with `surf.append(req["_wire_body"])`; keep path guard | 12 | 0 | 12 | 0/1/0 | Killed. Every original body hides the first signature character with a JSON Unicode escape; raw path/body matching misses all 12 even with the original case/whitespace checks. |
| M2 | Delete line 369, `surf += json_strings(body)` | 12 | 12 | 12 | 0/0/0 | Survived. Both serialisations of the decoded body contain each signature verbatim. |
| M3 | Delete lines 370–371, both `surf.append(json.dumps(...))` statements | 12 | 12 | 12 | 0/0/0 | Survived. `json_strings[7]`, the decoded `response_format.type` value, contains each signature verbatim. |
| M4 | Line 348 becomes `return sig in text or re.sub(r"\s+", "", sig) in re.sub(r"\s+", "", text)` | 12 | 12 | 12 | 0/0/0 | Survived. Exact-case, verbatim matches in decoded values and both serialisations cover all 12. Both alternatives in `occurs` are genuinely case-sensitive; the lowercase in `squash` is not called here. |
| M5 | Line 348 becomes `return sig.lower() in text.lower()` | 12 | 12 | 12 | 0/0/0 | Survived. Verbatim matching in decoded values and both serialisations covers all 12; no whitespace removal is needed. |

Actual diffs: `M1.diff` through `M5.diff`. Row-level outputs, match surfaces and import before/after hashes: `M<1..5>.<pristine|mutated|restored>.json`. Aggregate: `summary.json`. Exact commands and trimmed stdout: `commands-and-output.txt`.

Original and every restored SHA-256: `49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765`.

| Mutant | Mutated SHA-256 |
|---|---|
| M1 | `29b227d8695f4c24f794768c8a4994c471dbb7a965af808baf2acd772d3f72d9` |
| M2 | `e07f29935fab378a4952a326f52064bf93392e3d02a3ee2b0eb04ec5426d07f0` |
| M3 | `41b09ff0b5bb297295c698472ad1c6a4d37813650fc87bd7caf0954883e8c6be` |
| M4 | `27b895668065bed6062592be903f5361e7044db0a279d3ea391452f27e34b934` |
| M5 | `3c29e44cfad5358ad315670bd9c4a6fc327ffc0ffbfcc85a9c47b6b9691a482e` |

Scope: the round-26 registry stores each already-encoded wire body as a string. The harness decodes it once into the round-27 function's body-object schema and retains the exact original wire body in a harness-only `_wire_body` field for M1. This is a function-level replay, not a run of round-27 registry validation or transmission: no `static_checks`, `main`, server, counting command, or network request ran. No claim is made that round-27 would retransmit the original escape spelling unchanged. Surviving mutants are coverage findings for these bytes, not permission to remove guards. Case, whitespace, quoting/backslashes and non-ASCII serialisation differences were not independently varied. No tools were installed or updated.
