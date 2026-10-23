# CriticClaimSize — frozen C1/C2 admission attack

## Scope, axes, and evidence identity

Axes examined: **depth, calibration, coverage, operability, freshness, adjacency**. This is adversarial evidence, not a judgment or a positive claim receipt.

The lane was not edited and no git command ran in it. All fixture changes are in `/tmp/r31w1-CriticClaimSize`, cloned with `--no-hardlinks` and checked out at assignment revision `0e6f8ed6891c09d5208ac1fdcb294ed9a842832e`. The counters' own baseline is the different revision `07794a4d30a54a60ebdff50ac76d12c6df40a0f1`; these identities are not interchangeable. Counter SHA-256 values were observed as the preregistered C1 `d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216`, C2 `2d06f38d5a686b4d7a316c8db67256ff862fa6e922c1603c156341ff9a33c6fe`, and HOLD `c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d`. None was modified.

All filenames below are relative to this report's directory unless otherwise specified. `commands.json` records every shell command and exit, including the initial C2 output-directory failure (exit 1), its successful retry, and the scratch commits. `scratch-fixtures.bundle` exports the three fixture commits with the assignment revision as prerequisite; it is not proposed lane content.

For the abbreviated reproduction commands below, set:

```sh
L=/home/vgpnk/Projects/shokunin/kama-shokunin
S=/tmp/r31w1-CriticClaimSize
C1="$S/.ufo/waves/round-31/count-c1.py"
C2="$S/.ufo/waves/round-31/count-c2.py"
```

The recorded runs included `--out` pointing into this report's directory; the abbreviated commands omit it to avoid overwriting receipts.

## 1. Can a do-nothing registry meet C1 without measurement-dependent work?

**Yes, without author-side live discovery; no, not with the counter's mandatory live server omitted.** The distinction matters: every successful run below used the frozen counter's own real pinned server. The attack is that the predicted outcome needs no new live knowledge, not that requests or receipts were forged.

### Cheapest construction actually scored

Base body:

```json
{"messages":[{"role":"user","content":"Hello"}],"max_tokens":1,"temperature":0,"seed":1}
```

Register twelve copies of the following row, changing only `id` from `NOOP-01` through `NOOP-12`:

```json
{"id":"NOOP-01","param":"max_tokens","sent":1,"outcome":{"kind":"slot","set":{"n_predict":1}},"source":{"row":"S990","file":"server-common.cpp","line":1530,"contains":"llama_params[item.key()] = item.value();"}}
```

Include the true binary/library/model digests, twelve matching SKILL table rows, and one new S990 source row quoting that pinned line. The meaning text explicitly says: “This repeats the unchanged base request without adding knowledge.” This is nine words, so it satisfies the eight-word gate. `req[max_tokens] = 1` leaves the base request unchanged.

The native schema already declares `n_predict`'s `max_tokens` alias (`server-schema.cpp:44-48`); the task serializer already names `n_predict` (`server-task.cpp:122-123`). The adapter's copy loop is `server-common.cpp:1524-1531`. No sampler effect, new parameter distinction, or new outcome was learned.

**Falsifying command:**

```sh
/usr/bin/python3 "$C1" --lane "$L" --repo "$S" --tip e722ead7889363ffd1cdb352850516d6d70e6936
```

Observed exit **0**, `registered 12 counted 12 target 12 met True not-counted []`; receipt **`c1-noop.json`**.

The counter enforces unique ids, not distinct parameters or a new S-row for each counted row (`count-c1.py:379-387,438-462`). Its mapping test is only `any(k != param ...)` (`467-468`), so a native schema alias is accepted as a supposedly non-schema mapping.

### Stronger construction: uniqueness is not the whole defect

At `7f4e7984f4419bea76a8e58e7736f6a9813f2403`, the registry has twelve **distinct** parameters and twelve **distinct new** S-row identities: `max_tokens`, `max_completion_tokens`, `temperature`, `top_p`, `presence_penalty`, `frequency_penalty`, `seed`, `n`, `stream`, `stop`, `stream_options`, and `messages`. Every row merely asserts the unchanged base `n_predict = 1`. For unrelated parameters, that is not a mapping of the tested parameter at all. Each source row honestly quotes the property-copy line, without pretending the line proves causation. The meaning text explicitly limits the assertion to the unchanged token budget.

```sh
/usr/bin/python3 "$C1" --lane "$L" --repo "$S" --tip 7f4e7984f4419bea76a8e58e7736f6a9813f2403
```

Observed exit **0**, **12/12, met True**; receipt **`c1-distinct-baseline.json`**. Thus deduplicating parameters and source identities alone would not repair the instrument. `slot` outcomes need not differ from base, and the asserted slot key need not be causally related to `param` (`509-520`). A correct quote plus unrelated stored state can manufacture apparent depth.

**Impacted axes:** depth and coverage validity; calibration if this numeric pass is advertised as evidence of twelve learned adapter behaviors.

