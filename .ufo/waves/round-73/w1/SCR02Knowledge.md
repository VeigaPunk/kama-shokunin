# SCR02Knowledge — knowledge entries, coverage-map rows, quality criteria, considerthese disposition

- Seat: SCR02Knowledge (scribe, axes: expansion), milestone kama r73 w1.
- Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin` (L). Tip at every write: `git -C L rev-parse
  master` → `bc9e30599b6c6133bb094f0e7abd1a9f512778ec` (the wave-spec freeze commit; the plan's
  freeze base is `6e961996`, two commits earlier).
- Scratch: not used. `/fast/scratch/hyaku/kama-r73/SCR02Knowledge` was never created; nothing to
  delete.
- No subagent dispatch, no fleet-root write, no git/jj mutation, no `ask`.

## What I built

1. `corpus/knowledge/host-identity-drift-gate.md` (83 lines, under the 90-line cap): what a
   `Round-<N> host-identity block (YYYY-MM-DD)` records (the `uname -s` / `uname -m` /
   `/etc/os-release` `ID` triple, parsed not sourced), why a kernel-only update leaves it fixed
   while a machine or OS change moves it, what the counter grades (newest block in file order wins,
   append-only, `stale=0` iff recorded equals live, unparsable triple is `stale-host` not a skip,
   0/1/2 exit map) and what it does not show (a serving surface, the kernel version, a correction of
   the round-71 surface claims, that the block was measured, a history of host moves). Limits:
   os-release `ID` is distro identity not version; graded state is the file at grading time;
   container/VM semantics marked `[INFERENCE]`. Source after SCR01Sources landed the row: S544
   (`uname(1)`, quote "`-s` prints the kernel name and `-m` the machine hardware name").
2. `corpus/knowledge/round-scope-survivor-cases.md` (61 lines): the three round-72 survivors as a
   decision table — A5 linked worktree, A6 valid older label hiding a newer round's ignored work,
   A7 `submodule.<name>.ignore=all` — with the base hole, the committed fixture (`c1_a5`, `c1_a6e`,
   `c1_a7sub2`), the v2 case and the exact command it runs, the fixed six-case population and
   order, the `M >= N` bound with the reason older rounds are excluded, and the limits (no
   `--allow-ignored` escape; an uninitialised submodule is skipped and named; git state only; a red
   fixture proves the counter, not the lane). Source after SCR01Sources landed the row: S545
   (`gitmodules(5)`, quote "`all` makes the submodule never considered modified while it can still
   be staged").
3. `corpus/README.md`: one appended coverage-map section with the two entry rows (append-only; no
   existing line moved; measured counts in the section).
4. `corpus/QUALITY.md`: KQ120 (one named fixture per survivor class AND the base counter accepting
   each as the control, both exits recorded by one scorer run) and KQ121 (a host-identity record is
   graded against the live triple, newest block winning, never against its own prose), plus KQ122
   (one pin-gap line per pinned engine from that round's own live `pin-watch` run, every `behind`
   row naming its `source` rows) — added because `considerthese/2026-10-26.md` proposal 4 is cited
   and the live run really happened (below).
5. Ten receipts under `.ufo/waves/round-73/w1/SCR02Knowledge/`.

## Files written (exact)

| Path | Lines | Kind |
|---|---|---|
| `corpus/knowledge/host-identity-drift-gate.md` | 1–83 (frontmatter 1–3, body 5–83) | new |
| `corpus/knowledge/round-scope-survivor-cases.md` | 1–61 (frontmatter 1–3, body 5–61) | new |
| `corpus/QUALITY.md` | appended 12 lines at 559–570 (`## Criteria added — round 73` at 560; KQ120/121/122 at 568–570) | append |
| `corpus/README.md` | appended 15 lines at 1649–1663 (`## Coverage map — round 73 addition` at 1650; rows at 1662–1663) | append |
| `.ufo/waves/round-73/w1/SCR02Knowledge/pin-watch.out` | 8 | receipt |
| `.ufo/waves/round-73/w1/SCR02Knowledge/live-triple.out` | 8 | receipt |
| `.ufo/waves/round-73/w1/SCR02Knowledge/corpus-measure.out` | 14 | receipt |
| `.ufo/waves/round-73/w1/SCR02Knowledge/sources-state.out` | 14 | receipt |
| `.ufo/waves/round-73/w1/SCR02Knowledge/appends.out` | 11 | receipt |
| `.ufo/waves/round-73/w1/SCR02Knowledge/readme-append.out` | 18 | receipt |
| `.ufo/waves/round-73/w1/SCR02Knowledge/pycache-check.out` | 4 | receipt |
| `.ufo/waves/round-73/w1/SCR02Knowledge/entries-final.out` | 11 | receipt |
| `.ufo/waves/round-73/w1/SCR02Knowledge/source-rows.out` | 11 | receipt |
| `.ufo/waves/round-73/w1/SCR02Knowledge/entries-final2.out` | 8 | receipt |

