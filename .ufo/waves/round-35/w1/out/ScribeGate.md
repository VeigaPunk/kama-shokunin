# ScribeGate

Seat: ScribeGate. Lane: kama. Round 35, wave w1, attempt 1. Role: scribe. Judged on: coverage. Leaf: no subagents. No git mutation. No lesson edit. No corpus write. No shokuknow write.

## Behavior

Re-opened the staged probe and hosted entries, fetched the cited public pages, and drafted a Gate with one admit and two rejects. The admit fires only because this seat located quotes. Sibling quote-location seats had not filed reports; their contracts were not treated as evidence. `hosted-health-route-configuration.md` is rejected as remote platform health (kake) with a flip condition that is not met. The staged probe file is rejected as a byte-copy. The lane lesson was not edited. Neither frozen predicate was changed.

A first draft of these two files was already on disk and was false against later observation (it said the knowledge file and S327 were absent, that the Google pages were not fetched, and that C2 could not flip). This report replaces that draft. This seat did not commit the corpus changes that made the no-tip and later-tip counters pass.

## Gates

- Admit, condition met by ScribeGate only: a lane-written `corpus/knowledge/endpoint-health-probe-conventions.md`, because the vLLM admission-503 sentence was located (20 whitespace-delimited words). Docker HEALTHCHECK, Compose `service_healthy`, blackbox `probe_success`, and the llm-d liveness sentence were also located and are listed as further quotes, not as a byte-copy and not as sentences this seat wrote into the corpus.
- Reject: `hosted-health-route-configuration.md` as remote platform health (kake). Flip unmet: no located quote says a local probe on this host must request the platform path, and the province texts still assign remote endpoint health away from kama. Staged S346/S349/S350 stay unappended.
- Reject: staged `endpoint-health-probe-conventions.md` as a byte-copy. Two staged section labels were not on the opened pages.

## Touched surfaces

Written by this seat:

- `.ufo/waves/round-35/w1/out/ScribeGate/gate.md` (replaced)
- `.ufo/waves/round-35/w1/out/ScribeGate.md` (this report, replaced)
- `.ufo/waves/round-35/w1/out/ScribeGate/fetch/vllm-engine-args.html`
- `.ufo/waves/round-35/w1/out/ScribeGate/fetch/dockerfile.html`
- `.ufo/waves/round-35/w1/out/ScribeGate/fetch/compose-services.html`
- `.ufo/waves/round-35/w1/out/ScribeGate/fetch/blackbox-readme.md`
- `.ufo/waves/round-35/w1/out/ScribeGate/fetch/sglang-llmd.html`
- `.ufo/waves/round-35/w1/out/ScribeGate/fetch/hosted-s346.html`
- `.ufo/waves/round-35/w1/out/ScribeGate/fetch/hosted-s349.html`
- `.ufo/waves/round-35/w1/out/ScribeGate/fetch/hosted-s350.html`

Present in the seat directory, not created by the commands below, byte-identical (`cmp` exit 0) to the bodies this seat fetched: `fetch/docker-dockerfile.html`, `fetch/docker-compose-services.html`. Not used as extra evidence.

Not written by this seat: `corpus/lessons/round-35.md`, `corpus/knowledge/endpoint-health-probe-conventions.md`, `corpus/SOURCES.md`, `corpus/README.md`, `MISSION.md`, `considerthese/`, shokuknow, sibling lanes, git index. `corpus/knowledge/hosted-health-route-configuration.md` is absent.

## Out of scope

- Editing the lane lesson, including the 18-versus-20 word conflict.
- Appending registry rows.
- Hand-checking quarantine rows. The lesson's quarantine table was not re-derived here and is not this seat's evidence.
- Mining `considerthese/`.
- Service restoration, secrets, endpoint-admin state. Deploy snippets on the Google pages contain the name `HF_TOKEN`; no secret value was copied.
- Treating other seat reports as quote evidence. Quote-location reports were absent at the check below.

## Findings

