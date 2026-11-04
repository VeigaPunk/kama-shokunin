# SCR01Sources — round 75 w1

## Behavior and axes

Freshness: independently opened https://git-scm.com/docs/gitattributes on 2026-11-04. Expansion: appended exactly one source row, S547, after S546 at the Registry table's end in `corpus/SOURCES.md` (line 299). Existing row lines were not edited. The row is docs, tier A, mined, recheck on-release; used-by is `corpus/knowledge/append-only-accepted-history.md`, which the sibling seat had written before the mirror copy. This seat did not write that entry.

Read `plans/round-75-claims.md` in full before implementation. Observed lane revision: `0908bab5cbf0ab6b435144fc525a3e18443dc08f`; its preceding log entry was base `dc58e51315e79d36df5fc530c95fbd3aecbf7593`. No git/jj mutations, tool installations, product-code edits, or frozen-file edits were performed.

## Source receipt

Exact command:

```sh
curl -sL --max-time 60 https://git-scm.com/docs/gitattributes -o /fast/scratch/hyaku/kama-r75/SCR01Sources/gitattributes-live.html
```

Exit 0. `wc -c` printed 131174 bytes; `sha256sum` printed `ceb3351f931ae86283f51416cf0042fd78265eda59e5af7d09e17581ec0f77f7`. `cmp -s` against `.ufo/waves/round-75/w1/sources/gitattributes.html` took the success branch, printing `BYTE-IDENTICAL`. A subsequent receipt capture compared those byte arrays as equal. Live-fetch bytes are retained in `pre-append/gitattributes-live.html` alongside this report.

Located quote (16 whitespace-delimited words):

> Line endings are normalized to LF in the index every time the file is checked in

Location: §Checking-out and checking-in (`#_checking_out_and_checking_in`) → `text` (`#_text`) → **Set** (`#Documentation/gitattributes.txt-Set-1`). The term is at retained HTML line 2676; its paragraph spans 2678–2681; the quote crosses lines 2679–2680. Page version stamp at line 1300: `gitattributes last updated in 2.56.0`. The row uses this precise locator, not the unrelated merge-driver `text` term at line 3852.

The documentation grounds LF normalization semantics, not the historical event's cause or its acceptance. No historical-audit success is claimed here.

## Gates and outcomes

Commands below ran in the order shown. Each exited 0; warnings were allowed.

1. Live baseline:
   `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`
   Output relied on: `file\tok\t/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`.
2. Mirror baseline: copied the lane's `corpus/` to `/fast/scratch/hyaku/kama-r75/SCR01Sources/mirror-lane/corpus/`, plus the round-74 mirror's repo-root used-by targets (`SCORECARD.md`, `SKILL.md`, `tools/`, `registry/`, `tests/`, `.ufo/waves/round-29/`). No fabricated used-by target was created; the actual knowledge entry was in the corpus copy.
   `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file /fast/scratch/hyaku/kama-r75/SCR01Sources/mirror-lane/corpus/SOURCES.md`
   Output relied on: `file\tok\t/fast/scratch/hyaku/kama-r75/SCR01Sources/mirror-lane/corpus/SOURCES.md`.
3. Inserted S547 into the mirror, then ran the identical mirror command. Exit 0 and the same final `ok` line. **This successful gate preceded the real append.** Retained full output: `pre-append/mirror-validate-final.out`.
4. Appended the identical row to the real Registry table using the edit tool, then ran the explicitly assigned acceptance command:
   `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
   Exit 0. Output relied on: `kama\tok\t/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`. Full output: `post-append-census.out`.

Receipt capture selected lines starting `| S547 |` and observed exactly one; the exact selected row is retained in `receipt.json`. No builds, counter tests, or broader round gates were run by this seat.

## Findings, dead ends, and disagreements

- Assigned rules path `/home/vgpnk/Projects/shokunin/kama-shokunin/CORPUS.md` did not exist. Glob located `/home/vgpnk/Projects/shokunin/CORPUS.md`, whose complete corpus/source registry contract was read. The initial survey's `wc` therefore exited 1 despite successful earlier git/hash commands.
- The used-by entry was initially absent, then appeared while sibling work ran. It existed before the mirror copy and append; no placeholder or invented entry was used.
- A single-line search for the entire quote found nothing because HTML wraps it. Searching `checked in` located line 2680 and resolved the correct paragraph. The first candidate `Documentation/gitattributes.txt-text` is a merge-driver term, not this quote's anchor.
- The assigned id is S547, but `git grep -n S547 0908bab5cbf0ab6b435144fc525a3e18443dc08f -- .` returned no matching text. Reservation was explicit in the seat assignment; no freeze bytes were changed.
- The retained before-receipt's locator is imprecise. Verbatim conflict for canonical adjudication:

  ```text
  locator  §"Performing a three-way merge"? no — §"Generating diff text" precedes; the quote sits
           in the `text` attribute paragraph under §"DEFINING MACRO ATTRIBUTES"'s preceding
           ATTRIBUTES section
  ```

  The independently located hierarchy is Checking-out and checking-in → text → Set, as above. The source bytes and quoted words agree; the frozen claim itself was not reinterpreted or edited.
- An attempted dispatch read omitted its `w1/` directory and returned not found; the later targeted search located `.ufo/waves/round-75/w1/w1-dispatch.json`. No dependency on that failed read remains.

## Touched surfaces and artifacts

All relative paths below are under `/home/vgpnk/Projects/shokunin/kama-shokunin`.

- `corpus/SOURCES.md`: one inserted S547 row only.
- `.ufo/waves/round-75/w1/SCR01Sources/report.md`: this report.
- `.ufo/waves/round-75/w1/SCR01Sources.md`: scoped summary.
- `.ufo/waves/round-75/w1/SCR01Sources/receipt.json`: source metadata, row, gate exits and exact acceptance command.
- `.ufo/waves/round-75/w1/SCR01Sources/pre-append/`: independent source bytes and live/mirror baseline/final census transcripts.
- `.ufo/waves/round-75/w1/SCR01Sources/post-append-census.out`: full acceptance transcript.

Out of scope: C1/C2/C3 counter implementation, accepted-history register generation, knowledge-entry authorship, round integration, judge verdict, commits and publication. Retaining receipts does not mean a git commit was made.

## Completion self-evaluation

Accuracy 4/5: byte comparison, located paragraph and census exits are observed; historical acceptance remains explicitly outside scope. Completeness 4/5: requested row and both gates delivered; reservation wording conflict is disclosed rather than silently repaired. Clarity 4/5: commands and paths are explicit; the required duplicate summary adds some redundancy. Actionability 4/5: full transcripts and exact row are retained, but scratch paths intentionally expire. Conciseness 4/5: report includes necessary dead ends and verbatim locator conflict. Mean 4.0/5. Highest-impact improvement already applied: use the independently verified Set anchor rather than the misleading merge-driver term. A reader should be able to reproduce the source and census findings without trusting narrative alone.
