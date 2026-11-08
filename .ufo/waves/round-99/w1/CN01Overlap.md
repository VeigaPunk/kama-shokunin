# CN01 — sibling overlap and vocabulary scan (kama round 99, w1)

Seat: connector, read-only. No tracked lane file, fleet repo file, jj state or Git index was written; the only
writes are this report and `.ufo/waves/round-99/w1/out/CN01Overlap/`, both untracked wave paths. Every receipt is
under `.ufo/waves/round-99/w1/out/CN01Overlap/`; scratch `/fast/scratch/hyaku/kama-r99/CN01Overlap/` was
deleted after the receipts were copied. No tool was installed.

Command set (real, read-only): `grep -rnE 'models[-_]autoload' kengaku-shokunin/`;
`grep -rnE 'models[-_]autoload|router-unloaded|router-autoload|router-sleeping|MODEL_UNLOADED' scripts/`
(0 hits); the grep tool over all 21 non-kama `*-shokunin` directories with hidden files included
(`gitignore:false`) for `router-unloaded|router-autoload|router-sleeping|MODEL_UNLOADED` → **No matches found**;
for `models_autoload|models-autoload|…` → kengaku round-51 only; fleet-root `tools/ counters/ census/ templates/`
with the same vocabulary → **No matches found**. (Absolute-glob paths such as
`/home/vgpnk/Projects/shokunin/*-shokunin` return a false "No matches found" in the grep tool — reported through
`report_issue`; relative per-lane paths were used instead.)

## 1. Hits outside kama

Thirteen hits, one lane, all in kengaku's round-51 wave; **none** is a parser or an instrument.

| file:line | what the hit is |
|---|---|
| `kengaku-shokunin/.ufo/waves/round-51/w1-results.json:16` | embedded `C1ExecEndpoints` output, captures `/props` `…"models_autoload":true…` |
| `kengaku-shokunin/.ufo/waves/round-51/w1-results.json:334` | embedded `C1ExecNewSurface` output, same capture |
| `kengaku-shokunin/.ufo/waves/round-51/w1/C1CritEndpointId.md:81` | quoted `/props` body of `:1234` (`role=router, max_instances=2, models_autoload=true`) |
| `kengaku-shokunin/.ufo/waves/round-51/w1/C1ExecEndpoints.md:145` | argv text: `--models-dir … --models-max 2 --models_autoload` |
| `kengaku-shokunin/.ufo/waves/round-51/w1/C1ExecEndpoints.md:235` | quoted `/props` body (same capture) |
| `kengaku-shokunin/.ufo/waves/round-51/w1/C1ExecNewSurface.json:57` | surface row text: `… /props (role=router, max_instances=2, models_autoload=true, build b1-39febd2) …` |
| `kengaku-shokunin/.ufo/waves/round-51/w1/C1ExecNewSurface.json:67` | `"props"` field holding the raw body |
| `kengaku-shokunin/.ufo/waves/round-51/w1/C1ExecNewSurface.md:29` | the same raw body, quoted |
| `kengaku-shokunin/.ufo/waves/round-51/w1/C1ExecNewSurface.md:81` | the same surface row as prose |
| `kengaku-shokunin/.ufo/waves/round-51/w1/C1ScribeKnowledge.md:124` | quoted `/props` body, field order differs |
| `kengaku-shokunin/.ufo/waves/round-51/w1/C1ScribeKnowledge.served-endpoint-identity-pin.md:47` | the pin note quotes the same body |
| `kengaku-shokunin/.ufo/waves/round-51/w1/SrcLlamaServer/llamacpp-tools-server-README-v0.8.0.md:234` | vendored README option row: `--models-autoload, --no-models-autoload` |
| `kengaku-shokunin/.ufo/waves/round-51/w1/SrcLlamaServer/llamacpp-tools-server-README-v0.8.0.md:2161` | vendored README prose: per-request `?autoload=true|false` |

Zero hits for `router-unloaded`, `router-autoload*`, `router-sleeping`, `MODEL_UNLOADED` in **any** non-kama lane
and in `scripts/`. So no lane owns, emits or parses the router reason vocabulary, and no tool outside kama can
break on a new reason. (The fleet *report* records quote the strings — e.g. `.ufo/reports/round-88/kama.md:27`,
`:36`, `.ufo/reports/round-92/kama.md:27` — but they are prose, outside the `*-shokunin`/`scripts` scope, and
parse nothing.)

## 2. Competing `/props` claim: kumitate, kengaku, mori

| lane | line that decides it | verdict |
|---|---|---|
| kumitate | `kumitate-shokunin/PROVINCE.md:32` "Local model serving and endpoints → kama. Prompt and skill craft → kotoba. Research method → chousa." (repeated :48, :75) | defers |
| mori | `mori-shokunin/PROVINCE.md:15` "endpoint and model-serving health (→ kama); credential material (→ kagi)."; :67 "kama \| Owns local model-serving and endpoint health; mori does not infer serving health from host/resource signals." | defers |
| kengaku | `kengaku-shokunin/PROVINCE.md:15` "… \| capability interpretation only; flag authority is kama's (serving plane). Capture-time pin 2026-10-28 …" | defers, but see contradiction |
| kama | `kama-shokunin/SKILL.md:1758` "## Round-88 router-mode readiness (owner: kama)"; `kama-shokunin/PROVINCE.md:421` "Round 88: llama.cpp **router mode** is a governed serving surface."; :143-144 "kengaku excludes the model-serving plane" | owns |

