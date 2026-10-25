# ExecCensusEnd — kama lane census at the working-tree state (round 36, wave 3)

Seat: ExecCensusEnd · 2026-10-24 · leaf, no subagents, no registry mutation.

## Measured results

### 1. Census validate run

Command (as assigned):

```
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
```

- **Exit code: `0`** (0 = clean or warnings per the script's documented exit contract).
- **Final ok line (verbatim, TAB-separated):**

```
kama	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
```

- Full stdout for this run (verbatim, 6 lines total) is preserved at
  `.ufo/waves/round-36/w3/out/ExecCensusEnd/stdout.txt` (stderr empty,
  exit code in `exitcode.txt`). Preceding the ok line, the only other output was
  four W04 warnings (warnings do not affect the clean verdict):

```
kama	W04	S187 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S188 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S189 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S191 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
```

  (Verbatim from this run's captured stdout; the same bytes are in `stdout.txt`.)

Interpretation for the wave: exit 0 with only W04 means no E-codes fired on the
working tree — the draft rows S328/S329 (last two data rows, file lines 214–215)
introduce no E01 malformed row, E02/E03 id defect, E04 duplicate URL+scope, E05–E07
enum violation, E08/E09 date defect, E10 tier violation, E11 missing used-by path,
or E12 row-outside-Registry finding. The used-by targets of both draft rows
(`corpus/knowledge/sglang-native-route-deprecation.md`) exist on disk and pass E11.

### 2. SOURCES.md data-row count

- **Data rows in `corpus/SOURCES.md`: 203.**
- Count method A (measured): Grep `^\|\s*S\d{3,}\s*\|` over the file → 203 occurrences.
- Count method B (measured, independent cross-check): the `## Registry` table runs from
  line 9; header line 11, separator line 12, data rows lines 13–215 inclusive →
  215 − 13 + 1 = 203. `## Paths` begins at line 217. Methods agree exactly.
- Last two data rows are `S328` (line 214) and `S329` (line 215) — matching the wave's
  draft-row identification. Ids are sparse (gaps are expected; statuses include rejected).

## Inference (labelled, not measured)

- None beyond the E-code interpretation above, which follows the script's own
  documented code table (script header, lines 24–33). The four W04 findings are
  pre-existing rows S187–S191, unrelated to the round-36 draft bytes.

## Bounds compliance

- `scripts/sources-census.sh` is read-only by its own header contract ("writes only
  stdout or --out"); it was run with stdout/stderr redirected into this seat's
  scratch dir `.ufo/waves/round-36/w3/out/ExecCensusEnd/`. No `--out` write.
- No registry edit, no git/jj mutation, no writes outside the seat scratch dir and
  this report file. Fleet repo, siblings, SCORECARD.md, LOG.md untouched.
