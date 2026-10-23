```RESULTS
cwd (both commands): /home/vgpnk/Projects/shokunin/kama-shokunin

COMMAND 1:
sha256sum .ufo/waves/round-31/count-c1.py .ufo/waves/round-31/sources/llama.cpp-704366d/server-common.cpp .ufo/waves/round-31/sources/SNAPSHOT.json registry/chat-param-outcomes-r31.json .ufo/waves/round-31/w1/out/DataA10/row.json .ufo/waves/round-31/w1/out/DataA10/counter.json
EXIT CODE: 0
VERBATIM TAIL (complete stdout):
d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216  .ufo/waves/round-31/count-c1.py
b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442  .ufo/waves/round-31/sources/llama.cpp-704366d/server-common.cpp
685b93876ed40cdf1f40a38e093ab179f23ad9f1000591cd7c7414bd8343b021  .ufo/waves/round-31/sources/SNAPSHOT.json
c79d193605997d21d7f4fa7f621b6f8b56ab1442963daf12ef31a3f4476447f5  registry/chat-param-outcomes-r31.json
276c614b1d9600d2f75cf06e8b4c2b1de6f0e641ab07e229f1732b4363bdfa08  .ufo/waves/round-31/w1/out/DataA10/row.json
a04f16c44e4a4047ac50745e2930eefb6ead9b329ba07bcfef9ac04b556a094e  .ufo/waves/round-31/w1/out/DataA10/counter.json

COMMAND 2:
python3 -c 'import json,sys; raw,actual,suffix=sys.argv[1:]; literal=json.loads(raw); print("raw_cpp_literal="+raw); print("decoded_cpp_literal="+literal); print("inherited_emitted_message="+actual); print("sent_response_type="+suffix); print("emitted_equals_static_literal="+str(actual==literal)); print("emitted_equals_literal_plus_value="+str(actual==literal+suffix)); print("difference_after_decoding="+repr(actual[len(literal):] if actual.startswith(literal) else None)); print("decoded_prefix_occurs_in_raw_literal="+str(literal in raw)); print("full_message_occurs_in_raw_literal="+str(actual in raw))' '"response_format type must be one of \"text\" or \"json_object\", but got: "' 'response_format type must be one of "text" or "json_object", but got: xml' xml
EXIT CODE: 0
VERBATIM TAIL (complete stdout):
raw_cpp_literal="response_format type must be one of \"text\" or \"json_object\", but got: "
decoded_cpp_literal=response_format type must be one of "text" or "json_object", but got: 
inherited_emitted_message=response_format type must be one of "text" or "json_object", but got: xml
sent_response_type=xml
emitted_equals_static_literal=False
emitted_equals_literal_plus_value=True
difference_after_decoding='xml'
decoded_prefix_occurs_in_raw_literal=False
full_message_occurs_in_raw_literal=False

No other shell commands ran. Both stderr streams were empty. Read/grep/glob/write operations are recorded separately in the evidence notes, not assigned shell exit codes.
```
FINDING: refusal correct yes under frozen rule (e); this is a genuine adapter-authored dynamic message that the literal-source test excludes.
LIMITS: No live server, frozen counter, canonical judge, build, or test suite was run. The emitted response is inherited DataA10 evidence, not a fresh observation; the comparison command uses transcribed strings. This review establishes neither current endpoint health nor the overall C1 count/admission.

## Two strings, side by side

Decoded string values shown in JSON notation; the pinned static literal ends with one space.

| Pinned static literal, L1375 | Recorded emitted message for `{"type":"xml"}` |
|---|---|
| `"response_format type must be one of \"text\" or \"json_object\", but got: "` | `"response_format type must be one of \"text\" or \"json_object\", but got: xml"` |

- **(a) Equal? No** to the static literal or raw snapshot substring. **Yes** to the pinned expression's value for this input: the source throws `std::invalid_argument(<literal> + response_type)`, and L1366 obtains `response_type` from `response_format.type`.
- **(b) Exactly the offending value? Yes after C++ unescaping:** the only appended bytes are `xml`. But **not merely a suffix issue for the frozen raw-source test**: the source spells the inner quotes `\"`, whereas the decoded error message contains `"`. Even removing `xml` would not make that decoded prefix occur verbatim in the raw snapshot; both whole-file grep probes found no match.
- **(c) Refusal correct yes:** rule (e), `count-c1.py:42-43`, explicitly demands verbatim occurrence. Its implementation at L465-466 is raw substring membership and appends `reject-message-not-adapter`. The inherited `DataA10/counter.json` records precisely that sole reason and `live: {}`; L476-478 shows a preflight reason skips the row's live check. This is not evidence of a failed live message comparison.

## Counterexample and evidence

`registry/chat-param-outcomes-r31.json:190-205` and `SKILL.md:1256` agree on the exact 400 / `invalid_request_error` message and cite S181, `server-common.cpp:1375`. S181 quotes the dynamic throw expression. The inherited `w1/out/DataA10/row.json:134-140` contains that exact error envelope in both `response_excerpt` and the server-log exception. Its old source id S198 was remapped to S181 in the integrated registry; the filename and L1375 remain the same.

The counter and source hashes match their frozen pins (command 1). The local evidence therefore defeats the interpretation “uncounted because the error was not authored by the adapter.” It does **not** defeat the narrower statement “uncounted because the complete decoded message is absent from the source bytes.” The rule is over-narrow for its adapter-provenance purpose, while this refusal obeys the frozen rule.

## Axes and smallest safe correction

- **Depth:** one evidenced reject behavior is excluded by a false-negative provenance proxy.
- **Calibration:** distinguish frozen-rule compliance from source provenance and live equality; `reject-message-not-adapter` is not a reliable semantic diagnosis here.
- **Operability:** no service, port, runtime fixture, or lane implementation was changed.

Keep K31-10 refused in round 31; do not edit the frozen rule or strip the outcome message to obtain a count. A later, pre-data rule can accept a decoded pinned literal plus the explicitly bound request value at the cited throw expression, while retaining the exact live envelope/message comparison. A generic prefix/substring exemption would discard the protection. This is advisory evidence, not a round verdict or admission.

Raw receipts: `commands.log`, `source-evidence.txt`, and `inherited-counter.json` in this directory. No tools were installed or upgraded. No tracked lane file was edited.
