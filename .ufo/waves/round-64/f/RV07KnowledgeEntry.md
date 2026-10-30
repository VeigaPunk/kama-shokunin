# RV07KnowledgeEntry — round 64 wave f

Axes: operability + calibration; assigned judgment surface: operability knowledge draft.
Recommendation: **admit-with-repairs**, not admission and not a verdict on C1/C2.
The procfs distinctions are useful and in province. Do not promote the present draft as a description of the amended instrument without the repairs below. Preserve the wave-b draft as historical bytes; publish the corrected entry separately or append a dated supersession.

## Scope and evidence

Reviewed `.ufo/waves/round-64/b/out/SB01Knowledge/process-bound-listener.md` (164 lines), its quote-check source/output and first demo receipt; `corpus/QUALITY.md` through KQ115; `PROVINCE.md`; `corpus/SOURCES.md` rows S049/S495/S496/S499/S529–S532; freeze including amendments 1, 1a **and 1b**; and wave-b MT01DumpableHide, MT05EnvInject, MT06MapsLib, MT13ProbeTokens.
`D:L` below means a draft line; `C:L` means `tools/round64-c1-counter.py` at measured candidate `23b3fdb1a925129a9961cf551f6d40bf251602cb`.

Inspected counter file and that candidate's git blob both hash to `1ffea590bcb4a2db3e1183221ebe1f2dd9841f4811c9bcd54de80f2484b817d9`.
Commands: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 23b3fdb1a925129a9961cf551f6d40bf251602cb:tools/round64-c1-counter.py | sha256sum`; `sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round64-c1-counter.py`.
These are source correspondence checks, not a live-counter measurement.

LSP device prerequisite: `read xd://lsp` returned `No such tool: xd://lsp`; no server/status/references/definition/diagnostics surface is mounted. Used literal searches and source reads, not semantic caller proof.
No code, demo, quote checker or counter was executed; no clone or scratch root was needed; no processes started or signalled; no installs/upgrades; no source edits, git mutation, or sibling messaging.

## High severity findings

### H1 — the headline binding exceeds what its observations establish

D9–20, D59, D67–69 and D161 describe a conjunction identifying the answering process. S529 supports the socket-inode/fd join, not a complete unprivileged holder inventory. S495/S499 support opening the executable file, not measuring every running memory page. The explanatory qualification at D56 is too weak: it calls an already demonstrated counterexample an untested inference.

- MT01 §1/§3: O3 answers via a pre-existing non-dumpable helper while the real child is the sole *visible* holder; O4 silently retains a duplicate descriptor. Both passed the old counter. Amendment 1's state check addresses O3's stopped real child, but the silent older helper limit remains acknowledged at freeze lines 175–180. C452–455 still excludes pre-tool unreadable tables from the failing set. Say **every observed/readable holder**, with the old-unreadable exclusion immediately beside the claim, not an unconditional every-process guarantee.
- MT05 F2: `/proc/<pid>/mem` changes served `id` bytes without changing disk digests, namespaces, mapped-file identity or TracerPid. This survives the proposed namespace/tracer/map fixes (MT05 lines 145–160); freeze explicitly retains the limitation. D67's “image the process runs” and D69's universal “Any holder ...” need file-byte versus live-memory qualification. An executable digest is not complete code integrity (also KQ94).
- D18 says steps 1–5 are the binding, but the numbered list includes exit as observation 5 while the later headings put ancestry in Step 5 and teardown in Step 6. Normalize the enumeration; otherwise “steps 1–5” changes meaning mid-entry.

Repair: frame this as bounded Linux snapshot evidence for the lane-owned fixture; state what the join observes, not an unqualified identity theorem. Keep reference agreement separate, but do not imply procfs alone closes the demonstrated answerer counterexample.

### H2 — receipt replay is missing from the teaching entirely

