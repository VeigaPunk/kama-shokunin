# RV04C2CounterCode — C2 counter review

Axes: operability + calibration. Advisory findings only; no claim verdict or admission.
Reviewed all 1825 lines of `tools/round64-c2-counter.py` at `23b3fdb1a925129a9961cf551f6d40bf251602cb`, freeze including amendments, and wave-b X01C2Counter/X10EnvIdleProbe. Base-to-tip diff adds this counter and both registries. Line references below are to that tip unless another file is named.

## Findings, by severity

### High — D1: timeout group kill misses the actual context server

`Runner.run` creates a session for the shell (742–744), kills only that process group on timeout (748–752), and `kill_group` ignores missing-group/permission failures (768–772). The pinned context tool starts its server in **another session** (`tools/kama-context-capacity.py:307–311`), without a parent-death hook. Its cleanup is Python `finally` (375–377), which SIGKILL cannot execute. Thus a context run timing out during a live cell can leave its server alive. No descendant enumeration, detached-child cleanup, or independently observed teardown occurs in the counter. `run_recon`, `run_tally`, and `tally_selftest` additionally use plain `subprocess.run(timeout=...)` without session/group cleanup (831–835, 970–974, 1012–1015).

Evidence: `out/RV04C2CounterCode/focused-probes.json` exercises the actual Runner with a 0.25-second timeout and a scratch-only Python command starting an own-uid detached `sleep`. Runner returned rc=124/TIMEOUT while child PID 1938360 still existed. I killed that own child immediately. No live-server timeout was induced.

Verdict direction: the timed-out row itself fails closed, toward **met=False**. A leaked server can change later idle results or exhaust resources, also causing false negatives; successful cleanup is not a conjunct, so a cleanup failure after an otherwise accepted execution can coexist with **met=True**. If an escaped child inherits the captured output pipe, the unbounded second `communicate()` at 750 can hang instead of returning a verdict. The current context server redirects its own logs, so that particular pipe hang is not asserted for its server.

Recommendation: track/reap detached descendants or use an enclosing lifecycle boundary that cannot be escaped by these intentional server sessions; independently check teardown. Keep post-timeout pipe draining bounded and make unexpected cleanup errors observable.

### Medium — D2: regression-table errors are printed but do not enter the gate

`regress_plan` returns table-level errors (651–676): malformed rows and unbound capability names. `score_tip` stores them as `rerrs` (1490), but `F['errors']` includes only registry and canonical-list errors (1628). `rerrs` appears only in stderr diagnostics (1689–1690). All twelve legitimate plans can remain unchanged while extra invalid rows are ignored.

Focused probe: appending an unbound four-column row plus a malformed row produced `['regress-cols:1', 'regress-unbound:not-a-cap']` while all twelve plans remained byte-identical. A missing mandatory `pin-watch` row correctly produced `regress-missing`; this is **not** a silently skipped mandatory-row bug.

Verdict direction: **toward met=True / errors=0 despite known input errors**. [INFERENCE] A full score with those extra rows can preserve all target counts: no full mutated-counter run was performed. `regress_table_controls` also omits baseline table-level errors from `base_tags` (1727), so its unbound-cap control can be credited for a pre-existing error rather than its new plant. This violates the stated "new failure absent from baseline" interpretation of controls.

Recommendation: include table-level errors in the baseline error count and include their tags in regression-control baseline tags.

### Medium — D3: tally subprocess failure is ignored

`run_tally` parses stdout and returns records without checking `p.returncode` (970–977). `tally_count` counts any nonempty status except two negative prefixes (961–967). A tally that prints complete records and then exits nonzero still supplies `tally_disclosed=8/8`; the same unchecked helper serves the independent no-disclosure fixture (1004–1005). The separate selftest only proves another invocation exited successfully (1017).

Verdict direction: **toward met=True** when the scored tally invocation fails after printing records but its separate selftest/fixture invocations succeed. This is a code-path finding, not an observed failure of the current tally. Unlike the reconciler, the tally is not byte-pinned in PINS/DEP_PINS.

Recommendation: require successful exit before using records, and surface failure rather than representing valid-looking partial stdout as a successful read.

### Low — D4: host/path-dependent manifest and unquoted shell substitution

`MODEL` expands the invoking HOME at import time (71), becomes part of the exact expected registry command (136–137), and is compared literally with the committed run template (561–563). The registry's llama lifecycle row contains `/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf` (`registry/capability-claims-r64.tsv:4`). Changing HOME changes the expected contract even when the committed artifacts are unchanged. Bound tools additionally locate their server/model in user-local installations (`kama-context-capacity.py:58–59`; `kama-ollama-live.py:324–325`). These are host prerequisites, not tip-contained inputs.

`placeholders` substitutes tree/work/repo strings without quoting (282–284); Runner passes the result to `bash -c` (742). A valid work or repository path containing spaces therefore splits arguments and can cause a counter failure unrelated to capability behavior.

Verdict direction: **toward met=False** on a different HOME, absent installation, or whitespace-containing path. No such failure occurred with this seat's prescribed host/path. Recommendation: use explicit fixture paths and argv construction, or reject unsupported path syntax before scoring.

## Requested hazard audit / residual risks

