# SN01Scope — round85 w1 sentinel findings

Axes: calibration (assigned), operability (supporting boundary review). Author-side advice only: no claim admission, integration, or security certification.

## Exact finite scope

Read the complete round85 frozen plan, frozen counter, round84 closure's routed R84V2/V5, retained terminal-green and red-control receipts, wave routing, and the delivered debt tool's Git/path/selftest launch boundaries. Executed nine bounded C1 probes on committed, artificial SCORECARD trees in one fresh scratch fixture repository. No C2/selftest/build/lint/full campaign executions, network requests, live endpoints, credential files, other runtimes, or delegated work. `resume_continuity_v1` is not part of this assigned surface and was not reviewed.

All durable seat writes are inside `.ufo/waves/round-85/w1/out/SN01Scope/`; fixture commits were only in own scratch. The requested `.ufo/waves/round-85/w1/SN01Scope.md` is outside the explicitly owned directory, so this file is its staged replacement, not a production edit.

## Findings

### HIGH — fenced examples can replace both live cells in the counter

- **Exploit path:** place a fenced Markdown example before the actual stale authority paragraph and first rendered Axes section. Inside the literal code example put a correct-looking `**Current authority**` line, `## Axes`, and calibration row. Neither actual live cell is repaired.
- **Evidence:** frozen `count.py:13–21` removes correction sections but does not recognize fenced code; its first-match regexes therefore select literal code as live cells. `receipts/fenced-shadow.md` preserves the complete specimen. At fixture revision `8297f6e98c785b12f07105ff14b380799f381399`, the unchanged frozen counter exits **0**, printing exactly `AUTHORITY_CELLS facts=2 mismatches=0 gate=1 closure=1 newest=round-84-verifier-spotcheck.md`. `receipts/fenced-shadow.out`, `summary.json`, and `commands.json` retain output, revision, argv, and true child exits. Both rendered live cells remain stale in the specimen.
- **Impact:** the stronger “committed live cells, not arbitrary witness occurrence” assurance is not established. Ordinary unrelated-token and 0–3-space correction controls reject correctly, yet a quoted fenced example produces the identical frozen green output. This is evidence relevant to the plan's explicitly named false-pass kill condition; L1 retains disposition authority.
- **Smallest remediation:** do not quietly alter this frozen counter. Preserve the failed control and let L1 apply the frozen contract. For a separately declared repair, identify actual Markdown block structure, exclude literal code blocks, then select the intended live paragraph/section; retain this exact negative control alongside the positive one.

### MEDIUM — correct backing tokens can bless an explicitly wrong measured revision

- **Exploit path:** within the selected authority line say measured revision is `4401b72f64a2202fd30f26479c463e9b9d9cabad`, then append the expected PRE_REPORT and `b53cd336e0cb204cf71246e95fdf7494babeafa4` as unrelated backing. Keep the closure row correctly named.
- **Evidence:** `count.py:26` tests independent substring membership, not the measured-revision assertion or its receipt/command. Fixture revision `76b22eadb94bd2ed7fc05f76611aee601ad8e1c4` exits **0** with the exact frozen green output. See `receipts/wrong-measured-with-backing.md` and `.out`.
- **Impact:** cell locality alone does not bind the number, revision, receipt, and command into one truthful terminal-measurement assertion. A contradictory actual measured-revision statement can coexist with sufficient matching tokens.
- **Smallest remediation:** in a future declared instrument bind exactly one measured revision and required command/receipt to the assertion, rejecting contradictory measured values. For this frozen round retain this limitation and control; no production remediation was authorized or applied.

### INFO — revision/closure provenance remains an operator trust boundary

- `count.py:7–8,27–31` reads committed blobs and closure **filenames**, not closure dispositions/content or terminal receipt provenance. The positive fixture deliberately contains only `Not a closure receipt; placeholder fixture data.` in the round84 closure file, and has no `b53cd336…` commit object. It still exits0. A subsequent explicit fixture `git cat-file -e b53cd336…^{commit}` exits128. This does not assert the real repository lacks that commit or receipt.
- `BASE` at line4 is unused. `--repo` and `--rev` choose the subject; there is no built-in repository-identity/ancestry assertion. The canonical predicate fixes cwd/repository and `master`; arbitrary fixture invocations do not satisfy that operator-side condition. The fenced-shadow and contradictory-line probes above nevertheless produce the **exact** frozen expected output, not merely another newest filename.
- **Impact:** green output establishes these narrow textual/tree relations, not authenticity of a completed outside closure, measured revision, or correct repository. **Smallest remediation:** retain explicit resolved revision/repository and frozen receipt provenance in the operator receipt; never describe this filename check as closure authentication. Expand instrumentation only under a separately frozen contract.

## Controls and provenance that held

