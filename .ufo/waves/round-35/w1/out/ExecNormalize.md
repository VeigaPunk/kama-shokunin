# ExecNormalize — scratch normalization of staged S327

Seat: ExecNormalize. Axis judged: operability. Axis authority was not touched. MISSION.md was not edited. C1 and C2 predicates were not retargeted. corpus/SOURCES.md was not appended.

## Files changed

- `.ufo/waves/round-35/w1/out/ExecNormalize/s327-normalized.md` — created. One fleet-schema data row (S327) under a `## Registry` header so the 11-column shape is parseable. Not an append.
- `.ufo/waves/round-35/w1/out/ExecNormalize.md` — this report.

Read-only inputs: `/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md` (staged S327). No write into shokuknow. No git mutation.

## Behavior

The staged S327 recheck cell was `90d` plus prose that embedded one escaped pipe (`\|`). Census splits on every `|`, so that escape makes NF=14 (E01) instead of the fleet 11-column shape (NF=13).

The scratch row keeps the other ten staged cells, sets recheck to exactly `90d`, keeps status `mined`, and keeps used-by `corpus/knowledge/endpoint-health-probe-conventions.md`. Cell interiors contain no literal `|` and no `\`. Delimiter pipes are the schema separators only.

## Stripped recheck prose

Removed from the row. Not present in `s327-normalized.md`. Exact remainder of the staged recheck cell after the cadence token `90d`, surrounding whitespace stripped (original cell was `90d` + one space + this prose). Leading character is U+2014.

```
— re-run `curl -fsSL 'https://docs.vllm.ai/en/v0.32.0/configuration/engine_args/' \| grep -c 'rejected with HTTP 503'` (expect ≥1) (ran 2026-10-23)
```

## Exact evidence

Staged append sha256 unchanged: `3f4cd9d713885efd2ec868065ee227317a556da157c8f48af36ecc9cde96de2f`.

`corpus/SOURCES.md` sha256 unchanged: `d88e497c5c10ffacb7caed0c137a9bf4c6b1bbc0e7520749bdae9f9dfa855603`. `S327` is absent from that file.

gawk `-F'|'` on the S327 data row:

```
NF 13
recheck  90d
status  mined
usedby  corpus/knowledge/endpoint-health-probe-conventions.md
NO_BACKSLASH
s327_rows 1
```

Trimmed recheck cell is exactly `90d`.

```
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --today 2026-10-24 --file /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-35/w1/out/ExecNormalize/s327-normalized.md
```

```
file	E11	S327 missing used-by corpus/knowledge/endpoint-health-probe-conventions.md
census_exit=1
```

E11 is the only census finding. E01–E10 and E12 did not fire. `--file` resolves used-by against `dirname(file)/..` (`.ufo/waves/round-35/w1/out/`), not the lane root. The lane path `corpus/knowledge/endpoint-health-probe-conventions.md` is also absent at this seat's write time. Creating it is outside this seat.

## Remaining risks

- Census cannot exit 0 on this scratch path until that used-by file exists where the checker looks. This seat must not create it and must not append the row to the lane registry.
- This seat did not re-open the live vLLM page. Quote fidelity of the staged anchor is not attested here.
- A same-seat sidecar `stripped-recheck.txt` appeared during the write and was removed so the prose lives only in this report.

## Blockers

None.
