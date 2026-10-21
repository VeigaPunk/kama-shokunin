# ConnPriorSources — S089–S101 cross-check; r24 claim → sourced-row mapping

**Verdict: the r24 repair's sourcing is sound and no source registration is missing. Two support defects are in the ledger, not in the reasoning: (1) the auditor's live decode dependency is recorded on the rejected row S095 instead of the admitted S096; (2) the applied knowledge entry's isolation sentence rests on S089/S100 while its own `source:` line names neither. One bounded, append-only-legal move is proposed: a `used-by` reconciliation for the reused rows (mutable cells only). One peer note must not be acted on: S103's anchor is correct, and the wave's candidate id map (S103/S104/S105) collides with the admitted ids.**

No production file edited. No registry row added. No commit/push. No install. Base `0df800e8` → integration `ed1cc3a`; scratch clone `/fast/scratch/hyaku/kama-r24/ConnPriorSources/clone`.

---

## 1. Provenance of the reused band S089–S101 — every row traces to a source task

| row | opened by | verification record | r24 reuse |
|---|---|---|---|
| S089 | r23 seat `SrcGitEnv` (provisional S089) | `SrcS089.md:6` ADMIT | lesson `:39`; auditor `:138` |
| S090 | r23 seat `SrcGitReplace` (provisional S089) | `SrcS090.md:11` ADMIT | `--no-replace-objects` `auditor:138` |
| S091 | r23 seat `SrcGitConfig` / `SrcGitEnv` (provisional S089/S091) | `SrcS091.md:9` Admit | superseded by S100 |
| S092 | r23 seat `SrcPartialClone` (provisional S089) | `SrcS092.md:8` ADMIT (one Gate over-attribution) | superseded by S099 |
| S093 | r23 seat `SrcGitLogFollow` (provisional S089) | `SrcS093.md:6` ADMIT | `auditor:133-137` |
| S094 | r23 seat `SrcGitRepoLayout` (provisional S089) | `SrcS094.md:7` ADMIT | lesson `:40`; `CaseAlternatesComplete` |
| S095 | r23 seat `SrcPythonDecode` (provisional S090) | `SrcS095.md:7` **REJECT** | superseded by S096; cited *as rejected* `lesson:58` |
| S096–S100 | r23 **replacement L1**, `corpus/lessons/round-23.md:148-159` — no per-seat advice file | **no second reader in the tree** | S096/S097/S098 → knowledge `:79`; S099/S100 live |
| S101 | r23 replacement L1, `round-23.md:162` | **outside** re-open: `CritNoTrade/closure-r428.txt:41` re-read `commit.c:249-260` | lesson `:57`; `grafts_effective` `auditor:610,699` |

Facts behind the table:
- All seven r23 build seats drafted **provisional id S089** (plus S090/S091) for different pages; the L1's admission allocated the final ids. The id-allocation hazard is already resolved.
- S089–S095 each have a falsify-wave re-open report (7 files, `.ufo/waves/round-23/falsify/advice/SrcS089.md`…`SrcS095.md`). S096–S100 have **none** — pre-existing r23 asymmetry, disclosed in the r24 lesson as "Reopened sources" (`:39-40`).
- No S001–S101 cell changed across the round: `git diff 0df800e8 HEAD -- corpus/SOURCES.md` touches only the three new rows. `python3 tools/sources-append-only.py --from 245a37f6 --to ed1cc3a` → "no append-only violations"; `bash scripts/sources-census.sh validate .` → exit 0, 0 E-codes.

## 2. r24 claim → row → real consumer (every claim sourced; nothing invented)

