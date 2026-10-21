# CritNoHarm — attack on the round-23 C1 no-harm plan

Seat: CloseKama22.CritNoHarm (critic, leaf). Date 2026-10-21. git 2.56.0, Python 3.14.8 (utf8_mode 0, locale UTF-8).
Arms compared:
- **frozen** = blob `4fe9339f:tools/report-landing-audit.py`, extracted to `/tmp/kama-r23/CritNoHarm-probe/frozen/report-landing-audit.py`, sha256 `09ecd63b…3b3f`. This equals the L1 copy `/tmp/kama-r23-probe/frozen-audit.py`.
- **candidate** = the *uncommitted* lane working-tree file `kama-shokunin/tools/report-landing-audit.py`, sha256 `b6064767…bda`, mtime 2026-10-21 12:07:55 -0300. It adds `GIT_ISOLATION` (`--no-replace-objects --no-lazy-fetch -c i18n.logOutputEncoding=UTF-8 -c log.follow=false`), bytes stdout with a strict UTF-8 decode that raises `EvalError`, and CR/CRLF normalization.

## Verdict on the four named guarantees (both arms, measured)

| Guarantee | Frozen | Candidate | Evidence |
|---|---|---|---|
| Audit selftest 50/50 | 50/0 fail, rc0 | 50/0 fail, rc0 | `--selftest` outputs `g/st.{frozen,cand}`; `diff` of case-name lines: **identical** |
| Witness selftest 6/6 + witness | selftest-clean 6/0; witness red-green-match rc0 (frozen passed as `--candidate`) | selftest-clean 6/0 (all 6 cases passed); witness red-green-match rc0 | `red-green-witness.py [--selftest]`; candidate_sha `b6064767…`. Manifest pins only `cc9f8d3` old script, registry and census, **not** the current script, so a script edit cannot trip `snapshot_tampered`. |
| Historical ledger (9 corrected) | 10–21: 12 reports, 9/9 corrected, 49 required, 5 post, clean rc0; raw rc1 | identical | JSON for raw/ledger × 10–21/10–22: **byte-identical** frozen vs candidate (`cmp`). 10–22: 13 reports, 9/9, 54 required, 5 post, round 22 has 0 defects. |
| Citation 17/17 | — | required 17, found 17, verified 17, missing/mismatch/off_ref 0, rc0 | `tools/citation-provenance.py --json`. This tool does not reference the audit (`rg report-landing tools/citation-provenance.py` returns nothing), so it is causally independent of the change. |

Why the historical ledger is safe: the real lane and fleet have 0 `refs/replace`, no `info/grafts`, no `shallow`, no alternates, and no `*.promisor` packs. They also set none of these local keys: `extensions.partialClone`, `i18n.*`, `log.follow`, `log.showSignature`, `core.quotePath`, `remote.*.promisor`, `diff.*.textconv`, `filter.*`. All 13 committed fleet reports (r10–r22), plus `corpus/SOURCES.md`, the errata blob and lane `git log`, contain 0 CR bytes and are valid UTF-8. All 96 lane commits have an empty `%e` (encoding header). So every new flag and the decode path are no-ops on today's inputs.

## Findings (counterexamples)

### N1 — HARM (measured): `--no-lazy-fetch` turns a legitimate partial clone from clean into a **false failed verdict**
Fixture `out/CritNoHarm/partial-clone-noharm.sh` (sha256 `a2aa88b0…d3c1`): a `blob:none` partial-clone fleet with a `file://` promisor (no network, no repo-configured command). The report cites a 40-hex blob, outside `## Landed changes`, that exists only on the promisor. The report blob itself is fetched beforehand.

```
frozen exit=0 blob_local_before=no after=yes defects=[]
cand   exit=1 blob_local_before=no after=no  defects=[('unresolved-full-hash', 'c2981a9931')]
```

