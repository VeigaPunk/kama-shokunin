# Round 60 C1 do-nothing counterexample (A12C1DoNothingCritic)

**Axes:** operability (primary; the counter can report operational success without lifecycle operability); calibration (secondary; receipt artifacts are not independent provenance). No lane source was edited.

## Counterexample and evidence

I exercised four disposable fixture-repo tool implementations against the frozen `round60-c1-counter.py`. Each was created under `/fast/scratch/hyaku/kama-r60/A12C1DoNothingCritic/`, with its tool files committed in a fixture repository after asserting its `git rev-parse --show-toplevel` equaled that fixture. Each implementation passes the real pinned binary/model digest gates, then returns an asserted `MODEL_OK` receipt and writes enough files to satisfy the independent verifier, without starting Ollama in the measured run:

* **V1 synthetic:** makes internally consistent HTTP capture bodies, capture hashes, a nonce-named manifest containing the frozen model digest, copies the fixture GGUF as the expected blob, writes a fabricated listening/generate log, and reports teardown success.
* **V2 earlier capture:** rewrites nonce and port into the committed earlier receipt captures / serve-lines and recreates manifest/blob artifacts.
* **V3 copied real run:** uses a genuine run's capture bodies and log, substitutes nonce/port, and copies generated model-store artifacts (home key, metadata, blobs, manifest).
* **V3B retimestamped copy:** same as V3, with log timestamps rewritten to the current interval.

Exact counter outcomes are saved in `hardened-results.jsonl`. For each fixture, the frozen verifier returned `[]` (accepted), the C1 counter returned exit 0, and reported `tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=3/3 log_rejected=1/1 errors=0 met=True`. The additional in-run `/proc` sampler saw no Ollama process owning the fixture work dir/receipt port for any forged variant; each took ~0.06 s. In contrast, the honest lane-tip baseline took ~1.6 s and the sampler observed the pinned Ollama process owning the selected listener. Results are in `hardened-results.jsonl`.

The original attempt before fixing my fixture-hook placement accidentally ran the real lifecycle; it is retained as `honest-receipt.json` and `honest-serve.log`, not treated as a forged pass. After correcting the placement, the outputs above are from the actual forgeries. `do-nothing-watch-results.jsonl` records the corrected run's first three variants, counter exit 0, `met=True`, no Ollama executable with cwd/command tied to the measured work tree, and no new listening ports.

## Which checks fail to reject the controls

All seven counter control families are rejected as implemented; that does not test lifecycle provenance. The main counterexample passes its `live_ok` predicate while its synthetic/replayed artifacts do not correspond to a process that served them. Specifically, the counter checks the receipt's `port` is now unregistered/not listening, but does not establish that the pinned process ever owned that port during the invocation. The receipt's `listener-owned`, `running-exe-digest`, checks are merely booleans and can be asserted. Log matching only needs a listening line with the receipt port/version plus any POST `/api/generate`; it does not bind those lines to the nonce or run interval. Manifest/blob hashing proves bytes and claimed content, not that Ollama imported them during this run. The seven controls perturb a valid receipt/artifact set; they don't attempt a tool that fabricates the entire set.

## Smallest safe correction / falsifiers

1. **Required independent closure:** have the counter observe the measured tool invocation, not trust its receipt. While the child runs, poll `/proc` (or use an equivalent OS process/socket observation) and require a process whose executable SHA-256 equals the frozen binary SHA, whose listening socket is the receipt port, and whose cwd/environment ties its model store to this invocation's unique run directory. Require the observation during the invocation and fail closed if it is unavailable. Counter-side enforcement matters: modifying only the candidate lane tool would not be independent.
2. **Useful additional binding, not sufficient alone:** require a nonce-specific request (e.g. `GET /v1/models/kama-<nonce>`) in the run log, and tie its timestamp to the counter's invocation interval. V1's log fails this; V2/V3 can rewrite nonce text and timestamps, so log grep/time alone is not closure. `H1` through `H3` in the accompanying scratch-only experiment demonstrate this progression: V1 fails all three, V2/V3 pass nonce-log binding but lack server artifacts/time, V3B can also pass the timestamp check.
3. Keep the existing digest, blob/manifest, capture, and tamper checks as useful integrity checks, but do not describe them as proof of live service without the independent process/socket observation. The simplest strong falsifier is to pass the forged fixtures above and an honest run through the enhanced counter: reject all four for lack of an observed pinned listener on their declared port; accept the honest run only when that process/socket observation occurs.

## Commands / status

* `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-live.py --work /fast/scratch/hyaku/kama-r60/A12C1DoNothingCritic/src-run --nonce srcrunaa11 --out /fast/scratch/hyaku/kama-r60/A12C1DoNothingCritic/src-receipt.json` — exit 0, genuine `MODEL_OK` run; copied evidence is included above.
* `S=/fast/scratch/hyaku/kama-r60/A12C1DoNothingCritic; S=$S python3 $S/hardened.py V1 V2 V3 V3B` — each internal frozen-counter invocation exit 0; the harness output reports all four forgeries accepted by frozen verify and rejected by H4, and honest baseline accepted by H4. Captured output: `hardened-results.jsonl`.
* `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round60-c1-counter.py --repo $S/repo-V1 --tip HEAD --work $S/cw-V1` (likewise V2/V3 in initial corrected run) — exit 0, `met=True` for each while the corrected run observed no related Ollama executable and no new listener. See `do-nothing-watch-results.jsonl`.

Tool installation/update: none.
