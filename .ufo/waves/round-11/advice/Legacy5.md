# Legacy5 — provenance supplement, `corpus/knowledge/endpoint-identity.md` (round 11)

Seat: Legacy5 (executor, leaf). Owned target: `corpus/knowledge/endpoint-identity.md` only.
Actual review date: **2026-10-20T02:14:28Z UTC** (`date -u`). Heading keeps the steered round label `2026-10-19` per parent IRC erratum; the actual review date is stated inside `verified-at`, and this seat acknowledges the C1 axis correction to **calibration** (dates/confidence/recheck limits, not a freshness refresh).

## Change (append-only)

Appended after the last existing byte:

- `## Provenance supplement — round 11 (2026-10-19)`
- `source:` / `verified-at:` / `recheck:` lines at column zero (single physical line each)

No other edit; no prepend; no rewrite; no sibling file touched. No commits/pushes.

## Byte-integrity evidence

Before (equals `.ufo/waves/round-11/legacy-baseline.json` entry `068fe659…`, 19263 bytes):

```
$ sha256sum corpus/knowledge/endpoint-identity.md
068fe65966aa4b497ed3556cb834e365114329b97f6f6f2dfbd3a4da4858c266
bytes=19263
```

After (prefix — first 19263 bytes — is byte-identical; only the 1794 appended bytes are new):

```
$ head -c 19263 corpus/knowledge/endpoint-identity.md | sha256sum
068fe65966aa4b497ed3556cb834e365114329b97f6f6f2dfbd3a4da4858c266
$ sha256sum corpus/knowledge/endpoint-identity.md
48a95aa2662e37b2c0dc94aad954714243c9aac3bdfa15e8c0deb1ef4026e977
bytes=21057   appended_bytes=1794
heading=1  source=1  verified-at=1  recheck=1
```

Field counts were 0/0/0 before (baseline `missing` list) and are 1/1/1 after, each matched at column zero (`grep -c '^source:'` etc.).

## Why each field is honest

- **`source:`** Every cited item was verified to exist read-only in-repo at the stated path: `tools/kama-probe.sh` (1092 lines), `registry/endpoint-consumers.tsv` (36 lines), `corpus/knowledge/listener-census.md` (381), `corpus/knowledge/served-model-identity.md` (37), `corpus/knowledge/consumer-registry.md` (390), `corpus/lessons/round-1-citations.md` (78), `corpus/lessons/round-1.md` (84), `SKILL.md`. F1–F12 are cited only as *retained/re-derived* in the round-1 citation table — not as live values. Dates come from the artifacts themselves or git commit dates, not memory:
  - `corpus/knowledge/listener-census.md:3` — "Measured: 2026-09-28 ~22:47–22:52 -0300, host `plazir27`, live on-box probes."
  - `corpus/knowledge/consumer-registry.md:4-5` — "every row is a live re-read/re-probe, not a carried-forward claim"; its `§Errata — 2026-10-14 re-census` and `§Corrections — round 10 (2026-10-19)` are in-file.
  - `corpus/lessons/round-1.md:3-4` — "Every rule below is grounded in a command run on 2026-09-28".
  - `git log --date=short`: `endpoint-identity.md` → `c6199a2` 2026-09-28 (round 1), `47f3aed` 2026-10-14 (round 4), `1e41928` 2026-10-19 (round 10); `served-model-identity.md` → only `c6199a2` 2026-09-28; `round-1-citations.md` → `c6199a2` 2026-09-28 + `83bee7f` 2026-09-29.
- **`verified-at:`** Separates three distinct things: (a) original on-box observation date 2026-09-28 (round-1 live census), (b) file revisions 2026-10-14 (round 4) and 2026-10-19 (round 10 appended corrections), (c) the round-11 review itself, performed **2026-10-20T02:14Z** as metadata only. It explicitly states no endpoint/socket/service was contacted and no on-box observation was revalidated live, and it names the confidence limit: "provenance-of-record only, not endpoint health". No live-revalidation claim is made anywhere.
- **`recheck:`** Gives one precise, safe path/command for future authorized revalidation: from the repo root `bash tools/kama-probe.sh check --json` (loopback-only metadata `GET /v1/models` per registry row, no credentials; `listeners --json` for a fresh loopback census) compared against the file's own decision table, with the historical F1–F12 route through `corpus/lessons/round-1-citations.md` rows and its recorded commands under an explicit authorization caveat. It records that Round 11 ran none of these (no endpoint census in scope). No placeholder, no vague "revisit later".

## Retained-evidence / limit checks (all read-only, repo-local)

- `SKILL.md:44-45` (opened, current state) — "`qwen-coder.service` reports `LoadState=not-found`, `ActiveState=inactive`, `SubState=dead`, `MainPID=0`": the target file's live examples are historical, consistent with its round-10 corrections and the retained pointers.
- This seat executed **no** network or host commands: no `curl`/`ss`/`systemctl`/`docker`; only repo-local `read`/`grep`/`glob`, `sha256sum`/`stat`/`wc`/`head`/`tail` on repo files, `git log` on repo paths, and `date -u`. No host config/env/credential body was read. No endpoint census was run.
- F-fact **content** correspondence was deliberately not re-derived (that needs the recorded host commands, out of scope this round); only existence/shape of the retained files was checked. That is exactly the confidence boundary stated in `verified-at`.

## Limits / defects

- Heading date `2026-10-19` is the steered round label, not the access date; if a checker parses the heading date as review date, `verified-at` (2026-10-20T02:14Z) is the disambiguating field.
- The supplement asserts nothing about present endpoint health; the file's on-box claims remain historical (round-10 corrections untouched).
- This report is author-advisor evidence, not outside verification.
- No tool installs or upgrades were needed or performed (nothing to record under the tooling directive).

## Files changed

- `corpus/knowledge/endpoint-identity.md` — append-only, +1794 bytes, prefix bytes retained exactly (baseline hash preserved).
