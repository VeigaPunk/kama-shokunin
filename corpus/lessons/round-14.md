# Round 14 — executable offline Ollama evidence reconciliation

Steered round 14, 2026-10-20 UTC. Starting commit: `e1b3d746dbfd2100b61c67b6389217252592460f`; clean initial tree. Prior non-author artifact `round-13-verifier-spotcheck.md` remains read-only.

## Declared claim

**C1 calibration capability — ollama-offline-evidence-replay.** Calibration 7 is the lowest assigned axis versus operability 8 (`../shokunin.conf` kama row); no stagnation waiver. Existing crosswalk prose distinguishes available inventory, loaded metadata and remote entries but lacks an executable offline replay classifier. Before: no such tool. After: a fixed adversarial fixture corpus produces literal expected finding IDs and exits through the actual CLI. Numeric calibration remains 7 → 7, delta 0; no universal mastery score is inferred from fixture coverage. This is a new runnable repertoire, not a claim that the conceptual tags/ps distinction is new.

Classifier inputs are caller-authorized exported JSON, never acquired by this feature. Equal selected name and nonempty digest in `/api/tags` and `/api/ps` supports only captured metadata correspondence. `readiness` remains `unknown` for every result. No network, live runtime, generation request, current residency, local-weight proof, cross-snapshot simultaneity or installation is claimed. Capture date/expiry do not establish present state. The strict selected-entry/schema and digest-join policy is **[INFERENCE]**, not a vendor guarantee.

## Gate

| Candidate | Decision | Grounding / limits |
|---|---|---|
| Runnable offline tags/ps classifier with independent literal fixtures and child CLI selftest | admit conditional on final measured cases | S012/S031 source fields; KQ1/KQ2/KQ4/KQ13 and new KQ17; fixture behavior is not runtime integration |
| Equal available model name alone proves loaded/ready/local weights | reject | S012 separates running metadata; S031 documents remote inventory fields; no readiness proof |
| Equal name/digest in two captures proves current readiness or simultaneous capture | reject | No acquisition/time authority exists; readiness stays unknown even for metadata match |
| GGUF basename normalization applied to Ollama names | reject | Exact-name API evidence does not authorize path or case normalization |
| Rewrite historical round-12 table or receipt to hide mismatch-count ambiguity | reject | Outside round-13 D2 requires appended clarification; old bytes remain intact |

### Opened sources

L1 opened https://docs.ollama.com/api/ps and https://docs.ollama.com/api/tags on 2026-10-20. Both served OpenAPI 3.1.0, info.version 0.1.0. Located S012 quote: GET `/api/ps`, responses `200`, description: “Models currently loaded into memory” (5 words). Located S031 quote: ModelSummary `remote_model.description`: “Name of the upstream model, if the model is remote” (10 words). GET `/api/tags` `200` description says “List available models”. These support fields and their documented distinction, not the lane's strict join or a real execution. Existing row opening dates/immutable cells remain historical; allowed used-by changes are listed in final source disposition below.

## Mistakes

| Class | Evidence pointer | Captured-by | Fix / failure obligation |
|---|---|---|---|
| verdict/count conflation | Outside `round-13-verifier-spotcheck.md` D2; round-12 lesson table row for redirected manifest | KQ16 distinguishes verified source-only mismatch count from outer admission; the old table's prose mixed them | Append explicit clarification below. Discovery credit belongs to CloseKamaR13; no C1 count or axis/trend credit is assigned to this clarification. Historical gate receipts already record the correct count and are not rerun. Outside review determines routed-debt closure |
| ambiguous design precedence | This round's initial `spec.json` allows remote inventory and differing-digest findings to overlap; advisory AttackAmbiguity/ReviewRemote identify the ambiguity before implementation | KQ13's claim/source separation; shared contract initially lacked a total order | `rulings.json` pins precedence; literal conflicting-field and remote/digest controls will show the implementation can reject unsupported conclusions. This is a current design mistake, not a claim the earlier prose crosswalk was wrong |

### Named historical clarification — round-13 outside D2

