# ConnPriorSources — S089–S101 cross-check, reused-row support map, and r24 claim→row mapping

Seat: `KamaR23-2.ConnPriorSources-2` (leaf connector, no dispatch).
Base: `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` (r23 tip) → r24 integration `ed1cc3a342bd801fe2d0f54f7ba2eb4ca42d5f05`.
Scratch clone: `/fast/scratch/hyaku/kama-r24/ConnPriorSources/clone` (`git clone --no-hardlinks`).
No production file edited, no registry row added, no commit/push, no install.

---

## 1. Provenance of every reused row S089–S101 (source task → verification record)

| row | opened by (source task) | verification record | r24 reuse |
|---|---|---|---|
| S089 `git(1) global options` | r23 build seat `SrcGitEnv` (`build/advice/SrcGitEnv.md:27`, provisional id S089) | falsify seat `SrcS089.md:6` "ADMIT (holds)" | r24 lesson `:39` reopens; auditor keeps both flags (`tools/report-landing-audit.py:138`) |
| S090 `git-replace(1)` | r23 build seat `SrcGitReplace` (`SrcGitReplace.md:35`, provisional S089) | `SrcS090.md:11` "ADMIT (row holds)" | mechanism retained via `--no-replace-objects` (auditor `:138`) |
| S091 `git-config(1)` | r23 build seat `SrcGitConfig` (`SrcGitConfig.md:38`, provisional S089) / `SrcGitEnv.md:37` (provisional S091) | `SrcS091.md:9` "Admit" | **superseded by S100**; not cited in r24 corpus |
| S092 `partial-clone` | r23 build seat `SrcPartialClone` (`SrcPartialClone.md:27`, provisional S089) | `SrcS092.md:8` "ADMIT … with one Gate over-attribution" | **superseded by S099** |
| S093 `git-log(1)` | r23 build seat `SrcGitLogFollow` (`SrcGitLogFollow.md:36`, provisional S089) | `SrcS093.md:6` "ADMIT" | mechanism retained (`-c log.follow=false`, `i18n.logOutputEncoding=UTF-8`) |
| S094 `gitrepository-layout(5)` | r23 build seat `SrcGitRepoLayout` (`SrcGitRepoLayout.md:17`, provisional S089) | `SrcS094.md:7` "ADMIT (holds)" | r24 lesson `:40` reopens; alternates exercised by `CaseAlternatesComplete` |
| S095 `bytes.decode` (`/library/` URL) | r23 build seat `SrcPythonDecode` (`SrcPythonDecode.md:28`, provisional S090) | falsify seat `SrcS095.md:7` "**REJECT** the row as registered (narrow)" | status mined→rejected; **superseded by S096**; cited in r24 lesson `:58` *as rejected* |
| S096 `bytes.decode` (redirect target) | r23 **replacement L1** (`corpus/lessons/round-23.md:148`) — no per-seat advice file | no wave re-open; no outside re-open | live decode row for the auditor |
| S097 `subprocess` text mode | replacement L1 (`round-23.md:151`) | no wave re-open | used by the knowledge entry `:79` |
| S098 `io.TextIOWrapper` | replacement L1 (`round-23.md:154`) | no wave re-open | used by the knowledge entry `:79` |
| S099 `partial-clone §Handling Missing Objects` | replacement L1 (`round-23.md:156`) | no wave re-open | r24 lesson `:40` reopens; live lazy-fetch authority |
| S100 `git-config#_variables` | replacement L1 (`round-23.md:159`) | no wave re-open | `-c log.showSignature=false`, `core.sshCommand`, `gpg.program` in auditor `:133-137` |
| S101 `commit.c read_graft_line` | replacement L1 (`round-23.md:162`) | **outside** re-open: `CritNoTrade/closure-r428.txt:41` re-read `commit.c` lines 249-260 | r24 lesson `:57`; `grafts_effective` in auditor `:610,699` |

### 1a. Structural facts behind the table

