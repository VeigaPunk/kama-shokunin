VERDICT: partial — the primary-source anchors and numerical receipts hold, but the entry still overstates clause-(f) reachability, literal binding, ASCII conformance, and the provenance of its frame replay.

# Scope and axes

This is the assigned sentence-level criticism of `corpus/knowledge/echo-discriminating-counters.md` **at commit `52632caa2ed813c1c12f7a9dcab3556b4f0bd9eb`**, not an X1 judgment, C1 score, admission, or integration decision. No target file was changed.

**Axis: calibration (X1).** Diagnostic dimensions: factual accuracy; source/receipt provenance; rule-to-code fidelity; honest scope of evidence. C1 is not evaluated here.

All repository pointers below are relative to `/home/vgpnk/Projects/shokunin/kama-shokunin`. Abbreviations:

- **Entry** = `corpus/knowledge/echo-discriminating-counters.md`.
- **A3** = `.ufo/waves/round-27/count-c1.py` at the reviewed commit.
- **R26** = `.ufo/waves/round-26/count-c1.py` obtained with `git show eb09e742:...`.
- **W** = `.ufo/waves/round-27/w1a3/`; thus Entry's `w1a3/out/...` shorthand is checked under W, not relative to its Markdown directory.
- **Shortcut** = `.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/`.
- **Upstream** = immutable raw GitHub bytes at `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`, with LF-based line numbering.

Every cited receipt/report and relevant harness was reopened from the named commit using read-only `git show`; checked object hashes and exact argv/exit codes are in `residual/out/CriticRevisedEntry/checked-objects.json`. Primary-source excerpts, URLs, HTTP statuses, and hashes are in `residual/out/CriticRevisedEntry/source-excerpts.txt`. These two paths are relative to `.ufo/waves/round-27/`.

# Counterexamples and smallest safe corrections

## F1 — a rejected string body still reaches clause (f)

**Counterexample:** Entry:100-102 says “Such bodies never reach it” immediately after explaining clause (f). A3:576-581 appends `e:bad-request`, but does not return or skip clause (f). A3:585-587 then calls `request_surfaces(req)` whenever the request is a dictionary with a string path, including when its body is a string. The request is excluded from **live execution**, later, at A3:657-659.

The committed evidence itself agrees: `W/out/ExecOfflineEchoReplay/replay.receipt.json:34-45` records four clause-(f) surfaces for the first string-body row, and `:296-303` records 0/12 echo detections alongside 12/12 shape rejections. That receipt is function-level evidence, not a full static-check run; the control-flow finding comes from the frozen code.

**Impacted dimension:** calibration / reachability accuracy. **Smallest correction:** “Stored string bodies are shape-ineligible and filtered out before live replay; clause (f) still evaluates their undecoded surfaces.” Keep the separate, supported 0/12, 12/12, 12/12 results. No frozen-counter edit is needed.

## F2 — clause (d) does not require membership in one actual C string literal

**Counterexample:** Entry:112-114 says clause (d) requires the signature to be a substring of “a C string literal on the cited line.” A3:338-340 returns every regex-extracted literal **plus the concatenation of all of them**, irrespective of intervening expressions. A3:565 accepts a match in any such candidate. The uniqueness scan uses the same candidates (A3:278-293).

This is not merely adjacent C string-literal concatenation. Actual upstream `server-models.cpp:657` is:

```cpp
throw std::invalid_argument("unknown sidecar '" + kind + "', expected one of " + string_join(kinds, ", "));
```

The helper's extra candidate is `unknown sidecar '', expected one of , `, which is not contained in any one of that line's three literals and joins across the dynamic `kind` and a separate function argument. Static extraction of those fragments is recorded in `checked-objects.json` under `nonadjacent_literal_witness`. **No full-counter acceptance of that candidate is asserted:** other checks, including live text, were not run.

**Impacted dimension:** calibration / source-binding fidelity. **Smallest correction:** describe “a regex-extracted literal or the helper's concatenation of all literals on the line,” and explicitly say this is weaker than the rule's one-literal boundary condition. Add A3:338-340 and :278-293 to the implementation citation. Do not silently strengthen the frozen predicate in prose.

