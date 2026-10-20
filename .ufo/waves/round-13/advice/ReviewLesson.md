# Round 13 — ReviewLesson advisory (KamaR13.ReviewLesson)

Scope: review the round-13 correction (KQ16 / KQ15 wording erratum) and the
round-13 lesson sourced binding, mistake vocabulary, counts and quality
attribution, against the round-12 verifier spot-check D1 and quality item.
Leaf review only. Advisory; the parent owns measurement, integration and acceptance.

## State observed (time-stamped; working tree is mid-flight)

- HEAD `941bb32c3f591bc63cbf7579b2b6c552228307cd`; round-13 start tree clean.
- Working tree while reviewing: modified `LOG.md`, `SCORECARD.md`,
  `corpus/QUALITY.md`, `corpus/README.md`, `corpus/SOURCES.md`; untracked
  `corpus/lessons/round-13.md` and `.ufo/waves/round-13/`. These are sibling
  edits. Findings below are against that snapshot and must be re-read when
  notified of further edits.

## Checks executed (no gate, selftest, reproduce, build, test or lint)

- Static reads: `corpus/QUALITY.md`, `SKILL.md:380-420` (registry row line 396),
  `.ufo/waves/round-12/fidelity.py` (`:44-72`, `:272`, `:319`, `:611-622`),
  `.ufo/waves/round-12/{acceptance,record}.json`, `reproduce.py`,
  `advice/{Fidelity,AttackSourceCuration,CountsConnection}.md`,
  `corpus/lessons/round-12.md`, `corpus/lessons/round-12-verifier-spotcheck.md`,
  `corpus/knowledge/served-identity-crosswalk.md:87-134`, `corpus/lessons/round-13.md`.
- Read-only git plumbing: `git show 79fa257|1df80ea:corpus/SOURCES.md`, `git diff --stat`,
  `git status --porcelain`, `git ls-files`.
- Row/tier/status counts: `awk -F'|' '/^\| S0/{...}'` over those revisions and the
  working tree (command counts only).
- `grep -c` for the literal audit phrases in the working-tree `corpus/QUALITY.md`
  (static string presence only, not semantic proof).
- Public docs fetched read-only with `curl` (git-scm.com `git-show`, `git-cat-file`,
  and the `/2.55.0` cat-file URL). Temp files removed from `/tmp`.
- Tools installed/updated: none.

Not executed: `fidelity.py` (any mode), `reproduce.py`, `sources-census.sh`, any
round-13 probe, any build/test/lint.

## Findings

### F1 — Capture-with-`git show` claim: admit only as author-recorded (Medium; currently worded correctly)

No committed code or receipt records a `git show` capture:
`acceptance.json` 0 `git show` hits; `record.json` 0 hits for either command;
`reproduce.py` and `fidelity.py` use `cat-file` only (`fidelity.py:272`, `:443`;
`reproduce.py:80`). The only `git show` capture evidence is author observation:
`advice/Fidelity.md:27,37-38,147` ("observed during generation"; "permitted one-shot
`git show` artifact generation") and the SKILL registry row (`SKILL.md:396`,
"captured byte-exactly via `git show`"). The round-12 lesson's Declared claim
(`round-12.md:13–15`) states the same.

An earlier draft of the round-13 lesson said "the actual round-12 code and receipt
identify which operation was used for each half." That is false for the capture half.
The current draft (`corpus/lessons/round-13.md` ~L40–44) says "capture with `git show` is
author-recorded provenance … not experimentally inferred", which is accurate.
KQ16 (current row) says "author-recorded method provenance", also accurate.

Recommendation: keep the author-recorded wording. Reject any text that presents the
`git show` capture as command-verified, receipt-recorded or reproducible from committed
code. The gate verifies bytes (`source_mismatch`/`clean`), not the capture command.

### F2 — KQ16 exit lead-in reads as precedence (Low–Medium; fix wording, keep the literal phrase)

KQ16 says "the exit is that of the selected primary finding under the documented finding
precedence: `source_mismatch=1; snapshot_tampered=2; source_unavailable=2`."

- The literal string is an exit map, not a precedence list. Its first entry
  (`source_mismatch`) reads as the top-ranked finding. The code ranks it lower:
  `PRIORITY` (`fidelity.py:64-72`) is `snapshot_unavailable, manifest_invalid,
  snapshot_tampered, source_unavailable, source_mismatch, unpinned, clean`.
  `snapshot_tampered` and `source_unavailable` outrank `source_mismatch`; `unpinned`
  ranks below it.
- `internal_error` is not in `PRIORITY`. It is emitted only from the exception handler
  (`fidelity.py:611-622`, exit 2). KQ16 lists it among exit-2 findings. That is
  accurate, but the "documented finding precedence" lead-in does not cover it.
- Exit mapping is confirmed: `fidelity.py:319` maps `clean`→0, `source_mismatch`→1,
  every other finding→2. This matches `SKILL.md:396` (exit-2 list:
  `snapshot_tampered, snapshot_unavailable, manifest_invalid, source_unavailable,
  unpinned, internal_error`).

Recommendation: keep the literal audit phrase `source_mismatch=1; snapshot_tampered=2;
source_unavailable=2` (required by the assignment). Change the lead-in from
"documented finding precedence" to "exit map", and state that primary-finding precedence
is the `PRIORITY` order and that `internal_error` is exception-path only.

