# CriticPredicateIdentity — round 29 C1

## Scope and axis

**Axis: calibration.** This is a read-only predicate-identity, baseline-receipt and freeze-chronology review, not a claim verdict or an axis-fit judgment. No correction data rows are supplied. No lane source, frozen artifact, route or judgment was changed; no counter, model server or judging runtime was invoked. No tools were installed or updated.

Evidence aliases below denote absolute paths:

- **P**: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/preregistration.json`.
- **C**: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py`.
- **R**: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/before/c1-base.json`.
- **O**: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/before/c1-base.out`.
- **D**: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlDuplicate/receipt.json`.
- **S**: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/SUMMARY.md`.
- **W**: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/dispatched-at.txt`.
- **J**: `/home/vgpnk/.omp/agent/sessions/-Projects-shokunin/2026-10-23T06-27-20-968Z_01a16771-4d08-7011-958e-0f9940db87a7/KamaR29.jsonl`.

## Principal finding: not literally ONE sentence in three places

C:4-5 claims the docstring is “the same sentence as preregistration.json C1.predicate and the label `unresolved` in the receipt”. These are not three copies of one sentence:

1. **P:14 contains two prose sentences.** The first defines the base statement, writing revision and HOLDS; the second combines UNRESOLVED, invalid-row penalties and an append-only override.
2. **C:7-40 expands those definitions into multiple sentences and six class-specific rules.** It is not a verbatim or whitespace-only rendering of P:14. C:42-43 separately states the target.
3. **R has no `predicate` or `receipt_label` field and no predicate sentence.** It has numeric `unresolved: 11`, `target: "mismatched_at_base >= 1 and unresolved == 0"`, and Boolean `met: false` (R:639-745). P:15 supplies the receipt-label mapping.

This is a literal-identity/provenance defect, not evidence by itself that a different target was used. P:14 explicitly incorporates the class checks from the counter docstring and the frozen extractor; the digest fixes the implementation. The core rules agree under that incorporation, subject to the precision differences below. A reader must not represent the three forms as byte-identical or treat the receipt's bare label as an independently complete definition.

## Inventory: wording and conditions across the three forms

### Shared structure and expansions

| Topic | Difference and evidence | Interpretation |
|---|---|---|
| Base/scope | P:14 gives one assertion found by the frozen extractor in the two named files at full base `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`; C:7-8 repeats that base/scope using a separate sentence. R:626 records the same full base, but not the definition. | Same base and file universe; receipt is an instance, not a third sentence. R's actual 69 extracted ids all begin with `SCORECARD.md:`; that does not contradict an extractor allowed to inspect both files. |
| Writing revision | P says the commit `git blame --line-porcelain` names for the line. C:9 spells out `<base> -- <file>`; C:128-137 actually uses BASE and the filename. R stores a full `W` for each statement rather than defining blame. | Expanded command, no observed revision-rule substitution. |
| HOLDS | P says “it HOLDS iff its class check … passes”; C says “A statement HOLDS iff its check passes”, then supplies each check. P lists `P pointer, H digest, N line count, C commit, T time, Q quoted output`; R has the same six class letters and a `holds` Boolean per listed statement. | Class names alone are not the full checks; P explicitly points to C for those checks. |
| P | C:11-12 adds lane-relative pointer forms `path:L`, `path:L-M`/en dash, excludes paths starting `../`, `/`, `~` or a URL scheme, and requires a blob at W with at least `max(L,M)` lines. None of this detail is written out in P's sentence or R's aggregate fields. | Incorporated expansion, not a new receipt condition. |
| H | C:13-15 adds a directly preceding backticked lane path, md5/sha256, at least eight hex characters, blob existence at W and **digest-prefix**, not necessarily full-digest, equality. | The generic word “digest” in P does not express these restrictions; R's observed values are concrete full digests where applicable. |
| N | C:16-18 adds the directly adjacent path/H binding and accepts either newline count or newline count + 1 for a nonempty unterminated last line. C:244-247 implements the two conventions. | Broader than a single conventional `wc -l` interpretation of “line count”; explicitly incorporated before freeze. |
| C | C:19-24 adds first hash in a Measured-commit cell, keyword-triggered hashes, 7-40 hex length, mixed digit/letter constraint for the keyword route, upstream/context exclusions, resolution to a lane commit and **strict** ancestry of W. | Commit existence alone is insufficient, and equality to W is rejected. P's short class label does not state this; R stores the resulting commit observations. |
| T | C:25-26 adds the accepted textual time forms and comparison with **committer**, not author, time of W; seconds may be absent. | More specific than P's word “time”; R records `time=… committed=…`. |
| Q | C:27-32 adds a 6-200-character single-backtick span, a digit, `=` or a space plus a listed word, command/prefix exclusions, verbatim matching and exclusion of the self-assessments, log and corpus evidence. | “Quoted output” is not unrestricted output checking. Its formal check is committed-text occurrence, not proof of execution or attribution to the purported command. Those limitations are already part of the incorporated rule; do not silently widen it. |
| Correction rows | P:14 says first cell `SA29:<sid>`, last cell the counter's printed observed value, “under the frozen heading”. C:34-36 additionally spells out **table row**, the exact heading `## Round 29 — self-assessment corrections`, and “exact string”. R gives row/valid/false counts and ids, not the parser rule. | No changed heading or value requirement was found in the core implementation. |
| Invalid corrections | Both prose forms list a holding/non-base statement, wrong observed value and duplicate sid, and add each false correction to unresolved. C:313-327 operationalizes validation and the penalty. R's `false_corrections` is a **list**, while stdout prints its **length**. | Representation differs, not the target. Duplicate counting has an ambiguity described below. |
| Append-only | Both prose forms say a tip SCORECARD not beginning with the base bytes makes **every** base statement unresolved; C:309-327 checks precisely that and still adds false-row penalties. R has `append_only: true`. | This is an explicit override to the earlier “iff it does not hold” formulation, not merely a condition on the 11 mismatches. S:17-18 records 69 unresolved for deletion/edit-in-place controls. Reading only the initial iff would be incomplete. SHONEN append-only is not required by either prose or code. |
| Target and label | P:15 is `unresolved`; P:19 says `mismatched_at_base >= 1 and unresolved == 0 at the measured lane tip (receipt field met)`; C:42 says the same formula “at the measured tip”; R:743 omits that prose context and stores the exact formula. C:341 computes the Boolean, not an alternative score. | Same operative conjunction; `met` is its Boolean evaluation, not a second independently calibrated target. |
| Execution boundary | C:43,46 explicitly distinguishes exit 0 (evaluated, whatever the count) from exit 2 (could not evaluate) and says committed objects only/no replace objects. P:18 prescribes a fresh clone of the lane remote and `--tip refs/heads/master`; the implementation also accepts other explicit repo/tip arguments. | Command/provenance requirements are not all enforced as target conjuncts. A successful process exit is not a met claim. Arbitrary `--tip` usage is not the prescribed measured command. |