Every `.out` starts with `# rev=bc9e30599b6c6133bb094f0e7abd1a9f512778ec`, read at write time.
No `__pycache__` and no `*.pyc` exist anywhere under `.ufo/waves/round-73` (`pycache-check.out`,
empty); every python command ran with `PYTHONDONTWRITEBYTECODE=1`.

## Commands and observed output

Reads (via the read tool, not re-typed here): `plans/round-73-claims.md` (all three claims,
Frontier, freeze control), `corpus/knowledge/pre-report-gate.md`,
`corpus/knowledge/receipt-tip-binding.md`, `corpus/knowledge/instrument-run-agreement.md:1-40`,
`corpus/QUALITY.md:540-558`, `considerthese/2026-10-26.md`, `tools/round72-round-scope.py:1-93`
and `:199-303`, `.ufo/waves/round-73/controls/build-survivors.py:60-220`,
`.ufo/waves/round-73/controls/score-survivors.py`, `tools/pin-watch.py:1-60`,
`/home/vgpnk/Projects/kimi-shokunin/skills/shokunin/protocol/CORPUS.md:1-80`.

Commands, in the order run:

1. `git -C L rev-parse master` → `bc9e30599b6c6133bb094f0e7abd1a9f512778ec`.
2. `git log --oneline -6` →
   `bc9e3059 round-73: freeze w1 wave spec (15 seats) and dispatch evidence` /
   `24bc96ad round-73: freeze three claims ... pre-freeze survivor controls` /
   `6e961996 round-72 verifier spot-check (integrator, hyaku): non-author admit/reject` /
   `db8b6fb0 round-72: final receipts at f3cd3623 and the L1 disclosure note (append-only)` /
   `f3cd3623 round-72: the record cites receipt files only (no directory or tsv citations)` /
   `82716f6c round-72: drop the extensionless collision-file citation from the Gate table`.
3. `ls -la tools/round73* tools/round72-round-scope.py` →
   `ls: cannot access 'tools/round73*': No such file or directory`;
   `-rwxr-xr-x 1 vgpnk vgpnk 27459 Nov  3 22:45 tools/round72-round-scope.py`.
   The round's three instruments do not exist at the tip; they are this wave's build seats.
4. `git status --porcelain -uall` (before my writes) → `?? .ufo/waves/round-73/w1.ready.dispatched`.
5. `grep -n 'host-identity block\|Round-[0-9]* host' PROVINCE.md | tail -20` → no match at first
   read; `sed -n '270,308p' PROVINCE.md` showed the `## Host re-derivation — round 71` section
   (`uname -s` → `Linux`, `uname -r` → `7.2.11-arch1-1`, 12 correction lines, 4 prose corrections).
6. `grep -n '^| Entry \|^|---\|^## ' corpus/README.md | tail -25` → last map section
   `## Coverage map — round 72 addition (2026-11-03)` at 1635, table at 1645.
7. `ls corpus/knowledge | tail -30` → 43 files at first read; `ls tools | grep round73` → no match,
   exit 1.
