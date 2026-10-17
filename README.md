# kama-shokunin

**Local model serving and endpoint health.**

Kama answers exactly one question:

> Is the thing at this baseURL the model this config believes it is, *right now*?

It never answers "is the model good" and never answers "is the request
safe". Identity and liveness are separate from quality (kengaku) and
from credentials (kagi).

This is a **shokunin lane** of the [shokunin fleet](https://github.com/VeigaPunk/shokunin).
Rank: **shonen**.

## The craft

- Discover whatever is listening on loopback serving ports
  (`tools/kama-probe.sh listeners`) — kama does not claim an installed
  server.
- Reconcile consumer `baseURL` pins against `GET /v1/models`.
- Probe liveness / readiness (`/health`, `/props`, `/slots`).
- Record drift history (`registry/history/`).

Verdict vocabulary from `tools/kama-probe.sh`:

`MODEL_OK` · `MODEL_MISMATCH` · `FOREIGN_SERVICE` ·
`UNAUTHORIZED_SERVICE` · `DEAD` · `NOT_HTTP`

Exit `0` = every declared consumer reconciles, `2` = ≥1 drift, `1` =
probe error. A 401 is *evidence about identity*; the key that would
open it is kagi's surface.

**Write boundary (hard):** kama never writes `~/.config`, `~/.omp`, or
systemd units. Those are operator-owned. Kama detects and reports stale
pins; the operator repoints them. Silent repoint of a credential-bearing
consumer is out of authority (`corpus/lessons/round-1-safety.md`).

## Current sampled state

Last recorded sample in `PROVINCE.md` / `SKILL.md` (2026-10-15): three
registry rows, all `DEAD` / connection-refused on `8080` and `34113`,
`model_ok=0`, `drift=3`, exit 2. File-match on a pin is **not**
`MODEL_OK`. Restoring a unit is operator-owned. The outage retires
nothing in the domain — discovery and drift reconciliation still live
here.

## Province

Owns: local LLM endpoints, baseURL drift, served-model reconciliation,
probe conventions, the endpoint-consumers registry.

**Refuses:** model quality / eval (kengaku), credential material and
auth flows (kagi), dispatch / route mechanism (kumitate), remote web
surfaces (kake).

See [`PROVINCE.md`](PROVINCE.md).

## What's in this repository

```
kama-shokunin/
├── SKILL.md                 one-question playbook + decision table
├── PROVINCE.md              surfaces, observed state, write boundary
├── SHONEN.md                promotion checklist
├── LOG.md                   append-only trail
├── SCORECARD.md             per-axis verdicts
├── MINT.md
├── AGENTS.md
├── tools/
│   ├── kama-probe.sh        listeners / snapshot / check
│   └── test-snapshot.sh
├── registry/
│   ├── endpoint-consumers.tsv
│   └── history/             latest.tsv, DELTA.md
└── corpus/
    ├── knowledge/           consumer-registry, cross-lane-scope
    └── lessons/
```

## Start here

```sh
bash tools/kama-probe.sh check
bash tools/kama-probe.sh check --json
bash tools/kama-probe.sh listeners
```

`DEAD` on a registered port is a valid, current answer. Do not restore
a systemd unit from this lane.

## How a round works

One axis-move, usually on operability or freshness. Lane identity:
`kama-shokunin <kama@shokunin.local>`.

## Fleet

[VeigaPunk/shokunin](https://github.com/VeigaPunk/shokunin) ·
[kimi-shokunin](https://github.com/VeigaPunk/kimi-shokunin)
