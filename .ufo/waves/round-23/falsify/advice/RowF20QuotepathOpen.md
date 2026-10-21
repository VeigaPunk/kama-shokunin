# Row F20-quotepath-open-range — verdict: **HOLDS** (fault real; expectation correct; no reachable same-channel variant that current gets wrong)

Attacked at lane master `245a37f69628c2c6bb29bbf17897d8fb5946c857`.
Clone: `/tmp/kama-r23w2/CloseKama22.RowF20QuotepathOpen-2` (HEAD verified equal).
Frozen blob `4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py`
→ `/tmp/kama-r23w2/frozen-audit.py`, sha256 `09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f`;
committed current auditor sha256 `f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7`.
No tool installs or updates were needed.

Axes attacked: (1) does the frozen arm really fault on this fixture; (2) is `exit 0 / []`
the semantically correct expectation, not just what current does; (3) does some near
variant of the same channel still break current (crash/flip/hang/exec); (4) is the
fault premise itself robust.

## 1. Fault premise: real and observed in the frozen arm (UTF-8 host locale)

The fixture was rebuilt by hand, not by importing the grid: two `git init -q -b master`
repos under `/tmp/kama-r23w2/f20`; lane commit `round-1: work` by `kama-shokunin` at
`@1000`; fleet commit `round-1: report` (author `fleet`, `@2000`) publishing
`.ufo/reports/round-1/kama.md` citing that lane commit; then a committed file
`.ufo/reports/caf\xe9.md` (raw 0xe9, content `x\n`) at `@2100`; then
`git config core.quotePath false`.

Observed premise (`bash /tmp/kama-r23w2/mkfix.sh /tmp/kama-r23w2/f20`):
`git ls-tree -r --name-only HEAD` hex is
`2e75666f2f7265706f7274732f636166e92e6d64…` — `caf` `e9` `.md` emitted raw, and lane
log is `kama-shokunin 1000 round-1: work`.

Frozen arm (env: `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`, all `GIT_*`
stripped, `--rounds 1- --no-errata --json`):

```
exit=1  stdout empty
stderr: Traceback … frozen-audit.py:381 in parse_rounds
          → frozen-audit.py:89 in git   (subprocess.run(..., text=True))
          → subprocess.py:1099 _translate_newlines
        UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 16
```

Current arm, same fixture and args:

```
exit=0
{"summary": {"rounds": [1], "defects": 0, "status": "clean", …}, "results": [{round 1, required 1, defects []}]}
```

The committed grid agrees (`python3 tests/report-audit/repo-state-grid.py
--case F20-quotepath-open-range --json`, run from the clone): current `1/1` faults met,
`tb 0`; frozen `0/1`, `tb 1`, kinds `unparseable`; grid exit 1 (frozen arm expected to
fail). Row builder: `tests/report-audit/repo-state-grid.py:431-446`; row:
`tests/report-audit/repo-state-grid.py:563`; open-range wiring:
`tests/report-audit/repo-state-grid.py:606-607`.

Causality checks:
- `core.quotePath=true` (default) on the same fixture: frozen `exit 0`, current `exit 0`
  — the repo-local config is the trigger, as the builder claims.
- explicit `--rounds 1` (no open range): frozen `exit 0`, current `exit 0` — the only
  crash site is the open-range `ls-tree` listing at frozen line 381 / current
  `tools/report-landing-audit.py:417-418`.
- M11 substitution (delete only `, errors="surrogateescape"` at
  `tools/report-landing-audit.py:418`, applied to a `/tmp` copy): `exit 2`,
  `could-not-evaluate: git ls-tree … output is not UTF-8`, no traceback. So the
  surrogateescape argument is load-bearing for the expected *verdict* (0 vs 2);
  the no-traceback property comes from `git()` mapping strict decode to `EvalError`
  (`tools/report-landing-audit.py:108-127`).

Grounding for the rendering: git `core.quotePath` — "If this variable is set to false,
bytes higher than 0x80 are not considered 'unusual' any more."
<https://git-scm.com/docs/git-config#Documentation/git-config.txt-corequotePath>
(same text in local `man git-config`).

## 2. The expected outcome (`exit 0`, no defect kinds) is the correct one

The odd path is not `.ufo/reports/round-<N>/<lane>.md`, so under the audit's own
contract it is not a report: ignoring it cannot drop a real report, and there is no
defect kind for "unrelated committed filename". The only real report,
`round-1/kama.md`, cites the only round commit required before its author-time cutoff
(lane `@1000` ≤ cutoff `@2000`), so there is no `landed-omitted`, and no token in the
report is unresolved. Therefore clean/0 is the only contract-consistent result.
Refusing (`exit 2`) would be a false could-not-evaluate caused by an irrelevant
artifact; reporting a defect (`exit 1`) would invent a defect kind. The expectation is
correct independent of the current implementation. (Verified current reports
`required=1`, `cutoff=2000`, `defects=[]`, `rounds=[1]`.)

## 3. Near-variant search on the same channel: none still wrong

