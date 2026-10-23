VERDICT: partial — X1 adds reusable codification, but the pre-round lane already prescribed decoded-request checks and recognized message splitting, so a wholly new-rule novelty claim does not hold.

## Scope and axes

Advisory critic evidence only, not admission, a score move, or the claim's verdict. Primary impacted axis: **calibration**, specifically truthful prior-state attribution and distinguishing new knowledge from promotion of existing lessons. **Depth** gains no new server-error repertoire from this entry; no adjacency improvement was evaluated.

Reviewed the required plan and round-27 lesson first. Historical searches cover `SKILL.md`, all `corpus/` (including `corpus/QUALITY.md`, knowledge and lessons), and round-26/27 preregistrations at `a720399e` and attempt-3 start `0ec32cac`. Neither historical root contains a root-level `QUALITY.md`; the quality bar is `corpus/QUALITY.md`.

## Strongest counterexample

**The decoded-value rule is already explicit method knowledge at the pre-round base, not merely a buried shortcut receipt.**

- `a720399e:corpus/lessons/round-26-verifier-spotcheck.md:234` says: “Before data, the next counter must compare signatures against every JSON-decoded request string value,” then requires coverage of warning/file-content echoes and a committed shortcut-control receipt per class before data. Its heading at :231 is “Routed defects (lane fixes next round).” This is a prescriptive rule in the lane corpus, not just observed round output.
- `a720399e:corpus/lessons/round-26.md:80` likewise says: “A next counter should add a per-row healthy control with the same argv, decoded-request and file-content echo checks, port reuse, a pin on the server library and a cleared environment.”
- `a720399e:SKILL.md:1070-1072` already distinguishes raw JSON escaped quotes from decoded `error.message`; :1076-1078 warns that the count alone is not proof because an echo shortcut with no error knowledge also meets the counter.
- `a720399e:corpus/lessons/round-26-verifier-spotcheck.md:106-113` already explains the leading `\u00XX` escape, decoding before echoing, and “one generic validation error plus 12 arbitrary strings.” This is historical evidence explaining the rule, not a new observation of this review.

**The frame finding needs a narrower distinction.** At `a720399e`, round-26 preregistration :26 names “one message split into several rows”; :12 already says “one fault, one counted row,” and :29 describes its earlier split-message amendment. These establish prior anti-splitting intent, but are not the precise message-minus-signature equivalence rule. The explicit normalized-frame rule is present in round-27 preregistration at `0ec32cac:12,34,49`, before this attempt's new knowledge entry. Treat that as **round-27 evidence/design**, not evidence that the precise algorithm existed before round 27.

The plan's narrow observation that `QUALITY.md` held no echo rule is supported by the searches. It does **not** establish that the lane's knowledge lacked the decoded-value principle: the base lesson already states it directly.

## Exact commands and observed outputs

All commands below ran against `/home/vgpnk/Projects/shokunin/kama-shokunin`; all completed successfully, exit **0**. The first two are the requested search and its base counterpart. Output below is trimmed; the complete hit-location inventory is classified in the next section. No historical receipt was regenerated.

```sh
ulimit -v 1048576 && timeout 60s git -C /home/vgpnk/Projects/shokunin/kama-shokunin grep -n -i -E 'decod|escape|echo|frame' 0ec32cac -- SKILL.md corpus .ufo/waves/round-26/preregistration.json .ufo/waves/round-27/preregistration.json
```

144 matching lines, including:

```text
0ec32cac:.ufo/waves/round-27/preregistration.json:34:    "message-frame": "one error message frame with many different embedded literals (the r26 CriticShortcutRows shape) -> at most one row per frame",
0ec32cac:SKILL.md:1077:echo shortcut with no error knowledge also meets this counter
0ec32cac:corpus/lessons/round-26-verifier-spotcheck.md:234:2. Counter F2: `count-c1.py:384` checks echo on raw bytes only. Before data, the next counter must compare signatures against every JSON-decoded request string value, and must also cover F1 (warning lines) and F3 (file-content echo). Commit one shortcut-control receipt per class before any data seat. If a control seat is refused, the receipt slot is unfilled and data waits.
```

```sh
ulimit -v 1048576 && timeout 60s git -C /home/vgpnk/Projects/shokunin/kama-shokunin grep -n -i -E 'decod|escape|echo|frame' a720399e -- SKILL.md corpus .ufo/waves/round-26/preregistration.json .ufo/waves/round-27/preregistration.json
```