- The seven r23 build-wave source seats all drafted **provisional id S089** (plus S090/S091) for *different* pages; the L1's admission is what allocated the final S089–S095 ids. This is the "reused row" allocation hazard of the round, and it is already resolved in the registry.
- **Asymmetry worth recording:** S089–S095 each have a falsify-wave re-open report (`SrcS089.md`…`SrcS095.md`, 7 files in `.ufo/waves/round-23/falsify/advice/`). S096–S100 have **no** second reader anywhere in the tree (grep for `S09[6-9]|S10[01]` over `.ufo/waves/round-23/` returns only `AppendParser.md`'s unrelated `S099` fixture id). Only S101 has an outside re-open. This is a pre-existing r23 asymmetry, not r24-introduced; r24 reused S089/S083/S094/S099 without adding re-opens, which the r24 lesson discloses as "Reopened sources" (`:39-40`).
- Row integrity confirmed: `git diff 0df800e8 HEAD -- corpus/SOURCES.md` changes **no** S001–S101 cell and adds only S102/S103/S104. `tools/sources-append-only.py --from 245a37f6 --to ed1cc3a` → "added S096 … added S101 (allowed) … no append-only violations".
- All 13 reused rows still carry 11 cells, tier A, `on-release` recheck, opened 2026-10-21; every `used-by` path exists on disk (census E11 clean).

## 2. The r24 repair's own rows: claim → row → real consumer

| r24 claim | admitted row | row anchor / quote (verified this session) | production consumer |
|---|---|---|---|
| "metadata alone never changes a verdict" | **S103** | partial-clone 2.56.0, §Handling Missing Objects first bullet: "These promisor packfiles consist of a \"<name>.promisor\" file with arbitrary contents" — present upstream at `Documentation/technical/partial-clone.adoc:116-118` (sha256 `9512d7ee…`) | `tests/report-audit/promisor-grid.py:268-270` (marker pairing) |
| "missing required object is detected locally, not fetched" | **S102** | git-rev-list 2.56.0 `--missing=<missing-action>`: "will also print a list of the missing objects. Object IDs are prefixed with a \"?\" character" (`Documentation/rev-list-options.adoc:1060-1061`, sha256 `8414be81…`) | `tools/report-landing-audit.py:673`; `tests/report-audit/promisor-grid.py:295` |
| "a green fsck is not availability proof" | **S104** (rejected) | `builtin/fsck.c` v2.56.0 `mark_object` lines 143-149 (sha256 `d25f3b1a…`, byte-identical to `out/SrcFsck/fsck-builtin.c`): `if (is_promisor_object(options->repo, &obj->oid))` … `return 0;` — the early return precedes the `HAS_OBJ` check at `:151` | cited as a rejected candidate in `corpus/knowledge/error-is-not-a-verdict.md:117` |
| "unknown citation in a promisor-backed repo is unknown, not absent" | **S083** (batch records) + **S099** (no promisor-object check) | cat-file 2.56.0 §BATCH OUTPUT: "If a name is specified on stdin that cannot be resolved to an object in the repository" / `<object> SP missing LF`; partial-clone "no check as to whether the missing object is actually a promisor object is performed" | `tools/report-landing-audit.py:212,242`; `promisor-grid.py:312` |
| "the isolation boundary is unchanged" | **S089** + **S100** | `--no-lazy-fetch` / `--no-replace-objects`; `log.showSignature`, `gpg.program`, `core.sshCommand` | `tools/report-landing-audit.py:133-138`; `promisor-grid.py:111` |
| "a comment-only grafts file rewrites nothing" | **S101** | `commit.c` v2.56.0 `read_graft_line`: `strbuf_rtrim(line); if (!line->len || line->buf[0] == '#') return NULL;` | `tools/report-landing-audit.py:610,699` |

**No invented source registration.** Corpus-wide scan of every committed file (`SKILL.md`, `LOG.md`, `corpus/lessons/*.md`, `corpus/knowledge/*.md`, `corpus/QUALITY.md`, `corpus/README.md`) finds **no** cited S-id absent from the registry. `S105` occurs only in four uncommitted wave artifacts (`advice/ScribeLesson.md:22,108,160`, `advice/SrcPartial.md:185,197`, `out/ScribeLesson/round-24-lesson-draft.md:124`, `out/SrcPartial/proposed-row.md:18,21`) and in no corpus file.

## 3. Overlap / support defects (this lane's remit)

**D1 — the auditor's live decode dependency is recorded on the *rejected* predecessor, not on the admitted superseder.**
`S095` (status **rejected**) lists `tools/report-landing-audit.py` in `used-by`; `S096` (status mined, "supersedes S095") does not — yet S096's own `teaches` cell says "the auditor's bytes-mode `git()` decode relies on it". The current auditor decodes bytes itself and never uses text mode: `grep -c text=True tools/report-landing-audit.py` → **0** at r24 HEAD and at r23 base `0df800e8`; only the *frozen* arm `4fe9339f` had `capture_output=True, text=True` (`:90`). So the ledger points the tool at the row whose claim was rejected and omits the row that states its mechanism.
*Fix (append-only legal):* add `tools/report-landing-audit.py` to S096's `used-by` (mutable cell). Whether to drop the tool path from S095 is a judgment call — the r23 Gate still cites S095 as the row that was checked — so leaving S095 as-is and adding S096 is the minimal, non-destructive correction.

**D2 — a rejected row keeps a positive-claim `teaches` cell, against the registry's own rejected-row shape.**
Contract (`CORPUS.md` §SOURCES.md, Shape): "Rejected rows read `REJECTED: <reason>; flip: <what would change the verdict>`." S063, S077, S104 comply. **S095 does not**: its `teaches` still reads "The default `strict` handler raises UnicodeError, so text-mode subprocess output with invalid bytes raises unless the caller maps the error." — a positive claim about text mode, and the exact claim the falsify seat rejected (`SrcS095.md:7`). Status and teaching therefore contradict each other in the registry. `teaches` is immutable (KQ22), so the repair route is a new superseding row (as S096 was), not an edit.

**D3 — the r24 knowledge entry's isolation sentence rests on rows its own `source:` line does not name.**
`corpus/knowledge/error-is-not-a-verdict.md:91-92` asserts the global `--no-lazy-fetch` / no-replace-objects / signature-log-suppression boundary; the governing rows are **S089** and **S100**. The section's `source:` line (`:117`) lists only `S102, S103, S104 (rejected candidate); corpus/lessons/round-24.md`. The unscoped draft in `out/ScribeKnowledge/error-is-not-a-verdict.round24-append.md:215` *did* list `S083, S089, S099, S102, S103, S104 (rejected)`. The applied file dropped the three reused ids. The claim is true and the rows exist; only the citation is missing. Same class as the r23 precedent (S096/S097/S098 are named at `error-is-not-a-verdict.md:79`).

**D4 — the reopened reused rows are not in the ledger.** r23's quoting Gate put `corpus/lessons/round-23.md` into the `used-by` of every row it quoted (S089–S095, S099–S101 all carry it). The r24 lesson names S089, S083, S099, S094 (`:39-40`) and S101/S095 (`:57-58`) but no reused row's `used-by` gained `corpus/lessons/round-24.md` — while the three *new* rows S102/S103/S104 did gain it. Judgment call, stated as such: r24's list is a re-verification record rather than a quoting Gate, so leaving reused rows untouched is defensible; but the r23 Gate precedent (quote ⇒ lesson path in `used-by`) is the house rule, and the two r24 rows whose *teaches* are quoted rather than merely named (S083 at `:42-43`, S089 at `:39`) are the strongest candidates. This is the one item where I flag a decision rather than assert a defect.

**D5 — `S103`'s anchor is right; a peer's contrary note must not be acted on.**
`advice/SrcRepoLayout.md:77` places the `.promisor` sidecar definition in partial-clone "**§Design Details**". Upstream `partial-clone.adoc` puts "these incomplete packfiles are marked as \"promisor packfiles\"" in §Design Details (`:99-100`) but the sentence S103 quotes — "These promisor packfiles consist of a \"<name>.promisor\" file with arbitrary contents" — in **§Handling Missing Objects, first bullet** (`:111-118`). The admitted S103 anchor (§Handling Missing Objects, first bullet) and the r24 lesson quote (`:21-24`) are correct; SrcRepoLayout's section attribution is the error. Do not "correct" S103 toward §Design Details. (S103's `teaches` remains partly inferential — "marking records promised-object provenance" — and the lesson labels its second sentence a lane inference, `:26-27`; that inference is registered as such only in the lesson, not in the row cell. Minor, and the row cell is immutable.)

