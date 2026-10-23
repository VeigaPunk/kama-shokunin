# kama — round 31 lesson (2026-10-23)

## Claims

- **C1 (depth).** `counted >= 12` over SKILL.md `## Round-31 chat-completions parameter
  outcomes`, `registry/chat-param-outcomes-r31.json`, one new `S###` row per cited line, and the
  frozen counter's own live run. Result at the landed tip `54c6f4fe`:
  `registered 18 counted 17 target 12 met True not-counted ['K31-10']`. **Not admitted as an
  improvement**: the control call's two KQ38 policies failed (`CtlTypeGuess` 1/12,
  `CtlSchemaProjection` 0/12), but a cheaper shortcut found after the freeze meets the target —
  twelve duplicate rows asserting the base request's own `n_predict = 1` count 12/12
  (`w1/out/CriticClaimSize/c1-noop.json`), and `RevCounterFair` F1/F2 show two further counted-row
  classes that prove nothing (an `ignored` claim on a field the chat session consumes; a `slot`
  mapping whose stored value equals the base's). The counter is frozen; the defect is routed.
- **C2 (calibration).** `rows >= 28 and unresolved == 0 and false_corrections == 0 and append_only`
  over the SCORECARD claim rows. Result at the landed tip `b4f3edc0`:
  `rows 30 base_mismatched 13 valid_corrections 10 false_corrections 0 unresolved 3 append_only True
  met False`. **Not met — counter defect**: the correction key is `(row, class)` and three distinct
  failing rows carry the Claim cell `C1` (rounds 11, 12, 13), so their three dispositions collapse
  into one key. The reference arm appended all thirteen and read `valid 10 false 3 unresolved 3`
  (`controls/RefRepair/`); the tree carries the ten expressible corrections and names the three
  inexpressible rows in prose.

## Gate

New source rows opened this round, all tier A, all quoted from the sha256-pinned snapshot
(`.ufo/waves/round-31/sources/llama.cpp-704366d/`, `SNAPSHOT.json`), accessed 2026-10-23. Each
quote is ≤25 words and was re-checked at its line by `sed -n '<n>p'`.

| row | URL (line) | quote |
|---|---|---|
| S180 | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1360 | `throw std::runtime_error("Cannot use both json_schema and grammar");` |
| S181 | …/server-common.cpp#L1375 | `throw std::invalid_argument("response_format type must be one of \"text\" or \"json_object\", but got: " + response_type);` |
| S182 | …/server-common.cpp#L1390 | `throw std::invalid_argument("Expected 'messages' to be an array");` |
| S183 | …/server-common.cpp#L1395 | `throw std::invalid_argument("All non-assistant messages must contain 'content'");` |
| S184 | …/server-common.cpp#L1399 | `throw std::invalid_argument("Assistant message must contain either 'content' or 'tool_calls'!");` |
| S185 | …/server-common.cpp#L1411 | `throw std::invalid_argument("Expected 'content' to be a string or an array");` |
| S186 | …/server-common.cpp#L1517 | `throw std::invalid_argument("logprobs is not supported with tools + stream");` |
| S187 | …/server-common.cpp#L1519 | `llama_params["n_probs"] = json_value(body, "top_logprobs", 20);` |
| S188 | …/server-common.cpp#L1521 | `throw std::invalid_argument("top_logprobs requires logprobs to be set to true");` |
| S189 | …/server-common.cpp#L1530 | `llama_params[item.key()] = item.value();` |
| S190 | …/server-schema.cpp#L47 | `->add_alias("max_tokens")` |
| S191 | …/server-schema.cpp#L64 | `->add_alias("n") // alias "n" as fallback (OpenAI completions API)` |

Reject decisions recorded (round-30 spot-check routed defect 6): the `CtlTypeGuess` arm's
twelve guessed rows were refused (eleven uncounted; one counted by coincidence of a native
alias), and the `RevCounterFair` F3 fixture — the schema bounds message copied as a `reject`
row — was refused pre-live as `reject-message-not-adapter`. Both are rejections of candidate
evidence, not of sources.

## Mistakes

| # | class | evidence | captured-by | fix (shown able to fail) |
|---|---|---|---|---|
| 1 | a preregistration absence claim was false: it said no lane file names `server-common.cpp`'s chat parser | `.ufo/waves/round-31/preregistration.json` C1.surface at `0e6f8ed6` vs `w1/out/ScoutFrontier/findings.md`: `oaicompat_chat_params_parse` occurs in seven tracked `.ufo/waves/round-26/27` files (and 433 files under `.ufo`); only `corpus/`, `SKILL.md` and `PROVINCE.md` were checked | none mechanical — the L1 wrote the claim from a memory of the corpus, not from a full-set read (KQ9's class) | state the absence at a named scope: `git -C <lane> grep -F -q oaicompat_chat_params_parse <base> -- . ':(exclude).ufo'` exits 1 (true: the committed corpus has never held it) while the same command without the exclusion exits 0 (the wave trees do). Both invocations are in `w1/out/ScoutFrontier/findings.md`; the exclusion is the discriminator, so the check fails when the claim is stated too broadly. |
| 2 | duplicate population row in a merged registry: the same parameter was drafted by a seat and by the L1, and both rows reached the registry | `count-c1.py` at `3b1e84f8` printed `registered 19 counted 16 ... not-counted ['K31-10','K31-14','K31-14']`; the fix commit `54c6f4fe` reads `registered 18 counted 17` | the frozen counter's `duplicate-id` rule (both copies uncounted, the count drops by two) | keep the counter's duplicate-id rule; it caught the defect without being told to. |
| 3 | source-row ids assigned by ordinal inside seats collided at integration (two seats both wrote S180 for different lines; another wrote S198) | `w1/out/SrcOpen1/sources.md` (S180 = L1360) vs `w1/out/DataA01/row.json` (S180 proposed for L47); integration remap at `54c6f4fe` | the counter's `source.line`/`source-file` checks plus the SKILL `source` cell check — a wrong id fails the row, not the census | assign ids at integration from the unique `(file, line)` set in sorted order (S180-S191 here); seats keep `S-TBD` and the exact `(file,line,contains)` triple. The remap changed 12 cells and left the count at 17/18, so the ids are now derived, not asserted. |
| 4 | twelve source rows were appended after the last `##` section of `corpus/SOURCES.md`, so the registry held them outside its one table | census at the dispatch base `d45f947e2`: `E12 row outside Registry section` for S180-S191, exit 1 (`.ufo/waves/round-31/census-start.out`, 12 findings); each row's own cells were correct, so nothing downstream of the registry complained | `scripts/sources-census.sh validate` E12 — the contract's one-registry rule; the C1 counter's source check reads rows by id and passed, so only the census caught it | move the twelve rows into `## Registry` with ids and cells unchanged, and prove the move is positional: the 12 sorted row lines are byte-identical before and after (`diff` empty), and the same census reads `ok`, exit 0 (`.ufo/waves/round-31/census-end.out`). The pre-repair receipt above shows the rule able to fail. |

