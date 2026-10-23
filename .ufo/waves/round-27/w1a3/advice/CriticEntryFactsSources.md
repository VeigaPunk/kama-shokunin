VERDICT: partial — the decoded-string echo and shared-frame motivation hold, but the universal six-character escape claim contradicts RFC 8259 and “whatever string” needs qualification.

# Scope and axes

Reviewed only `corpus/knowledge/echo-discriminating-counters.md:26-37` against reopened S136/S137 sources and the same-revision helper/HTTP path. Impacted declared axis: **calibration**. Source fidelity, scope precision, and error/frame identity are review dimensions, not additional scoring axes. This is source-attack evidence for the later non-author reviewer, not an X1 verdict or a C1 score. C1 remains withdrawn before data.

Paths below are lane-relative. `E` denotes `.ufo/waves/round-27/w1a3/out/CriticEntryFactsSources/opened-source-excerpts.txt`; it contains selected reader-returned excerpts, explicitly not raw-byte snapshots.

# Per-claim findings

## 1. Many spellings / every character fits one six-character escape — partial; the universal subclaim breaks

- **Holds:** JSON escapes permit distinct raw spellings of the same decoded nonempty string. The ASCII escape shortcut does not require supplementary Unicode characters. The existing historical example is explicit: `shortcut.registry.json:8,19` under `.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/` supplies `_NSGetExecutablePath failed after buffer resize` with its initial underscore written `\u005f`; `shortcut.receipt.json:25-31` records the decoded text in the 400 message.
- **Breaks:** entry `:29-30` says **“Any character can be a six-character `\uXXXX` sequence.”** Reopened [RFC 8259 §7](https://www.rfc-editor.org/rfc/rfc8259.txt) explicitly restricts that form to the Basic Multilingual Plane, then requires a **12-character UTF-16 surrogate pair** for a supplementary character (`E:6-19`). Its own counterexample is G clef U+1D11E, written `\uD834\uDD1E`, not one `\uXXXX` escape. This contradiction is in the primary source; no parser experiment is needed to establish it.
- The same overstatement is duplicated in `corpus/SOURCES.md:148` (S136) and `corpus/QUALITY.md:219` (KQ37). Fixing the entry alone leaves a second authority repeating it.
- **Smallest safe correction:** “Any character may be escaped: BMP characters use `\uXXXX`; supplementary characters use a UTF-16 surrogate pair.” Change all three textual occurrences. Prefer “absence from raw request bytes does not rule out a decoded echo” over the entry's broader “says nothing.” No change to the decoded-echo rule follows from this defect.

## 2. `json_value` supplies a decoded string — holds for a present, correctly typed string

The round-27 snapshot contains the call site but no `server-common.h`. The definition was found in the **same-revision round-16 snapshot**, `.ufo/waves/round-16/sources/llama.cpp-704366d/server-common.h:43-56`, and independently reopened at the [pinned upstream header](https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.h#L43-L56).

The complete relevant chain is:

1. Round-27 `sources/llama.cpp-704366d/server-context.cpp:5564-5574` calls `json::parse(req.body)` before `oaicompat_chat_params_parse`.
2. The helper aliases `json = common_json` (round-16 header `:25`) and returns `body.at(key).get<T>()` (`:48`; `E:23-36`).
3. Reopened [common/json.cpp at the same commit](https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/json.cpp) delegates parsing to `ordered_json::parse(text)` and its `get<std::string>` specialization to the backing JSON value's getter (`E:40-54`). This is value extraction, not `dump()` or raw-request slicing.
4. Round-27 `sources/llama.cpp-704366d/server-common.cpp:1365-1366` instantiates the helper with `std::string()` and stores the result in `std::string response_type`.

**Qualification:** `json_value` is not itself the decoder, and does not recursively unescape strings. Parsing has already happened. Missing/null values and caught type errors return the default (header `:45-55`), not an arbitrary string representation of the supplied JSON value.

**Smallest safe correction:** retain the fact, optionally say “`json_value` retrieves the already-parsed string; missing/null/wrong-type values use its default.” Add the helper definition to the supporting source anchor if full retrieval semantics are claimed. Do not attribute the helper body to the round-27 CPP-only snapshot.

## 3. One fixed frame plus “whatever string the caller chose” — holds at the throw, partial as an unrestricted HTTP promise

- The exact construction is supported: round-27 `sources/llama.cpp-704366d/server-common.cpp:1375` appends `response_type` to one constant prefix. The local file's SHA-256 equals S137's registered hash (command evidence below).
- **Direct counterexample to “whatever”:** `response_type == "json_schema"` takes a separate accepted branch (`:1371-1373`), despite that choice not appearing in the error text's list. `"json_object"`, `"text"`, and the empty string also do not take this throw (`:1367-1375`). Wrong-type/null/missing values can default to empty. Thus this is specifically a nonempty, unrecognized string reaching this branch, not every caller-selected string producing that error.
- **Stronger boundary, [INFERENCE], unrun:** a parsed type containing an embedded U+0000 can reach the append at `:1375`, but `sources/llama.cpp-704366d/server.cpp:62-65` subsequently assigns `e.what()` (a C string) into `message`. Ordinary C-string assignment would truncate at that NUL; the full caller string is not thereby guaranteed to survive into `error.message`. `server-common.cpp:128-132` only packages the resulting `message`. No live request or C++ reproduction was run, so this is a source-derived boundary, not an observed HTTP result.
- **Smallest safe correction:** scope the assertion to the construction: “For a nonempty type other than `text`, `json_object`, or `json_schema`, this throw appends the already-parsed string to a fixed prefix.” That avoids promising arbitrary-value acceptance or lossless HTTP rendering without weakening the demonstrated ASCII echo attack.

## 4. “One frame of this kind serves any number of signatures” — holds as a many-label mechanism; not a measured unlimited result

The source has one throw site and one constant prefix, not a distinct fault branch for each appended value (`server-common.cpp:1363-1375`). The existing receipt records **12** labels with that prefix: `.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.receipt.json:29,55,81,107,133,159,185,211,237,263,289,315`, with totals `:321-323` (`registered: 12`, `counted: 12`, `met: true`). These are prior committed observations, not observations made by this seat.

[INFERENCE] Within the branch's domain and ordinary request/resource limits, changing the appended unrecognized string can produce further differently labelled messages without discovering another error site. That supports the one-frame motivation. Neither S137 nor the 12-row receipt demonstrates literally unlimited realizable requests, every possible signature, or correctness of the counter's frame-extraction algorithm. The entry's own `:11-12,65-66` correctly withholds discrimination-on-data claims; preserve that limit.

**Smallest safe correction:** “The same frame can carry many distinct caller-supplied ‘signatures’; they are not distinct faults.” This is a precision improvement, not evidence that the one-frame guard should be rejected.

# Minimal combined wording

For the later author to consider; no corpus changes were made:

> Any character may be escaped: BMP characters use `\uXXXX`, while supplementary characters use a UTF-16 surrogate pair. Absence from raw request bytes therefore does not rule out a decoded echo.
>
> Here `json_value` retrieves an already-parsed string. For a nonempty type other than `text`, `json_object`, or `json_schema`, this throw appends that string to a fixed prefix. The same frame can carry many distinct caller-supplied “signatures”; they are not distinct faults.

These are fixable source/scoping defects. The strongest source counterexample does **not** negate the decoded-echo failure or establish that the withdrawn counter discriminates. No admission, score, integration, or canonical judgment is supplied.

# Commands, outputs, and provenance limits

All commands used lane cwd `/home/vgpnk/Projects/shokunin/kama-shokunin`.

1. `timeout 10s mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/w1a3/out/CriticEntryFactsSources` — exit 0; no output.

2. Exact raw-fetch attempt (exit **28**):

```sh
timeout 35s bash -c 'ulimit -f 1048576 && ulimit -v 1048576 && ulimit -u 128 && exec curl --fail --silent --show-error --location --connect-timeout 10 --max-time 25 --output /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/w1a3/out/CriticEntryFactsSources/rfc8259.txt https://www.rfc-editor.org/rfc/rfc8259.txt'
```

Output: `curl: (28) Resolving timed out after 10000 milliseconds`.

3. Exact independent helper raw-fetch attempt (exit **28**):

```sh
timeout 35s bash -c 'ulimit -f 1048576 && ulimit -v 1048576 && ulimit -u 128 && exec curl --fail --silent --show-error --location --connect-timeout 10 --max-time 25 --output /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/w1a3/out/CriticEntryFactsSources/server-common.h https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.h'
```

Output: `curl: (28) Resolving timed out after 10000 milliseconds`.

No raw output files were left by those failures (the directory read afterward was empty). Reader-tool fetches succeeded instead; excerpts are in `E`. I do **not** claim to have reverified S136's raw-fetch SHA-256 or a freshly downloaded header's hash.

4. Exact local provenance command (exit 0):

```sh
timeout 10s sha256sum .ufo/waves/round-27/sources/llama.cpp-704366d/server-common.cpp .ufo/waves/round-16/sources/llama.cpp-704366d/server-common.h
```

Output:

```text
b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442  .ufo/waves/round-27/sources/llama.cpp-704366d/server-common.cpp
ee401cf81ed0fb515f9870b018c762074903e72712dcb81a652e49761fe1577b  .ufo/waves/round-16/sources/llama.cpp-704366d/server-common.h
```

5. Primary-source reopening used `read` with these exact selectors (successful tool reads; shell exit code not applicable):

```text
https://www.rfc-editor.org/rfc/rfc8259.txt
https://www.rfc-editor.org/rfc/rfc8259.txt:355-389:raw
https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp:1363-1377
https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.h:1-60:raw
https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/json.cpp:195-228:raw
https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/json.cpp:390-475:raw
```

The reader renders RFC text with its own line selection, so RFC authority is cited by **§7**, not by pretending reader line 355 is the original downloaded RFC line. The existing S136 anchor stops before the supplementary-character counterexample.

6. `timeout 10s pgrep -af llama-server` completed via background delivery; its numeric exit code was not surfaced. Trimmed output identified existing servers at ports `47637`, `47644`, `47636`, and `47680`. None was launched by this seat; none was touched.

No tool installs/updates. No subagents, server, counter main, test/build/lint, judge, or other serving/orchestration runtime was started. No lane/index/config writes; only this report and the scoped excerpt artifact were written. All bounded subprocess commands have completed.
