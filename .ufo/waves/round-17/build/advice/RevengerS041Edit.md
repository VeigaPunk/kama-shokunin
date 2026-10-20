VERDICT: confirm — S041's `anchor` and `teaches` cells were rewritten in place at `ccc4bb31` after first commit `b8e485c`; contract rule 2 was available and required a superseding row.

# Seat: RevengerS041Edit (round-17 BUILD, revenger)

Read-only reconstruction of `corpus/SOURCES.md` history, bounded to S041. No
lane gate, measurement or mutant run was executed; the only command run outside
git reads was one read-only invocation of another seat's in-flight guard (see
"Captured-by", recorded as an observation, not a verdict).

## 1. What changed, exactly

S041 lives at `corpus/SOURCES.md:53` (13 `awk` fields = 11 columns) at both
`b8e485c` and `ccc4bb31`. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin
diff b8e485c ccc4bb31 -- corpus/SOURCES.md` is a single replaced line
(`@@ -50,7 +50,7 @@`); no other row moved, no row was added or removed, no field count changed.

Two of eleven cells changed, both outside the contract's mutable set:

- **`anchor`** — old: `receipt `kama-llamacpp-live/v1` 2026-10-20T13:49:38.040Z–13:49:38.170Z, port 32845, 10 checks`
  (grep of `git show b8e485c:corpus/SOURCES.md`). New: `receipt `kama-llamacpp-live/v1` 2026-10-20T14:06:27.859Z–14:06:27.974Z, port 37527, tool sha256 b8c5e8d4…, 10 checks`
  (`corpus/SOURCES.md:53`). Run identity, port and a new tool digest replaced.
- **`teaches`** — the new clause `answers `/v1/models` 503 with the exact loading envelope while loading, then `/health` 200`
  (`corpus/SOURCES.md:53`) is an added claim, not a restatement: the `b8e485c`
  cell asserted only ready-state facts (`/health` 200, `id` = alias,
  `owned_by` `llamacpp`, `/metrics` 501).

Unchanged: `id`, `source`, `kind` (own-work), `tier` (A), `scope`, `status`
(mined), `opened`, `recheck`, `used-by`. `source` still names the same mutable
path `.ufo/waves/round-16/live/receipt.json`, so the row's identity cannot
distinguish the two runs — only the rewritten `anchor` did.

The cited artefact at that path was replaced in the same commit: receipt blob
`75779e34c76572ce1aae19fe3d4ec2220c4be217` (sha256 `6fb32c05…5eeb`) at
`b8e485c`/`726f737a` → `1e4fb8232dd331a7507421da2739ed41a561f95f` (sha256
`076865e5…4669`) at `ccc4bb31`; `live/receipt-frozen-probe.json` was regenerated
alongside it (93 changed lines) and `corpus/knowledge/llamacpp-loading-lifecycle.md`
was rewritten (64+/38−), gaining the live loading bullet at
`corpus/knowledge/llamacpp-loading-lifecycle.md:116-125`. So the registry row,
the artefact it cites, and the knowledge entry citing the row were all refreshed
as one re-evidence. Of the three, only the artefact's bytes are not governed by
rule 2 [INFERENCE: the contract freezes registry cells, not evidence artifacts;
the artefact swap is what made the row's stale cells look like a refresh].

## 2. Why — receipt regeneration

Three commits, in order:

1. **`b8e485c`** (2026-10-20 10:50:42 −03:00) — row created; cited receipt ran
   `13:49:38.040Z–13:49:38.170Z` on port 32845. That receipt records
   `loading_observed false`, `loading_503 null`, `loading_envelope_exact null`,
   and pins probe sha `6edd3c4c…`; it has no `tool` block. The tool that wrote it
   hashed `cf95f382032d9c51…ef39ea`.
2. **`726f737a`** (11:10:32) — harness hardened (187+/98−; sha becomes
   `b8c5e8d4…`), probe replaced (`6edd3c4c` → `36b64978`), `check-receipt.py`
   rewritten (205 changed lines), SOURCES gained 23 lines of wave notes. The receipt blob
   did not change, so between `726f737a` and `ccc4bb31` the committed row cited a
   receipt that the committed tool could no longer reproduce: the in-receipt
   probe pin `6edd3c4c…` no longer matched committed `tools/kama-probe.sh`
   (`36b64978…`), and no tool digest was recorded to detect the split.
3. **`ccc4bb31`** (11:15:00) — new run at `14:06:27.859Z–14:06:27.974Z`, port
   37527, with the hardened tool (`tool.sha256 b8c5e8d4…`) and current probe
   (`36b64978…`): `loading_observed true`, `loading_envelope_exact true`,
   `loading_503` body `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`.
   The row was then edited to match.

Why the first run could not see the window, and the second could — the harness
itself says it. Pre-hardening loop: `Poll /health and /v1/models alternately from t=0.`
(`git show b8e485c:tools/kama-llamacpp-live.py`, `readiness_loop` docstring) with
a per-iteration sleep; hardened loop: `the ~5-6 ms loading window needs an unbroken request cadence`
(`tools/kama-llamacpp-live.py:441`). The falsify seat had already established the
window was observable: `the live 503 "Loading model" window is real and easily capturable`
(`.ufo/waves/round-16/falsify/advice/ExecLoadingWindowCapture.md:1`). The closure
commit message names the motive: `record measured C1/C2 results, falsify-wave dispositions and live loading capture`
(`git show -s --format=%s ccc4bb31`).

[INFERENCE] The author treated row and artefact as one document: a regenerated
receipt was seen as a refresh of the same source, and the newly observed loading
envelope was folded into the same row. Nothing indicates an intent to hide the
change — it is disclosed (see §4) — only that rule 2 was read as a logging
formality rather than as a prohibition.

## 3. Which rule/criterion was available at the time

**The rule was available, frozen, and sufficient.** `/home/vgpnk/Projects/shokunin/CORPUS.md:116-117`
(`## SOURCES.md — where a shokunin learns`, contract v1, kaika 2026-10-19, carried
in full from `.ufo/waves/kaika/SOURCES-CONTRACT-v1.md`) states:

> Only `status`, `recheck` and `used-by` change in place, and each change is logged old→new in the round lesson.

> A correction is a new row whose `teaches` opens `supersedes S0NN —`.

`anchor` and `teaches` are not in that set, and the contract carries no
same-round exception — `b8e485c` is the row's first commit, which is exactly the
state rule 2 protects. The contract-prescribed move was a new row (S042,
`teaches` opening `supersedes S041 —`) carrying the 14:06 receipt and the loading
observation, or retaining S041's cells and citing the new run from the knowledge
entry.

**The nearest QUALITY.md criterion was also available, but is a different
instrument.** `corpus/QUALITY.md:29` KQ7 rejects a round when
`a dated line is rewritten` (full reject cell: `Any ledger row stays uncorrected, a dated line is rewritten, or a mid-file insertion shifts other files' line anchors.`),
and `corpus/QUALITY.md:41` KQ14 `preserves its append-only rule`. Both point the
right way; neither names `SOURCES.md` registry cells, and no KQ row makes cell
immutability gradable — which is why KQ22 is being drafted this round
(`.ufo/waves/round-17/build/make_spec.py:240`: `registry cells other than status/recheck/used-by never change after a row's first commit`).

**The criterion that created the pressure did not require the edit.**
`corpus/QUALITY.md:109` KQ19 (round 16) admits a `MODEL_LOADING` verdict when it
`is shown by a literal stub matrix run through the probe CLI`; its evidence is
`run-before.json` / `run-after.json`, not S041. The loading claim was already
carried by S035–S037, and S041's `used-by` path did not change, so the row
amendment added live support the criterion never demanded.

## 4. What the author recorded, and what that record omits

- `corpus/lessons/round-16.md:147-149` is the only disclosure:
  `S041's anchor and teaches cells were amended before closure because the receipt file was regenerated`
  (sentence continues "; the row was first committed this round (`b8e485c`)").
  It explains the cause but does not log the old→new cell text, and it offers the
  same-round-first-commit fact as the justification rather than as the violation
  it is.
- `corpus/lessons/round-16.md:58` records `Row changes: new S035–S041; S017 used-by`
  and `corpus/lessons/round-16.md:60-61` `No status or recheck cell of an existing row changed.` — literally
  true, but silent on new-row cell rewrites.
