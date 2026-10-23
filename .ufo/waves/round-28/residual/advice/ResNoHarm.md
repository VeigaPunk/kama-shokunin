# ResNoHarm — round-28 residual whole-round harm review

Reviewed interval: `4179301f7516ad667509d54b5ebfe0a70a002d5b` → `9ce5bd377562117b3340709639d5d0eafe791bc1`.

**Critic assessment, not admission or a score decision:** append-only preservation holds, and no regression of an existing serving tool was found. An unqualified all-axis no-harm statement needs correction: the new numeric-conversion explanation is false for floating-point fields, and three displayed source-digest abbreviations are wrong. These are fixable text defects. A separate inherited raw-hash-key limitation also makes the new binding description too broad for arbitrary receipts.

## Per-axis assessment

| Axis | Does landed material lower it? | Evidence |
|---|---|---|
| Depth | **Localized lowering in the explanation (F1); no destruction of earlier held text.** The table's scope is appropriately one observed point per field, but its new introductory statement incorrectly says fractional values are truncated without limiting that claim to integer fields. | False general statement: `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md:1158-1160`. Direct stored counterexample: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/DataG08/adapt_decay_0.5.raw.json:1` has `adaptive_decay: 0.5`. Appropriate pointwise limit: `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md:1151-1157`. |
| Coverage | **No lowering found.** All five append-only surfaces have zero deleted lines, including every source-changing commit in the interval. Existing open frontiers are retained, not silently declared solved. | History and file census below; `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/README.md:429-434` leaves other endpoints, grammar transformation, other launch bounds/builds/engines, K05 and consumer reconciliation open. `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md:274-276` keeps the boundary cost and missing F3 implementation explicit. |
| Operability | **No existing-tool lowering found by static review and retained evidence.** The only modified existing counter adds acceptance conditions rather than removing old structural checks. New registry and echo tools implement their stated narrow contracts; their results must not be promoted to stronger guarantees. | `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/count-c2.py:305-348,365-381`; retained parity and negative cases in `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/ExecCountC2Fix/demo-run-all.out:4-28`. Registry predicate: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/gate-registry-check.py:113-128`. Echo cleanup/output refusal: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/echo-recheck.py:383-419,441-479`. F3 below is inherited, not a newly weakened predicate. |
| Freshness | **No lowering of dated observations found.** New evidence remains pinned to the fixture; nothing refreshes consumer identity by implication. The echo recheck is an executable old-build replay, not validation of a future release. F2 is an erroneous identity citation, not evidence that the pinned bytes changed. | Fixture and non-health limits: `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md:1137-1150`; recheck cadence: `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/echo-discriminating-counters.md:1-3`. Fixed paths/pins: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/echo-recheck.py:58-71,280-289`. Retained replay time and shutdown: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/ExecEchoRecheck/run1.json:20-25,132-145`. |
| Calibration | **Localized lowering from F1/F2 and overbroad binding wording in F3.** Important counter limitations otherwise remain candid: A1 was data-informed, the author does not promote depth, and a source-informed writer can meet the counter without running the server. | `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-28.md:148-169`; held scores: `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:1415,1432-1435`. The new row also expressly limits the gate to path occurrence: `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md:1227`. |
| Adjacency | **No lowering found.** The extension concerns this server's request handling, not credentials, route mechanisms, sampling quality, served identity or registered endpoint health. No sibling authority was rewritten. | Existing refusals: `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md:27-31,1090-1098`; added exclusions: `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md:1147-1150`; province boundary: `/home/vgpnk/Projects/shokunin/kama-shokunin/PROVINCE.md:109-115`. |

## Whole-round and non-wave file census

The assigned whole-round `git diff --stat` reports **759 files, 74,615 insertions, 27 deletions**. All 13 changed tracked paths outside the round-28 wave directory were reviewed, including the complete new registry, complete new tools and the full modified older counter:

