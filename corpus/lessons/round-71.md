# Round 71 — dispatched stream completion evidence

date: 2026-11-03
status: awaiting first technical batch and independent adjudication

## Claim and provenance

C1 proposes bounded serving-side calibration: classify owned synthetic chat-stream projections as COMPLETE, INCOMPLETE, STREAM_ERROR or INVALID_OR_INSUFFICIENT using dispatched event boundaries and final/error state, without live claims. Assigned calibration 7 and operability 8 are held; no scalar lift is proposed. This is distinct from round70 advertised identity and from the historical round31 SSE-presence objective.

Fresh direct `git ls-remote origin HEAD refs/heads/master refs/heads/cloud-kama-training-20261103` before numbered work returned HEAD/master 6035e952c2521999e192d6f236331f265ac98392 and no named cloud branch. Local baseline ac6791c20e9a2414264946e0996d9de45e812740 was clean. All history uses the reviewed local-only jj adapter; no remote publication or main/master write.

Independent contract/oracle freeze b2f1f17ffa88dce5d68ee21eaed89e932089bdef precedes candidate 1ccd5d0db476344fefcd58e4ab342f66d8f1f9d4. Candidate SHA256 be3dec7e88cc49bec38da717580f1f802e2e86bdd29d06bb7951776a34f60201. Freeze has 83 explicit semantic cases, 5 invocation arms, 10 semantic-mutant pairs, 16 scope mutants and 8 historical-presence comparisons. Until executed and independently re-adjudicated these are planned tests, not results.

## Learn and distinguish

S544 supplies dispatched event boundaries, not completion semantics. S545 and S546 supply pinned emitter distinctions between final choice metadata, optional usage, exhausted-stream marker and error termination. Strict size/Unicode/JSON/projection policy is lane-defined. Source readings retain only hashes, metadata, short quotes and own notes, never full third-party captures.

Round31's source detector at count-c1.py:547–560 uses parseable JSON plus a marker-shaped data line to measure SSE presence. That detector was not intended to establish full stream completion. Reusing it as the answer to the new question loses boundary/error/final-state information. Round71 tests this new capability rather than relabeling prior results.

## Mistakes retained

1. Author source check expected an error-return quote at 5117; the fresh pinned source located 5118. Original script and false located-anchor receipt are preserved; corrected script reopens sources and succeeds. This does not earn capability credit.
2. Before freeze, reviewer corrected a double-BOM oracle during manual review, disclosed in the freeze LOG. A second BOM belongs to the first field name and is not globally forbidden by the framing grammar. No candidate yet existed; this is a prospective oracle correction, not an outcome repair.

## No-harm baseline

Registry 79 clean. Self-description baseline returns exit 1 with 9 residual findings, retained unmodified in author/selfdesc-baseline.json. Six protected legacy files are hash-pinned, including original probe, consumer registry/history, Ollama evidence and round70 identity tool. No runtime observation or historical-host test rerun is represented by these metadata checks.

## Gate

Pending actual first outputs, independent negative-control judgment, source taste judgment, final metadata gates and closure. Parent owns fleet ledger/publication. No completion/admission claimed in this draft.

## Independent source-taste review and pointer correction

Before execution, independent reviewer agreed the narrow source/policy distinctions and held numeric scores. Reviewer found the SKILL instrument row cited `tests/round71-independent/MANIFEST.json`, omitting the actual `freeze/` directory. Corrected prospectively to `tests/round71-independent/freeze/MANIFEST.json`; original wrong row remains in commit 15e09c9b. The old registry gate is limited to round-named counters and did not detect this new classifier-row pointer; its clean result is not validation of every instrument citation. Candidate and frozen oracle unchanged.

## Actual first batch and bounded technical admission

The independent reviewer re-adjudicated all 132 original invocation records against the preimplementation oracle, not the runner's pass flag: 83 semantic cases (20 COMPLETE, 14 INCOMPLETE, 3 STREAM_ERROR, 46 INVALID_OR_INSUFFICIENT), five invocation refusals, ten source-mutant semantic kills with ten benign controls, sixteen exact scope-field mutations and eight historical-presence comparisons. Candidate bytes and first outputs are unchanged; no rerun. Exact technical/source/isolation judgment: `.ufo/waves/round-71/result/TECHNICAL-VERDICT.md`; original evidence and readback share that directory.

The historical proxy misses valid CR/no-space/multiline examples and accepts missing-finish, undispatched terminal, post-terminal malformed and error-terminal examples on the new completion question. This is not a retrospective failure of its presence objective. The new capability is bounded offline evidence discrimination. Expansion, quality and discernment improve on that demonstrated task; scalar calibration 7 and operability 8 remain held. No runtime readiness/identity/quality inference or promotion.

Actual Python 3.14.8 ran in the previously reviewed minimal read-only bwrap envelope with private PID/network, per-call CPU 2s/address 256MiB/wall 5s/output 1MiB, within systemd memory 512MiB/swap 0/tasks 64/runtime 600s. Reused runtime inventory matched with no drift. Unit cleanup inspected absent/inactive and empty ControlGroup, not a separate process-membership census. Final metadata readback and terminal closure follow; prior pending paragraphs are historical steps, not current missing execution.

## First final-metadata gate correction

At e983ff33, final registry/source/landing/census checks passed and all protected six files plus candidate remained unchanged. Self-description reported eight findings versus baseline nine, but this total hid one new author error: a broad calibration-row replacement removed the existing verifier-spotcheck run fact. Restored the full original run fact while updating only the exact dated pointer; original faulty row and red receipt are retained. The current closed pointer remains round 69 until the reviewer actually closes round 71, even though the legacy checker counts its pending file as newest. No underlying gate or predicate was weakened.

## Terminal closure

Independent reviewer terminally ADMITTED the bounded capability at 2f11ca1049a09bcc3171d0ed707c79c113a8e814 after binding actual first outputs, repaired metadata, protected files and seven disclosed residual findings. The dated calibration pointer is now advanced from the prior closed69 to the actual closed71; superseded row retained. Six inherited run/province findings remain. No technical rerun, candidate/oracle edit, numeric lift or stronger runtime claim.
