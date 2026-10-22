# CritNoTrade — r24 falsify: outside-closure workflow and blobless locally-sufficient shape

Seat: KamaR23-2.CritNoTrade-3 · critic (leaf) · git 2.56.0 · 2026-10-21
Candidate: `2e254a1763a9c08aa07fc53081287f506c447d84` (scratch-only detached checkout at
`/fast/scratch/hyaku/kama-r24/falsify/CritNoTrade/src`, cloned `--no-hardlinks`, HEAD observed
exactly `2e254a17…`). The source tool's sha256 is
`ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220`, matching the pin. The runner
`tests/report-audit/promisor-grid.py` has sha256
`b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa`, also matching (not run).
The frozen r23 arm is `0df800e8:tools/report-landing-audit.py`, sha256 `da5041a8…65af1`.
Lane source is the real `/home/vgpnk/Projects/shokunin/kama-shokunin` at `2e254a17`. Fleet
source is the real `/home/vgpnk/Projects/shokunin` at
`061fe1706a9401d33fa3a00734858a83a05cfe07`. Both were read-only clone sources; neither was
configured or written.

## Verdict: HOLDS

The outside-closure workflow is restored with no metadata refusal, and it produces exact
full-clone output. The setup is a real lane plus a real fleet, rounds 10–22, ordinary errata
from the lane tip. The ordinary errata include the round-20 splice
`0957ce619789d13d894ef21bc863486bcb35b56c`, a hash that no audited store can resolve.

The test covered every lane × fleet combination of three shapes:

- **full**: an ordinary full clone;
- **pc**: complete promisor-marked (the server ignored the filter, so all objects are local but
  the promisor config and marker are present);
- **bl**: honored `blob:none` (405 lane and 1,025 fleet historical blobs missing, 0 missing
  trees or commits).

Results:

- **Matching output.** All 9 combinations give byte-identical JSON after path normalization:
  - with errata, sha256 prefix `6133c5677be60cba`, exit 0, `clean`;
  - with `--no-errata`, prefix `bdecdcbb2edbc0a7`, exit 1, `failed`.
- **Same summary everywhere:** 13 reports, 54 required commits, 9 defects with 9 corrected
  (0 corrected with `--no-errata`), 0 unmatched, 0 invalid. stderr is empty in all 18 runs.
- **Same 9 finding IDs:**
  - `r10:landed-omitted:40660352…`;
  - `r18:landed-omitted` for `101f3991…`, `1c325b2e…` and `c6dc46fa…`;
  - `r20:landed-omitted` for `0957ce61…bb57…`, `33a67778…`, `846e366d…` and `92b14625…`;
  - `r20:unresolved-full-hash:0957ce619789d13d894ef21bc863486bcb35b56c`.
- **No lazy fetch.** The trap (`remote.origin.uploadpack`, set in scratch clones only) never
  fired. After the runs the blobless clones were still missing 405 and 1,025 objects.
- **Unused historical blobs are not a precondition.** The unresolved splice token forces the
  store-wide missing-object diagnosis to run over 405 and 1,025 missing blobs, and it does not
  refuse. There is no blanket completion precondition.

No falsifying counterexample was found within this scope. There is one minor, fixable
reason-text inconsistency (finding 5 below); it is not a verdict harm.

## Measurements (command → exit → finding)