| Absolute path | Added / deleted | Review disposition |
|---|---:|---|
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/count-c2.py` | 217 / 25 | Re-derivation repair; existing checks retained; inherited hash-key gap qualified below. |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/LOG.md` | 31 / 0 | Append-only; wrong displayed digest suffix (F2). |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/PROVINCE.md` | 8 / 0 | Additive fixture scope; no identity or sibling-owner transfer. |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md` | 39 / 0 | Append-only; depth held at 7; post-data amendment disclosed. |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md` | 95 / 0 | Additive table/registry; F1/F2 and binding qualification below. |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md` | 15 / 0 | Append-only supersessions; does not claim an implemented F3 leg. |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/README.md` | 13 / 0 | Append-only frontier disposition; unresolved surfaces remain open. |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md` | 34 / 0 | Adds S140–S173 without rewriting existing rows. |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/echo-discriminating-counters.md` | 5 / 2 | Replaces non-runnable recheck guidance and qualifies boundary scope; earlier limits retained. |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-28.md` | 198 / 0 | Reports counter chronology, limits and no depth promotion. |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/registry/request-field-outcomes-r28.json` | 965 / 0 | 34 registered points; generic conversions remain registered but uncounted under A1. |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/echo-recheck.py` | 483 / 0 | New pinned replay; refuses existing output/sidecar; does not test a replacement release. |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/gate-registry-check.py` | 153 / 0 | New occurrence-only check, not full registry-row validation. |

The 27 deleted lines are exactly 25 in the older counter and 2 in the non-append-only knowledge entry. The required ledgers have **zero deleted lines**. Read-only per-commit history additionally shows:

- `e49b4cf77046024551ba83d490ef83d9dee061ed`: 15/0 in `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md`; 34/0 in `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`.
- `9ce5bd377562117b3340709639d5d0eafe791bc1`: 31/0 in `/home/vgpnk/Projects/shokunin/kama-shokunin/LOG.md`; 39/0 in `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md`; 13/0 in `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/README.md`.
- No other commit in the interval changes those append-only surfaces, nor the root-level README/SOURCES/QUALITY pathspecs.

The retained source guard independently reports all 34 additions and no violation: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/final/sources-append-only-final.out:1-36`. That receipt alone is not substituted for the per-commit history inspection above.

## F1 — fractional truncation is incorrectly generalized to floating-point fields

**False text:** `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md:1158-1160` says that numbers are converted to the field's C++ type and then states, without an integer-type qualification, “a fractional value is truncated toward zero first”.

**Strongest local counterexample:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/DataG08/adapt_decay_0.5.raw.json:1` stores `adaptive_decay = 0.5`, not 0. Further, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/DataG08/adapt_decay_0.995.raw.json:1` is a 400 bounds error naming `0.995000`, not a successful check of a truncated zero.

The pinned implementation explains both: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.h:47-65` retains a templated field type; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp:171-173,531-545` uses floating limits for adaptive decay and obtains `T`, not an unconditional integer, before checking bounds.

**Impacted axes:** depth and calibration. This is a fixable explanatory defect, not a counter-design tradeoff. The counted table cells need not change.

**Exact corrected replacement for the three explanatory lines:**

> Numbers are converted to the field's C++ type before bound checking or clamping. Integer-typed fields truncate fractional JSON values toward zero before that check; float-typed fields retain fractional values subject to float32 rounding. Bounds apply to the converted value, not necessarily the JSON number as written.

## F2 — three displayed schema digest abbreviations have the wrong suffix

**False text locations:** `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md:1145,1224` and `/home/vgpnk/Projects/shokunin/kama-shokunin/LOG.md:1811` use `1f9d7b73…0050`.

A read-only SHA-256 calculation of `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp` returned:

```text
1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050
```

