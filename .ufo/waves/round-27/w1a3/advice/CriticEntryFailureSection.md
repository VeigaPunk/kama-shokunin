VERDICT: holds — All four factual sentences in “The failure it answers” match the committed counter and the 12-row shortcut evidence; no wrong line, count, escape, or message-frame assertion was found.

# Scope and axes

Reviewed only `corpus/knowledge/echo-discriminating-counters.md:14-24`, against commit `324d5d62e61276af312c8eb42f678004aec245d1` and the named round-26 counter revision `eb09e742`. Axes: **calibration** (what the old counter actually credited), **factual precision** (counts, line anchors, encodings and frames), **provenance** (committed rather than scratch evidence). This is a local sentence audit, not a verdict on X1 or the withdrawn C1.

All shell commands below ran with cwd `/home/vgpnk/Projects/shokunin/kama-shokunin`; all exited **0**. No counter main, generator, server, model, build or test was run. No tools were installed or updated. All processes started by this seat were finite commands and have returned.

# Per-sentence table

Command letters refer to the exact commands and observed outputs below. Line references are relative to the lane root.

| Sentence | Check command | Observed | Holds/breaks |
|---|---|---|---|
| “Round 26 froze a counter that credited a row when the live error message held the signature and the signature was \"not echoed\".” (`:16-17`) | A, B; `read` of `.ufo/waves/round-26/count-c1.py:350-409` | The preregistration-era counter at `a23c0e04` and the counter at `eb09e742` have the same specified SHA-256. Lines 382-384 require an observed error, the signature in the channel, and `e_not_echoed`; line 396 also requires all other checks. This sentence describes those echo/error conditions, not their sufficiency by themselves. | holds |
| “The echo check compared the signature with the **raw request bytes** (`git show eb09e742:.ufo/waves/round-26/count-c1.py`, line 384: `c[\"e_not_echoed\"] = sig not in req_bytes`).” (`:17-20`) | A, B; `read` of `.ufo/waves/round-26/count-c1.py:350-409` | **Line 384 is exactly the quoted assignment.** Lines 369-374 preserve a string-valued body without JSON-decoding it and include that body in `req_bytes`. Technical precision: `req_bytes` is a composite Python string, not a captured transport-byte buffer; it additionally includes serialized trigger metadata, args, path and headers. The claimed raw-versus-decoded failure is nevertheless correct. | holds |
| “After data, a critic met the frozen target from the base tree with 12 rows.” (`:20-21`) | B, C, E; `read` of `corpus/lessons/round-26-verifier-spotcheck.md:90-125` and `gen_shortcut.py:55-124` under the shortcut output directory | Receipt: base `1560e4d83f42b04f40336357de6f9637eafa0f4b`, registered 12, counted 12, target 12, met true. Generator lines 61 and 72-124 construct a base extract plus the frozen counter, pinned source scaffold and 12 fixture rows. The spot-check explicitly records the post-data shortcut (`:25-27`, `:100-103`). E independently places the shortcut receipt's landing after the data registry's landing; commit order alone is not a runtime timestamp. “From the base tree” must not be read as an untouched base tree: the sentence itself specifies adding rows. | holds |
| “Each was one generic message plus a string the request supplied: every request body spelled the value with a leading `\u00XX` escape, so the raw bytes never held the signature, while the server's message did (`lessons/round-26-verifier-spotcheck.md:98-116`).” (`:21-24`) | C, D, F; `read` of `corpus/lessons/round-26-verifier-spotcheck.md:98-116` | All 12 bodies begin `response_format.type` with the stated escape; none contains its full signature literally, while JSON decoding yields exactly its signature. Every recorded response has status 400 and `error.message` exactly equal to the same fixed prefix plus that row's signature. All 12 IDs and signatures pair correctly between registry and receipt. The cited spot-check states these facts at 106-110; its 111-113 identifies the one generic error plus 12 strings. | holds |

# Strongest local attack and smallest safe correction

**Counterexample attempted:** a thirteenth row, one body without the leading escape, one signature already present literally, or one response with a different frame would break the universal wording. The complete registry/receipt scan found none: 12/12 satisfy every stated encoding and frame property. Representative `X26-01` uses `\u005fNSGetExecutablePath failed after buffer resize` in the body (`shortcut.registry.json:19`), while the recorded message contains `_NSGetExecutablePath failed after buffer resize` (`shortcut.receipt.json:29`). This is a counterexample to the round-26 echo guard, not to the proposed failure description.

