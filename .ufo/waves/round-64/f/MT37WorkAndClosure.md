# MT37WorkAndClosure — round 64 / wave f

Axes: operability + calibration; this leaf reports calibration probes only. Advisory findings, not a verdict on C2. No lane source edits or commits; commits were scratch-clone fixtures only. No installs or upgrades (versions in `out/MT37WorkAndClosure/versions.txt`).

## Method and bounds
Pristine tip: `23b3fdb1a925129a9961cf551f6d40bf251602cb`. Read freeze, X01C2Counter and X06Reconciler reports. Two shared scratch clones; all counter runs used fresh explicit scratch work paths. Detector: `python3 tools/round64-c2-counter.py --repo CLONE --tip TIP --work FRESH`, from clone tools/. Counter mutants ran from clone2/tools/ against the committed pristine tip; tree mutants were committed and scored by the unchanged counter.
KILLED = counter exits 1 with met=False; SURVIVED = exits 0 with met=True. Guard-only probes are separately labeled REFUSED/FREE, not falsely called met=False runs. Baseline and restored full runs both exit 0, met=True, 120/120. Seven tree probes were repeated to retain complete receipts after the first driver printed only prefixes; all classifications agreed. No observed live-run flakes. Full stdout/stderr, exact patches, mutant hashes, tip IDs and restoration evidence are under `out/MT37WorkAndClosure/`.

## Findings (no claim verdict)
- **W2/W3 SURVIVED:** replacing lexists with exists or isdir leaves work=3/3 and 120/120 met=True. Concrete guard probes show W2 accepts a dangling tip symlink; W3 also accepts regular files named tip/run. Pristine refuses those. These are control-coverage findings, not evidence that a genuine populated tip directory can be silently reused. Both mutants still refuse a real used directory, including through a symlink.
- **B5 accepted (SURVIVED):** a same-commit pointer repair to round 64 plus a newly authored round-64 spotcheck file gives met=True, 120/120. This satisfies the frozen numeric/tree-equality predicate. It does **not** establish independent authorship, provenance, or temporal “outside-ness”; do not treat this as a frozen-predicate violation. X01 already disclosed the pre-closure scoring ordering constraint. The added file contains fixture prose claiming a closure; that prose is an injected mutant, not a genuine closure report.
- **B4 KILLED by a backstop:** the nonexistent round-063 path passes the numeric closure checks (counter closure_ptr=1 and reconciler closure_ptr=1), but r41 dead-path adds one mismatch. Durable `B4-reconciler.out` explicitly says `detail: r41 calibration dead path corpus/lessons/round-063-verifier-spotcheck.md`.
- **B7 KILLED by reconciler:** correct pointer plus stale “including round 62” gives counter closure_ptr=1 but recon closure_ptr=0/mismatches=1. Thus recon_mismatches is independently load-bearing here.

## Pristine work-input probes
`guard-probes.txt/json` contains exact rc/output for all shapes and W2/W3 comparisons. With --probe-work: empty tip/, run/ only, tip symlink to a directory, dangling tip symlink, regular files named tip/run, used work, relative used/./used, and a symlink to used work all return 2 `work-reused` on pristine. Clean or hidden-file-only work returns 0 `work-free` (no tip/run exists, consistent with the predicate).
An actual second full invocation on the completed work returns 2 and only `work-reused: ... refusing to score`, no met= line (`w-second.second.out`).
Pre-existing counter-owned scratch `wr/` (empty directory) is called FREE by the entry guard but a full run fails closed after scoring work: exit 1, `errors=1 met=False  (internal FileExistsError: [Errno 17] File exists: .../wr)`. The guard recognizes tip/run, not every possible collision. No claim-level silent reuse was demonstrated by this collision.

## Exact tree edits and counter one-liners
All B patches are retained verbatim. They change the live Axes calibration row unless stated otherwise; all other files unchanged except the named added spotcheck. Before/mutant SCORECARD SHA-256 and full fixture commit IDs are in `tree-meta.json`.

### B1-two-pointers: KILLED
Append `; second pointer latest outside closure `corpus/lessons/round-62-verifier-spotcheck.md` (older);` after the existing round-63 pointer/inclusion clause. Decides: closure_ptr=0 and recon_mismatches=1.
Fixture tip: `2f7989aa8e6e7f1f91b085797c72a6797aeb0934`. Exit 1.
```text
tip=2f7989aa8e6e population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=0 recon_mismatches=1 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=0/120 errors=0 recon[closure_ptr=0,mismatches=1,maxN=64,met=False] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[] met=False
```

### B2-backtick-style: KILLED
Wrap the round-63 pointer path in double rather than single backticks. Decides: closure_ptr=0 and recon_mismatches=1.
Fixture tip: `bc08090c1653f6d89417a40203a8ebad73d89747`. Exit 1.
```text
tip=bc08090c1653 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=0 recon_mismatches=1 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=0/120 errors=0 recon[closure_ptr=0,mismatches=1,maxN=64,met=False] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[] met=False
```

### B3-pointer-in-historical: KILLED
Replace the live pointer clause with “the latest outside closure is re-derived at the measured tip by the named counter”; prepend the original pointer/inclusion clause to the historical `| calibration | 1 → 7 |` row. Decides: missing live pointer, closure_ptr=0/recon_mismatches=1.
Fixture tip: `7038b09724730971ef8a763e4457281071d201d0`. Exit 1.
```text
tip=7038b0972473 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=0 recon_mismatches=1 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=0/120 errors=0 recon[closure_ptr=0,mismatches=1,maxN=64,met=False] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[] met=False
```