### Implementation precision absent from, or different from, the prose

The following are additional identity-relevant qualifications, not proposed changes to the frozen extractor:

1. **P/H/N path grammar is narrower than generic `path`.** C:62-74 restricts these to lowercase extensions `md, py, sh, json, jsonl, tsv, txt, out, conf, cpp, yml, yaml, toml, err, log` and components matching `[\w.-]+` separated by `/`. Spaces and other punctuation are outside this grammar. P's sentence and C's class prose do not enumerate the whitelist. P uses a negative lookbehind to avoid embedded/absolute/scheme-like starts, and C:140-142 rejects the listed non-lane prefixes and `://`. The grammar is frozen via the extractor reference; it is not a general human assertion census.
2. **H/N exact lexical binding.** C:70-71 requires literal single ASCII spaces in the binding syntax, lowercase `md5`/`sha256`, lowercase `[0-9a-f]`, and a regex digest capture of **8-64** characters. C:13 says only `>= 8 hex`. That capture has no terminal hex boundary, so [INFERENCE] a longer adjacent hex run can be captured as a 64-character prefix rather than rejected as a whole token. Hex backticks are optional in the regex. N requires the literal plural `lines` and the opening ` (` form; the closing parenthesis is not required. These are omitted lexical details, including an upper capture limit absent from the docstring.
3. **C lexical/structural details.** C:73-74 and 146-163 use lowercase hashes and lowercase keyword text with one literal space; the optional opening backtick is on the hash, not the keyword. The table header is compared case-insensitively with `measured commit`, but the standalone form is anchored exactly as `Measured commit:`. The table-column state ends on a non-table line. These details are not written out in the docstring.
4. **C occurrence multiplicity and exclusion scope.** C:211 uses `t not in ctoks`, so repeated identical commit tokens on one line are deduplicated, including a keyword repetition of the first Measured-commit token. The docstring says “every” matching keyword token without stating deduplication. The upstream/context test (C:206-210) applies only to the keyword route; the first Measured-commit-cell hash (C:202-205) is appended without it. The docstring's trailing “unless” can be read as applying to both routes. These are a multiplicity difference and an exclusion-scope ambiguity, respectively.
5. **T year/parsing boundary.** C:72 recognizes only `20\d\d` years, whereas C:25 says `YYYY`. C:253-258 parses the matched value; a syntactically matched but invalid date/time raises into the counter's could-not-evaluate path (C:347-349), rather than yielding the advertised future-time failure label. No current baseline error is shown by this observation.
6. **Q `sh` prefix is a genuine prose/code difference.** C:29 lists excluded prefix `sh`; C:66 actually uses **`"sh "` with a trailing space**. [INFERENCE] a span such as `shell=1` passes the digit/equals and non-command-prefix extraction tests in code, but is excluded by a literal reading of the prose's `sh` prefix. This is a static counterexample, not a run or an added base statement. None of the 25 Q tokens opened from R starts with `sh`, so this specific counterexample is not an observed change to the frozen 69-statement base receipt.
7. **Q exact matching implementation.** C:65,219-223 uses case-sensitive listed words/word boundaries; C:260 uses `git grep -F -q -e`, not a regex search or full-line equality. Exclusion arguments are `:(exclude)SCORECARD.md`, `:(exclude)SHONEN.md`, `:(exclude)LOG.md`, `:(exclude)corpus` (C:67-68), whereas C:32 writes `corpus/**`. This reports the exact pathspec spelling difference, not a demonstrated difference for a corpus directory tree. There is no check that an occurrence was produced by the asserted command; any permitted committed-text occurrence suffices.
8. **Extraction is regex/line driven, not Markdown-semantic.** C:178-228 does not exclude fenced code, comments, table examples or quoted statements. Statement ids (C:178-184,225-228) include filename, class, a ten-hex SHA-256 line fingerprint (with a repetition suffix for repeated fingerprints), and class-local match index. The prose uses an opaque `<sid>` and delegates this identity machinery to the extractor.
9. **Correction parsing normalizes cell wrappers.** C:268-278 recognizes only column-zero `## ` headings and `|` rows. It strips cell whitespace and leading/trailing backticks before comparing ids/observations, so “exact string” is exact **after** that normalization. It requires no header/separator row, no fixed cell count, and no validated middle-cell statement text. It does not suppress rows inside code fences. A new H2 heading changes parser state; an H1 does not. These are implementation-level qualifications absent from the prose's ordinary “under the heading” wording.
10. **Duplicate penalties count later occurrences, then invalidate the sid.** C:315 counts a row as duplicate only if already in `seen`; C:322 removes that sid from valid corrections. D provides an observed counterexample to a symmetric reading of “duplicating another row's sid”: 22 correct-value rows (two per mismatch) produce **11**, not 22, false corrections, zero valid corrections, and unresolved 22. Each original mismatch is unresolved again and each later duplicate adds one. A reading making every member of a duplicate pair false would instead count 33 unresolved; that is not the frozen implementation. The zero/nonzero target outcome of that existing control is the same either way.
11. **Failure-label wording does not equal the actual printed observed value for several branches.** The docstring advertises `p:beyond-eof`, `h:digest`, `n:count`, `c:not-ancestor`, `t:future`. C:238-258 instead prints, respectively, `eof=<n>`, `<algo>=<actual digest>`, `newlines=<n> unterminated=<bool>`, `commit=<resolved hash> not-ancestor`, and `time=<seconds> committed=<seconds>`. Missing P/H/N blobs use the advertised `*:absent`; unresolved C and missing Q artifacts also match their advertised strings. A correction based on the advertised labels rather than the counter's actual printed observed value would be invalid. R's 11 mismatches use only `p:absent` (4) and `q:no-artifact` (7), so those five diagnostic-label discrepancies are not the observed values of this baseline's mismatches.

