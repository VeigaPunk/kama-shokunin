```RESULTS
[01-mkdir]
$ mkdir -p /tmp/kama-r31w2/RevRowD /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowD
exit: 0
verbatim tail:

[02-clone]
$ /usr/bin/git clone --no-hardlinks --no-checkout /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r31w2/RevRowD/lane
exit: 0
verbatim tail:
Cloning into '/tmp/kama-r31w2/RevRowD/lane'...
done.

[03-checkout]
$ /usr/bin/git -C /tmp/kama-r31w2/RevRowD/lane checkout -q 382d11b2107d335705875da1a4d889b074bd6fa6
exit: 0
verbatim tail:

[04-counter-sha256]
cwd: /tmp/kama-r31w2/RevRowD/lane
$ sha256sum .ufo/waves/round-31/count-c1.py
exit: 0
verbatim tail:
d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216  .ufo/waves/round-31/count-c1.py

[05-c1-live]
cwd: /tmp/kama-r31w2/RevRowD/lane
env: TMPDIR=/tmp/kama-r31w2/RevRowD PYTHONDONTWRITEBYTECODE=1
$ /usr/bin/python3 .ufo/waves/round-31/count-c1.py --lane /tmp/kama-r31w2/RevRowD/lane --repo /tmp/kama-r31w2/RevRowD/lane --tip 382d11b2107d335705875da1a4d889b074bd6fa6 --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowD/c1-live.json
exit: 0
verbatim tail:
registered 18 counted 17 target 12 met True not-counted ['K31-10']

[06-meaning-probe]
cwd: /tmp/kama-r31w2/RevRowD/lane
env: TMPDIR=/tmp/kama-r31w2/RevRowD PYTHONDONTWRITEBYTECODE=1
$ /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowD/probe-meaning.py --clone /tmp/kama-r31w2/RevRowD/lane --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowD/meaning-probe.json
exit: 0
verbatim tail:
base status=200 sse_done=False non_done_frames=0
K31-11-registered status=500 sse_done=False non_done_frames=0
{"error":{"code":500,"message":"Cannot use both json_schema and grammar","type":"server_error"}}
K31-11-counterexample status=200 sse_done=False non_done_frames=0
K31-12-registered status=400 sse_done=False non_done_frames=0
{"error":{"code":400,"message":"logprobs is not supported with tools + stream","type":"invalid_request_error"}}
K31-12-counterexample status=200 sse_done=True non_done_frames=3

[07-hand-render-compare]
cwd: /tmp/kama-r31w2/RevRowD/lane
env: PYTHONDONTWRITEBYTECODE=1
$ /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowD/compare-cells.py --clone /tmp/kama-r31w2/RevRowD/lane --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowD/cell-comparison.json
exit: 0
verbatim tail:
K31-11 committed-cell==rendered=yes utf8_bytes=64
K31-12 committed-cell==rendered=yes utf8_bytes=79

```

FINDING: Both registered rejection outcomes reproduce exactly, but both meaning cells overclaim. K31-11 accepts an empty grammar; K31-12 accepts explicit `logprobs:false` with tools and streaming.

LIMITS: These are observations on pinned b11755, stories260K, and default server arguments, not all builds, models, payloads, or API effects. HTTP 200 does not prove schema-constrained generation or tool execution. This review does not validate the other 16 rows, the C1 target's discrimination, or round admission. The full counter's exit 0 means it evaluated, not that its meaning prose is correct. One full frozen-counter run and one five-request contrast probe ran; no other live checks ran.

Axes: depth (actual adapter behavior), calibration (scope of prose versus measured evidence), operability (correct client advice). No improvement/admission judgment is made.

## Assigned rows

```text
K31-11 | committed-cell==rendered yes | live-status 500 server_error, code 500 | overclaim blanket grammar prohibition: the same schema with grammar:"" returns 200
K31-12 | committed-cell==rendered yes | live-status 400 invalid_request_error, code 400 | overclaim must omit logprobs: explicit logprobs:false with unchanged tools and stream returns 200
```

## Rendering, independently derived

For each registry `outcome.kind = reject`, concatenate `reject `, the decimal status, one space, the type, `: `, and the message. The frozen bytes put RENDER at docstring lines 50–54, not the assignment's stale 40–46 pointer.

- K31-11: `reject 500 server_error: Cannot use both json_schema and grammar` — 64 UTF-8 bytes, byte-identical to the committed outcome cell at SKILL.md:1257.
- K31-12: `reject 400 invalid_request_error: logprobs is not supported with tools + stream` — 79 UTF-8 bytes, byte-identical to SKILL.md:1258.

