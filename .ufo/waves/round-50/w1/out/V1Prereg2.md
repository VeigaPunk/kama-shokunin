# V1Prereg2 — round-50 freeze integrity

VERDICT: **freeze holds — no defect.** Prereg predicates == counter docstring PREDICATE sentences; both counter_sha256 == `git show 601c8889:<path> | sha256sum`; both counters byte-identical at freeze 601c8889f33d and tip 97c864bead3e (and the live worktree); `frozen_at_utc` precedes the freeze committer time; the committed `prereg-time-check.out` is byte-identical to a rerun on a shared clone; every build mechanism (live_env, model_mapping, fence helpers, birth-DAG origins, S496–S498) is absent at the freeze commit and present at tip.

Conventions: `F` = freeze `601c8889f33d1797c712feb753974c20cf891264`, `T` = build tip `97c864bead3ee4a2f629574e77263d33834ec98a`, `L` = `/home/vgpnk/Projects/shokunin/kama-shokunin`, clone `git clone --shared $L $S/lane`, `S` = `/fast/scratch/hyaku/kama-r50/V1Prereg2`.

## 1. Predicate sentences == PREDICATE sentences in counter docstrings — PASS

Extracted the `PREDICATE (same sentence in the preregistration):` paragraph from each counter's docstring at F and T, whitespace-normalized (collapse runs → single space), compared to `claims[].predicate` in `F:.ufo/waves/round-50/preregistration.json`:

- C1: prereg == docstring@F: **True**; docstring@F == @T: **True**.
- C2: prereg == docstring@F: **True**; docstring@F == @T: **True**.

Sources: `tools/round50-replay-bind-audit.py:78-84` (PREDICATE paragraph), `tools/round50-append-audit-v5-check.py:74-80`; `preregistration.json` `claims[0].predicate` / `claims[1].predicate`. (Docstrings wrap at ~75 col; comparison done after whitespace normalization — the "same sentence" contract.)

## 2. counter_sha256 == git-show hash at the freeze — PASS

`git -C $L show F:<path> | sha256sum`:

- `tools/round50-replay-bind-audit.py` → `ff6ac2ace541ea35a4d240ceebb019653c11a2a08c025e514770f3f94a9c5e89` == `claims[0].counter_sha256`.
- `tools/round50-append-audit-v5-check.py` → `925f07a48a02ad54a9c89230aac7e54c8dafee4ba2e8a823dcb851b9cf48ca46` == `claims[1].counter_sha256`.

## 3. Counters byte-identical at 601c8889 and 97c864be — PASS

`git show T:<path> | sha256sum` yields the identical digests (`ff6ac2…` C1, `925f07…` C2); the working-tree files also hash to those same digests (`sha256sum $L/tools/round50-*.py`), so the runnable copies are the frozen ones. `git diff --name-only F..T` lists only `.ufo/waves/round-50/freeze/prereg-time-check.out`, `corpus/SOURCES.md`, `tools/append-only-audit.py`, `tools/kama-live-replay.py`, `tools/kama-llamacpp-live.py` — the counters are not in the build diff. `F:.ufo/waves/round-50/preregistration.json` == `T:` == worktree (sha256 `0743786460839e36…` all three).

## 4. frozen_at_utc precedes the freeze commit time — PASS (with note)

- `frozen_at_utc` = `2026-10-27T00:20:47Z` (`preregistration.json:6`, confirmed `sed -n '6p'`).
- Freeze commit `git show -s --format='%cI %aI'` F → committer `2026-10-26T21:20:51-03:00` (= `00:20:51Z`), author `2026-10-26T21:07:55-03:00` (= `00:07:55Z`).
- `00:20:47Z < 00:20:51Z`: precedes committer time by 4 s. **Note (not a defect):** frozen_at_utc sits *between* author and committer time — the prereg was timestamped while authored and committed 4 s later. `prereg-time-check.py` anchors on committer time (`committer_time` via `%cI`), which is the right anchor for "was this text present at the freeze commit".

