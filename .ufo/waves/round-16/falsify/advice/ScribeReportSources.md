VERDICT: confirm — round-16 "Sources & frontier" draft checked against the registry before/after snapshots, the live census, and lessons/round-16.md §Gate (registry rows, tier/status deltas, touched cells, frontier advance).

# ScribeReportSources — round 16, Sources & frontier

## Draft section for the round report

### Sources & frontier

Registry: `corpus/SOURCES.md` (SOURCES-CONTRACT-v1), lane kama. Before = commit 20e392e (round-15 end); after = b8e485c (round-16 lane commit; worktree byte-identical to b8e485c for SOURCES.md).

| Metric | Before (20e392e) | After (b8e485c) | Delta |
|---|---|---|---|
| rows | 34 | 41 | +7 |
| tier A / B / C | 31 / 0 / 3 | 38 / 0 / 3 | +7 / 0 / 0 |
| status mined / queued / rejected | 24 / 5 / 5 | 31 / 5 / 5 | +7 / 0 / 0 |
| invalid / missing | 0 / 0 | 0 / 0 | 0 |

Rows added by tier: **A +7, B +0, C +0.** New rows S035–S041, all `mined`: S035 docs, S036 code, S037 code, S038 docs, S039 dataset, S040 docs, S041 own-work (kind per row). Pinned-commit URL for S035 is distinct from S001's master URL (validate E04 clean).

Rows touched, old → new: **one existing cell.** S017 `used-by`: `corpus/knowledge/runtime-health-surface-matrix.md` → `corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/llamacpp-loading-lifecycle.md`. A field-level comparison of all 34 pre-existing rows found no other changed cell (status, recheck, opened, teaches, anchor unchanged). Prose-only additions: round-16 search-log supplement and the S012 synthesis note (no cell).

Frontier rows advanced:
- **Status advancement: none.** Queued frontier rows S021, S022, S023, S025, S029 are unchanged. Rejected rows S024, S026, S027, S028, S030 are unchanged.
- **S021 superseded by row, not by status.** S040 (llm-d v0.10) records "supersedes S021" because S021's recorded URL returns 404 on 2026-10-20. S021 keeps `queued`, as the lesson states (§Gate, "S021 stays `queued` and unedited"). [INFERENCE] The census therefore still counts a superseded row in its queue total of 5.
- **Frontier advanced by addition:** the llama.cpp loading-envelope frontier now has code rows (S036 `server-http.cpp` gate and body, S037 `server.cpp` readiness order), an identity row for the pinned release (S038), a fixture identity row (S039), a versioned readiness-vocabulary row (S040), and a lane-owned live sample (S041).
- **Not advanced:** the SOURCES §Leads Ollama health/readiness route lead (unopened) and the Reddit lead (blocked on fetch). Both remain as written.
- **Open per `corpus/README.md` §Round-16 frontier disposition (lines 215-221):** live grading of a loading server (no 503 captured by the receipt), router mode and sleep (source reads only; S037 covers router start-up order), other engines (advice only, not rows), K05 declared-vs-served context, and the registered consumers (still `DEAD`, not probed).

Expansion: one admitted knowledge entry (`corpus/knowledge/llamacpp-loading-lifecycle.md`) and one capability (`live-llamacpp-lifecycle`), per the README round-16 table. Row growth itself is not counted as expansion (the round-12 rule that expansion is "not inferred from row growth").

## Verification of the lesson's §Gate claims (lessons/round-16.md:54-58)

- "New S035–S041; S017 used-by … → same plus …" — confirmed by field diff (exactly one cell, S017 `used-by`).
- "No status or recheck cell of an existing row changed." — confirmed (diff: only S017 line differs among pre-existing rows; `diff` exit 1 is the expected "differences present" status, see Commands).
- "S021 stays `queued` and unedited; S040 supersedes it by row." — confirmed (S021 row present and `queued`; "supersedes S021" appears in S040 only, count 2 matches S040 teaches + search-log prose).
- Search-log counts "included 7 new rows … reopened 1 (S017, used-by only)" — confirmed (7 rows; S017 only reopened row).

## Commands run and exit codes

All read-only. No install or update performed (no tool installed; no channel used).

1. `./scripts/sources-census.sh --root /home/vgpnk/Projects/shokunin kama` (run from /home/vgpnk/Projects/shokunin) → **exit 0**; output: kama rows 41, tier.A 38, tier.C 3, status.mined 31, status.queued 5, status.rejected 5; FLEET identical; missing 0.
2. `./scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → **exit 0**; `W04 S031 duplicate url docs.ollama.com/api/tags across scopes` (pre-existing warning; does not affect clean lanes) and `ok`. No E-codes.
3. `./scripts/sources-census.sh overdue --root /home/vgpnk/Projects/shokunin --today 2026-10-20 kama` → **exit 0**; no `overdue` lines; cadence lines only (on-release, 90d, every round for S030/S034/S039/S041).
4. `git show 20e392ea683a36bc223eb7cb45897acfb45456a3:corpus/SOURCES.md` → **exit 0** (93 lines, 34 rows).
5. `git show b8e485c:corpus/SOURCES.md` → **exit 0** (127 lines, 41 rows); `cmp` of worktree `corpus/SOURCES.md` against it → **exit 0** (identical).
6. `diff SOURCES-before.md SOURCES-after.md` → **exit 1** (differences; the pipeline in my shell reported 0 because it ran through `cut`, so the recorded status is the piped one, and the real diff status is 1). Differences: S017 cell and seven added rows S035–S041 plus appended prose.
7. Per-field `awk` over the S017 row → **exit 1** (expected: differs only in the `used-by` field, field 11).
8. `awk`/`grep -cE` counts on before and after registry → **exit 0**: before 34 rows (A 31, C 3; mined 24, queued 5, rejected 5); after 41 rows (A 38, C 3; mined 31, queued 5, rejected 5).
9. Reads: `round-16/sources-before-census.txt` (exit 0 `census`), `round-16/sources-before-validate.txt` (`ok`, W04 only), `corpus/lessons/round-16.md` §Gate, `corpus/README.md` lines 200-240.
10. `grep -i frontier` over `corpus`, `SKILL.md`, `README.md`, `PROVINCE.md`, `SCORECARD.md` → matches read for definition context only; frontier used as "queued/leads plus README §Frontier disposition".

Scratch: `/tmp/kama-r16-ScribeReportSources/` (SOURCES-before.md, SOURCES-after.md) removed after this report.

## Limitations

- The census script reports only aggregate counts, so the per-row analysis above (field diff, status lists) comes from my own `awk`/`diff` on `git show` output, not from the script.
- "Frontier" is not defined as a machine field in SOURCES.md. I used queued rows, §Leads, and the README §Frontier disposition, which is my reading. [INFERENCE]
- I did not re-open any source URL; claims are limited to the registry text and the lane's own round-16 gate.

## Findings for the main agent

- No defect in the round-16 Sources accounting: counts, tier/status deltas, the single touched cell, and the new-row set all agree between the lesson, the registry diff, and the census.
- Watch item (not a defect): S021 remains `queued` while superseded by S040. A future round could close the queue cell under the contract; this round did not, by its own stated rule.
- Pre-existing W04 (S011/S031 share one tags URL) is unchanged from before the round.

## Installs

None.