| r24 claim | row | verified anchor | consumer |
|---|---|---|---|
| metadata alone never changes a verdict | **S103** | partial-clone §Handling Missing Objects bullet 1: "These promisor packfiles consist of a \"<name>.promisor\" file with arbitrary contents" — `Documentation/technical/partial-clone.adoc:116-118` (sha256 `9512d7ee…`) | `promisor-grid.py:268-270` |
| missing required object detected locally, never fetched | **S102** | git-rev-list `--missing=<missing-action>`: "will also print a list of the missing objects. Object IDs are prefixed with a \"?\" character" — `rev-list-options.adoc:1060-1061` (sha256 `8414be81…`) | `auditor:673`; `promisor-grid.py:295` |
| a green fsck is not availability proof | **S104** (rejected) | `builtin/fsck.c` v2.56.0 `mark_object` :143-149 (sha256 `d25f3b1a…`, byte-identical to `out/SrcFsck/fsck-builtin.c`): `if (is_promisor_object(...)) return 0;` — the early return precedes the `HAS_OBJ` check at `:151` | `corpus/knowledge/error-is-not-a-verdict.md:117` |
| unknown citation is unknown, not absent | **S083** + **S099** | cat-file §BATCH OUTPUT "<object> SP missing LF" / "cannot be resolved to an object in the repository"; partial-clone "no check as to whether the missing object is actually a promisor object is performed" | `auditor:212,242`; `promisor-grid.py:312` |
| isolation boundary unchanged | **S089** + **S100** | `--no-lazy-fetch` / `--no-replace-objects`; `log.showSignature`, `gpg.program`, `core.sshCommand` | `auditor:133-138`; `promisor-grid.py:111` |
| comment-only grafts file rewrites nothing | **S101** | `commit.c` v2.56.0 `read_graft_line`: `if (!line->len \|\| line->buf[0] == '#') return NULL;` | `auditor:610,699` |

**No invented source registration:** every S-id cited in any committed file (`SKILL.md`, `LOG.md`, `corpus/lessons/*.md`, `corpus/knowledge/*.md`, `corpus/QUALITY.md`, `corpus/README.md`) exists in the registry — scan reports "committed corpus ids absent from registry: NONE". `S105` occurs only in uncommitted wave artifacts (`advice/ScribeLesson.md:22,108,160`, `advice/SrcPartial.md:185,197`, `out/ScribeLesson/round-24-lesson-draft.md:124`, `out/SrcPartial/proposed-row.md:18,21`) and in no corpus file.

## 3. Support / overlap defects

**D1 (ledger, actionable) — the auditor's live decode dependency sits on the rejected row, not the admitted one.**
`S095` (status **rejected**) lists `tools/report-landing-audit.py` in `used-by`; `S096` (mined, "supersedes S095") does not, although S096's own `teaches` says "the auditor's bytes-mode `git()` decode relies on it". The current auditor never uses text mode — `grep -c text=True tools/report-landing-audit.py` → **0** at r24 HEAD and at base `0df800e8`; only the frozen arm `4fe9339f` had `capture_output=True, text=True` (`:90`). The ledger therefore points the tool at the row whose claim was rejected and omits the row that states its mechanism.

**D2 (row shape, needs a new row not an edit) — a rejected row keeps a positive-claim `teaches` cell.**
`CORPUS.md` §SOURCES.md Shape requires "Rejected rows read `REJECTED: <reason>; flip: <what would change the verdict>`" (S063, S077, S104 comply). **S095 does not**: its `teaches` still reads "The default `strict` handler raises UnicodeError, so text-mode subprocess output with invalid bytes raises unless the caller maps the error." — the positive claim the falsify seat rejected (`SrcS095.md:7`). Status and teaching contradict each other. `teaches` is immutable (KQ22), so the route is a superseding row, as S096 was.

**D3 (citation completeness, actionable) — the applied knowledge entry's isolation sentence cites nothing.**
`corpus/knowledge/error-is-not-a-verdict.md:91-92` asserts the `--no-lazy-fetch` / no-replace-objects / signature-log-suppression boundary; the governing rows are **S089** and **S100**. The section's `source:` line (`:117`) lists only `S102, S103, S104 (rejected candidate); corpus/lessons/round-24.md`. The unscoped draft `out/ScribeKnowledge/error-is-not-a-verdict.round24-append.md:215` *did* list `S083, S089, S099, S102, S103, S104 (rejected)` — the applied file dropped the three reused ids. Claim true, rows exist; only the citation is missing. Same class as the r23 precedent at `error-is-not-a-verdict.md:79`.

