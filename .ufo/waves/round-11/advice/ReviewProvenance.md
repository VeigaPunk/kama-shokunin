# ReviewProvenance — C1 design review against baseline truth

Seat: ReviewProvenance (reviewer, author-advisor; not an outside verifier).
Actual review access date: **2026-10-20 UTC** (`date -u` → `2026-10-20T02:14:53Z`). The steered round label 2026-10-19 is kept only as the round heading; no verification in this report is dated 2026-10-19. Historical observation dates below are quoted from the files and are not re-observed.
Tools installed or updated: none. Read-only commands only (`date -u`, `grep`, `sed`, `od`, `sha256sum`, `wc`). No builds, tests, lint, or formatters. No endpoint, service, or host config contacted. Corpus not modified.

## Scope

"Three baseline files" was not enumerated in the spec. I chose the three that span the distinct provenance risk classes in `.ufo/waves/round-11/legacy-baseline.json`:

- `corpus/knowledge/served-model-identity.md`: undated command outputs.
- `corpus/knowledge/endpoint-identity.md`: mixed-date decision guide with round-10 correction blocks.
- `corpus/knowledge/listener-census.md`: dated census with its own measurement header.

Baseline integrity check: all 9 legacy files match the recorded SHA-256 prefixes and byte counts in `legacy-baseline.json`. Sizes are 7595, 39951, 18448, 7428, 19263, 3914, 34489, 1221, 6067 bytes.

## Finding 1 — Appended `verified-at` cannot make an endpoint fresh (verified)

- `corpus/README.md:9-10`: each entry is "a **dated census record** of what was observed on its citation date — never proof that an endpoint serves today."
- `corpus/QUALITY.md:3-4`: "Existing dated knowledge is history, not proof of a present responder."
- `corpus/QUALITY.md` KQ1 rejects a "configured URL, listener, `/health` answer, completion success, or September MODEL_OK" offered as present served-model identity.
- `SKILL.md:44-47` (sample dated 2026-10-15): "the bounded socket query found no listener on the two registered ports."

Consequence: a provenance line can only state what was observed and when. The review date proves that the provenance text was checked, not that the endpoint is live. Writing `verified-at: 2026-10-20` against endpoint prose would be exactly the inflation KQ1 rejects.

## Finding 2 — Per-file state of the three baseline files

| File | Bytes / last byte | Observation-date evidence in file | Present-tense / undated risk | Current state evidence outside file |
|---|---|---|---|---|
| `served-model-identity.md` | 1221; last byte `\n`; starts `\n\n### Exact readiness-field probes` (no H1) | None. Outputs at lines 13–22 and 30–36 carry no timestamp. Line 5: "their outputs are exact for those commands." | "exact" applied to undated output | `SKILL.md:44-47`: no listener on the registered ports (2026-10-15 sample). Shape of the `/slots` output (2 slots, `n_ctx` 16384) matches `listener-census.md` §5 C2 (2026-09-28). That match is **[INFERENCE]**, not a recorded date. |
| `endpoint-identity.md` | 19263; last byte `\n`; H1 at line 1 | No single observation date. Line 23: "Fresh loopback smoke output excerpt:" is undated. Nine `2026-10-19` tokens, all in correction lines 131–147. | "Fresh" (line 23); present-tense "live" used about endpoints in body | Correction A06 (line 143): "the claimed live llama-server at 34113 and Janitor 8080 pin are historical as well." |
| `listener-census.md` | 34489; **last byte `*` (no LF)**; header line 3 | Line 3: "**Measured:** 2026-09-28 ~22:47–22:52 -0300, host `plazir27`, live on-box probes." §7.1 records a same-session delta. | Line 115: "*historical: 34113 connection-refused today*". The word "today" has no date in the row; the file also contains 2026-10-14 tokens (line 115 "re-measured 2026-10-14"). Reading "today" as 2026-10-14 is **[INFERENCE]**. | `consumer-registry.md` errata (2026-10-14): 34113 "connection-refused today." |

## Finding 3 — Safe verified-at phrasing for the three files

These phrases state the actual review date (2026-10-20 UTC) separately from historical observation dates. Use them as drafts for the parent integration. Field placement and parser rules are in Finding 5.

**`served-model-identity.md`**
```
source: local command outputs quoted in this file (lines 10-36); no path:line census row
verified-at: not recorded in file (undated outputs, lines 13-36); provenance review 2026-10-20 UTC, no endpoint contacted; outputs are historical samples, not current serving state
recheck: bash tools/kama-probe.sh check --json --port 34113 --expect Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS --id model-match  (run only under an authorized probe; the file's own curl lines 10 and 27 are read-only loopback GETs)
```

