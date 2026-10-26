# K1Binding — attack on the declaration binding rule (C1, append-only-audit v3)

Verdict: the binding rule is under-constrained in four ways — a self-declaration loophole (any line inside a file matching a wildcard pattern binds the whole pattern), substring token matching (`log` inside `chronological`/`catalog`), a fixed four-string negation list that real denials escape, and no acceptance of `appended only`/split declarations. The lane's own `corpus/lessons/*.md` row binds today only through the loophole: its declared anchor is the sentence tail `are append-only.` in `corpus/lessons/round-23.md:100`, a local statement about round-23.md's own corrections region that never names the family. A stricter rule (word-bounded phrase and token, negation window, exact self-declaration only) flips the frozen tool's exit 0 → 1 on exactly that row (bad_declarations=1, all else unchanged: 89 files, 5 events, regressed 0, ungraded_lines 89), passes all 27 selftest cases, and is satisfiable today with an existing family-naming line (`corpus/lessons/round-42-verifier-spotcheck.md:20` → exit 0).

Scope: `binds()` in `tools/append-only-audit.py:190-199` and `tools/round48-append-audit-v3-check.py:226-233` (identical logic; NEG/NEGATIONS tuples at auditit:119 / check:147). All runs against a scratch clone `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` at `380bcdff9c8af06997c482f6eb03db926a794a2b` (read-only `git show`). Counters/tools untouched; the stricter rule is a probe wrapper that monkeypatches `binds` into unmodified copies of both frozen files.

## 1. Self-declaration loophole: any line inside a matched file binds a wildcard pattern

`binds` returns True when `fnmatch.fnmatchcase(decl_path, pattern)` — for pattern `corpus/lessons/*.md`, any line in any lesson file that merely contains `append-only`/`append only` (non-negation) binds the whole family row.

- The lane's actual anchor is `corpus/lessons/round-23.md:100`, whose whole text is `are append-only.` — the tail of the sentence ending at lines 99-100 of that file: `…Everything above this section was written at `245a37f6` and stays unchanged; corrections below are append-only.` That declares **round-23.md's own corrections region** append-only, not the lessons family; it contains no family token (no `lessons`, no `corpus/lessons`). It binds solely because its file matches the pattern. `binds("corpus/lessons/*.md", "corpus/lessons/round-23.md")` = True (verified).
- 105 lines inside `corpus/lessons/*.md` contain the phrase at this commit; any of them is a valid anchor for the whole pattern under the current rule. Examples: `corpus/lessons/round-16-verifier-spotcheck.md:41` (a SCORECARD observation), `corpus/lessons/round-17-verifier-spotcheck.md:157` (a denial — see §3), `corpus/lessons/round-46.md:40` (a C2 defect note).
- No genuine family-level declaration exists in live (non-`.ufo`) docs: a search for a word-bounded `lessons` + phrase returns only the verification rows inside lesson files themselves (e.g. `corpus/lessons/round-42-verifier-spotcheck.md:20`) and LOG/SCORECARD prose.

## 2. Substring token matching: a token inside an unrelated word binds

`binds` requires `tok in low` (substring). `log` ⊂ `chronological`/`catalog`/`logic`/`prologue`; `sources` ⊂ `resources`; `quality` ⊂ `equality`; `scorecard` ⊂ `scorecards`.

- Concrete, verified: `tools/kama-probe.sh:1079` begins `printf '# Append-only; one line per row-field change between snapshots, in\n# chronological order. …`. It never mentions LOG.md, yet `binds(text, "LOG.md", "tools/kama-probe.sh")` = True — `log` rides inside `chronological`.
- Surface: 95 tree lines pair the phrase with a token-substring word (5 in live docs: `tools/kama-probe.sh:1079`, `LOG.md:2312`, `corpus/QUALITY.md:72`, `corpus/lessons/round-12-verifier-spotcheck.md:151`, `corpus/lessons/round-46.md:40`, all via `log`/`quality` inside `chronological`/`equality`). Under the current rule 477 lines bind the LOG.md row, 1588 the SOURCES row, etc. (full counts in `scan-summary.txt`).

## 3. Negation evasion: only four fixed substrings are denied

The negation list is exactly `not append-only`, `not append only`, `no longer append`, `never append-only`. `not an append-only`, `isn't append-only`, `never been append-only` all escape.

- Verified: `corpus/lessons/round-17-verifier-spotcheck.md:157` = `  is not an append-only file.` — an outright denial — `binds("corpus/lessons/*.md", …)` = True (double bug: also §1). The lane itself uses this line for the opposite purpose (`corpus/lessons/round-17-verifier-spotcheck.md:157`; `.ufo/waves/round-46/w1/out/Rev2Decl.md:31-32`).
- 57 tree lines have a negation word within 24 chars before the phrase and still bind.

## 4. Missed declarations: forms the rule does not bind

