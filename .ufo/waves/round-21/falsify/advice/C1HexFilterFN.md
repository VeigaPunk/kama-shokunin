VERDICT: partial - the 7-hex false-negative class is real; lesson discloses the heuristic, SKILL does not state its limit plainly
Target: C1 `checkable_abbrev` in `tools/report-landing-audit.py` at a6617149722c73d90e142fbdc8154d6967055f7e.
Axes: calibration 7 (C1 affected); operability 8/C2 unaffected.

Counterexample
- `ABBREV` admits 7–40 lowercase hex tokens (source lines 60, 188). The filter checks a Landed token only when its length is 40 or it contains both a decimal digit and `[a-f]` (126–130).
- Therefore a missing short all-hex-letter token such as `deadbee` and a missing short all-digit token such as `1234567` are excluded from `lookup`; neither produces `landed-unresolved`. This is a real false-negative class, not merely a theoretical parser edge.
- Important nuance: `cited` is built from every `ABBREV` token, before filtering. An all-digit real prefix can still satisfy the later `landed-omitted` prefix test (188–199); it is accepted for coverage, but not validated for resolution. Full 40-hex tokens are always checkable.

Executed evidence
1. On the scratch clone at the target revision, `python3 tools/report-landing-audit.py --selftest` exited 0; stdout ended `selftest cases=32 failed=0` and included `ok hex-words-not-citations`. The selftest asserts `defaced` and `1234567` are uncheckable and `deadbee1` is checkable (443–445); it does not exercise unresolved all-letter/all-digit tokens end-to-end or a real all-digit citation.
2. Temp-repo demo used a single required commit `4671357eba93f181da7997ede3fcb090308b8bb0` (`round-1:`; 7-hex prefix `4671357`). The executed command `printf 'deadbee\n1234567\n4671357\n' | git -C /tmp/kama-r21-C1HexFilterFN/demo3/lane cat-file --batch-check && printf 'deadbee\n1234567\n4671357\n' | git -C /tmp/kama-r21-C1HexFilterFN/demo3/fleet cat-file --batch-check` exited 0; lane output was `deadbee missing`, `1234567 missing`, and the full commit as `commit`; fleet returned all three missing.
3. The executed audit with Landed entries `deadbee`, `1234567`, and real `4671357` was `/usr/bin/python /tmp/kama-r21-C1HexFilterFN/lane/tools/report-landing-audit.py --lane-repo /tmp/kama-r21-C1HexFilterFN/demo3/lane --fleet-repo /tmp/kama-r21-C1HexFilterFN/demo3/fleet --branch master --lane kama --rounds 1 --report 1=/tmp/kama-r21-C1HexFilterFN/demo3/with-real.md --no-errata --json`; it exited 0, stdout had `defects: []`, all five defect counts zero, `required: 1`, `status: clean`. The same command with `--report 1=/tmp/kama-r21-C1HexFilterFN/demo3/without-real.md` exited 1 with `landed-omitted` for the full required commit and `landed-unresolved: 0`. Thus both fake tokens are silently ignored while the real numeric token counts for coverage. The temporary repositories were deleted after the probe.
4. Executed probability calculation exited 0 and printed: all-digit `10000000/268435456 = 3.725290%`; all-letter `279936/268435456 = 0.104284%`; disjoint union `10279936/268435456 = 3.829575%`.

Probability interpretation
For a uniformly distributed 7-hex prefix, the skipped share is `(10/16)^7 + (6/16)^7 = 3.829575%`: decimal-only and a–f-only are disjoint. This is a per-random-7-hex-prefix estimate, not an observed rate among real report citations or Git's actual unique abbreviations. [INFERENCE] Under the usual uniform-hash model it estimates the chance a genuine 7-character hash prefix falls into the skipped classes; the rate declines exponentially for longer prefixes. The 40-character case is exempt from this blind spot.

Documentation judgment
- `corpus/lessons/round-21.md:76–77` explicitly says “hex words and pure numbers not checked as citations”; this is honest disclosure of the false-positive-avoidance trade-off. `:107` also excludes prose correctness from scope.
- `SKILL.md:683` only lists “hex words” among selftest coverage; it does not state pure-number filtering or explain that unresolved hash-like tokens in those classes evade checking. Neither document quantifies the 7-hex class or clarifies that real numeric hashes still count toward omission coverage. So disclosure exists in the lesson, but operational limitation is incomplete in the persistent skill.

Smallest safe correction
Do not pretend token shape can distinguish a numeric/letter-only hash from prose. Keep the behavior only with a precise scope note in SKILL and lesson: unresolved Landed abbreviations are detected only for full 40-hex or mixed digit/[a-f] tokens; short a–f-only and digit-only tokens are unchecked (while still eligible for omission coverage). Add an end-to-end selftest for missing `deadbee`/`1234567` and a real numeric prefix. If complete unresolved-citation coverage is required, introduce explicit hash markup/convention or check every hex token and accept the corresponding prose false positives; the present data does not choose between those product trade-offs.

Tools installed/updated: none.