**Precision pressure:** “raw request bytes” is shorthand for non-decoded request text, and “from the base tree” is shorthand for a base extract augmented by shortcut rows and pinned evaluation scaffold. Neither changes the documented 12/12 result. No factual correction is required. The smallest optional clarification is to say **“non-decoded request text (`req_bytes`, including the raw body)”** and **“a base-tree extract with 12 shortcut rows and the pinned counter/source scaffold.”** No counter or target change follows from this audit. No impacted axis is shown to regress by these four sentences; whether X1 merits any axis judgment belongs to the later non-author reviewer/canonical judge.

# Commands and evidence

## A — Frozen and inspected counter bytes

Exact commands:

```sh
timeout 20s git -C /home/vgpnk/Projects/shokunin/kama-shokunin show a23c0e04:.ufo/waves/round-26/count-c1.py | sha256sum
timeout 20s git -C /home/vgpnk/Projects/shokunin/kama-shokunin show eb09e742:.ufo/waves/round-26/count-c1.py | sha256sum
timeout 20s sha256sum .ufo/waves/round-26/count-c1.py
```

Each exit 0; each SHA-256:

```text
6501737c749926be9d6b37761175d76f89876976c46bd5951fc1a3520c796588
```

The inspected file's line 384, returned by `read` at `:350-409`:

```text
384: c["e_not_echoed"] = sig not in req_bytes
```

## B — Committed identities and inspected-byte correspondence

Exact commands:

```sh
timeout 20s git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree -r 324d5d62e61276af312c8eb42f678004aec245d1 -- corpus/knowledge/echo-discriminating-counters.md corpus/lessons/round-26-verifier-spotcheck.md .ufo/waves/round-26/count-c1.py .ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/gen_shortcut.py .ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.registry.json .ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.receipt.json
timeout 20s git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --exit-code 324d5d62e61276af312c8eb42f678004aec245d1 -- corpus/knowledge/echo-discriminating-counters.md corpus/lessons/round-26-verifier-spotcheck.md .ufo/waves/round-26/count-c1.py .ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/gen_shortcut.py .ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.registry.json .ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.receipt.json
```

Both exit 0. `ls-tree` returned all six files as blobs, including:

```text
90a301d57c8c127db6367c158b38986a41013cd7  count-c1.py
764da3ff6722f1c0c035466916e4e4c2b11d7874  gen_shortcut.py
1409cc194d24b973d9e5e2d88f6b0bdbb551692b  shortcut.receipt.json
16505640d01a390ef0de47fe94ad070612f69ae1  shortcut.registry.json
4e74b5b583819dd3aa2202ae89d15e83b7aa818c  echo-discriminating-counters.md
87afbfb317f8bf7bfbcc2616f69495813f666fa9  round-26-verifier-spotcheck.md
```

`diff` output was empty. Blob paths above are trimmed to filenames; the command used their full paths.

## C — Count and exact shared message frame

```sh
timeout 20s jq '{base,target,registered,counted,met,rows:(.rows|length),all_counted:([.rows[].counted]|all),all_status_400:([.rows[].observed.status==400]|all),all_one_frame_plus_signature:([.rows[]|(.observed.channel_excerpt|fromjson|.error.message)==("response_format type must be one of \"text\" or \"json_object\", but got: "+.signature)]|all),all_echo_check_true:([.rows[].checks.e_not_echoed]|all)}' .ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.receipt.json
```

Exit 0:

```json
{"base":"1560e4d83f42b04f40336357de6f9637eafa0f4b","target":12,"registered":12,"counted":12,"met":true,"rows":12,"all_counted":true,"all_status_400":true,"all_one_frame_plus_signature":true,"all_echo_check_true":true}
```

Count anchors: `shortcut.receipt.json:5,321-323`. Message anchors: `:29,55,81,107,133,159,185,211,237,263,289,315`.

## D — Every raw/decoded body and leading escape

```sh
timeout 20s jq '{rows:(.signatures|length),all_leading_u00:([.signatures[].request.body|test("\"type\":\"\\\\u00[0-9a-fA-F]{2}")]|all),no_raw_signature:([.signatures[]|. as $s|(.request.body|contains($s.signature)|not)]|all),all_decoded_equal:([.signatures[]|. as $s|(.request.body|fromjson|.response_format.type)==$s.signature]|all)}' .ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.registry.json
```

Exit 0:

```json
{"rows":12,"all_leading_u00":true,"no_raw_signature":true,"all_decoded_equal":true}
```

