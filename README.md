# kama-shokunin

Is the thing at this base URL the model the config believes it is, right
now?

Kama discovers local serving ports, reads consumer pins, and reconciles
them with `GET /v1/models`. It reports pin correctness and serving liveness
as separate facts. A correct pin on a dead port is not `MODEL_OK`. A
deleted unit file does not retire the domain: discovery and drift
reconciliation stay here. Restoring a server is operator work.

Rank: **shonen**. `SHONEN.md` is still here. Registered in the fleet
`MANIFEST.json` roster since 2026-09-29.

## Province

**Owns.** Producer discovery on loopback. The consumer registry in
`registry/endpoint-consumers.tsv`. Served-model-id reconciliation.
Liveness conventions (`/health`, `/props`, `/slots`). Endpoint-drift
history under `registry/history/`.

**Hands off.** Whether the model is good (kengaku). Whether the request
is safe, and any credential material (kagi). Dispatch and route mechanism
(kumitate). Remote web surfaces (kake).

**Write boundary.** Kama never writes `~/.config`, `~/.omp`, or systemd
units. It detects and reports. The operator repoints.

`PROVINCE.md` records the observed state at the lane baseline: the three
registry rows sampling `DEAD` / connection-refused, and the former
`qwen-coder.service` unit gone. That observation is a snapshot with a
date, not a promise about your machine.

## Start here

1. `PROVINCE.md` — surfaces, the write boundary, the latest observed sample.
2. `SKILL.md` — decision table and error signatures.
3. `registry/endpoint-consumers.tsv` — the rows `check` evaluates.
4. `registry/history/DELTA.md` — transitions, including deletions.
5. `corpus/knowledge/cross-lane-scope.md` — who owns the neighboring question.

## Run the probe

From the repository root:

```sh
bash tools/kama-probe.sh --help
bash tools/kama-probe.sh listeners
bash tools/kama-probe.sh check
bash tools/test-snapshot.sh
```

`listeners`, `consumers`, and `check` are read-only toward live services
and write only into a removed temp directory. `snapshot` also writes inside
its history directory. Exit 0 means every declared consumer reconciled.
Exit 2 means at least one drift. Exit 1 is a probe error, never a verdict.
Verdict words are exact: `MODEL_OK`, `MODEL_MISMATCH`, `FOREIGN_SERVICE`,
`UNAUTHORIZED_SERVICE`, `DEAD`, `NOT_HTTP`.

## How to read a score

The scorecard's opening banner is the current authority: assigned axes,
and a statement that the numeric rows are historical assessments. Round 5
is recorded there as a blocked attempt that advanced no scalar. Re-run
`check` if you need the machine in front of you.

## Fleet

Minted under [shokunin](https://github.com/VeigaPunk/shokunin).
