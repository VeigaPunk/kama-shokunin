# Provenance2 — consumer-registry.md provenance supplement (round 11, advisory)

Seat: `KamaR11.Provenance2` (leaf verifier). Assigned target: the appended provenance
supplement in `corpus/knowledge/consumer-registry.md` (lines 392–395), its retained
historical context, and `corpus/QUALITY.md` KQ11. Parent owns measurement/integration;
nothing here is a runtime or acceptance verdict.

Axis named: **operability** (artifact survives re-reading without false currency), measured
against KQ11's four requirements. Temporal freshness is the failure mode under test, not a
score this seat may raise.

## Verdict

The supplement is **substantially honest and append-only**: the original byte prefix is
byte-identical, all seven cited in-repo anchors were re-opened and support what they are
cited for, historical dates and the metadata-only/live boundary are explicit, and the
recheck is bounded and scope-safe. Two semantic defects remain, one material:

- **D1 (medium)** — line 393's final sentence asserts `#1–#16, #35 … not live files`,
  contradicting the retained prefix, which records #12, #13, #35 as still present and
  #17–#20's relocated checkout as surviving. It also states host absence without the
  shape-only command that the same file's round-10 corrections (A19–A24) recorded.
- **D2 (low)** — the baseline timestamp `2026-09-29T04:30:44Z` is attributed to the
  `DELTA.md + latest.tsv` pair; only `DELTA.md:6` holds it, while `latest.tsv` is the
  `20261014T124232Z` snapshot.

Neither defect touches the prefix, the observation dates, or the recheck boundary.

## Evidence actually retained (read-only; no checks executed)

Repo-byte comparison (not a runtime probe):

```text
git show HEAD:corpus/knowledge/consumer-registry.md | wc -c        -> 39951
git show HEAD:corpus/knowledge/consumer-registry.md | sha256sum    -> ee2c399226ede70d2e217044a0f17ad70002846cc19da090f48f35065d182972
head -c 39951 corpus/knowledge/consumer-registry.md | sha256sum    -> ee2c3992…d182972   (match)
git diff --numstat -- corpus/knowledge/consumer-registry.md        -> 5  0
git diff hunk header                                               -> @@ -389,2 +389,7 @@
working file                                                       -> 395 lines / 41760 B, sha256 6ca37b77…4abd28
```

So the claim "pre-existing bytes (39951 B, sha256 ee2c…d182972) retained as prefix" is
exactly true: 5 added lines, zero deletions, insertion only at EOF after line 390.

Dates corroborated by file metadata (`stat -c '%y'`, `date -u`; read-only):

| cited source | claim | observed |
|---|---|---|
| `corpus/lessons/round-1.md:3-5` | round-1 commands run 2026-09-28 | lines 3–5 state 2026-09-28; file mtime 2026-10-14T12:45Z (rewritten in round 4, observation date retained) |
| `corpus/lessons/round-1-citations.md:7-18` | F1–F12 audit | lines 7–18 are exactly rows F1–F12 |
| `corpus/lessons/round-4-recensus.md:26-27` | 2026-10-14 teardown | "dead endpoint. `qwen-coder.service` gone; `34113` and `8080` refuse." |
| `registry/history/DELTA.md:6-22` | baseline + transitions | line 6 baseline `2026-09-29T04:30:44Z`; lines 7–22 all `2026-10-14T12:42:32Z`; mtime equals that stamp |
| `registry/history/latest.tsv` | (paired source) | `#@snapshot_id 20261014T124232Z`; 3 DEAD rows — see D2 |
| `corpus/lessons/round-1-relaunch-freshness.md:10-16` | 3 rows DEAD, exit 2 | lines 10–16 match verbatim; mtime 2026-10-15T04:59Z |
| `.ufo/round-10/audit/stale-anchors.tsv` | rows A19–A24, A51 | all seven rows present at tsv lines 19–24 and 51 |
| `.ufo/round-10/gates/check.json` | sample 2026-10-19T21:35:49Z; contested | `sampled_utc` exact; notes say "Not evidence for any admitted round-10 claim … contest its admissibility" — paraphrase accurate |
| `verified-at` | `date -u 2026-10-20T02:14Z` | file mtime 2026-10-20T02:18:19Z (23:18:19 −0300); write 4 min after the date capture — consistent, not falsified |

No public URL was assigned to this seat; all evidence is in-repo. No endpoint was contacted,
no build/lint/test/formatter was run, no tool installed or upgraded.

## KQ11 clause-by-clause

