# kama-shokunin — local model endpoints

The question this lane answers is whether the thing at a configured baseURL is the model that config believes it is, right now (`PROVINCE.md`, `tools/kama-probe.sh`).

**Rank:** `SHONEN.md` boxes are `[~]` and each note says the mark is an author assertion with no named non-author verifier. That is not a promotion. `MINT.md` records the mint on aggregator evidence from kagi round 3 and kengaku round 4.

## Owns / refuses

Owns producer discovery and read-only inspection of local serving ports, baseURL pins in the surviving consumer registry, served-model-id reconciliation, liveness and readiness probe conventions, endpoint-drift detection, and the consumer registry (`PROVINCE.md`).

Refuses model quality (kengaku), credential material and auth flows (kagi), dispatch and route mechanism (kumitate), and remote web surfaces (kake). The write boundary is hard: this lane does not write `~/.config`, `~/.omp`, or systemd units. It detects and reports. The operator repoints (`PROVINCE.md`).

## Start here

`PROVINCE.md` records the lane baseline: `bash tools/kama-probe.sh check` evaluates the registry rows, and exit `2` means drift. The script header says exit `0` is every declared consumer reconciled, exit `2` is at least one drift, exit `1` is a probe error rather than a verdict. `listeners`, `consumers`, and `check` are read-only toward live services and consumer configs. `snapshot` additionally writes inside its history directory; it is not the read-only check.

```sh
bash tools/kama-probe.sh check
```

The same province section says a later round-5 sample was still `DEAD` / connection-refused, exit 2, on the three registry rows. A drift result is the report. It is not permission to restore a unit.

## How to read the corpus

`corpus/README.md` is the coverage map. Its bytes are pinned in `.ufo/round-5/worktree-byte-manifest.json`, so this change does not edit it. `corpus/knowledge/` holds the consumer registry and cross-lane scope notes. `corpus/lessons/` holds round lessons. `registry/` holds `endpoint-consumers.tsv` and `history/`.

## Map

| Path | What it is |
|---|---|
| `PROVINCE.md` | Surfaces, observed state, write boundary |
| `SKILL.md` | Executable layer for the same question |
| `SHONEN.md` | Checklist, author-asserted `[~]` |
| `MINT.md` | Mint cause |
| `LOG.md` | Append-only record |
| `SCORECARD.md` | Axis verdicts |
| `AGENTS.md` | Operating rules |
| `corpus/` | Knowledge, lessons, quality bar |
| `registry/` | Consumer rows and history |
| `tools/kama-probe.sh` | Read-only probe |
| `plans/` | Round plans |
| `.ufo/` | Round machinery |

## Neighbors

kengaku (is the model good), kagi (is the request safe), kumitate (how a route is chosen), kake (remote web). Out of province is named in the round report (`corpus/knowledge/cross-lane-scope.md`, cited from `PROVINCE.md`).

Fleet protocol: [VeigaPunk/shokunin](https://github.com/VeigaPunk/shokunin).
