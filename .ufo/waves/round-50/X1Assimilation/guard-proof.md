# Item 2 — indented-collision guard proof (2026-10-26)

The guard is the extractor pair in the collision recipe: `^ {0,3}\|` (0-3 leading
ASCII spaces, matching the census parser's own row rule, `scripts/sources-census.sh`
line 42-44: "Maintained parser accepts 0–3 leading ASCII spaces before Markdown
rows/headings") versus the column-zero-only `^\|`, which false-greens.

Fixture (written to scratch only, copied here verbatim):

    $S/guard/corpus/SOURCES.md
    # SOURCES — guard fixture
    ## Registry
    | id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
    |---|---|---|---|---|---|---|---|---|---|---|
    | S001 | fixture source one — https://example.invalid/one | docs | A | fixture scope one | §One — "one" | fixture teaches one, long enough | mined | 2026-10-26 | 90d | — |
      | S002 | fixture source two — https://example.invalid/two | docs | A | fixture scope two | §Two — "two" | fixture teaches two, long enough | mined | 2026-10-26 | 90d | — |

    $S/guard/staged.ids = S002, S999   (S002 collides with the indented row; S999 with nothing)

## Runs

1. The registry is census-valid with the indented row:

       $ bash scripts/sources-census.sh validate --file $S/guard/corpus/SOURCES.md
       file	W03	S001 mined but unused
       file	W03	S002 mined but unused
       file	ok	$S/guard/corpus/SOURCES.md
       exit=0

       $ bash scripts/sources-census.sh census --file $S/guard/corpus/SOURCES.md
       file	rows	2
       file	tier.A	2
       file	status.mined	2

   Two rows, not zero: the parser sees the indented row.

2. Maintained pattern (0-3 leading spaces) catches the indented collision:

       $ grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' registry | grep -oE 'S[0-9]+' | sort
       S001
       S002
       $ comm -12 reg-ids-maintained staged.ids
       S002                       # nonempty -> 1

3. Column-zero-only pattern false-greens:

       $ grep -oE '^\|[[:space:]]*S[0-9]{3,}' registry | grep -oE 'S[0-9]+' | sort
       S001
       $ comm -12 reg-ids-zero staged.ids
       (empty)                    # 0 — the indented S002 row is invisible

4. Second layer, the census's own duplicate-id check, also sees the indented row:
   appending `  | S002 | … |` to the fixture gives

       file	E03	S002 duplicate id
       exit=1

So the guard is not broken: an indented collision is caught by the recipe's
maintained pattern and independently by census E03. The column-zero-only variant
is the failure mode the maintainer pattern exists to prevent, and it is confirmed
to fail.

Artifacts: `w1/out/X1Assimilation/guard-fixture-ordinary.md`,
`guard-fixture-indented-duplicate.md`, `guard-collisions-maintained.txt`
(1 line), `guard-collisions-column-zero.txt` (0 lines).