D16/D125–127 discuss only two outside probes. MT13 §3 showed a genuine pinned child plus a replayed lifecycle receipt passed every old binding check and 76/76 controls. Thus the draft's recipe can still certify a lifecycle that the tool did not perform. This is distinct from whether an answering process is pinned.

Amendment 1 adds a per-run tool request and reference comparison. C807–826 grades `receipt_req`, `receipt_ref_text`, `receipt_ref_usage`; C875 onward draws three requests, including the tool request. Teach the new join and its limit: equality with reference bytes is not independent observation of every claimed HTTP interaction. The old text remains valid only as explicitly superseded freeze-era analysis. KQ108 applies directly.

### H3 — maps/argv/environment descriptions contradict the candidate

- D80 says selected flag-value checks; candidate C491–496 checks equality to `expected_argv` (C553–557). Extra flags and alternative model forms are no longer accepted by that check. Keep empty-argument dropping as a separate residual normalization fact (C400–402), not a reason that the current comparator uses pairs.
- D84/D90 say keys only and a denylist. Candidate C406–413 records values; C498–503 admits only keys present in the expected allowlist with equal values (it does not require every allowed key to be present).
- D55 says only own-uid unreadable tables fail and other uids vanish. Candidate C270–316 retries unreadable tables of any uid, four times at 50 ms; C452–455 applies the start-time exclusion. Explain amendment 1b's transient-exec readability retry, without calling it complete race elimination.
- D93/D98/D164 say dev/inode comparison is unimplemented and propose comparing to stat(path). Amendment 1a implements live/reference `(path,dev,inode)` set comparison, C831–840. MT06 lines 137–144 specifically reports a stat-based implementation rejecting honest btrfs mappings; the surviving recommendation is not a drop-in fix.
- D99's “no control exercises this” is obsolete: MT06 d exercises `/usr/lib` shadowing; amendment 1a adds reference-file controls at C1672–1679. `bind_maps` still skips those prefixes (C524–525), but `bind_ref_files` is an additional guard. Describe both, not blanket system-path acceptance by the complete candidate.
- D106 omits the hold-mtime upper bound added at C544–549. D125 omits namespaces, tracer and state observations now relevant to binding (C504–510, C841–844); cite S533/S534 if teaching their documented semantics.

These are drift, not proof the author's historical readings were false: D2 pins f6a4. KQ3/KQ39 require an explicit temporal boundary rather than silently treating them as current facts.

## Medium severity findings

### M1 — missing or overstated limits from the named falsifiers

| Source | Required treatment in repaired entry |
|---|---|
| MT01 O3/O4 | Replace “inference” at D56 with attributed observed counterexamples; distinguish answering helper from silent duplicate holder, and old instrument from amended state check. Do not generalize unprivileged invisibility into impossibility for privileged observers. |
| MT05 F1/F8 | Add demonstrated mount-namespace/path-shadow distinction. Namespace equality and reference file identity now constrain it; D43/D133 alone do not teach the fix. |
| MT05 F2/F6 | State disk versus memory divergence remains; snapshot TracerPid=0 does not imply nobody previously modified memory. F6's tracer is now explicitly checked. |
| MT05 F3/F5 | Distinguish old key-only gap from present allowlist-with-values; do not retain D90. |
| MT05 F4 | The man page's “initial environment” wording is not an immutable exec-time snapshot: same-length writes into its backing block are visible. The draft's ordinary os.environ experiment at D86 does not refute this observed case. |
| MT06 a1/a2/a4/b2 | Describe namespace shadow, model replacement/new inode, identical-byte copy identity, and in-place content change separately. Candidate fresh hashes/reference identities address different distinctions; inode equality alone does not prove mapped memory equals disk. |
| MT06 c/d | Explain pinned-but-never-normally-loaded library and system-path shadow controls, now caught by reference mapped-file set. |
| MT06 §6 | Preserve two-snapshot/transient-change limitation (D42/D134 already acknowledge it); add finite-probe/unprobed-prompt limit rather than claiming exhaustive behavior. |
| MT13 §1/§4 | Reference testing is a finite sampled population, not universal agreement. Old genuine fuzz never exercised EOS/stop (1210/1210 were length); draw-distribution, status and fingerprint-shape mutants survived. Attribute these as freeze-era results, not rerun claims against candidate. |
| MT13 §3 | Include replay and amended receipt binding as H2. |

