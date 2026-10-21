# CaseCompleteLane — PROM-COMPLETE-LANE oracle case

**Lane:** `CaseCompleteLane` (KamaR23-2.CaseCompleteLane-2) · **Role:** reviewer
**Base:** `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` (auditor blob sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1`)
**Verdict: the case is specified, executed, satisfiable and discriminating. PROM-CLEAN and PROM-OMIT are jointly satisfiable with the contract's exit-2 requirement for unavailable evidence (rule R2 satisfies all three rows). The base fails both rows — that is the round-23 harm this case pins down.**

## 1. The case (preregistered before implementation)

A lane repository that is a **complete local clone** (every object the audit reads is present) but whose origin remote is **declared promisor** (`remote.origin.promisor=true`). The declaration is metadata only: no `.promisor` pack marker, no missing object, and the origin URL is an inert non-existent local path (`/nonexistent/kama-promisor-origin.git`), so no transport is reachable.

| row | fixture | expected exit | expected defect kinds | full-clone twin |
|---|---|---|---|---|
| `PROM-CLEAN` | cited lane commit, nothing omitted | **0** | `[]` | `C01-clean` (`tests/report-audit/repo-state-grid.py:632`) |
| `PROM-OMIT` | genuine pre-cutoff lane commit omitted from `## Landed changes` | **1** | `["landed-omitted"]` | `C02-real-omission` (`tests/report-audit/repo-state-grid.py:633`) |

The expected values are not invented here: they are the round-23 control rows' own values, and the promisor row must equal its full-clone twin in exit code **and** in the exact `(kind, token)` defect set.

A third row, `INCOMPLETE-PROMISOR`, is the contrast case (same metadata, but the one required evidence object removed from the local store): expected **exit 2**, never a guessed verdict. It belongs to the contract, not to this lane's row set, but it is what makes the two PROM rows discriminating.

## 2. Base observations (the harm, located)

`tools/report-landing-audit.py:514-515` calls `check_history_repo(repo)` for the lane and the fleet **before any object lookup**. `:458-465` scans the config list and raises on the metadata alone:

```python
        if key == "extensions.partialclone" or (
                re.fullmatch(r"remote\..+\.promisor", key)
                and git_bool(value)):
            raise EvalError(f"{repo}: partial clone ({key})")
```

Observed at the base (`out/CaseCompleteLane/oracle-spec.json`, `base-observation.json`, `derivation.json`):

```
PROM-CLEAN  promisor: exit 2  "could-not-evaluate: …/lane-promisor: partial clone (remote.origin.promisor)"
PROM-CLEAN  full:    exit 0  defects []
PROM-OMIT   promisor: exit 2  "… partial clone (remote.origin.promisor)"
PROM-OMIT   full:    exit 1  defects [("landed-omitted","29e8ea69cc44bbb72af22255c5231a7d13b577e0")]
```

A *complete* promisor-marked lane is refused for its **metadata**, and the refusal happens before the audit can establish that every required object is in fact local. That is the r23 blanket refusal.

## 3. Satisfiability (the oracle is not over-constrained)

Three rules were simulated as **scratch copies of the base auditor** (never installed into the production tree; `out/CaseCompleteLane/simulation.json`):

| rule | PROM-CLEAN | PROM-OMIT | INCOMPLETE-PROMISOR |
|---|---|---|---|
| **R0** base (0df800e) | exit 2 ✗ | exit 2 ✗ | exit 2 ✓ |
| **R1** naive removal of the promisor-config refusal | exit 0 ✓ | exit 1 ✓ | exit 1 ✗ (`unresolved-full-hash` — a *guessed* absence) |
| **R2** content-based (record the declaration; a required object unreadable ⇒ EvalError) | exit 0 ✓ | exit 1 ✓ | exit 2 ✓ |

**R2 satisfies all three rows at once**, so PROM-CLEAN and PROM-OMIT are jointly satisfiable together with the contract's "missing required object evidence is exit2, never guessed absence" clause. R1 shows that *removing the refusal alone is not the repair* — it silently converts unavailable evidence into a failed verdict.

R2 also leaves the adjacent round-23 rows intact (bounded run of the existing harness, current arm = the R2 scratch copy, `validate/grid-adjacent-r2.py`):

```
current C01-clean control exit=0 met      current F06-lazy-fetch-command fault exit=2 met
current C02-real-omission control exit=1 met  current F23-promisor-pack-without-config contract exit=2 met
current C09-promisor-false-config control exit=0 met  current F27-filter-only-promisor-remote fault exit=1 met
current C10-orphan-promisor-marker control exit=0 met  current T01-blobless-partial-clone tradeoff exit=2 NOT-MET
```

`T01-blobless-partial-clone` (`repo-state-grid.py:689`) is a **tradeoff** row, reported and never graded; its round-23 expectation was exit 0 and R2 gives exit 2, which is the contractually correct answer for a genuinely incomplete clone. **L1 must document that expectation change explicitly** — it is a policy row, not a regression, and the preregistration's "retained historical r23 grid with explicitly documented policy-row expectation changes" covers exactly this.

## 4. Premise effectiveness (the case cannot pass trivially)

A fixture whose fault never materialized would pass vacuously. The premise is checked, and the case is proved discriminating by requiring that the base refuse **for the promisor reason**:

- `promisor_pack_markers == 0`, `missing_objects == []` (from `git rev-list --objects --all --missing=print`), every required commit resolves via `cat-file -e`, twin tip == source tip, `remote.origin.promisor == true`;
- `premise_effective: true` for both rows: the base exits 2 **with the pinned string** `partial clone (remote.origin.promisor)`. If the fixture had degenerated into a plain clone, the base would have exited 0/1 and the row would have failed loudly.

Lifted into the real harness (`validate/grid-with-promisor-case.py`, the round-23 grid with only my two rows injected):

```
current PROM-CLEAN control exit=2 expected_exit=0 kinds=None met=false
current PROM-OMIT  control exit=2 expected_exit=1 kinds=None met=false
```

Both rows fail at the base, for the intended reason, with no traceback, no timeout and no executed program.

## 5. Containment, transport and program-execution evidence

- **Fixtures live only under** `/fast/scratch/hyaku/kama-r24/CaseCompleteLane/` (`run/`, `oracle/`, `derive/`, `simulate/`, `trace*/`, `validate/`). Nothing was written to `/tmp` by this lane's scripts; the two `/tmp` deltas observed in `derivation.json` (`kengaku-r29-*`) belong to a sibling lane and are not mine.
- **No network transport.** The promisor origin URL is an inert non-existent local path, and `strace -f -e trace=network,execve` over the auditor (base, R1 and R2, both the complete and the incomplete fixture) recorded **0 network syscalls** (`connect`/`socket`/`sendto`/`recvfrom`) and **0 non-git `execve`** — i.e. no repository-configured program ran (`out/CaseCompleteLane/simulation.json`, traces under `scratch/…/trace2`, `scratch/…/trace3`).
- **No lazy fetch.** `--no-lazy-fetch` stays in `GIT_ISOLATION` (`tools/report-landing-audit.py:93-96`, together with `--no-replace-objects`, `log.follow=false`, `log.showRoot=true`, `log.showSignature=false`, `log.mailmap=false`). The object store of the audited promisor clone is byte-for-byte unchanged after the audit (`objects_unchanged_after_audit: true`).
- **No fixture escaped into the production tree.** My writes are exactly the nine files under `.ufo/waves/round-24/build/out/CaseCompleteLane/`. The production lane's Git index is clean (`git diff --cached --name-only` → 0 lines), no commit and no push was made, and `tools/report-landing-audit.py` is byte-identical to the base blob (sha256 equal to the base's).

