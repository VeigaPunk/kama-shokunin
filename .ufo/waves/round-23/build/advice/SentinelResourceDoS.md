# Resource-exhaustion review: `report-landing-audit.py`

**Scope / axes reviewed:** report size and token cardinality; lane/fleet commit-history size; committed `SOURCES.md` URL-alternative count/length; `cat-file` query and response buffering. Findings are resource limits, not integrity findings. No source change is proposed.

## Findings

1. **Unbounded report size and hash-token processing — Moderate availability limit.**
   - **Exploit path:** A selected hostile fleet report can be a very large committed blob; alternatively, a caller can pass a large draft with `--report`. The committed path is read by `git show` and the draft by `Path.read_text`, both as complete in-memory text (`tools/report-landing-audit.py:87-97,171-177,258-280`). The text is then scanned in full; hash and abbreviation scans build lists/sets (`239-255,291-305`).
   - **Impact:** Memory and CPU grow with report bytes and matching-token count, with additional in-memory structures and eventual rendered/JSON output. There is no report-byte or token-count ceiling. Very large inputs can exhaust process/host resources before the declared typed evaluation-error path; actual exhaustion behavior was not exercised.
   - **Smallest remediation:** Enforce a documented maximum report size before decoding/scanning, and return `EvalError` when it is exceeded.

2. **Whole-history scan repeated per selected round — Moderate availability limit.**
   - **Exploit path:** Put a very large history in the selected lane repository and audit multiple rounds. Each `round_commits` invocation runs `git log` on the entire branch and captures all commit metadata/subjects before filtering by round in Python (`147-162`). `audit_round` invokes it once per report (`285`); `run` iterates every selected round (`399-407`). The fleet report cutoff also invokes `git log` for each report (`165-168,270`).
   - **Impact:** For C lane commits and R selected rounds, lane-history output and parsing are repeated at least R times (O(R·C) output/processing); each individual scan also buffers and splits the complete log. Millions of commits can therefore impose large latency and memory use. No maximum history/round count or shared history pass is present in the inspected path.
   - **Smallest remediation:** Bound the commit enumeration and fail with a typed limit error on overflow; at minimum, share one bounded history pass across selected rounds.

3. **Unbounded registry-built regex — Low/Moderate availability limit; regex injection not found.**
   - **Exploit path:** Add many valid `S###` registry rows with long, closely related URLs to committed `SOURCES.md`. The loader reads the entire blob, collects URL forms, builds two full alternation strings and compiles them into one regex without a row, byte, or alternative-count limit (`180-236`). That regex is then scanned over each selected report (`239-255,279-280`).
   - **Impact:** Compilation storage/time grows with the total alternative text, and each report scan uses the resulting large expression. The URL alternatives are passed through `re.escape` (`229-236`), so source values cannot inject regex operators; this review does **not** establish catastrophic backtracking. The demonstrated concern is unbounded expression size and associated work.
   - **Smallest remediation:** Set explicit limits on accepted registry rows/aggregate URL bytes (refusing over-limit input), or replace the alternation with a bounded literal-matching approach.

4. **Unbounded `cat-file --batch-check` input/output buffering — Moderate availability limit.**
   - **Exploit path:** Put many distinct hash-shaped tokens in a selected report or many citations in its landed section. Token collections are sorted/materialized, then all queries are joined into one stdin string (`100-115,239-255,291-293`). `git` passes that complete input to `subprocess.run` with `capture_output=True, text=True`; the complete response is retained and split (`87-97,113-130,116`). Lookups run against both lane and fleet repositories (`276-283`).
   - **Impact:** Input, Git response, split-line list, token collections, and status map all scale with token count; a token-dense report can amplify the report-size cost and exhaust memory or spend excessive time in Git/Python. There is no query batch size or total-token ceiling.
   - **Smallest remediation:** Cap total distinct tokens and issue bounded query batches, with a typed refusal before processing if the total exceeds the supported limit.

## Evidence and limits

- **Observed source:** `read tools/report-landing-audit.py:79-168,171-312,363-429` returned the code locations cited above. This was a source-only review; no runtime command, benchmark, malicious fixture, multi-million-commit repository, or maximum-size input was run. Therefore the resource impact is a static complexity/buffering assessment, not a measured threshold or reproduced crash.
- No external URLs or outside sources were used. No code, tests, or other files were changed; this report is the only file written.
