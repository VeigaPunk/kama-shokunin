# X07Anchors — round 56, S512 quote anchor bound

Scope: bounded, read-only test that the S512 quote stated in
`corpus/lessons/round-56.md` occurs in the opened snapshot
`.ufo/waves/round-56/sources/rtld-audit.7.html`, and that the lesson's quote is
<= 25 words. No lane file was modified.

## Artifacts

| Artifact | SHA-256 |
|---|---|
| `x07-quote-anchor-check.py` (test) | `ab95bb4fcf020b938844b5af13cc0cfa2270ee1fabfc4e17fbbf958fe223af15` |
| `quote-anchor.out` (receipt) | retained run below |
| snapshot `rtld-audit.7.html` (read) | `a95aa3fb6407ac8d1890190ca92837445dab774e53996d3d4cf079412c813153` |
| lesson `round-56.md` (read) | `d2875ca81831cc7e1c65144c10cf31f39b52689fb84b8fe85d944abf1d8430ee` |

## Method

The quote is extracted from the S512 bullet's U+201C..U+201D span; the snapshot is
read as UTF-8, HTML tags stripped, entities decoded and whitespace collapsed to one
space (the snapshot itself splits the quote with `<b>LD_AUDIT </b>` and a line
break at lines 89-91, so a byte-literal search fails). Two mandatory checks:
occurrence count >= 1 inside the DESCRIPTION section, and word count <= 25. Two
negative controls keep the checks falsifiable: a token-mutated quote must not be
found, and a 26-word span must be rejected by the bound. A secondary, reported-only
check compares the lesson's declared `(N words)` with the measured count.

## Exact run

```
$ cd /fast/scratch/hyaku/kama-r56/X07Anchors
$ TMPDIR=/fast/scratch/hyaku/kama-r56/X07Anchors \
    python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-56/w1/out/X07Anchors/x07-quote-anchor-check.py
A1 quote_occurrences=1 section='DESCRIPTION top'
B1 quote_words=15 bound=25 ok=True
O1 declared_words=15 measured_words=15 consistent=True
N1 mutated_quote_occurrences=0 expected=0
N2 long_span_words=26 bound_rejects=True
RESULT=PASS
exit=0
```

Receipt: `quote-anchor.out` (same five lines plus `exit=0`).

## Findings

- **PASS.** The lesson quote “the environment variable LD_AUDIT must be defined to
  contain a colon-separated list of shared libraries” occurs exactly once in the
  snapshot's normalized text, inside the DESCRIPTION section (match position is
  between the DESCRIPTION `<h2>` at line 75 and the VERSIONS `<h2>` at line 368;
  source sentence at lines 89-91).
- **PASS.** Measured quote length is 15 words, inside the <= 25 bound.
- **Consistent.** The lesson's declared `(15 words)` equals the measured 15.
- **Controls live.** The token-mutated quote is absent (`0` occurrences), and a
  26-word synthetic span is rejected, so neither check is vacuous.

## Defects

None in the lane artifact under test. Methodological note for reviewers: a raw
byte/substring grep for the full quote over `rtld-audit.7.html` returns nothing
because of the inline `<b>` element and the line break; any independent replay of
this check must strip markup and collapse whitespace before matching.

## Risks and limits

This bounds text presence and length only. It does not attest how the snapshot was
fetched, its page date, or whether other statements on the page support the lesson's
inference; those are outside this seat's ticket. No tool installs were needed
(stdlib Python 3.14.8 only). Scratch `/fast/scratch/hyaku/kama-r56/X07Anchors/`
was removed after the receipt was copied here.