134 matching lines, including:

```text
a720399e:.ufo/waves/round-26/preregistration.json:26:    "shortcut keyed on ids or labels (rows reusing signatures the lane already holds; request-echo; one message split into several rows)"
a720399e:corpus/lessons/round-26-verifier-spotcheck.md:109:- `count-c1.py:384` checks echo against the raw request bytes. The server
a720399e:corpus/lessons/round-26-verifier-spotcheck.md:110:  decodes JSON before echoing, so `e_not_echoed` is defeated.
a720399e:corpus/lessons/round-26-verifier-spotcheck.md:234:2. Counter F2: `count-c1.py:384` checks echo on raw bytes only. Before data, the next counter must compare signatures against every JSON-decoded request string value, and must also cover F1 (warning lines) and F3 (file-content echo). Commit one shortcut-control receipt per class before any data seat. If a control seat is refused, the receipt slot is unfilled and data waits.
```

Historical surface identity and chronology:

```sh
ulimit -v 1048576 && timeout 60s git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --name-status a720399e 0ec32cac -- SKILL.md corpus QUALITY.md .ufo/waves/round-26/preregistration.json .ufo/waves/round-27/preregistration.json
```

```text
A	.ufo/waves/round-27/preregistration.json
```

```sh
ulimit -v 1048576 && timeout 60s git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree a720399e -- SKILL.md corpus QUALITY.md .ufo/waves/round-27/preregistration.json && printf 'EXIT=0\n'
ulimit -v 1048576 && timeout 60s git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree 0ec32cac -- SKILL.md corpus QUALITY.md .ufo/waves/round-27/preregistration.json && printf 'EXIT=0\n'
```

Both list the identical SKILL blob `186906468b36f94193a67878059840a3ec6c5075` and corpus tree `8a394e48957b06febe679ec12ac3e98eeb98a8d3`. Only the latter lists the round-27 preregistration, blob `e1f03b14aeab837094fa5310165f723db0d14cf9`. Each prints `EXIT=0`.

```sh
ulimit -v 1048576 && timeout 60s git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree -r --name-only a720399e -- corpus/QUALITY.md corpus/knowledge/echo-discriminating-counters.md corpus/lessons/round-27.md && printf 'EXIT=0\n'
```

```text
corpus/QUALITY.md
EXIT=0
```

Supplemental historical context reads (each exit 0):

```sh
ulimit -v 1048576 && timeout 60s git -C /home/vgpnk/Projects/shokunin/kama-shokunin grep -n -C 10 -E 'Every request body|count-c1.py:384|Counter F2|registered 12 counted 12|counter weaknesses found' a720399e -- corpus/lessons/round-26-verifier-spotcheck.md corpus/lessons/round-26.md
ulimit -v 1048576 && timeout 60s git -C /home/vgpnk/Projects/shokunin/kama-shokunin grep -n -C 10 -E 'signatures,|echo shortcut' a720399e -- SKILL.md
ulimit -v 1048576 && timeout 60s git -C /home/vgpnk/Projects/shokunin/kama-shokunin grep -n -E 'predicate|pre_data_amendment_A0' a720399e -- .ufo/waves/round-26/preregistration.json && printf 'EXIT=0\n'
ulimit -v 1048576 && timeout 60s git -C /home/vgpnk/Projects/shokunin/kama-shokunin grep -n -C 3 -E 'shortcut keyed|"predicate"|"echo-replay"|"message-frame"' 0ec32cac -- .ufo/waves/round-26/preregistration.json .ufo/waves/round-27/preregistration.json
ulimit -v 1048576 && timeout 60s git -C /home/vgpnk/Projects/shokunin/kama-shokunin grep -n -C 2 -i -E 'counter|signature|echo|frame|novel|knowledge|new' a720399e -- corpus/QUALITY.md QUALITY.md
```

Relevant supplemental outputs: round-26 preregistration :29 calls out a “split-message shortcut: two halves of one error body with trivially different triggers”; base QUALITY :39 (KQ12) already requires identifying prior overlapping coverage and rejects row/field growth being called new knowledge without a new sourced distinction. No decoded-echo/frame criterion was found in historical QUALITY.

Current proposal read directly with the read tool: `corpus/knowledge/echo-discriminating-counters.md:14-54` and `corpus/QUALITY.md:219` (KQ37). The entry specifies path, recursively decoded keys/values, both body serializations, case/whitespace normalization, and message-minus-signature frame comparison. These reads are document inspection, not execution of the counter.

