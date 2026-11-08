# DRAFT — SKILL.md changes for round 99 (seat SB01Entry, lane kama)

Status: DRAFT for the committer (KamaR99). Not applied to any tracked lane file by this seat.
Target file: `SKILL.md`, section `## Probe reason codes` (heading at `SKILL.md:1831`).

## 1. The current lines this change touches (quoted verbatim from `SKILL.md` at `f6e7ccc2`)

`SKILL.md:1867` (the row to be adjusted):

```
| `router-unloaded` | `MODEL_UNLOADED` | entry `unloaded` and the probe could not confirm autoload: `GET /props` did not answer `role: router` with `models_autoload: true` (a no-autoload router, or a `/props` that failed, was over the 4 MiB cap, or was not JSON); check `/props` before sending `POST /models/load` | `R-router-unloaded` |
```

`SKILL.md:1862` (the neighbouring autoload-on row, unchanged):

```
| `router-unloaded-autoload` | `MODEL_OK` | router entry `unloaded` and `GET /props` says `models_autoload: true`; the first request loads it | `R-router-unloaded-autoload` |
```

`SKILL.md:1868` (the following row, unchanged):

```
| `body-too-large` | `FOREIGN_SERVICE` | the `/v1/models` answer exceeds the probe's 4 MiB cap (curl `--max-filesize`, rc 63); nothing was parsed, so no model verdict is possible (round 90) | `R-body-too-large` |
```

## 2. The proposed replacement (two rows: one new, one adjusted)

Replace the single `router-unloaded` row at `SKILL.md:1867` with these two rows, in this order
(`router-autoload-unread` first, then the narrowed `router-unloaded`):

```
| `router-autoload-unread` | `MODEL_UNLOADED` | the probe could not read the autoload flag — timeout, over the 4 MiB cap, not JSON, or no explicit router field; check `/props` before concluding autoload is off | `R-router-autoload-unread` |
| `router-unloaded` | `MODEL_UNLOADED` | a router that answers `models_autoload:false` | `R-router-unloaded` |
```

Rationale, one line each, grounded in S624/S625 (both re-opened by this seat on 2026-11-08, receipt
`../receipts/s624-s626-reopen.txt`):

- `router-autoload-unread` — the `/props` answer could not be read, so the probe has no evidence of
  the autoload state at all; S625 shows the field defaults to `true`, so an unread answer is never
  evidence of an autoload-off router.
- `router-unloaded` — narrowed from "could not confirm autoload" to "answers `models_autoload:false`":
  only an explicit `false` is an autoload-off configuration (S624: the field is built from
  `params.models_autoload`; S625: the default is `true`).

The verdict for both rows is unchanged (`MODEL_UNLOADED`, exit 2): C3 changes the reason vocabulary,
not the verdict.

## 3. Prose that must move with the table (two edits, same section)

`SKILL.md:1839-1841` currently reads:

```
Only `MODEL_OK` rows exit 0. Read the reason before the verdict: two `MODEL_OK` reasons are cold starts, and
five `MODEL_UNLOADED`/`MODEL_LOADING` reasons (`router-loading`, `router-downloading`, `router-model-missing`,
`router-model-invalid`, `router-unloaded`) come from the router `status` object, not from a request.
```

The count "five" and the parenthetical list become stale once `router-autoload-unread` is a row: the new
reason is `MODEL_UNLOADED` but it does **not** come from the `status` object — it comes from a `/props`
read that failed. Proposed replacement:

```
Only `MODEL_OK` rows exit 0. Read the reason before the verdict: two `MODEL_OK` reasons are cold starts, and
five `MODEL_UNLOADED`/`MODEL_LOADING` reasons (`router-loading`, `router-downloading`, `router-model-missing`,
`router-model-invalid`, `router-unloaded`) come from the router `status` object, not from a request; a sixth,
`router-autoload-unread`, is also `MODEL_UNLOADED` and comes from a `/props` answer the probe could not read.
```

## 4. The decision-table row in the round-88 section (`SKILL.md:1773`)

The round-88 decision table's last row currently reads:

```
| matching entry `unloaded` without autoload, `failed: true` (reason gains `-failed`), `incomplete` or unknown | `MODEL_UNLOADED` / `router-<value>`, drift, exit 2 | A request fails until loaded: `POST /models/load {"model":"<id>"}`. |
```

That row predates the vocabulary split and lumps the unread case with the off case. The proposed
round-99 addition (a new row, not an edit of the round-88 row, so the round-88 bytes stay as they were):

```
| matching entry `unloaded` (not failed) and `GET /props` could not be read — timeout, over the 4 MiB cap, not JSON, or no explicit `models_autoload` field | `MODEL_UNLOADED` / `router-autoload-unread`, drift, exit 2 | The autoload state is unknown, not off: read `/props` yourself, or re-probe; do not `POST /models/load` on the assumption that autoload is off. |
```

and the round-88 row's "without autoload" wording narrows to an explicit `false`:

```
| matching entry `unloaded` and `GET /props` answers `"models_autoload":false`, or `failed: true` (reason gains `-failed`), `incomplete` or unknown | `MODEL_UNLOADED` / `router-<value>`, drift, exit 2 | A request fails until loaded: `POST /models/load {"model":"<id>"}`. |
```