**Contradiction, stated, not smoothed:** `kengaku-shokunin/PROVINCE.md:6` ("**Refuses:** anything outside this
domain …") and :26-27 ("**Not owned:** the model-serving plane (llama-server flags, slot/batch config) — no lane
owns it; escalate to the integrator instead of remediating.") sit under the dated heading "Refusals and
reported-out scope (round 9, `corpus/evidence/round9-fleet/sibling-overlap.md`)". They contradict kengaku's own
later row :15 ("flag authority is kama's"). The later row, kama's SKILL owner line and kama's PROVINCE surface
claim decide it against the dated round-9 sentence; that sentence is stale in kengaku, which is adjacent to this
round, not part of it.

## 3. Duplicates and collisions in kama's own surfaces

- **No duplicate name.** The `## Probe reason codes` table (`SKILL.md:1832` heading, rows `:1843-1868`) has 24
  rows / 23 reasons plus `body-too-large`; its `router-*` rows are `router-sleeping` (:1861),
  `router-unloaded-autoload` (:1862), `router-loading` (:1863), `router-downloading` (:1864),
  `router-model-missing` (:1865), `router-model-invalid` (:1866), `router-unloaded` (:1867).
  `router-autoload-unread` appears in no tracked kama byte outside the round-99 wave files, the candidate probe,
  `corpus/knowledge/router-props-autoload.md`, `corpus/lessons/round-99.md`, the plan and the counter docstring.
- **Superseded statements that must be narrowed at M3** (each now false against the candidate):
  - `SKILL.md:1867` — `router-unloaded`'s trigger text still includes "a `/props` that failed, was over the
    4 MiB cap, or was not JSON". The candidate moves those to `router-autoload-unread`.
  - `corpus/knowledge/probe-answer-bounds.md:29-30` — "an oversize `/props` is read as 'router does not
    autoload', the conservative direction (an `unloaded` entry then grades `MODEL_UNLOADED router-unloaded`,
    cell H3)". Falsified by the candidate: oversize `/props` grades `MODEL_UNLOADED router-autoload-unread`
    (`controls/c3-candidate.out:8`, cell U2). This is a tracked knowledge entry, not a wave receipt.
  - `corpus/knowledge/router-mode-readiness.md:49` — "`unloaded` without autoload, `unloaded` + `failed: true`,
    `incomplete`, unknown → `MODEL_UNLOADED` / `router-<value>[-failed]`". The generic `router-<value>` no longer
    covers the unread answer.
- **Not a collision, but stale prose:** `tests/probe-verdicts/RouterUnloaded.json:5` says the row's `/props`
  "does not assert models_autoload", while the row's route (`:14-18`) answers
  `{"role":"router","models_autoload":false}` — an explicit off. The verdict is unchanged, and the whole matrix
  is green at the candidate: `tests=77 passes=77 failures=0` at base (`probe_sha256=40ab387e…`) and at the
  candidate (`probe_sha256=829fbde5…`) — `out/CN01Overlap/verdict-matrix-77.txt`. After round 99 that `why`
  sentence describes the *unread* case, which the probe would grade `router-autoload-unread`.

## 4. The one non-obvious finding: the new row is unbindable under `## Probe reason codes`

`tools/round90-reason-rows.py:37-53` freezes a 23-reason `POPULATION`, parses rows **only** under
`HEADING = "## Probe reason codes"`, and binds each row to a line of
`.ufo/waves/round-90/measured/reason-cells.jsonl` whose `probe_sha256` equals the probe at `--rev`. A row
outside the population is reported as `additional` (not a failure) **but still counts in `rows` and must be
bound**. `tools/round90-reason-capture.py`'s frozen cell list (24 cells) answers `/props` only with
`props(True)` or `props(False)`; it has no cell that omits `/props`, oversizes it, sends non-JSON, or sends a
router document without the field. Therefore **no capture cell can ever print `router-autoload-unread`**, and a
25th row under that heading can never bind — the round-92 repair (re-capture the receipt, `bound=24 unbound=0`,
`corpus/lessons/round-92-verifier-spotcheck.md:95-99`) can only ever reach the 24 existing cells.

Measured A/B/C on a fixture repo (`git init` under scratch, toplevel asserted; SKILL and probe bytes from
`439fdb3d`, receipt re-captured for real with `--probe-file` on those exact probe bytes; commits
`7703f7f`/`2859214`/`0783fe7` in `out/CN01Overlap/fixture-commits.txt`):

