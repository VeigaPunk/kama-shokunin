# CaseMissingLaneBlob — offline oracle case: required lane SOURCES blob absent ⇒ exit 2 (CNE), never an exemption

Seat: `KamaR23-2.CaseMissingLaneBlob-2` (reviewer, leaf). Round 24, base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`.
Auditor under observation: `tools/report-landing-audit.py`, sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1`
(byte-identical to `git show 0df800e:tools/report-landing-audit.py`; lane HEAD `d1b9d956a0beda9ac32a1a2cf6ced875faeada0d`
adds only the round-24 preregistration). Host: git 2.56.0, Python 3.14.8.
Scratch: `/fast/scratch/hyaku/kama-r24/CaseMissingLaneBlob/{repo,fixture}`.

## Verdict

**Case specified, constructed and measured; the expectation is fixed before any candidate exists.**
The treatment arm must exit **2 (could-not-evaluate)**. The r23 base already exits 2 for it, but for the
*wrong* reason (metadata refusal at `tools/report-landing-audit.py:457`), so the base exit code does **not**
discriminate the repair. The arm that does is `probe_metadata_stripped` (promisor metadata removed, blob still
missing): there the **only** possible reason is the missing object, and the base already answers exit 2 with the
content reason (`tools/report-landing-audit.py:268` → `EvalError` → `main` exit 2, `tools/report-landing-audit.py:948-950`).
The failure mode this case exists to catch is the **exemption**: an unreadable *committed* registry treated as the
legacy "no registry" case (`tools/report-landing-audit.py:259,262` → `source_urls = None`), which yields
exit 1 with a false `unresolved-full-hash` (`tools/report-landing-audit.py:283-300`) or exit 0 with a false clean.
Both signatures are reproduced and labelled below.

## The case

One lane repository, promisor-marked, whose **committed `corpus/SOURCES.md` blob object is absent from the local
object store** (a `blob:none` clone that was never fetched). The registry is *committed* (the tree names it), so
the evidence is **required**; it is simply not readable offline.

Fixture (deterministic; all timestamps fixed):

| item | value |
|---|---|
| origin lane tip | `7f03e554cdc06b4c97a19e3191a4c7ab9c220462` |
| lane round-1 commit (`kama-shokunin`, author time `@1000`) | `db796f8b820bf3825c58832419138cdba23206a7` |
| `corpus/SOURCES.md` blob oid | `b109f41fdebcb812e709b8e671d692a15f343218` |
| fleet report commit (author time `@2000`) | `.ufo/reports/round-1/kama.md` |
| cited registry URL | `https://example.invalid/fixture/blob/1234567890abcdef1234567890abcdef12345678` |

The fleet report cites the lane commit in `## Landed changes` and the registry URL under `## Notes`
(outside the landed section, as the contract requires for the URL exemption,
`tools/report-landing-audit.py:283-300`).

Promisor lane: `git clone --no-checkout --filter=blob:none --no-local file://<origin lane>` →
`remote.origin.promisor=true`, `remote.origin.partialclonefilter=blob:none`, one
`.git/objects/pack/pack-6dc76237d1c459a61e806adc888fd9222bdb575a.promisor`.
(`extensions.partialclone` is **absent**: git 2.56 writes only the two remote keys. The base's config check
`tools/report-landing-audit.py:463-465` therefore does not fire; the pack check at `:455-457` does.)

## Expected exits and findings (fixed now, before implementation)

| arm | lane state | expect rc | expect stdout | expect findings |
|---|---|---|---|---|
| `control_full_clone` | complete local objects | **0** | verdict JSON | 0 defects, `status=clean`, `source_url_hashes` contains `1234567890abcdef1234567890abcdef12345678` |
| `treatment_promisor` | promisor-marked, committed SOURCES blob absent | **2** | none | no verdict at all; stderr names the unavailable required object; stderr must not be a transport/fetch error |
| `probe_metadata_stripped` | same repo, promisor metadata removed, blob still absent | **2** | none | stderr names the missing blob oid / `cat-file` — the only possible reason is the missing object |
| `legacy_exemption` | lane that never committed `corpus/SOURCES.md` | **1** | verdict JSON | 1 defect: `unresolved-full-hash` `1234567890abcdef1234567890abcdef12345678` — **documentary, not a pass criterion**: this is the exemption signature |
| `treatment_no_remote` | promisor-marked, remote URL → nonexistent local path | **2** | none | stderr identical to `treatment_promisor` after normalising the repo path |

Invariants checked on every arm: **no object id is added to the lane clone's local object store by the audit**
(comparison of `git --no-lazy-fetch cat-file --batch-check --batch-all-objects --unordered` before/after);
the missing blob never appears locally, so **no lazy fetch ran**. The only remote is a local `file://` path —
**no network transport**; **no remote program, hook or command** is configured or triggered; the fixture's own
git calls use a 60 s ceiling and the auditor keeps its own 20 s deadline
(`tools/report-landing-audit.py:108,111-135`).

## Base observations (r23 tool, `da5041a8…`)

```
control_full_clone       rc 0  0 defects  status=clean  source_url_hashes=[1234…5678]
treatment_promisor       rc 2  stderr "could-not-evaluate: <lane>: partial clone (promisor pack)"
probe_metadata_stripped  rc 2  stderr "could-not-evaluate: git cat-file blob b109f41f… in <lane>: rc=128
                                fatal: git cat-file b109f41f…: bad file"
legacy_exemption         rc 1  1 defect: unresolved-full-hash 1234…5678
treatment_no_remote      rc 2  stderr identical to treatment_promisor (repo path normalised)
no_object_added_by_any_audit = true (all five arms)
```

