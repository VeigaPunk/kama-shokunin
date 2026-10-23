VERDICT: partial — the assigned boundary leg refuses all 24 shortcut/variant rows but retains only 14/17 genuine E26 rows; correcting quote representation alone does not eliminate the genuine-row cost.

## Axes and scope

- **Calibration:** shortcut rejection versus false refusal; lexical overlap is not causal request provenance.
- **Depth/coverage:** conditional loss of genuine error coverage, not a scored C1 result. C1 remains withdrawn before data (`.ufo/waves/round-27/a3/plan.json:6-18`). No claim judgment, admission, integration, or judging-runtime invocation is supplied by this review.

Lane root for relative pointers below: `/home/vgpnk/Projects/shokunin/kama-shokunin`.
Output root: `.ufo/waves/round-27/residual/out/CriticBoundaryLegProbe/`.
“Final receipt” means `.ufo/waves/round-26/final/c1-final-tip-receipt.json`; “pinned” source filenames mean `.ufo/waves/round-27/sources/llama.cpp-704366d/`. Harness/probe receipt filenames are under the output root.

Implemented `harness.py`; generated `boundary-leg.receipt.json`. This is an offline function-level probe of `corpus/QUALITY.md:226-235`, with the assignment's **length >= 4** restriction. It is not the complete, unqualified KQ37 test or the frozen C1 counter.

## Result

| Set | Rows | Refused | Kept | Refused by literal conjunct alone | Refused by overlap conjunct alone |
|---|---:|---:|---:|---:|---:|
| Boundary-shifted variants | 12 | 12 | 0 | 12 | 12 |
| Round-26 shortcut rows | 12 | 12 | 0 | 0 | 12 |
| Genuine E26 rows, unchanged registered signatures | 17 | 3 | 14 | 3 | 0 |

Evidence: `boundary-leg.receipt.json:86-140`. Every row and its source line, decoded message, signature spans, request strings and overlap reasons are retained in the receipt.

**The leg can fail, and the second conjunct is not redundant.** Even granting the original shortcuts a matching literal-line anchor, their literal conjunct passes 12/12, while their overlap conjunct refuses 12/12. The boundary variants fail both conjuncts. Example X26-01: the variant signature occupies message span `[68,117)`, overlapping its decoded `response_format.type` value at `[70,117)`; the original shortcut signature occupies exactly `[70,117)`. The constant S137 literal does not contain the variant signature (`boundary-leg.receipt.json:145-215,1023-1098`; pinned `server-common.cpp:1375`). Offsets are zero-based, half-open Unicode codepoints.

## Every refused genuine row

| Row | Exact primary reason | Evidence |
|---|---|---|
| **E26-07** | `not_substring_of_one_literal_on_source_line`. The registry signature contains backslash-quote pairs (`\"input\"`, `\"content\"`), whereas the decoded source literal and decoded HTTP error.message contain plain quotes. The registered signature therefore also has no occurrence in the decoded message. | `registry/error-signatures-r26.json:157-181`; final receipt `:164-187`; pinned `server-context.cpp:6151`; probe receipt `:2186-2217`. |
| **E26-14** | The same literal/representation mismatch: the registered signature begins `\"prompt\"`, but the decoded literal/message begins `"prompt"`. No registered-signature occurrence exists in the decoded message, so the primary overlap result is vacuous, not proof of independence. | Registry `:357-380`; final receipt `:346-369`; pinned `server-common.cpp:1114`; probe receipt `:2470-2501`. |
| **E26-17** | `not_substring_of_one_literal_on_source_line`. Its cited line is `GGML_ASSERT(n_outputs >= 1);`, which contains **no string literal**. A genuine assertion-derived error cannot satisfy this literal-only requirement. | Registry `:415-430`; `corpus/SOURCES.md:142` (S130); pinned `llama-context.cpp:2624`; probe receipt `:2547-2566`. |

Primary results do **not** silently unescape or replace historical signature identities.

### Strongest counterexample after separating representation from policy

The harness also runs two explicitly segregated, non-primary diagnostics using the quote-unescaped E26-07/E26-14 signatures (`harness.py:194-198`; receipt `:2570-2672`).

- E26-07 then passes both conjuncts.
- **E26-14 still fails the overlap conjunct.** Its decoded signature is exactly the server-owned fixed literal on pinned `server-common.cpp:1114`, and its captured HTTP 400 message is that literal. The request key `prompt` (six characters) occurs in the message at `[1,7)` and `[81,87)`, both inside the signature span `[0,132)`. The rule refuses this fixed diagnostic solely because the same key text appears in it. This is an exercised offline counterexample, not a newly observed live run (`boundary-leg.receipt.json:2609-2671`; final receipt `:363-367`).

Thus the primary 3/17 cost comprises two historical wire-vs-decoded representation incompatibilities and one nonliteral assertion. Fixing representation exposes a separate conservative lexical-overlap cost on E26-14; it does not establish no-harm retention.

