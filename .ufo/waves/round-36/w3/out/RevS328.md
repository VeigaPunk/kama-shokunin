# RevS328 — falsification attempt on the S328 landing bytes (round 36, wave 3)

Seat: RevS328 (leaf, no subagents). Scope: attack the S328 row and the entry draft
against the source bytes. One fetch of the target URL, nothing appended, no corpus
or registry write, lane jj/git state untouched.

## Measured results

- URL: https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx
- HTTP status: 200 (single curl fetch, 2026-10-24)
- Body size: 17359 bytes; 467 lines; md5 d268509f4df1878934d59346b8973e9e
- Saved bytes (seat scratch): .ufo/waves/round-36/w3/out/RevS328/native_api_v0.5.22.mdx
- Occurrences of `get_model_info`: 2 (lines 9 and 71; both are `/get_model_info`)
- Occurrences of the route `/model_info` (literal): 0 — `grep -o '/model_info'` matched nothing
- Occurrences of bare substring `model_info`: 2, both inside `get_model_info`
- Route-list entry line: 9 — line 9 is exactly ``- `/get_model_info` `` in the route list
- Worked-example line: 71 — line 71 is exactly `url = f"http://localhost:{port}/get_model_info"`
- Line 6 (20 words, quoted in full, within the 25-word bound):
  "Apart from the OpenAI compatible APIs, the SGLang Runtime also provides its native server APIs. We introduce the following APIs:"

## Comparison against the S328 row (corpus/SOURCES.md:214) and the entry draft

| Draft claim | Measured | Verdict |
|---|---|---|
| S328 anchor "line 6 and route-list line 9" | Quote sentence sits on line 6; route-list `/get_model_info` entry is line 9 | holds |
| S328 quote (15 words) "Apart from the OpenAI compatible APIs, the SGLang Runtime also provides its native server APIs." | Byte-exact substring of line 6 (15 words; full line is 20 words — the draft quotes the first sentence only and does not claim the whole line) | holds |
| S328 "still lists only /get_model_info and never names /model_info" | `get_model_info` = 2, both `/get_model_info` (lines 9, 71); `/model_info` = 0 | holds |
| Entry "route list, on line 9, still names /get_model_info" | line 9 = ``- `/get_model_info` `` | holds |
| Entry "the string /model_info does not occur anywhere in that file — the count is zero" | 0 occurrences | holds |
| Entry "worked example on line 71 still asks for http://localhost:{port}/get_model_info" | line 71 matches the cited request string exactly | holds |
| Lesson gate: "HTTP 200, 17359 bytes" | 200; 17359 | holds |
| Entry "opens with one sentence: '…'" | The quoted sentence is the page's opening sentence, byte-exact at line 6; line 6 also carries a second sentence ("We introduce the following APIs:"). The quote itself is exact and located; only the word "opens" is loose, not a quoted byte | holds (quote), minor wording note |

## Findings

1. Falsification failed. Every checkable number and anchor in the S328 row, the entry
   draft, and the lesson's S328 gate paragraph reproduces from the fetched bytes:
   status 200, size 17359, route-list line 9, worked-example line 71, `/model_info`
   count 0, `get_model_info` count 2, quote byte-exact at line 6, quote 15 words
   (under the 25-word bound).
2. KQ45 reading: the S328 quote is byte-exact at the anchor line its cell names and is
   not a stripped-markup paraphrase; the row is not the S174/S193 pattern. The entry's
   "opens with one sentence" phrasing is the only loose wording: line 6 contains 20
   words in two sentences, of which the quote takes the first 15 verbatim. This is an
   observation on prose, not a numeric defect; no correction row is warranted from
   this seat (and none was appended).
3. No divergence to report: measured values equal draft values on every axis named in
   the task (status, byte size, both counts, both line numbers, line-6 quote).

## Inference (marked as such)

- Inference: the "opens with one sentence" phrase reads the page's opening sentence,
  which the draft quotes exactly; a hostile reader could read it as "line 6 is one
  sentence," which is false (20 words). If a later round wants zero loose wording,
  an appended note — never a cell rewrite — could narrow it to "line 6 opens with
  the sentence:". Not required by any measured defect.

## Method note

Fetch performed once via curl with status capture; counts and line numbers derived
from the saved bytes with grep -o/-n and sed, so every figure above is re-derivable
from the scratch file. No second fetch of the URL was made. No SOURCES.md,
QUALITY.md, README.md, lesson, or entry file was modified; writes were confined to
this seat directory.
