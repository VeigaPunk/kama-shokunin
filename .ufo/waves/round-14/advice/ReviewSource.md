# ReviewSource — round 14 review of SOURCES.md immutable cells vs used-by edits

Reviewer: KamaR14.ReviewSource (leaf, read-only except this report).
Snapshot: `corpus/SOURCES.md` working tree vs HEAD `e1b3d74`, observed 2026-10-20T06:28Z.
If the Sources or ReplayKnowledge seat lands again, this review is stale and must be re-read.

## Verdict

The registry edit is contract-compliant on immutable cells: no cell in columns 1–10 of any
row changed, and only the two `used-by` cells the spec allows changed. One ordering defect
(F1) must be resolved before any validation runs: both new `used-by` targets are missing on
disk. Remaining items are source-versus-policy wording (F2, F3, F4) and record-keeping (F5,
F6). No blocking content defect in the registry itself.

## Findings (by severity)

**F1 — High (validation ordering): `used-by` names a file that does not exist.**
- S012 and S031 `used-by` now end with `corpus/knowledge/ollama-evidence-replay.md`.
- `test -e corpus/knowledge/ollama-evidence-replay.md` → missing (checked 06:28Z).
- Round-11 ReviewContract S2 (`.ufo/waves/round-11/advice/ReviewContract.md:31`) records that
  the census check E11 fails when a `mined` row's `used-by` path is not on disk. I did not
  re-run the census or validate (out of scope; script not read — it lives outside this lane).
- Owner: `KamaR14.ReplayKnowledge` must land the file at exactly that path. No further
  `SOURCES.md` change is needed if the path matches. No validate/census run until it exists.

**F2 — Medium: replay policy must not borrow source authority through `used-by`.**
- The fetched pages document these fields only:
  - `/api/tags` `ModelSummary`: `name`, `model`, `remote_model`, `remote_host`, `digest`
    ("SHA256 digest identifier of the model contents"), `details`.
  - `/api/ps` `Ps`: `name`, `model`, `size`, `digest` ("SHA256 digest of the model"),
    `details`, `expires_at` ("Time when the model will be unloaded"), `size_vram`,
    `context_length`. **No remote field appears on the ps schema.**
- Consequence: any "remote marker on ps → remote_inventory" rule (spec `Classifier` interface)
  and any digest-join between tags and ps are kama policy. They are not supported by S012.
  The `used-by` link means only "this entry uses the row", not "the row endorses the rule".
- Owner: `KamaR14.ReplayKnowledge` labels each such statement `[INFERENCE]` and names the
  page field it builds on. S012 must not be cited for remote or join policy.
- Decision for L1 (not decided here): whether ps-side remote markers stay as a classifier
  rule. Evidence says the page does not define them.

**F3 — Low (already mitigated; no edit): S031 cell states inference as flat fact.**
- S031 scope and teaches say "available-model membership is not proof of local residency" and
  "list membership does not prove local residency". The opened page's own ModelSummary
  description says "Summary information for a locally available model".
- The inference is already labelled in the appended D4 paragraph (`SOURCES.md` correction
  block, "D4 — inference and supersession"). Immutable cell untouched — correct under rule 2.
- Action: none. Do not rewrite the cell; any further correction must be appended at EOF.

**F4 — Low (immutable prior-round cell; no edit): S012 teaches paraphrase.**
- S012 teaches "Separates running models from the available-model list". The ps page says
  "Retrieve a list of models that are currently running" and "Models currently loaded into
  memory". "Separates from the available-model list" is kama's framing, not page wording.
- Action: none to the cell. Replay text must not present the separation as a page quote.

**F5 — Info (conforming): round-14 search note and quotes.**
- Search log bullet "round-14 offline replay re-open" gives opened dates 2026-10-20 and three
  quotes. I checked each against the pages read in this review:
  - "SHA256 digest identifier of the model contents" (tags `ModelSummary.digest`) — matches.
  - "Retrieve a list of models that are currently running" (ps summary) — matches.
  - "SHA256 digest of the model" (ps `Ps.digest`) — matches.