## 5. freeze/prereg-time-check.out consistent with a rerun — PASS

`python3 $L/tools/prereg-time-check.py --repo $S/lane --path .ufo/waves/round-50/preregistration.json --rev 601c8889f33d1797c712feb753974c20cf891264; echo exit=$?` produced output **byte-identical** to `.ufo/waves/round-50/freeze/prereg-time-check.out` (exit 0; `diff` clean). Rerun copy: `.ufo/waves/round-50/w1/out/V1Prereg2/prereg-time-check.rerun.out`. It reports `ok line 6: 2026-10-27T00:20:47Z (at/before commit)` / `RESULT pass`. Note: the `.out` file itself was *added by the build commit* (it is in the F..T diff, not in the base..F freeze diff) — placement, not integrity; content still reproduces exactly.

## 6. Build paths absent at 601c8889 — PASS

All four touched files exist at F (pre-build versions); every build marker is absent at F and present at T. Marker counts (`grep -c`, freeze file vs tip file):

| path | marker | F | T |
|---|---|---|---|
| `tools/kama-live-replay.py` | `set_own_pdeathsig` | 0 | 2 |
| | `live_env` | 0 | 2 |
| | `preexec_fn` | 0 | 1 |
| | `sys.executable, "-I"` | 0 | 1 |
| | `PDEATHSIG` | 0 | 5 |
| `tools/kama-llamacpp-live.py` | `model_mapping` | 0 | 4 |
| `tools/append-only-audit.py` | `fence` (case-insens.) | 0 | 19 |
| | `birth` | 0 | 3 |
| `corpus/SOURCES.md` | `S496`/`S497`/`S498` | 0/0/0 | 1/1/1 |

- F `append-only-audit.py` docstring says `v4 definitions` ("first blob in rev-list … origin"); tip says `v5 definitions` with fence/birth-DAG origin — `origin` exists at F (22 hits) only in the v4 rev-list sense; the v5 "union of section titles at every birth" machinery (`fence`, `birth`) is absent at F. CRLF normalization: `carriage`/`rstrip` at F are unrelated (exit-message/locale wording), no trailing-CR key normalization.
- F `corpus/SOURCES.md` max row S494 (S495 also present? highest S-id found = 495); S496 proc_pid_maps(5), S497 PR_SET_PDEATHSIG(2const), S498 CommonMark 0.31.2 §4.5 appear only at T (`SOURCES.md:249-251`). No `proc_pid_maps`/`PR_SET_PDEATHSIG`/`CommonMark` strings at F.
- Freeze-era artifacts unchanged by the build (sha256-equal F vs T): `controls/base.c1.out`, `controls/base.c2.out`, `census/start.out`, `c1/proc_pid_maps.5.txt`, `c1/PR_SET_PDEATHSIG.2const.txt`, `c2/commonmark-0.31.2-s4.5.txt`. Controls both read `met=False` (`base.c1.out:2`, `base.c2.out:2`) — consistent with a true freeze snapshot.
- Both counters accept `--out` (`round50-replay-bind-audit.py:547`, `round50-append-audit-v5-check.py:504`), so the prereg `command` strings are runnable.

## Residual risk / gaps

- Absence was checked by marker tokens, not by behavioral diff of the whole F..T patch; the diff is limited to the five files above, each consistent with the stated build.
- `frozen_at_utc` is 4 s before committer time — evidence the field was authored-then-committed (normal); a forged timestamp would typically sit earlier, not closer.
- Known integration items (counters absent from SKILL.md registry — confirmed: no `round50-` hits in `SKILL.md`; S496–S498 `used-by`, scribe docs pending at integration) match the stated status; not re-reported as findings.

## Evidence files

- `.ufo/waves/round-50/w1/out/V1Prereg2/prereg-time-check.rerun.out` — rerun of the freeze time check (byte-identical to the committed `.out`).

No tools installed; no lane mutation; `git` used read-only on `$L` and a `--shared` clone.