- **pgrep snapshots:** 263–279 ignores the pgrep exit status and unreadable/disappeared `/proc/<pid>/stat` entries. The counter snapshots surround the entire execution (740, 753), not the tool's individual polls. `busy_check` requires only `(before & after) <= seen` (481). A focused direct call accepted an invented nonempty set `[999999999]` when before={101}, after={202}. This is a vacuous-intersection limitation, **toward met=True**, not a contradiction of the explicitly amended freeze rule. It does not establish continuous occupancy or an exact observed set; PID reuse/polling races remain. The docstring's stronger "covered by observations" wording (22–24) and comment "cannot be met by an invented set" (461–464) are not supported. No stronger snapshot equality is claimed by this review.
- **Timing-dependent negatives:** an execution must meet live-tool deadlines and Runner's 900-second deadline (69, 746), including the forced-idle live fixture on a busy host. Host contention can produce **met=False** without changed repository state. No flake occurred in the required run, so no rerun was needed.
- **21-second wait:** only the baseline context row waited 21.0 seconds in this run. It does **not** multiply across all twelve rows: other rows have no host-idle wait; the committed context regression inverts the model preflight and refuses before the wait (`registry/capability-regress-r64.tsv:6`); printers return immediately; idle-live uses a fake pgrep (732–739). It may add contention/wall time across independent counter instances, but no within-counter 12×21-second defect was found.
- **TMPDIR/temp placement:** Runner deliberately replaces inherited TMPDIR with `work/run` (690–692); auxiliary live tools receive `TMPDIR=work` (1467–1469), and tally selftest receives its own work subtree (1011). No counter-authored `tempfile` or hard-coded `/tmp` path was found. Git/archive/tar plumbing and work-probe subprocesses inherit the parent environment instead (214–221, 255–257, 895, 985, 1613–1619); therefore the "everything under work" claim is not a sandbox guarantee. No actual out-of-work temporary write was observed or traced.
- **Overlay symlinks:** all non-tools top-level entries are shared symlinks into `work/tip` (704–707). A writer can contaminate other overlays, so these are not isolated trees. `copytree` uses its default dereference behavior (708–709), so an input tools symlink can also read outside the tree. Replacement writes use unrestricted joined paths (710–712), though all production callers supply fixed tool paths. No escape or verdict flip was demonstrated for the scored tip; the shared targets there remain under work. Counter executes tip tools before checking pins (1494–1547), so failed pins do not protect execution from an untrusted tip.
- **String-keyed missing rows:** mandatory capabilities are iterated via SLUGS; missing regression rows get explicit tags (659–663), missing registry rows lose coverage (588), missing tally rounds lose their count (964–967), and missing gate fields fail closed (1050–1053). No mandatory missing-row skip found. Extra table errors are D2.
- **Exception handling:** outer `except Exception` explicitly fails the run (1470–1474); bad JSON/absent receipts fail classification (409–418, 441–442, 470–471); no broad scoring exception that returns success was found. Cleanup suppressions and pgrep error handling are the narrower exceptions described above. Outer failures print text after `met=False` (1473), so failure-path stdout does not literally end with the met token promised by the command description.
- **No scope substitution:** C2 proves the declared registry executions/pins/regression behavior, not a canonical serving runtime, identity rerouting, saturation, or resume continuity. Those contracts are not implemented or graded by this counter; no verdict about them is made here.

## Run evidence and verification gaps

Required command ran from the prescribed shared clone at the measured tip with fresh scratch `work-1`: exit **0**, elapsed **24.50 s**. Original stdout/stderr and detail JSON copied to `.ufo/waves/round-64/f/out/RV04C2CounterCode/` as `counter-1.out`, `counter-1.err`, `detail-1.json`. `pgrep -af llama-server` snapshots are `pgrep-before.txt` and `pgrep-after.txt`. Before included peer servers 1789052/1789100 and pre-existing server 3262613; after included server 3262613 and a transient pgrep command. No own live server remained in the after snapshot. Snapshot differences alone do not prove ownership or exclude sub-snapshot leaks; no foreign process was touched.

LSP unavailable: `read xd://lsp` returned "No such tool"; no semantic references/definition/diagnostics service was available. Used complete source reading and targeted literal dependency search instead; these are not presented as semantic proof. No installed/updated tools. No lane source/index changes or commits. Scratch clone and own probes removed before yield; durable receipts above retained. No full live timeout, genuine idle-host run, filesystem-write tracing, malformed-table full mutant, or tally crash mutant was exercised.

Self-evaluation: accuracy 4/5 (conditional verdict impacts labeled); completeness 4/5 (all requested hazard classes covered, real live timeout deliberately not induced); clarity 4/5 (separates amended-rule limits from defects); actionability 4/5 (concrete locations/remedies, no full mutants); conciseness 4/5 (scope-complete report). Overall 4.0. Highest-value further verification is a controlled context-child timeout with independent descendant teardown observation; this remains a gap, not a reported live result.

## Exact required counter output

tip=23b3fdb1a925 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[canon=4/4,closure=5/5,flip=11/11,gate=16/16,idle=21/21,pattern=5/5,pins=5/5,printer=2/2,reconciler=11/11,registry=17/17,regress=11/11,selftest=1/1,tally=8/8,work=3/3] met=True
