VERDICT: confirm — 36/41/2 reproduces exactly as keyword-priority over the first VERDICT-bearing line, not the first line; the true first-line count is 34/40/0 + 5 nonconformant.

# RevengerSummaryProducer — how round-16 falsify's `verdict_first_lines` got 36/41/2

Lane root `/home/vgpnk/Projects/shokunin/kama-shokunin`. Read-only seat: no lane file edited, no port bound, no measurement command from the L1 reservation list run. No installs.

## Answer in one paragraph

`completion-summary.json` has no producer script. Its `verdict_first_lines` value is a hand/inline-shell count that relaxed a first-line count in three independent ways at once: **line scope** (first line *containing* `VERDICT`, anywhere in the file), **token scope** (any `confirm|partial|refute` substring in that whole line, not the token after `VERDICT:`), and **priority** (`refute` before `partial` before `confirm`, case-folded). Of six plausible parsing variants I tested, exactly one reproduces all three cells (36/41/2): that combination. The arithmetic is fully accounted for: 36 confirm declarations stay 36; 43 partial declarations lose 2 that narrate "refuted"/"Refuted" and become 41; those 2 become the 2 refutes. The total stays 79, which is why it survived review.

## 1. No script produced it (what I searched)

- `.ufo/waves/round-16/falsify/completion-summary.json:22-25` — `"verdict_first_lines": { "confirm": 36, "partial": 41, "refute": 2 }`.
- `grep -rIl 'completion-summary'` over the lane, `/home/vgpnk/Projects/shokunin` and `/home/vgpnk/Projects/ufo-fsd-alpha` (excluding `.ufo` payloads, session stores, `.git`, `.jj`, `node_modules`) returns only two prose hits: `corpus/lessons/round-15-verifier-spotcheck.md` and `corpus/lessons/round-16-verifier-spotcheck.md`. No code.
- `.ufo/waves/round-16/falsify/` contains only `make_spec.py` plus JSON/text data. The round tree's complete script inventory is `measure.py`, `dispatch-provenance.py`, `stale-statements.py` (round-16 root), `build/make_spec.py` and `falsify/make_spec.py`. None mentions or writes the summary (`grep -l 'completion-summary'` over all five → no output).
- The wave runner has no summary writer: `grep -n 'summary' /home/vgpnk/Projects/ufo-fsd-alpha/scripts/ufo-swarm-wave.mjs` → no output.
- Round-15 is a different schema, proving the field is round-16 bespoke: `.ufo/waves/round-15/falsify/completion-summary.json` keys are `['spawns','completed','failed','no_replacements','basis','used_validation','preliminary_validation']`, no verdict tally.
- File ordering confirms post-wave authorship: newest advice `.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md` mtime `11:11:54`, summary mtime `11:14:10`, commit `ccc4bb3` at `11:15:00`.
- Every other field is exactly derivable (I recomputed them): `falsify/spec.json` has 79 items whose role histogram is byte-equal to `completion-summary.json:4-15`; `advice/*.md` is 79 files 1:1 with item names (`missing: [] extra: []`); the 80th directory entry is `advice/swarm-registry.json:2` `"schema": "ufo-swarm-registry-v1"`, correctly excluded.

[INFERENCE] L1 typed the verdict tally by hand or in an inline shell loop after the last seat landed, then wrote the prose `misroots`/`note` fields. No artifact records the literal command; the mechanism below is established by exact numerical reproduction, not by recovering the command text.

## 2. The mechanism, reproduced end to end

Run from `.ufo/waves/round-16/falsify/advice`:

```sh
for f in *.md; do
  l=$(grep -m1 -i 'VERDICT' "$f" | tr '[:upper:]' '[:lower:]')
  case "$l" in
    *refute*)  echo refute  ;;
    *partial*) echo partial ;;
    *confirm*) echo confirm ;;
    *)         echo other   ;;
  esac
done | sort | uniq -c
```

Observed output (I ran it):

```
     36 confirm
     41 partial
      2 refute
```

Decomposition, from the 79 declaration lines (`grep -h '^VERDICT:' *.md`):

