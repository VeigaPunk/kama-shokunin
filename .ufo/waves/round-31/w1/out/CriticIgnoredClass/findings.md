# CriticIgnoredClass — bounded no-ops, not universally ignored parameters

## Scope and axes

Assigned review only: C1 rows K31-13/14/15 on the exact pinned build, model, default argv, and base body `{"messages":[{"role":"user","content":"hi"}],"max_tokens":1}`. Axes at risk are **depth** (what the observation actually establishes), **calibration** (not inflating a projected equality into global ignorance), and **operability** (client advice about tools and effective defaults). This report neither judges nor admits the round.

**Result:** all three are `ignored-confirmed` for the frozen counter's bounded observational meaning. No parameter-attributable hidden effect was demonstrated on this fixture. **The weakest claim is K31-14, `parallel_tool_calls=false`: it explicitly supplies the already-effective false default, with no tools present.** This is a weak contrast, not evidence that the adapter never reads the parameter. The most hazardous broader extrapolation is that `tools` is universally ignored.

## Reproduction and evidence

All files linked below are in this item's exclusive output directory:

- [measure.py](measure.py): reproducible probe; imports only the frozen counter's normalization/comparison helpers, never its `main`.
- [raw.json](raw.json): exact request/response bodies, complete newest-slot records, per-request log byte ranges and text, response timings and usage, process identity, `/props`, metrics refusals, pins and cleanup.
- [summary.json](summary.json): per-arm counts, choice distributions, timing ranges and matched-seed comparisons.
- [server.log](server.log): complete server output, including initialization and shutdown.

Commands actually executed, all exit **0**:

```text
git clone -q --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/r31w1-CriticIgnoredClass && git -C /tmp/r31w1-CriticIgnoredClass checkout -q 0e6f8ed6891c09d5208ac1fdcb294ed9a842832e
sha256sum /home/vgpnk/.local/opt/llama-b11755/llama-server /home/vgpnk/.local/opt/llama-b11755/libllama-server-impl.so /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf
/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w1/out/CriticIgnoredClass/measure.py
```

The probe's `git -C /tmp/r31w1-CriticIgnoredClass rev-parse HEAD` also exited 0 and returned exactly `0e6f8ed6891c09d5208ac1fdcb294ed9a842832e`. No git command was run in the lane. No tracked lane file, frozen counter, registry or source row was changed.

Observed hashes, checked before starting the server:

| Artifact | SHA-256 |
|---|---|
| llama-server | `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804` |
| libllama-server-impl.so | `e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed` |
| stories260K.gguf | `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` |

All four source snapshot hashes matched `SNAPSHOT.json`; frozen C1 counter hash matched `d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216`. Full source hashes are in `raw.json.source_pins`.

The only server started was PID **4103564** on loopback port **47956**, free before launch, with this exact argv and `LD_LIBRARY_PATH=/home/vgpnk/.local/opt/llama-b11755`:

```text
/home/vgpnk/.local/opt/llama-b11755/llama-server -m /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 47956
```

`/proc/<pid>/exe` and cmdline matched that identity. `/props` reported `b11755-704366d76`, the pinned model path, four slots, 2048 context per slot, and a ChatML-like template referencing only messages and the generation-prompt flag. Its `supports_tools`, `supports_tool_calls` and `supports_parallel_tool_calls` capabilities were all **false**.

## Per-parameter observations

The default phase used **20 cycles**: exact base first, then each treatment once in deterministically shuffled order. All requests completed sequentially so `/slots`' largest `id_task` unambiguously belonged to the preceding completion. The second phase used **20 matched seeds, 0–19**, adding the same seed to each base/treatment pair. Those are separate causal controls, not a replacement for the exact-base measurements: **160 chat requests total**.

| Row / parameter and sent value | Finding | Default phase | Matched-seed control / deciding observation |
|---|---|---|---|
| K31-13 `user="probe-user"` | **ignored-confirmed** | 20/20 HTTP 200; 0/20 full slot-parameter deltas; 20/20 normalized responses equal the cycle base; `usage.prompt_tokens=42` throughout | 20/20 choice messages identical to their same-seed base, also with zero parameter deltas. No request log contained the user identifier or an identity-specific warning. |
| K31-14 `parallel_tool_calls=false` | **ignored-confirmed** | 20/20 HTTP 200; 0/20 full slot-parameter deltas; 20/20 normalized responses equal the cycle base; `usage.prompt_tokens=42` throughout | 20/20 choice messages identical to their same-seed base. `/props` reports `supports_parallel_tool_calls=false`, exactly the default read by adapter line 1426. Thus this confirms a default-equivalent no-op, not an unread key. |
| K31-15 nonempty `tools=[{"type":"function","function":{"name":"f","parameters":{"type":"object"}}}]` | **ignored-confirmed** | 20/20 HTTP 200; 0/20 full slot-parameter deltas; 20/20 normalized responses equal the cycle base; `usage.prompt_tokens=42` throughout | 20/20 choice messages identical to their same-seed base. The active template does not reference tools and advertises no tool support; all 20 default tool requests logged full prompt similarity (`f_sim_best=1.000`, `f_keep=1.000`) and retained the 42-token prompt. No evidence that this tool definition changed the rendered prompt. |

For all arms, `usage.completion_tokens=1`, `usage.total_tokens=43`, and choice `finish_reason="length"` throughout both phases. The seeded phase also preserved full slot-parameter equality against each **same-seed** baseline; changes of seed against the initial unseeded anchor are intentional controls, not parameter effects.

### Choice text distribution over 20 exact-base repeats