## F3 — the ASCII qualification does not establish conformance

**Strongest existing counterexample:** Entry:120-121 concludes that the counter “therefore meets the rule for ASCII signatures and positional frames only.” But `W/out/CriticEntryRuleVsCode/probe.stdout.txt:4` already supplies an **ASCII** signature, `invalid-strasse-marker`, in a decoded surface containing `invalid-straße-marker`; `counter_occurs` is false and `unicode_casefold_occurs` is true. Restricting the signature alone to ASCII does not make `lower()` equivalent to case folding. The same committed output at `:13` shows the ASCII TAB-only remainder mismatch, also not cured by positional frames.

These are component witnesses; neither is represented here as a full A3 bypass or row-admission result.

**Impacted dimension:** calibration / premature conformance claim (and premature frame saturation for the TAB case). **Smallest correction:** replace the concluding guarantee with “The implementation uses lowercasing, positional NUL placeholders, and NUL/ASCII-space blankness; it does not fully implement the rule as stated.” If an ASCII equivalence statement is retained, it must constrain compared text as well as signatures and separately exclude the whitespace-only mismatch.

## F4 — the frame result is a metadata-controlled projection, not the unchanged round-26 rows

Entry:109-111 attributes the 1-versus-12 result to “the 12 round-26 rows” without disclosing changed fields. The numbers hold, but `W/out/MutFrameLoadBearing/probe.py:62-70` constructs new clause-(h) inputs with:

- `why=[]`;
- synthetic distinct source lines `10000 + n`;
- synthetic source-row ids `FRAME-SYNTH-*`;
- synthetic distinct `_next` actions.

`W/out/MutFrameLoadBearing/preparation.json:151-154` expressly scopes it to clause (h), with a-g unevaluated. The captured signatures, request bodies, and decoded messages are retained; the original source metadata is recorded separately at `:2-122`. The source-line/next-action checks therefore ran against fabricated-distinct component metadata, not the original complete row records. Original round-26 registry sources do not even have A3's source-line field (`Shortcut/shortcut.registry.json:21-24`).

**Impacted dimension:** calibration / false provenance of the replay scope. **Smallest correction:** “An isolated clause-(h) replay of the twelve captured signatures/messages, with synthetic distinct source lines, source-row ids and next actions and cleared prior reasons, retains 1 row; removing its frame branch retains 12.” Keep the numerical result, but not an implication that a-g or the unchanged original metadata passed.

## F5 — minor source/probe scope conflation

Entry:139-140 scopes both S137 and the live probe to “ASCII signatures.” The live fixtures are indeed ASCII. S137's code has no ASCII restriction: `server-common.cpp:1365-1375` appends the parsed `std::string`; `server-common.h:43-56` likewise has no ASCII guard. This is an unnecessarily narrow attribution, not evidence that non-ASCII live behavior was tested.

**Smallest correction:** “S137 is pinned to 704366d76; the live probe tested ASCII signatures only.”

The positional-hole versus literal-deletion frame definition remains a **semantic tradeoff for the canonical reviewer**, not something this critic changes or judges. F1-F5 are fixable descriptions/provenance issues, not an X1 verdict.

# Per-sentence table

“holds (normative)” means the text states a proposed rule or scope limit, not that a receipt proves universal implementation. Semicolon-separated factual clauses are all checked in the indicated row. Breaks identify the unsupported portion; the remaining supported clauses are noted.

