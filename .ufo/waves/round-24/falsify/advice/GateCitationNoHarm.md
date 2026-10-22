# GateCitationNoHarm — citation-provenance pinned-clone falsification (round 24)

VERDICT: **HOLDS** (no harm found). The pinned clone at `2e254a1763a9c08aa07fc53081287f506c447d84`
reproduces the retained exact-citation count vector and exit status byte-for-byte on the
countable surface, and the round-24 documentation append did not rewrite, delete, or
re-point any pinned historical citation token or source row.

Scope: exactly one bounded measurement — `python3 tools/citation-provenance.py --json` on a
pinned scratch clone — plus the read-only static checks needed to interpret it (token
inventory, SOURCES.md cell comparison, independent digest recomputation). No other lane
suite was run. No production file was written or modified.

## Axes and results

| # | Axis | Result |
|---|---|---|
| A1 | Exact command + exit on pinned clone | PASS — exit 0, counts `required=17 docs_unreadable=0 found=17 verified=17 missing=0 mismatch=0 off_ref=0` |
| A2 | Retained expected outcome (round-20 official run) | PASS — identical count vector and exit to `.ufo/waves/round-20/runs/0957ce61/commands.json` (`citation-count`, exit 0, `expected_exit` 0) and to `.ufo/waves/round-20/falsify/advice/CitationRegistryCount.md` |
| A3 | Retained exact citations (17 registry rows) | PASS — registry unchanged base→HEAD; 17/17 tokens present in their bound doc; 17/17 independently recomputed blob SHA-256 match; all 17 cited revs are ancestors of the pinned tip |
| A4 | Docs append did not rewrite pinned historical citations | PASS — token multiset identical base→HEAD (17 = 17, no removed/changed/added token); `corpus/lessons/round-18.md` (sole token carrier) untouched in round-24; LOG.md/SCORECARD.md are pure appends (0 deletions); SOURCES.md changes confined to the mutable `used-by` cell of pre-existing rows plus 4 appended rows |
| A5 | No new unregistered citation token introduced | PASS — 0 `cite(...)` tokens in the new round-24 docs; default docs contain exactly the 17 registry-bound tokens, 0 orphans, 0 registry rows without a token |

## A1 — pinned-clone measurement (observed)

Scratch clone (no hardlinks, detached at the pinned revision), nothing in production touched:

```
git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin \
    /fast/scratch/hyaku/kama-r24/falsify/GateCitationNoHarm/lane
cd /fast/scratch/hyaku/kama-r24/falsify/GateCitationNoHarm/lane
git checkout --detach 2e254a1763a9c08aa07fc53081287f506c447d84
HEAD=2e254a1763a9c08aa07fc53081287f506c447d84   # detached, tree clean
git --version -> git version 2.56.0 ; python3 --version -> Python 3.14.8
```

Command and exit:

```
$ cd /fast/scratch/hyaku/kama-r24/falsify/GateCitationNoHarm/lane
$ TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/GateCitationNoHarm/tmp \
    python3 tools/citation-provenance.py --json
EXIT=0
counts: {"required": 17, "docs_unreadable": 0, "found": 17, "verified": 17,
         "missing": 0, "mismatch": 0, "off_ref": 0}
stderr: (empty)
```

All 17 result rows carry `"status": "ok"`, with `observed_sha256` equal to the registry
` sha256` in every row, `error: null`, and `documents` naming
`corpus/lessons/round-18.md`. Row ids: `s055-commands`, `gate-live-1`, `c2-official-stdout`,
`gate-live-checkpoint`, `r18-live-receipt-1`, `r18-validation-supplement`,
`r18-terminal-evidence`, `r18-falsify-validation`, `r18-falsify-spec`, `r18-swarm-registry`,
`r18-dispatch-95`, `r18-c2-pre-repair-json`, `r18-c1-checkpoint-exit`,
`r18-c2-checkpoint-exit`, `r18-c1-corrected-measure`, `r18-retrospective-assignments`,
`r18-c2-corrected-preofficial-json`.

## A2 — comparison with the retained expected outcome (observed vs retained)

Retained official run (read-only): `.ufo/waves/round-20/runs/0957ce61/commands.json` pins
`measured_commit 0957ce619789d13bb5779606078fa1498114d2c7`; its `citation-count` entry uses
argv `["/usr/bin/python3","/home/vgpnk/Projects/shokunin/kama-shokunin/tools/citation-provenance.py","--json"]`
with `exit 0`, `expected_exit 0`, `timed_out false`, `as_expected true`; the companion
`.ufo/waves/round-20/runs/0957ce61/citation-count.exit` reads `exit=0`. Retained advice
`.ufo/waves/round-20/falsify/advice/CitationRegistryCount.md` records the same vector
(`required=17 … verified=17 missing=0 mismatch=0 off_ref=0`, exit 0), and
`.ufo/waves/round-20/build/out/R18CitationRows/transcript.txt` records the same for the
non-`--json` argv.