- Each quote is ≤25 words. The note labels join, verdict precedence and remote-conflict rules
  `[INFERENCE]`/own-work. Conforming.

**F6 — Info (precedent, no anchor breakage found): two mid-file inserts.**
- Insertions at `SOURCES.md` search-log (new bullet after line 61, hunk `@@ -61,0 +62 @@`) and
  after the Round-13 correction (hunk `@@ -74,0 +76,2 @@`). Leads and later prose move by +1/+2.
- Grep of `corpus/` for `SOURCES.md:N` found only `lessons/round-11-verifier-spotcheck.md:213`,
  which cites lines 6–7. Nothing references N ≥ 62. No anchor breakage found.
- This matches the round-13 F6 precedent. Noted because KQ7 names mid-file insertion as a risk.

## Verified (evidence)

- `git diff --numstat HEAD -- corpus/SOURCES.md` → 5 insertions, 2 deletions.
- Hunks: `-24`/`+24` (S012 row), `-43`/`+43` (S031 row), `+62` (search bullet), `+76,2` (round-14 note).
- Per-cell comparison, HEAD vs working tree, keyed on column 2 ID, 33 rows each:
  - Columns 1–10 (id through `opened`, `recheck`, `status`, `teaches`, `anchor`, `scope`): zero
    changes for all 33 rows.
  - Column 11 (`used-by`): changed for S012 and S031 only.
  - `status` and `recheck`: zero changes.
- Old → new `used-by`:
  - S012: `runtime-health-surface-matrix.md, served-identity-crosswalk.md` → same + `ollama-evidence-replay.md`.
  - S031: `served-identity-crosswalk.md` → same + `ollama-evidence-replay.md`.
- S034 not added; row count stays 33.
- Opened pages read in this review (read-only): `https://docs.ollama.com/api/tags`
  (OpenAPI 3.1.0, info.version 0.1.0) and `https://docs.ollama.com/api/ps` (same version).
- Contract text: `.ufo/waves/kaika/SOURCES-CONTRACT-v1.md` is cited by round-11/12/13 advice
  but is **not present on disk** (`find` by name returns nothing; no `kaika` path in git
  history). Rule 2 (only status/recheck/used-by change in place) is taken from the round-11
  advice (`ReviewContract.md:47`) and the round-13 ReviewRegistry, not from the frozen file.

## Limits

- Census, validate, tests and builds not run (assignment: do not run verification).
- The census script was not read; E11 behaviour is cited from round-11 advice only.
- The contract file is absent; its wording is unverified here.
- Replay file pending; F1 and F2 are re-checkable only after it lands.
- Snapshot-bound: Sources and ReplayKnowledge seats may still edit.

## Tooling directive record

No packages, tools or dependencies installed or upgraded in this review. Read-only: `read`,
`grep`, `bash` (`git`, `test`, `python3` stdlib string comparison, `date -u`).

## Owner recommendations (sent as bounded peer messages)

- `KamaR14.ReplayKnowledge`: land `corpus/knowledge/ollama-evidence-replay.md` (F1); tag
  ps-remote and digest-join statements `[INFERENCE]`; do not cite S012 for them (F2).
- `KamaR14.Sources`: current registry state is conforming; no further cell edits; do not add
  S034; any correction appended at EOF only (F3, F5, F6).

## Closure update (2026-10-20T06:29Z)

- F1 closed: `corpus/knowledge/ollama-evidence-replay.md` exists (16,273 bytes), and its `source:` line cites S012 and S031 only (no S011). The registry diff is unchanged (5 insertions, 2 deletions). The census was not re-run; E11 resolution is for L1 validate.
- F2 and F4 remain open for the replay owner's wording review; F3, F5 and F6 unchanged.
