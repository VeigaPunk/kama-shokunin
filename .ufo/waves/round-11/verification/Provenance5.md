# Provenance5 — `endpoint-identity.md` provenance supplement (round 11, advisory)

Seat: `KamaR11.Provenance5` (leaf verifier). Target: the appended
`## Provenance supplement — round 11 (2026-10-19)` block (`corpus/knowledge/endpoint-identity.md:149-164`),
its retained historical context (lines 1-147), and `corpus/QUALITY.md` KQ11 (line 38).
Parent owns measurement, integration and acceptance; nothing here is a runtime or
acceptance verdict. All paths are relative to `/home/vgpnk/Projects/shokunin/kama-shokunin/`.

Axis named: **operability** (the document survives re-reading without false currency)
and **calibration** (historical evidence is dated, not refreshed). No score or
denominator assertion is made.

Method: read-only. File reads, `grep`, `git log`/`git status`, `stat`. No
`measure.py`, no `kama-probe` invocation, no build/lint/test/formatter, no
endpoint/socket/service contact. One public documentation URL was opened to
verify the newly appended S001 claim (recorded below; allowed by contract).

## Verdict

The supplement's own trio is **honest**: source, observation date, review date and
review/live separation all check out, and all three fields the legacy baseline
recorded as missing are now present. The original prefix is append-only at the
locations I compared. However, the supplement (a) names a recheck that revives
obsolete config-body reads — the exact KQ11 reject case — and (b) asserts F1-F12
as source without reconciling two body attributions that the frozen citation rows
themselves contradict. Findings below, highest impact first.

## Findings

### P5-1 — HIGH (KQ11 reject clause): recheck revives obsolete config-body reads

`corpus/knowledge/endpoint-identity.md:153` ends the recheck with:

> for the historical F1–F12 facts, re-open `corpus/lessons/round-1-citations.md` rows F1–F12 and re-derive at the recorded commands (host commands require authorization).

The recorded commands include operator config-body reads: F6 (`corpus/lessons/round-1-citations.md:12`,
`nl -ba ~/.config/opencode/opencode.json | grep ...`), F7 (`:13`, `~/.config/opencode/agents/janitor.md`),
F11 (`:17`, `~/.omp/agent/config.yml`), and F12 (`:18`, fleet report bodies). F6 is
already declared obsolete **in this same file**: A06 (`:143`) records
`wc -l ~/.config/opencode/opencode.json => 5` and that the claimed live pins are
historical; `corpus/knowledge/consumer-registry.md:378-380` (A19/A20) repeats the
point. KQ11's reject column is literal: "an obsolete config-body read is revived as
a current recheck."

Smallest repair (line 153 lies outside the frozen prefix, so no byte control is
touched): scope the clause to read-only host-shape probes (F1-F3, F8-F10) under
authorization, and state that F6/F7/F11/F12 body reads stay historical and are not
re-run; or replace the blanket clause with "re-open rows F1-F12 as history; do not
re-read operator config or report bodies (A06/A19/A20)."

### P5-2 — MEDIUM (source honesty): `docker-proxy` ownership is not supported by F1/F2

`:78` says `127.0.0.1:8080` "was owned by `docker-proxy` and mapped to the Jitsi JVB
container (F1, F2)"; `:121` repeats "had a live `docker-proxy` listener mapped to
Jitsi (F1, F2, F3)". The cited frozen rows say otherwise: F1
(`corpus/lessons/round-1-citations.md:7`) is **PARTIAL** — `ss` exposed no owner for
8080 — and F2's corrected detail (`:8`) says the command "names the container, not
the host-side `docker-proxy` process."

Smallest repair: append a dated correction (append-only, preserving :78/:121):
"8080 was a Docker-published Jitsi JVB mapping (F2); host-side proxy ownership was
not established (F1 PARTIAL)."

### P5-3 — MEDIUM-LOW (source honesty): the F3 "recorded POST" does not exist in F3

`:74` states "The recorded chat-completions POST to `8080` also returned Jetty HTML
404 (F3)." F3 (`corpus/lessons/round-1-citations.md:9`) records `curl -sSI` (HEAD)
and a GET of `/` only; no POST or chat-completions request appears in the row.

Smallest repair: appended correction dropping the POST claim, or cite the artifact
that actually recorded it.

### P5-4 — LOW (citation thinness): F4 does not record the header or `data[]`

`:63` attributes "`Server: llama.cpp` plus both `models[]` and `data[]` arrays
(F4)"; `:80` likewise. F4 (`corpus/lessons/round-1-citations.md:10`) records only
`models[0].name`. The claim is plausible but thinner than its citation.

Smallest repair: cite the raw response artifact, or narrow the wording to the
recorded `models[0].name`.

### P5-5 — LOW (temporal overclaim control): "Fresh" remains an undated present-tense label

`:23` reads "Fresh loopback smoke output excerpt:" and `:65` instructs that the
port-confusion signature "can be inspected" (present tense); A01-A08 (`:133-147`)
do not cover either line. The supplement dates all original observations to
2026-09-28 (`:152`), which mitigates at file scope, but a literal claim that the
file contains "no runtime freshness claim" is not true of the retained bytes.

