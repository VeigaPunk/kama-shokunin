# ReviewWordCount

Recommendation: the S327 quote is 20 whitespace-delimited words. The same paragraph records 18. They do not match. Do not treat 18 as the count of that quote. The lesson was not edited. No tool was installed.

Judged axis: calibration.

## Extracted sentence

Source: `corpus/lessons/round-35.md` line 28. That line is the only `Quote:` in the file. Working-tree bytes equal `e5a8ececf3d60fd53b36bb74299693a29e8f74b6:corpus/lessons/round-35.md` blob `428f1f8a0e8871022f7c1e8ea47e50ba5a8d6412`. The same blob is at HEAD `9014843cb7de8fbe87a97954c13832b67d55f046`. `git status --porcelain -- corpus/lessons/round-35.md` was empty.

Sentence between the opening quote after `Quote:` and the closing quote (111 ASCII bytes, only U+0020 spaces, no double space):

When the limit is reached, new requests are rejected with HTTP 503 so the client can retry on another instance.

Characters strictly after `Quote:` and before that closing quote are a leading space plus the opening `"` plus that sentence. `split()` attaches the quote to the first token (`"When`) and still yields 20 words.

## Count

Whitespace-delimited count: 20.

| n | token |
| --- | --- |
| 1 | When |
| 2 | the |
| 3 | limit |
| 4 | is |
| 5 | reached, |
| 6 | new |
| 7 | requests |
| 8 | are |
| 9 | rejected |
| 10 | with |
| 11 | HTTP |
| 12 | 503 |
| 13 | so |
| 14 | the |
| 15 | client |
| 16 | can |
| 17 | retry |
| 18 | on |
| 19 | another |
| 20 | instance. |

`wc -w` on that span printed 20 (exit 0), with and without a trailing newline. `quote_words` in `tools/round36-statement-audit.py`, applied to `git show e5a8ececf3d60fd53b36bb74299693a29e8f74b6:corpus/lessons/round-35.md`, returned 20. Attached punctuation (`reached,`, `instance.`) does not add tokens.

## Recorded count

Same paragraph, immediately after the closing quote: `18 words`. That is the only `<integer> words` token in the paragraph. `20 words` does not occur in the paragraph.

Match: no. 20 does not equal 18.

## Findings by severity

### High

1. False recorded word count. Path: `corpus/lessons/round-35.md:28`. The paragraph asserts `18 words` for the S327 quote. An independent whitespace split, `wc -w`, and the C1 `quote_words` extractor all return 20. The recorded count does not match the quote in that paragraph.

### Medium

None.

### Low

None in the quote span. HEAD `9014843cb7de8fbe87a97954c13832b67d55f046` is not frozen tip `e5a8ececf3d60fd53b36bb74299693a29e8f74b6`, but the lesson blob is identical, so the count is of the frozen lesson bytes.

## Residual risk

- This seat did not re-fetch the vLLM page. The count is of the lesson quote as committed, not a live-page identity check.
- Fleet blob `6d8f317378ba6048d8a3dfb4944adaf24f341eea` (`HEAD:.ufo/reports/round-35/kama.md`) line 21 restates the same sentence and contains neither `18 words` nor `20 words`. That report does not carry the false integer. Do not rewrite it, and do not edit `corpus/lessons/round-35.md`, to fix the count.
- No correction row was written here.

## Verification gaps

- `https://docs.vllm.ai/en/v0.32.0/configuration/engine_args/` was not opened.
- The full C1 counting command was not run. Only `quote_words` on the frozen lesson was executed. This seat does not claim C1 met or unmet.
- The S327 cell in `corpus/SOURCES.md` contains the same sentence and no word-count cell. It was not used as the recorded count.