## Repairs (routed by `corpus/lessons/round-30-verifier-spotcheck.md`; not claims)

1. The round-30 report's Landed-changes table omitted `f41dce3` and `043ba425`
   (`w1/out/ExecRepairReport/checklist.md`); this round's report lists every landed commit.
2. The round-30 completion digest was future-dated against the lane tip; this round records the
   completion time only after the last commit, and the report cites committer times.
3. `instrument-agreement` now has a SKILL.md instrument-registry row (name, entry, exit map,
   selftest/pins, write scope) — `w1/out/ExecRepairInstrument/registry_row.md`, applied in the
   Round-31 registry block.
4. Its "isolated temp dirs" wording is corrected in that block and in
   `w1/out/ExecRepairInstrument/correction.md`: runs share `cwd` and get a fresh `TMPDIR` only, and
   the receipts name `cwd` rather than a measured revision.
5. The round-30 lesson's two wrong receipt pointers are corrected by appended records
   (`w1/out/ExecRepairLesson30/corrections.md`): the bound-68 reading lives in `bound68.json`
   (`72 statements / 68 items / 4 unbound`), and the oracle-revision-pin failure has no committed
   receipt (it stays an unretained observation).
6. The round-30 `## Gate` reject rows are recorded above.
7. The round-30 counter's docstring drift (`## Round 29`/`SA29:` vs the code accepting Round 30 and
   `SA30:`) is cited, not fixed, in the round-31 instrument-registry row; the round-31 counters
   document their own population in their docstrings and in `preregistration.json`.

## Wave findings that shaped the verdicts

- `CtlTypeGuess` counted 1 of 12; `CtlSchemaProjection` 0 of 12; `CtlNoLive` 5 of 12; `CtlWrongCell`
  0 of 3 (the counter binds the SKILL cell text); `CtlTamper` showed the pin, not the run, is the
  guard.
- `CtlDoNothing` `met False`; `CtlAllRows` false 18; `CtlWrongObserved` and `CtlNoId` false 13;
  `CtlEditInPlace` caught by `append_only`; `CtlBaseTree` reproduced the key collision.
- `MutC2` five mutations: three caught; a duplicate id appended to a new row survived
  (`rows 29 ... met True`) and a new row with a dead evidence path survived because P2 is satisfied
  by the counting-command path. `RevCounterFair` F1/F2 are the counted-while-meaningless classes.
  `CriticClaimSize`'s no-op baseline is the cheapest C1 shortcut. All five are recorded as frozen
  counter/limit defects for round 32, not repaired here.
- `ExecHoldCheck`: the round-30 counter still reads `met True`, 141 statements, unresolved 0 at the
  round-31 base (`.ufo/waves/round-31/c1/hold-r30.out`).

## Limits

