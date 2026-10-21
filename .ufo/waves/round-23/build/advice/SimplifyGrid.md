# SimplifyGrid — minimal C1 fault-grid case table

## Godspeed axes

| Axis | This move |
|------|-----------|
| **Coverage** | Each L1 fault class (a–e) and the happy-path control have a dedicated row; no row shares the same frozen+fixed oracle pair. |
| **Cost** | Six rows total for claim (a–e)+control; F6 (`log.follow`) is an optional seventh only with the rich fixture (probe.sh F6 ≡ control on frozen). |
| **Discrimination** | Every fault row differs from C0 and from every other row on at least one frozen observable in the table. |
| **Harness honesty** | F3 requires `commit-tree` identity under `GIT_CONFIG_GLOBAL=/dev/null` (see below). |

## Sources reviewed

| Artifact | Role |
|----------|------|
| `/tmp/kama-r23-probe/probe.sh` | Same script as `.ufo/waves/round-23/probe/probe.sh` (byte match observed). |
| `.ufo/waves/round-23/probe/probe-4fe9339f.stdout` | Canonical frozen run at auditor `4fe9339f…` (F3 exit 0 when `commit-tree` succeeds). |
| `tools/report-landing-audit.py` @ `4fe9339f8fc3a4a4a479d9c938a850da12f1124d` | Exit contract L42–44; `git()` L87–97; omission L300–305; `report_cutoff` L165–168. |

**Installs:** none.

## Probe harness note (F3 / F4)

Lines 43–45 call `git commit-tree` without `-c user.name` / `-c user.email`. With `GIT_CONFIG_GLOBAL=/dev/null`, `commit-tree` fails on this host (`Author identity unknown`; empty `Y`), so **F3 does not reproduce false clean** and stderr noise appears before F4.

**Minimal fix for the grid (not lane code):**  
`git -C "$L" -c user.name=x -c user.email=a@x commit-tree …`  
With that, manual replay matches canonical stdout: F3 `exit=0`, `defects []`, `required 1` while a second `round-1:` commit exists (replace rewrites log subject to `unrelated`, dropping it from `round_commits()`).

Evidence (scratch, frozen auditor):

```text
# after replace with commit-tree -c user.name=k -c user.email=a@x
defects [] required 1   # omission hidden — false clean
```

Canonical: `.ufo/waves/round-23/probe/probe-4fe9339f.stdout` lines 5–6 (`f3-replace-omit exit=0`).

## Merge analysis (why not fewer rows)

| Candidate merge | Verdict |
|-----------------|--------|
| F1 + F2 (both `UnicodeDecodeError` → exit 1) | **Reject.** Different code paths: lane `git log` (`round_commits`, probe F1) vs fleet `git show HEAD:…` (probe F2). One row cannot catch regressions in only one path. |
| F3 + F4 (both replace, frozen exit 0) | **Reject.** F3 hides **landed-omitted** via log subject rewrite; F4 satisfies **unresolved-full-hash** via `refs/replace/<fake>`. Post-fix oracles differ (`landed-omitted` vs `unresolved-full-hash`). |
| F5 + F4 (both cite missing 40-hex) | **Reject.** F5 adds promisor + `core.sshCommand` side channel (`MARKER CREATED` on frozen). |
| F6 as in probe.sh + C0 | **Reject for minimal grid.** Frozen observables identical to C0 (`exit=0`, `required 1`, `cutoff 2000`, `defects []` per `probe-4fe9339f.stdout` lines 1–2 and 14–15). |
| F6 rich fixture + C0 | **Keep as optional row 7** when `log.follow` is in scope (see below). |

## Minimal case table (6 rows — L1 claim a–e + control)