Smallest repair: append a dating correction ("line 23 'Fresh' refers to the
2026-09-28 round-1 sample; 34113/8080 have no listener per A08 and
`SKILL.md:44-47`"), or state the wave claim as "the supplements make no runtime
freshness claim; legacy prefixes retain historical 'Fresh' labels now dated at
file scope."

### P5-6 — LOW (trio source coverage): readiness correction's sources are not in `source:`

The newly appended `### Readiness terminology correction — round 11` (`:155-164`)
relies on `S001` and `S011/S012`, but `:151` enumerates only F1-F12, retained
artifacts, the contract artifacts and the round-10 corrections block; it does not
name `corpus/SOURCES.md` rows S001 (`:13`), S011 (`:23`), S012 (`:24`). The claim
itself is true (verified below), so this is traceability, not falsehood.

Smallest repair: append to `:151` "and `corpus/SOURCES.md` S001 (§GET `/v1/models`
@ c0fd786), S011, S012".

### P5-7 — LOW (date labeling): mixed 10-19/10-20 labels

`:149` heads round 11 as `(2026-10-19)`; `:152` says review `2026-10-20T02:14Z`;
`:155` says `(2026-10-20 UTC)`; KQ11 says "reviewed 2026-10-20 UTC". 02:14Z is
23:14 -0300 on 10-19 and the file mtime is `2026-10-19 23:19:30 -0300`, so the
heading date is defensible, but the mixed labels invite the temporal confusion
KQ11 polices. Smallest repair: add `-0300` to `:149`, or use UTC in both headings.

## What is already correct (grounded)

- **Append-only prefix.** `.ufo/waves/round-11/frozen/before/corpus/knowledge/endpoint-identity.md`
  ends at A08; current `:147` is that same A08 line and `:149` begins the supplement.
  Sampled lines `:5`, `:23`, `:89`, `:122`, `:127`, `:128`, `:147` are identical in
  frozen and current. Baseline records sha256 `068fe659…`, 19263 bytes
  (`.ufo/waves/round-11/legacy-baseline.json`); current file is 21752 bytes. The
  byte/hash equality and mutation controls remain **parent measurement**; I did not
  run them.
- **Trio present once, at column zero.** `:151-153` supply `source:`, `verified-at:`,
  `recheck:`; the baseline lists all three as previously missing for this file.
- **Dates are accurate.** `listener-census.md` header says measured
  `2026-09-28 ~22:47–22:52 -0300`, matching `:151`. `git log` shows the file at
  `c6199a2` (2026-09-28T23:15:05-03:00), `47f3aed` (2026-10-14T21:23:34-03:00,
  round 4) and `1e41928` (2026-10-19T19:34:42-03:00, round 10), exactly the
  revisions `:152` names. `consumer-registry.md` has its 2026-10-14 errata (`:30`)
  and round-10 corrections (`:376`); `SKILL.md` was last touched by the round-10
  commit; `corpus/lessons/round-1-citations.md` holds 12 rows F1-F12 and its stated
  method (live-box audit, reduced output) supports "retained/re-derived."
- **Metadata vs live is explicit.** `:152` states the review was metadata only and
  that "no endpoint, socket or service was contacted"; `:153` states round 11 ran no
  census. No round-11 JSON artifact contains endpoint census output (the only
  census-named files are `sources-census-before.json` / `sources-validate-before.json`,
  which census `SOURCES.md` rows). This is artifact-level support, not proof of
  process history.
- **Recheck is bounded and credential-free.** `tools/kama-probe.sh check --json` is
  the registry-row reconciliation gate (`tools/kama-probe.sh:18-19`); `classify`
  fetches `GET /v1/models` (`:411-418`); the registry has three rows, all
  `127.0.0.1` (`registry/endpoint-consumers.tsv`); the script contains no
  `Authorization`/`API_KEY`/`Bearer` match. `listeners|consumers|check|snapshot` all
  exist (`:88-93`). Historical host commands are gated by "require authorization."
- **Readiness correction is substantiated.** Opening the pinned public README
  (https://raw.githubusercontent.com/ggml-org/llama.cpp/c0fd78626405c6d9b934efef0ec7291fcc20e3d6/tools/server/README.md,
  accessed 2026-10-20), §GET `/v1/models`: OpenAI-compatible Model Info API, line
  1256: "The `meta` field can be `null` (for example, while the model is still
  loading)." (17 words.) `SOURCES.md` S001 pins that commit and lists §GET
  `/v1/models`; S011/S012 rows separate available inventory from loaded/running
  state. The correction's separate-propositions conclusion is consistent with KQ13.
- **Line-89 anchor resolves.** `:89` is the "Identity readiness" row the correction
  quotes; the correction is appended, so KQ7's no-mid-file-insertion rule holds.
- **"Unchanged implementation" is supported at working-tree level:** `git status`
  shows only `corpus/knowledge/endpoint-identity.md` modified among the files this
  seat checked; `tools/kama-probe.sh` and `registry/endpoint-consumers.tsv` are not
  modified in this wave.

## Risks / handoff

- P5-2/P5-3/P5-4 are body-vs-citation defects the supplement does **not** create,
  but its claim to name F1-F12 as source leaves them standing; parent decides
  whether they enter this wave's integration or a later correction round. All three
  repairs are append-only and preserve the frozen prefix.
- P5-1 is the only finding that bears directly on KQ11 admission of this file.
- This report is author-side advisory (KQ11 review boundary); it is not an outside
  non-author verdict. Concurrent seats were writing sibling reports while I read;
  nothing I read was modified by me.

## Installs and checks

- **Installs/updates: none.** No tool was installed or upgraded; no install record to
  make. No `pacman`/`uv`/`npm`/`cargo` command ran.
- **Checks run: none.** No `measure.py`, no `kama-probe`, no digest/diff, no
  build/lint/test/formatter. Only reads, `grep`, `git log`, `git status`, `stat`,
  and one read-only public documentation fetch for S001.
