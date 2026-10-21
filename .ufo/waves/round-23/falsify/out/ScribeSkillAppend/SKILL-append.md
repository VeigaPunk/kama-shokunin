# DRAFT — append-only SKILL.md section (not applied to the lane checkout)

Target: `SKILL.md` at 245a37f6, after the Round22 section (committed EOF, line 774).
Insert as a new section; do not edit the R21 row (line 683), the R21 correction
block (lines 698-708), or the R22 trust paragraph (lines 732-738, 769-771).

## Round-23 report auditor repository-state isolation (owner: kama)

Appended; the R21/R22 trusted-repository restriction above still holds
(KQ32; KQ34 narrows only the graded fault rows and does not supersede KQ32).
The auditor is supported only on the trusted lane and fleet repositories. It
is not safe for arbitrary or untrusted repositories, and no claim below
extends to one.

**Isolation.** Every git invocation of `tools/report-landing-audit.py` passes
through one helper, `git()`, the only `subprocess.run` site in the file. It
runs as `git --no-replace-objects --no-lazy-fetch -c i18n.logOutputEncoding=UTF-8
-c log.follow=false -c log.showRoot=true -c log.showSignature=false
-c log.mailmap=false -C <repo> …`, with `GIT_CONFIG_GLOBAL=/dev/null`,
`GIT_CONFIG_NOSYSTEM=1` and inherited `GIT_*` variables removed. Stdout is decoded
strictly as UTF-8. `surrogateescape` is used at exactly two sites, the lane
`log -z` records and the fleet `ls-tree` report listing, which are matched on
ASCII and never emitted. Lane log records are NUL-delimited (`%x00`). A plain
`--branch` name resolves to `refs/heads/<name>` first, pinned once per run.

**Refusals.** Exit 2 (could-not-evaluate), with the reason on stderr and the
reason pinned in the grid for each refusal row:

- non-UTF-8 git output;
- shallow repository, `info/grafts`, partial clone (`extensions.partialclone`,
  `remote.*.promisor`, or a `.promisor` pack), non-sha1 object format, and a
  repository that is not its top level;
- a Landed citation that names a ref;
- an unparseable log record;
- any unanticipated exception (catch-all; never a verdict).

Declared tradeoff T01: shallow and partial clones are refused even when every
cited object is local.

**Git floor.** git ≥ 2.45 is required. `--no-lazy-fetch` is a global option
introduced in 2.45 (Git v2.45.0 release announcement: `git --no-lazy-fetch cmd`
runs `cmd` "while disabling lazy" fetching). Older git rejects the option; the
audit then exits 2 on every run. The 2.44 exit-129 behaviour is the L1's
observation (lesson round-23 OldGitFloor) and was not re-run by the scribe.

**Graded evidence (L1-reported; scribe did not re-run).**

| Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| Repository-state fault grid | gate: `python3 tests/report-audit/repo-state-grid.py --arm frozen\|current\|both [--json]` | 0 every graded row met; 1 a row not met (`--arm frozen` and `both` are 1 by design); 2 fixture premise failed or harness error | premise `require()` per builder; exit-2 rows pin the refusal reason | 26 fault rows F01–F26, 8 controls C01–C08, 2 open O01–O02, 1 tradeoff T01; frozen arm = file `tools/report-landing-audit.py` at commit `4fe9339f` (blob `fcc255ce`); 30 s per-case timeout | temporary fixture repos only | kama |
| Isolation mutants | gate: `python3 tests/report-audit/isolation-mutants.py [--json]` | 0 pristine passed and every mutant ran; 2 pristine failed or a pattern did not match once | pristine run is the positive control | 24 single-literal mutants M01–M25 (M08 is not present); survivors M02 and M20 are defensive-only | temporary copies only | kama |

Frozen arm (L1 run): 0/26 faults met, 8/8 controls. Current arm (L1 run):
26/26 faults, 8/8 controls, 0 tracebacks, executions or timeouts. Mutants (L1
run): 22 of 24 killed. `--no-lazy-fetch` (M02) is defensive-only because the
promisor refusal runs first; the 40-hex `%H` check (M20) is defensive-only
because signature display is disabled. No-harm (L1 run): selftest 50/50;
ledger rounds 10–22 byte-identical to the frozen arm (exit 0; `--no-errata`
exit 1 with 9 defects).

**Open, not claimed (identical in both arms).** Objects borrowed through
`objects/info/alternates` (O01) or a `.git` gitfile redirect (O02) resolve as
local. A peel or cross-repository prefix ambiguity can be overwritten by a later
`found`. Only the first `## Landed changes` section is read. A CR inside an
errata line splits it. `log.follow` keeps path-versus-lineage semantics as path.
The sibling tools `citation-provenance.py` and `sources-append-only.py` are not
isolated. Repository-local channels outside the graded rows are not claimed.

**Trust restriction (unchanged).** Audit trusted repositories only. The
Round-23 rows add isolation for graded channels; they are not history-integrity
proof, untrusted-repository safety, or a general hardening claim.