8. `cat .ufo/waves/round-73/measured/before/score-survivors-base.out` →
   `BASE_C1 c1_a5 exit=0 verdict=GREEN ROUND_SCOPE round=73 cases=3 findings=0` /
   `BASE_C1 c1_a6e exit=0 verdict=GREEN ROUND_SCOPE round=71 cases=3 findings=0` /
   `BASE_C1 c1_a7sub2 exit=0 verdict=GREEN ROUND_SCOPE round=73 cases=3 findings=0` /
   `SURVIVORS c1 base_green=3 v2_killed=0 v2=absent clean=n/a` /
   `BASE_C2 c2_b6 exit=0 verdict=GREEN RECEIPT_TIP_BINDING round=72 cited=1 bound=1 unbound=0
   shifted=0 stale=0` / `SURVIVORS c2 base_green=1 v2_killed=0 v2=absent` /
   `BASE_C3 c3_stale exit=0 verdict=GREEN block-exists-shortcut blocks=1` /
   `SURVIVORS c3 base_green=1 v2_killed=0 v2=absent` (header `# rev=6e961996...`).
9. `PYTHONDONTWRITEBYTECODE=1 python3 tools/pin-watch.py check --pins registry/engine-pins.tsv`
   → see §Pin-watch; wall time 1.35 s, exit 1.
10. `sed -n '640,645p' corpus/SOURCES.md` → round-46 re-verification prose;
    `grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md | sort -V | tail -4` →
    `S540 S541 S542 S543` (S543 last: `git-check-ignore`); `cat registry/engine-pins.tsv` → header
    plus `sglang ... v0.5.22 S474`, `vllm ... v0.32.0 S327 S363`, `llama.cpp ... b11755 S038`.
11. `sed -n '1,20p' corpus/QUALITY.md` → criteria table header (`| ID | Admit only when | Reject or
    limit when | Motivating lesson |`).
12. Live probes: `uname -s` → `Linux`; `uname -m` → `x86_64`; `grep '^ID=' /etc/os-release` →
    `ID=arch`; `uname -r` → `7.2.11-arch1-1` (`live-triple.out`, exit 0).
13. `grep -n 'S544\|S545' corpus/SOURCES.md` → no output, exit 1 (rows absent);
    `grep -n 'KQ12[0-9]' corpus/QUALITY.md` → no output (ids free);
    `grep -n 'host-identity block' PROVINCE.md` → no match at that moment.
14. Map measurement before appending (`PYTHONDONTWRITEBYTECODE=1 python3 -c ...`) →
    `knowledge_files 45` / `map_rows 39 distinct 36` / unindexed = the 7 pre-existing gaps plus my
    two new files (9 names).
15. Writes: two `write`s (entries), three `edit`s (QUALITY append, README append, one sentence in
    entry 1 citing the round-73 block), all listed above.
16. `sed -n '306,311p' PROVINCE.md` → the round-71 section tail and
    `Round-73 host-identity block (2026-11-03). Host triple: \`uname -s\` -> \`Linux\`; \`uname -m\`
    -> \`x86_64\`; \`/etc/os-release\` \`ID\` -> \`arch\`. Graded by
    \`tools/round73-province-host-drift.py\`; a host move is answered by appending a later block,
    never by editing this one.` (line 310; uncommitted worktree edit from seat EX03HostDrift,
    `git status` shows ` M PROVINCE.md`).
17. Map measurement after appending → `knowledge_files 45` / `map_rows 41 distinct 38` /
    unindexed = 7: `battery-execution-evidence.md`, `completion-request-plane.md`,
    `ollama-live-amendment-r61.md`, `ollama-live-lifecycle.md`, `process-bound-listener.md`,
    `sglang-docs-version-pinning-amendment-2026-10-23.md`, `sglang-docs-version-pinning.md`
    (`corpus-measure.out`).
18. `wc -l` on the two entries → `83` and `60` (`corpus-measure.out`).
19. `grep -c '^| KQ12[012] ' corpus/QUALITY.md` → `3` (`corpus-measure.out`).
20. `git -C L diff --numstat -- corpus/QUALITY.md corpus/README.md` →
    `12	0	corpus/QUALITY.md` / `15	0	corpus/README.md` — pure additions, no existing byte
    removed (`appends.out`).
