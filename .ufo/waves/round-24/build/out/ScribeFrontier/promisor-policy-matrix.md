# Round-24 promisor policy matrix (reading B) — README correction ↔ preregistration ↔ code

Leaf scribe (ScribeFrontier). Draft aid; no production edits. No gate run.

**Policy:** reading **B** (L1 decision, round 24). Availability is *per
required read*; no whole-root precondition. `oracle-amendment-1.json`
supersedes `preregistration.json` `expected_after[3]` only; the initial
registration stays immutable and is reported separately as **not met**.

## Preregistration / amendment items → README sentence → code anchor

| Registered item | Status | README correction sentence (variant A) | Code anchor in the auditor (base `0df800e`) | State |
|---|---|---|---|---|
| "Complete local promisor-marked lane and fleet clones with valid cited commits: exact same substantive clean/failed findings as otherwise identical full clones, not exit2." | stands | bullet 1 ("the same substantive finding as the otherwise identical full clone — clean, or the same defect set … and not exit 2") | refusals at `tools/report-landing-audit.py:457`, `:462-465` (both must stop firing) | policy stated; **unrun** — round-24 grid not executed |
| "A genuine omitted pre-cutoff lane commit remains landed-omitted exit1 with promisor metadata." | stands | bullet 2 (`landed-omitted`, exit 1) | `:448-465` refusal block, then the normal citation/omission path | policy stated; **unrun** |
| "An unavailable required commit/tree/blob/report object: exit2 could-not-evaluate, never a clean or failed verdict." | stands, narrowed to required reads | bullets 3-4 ("content that an audit read actually requires and that cannot be supplied locally is exit 2"; "unless it names content that is referenced but unavailable locally") | `EvalError` `:53-55`; `main()` maps it to exit 2 | policy stated; **unrun** |
| "A missing citation in any promisor-backed repository is unknown, not proved absent: exit2 unless resolved locally by another audited repository." | **withdrawn prospectively** by `oracle-amendment-1.json` (conflicts with base `tools/report-landing-audit.py:12-19`) | amendment paragraph: "One preregistered expectation is withdrawn prospectively … it is reported as not met, not as passed" | — | **not met** (by withdrawal, not by achievement); must be reported separately |
| "No lazy network fetching, transport invocation, signature verification, replace-ref substitution or config-caused hangs; preserve existing global Git isolation and deadlines." | stands | "Isolation is unchanged" paragraph | `:93-99` `GIT_ISOLATION`, `:108` `GIT_TIMEOUT = 20`, `git_env` `:101-106` | preserved by construction; **not re-measured in this lane** |
| "Metadata-only declarations do not establish incompleteness; content completeness and availability of required evidence determine the outcome." | stands (B wording) | lead paragraph ("it never changes local-object resolution, and it never changes a clean or failed verdict") + bullet 5 (locally sufficient repository is not refused for unrelated missing content) | the two metadata refusals | policy stated; **unrun** |
| "r23 filed evidence unchanged; append corrections: 69 falsify-wave lane reports, not 68; 40 of 56 killed FIFO-process identities retained, not full identity evidence." | stands, other lanes | — (not in this scoped file) | — | counts live in `corpus/lessons/round-23.md:178` and `:174`; `corpus/README.md` carries neither |
| "D4 remains partial" / "no new serving capability" | stands | closing two paragraphs | — | drafted; no endpoint sample or service restoration asserted |

## Retained-grid rows the B reading touches

| Row | File:line | Round-23 expectation | What round 24 must do to it under B |
|---|---|---|---|
| `F06-lazy-fetch-command` (graded fault) | `tests/report-audit/repo-state-grid.py:651`; reason pin `:697` ("partial clone") | exit 2, reason "partial clone" | exit 1 with the **same findings as its unmarked twin**; the reason pin `:697` is **dropped** (the metadata refusal no longer exists) |
| `F23-promisor-pack-without-config` (graded contract) | `:670`; reason pin `:704` ("promisor pack") | exit 2, reason "promisor pack" | **stays exit 2**, but the reason pin must become **content-derived** (the cited blob is unreadable locally), not a metadata string |
| `T01-blobless-partial-clone` (tradeoff) | `:689` | frozen exit 0 / current exit 2, `met false` = the declared trade | audits **clean under B** (the clone is locally sufficient for the audit's required reads) → the declared trade is **withdrawn**; the README's round-23 "Declared trade" sentence is what this correction withdraws |
| `F27-filter-only-promisor-remote` (graded fault) | `:674-675` | exit 1, `landed-unresolved` + `unresolved-full-hash` | **keeps exit 1** (no metadata refusal ever applied; a locally unresolved citation keeps the ordinary failed verdict) |
| `C09-promisor-false-config`, `C10-orphan-promisor-marker` (controls) | `:679-680` | exit 0 in both arms | keep; they already encode "metadata that does not describe a promisor remote is not evidence" |
| `O01-alternates-foreign-object`, `O02-gitfile-redirect` (open) | `:690-691` | reported, not graded | stay open; the B reading does not close them |

## Reading discipline used in the draft

- "withdrawn as a policy reading" — the round-23 sentence stays in the file
  as filed; the appended section withdraws its interpretation.
- "proved absent" is withdrawn wording: exit 2 is could-not-evaluate with a
  content-derived reason; a locally unresolved citation otherwise keeps the
  ordinary failed verdict with the same finding kinds as the identical
  unmarked twin (authorized errata still applying).
- "per required read" replaces any whole-root phrasing: an unrelated
  historical blob, an unselected branch or an unused file that is missing
  is not a reason to refuse a locally sufficient repository.
- "complete local promisor-marked clone" is qualified by "with valid cited
  commits" so it cannot be read as a completeness certificate.
- The metadata-refusal withdrawal and the availability rule land together;
  the draft says so explicitly, because removing the refusal alone was
  measured to turn genuinely-incomplete repositories into false clean /
  false defect verdicts.

## Notes carried to the executor and grid lanes (not README text)

- Under `--no-lazy-fetch` with the promisor remote pointed at
  `file:///nonexistent`: `cat-file --batch-check` reports "<sha> missing"
  (rc 0, no fetch) and `rev-list --objects --missing=print` reports
  "?<sha>"; `rev-list --all --missing=print` *without* `--objects` does not
  list the missing blob, so a missing-object probe must use the `--objects`
  form — and must stay bounded to the audit's required reads, not become a
  whole-root precondition. (Measured by the round-24 SKILL scribe on the
  base auditor blob `cf706c52`; quoted here as peer-measured data, not as
  this lane's run.)
- Abbreviation uniqueness is judged over the audited **local** object set
  only; no remote abbreviation uniqueness and no remote repository
  completeness is claimed.
- The withdrawn registration must appear in the wave evidence as **not
  met** (withdrawn by amendment), separately from the outcomes that are
  measured and met.
