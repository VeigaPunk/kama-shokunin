# kama-shokunin — local model serving & endpoint health

**One question only:** is the thing at this baseURL the model this
config believes it is, *right now*.

This is a [shokunin](https://github.com/VeigaPunk/shokunin) lane. Rank:
shonen. It never answers "is the model good" (that is
[kengaku](https://github.com/VeigaPunk/kengaku-shokunin)) and it never
answers "is the request safe" (that is
[kagi](https://github.com/VeigaPunk/kagi-shokunin)).

Kama detects and reports stale pins. It never writes to `~/.config`,
`~/.omp`, or systemd units. Those are operator-owned. A lane that
silently repoints a credential-bearing consumer would be acting outside
its authority (`corpus/lessons/round-1-safety.md`).

## Province

**Owns:** producer discovery of local serving ports; `baseURL` pins in
surviving consumers; served-model-id reconciliation (`GET /v1/models`
vs `--alias` vs the configured id); liveness / readiness probe
conventions (`/health`, `/props`, `/slots`); the endpoint-consumers
registry and its drift history.

**Refuses:** model quality and eval (kengaku); credential material and
auth flows (kagi); dispatch / route mechanism (kumitate); remote web
surfaces (kake). Restoring a serving unit is operator-owned work.

Host fact (`PROVINCE.md`, snapshot `20261014T124232Z` and the round-5
sample): the former `qwen-coder.service` is deleted; registered ports
`8080` and `34113` sample `DEAD` / connection-refused. `file_match=yes`
attests a pin, **not** a live `MODEL_OK`. The outage retires nothing in
this domain — discovery and drift reconciliation remain governed here.

Full boundary: [`PROVINCE.md`](PROVINCE.md).

## Start here

1. [`SKILL.md`](SKILL.md) — the one-question contract and verdict vocabulary.
2. [`PROVINCE.md`](PROVINCE.md) — surfaces, observed state, write boundary.
3. [`tools/kama-probe.sh`](tools/kama-probe.sh) — the executable probe.
4. [`registry/endpoint-consumers.tsv`](registry/endpoint-consumers.tsv) — declared consumers.

## The probe

```
bash tools/kama-probe.sh listeners     # loopback TCP + classification
bash tools/kama-probe.sh consumers     # declared-vs-actual baseURL from each file
bash tools/kama-probe.sh check         # reconcile registry vs live (the exit gate)
bash tools/kama-probe.sh snapshot      # check + dated history + DELTA.md
```

Verdict vocabulary (exact strings): `MODEL_OK` · `MODEL_MISMATCH` ·
`FOREIGN_SERVICE` · `UNAUTHORIZED_SERVICE` · `DEAD` · `NOT_HTTP`.

Exit `0` every declared consumer reconciles · `2` at least one drift ·
`1` probe error (never a verdict). Common flags: `--json`, `--registry`,
`--timeout`. Snapshot writes only under its explicit history dir
(`registry/history/` by default).

Served-id comparison is normalised: basename, then strip one trailing
`.gguf`, case-sensitive. An empty side after normalisation is
`MODEL_MISMATCH` / `unresolvable-id`.

## What's in the repo

```
kama-shokunin/
├── SKILL.md          executable craft
├── PROVINCE.md       domain boundary + observed host state
├── SHONEN.md         promotion checklist
├── MINT.md           why this lane was minted
├── LOG.md            append-only audit trail
├── SCORECARD.md      axis verdicts
├── AGENTS.md         operating rules
├── tools/            kama-probe.sh, test-snapshot.sh
├── registry/         endpoint-consumers.tsv + history/
└── corpus/           knowledge/, lessons/, QUALITY.md
```

Protocol: append-only corpus; every claim separates observation /
inference / unknown; rounds are non-author-verified. See the fleet
[README](https://github.com/VeigaPunk/shokunin#readme) for how a lane
learns.