21. `git status --porcelain -uall -- corpus/knowledge corpus/QUALITY.md corpus/README.md` →
    ` M corpus/QUALITY.md` / ` M corpus/README.md` /
    `?? corpus/knowledge/host-identity-drift-gate.md` /
    `?? corpus/knowledge/round-scope-survivor-cases.md` (`sources-state.out`).
22. `find .ufo/waves/round-73 \( -name __pycache__ -o -name '*.pyc' \)` → no output (`pycache-check.out`).
23. `grep -n 'S544\|S545' corpus/SOURCES.md` re-run at the end → no output, exit 1 (still absent).
    `grep -c 'S544\|S545' corpus/SOURCES.md` → `0` (`entries-final.out`).
24. `wc -l` on the two entries at the end → `83` / `61`; `sed -n '1p'` shows both source lines
    carry the `pending ... at admission` clause (`entries-final.out`).
25. After seat SCR01Sources landed the sources: `grep -n 'S544\|S545' corpus/SOURCES.md` → S544 at
    line 296, S545 at line 297; both 11-column rows are kind `docs`, tier `A`, status `mined`,
    accessed 2026-11-03, `uses`/quote columns carrying the located quotes below, `used-by` =
    `corpus/knowledge/host-identity-drift-gate.md` (S544) and
    `corpus/lessons/round-73.md, corpus/knowledge/round-scope-survivor-cases.md` (S545); registry
    row total `285` (`source-rows.out`). Quotes cited: S544 "`-s` prints the kernel name and `-m`
    the machine hardware name"; S545 "`all` makes the submodule never considered modified while it
    can still be staged".
26. Re-pointed both `source:` lines to S544/S545; `wc -l` after the edit → `83` / `61`
    (`entries-final2.out`). No S175 fallback remains in either entry.
27. `ls -l tools/round73*` (read-only, after the siblings' builds) → the three instruments exist in
    the worktree uncommitted (`round73-province-host-drift.py` 23:35,
    `round73-round-scope-cases.py` 23:37, `round73-receipt-claim-binding.py` 23:39) and are NOT in
    `bc9e3059`. `grep` of their `PREDICATE`/`CASE_ORDER`/block parser matches the grammar both
    entries describe. No counter was run.

## Pin-watch (proposal 4, run for real)

Command: `PYTHONDONTWRITEBYTECODE=1 python3 tools/pin-watch.py check --pins registry/engine-pins.tsv`
(live network via `git ls-remote`; 1.35 s; exit 1; receipt `pin-watch.out`):

```
engine=sglang pin=v0.5.22 newest=v0.5.23 newer=1 status=behind
engine=vllm pin=v0.32.0 newest=v0.33.0 newer=1 status=behind
engine=llama.cpp pin=b11755 newest=b12094 newer=269 status=behind
pins=3 current=0 behind=3 missing=0 error=0
```

Exit 1 is `behind`, not a failure to evaluate: `missing=0 error=0`. Per the tool's own limit a
`behind` line is a recheck trigger, not proof that pinned knowledge is wrong — the pinned docs
still describe the pinned release. Disposition: `considerthese/2026-10-26.md` proposal 4 is cited in
KQ122 and implemented in the form the round's plan directs (a QUALITY criterion plus this round's
real run), not as an edit to a daily file; no 2026-11-03 daily file was written. This is a
plan-directed narrowing of the proposal's wording, reported rather than silently applied.

## Gates and their state

- C1/C2/C3 counters (`tools/round73-*.py`) are absent at `bc9e3059` (command 3) but exist in the
  worktree uncommitted (command 27). I read their `PREDICATE`/`CASE_ORDER`/block parser against my
  entries; no run of them is claimed anywhere in my files, and both entries say so in `verified-at:`.