This is not a refusal. `cat-file --batch-check` answers `missing`, and `lookup()` maps that to a defect. It violates "Errors are never verdicts" (docstring :43): an object *promised* by the repo is reported as "no git object in the lane or fleet repo".

This is distinct from CritSeparability §2, where an absent SOURCES/report blob causes a refusal (exit 2). Here the needed blobs are present and only a cited object is remote, so the outcome is a verdict flip on a control.

Impacted axes: calibration (false verdict), operability.

Smallest safe correction: before lookup, detect a promisor repo and make `missing` from that repo an `EvalError`. The simpler variant is to refuse partial clones outright in `run()`, which is consistent with the refusal tradeoff CritSeparability already names. Detection must not rely only on `extensions.partialClone`: a git 2.56 `clone --filter=blob:none` wrote only `remote.origin.promisor=true` / `partialclonefilter` and `core.repositoryformatversion=1` (observed in `git config --list --local`). Use `remote.*.promisor` or `objects/pack/*.promisor`. Add this fixture as a declared control: expect exit 2, or exit 0 if fetching is re-allowed for `file://` only (not recommended).

### N2 — Frozen-arm hazard (measured): the lane worktree path is no longer the frozen arm
`kama-shokunin/tools/report-landing-audit.py` is the uncommitted candidate. A read-only hash-object sweep of `tools registry corpus/QUALITY.md tests …/report-source-fix` against `4fe9339f` shows it is the only modified tracked file there.

My first run used `FROZEN=<lane>/tools/report-landing-audit.py` and silently compared candidate against candidate: P1/P2/P3 all "unchanged". Every recipe line using `{lane}/tools/report-landing-audit.py`, and the witness default `--candidate`, measures whatever is in the worktree.

Correction: the frozen arm must be `git cat-file blob 4fe9339f:tools/report-landing-audit.py` (sha256 `09ecd63b…`). The candidate arm must be measured from a clean checkout of the *committed* candidate revision, as the round-22 receipts did at `80a6d07c`. Never measure through a dirty lane path.

### N3 — Fault-grid row (c) does not reproduce under the stated isolation (measured)
In `probe.sh` f3, `git commit-tree` runs without explicit identity. With `GIT_CONFIG_GLOBAL=/dev/null` and no `EMAIL` in my environment it fails ("Author identity unknown … `vgpnk@plazir27.(none)`"), so `Y` is empty and `git replace` installs nothing (my f3 lane: 0 `refs/replace`). Frozen then returns the *correct* verdict (exit 1, `landed-omitted 4312b0a5…`), not "false clean exit0". The L1's own runs (`/tmp/kama-r23-probe/run.*/f3/lane`) each have 1 replace ref, so (c) depends on ambient identity.

Correction: pin `GIT_AUTHOR_*` and `GIT_COMMITTER_*` for `commit-tree`. Assert fixture preconditions (replace-ref count == 1 for f3/f4, marker absent before f5) before scoring a cell; a fixture that fails setup must be not-evaluated, not scored.

Grid on this host:

| Fault | Frozen | Candidate |
|---|---|---|
| (a) f1 | traceback exit1 | exit0, correct |
| (b) f2 | traceback exit1 | exit2, typed |
| (c) f3 | not evaluated here | — |
| (d) f4 | false clean exit0 | exit1 `unresolved-full-hash` |
| (e) f5 | marker created | no marker; exit1 for the fabricated token |
| f6 (`log.follow`) | exit0 | exit0, **no red cell** |

The `-c log.follow=false` flag has no demonstrated fault on this host. Either add a red cell for it or label it unmeasured.

### N4 — "selftest 50/50 unchanged" is not evidence of the fix (code-read + measured)
The candidate's selftest case names are identical to frozen's, and no case exercises `GIT_ISOLATION`, non-UTF-8 output, replace refs or a promisor. `[INFERENCE]` Deleting any isolation flag or the decode guard would keep 50/50 green; I did not run that mutation. MutExistingSelftest/GridMutants own it.