The full pin agrees at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/count-c1.py:88-90` and `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-28.md:74-80`. Its last four characters are **4050**, not 0050. The executable pin is correct; this is false displayed provenance, not a demonstrated wrong-input measurement.

**Impacted axis:** calibration; freshness evidence identity should also be cited accurately.

**Smallest safe correction:** use `1f9d7b73…4050` at both SKILL locations. Because LOG is append-only, do not rewrite its old line; append this exact correction instead:

> Round-28 source-digest correction: the server-schema.cpp SHA-256 is `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050` (`1f9d7b73…4050`). The earlier abbreviation `1f9d7b73…0050` is a transcription error.

## F3 — inherited missing-hash-key gap limits the new “sha256-bound” description

**New overbroad descriptions:** `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md:1226`, `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-28.md:64`, and `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/count-c2.py:31-47` describe re-derivation from the raw bytes bound by each cell's hashes without stating that hash-key completeness is not enforced.

**Static counterexample, not executed:** the committed K3 raw map is at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/final/context-capacity-receipt.json:260-265`. Remove only its `raw_props` member. The map remains nonempty; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/count-c2.py:148-161` checks only supplied members and never requires `raw_props`. Yet `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/count-c2.py:239-242,273-280` still derives from that props body. [INFERENCE] With all other bytes unchanged, observation and binding remain true although the props input has no receipt hash. This is distinct from the already-disclosed coordinated raw+cell+hash rewrite: here a required input can simply have no hash entry.

**What holds:** the old implementation also iterated only supplied raw members; this is **not a new acceptance-set weakening**. The repair adds raw re-derivation and rejects the retained forged-cell and forged-raw mismatch cases. It does not establish complete hash coverage for arbitrary receipts.

**Impacted axis:** calibration of the new repair description, not a newly demonstrated operability regression.

**Smallest safe correction without changing an instrument:** qualify the repair's binding descriptions with this exact text:

> Capacity and request-outcome values are re-derived from present raw bodies and logs and compared with receipt fields. Every supplied hash in a nonempty raw object must match, but the checker does not require every named raw-hash key. Complete SHA-256 coverage therefore depends on retaining the full raw-hash map; argv and absolute timestamps remain receipt-internal checks.

If complete hash coverage is instead required as executable behavior, the minimal code change is to require all `RAW_FILES` keys after the nonempty-dictionary check in `cell_raw_bound`. That would be a separate repair requiring updated instrument identity and evidence, not something this read-only critic has applied or verified.

## What survives the attacks; what is not established

- **Numerical receipts hold as recorded, not rerun here.** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/final/c1-9ce5bd37.out:1-3` reports A1 `registered 34 counted 26 target 18 met True`, and `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/final/c1-A0-9ce5bd37.out:1-3` reports A0 34/34. Those numbers do not test the correctness of surrounding prose: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/count-c1.py:43-44,468-472` checks only a meaning-cell word count beyond counted cells.
- **No earlier SKILL identity rule is displaced.** Completion settings are expressly separated from props defaults and from identity/health at `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md:1147-1150`; earlier served-context guidance remains at `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md:677-690`. A bounds-specific 400 is not asserted to explain every old 400: `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md:1190` explicitly says “not every 400”.
- **The registry gate is deliberately weaker than its display name.** `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/gate-registry-check.py:29-34,124-128` accepts any path occurrence, including prose; the new SKILL row discloses this. The final `registered 5 unregistered 0` at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/final/gate-registry-final.out:1-2` proves path naming, not complete registry rows, pinned values or semantic admission.
- **The echo tool is not a release-upgrade validator.** It checks fixed b11755 pins before starting and refuses mismatches. A newer build cannot become refreshed evidence through a `same 6/6` result from this old fixture; the entry and tool explicitly name the pinned build. The source/criterion corrections retain the missing F3 limitation and 3/17 boundary cost rather than hiding either.
- **Counter chronology is not repairable by a wording cleanup.** The author records that a type-only policy met A0 at 20/52 and that A1 followed data scoring; see `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-28.md:148-169`. These are substantive limits for canonical judgment, not permission to treat the A1 count as pre-data-frozen depth evidence. No depth promotion is recommended by this report.

## Method and execution bounds

Read the assigned lesson first, then the Godspeed skill and operator rules. Inspected the assigned diffstat, every non-round-28-wave diff, complete changed tool implementations, the new measurement counter, pinned numeric-field code, relevant earlier SKILL boundaries, and retained receipts. Read-only Git commands and the single SHA-256 calculation were each wrapped in `timeout`. No tests, gates, counters, servers, model-serving processes, alternative runtimes, installs or updates were run. No tracked file, state file or sibling lane was changed; only this report was written.