Shared setup: `base()` from probe (lane `round-1: work` @1000, fleet report cites `LC`, fleet report commit @2000), `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, `--rounds 1 --no-errata --json`, auditor `@ 4fe9339f…`.

| ID | Class | Fixture delta (after `base()`) | Frozen oracle (4fe9339f auditor) | Post-fix oracle (candidate hardening) | Discriminates vs |
|----|-------|--------------------------------|-------------------------------------|----------------------------------------|------------------|
| **C0** | control | none | exit **0**; JSON; `defects []`; `required 1`; `cutoff 2000`; no traceback | unchanged | all faults |
| **F1** | (a) enc-git | `cm … someone 1100 "note café"`; `git -C "$L" config i18n.logOutputEncoding ISO-8859-1` | exit **1**; stderr `UnicodeDecodeError` … `0xe9` … `_translate_newlines` | exit **2**; stderr `could-not-evaluate:` (no traceback); audit completes without verdict | C0, F2; path = lane log |
| **F2** | (b) enc-report | append `\xff\xfe bad\n` to report; fleet commit @2100 | exit **1**; stderr `UnicodeDecodeError` … `0xff` | exit **2**; `could-not-evaluate:` on report read/decode | C0, F1; path = fleet blob |
| **F3** | (c) replace-omit | `X=$(cm … 1200 "round-1: more")`; `Y=$(git … commit-tree …)`; `git replace "$X" "$Y"` (**with committer identity**) | exit **0**; `defects []`; `required 1` (false clean — second round commit omitted from population) | exit **1**; `landed-omitted` token `X`; `required 2` | C0, F4; omission channel |
| **F4** | (d) replace-fake | `FAKE=1234567890abcdef1234567890abcdef12345678`; cite in report; `git -C "$L" update-ref refs/replace/$FAKE "$LC"` | exit **0**; `defects []` | exit **1**; `unresolved-full-hash` (+ landed-unresolved) for `FAKE` | C0, F3; lookup channel |
| **F5** | (e) lazy-fetch | partialClone + promisor `origin` + `core.sshCommand "touch $M; false"`; cite `FAKE2=abcdef…abcd` in report | exit **1**; defects on `FAKE2`; **`[ -e "$M" ]` true** (command ran) | exit **1** or **2** without marker; no ssh side effect; hash stays unresolved | C0, F4; side effect + fetch |

**Row count:** 6 — smallest set that separates (a)–(e) and C0 on frozen observables above.

### Optional row 7 — F6 `log.follow` (outside L1 a–e, in probe as F6)

Probe.sh F6 (lines 50–51) is **not** minimal: frozen metrics match C0.

Use this **rich fixture** (scratch replay, frozen auditor) when testing `-c log.follow=false`:

| ID | Class | Fixture | Frozen w/ `log.follow=true` | Frozen w/ override / post-fix |
|----|-------|---------|----------------------------|------------------------------|
| **F6r** | log.follow cutoff | Report first added @1500 at `other/kama.md`; lane `round-1: between` @2000; rename to `.ufo/reports/round-1/kama.md` @2500; fleet `log.follow true` | `cutoff 1500`; `required 1`; `defects []` (false clean vs lane @2000) | `cutoff 2500`; `required 2`; `landed-omitted` for between commit |

Evidence (frozen `/tmp/kama-r23-frozen-audit.py`, rich fixture):

```text
follow    req 1 cut 1500 def []
no-follow req 2 cut 2500 def [('landed-omitted', 'c02b5d2b')]
```

## Grid runner observables (single pass per row)

| Observable | C0 | F1 | F2 | F3 | F4 | F5 |
|------------|----|----|----|----|----|-----|
| exit code | 0 | 1 | 1 | 0 | 0 | 1 |
| JSON verdict body | yes | no | no | yes | yes | yes |
| traceback in stderr | no | yes | yes | no | no | no |
| `required` | 1 | — | — | 1 | 1 | 1 |
| `defects` empty | yes | — | — | yes | yes | no |
| side marker `$M` | — | — | — | — | — | **created** |

Post-fix column: C0/F1 clean handling; F2 exit 2; F3/F4 failed verdict with distinct kinds; F5 no marker.

## Evidence commands (this seat)

| Command | Observed |
|---------|----------|
| `AUDIT=/tmp/kama-r23-frozen-audit.py bash .ufo/waves/round-23/probe/probe.sh` | F1/F2 exit 1 + traceback; F3 exit 1 (harness bug); F4 exit 0; F5 exit 1 + marker; F6 ≡ C0 metrics |
| `AUDIT=/tmp/kama-r23-frozen-audit.py bash /tmp/kama-r23-probe/probe.sh` | Same as above |
| Read `probe-4fe9339f.stdout` | F3 exit 0 when harness succeeds |
| Patched probe via `out/SimplifyWrapper/git-wrapper.patch` | F4/F5 fixed behaviour; F5 `no marker`; F3 still exit 1 until commit-tree identity fixed |

## Not verified

- Full automated grid script wired to CI (table only).
- Patched auditor oracles for F1/F2/F3 after DecodeFix/ReplaceFix land (inferred from `SimplifyWrapper.md` + partial patched probe).
- F6r post-fix with `-c log.follow=false` only (override not re-run on patched binary this seat).
- Git &lt; 2.44 `--no-lazy-fetch` fail-closed (OldGit seat).

## Files written

- `.ufo/waves/round-23/build/advice/SimplifyGrid.md` (this file)