**D4 (judgment, flagged not asserted) — reused rows reopened by r24 are not in the ledger.** The r24 lesson names S089, S083, S099, S094 (`:39-40`) and S101/S095 (`:57-58`), but no reused row's `used-by` gained `corpus/lessons/round-24.md`, while the three new rows S102–S104 did. r24's list reads as a re-verification record rather than a quoting Gate, so leaving reused rows alone is defensible; the r23 house rule (a quoting Gate puts the lesson path in `used-by`) is the counter-precedent, and S083/S089 are the two rows whose `teaches` are quoted rather than merely named. L1's call.

**D5 (do-not-act) — S103's anchor is right; a peer's contrary note would break it.** `advice/SrcRepoLayout.md:77` puts the `.promisor` sidecar definition in partial-clone "§Design Details". Upstream puts "these incomplete packfiles are marked as \"promisor packfiles\"" in §Design Details (`:99-100`) but the sentence S103 quotes — "These promisor packfiles consist of a \"<name>.promisor\" file with arbitrary contents" — in **§Handling Missing Objects, first bullet** (`:111-118`). The admitted S103 anchor and the r24 lesson quote (`:21-24`) are correct; SrcRepoLayout's section attribution is the error. Do not "correct" S103 toward §Design Details.

**D6 (merge hazard) — the wave's candidate id map collides with the admitted ids.** `advice/ScribeLesson.md:21-22,108` and `out/ScribeLesson/round-24-lesson-draft.md:87-140` propose **S103 = git-cat-file**, **S104 = git-config**, **S105 = partial-clone config list**; the registry has **S103 = partial-clone promisor-pack**, **S104 = fsck.c**, no S105. `advice/SrcPartial.md:185` likewise says "append **S105** after S104 (S102-S104 are now taken)". Nothing in the corpus cites these provisional ids, so there is no live mis-citation — but the draft's id map is stale: do not promote `out/ScribeLesson/round-24-lesson-draft.md` verbatim.

## 4. The one bounded move (candidate patch, not applied)

**`used-by` reconciliation for the reused rows** — mutable cells only (KQ22), logged old→new in `corpus/lessons/round-24.md` as S102–S104 already are. Patch: `out/ConnPriorSources/used-by-reconciliation.patch` (10 additions, 0 immutable-cell changes): S083 += lesson + auditor + grid; S089 += lesson; S094 += lesson; S095 += lesson; **S096 += auditor (D1)**; S099 += lesson; S100 += lesson + grid; S101 += lesson; S102 += auditor + grid; S103 += grid.

Verified in the scratch clone (commit `4fb493f` on `ed1cc3a`): `python3 tools/sources-append-only.py --from ed1cc3a --to HEAD` → "no append-only violations"; `bash scripts/sources-census.sh validate .` → **exit 0**, 0 E-codes, W04 unchanged apart from the pre-existing S103-vs-S099 same-URL pair (house pattern: S085/S093, S091/S100, S071/S083); `census .` → rows 104, mined 86 / queued 8 / rejected 10 — unchanged. Advisory: L1 may accept, narrow, or decline.

## 5. Not verified

- No grid, selftest, mutant, or probe was run (lane bounds) — **no statement about the r24 measurement outcome**; `promisor-grid.py --arm both --json` unrun here.
- `promisor-grid-expectations.json` (1508 lines) and `oracle-amendment-1.json` / `oracle-supplement-2.json` were read as filenames and cited policy text only; their row-to-oracle correspondence was not audited.
- S089–S095's eight r23 pages were not re-opened by me (their falsify seats did). My quote re-verification covered partial-clone, rev-list, git-config, git-cat-file (via the wave copy), commit.c, fsck.c, plus spot checks of git/git-log/git-replace/gitrepository-layout.
- S089's `teaches` cross-row inference ("Neither covers info/grafts or shallow") was flagged by `advice/SrcGlobalGit.md`; I did not re-adjudicate or change it.
- Tools installed or upgraded: **none**. Only plain HTTPS fetches of official git-scm.com / raw.githubusercontent.com pages; no network transports, no execution payloads.

## Files

- `.ufo/waves/round-24/build/advice/ConnPriorSources.md` (this report)
- `.ufo/waves/round-24/build/out/ConnPriorSources/s089-s101-crosscheck.md` (full evidence table, digests, commands)
- `.ufo/waves/round-24/build/out/ConnPriorSources/used-by-reconciliation.patch` (candidate patch, unapplied)
