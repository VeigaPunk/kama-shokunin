# ReviewGateRegistryCheck — round-28 wave-2 falsify report

Item: mined-mistake fix `tools/gate-registry-check.py` (occurrence check for the
"counter has no gate registry row" mistake class). Runs at base `4179301f` and tip
`e49b4cf` against the lane (read-only git). No tools installed (python3/git already
present; the tooling-directive channel was unused).

## 1. It fails at base and passes at the tip — verified, matches receipts

- Base `4179301f`: exit 1, `unregistered .ufo/waves/round-25/count-c2.py`,
  `unregistered .ufo/waves/round-27/count-c1.py`, `registered 2 unregistered 2`.
  Byte-identical to the cited receipt
  `.ufo/waves/round-28/w1/out/ExecGateRegistryCheck/base-4179301.out`.
- Tip `e49b4cf`: exit 0, `registered 5 unregistered 0` (all five tracked counters:
  round-17/count-verdicts, round-25/count-c2, round-26/count-c1,
  round-27/count-c1, round-28/count-c1 — my own `git ls-tree` listing agrees).
- Error paths exit 2 per receipts (bad-rev, notgit, scratch variants all exit 2).

## 2. Finding (main): the occurrence-only check is satisfiable by prose — it cannot
prove a registry row exists

The predicate is `path in SKILL.md_text` (substring, verbatim). Scratch demos under
`/fast/scratch/hyaku/kama-r28/w2/ReviewGateRegistryCheck/prose-demo` (git repo, one
tracked counter `.ufo/waves/round-99/count-x.py`):

| SKILL.md content | exit | output |
|---|---|---|
| prose sentence only: "We no longer run `.ufo/waves/round-99/count-x.py` in CI." | 0 | registered 1 unregistered 0 |
| mention only as substring of a longer token (`.ufo/waves/round-99/count-x.py.bak`) | 0 | registered 1 unregistered 0 |
| proper 5-column registry row | 0 | registered 1 unregistered 0 (identical output) |
| no mention at all | 1 | registered 0 unregistered 1 |

So a prose mention satisfies registration with **no registry row anywhere**; the tool
cannot tell a registry row from a prose mention (identical exit/output). In-lane proof:
at base, round-17/count-verdicts.py (SKILL.md:582, "Wave artifacts … are process
tools") and round-26/count-c1.py (SKILL.md:1073, "re-derivation command is python3 …")
were counted "registered" by prose alone — the base `registered 2` includes two counters
with no registry rows. The round-27 defect ("counter has no gate registry row") would go
undetected if the path string appeared anywhere in SKILL.md (e.g. "we disabled
`.ufo/waves/round-27/count-c1.py`"). The tool's own docstring and its SKILL.md row
(1219/1221) state this boundary, so it is documented — but the repair guarantees only
naming, not the registry-row requirement the defect names. A partial "fix" that merely
mentions the path passes.

## 3. Lesson mistake-row accuracy

- The repaired rows exist: `## Round-28 instrument registry (owner: kama)` (SKILL.md
  :1211) has rows for round-28 count-c1.py (:1218), round-27 count-c1.py retired
  (:1219), round-25 count-c2.py repaired (:1220), gate-registry-check.py (:1221),
  echo-recheck.py (:1222). Disposition matches.
- Inaccuracy 1: lesson repairs row 3 cites SKILL.md `## Local gate/probe registry —
  round-28 rows`; no such heading exists — the actual new section is `## Round-28
  instrument registry (owner: kama)`.
- Inaccuracy 2: the mistake row names only the round-27 counter, but at base the
  round-25/count-c2.py was equally unregistered (both in the base receipt and in my run);
  the disposition did repair both, so the text understates the base state.
- Otherwise the row is accurate (retire round-27, register round-28 counter + the two
  tools).

## Verdict / residual risk

Fix works as an occurrence gate (fails at base, passes at tip, exit map correct) but is
weak as the "no registry-row" falsifier: prose/substring mentions satisfy it, and at the
tip 2 of 5 registered counters (round-17, round-26) still have no registry row — the
pass verdict does not imply row completeness. Risk is bounded because the boundary is
documented in the tool docstring, its registry row, and the executor's
`proposed-skill-row.md` (which explicitly warns not to present it as grading row
completeness). No action needed if the boundary is accepted; if row existence matters,
the check would need a row-structure (table/columns) predicate.