## 6. Deliverables (all under my out directory)

| file | what it is |
|---|---|
| `promisor-complete-lane-case.py` | **the case fragment** — drop-in builders `p_complete_lane_clean` / `p_complete_lane_omit` plus `PROMISOR_CASES` rows, written against the `repo-state-grid.py` helper names. Liftable block = from the line `INERT_ORIGIN = ` to EOF. |
| `oracle-spec.json` | the preregistered expectations + base observations + premise-effectiveness flags |
| `simulation.json` | R0/R1/R2 rule simulation over all three rows |
| `derivation.json`, `base-observation.json` | the base-harm observation and the naive-removal contrast |
| `build-oracle-spec.py`, `derive-case.py`, `run-oracle-case.py`, `simulate-rules.py` | the bounded local runners that produce the JSON above (re-runnable, offline) |

Reproduce with:

```
python3 .ufo/waves/round-24/build/out/CaseCompleteLane/build-oracle-spec.py
python3 .ufo/waves/round-24/build/out/CaseCompleteLane/simulate-rules.py
```

## 7. Requirements this case places on the repair (for L1)

1. The promisor **declaration** must not by itself decide the outcome; content availability must (`PROM-CLEAN` exit 0, `PROM-OMIT` exit 1).
2. A required object that cannot be read from the audited repositories, in a promisor-backed repository, must be **exit 2**, not a guessed absence (R1 fails this; R2 passes).
3. `--no-lazy-fetch`, `--no-replace-objects`, the log/signature suppressions and the git timeout must survive the repair; the r23 grid rows F06, F23, F27, C09, C10 must keep their expectations.
4. The round-23 grid row **T01-blobless-partial-clone** (tradeoff, `repo-state-grid.py:689`) changes expectation from exit 0 to exit 2 under any content-based rule; that change must be recorded explicitly, not silently.

## 8. Scope and non-goals

This lane covers the **lane** side only. Not claimed, not tested here: promisor-marked **fleet** repositories, `extensions.partialclone` marker repositories, blobless/hydrated clones, `remote.<name>.partialclonefilter`-only remotes, cross-repository resolution of an unknown citation, and the closure of the inherited parser/alternates/gitfile/size-limit findings. Those are other lanes' rows (`CaseCompleteFleet`, `CaseMarkerLane`, `CaseHydratedLane`, `CaseUnknownCitation`, `CaseCrossRepoFound`, `CaseAlternatesComplete`).

**Unrun = unverified:** the candidate implementation itself (none existed when this case was frozen) and the full round-24 grid; the measurements above are bounded local runs of the base auditor and of scratch rule copies only.