These are observed unseeded frequencies, **not** evidence of a changed probability law:

| Arm | Content → occurrences |
|---|---|
| base | `"`:12, A:1, i:1, ad:1, S:1, T:1, O:1, H:1, J:1 |
| user | `"`:8, ad:2, L:2, H:3, i:1, W:1, O:1, S:1, T:1 |
| parallel_tool_calls | `"`:11, H:3, T:1, O:1, S:1, A:1, M:1, B:1 |
| tools | `"`:12, ad:1, M:1, H:1, J:1, B:2, W:1, y:1 |

Unseeded content differed from the corresponding base in 17/20 user, 13/20 parallel-tool and 12/20 tool requests. However, with matched seeds **all four arms had exactly the same distribution** (`"`:13, T:2, M:1, J:1, y:1, F:1, W:1) and zero paired message differences. Twenty observations cannot establish universal distributional equality; they do prevent treating ordinary default-sampler variation as this run's demonstrated parameter effect.

### Logs, usage, timings and metrics the projection omits

- The cold first base had `cached_tokens=0`, `timings.cache_n=0`, `prompt_n=42`, `prompt_ms=1.138`; its first user successor had `cached_tokens=41`, `cache_n=41`, `prompt_n=1`, `prompt_ms=0.226`. Both normalize identically. Thus the projection definitely misses cache/timing changes.
- The repeated unmodified base itself subsequently had the same cache behavior: 19/20 default baselines and 20/20 requests for **each** treatment logged full prompt similarity plus `need to evaluate at least 1 token` / `n_past was set to 41`. There was no request-level ` E ` log and no `tool`, `parallel` or `probe-user` text in any default request log slice. The cache warning is therefore not a treatment-specific effect.
- Default `prompt_ms` medians: base 0.153, user 0.1765, parallel-tool 0.1435, tools 0.153. Default HTTP wall-time medians in milliseconds: base 0.674896, user 0.6563655, parallel-tool 0.645900, tools 0.681845. These are descriptive timings, not a calibrated latency experiment or a claimed performance effect; the cold first base and uncontrolled scheduling preclude that conclusion.
- `/metrics` was actually probed before and after: HTTP **501** both times, exact error `{"error":{"code":501,"message":"This server does not support metrics endpoint. Start it with \u0060--metrics\u0060","type":"not_supported_error"}}`. `/props.endpoint_metrics=false`. No metrics-label or counter equivalence is claimed, and no forbidden extra argv was added to enable the endpoint.

## Strongest counterexample and the smallest safe correction

**Concrete counterexample to literal “no response change”:** default repeat 0 returned choice content `"` for base, `ad` for user, and H for parallel-tool; cache counts and timings also changed. All three normalized identically, with empty slot deltas. This disproves raw-response identity, **not** the frozen bounded ignored predicate: the matched-seed controls and repeated baselines provide no causal hidden effect for these sent values.

The relevant frozen source is `sources/llama.cpp-704366d/server-common.cpp` at `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`:

- **L1426:** `inputs.parallel_tool_calls = json_value(body, "parallel_tool_calls", caps["supports_parallel_tool_calls"]);` (spacing abbreviated here). The key is explicitly consumed before template rendering. On this fixture `false` equals the advertised default. Treating absence from the native schema as proof it is unread would be false provenance.
- **L1336–1347, L1421, L1453–1456, L1489–1494:** tools are parsed, passed to template inputs and involved in grammar validation before the prompt is rendered. In particular, the source has `Cannot use custom grammar constraints with tools.` **That interaction was not live-tested by this review**, and is outside the exact row body; it is a pinned-source boundary against global “tools are ignored” advice, not a fabricated live failure of K31-15.
- **L1524–1531:** the copy-remaining-properties loop copies keys; L1530 by itself proves neither that a key was unread earlier nor that all its effects are absent.
- `server-task.cpp` **L357–363, L406–449** explicitly serializes cached usage, message content and timing values outside the counter's narrow equality projection. The projection is not a full response comparison.

**Smallest safe correction (prose/source attribution only):** preserve the frozen renderer, predicate, target, counter bytes and HOLD. State that “ignored” means only zero stored-parameter delta plus equality of the six frozen normalized fields **for this sent value, base, build, model and argv**. For K31-14 explicitly say it supplies the fixture's already-false default without tools; for K31-15 explicitly say the active template advertises no tool support. Cite the consumed-input/template branches, not the copy loop alone, for these qualifications. Do not claim output identity, tool support, global parameter ignorance or equal latency.

The local defect is fixable overbroad wording/source attribution; no frozen-row failure was observed. A decision to preserve universal ignored-parameter advice merely because the counter counts a row would trade calibration/operability for a depth count, and belongs to the canonical judge rather than this critic. This item makes no claim of round saturation or promotion.

## Limits and cleanup

No complete C1/C2 counter, round-30 HOLD, canonical judge, admission, integration or other serving runtime was run. These are independent probe observations, not a frozen-counter receipt. No `/apply-template` response or byte-for-byte rendered prompt was obtained: unchanged prompt count alone is insufficient proof of identical prompt bytes, although the template properties and full-LCP logs corroborate the bounded result. Other models/templates, other parameter values, tool interactions, streaming and longer generations are not covered.

The only started server was terminated and reaped with exit **0**; the probe verified port **47956 free afterward** (`raw.json.port_free_after=true`). No background job, installation, update or host-service change was used. Nothing here changes or weakens HOLD. L1 must not trust these point observations as universal no-op, distributional-equivalence, metrics or latency claims.