Also carry freeze's post-release-holder limit (CR03 K5): an observed closed listener at the poll is not a guarantee that no new holder appears later. D121 mentions new listeners during the window, but not after it.

### M2 — provenance/recheck is present but cannot detect the advertised freshness drift

D1–3 contain the required provenance trio and explicitly disclaim a live result, which is good. But the recheck reads the *same old commit forever*. Moved lines in the current instrument cannot change `git show f6a4:...`. `recheck-quotes.py:16,127–133` defaults to f6a4, prints the old family count, and exits only on quote membership. The line-number grep is a separate manual expectation, not an enforced correspondence test. Its listed function order also places `pid_gone` before `reference_run`, contrary to source order.

The helper checks page-wide whitespace-normalized membership (`:96–98`), not paragraph/line anchors, so 27/27 is not proof of every located anchor. It prints S049 line locations and digest equality (`:102–107`) without including either in exit status. The receipt `recheck-quotes.out:39–40` establishes what was printed historically, not those stronger promises. Recheck of the full long environment quote at D84 is only fragment checks (`:63–65`), not the whole quoted sentence.

Repair: separate historical f6a4 reproduction from a current revision recheck; make correspondence/anchor expectations explicit and report quote, anchor, digest, and code correspondence separately. KQ14/KQ45/KQ56/KQ96/KQ113.

### M3 — counts and negatives need bounded reproducibility

- D147's 76/28 is a frozen declaration, not the amended population. Label f6a4 explicitly beside the number; a current declaration is 91 targeted controls and 8 evaluator plants (freeze amendment 1b), not a measured result supplied by this review.
- D110/D155 cite unsaved transcript runs as numerical evidence; omit those counts from the durable entry or retain the actual transcript artifact and exact invocation context. Relative `python3 procfs-demo.py` and bare `procfs-demo.run1.out` need the evidence-directory cwd/path, observation date and exits. D154's lane-relative command is preferable.
- D29's command checks only forge.out; its claim also includes sleeper.out. Supply commands for both and the run-command/exit receipts if presenting these as counter results (KQ43).
- D43's “S049 does not say so” and D99's “no control exercises this” carry no named full-set sweep. First is supportable from the full short document I opened; second is obsolete. Cite full pinned-document read/search for source negatives; enumerate/search all pinned control builders for code negatives. Do not treat “inference” as exemption from negative-claim scope rules.

## Anchor ledger — old references are historical, not invalid at their pinned revision

Every following counter citation in D is stale **if used as a current/candidate pointer**. Preserve the old revision, and append this supersession rather than rewriting historical evidence.