**Smallest safe correction:** do not integrate these fixtures as knowledge or use their passes as positive evidence. Do not patch the frozen counter or change the target. Distinctness, native-alias exclusion, and parameter-specific rather than baseline-only outcome checks would require a separately preregistered future instrument. Current-wave explanatory prose cannot retroactively repair pre-freeze discrimination.

## 2. Can C2 be met by pasting `--list`, and what does that prove?

**Yes after mechanical deduplication by the counter's own key; a literal one-row-per-listed-problem paste does not meet.** The baseline has 28 rows, 13 problems, one exemption, and every problem is `p1:no-revision`.

The ids `C1` at SCORECARD lines **266, 320, 379** belong to rounds **11, 12, 13**, respectively. The implementation keys corrections by `(row first-cell text, class)`, not round, line, or a revision-keyed stable row identity (`count-c2.py:175-195,251-268`). These three population rows collapse to one key.

**Falsifying commands:**

```sh
/usr/bin/python3 "$C2" --repo "$S" --tip 0e6f8ed6891c09d5208ac1fdcb294ed9a842832e --list
/usr/bin/python3 "$C2" --repo "$S" --tip e722ead7889363ffd1cdb352850516d6d70e6936 --list
/usr/bin/python3 "$C2" --repo "$S" --tip c0b9b26360b4945e93aed4149a9bc822d90f12dc --list
```

All exit **0**. Observed receipts:

| Receipt | Construction | Valid corrections | False corrections | Unresolved | Met |
|---|---|---:|---:|---:|---|
| `c2-base.json` | no correction appendix | 0 | 0 | 13 | False |
| `c2-literal-paste.json` | thirteen listed problems pasted as thirteen CR31 rows | 10 | 3 | 3 | False |
| `c2-dedup-paste.json` | same paste with the two extra `C1` correction rows removed | 11 | 0 | 0 | True |

The last receipt still reports **`base_mismatched 13`** and all thirteen listed observations are still **`p1:no-revision`**. No historical row acquired a revision or supporting measurement. One valid correction services three identically named claims. Also, P1 failure immediately `continue`s, so P2/P3 are not evaluated for these thirteen rows (`193-196`).

What the pass actually proves is an append-only, byte-exact acknowledgment of the instrument's first failing predicate for each recognized **key**, while the existing other rows meet its structural checks or exemption. That is a useful bounded missing-evidence inventory. It does **not** prove all rows carry revision-keyed evidence, that old outcomes or judgments are true, that every later predicate was checked, or that a self-assessment was false at its writing revision.

This is consistent with the limits already stated in rounds 29 and 30 (`SCORECARD.md:1477-1488,1521-1526,1540-1545`): missing retained evidence is not proof of a wrong judgment. KQ39 explicitly calls a paste reference policy **not calibration-axis-fit proof** (`corpus/QUALITY.md:289`).

**Impacted axes:** calibration, through title-to-predicate overreach and collapsed row identity. This is not an attack on the validity of honestly recording missing evidence.

**Smallest safe correction:** disclose the exact inventory interpretation and explicitly disambiguate the three C1 rows in explanatory prose, without adding duplicate correction rows that the frozen counter rejects. Do not describe `unresolved 0` as restored historical evidence or proof of calibration-axis improvement. A future row-keyed instrument must include round and stable row identity and test identity collisions. Whether the bounded inventory satisfies the declared axis move remains for the canonical judge; renaming the claim after scoring is not a repair.

## 3. Do the claims name surfaces rather than only numbers?

**Both name real surfaces.** Preregistration C1.surface names the previously absent `/v1/chat/completions` adapter outcome section, registry, and source bindings. C2.surface names SCORECARD claim-table rows, distinct from rounds 29/30's statement populations. Their numeric targets are not their complete declared work.

The problem is the link from count to surface movement: C1 permits twelve accepted witnesses to one unchanged base fact, including the distinct-parameter construction above. C2 permits acknowledging absent evidence to be counted as resolving the census while no revision is supplied. Neither saturation nor a complete adapter response function follows from those numbers. KQ40 already distinguishes classified observations from mere row growth (`corpus/QUALITY.md:297`).

**Falsifier of “twelve counted rows necessarily establish the named technical surface”:**

```sh
/usr/bin/python3 "$C1" --lane "$L" --repo "$S" --tip 7f4e7984f4419bea76a8e58e7736f6a9813f2403
```

Observed **12/12, met True**, despite the explicitly baseline-only meanings and no parameter-specific mapping assertion.

**Impacted axes:** depth, coverage, calibration. **Smallest safe correction:** separately report which concrete client decisions changed; retain the frozen predicate as a measurement, not a substitute authority for technical meaning or axis admission.

## 4. Is any axis harmed?

**No lane axis was changed by this scratch-only review.** The demonstrated defect is that a proposed promotion based only on these numeric passes can overstate depth and harm calibration. It is not evidence that the actual serving runtime regressed. A new correctly scoped adapter decision table could still be useful; these receipts do not establish its quality.