## Complete hit-location classification

Legend: **K** = relevant lane knowledge/corpus prescription or standing caveat; **E** = round evidence or round-specific preregistered design; **U** = unrelated lexical hit. A lesson line can contain both a historical result and a prospective rule (**K+E**). A file being under `corpus/knowledge/` does not make an unrelated use of “decode” relevant to X1.

### Relevant hits common to both revisions

| Path | Matching lines | Class | What it establishes |
|---|---|---|---|
| `.ufo/waves/round-26/preregistration.json` | 26 | E | Already names request-echo and one-message/many-row shortcut classes; not the precise normalized-frame test. |
| `SKILL.md` | 1070,1071 | K | Existing raw-JSON versus decoded-message representation distinction. |
| `SKILL.md` | 1077 | K | Existing standing warning that an echo shortcut can meet the counter without error knowledge. |
| `corpus/lessons/round-26-verifier-spotcheck.md` | 26,106,109,110,114 | E | Shortcut result, escaped requests, decode-before-echo explanation and bounded landed-row observations. |
| `corpus/lessons/round-26-verifier-spotcheck.md` | 234 | K | Explicit next-counter requirement to compare every JSON-decoded request string value, plus pre-data receipts. |
| `corpus/lessons/round-26.md` | 79,80 | K+E | Historical shortcut/failure findings and prospective decoded-request/file-content echo and control requirements. |

Supplemental context not matched by the requested regex: round-26 preregistration :12 and :29 contain the one-fault/one-row predicate and split-message amendment; spot-check :107-113 identifies the repeated generic message.

### Additional hits only at `0ec32cac`

All ten are in `.ufo/waves/round-27/preregistration.json`, all classified **E** (round-specific design/history), not pre-round reusable knowledge:

| Line | Content |
|---|---|
| 11 | Rebuilding the counter after round-26 request-echo failure. |
| 12 | Current predicate: decoded request surfaces in (f); explicit normalized message frame in (h). |
| 27 | Echo-replay class includes escaped strings, keys and nested values. |
| 33 | Assembled/transformed echo class. |
| 34 | Explicit at-most-one-row-per-frame requirement. |
| 38 | Historical A0 predicate already compares decoded request surfaces. |
| 42 | Historical A1 predicate retains decoded-surface comparisons. |
| 44 | A2 novelty redesign after recycling previously held evidence. |
| 46 | Historical A2 predicate retains decoded-surface comparisons. |
| 49 | A3 amendment explicitly adds message-minus-signature frame identity. Only the landed amendment's definition is used here; no dead-seat scratch was opened or treated as evidence. |

### Unrelated hits common to both revisions

The following lists every remaining match location; all are **U** relative to the requested X1 rule.