- `corpus/SOURCES.md:129` still asserts `Round-16 falsify-wave notes on S035–S041 (2026-10-20; no cell changes).`
  True of commit `726f737a`; in the final file that note sits 76 lines below the
  row it no longer describes [INFERENCE: a reader taking the note as round-scoped
  is misled about S041's stability].

## 5. Captured-by

**Actually caught by** a non-author history read, not a gate:
`corpus/lessons/round-16-verifier-spotcheck.md:184` (routed defect 3) —
`S041's anchor and teaches cells were amended after the row's first commit in `b8e485c` (disclosed).`
followed by `Contract rule 2 lets only `status`/`recheck`/`used-by` change in place, so a later receipt regeneration must take a superseding row.`
That is prose, written after closure, with no exit code.

**The round-16 gate structurally could not see it:**

- Nothing read `SOURCES.md` as a diff: `grep -rln --exclude-dir=.git --exclude-dir=.jj SOURCES tools/ scripts/`
  returns no file, and this lane has no `scripts/` directory (`ls -d scripts` → no such file).
- The census the contract ships checks shape, enums, duplicates, tier inflation
  and `used-by` existence only (`/home/vgpnk/Projects/shokunin/CORPUS.md:131-148`);
  a cell rewrite passes all of it. The recorded round-16 runs confirm this:
  `.ufo/waves/round-16/sources-final-census.txt` is counts only and
  `sources-final-validate.txt` reports `kama` `ok` with `exit=0`.
- `acceptance.json`'s `touched` list cannot name a new row's rewrite: it records
  `rows_before 34` / `rows_after 41` and `.ufo/waves/round-16/acceptance.json:93`
  shows `"touched": [` with only `S017 used-by`, while the same commit `ccc4bb31`
  rewrote S041 [INFERENCE: no generating script exists in the lane; the block is
  consistent with a pre-round-base comparison, under which S041 is only `added`].

**Fail-capable capture now exists in spec, not yet in runnable form:**
`.ufo/waves/round-17/build/make_spec.py:112` defines `Fail-capable guard for SOURCES contract rule 2`,
`tools/sources-append-only.py`, whose contract is `--from REV --to REV` over the
registry with `{status, recheck, used-by}` as the only mutable set. The intended
ledger line is `--from b8e485c --to ccc4bb31`, which must report S041's `anchor`
and `teaches` old→new and exit 1. At read time (2026-10-20T15:19:23Z) the file
exists (`sha256 e28ab320579c2f6ffe629c0b68ea7a1f639e3e8e160a123d85da23d279fb5734`)
but aborts before grading with `TypeError: unsupported operand type(s) for |: 'tuple' and 'frozenset'`
at `tools/sources-append-only.py:156`, so today's capture is still the spotcheck
paragraph. Owner notified (`KamaR17.SourcesAppendOnly-2`).

## 6. Output for the Mistakes table

| Class | Evidence pointer | Captured-by |
|---|---|---|
| append-only registry violation: `anchor` and `teaches` of a committed own-work row rewritten in place to absorb a regenerated artefact and a newly observed state, where rule 2 required a superseding row (`supersedes S041 —`) | `corpus/SOURCES.md:53` diff `b8e485c`→`ccc4bb31` (one line; `git diff b8e485c ccc4bb31 -- corpus/SOURCES.md`); artefact supersession `.ufo/waves/round-16/live/receipt.json` blob `75779e34…` → `1e4fb823…`; only disclosure `corpus/lessons/round-16.md:147-149`; rule `/home/vgpnk/Projects/shokunin/CORPUS.md:116-117` | non-author spotcheck `corpus/lessons/round-16-verifier-spotcheck.md:184` (routed defect 3, no exit code); fail-capable: `tools/sources-append-only.py --from b8e485c --to ccc4bb31` (spec `.ufo/waves/round-17/build/make_spec.py:112`) — not yet executable at read time, `TypeError` at line 156 |

Related contributing defect, if a second row is wanted: **mutable-path evidence
identity** — S041's `source` cell cites a path and a command, so when the round
overwrites that path the row can only stay truthful by rewriting its immutable
cells; [INFERENCE] a digest in an immutable cell (or a per-run path) would have
made the regeneration visible without touching S041.

## 7. Limitations

- Scope is exactly one row. Whether other rows were rewritten in place is the
  `SourcesHistoryRule2` seat's sweep; I did not duplicate it.
- Intent is inferred from `round-16.md:147` and the commit messages; no author
  statement beyond those was read.
- The guard observation is a snapshot of a sibling's in-flight file; it may be
  repaired after 2026-10-20T15:19:23Z.
- I did not run `measure.py`, the matrix, the controls or any lane gate, and did
  not touch `jj` or git writes.

## 8. Installs

None. No package, tool or upgrade was installed or changed.