### F3 — Mistake vocabulary: `number-drift` is minted, not mined (Low)

- `grep -rn "number-drift" --include=*.md` over the repo before round-13 returned zero hits.
  The `number-drift` row in `corpus/lessons/round-13.md` (Mistakes table) is therefore a
  new class with no corpus precedent.
- `reference-drift` has precedent: `corpus/lessons/round-11.md:83-86,165`, used for
  cited text that disagrees with its source. Both round-13 defects are of that type:
  KQ15 exit-class text versus `fidelity.py:319`/`SKILL.md:396`, and KQ15's `git show`
  fetch attribution versus `fidelity.py:272`.

Recommendation: either label `number-drift` as "new class, first use, round 13" in the
lesson, or use `reference-drift` for both rows. Do not present `number-drift` as mined
vocabulary. Either choice is admissible.

### F4 — Sourced binding: quotes verified (no defect)

- S032, git-show manual (2.56.0, 2026-09-28): DESCRIPTION "For plain blobs, it shows the
  plain contents." (8 words) present. DISCUSSION "The contents of the blob objects are
  uninterpreted sequences of bytes. There is no encoding translation at the core level."
  (20 words) present; the fetched HTML breaks the sentence across lines.
- S033, git-cat-file manual (2.56.0): OUTPUT "If `<type>` is specified, the raw (though
  uncompressed) contents of the `<object>` will be returned." (15 words) present. The
  same sentence is present at the `/2.55.0` URL. `textconv` and `--filters` appear in
  the page (13 and 12 hits, respectively).
- Both are method support only. Neither proves a comparison ran or endpoint truth. The
  lesson and S033 row say so.

### F5 — KQ15 defect confirmed (no defect in the routed diagnosis)

KQ15 (`corpus/QUALITY.md:49`) says "mismatch, snapshot tamper and unavailable source each
have distinct nonzero exits." Code and registry give mismatch→1 and both
could-not-evaluate cases→2 (F2 above). The distinct stable IDs are the real identity.
The routed D1 diagnosis is correct. KQ16's correction direction is correct.

### F6 — Counts (recounted; registry counts only, no serving knowledge)

Command: `awk -F'|' '/^\| S0/{n++; t[$5]++; s[$9]++}' corpus/SOURCES.md` (and the same
over `git show <rev>:corpus/SOURCES.md`):

| Revision | Rows | Tier A | Tier C | mined | queued | rejected |
|---|---:|---:|---:|---:|---:|---:|
| 79fa257 (round-11 end) | 31 | 28 | 3 | 21 | 5 | 5 |
| 1df80ea (round-12 delivered) | 32 | 29 | 3 | 22 | 5 | 5 |
| working tree (mid-flight, round-13) | 33 | 30 | 3 | 23 | 5 | 5 |

Round-12 closure figures (31→32, A 28→29, mined 21→22) are confirmed. The round-13
working tree adds S033 only. The round-13 lesson currently has no census section; when
it is written it must record 32→33, A 29→30, mined 22→23 from a fresh read. These are
registry counts. No `corpus/knowledge/` file changed in the working tree
(`git diff --stat`: 5 files, none under `corpus/knowledge/`), so no new knowledge entry,
coverage or capability is established by these counts.

### F7 — Quality attribution (credit D4; admit)

`corpus/knowledge/served-identity-crosswalk.md:87-134` exists and contains the round-12
D4 correction (locality conclusion labelled [INFERENCE]; `supersedes S011` scoped as
lane-registry supersession, not upstream change). This is the knowledge-entry
interpretation the round-12 closure cites. The round-13 lesson's rejection of
"gate machinery alone establishes improved quality" is consistent with that. Quality
stays unchanged this round. No finding.

## Admit / reject recommendations

| Candidate | Recommendation | Basis |
|---|---|---|
| Append KQ16 superseding only KQ15's exit-class and fetch-method formulations | ADMIT (conditional on the parent's red/green textual measurement, which I did not run) | F2, F5; other KQ15 clauses preserved |
| Capture "via `git show`" as command-verified or reproducible from committed code | REJECT; keep as author-recorded | F1 |
| Change `fidelity.py` to produce three distinct numeric exits | REJECT | `fidelity.py:319`; registry already distinguishes via IDs |
| `number-drift` as mined vocabulary | REJECT as mined; ADMIT only if labelled new, else relabel `reference-drift` | F3 |
| S032 / S033 quotes as method support | ADMIT | F4 (verified) |
| Round-13 counts 32→33, A 29→30, mined 22→23 | ADMIT once the census section is written from a fresh read | F6 |
| Quality credit to D4 crosswalk; no gate-machinery credit | ADMIT | F7 |

## Residual risk and verification gaps

- The working tree is mid-flight. `corpus/QUALITY.md` KQ16, `corpus/lessons/round-13.md`
  and `corpus/SOURCES.md` may change. Re-read before integration.
- No gate, selftest, reproduction or probe was run. The literal-phrase presence checks
  are string greps only. They are not semantic proof and not a substitute for the
  parent's measurement.
- `round-12` capture of the frozen snapshot via `git show` rests on author observation
  (`advice/Fidelity.md`). It is not committed-reproducible. Stated as a limit (F1).
- Probe and criterion-writer outputs were not reviewed here.
