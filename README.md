# kama-shokunin

Local model serving and endpoint health.

Rank: **shonen**. [`SHONEN.md`](SHONEN.md) marks its four boxes `[~]` —
author assertions, waiting on a named non-author verifier.

Fleet: [shokunin](https://github.com/VeigaPunk/shokunin).

## The question

> Is the thing at this baseURL the model this config believes it is, right
> now?

That is the whole province. The lane reports pin correctness and serving
liveness as separate facts. A config that names the right URL while
nothing is listening is a correct pin and a dead endpoint.

Verdict vocabulary, shared with `tools/kama-probe.sh`:

`MODEL_OK` · `MODEL_MISMATCH` · `FOREIGN_SERVICE` · `UNAUTHORIZED_SERVICE` · `DEAD` · `NOT_HTTP`

Exit `0` when every declared consumer reconciles, `2` when at least one
drifts, `1` on a probe error.

## Boundary

**Owns:** producer discovery on local serving ports, baseURL pins in the
consumer registry, served-model-id reconciliation (`GET /v1/models` vs
alias vs configured id), liveness surfaces (`/health`, `/props`,
`/slots`), and the drift timeline under `registry/history/`.

**Hands off:** model quality (kengaku), credential material and auth flows
(kagi), dispatch mechanism (kumitate), remote web surfaces (kake).

**Write boundary:** kama never writes `~/.config`, `~/.omp`, or systemd
units. Those are operator-owned. The lane detects and reports a stale pin.

`PROVINCE.md` records the sampled state at the round-5 read: three
registry rows, all `DEAD` / connection-refused, exit 2. That sample does
not retire the domain. Restoring a server is operator work.

## Run

```sh
bash tools/kama-probe.sh check
bash tools/kama-probe.sh listeners
```

`check` evaluates `registry/endpoint-consumers.tsv`. `listeners` enumerates
loopback listeners. `snapshot` records a point in the drift timeline.
`tools/test-snapshot.sh` is the snapshot test beside the probe.

## Map

| Path | What it is |
|---|---|
| [`SKILL.md`](SKILL.md) | decision table, error signatures, checklist |
| [`PROVINCE.md`](PROVINCE.md) | surfaces, sampled state, write boundary |
| [`registry/endpoint-consumers.tsv`](registry/endpoint-consumers.tsv) | the consumer rows |
| [`registry/history/`](registry/history/) | `latest.tsv` and `DELTA.md` |
| [`corpus/knowledge/`](corpus/knowledge/) | including the cross-lane scope note |
| [`LOG.md`](LOG.md), [`SCORECARD.md`](SCORECARD.md) | audit trail and axis verdicts |

A 401 is evidence about identity. The key that would open it belongs to
kagi.
