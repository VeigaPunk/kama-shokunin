# FrontierReadme — S174–S177 and self-assessment vs `corpus/README.md` ## Frontier

Seat: FrontierReadme (kama round 29 attempt 2, w2). No lane files edited. No tools installed. LSP device is not mounted (`xd://lsp` absent; mounted devices are `ast_edit` and `debug` only). This is a document question, so the evidence is the README text plus read-only git, not a symbol graph.

## Verdict

**Neither the worktree S174–S177 rows nor `corpus/knowledge/self-assessment-at-writing.md` advance any frontier row listed in `corpus/README.md`.**

**No frontier row should move to core** under that file’s own rule. The round-29 artifacts are a calibration-method note plus four Git-manual source rows. The README treats that shape as not a covered surface, not a serving capability, and not a promotion.

Confidence: high.

## Evidence identity

| Fact | Evidence |
|---|---|
| README working tree equals HEAD | `git diff -- corpus/README.md` is 0 bytes (`/home/vgpnk/Projects/shokunin/kama-shokunin`) |
| Last README commit | `9ce5bd377562117b3340709639d5d0eafe791bc1` `2026-10-23T06:17:31-03:00` subject `round-28: … README/PROVINCE round-28 sections` |
| README does not name round 29, S174, or the knowledge entry | `grep` of `corpus/README.md` for `S174`, `self-assessment`, `round 29`, `round-29`: no matches |
| S174–S177 are uncommitted insertions only | `git status --porcelain`: `M corpus/SOURCES.md`; `git diff --numstat`: `4 0 corpus/SOURCES.md`; four added registry lines after S173 |
| HEAD registry ends at S173 | `git show HEAD:corpus/SOURCES.md` last `\| S### \|` id is `S173`; `git grep S174 HEAD -- corpus/SOURCES.md corpus/README.md` prints nothing |
| Knowledge entry is untracked | `git status --porcelain`: `?? corpus/knowledge/self-assessment-at-writing.md` (also `?? corpus/lessons/round-29.md`) |

## Listed frontier rows (section `## Frontier`, lines 66–78)

The heading `## Frontier` is one four-bullet list. Later headings are dispositions (`## Frontier disposition — round 11` through `## Frontier disposition — round 28`), not replacements of those bullets. Append-only practice is stated at line 86: “Appended rather than inserted, so no existing line moves.”

| # | Row (README:68–78) | Own condition for movement | Do S174–S177 or the knowledge entry meet it? |
|---|---|---|---|
| F1 | Correct still-live source anchors through new cited correction entries; historical samples stay immutable; Round-4 debt is not erased by a current-state banner | A cited correction of a still-live anchor, not a banner and not a rewrite of historical samples | No. The four rows are new Git manuals (`git-blame`, `git-merge-base`, `git-grep`/`gitglossary`, `pretty-formats`). Their `teaches` cells describe blame porcelain, `--is-ancestor` exit status, tree blob search, and `%ct`/`%cI`. None says `supersedes`. The knowledge entry (33 lines) describes C1 classes P/H/N/C/T/Q on SCORECARD/SHONEN lines. It is not a probe-citation or source-anchor correction. |
| F2 | Reconcile declared-vs-served context size only as a separate feature move when an authorized serving runtime permits a real comparison | A real comparison on an authorized serving runtime | No. Neither artifact mentions context size, KV pool, `/completion` fit, or a serving sample. `verified-at` on the knowledge entry says “no fresh counter run performed.” |
| F3 | Non-author spot-check of at least one admitted and one rejected candidate; unavailable in round 5, so discernment and promotion remain unverified | That spot-check; until then promotion stays unverified | No. Both artifacts are lane wave/L1 drafts. They are not an outside admit/reject sample. |
| F4 | Operator/integrator prerequisites, not corpus expansion: native role bindings, a real receipt binding, serving-runtime disposition, historical verified-round reconciliation; no outside-repo repair is absorbed | Those operator acts, explicitly not corpus expansion | No. Adding source rows and a knowledge file is corpus expansion, which this bullet excludes. No role binding, receipt binding, or runtime disposition is in either artifact. |

