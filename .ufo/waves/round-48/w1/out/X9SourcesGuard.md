# X9SourcesGuard — round-48 D8: `tools/sources-append-only.py` blind since round 45

**Verdict: reproduced and root-caused.** The guard's whole-blob "row-like line" scan (`tools/sources-append-only.py:76` `ROWLIKE_RE`, used at `:227-233`) refuses *any* table row whose first cell is an S-id anywhere outside the `## Registry` section. The round-45 re-verification table (`corpus/SOURCES.md:520-530` at `380bcdff`, first landed by `052cb1e9`) is the first such table, so every SOURCES transition since the round-45 freeze has exited 2 and rule 2 has graded nothing for rounds 45, 46, 47 and 48. A proposed fix (`proposed.diff`, 5 hunks, 143 lines) narrows the outside-section scan to runs that are genuinely registry-shaped: patched copy passes `45/45` selftest (original `42/42`), grades r45→r46→r47→r48 at exit 0 naming the rows each round appended, and still grades a deleted registry row / an edited immutable cell at exit 1 on the real corpus text.

## 1. Reproduction (lane clone, read-only)

`S=/fast/scratch/hyaku/kama-r48/X9SourcesGuard`, `git clone --shared <lane> $S/lane`, tip of measurement `380bcdff9c8af06997c482f6eb03db926a794a2b`; the tool is at lane commit `380bcdff` blob `cd26e6f7b9058b8454395a68c361f81c99d5a592`, working-tree sha256 `4d7868564226b6caa5957e9d7f4f8910a1c459ec26462a52d42e802be6079c2d` (byte-identical at lane HEAD `b85783e8`).

```
python3 tools/sources-append-only.py --repo lane --from 0163fea2 --to 172b8ad0   # r45 -> r46
  error: 0163fea2:corpus/SOURCES.md:514: row-like line outside the parsed registry table; refusing to drop it   exit 2
python3 tools/sources-append-only.py --repo lane --from 172b8ad0 --to 33e00582   # r46 -> r47
  error: 172b8ad0:corpus/SOURCES.md:516: ...                                                                       exit 2
python3 tools/sources-append-only.py --repo lane --from 33e00582 --to 380bcdff   # r47 -> r48
  error: 33e00582:corpus/SOURCES.md:520: ...                                                                       exit 2
python3 tools/sources-append-only.py --repo lane --from d48e8cc3 --to 6b8ccfb3   # last graded (r44 spot-check)
  no append-only violations                                                                                        exit 0
```

Boundary of the break, exactly:

```
python3 tools/sources-append-only.py --repo lane --from 1641aa07^ --to 1641aa07   # r44 closure -> r45 freeze
  no append-only violations                                       exit 0
python3 tools/sources-append-only.py --repo lane --from 1641aa07  --to 052cb1e9   # r45 freeze -> r45 C1 evidence
  error: 052cb1e9:corpus/SOURCES.md:514: row-like line outside the parsed registry table; refusing to drop it  exit 2
```

`git -C lane log --oneline -S'| `S010` | ollama' -- corpus/SOURCES.md` → `052cb1e9 round-45: C1 evidence (…) SOURCES round-45 section`. So the break is caused by the round-45 build appending a re-verification section with an S-keyed table; it is not a change to the guard (`ROWLIKE_RE` itself dates from `c6dc46fa`, round 18 — it had simply never met an S-keyed non-registry table before).

Every SOURCES.md commit inside r45..r48 (5 commits, `6b8ccfb3` → `380bcdff`), pairwise, original tool: **5/5 exit 2** (`sweep-orig.txt`).

## 2. Parser cause — file:line