- One build, one model, one default argv, one request per parameter; `n_slots` 4.
- The `/slots` parameters are the stored task settings, never proof of sampler use; a session-level
  grammar is invisible there (hence F1's false `ignored`).
- `K31-10` is a true observation the counter cannot count: the adapter appends the offending value
  to the message, so no verbatim pinned quote exists for it.
- The round's depth claim is measured on a counter that a no-op registry meets; the closure should
  read the count together with `w1/out/CriticClaimSize/c1-noop.json`.

## Attempt 2 (2026-10-23) — inherited state re-measured, wave-2 falsification

Attempt 1's claims, data and lesson are inherited unchanged. This section records what attempt 2
measured, what its 44-seat wave falsified, and the mistakes this attempt mined.

### Gate

No source row was opened for the first time this attempt; all twelve round-31 rows S180-S191 were
re-opened against the pinned snapshot by six seats (two rows each), each re-checking the URL line
anchor, the access date (2026-10-23), the ≤25-word quote at its `sed -n '<line>p'` line, and the
`used-by` target's existence: twelve `quote-verbatim yes`, twelve `line match yes`, zero
disagreements (`.ufo/waves/round-31/w2/out/SrcReopen{1..6}/report.md`). Zero rows added, zero
rejected, zero cells changed. Rejections recorded this attempt are claim-evidence rejections, not
source rejections: the C1 no-op registry (counted but meaningless), the C3 bogus registry row
(passes the gate), and the six meaning cells whose prose the probe falsified.

### Mistakes

| # | class | evidence | captured-by | fix (shown able to fail) |
|---|---|---|---|---|
| 5 | two measurement receipts (`c1/c1-382d11b2.json`, `c2/c2-382d11b2.json`) were written into the lane but never committed, so the round's only measurements at its landing tip were untracked when the session died | `git -C … status --porcelain .ufo/waves/round-31` at the start of attempt 2 printed exactly those two `??` lines; the committed tree at `382d11b2` held neither | none — the report cites landed hashes, and an untracked receipt cannot be cited, but nothing ran that check before the loss | a report-time gate: `test "$(git -C <lane> status --porcelain .ufo/waves/round-N | grep -c '^??')" -eq 0`; it fails (prints 2, exit 1) on the inherited tree and passes after the receipts are committed (attempt-2 commit `bda324bb` plus the wave-2 artifact commit) |
| 6 | a committed source snapshot carried a failed fetch as if it were a source: `sources/llama.cpp-704366d/utils.hpp` is the 14-byte body `404: Not Found`, and two unpinned 37 KB duplicates (`server-http.cpp`, `server-models.cpp`) sat beside it | `head -1 .ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp`; `SNAPSHOT.json` pins only `server-common.cpp`, `server-schema.cpp`, `server-task.cpp`, `server-chat.cpp` | none — the counter verifies only the files the manifest names, so extra files were never inspected | the snapshot dir must equal the pinned set: `comm -23 <(ls …/llama.cpp-704366d | sort) <(jq -r '.files|keys[]' …/SNAPSHOT.json | sort)` prints 3 lines at `382d11b2` and nothing after `a9181096` (removal) |
| 7 | six of eighteen graded `meaning` cells asserted behaviour the fixture contradicts (K31-02, -05, -08, -09, -11, -12) | `w2/out/RevRow{A,B,C,D}/` counterexample probes: `content:null` → 200, `logprobs:true` alone → `n_probs: 20`, `grammar:""` → 200, `logprobs:false` with tools+stream → 200, native `n_predict` overrides the OpenAI aliases, assistant `content` without `tool_calls` → 200 | none — the frozen counter requires eight words, not truth (`count-c1.py` docstring L47-48 "Not checked … meaning prose") | **KQ42**: a graded prose cell is admitted only after a counterexample search on the pinned fixture with its probe receipt committed; applied to the round-31 table it fails 6 of 18 rows, and the appended SKILL block carries the measured counterexample for each |
| 8 | C3 was frozen as a "capability acquisition" whose target the instrument's own docstring says it cannot discriminate: the gate checks path occurrence only, so a row with an empty exit map meets `unregistered 0` | `preregistration-c3.json` C3.known_limits names the limit, yet the frozen predicate still stopped at the gate's output; `w2/out/ExecC3Control/` (empty-exit-map row → exit 0) and `w2/out/CriticC3Control/` (nonexistent metadata path → exit 0) | none — the freeze-time rule says to run the cheapest shortcut control before freezing, and no seat had run it; the wave found it after the freeze, which is why the claim is reported met-on-predicate and not admitted | a claim resting on a gate must put in its target one condition the gate cannot check and the L1 can re-derive (here: the row's five cells re-read against the counter's argparse and exit paths); that condition fails on the bogus-row receipt and passes on the delivered row |

### Limits added by the wave

- `count-c1.py` reads pins from the tip blob and checks only `sha256` fields: a working-tree pin edit
  and the declared `bytes` field are silently ignored (`w2/out/MutC1Pin/`, three surviving mutants).
- `count-c2.py`'s `append_only` is a base-prefix check: deleting the correction suffix passes it
  (`w2/out/MutC2Append/`, mutant D).
- The C1 counter's live reading is deterministic across runs (`w2/out/RevLiveRepeat/`,
  `IA runs=3 agree=3 disagree=0`, three byte-identical receipts) — determinism is not correctness.
- The round-30 hold still reads `statements 141 … unresolved 0 met True` at the round-31 tip
  (`w2/out/ReRunHold/`, `w2/out/ExecHoldRepro/`); only the `tip` field differs from the committed
  receipt.