### B4-round-063: KILLED
Only change live pointer filename round-63 to round-063 (no such blob). Decides: recon_mismatches=1, r41 dead-path; both numeric closure flags remain 1.
Fixture tip: `fabf8dd79e65655929dc87f21f8a963a6106586f`. Exit 1.
```text
tip=fabf8dd79e65 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=1 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=0/120 errors=0 recon[closure_ptr=1,mismatches=1,maxN=64,met=False] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[] met=False
```

### B5-round64-same-commit: SURVIVED
Change pointer to round-64 and “including round 64”; add `corpus/lessons/round-64-verifier-spotcheck.md` in the same fixture commit. Exact six-line content in patch. Decides: all target fields and families remain met; no temporal/content provenance check asserted.
Fixture tip: `7c749ca50675011554cb0f7ade852320ea19087c`. Exit 0.
```text
tip=7c749ca50675 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[canon=4/4,closure=5/5,flip=11/11,gate=16/16,idle=21/21,pattern=5/5,pins=5/5,printer=2/2,reconciler=11/11,registry=17/17,regress=11/11,selftest=1/1,tally=8/8,work=3/3] met=True
```

### B6-round64-stale: KILLED
Add the identical round-64 spotcheck file without changing the round-63 pointer. Decides: closure_ptr=0 and recon_mismatches=1.
Fixture tip: `029021152c8f199c302e2983cef106109eedac54`. Exit 1.
```text
tip=029021152c8f population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=0 recon_mismatches=1 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=0/120 errors=0 recon[closure_ptr=0,mismatches=1,maxN=64,met=False] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[] met=False
```

### B7-including-stale: KILLED
Keep round-63 pointer; only change “including round 63” to “including round 62”. Decides: recon_mismatches=1 (reconciler closure flag 0), counter closure_ptr=1.
Fixture tip: `ba054de8755cb5763cb868e39d7d60efde8110ae`. Exit 1.
```text
tip=ba054de8755c population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=1 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=0/120 errors=0 recon[closure_ptr=0,mismatches=1,maxN=64,met=False] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[] met=False
```

## Guard implementation mutants and one-liners
Each is a single behavior-bearing replacement; full source and exact patch retained. Counter before/restored SHA-256 is in restoration.json; mutant hashes are in corresponding .sha256 files.

### W1-drop-run: KILLED
Guard tuple `(tip, run)` -> `(tip,)`. `work/run-dir-only` fails; work_reuse_refused=0. Controls not credited because baseline gate is unmet.
```text
tip=23b3fdb1a925 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=0 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=0/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[] met=False
```

### W2-exists: SURVIVED
In work_reused, `os.path.lexists` -> `os.path.exists`. Same 3/3 work controls; dangling tip symlink incorrectly says FREE in the guard probe.
```text
tip=23b3fdb1a925 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[canon=4/4,closure=5/5,flip=11/11,gate=16/16,idle=21/21,pattern=5/5,pins=5/5,printer=2/2,reconciler=11/11,registry=17/17,regress=11/11,selftest=1/1,tally=8/8,work=3/3] met=True
```

### W3-isdir: SURVIVED
In work_reused, `os.path.lexists` -> `os.path.isdir`. Same 3/3 work controls; dangling tip symlink and regular files tip/run incorrectly say FREE.
```text
tip=23b3fdb1a925 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[canon=4/4,closure=5/5,flip=11/11,gate=16/16,idle=21/21,pattern=5/5,pins=5/5,printer=2/2,reconciler=11/11,registry=17/17,regress=11/11,selftest=1/1,tally=8/8,work=3/3] met=True
```

### W4-guard-skipped: KILLED
CLI guard `if work_reused(work):` -> `if False and work_reused(work):`. second-run-same-work subprocess check fails; work_reuse_refused=0.
```text
tip=23b3fdb1a925 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=0 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=0/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[] met=False
```

### W5-nonempty: KILLED
Guard requires a nonempty directory for each of tip/run: `isdir(path) and bool(listdir(path))`. empty-tip-dir and run-dir-only no longer refuse empty directories; work_reuse_refused=0.
```text
tip=23b3fdb1a925 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=0 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=0/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[] met=False
```

## Restoration and interpretation
SCORECARD before = after in both clones: `e73d2383aa7a420bf402136756cec02730ec45b5844a8ba9a949262bcd393982`.
Counter before = after in both clones: `c8b725e57f6e761735e832d127ec6df622d4a9dff09893b5fa31131c64d93e2e`. Exact byte equality recorded for all four files in restoration.json. Added round-64 fixture file absent after restore. No lane source changed; evidence copied before deleting the seat scratch root.
No inference of claim acceptance/rejection: W2/W3 are narrow coverage gaps; B5 is accepted self-consistency under the stated predicate, not proof of independent closure. Suggested controls for L1 consideration: a dangling tip symlink and regular tip/run files with expected exit 2/no met=; if temporal outside-ness is intended, specify it in the contract before adding a provenance control.
Self-evaluation: accuracy 4/5 (B5 is explicitly limited to the literal predicate); completeness 4/5 (listed shapes covered, not exhaustive races); clarity 4/5 (full long counter lines retained as requested); actionability 4/5 (exact patches/probes retained); conciseness 4/5 (verbose receipts necessary). Overall 4.0/5; highest-impact improvement applied: avoid calling B5 a claim violation and distinguish numeric flags from the r41 backstop.

Restored counter output:
tip=23b3fdb1a925 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[canon=4/4,closure=5/5,flip=11/11,gate=16/16,idle=21/21,pattern=5/5,pins=5/5,printer=2/2,reconciler=11/11,registry=17/17,regress=11/11,selftest=1/1,tally=8/8,work=3/3] met=True
