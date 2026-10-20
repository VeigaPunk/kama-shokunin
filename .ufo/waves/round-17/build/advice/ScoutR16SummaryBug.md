VERDICT: confirm — recount is 34 confirm / 40 partial / 0 refute / 5 nonconformant; the summary's 36/41/2 differs on exactly six named reports.

# Scope and method

Read-only recount of `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/falsify/advice/*.md` (79 files) at lane tip `cff9e62`, compared with `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/falsify/completion-summary.json`. Every file contains exactly one `^VERDICT:` line; five open with an H1 header and carry the verdict on line 3.

# Counts

- **Strict first line** (`head -n1`; nonconformant = no `VERDICT:` prefix): **34 confirm / 40 partial / 0 refute / 5 nonconformant** (79 total).
- **First `^VERDICT:` line anywhere** (header-tolerant): **36 confirm / 43 partial / 0 refute** (79 total).
- **Summary**: `completion-summary.json:22-25` — `"verdict_first_lines": { "confirm": 36, "partial": 41, "refute": 2 }`.
- No `^VERDICT:` line reads `refute`. Exactly two first-verdict lines carry the substring "refut" inside the rationale: `ReviewKnowledgeEntry.md:1` ("refuted") and `ScribeNumbersLedger.md:3` ("Refuted:").

Reproduction commands (run in the advice directory):

```
for f in *.md; do head -n1 "$f"; done \
  | sed -nE 's/^VERDICT: (confirm|partial|refute).*/\1/p' | sort | uniq -c
#      34 confirm
#      40 partial

grep -h -m1 '^VERDICT:' *.md \
  | sed -E 's/^VERDICT: ([a-z]+).*/\1/' | sort | uniq -c
#      36 confirm
#      43 partial

for f in *.md; do printf '%s\t%s\n' "$f" "$(grep -m1 '^VERDICT:' "$f")"; done | grep -ic refut
#       2
```

# Exact per-file classification differences (6 of 79)

| File | Strict first line | Summary | Evidence |
|---|---|---|---|
| `ConnectSiblingCollision.md` | nonconformant | **partial** | `:1` `# ConnectSiblingCollision — fleet-root misroot listing (read-only)`; `:3` `VERDICT: partial — untracked fleet-root files naming kama/round-16` |
| `ExecNoPythonFallback.md` | nonconformant | **confirm** | `:1` `# ExecNoPythonFallback — no-python3 fallback to FOREIGN_SERVICE`; `:3` `VERDICT: confirm — without python3, the probe keeps the old FOREIGN_SERVICE path` |
| `ReviewKnowledgeEntry.md` | **partial** | **refute** | `:1` `VERDICT: partial — … One material overclaim is refuted by the entry's own cited advice; … the rest confirms.` |
| `ReviewLesson.md` | nonconformant | **partial** | `:1` ``# ReviewLesson — `corpus/lessons/round-16.md` against receipts and round-15 routed defects``; `:3` `VERDICT: partial — every asserted measurement number reproduces` |
| `ScribeNumbersLedger.md` | nonconformant | **refute** | `:3` `VERDICT: partial — … Refuted: the "measured results appended/follow" pointers (no such entries exist)` |
| `ScribeReportWaves.md` | nonconformant | **confirm** | `:1` `# ScribeReportWaves — round 16 build-wave accounting`; `:3` `VERDICT: confirm — build-wave accounting` |

The other 73 reports agree: 34/34 strict confirms and 39/40 strict partials (the single moved strict partial is `ReviewKnowledgeEntry.md`).

The five nonconformant files, and their embedded verdicts the summary evidently read, are: `ConnectSiblingCollision.md:3` partial, `ExecNoPythonFallback.md:3` confirm, `ReviewLesson.md:3` partial, `ScribeNumbersLedger.md:3` partial, `ScribeReportWaves.md:3` confirm.

# How 36/41/2 arises (arithmetic identity)

- **confirm 36** = 34 strict first-line confirms + `ExecNoPythonFallback` + `ScribeReportWaves` (both header-first reports whose line-3 verdict is confirm).
- **partial 41** = 40 strict first-line partials − `ReviewKnowledgeEntry` (promoted to refute) + `ConnectSiblingCollision` + `ReviewLesson` (header-first reports with line-3 partial). `ScribeNumbersLedger` is header-first with line-3 partial but is promoted to refute, so contributes zero partial.
- **refute 2** = `ReviewKnowledgeEntry` + `ScribeNumbersLedger` — exactly the two reports whose first `^VERDICT:` line contains "refut".
- **nonconformant 5 → 0**: every header-first report was counted from a later `VERDICT:` line, so the summary has no nonconformant bucket at all.

[INFERENCE] The tally rule that reproduces 36/41/2 exactly on all 79 files is: take the **first `^VERDICT:` line anywhere in the file** (header-tolerant), then classify `refute` if that line contains the substring `refut`, otherwise use the leading token after `VERDICT:`. Simulated over the corpus this yields `{confirm: 36, partial: 41, refute: 2}`; no other simple rule tested matches (leading-token-only gives 36/43/0; whole-file keyword priority gives 18 refutes; refute-then-confirm-substring gives 39/38/2). Two independent defects are therefore present: (a) header tolerance contradicts the `verdict_first_lines` name, and (b) the refute-word override promotes verdict *rationale* text to the verdict itself.

[INFERENCE] No persisted producer was found: `grep -rn "verdict_first_lines"` over the lane and `/home/vgpnk/Projects/ufo-fsd-alpha/scripts` returns only the round-17 spec text, and `grep -rn "completion-summary"` over `ufo-fsd-alpha` returns nothing. The summary's own note says "terminal status from task completion notices", so it was hand-authored by L1; its only commit is `ccc4bb3`.

# Cross-reference

The round-16 verifier spotcheck already recorded the aggregate mismatch but not the per-file split or the refute mechanism: `corpus/lessons/round-16-verifier-spotcheck.md:59` — "A count of the committed `VERDICT:` lines gives 36 confirm / 43 partial / 0 refute, and 5 of 79 reports do not open with `VERDICT`." Its routed repair at `corpus/lessons/round-16-verifier-spotcheck.md:183` — "Correct `verdict_first_lines` by an appended note: 36/41/2 recorded vs 36/43/0 committed. Enforce the `VERDICT` first line (5/79 deviated) or report non-conformant seats."

# Limitations

- The producer mechanism is [INFERENCE]: no script, shell history, or completion notice is available inside the privacy bounds (session stores and `~/.omp` are out of scope), so an L1 judgment call cannot be excluded. The six-file delta and the exact 36/41/2 reproduction are observed either way.
- Observed after cleanup, not mine and not touched: `/home/vgpnk/Projects/shokunin/.ufo/waves/round-17/build/advice/RevengerS041Edit.md` (first line `VERDICT: confirm — S041's …`) sits at the fleet root, the same relative-path misroot class reported in round 16.
- Final tree state: only this report was added to the lane; no measurement, gate, or server was run. One transient misplaced copy created at the fleet root by the report writer's relative path (`.ufo/waves/round-17/build/advice/ScoutR16SummaryBug.md`) was deleted, and its sole-created empty directories removed. Installs: none.