## 5. Operability note the committer must act on — the reason-table row is not free

`tools/round90-reason-rows.py` binds every row of the `## Probe reason codes` table to a captured
probe answer in `.ufo/waves/round-90/measured/reason-cells.jsonl`, and it exits 1 if any row is
unbound. Measured by this seat (receipt `../receipts/reason-rows-after-new-row.out`):

- with only the two-row change above and the existing receipt, the counter prints
  `rows=25 bound=24 unbound=1 missing=0 duplicates=0 additional=1` and **exits 1** — the new
  `router-autoload-unread` row is unbound, because no captured cell produces that reason;
- the same table with a re-captured receipt bound to the candidate probe and one added capture cell
  (`R-router-autoload-unread`, an HTTP `/props` stub answering `text/html`) prints
  `rows=25 bound=25 unbound=0 missing=0 duplicates=0 additional=2` and **exits 0**
  (receipt `../receipts/reason-rows-green.out`).

So landing the SKILL.md row requires two companion changes, or the round-90 reason-table counter
goes from green to red for a new reason:

1. `tools/round90-reason-capture.py` gains a `R-router-autoload-unread` cell (an `/props` answer the
   probe cannot read — non-JSON is enough, as measured above), and
2. `.ufo/waves/round-90/measured/reason-cells.jsonl` is re-captured against the round-99 probe
   bytes, so its `probe_sha256` matches.

Note the receipt is already stale at the round-99 freeze commit: the round-90 counter at `f6e7ccc2`
prints `bound=0 unbound=24 receipt=stale` and exits 1
(receipt `../receipts/reason-rows-at-freeze.out`), because the committed receipt's `probe_sha256`
(`1e21c1fb5d3fac1d6abc06ef1c541531e261acba36fb6678c1fb3fe9591e29c3`) belongs to an older probe than
the committed `tools/kama-probe.sh` (`40ab387ee9877a9505af61172db5fc1cd2006021fb026e761e558e307a5b4a6e`).
The round-99 lesson draft already routes that re-capture to round 100; this draft says the SKILL.md
row cannot land before it, or it lands on top of an already-red counter.

## 7. Landed state at `00394f3b` — this draft's row was NOT the shape the L1 chose, and the numbers below say why both are defensible

The L1 landed round-99 amendment 1 (`00394f3b`) while this seat was drafting. It documents
`router-autoload-unread` in a dedicated `## Round 99 unread-autoload reason` section plus a decision
row (`SKILL.md:1773`), and it **declines** a `## Probe reason codes` row, with the sentence: "a row
there cannot bind without editing the round-90 instrument" (`SKILL.md:1832-1835`). The measurement
in §5 of this draft is the arithmetic behind that sentence:

- a new row alongside a receipt that has no cell for it → `rows=25 bound=24 unbound=1`, **exit 1**;
- a new row with a new capture cell and a 25-cell receipt → `rows=25 bound=25 unbound=0`, exit 0,
  i.e. the row is landable **only** by editing `tools/round90-reason-capture.py` and re-capturing.

Since `router-autoload-unread` is outside the counter's frozen 23-reason population, leaving it out of
the table costs nothing at the counter: `additional` and `missing` only look at the population, so the
landed shape keeps `missing=0` and adds no `unbound`. The table is red at the tip either way, but for
an unrelated reason — the amendment changed `tools/kama-probe.sh`, so the round-90 receipt is stale
(`bound=0 unbound=24 receipt=stale probe_sha256=05ebee88…`, exit 1 at `00394f3b`,
`../receipts/landed-state-vs-drafts.out` section C).

So this draft is a **superseded alternative**, not a live patch: it is the shape to use *if* the
committer decides the reason table should carry the row, and it becomes cheap only after the round-100
re-capture. Its §6 note about the harness still stands either way (no `RouterUnloaded` row expects the
new reason, and the harness is green without it).

## 6. The verdict-matrix harness has no cell for the new reason either

`tests/probe-verdicts/RouterUnloaded.json` carries five rows —
`router-unloaded-no-autoload` (`/props` answering `models_autoload:false`), `router-unloaded-failed`,
`router-model-missing-autoload`, `router-model-invalid-non-gguf`, `router-model-invalid-gguf-v1` — and
**no** row whose `/props` answer cannot be read. The whole matrix is 77 rows over ten files
(`tests/probe-verdicts/*.json`), and none expects `router-autoload-unread`; the candidate probe still
passes all 77 (`tests=77 passes=77 failures=0`,
`.ufo/waves/round-99/controls/c3-harness-candidate.out`). So the new reason is graded only by
`tools/round99-autoload-states.py`'s stub cells (five at the freeze commit, eight after
amendment 1's U5/U6/U7), and the lane's own verdict-matrix harness — the
instrument that normally binds a verdict/reason pair — does not know it exists. If the committer wants
the harness to carry it, a sixth `RouterUnloaded` row with a non-JSON `/props` route and
`{"verdict": "MODEL_UNLOADED", "reason": "router-autoload-unread", "exit": 2}` is the shape that would
match; that is a `tests/` edit and this seat did not make it (no tracked file writes).
