# CriticC2Outside

Axis: coverage. Attacked object: `tools/round35-coverage-audit.py` (`ff5318494c01cd545455d386f65b9dcfdd64d361d4e94e98454081a7cb55d013`) as the C2 kill "a name outside the round-35 heading must not pass." The tool was not edited. The predicate was not retargeted. MISSION.md was not edited; axis authority was not touched.

**Yes. A junk mention of `knowledge/endpoint-health-probe-conventions.md` outside the heading line can meet the target** (`named 1 file_exists 1 cited_row 1 met True`). The selftest fixture cannot, and its `pass=1` does not prove the kill.

## Selftest output

Command:

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round35-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --selftest
```

stdout (exit 0):

```
SELFTEST base_met=False junk_met=False pass=1
base named 0 file_exists 0 cited_row 0 met False
```

Same two lines as `.ufo/waves/round-35/controls/c2-selftest.out`. The script does not print the junk `named` / `file_exists` / `cited_row` line.

## Counterexample

`block_names` (lines 47-52) opens on the first substring hit of `HEADING` and closes only on the next `\n## `. It does not require the heading to be a line. The selftest (lines 113-118) appends the entry path to base `719655f12517a9ce6b1a5ca44316897fed8420b0:corpus/README.md`, which does not contain that heading, so the append is never scanned. `outside_ok` is the heading-absent short-circuit, the same reason `base["named"] == 0`.

Strongest executed false pass: the only copy of the entry path sits outside the real heading line, the other two conjuncts are already true, and `met` is True.

Fixture (heading constant taken from the module, U+2014):

```
The report quoted ## Coverage map — round 35 addition but that section was absent.
see knowledge/endpoint-health-probe-conventions.md outside the real heading

## Coverage map — round 35 addition

empty real block
```

Scored with the same synthetic entry and sources the selftest uses (`source: S327\n`, `| S327 | x |\n`):

```
named=1 file_exists=1 cited_row=1 met=True
```

Counted window, from `split(HEADING, 1)[1].split("\n## ", 1)[0]`:

```
 but that section was absent.
see knowledge/endpoint-health-probe-conventions.md outside the real heading
```

The real heading line is the closer, not the opener. The path never enters that section.

Same `met=True` for a name under a different heading that merely starts with the required string (`## Coverage map — round 35 addition rejected`), under a blockquoted or 4-space copy of the heading line, after a following `# ` section, and after a setext `----` section. In each case `file_exists` and `cited_row` were already 1. The kill fails in `named` alone.

The narrow case the selftest comment describes does hold, and is not what `pass=1` ran: path only after a later `\n## `, or only before a real first occurrence of the heading string, scores `named=0 met=False`. A name under base `## Coverage map` (line 25) with an empty round-35 heading appended also scores `named=0 met=False`. Those are not the hole.

## Evidence

- Base `git show 719655f12517a9ce6b1a5ca44316897fed8420b0:corpus/README.md`: `HEADING` count 0, `ENTRY` count 0, 529 lines, one ATX h1 at line 1, every later section an ATX h2. Selftest junk detail from the same `score()` the script calls: `named=0 file_exists=1 cited_row=1 met=False`. One `named` flip from meeting the target. The printed `junk_met=False` hides that.
- Positive control, path once under the exact heading and before `## Later`: `named=1 met=True`. The counter is not stuck false.
- `inside` plus a second mention after `## Later`: `named=1 met=True`. An extra outside mention does not keep `met` false when the block itself names the path once. That matches the predicate (the block names the file). It is not the defect.
- Probes imported the file with `PYTHONDONTWRITEBYTECODE=1`. No `__pycache__` under `tools/`. No git mutation. No tool edit.

## Impacted axes

- Coverage (C2). A tip whose README quotes the heading string, or uses a longer heading with that prefix, can reach `met True` without the round-35 block naming the entry. That is a false coverage admit. The frozen target is `named 1 file_exists 1 cited_row 1 met True` only when the block names the file.
- Kill fidelity. Preregistration kill and the docstring line "A name outside the heading does not count" are not what `--selftest` exercises.
- Selftest soundness. `pass=1` is premature saturation: the boundary the kill names does not exist in the fixture.

Not impacted: the predicate text. It matches the preregistration. Do not edit it. C1 and MISSION.md:29 were not touched.

## Tradeoff the correction must not take

Do not poison `met` when the path also appears after the closer. The predicate does not require exclusivity. Round-style coverage blocks name the entry in the addition section; a later disposition mention must not flip a true block to false. `inside_and_outside` staying `met True` is the hold.

Do not add a setext closer in this patch. A name after `----` does meet the target today, but a `---` / `----` closer false-closes on thematic breaks. This README's section breaks are ATX. Leave setext as a residual, with a negative fixture if a later patch adds it.

Do not parse fences. A fenced `\n## ` already closes the window early (`named=0` for a later in-section name). A line-anchored ATX closer has the same limit. A markdown parser is not the smallest fix.

## Smallest safe correction

In `block_names` only, plus selftest fixtures. No predicate change. No exclusivity change.

Open on a full line, 0-3 leading spaces (CommonMark ATX), optional closing hashes, using the existing `HEADING` constant so the em dash cannot drift:

```python
_OPEN = re.compile(r"^ {0,3}" + re.escape(HEADING) + r"[ \t]*(?:#+[ \t]*)?$")
_CLOSE = re.compile(r"^ {0,3}#{1,2} ")
```

Count `ENTRY` only on lines after that open line and before the next line `_CLOSE` matches. The space after `#{1,2}` is load-bearing: `### ` must stay inside the block. Do not keep `HEADING not in readme` or `split(HEADING, 1)`.

Selftest, as direct `score()` fixtures, not appends to a heading-less base:

1. Exact heading, path only after the next `## ` line, entry cites `S327`, sources row `| S327 |` → `named 0 met False`.
2. Prose or prefix occurrence of the heading string with the path in that false window, exact heading line empty → `named 0 met False`.
3. Path once under the exact heading, before the next `## ` → `named 1` (and `met True` with the same entry/sources). Without this, a counter that always returns 0 still passes.
4. Keep the base check (`named 0 file_exists 0 met False` at `719655f…`). Print the junk `emit` line, not only `junk_met`.

Expected after the patch: fixture 1 and 2 stay false; fixture 3 stays the only `named 1`. The current append-to-base junk check may remain, but it must not be the sole outside check.

This seat did not apply the patch.