| Bounded C1 specimen | Child exit | Observed result |
| --- | ---: | --- |
| repaired live cells | 0 | facts2, mismatches0, gate1, closure1 |
| stale live cells | 1 | facts2, mismatches2, gate0, closure0 |
| witnesses in correction heading with 0 / 1 / 2 / 3 leading spaces | 1 each | same stale rejection |
| unrelated raw witness tokens | 1 | same stale rejection |
| preceding fenced example; real cells stale | 0 | false-pass specimen above |
| explicitly wrong measured revision plus correct backing tokens | 0 | contradictory-assertion acceptance above |

Freeze `7d3c987c0e3a6ee62673c18c26ecdd22f39e5cdd` is a **Git commit id**, not a file digest. It resolved successfully. Counter blob at that commit and working-file `git hash-object` both equal `1bd28b7bb94313c1c7af21c9bd1ee248b8842858`; SHA256 is `e550a24786d7c3e073c549a8dcb03d456579696ba92a7f2a15ea2e7c04bedca9`. Initial SHA comparisons against the commit id were not evidence of freeze drift. `receipts/provenance.json` retains committed bytes and explicit-path commands/exits. No freeze-content change found in this review.

## Routed R84V2 / R84V5

- **R84V2:** frozen round84 closure lines70–72,87 records an exact-path HTTP404 reject missing from SOURCES, not global documentation absence. Round85 SCR01Frontier is explicitly assigned a rejected S577 row with reason/flip and no production edits. At inspection, `corpus/SOURCES.md:332` contains S577 with `rejected`, exact-path HTTP404, and retrievable revision-specific path flip. This is a read observation, **not** an independently run schema validation or HTTP acquisition. L1 owns integration/validation.
- **R84V5:** explicit committed reads at the freeze show `measured/before/red-selfrecord.out` absent (Git show exit128); actual `measured/after/c2-red.out` exists (exit0), names revision `3e93febb0f40955b08dc80367e8ef658eaccdfd6`, command `--no-corrections`, six mismatches/zero corrections/six unbacked, EXIT=1. The assigned and delivered `SCR01Frontier/lesson-fragment.md` append-only erratum distinguishes this control from the promised historical uncorrected-tree execution. It does not supply the missing historical run. Frozen round84 plan must remain unchanged.
- Terminal gate receipt at the freeze names `b53cd336e0cb204cf71246e95fdf7494babeafa4`, command `python3 tools/pre-report-gate.py --repo . --round 84 --tip master`, PRE_REPORT round84/arms13/failed0/uncommitted0, EXIT=0. This is retained committed evidence, not a fresh gate execution or a run attributed to the publication tip.

## Command, path, secrets, and cleanup boundaries

- Counter Git reads use argv lists, explicit `git -C <repo>`, committed `rev:path`, and a bounded `corpus/lessons` tree path; no shell interpolation or network command appears. Debt tool Git helpers (`tools/round81-append-debt.py:329–399`) similarly use explicit paths/revisions and timeouts. Its `--late` binder resolves under repository root and compares file bytes to committed bytes.
- This is **not** blanket clearance for every debt-tool mode: non-selftest `--audit-json` and `--register` can intentionally read supplied filesystem paths, and its default audit executable comes from the worktree (`:660–685`). Those paths were not executed here. No credential material was opened; no claim is made that arbitrary supplied repositories/code or inherited environments are safe.
- Counter C2 runs committed Python from the selected revision, inherits parent environment (including anything the operator placed there), and sets child TMPDIR under its own TemporaryDirectory `--work`. This is trusted-code execution, not a sandbox. Counter-level subprocess calls have no timeout, so a hanging child can prevent completion/automatic cleanup; no hang probe was run. Existing debt Git helpers have their own timeouts.
- Own successful probes set TMPDIR to exact seat scratch, use explicit `git -C` for every fixture operation, and assert show-toplevel equals the fixture root before its first commit. Zero source clones, zero production commits/pushes, zero PATH/host-config changes or installs. Earlier failed fixture-driver attempts affected only own scratch; `receipts/probe-summary.txt` is an initial setup-failure trace, **not** measurement evidence. Failures were missing initialization (pipeline exit1), nonexistent default branch (Python failed; tee pipeline exit0), then no-change commit (Python failed; tee pipeline exit0). Final successful driver exits0 and records every actual counter/Git child exit without a masking pipeline.
- Evidence and driver files were retained inside this owned output directory before removing the exact owned scratch tree. No services were started.

## Self-check

Accuracy4: observed false-pass receipts replace earlier speculative parser claims. Completeness4: assigned finite surfaces covered; source schema/HTTP and C2 execution deliberately left to assigned owners. Clarity4: findings separate actual exact-output bypasses from operator provenance limits. Actionability4: exact specimens/argv/revisions retained, remediation constrained by freeze. Conciseness4: provenance/setup notes are retained to avoid overstating results. Overall4.0; improvements: prioritize the two concrete counterexamples, preserve the historic missing-run distinction, and do not generalize to universal security. L1 should be able to reproduce the same bounded results from retained fixtures without touching production.
