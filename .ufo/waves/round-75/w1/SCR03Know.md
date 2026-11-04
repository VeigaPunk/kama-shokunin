# SCR03Know — accepted-history knowledge entry

## Behavior and axes

Axes: freshness and expansion. Added one append-only knowledge entry:
`corpus/knowledge/append-only-accepted-history.md`.
It distinguishes audit restoration, disclosure and undisclosed line entries; states
the round-51 disclosure cutoff; specifies the frozen six-column register binding;
and explains the S537 LF re-land without claiming acceptance erases history.
No product code, existing knowledge entry, frozen tool or another seat's file was edited.

## Commands and observed outcomes

Commands below used absolute paths; no Git mutation occurred.

1. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD`
   — exit 0; output `0908bab5cbf0ab6b435144fc525a3e18443dc08f`.
2. `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --json`
   — exit 1, stderr empty. Launched through subprocess with cwd and explicit TMPDIR
   `/fast/scratch/hyaku/kama-r75/SCR03Know`. JSON `to` equals the revision in item 1.
   The retained summary extracted from that output is:

   ```json
   {"bad_declarations":5,"bad_disclosures":0,"binary":0,"commits":576,"disclosed":5,"disclosed_lines":10,"events":223,"files":143,"partial":0,"permitted_lines":633,"regressed":0,"restored":87,"ungraded":78,"ungraded_lines":330,"unmatched":0,"unrestored":53,"vanished":0}
   ```

   An in-memory extraction of this same JSON (no second audit run) found 53 events
   with nonempty `undisclosed`. The largest such event was:

   ```json
   {"commit":"ea33a78f2b0bcbbebcde60d2851a81c54746baa8","file":"corpus/SOURCES.md","deleted":639,"graded":362,"permitted":277,"ungraded":0,"status":"unrestored"}
   ```

   Its undisclosed counts sum to 362; their only mechanical class is `in-place-edit`.
   The largest deletion event overall is instead a restored SCORECARD event;
   the knowledge entry deliberately limits its superlative to undisclosed events.
3. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show --no-patch --format=fuller ea33a78f2b0b`
   — exit 0; subject `round-65: S537 byte-exact re-land (LF), wave receipts, lesson mistakes 9-10`.
4. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --diff-filter=A --format='%H %s' -- registry/append-only-disclosures.tsv`
   — exit 0; output `b6bed925b032ac2c19b63ef4af358ebdd5922c26 round-51: build — server_exe record and own-member replay check (C1), append-only-audit v6 + disclosure ledger (C2), S499, freeze receipts`.
5. `sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-75/w1/sources/gitattributes.html`
   — exit 0; digest `ceb3351f931ae86283f51416cf0042fd78265eda59e5af7d09e17581ec0f77f7`.

The audit's nonzero exit is a measured historical finding, not a passed gate.
Scratch was removed in `finally`; tool output was `scratch_removed: True`.
No installations, updates, clones, fixture commits or other runtimes were used.

## Provenance and gates

Read the entire frozen claim file, the audit docstring and the prescribed recent
knowledge entry. Inspected the retained HTML: lines 2679–2681 contain the `text`
attribute's normalization rule. Its existing access receipt is
`.ufo/waves/round-75/measured/before/source-gitattributes.receipt`, recording the
2026-11-04 live fetch; this seat did not perform or claim that fetch.
`source: S547` is present in the entry; S547 is the frozen reserved id. A SOURCES
search found no appended S547 row at observation time. Source registration belongs
to SCR01, not this seat. Likewise the register and round-75 counter were absent
at initial discovery; the explicitly permitted baseline-audit fallback was used.
No acceptance-counter run, landed register inspection, source census gate result,
build, lint or test pass is claimed. No historical receipt was re-stamped.

## Conflicts, limits and out-of-scope items

Report destinations in the assignment disagree verbatim:
`Report: .ufo/waves/round-75/w1/SCR03Know/report.md.` versus
`Report: write your scoped findings to .ufo/waves/round-75/w1/SCR03Know.md`.
This report follows the final scoped-report instruction, at the latter path.

The source receipt contains an uncertain section locator; the entry instead uses
the directly observed `text` attribute / `Set` paragraph. The frozen pre-base
receipt counts 575 commits; this seat measured 576 at the freeze commit, with the
same event/restoration/disclosure totals. No rule or receipt was changed.
Later register acceptance and the source row landing remain outside this seat's
execution evidence; this entry labels its measured revision and contract-only claims.

## Self-evaluation

Accuracy 4/5: measured baseline and retained quote; later landed-register execution
is unobserved. Completeness 4/5: required content present, source-row append owned
elsewhere and not observed. Clarity 5/5: separates event status from row class.
Actionability 5/5: names pinned audit reproduction and counter command.
Conciseness 4/5: provenance consumes the long header lines. Mean 4.4/5.
Highest-impact handoff: main agent should check the eventual S547 row and landed
register against this explicitly revision-bound entry; no rerun was done to decorate
this report. The user should agree with the stated evidence boundary.

## Artifact paths

- `corpus/knowledge/append-only-accepted-history.md`
- `.ufo/waves/round-75/w1/SCR03Know.md`