Read against the code: `treatment_promisor` stops at `check_history_repo`
(`tools/report-landing-audit.py:438-466`, pack refusal `:455-457`) — a **metadata** refusal, the r23 harm class.
`probe_metadata_stripped` passes that gate and stops at `load_source_urls`
(`tools/report-landing-audit.py:260` `ls-tree` succeeds → `:268` `cat-file blob` fails → `EvalError` → exit 2) —
the **content** refusal. `legacy_exemption` shows what "exemption" looks like when the registry is *not committed*:
`load_source_urls` returns `None` (`:262`) and `classify_full_hashes` (`:283-300`) scans the URL's 40-hex as a
plain token → false `unresolved-full-hash` → exit 1.

**Why the repair must keep the distinction.** A committed-but-unreadable registry is *not* the legacy case at
`:259-262`; the "absent" branch there is `ls-tree` returning nothing (the file is not in the tree), which is a
different fact from "the tree names it and the object cannot be read". If the repair relaxes `:268` into the
`:262` path, `treatment_promisor` degrades to `legacy_exemption`'s exit 1 or to a false clean exit 0 — the two
outcomes this case forbids.

**Hazard worth naming for L1.** The promised blob *is* reachable offline in this fixture: with lazy fetch allowed,
`git cat-file blob b109f41f…` returns the registry bytes from the local `file://` remote. A candidate that dropped
`--no-lazy-fetch` (`tools/report-landing-audit.py:93-97`) would silently materialise the blob and report a clean
exit 0 — the exact false clean this case must catch. The fixture therefore also measures flag preservation.

## Grid adoption

* Builder (grid-ready, `build(tmp)` returns the round-23 grid tuple
  `(lane, fleet, argv_extra, marker)`):
  `.ufo/waves/round-24/build/out/CaseMissingLaneBlob/case_missing_lane_blob.py`
  sha256 `90874c0d9cfe6b071a17903e9fd790e10f1383c4fab38d425633c8e42efe9a89`.
* Machine-readable expectations: `.ufo/waves/round-24/build/out/CaseMissingLaneBlob/expected.json`.
* Raw run: `.ufo/waves/round-24/build/out/CaseMissingLaneBlob/evidence.log` (+ scratch `base-run.json`).
* Reproduction (single command, no suite):
  `python3 .ufo/waves/round-24/build/out/CaseMissingLaneBlob/case_missing_lane_blob.py --workspace <scratch> --auditor <tool> --json`
* Recommendation for `tests/report-audit/promisor-grid.py`: grade `treatment_promisor` and
  `probe_metadata_stripped` on **rc == 2**, and grade `probe_metadata_stripped`'s stderr for the content reason
  (its repository carries no promisor metadata at all, so the wording is deterministic and cannot be over-fitted
  to a metadata refusal). Grade `control_full_clone` on rc 0 / 0 defects, and keep `legacy_exemption` as a
  labelled control that documents the exemption signature rather than as a pass criterion.

## Containment

* Every fixture path is under `/fast/scratch/hyaku/kama-r24/CaseMissingLaneBlob/`.
  `find /tmp -maxdepth 2 -newermt '-2 hours' \( -name '*kama*' -o -name '*report-landing*' -o -name '*promisor*' -o -name '*fixture*' \)` → **no hits**.
* Scratch clone is `--no-hardlinks`: `find repo/.git/objects -type f -links +1` → empty (no object shared with the source repo).
* Lane repo untouched: HEAD still `d1b9d956a0beda9ac32a1a2cf6ced875faeada0d`; no commit, no push, no index write.
  Only files written: this advice file and `.ufo/waves/round-24/build/out/CaseMissingLaneBlob/`.
* No tool installed or updated (git 2.56.0 and Python 3.14.8 were already present).

## Residual risk / verification gaps

* **The r24 candidate was not run** — it does not exist yet at base. Every rc in this report is an observation of
  the r23 base tool or a fixture premise; the r24 expectation is a specification, not a measurement.
* The treatment arm's rc alone does not separate "metadata refused" from "content judged missing"; the
  `probe_metadata_stripped` arm is the discriminating one, but it exercises a repository *without* promisor
  metadata, so a repair that keeps a metadata refusal for genuinely incomplete promisor repos is neither
  rewarded nor punished by it. A third arm (promisor-marked **and** complete, e.g. the hydrated lane) is needed to
  prove the r24 harm is gone — that is `CaseHydratedLane`/`CaseCompleteLane`, not this lane.
* Only `blob:none` was exercised. A `tree:0` clone (missing trees) and a missing *commit* are separate arms
  (`CaseMissingLaneTree`, `CaseMissingAncestor`); not covered here.
* The tool's own `GIT_TIMEOUT` (20 s, `tools/report-landing-audit.py:107`) was not exercised against a hanging
  repository in this case; the fixture contains no FIFO/config trap, so "no config-caused hang" is asserted by
  construction, not measured.
* `--selftest` of the base tool was **not** run (suite, out of lane bounds).

## Files

* `.ufo/waves/round-24/build/advice/CaseMissingLaneBlob.md` (this report)
* `.ufo/waves/round-24/build/out/CaseMissingLaneBlob/case_missing_lane_blob.py` (fixture builder, grid-ready)
* `.ufo/waves/round-24/build/out/CaseMissingLaneBlob/expected.json` (expected exits/findings)
* `.ufo/waves/round-24/build/out/CaseMissingLaneBlob/evidence.log` (append-only evidence)
* scratch (outside the lane tree): `/fast/scratch/hyaku/kama-r24/CaseMissingLaneBlob/{repo,fixture,base-run.json,base-run.err}`