All fixtures hand-built; both arms run as above.

| variant | frozen | current |
|---|---|---|
| v2 `core.quotePath=true`, odd raw path | exit 0 clean | exit 0 clean |
| v3 odd raw path under `.ufo/reports/round-2/oth\xe9r.md` + valid round-1 | traceback | exit 0 clean |
| v4 odd raw path, no valid report | traceback | exit 2 `no rounds selected` (designed) |
| v5 odd raw path at fleet top (`caf\xe9-other.md`) | exit 0 | exit 0 |
| v6 tree `.ufo/reports/round-1/kama.md/x` (no report blob) | exit 2 no rounds | exit 2 no rounds |
| h3 raw-byte **round subject** `round-1: caf\xe9` created via `hash-object`, cited | traceback | exit 0 clean |
| h4 same subject, uncited | traceback | exit 1 `landed-omitted` (correct) |
| h1 non-UTF-8 bytes in lane `corpus/SOURCES.md` content | traceback | exit 2 `output is not UTF-8` |
| h2 non-UTF-8 bytes in fleet report content | traceback | exit 2 `output is not UTF-8` (matches F02 policy) |
| raw 0xe9 in a repo config section header | exit 2 (git: bad config line) | exit 2 same |
| raw embedded newline in a committed path (quotePath=false) | n/a | git still C-quotes it (control chars always escaped), so `listed.split("\n")` cannot be fed a forged report line |
| explicit `--rounds 1` | exit 0 | exit 0 |

Why no same-channel variant can flip selection: with `quotePath=false` only bytes
>0x80 are unquoted; the report regex is `fullmatch` over the ASCII skeleton
`.ufo/reports/round-([0-9]+)/kama.md`, so a raw-byte line can neither match nor inject a
line. The other path-listing call, `git ls-tree branch -- corpus/SOURCES.md`
(`tools/report-landing-audit.py:248`), prints only that exact ASCII path (tree/symlink
variants yield an explicit `not a regular blob` refusal). No reachable crash, verdict
flip, hang, or program execution was found on this channel.

Adjacent residual (below the declared C1 bar, not the quotePath channel): invalid UTF-8
*content* in lane `corpus/SOURCES.md` makes current refuse with `exit 2` where a lenient
audit could treat it as legacy and return 0. Frozen tracebacks there. This is content
decoding, not path rendering, and is consistent with the project's declared exit-2
policy for invalid UTF-8 report/errata content (F02/F16).

## 4. Premise caveat (row robustness, not a fix defect)

The frozen F20 crash depends on Python's preferred encoding for `text=True`. Using a
temporary Latin-1 locale (`localedef -i en_US -f ISO-8859-1 /tmp/kama-r23w2/locales/…`,
`LOCPATH=… LC_ALL=en_US.ISO-8859-1`), the frozen arm decodes 0xe9 as a valid Latin-1
character and **also exits 0 clean** (row met for frozen). Current exits 0 under the host
UTF-8 default, `LC_ALL=C.UTF-8`, `LC_ALL=C PYTHONUTF8=0`, and the Latin-1 locale — it is
locale-independent. The grid's `env()` clears only `GIT_*` and inherits locale, so F20's
frozen-arm fault is reproducible only while the runner's preferred encoding rejects
0xe9 (true for the claimed host run). Recommendation: pin a UTF-8 subprocess encoding
(e.g. `PYTHONUTF8=1`, `PYTHONCOERCECLOCALE=0`) in the grid's `env()` if the frozen premise
must be environment-independent.

Second grid-quality note: F20's builder returns `marker=None`
(`tests/report-audit/repo-state-grid.py:446`), so the grid's `executed=0` column is
vacuous for this row; the fixture contains no program-running channel anyway.

## Not verified

- Full grid, `--selftest`, and `tests/report-audit/isolation-mutants.py` as harnesses
  (L1 scope); I only reproduced M11's exact substitution on a `/tmp` copy.
- Frozen/current under every possible preferred encoding (only UTF-8 default, C/C.UTF-8,
  C+`PYTHONUTF8=0`, and ISO-8859-1 were exercised); git < 2.45 (declared floor);
  O01/O02 and the other declared open items; the 24-mutant kill list beyond M11.
- No web source beyond the git-scm `core.quotePath` entry quoted above (I read the same
  text from local `man git-config`).

## Files written

- `.ufo/waves/round-23/falsify/advice/RowF20QuotepathOpen.md` (this report)
- `/tmp/kama-r23w2/CloseKama22.RowF20QuotepathOpen-2/` (clone, unmodified)
- `/tmp/kama-r23w2/frozen-audit.py`, `/tmp/kama-r23w2/mutant-M11.py`
- `/tmp/kama-r23w2/mkfix.sh`, `/tmp/kama-r23w2/variants.sh`, `/tmp/kama-r23w2/badsubj.py`
- fixtures/outputs under `/tmp/kama-r23w2/{f20,variants,h1..h4,locales}/`, `*.out`, `*.err`, `grid-f20.json`