Body anchors: `shortcut.registry.json:19,41,63,85,107,129,151,173,195,217,239,261`. Escapes in row order: `\u005f`, `\u0047`, `\u0052`, `\u0054`, `\u0079`, `\u0075`, `\u0049`, `\u0075`, `\u0045`, `\u0043`, `\u0043`, `\u0073`.

## E — Artifact landing chronology

```sh
timeout 20s git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --format=%H%x20%cI%x20%s 324d5d62e61276af312c8eb42f678004aec245d1 -- registry/error-signatures-r26.json .ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.receipt.json
```

Exit 0; output trimmed to commit, timestamp and relevant subject:

```text
fd48f9a3b7ca9dc7be342d9e7ce56844f0a21e50 2026-10-23T01:09:37-03:00 round-26: falsify-wave corrections ... wave-2 evidence
7f84cd0e7662432b7b93e7586f86a40b06e5fdae 2026-10-23T00:50:35-03:00 round-26: C1 live error signatures ... wave-1 evidence
```

The explicit post-data attribution is in the committed spot-check `:25-27,98-113`, rather than inferred solely from these commit timestamps.

## F — Complete row pairing and composite request-text scan

```sh
timeout 20s jq -s '.[0] as $r | .[1] as $p | [range(0; ($r.signatures|length)) | . as $i | $r.signatures[$i] as $s | $p.rows[$i] as $o | ($s.request.body | fromjson) as $b | ($o.observed.channel_excerpt | fromjson) as $m | {id:$s.id, paired:($s.id==$o.id and $s.signature==$o.signature), prefix_escape:($s.request.body | test("\"type\":\"\\\\u00[0-9a-fA-F]{2}")), raw_signature_present:($s.request.body|contains($s.signature)), decoded_signature_equal:($b.response_format.type==$s.signature), message: $m.error.message, frame:($m.error.message | sub($s.signature|"";"")), exact_frame_plus_signature:($m.error.message==("response_format type must be one of \"text\" or \"json_object\", but got: "+$s.signature)), observed_status:$o.observed.status, counted:$o.counted}] as $rows | {base:$p.base, registry_rows:($r.signatures|length), receipt_rows:($p.rows|length), registered:$p.registered,counted:$p.counted,target:$p.target,met:$p.met,paired:([$rows[].paired]|all),leading_u00_escape:([$rows[].prefix_escape]|all),raw_contains_signature:([$rows[].raw_signature_present]|any),decoded_equals_signature:([$rows[].decoded_signature_equal]|all),same_frame:([$rows[].exact_frame_plus_signature]|all),all_status_400:([$rows[].observed_status==400]|all),all_counted:([$rows[].counted]|all)}' .ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.registry.json .ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.receipt.json
```

Exit 0. Output, trimmed to the independent pairing result and core totals:

```text
registry_rows=12 receipt_rows=12 paired=true
leading_u00_escape=true raw_contains_signature=false decoded_equals_signature=true
same_frame=true all_status_400=true all_counted=true
```

A separate complete-row command also included the trigger serialization, args, path and headers in the non-decoded comparison surface (matching the surface categories at counter `:366-374`):

```sh
timeout 20s jq -sr '.[0] as $r | .[1] as $p | range(0; ($r.signatures|length)) as $i | $r.signatures[$i] as $s | $p.rows[$i] as $o | ($s.request.body|fromjson) as $b | ($o.observed.channel_excerpt|fromjson) as $m | ([$s|{channel,args,model,occupy_port,request}|tojson, ($s.args|join(" ")), $s.request.path, ($s.request.headers|tojson), $s.request.body]|join("\n")) as $raw | [$s.id, ($s.request.body|capture("\"type\":\"(?<escape>\\\\u[0-9a-fA-F]{4})").escape), ($s.signature|length), (($raw|contains($s.signature))|not), ($b.response_format.type==$s.signature), ($m.error.message==("response_format type must be one of \"text\" or \"json_object\", but got: "+$s.signature)), $o.observed.status, $o.counted] | @tsv' .ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.registry.json .ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.receipt.json
```

Exit 0. Columns: id, escape (TSV-escaped), signature length, absent from composite request text, decoded-equal, exact-frame-plus-signature, status, counted. First and last output rows:

```text
X26-01  \\u005f  47  true  true  true  400  true
X26-12  \\u0073  49  true  true  true  400  true
```

The intervening ten rows likewise returned `true true true 400 true`. This jq serialization is not asserted byte-for-byte identical to Python `json.dumps`; the literal code and the recorded `e_not_echoed` checks provide the exact Python-counter evidence. Nothing here is a fresh live reproduction.
