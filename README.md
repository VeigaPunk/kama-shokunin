# kama-shokunin

Local model serving and endpoint health. The lane answers one question:

**Is the thing at this baseURL the model this config believes it is, right now?**

It reports pin correctness and serving liveness as separate facts. A
config that still names the right URL while nothing is listening is a
correct pin and a dead endpoint, not a healthy model.

## The job

`PROVINCE.md` owns producer discovery on local serving ports, the
baseURL pins in the surviving consumer registry, served-model-id
reconciliation (`GET /v1/models` against the configured id), and the
liveness conventions (`/health`, `/props`, `/slots`). The registry is
`registry/endpoint-consumers.tsv`. History of what those rows did is
`registry/history/`.

Verdicts, shared with `tools/kama-probe.sh`: `MODEL_OK`,
`MODEL_MISMATCH`, `FOREIGN_SERVICE`, `UNAUTHORIZED_SERVICE`, `DEAD`,
`NOT_HTTP`. Exit 0 means every declared consumer reconciles. Exit 2
means at least one drift. Exit 1 is a probe error.

The lane refuses model quality (kengaku), credential material and auth
flows (kagi), dispatch and route mechanism (kumitate), and remote web
surfaces (kake). It never writes `~/.config`, `~/.omp`, or systemd
units. Those are operator-owned; kama detects a stale pin and reports it.
The reason is recorded in `corpus/lessons/round-1-safety.md`: a lane that
silently repoints a credential-bearing consumer config is outside its
authority.

## What a check means on the recorded host

`PROVINCE.md` records the lane baseline: `bash tools/kama-probe.sh check`
evaluates the three registry rows, `model_ok=0`, `drift=3`, exit 2, with
`8080` and `34113` connection-refused. The previously pinned
`qwen-coder.service` unit is gone. That outage does not shrink the
province. Restoring a unit is operator work. A later checkout should
re-run the probe and read `registry/history/DELTA.md` rather than trust
this paragraph.

```sh
bash tools/kama-probe.sh check
```

`tools/kama-probe.sh listeners` enumerates loopback listeners.
`snapshot` records a point in time under `registry/history/`.

## Read this first

1. [`PROVINCE.md`](PROVINCE.md) — surfaces, the write boundary, the last measured sample.
2. [`SKILL.md`](SKILL.md) — the question, the verdict vocabulary, the exit codes.
3. [`corpus/knowledge/cross-lane-scope.md`](corpus/knowledge/cross-lane-scope.md) — what gets reported out.

## On disk

| Path | Role |
|---|---|
| `SKILL.md` | The one question and the verdict table. |
| `PROVINCE.md` | Surfaces and the hard write boundary. |
| `tools/kama-probe.sh` | Listeners, snapshot, check. |
| `registry/` | Consumer rows and probe history. |
| `corpus/` | Knowledge and lessons, including the safety lesson. |
| `MINT.md`, `SHONEN.md` | Mint record and promotion checklist. Rank is shonen. |
| `LOG.md`, `SCORECARD.md` | Audit trail and axis verdicts. |

## Fleet

Protocol and roster: [shokunin](https://github.com/VeigaPunk/shokunin).
Roster id `kama`, rank **shonen**.