- C2 binding: `corpus/knowledge/**` and `corpus/QUALITY.md` are instrument inputs; `corpus/README.md`
  is a record path. Landing my two entries and the QUALITY rows changes instrument-input bytes, so
  **every receipt naming an earlier revision becomes `shifted` at a tip that carries them**.
  Commit order for L1: land the round's tools + these entries + the plan/PROVINCE/SOURCES edits
  first, then take the round's receipts naming that revision, then commit only record paths (wave
  receipts, lesson, SCORECARD, LOG, README). This is the `receipt-tip-binding.md` operational
  consequence, not a new rule.
- Pre-report gate arm 6 rewiring (`tools/pre-report-gate.py` → v2 counter) is seat EX04GateArm's;
  I touched neither `tools/` nor `SKILL.md`.

## Findings and limits (report, do not repair)

1. **S544 / S545 landed after the first write pass; both entries were re-pointed.** At admission the
   rows were pending (the S545 census item was blocked on `corpus/lessons/round-73.md`, which did
   not exist), so the first pass cited S175 and said "pending at admission"
   (`sources-state.out`, `entries-final.out`). Seat SCR01Sources then landed S544 and S545 at lines
   296-297; I edited both `source:` lines to cite the row ids with the rows' located quotes
   (`source-rows.out`, `entries-final2.out`). No S175 fallback remains in either entry.
2. **`used-by` for the gitmodules row — raised and resolved.** SCR01Sources added
   `corpus/knowledge/round-scope-survivor-cases.md` to S545's `used-by` alongside
   `corpus/lessons/round-73.md`; S544's `used-by` names `corpus/knowledge/host-identity-drift-gate.md`.
   That edit is SCR01's; I did not edit `corpus/SOURCES.md`.
3. **The round-73 block citation in entry 1** rests on `PROVINCE.md:310`, an uncommitted sibling
   edit at the time I wrote the sentence. The triple it records (`Linux` / `x86_64` / `arch`)
   matches my independent live probes, so the factual claim survives a PROVINCE.md revert; a line
   number does not. The entry gives `grep -n 'host-identity block' PROVINCE.md` as the locator
   rather than the line number.
4. **`recheck:` commands name tools that are uncommitted in the worktree.** At `bc9e3059` they
   exit `No such file or directory`; the three instruments appeared uncommitted by 23:39 and their
   `PREDICATE`/`CASE_ORDER`/block parser match both entries (read-only check). The recheck lines
   are forward-looking, and no counter run is claimed.
5. **README map gap shrinks from 9 to 7 files** (the two new entries are now indexed; the seven
   pre-existing gaps are named in the new section). Measured, with the command in the section.
6. **PROVINCE.md was modified by a sibling during my run** (` M PROVINCE.md`, round-73 block at 310)
   and `.ufo/waves/round-73/w1/EX03HostDrift*` and `CON01Overlap/` receipts appeared; those are
   not my writes. My write scope was exactly the table above.
7. **No receipt is claimed for a command I did not run.** `pin-watch.out` transcribes the live
   run's stdout and its `EXIT=1`; every other receipt was produced by its own invocation.

## Out of scope / not done

- No edit to `tools/**`, `SKILL.md`, `PROVINCE.md`, `corpus/SOURCES.md`, `plans/**`, `registry/**`,
  `SCORECARD.md`, `LOG.md`, `.ufo/state/**`, the fleet repo, or any sibling lane.
- No C1/C2/C3 counter run, no selftest, no lane-cleanliness verdict; those belong to their build
  and review seats.
- No daily-file pin-gap edit (proposal 4's literal surface); disposition is KQ122 + this round's
  real run, per the plan's Frontier step.

## Artifact paths

- Entries: `corpus/knowledge/host-identity-drift-gate.md`,
  `corpus/knowledge/round-scope-survivor-cases.md`.
- Appends: `corpus/README.md:1649-1663`, `corpus/QUALITY.md:559-570`.
- Receipts: `.ufo/waves/round-73/w1/SCR02Knowledge/{pin-watch,live-triple,corpus-measure,sources-state,appends,readme-append,pycache-check,entries-final,source-rows,entries-final2}.out`.
- This report: `.ufo/waves/round-73/w1/SCR02Knowledge.md`.