**`endpoint-identity.md`**
```
source: tools/kama-probe.sh verdict vocabulary and rules (lines 9-19); listener-census.md:49-66 for live-evidence examples
verified-at: mixed — body probe excerpts undated (line 23 "Fresh loopback smoke output excerpt" has no date); correction blocks lines 131-147 dated 2026-10-19 check anchors shape-only; provenance review 2026-10-20 UTC; no endpoint contacted; endpoint claims are historical
recheck: bash tools/kama-probe.sh check --json   (registry mode; authorized run only)
```

**`listener-census.md`**
```
source: listener-census.md §5 command ledger C1–C19 (path:line); not an S-row in SOURCES.md
verified-at: 2026-09-28 ~22:47–22:52 -0300 (line 3, live on-box probes); rows 34113/8080 verdicts are historical; provenance review 2026-10-20 UTC, no re-probe
recheck: sudo -n ss -ltnp | awk '$4 ~ /127\.0\.0\.1|0\.0\.0\.0/ {print $4, $NF}'   (line 321; read-only; authorized run only)
```

Each appended block needs a leading LF for `listener-census.md`, because the file ends in `*`. Without it, the first field fuses to the last table line (`*verified-at:`) and fails a `^verified-at:` check.

## Finding 4 — Consumer risks of appended metadata

1. **Date-harvesting inflation.** Seven of nine legacy files contain `2026-10-19`, all in correction lines, and none is an observation date: `alias-endpoint-normalization` 4, `consumer-registry` 8, `cross-lane-scope` 14, `drift-timeline` 2, `endpoint-identity` 9, `free-tier-provider-limits` 2, `snapshot-history` 7 (line counts). A "latest date in file = verified-at" rule would return 2026-10-19 for these files, and 2026-10-20 if the appended review date is included. `listener-census.md` and `served-model-identity.md` have no 2026-10-19 tokens. Their latest token would be 2026-09-28 or none. Any date-harvesting consumer must exclude `## Corrections` blocks and any review-date token.
2. **Self-satisfying field match.** The three new field names appear **zero** times in all nine files (checked as unanchored substrings `verified-at|recheck:|source:`). The measure should use `^(source|verified-at|recheck): ` anchored to line start. An unanchored match would pass a correction line that quotes the phrase.
3. **Present-tense prose above the appended block.** Appended metadata sits at EOF and does not override body text. Examples: `endpoint-identity.md:23` "Fresh loopback smoke output excerpt"; `listener-census.md:3` "live on-box probes" (dated 2026-09-28). Readers who stop at the top see undated present-tense claims. Original bytes must stay unchanged, so this cannot be fixed by editing the body. The residual risk should be stated in the lesson.
4. **Template mismatch.** Round-10 files put `source/verified-at/recheck` at lines 2–4 after the H1 (`gguf-runtime-compatibility-boundary.md:2-4`, `runtime-health-surface-matrix.md:2-4`, `serving-metrics-crosswalk.md:2-4`). The legacy appended block is at EOF. That is acceptable for correction-style addition under QUALITY KQ7, but a header-position checker would miss it. Pick one placement rule and state it in the measure.
5. **Vendor phrase misuse.** The round-10 phrase "vendor/spec docs opened; no local runtime contacted" is safe only where sources are S-rows in `SOURCES.md`. Do not reuse it for local census or probe files. `source:` for legacy files must cite `path:line` or a command ledger, not a new S-row (QUALITY KQ6 limits S-rows to opened vendor/spec pages).
6. **Recheck executed by tooling.** `recheck:` strings are commands. A future automated checker must not run them. Round 11 forbids network and host commands, so `recheck:` must be descriptive text unless a later authorized round runs it.
7. **Gaming the count.** A block of `verified-at: 2026-10-20` with no scope passes a presence count while carrying no observation date. Minimal negative control: a legacy file whose `verified-at` value lacks an observation-date or "historical" scope token must be flagged as freshness inflation, even though the field is present.

## Finding 5 — Parser and placement rules for the measure (recommendations)

- Anchored field lines: `^(source|verified-at|recheck): ` multiline.
- Require a review date token (2026-10-20) and a historical scope token ("historical", "not re-probed", "no endpoint contacted") inside `verified-at`.
- Do not parse `2026-10-19` from correction blocks as an observation date.
- Verify byte prefix equality against `legacy-baseline.json` SHA-256 over the original length only, and require that the appended region begins with LF when the original does not end in LF.

## Verification gaps

- Not checked: `consumer-registry.md`, `cross-lane-scope.md`, `alias-endpoint-normalization.md`, `drift-timeline.md`, `free-tier-provider-limits.md`, `snapshot-history.md`. Only the grep counts above were taken from them.
- The `today` = 2026-10-14 reading in `listener-census.md:115` is an inference from in-file tokens and the registry errata, not a recorded date.
- `endpoint-identity.md` smoke-excerpt origin is unknown. Its date cannot be recovered from the file.
- No endpoint was contacted, so no liveness claim is made here. All endpoint statements are historical.
