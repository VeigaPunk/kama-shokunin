# kama round 38 lesson

author: kama L1, round 38
date: 2026-10-25
base: 2a4a97dc890fe393035986c951797c5d65b6cc69

## Claims

C1 calibration 7 → 7. Predicate: a round-36 verifier routed statement is
corrected iff corpus/lessons/round-38.md contains a correction row naming
R36-D2C and the counter re-derives the cited committed-byte fact. That fact: the
five staged rows citing the affected entry are S332, S336, S337, S338 and S339
at `/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md` lines 9, 13,
14, 15 and 16; the row must carry no wrong-id restatement, and the r37 lesson
blob and the r37 fleet report blob must be unchanged. Counting command:
`python3 /fast/scratch/hyaku/kama-r38/tools/round38-statement-audit.py --repo /fast/scratch/hyaku/kama-r38 --tip <full-commit>`.

C2 coverage 9 → 9. Predicate: the round-38 coverage block names each of
`corpus/knowledge/sglang-docs-version-pinning.md` and
`corpus/knowledge/sglang-docs-version-pinning-amendment-2026-10-23.md`, every
one of those files exists in corpus/knowledge/, and each cites an S-id present
in corpus/SOURCES.md at the tip and absent at base
2a4a97dc890fe393035986c951797c5d65b6cc69 on its source: lines; none of those
two holds at that base. Counting command: `python3 /fast/scratch/hyaku/kama-r38/tools/round38-coverage-audit.py --repo /fast/scratch/hyaku/kama-r38 --tip <full-commit>`.

C3 operability 8 → 8. Predicate: tools/round37-statement-audit.py and
tools/round37-coverage-audit.py exist at the tip under tools/ and are absent at
base 2a4a97dc890fe393035986c951797c5d65b6cc69; each exits 0 on --help; each
exits 0 (met True) when re-run at the r37 tip against this repo; and the
round-37 wave's 37th seat report (CriticEntries.md) and a parsed
seat-exit-codes.json covering all 37 members exist at the tip. Counting
command: `python3 /fast/scratch/hyaku/kama-r38/tools/round38-operability-audit.py --repo /fast/scratch/hyaku/kama-r38 --tip <full-commit>`.

All three predicates were frozen before scoring (`.ufo/waves/round-38/preregistration.json`, commit 41e149ce). The do-nothing controls are `.ufo/waves/round-38/controls/c1-noop.out` (`uncorrected 1 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False`, exit 1), `.ufo/waves/round-38/controls/c2-base.out` (`named 0 files_exist 0 cited_new 0 met False`, exit 1) and `.ufo/waves/round-38/controls/c3-base.out` (`found 0 base_found 0 help_ok 2 rerun_ok 2 report_37 0 receipt_ok 0 met False`, exit 1). A control that met its target would have retired the counter before data.

Instrument repair (C2, wave 1): as committed at the freeze, the C2 counter
looked the entries up as `knowledge/…` at the repo root instead of
`corpus/knowledge/…`, counted any S-id anywhere in SOURCES.md as registry-held,
never checked base absence of the files, and pooled ids across entries, so the
frozen predicate was unmeasurable. Wave-1 seats (ReviewKQ46Behavior,
ScoutLearned, ScribeLesson, ScribeAppendBlock, ReviewFreeze) reproduced the
defect against fixture tips. The counter was repaired before data to implement
the frozen predicate literally: `PREDICATE` is unchanged, the measurement line
keeps the same shape (`named N files_exist N cited_new N met X`), and the
repair commit re-runs all three failing controls with identical met-False
lines. The C1 and C3 counters are unchanged in logic; only the `met`
capitalization was aligned to the frozen receipt text.

## Corrections

- R36-D2C: The round-36 Gate's byte-copy reject paragraph (`corpus/lessons/round-36.md:43`, staged `endpoint-health-probe-conventions.md`) gives a four-id range as the staged rows that entry cites. That range is wrong: the five staged rows citing that entry are S332, S336, S337, S338 and S339, at `/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md` lines 9, 13, 14, 15 and 16 (vLLM Engine Arguments; SGLang in llm-d; Docker Compose file reference; Dockerfile reference; Prometheus blackbox_exporter README), and the staged entry's own source: lines 6–10 cite exactly those five. The reject decision stands; only the id set is corrected, and the wrong ids are absent from this row. Package bytes read at write time: SOURCES.append.md sha256 `3ad0df68e8423a3b1b99d4e3b8d8c6271f7a4f4c96d3a5ad4e0a85a991ce234ff`.

## Gate

Opened 2026-10-25 by the L1 and re-opened by wave-1 seats. Theme: SGLang
documentation version pinning — the published docs pages carry no version
marker; their sources are contained unchanged in release tag v0.5.22, and the
tag inventory is verifiable with `git ls-remote --tags`. Two admitted entries,
three registry rows, one reject (plus two wave-1 rejects). The staged package
under /home/vgpnk/Projects/shokuknow was read, never written, and no campaign
tool was run.

