# Item-10 ID collision check — round 34, W1

## Scope and procedure

- Lane registry (read-only): `corpus/SOURCES.md`.
- Staged package (read-only): `/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md`.
- No registry or staged-package content was edited; no append was performed.
- Extracted each ID list with the assigned pipeline, using `LC_ALL=C sort` for deterministic `comm` input:

```sh
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' <file> | grep -oE 'S[0-9]+' | LC_ALL=C sort
```

- Produced collisions with `LC_ALL=C comm -12 reg-ids staged-ids`.
- Both input lists pass `LC_ALL=C sort -c`; an independent set-intersection cross-check equals the `comm -12` output.

## Results

| Measurement | Observed result |
| --- | --- |
| Lane extracted-ID count | 194 |
| Lane highest ID | **S194** |
| Staged extracted-ID count | 129 |
| Staged observed ID range | **S195–S323** |
| Collision count | **0** |

### Full collisions list

**None.** The `collisions` file is empty (0 lines).

## Output artifacts

All paths below are relative to the lane root:

- `.ufo/waves/round-34/w1/out/ExecIdCollision/reg-ids`
- `.ufo/waves/round-34/w1/out/ExecIdCollision/staged-ids`
- `.ufo/waves/round-34/w1/out/ExecIdCollision/collisions`
- `.ufo/waves/round-34/w1/out/ExecIdCollision/scratch-registry` (guard fixture)

## Guard proof: indented rows are not dropped

Scratch fixture `.ufo/waves/round-34/w1/out/ExecIdCollision/scratch-registry` contains exactly:

```text
  | S002 | scratch guard fixture |
```

The assigned 0–3-space extraction was run against that fixture:

```sh
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' "$SCRATCH" | grep -oE 'S[0-9]+' | LC_ALL=C sort
```

Output:

```text
S002
```

The column-zero-only control was also run:

```sh
grep -oE '^\|[[:space:]]*S[0-9]{3,}' "$SCRATCH" | grep -oE 'S[0-9]+' | LC_ALL=C sort
```

Output: **empty** (no IDs extracted). The captured-output evidence was:

```text
0-3-space pattern output:
S002
column-zero-only pattern output:
<empty>
output_byte_counts: 0-3-space=4, column-zero-only=0
```

Here `<empty>` annotates zero-byte stdout. Thus the required 0–3-space pattern extracts `S002` from the indented row, while the column-zero-only pattern extracts nothing.

## Scope limit

This is only the requested lexical ID-collision procedure and guard proof. It does not validate, normalize, or admit any staged source row, and it makes no serving-health or model-quality claim.