## Later open rows (same file; not closed by these artifacts)

The latest disposition, `## Frontier disposition — round 28` (lines 423–434), leaves open: the same request fields through `/v1/chat/completions` and other endpoints; the json_schema → grammar transform; launch-dependent bounds under other argv (`n_parallel`); other builds and engines; K05 beyond the fixture; registered-consumer reconciliation.

Still named open earlier and not closed by rounds 25–28: router-mode model errors, held-back round-26 signatures, the unreproduced `--embeddings` `/completion` crash (lines 407–410); external-system-library identity, receipt-header minimization, historical crash-as-kill leaves, Git>=2.45 / R23-H2 (lines 382–389); D4 remains partial (line 343).

S174–S177 and the knowledge entry do not mention any of those subjects. Round 25 (lines 397–400) already says K05 “is advanced on the lane-owned fixture only” and the rest “stay open.” These artifacts do not change that.

## README’s own rule for moving a row to core

The section does not use the words “move to core.” The rule is the combination of the four bullets above and the dispositions in the same file:

1. **A named gap leaves frontier only when a disposition records it held.** Round 17 (lines 241–245): “live grading of a loading server by the receipt … is now held” and is then absent from that paragraph’s “Still open” list. Rounds 26 and 28 use the label **“New core surface”** only for a SKILL.md section that holds a measured llama-server surface, with a registry and a counter (lines 404–407, 425–429). The open remainder stays listed.
2. **Partial or fixture-only advance stays frontier.** Round 25 lines 397–400. Round 23/24: “D4 remains partial”; “No new frontier capability, no score promotion” (lines 343, 384–386).
3. **Calibration repair and new source rows are not a core move.** Round 12 (lines 138–145): “This is calibration repair, not an additional knowledge entry, covered surface, serving capability or endpoint sample. … no promotion box is newly certified.” Round 15 (lines 195–199): “No new knowledge entry, API surface or capability row is added. … frontier gaps remain open. No authorized serving runtime was sampled or restored.”

Applied here: the knowledge entry is a bounded extractor note for the frozen counter `.ufo/waves/round-29/count-c1.py` (it cites sha256 `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` and baseline `before/c1-base.json`). S174–S177 document the Git commands that counter uses. That matches rule 3, not rule 1. It does not satisfy F2’s “authorized serving runtime” gate or F3’s non-author spot-check, and F4 forbids counting it as corpus expansion. **No listed row should move to core.**

Rows the README already marked held (K02 crosswalk, loading-receipt grading, round-26 error signatures, round-28 request-field outcomes) are already recorded as held or “New core surface,” with their remainders left open. Nothing in that open remainder has a “now held” record that was left stranded on the frontier list. [INFERENCE] Those earlier core marks are not re-opened or extended by S174–S177.

## Defects (report only; not fixed)

1. **Frontier step named, not landed in the README.** Untracked `corpus/lessons/round-29.md` line 4 says the round includes “the frontier step.” `corpus/README.md` has no round-29 frontier heading; the last one is `## Frontier disposition — round 28`. The working tree did not append a disposition. SCORECARD’s uncommitted round-29 section (around line 1498) says “Capabilities: none claimed” and “calibration 7 → 7 (no promotion…)”, which agrees with “do not move to core,” but the lesson’s “frontier step” has no README record and these artifacts do not earn one.
2. **Do not index the worktree rows as core or as an advanced frontier row.** They are four uncommitted lines in `corpus/SOURCES.md`. HEAD still ends at S173. The knowledge file is untracked and is not in the README coverage map (lines 25–47 and the later coverage tables). `used-by` on the worktree rows points at `corpus/knowledge/self-assessment-at-writing.md` and `.ufo/waves/round-29/count-c1.py`; that citation does not place either path on a frontier row.

## What was not claimed

No counter was run. No fresh serving sample was taken. No statement here says the C1 receipt is true or false; that is other seats’ work.
