# CN04ClosureForecast — round 64 non-author closure forecast

Advisory connector; calibration milestone. No claim verdict, admission decision, commit, source edit, live execution, or runtime invocation. Axes considered: calibration + operability. Read-only local evidence only; no installs. No scratch was created, so none remains to remove.

## 1. What the last three closures actually did

References below are `corpus/lessons/round-N-verifier-spotcheck.md`.

- **61, lines 32–60:** closure reran both counters, including the live hold lifecycle, and compared their output to committed receipts. It separately checked the fixture hash and read committed do-nothing controls. Its gate-standard interpretation explicitly distinguished lane counters from sibling gates. It recorded absent seat falsification as an orchestrator defect (94–99), not a reason to withhold its axis findings.
- **62, lines 13–20:** closure did **not** rerun the live gates. It read committed counter output, counted registry rows, and inspected the sensitivity expression. Green C1 output did not compensate for an unsettled falsification wave; C2's four mismatches and tautological sensitivity were independently decisive weaknesses. Untracked files were a status-neutral conformance defect, not equivalent to a false claim (7–11).
- **63, lines 29–55:** closure expressly refused both lane counters because they start servers **or execute the tip's own tools**, citing PROTOCOL §Gate standard. It accepted receipts as **evidence-verified**, not re-measured; independently hashed instrument blobs across revisions, inspected `/exe`/helper provenance, counted registry/corpus facts, compared SCORECARD, and inspected committed forgeries. It distinguished a seat-written zero-log note from independently observable proof. C2's green frozen predicate did not demonstrate discrimination; a stale calibration pointer survived a zero-mismatch reconciler.

**Explicit contradiction:** round 61's live rerun practice is not the current permission precedent. Rounds 62–63 and this assignment require the refusal boundary. Forecast [INFERENCE]: round 64 closure will inspect the experiment's committed evidence and remeasure plain repository facts, not rerun C1/C2. Refusal itself is not a defect; claiming the closure independently reran a receipt would be one.

## 2. Most important local evidence boundary

Define these exact shell bindings for the commands below:

```sh
R=/home/vgpnk/Projects/shokunin/kama-shokunin
T=23b3fdb1a925129a9961cf551f6d40bf251602cb
F=f6a4ea9a8b5a876d685b08e7e582ec0723412a4a
P=.ufo/waves/round-64
```

The current worktree is **not** a snapshot of T. Read-only commands I executed:

```sh
git -C "$R" ls-tree -r "$T" "$P/measured" "$P/controls/c1-mutants-a1.txt" "$P/controls/c1-final-prewave-runs.txt" "$P/controls/c2-prewave-tip.txt" "$P/controls/c2-base.txt"
```

prints exactly one entry:

```
100644 blob e69de29bb2d1d6434b8b29ae775ad8c2e48c5391	.ufo/waves/round-64/controls/c1-mutants-a1.txt
```

Thus the named measured directory and three named prewave receipts are absent **at T**; the mutants receipt is the empty blob. `git show "$T:$P/controls/c1-mutants-a1.txt"` prints nothing. This does not establish that the current files are uncommitted or unavailable at a later revision; it establishes only their absence/emptiness at the nominated measured tip.

Current files read, not attributed to T:
- `measured/final.tip`: `23f341c84e1d92a7b5ba6d97a13dae0436241584`.
- `measured/final-c2.tip`: `c2db22c8d027cde38b1241591383c41f1faddc7b`.
- `measured/c1-final.out`: green 91/91, 8/8, errors=0; the line itself contains no revision.
- `measured/c2-final.out`: starts `tip=c2db22c8d027`, includes `deps_pinned=2/2`, `maxN=64`, 120/120, met=True.
- Current freeze includes **AMENDMENT 1b** and a C2 busy-rule replacement. `git show "$T:$P/controls/freeze.txt"` ends at **1a**; its C2 sentence still requires equality to the same-moment pgrep set. Therefore the current corrected text cannot simply be cited as the frozen text at T.

These are distinct revision associations, not a scalar confidence penalty. They require an explicit provenance account, not silently substituting HEAD for T.

## 3. C1: exact closure-safe commands, output, and limits

Commands in this section were executed read-only; the hashes/counts are observations.