This supersedes only the presentation of `round-12.md:213` in the column “Source-only mismatch count”, not any recorded output. The redirected-manifest case records **source-only mismatch count 1 under a verified source anchor**, while the **outer finding is `manifest_invalid`, exit 2**. “Not admitted as a comparison” describes outer admission, not an absent/zero mismatch count. The historical lesson, acceptance receipt and fidelity implementation remain unchanged. KQ16 already states the correct distinction; this is supplementary historical clarification pending outside disposition, not a second axis claim. A missing executable replay tool was a capability gap, not an error in the already-correct conceptual crosswalk.

## Scope and orchestration

One validated 32-seat wave; six executor, two revenger, five scout, three connector, seven reviewer, four critic, two sentinel, two scribe, one simplifier. L1 holds the canonical planner seat; PlannerWalk is bounded revenger data-walk. Every dispatched payload is unchanged from validated `taskCall`; no model parameter. Reports are lane-relative under the absolute lane root. Seats advise; they are not independent non-author admission or promotion reviewers. New code/fixtures are lane-local, existing serving probe/registry/history untouched. No operator/sibling source, route, service, environment or credential action is taken.

Stale-lane: respawn-per-round; no other mission of kama is open. Inherited author work: none. Tools installed/updated: none to date. Registry record initially refused a filename passed where inline JSON was required; corrected invocation succeeded without routing mutation. Final observations are appended after integration; unrun checks are not passes.

## Integration correction — actual draft precedence defect

The L1 static integration read found two concrete defects in the new same-round
classifier draft, preserved byte-for-byte as
`.ufo/waves/round-14/frozen/precedence-before.py` (manifest beside it):
`classify` returned no-tags `unknown` before checking duplicate ps selection,
and checked valid remote markers before detecting missing selected digests.
Both violated the already-pinned L1 `rulings.json`. The Classifier owner was
directed to change only that decision ordering; Fixtures adds discriminating
controls, and ReplayKnowledge aligns its decision table. This is an actual
current implementation mistake, not an invented old runtime failure.

| Class | Evidence pointer | Captured-by | Fix / failure obligation |
|---|---|---|---|
| precedence implementation drift | Preserved actual draft `frozen/precedence-before.py:222–255`; authoritative `rulings.json` | L1 static contract/code correspondence; KQ17 preserves indeterminate vs classified results | Same final fixture corpus is run against this actual draft and corrected tool after all owners finish. The missing-digest/remote and no-tags/duplicate-ps controls must fail against the draft and match expected literal IDs/exits after the ordering fix; real observed receipts are appended below |

The immutable round-start absence baseline and this same-round red-before
defect snapshot answer different questions. The former measures new repertoire;
the latter demonstrates the current mistake's fix can fail. Selftest and
measurement use the same separately authored fixed oracle, not independent
external corroboration. Neither certifies arbitrary input or actual Ollama.

## Source curation and initial census

No new source row is needed: the operational distinction uses reopened
S012/S031, not a newly discovered vendor fact. Rows added by tier: A0/B0/C0.
Only `used-by` changes, recorded old → new:

- S012: `corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/served-identity-crosswalk.md`
  → the same two paths plus `corpus/knowledge/ollama-evidence-replay.md`.
- S031: `corpus/knowledge/served-identity-crosswalk.md`
  → the same path plus `corpus/knowledge/ollama-evidence-replay.md`.
- All status/recheck cells and all other rows remain unchanged, including
  historical opened dates. Source-owner detail: `advice/Sources.md`.

Bounded search: question whether tags/ps fields justify the offline replay
inference; two official URLs identified, screened and included for existing
rows, zero excluded, zero new rows; stop once exact identity/digest/remote
fields and available/running descriptions are located. No community or
acquisition search is needed.

Required start commands, both exit **0**, complete streams in
`.ufo/waves/round-14/sources-before-{validate,census}.json`:

```sh
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama
```

Start validate output (original TSV columns displayed with spaces):

```text
kama W04 S031 duplicate url docs.ollama.com/api/tags across scopes
kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
```

Start census: rows33, A30/B0/C3, mined23/queued5/rejected5,
invalid tier/status0, missing0. W04 is existing same-URL scoped curation,
not independent corroboration. Final outputs and exits are recorded below
after all implementation owners finish. Frontier advanced: executable
offline evidence replay repertoire only; no new API concept or live runtime.