- `appended only`/`appended-only`: 34 instances. Verified: `SCORECARD.md:477` `Supplemental outside D2 historical table clarification is appended only in` → `binds("SCORECARD.md")` = False, though it genuinely claims an append-only property of SCORECARD.md. The lane's own criterion KQ67 (`corpus/QUALITY.md:387`) counts `appended only` statements as append-only claims.
- Split across lines: the lessons row's declaration is split (referent on line 99, phrase on line 100); a single-line pointer cannot capture it — the root cause of §1's weak anchor. No `append-` / `only` hard line break found elsewhere.

## 5. Per-row contract audit at 380bcdff (all 9 rows)

| row | declared_at (line text, truncated) | region pointer | truly declares for that path? | current | strict |
|---|---|---|---|---|---|
| LOG.md | README.md:16 `- \`LOG.md\` — append-only round log: …` | * | yes — names LOG.md | ✓ | ✓ |
| SCORECARD.md | corpus/README.md:761 `append-only (SCORECARD.md, LOG.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md)` | exempt@SCORECARD.md:6 (names all five titles + "re-derived" — verified) | yes | ✓ | ✓ |
| corpus/QUALITY.md | corpus/README.md:761 (same line) | * | yes | ✓ | ✓ |
| corpus/README.md | corpus/README.md:761 (same line, self-file) | * | yes | ✓ | ✓ |
| corpus/SOURCES.md | SKILL.md:578 `\| SOURCES append-only guard \| gate: \`python3 tools/sources-append-only.py …\` …` | * | borderline — names both words but states a guard tool, not the norm; no better live line exists | ✓ | ✓ |
| corpus/lessons/*.md | corpus/lessons/round-23.md:100 `are append-only.` | * | **no** — sentence tail declaring round-23.md's own corrections region; no family token; binds only via §1 | ✓ | ✗ |
| registry/history/DELTA.md | itself:3 `# Append-only; one line per row-field change …` | * | yes — self-declaration | ✓ | ✓ |
| registry/report-landing-errata.tsv | itself:1 `# Append-only corrections for defects …` | * | yes — self-declaration | ✓ | ✓ |
| corpus/knowledge/consumer-registry.md | itself:30 `## Errata — … (append-only; rows below keep their round-1 text)` | only=## Errata@itself:30 (same line, contains "Errata") | yes — section-scoped self-declaration | ✓ | ✓ |

## 6. Stricter rule and its effect on the lane

Proposed `binds` (full code: `out/K1Binding/strict_binds.py`; same signature):
1. phrase must be word-bounded: `(?<![a-z0-9])append[- ]only(?![a-z0-9])`;
2. reject the four NEG substrings anywhere, and any negation word within 24 chars before the phrase (`not|never|no longer|isn't|aren't|wasn't|weren't|hasn't|don't|doesn't`);
3. exact (wildcard-free) self-declaration kept: a line inside the very file it declares binds without naming the token;
4. otherwise the row's token must appear as a whole word (`(?<![a-z0-9])<tok>(?![a-z0-9])`) — closes §1 and §2;
5. optional extension (not in the probe): accept `appended only`/`appended-only` as positive phrase forms, closing §4.

Effect, measured by running the strict monkeypatched copies of the frozen tools on the lane at 380bcdff:

- `python3 out/aoa_strict.py --repo <clone> --to 380bcdff --json` → exit 1; declarations: exactly one bad — `corpus/lessons/*.md` `declared_at corpus/lessons/round-23.md:100 does not say append-only for corpus/lessons/*.md`; summary otherwise identical (`files 89, events 5, restored 5, partial 0, unrestored 0, ungraded_lines 89, regressed 0, vanished 0`).
- The frozen C1 counter's own contract leg agrees: `contract: corpus/lessons/*.md: declared_at corpus/lessons/round-23.md:100 does not bind`.
- Standard selftest under the strict rule: `AOA_SELFTEST pass=27 fail=0`, exit 0 — the tightened rule does not break the intended positive/negative fixtures.
- Amending only the lessons row's `declared_at` to the existing family-naming line `corpus/lessons/round-42-verifier-spotcheck.md:20` (`| Append-only | \`git diff --numstat … -- corpus/SOURCES.md LOG.md corpus/lessons/round-38.md\` …`): exit 0, bad_declarations=0, files/events/regressed unchanged (`out/contract-amended.tsv`, `out/strict-tool-amended.json`). A stricter rule is therefore satisfiable today without new text; preferably a dedicated family declaration should be added (e.g. in PROTOCOL.md or README).

## Witnesses
- `out/K1Binding/strict-tool.json` — strict run, exit 1, one bad declaration.
- `out/K1Binding/strict-tool-amended.json`, `out/K1Binding/contract-amended.tsv` — amended anchor, exit 0.
- `out/K1Binding/counterexamples.txt` — all five verified lines with both rules' verdicts.
- `out/K1Binding/scan-summary.txt` — tree-wide counts (5430 phrase lines, per-row bind counts, 95 coincidence, 105 lesson anchors, 34 `appended only`).
- `out/K1Binding/strict_binds.py` — proposed rule.
