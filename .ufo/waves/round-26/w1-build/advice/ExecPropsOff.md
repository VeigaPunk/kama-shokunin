# ExecPropsOff — advice (round-26 C1 w1-build)

Verdict: confirmed 1 distinct fault (POST /props without `--props` returns 501 with literal message); candidate signature counts 1/1 under the frozen counter in a scratch extract; ready for L1 integration.

## Fault and trigger

Fault family: global properties change requested without `--props` (POST /props).
Trigger used: `POST /props` with JSON body `{"chat_template":"x"}`, Content-Type `application/json`, on a healthy fixture server launched without `--props`.
Observed response (both reproductions, ports 47612; HTTP status 501):

```
{"error":{"code":501,"message":"This server does not support changing global properties. Start it with `--props`","type":"not_supported_error"}}
```

## Reproduction evidence (two independent launches)

Run 1 (port 47612):
- `timeout 40 ~/.local/bin/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 47612 -t 2 > run1.log 2>&1 &`; health 200 at first poll; POST /props -> 501 (raw/run1.resp); server killed; port closed.
Run 2 (port 47612, same commands): health 200 at first poll; POST /props -> 501 (raw/run2.resp); server killed; port closed.
Healthy baseline (port 47613): launch same; GET /props -> 200 (raw/baseline_props.resp); `--help` exit 0 (raw/help.txt); `--version` exit 0 (raw/version.txt).

## Signature

`changing global properties. Start it with `--props`` (49 bytes; >= 20 required).
- Verbatim in pinned source: tools/server/server-context.cpp line 5453, literal argument of `format_error_response(...)` inside the `post_props` handler: `"This server does not support changing global properties. Start it with `--props`"` (quote, 16 words, line 5453).
- Source pin: committed snapshot `.ufo/waves/round-26/sources/llama.cpp-704366d/server-context.cpp` sha256 `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329` == fresh fetch of `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp` (same sha256); access date 2026-10-23. Pinned source sha in count-c1.py SOURCE_SHA256 matches.
- Absent at base 1560e4d8: `git grep -F -q -e 'changing global properties. Start it with `--props`' 1560e4d8 -- SKILL.md corpus` -> exit 1. Full-message variant also exit 1; section heading `## Round-26 live error signatures` also exit 1.
- Absent from healthy baseline: grep count 0 in baseline_props.resp, help.txt, version.txt, baseline_launch.log, and squashed-help comparison.
- Not echoed from request: request path `/props`, headers, body `{"chat_template":"x"}` contain none of the signature.
- Channel: http (response body of a status >= 400 response; observed 501).

Reason for choosing the post-prefix substring rather than the full message: the full message starts with the shared family prefix `This server does not support `. Under predicate clause (g), a row whose signature is a substring or superstring of an earlier counted signature fails, and an earlier counted signature appearing in this channel text fails it. The chosen signature avoids the bare family prefix (so it is not defeated by a sibling row counting just `This server does not support ` processed earlier) while remaining >= 20 bytes and source-verbatim. [INFERENCE] Residual clause-(g) risk: any earlier counted row whose signature is a superstring of this one, or any earlier counted signature that appears verbatim in this channel text (e.g., a sibling choosing the full message or another substring of it), would fail this row if processed earlier; this is inherent to the family and matches the L1 control-wave observation that the family prefix blocks family members under clause (g).

## Scratch counter run

Scratch extract of frozen tip a23c0e042114016a909eb15173aa6df74b5b7eb0 at `/fast/scratch/hyaku/kama-r26/ExecPropsOff/scratch` (git archive; GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE unset). Added in scratch only: `registry/error-signatures-r26.json` (one entry, id TBD, source.row S900), SKILL.md section `## Round-26 live error signatures` with row `| TBD | http | changing global properties. Start it with `--props` | S900 |`, corpus/SOURCES.md row `| S900 | ... server-context.cpp ... 704366d ... |`.

Command (from extract root, under host-wide lock):
```
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 900 python3 .ufo/waves/round-26/count-c1.py --out receipt.json
```
Output:
```
registered 1 counted 1 target 12 met False not-counted []
```
Exit code 0. Receipt (raw/counter-receipt.json): all checks true (id_unique, a_skill_row, b_long, b_new_at_base, c_source_row, d_source_pinned, d_in_source, e_error_shown, e_signature_seen, e_not_echoed, f_absent_from_baseline, g_distinct); observed status 501; counted true. Baseline sha256 `ecf8bf3c23e68783a4f9b4504c2c45bc04966f2dc464cfa5c62ee4069fea916c`; no could-not-evaluate.

## Files written

- .ufo/waves/round-26/w1-build/out/ExecPropsOff/candidates.json (registry entry; id TBD, source.row TBD, source.file server-context.cpp)
- .ufo/waves/round-26/w1-build/out/ExecPropsOff/RUNS.txt (every command, output, exit code)
- .ufo/waves/round-26/w1-build/out/ExecPropsOff/raw/run1.resp, run2.resp, run1.log, run2.log, baseline_props.resp, baseline_launch.log, help.txt, version.txt, counter-receipt.json
- .ufo/waves/round-26/w1-build/advice/ExecPropsOff.md (this report)
- Scratch only (not lane): /fast/scratch/hyaku/kama-r26/ExecPropsOff/scratch/... (archive extract + scratch edits) and /fast/scratch/hyaku/kama-r26/ExecPropsOff/*.log/*.resp/*.txt

## Risks / blockers

- Row id and source row are TBD pending L1 allocation (counter run used id TBD and placeholder source row S900 in scratch; row S900 does not exist at base and is not written to the lane).
- Clause-(g) ordering risk described above (family prefix). If the L1 integrates sibling rows using the bare prefix or overlapping substrings of this message, this row may not count depending on registry order; this seat cannot control other seats' signatures.
- No other blockers; no tools installed (none needed).