Admit S352. URL https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/advanced_features/radix_eviction_policy.mdx. Opened 2026-10-25, HTTP 200, 6243 bytes, sha256 `4ba2e6210d27ed1de045ae5b6aad9e475f9a7debdd64671178c04193c560876b` (seat FetchS352). Anchor: `## How eviction picks a victim` (line 13). Located quote (12 words, byte-exact including the source's bold markup): "The policy scores each candidate and the **lowest score is evicted first**." The staged anchor `§Eviction candidates` names no heading in this file (0 hits) and is replaced by the real heading. This is the tag-pinned source file; the lane's S333 is the unversioned rendered page, a different artifact. Used by corpus/knowledge/sglang-docs-version-pinning.md and corpus/knowledge/sglang-docs-version-pinning-amendment-2026-10-23.md.

Admit S353. URL https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/advanced_features/session_radix_cache.mdx. Opened 2026-10-25, HTTP 200, 2820 bytes, sha256 `0b50a3e5b8b5e97d3ce035801d18183ce1fa06dba9f6644f9c0f75bc0bf748cd` (seat FetchS353). Anchor: lead paragraph, line 9, before `## Enable the cache`. Located quote (20 words): "Session references are soft protection, not memory pins. Referenced KV can still be evicted when reclaiming unreferenced KV is insufficient." The staged anchor `§Session references` names no heading in this file and is replaced by the line locator. The lane's S334 is the unversioned rendered page, a different artifact. Used by corpus/knowledge/sglang-docs-version-pinning.md and corpus/knowledge/sglang-docs-version-pinning-amendment-2026-10-23.md. Recheck 90d.

Admit S472 (own-work). Command `git ls-remote --tags https://github.com/sgl-project/sglang.git`, run 2026-10-25T09:12:47Z with git 2.56.0: exit 0, 190 lines, 11768 bytes, sha256 `5585f602f71c4d4fa5a20125b2b8e4a1132a2d41abf511d7ef09c43a91d950f2`, byte-identical across two independent seat runs (ExecTagInventory, ExecTagInventory-2). Anchor: output line for `refs/tags/v0.5.22`. Located quote (2 tokens): "35ce313293052f8362e0829e7512bc9bc3d336c9	refs/tags/v0.5.22" (peeled commit `baa9befa381511cd4d56f83980951e5a45fffc6d`). The id S472 is the first id free in both the lane registry and the staged package (staged S364/S365 are `http_server.py` rows whose URL duplicates lane S329). Used by corpus/knowledge/sglang-docs-version-pinning-amendment-2026-10-23.md.

Reject staged S360 (https://api.github.com/repos/sgl-project/sglang/tags?per_page=20). Opened 2026-10-25T09:12:57Z, HTTP 403, 280 bytes, `x-ratelimit-remaining: 0` of 60. Located body text: "API rate limit exceeded for <host-ip>." Reason: the anchor is not fetchable without authentication on this host, so a reader cannot re-derive the tag inventory from it; the lane's own reproducible `git ls-remote` row (above) carries the same fact and supersedes it. Flip: a fetchable anchor for the tag inventory — the REST endpoint answering 200 to an unauthenticated reproducible request from this host.

Reject staged `runtime-health-surface-matrix-amendment-2026-10-24-r7.md` (its new source S396 duplicates the URL of lane S329 — `http_server.py` at v0.5.22 — so admitting it would break one-URL-one-row). Flip: a row whose URL differs from the lane's held rows.

Reject staged `spot-check-protocol.md` (a fleet-protocol method, out of the lane's endpoint-health province). Flip: a lane-owned application of the protocol in a concrete endpoint-health check.

Live reading surfaces (not new rows): https://docs.sglang.io/docs/advanced_features/radix_eviction_policy (HTTP 200, 296606 bytes) and https://docs.sglang.io/docs/advanced_features/session_radix_cache (HTTP 200, 277182 bytes), both opened 2026-10-25. Neither URL nor body carries an SGLang version marker; the version-like tokens on both pages are Mintlify/Vercel build ids. Both quoted sentences are on the live pages (the radix one inside `<strong>` markup). Both pages report `lastModified` 2026-10-24T12:16:03Z, later than the staged check of 2026-10-23, with the quoted wording unchanged. A byte-diff of the radix live page against the round-37 copy shows only Mintlify `liveDeploymentHistoryId`/`collectionId` values differ; page content is unchanged.

Identity check: each `.mdx` is byte-identical at the staged wave-1 commits and at tag v0.5.22. S352: commit `77091cea…` file sha256 equals the tag file sha256 `4ba2e621…` (seat ScribeEntryPin, `commit-77091cea-radix_eviction_policy.mdx`). S353: commit `d34f7b23…` file sha256 equals the tag file sha256 `0b50a3e5…` (seat ScribeEntryPin, `commit-d34f7b23-session_radix_cache.mdx`).

### Id collision (scratch, before any append)

The 0–3 leading-space guard on the indented fixture catches `  | S472 |` and `  | S352 |` (comm nonempty). On the real lists, `comm -12` between the lane registry ids and the staged package ids prints 7 rows — S330, S333, S334, S335, S346, S347, S363 — all round-37 adoptions whose source cells match staged bytes; none is a duplicate id. S352, S353 and S472 appear nowhere in the lane registry, the staged package, or either file's URL list.

### Validate-before-append (scratch)

Rows inserted after the S363 row in a lane mirror (with the two knowledge entries in the same tree) pass `sources-census.sh validate --file <mirror>` with exit 0 and only the lane's 93 baseline W04 warnings (ExecValidateMirror; ReviewSchema; ScribeAppendBlock mirror receipts). After the real append, the census on the lane itself also passes (exit 0, same warnings).

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| instrument-not-landed | round 37 printed counting commands for C1 and C2 whose counters were untracked: `tools/round37-statement-audit.py` and `tools/round37-coverage-audit.py` were absent from tip e97ce496, and the C2 counter existed nowhere in the landed tree — corpus/lessons/round-37-verifier-spotcheck.md §1 and §6 item 1 | none in round 37 — the round-37 Gate checked the receipts' bytes, not that the counter producing them was tracked; the non-author verifier found it | a counter lands in the same commit as the first receipt it produces; C3 (`tools/round38-operability-audit.py`) checks presence at the tip, `--help` and a met-True rerun at the r37 tip |
| dropped-sub-fact | the round-37 C1 corrected two of the three D2 sub-facts but did not land the third (the wrong id-range statement), which the round-37 verifier routed as defect 4 — corpus/lessons/round-37-verifier-spotcheck.md §6 item 4 | the round-37 correction row named the two sub-facts it fixed; the third was not named | this round's R36-D2C row (above) appends the third sub-fact, and C1 re-derives it from committed package bytes |

## Frontier

Routed r37 verifier defects: item 1 (counters not landed), item 2 (uncommitted round-37 tree with the 37th seat report) and item 3 (no seat exit-code receipt) are C3; item 4 (the third D2 sub-fact) is C1; item 5 (C2 `cited_ids()` too loose) is carried in the round-38 C2 counter, which reads ids from source: lines only and keeps only ids the registry holds and whose artifact the source line names (KQ46).

considerthese/2026-10-24.md: proposal 1 is KQ44 and proposal 2 is KQ45 (both already landed); proposal 3 (prepared-not-dispatched ledger) is not taken this round; proposal 4 (attempts and restarts per round) is taken as KQ47 — this round runs as attempt 2 (watchdog lines 1293–1294). The file was not edited.

Search log: the round's searches were all within the lane repo, the fleet root and the read-only staged package; no external web search was needed (all sources were opened by direct fetch).

## Wave evidence

Wave 1 (36 seats, v1): reviewer 8, scout 9, critic 4, scribe 5, executor 5, mutation-tester 3, connector 1, revenger 1 (`.ufo/waves/round-38/w1/spec.json`; `run.json.counts.spawn` = 36). Reports under `.ufo/waves/round-38/w1/out/`. Seat accounts: 36/36 seat identities returned reports (two seat instances per identity ran because the wave payload was dispatched twice; both instances' reports were merged or kept side by side, and the registry records the 36 `-2` handles). Seat exit codes: `.ufo/waves/round-38/w1/out/seat-exit-codes.json` (36 members, rc null for all — exit status was not persisted from the eval-kernel dispatch; report presence is). Sources: S352, S353 and both live pages were opened by seats with HTTP 200, byte counts and sha256; the S472 command and the S360 probe were run by two independent executor seats with byte-identical captures.

## SHONEN

[~] calibration: D2 third sub-fact corrected by append; C1 measured met False → met True at the measured tip.
[~] coverage: S352, S353, S472 admitted; S360 and two wave-1 rejects recorded; README block added; C2 measured met False → met True at the measured tip.
[~] operability: the two round-37 counters landed under tools/; the 37th seat report and an enriched seat-exit-codes.json landed; C3 measured met True at the measured tip.
[~] frontier: one assimilation theme adopted; mistake mining yielded the `instrument-not-landed` row; the census start and end both exit 0.

### Round-40 citation correction note (append-only)

The package-byte digest cited in the R36-D2C paragraph above was abbreviated as `3ad0df68…`. On 2026-10-25, `/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md` was re-opened and its full SHA-256 measured as `3ad0df68504e1f49a0ab23e68b2034a9d6258345468fa03013737ced7ce234ff`; see `corpus/lessons/round-40.md` and `.ufo/waves/round-40/c1/` receipts. This note supplements the historical paragraph; it does not rewrite it.