- **Depth:** baseline-only and explicit type-rule witnesses can be credited as new measured knowledge.
- **Coverage:** repeated witnesses do not govern twelve distinct behaviors; even distinct names can all test the same unrelated fact.
- **Calibration:** C2's unresolved count can reach zero while thirteen rows still have no revision; writing-time truth is not tested by this counter. Treating this as KQ39-style truth correction would be overreach.
- **Operability:** no production tool or server was changed. Only pinned counter-owned servers were used, with cleanup below. No new capability or runtime regression is established.
- **Freshness:** one pinned build/model/argv and evidence existence at tip are bounded observations, not generalization or writing-time evidence. These are disclosed limits, not an observed runtime harm.
- **Adjacency:** no sibling domain or repository was absorbed or modified; no adjacency improvement is demonstrated.

**Regression falsifier required by HOLD:**

```sh
/usr/bin/python3 "$S/.ufo/waves/round-30/count-c1.py" --repo "$S" --tip 7f4e7984f4419bea76a8e58e7736f6a9813f2403
```

Observed exit **0**, `statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 13 false_corrections 0 unresolved 0 met True`; receipt **`hold-r30.json`**. HOLD surviving these adversarial additions is not proof that their C1 depth content is good. This is a **scratch-tip** HOLD, not the eventual landing-tip HOLD.

**Smallest safe correction:** preserve the bounded limits and original records, and avoid claiming that an instrument-soundness defect is a harmless trade of axes. The canonical judge, not this critic or either Python counter, decides admission. No all-axis or final-tip certification is made here.

## 5. KQ38: are type-guess and schema projection actually excluded?

**No: the frozen discrimination rules do not universally exclude either shortcut family.** This conclusion is about the rules; it is not an invented result for the separately named pre-data control seats.

1. **Schema projection:** the alias `max_tokens → n_predict` is explicitly declared in the pinned native schema at lines 44-48. Nevertheless C1's mapping test only compares the two names, and the no-op registry reaches 12/12. It does not check whether the alias is declared or whether anything changed from base.
2. **Type prediction:** the adapter explicitly tests `messages.is_array()` (`server-common.cpp:1385-1390`) and throws the literal `Expected 'messages' to be an array`. C1 rejects a reject-row only when its message is absent from server-common.cpp (`count-c1.py:465-466`). Thus this source-explicit type rule passes the very gate claimed to exclude type-predictable outcomes. At `c0b9b263...`, twelve unique ids repeat `messages={}` with the predicted 400 envelope and source line 1390.

**Falsifying commands:**

```sh
/usr/bin/python3 "$C1" --lane "$L" --repo "$S" --tip e722ead7889363ffd1cdb352850516d6d70e6936
/usr/bin/python3 "$C1" --lane "$L" --repo "$S" --tip c0b9b26360b4945e93aed4149a9bc822d90f12dc
```

Both observed exit **0**, **12/12, met True**; receipts **`c1-noop.json`**, **`c1-type-guess.json`**. The distinct-parameter construction additionally defeats the response “just enforce one row per parameter.”

Some restrictions are real: schema-authored bounds messages are normally refused as rejects; declared OAI names are refused as ignored rows; response checks are confined to four shapes. But adapter-message provenance is not measurement dependence, a different slot-key spelling is not a novel mapping, and response-shape observations need not be effects of the parameter. KQ38's rule is about predictable outcomes, not merely whether a live confirmation occurred (`corpus/QUALITY.md:283`). Round 28's own claim row already records why a shortcut meeting a pre-data rule could not be cured by a later amendment (`SCORECARD.md:1415,1425-1427`).

**Impacted axes:** depth and calibration. **Smallest safe correction:** retain frozen bytes and all attack receipts, disclose the counterexample, and route its admission consequence to the canonical judge. Do not present post-freeze attacks as the required pre-freeze controls or quietly substitute a stronger instrument. A future instrument needs source-rule/alias exclusions and a genuine parameter-specific, measurement-dependent positive control before freeze.

## Operational evidence and trust boundary

- Before and after all three C1 runs, `ss -Hltpn 'sport >= :47900 and sport <= :47999'` exited **0** with **no output**: no listeners in the allowed range at those observations. The frozen counter started/stopped each server; no manual server or persistent job was left running.
- No installs, updates, host-service actions, lane git commands, or tracked-lane edits occurred. Scratch git identity is explicitly `CriticClaimSize scratch`, not falsely attributed to the lane.
- Do **not** trust any `c1-*.json` here as positive depth evidence, final landing receipts, or pre-freeze control evidence. Do **not** trust `c2-dedup-paste.json` as restored evidence or a writing-revision truth census. Do **not** trust `hold-r30.json` as a final landing-tip check.
- The actual named control arms' timing and results, the landing-tip counts, and admission were not assessed or fabricated. This report completes only the assigned claim-size review.
