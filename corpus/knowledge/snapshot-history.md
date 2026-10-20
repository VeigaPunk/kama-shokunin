# Endpoint snapshot history — invocation contract

Round 2 adds stateful comparison to the read-only endpoint gate. It does **not**
install or imply a scheduler. Freshness is now diffable whenever an authorized
caller invokes the command; cadence remains operator-owned.

## Run it

```sh
bash tools/kama-probe.sh snapshot
```

The command evaluates the same registry rows and returns the same gate status as
`check`: `0` when every declared consumer reconciles, `2` when at least one row
drifts, and `1` for a probe/tool error (`tools/kama-probe.sh:932-1003`). Therefore
an exit `2` means the snapshot was written successfully **and** captured drift;
it is not a persistence failure.

Use `--history DIR` for an isolated history root. `snapshot --port N` is refused
because a single-port probe has no registry row set to persist
(`tools/kama-probe.sh:111-150`).

## Persisted contract

| Artifact | Contract | Tracked |
|---|---|---|
| `<ISO-UTC>.json` | Full normalized row state for one invocation; schema `kama-probe/v2` | no; local run evidence |
| `latest.tsv` | Comparison baseline: `id`, `verdict`, `reason`, normalized served-model id, port, file-match | yes |
| `DELTA.md` | Append-only, one line per changed field or row-set transition | yes |
| `.lock` | `flock` serialization for concurrent invocations | no |

The first run writes one `baseline recorded` line and zero transitions. An
unchanged run writes its local dated JSON but leaves both tracked artifacts
byte-stable; `latest.tsv` advances only with a transition or recovery rebaseline.
Later runs compare `verdict`, `reason`, `served_model`, `port`, and `file_match`;
row additions and removals are explicit transitions (`tools/kama-probe.sh:833-903`).
The dated JSON must validate before either tracked artifact advances, so a failed
snapshot is retried against the previous baseline rather than silently consuming
a transition (`tools/kama-probe.sh:932-1007`).

A malformed or unreadable baseline cannot turn garbage into a phantom
`row-absent` event. Malformed lines are discarded and warned; if no usable rows
remain, the run rebaselines. `DELTA.md` records a `baseline-note` audit line.
This preserves the endpoint gate result while making loss of history visible.

## Persistence boundary

Endpoint URLs, registry notes, raw evidence strings, and full model paths do not
land in tracked state. `latest.tsv` and `DELTA.md` keep only normalized fields;
served ids are basenames with a trailing `.gguf` removed
(`tools/kama-probe.sh:911-928`). Control characters are stripped. Userinfo,
query, and fragment components are removed before a resolved URL can reach the
snapshot path (`tools/kama-probe.sh:555-572`). The history root and tracked
outputs refuse symlinks, and `flock` plus atomic baseline replacement prevent
interleaved/torn writes (`tools/kama-probe.sh:932-1003`). The command remains
read-only toward consumers and services; its only writes are beneath the chosen
history directory.

## Round-2 measurements

- Final live default-history baseline:
  `snapshot=20260929T043044Z prev=- rows=11 model_ok=3 drift=8 transitions=0 exit=2`.
- Immediate stable re-run:
  `snapshot=20260929T043052Z prev=20260929T043044Z rows=11 model_ok=3 drift=8 transitions=0 exit=2`.
- Hermetic behavioral harness:
  `bash tools/test-snapshot.sh` → `RESULT pass=24 fail=0` in 1.15 s. It exercises
  baseline creation, stable rerun, `MODEL_OK→DEAD`, served-id change, row add,
  row removal, malformed-baseline recovery/audit, `--port` refusal, and symlink
  containment.

The tracked baseline is `registry/history/latest.tsv`; the first-run ledger is
`registry/history/DELTA.md`. The unchanged live rerun added no ledger line.

## Limits and scheduling handoff

This is sampled state, not event capture: a transition that begins and ends
between invocations is invisible. Nothing in this repository invokes `snapshot`
on a clock. Host inspection found systemd user timers are the viable scheduler
surface and cron/at/anacron absent, but `PROVINCE.md` forbids kama from installing
or enabling units. The operator must choose cadence and failure notification.
Until then, the honest claim is **invocation history**, not periodic monitoring.

