# R57Item27LessonDraft — distinct case 48

Read-only independent checks, from `/home/vgpnk/Projects/shokunin/kama-shokunin`; no source or lesson edits. This case is distinct from the sibling case-28 S513 quote-count/missing-receipt test.

## Commands and actual outputs

```sh
python3 .ufo/waves/round-57/controls/c1-noop.py
printf 'noop_exit=%s\n' "$?"
python3 -c "import glob; print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"
printf 'spotcheck_count_exit=%s\n' "$?"
grep -n -F "all environment pairs GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> up to that number will be added to the process's runtime configuration" .ufo/waves/round-57/sources/git-config-live-2026-10-27.html | wc -l
printf 'source_phrase_hits_exit=%s\n' "$?"
```

Observed combined output:

```text
mismatches=0 maxN=46 met=True
noop_exit=0
43
spotcheck_count_exit=0
0
source_phrase_hits_exit=0
```

The no-op control is a demonstrated false green: the frozen `c1-noop.py` comment states it does no registry, self-description, or canonical-table inspection, yet its summary is `met=True` and exit 0. The independently derived 43 count agrees with the round-57 lesson's calibration correction from 42; this verifies the file census, not the counter's corrected output.

The exact S515 quote did not appear as a contiguous literal in the saved round-57 HTML snapshot (0 hits). I separately re-opened the live Git manual URL with the reader; its page identifies git-config 2.56.0, last updated 2026-09-28. The located quote, location and 18-word count are reported by the round-57 source-reopen record `.ufo/waves/round-57/sources/SourcesReopen06.md`. This seat's snapshot literal-search miss is not a counterexample to the live source quote; likely HTML encoding/markup prevents contiguous literal matching [INFERENCE]. No admit/reject spot-check is claimed.

## Verdict

This assigned case is a read-only lesson-evidence check, not a source mutation probe: the prompt explicitly prohibits lesson/source writes and provides no behavioral detector contract for prose mutation. No killed/survived mutation verdict is asserted. Exact outputs above are the case evidence.

Report: .ufo/waves/round-57/w1/out/R57Item27LessonDraft-case48.md