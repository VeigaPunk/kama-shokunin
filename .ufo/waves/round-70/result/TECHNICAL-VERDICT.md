# Kama70 independent technical review — actual first batch

Reviewer judge_kama_round70_plan, parent-appointed non-author; 2026-11-03. Actual batch finished03:05:53UTC; exact bytes recovered later after capacity errors, no rerun. **Technical claim verifies; final lane report/no-harm readback and runtime-pin reference remain to be bound before final closure recommendation.**

## Evidence and independent re-adjudication

Prospective43-case oracle was committeda1aa47528aef1ed4d67fd485be62aa5e94b0ed11 before candidate implementation. Candidate first landeded68fc1552e372f8bb9f14e875f970ffed4f22c5, tool SHA2564ab1c36b3e0fd892e7bd25a7cae8b853266fd037a73025ef207c51d92a4bbfc7. Evaluator+actual source mutants were frozen before outcomes; cleanup-hardened finalc0681dbeff76360b2ec8cd5803f01d2377514525, payload manifestc6089e85d3f00fc7dd5aed11661660a547cd4a0d95daa8120bef79859695e98b.

Raw RESULTS.json:467630bytes, SHA256380bbabacce04e232f246230f4a7656074d072dc92b0453e03b6f718078100b0. Controller2441bytes, SHAc2233171df7ae4473f5372bdea0be8a8c3a83b1a05a64c71d97813e5d4ab330d. Recovered original run01a19f5d-8620-7711-a8be-67909f020833. I independently parsed all82records, rederived expected fields/types/exit/canonical bytes from frozen manifest, inspected stderr and argv/mounts, and rejected duplicates/missing records. Did not trust passed=true alone. Own result: RECOVERED-AUDIT.json, zero faults.

-43/43 original semantic cases match exact oracle. Cases cover exact name vs normalized-only collisions, exact alongside colliding alternate names, permutation, case, scalar Unicode/escaping, missing/invalid/duplicate input, and exact byte/list/scalar boundaries and one over.
-5/5 invocation refusals return64 with no JSON verdict and the bounded invocation diagnostic: missing argument, extra argument, missing file, directory, symlink.
-9/9 real source mutants produce the intended status error with valid JSON/legitimate classifier exit, not a crash; all9 benign controls remain correct. Mutants cover basename/suffix exactness, first-only selection, case folding, early success masking bad tail, duplicate key/ID permission, invalid-as-mismatch, constant refusal.
-16/16 scope mutants each alter exactly one epistemic field at one of four statuses; exit unchanged and all other fields unchanged. Evaluator catches the intended field and canonical-byte difference. Thus assertion detection is not limited to happy-path output.

## Isolation, resources, cleanup and provenance

Actual interpreter Python3.14.8, not asserted historical equivalence. Per-call raw stderr KAMA_LIMITS records CPU2s, AS268435456bytes, core0/file-size0/open-files32 and private PID/network namespace identifiers. Pinned controller compared those identifiers with its host namespaces and would set stop on equality; host baseline IDs are not separately present in the receipt, so do not claim independent post-hoc inode-pair comparison. All82 stop fields null and cleanup_errors empty. Exact readonly runtime mount pairs match frozen profile; only reviewed script, selected fixture and inside-wrapper application files are mounted. No writable hostroot/home/config, no candidate services/provider calls.

Max observed per-call wall0.081582869seconds, max combined output2137bytes, both below5s/1MiB. Batch4.354seconds; actual verified systemd cgroup512MiB/swap0/tasks64, batch600s limit. Controller finished exit0. Kill/stop returned unit-not-loaded after natural collection; exact subsequent inspection exit0 showed LoadState=not-found, ActiveState=inactive, empty ControlGroup. These nonzero cleanup action returns are not execution failure; the inspected absence establishes cleanup.

Staging receipt says107 runtime objects and664 stdlib files matched prior pins, drift empty. Final report must cite the existing fingerprint manifest used, not invent hashes from version text. Interpreter/runtime byte parity with past training is not claimed.

