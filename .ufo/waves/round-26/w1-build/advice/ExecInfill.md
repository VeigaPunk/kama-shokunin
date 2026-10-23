Verdict: Confirmed one distinct live missing-FIM `/infill` fault: two fixture server launches returned the same 501 for requests both with and without `input_prefix`/`input_suffix`; the scratch frozen counter counted the candidate 1/1.

## Exact observations

- Server binary SHA-256: `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804` (exit 0); fixture SHA-256 was validated by the frozen counter as `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`.
- Before launching, ports 47628–47631 were free: `ss -ltn | grep -E '4762[89]|4763[01]'` had no matches (exit 1, expected for free ports).
- Two launches used `--host 127.0.0.1`, `-t 2`, and ports 47628 and 47629. Each launch sent both request shapes to `POST /infill`. All four responses were HTTP 501; each raw body is exactly `{"error":{"code":501,"message":"Infill is not supported by this model: prefix token is missing. suffix token is missing. middle token is missing. ","type":"not_supported_error"}}`. The captured headers say `HTTP/1.1 501 Not Implemented`. See the four `infill-*.body` and four `infill-*.headers` files listed below.
- A healthy `POST /completion` returned HTTP 200 on both launches; raw bodies are retained. Each server log records model load/listening and cleanup. My launch ports were closed after each launch and after the counter; final `pgrep -af llama-server` (exit 0) showed a sibling server/timeout on port 47654 only, not my processes. Final `ss -ltn` (exit 0) showed no listener on ports 47628–47631. I did not signal or change sibling processes.
- Candidate signature: `Infill is not supported by this model` (37 bytes). It appears in each 501 body, is not in the request, and is a verbatim substring of the pinned format string. The handler checks absent FIM tokens before checking the `input_prefix`/`input_suffix` fields: pinned `server-context.cpp:5466-5478`, especially line 5476. The source quote is `Infill is not supported by this model: %s` (8 words).
- Fresh source fetch on 2026-10-23: `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5476`. Fetch exit 0; the fetched file and pinned snapshot both have SHA-256 `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`; `cmp -s` exit 0.
- Base check: `git grep -F -q -e 'Infill is not supported by this model' 1560e4d8 -- SKILL.md corpus` returned 1, confirming absence at base. `llama-server --help` and `--version` each yielded zero matches for `Infill is not supported` (grep status 1). The healthy launch logs also had zero matches. The scratch counter independently reported `f_absent_from_baseline: true`.
- Scratch-only frozen-counter check: archived frozen tip `a23c0e042114016a909eb15173aa6df74b5b7eb0` under `/fast/scratch/hyaku/kama-r26/ExecInfill/counter-tree`; added a temporary SKILL row and SOURCES row S901 there, and used S901 in the scratch registry. No production lane files were changed. Exact command, under the required host lock: `flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 900 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w1-build/out/ExecInfill/scratch-counter-receipt.json` (exit 0). Exact output: `registered 1 counted 1 target 12 met False not-counted []`. Receipt checks a–g are all true for this entry; this one candidate does not meet the overall target.

## Files written

Advice report:
- `.ufo/waves/round-26/w1-build/advice/ExecInfill.md`

Evidence output:
- `.ufo/waves/round-26/w1-build/out/ExecInfill/candidates.json` (one entry; registry `id` and `source.row` intentionally remain `TBD` for L1 integration)
- `.ufo/waves/round-26/w1-build/out/ExecInfill/RUNS.txt`
- `.ufo/waves/round-26/w1-build/out/ExecInfill/infill-with-47628.body`
- `.ufo/waves/round-26/w1-build/out/ExecInfill/infill-with-47629.body`
- `.ufo/waves/round-26/w1-build/out/ExecInfill/infill-without-47628.body`
- `.ufo/waves/round-26/w1-build/out/ExecInfill/infill-without-47629.body`
- `.ufo/waves/round-26/w1-build/out/ExecInfill/infill-with-47628.headers`
- `.ufo/waves/round-26/w1-build/out/ExecInfill/infill-with-47629.headers`
- `.ufo/waves/round-26/w1-build/out/ExecInfill/infill-without-47628.headers`
- `.ufo/waves/round-26/w1-build/out/ExecInfill/infill-without-47629.headers`
- `.ufo/waves/round-26/w1-build/out/ExecInfill/server-47628.log`
- `.ufo/waves/round-26/w1-build/out/ExecInfill/server-47629.log`
- `.ufo/waves/round-26/w1-build/out/ExecInfill/health-47628.body`
- `.ufo/waves/round-26/w1-build/out/ExecInfill/health-47629.body`
- `.ufo/waves/round-26/w1-build/out/ExecInfill/completion-47628.body`
- `.ufo/waves/round-26/w1-build/out/ExecInfill/completion-47629.body`
- `.ufo/waves/round-26/w1-build/out/ExecInfill/scratch-counter-receipt.json`
- `.ufo/waves/round-26/w1-build/out/ExecInfill/scratch-counter.stdout.txt`

Scratch-only artifacts are under `/fast/scratch/hyaku/kama-r26/ExecInfill/`: the reproduction script, raw launch/request files and fresh source copy; the frozen `git archive` extract and its temporary edits are under `counter-tree/` (including its `SKILL.md`, `corpus/SOURCES.md`, and `registry/error-signatures-r26.json`).

## Risks / blockers

No blocker to this scoped reproduction. The candidate has placeholder registry ID/row and needs L1-assigned identifiers and a permanent SOURCES row before integration. This single counted entry is not evidence that C1's overall target of 12 is met.