No-harm must compare the **case-name set** (old 50 ⊆ new, all ok), not a count. Prior lane lesson: a count floor is not an injectivity check (considerthese/2026-10-20.md).

### Checked, no harm found
- **Textconv:** repo-local `diff.tc.textconv` (marker command) plus `.git/info/attributes *.md diff=tc` on the fleet. `git show HEAD:<rel>` did not run it in either arm (exit0, no marker).
- **Lone-CR report:** `# r1\r## Landed changes\r…`. Frozen (text-mode universal newlines) and candidate (explicit `\r\n`/`\r` → `\n`) both exit0 with no defects. Newline semantics are preserved; a plain bytes `.decode()` without that normalization would have regressed CRLF `SOURCES.md` (`## Registry\r`) and lone-CR headings. That second half is a code-read inference.
- **Locale:** the candidate decodes UTF-8 regardless of locale, whereas frozen `text=True` used the locale encoding. Under a latin-1 locale, frozen never raised and the candidate would refuse. This is a behavior change toward correct; no committed input differs (all valid UTF-8).

## Mandatory reruns before admission (on the committed candidate revision, clean checkout)
1. `report-landing-audit.py --selftest`: exit 0, and the case-name set must be a superset of the frozen 50 names (name diff, not count).
2. `red-green-witness.py --selftest` (6/6) and `red-green-witness.py`: red-green-match exit 0, with `candidate_sha256` equal to the committed candidate blob's sha.
3. Historical `--rounds 10-21` and `10-22`, each raw (`--no-errata`, expect exit1) and ledger (expect exit0), against the real lane and fleet. Run **both arms** (frozen = extracted `4fe9339f` blob) and require byte-identical JSON. Remembered counts alone are insufficient.
4. `citation-provenance.py --json`: 17/17. It is causally independent but part of the declared no-harm set.
5. Fault grid with pinned identity and fixture preconditions (N3), plus the new partial-clone control (N1). As the candidate stands, N1 is red: it must become exit 2 (or a correct 0) before admission.
6. Old-git floor (OldGitFloor): a git that rejects `--no-lazy-fetch` must yield exit 2 for every run. This is not reproducible on this host (2.56.0).
7. The other round-22 recipe lines (sources validate/census, sources-append-only, io-current-noharm) do not touch this file. Rerun them only because the recipe is whole-tree; no causal exposure was found.

Docs coupling: `corpus/QUALITY.md:165` (KQ32) limits the audit to trusted repos until hardening is "demonstrated separately". Any edit must stay scoped to the measured grid and must not claim partial-clone or untrusted-repo safety (see N1).

## Not verified
- Mutation runs removing individual flags.
- `tree:0` partial clones.
- ssh/https promisors.
- Old git versions.
- Python < 3.14 or non-UTF-8 locales.
- f3 under the L1's exact environment.
- The L1's integration intent for the uncommitted worktree file. I treated it as the candidate.

## Files written
- `.ufo/waves/round-23/build/advice/CritNoHarm.md` (this report)
- `.ufo/waves/round-23/build/out/CritNoHarm/partial-clone-noharm.sh` (N1 fixture; it sets FROZEN to my extracted blob and CAND to the lane worktree path, so edit both before reuse)
- Scratch only: `/tmp/kama-r23/CritNoHarm/` (clone; `tools/report-landing-audit.py` holds my own throwaway minimal candidate, not a deliverable) and `/tmp/kama-r23/CritNoHarm-probe/` (frozen blob, `noharm.sh`, `partial.sh`, `probe-copy.sh` with the T dir redirected, outputs `g/`, `w*.json`, `cit.json`, `grid.*`, `run.*`, `partial.*`)

No installs, no commits, no lane/fleet writes. Real lane and fleet were only read, by audit/witness/citation runs and read-only git (`for-each-ref`, `config --get`, `cat-file`, `hash-object` without `-w`, `ls-tree`, `log`).