| Command | What it prints | What it cannot show |
|---|---|---|
| `git -C "$R" show "$T:tools/round64-c1-counter.py" \| sha256sum` | `1ffea590bcb4a2db3e1183221ebe1f2dd9841f4811c9bcd54de80f2484b817d9  -` | That any process ran, or that a particular receipt used these bytes. |
| `git -C "$R" show "$T:tools/kama-completion-live.py" \| sha256sum` | `a0c26e14184d664bef75013aac6f1c2a7bb47881eb4bf372b5bb70a26861423c  -` | Pinned answering-process identity in a live run. |
| `git -C "$R" show "$F:tools/kama-completion-live.py" \| sha256sum` | The same `a0c26e…1423c` digest | Tool improvement after wave b: these bytes are unchanged. |
| `git -C "$R" show "$T:$P/controls/c1-base.txt"` | Old 76-control red-before receipt: `live_ok=0/1`, `eval_selftest=0/3`, `errors=1`, `met=False`, exit annotation 1 | Red-before under the final 91-control instrument; the stored command even abbreviates the base revision incorrectly, while its separate `tip=` line supplies the full base. |
| `git -C "$R" show "$T:$P/controls/freeze.txt"` | Original predicate, amendment 1 and 1a; declared 91 controls after 1a | Amendment 1b timing or the corrected C2 busy rule in current bytes. |

**Do not run in closure:** `python3 tools/round64-c1-counter.py --repo "$R" --tip "$T" --work <fresh-scratch>` starts live servers. A green stored summary is expected to contain `live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[] eval_selftest=8/8 errors=0 met=True`; current `measured/c1-final.out` contains these fields, but is associated by its pointer with 23f341c8, not T. No C1 execution was performed by this seat.

Closure may read an archived summary using `git show E:.ufo/waves/round-64/measured/c1-final.out` **only after E is supplied as an evidence-containing commit**. No such E is invented here. Its output is the archived text, not a new experiment. Process identity, request/answer/reference agreement, named-control reasons and teardown require archived detailed witnesses plus the counter source; a summary alone does not reconstruct ephemeral procfs.

## 4. C2: exact closure-safe commands, output, and limits

Executed read-only:

| Command | What it prints | What it cannot show |
|---|---|---|
| `git -C "$R" show "$T:tools/round64-c2-counter.py" \| sha256sum` | `c8b725e57f6e761735e832d127ec6df622d4a9dff09893b5fa31131c64d93e2e  -` | That its pin/regression/printer experiments ran, or that no joint instrument/tool edit can bypass them. |
| `git -C "$R" show "$T:registry/capability-claims-r64.tsv" \| wc -l` | `13` | Unique canonical coverage or executed work: it is only header + row cardinality. |
| `git -C "$R" show "$T:$P/b/out/X06Reconciler/after-new-tool-clone-tip.out"` | `tip=0913c70d79d8eae2867954d6ac357f9a88cf4430`, then `r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 closure_ptr=1 mismatches=0 maxN=63 met=True` | A rerun at T: the receipt identifies its own scratch revision. |
| `git -C "$R" show "$T:$P/b/out/X07Tally/after-56-63.txt"` | Header `rev=0c1eff3c…`, eight rows and located disclosure detail; statuses listed below | T's current execution, correctness of each historical claim, or numerical shortcut/mutant totals. |

Exact commands a closure can use for **plain offline remeasurement**, after extracting the scripts from T into its own permitted scratch clone D checked out at T (not executed by this seat):

```sh
python3 "$D/tools/round42-selfdesc-reconcile.py" --repo "$D" --tip "$T"
python3 "$D/tools/shortcut-tally.py" --repo "$D" --rev "$T" --rounds 56-63
```

These are not the live gate. The reconciler's ordinary path reads git blobs; do not add `--selftest` casually (it creates/commits fixture variants). Its formatter prints `tip=<resolved tip>` and a fact line ending `closure_ptr=<0|1> mismatches=<n> maxN=<n> met=<bool>`, followed by details. [INFERENCE] with the corrected T calibration row, expected facts are the zero-mismatch line above with `tip=T`, `maxN=63`; this expectation is **not an observed T rerun**.

Tally prints a repo/revision header, table, then located statement details, not one scalar success line. Expected statuses [INFERENCE from the committed X07 output, not a T rerun]:

```
56 disclosed:shortcut+survivor
57 disclosed:shortcut+survivor
58 disclosed:survivor
59 disclosed:shortcut
60 disclosed:shortcut
61 disclosed:no-falsify
62 disclosed:no-falsify+shortcut
63 ok
```

`disclosed:*` means a statement exists, not that its content is true or countable. X07 explicitly says `--check 63` cannot certify the shortcut count; do not substitute it for the frozen non-`no-disclosure` predicate. A closure can also inspect the ordinary scripts statically instead of executing lane-owned Python if applying the stricter refusal boundary.

**Do not run in closure:** `python3 tools/round64-c2-counter.py --repo "$R" --tip "$T" --work <fresh-scratch>` executes the bound tools, including live serving/context checks. Required stored fields include `covered=12/12 mismatches=0 pinned=13/13 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 sens_selftest=4/4 controls_rejected=120/120 errors=0 met=True`. Current green output has these but labels c2db22c8, not T. Host-busy is a declared refusal outcome, not proof that an idle capacity experiment ran.

## 5. Five likely rejection reasons, ranked by earlier closure evidence