| Field | Retained (round-20, measured 0957ce61) | Observed (pinned 2e254a1) | Match |
|---|---|---|---|
| exit | 0 | 0 | yes |
| required | 17 | 17 | yes |
| docs_unreadable | 0 | 0 | yes |
| found | 17 | 17 | yes |
| verified | 17 | 17 | yes |
| missing | 0 | 0 | yes |
| mismatch | 0 | 0 | yes |
| off_ref | 0 | 0 | yes |

[INFERENCE] The stdout SHA-256 recorded in the retained official run
(`1090ac150c46b3f10f75f75ce9d395e4998c9c3095ae336011763671bd546586`) is **not** directly
comparable to the pinned clone's stdout digest: the JSON embeds absolute document paths
(`…/lane/corpus/lessons/round-18.md` vs the production path), so the bytes differ by path
prefix while the counted facts are identical. Counts, not stdout bytes, are the comparable
surface here.

## A3 — retained exact citations (observed)

- `registry/required-citations.json` is byte-identical between the wave base
  `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` and the pinned tip (parsed-equal; last change is
  `33a6777`, round-20). `tools/citation-provenance.py` is also unchanged in round-24
  (sha256 `414f440728b09773345c6f1bbf4823174ecc582dcd831248c92fdc7e7ab28ed0`).
- Independent recomputation (my own `git cat-file blob <rev>:<path>` + SHA-256, and
  `git merge-base --is-ancestor <rev> origin/master`) over all 17 registry rows:
  0 digest mismatches, 0 unreadable blobs, 0 non-ancestor revs. This is a second source for
  the tool's own `observed_sha256`/`off_ref` verdicts.
- Token ↔ registry bijection at the pinned tip: 17 tokens in the default docs, 17 registry
  rows, 0 orphan tokens, 0 registry rows lacking a token, and every row's token present in
  its registry-bound `doc` (`corpus/lessons/round-18.md`).

## A4 — docs append did not rewrite pinned historical citations (observed)

Diff of the pinned range `0df800e896f6bce285a81e794ad4ae1d1e6c3a71..2e254a1`:

```
LOG.md            110 insertions, 0 deletions   (single hunk @@ -1409,0 +1410,110 @@ — tail append)
SCORECARD.md       25 insertions, 0 deletions   (single hunk @@ -1188,0 +1189,25 @@ — tail append)
corpus/SOURCES.md  12 insertions, 8 deletions
corpus/lessons/round-18.md   unchanged  (sole carrier of all 17 cite() tokens)
corpus/lessons/round-19.md   unchanged
registry/required-citations.json  unchanged
tools/citation-provenance.py      unchanged
```

- Token inventory: the multiset of `cite(<rev>, <path>, sha256=…)` triples across the five
  default docs is **identical** at base and at the pinned tip (17 = 17; zero removed, zero
  changed, zero added). No pinned historical citation was re-worded, re-pointed, or deleted.
