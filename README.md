# kama-shokunin

**Local model serving and endpoint health.**

This lane answers exactly one question:

> Is the thing at this baseURL the model this config believes it is, *right now*?

A **shokunin lane** minted and trained under the
[shokunin](https://github.com/VeigaPunk/shokunin) skill.

**Wiki:** [lane overview](https://app.devin.ai/org/veigapunk/wiki/VeigaPunk/kama-shokunin?branch=master)

## Domain

From `PROVINCE.md` and `SKILL.md`:

- producer discovery and read-only inspection of local serving ports
- `baseURL` pins in surviving / loadable consumers
- served-model-id reconciliation (`GET /v1/models` vs `--alias` vs configured id)
- liveness / readiness (`/health`, `/props`, `/slots`)
- endpoint-drift detection and invocation history
- the cross-lane consumer registry

It never answers "is the model good" or "is the request safe."

## Verdict vocabulary

Shared with `tools/kama-probe.sh`:

| Verdict | Meaning |
|---|---|
| `MODEL_OK` | declared consumer reconciles with the live endpoint |
| `MODEL_MISMATCH` | something answers, but not the expected model |
| `FOREIGN_SERVICE` | a non-model HTTP service occupies the pin |
| `UNAUTHORIZED_SERVICE` | identity evidence is a 401, not a model id |
| `DEAD` | connection refused / not serving |
| `NOT_HTTP` | listener is not an HTTP model endpoint |

Exit `0` = every declared consumer reconciles · `2` = ≥1 drift · `1` = probe error.

Pin correctness (`file_match=yes`) is **not** `MODEL_OK`. Serving liveness
is reported separately. Restoring a deleted systemd unit is
operator-owned — kama never writes `~/.config`, `~/.omp`, or unit files
(`corpus/lessons/round-1-safety.md`).

## In this repository

```
PROVINCE.md     surfaces, observed state, write boundary
SKILL.md        the one-question playbook
SHONEN.md  SCORECARD.md  LOG.md  MINT.md
registry/
  endpoint-consumers.tsv
  history/{latest.tsv,DELTA.md}
tools/
  kama-probe.sh
  test-snapshot.sh
corpus/         knowledge/, lessons/, QUALITY.md
```

## Probe

```bash
bash tools/kama-probe.sh listeners
bash tools/kama-probe.sh check
bash tools/kama-probe.sh snapshot
```

A `DEAD` / connection-refused sample is an honest serving-plane report,
not a retired domain. Province contraction is an L0 decision.

## What it refuses

| Out of province | Owner |
|---|---|
| model quality / eval | [kengaku](https://github.com/VeigaPunk/kengaku-shokunin) |
| credential material and auth flows | [kagi](https://github.com/VeigaPunk/kagi-shokunin) |
| dispatch / route mechanism | [kumitate](https://github.com/VeigaPunk/kumitate-shokunin) |
| remote web surfaces | [kake](https://github.com/VeigaPunk/kake-shokunin) |

## How a lane learns

Append-only corpus; every claim separates observation / inference /
unknown; rounds are non-author-verified. See the fleet
[README](https://github.com/VeigaPunk/shokunin#readme).