**D6 — the wave's candidate id map collides with the admitted ids.** `advice/ScribeLesson.md:21-22,108` and `out/ScribeLesson/round-24-lesson-draft.md:87-140` propose **S103 = git-cat-file**, **S104 = git-config**, **S105 = partial-clone config list**; the admitted registry has **S103 = partial-clone promisor-pack**, **S104 = fsck.c**, and no S105. `advice/SrcPartial.md:185` likewise says "append **S105** after S104 (S102-S104 are now taken)". Nothing in the corpus cites these provisional ids, so there is no live mis-citation — but the uncommitted draft's id map is stale, and merging that draft's Gate table into the corpus would mis-cite S103/S104. Recommendation to L1: do not promote `out/ScribeLesson/round-24-lesson-draft.md` verbatim.

## 4. The one bounded proposal (applied to nothing; candidate patch attached)

**Proposal:** reconcile `used-by` for the reused rows the r24 corpus actually relies on, using the mutable-cell allowance (KQ22) and logging old→new in the round-24 lesson, as `corpus/lessons/round-24.md` already does for S102–S104.

Candidate patch (not applied): `out/ConnPriorSources/used-by-reconciliation.patch` — 10 `used-by` cell additions, 0 immutable-cell changes:
`S083 += corpus/lessons/round-24.md, tools/report-landing-audit.py, tests/report-audit/promisor-grid.py` ·
`S089 += corpus/lessons/round-24.md` ·
`S094 += corpus/lessons/round-24.md` ·
`S095 += corpus/lessons/round-24.md` ·
`S096 += tools/report-landing-audit.py` (D1) ·
`S099 += corpus/lessons/round-24.md` ·
`S100 += corpus/lessons/round-24.md, tests/report-audit/promisor-grid.py` ·
`S101 += corpus/lessons/round-24.md` ·
`S102 += tools/report-landing-audit.py, tests/report-audit/promisor-grid.py` ·
`S103 += tests/report-audit/promisor-grid.py`.