| fixture | counter line | exit |
|---|---|---|
| A control: base SKILL + fresh receipt | `REASON_ROWS population=23 documented=23 rows=24 bound=24 unbound=0 missing=0 duplicates=0 additional=1 receipt=current` | 0 |
| B row inserted under `## Probe reason codes` | `REASON_ROWS population=23 documented=23 rows=25 bound=24 unbound=1 missing=0 duplicates=0 additional=1 receipt=current` | **1** |
| C same row, same reason/verdict, moved to the `## Round-88 router-mode readiness` decision table | `REASON_ROWS population=23 documented=23 rows=24 bound=24 unbound=0 missing=0 duplicates=0 additional=1 receipt=current` | 0 |

Receipts: `out/CN01Overlap/reason-rows-{A-control,B-row-under-reason-codes,C-row-in-decision-table}.out`,
`reason-capture-fresh.out`. The lane's tip today is already red on this instrument
(`receipt=stale`, `bound=0`, exit 1 — `reason-rows-lane-base.out`), because the probe changed after the last
re-capture; the row addition converts a *repairable* red into one that cannot be repaired without editing a
round-90 instrument.

## Ownership call

**Adjacency report, not contested ownership.** kama owns the router reason vocabulary; kengaku's thirteen hits
are capture-time observations under its own "capability interpretation only; flag authority is kama's (serving
plane)" row; kumitate and mori route the serving plane to kama by province. No handoff is owed for the new
reason. One adjacent, out-of-round correction is owed to kengaku: its round-9 refusal sentence
(`PROVINCE.md:26-27`, "no lane owns it") is stale against its own `PROVINCE.md:15`.

## Sentence the report should carry (verbatim)

> All five round-88/89 router reasons and the new `router-autoload-unread` are kama's alone: a read-only scan
> of every other `*-shokunin` lane repo (hidden files included) and `scripts/` finds no owner and no parser —
> the only non-kama occurrences are kengaku's round-51 observation records of the `/props` body field
> `models_autoload` (`kengaku-shokunin/.ufo/waves/round-51/w1/C1ExecNewSurface.md:29` and twelve siblings),
> filed under `kengaku-shokunin/PROVINCE.md:15` "capability interpretation only; flag authority is kama's
> (serving plane)"; the province line that decides it is `kama-shokunin/SKILL.md:1758`
> "## Round-88 router-mode readiness (owner: kama)" (`kama-shokunin/PROVINCE.md:421`).
>
> The `router-autoload-unread` row must not land under `## Probe reason codes`: the frozen round-90 counter
> binds every row there to a capture cell and its frozen 24-cell population has no unread-`/props` cell, so a
> 25th row reads `unbound=1` exit 1 even after the round-92 re-capture repair (measured: rows=24
> bound=24 unbound=0 exit 0 without the row; rows=25 bound=24 unbound=1 exit 1 with it under that heading;
> rows=24 bound=24 unbound=0 exit 0 with the same row in the round-88 router decision table).

## Affected axes, risks, verification

- **calibration (7, lowest)** — the two stale knowledge sentences (`probe-answer-bounds.md:29-30`,
  `router-mode-readiness.md:49`) and the SKILL trigger text would otherwise state a reason the committed tip
  no longer prints; the row-placement decision is a calibration fact, not a style choice.
- **depth (7, lowest)** — a reason row whose evidence cell cannot exist would claim a capture the instrument
  cannot produce.
- **operability (8)** — unharmed: candidate `bash -n` ok, verdict matrix 77/77 at base and at the candidate
  (`out/CN01Overlap/bash-n.txt`, `verdict-matrix-77.txt`), P1 explicit-off cell unchanged.
- **adjacency (7)** — no competing claim; one stale kengaku refusal sentence.

Proposed move (bounded): put the new reason row in the round-88 router decision table (`SKILL.md:1767-1774`)
and keep `## Probe reason codes` at its 24 rows, cross-referencing `corpus/knowledge/router-props-autoload.md`
and narrowing `SKILL.md:1867`, `probe-answer-bounds.md:29-30` and `router-mode-readiness.md:49` in the same M3.
Risk: a reader grepping the reason table for the new string finds nothing — mitigated by the decision-table row
plus the knowledge entry (already written) and the SKILL decision row the plan already schedules. Alternative,
if the row must sit in the reason table: add an unread-`/props` cell to `tools/round90-reason-capture.py` (a
round-90 instrument edit, disclosed as an in-round instrument repair, receipt re-captured; the counter would
then read `unbound=0 additional=2`) — costlier and against the lane's never-edit-frozen-instrument convention.

Limits: every `SKILL.md` line number above is the base revision `439fdb3d` (`git diff --stat 439fdb3d..HEAD --
SKILL.md` is empty at the tip read, `f6e7ccc`; the reason table still has 24 rows and no `router-autoload-unread`
row, so the finding is prospective and the M3 edit can still avoid it); the A/B/C fixture carries my wording of
the row, not the L1's final text (the mechanism depends on placement only); the fixture receipt is a real
re-capture of the base probe, not of the tip probe; the round-90 population is frozen at the round-90 base probe
and reports out-of-population rows as `additional`, never as a failure on their own.