| KQ11 requirement | Result |
|---|---|
| preserve original byte prefix | **PASS** — digest and size exact; 5/0 append-only |
| identify historical observation dates or unknown dates | **PASS** — 2026-09-28, 2026-10-14, 2026-10-15, 2026-10-19 enumerated; verified-at 2026-10-20 |
| distinguish metadata review from live revalidation | **PASS** — "metadata-only review … no endpoint contacted, no live revalidation claimed"; the one probe sample is explicitly labeled contested/non-authority |
| name a bounded current recheck or explicit unavailable surface | **PASS** — `check` + `snapshot`, 3 registered rows, shape-only `test -e`/`wc -l`, endpoint contact only under authorized scope |
| new entries open with provenance trio | **N/A here** — legacy file; supplement itself uses the `source:`/`verified-at:`/`recheck:` trio. New-entry trio not assessed (outside this seat's file) |

## Findings

### D1 — medium — line 393 overstates host-file absence, contradicting the prefix

Exact text (`corpus/knowledge/consumer-registry.md:393`, final sentence):

> Host-side row targets (#1–#16, #35; relocated/deleted trees) are historical record only, not live files.

Contradicted by retained bytes in the same file:

- `:66-67` — "`~/.local/bin/omp` (#12) still contains `LLAMA_CPP_BASE_URL || "http://127.0.0.1:8080"`".
  #12 is a live host file and, per the prefix, the surviving carrier of the 8080 default;
  the blanket leaves it reading as deleted.
- `:68` — "`~/.omp/agent/config.yml` still exists; its `:168` auth-broker URL is gone".
  #13 exists.
- `:69` — "`opencode.log` (#35) still exists."
- `:217-221` — "One checkout survives — `~/Projects/ufo-fsd-alpha` … Both pin-bearing files
  still carry the 34113 value." Rows #17–#20 are not "not live files"; the ports are dead,
  the files are not documented as gone.

The prefix draws the line precisely — `:64` excludes #12/#13 from the historical list
("Rows #1-#11, #14-#16, #21, #31-#34 are therefore historical") — and the supplement erases
that distinction. The sentence is also an unrecorded host-presence measurement, unlike the
A19–A24 corrections it cites, which each embed the exact `test -e`/`wc -l` command (KQ8-style
discipline; KQ11's "explicit unavailable surface").

Smallest repair (replace only the final sentence; prefix untouched):

> Host presence was not re-measured in this review. Per §Errata `:62-75`, rows
> #1–#11, #14–#16, #21, #31–#34 are documented deleted; #12 still exists with the 8080
> builtin default (`:66`), #13 exists without loopback strings (`:68`), #35 exists (`:69`);
> #17–#20's surviving relocated checkout at `:217-221` is file-present but port-dead.
> Treat every verdict on those rows as historical.

Do not re-assert `not live files` without a recorded shape-only command per row.

### D2 — low — baseline timestamp attributed to the wrong source

Text (`:393`): "`registry/history/DELTA.md:6-22 + registry/history/latest.tsv (baseline
2026-09-29T04:30:44Z; MODEL_OK→DEAD and row-absent transitions at 2026-10-14T12:42:32Z)`".

`latest.tsv` opens `#@snapshot_id 20261014T124232Z` and holds three DEAD rows; it does not
contain the 2026-09-29 baseline. The baseline is `DELTA.md:6` only. A reader who opens
`latest.tsv` to verify the baseline finds a different timestamp.

Smallest repair: move the baseline into the DELTA clause and state what `latest.tsv` is —
"`DELTA.md:6-22` (baseline `2026-09-29T04:30:44Z`; transitions `2026-10-14T12:42:32Z`) +
`latest.tsv` (3 DEAD rows, snapshot `20261014T124232Z`)".

## Already correct (do not "repair")

- **Prefix integrity is exemplary.** Exact size + SHA-256 of committed bytes, exact match
  against the first 39951 bytes of the working file, 5/0 diff, insertion at EOF. This is the
  KQ11 positive control and it passes.
- **Temporal separation is explicit and correct.** `verified-at: 2026-10-20` with the
  disclosed steered heading label `2026-10-19`; the four observation epochs are listed;
  the 2026-10-19 gate sample is downgraded to "contested admissibility, not admitted
  authority". `QUALITY.md:34` labels the criterion round "reviewed 2026-10-20 UTC" — the
  divergence is disclosed in-line, not concealed.
- **No runtime freshness is claimed.** "no endpoint contacted, no live revalidation claimed"
  is consistent with every added line; nothing in the supplement revives an obsolete
  config-body read as a current recheck.
- **All seven in-repo anchors resolve and support their citation**, including the exact
  F1–F12 row span and the verbatim `3 rows DEAD, exit 2` sample. No invented source.
- **Recheck is bounded and scope-safe.** Two named commands with known denominator (3
  registered rows) and exit domain (0/2), shape-only host checks, and endpoint contact
  deferred to an authorized probe scope — satisfies KQ11's last clause and KQ10/KQ5.

## Residual limits

- Host-file existence (#12/#13/#17–#20/#35) was **not** measured by this seat; D1 is
  established from internal contradiction with retained bytes, not from a `test -e` run.
  Parent may settle it with the shape-only commands already named in the supplement.
- KQ11's "missing-field and altered-prefix controls must fail" negative control is not
  evidenced inside this file; that calibration belongs to the C1 seat.
- §Errata-listed archival rows #31–#34 and #21 are out of this file's live surface and
  were not re-opened.

## Install / update record

None. No package, tool, binary, or channel action was taken; no `sudo`, `pacman`, `uv`,
`cargo`, or `npm` command ran.