1. Admit condition is met by this seat. The deciding quote is on the vLLM v0.32.0 engine-args page under SchedulerConfig `--max-num-queued-reqs`: "When the limit is reached, new requests are rejected with HTTP 503 so the client can retry on another instance." Whitespace split: 20 words. A second 12-word 503 sentence is under `--max-num-queued-tokens`.
2. Staged section labels that were not on the opened pages: blackbox quote is under `### Checking the results`, not `§Probing`; llm-d quote is under `Health Checks`, not `§Health endpoints`. The sentence text for those two quotes did match the staged wording.
3. Docker HEALTHCHECK and Compose `service_healthy` are local container probe conventions, not remote platform health. Blackbox `probe_success` is an external probe metric. The opened blackbox sentence does not say the module name decides success.
4. llm-d liveness quote was located and is not new ground. Matrix line 16 already documents SGLang `/health` and excludes `/health_generate` from kama probes because it generates. Matrix line 22 assigns routing/gateway health dispatch to kumitate.
5. Hosted pages were fetched (HTTP 200). Located fields are platform deployment settings (`serving_container_health_route="/ping"` and `="/health"`, `containerSpec.healthRoute`, `AIP_HEALTH_ROUTE`). That confirms the reject subject. It does not meet the flip.
6. C2 at base `719655f12517a9ce6b1a5ca44316897fed8420b0`: `named 0 file_exists 0 cited_row 0 met False`, exit 1. C2 at later HEAD `82886c28f7da564a706bb4385b45b72d49b49bcb`: `named 1 file_exists 1 cited_row 1 met True`, exit 0. An intermediate tip `d419b99df20d1f0b34caf65807e913784e69baf5` also printed `met True`. This seat did not make those commits. Predicate unchanged. Hosted file absent at both later tips (`git cat-file -e` exit 128).
7. Working tree moved during this seat. First `rev-parse` was `719655f12517a9ce6b1a5ca44316897fed8420b0`. Last `rev-parse` was `82886c28f7da564a706bb4385b45b72d49b49bcb`, subject `round-35: scorecard, log, inherited-path disposition`, author `kama-shokunin`. Read-only git only.

## Commands and outcomes

Fetches, each a separate curl, cwd the seat `fetch/` directory, access 2026-10-24 21:24 -0300 unless noted:

```
curl -fsSL --max-time 40 -A 'kama-scribe-gate/round-35' -o vllm-engine-args.html -w 'vllm %{http_code} %{size_download}\n' 'https://docs.vllm.ai/en/v0.32.0/configuration/engine_args/'
curl -fsSL --max-time 40 -A 'kama-scribe-gate/round-35' -o dockerfile.html -w 'dockerfile %{http_code} %{size_download}\n' 'https://docs.docker.com/reference/dockerfile/'
curl -fsSL --max-time 40 -A 'kama-scribe-gate/round-35' -o compose-services.html -w 'compose %{http_code} %{size_download}\n' 'https://docs.docker.com/reference/compose-file/services/'
curl -fsSL --max-time 40 -A 'kama-scribe-gate/round-35' -o blackbox-readme.md -w 'blackbox %{http_code} %{size_download}\n' 'https://raw.githubusercontent.com/prometheus/blackbox_exporter/8eff0fc90e725fc7325186a530d3252507b032ca/README.md'
curl -fsSL --max-time 40 -A 'kama-scribe-gate/round-35' -o sglang-llmd.html -w 'sglang %{http_code} %{size_download}\n' 'https://llm-d.ai/docs/dev/architecture/model-servers/sglang'
```

Stdout: `vllm 200 365096`, `dockerfile 200 1066624`, `compose 200 885676`, `blackbox 200 18022`, `sglang 200 46440`. Each exit 0.

```
curl -fsSL --max-time 40 -A 'kama-scribe-gate/round-35' -o hosted-s346.html -w 's346 %{http_code} %{size_download}\n' 'https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/open-models/vllm/use-vllm?hl=ja'
curl -fsSL --max-time 40 -A 'kama-scribe-gate/round-35' -o hosted-s349.html -w 's349 %{http_code} %{size_download}\n' 'https://docs.cloud.google.com/vertex-ai/generative-ai/docs/open-models/deploy-custom-vllm?hl=ja'
curl -fsSL --max-time 40 -A 'kama-scribe-gate/round-35' -o hosted-s350.html -w 's350 %{http_code} %{size_download}\n' 'https://docs.cloud.google.com/vertex-ai/docs/predictions/custom-container-requirements?hl=zh-tw'
```

Stdout: `s346 200 586573`, `s349 200 481070`, `s350 200 436517`. Each exit 0.

Saved-body counts: `rejected with HTTP 503` 2; `Readiness` 1; `service_healthy` 5; `unhealthy` 3; `probe_success` 1. `Probing` absent from the blackbox README. `Health endpoints` count 0 on the llm-d page.

Quote-seat absence at 2026-10-24T21:28:36-0300:

```
ls: cannot access '.../ScoutVllm503.md': No such file or directory
ls: cannot access '.../ScoutDockerHc.md': No such file or directory
ls: cannot access '.../ScoutProbeEntry.md': No such file or directory
ls: cannot access '.../ScoutHostedReject.md': No such file or directory
ls: cannot access '.../ConnSibling.md': No such file or directory
ls: cannot access '.../CriticProvince.md': No such file or directory
```

C2:

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round35-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 719655f12517a9ce6b1a5ca44316897fed8420b0
named 0 file_exists 0 cited_row 0 met False
base_exit:1