- Declaration histogram: `36 confirm`, `43 partial`, `0 refute` (no `refute` token exists anywhere in a verdict declaration).
- Of the 43 partial declarations, 2 also contain the substring `refut` → priority sends them to `refute`: 43 − 2 = **41 partial**, **2 refute**.
- 40 declaration lines contain the substring `confirm`, but the 4 extras are partial declarations (no declaration line declares `refute`) absorbed by line priority, so `confirm` stays **36**.
- 36 + 41 + 2 = 79 = `dispatched` and `advice_reports` (`.ufo/waves/round-16/falsify/completion-summary.json:3,20`).

Variant search (same 79 files, Python, to isolate the rule): `first non-empty line + token regex` → 34/40/0 + 5 nonconformant; `first non-empty line + keyword priority` → 34/39/1 + 5 nonconformant; `first VERDICT line + token regex` → 36/43/0; `first VERDICT line + case-sensitive priority` → 36/42/1; `first VERDICT line + case-insensitive priority` → **36/41/2 (unique match)**. Case folding is required: `ScribeNumbersLedger.md` capitalises "Refuted".

## 3. Why it differs from a first-line count — three separable defects

### D1 — Line scope: the count never required the verdict to be the first line

Five of 79 reports open with a `#` title and put `VERDICT:` on line 3. The recorded method classified them instead of flagging them. A first-line counter must report them as nonconformant.

| file (`.ufo/waves/round-16/falsify/advice/`) | line | declared token |
|---|---:|---|
| `ConnectSiblingCollision.md` | 3 | partial |
| `ExecNoPythonFallback.md` | 3 | confirm |
| `ReviewLesson.md` | 3 | partial |
| `ScribeNumbersLedger.md` | 3 | partial |
| `ScribeReportWaves.md` | 3 | confirm |

Evidence: `ScribeNumbersLedger.md:1` `"# ScribeNumbersLedger — round-16 number ledger (falsify wave)"`, then `ScribeNumbersLedger.md:3` `"VERDICT: partial — round-16 numbers across lesson, SKILL §Round-16, SCORECARD, LOG"`. Net: +2 confirm, +3 partial — the exact +2/+3 compensation that turns 34/40 into 36/43 and hides all five format violations.

### D2 — Token scope: classification scanned the whole sentence

Only two of the 79 declaration lines contain `refut` (18 reports use the word somewhere, which is why a whole-file keyword scan yields 16 refutes); both are `VERDICT: partial` declarations whose prose discusses refutation:

- `ReviewKnowledgeEntry.md:1` — `"One material overclaim is refuted by the entry's own cited advice"` → recorded as `refute`.
- `ScribeNumbersLedger.md:3` — `"Refuted: the \"measured results appended/follow\" pointers (no such entries exist)"` → recorded as `refute`.

A positional parser (`^VERDICT:\s*(confirm|partial|refute|n/a)`) returns `partial` for both; 0 refutes exist in the wave.

### D3 — Priority and case folding: `refute` wins even when it is not the verdict

The `case`/`elif` chain tests `refute` first, on a lowercased copy of the line. That makes any narrative use of "refute"/"refuted"/"Refuted" override the declared token, and it is why `confirm` does not inflate despite 40 declaration lines containing "confirm": those lines match `partial` (or `refute`) earlier in the chain.

## 4. Three internally consistent counts, all summing to 79

| Method | confirm | partial | refute | nonconformant |
|---|---:|---:|---:|---:|
| Strict first non-empty line, positional token | 34 | 40 | 0 | 5 |
| First `VERDICT`-containing line, positional token (what the lesson calls "committed VERDICT lines") | 36 | 43 | 0 | 0 |
| First `VERDICT`-containing line, keyword priority, case-folded (**recorded**) | 36 | 41 | 2 | 0 |

The three rows are permutations, not losses — every row totals 79. A "does it sum to dispatched?" check cannot distinguish them; only a per-file recount can.

## 5. The defect is already propagating into round-17