The schema also does not cover declared-vs-served context size; it records
endpoint identity only. That remains a separate freshness gap.

## Corrections — round 10 (2026-10-19)

*[correction 2026-10-19 (round 10, A09): `tools/kama-probe.sh:932-1003` at line 15 is stale (nl -ba tools/kama-probe.sh | sed -n '110,111p;845,848p;932,1003p' => 932-1003 is baseline/snapshot logic; exit meanings are at 110-111 and check JSON at 845-848); current anchor: `tools/kama-probe.sh:110-111,845-848`]*

*[correction 2026-10-19 (round 10, A10): `tools/kama-probe.sh:111-150` at line 21 is stale (nl -ba tools/kama-probe.sh | sed -n '111,159p' => the --port snapshot refusal is at 157-159, beyond the old cited range); current anchor: `tools/kama-probe.sh:157-159`]*

*[correction 2026-10-19 (round 10, A11): `tools/kama-probe.sh:833-903` at line 36 is stale (nl -ba tools/kama-probe.sh | sed -n '833,903p;919,943p' => additions and removals are now emitted at 919-943); current anchor: `tools/kama-probe.sh:919-943`]*

*[correction 2026-10-19 (round 10, A13): `tools/kama-probe.sh:911-928` at line 51 is stale (nl -ba tools/kama-probe.sh | sed -n '911,928p;959,970p' => served-id persistence normalization is now at 959-970); current anchor: `tools/kama-probe.sh:959-970`]*

*[correction 2026-10-19 (round 10, A14): `tools/kama-probe.sh:555-572` at line 53 is stale (nl -ba tools/kama-probe.sh | sed -n '555,572p;608,612p' => 555-572 expands paths; resolved-URL userinfo/query/fragment stripping is at 608-612); current anchor: `tools/kama-probe.sh:608-612`]*

*[correction 2026-10-19 (round 10, A15): `tools/kama-probe.sh:932-1003` at line 55 is stale (nl -ba tools/kama-probe.sh | sed -n '932,1003p;1040,1054p' => symlink refusals and flock are at 987-1003; atomic baseline replacement is at 1040-1054); current anchor: `tools/kama-probe.sh:987-1003,1040-1054`]*

## Provenance supplement — round 11 (2026-10-19)

source: retained historical evidence — `tools/kama-probe.sh` snapshot implementation and the round-10 appended correction anchors; `tools/test-snapshot.sh` fixture harness (its 24/0 result is historical, not run this round); `registry/history/latest.tsv` snapshot 20261014T124232Z; `registry/history/DELTA.md:6` baseline and dated October transitions; `corpus/lessons/round-2.md`; history commits `83bee7f` and `1e41928`. The dated JSON behind round-2 ids 20260929T043044Z/20260929T043052Z is not retained; those ids and summary strings survive as prose, not reproducible original JSON evidence.
verified-at: original observations 2026-09-29 and 2026-10-14; metadata review 2026-10-20 only. Baseline timestamp and row count are corroborated by `registry/history/DELTA.md:6`; `model_ok=3 drift=8 exit=2` remains round-2 history without retained dated JSON. The tracked October sample is in `latest.tsv` and DELTA transitions. No live probe, snapshot run or endpoint revalidation occurred in round 11; none of this file's endpoint-state claims is refreshed.
recheck: `bash tools/test-snapshot.sh` checks the hermetic loopback-fixture contract, not current endpoints. A separately authorized live sample may use `bash tools/kama-probe.sh snapshot --history .ufo/manual-snapshot` (writes isolated lane history, not read-only, and never replaces the cited tracked baseline). Reopen the round-10 appended implementation anchors with ranged file reads before relying on their current contents.

## Correction — round 16 (2026-10-20)

`bash tools/test-snapshot.sh` now reports `RESULT pass=30 fail=0`
(`.ufo/waves/round-16/run-test-snapshot.txt`); the 24/0 figure above is the
historical count. The six new assertions check that a seeded `latest.tsv` row
with verdict `MODEL_LOADING` is accepted by `diff_baseline`, and that the
near-miss `MODEL_LOADED` is still dropped as malformed. The snapshot schema
string stays `kama-probe/v2`; an older probe copy reading a history written by
the new probe would drop `MODEL_LOADING` rows as malformed (rollback limit).