| Path | Matching lines | Reason |
|---|---|---|
| `SKILL.md` | 162,199,228,290,595,613,659,741,801,802 | Model/registry echoes, shell `echo`, exception escapes, IPv6/GGUF/UTF-8 decoding and install faults. |
| `corpus/SOURCES.md` | 63,93,107,108,109,110,117,121,145,264 | Exception boundaries, Go source decoding, Python text decoding and model KV decoding; no decoded-request/frame rule. |
| `corpus/knowledge/alias-endpoint-normalization.md` | 60 | Historical correction and shell `echo`. |
| `corpus/knowledge/consumer-registry.md` | 94,165,378,380,382,384,386,388 | Printed endpoints/model identity and shell commands in correction records. |
| `corpus/knowledge/context-capacity.md` | 1,132 | Model KV decoding. |
| `corpus/knowledge/cross-lane-scope.md` | 57,59,61,63,67,71,75 | Shell commands in historical pointer corrections. |
| `corpus/knowledge/error-is-not-a-verdict.md` | 60,68,69,126,133,144,145,146,158,159,160,162,163 | UTF-8/subprocess decoding and source-authority scope, not request echo. |
| `corpus/knowledge/free-tier-provider-limits.md` | 20,75 | Provider decode throughput and shell `echo`. |
| `corpus/knowledge/gguf-declared-identity.md` | 21,22 | GGUF metadata decoding. |
| `corpus/knowledge/listener-census.md` | 178,252 | Model-identity echo and shell output. |
| `corpus/knowledge/llamacpp-loading-lifecycle.md` | 279,341,384 | Exception escape, digest encoding and producer-boundary scope. |
| `corpus/knowledge/loopback-listener-ownership.md` | 30,77,105 | IPv6 procfs decoding. |
| `corpus/knowledge/ollama-evidence-replay.md` | 77,81,85 | Shell status output and expected-model echo. |
| `corpus/knowledge/served-model-identity.md` | 10,42 | Historical shell commands. |
| `corpus/lessons/round-1-citations.md` | 18 | Historical citation-check command. |
| `corpus/lessons/round-1-safety.md` | 20 | Decode metric name. |
| `corpus/lessons/round-1.md` | 17 | Served-model identity echo. |
| `corpus/lessons/round-10.md` | 115 | Shell `echo`. |
| `corpus/lessons/round-13-verifier-spotcheck.md` | 99 | Python bytes decoding. |
| `corpus/lessons/round-15-verifier-spotcheck.md` | 80,98 | Test-output decoding/receipt correspondence. |
| `corpus/lessons/round-16-verifier-spotcheck.md` | 26,187 | Shell output and exception escape. |
| `corpus/lessons/round-16.md` | 163 | Harness exception escape. |
| `corpus/lessons/round-17-verifier-spotcheck.md` | 73,240,244 | Malformed output, schema bypass and exception escape. |
| `corpus/lessons/round-17.md` | 36,122,167,256,271,284 | Harness/receipt exception escapes and surviving timeout child. |
| `corpus/lessons/round-18-verifier-spotcheck.md` | 68,69 | Environment-value privacy echo controls, not live error-signature credit. |
| `corpus/lessons/round-18.md` | 23,137,239,279 | Decoder limits, exception debt and environment-value privacy. |
| `corpus/lessons/round-19-verifier-spotcheck.md` | 149 | Digest/symlink scope. |
| `corpus/lessons/round-19.md` | 77 | Symlink escape from directory digest. |
| `corpus/lessons/round-20.md` | 65,123 | Model declaration decoding and harness escape sets. |
| `corpus/lessons/round-22.md` | 38,59,135,336 | Producer/helper scope, decoded source snapshot and Git decoding errors. |
| `corpus/lessons/round-23.md` | 24,49,55,70,71,148 | Python/UTF-8 decode policy and sources. |
| `corpus/lessons/round-24.md` | 94,96,99,151,152,188,199,200,201,216,217,219,222,226 | Python decoder-source authority corrections. |
| `corpus/lessons/round-26-verifier-spotcheck.md` | 192 | KV-cache decode source-anchor correction. |

No requested-regex hits occur in historical `corpus/QUALITY.md`; no other matching paths were returned. The complete common inventory is 134 matching lines; the ten round-27 preregistration additions give 144 at `0ec32cac`.

## Final novelty assessment and smallest safe correction

**Against `a720399e`:** refusal of JSON-decoded value echoes is already lane method knowledge. Anti-splitting intent and the generic-message failure are also known. The exact generalized comparison surfaces and normalized-frame equivalence are not specified in the relevant base prescriptions; the new entry and KQ37 provide a durable, sourced, reusable formulation rather than a wholly new principle.

**Against `0ec32cac`:** both detailed rules already occur in the landed round-27 preregistration. X1 moves them into the reusable corpus/quality surface; it does not newly discover them in attempt 3. This revision is after earlier round-27 attempts, so its preregistration must not be mislabeled pre-round evidence.

[INFERENCE] Consolidating a known lesson into an explicit reusable criterion may improve calibration and future discoverability. That benefit is distinct from epistemic novelty, and this review does not establish its score value or the counter's empirical discrimination.

Smallest safe correction: retain the implementation and entry, but narrow the prior-state description to: **“Round 26 already prescribed decoded-request checks and identified message splitting; round 27 promotes that lesson to a sourced reusable entry and KQ37, expands the comparison surfaces, and makes normalized message-frame identity explicit. QUALITY previously lacked the dedicated criterion.”** Cite base lesson :234 and round-26 preregistration :26/:29 alongside the new sources. Keep frozen predicates authoritative for their own rounds; do not imply that KQ37 retroactively changes them.

This is a fixable attribution/novelty defect, not evidence that the repair is useless. Whether reusable codification alone warrants the exploratory calibration claim remains for the named non-author reviewer and canonical judgment path. No C1 count or target was scored, no server/background job was started, no counter main was invoked, and no tool was installed or updated.