- `tools/sources-append-only.py:76`
  `ROWLIKE_RE = re.compile(r"^\s*\|?\s*[`*_\[]*[Ss][0-9]+[`*_\]]*\s*\|")`
  — "what a reader takes for a registry row": an S-number first cell, leading pipe optional.
- `tools/sources-append-only.py:227-233` (inside `parse_registry`)
  ```python
  for idx, line in enumerate(lines):
      if idx not in row_lines and ROWLIKE_RE.match(line):
          raise ParseError(f"{label}:{idx + 1}: row-like line outside the parsed registry table; …")
  ```
  — `row_lines` holds only the graded data rows of the `## Registry` section (lines 10-247 of the `380bcdff` blob, heading at line 9, level 2). The scan itself is whole-blob, so the module docstring's rule ("a row-like line … **anywhere in the blob** that was not read as a registry row are parse errors") makes every re-verification table appended by the lane a hard exit 2.
- Offending lines, counted (`row-like-lines.txt`): **27** row-like lines outside the section at `380bcdff` — 6 in the round-45 re-verification table (`corpus/SOURCES.md:522,523,524,527,529,530`; table at `:520-530`, 4 cells) and 21 in the round-46 changed-files table (`:567-587`, 5 cells). None is a registry row: the tables' headers are `| key | pin → current | class | what the witness shows |` and `| id | b11889 verdict | b11906 verdict | pin lines → b11906 lines | read by |`, neither has the contract's eleven cells, and no row in them has eleven cells.
- Additional under-inclusiveness of the same regex, worth recording: multi-id first cells (`corpus/SOURCES.md:525` `| `S048` `tcp_ipv6.c` | …`, `:526`, `:528` `| `S041`, `S046`, `S055` | …`) do **not** match `ROWLIKE_RE` (it needs `|` immediately after the closing markup). So the old scan was simultaneously over-inclusive (any S-keyed table → exit 2) and under-inclusive (multi-id cells never examined).

Because both revisions of a pair are parsed, the failure also fires on the *older* side once that side carries a re-verification table — which is why the r45 freeze → r45 evidence pair already failed and every later pair fails at `from`.

## 3. Proposed fix

`proposed.diff` (in this directory; applies with `git apply` / `patch -p1` at the lane root against `tools/sources-append-only.py` sha256 `4d78685…`):

1. `parse_registry` records `section_end` when the section ends (`:238`, `:244`) and calls a new `scan_row_like(lines, start, section_end, label)` in place of the inline loop (`:296`).
2. `scan_row_like` (`:161`) walks the blob but skips `[start, end)` — the section it already graded — and groups `|`-led runs into table segments. A segment is refused only when it is registry-shaped:
   - its header is exactly the contract header (`sorted(header) == sorted(CONTRACT_COLUMNS)`) → `a copy of the registry table outside the ## Registry section` (a registry table that lost its section);
   - or one of its rows has the registry's eleven cells and an `S0NN` first cell after markup strip (`markup_free_id`, `:156`) → `registry-shaped row in a table outside the ## Registry section`;
   - a row-like line that sits in **no** `|`-led run is still refused exactly as before (`row-like line outside the parsed registry table`), so the message the existing selftest case 30 matches is preserved.
3. The module docstring's row-like rule is rewritten to state the narrowed rule and its fail-closed bias ("A non-registry table whose own header is the contract header, or that carries an eleven-cell `S0NN` row, is refused rather than guessed at").

Why this is the right axis: the invariant rule 2 needs is "never drop a registry row", not "every S-id in the file belongs to the registry". A table whose header is not the contract header and whose rows are not eleven cells cannot hold a registry row, so refusing it produces only blindness. Anything that *could* be a registry row — the contract header without its section, an eleven-cell `S0NN` row, a row-like line with no table around it — is still a hard exit 2. Verified fail-closed on the real blob, not only in fixtures (§6 variant c).

## 4. New selftest cases — fail before the fix, pass after

Three cases added at `run_selftest` (numbered 40-42, patch hunk `@@ -521,6 +585,27 @@`):

| case | fixture | want |
|---|---|---|
| `S-keyed table outside the registry section` | a 4-cell `key` table and a 5-cell `id` table after `## Paths`, rows starting `| `S001` |` | exit 0 |
| `registry header copied outside the section` | the contract header + separator + one row appended under `## Copy` | exit 2, error `copy of the registry table outside` |
| `registry-shaped row outside any table` | an eleven-cell `S002` row appended after prose, no header | exit 2, error `registry-shaped row` |

Before the fix, with the same three cases injected into the unmodified tool (`sources-append-only.orig-plus-cases.py`, reproduced in `selftest-orig-plus-cases.txt`):

```
FAIL: S-keyed table outside the registry section (want exit 0, got exit 2 error 'to:17: row-like line outside the parsed registry table; refusing to drop it')
FAIL: registry header copied outside the section (want exit 2 error ~'copy of the registry table outside', got exit 2 error 'to:16: row-like line outside …')
FAIL: registry-shaped row outside any table (want exit 2 error ~'registry-shaped row', got exit 2 error 'to:12: row-like line outside …')
42/45 selftest cases passed        exit 1
```

After the fix: `45/45 selftest cases passed`, exit 0 (`selftest-patched.txt`). The unmodified tool on its own 42 cases: `42/42`, exit 0 (`selftest-orig.txt`) — the 39 pre-existing exit/verdict cases and 3 detector checks are unchanged, including case 30 (`row-like line outside the registry`), which now exercises the eleven-cell branch.

## 5. Patched copy grading the round transitions

Patched copy executed as `python3 $S/OUT/sources-append-only.patched.py --repo lane --from <a> --to <b>` (lane clone; the tool itself untouched in the lane):

| transition | original | patched |
|---|---|---|
| `0163fea2` → `172b8ad0` (r45→r46) | exit 2 (`:514`) | **exit 0**: `added S486 (allowed)`, `added S487 (allowed)`, `no append-only violations` |
| `172b8ad0` → `33e00582` (r46→r47) | exit 2 (`:516`) | **exit 0**: `added S488`, `S489`, `S490`, `S491`, no violations |
| `33e00582` → `380bcdff` (r47→r48) | exit 2 (`:520`) | **exit 0**: `added S492`, `added S493`, no violations; `--json` → `"violations": [], "added": ["S492","S493"], "ok": true` |
| `052cb1e9` → `0718b6ab` (r45 build → r45 integration) | exit 2 | exit 0, no rows added (the r45 evidence commit had already added S484/S485) |
| `1641aa07` → `052cb1e9` (first break) | exit 2 (`:514`) | **exit 0**: `added S484`, `added S485` |
| `d48e8cc3` → `6b8ccfb3` (last graded pair, r44 spot-check) | exit 0 | exit 0 (unchanged) |

Whole r45..r48 sweep, all 5 consecutive SOURCES.md commits: patched **5/5 exit 0**, original **5/5 exit 2** (`sweep-patched.txt`, `sweep-orig.txt`). The rows named match the rows each round's commit message claims to append (r46: S486/S487; r47: S488-S491; r48: S492/S493).

## 6. The guard still grades — real corpus text, not just fixtures

Fixture repo `$S/fixture.QgiM` (`git init`, `git rev-parse --show-toplevel` verified equal, three variant commits, each reset to the fixture base), whose `corpus/SOURCES.md` is the byte-exact `380bcdff` blob; both tools run as `--repo <fixture> --from <base> --to <variant>`:

| variant (real blob, edited) | original | patched |
|---|---|---|
| a — registry row `S492` deleted in place | exit 2 (`:522`, blind) | **exit 1**: `VIOLATION S492: row removed`, `1 append-only violation(s)` |
| b — `S492` `anchor` cell edited in place | exit 2 (`:522`, blind) | **exit 1**: `VIOLATION S492: cell `anchor` changed in place` with old/new, exit 1 |
| c — contract header + separator + one row appended under `## Copied table` | exit 2 (`:522`) | **exit 2**: `a copy of the registry table outside the `## Registry` section; refusing to drop its rows` |

Variant c is the narrowing guard: the fix does not buy exit 0 at the price of dropping a registry table that lost its section.

## 7. Residual hole (stated, not hidden)

A registry row *truncated to fewer than eleven cells* and pasted inside a foreign table outside the section is indistinguishable from that table's own row, so the patched guard lets it pass (fail-open). Truncation without a table around it, truncation under the contract header, or any eleven-cell row is still refused. The corpus has no such line (`row-like-lines.txt`: 27 candidates, all 4 or 5 cells); the guard's in-section behaviour is unchanged, so a truncated row *inside* `## Registry` is still exit 2 (`row has N cells, header has M`).

## 8. Integration items for the L1 (not edited here)

- Apply `proposed.diff` to `tools/sources-append-only.py`; the tool's selftest becomes `45/45`. `SCORECARD.md:14` (operability row, inside the `## Axes` exempt head region per `registry/append-only-contract.tsv`) still quotes `run `python3 tools/sources-append-only.py --selftest` → `42/42 selftest cases passed``; re-anchor it to `45/45` when the patch lands.
- `tools/sources-append-only.py` is **not** a graded path in `registry/append-only-contract.tsv`, so the patch is not a C1 append-only event; re-running C1 over the commit that lands this must stay `regressed=0 exit 0`.
- Round-47 lesson row (`corpus/lessons/round-47.md:49`) and spot-check D8 (`round-47-verifier-spotcheck.md:104`) now have a fix; rounds 45-48's SOURCES appends become gradable retroactively (the sweep above is that retroactive grading: no violation in any of them).
- Not re-reported (already known to the L1): gate-registry unregistered round-48 counters; spot-check count 33 vs 34; hexrun unknown `d0012618`.

## 9. Artifacts, hashes, hygiene

- `proposed.diff` — unified diff, `a/tools/sources-append-only.py` → `b/tools/sources-append-only.py`, 143 lines; `patch -p1 --dry-run` clean, applying it reproduces `sources-append-only.patched.py` byte-exactly (`cmp` clean) and that copy passes `45/45`.
- `sources-append-only.patched.py` — full proposed text (sha256 `2e23a04e6b34b2381f403c34fd6f765ad0355315dfb79dbfd749663d946d568d`); original sha256 `4d7868564226b6caa5957e9d7f4f8910a1c459ec26462a52d42e802be6079c2d` (`patched-hashes.txt`).
- `selftest-patched.txt` (45/45, exit 0), `selftest-orig.txt` (42/42, exit 0), `selftest-orig-plus-cases.txt` (42/45 with the three FAIL lines, exit 1).
- `transitions-r45-r46.{before,patched}.txt`, `transitions-r46-r47.{before,patched}.txt`, `transitions-r47-r48.{before,patched}.txt`, `transitions-first-break.patched.txt`, `transitions-last-graded.patched.txt`, `transition-r47-r48.json`.
- `sweep-patched.txt`, `sweep-orig.txt`, `row-like-lines.txt`, `fixture-variant-{a,b,c}.{orig,patched}.txt`.
- Python 3.14.8; no tool installs or upgrades were needed (no pacman transaction was run). Lane used only through a `--shared` clone; no lane file, index or jj state touched; no service started. Scratch `/fast/scratch/hyaku/kama-r48/X9SourcesGuard` removed after the last command.
