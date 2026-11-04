# Round 85 verifier spot-check

author: hyaku closure (non-author integrator, @m_zfl)

Subject: kama r85, base `4401b72f64a2202fd30f26479c463e9b9d9cabad`, delivered `6abaf0a8d11a76b141f37a9e9f6144b797af0b24`; terminal measurement revision `948dec784a9736b4a36d6a10d303fbee054b19c6`. Review date 2026-11-04. This review does not execute lane-owned gates, counters, or selftests. Numeric documentary facts below are independently measured over committed bytes; executable outcomes are evidence-verified, not re-executed.

## Conformance

- `git log --format='%an %H' -- .ufo/reports/round-85/kama.md` in fleet: `kama-shokunin 5bc126b3e9c98c5aa292ea8d1e1233f65d53c2e0`. Real report, three checkable round-work commits with LOG ties, not a marker. `## SHONEN` has four `[~]` evidence-bearing assessments; no promotion approval is implied.
- For every full 40-hex lane commit cited in that report (base, freeze `7d3c987c0e3a6ee62673c18c26ecdd22f39e5cdd`, measured revision, delivered revision), `git -C kama-shokunin merge-base --is-ancestor HASH master` returned 0. Branch, not detached HEAD/upstream syntax, was used.
- `scripts/hyaku/jj-lane.sh state /home/vgpnk/Projects/shokunin/kama-shokunin`: `branch=master local=6abaf0a8d11a76b141f37a9e9f6144b797af0b24 remote=6abaf0a8d11a76b141f37a9e9f6144b797af0b24 ahead=0 behind=0 head=detached tracked=0 untracked=0`. `git status --porcelain` printed nothing.
- Dispatched `.ufo/prompts/kama-round-85.md` carries mission/axes binding, 1–3 distinct falsifiable claims, lowest-axis rule, L2 minimum and role split, report path/SHONEN/hash/commit ordering, push scope, L0, and lane write-scope mechanics. C1 works assigned calibration7 versus operability8.
- Status-neutral role conformance defect: report/plan say planner=L1 and list ten L2 roles without an L2 planner, whereas template §3 requires a planner in the batched L2 minimum role split. Results lack per-seat status/id/error and contain an empty scout output; useful scout execution is unestablished, as honestly disclosed. Route these to lane/dispatcher; do not invent success or replacement.
- Driver digest copied from dispatch: `2026-11-04T12:30:23-03:00 launch kama round=85 pgid=21079 driver=hyaku-inline attempt=1`; `2026-11-04T15:16:26-03:00 complete kama round=85; hyaku-inline attempt=1`.

## Claim re-checks

All paths below are lane-relative. Plain measurements used Python `subprocess.check_output(['git','-C',repo,'show',rev+':'+path])` over the two fixed revisions, never worktree execution of the lane scripts.

### C1 calibration — unprovable; frozen claim fails, honest stop

Independent actual-line measurement selects the first line starting `**Current authority` and the first line starting `| calibration |` in committed SCORECARD.md. The gate fact requires the full `b53cd336e0cb204cf71246e95fdf7494babeafa4`, exact `PRE_REPORT round=84 arms=13 failed=0 uncommitted=0`, `python3 tools/pre-report-gate.py --repo . --round 84 --tip master`, and `.ufo/waves/round-84/measured/after/gate-final-green.out` in the authority line, with no `under terminal measurement`. Closure fact requires the round84 spot-check path and rejected-honest-stop in the calibration line. Observed base `gate=0 closure=0 mismatches=2`; delivered `gate=1 closure=1 mismatches=0`. Thus the reported two actual-line repairs remeasure correctly.

That numeric repair is not the whole frozen claim. `plans/round-85-claims.md:15` kills C1 for any falsely passing stale-cell control. Reopened committed `w1/out/SN01Scope/receipts/fenced-shadow.md`: lines3–9 contain a fenced example with both correct-looking cells; rendered live authority at13 still says under terminal measurement and live calibration at17 still cites round83. Its retained `.out`/SN01 report records exact green facts2/mismatches0 exit0 at fixture `8297f6e98c785b12f07105ff14b380799f381399`. CR01 independently retains fenced/comment false greens. Evidence verifies the frozen kill condition. This is not a merely missing reopen, and no exploratory exception is requested. Calibration improvement as frozen is unprovable, not harmed: the actual record was corrected, the selector limitation was exposed and marked, and no score rose.

Freeze integrity independently measured with `hashlib.sha256(git show FREEZE:.ufo/waves/round-85/count.py)` and delivered equivalent: both `e550a24786d7c3e073c549a8dcb03d456579696ba92a7f2a15ea2e7c04bedca9`.

### C2 operability — improved, finite target evidence-verified

Plain source measurement of quoted owning-arm labels in `tools/round81-append-debt.py`: `note-deletion-equals-subject`, `note-deletion-above-subject`, `note-subject-exact-summary` each occur0→3. Byte comparisons before `def selftest(` and from `\ndef main(` onward are both equal across base→delivered. Only selftest behavior changes; unchanged production behavior supports no operability harm.

Committed `.ufo/waves/round-85/measured/before/c2.out` records three actual M2/M3/M4 runs, each child exit0, pass31/fail0, killed0/escaped3/invalid0, counter exit1. After `c2.out` and `commands.json` name measured source revision `948dec784a9736b4a36d6a10d303fbee054b19c6`: M2 child exit1, owning equality failure, pass33/fail1; M3 child exit1, owning above-subject failure, pass33/fail1; M4 child exit1, above-subject plus exact-summary failures, pass32/fail2. Each has one completed consistent summary. Aggregate killed3/escaped0/invalid0 exit0; pristine debt-selftest pass34/fail0 exit0 with empty stderr. These are committed execution evidence, not freshly executed by closure. Synthetic unrelated-arm/contradictory-summary classifier escapes are explicitly not certified or credited as actual mutant executions.

