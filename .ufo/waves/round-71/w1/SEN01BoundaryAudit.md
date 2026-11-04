# SEN01BoundaryAudit — round-71 boundary and secret audit (read-only)

- Seat: SEN01BoundaryAudit (sentinel), kama lane, round-71 w1. Full evidence: `.ufo/waves/round-71/w1/SEN01BoundaryAudit/audit.md`.
- Lane tip `b43e71a8a5f22b8343e3bb95a012f65c027e540c` (= `master`); `HEAD` **detached** (`HEAD detached from 9307b15e`).
- Audit window 2026-11-03T21:36–21:41 -03:00. Read-only: no mutation, no commit, no service touched.
- Result: 5/5 items answered. 0 secret-shaped strings, 0 out-of-scope writes, 0 unit actions/serving constructs/endpoint requests.
  C2's after-state is **unproven** (tool absent during the audit) and one credibility defect (F1) needs the executor's receipt.

## 1. Waiver path — clean

```
$ git -C <lane> grep -n -- '--waive' -- ':!.ufo'
LOG.md:2681; SCORECARD.md:3710; corpus/lessons/round-70-verifier-spotcheck.md:71;
corpus/lessons/round-70.md:19; tools/round65-host-census.py:22,126,133,136,137,151,203,205   EXIT=0
```
Every non-wave hit is prose about the waiver or the census's own parser/definition — **no committed invocation**:
```
$ git grep -nE '(python3?|executable|run)[^\n]*round65-host-census\.py[^\n]*--waive' -- ':!.ufo'   → no output, EXIT=1
$ git grep -nE 'HOST_CENSUS .*waived=[1-9]' -- ':!.ufo'                                          → no output, EXIT=1
$ git grep -n 'CENSUS_WAIVE' -- ':!.ufo'                                                         → no output, EXIT=1
$ grep -n 'CENSUS_WAIVE\|os.environ\|getenv' tools/round65-host-census.py                        → no output, EXIT=1
$ git grep -oE 'round65-host-census\.py[^`|]*' -- SKILL.md LOG.md SCORECARD.md | sort -u         → `round65-host-census.py` (no flags)
```
The seat-spec's second form is unreproducible: `git grep -n -- '--waive' bs` → `fatal: ambiguous argument 'bs': unknown
revision or path not in the working tree`, EXIT=128; `ls -d bs` and `find . -maxdepth 3 -name bs` → nothing (F3).

Landed census bytes are unchanged (`git hash-object` = `git rev-parse HEAD:tools/round65-host-census.py` =
`e2929bfd8c…`; `git diff --stat` empty). Exact-name-only acceptance, quoted:
```
154:        if member_name in waive_set:              # exact MEMBERS name; a prefix/variant never matches
157:        unwaived_ne.append(member_name)           # unmatched member stays not-evaluated → exit 1
203:            print(f"warning: --waive {w!r} is not a census member name", file=sys.stderr)
205:            print(f"warning: --waive {w!r} unused: member was evaluated (…fail…); a waiver covers only not-evaluated members")
221:    return 0 if (failed == 0 and not unwaived_ne) else 1
```
Only `record_ne()` (refusal marker, budget, `OSError` spawn) consumes a waiver; pass/fail branches never call it, so a
waiver cannot remove a fail. Mis-parses are fail-closed (unknown name → warning, no effect; intended member unwaived → exit 1).

## 2. Secret scan — 0 hits

Scanner `.ufo/waves/round-71/w1/SEN01BoundaryAudit/scan.py` (sha256 `7c7341c0…f6b3a1`); population = every file under
`.ufo/waves/round-71` + the 26 inherited round-70 files (`git show --name-only b43e71a8 | grep '^\.ufo/waves/round-70/'`
→ 26); 15 patterns (`sk-`, `ghp_`/`gho_`/`github_pat_`, `op://`, `AKIA`, `xox[baprs]-`, PEM private-key header,
`Bearer <12+>`, `Authorization:`, `cookie[:=]`, `session token`, `api_key[:=]`, `secret[:=]`, `password[:=]`).
```
$ python3 /fast/scratch/hyaku/kama-r71/SEN01BoundaryAudit/scan.py   # same bytes as the preserved copy
SCAN_FILES=101 (round71=75 round70=26) PATTERNS=15 HITS=12
```
Strong-credential patterns: **0 hits**. The 4 population hits are the audit prompt's own pattern list embedded in
`w1-spec.json:114` / `w1-dispatch.json:216` (`… Authorization:, cookie, session token, private-key headers …`); the other 8 are
this audit file quoting the list. Redacted, no credential material. 26 round-70 files: 0 hits of any pattern.
Largest new artifact verified: `git-status.html` sha256 `22ff28ff…b0180` = its `.sha256` sidecar.

## 3. Write scope — 0 out-of-scope paths

`git status --porcelain -uall` at 21:39:50 (4 M + 31 wave ?? + `?? tools/pre-report-gate.py`) and at 21:40:35
(73 entries: 4 M, 67 untracked wave paths, 2 untracked tools, 1 ignored `__pycache__`). Classification:

| Path | Class | Note |
|---|---|---|
| `PROVINCE.md` | lane-expected | +20/−0 append-only (C3 corrections) |
| `SCORECARD.md` | lane-expected | +1/−1 calibration-row rewrite (see F1) |
| `corpus/SOURCES.md` | lane-expected | +2/−1 |
| `corpus/lessons/round-70.md` | lane-expected | +22/−0 append-only (KQ7 respected) |
| `.ufo/waves/round-71/**` | lane-expected | wave artifacts/receipts only |
| `tools/pre-report-gate.py`, `tools/round71-province-host-claims.py` | lane-expected | new instruments, untracked |

