# Indent-guard re-run — round 36, ExecCollision

Lexical check only. `grep -oE` is a literal text match, not a semantic registry parse. Lane registry `corpus/SOURCES.md` was not edited. Target fixtures under `.ufo/waves/round-36/assimilation/guard/` were read only. Scratch and command output live in `.ufo/waves/round-36/w1/out/ExecCollision/`.

Transcript: `.ufo/waves/round-36/w1/out/ExecCollision/indent-guard.txt` (`bash indent-guard.sh`, exit 0, stderr 0 bytes). `grep (GNU grep) 3.12-modified`.

## Fixtures

Seat copies are byte-identical to the target guard fixtures (`cmp` identical). Written with `printf`, not by editing the lane registry.

Scratch registry, 38 bytes (`od -An -tx1`):

```text
7c 20 53 30 30 31 20 7c 20 72 65 61 6c 20 7c 0a
20 20 7c 20 53 30 30 32 20 7c 20 69 6e 64 65 6e
74 65 64 20 7c 0a
```

```text
| S001 | real |
  | S002 | indented |
```

The `S002` row starts at two ASCII spaces (`20 20`), then `|`.

Staged file, 18 bytes:

```text
7c 20 53 30 30 32 20 7c 20 73 74 61 67 65 64 20
7c 0a
```

```text
| S002 | staged |
```

That staged row is column zero, so both patterns can see `S002` on the staged side. The miss is on the registry side.

## Commands

```sh
PAT_COL0='^\|[[:space:]]*S[0-9]{3,}'
PAT_SPACE='^ {0,3}\|[[:space:]]*S[0-9]{3,}'
grep -oE "$PAT" <file> | grep -oE 'S[0-9]+' | LC_ALL=C sort
LC_ALL=C comm -12 <reg-ids> <staged-ids>
```

The `{3,}` bound is on the first pattern. The second `grep` only cuts the id token out of an already-bounded match. `LC_ALL=C sort -c` passed on all four id lists. An independent Python set intersection equals both `comm -12` results.

## Result

| Pattern | Registry ids | Staged ids | `comm -12` | Collision bytes |
| --- | --- | --- | --- | --- |
| Column zero `^\|` | `S001` (5 bytes) | `S002` (5 bytes) | empty | **0** |
| 0–3 spaces `^ {0,3}\|` | `S001`, `S002` (10 bytes) | `S002` (5 bytes) | `S002` | **5** |

Column-zero raw match (7 bytes), exit 0:

```text
| S001
```

0–3 raw match (16 bytes = 7 + 9), exit 0. The second line keeps its two leading spaces:

```text
| S001
  | S002
```

Column-zero collisions (0 bytes, 0 lines, `comm` exit 0):

```text
```

0–3 collisions (5 bytes, 1 line, `comm` exit 0):

```text
S002
```

Python: `py_col0_intersection=[]`, `py_space_intersection=['S002']`, both `matches_comm=True`.

Column zero does not fail to read the file. It extracts the column-zero `S001` row and the column-zero staged `S002` row, then reports no collision. The indented registry `S002` is the row it drops. The 0–3 pattern extracts that row and the intersection is `S002`. A column-zero-only check false-greens this collision.

## Target guard outputs

Same two patterns, read-only, on `.ufo/waves/round-36/assimilation/guard/scratch-registry.md` and `scratch-staged.md`. `cmp` against the precomputed target files:

| Target file | Re-run |
| --- | --- |
| `col0-ids` | identical |
| `space-ids` | identical |
| `staged-ids` | identical |
| `col0-collisions` | identical (0 bytes) |
| `space-collisions` | identical (`S002`) |

`zero-ids` is also byte-identical to the 0–3 id list on this fixture. So are `^ *\|` and `^[[:space:]]*\|`. Those three patterns are not distinguished by this fixture. No recorded command text for `zero-ids` was found, so that filename is not provenance. The miss/catch split does not depend on it.

## 4-space negative control

Not the assigned collision. Seat file `scratch-four-space.md` is four spaces then `| S002 |`. Both patterns exit 1 and write 0 bytes. That matches the census comment that 4 or more leading spaces are indented code (`scripts/sources-census.sh` lines 40–42). A collision hidden at 4+ spaces would be missed by both patterns. The assigned row is 2 spaces, inside the 0–3 window.

## Lane registry untouched

`corpus/SOURCES.md` before and after this run:

| Check | Before | After |
| --- | --- | --- |
| sha256 | `57352f20b1de70c01405adea6f77bf165006e6cdafda459f4dd985f87f679a46` | same |
| size | 181743 | 181743 |
| mtime | 2026-10-24 21:27:16.112479233 -0300 | same |
| `git status --porcelain -- corpus/SOURCES.md` | 0 bytes | 0 bytes |
| `git diff -- corpus/SOURCES.md` | 0 bytes | 0 bytes |
| worktree blob | `cad79b6ae9bdd7d037eda5bebfe6ef0d25d546c6` | same |
| `HEAD:corpus/SOURCES.md` | `cad79b6ae9bdd7d037eda5bebfe6ef0d25d546c6` | same |

Nothing was appended. No renumber. This run does not re-derive the live registry/staged collision list.

## Artifacts

- `.ufo/waves/round-36/w1/out/ExecCollision/indent-guard.sh`
- `.ufo/waves/round-36/w1/out/ExecCollision/indent-guard.txt`
- `.ufo/waves/round-36/w1/out/ExecCollision/scratch-registry.md`
- `.ufo/waves/round-36/w1/out/ExecCollision/scratch-staged.md`
- `.ufo/waves/round-36/w1/out/ExecCollision/seat-col0-collisions` (0 bytes)
- `.ufo/waves/round-36/w1/out/ExecCollision/seat-space-collisions` (`S002`)