Forecasts only; ranks express recurrence/directness of historical evidence, not a judgment of this round.

| Rank | Likely reason and precedent | Repair the report can pre-empt without changing the experiment |
|---|---|---|
| 1 | **Green counter certifies the wrong thing / survivors contradict the claimed property.** R63 C1 forgeries and C2 tip-tool printers; R62 tautological sensitivity. | Give each decisive survivor its named clause, tool/counter revision, full output and scope. Distinguish answering-process evidence from tool bookkeeping and work-sensitivity from printed strings. Preserve original and amended readings: amendment 1 acknowledges K1c violates the original kill wording. Disclosure is not a cure for a false universal property. |
| 2 | **No settled independent falsification handoff.** R62 C1 remained provisional despite green output; R61's contrary treatment is not reliable current precedent. | Cite the final f dispatch/results/settlement artifact, completed/dead seats, and every material unresolved finding at report cut-off. Seat count or dispatch alone is not settlement. Do not claim a future handoff already exists. |
| 3 | **Evidence is not bound to the scored revision/instrument.** R63 compared counter hashes across freeze, measured and closure commits and carefully qualified the forgery-log note. | Supply the two-revision capsule below, exact full hashes, instrument digests, command/env/work/exit annotations and receipt paths. Explicitly separate original 76-control red-before from final 91-control runs; do not call the empty T mutants file six kills. |
| 4 | **Zero mismatches misses an observable self-description contradiction.** R63's stale latest-closure row defeated the broader calibration story. | Include independent row/registry/corpus facts plus the pointer check at measured T. Explain that adding closure 64 changes the maximum and requires closure-time reconciliation at a new revision; do not present the old green receipt as valid automatically after that edit. |
| 5 | **Post-data amendments / improvement attributed to a tool already doing the work.** R63 conformance audited amendment timing and unchanged post-wave instruments; R63 excluded a real but unclaimed proxy side effect from axis credit. | List original freeze, wave-b scored hash, each numbered amendment and first affected measurement; say tool bytes remain a0c26e…1423c. Separate stronger observation from a newly enabled endpoint. State original/amended busy-rule and schema-kill contradictions verbatim; leave their legitimacy to the non-author closure. |

Broad clean-state claims are also worth avoiding: R61–62 examined untracked leftovers, but explicitly treated them as status-neutral, so they rank below these substantive reasons.

## 6. One bounded proposed move: two-revision closure capsule

**Move:** add one report-local provenance table that separates **measurement revision M** from **evidence publication/closure revision E**, per claim, with frozen counter SHA, exact command, output+exit, detailed witness locations, original/amended predicate text and settled-wave reference. This is a reporting synthesis, not a counter/tool change and not a second runtime.

- **Evidence:** T lacks measured receipts and contains an empty mutants receipt; current C1/C2 pointers name different later revisions; X06 warns that a new spot-check makes the old pointer stale. R63 already practiced evidence-vs-remeasurement separation.
- **Calibration gain [INFERENCE]:** closure can verify committed bytes at M while retrieving the later-published experiment at E without mistaking a publication for a fresh measurement or a closure-induced mismatch for a failed original run.
- **Operability unchanged:** no listener, server, pin or runtime behavior changes. Closure performs only git reads and optionally plain offline fact checks, avoiding host interference.
- **Contract/substrate effects:** preserve both readings of amendments; publish evidence after running rather than pretending it existed inside its own measured tip. Hash comparison establishes instrument identity, not receipt authenticity. E must actually contain the cited files.
- **Verification:** closure checks `git show M:tools/round64-c{1,2}-counter.py` hashes; reads `git show E:<receipt>` plus its declared M/command/exit and detailed witnesses; checks the settled wave's revision association; remeasures row counts/pointer/tally facts only under the documented boundary. If a closure file is appended, report old M facts and new closure revision facts separately.
- **Risks:** a precise capsule may expose rather than remove a substantive survivor or freeze-timing defect. That is desired calibration; it must not be sold as resolving one. Do not rename later measurements as T measurements, rewrite frozen receipts, or rerun live gates in closure to fill the gap.

Self-evaluation: accuracy 4/5 (offline T outcomes explicitly inferred, not executed); completeness 4/5 (future closure decision intentionally unavailable); clarity 4/5 (two-revision distinction is essential but dense); actionability 4/5 (E must be supplied by publication owner); conciseness 4/5 (command/output tables retain audit detail). Overall 4.0/5. Highest-value improvement is the capsule with actual E and settled-wave links; this seat cannot manufacture them. Would the user agree? [INFERENCE] yes: the forecast preserves refusal boundaries and evidence gaps rather than issuing a verdict.

Counter/tally execution: NOT RUN (closure-forecast advisory; git-only observations above, no live gate or Python runtime invoked).