Nothing outside the allowed prefixes; nothing staged (`git diff --cached` empty); no write to fleet root, sibling lanes,
`.ufo/state`, `.ufo/watchdog.log`, `MANIFEST.json`, fleet scripts/templates, `~/.config`, `~/.omp`, PATH dirs, or systemd.
`.ufo/waves/round-70` is clean (`status -uall -- .ufo/waves/round-70` empty) — the freeze commit landed the 26 files.

## 4. Service / consumer boundary — 0

```
$ grep -rnE 'systemctl|launchctl|net start|sc start|service X (start|stop|restart|enable|disable)' .ufo/waves/round-71/   → no output, EXIT=1
$ grep -rnE 'http\.server|socketserver|serve_forever|\.listen\(|\.bind\(' .ufo/waves/round-71/                            → no output, EXIT=1
$ grep -rnE '8080|34113|11434' .ufo/waves/round-71/  → 4 lines: w1-spec.json:11,114; w1-dispatch.json:161,216
```
The 4 port hits are the seat constraint sentence `never contact 8080/34113/11434; …` (a prohibition in the dispatch
payload), not a request. No `requests.`/`urllib`/`http.client`/`curl`/`wget` in code; the only `https://` strings are
upstream link tags inside the two captured manual pages, which no tool reads. Process starts are local fixture drivers only
(`census-shim-control.py:47,59`; `pre-report-shortcut.py:64-66,77,82` operating **inside a scratch clone**; LAB probes import a
scratch copy in-process; `SCT01HostCensus/probe.sh:92` is `command -v systemctl`, a PATH lookup).

## 5. C2 predicate vs the landed boundary tool — tool absent

Freeze: *"`python3 tools/census-waiver-boundary.py --census tools/round65-host-census.py` prints `BOUNDARY cases=7 killed=5
survivors=0` and exits 0; it exits 1 if any named shim survives, if a waiver covers an evaluated failing member (that fixture
must exit nonzero), or if the landed census bytes are killed by mistake."*

```
$ ls -la tools/census-waiver-boundary.py
ls: cannot access 'tools/census-waiver-boundary.py': No such file or directory
$ git grep -n 'BOUNDARY cases=' -- tools/   → no output, EXIT=1
```
`EX02CensusBoundary` is live and had written no tool during the audit; the two labrat reports independently record the
same absence (`w1/LAB01WaiverProbe.md:140-142`, `w1/LAB01WaiverProbe/probe.md:176-177`). So the after-target is **unproven**:
no kill receipt exists for the five named shims (the only committed table still shows `s4/s5t/s6w/s8r/s10d … PASS (hole)`).
The census half of the sentence is enforced (§1) and its bytes are the base bytes, which satisfies the "landed bytes not
killed by mistake" side only in the sense that nothing has been changed yet. No disagreement with the freeze — a missing landing.

## Findings

| # | Sev | Evidence | Exploit path / impact | Smallest remediation |
|---|---|---|---|---|
| F1 | MED | `SCORECARD.md` calibration row (uncommitted) cites `run python3 tools/pre-report-gate.py --repo . --round 71 --tip master → PRE_REPORT round=71 arms=5 failed=0 uncommitted=0 (exit 0)`; the tool was absent when the row appeared and landed untracked at 21:39:28; the gate's arm 5 counts uncommitted `.ufo/waves/round-71` paths (`pre-report-gate.py:174-178`) and 31+ were uncommitted. | A scorer/verifier reading the score file at the wave's own landing credits calibration 7 on a run that could not have printed that line (fabricated readiness). | Re-derive that line with a receipt at the evidence commit, or drop the line until then. |
| F2 | MED | `tools/census-waiver-boundary.py` absent at 21:41:42 (last check); no `BOUNDARY` line from any tool; five shims still `PASS (hole)` in `measured/before/shim-control-table.out`. | C2's `killed=5 survivors=0` can be cited without a kill ever being observed; a waiver-swallowing shim (s6w) would go unnoticed. | Executor lands the tool and its receipt before C2 is scored; the report must not quote the after-line until it exists. |
| F3 | LOW | `git grep -n -- '--waive' bs` → `fatal: ambiguous argument 'bs'` (EXIT=128); no `bs` path. | The seat's second proof command cannot be reproduced; a reader could take the failure as a finding. | Fix the seat-spec path (the `:!.ufo` grep plus three extra greps cover the intent). |
| F4 | LOW | `HEAD` detached at `b43e71a8`; `master` also `b43e71a8`; `git symbolic-ref -q HEAD` exit 1. | A wave commit made detached advances HEAD only; `--tip master` (C1's counter and the SCORECARD line) would then grade the freeze commit as the "report tip" — a false green. | L1 commits onto `master` (or moves it) and the gate is run with the resulting commit as `--tip`. |
| F5 | INFO | 126 KB of captured HTML in `SCR02SourceRow/source/` with external `<script src>`/`<a href>` URLs; no tool reads them. | None today; a future renderer would fetch third-party resources from a lane artifact. | Keep as quoted source data only (already the case). |
| F6 | INFO | Scan: 0 real secrets in 101 scoped files; 12 pattern hits are the audit prompt and this audit quoting the pattern list. | — | — |

## Could not verify

- C2 `BOUNDARY cases=7 killed=5 survivors=0` and the five shim kills — the tool did not exist during the audit (F2).
- C1 `PRE_REPORT … failed=0 uncommitted=0` at the report tip — the gate landed mid-audit and the tip commit does not exist yet (F1).
- The actual 22-member census was not executed (read-only seat; the scout's and labrat's items own it); §1 rests on code plus
  committed round-70 receipts.
- Tool installs: none (nothing was needed).