`$S` = `/fast/scratch/hyaku/kama-r24/falsify/CritNoTrade`. Every subprocess ran with
`TMPDIR=$S/tmp`. Fixtures were built with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`.

1. **Matrix, candidate.** Command: `python3 $S/matrix.py`. For each cell it runs
   `python3 src/tools/report-landing-audit.py --lane-repo fx/lane-{full,pc,bl}
   --fleet-repo fx/fleet-{full,pc,bl} --rounds 10-22 --json [--no-errata]`.
   - Result: 9/9 exit 0 with errata, 9/9 exit 1 without. All normalized hashes equal
     `full-full`. Each run took 0.25–0.56 s.
   - `matrix.json` holds per-cell exit, timing, summary and finding IDs.
2. **Frozen r23 contrast.** Command:
   `python3 frozen-r23.py --lane-repo fx/lane-L --fleet-repo fx/fleet-F --rounds 10-22 --json`.

   | Lane × fleet | Exit | Message |
   |---|---|---|
   | full × full | 0 | — |
   | pc × pc | 2 | `partial clone (promisor pack)` |
   | bl × bl | 2 | `partial clone (promisor pack)` |
   | pc × full | 2 | `partial clone (promisor pack)` |
   | full × bl | 2 | `partial clone (promisor pack)` |

   The candidate removes exactly that metadata refusal and restores the full-clone verdict.
3. **Lazy-fetch trap positive control.** Command: `git -C fx/lane-bl cat-file -t 0e006fca…`,
   with no `--no-lazy-fetch`.
   - Result: exit 128 and the marker `LAZY-FETCH-RAN` was created, so the trap is live. The
     marker was removed; after every later run it stayed absent.
4. **Blobless `--no-checkout` (actually required blobs unavailable).**
   - Lane `nc` (4,956 blobs missing, 0 non-blob) × fleet full: exit 2,
     `unavailable required object: 2e254a17…:corpus/SOURCES.md (f8019375…)`.
   - Lane full × fleet `nc` (4,333 blobs missing): exit 2,
     `unavailable required object: .ufo/reports/round-10/kama.md at fleet HEAD (tip tree 5c0cea5c…)`.
   - With `SOURCES.md` hydrated only: exit 2,
     `round 12: unknown: unavailable required object: 7de13606… is referenced by the history of
     …lane-nc but the repository cannot serve it`. `7de13606…` is a tip blob cited as a full hash
     in round 12, and the full twin resolves it, so this is the correct cited-unavailable refusal,
     not a guessed absence.
5. **Every tip blob hydrated except `registry/report-landing-errata.tsv` (`90d84c9d…`).** Lane
   `nc` is then still missing 406 historical blobs and 0 non-blobs.
   - Without errata: exit 1, byte-identical to `full-full --no-errata` (`bdecdcbb2edbc0a7`). This
     shape is locally sufficient with unused historical blobs missing, and it is not refused.
   - With errata: exit 2,
     `git show 2e254a17…:registry/report-landing-errata.tsv in …: rc=128 fatal: bad object …`.
     The outcome is correct (CNE2, not a guessed empty ledger). However, this is the only required
     read without the `unavailable required object:` prefix: `load_errata`
     (`tools/report-landing-audit.py:539`) is not wrapped by `required_read`.
6. **Real-lane `tree:0` (opaque holes; 105 missing, all non-blob) × fleet full.**
   - `--rounds 10-19`: exit 0, identical to the full twin (`e0d2894af7903ab7`: 10 reports, 33
     required commits, 4 defects with 4 corrected). A missing tree with no unresolved token does
     not block.
   - `--rounds 10-22`: exit 2,
     `round 20: unknown: unavailable required object: 0957ce61…d894… could be hidden behind the
     missing tree or commit 00ef375c… in …lane-t0`. This is consistent with supplement-2: an
     opaque missing tree plus an actually unresolved token gives CNE2.
7. **Static floor check.** `grep -n "print-info|missing-only|allow-promisor|allow-any|exclude-promisor"`
   over the tool returns exit 1, no match. Only `--missing=print`, `--filter=blob:none` and
   `--no-lazy-fetch` are used, so the Git ≥ 2.45 floor is not raised.

## Observed vs inferred

- **Observed:** everything above, on git 2.56.0 only.
- **[INFERENCE]** The trap proves only that no fetch went through
  `remote.origin.uploadpack`/file transport. The `--no-lazy-fetch` flag on every `git()` call
  (lines 138 and 162) is the structural guarantee.
- **Tradeoff, not a defect.** Row 6 (rounds 10–22) is a declared loss against the r22 auditor:
  r22 would lazy-fetch, while the candidate must refuse because the unresolved round-20 splice
  could be hidden behind a missing tree. Per supplement-2 and the amendment this is required, and
  it must stay reported as fetch-dependent, never as "unchanged".

## Fixture-premise recheck (CaseFleetBlobless IRC hazard: a stray probe that lazy-fetches erases the missing-object premise)

Every partial clone here had `remote.origin.uploadpack=$S/trap.sh` set before any audit. That
trap exits 1 and leaves a marker. The `pc`/`bl` clones also had `remote.origin.url` repointed to
`file:///nonexistent-*`. The `nc`/`t0` clones keep the real URL; the trap still intercepts them
[INFERENCE from the trap's positive control].

Every inspection probe used `--no-lazy-fetch`. The only unprotected probe was the deliberate
positive control (row 3); the trap made it fail with exit 128, so no blob was fetched.

The post-measurement recount used `--no-lazy-fetch` only:

| Clone | Missing objects | Missing non-blobs |
|---|---|---|
| `lane-bl` | 405 | 0 |
| `fleet-bl` | 1,025 | 0 |
| `fleet-nc` | 4,333 | 0 |
| `lane-t0` | 105 | 105 |
| `lane-nc` | 406 | 0 |

`lane-nc` dropped from 4,956 only through the deliberate `unpack-objects` hydration in rows 4–5.
The `LAZY-FETCH-RAN` marker is absent. Every premise held for the whole measurement.

## Smallest safe correction (optional, reason text only)

Wrap the tip errata read the same way `load_source_urls` wraps its read:

```python
try:
    text = git(lane_repo, "show", f"{tip}:{ERRATA}")
except EvalError as exc:
    tree = root_tree(lane_repo, tip)
    what = (f"{tip}:{ERRATA} (tip tree {tree}) in {lane_repo}" if tree
            else f"{tip}:{ERRATA} in {lane_repo}")
    raise required_read(what, exc) from exc
return parse_errata(text, f"{args.branch}:{ERRATA}")
```

This changes no exit code or verdict. It only makes the reason class `unavailable` uniform for
every required read. Production was not edited.

## Impacted axes

- **Operability:** restored for the outside-closure workflow, with no harm observed.
- **Calibration:** exit 2 appears only for actually required unavailable objects, or for an
  unresolved token behind an opaque hole.
- **Discernment:** declare row 6 as fetch-dependent.
- **No new serving capability and no higher numeric score are implied.** The inherited
  Git ≥ 2.45 prerequisite remains open at L0.

## Files written

All files are under
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CritNoTrade/`:

| File | sha256 | Contents |
|---|---|---|
| `matrix.json` | `76e61aad…093a` | — |
| `matrix.py` | `5dbef9c3…81d1` | — |
| `trap.sh` | `30dc936a…2d6f` | — |
| `run-outputs.tgz` | `a2e5bc10…c1f8` | all JSON and stderr from rows 1, 2 and 4–6 |

Scratch fixtures remain under `$S/fx`: lane and fleet in `full`, `pc` and `bl` shapes, plus lane
`nc` (`--no-checkout` blobless, later hydrated as in rows 4–5), fleet `nc` and lane `t0`. They
are mine only.

## Unverified

- Git 2.45–2.55 behaviour.
- `promisor-grid.py`, `--selftest`, mutation runs and the full grid; none were run, by design.
- Fleet shapes with opaque holes.
- Non-file transports.
- PM08, which was not executed.

Tool installs/updates: none. `/usr/bin/time` was absent, so Python's monotonic clock was used
instead.