python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round35-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 82886c28f7da564a706bb4385b45b72d49b49bcb
named 1 file_exists 1 cited_row 1 met True
head_exit:0
```

`git cat-file -e 719655f12517a9ce6b1a5ca44316897fed8420b0:corpus/knowledge/endpoint-health-probe-conventions.md` exited 128. The same path exists at the later HEAD. This seat did not create it.

Corpus search before the S327 row appeared: `rejected with HTTP 503`, `service_healthy`, and `probe_success` had no hits under `corpus/`. After the tip moved, `rejected with HTTP 503` is in `corpus/SOURCES.md:213` and the new knowledge file. That later hit is not this seat's write.

## Provenance

- Staged files read, not modified: `/home/vgpnk/Projects/shokuknow/merge/kama/knowledge/corpus/knowledge/endpoint-health-probe-conventions.md`, `hosted-health-route-configuration.md`, and the S327/S331/S332/S333/S334/S346/S349/S350 lines of `SOURCES.append.md`.
- Province text re-opened: kama `PROVINCE.md`; kake `PROVINCE.md` adjacent line and round-31 Render health-check note (S057–S060, a different surface); kumitate `PROVINCE.md`; `corpus/README.md:64`.
- Held overlap re-opened: `runtime-health-surface-matrix.md:14-22`; `served-model-id-resolution.md:37-46`.
- Lesson Gate read at `corpus/lessons/round-35.md:24-32` and not edited.
- `MISSION.md:29` and `shokunin.conf:52` read. Neither edited.

## Conflicts (verbatim, for the L1)

`corpus/lessons/round-35.md:28`: Admit S327. Quote: "When the limit is reached, new requests are rejected with HTTP 503 so the client can retry on another instance." 18 words.

This seat, same sentence, `str.split()` whitespace count: 20. The lesson was not edited.

`corpus/lessons/round-35.md:32`: Reject the staged five-source `endpoint-health-probe-conventions.md` as a byte-copy. Reason: it cites S331, S332, S333 and S334, which this round did not re-open into the admitted entry. Adopting the file would cite unopened rows. Flip: re-open those four and admit only sentences whose quotes locate.

This seat did re-open those four URLs and located quotes. The committed entry still excludes them. The "did not re-open" clause is false for this seat. The byte-copy reject stands for a different reason (section labels not on the pages). The lesson was not edited.

`corpus/lessons/round-35.md:30`: Flip: a local container on this host whose configured health route differs from the engine route, observed by the lane probe, not a cloud vendor guide.

This seat's Google quotes are cloud vendor guides. They do not meet that flip. This draft's flip also requires a local-probe quote and a province text that no longer assigns the surface away from kama. Neither is met.

`corpus/README.md:64`: "No coverage of *remote* endpoint health (that is kake/kumitate territory)."

kama `PROVINCE.md` refuses "remote web surfaces (kake)" and "dispatch/route mechanism (kumitate)".

kumitate `PROVINCE.md`: "Local model serving and endpoints → kama."

kake `PROVINCE.md`: "kama owns local model-serving endpoints; kake owns remote web properties."

Assigned reject label, followed and not rewritten: remote platform health (kake).

`MISSION.md:29`: `kama:       { cwd: kama-shokunin/,   axes: "operability + freshness (local model serving/endpoints)" }`

`shokunin.conf:52`: `kama|kama-shokunin|operability + calibration (local model serving and endpoint health)`

This seat is judged on coverage. `MISSION.md` was not edited. Neither predicate was changed.

## Known limits

- Sibling scout reports may have appeared after 2026-10-24T21:28:36-0300. They were not inputs.
- The lesson's quarantine verdicts were not re-run.
- Word counts are whitespace-delimited, not a linguistic tokenizer. The 18-versus-20 conflict is unresolved.
- Blackbox content is whatever the pinned raw URL returned. This seat did not clone the repository to re-verify the commit.
- Docker and Google docs pages are unversioned. Access date is the local fetch date 2026-10-24.
- HEAD moved during the seat. The C2 pass is an observation of commits this seat did not make.
- No install. Pacman was not run. `RULES.md` was not read because no tool was installed.

## Artifact paths

- `.ufo/waves/round-35/w1/out/ScribeGate/gate.md`
- `.ufo/waves/round-35/w1/out/ScribeGate.md`
- `.ufo/waves/round-35/w1/out/ScribeGate/fetch/vllm-engine-args.html`
- `.ufo/waves/round-35/w1/out/ScribeGate/fetch/dockerfile.html`
- `.ufo/waves/round-35/w1/out/ScribeGate/fetch/compose-services.html`
- `.ufo/waves/round-35/w1/out/ScribeGate/fetch/blackbox-readme.md`
- `.ufo/waves/round-35/w1/out/ScribeGate/fetch/sglang-llmd.html`
- `.ufo/waves/round-35/w1/out/ScribeGate/fetch/hosted-s346.html`
- `.ufo/waves/round-35/w1/out/ScribeGate/fetch/hosted-s349.html`
- `.ufo/waves/round-35/w1/out/ScribeGate/fetch/hosted-s350.html`
