# RV01Claims — round85 independent author-side review

Axes: calibration and operability. Recommendation only; no admission or integration performed.

## Findings by severity

### P2 — C1's numeric green does not establish all declared authority facts

Evidence: frozen `.ufo/waves/round-85/count.py:24-32`, especially line26, checks a summary substring, presence of the fixed gate hash, and absence of one stale phrase. It does not check the promised command, receipt, relationship of that revision to the summary, round84 rejected-honest-stop disposition, or retained round83 history (`plans/round-85-claims.md:10-15`). A paragraph containing the required tokens while falsely attributing a separate measured revision, or lacking the command/receipt entirely, satisfies these Boolean checks [INFERENCE from source; not executed]. Likewise line31 checks only the closure filename, not its disposition. Thus facts=2/mismatches=0 means two bounded token predicates passed, not that every factual assertion in those two cells agrees with terminal evidence.

Integration acceptance: inspect both actual committed cells against the retained round84 terminal receipt and outside closure; require command, receipt, exact measured revision and rejected dispositions. Do not generalize counter green into whole-record correctness. Keep the frozen counter unchanged; report any failing declared control honestly rather than weakening it.

### P2 — C2 recognizes semantic-looking output, not a verified owning-arm transcript

Evidence: frozen `count.py:45-47` accepts exit1, the first matching summary with fail>0, any stdout substring `APPEND_DEBT_SELFTEST_FAIL note-`, and empty stderr. It does not bind that substring to an actual line/known arm, reconcile the tally with failure records, require a unique terminal summary, or verify the pristine executable. A fabricated or inconsistent stdout transcript can therefore earn a kill [INFERENCE; no spoof execution performed]. Ordinary traceback crashes with nonempty stderr do not earn kills; missing mutation sites raise and cannot return success. This is materially better than counting arbitrary nonzero exits, but is not proof against dishonest selftest output.

Integration acceptance: inspect delivered selftest additions and raw per-mutant transcripts; separately require pristine exit0, equality/direction/exact-summary controls, preserved mismatch/unresolvable cases, unchanged grade behavior, and real-register/round84-fixture evidence. Any survivor, invalid execution or pristine regression remains a claim failure. Do not change the frozen predicate after scoring.

### P3 — C1's locator is not a Markdown parser

Evidence: frozen `count.py:10-22` matches line text without tracking fenced code/HTML blocks, and reads only the first matching authority line (not an entire multiline paragraph). Markdown-looking authority/axes lines inside a fenced example placed before the real cells can be selected [INFERENCE; not executed]. The 0–3-space correction-heading exclusion does not solve this distinct context problem. Four-space indentation is correctly outside that heading regex, but this alone is not CommonMark compliance.

Integration acceptance: inspect the committed SCORECARD diff and actual cell locations, not merely correct witness tokens; retain bounded-parser wording. Do not claim this counter excludes every unrelated-text escape. A demonstrated stale-cell false green fails C1 under the frozen plan.

## Independent baseline replay

Read the complete plan, including untruncated line21. Reviewed the actual freeze diff from base to `7d3c987c0e3a6ee62673c18c26ecdd22f39e5cdd`. That identifier is the freeze commit, not a counter digest. Its counter blob is `1bd28b7bb94313c1c7af21c9bd1ee248b8842858`; SHA256 `e550a24786d7c3e073c549a8dcb03d456579696ba92a7f2a15ea2e7c04bedca9`.

One local clone, created with `git clone --no-hardlinks --no-checkout /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r85/RV01Claims/repo`, exit0. `git -C <clone> rev-parse --show-toplevel` printed that exact clone path, exit0; checkout `--detach 4401b72f64a2202fd30f26479c463e9b9d9cabad` exit0. Frozen counter bytes were obtained with `git -C <source> show <freeze>:.ufo/waves/round-85/count.py` (exit0) and placed only in owned scratch. Both runs used owned scratch as cwd and TMPDIR; full argv/stdout/stderr/true exits are retained in `c1-base.json` and `c2-base.json` beside this report.

| Assigned command | Revision | Observed result | True exit |
|---|---|---|---|
| `python3 <scratch>/count.py c1 --repo <scratch>/repo --rev 4401b72f64a2202fd30f26479c463e9b9d9cabad --work <scratch>` | base | `AUTHORITY_CELLS facts=2 mismatches=2 gate=0 closure=0 newest=round-84-verifier-spotcheck.md` | 1 |
| same command with `c2` | base | M2/M3/M4 each exit0, pass31/fail0; `DEBT_MUTANTS mutants=3 killed=0 escaped=3 invalid=0` | 1 |

Both exactly reproduce frozen before receipts. No-work discrimination is real. C1 and C2 are causally separable: C1 reads committed SCORECARD plus lesson path inventory; C2 reads committed debt-tool bytes and executes mutations of that tool. Changing only one surface cannot repair the other predicate. Neither counter measures a runtime serving improvement or justifies a score increase.

The source of the three survivors is coherent with `tools/round81-append-debt.py:612-637`: existing mismatch case uses deletion78/subject79; M2 still rejects it, M3 still sees78<79, and M4 retains the bad finding even after falling through to coverage. Existing exit/class checks miss the changed bucket accounting. Equality, deletion>subject, and exact summary coverage target genuinely different failure modes; production grade changes are not necessary to kill them.

## Round84 acceptance traps

Read `corpus/lessons/round-84-verifier-spotcheck.md` in full, especially lines84–90.

- R84V1: no fabricated event-loss disclosure; the old full C1 remains missed and round84 rejected-honest-stop. Population rotation is not evidence of event restoration/loss.
- R84V2: require an actual schema-valid rejected SOURCES row with reason and flip, not only lesson prose.
- R84V3: distinguish historical spec-only survivors from this round's delivered-file replay. Fabricated-but-hash-consistent extracts remain a source-origin gap; hashes do not prove acquisition.
- R84V4: name terminal green at `b53cd336e0cb204cf71246e95fdf7494babeafa4`, not the later publication tip; retain round83 adverse history.
- R84V5: append citation/provenance erratum. The absent `before/red-selfrecord.out` is not retroactively supplied by `after/c2-red.out` with `--no-corrections`; do not rewrite the round84 frozen plan.

## Residual risk and verification gaps

LSP device unavailable: `read xd://lsp` returned `No such tool`; references/definition/diagnostics were unavailable. Text search/read is fallback evidence, not semantic reference proof. Static escape findings above were not experimentally scored: only the two explicitly assigned base replays were executed. No final integrated changes or final-master predicates were verified, no live endpoint sampled, no other runtime invoked, no tool installed/updated, no source checkout mutation and no source commit/push. Scratch-only selftest fixture commits are internal to the assigned counter replay and explicitly root-checked by `late_path_selftests()` at debt-tool lines415–423. No canonical-runtime/rerouting/resume implementation is changed in this frozen diff; those role checks are not applicable.

Report stays inside owned output directory; the supplied Report trailer points outside that directory, so no file was written there. Receipts retained before removing scratch.

## Self-evaluation

Accuracy4: replay evidence is direct; escape consequences are explicitly static inference. Completeness4: assigned baseline and R84V1–V5 covered; final integration is outside this seat's verification. Clarity4/actionability4: source-line findings and explicit integration acceptance checks; no dynamic exploit receipt claimed. Conciseness4: detailed evidence retained for audit. Overall4.0; highest-impact next verification belongs to integrator: bind final raw evidence to the unchanged frozen acceptance contract.
