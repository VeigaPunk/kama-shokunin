# A06C2Population — C2 frozen-population binding attack

Source: `git show master:tools/round62-c2-counter.py` at master `65d7cad0fce90e34de37527cde22e97b63b118bf`; scratch-only probes loaded that source and the SCORECARD bytes from the same tip. No lane files were changed.

## Findings

- **Later-numbered empty heading: does not pass; it denies the predicate.** Appending `**Capabilities — canonical list as of round 999**` with no rows makes `canonical_rows()` select round 999 and return zero rows. The main predicate then records missing frozen rows/prefixes and fails (`bool(can_rows)` is false). This is a fail-closed false negative, not a population-binding bypass; it also means an irrelevant later heading can suppress a valid round-62 section.
- **Heading and rows inside a fenced block: defeats the intended canonical-section provenance.** Appending a fenced ` ```md ` block containing a round-999 heading and the 12 exact frozen rows yielded `canonical_rows() == (999, 12 rows)`, with no duplicate, missing-capability, or prefix errors. The parser scans every line without tracking Markdown fence state. Therefore C2 can treat code-example text as the newest canonical list. The real registry/live checks still apply, but the claim that these rows occur in the newest *canonical capabilities section* is not established.
- **Duplicate slug: rejected.** Appending a round-999 heading followed by the 12 rows plus a duplicate `sources-registry` row returned 13 rows and duplicate slugs. `main()` explicitly checks `len(slugs) != len(set(slugs))` and adds `canonical rows must contain each frozen capability once: ...` to `canon_mismatch`, so `met` is false. This does not defeat the binding.

Reproducible observations from scratch probe:

```text
baseline: round=62 rows=12
later_empty_heading: selected_round=999 rows=0 (missing frozen population)
fenced_full: round=999 rows=12 duplicate=False all_expected=True
 duplicate: round=999 rows=13 duplicate=True all_expected=True
```

The fenced probe used all 12 exact SCORECARD round-62 capability rows, preserving frozen prefixes; the fence is the only semantic difference from a real heading/table section.

## Smallest safe correction

Make `canonical_rows()` ignore headings and candidate rows inside Markdown fenced code blocks (track opening/closing backtick or tilde fences, including fence length), and recognize only an actual Markdown heading for the canonical section. Continue rejecting duplicate slugs. This prevents fenced examples from becoming population authority. Separately, consider treating an empty later heading as malformed rather than silently selecting it; it currently fails closed and is not the semantic bypass.

Tool installs/updates: none.

Report: .ufo/waves/round-62/w1/A06C2Population.md