**Verified in the scratch clone** (commit `4fb493f` on top of `ed1cc3a`):
- `python3 tools/sources-append-only.py --from ed1cc3a --to HEAD` → "no append-only violations" (only `used-by` moved).
- `bash scripts/sources-census.sh validate .` → **exit 0**, zero E-codes; W04 count unchanged except the S103 partial-clone duplicate-URL warning that already existed at base (23 → 24 W04s, the new one being S103 vs S099 on the same URL — a scope-distinct pair, the established house pattern: S085/S093 git-log, S091/S100 git-config, S071/S083 cat-file).
- `census .` → rows 104, tier A 99 / B 2 / C 3, mined 86 / queued 8 / rejected 10 — unchanged.

L1 may accept, narrow, or decline; the patch is advisory and the applied registry is untouched.

## 5. Verified in this lane (commands and their results)

```
# integrity of the reused band
git show 0df800e8:corpus/SOURCES.md | diff - <(git show HEAD:corpus/SOURCES.md)   # no S001-S101 cell differs; +S102,S103,S104
python3 tools/sources-append-only.py --from 245a37f6 --to ed1cc3a                  # no violations
python3 tools/sources-append-only.py --from 0df800e8 --to ed1cc3a                  # added S102..S104 (allowed)
bash scripts/sources-census.sh validate .                                          # exit 0, 0 E-codes
bash scripts/sources-census.sh census .                                            # rows 104

# every cited S-id exists (whole corpus)
python3 - <<'PY'  # committed SKILL.md, LOG.md, corpus/**  ->  "committed corpus ids absent from registry: NONE"
# S105 exists only in uncommitted wave artifacts; 0 occurrences in corpus/ or SKILL.md

# live mechanisms vs rows
grep -c text=True tools/report-landing-audit.py                                      # 0 (bytes mode) at HEAD and 0df800e8
git show 4fe9339f:tools/report-landing-audit.py | grep -n text=True                  # the frozen arm did use text mode
grep -n "rev-list\|--missing=print" tools/report-landing-audit.py                    # :673
grep -n "batch-all-objects" tools/report-landing-audit.py                            # :640
grep -n "missing=print\|batch-all-objects" tests/report-audit/promisor-grid.py       # :295, :312
grep -n "partialclonefilter\|\.promisor" tests/report-audit/promisor-grid.py          # :264-270 (promisor_facts)

# upstream quote re-verification (plain HTTPS, official git.git at v2.56.0)
sha256sum partial-clone.adoc rev-list-options.adoc extensions.adoc remote.adoc
  9512d7ee0b79680f61d3f98c9eae42cc1dbaeef63535c5502cff66d7bce19264  partial-clone.adoc
  8414be814954bad98c510c44a5bbf477c07072b185c0c079600fceedf5f5b371  rev-list-options.adoc
  9729ce5168f8b2059c86fef0b44e26631b4ffd22ef378b08561a398fc42761bc  extensions.adoc
  f52705b3001bec2f77a33fd160422a6399e8cdb29be6988f5ad0e510704a513b  remote.adoc
grep -n "promisor remote" extensions.adoc        # 41-45  (the "promises that all such omitted objects can be fetched" sentence)
grep -n "Remotes that are considered" pc.adoc    # 200-206 (the three promisor-remote config keys)
grep -n "filter=blob:none" rev-list-options.adoc # 986
```

## 6. Not verified / out of scope

- No grid, selftest, mutant, or probe was executed (lane bounds); no `promisor-grid.py --arm both --json` run, so no statement here about the r24 measurement outcome.
- The `promisor-grid.py` expectations manifest (`promisor-grid-expectations.json`, 1508 lines) and the L1's `oracle-amendment-1.json` / `oracle-supplement-2.json` were read only as filenames and as cited policy text; I did not audit their row-to-oracle correspondence.
- I did not re-open the eight r23 source pages for S089–S095 (their falsify seats did; my re-fetch covered partial-clone, git-rev-list, git-config, git-cat-file, git, git-log, git-replace, gitrepository-layout). My quote checks were: partial-clone, rev-list, git-config, git-cat-file (via the wave copy), commit.c, fsck.c, and spot checks of git/git-log/git-replace/gitrepository-layout.
- S089's `teaches` cell contains a cross-row inference ("Neither covers info/grafts or shallow"), flagged as such by `advice/SrcGlobalGit.md`; I did not re-adjudicate it and did not change it.
- Tools installed or upgraded: **none**. No network transport other than plain HTTPS fetches of official git-scm.com / raw.githubusercontent.com pages.