The hand-derived literals were compared by `compare-cells.py`, which never imports the counter or calls `render()`. Exact table rows, committed and derived strings, and both hex encodings are saved in [cell-comparison.json](cell-comparison.json). Extraction strips table delimiter padding, as the frozen cell definition does.

## Full frozen-counter receipt

The isolated clone was checked out at `382d11b2107d335705875da1a4d889b074bd6fa6`; the frozen counter SHA-256 matched `d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216`. Its complete run printed:

```text
registered 18 counted 17 target 12 met True not-counted ['K31-10']
```

Assigned `live` blocks from [c1-live.json](c1-live.json):

```json
{
  "K31-11": {
    "status": 500,
    "error_keys": ["code", "message", "type"],
    "message": "Cannot use both json_schema and grammar",
    "type": "server_error",
    "code": 500
  },
  "K31-12": {
    "status": 400,
    "error_keys": ["code", "message", "type"],
    "message": "logprobs is not supported with tools + stream",
    "type": "invalid_request_error",
    "code": 400
  }
}
```

These support the two registered request/error contracts, independently of the `counted` flags. They do not support all conditions in the meaning prose. The frozen counter itself says meaning correctness is not checked (docstring lines 56–57); implementation lines 433–434 check only word count.

## Counterexamples and smallest safe corrections

**K31-11 — missing nonempty qualifier.** The registered request is the base `{messages:[{role:"user",content:"hi"}],max_tokens:1}` plus `json_schema:{"type":"object"}` and `grammar:'root ::= "a"'`. The contrast probe first reproduced its exact HTTP 500 envelope, then changed only `grammar` to `""`. It returned HTTP 200 while both keys remained present. The pinned source corroborates the distinction: server-common.cpp:1359 tests `!json_schema.is_null() && !grammar.empty()` before throwing at line 1360. This is a fixable precision defect in the prose, not evidence against the measured reject cell. Smallest safe meaning correction:

> On this fixture, a non-null json_schema combined with a nonempty grammar string is rejected with HTTP 500.

**K31-12 — omission is not necessary.** The registry sends `logprobs:true`, `stream:true`, and one `noop` function tool. The contrast probe reproduced the HTTP 400 envelope, then changed only `logprobs` to `false`. It returned HTTP 200, three non-DONE JSON data frames and `[DONE]`; the key was still present. Thus clients need not omit the field. The source at server-common.cpp:1515–1517 places the tools/stream rejection inside the truthy-logprobs branch. The fixture has no `top_logprobs`; the separate line-1520 rejection is not being generalized away. Smallest safe meaning correction:

> On this fixture, tools plus streaming rejects logprobs:true; omit logprobs or set it false when not requesting top_logprobs.

Both corrections narrow advice to the actual predicate, preserving the measured outcome cells and frozen registry. Neither establishes a round-level improvement or repairs the separately documented no-op counter attack.

## Evidence and scope

- [commands.json](commands.json) records every seat-launched process command, exit, complete combined stdout/stderr, and verbatim tail. The opening block contains all seven commands; empty tails are intentionally empty. Counter/probe-internal git and server subprocesses are part of those recorded entry commands.
- [c1-live.json](c1-live.json), [05-c1-live.log](05-c1-live.log): full frozen run and console output.
- [meaning-probe.json](meaning-probe.json), [06-meaning-probe.log](06-meaning-probe.log): all five actual requests, HTTP statuses/headers, UTF-8 response bodies, lossless body hex, and SSE checks. The probe revalidated binary, implementation-library, and model hashes against the cloned registry and used the frozen server lifecycle helper; its recorded port was 47917.
- [meaning-server.log](meaning-server.log): raw probe server log snapshot taken before shutdown; the helper stopped the owned process in `finally`.
- [source-evidence.json](source-evidence.json): relevant pinned source guards and provenance. The full counter also checked snapshot digests.
- [probe-meaning.py](probe-meaning.py), [compare-cells.py](compare-cells.py): exact scoped probe/comparison programs, not counter replacements.
- Tools installed or updated: none. No tracked lane file was edited; git writes were confined to the fresh scratch clone. No services were restarted.
- The flat trailer path `.ufo/waves/round-31/w2/out/RevRowD.md` is outside the developer-authorized seat directory and was not written. The report is at the explicitly requested, authorized `.ufo/waves/round-31/w2/out/RevRowD/report.md`.
