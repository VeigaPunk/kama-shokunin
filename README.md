# kama-shokunin — 釜

**Local model serving and endpoint health.**

This lane answers exactly one question:

> Is the thing at this baseURL the model this config believes it is,
> **right now**?

Never *is the model good* (→ [kengaku](https://github.com/VeigaPunk/kengaku-shokunin)).
Never *is the request safe* (→ [kagi](https://github.com/VeigaPunk/kagi-shokunin)).
Never *how was this request routed* (→ [kumitate](https://github.com/VeigaPunk/kumitate-shokunin)).

A **shokunin lane**: an expert agent for one domain, minted and trained
under the [shokunin skill](https://github.com/VeigaPunk/shokunin).
Rank: **shonen**. Promotion is a named non-author review of
[`SHONEN.md`](SHONEN.md), never self-attestation.

## Domain

From [`PROVINCE.md`](PROVINCE.md): loopback serving ports, consumer
`baseURL` pins, served-model-id reconciliation (`GET /v1/models` vs
`--alias` vs configured id), liveness/readiness (`/health`, `/props`,
`/slots`), and the endpoint-consumers registry.

kama **never writes** to `~/.config`, `~/.omp`, or systemd units. Those
are operator-owned. kama detects stale pins; the operator repoints them.

The producer formerly pinned here (`qwen-coder.service` on
`127.0.0.1:34113`) is deleted. Sampled state as of 2026-10-15: three
registry rows, all `DEAD` / connection-refused, exit 2. That is a
sample, not continuous monitoring. Restoring a unit is operator work.
The domain — discovery and drift reconciliation — is not retired.

## Verdicts

`MODEL_OK` · `MODEL_MISMATCH` · `FOREIGN_SERVICE` ·
`UNAUTHORIZED_SERVICE` · `DEAD` · `NOT_HTTP`

Exit: `0` every declared consumer reconciles · `2` ≥1 drift · `1` probe
error (never a verdict).

## What's here

| Path | Role |
|---|---|
| [`SKILL.md`](SKILL.md) | the one-question contract, current sampled state, probe conventions |
| [`PROVINCE.md`](PROVINCE.md) | surfaces, write boundary, refusals |
| [`tools/kama-probe.sh`](tools/kama-probe.sh) | listeners / consumers / check / snapshot |
| [`registry/endpoint-consumers.tsv`](registry/endpoint-consumers.tsv) | declared consumers |
| [`registry/history/`](registry/history/) | snapshot JSON, `latest.tsv`, append-only `DELTA.md` |
| [`corpus/`](corpus/) | knowledge and lessons |
| [`SCORECARD.md`](SCORECARD.md) · [`LOG.md`](LOG.md) · [`SHONEN.md`](SHONEN.md) | axes, trail, promotion |

## The probe

```sh
bash tools/kama-probe.sh --help
bash tools/kama-probe.sh listeners
bash tools/kama-probe.sh consumers
bash tools/kama-probe.sh check
bash tools/kama-probe.sh check --json
bash tools/kama-probe.sh snapshot          # persists history; the only write path
```

`listeners` / `consumers` / `check` write only to a removed mktemp dir.
`snapshot` additionally writes inside its history dir.

## How a lane learns

Append-only corpus; every claim separates observation / inference /
unknown; rounds are non-author-verified. See the fleet
[README](https://github.com/VeigaPunk/shokunin#readme).