Committed `commands.json` also records full gate arms13/failed1/uncommitted0 exit1 and debt events79/accepted53/late23/pending1/unaccepted3/bad_rows0 at the same revision. The failed arm is round75-instruments/inherited acceptance debt; no gate-green target was frozen. Wrong-round fixture retains one note-wrong-deletion-round finding, bad_rows1, exit1. Gate redness is routed, status-neutral; not marker evidence. No mutable fleet snapshot claim is substituted for the fixed committed-source mutant runs.

## Per-axis verdicts

`git diff BASE DELIVERED -- SCORECARD.md` reviewed along with frozen plan, lesson, retained receipts, source rows and specimens. All numeric scores stay unchanged, no new capability row is credited; documentary knowledge paths have no changes (`git diff --name-only BASE DELIVERED -- corpus/knowledge` prints nothing).

| Axis | Verdict | Evidence |
|---|---|---|
| calibration | unprovable | C1 actual lines2→0 repaired, but frozen stale-cell false-pass kill fires |
| operability | improved | finite three delivered-mutant owning-arm failures, pristine34/0; production prefix/main identical |
| freshness | unchanged | no new endpoint/source-origin certification; existing limitations explicitly retained |
| depth | unchanged | registry/limitation wording updated, no distinct depth move claimed |
| coverage | unchanged | no new knowledge or capability/frontier-to-core credit |
| adjacency | unchanged | own two-cell/debt instrument boundary preserved; sibling domains not absorbed |

## Discernment: reopened sources

| Item | Decision | Re-opened source | Judgment | Reason |
|---|---|---|---|---|
| S576 | admit | https://spec.commonmark.org/0.31.2/#atx-headings, §4.2, 2026-11-04 | agree | Primary spec says “The opening # character may be preceded by up to three spaces of indentation.” Quote is14 whitespace-delimited words, matches lesson and scoped row; grounds indentation, not full parser correctness. |
| S577 | reject | https://raw.githubusercontent.com/ggml-org/llama.cpp/b7200/examples/server/README.md, 2026-11-04 | agree | Native read returned HTTP404; independent urllib HTTPError read returned status404 and exact body `404: Not Found`. Exact ref/path availability only; no global absence claim. Retrievable-document flip is appropriate. |

New SOURCES rows331–332 reopened and checked against these quotes. Canonical `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` executed: exit0, final `kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`; W01 S481 tierC/mined and W04 duplicate-URL warnings remain, including S576. Independently parsing committed pipe rows with numeric S ids produced base315 rows/A300/B11/C4/mined283/queued8/rejected24; delivered317/A302/B11/C4/mined284/queued8/rejected25. Report matches. No old source-row credit is silently rewritten.

Read-only reviewer seat `CloseKamaR85.Kama85Claims` additionally remeasured committed AST selftest populations31→34 (22→25 direct cases, five loop-expanded and four path cases), tool bytes36502→38592, and confirmed39 insertions/0 deletions confined to selftest. Tool SHA256 at measured and publication revisions matches `7683c8b0cc9ae2e32546ac03eb6d58fe8a0de72e2d726aa3ed7dce6f799fb3c4`. Its owning-arm receipt review agrees with the finite C2 credit and frozen C1 rejection. Closure, not that advisory seat, owns the verdict; inherited red gate alone is status-neutral, not an independent admission predicate.

## Trends and admission

- expansion: unchanged — no changed knowledge path, no admitted capability; two source rows alone are not expansion.
- quality: improved — selftest sensitivity to the three actual survivors improves, production semantics preserved, stale authority text corrected; selector and inherited gate debt explicitly remain marked, not hidden.
- discernment: improved — outside sample agrees on both admit and reject; lesson learns prior outside authority defect via KQ137 and current false greens via KQ138, rejecting C1 instead of weakening the frozen predicate.

Status `ok`; admitted `false`; verdict `rejected-honest-stop`. Every claim must verify, and C1 does not. No observed harmed axis. SHONEN assessments remain partial; no operator promotion recommendation from these instrument-only observations.

## Routed defects for next round

- R85V1 calibration: freeze rendered-block identity (exclude fences/comments) and coupled revision/command/receipt assertions prospectively; preserve fenced/comment and contradictory-revision red controls. Do not alter the frozen round85 counter or retrospectively admit C1.
- R85V2 operability: retain owning-arm/unique-summary/cardinality checks for classifier escapes; current credit is only the three actual delivered mutants, not general classifier robustness.
- R85V3 inherited acceptance debt: keep gate red honestly and repair through a separately declared round; source-origin corroboration and missing historical red-selfrecord run remain unresolved, not supplied by round85.
- R85V4 conformance/dispatcher: include required L2 planner and durable per-seat status/id/error evidence; empty scout output cannot establish useful execution.

No tools installed/updated; no lane gate/selftest rerun. Self-evaluation: accuracy4 (committed outcomes distinguished from reruns); completeness4 (sampled, not universal source audit); clarity4 (numeric repair versus frozen failure separated); actionability4 (routed falsifiers); conciseness4 (command details retained for reproducibility). Overall4.0; improvement: keep future gate-evidence registries narrower so closure can cite less historical debt.