## Exact `before` comparison

Read-only `jq` compared the opened P, R and O bytes; the counter was not rerun.

- P `claims.C1.before.line` **equals O's first line exactly**, without its line terminator:

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 2aa46e2481d2
```

- **It is not the entire O file.** O is 141 UTF-8 bytes and contains the additional second line `exit 0`, followed by a newline. Comparing `before.line + "\n"` with the entire O returned false. This is an omitted wrapper-status line, not a count mismatch.
- P `before.receipt` identifies R; P `before.by_class` exactly equals R `by_class`: C=27, H=2, N=2, P=10, Q=25, T=3.
- P base and counter digest exactly equal R base and counter digest. The 12-character stdout tip is the prefix of R's full base/tip, not a different revision.
- R has 69 statements, 11 mismatches, append-only true, zero row/valid counts, an empty false-correction list, unresolved 11, and `met: false`. The declared formula independently evaluates to false from those fields. JSON `false` versus stdout `False`, a full versus abbreviated hash, and an array versus its printed length are representational differences, not changed conditions.

## Freeze and dispatch chronology

The observed records put the freeze before **all 14 control seats and all 32 wave-1 seats** in these batches:

| Event | Recorded UTC time | Opened evidence |
|---|---|---|
| Freeze commit `827d136546b85059a984b34970f5b493d9a71290` | **2026-10-23 10:55:43Z** | Read-only `git show --no-patch --format=fuller --date=iso-strict` reports CommitDate `2026-10-23T07:55:43-03:00`; AuthorDate is separately `2026-10-23T06:55:34-03:00`. Use committer time for this comparison. |
| One task call containing all 14 controls/reference seats | **2026-10-23T10:58:50.336Z** | J assistant event `3df1bb91`, tool call `toolu_01QXfiZt4xYUqDYz2E9SDdZ6`; selected raw event names all 14 seats. |
| That call's spawn result | **2026-10-23T10:58:50.348Z** | J toolResult names the same 14 and says `Spawned 14 background agents using executor, mutation-tester.` |
| Control receipts commit `35b90184f638ab6a4149092b93143c7a2b873787` | **2026-10-23 11:11:28Z** | Read-only git log gives its parent as the freeze commit. |
| Wave 1 call | **2026-10-23T12:02:03.361941+00:00** | W; the raw J assistant `eval` call at `12:02:03.360Z` awaits `tool.task(payload)`. |
| Wave 1 result | **2026-10-23T12:02:07.612Z** | J toolResult contains `Spawned 32 background agents`; the opened saved spawn result names all 32 including this critic. |

There was an earlier un-awaited `tool.task` expression at 12:01:58.578Z whose result was a coroutine object, followed by the awaited call above. It does not supply evidence of an earlier successful seat dispatch, and even that attempted expression is after the freeze.

**Two-second prose discrepancy:** S:4 labels the freeze as `10:55:45Z`; the immutable commit metadata says `10:55:43Z`. The raw control call is also more precise than S's rounded `10:58Z` or the assignment's approximate `11:00Z`. Neither discrepancy reverses the recorded order. Git metadata and session timestamps establish the available recorded chronology, not independently authenticated wall-clock time.

Read-only `git log --reverse --diff-filter=A` identifies the freeze as the introduction commit for P/C/R/O. `git ls-tree` shows all four objects in that commit. A scoped `git diff --exit-code` against the freeze for these four paths returned no diff. SHA-256 of C both from the freeze object and the opened checkout is exactly:

```text
fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383
```

The selected timing records and freeze object ids are copied into `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/CriticPredicateIdentity/timing-evidence.json` so the evidence does not depend solely on a transient session pointer.

## Smallest safe correction and classification

1. **Fixable reporting defects:** state that P incorporates a frozen extractor/docstring and that R records an instance of its target; do not claim one literal sentence appears three times. State “first counter-output line matches” rather than “the complete output file matches”, retain the `exit 0` wrapper line when quoting the complete O, and cite freeze committer time 10:55:43Z with the two-second summary discrepancy disclosed.
2. **Frozen precision limits:** disclose the `sh`/`sh ` mismatch, undeclared lexical restrictions, C multiplicity/exclusion ambiguity, duplicate-row interpretation and printed-diagnostic differences as limitations. **Do not edit P, C, the target, baseline or correction data to eliminate them in this claim.** P:20 forbids that post-freeze repair.
3. If literal byte-identical three-way predicate wording or changed extraction semantics is required, that requires a separately frozen future claim, not a retroactive narrowing or a second authority for round 29. This seat does not decide whether these limits are admission-blocking; that remains the canonical judge's decision.

No axis tradeoff or claim saturation was measured here. The evidence supports recorded pre-seat freezing and agreement of the baseline's operative target fields, while falsifying the literal three-copy sentence claim. Nothing in this review independently establishes that the 11 recognizer mismatches are 11 substantively false self-assessment assertions.