- The 8 "deletions" in `corpus/SOURCES.md` are table-row rewrites. Cell-level comparison of
  all 101 base rows vs 105 tip rows: **no row removed**; 4 rows added (`S102`, `S103`, `S104`,
  `S105`); on every pre-existing row the **only** changed cell is column #10, the mutable
  `used-by` cell (`S083`, `S089`, `S094`, `S095`, `S096`, `S099`, `S100`, `S101` — each gains
  `corpus/lessons/round-24.md` and/or `corpus/knowledge/error-is-not-a-verdict.md`). The
  `teaches`, `anchor`, quote and status cells of every pre-existing row are byte-identical to
  base. In particular `S095` keeps its original `teaches` text and its pre-existing
  `rejected` status, and the cross-API rejection is recorded as the **new** row `S105`
  ("supersedes S095 — REJECTED: bytes.decode strict-default documentation does not establish
  subprocess text-mode or TextIOWrapper defaults") — consistent with the ledger supplement
  statement that only mutable `used-by` cells were reconciled.
- Every `used-by` path listed in `corpus/SOURCES.md` at the pinned tip exists as a path in
  the tip tree (`git cat-file -e HEAD:<path>`): 0 dangling pointers (the 13 apparent misses
  are the em-dash placeholders `—`, not paths). No new S055-class pointer drift was
  introduced by the round-24 append.
- The two new round-24 documents (`corpus/lessons/round-24.md`, 161 lines;
  `corpus/knowledge/error-is-not-a-verdict.md`, 127 lines) contain 0 `cite(...)` tokens, so
  the default-doc token set is still exactly the 17 registry-bound citations — no
  unregistered material citation was added under the tool's blind spot.

## Residual risk / caveats (observed, not a round-24 regression)

1. **The off-ref guard depends on a resolvable `origin/master` in the measured clone.**
   Measured in a second scratch clone of the same pinned revision with
   `refs/remotes/origin/master` deleted:
   `python3 tools/citation-provenance.py --json` → exit **1** with
   `required=17 docs_unreadable=0 found=17 verified=0 missing=0 mismatch=0 off_ref=17`
   (every row `"status": "off-ref"`), even though each citation is present and each blob
   digest matches. The ancestry probe (`git merge-base --is-ancestor <rev> origin/master`,
   `tools/citation-provenance.py:118-126`) fails when the remote-tracking ref is absent, and
   `check()` treats a non-zero probe result as `off_ref`. The pinned clone used for the
   headline measurement does carry `origin/master` = `2e254a1` (the clone source's master
   tip), which is why `off_ref=0`. Anyone reproducing the pinned number from a clone without
   a remote-tracking `master` (e.g. a bundle, a mirror with `remote.origin.fetch` unset, or a
   pruned `git remote prune`) will see exit 1 and must add `--allow-off-ref`. This is
   pre-existing behaviour (the tool is unchanged since round-20), not something round-24
   introduced; no correction is proposed because the guard is intentional.
   [INFERENCE] The consequence is that the checker's exit status is not purely a function of
   citation content — it also encodes the presence of a remote-tracking ref.
2. The 17-row registry and the `cite(...)` token set have been stable since round-20; this
   falsification therefore confirms *stability* of the pinned historical citations, not
   re-derivation of the round-18 evidence itself. The round-18 blobs are verified by digest
   only, not re-measured.
3. Stale historical counts remain visible in `SCORECARD.md:823-824` (`required=3 …`) and
   `SCORECARD.md:856-857` (`required=4 …`) and in `corpus/lessons/round-19.md:11`
   (`required=4 found=4 verified=4`). These are revision-bound to the 3- and 4-row registries
   of their waves and were already flagged as historical in round-20/round-21
   (`StaleCountSweep.md`, `MistakeSweep.md` R08). They are **not** rewritten by round-24 and
   are not `cite(...)` tokens, so they are outside this gate's mechanical contract; they
   remain historical prose, not current counts.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/GateCitationNoHarm.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/GateCitationNoHarm/pinned-citation-provenance.json` — pinned-clone `--json` stdout
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/GateCitationNoHarm/pinned-run.txt` — command transcript with `EXIT=0` and counts
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/GateCitationNoHarm/pinned-citation-provenance.stderr.txt` — empty stderr capture
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/GateCitationNoHarm/noref-origin-master-absent.json` — residual-risk-1 measurement (`off_ref=17`, exit 1)

Scratch (outside the repo): `/fast/scratch/hyaku/kama-r24/falsify/GateCitationNoHarm/{lane,lane-noref,tmp}`.

Production lane `production/.jj/index`, fleet, sibling lanes, operator config, routing,
services and real object stores were not touched. No network, transport or execution payload
was used; `PM08` was not executed. No tool was installed or updated (system Python 3.14.8 and
git 2.56.0 were already present).

## Unverified items

- No lane suite other than the assigned single command was executed; in particular
  `--selftest`, `tests/report-audit/promisor-grid.py`, `tests/report-audit/repo-state-grid.py`
  and the mutation grids were **not** run (out of scope for this lane).
- The checker was not exercised against a deliberately broken citation; the negative-path
  behaviour is inherited from the tool's own round-19 selftest and was not re-measured here.
- The tool's stdout digest was not compared for byte equality with the retained round-20
  official digest (absolute paths differ by construction) — see A2.
- The round-18 evidence blobs were verified by SHA-256 identity only; their content was not
  re-derived.
- The `off_ref` caveat (residual risk 1) was measured on a second scratch clone at the same
  pinned revision; it was not measured in the production checkout.

## Correction to a line citation (appended, nothing above is removed)

Residual risk 1 cites the ancestry probe as `tools/citation-provenance.py:118-126`; the correct
range at the pinned tip is `tools/citation-provenance.py:104-110` (`elif not allow_off_ref:`
→ `git -C <lane> merge-base --is-ancestor <rev> origin/master` → `status = "off-ref"`), with
the `off_ref` counter at `:122` and `DEFAULT_DOCS`/`DEFAULT_REGISTRY` at `:33-35`. The measured
behaviour quoted above is unaffected.

## Appended: promisor / lazy-fetch exposure of this lane's clones (observed)

A sibling lane (CaseFleetBlobless) reported that a blobless promisor fixture whose
`remote.origin.url` still points at a reachable origin can have missing objects silently
materialised by a stray probe, turning a correct exit-2 refusal into a false clean exit 0.
Checked against both scratch clones used here:

```
lane      promisor=NONE  extensions.partialClone=NONE
lane-noref promisor=NONE extensions.partialClone=NONE
remote.origin.url = /home/vgpnk/Projects/shokunin/kama-shokunin   (local path, not a fetchable promisor)
count-objects -v: count 1498 loose, in-pack 5857, packs 3, size-pack 12218
```

Both clones are **full** (no promisor config, no partial-clone extension), so no probe in this
lane could materialise a missing object: the 17 cited blobs were already local, `git cat-file
blob` read them out of the local packs, and `verified=17` reflects bytes that were present
before the run, not bytes fetched during it. No `--no-lazy-fetch` flag was needed here and no
network or transport was used. [INFERENCE] The hazard therefore does not apply to this
measurement; it would apply to any reproduction that builds the pinned clone as a blobless
promisor clone.

Report: .ufo/waves/round-24/falsify/advice/GateCitationNoHarm.md