- `corpus/lessons/round-16-verifier-spotcheck.md:59` — `"A count of the committed \`VERDICT:\` lines gives 36 confirm / 43 partial / 0 refute"`. That is the *relaxed-line* count, yet the same sentence reports `"5 of 79 reports do not open with \`VERDICT\`"`; 36 + 43 + 5 = 84 > 79, so the sentence cannot be one classification scheme. The wording needs "first line containing `VERDICT`" for 36/43/0 and "first non-empty line" for 34/40/0 + 5.
- `corpus/lessons/round-16-verifier-spotcheck.md:183` — `"Correct \`verdict_first_lines\` by an appended note: 36/41/2 recorded vs 36/43/0 committed"`, plus `"Enforce the \`VERDICT\` first line (5/79 deviated)"`. Same conflation.
- `.ufo/waves/round-17/build/make_spec.py:118` — `"read the first non-empty line; classify \`VERDICT: confirm|partial|refute|n/a\`"` then `"expected 36/43/0 + 5 nonconformant for falsify per the outside check"`. **This spec is self-contradictory.** A correct first-line parser cannot emit 36/43/0 + 5; it will emit 34/40/0 + 5. An executor who trusts the expected value will either (a) relax the parser to scan anywhere — reintroducing D1 — or (b) report a false bug in their own tool. The same text is dispatched verbatim in `.ufo/waves/round-17/build/spec.json:49`.

Recommended correction for both lesson and spec: strict expectation is **34 confirm / 40 partial / 0 refute / 5 nonconformant** (`ConnectSiblingCollision`, `ExecNoPythonFallback`, `ReviewLesson`, `ScribeNumbersLedger`, `ScribeReportWaves`). Keep **36/43/0** documented as the relaxed-line variant and **36/41/2** as the keyword-priority artifact, each labelled, so all three are reproducible on demand and only one is load-bearing.

## 6. Mechanism for the lesson (paste-ready)

> **How round-16 falsify's `verdict_first_lines` was mis-produced.** The summary is hand-authored; no script wrote it. Its tally was taken by grepping the first line *containing* `VERDICT` in each report, lowercasing that whole line, and testing substrings in the order `refute` → `partial` → `confirm`. Two relaxations compound: (a) five reports put `VERDICT:` on line 3 behind a `#` title and were silently counted instead of reported nonconformant; (b) two `VERDICT: partial` reports use "refuted"/"Refuted" in the same sentence, so the keyword scan reclassified them as `refute`. Result 36/41/2 (sum 79, so it looked complete). A positional first-line parse gives 34/40/0 plus 5 nonconformant; a positional parse of the first `VERDICT`-bearing line gives 36/43/0. Any verdict tally must read the first non-empty line, take the token positionally after `VERDICT:`, keep `nonconformant` as a first-class bucket, and assert both `sum(counts)+nonconformant == dispatched` **and** a per-file classification list — a totals-only check cannot see this class of error.

## Limitations

- The literal command L1 ran is not recorded anywhere I can read: the summary landed inside `ccc4bb3` (`round-16: record measured C1/C2 results, falsify-wave dispositions and live loading capture`) with no dedicated commit or log. The mechanism is proven by exact three-cell reproduction and a six-variant uniqueness search, not by recovering the command bytes. [INFERENCE]
- An LLM-eyeballed count could in principle land on the same three numbers, but it would have to reproduce exactly the two prose-word flips and the five line-3 inclusions; the keyword-priority rule explains all three cells with one rule. [INFERENCE]
- I did not read `.ufo/interactive-sessions/`, `~/.omp/` (beyond `RULES.md`), `~/.config/`, or any transcript; privacy bounds respected. Every recursive grep carried `--exclude-dir=interactive-sessions --exclude-dir=.git --exclude-dir=.jj`.
- `build/advice` is 0/81 conformant for an unrelated reason and is not evidence against this mechanism: `.ufo/waves/round-16/build/make_spec.py:24` asks only for `"Report: concise findings with path:line or URL+quote evidence, limitations, and any install."`, never a `VERDICT` line, and `.ufo/waves/round-16/build/completion-summary.json` correspondingly has no `verdict_first_lines` key. The falsify spec did mandate it: `.ufo/waves/round-16/falsify/make_spec.py:24` `"Report: first line \`VERDICT: confirm|refute|partial — <what you attacked>\`"`.

## Installs

None. No packages, binaries, or upgrades were installed or changed.