## Method and provenance boundaries

- Imported the **complete frozen counter from a scratch copy**, after asserting the source and copy hashes equal `49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765`. Copy: `/fast/scratch/hyaku/kama-r27c/res-CriticBoundaryLegProbe/frozen_count_c1.py`. Import has a non-main module name; no counter `main()` ran (`harness.py:41-59`).
- Reused its `literal_texts`, excluding only the appended synthetic joined-literals candidate: the assigned qualification says **one** literal, while the frozen helper additionally returns joined literals (`count-c1.py:338-340`; harness `:56-59`). This retains that helper's parser limitations; it is not an independent C++ parser.
- The small predicate is `harness.py:95-111`: exact signature-in-one-decoded-literal **AND** no intersection between any signature occurrence and any qualifying request-string occurrence. It enumerates all occurrences, including repeats/overlaps. Comparisons are exact/case-sensitive; Unicode case-folding and whitespace variants belong to other legs and were not tested.
- Stored nonempty string bodies are JSON-decoded first. Request strings are body keys and string values at every depth, minimum four Unicode codepoints; no method/path/header/argv surfaces are added to this boundary-only probe (`harness.py:73-92`). The original shortcuts therefore are not rejected merely for their historical body shape.
- Genuine source lines come from the E26 SOURCES anchors (S114–S130). Snapshot files are hash-checked against the frozen counter's pins, plus the two round-26 pins for `gguf.cpp` and `llama.cpp` (`harness.py:114-138`; round-26 counter `:62,65`). Input digests are in receipt `:21-85`.
- **Original shortcut citations have no line numbers.** The harness explicitly supplies a diagnostic best-case mined matching literal line in each original cited file, retaining all matching line numbers. These are not falsely described as the original cited lines (`harness.py:164-175`; receipt `:1027-1038`). Boundary variants instead use their stated S137 anchor, line 1375. Even with this strengthening, every original shortcut fails overlap.
- Final receipts retain only startup-log prefixes for E26-15–17; they do not retain their actual error messages (`.ufo/waves/round-26/final/c1-final-tip-receipt.json:393,419,445`). **No messages were fabricated or substituted with signatures.** These three rows have no request/body strings, so overlap is vacuously safe independent of the unavailable message suffix. E26-15/16 pass this leg only; E26-17 deterministically fails the source-literal conjunct. This does not replay their historical live evidence.

## Smallest safe correction

For this round, append an explicit **conservative-retention limitation** and the measured exclusions above; do not describe this leg as retaining all genuine E26 rows or as proof of causal echo. Keep the frozen counter, old registry identities and historical receipts unchanged. Future decoded-message signatures need an explicit representation contract, not an implicit extra unescape during counting.

If complete genuine-row retention is required, lexical coincidence cannot be relabeled as taint: E26-14 requires source/template-derived ownership independent of the selected signature. Nonliteral assertion provenance also needs its own demonstrated branch or an honestly narrowed applicability statement. [INFERENCE] Broadly exempting request keys or macro calls would reopen unchecked echo/provenance paths; this evidence does not establish such an exemption safe.

The quote-representation incompatibility is fixable for future captures. The lexical false refusal and literal-only exclusion are demonstrated policy costs, not harness failures to suppress. A no-regression claim is not supported by this receipt; only the canonical judge/non-author claim reviewer can decide the tradeoff. No admission recommendation or X1 verdict is made here.

## Exact commands, outputs and exits

1. Hash check — exit **0**:

```sh
timeout 30s sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/count-c1.py
```

```text
49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/count-c1.py
```

2. Single bounded probe — exit **0**:

```sh
timeout 45s /bin/bash -c 'ulimit -f 1048576; ulimit -v 262144; ulimit -t 25; ulimit -u 64; exec /usr/bin/python3 -I -S -B /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/residual/out/CriticBoundaryLegProbe/harness.py'
```

Trimmed stdout (full per-set totals are the table and receipt above):

```text
counter_sha256=49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765
genuine_e26: {"accepted": 14, "literal_only_refused": 3, "overlap_only_refused": 0, "refused": 3, "refused_ids": ["E26-07", "E26-14", "E26-17"], "total": 17}
genuine_refused E26-07: not_substring_of_one_literal_on_source_line
genuine_refused E26-14: not_substring_of_one_literal_on_source_line
genuine_refused E26-17: not_substring_of_one_literal_on_source_line
receipt=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/residual/out/CriticBoundaryLegProbe/boundary-leg.receipt.json
```

No server, network request, counter main, nested agent, judging runtime, git/jj write, or tool installation was used. The harness installs an audit hook refusing subprocess launches, socket connects/binds and exec/system calls (`harness.py:36-41`). Both finite commands exited; no child process tree remains. File-writing execution was under the required timeout/file-size, memory, CPU and process caps; no write approached 100 MB.