| Draft location / old counter anchor | Candidate anchor / disposition |
|---|---|
| D3,D35: listeners 238–255 | 250–267 |
| D35: bind_listener 410 | 480–481 |
| D42: raw_a/raw_b 898–902; bind_stable 722 | 1049–1055; 845–846 |
| D49: holder_pids 258–286 | 270–316 (changed semantics/retries) |
| D55: 270–276 | 278–316; own-uid claim superseded |
| D56: collect 382–385 | 434–457, especially 452–455 |
| D57: bind_claim 730 | 847–854 |
| D65: holder_record 339–346; hash 344 | 391–398 |
| D65: bind_exe 417–419; SERVER_SHA 49 | 487–489; 57 |
| D80: cmdline 348–352; argv_ok 421–433 | 400–404; 491–496 and 553–557 |
| D84: env 354–359; bind_env 434–437 | 406–415; 498–503 |
| D93: read_maps 311–336,334 | 341–367,364–366; see additional reference-set guard |
| D93/D99: SYSTEM_* 140–141; skip 451 | 150–151; 524–525 |
| D93: maps_ok 439–462,456–458 | 512–536,529–532 |
| D95: deleted 445; D100: blank 449 | 518–519; 522–523 |
| D98: path hash 334; unimplemented dev/inode | 364–366 plus file_set 373–376 and score 831–840 |
| D106: stat_fields 289–296; ppid_chain 299–308 | 319–326; 329–338 |
| D106: ancestry 465–466; hold_fresh 469–476,472 | 538–549,547; additional mtime upper bound 546 |
| D106: pid_gone 843–855 | 971 onward; now unreadable ticks fail closed |
| D113: equality >= 472 | 547 |
| D115/D127: detach/proxy scenario 1592/1593 | 1989/1990 plan entries; execution at 1998. |
| D119: release 916; gone 922; port 924 | 1071; 1078; 1079 |
| D125: reference_run 806–840; probe_fails 631 | 932 onward; 714 onward |
| D125: draw_probes 751–765; RNG 1481 | replaced by draw_requests 875 onward; RNG 1816–1817 |
| D127: reference health 822 | 948 |
| D135: MODEL_SHA 48 | 56 |
| D150–153: extraction ranges 48–49,289–296 | 56–57,319–326 for candidate; old commands remain historical |

Tool pointers in D33/D41/D57 are to other files, not mechanically invalidated by counter edits; this review does not label them stale merely because the counter moved.

## Primary-source cross-check

I independently opened all seven distinct primary pages (S495/S499 are the same page), not only their registry rows:

- [S049 kernel v7.2 document](https://raw.githubusercontent.com/torvalds/linux/v7.2/Documentation/networking/proc_net_tcp.rst): deprecation, field diagram and listening-first text agree; no numeric TCP-state enumeration or IPv4 endian prescription. The entry correctly separates these from code-derived knowledge.
- [S529 fd DESCRIPTION](https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html): `type:[inode]`, socket join, access check and main-thread termination caveat agree. Does not promise every table is readable.
- [S530 stat DESCRIPTION](https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html): ppid field 4, starttime field 22, tick units agree. Fine-time order is an inference limited by resolution; draft already explains that.
- [S531 environ DESCRIPTION](https://man7.org/linux/man-pages/man5/proc_pid_environ.5.html): execve/ordinary environment-change/region-relocation quotes agree, but do not establish an immutable original-memory image; MT05 F4 supplies the necessary empirical qualification.
- [S532 cmdline DESCRIPTION](https://man7.org/linux/man-pages/man5/proc_pid_cmdline.5.html): NUL layout, rewrite freedom and “wants you to see” quotation agree.
- [S495/S499 exe DESCRIPTION](https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html): opens executable, deleted suffix and ptrace check agree; no promise of live-memory integrity or artifact-origin identity.
- [S496 maps DESCRIPTION](https://man7.org/linux/man-pages/man5/proc_pid_maps.5.html): dev/inode/path, anonymous mapping and deleted ambiguity agree. It does not guarantee pathname equals current file bytes. D100's anonymous explanation should not imply inode 0 is exclusively anonymous: the source also names BSS.

No fabricated quotation found in these opened passages. Locations are usually named DESCRIPTION rather than numbered paragraphs; tighten each to a paragraph or retained-copy line. Semantic observations do not substitute for byte-exact verification of the author's fetched HTML digests.

## Quality/admission rule disposition

- KQ1/KQ2/KQ4/KQ13: substantially respected by no-live-verdict disclaimer and separate behavior/identity discussion; add explicit “no registered-consumer health/model-quality result” scope. No present endpoint success is admitted here.
- KQ3/KQ6/KQ11/KQ27/KQ36/KQ39: dated source/version/trio are strengths; H3/M2/M3 prevent current use without revision-specific supersession. Frozen true statements later drifting are not retrospectively false-at-writing.
- KQ5/KQ10: review stayed read-only/in province; draft should retain controlled fixture-only scope, not authorize consumer/service changes.
- KQ7/KQ14/KQ26: publish an appended stale-anchor/content ledger preserving the old draft; in-bounds offsets alone do not establish the repaired semantics.
- KQ8/KQ9: policy-location gap below is explicit; negative claims need full bounded sweeps; no unexecuted command is represented as a pass.
- KQ20/KQ21/KQ23/KQ24/KQ25/KQ63: conjunction and teardown teaching must not imply universal/control-complete guarantees; name trigger, state, release/poll and finite controls, and distinguish errors/unobserved properties from semantic failures. This draft supplies no new mutation or live receipt.
- KQ43/KQ66/KQ69/KQ74–76: apply to demo/live receipts only insofar as offered as runtime/reproduction evidence; do not launder the local procfs demo into reproduced model-server integration. Current draft's explicit no-counter-run limit is correct; retained numerical receipts need exits/context as M3.
- KQ45/KQ46/KQ56/KQ96/KQ113: source ids resolve to the claimed artifacts and opened documentation agrees; quote helper membership is weaker than located-anchor checking (M2).
- KQ80/KQ81/KQ85/KQ91/KQ94/KQ106–109: relevant identity/provenance distinctions, not a requirement to claim archive replay here. H1–H3 identify the scope mismatches; don't claim digest implies which origin file or unchanged memory ran.
- KQ102/KQ103/KQ112/KQ114/KQ115: if counter control sufficiency is mentioned, disclose amended rules, work-reuse refusal and finite evaluator scope, not the old 76/3 population or universal saturation. No runtime/same-identity-rerouting/resume-continuity claim is made in this documentation item.
- KQ12's domain/overlap separation respected; no axis promotion/denominator claim is made. Remaining criteria govern other artifacts (append-only audit implementation, source-registry edits, report landing, C2 registry scoring, replay execution, release ledgers, staged refusals, etc.); this entry neither changes nor establishes them.

CORPUS.md: not present at the lane root; recursive filename searches in the authorized lane and `/home/vgpnk/Projects/shokuknow` returned no file. I did not traverse the forbidden fleet repository to obtain another copy. Applied the four rules explicitly supplied in the assignment: provenance trio present; count-command repairs M3; negative-sweep repairs M3; quoted-location repairs M2/source notes. Full independent CORPUS-policy-text review remains a verification gap, not a claimed pass.
PROVINCE.md:3–15,42–45,57–71,84–90 place local listener/process identity and lane-owned fixture health in kama. This is in province when limited to serving identity, not model quality or broad host security.

## Residual risk and handoff

A repaired entry remains a bounded method, not a saturation result: pre-tool unreadable holders, memory writes, transient behavior and post-release activity remain limitations. Candidate behavior is source-reviewed, not independently replayed here. The L1 should review the corrected prose/anchors and, if needed, run its fresh-work registered counter at the chosen committed tip; this report supplies no new met result. Historical output below is **read from** SB01Knowledge/recheck-quotes.out:40, not rerun by this reviewer.

Self-evaluation: accuracy 4/5 (candidate bytes pinned; no live replay); completeness 4/5 (all named wave-b reports and distinct primary sources opened; full CORPUS policy unavailable within bounds); clarity 4/5 (severity plus anchor ledger; long ledger is necessary for requested exhaustiveness); actionability 4/5 (specific repairs/source anchors; amended draft not yet supplied to this seat); conciseness 4/5 (one scoped report, no repeated counter family lists). Mean 4.0. Highest-impact repairs: headline/receipt scope, then revision/content supersession, then reproducible located quotes. The user should treat this as advisory review, not admission.

quotes OK=27/27