| Entry lines | Sentence / factual unit | Pointer checked | holds/breaks |
|---|---|---|---|
| 1 | `source:` S136/S139 JSON escapes, S139 supersession, S137 echo site, round-26 shortcut, frozen counter hash and landing revision, W receipts. | `corpus/SOURCES.md:148-151`; upstream RFC §7 and `server-common.cpp:1375`; spot-check:98-116; `git show` A3 at both 52632caa and 1471f676. | **holds** — both A3 objects hash to `49491b80…2765`; all named evidence paths exist in the reviewed commit. |
| 2 | Sources opened this round; b11755 live probe at 07:11:54Z; named-revision lines re-read. | SOURCES:148-151; `corpus/lessons/round-27.md:99-114`; `W/out/ExecLiveEchoProbe/receipt.json:16-38`; immutable source hashes. | **holds as recorded provenance** — date/time/build match the committed records. This audit independently reopened the source bytes; it does not independently witness the historical author opening them. |
| 3 | Recheck on release; RFC recheck 180d. | SOURCES:148-151 recheck cells. | **holds (normative)** — metadata agrees. |
| 7-8 | “Round-27 exploratory entry (axis: calibration — the lane's claim-measurement method).” | `.ufo/waves/round-27/a3/plan.json:10-18`. | **holds**. |
| 8-10 | “It records how a counter … must be built so that the server cannot be made to say the signature back.” | Entry's rule:70-87 and limits:125-140. | **holds (normative)** — purpose, not proof that A3 or this necessary rule defeats every transformed/channel echo. |
| 10 | “It is method knowledge for this lane's counters.” | Plan:12-18; Entry's rule and implementation sections. | **holds** as declared scope. |
| 10-12 | “It is not a new llama-server error signature, and it does not establish that any particular counter discriminates on data.” | Plan:7-18; Entry contains method/evidence rather than an admitted new row. | **holds**. |
| 14-18 | Round-26 preregistration named request-echo and split-message classes, and the outside spot-check prescribed decoded-string comparison. | `.ufo/waves/round-26/preregistration.json:26,29`; `corpus/lessons/round-26-verifier-spotcheck.md:234`. | **holds** — both quoted classes and the prescribed comparison are present. |
| 19-20 | “Those were round evidence and a routed defect, not lane knowledge or an admission criterion.” | Same round artifacts; pre-round-27 `a720399e` search of `corpus/QUALITY.md` and `corpus/knowledge/` for decoded/request/server-echo/message-frame wording. | **holds within the stated lane-knowledge/criterion surfaces** — search returned no matches; it does not erase the existing preregistered counter intent. |
| 20-23 | The entry adds primary sources, frame and boundary tests, build-specific live/offline evidence, reachability conditions, and limits. | SOURCES:148-151; Entry sections:41-140; named W receipts. | **holds** as an inventory of additions, with implementation-description defects below. |
| 27-28 | Round 26 froze a counter requiring the signature in the live error and “not echoed.” | R26:381-384; round-26 preregistration:12,18. | **holds** as a summary of those necessary checks, not the entire counted predicate. |
| 28-31 | Echo was compared with stored request text; a string body was verbatim; quoted `e_not_echoed` assignment. | R26:371-374,384. | **holds** — exact assignment and line numbers match. |
| 32 | “After data, a critic met the frozen target from the base tree with 12 rows.” | Spot-check:98-113; `Shortcut/shortcut.receipt.json:3-5,320-323`; `Shortcut/gen_shortcut.py:19,55-61`. | **holds** — base, registered/count/target 12, and base extraction are recorded. |
| 33-37 | Each body was a JSON string with a first-character `\u00XX`; those bytes were sent, decoded and echoed in a generic message; raw body lacked the signature. | All twelve committed Shortcut registry/receipt rows; R26:156-160; spot-check:106-110; upstream S137. | **holds** — static JSON recomputation confirms all twelve string bodies, first escapes, decoded values, and absent raw signatures. |
| 37-39 | Offline round-26 test flags 0/12 as echoes. | `W/out/ExecOfflineEchoReplay/replay.receipt.json:296-303`; harness:109-118. | **holds** — echo-flag count, not a fresh full-counter run. |
| 43 | “One JSON string value has many byte spellings.” | RFC §7:433-445,455-459. | **holds** — demonstrated spellings for nonempty values; not a claim about alternative spellings of the empty string. |
| 43-44 | RFC: “Any character may be escaped.” | Raw RFC LF line 433. | **holds** — exact quote. |
| 44-47 | BMP character: six-character `\uXXXX`; outside BMP: twelve-character UTF-16 surrogate pair; S139 corrects S136. | Raw RFC:433-440,455-459; SOURCES:148,151. | **holds** — the rewritten wording fixes the prior non-BMP overclaim. |
| 47-48 | Raw-byte absence does not exclude decoded echo. | RFC §7; Shortcut's twelve bodies and messages; live req2/req3/req6. | **holds**. |
| 49 | “llama-server b11755 puts decoded request values into error text.” | Upstream `server-common.cpp:1365-1375`; live receipt:17-22,42-113. | **holds**. |
| 50-51 | S137 throws the quoted prefix plus `response_type`. | Raw upstream `server-common.cpp:1375`. | **holds** — exact statement and line. |
| 52-56 | `json_value` returns a parsed string; nonempty type outside text/json_object/json_schema is appended; HTTP status is 400. | Raw `server-common.h:43-56`; `server-common.cpp:1363-1377,95-97`; `server.cpp:62-65` and continuation:79-84; live receipt status fields. | **holds** — cited anchors are correct; adding server.cpp:79-84 would make the response-rendering chain explicit. |
| 56-57 | One fixed frame can carry distinct caller strings; these are not distinct faults. | S137 concatenation; live receipt two decoded values and common frame; Shortcut messages. | **holds** for this validation branch; “any number” describes repeated choices, not an unbounded single request. |
| 57-61 | Plain, first-character `\u0065`, and fully escaped spellings yield byte-identical 400 bodies; two values share one frame. | `W/out/ExecLiveEchoProbe/receipt.json:42-113,167-213` and all six `.req`/`.resp` objects. | **holds** — all 12 fixture hashes/lengths match; first three response bytes are identical; parsed request/response fields agree with receipt. req4 is the 200 control, not an error case. |
| 62-66 | S137 is one of at least 12 frames; named tool_choice/reasoning/media/model sites and 14 request-JSON dump throws exist. | `W/advice/ScoutEchoSitesSnapshot.md:17-44`; raw chat:324,347-402,437,562-585,874; common:1216,1221,1234,1375; models:657,854,2170,2516. | **holds with the scout's counting definition** — 12 HTTP frames include the two rethrow wrappers; the 14 dump throws are inside those wrappers, not 14 additional independent HTTP frames or 12 disjoint scalar-only frames. All named Entry anchors are correct. |
| 70-71 | “A counter … must refuse it when either holds.” | Three ensuing legs at Entry:73-87. | **holds (normative)** — editorial nit: there are three legs, so “any of the following holds” is clearer than “either.” |
| 73-76 | Echo refusal covers folded/whitespace-stripped path, decoded keys/values at depth, and both body serialisations. | Rule text; RFC §7 motivation; A3:343-372 for implementation comparison. | **holds (normative)** — not a claim that lower() is full case folding. |
| 76-78 | Raw bytes alone are not enough; stored string bodies must be refused or decoded. | Rule; R26 shortcut; A3:580-581,657-659. | **holds (normative)**; A3 enforces refusal before live execution, not before clause (f). |
| 79-81 | Shared-frame refusal compares nonblank case-folded message remainders after removing the signature with credited rows. | Rule definition; implementation gap at A3:707-708; `W/advice/CriticEntryRuleVsCode.md:20-24`. | **holds (normative)** — deletion and positional-hole relations must not be silently equated. |
| 81 | “One message frame earns one row, whatever is spliced into it.” | Same rule and its preceding nonblank qualifier. | **holds (normative, with that qualifier)** — not an empirical guarantee of A3. |
| 82-84 | Boundary refusal requires a source-literal-owned signature and no overlap with decoded-request spans. | Rule definition; boundary probe; A3:565 and literal helper:338-340. | **holds (normative)** — stricter than A3's actual literal-candidate test and absent span test. |
| 85-87 | Without boundary, tail-plus-caller-value signatures pass echo/frame legs 12/12 on captured S137 messages. | `W/out/CriticKQ37Wording/frame_boundary_probe.json:2-11`; corresponding harness:32-68; all 12 rows. | **holds** — component scope explicit in receipt; not a full A3 bypass. |
| 89-90 | Unrelated request text equal to a genuine signature also causes conservative rejection. | Rule; A3:351-372,585-587 includes every field without causal attribution. | **holds** as a direct consequence, not a measured rate of such rejections. |
| 91-92 | Request overlap establishes possible supply, not actual echo provenance. | Same indiscriminate comparison. | **holds** — appropriate limitation of the inference. |
| 96-99 | Clause (f) walks decoded dictionary/list keys and string values, adds both dumps, and covers non-string scalars through serialisations only. | A3:343-372,585-587; `W/out/CriticEntryRuleVsCode/probe.stdout.txt:7-10`. | **holds** — top-level `None` means no HTTP body (A3:389), not a separately serialised null body. |
| 99-100 | “It does not parse a string body.” | A3:365-372. | **holds** — json_strings adds the stored string; dumps re-encodes it; no loads operation is present. |
| 100-102 | “Such bodies never reach it” because shape check rejects them; accepted bodies are serialised by counter. | A3:576-588,389,657-659. | **breaks** — string bodies still reach clause (f); they do not reach live replay. The shape rejection and accepted-body serialisation clauses hold. See F1. |
| 102-105 | Original 12 bodies: (f) flags 0/12; shape rejects 12/12; decoded-body (f) flags 12/12. | `W/out/ExecOfflineEchoReplay/replay.receipt.json:296-303`; harness:109-129. | **holds** — separate component applications, not full-counter receipts. |
| 105-107 | Five live fixtures: (f) refuses 5/5; round-26 test credits 3/5. | `W/out/ExecLiveEchoProbe/replay-function-level.json:18-84`; replay.py:32-48. | **holds for the named echo tests** — the three are raw-byte `e_not_echoed` passes only, not full R26 counted rows. Live bodies are decoded by replay.py:36 before A3 helper calls. |
| 108-109 | Clause (h), lines 707-709, replaces signature with NUL and lowercases. | A3:707-709. | **holds** — all exact occurrences are replaced; cited lines match. |
| 109-111 | “On the 12 round-26 rows it leaves 1 row”; disabling frame leaves 12 surviving other (h) checks. | `W/out/MutFrameLoadBearing/pristine.json:27-30,103`; mutated.json:90; preparation.json:151-154; probe.py:62-70. | **breaks as an unqualified original-row replay attribution** — 1/12 and 12/12 hold for projected inputs with synthetic-distinct metadata and no prior reasons, not unchanged round-26 row records. See F4. |
| 112-115 | Clause (d) requires one C literal, uniqueness on other lines; frame-tail signatures are not shown to meet it; no span-overlap check exists. | A3:565-571,338-340,278-293; entire parsed A3 function structure; boundary probe scope. | **breaks on “a C string literal”** — regex candidates include a nonadjacent concatenation; other-line uniqueness uses those same candidates within pinned files. The no-demonstrated-full-bypass and no explicit message-span check clauses hold. See F2. |
| 116-120 | lower() is not case folding; placeholder preserves cut position; TAB-only remainders are nonblank to the code. | A3:343-348,707-708; `W/advice/CriticEntryRuleVsCode.md:30-33`; its committed stdout:4,11-13. | **holds** — existing component evidence supports all three statements; not rerun here. |
| 120-121 | “The counter therefore meets the rule for ASCII signatures and positional frames only.” | Same committed stdout:4,13; A3:348,707. | **breaks** — ASCII signature already appears in the Unicode counterexample; ASCII TAB blankness remains wrong. See F3. |
| 125 | “It is a necessary condition, not a sufficient one.” | Entry rule and ensuing untested channels/transforms; plan's exploratory scope. | **holds as the stated limit** — this audit does not prove universal necessity for every possible counter design. |
| 125-126 | Non-body and transformed echoes are separate classes. | Round-27 preregistration:30,33; w1-controls/spec.json:52-54. | **holds** as the documented threat-class separation. |
| 127-130 | Preregistration names log/help/warning and transformed-request classes; CtlFileEcho was assigned file/model content. | `.ufo/waves/round-27/preregistration.json:30,33`; `.ufo/waves/round-27/w1-controls/spec.json:52-54`. | **holds** — exact classes and named seat exist in committed bytes; the old scratch paths in that task text were not followed or read. |
| 131-133 | No committed A3 control receipt for those classes; dead attempt-2 dispatched wave left no committed receipts. | Plan:7-8; lesson:14-20; reviewed w1-controls tree contains six dispatch/spec files, no out/advice; ancestor log for those receipt paths is empty. | **holds within the specified wave/A3 scope** — earlier A0/A1 control receipts do exist elsewhere; the sentence must retain its A3/attempt-2 qualifier. |
| 134-136 | Excludes help/version and log/responses of one default healthy profile; warnings reached only elsewhere are unsampled. | A3:480-503,652-656; baseline requests:144-153. | **holds** — an exclusion test, not universal sampling of all warning branches. |
| 137-138 | C1 was not run on data, so these counts do not establish genuine-fault versus shortcut discrimination on real rows. | Plan:7-18; lesson:14-38; receipt component scopes. | **holds** — no scoring run was performed by this critic. |
| 139-140 | Other servers/builds may echo elsewhere; both S137 and live probe are scoped to 704366d76 and ASCII signatures. | Upstream S137 and helper; live receipt's ASCII values and pinned version. | **breaks only on shared ASCII attribution** — build pin and ASCII probe scope hold; source code has no ASCII restriction. See F5. |

# Exercised evidence: commands, outputs, exit codes

## Committed bytes

Exact subprocess commands are enumerated in `checked-objects.json` as `git_commands[].command`; each has exit **0**, empty stderr, byte count and SHA-256. They use this exact form (the angle-bracket version is notation; the manifest contains every actual argument):

```text
timeout 20s git -C /home/vgpnk/Projects/shokunin/kama-shokunin show <revision>:<path>
```

Representative commands actually run:

```sh
timeout 20s git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 52632caa2ed813c1c12f7a9dcab3556b4f0bd9eb:corpus/knowledge/echo-discriminating-counters.md
timeout 20s git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 52632caa2ed813c1c12f7a9dcab3556b4f0bd9eb:.ufo/waves/round-27/count-c1.py
timeout 20s git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 1471f67659917cc0823caf6e08303a3a26977d66:.ufo/waves/round-27/count-c1.py
timeout 20s git -C /home/vgpnk/Projects/shokunin/kama-shokunin show eb09e742:.ufo/waves/round-26/count-c1.py
```

Computed from those returned bytes, not from filenames:

```text
Entry: 9183 bytes, sha256 fd0d2b084d921c6cd3bd4b4d6811ab8801c2760bcbd4d1164f1a6ce9e2051de6
A3 at both named revisions: 33468 bytes, sha256 49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765
R26: 18372 bytes, sha256 6501737c749926be9d6b37761175d76f89876976c46bd5951fc1a3520c796588
Shortcut receipt: sha256 6020a2c39cf698860f64216754925ed623c7225c47871a1644e0c8e6d3d7ac19
Shortcut registry: sha256 1b78c8aa0423151b9d84f6ad3cef35de7e5260e5ec869fea764ba5dbcc691b91
```

Additional exact read-only commands:

```sh
timeout 20s git -C /home/vgpnk/Projects/shokunin/kama-shokunin grep -n -i -E 'JSON-decoded|message.frame|request.echo|server.echo|not.echoed' a720399e627b23026143646cb8de470b266346b5 -- corpus/QUALITY.md corpus/knowledge
```

Exit **1**, stdout empty: no matches on the specified base surfaces. This is a scoped negative search, not a mathematical proof against every paraphrase.

```sh
timeout 20s git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree -r --name-only 52632caa2ed813c1c12f7a9dcab3556b4f0bd9eb -- .ufo/waves/round-27/w1-controls
```

Exit **0**; stdout contains exactly `dispatch.json`, `dispatched-payload.json`, `solution-spaces.json`, `spawn-result.txt`, `spec.json`, and `validate.err` under that directory.

```sh
timeout 25s git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --format=%H 52632caa2ed813c1c12f7a9dcab3556b4f0bd9eb -- .ufo/waves/round-27/w1-controls/out .ufo/waves/round-27/w1-controls/advice
```

Exit **0**, stdout empty. An earlier broader `ls-tree` command also included `.ufo/waves/round-27/controls`; it returned earlier-amendment control files as well. Those are not misreported as absent A3 receipts.

## Primary-source fetches

Actual programmatic read, in a bounded Eval cell, with at most six concurrent fetches:

```python
with urllib.request.urlopen(url, timeout=25) as r:
    data = r.read(2_000_000)
    status = r.status
lines = data.decode().split("\n")
```

All six URLs returned **HTTP 200**. These were Python/network operations, not subprocesses: OS exit code is **not applicable**; the Eval cells completed successfully. LF indexing matters because RFC 8259 contains form-feed page separators: `splitlines()` would shift its source line numbers.

| Source | SHA-256 |
|---|---|
| [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259.txt) | `61a5378f4255c720beb2a4b4a63b29540147c140f36988bf086291989b4cd2d7` |
| [server-common.cpp @ 704366d76](https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp) | `b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442` |
| [server-common.h @ 704366d76](https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.h) | `ee401cf81ed0fb515f9870b018c762074903e72712dcb81a652e49761fe1577b` |
| [server.cpp @ 704366d76](https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp) | `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4` |
| [chat.cpp @ 704366d76](https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/chat.cpp) | `3793510ff80015d575777f01f9edcf8a58d859188d4f988190a02c50763bab49` |
| [server-models.cpp @ 704366d76](https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-models.cpp) | `9c5a6f2cc7997a3a409482c53119a2462e8c409ddf001cc568a9a8740e708b4a` |

No incorrect Entry source-line anchor was found in these raw bytes. The defects concern what the correctly cited code/receipts establish, not a fabricated quote or shifted committed pointer. The URL `read` tool's ranged/raw output was not faithful to original-byte line indexing; it was reported through `xd://report_issue`, and the final audit uses the independently fetched, hash-matching raw bytes instead.

## Receipt recomputation from committed JSON/fixtures

These are static calculations from committed evidence, **not reruns of reported failing probes**:

```text
R26 original rows: 12; string bodies 12; first-character escapes 12;
raw-body signature absence 12; decoded response_format.type equals signature 12.
Offline receipt totals: r26_echo_flags=0; a3_f_echo_flags=0;
a3_f_echo_flags_if_decoded=12; a3_shape_rejects=12.
Live fixtures: 12/12 request/response hashes and lengths match their receipt;
all parsed request types/response JSON/messages match;
req1/req2/req3 response bytes identical; decoded error frames equal.
Live replay receipt: 5 rows, A3-f refuses 5, R26 raw-echo passes 3.
Frame receipts: pristine 1 (recorded detector exit 0),
mutated 12 (recorded detector exit 1), restored 1 (recorded detector exit 0).
Boundary receipt: captured messages 12, actual fixed prefix 1,
echo hits 0, literal-cut frames 12, mechanical echo/frame accepts 12.
```

The detector exits above are **read from existing receipts**, not newly exercised process exits. The live probe's 07:11:54Z run, binary/model version, shutdown and port closure are likewise historical receipt provenance; this critic did not start or independently rerun that server.

# Operational closure

Only this report and the two evidence exports under the assigned output directory were written. No tools were installed or updated. No source, Git index/state, operator configuration, dead-seat scratch, or other lane was written. No counter was imported/executed, no `main()` was called, no server was started, no nested agent/runtime was invoked, and all finite subprocesses started for Git reads returned. There are no seat-started services or server trees to kill. Universal discrimination, real-row admission, C1 scoring, and the canonical X1 verdict remain unrun and unverified by this critic.