## Domain and source judgment

One bounded calibration capability: a strict synthetic JSON projection distinguishes exact parsed advertised-name membership, legacy lossy equivalence, no match and insufficient evidence without pretending to observe readiness, weights, ownership or a live endpoint. Already-held alias knowledge is not newly discovered; existing normalizer contract is unchanged. New value is independently demonstrated discrimination and difficult-case execution.

Outside source taste check: agree with admitting S542 (pinned vLLM serving-name contract) and S543 (pinned llama.cpp direct-server model-list/loading caveat) for these narrow distinctions. Independently reopened both immutable sources, not merely their source rows. Agree with rejecting exact-name=>loaded-weights/current-readiness inference. Strict input grammar/resource thresholds are assessor design decisions, not upstream API mandates. No full third-party pages/PDFs copied into artifacts.

Provisional trends for claim: expansion improved (new executable repertoire), quality improved (stronger evidence discrimination under finite bounds), discernment improved (independent admit/reject agreement and adversarial mutants). Assigned calibration7 numeric score need not rise; finite coverage is not universal competence. Operability/other axes should be unchanged absent demonstrated harm; final documentation/no-harm check still pending.

## Honest review error retained

My first independent recovery-audit script guessed31 readonly mounts and flagged every record despite correct behavior. That was reviewer-only verification error, not candidate failure: fixed by comparing exact mount pairs against the already-frozen profile plus three explicit owned mounts. Original audit and script retained as RECOVERED-AUDIT-v1-reviewer-count-error.json and audit_recovered_v1.py. No oracle, candidate, evaluator, payload or execution result was changed and no rerun occurred.

## Closure obligations

Final source/knowledge/registry/report integration must cite measured bytes and narrow synthetic scope; register the tool without inventing --selftest or portable host-bound batch semantics. Preserve historical red selfdesc10 baseline findings, all receipts and original histories; disclose them, never claim all legacy gates green. Recheck protected probe/registry/history, source append-only, final landing and actual report pointer. No future round or capability count is advanced by this draft.

## Runtime fingerprint addendum,03:26UTC

Parent supplied already accepted audit/kengaku67-local-preflight/runtime-inventory.json,29410bytes, SHA256a59fe35541c7cd747087a9d6adc9c4163c2ea7736bbb9b9fbefda44465a194de. Independently rehashed it and checked every regular-file source mounted by Kama against its107object inventory: none missing. `/usr/bin/python3.14` digest375532f83be620283ab780c14ca6bcc5907dc379d2b621de0c5d0a112cf5458b;664stdlib Python tree digest3d8d99a0f12a8bcb98b139efe078589eb3621eeb98e9547405c6d3028142d240. Venv pure-Python files are outside inventory's exhaustive claim and not mounted/used by Kama. Staging receipt reports zero drift over107/664; parent is recovering exact prior pin-file path confirmation, not asking for a rerun. The byte inventory is real, not an inferred version match.

## Final technical verdict,03:29UTC

The parent recovered read-only confirmation that staging used `[local runtime inventory path omitted]`,29410bytes, SHA256a59fe35541c7cd747087a9d6adc9c4163c2ea7736bbb9b9fbefda44465a194de. This closes the pending runtime-pin-reference obligation above without remeasurement or rerun.

**C1 verified, synthetic offline calibration capability recommended for admission.** The unchanged first candidate meets the frozen43semantic/5invocation cases and all25targeted mutant kills with9benign controls. Scope is finite, synthetic, host-identified. Source admits/rejects independently agree. Numeric axis scores do not rise automatically. No native endpoint/loaded weight/ready service or universal identity capability is claimed.

This is the definitive technical verdict for author integration, superseding the draft's runtime-reference-pending qualification. Parent closure still needs final integrated lane/report byte/no-harm readback after author lands documentation, not another candidate execution. Prior baseline self-description10findings remain disclosed, not silently waived or counted as newly passing gates. This document itself is not a fleet ledger write or an additional training round.
