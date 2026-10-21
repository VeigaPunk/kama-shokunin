VERDICT: confirm - 0 verdict-line and 0 exit-code changes across the 37 committed schema-string receipts (and 40 supplementary JSON) at 7a6bc911 vs a29bb84; no committed receipt carries install_links.

# LinksBackCompatRegrade (round 21, build wave, executor seat)

## Scope
- Target: committed `.ufo/waves/**/*.json` containing `kama-llamacpp-live/v`, 37 files. Byte-identical at both commits (`git diff --quiet 7a6bc911 a29bb84 -- '.ufo/waves/**/*.json'`, exit 0). Gate blob: base e90be78, work 8a6b5dd.
- Invocation: `python3 tests/llamacpp-live/check-receipt.py RECEIPT`, cwd = clone root, no optional flags (my reading of "same arguments (none)").
- Supplementary: 40 committed JSON that mention `llamacpp-live` without the schema string. Same runs, reported separately.
- Arms: scratch clones at both pinned commits, clean and HEAD-verified. Scratch deleted afterwards.

## Commands (exit)
- `git clone` + `checkout` per arm: exit 0. HEADs re-read at cleanup: exit 0.
- `git grep -l 'kama-llamacpp-live/v' <commit> -- '.ufo/waves/**/*.json'`: exit 0, 37 hits per arm, listings equal.
- `git grep -l 'llamacpp-live\\/v'` (escaped-slash variant): exit 1, none.
- `git grep -l 'kama-llamacpp-live/v' <commit> -- ':(exclude).ufo/waves' '*.json'`: exit 1, none outside `.ufo/waves`.
- `git grep -l 'install_links' <commit> -- '.ufo/waves/**/*.json'`: exit 1, none carry install_links.
- `python3 .../LinksBackCompatRegrade/regrade.py`: exit 0 (77 regrade + 2 probe invocations per arm, 7 s).
- `python3 .../LinksBackCompatRegrade/verify.py`: exit 0, `RESULT: PASS`.
- Versions: git 2.56.0 (exit 0); Python 3.14.8 at /usr/bin/python3 (exit 0).

## Results
| scope | files | base | work | verdict-line changes | exit changes | raw output changes |
|---|---|---|---|---|---|---|
| schema string | 37 | VALID 12, INVALID 24, traceback-only 1 | same | 0 | 0 | 2 |
| mention-only | 40 | INVALID 40 | same | 0 | 0 | 0 |

- The 37: 18 real receipts (v1 4, v2 3, v3 11) plus 19 non-receipt JSON (dispatch, spec, spawn-result, measure, controls, gguf fixtures).
- 12 VALID = 11 live receipts under round-16..18 + `round-20/build/out/RegReceiptSixPin/null-tree.json`.
- `server.install_links` present in 0 of 37.

## Changes (the only ones)
- Raw output differs for two crash fixtures: `round-20/build/out/GateSelftestCrash/receipt-A-refusal-set-str.json` and `receipt-B-surrogate-summary-exit.json`. Both crash identically in both arms: A prints only the traceback header; B prints `INVALID ...: 1 problem(s)`, then crashes.
- After masking traceback line numbers and `...<N lines>...` counts, zero differences (verify.py check 3). The residue is shifted line numbers (328→356, 2213→2331, 2247→2366, 2235→2354) and `<3 lines>`→`<4 lines>` from the added `expect_links=` kwarg in `main()`. Crashing statements unchanged.

## Findings (measured; none is a back-compat regression)
1. Gate crashes exit 1, the same code as INVALID. A: `TypeError: '<' not supported between 'str' and 'int'` in validate (mixed port_refusal_set). B: `UnicodeEncodeError` on lone surrogate `\ud800` in `print`. Both pre-date 7a6bc911 and are untouched by a29bb84.
2. Stray digest accepted: P1 (seed `round-16/live/receipt-frozen-probe.json` plus `server.install_links_sha256`, no `install_links`) is VALID in both arms, exit 0. The new block runs only when the list is present, so a dangling digest is never recomputed.
3. P2 (P1 plus `--expect-install-links-sha256`): base exit 2 (unrecognized argument, expected for a new flag). Work exit 1, `INVALID ...: 1 problem(s)`, message "receipt has no server.install_links_sha256 digest". The digest is present and the list is missing, so the message misstates the cause.

## Not verified here
- [INFERENCE] The install_links acceptance path (list present, chain checks, digest recomputation) is not exercised by any committed receipt, so this regrade cannot confirm it. It is covered only by gate `--selftest`, which I did not run.

## Files (out/LinksBackCompatRegrade/)
- `regrade.tsv`: path, base verdict line, work verdict line (37 rows). `regrade-mention-only.tsv`: same columns, 40 rows.
- `regrade-detail.tsv`: blob sha256, declared schema, install_links flag, both exits, traceback and identity flags.
- `probes.tsv`, `run-base.log`, `run-work.log` (full stdout/stderr per invocation), `summary.txt`, `verify.txt`, `regrade.py`, `verify.py`.
- Verdict line = first stdout line, else first stderr line. For receipt-A the "verdict" is the traceback header, not a verdict.

## Tooling and lane
- No tools installed or upgraded.
- Lane untouched: scratch clones were read from it; no git command ran in the lane; writes are limited to out/ and this report.
