# SEN01BoundaryAudit — round 71 boundary and secret audit (read-only)

- Seat: SEN01BoundaryAudit (kama lane, round-71 w1, sentinel role)
- Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`
- Audit window: 2026-11-03T21:36–21:41 -03:00
- Lane tip at audit: `b43e71a8a5f22b8343e3bb95a012f65c027e540c` (= `master`), `HEAD` **detached** (`HEAD detached from 9307b15e`, `git symbolic-ref -q HEAD` exit 1)
- Wave dir: `.ufo/waves/round-71` (59 files at first scan, 75 at final scan)
- Scope: the five assigned items only. No remediation was performed; the two modified score/lesson/province
  files and the three new wave receipts belong to other seats.
- Tool installs: none.

Summary: the waiver boundary holds in code and no committed waiver invocation exists; the scoped secret scan is
clean; every working-tree path is inside the lane's expected set; the wave artifacts start no service and contact
no endpoint. Two claims could not be verified because their instruments were not landed during the audit (C2's
boundary tool absent; C1's gate landed untracked at 21:39:28, after SCORECARD already cited its output).

---

## 1. Waiver path

### 1.1 Committed `--waive` occurrences (non-wave)

```
$ cd /home/vgpnk/Projects/shokunin/kama-shokunin
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin grep -n -- '--waive' -- ':!.ufo'
LOG.md:2681:- C2 operability (a member that did not run is not a pass): `tools/round65-host-census.py`'s verdict separates `not_evaluated` from `pass` and derives its exit from it; an exact-name `--waive` covers only a not-evaluated member (a failed member is never waivable). …
SCORECARD.md:3710:| C2 — a census member that did not run is not a pass: the host census's exit is derived from the not-evaluated count | operability (held 8) | counter `python3 .ufo/waves/round-70/controls/refused-member-control.py tools/round65-host-census.py`; … an exact-name `--waive` covers only a not-evaluated member …
corpus/lessons/round-70-verifier-spotcheck.md:71:| Waiver scope | `--waive <member-name>` (repeatable, exact name); a waiver is consumed only by a not-evaluated member; `evaluated` members warn unused; unknown names warn; a waiver never covers a fail | same diff |
corpus/lessons/round-70.md:19:1. **verdict/exit coupling — a member that did not run was indistinguishable from a pass at the exit, the only field a caller reads** · … (prose)
tools/round65-host-census.py:22,126,133,136,137,151,203,205   (definition: docstring, parser, warn paths)
EXIT=0
```

Every non-wave hit is either prose about the waiver or the census's own parser/definition. There is **no committed
invocation** of the census with `--waive`:

```
$ git grep -nE '(python3?|executable|run)[^\n]*round65-host-census\.py[^\n]*--waive' -- ':!.ufo'
(no output) EXIT=1
$ git grep -nE 'HOST_CENSUS .*waived=[1-9]' -- ':!.ufo'      # a receipt proving a used waiver
(no output) EXIT=1
$ git grep -n 'CENSUS_WAIVE' -- ':!.ufo'                     # any env waiver channel
(no output) EXIT=1
$ grep -n 'CENSUS_WAIVE\|os.environ\|getenv' tools/round65-host-census.py
(no output) EXIT=1
$ git grep -oE 'round65-host-census\.py[^`|]*' -- SKILL.md LOG.md SCORECARD.md | sort -u
round65-host-census.py                                        # no flags in any documented invocation
```

The only `waived=[1-9]` receipts in the tree are round-70 synthetic fixtures
(`.ufo/waves/round-70/w1/out/CRT01ClaimC2/evidence/spawn-oserror-probe.out:14,21`,
`…/EX02CensusVerdict/demo.md:162`) whose synthetic censuses have `total=1..2`; every real 22-member
receipt carries `waived=0` or the token absent.

### 1.2 Requested second form is unreproducible

```
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin grep -n -- '--waive' bs
fatal: ambiguous argument 'bs': unknown revision or path not in the working tree.
Use '--' to separate paths from revisions, like this:
'git <command> [<revision>...] -- [<file>...]'
EXIT=128
$ ls -d bs
ls: cannot access 'bs': No such file or directory
$ find . -maxdepth 3 -name bs
(no output)
```

There is no `bs` path in the lane; the seat-spec command fails on its pathspec, not on a finding.

### 1.3 Landed census accepts exact member names only (code)

`tools/round65-host-census.py`, bytes identical to `HEAD` at audit time
(`git hash-object` = `git rev-parse HEAD:tools/round65-host-census.py` = `e2929bfd8c37c3de36603611fba539ef5b62cb7a`;
`git diff --stat -- tools/round65-host-census.py` empty):

```
133:        if cli[i] == "--waive" and i + 1 < len(cli):
134:            waive.append(cli[i + 1])
136:        elif cli[i].startswith("--waive="):
137:            waive.append(cli[i][len("--waive="):])
141:    waive_set = set(waive)
150:        # The member did not run, so there is no verdict about it: counted in
151:        # not_evaluated, waived only by an explicit --waive of its exact name.
154:        if member_name in waive_set:
155:            waived += 1
156:            return " [waived]"
157:        unwaived_ne.append(member_name)
203:            print(f"warning: --waive {w!r} is not a census member name", file=sys.stderr)
205:            print(f"warning: --waive {w!r} unused: member was evaluated "
206:                  f"({evaluated[w]}); a waiver covers only not-evaluated members",
221:    return 0 if (failed == 0 and not unwaived_ne) else 1
```

- Matching is `member_name in waive_set` over the **exact** members-table name (line 154): a prefix, a
  case variant, or a whitespace variant does not match, and the member stays in `unwaived_ne`.
- Only `record_ne()` (refusal marker, budget timeout, `OSError` spawn failure) can consume a waiver; the
  pass/fail branches never call it, so a waiver cannot remove a member from `failed`.
- Exit is `failed == 0 and not unwaived_ne` (line 221); a waiver on an **evaluated failing** member produces
  the stderr warning at 205–206 and leaves exit 1 through `failed` (`waived` stays 0).
- Unknown names only warn (line 203). The CLI parser is permissive — `--waive` consumes the next token even if
  it is another flag, and unrecognised tokens are ignored — but every mis-parse is fail-closed: it either names
  a non-member (warning, no effect) or leaves the intended member unwaived (exit 1).
- No `CENSUS_WAIVE`/env channel exists in the landed bytes; the waiver is CLI-only.

Committed empirical confirmation (round-70 critic, already in the tree, not re-run here):
`.ufo/waves/round-70/w1/out/CRT01ClaimC2/attack.md:80` — `--waive synthetic` (prefix of `synthetic-refused`) →
exit 1; `report.md:70` — waiver on an evaluated failing member → warning + exit 1.

**Conclusion 1:** no committed `--waive` usage exists in the lane; the landed census accepts only exact member
names and is fail-closed on every waiver misuse. The seat-spec's second grep (`bs`) is a path defect (EXIT=128).

---

## 2. Secret scan

Scanner (preserved, read-only): `.ufo/waves/round-71/w1/SEN01BoundaryAudit/scan.py`
(sha256 `7c7341c0c5e7f4adb5f81c6ddfb7953d6254736f98cc303f12383e5b59f6b3a1`; executed from scratch
`/fast/scratch/hyaku/kama-r71/SEN01BoundaryAudit/scan.py`, same bytes, scratch removed on exit).
Population = every file under `.ufo/waves/round-71` + the 26 inherited round-70 paths (enumerated from
`git show --name-only --format='' b43e71a8 | grep '^\.ufo/waves/round-70/'`, count = 26; list preserved at
`.ufo/waves/round-71/w1/SEN01BoundaryAudit/r70-26.txt`).
15 patterns: `sk-` (20+), `ghp_`/`gho_`/`github_pat_`, `op://`, `AKIA`, `xox[baprs]-`,
`-----BEGIN … PRIVATE KEY-----`, `Bearer <12+>`, `Authorization:`, `cookie[:=]`, `session[ _-]?token`,
`api_key[:=]`, `secret[:=]`, `password[:=]`.

```
$ python3 /fast/scratch/hyaku/kama-r71/SEN01BoundaryAudit/scan.py
HIT .ufo/waves/round-71/w1/w1-dispatch.json:216 [authorization-header] Author<redacted>
HIT .ufo/waves/round-71/w1/w1-dispatch.json:216 [session-token] sessio<redacted>
HIT .ufo/waves/round-71/w1-spec.json:114 [authorization-header] Author<redacted>
HIT .ufo/waves/round-71/w1-spec.json:114 [session-token] sessio<redacted>
SCAN_FILES=85 (round71=59 round70=26) PATTERNS=15 HITS=4
PATTERN openai-sk hits=0
PATTERN github-ghp hits=0
PATTERN github-gho hits=0
PATTERN github-pat hits=0
PATTERN 1password-op hits=0
PATTERN aws-akia hits=0
PATTERN slack-xox hits=0
PATTERN pem-private-key hits=0
PATTERN bearer-token hits=0
PATTERN authorization-header hits=2
PATTERN cookie-header hits=0
PATTERN session-token hits=2
PATTERN api-key-assign hits=0
PATTERN secret-assign hits=0
PATTERN password-assign hits=0
```

All four hits are the **audit instruction text itself**, embedded in the fleet's dispatch payload:

```
$ grep -oE '.{80}(Authorization:|session token).{80}' .ufo/waves/round-71/w1-spec.json
d round-70 files for secret-shaped strings (`sk-`, `ghp_`, `op://`, `Bearer `, `Authorization:`, `cookie`, `session token`, private-key headers). Report hits (path:line, reda
```

Classification: false positive (the seat's pattern list), redacted above; no credential material. Count of
real hits across both scoped populations: **0**. The 26 round-70 files contribute 0 hits of any pattern.

Re-run at audit close (2026-11-03T21:40:32, wave grew to 75 files):

```
SCAN_FILES=101 (round71=75 round70=26) PATTERNS=15 HITS=12
```

The 8 added hits are all inside this audit file itself (`SEN01BoundaryAudit/audit.md:121,127,129,142,151,152` —
the auditor quoting the pattern list and the earlier HIT lines). Excluding the auditor's own artifact the
population result is unchanged: 4 hits, all the seat prompt's pattern list, 0 credential material.

Supporting SHA check on the largest new artifact (100 KB captured manual page):
`sha256sum .ufo/waves/round-71/w1/SCR02SourceRow/source/git-status.html` =
`22ff28ff73f83696c4a503e9c92e7a15f4ded2f91d96cc5668ee79db0a1b0180`, matching its `.sha256` sidecar.

Supplementary (outside the assigned populations, informational): a `git grep` of the whole tracked tree for the
strong patterns shows only historical placeholder tokens — `Bearer no-key` in upstream llama.cpp READMEs,
`Bearer kamatest`/`wrong-key-here` in rounds 18/26 test receipts. No live-looking credential anywhere.

**Conclusion 2:** 0 secret-shaped strings in the scoped populations (4 redacted false positives, all the audit
prompt's own pattern list).

---

## 3. Write scope

```
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain -uall      (2026-11-03T21:39:50 ±5 s)
 M PROVINCE.md
 M SCORECARD.md
 M corpus/SOURCES.md
 M corpus/lessons/round-70.md
?? .ufo/waves/round-71/w1-spec.json
?? .ufo/waves/round-71/w1.ready
?? .ufo/waves/round-71/w1.ready.dispatched
?? .ufo/waves/round-71/w1/LAB01WaiverProbe.md
?? .ufo/waves/round-71/w1/LAB01WaiverProbe/census-probe.copy.py
?? .ufo/waves/round-71/w1/LAB01WaiverProbe/probe-extra.out
?? .ufo/waves/round-71/w1/LAB01WaiverProbe/probe-extra2.out
?? .ufo/waves/round-71/w1/LAB01WaiverProbe/probe-extra3.out
?? .ufo/waves/round-71/w1/LAB01WaiverProbe/probe-identity.out
?? .ufo/waves/round-71/w1/LAB01WaiverProbe/probe-run.out
?? .ufo/waves/round-71/w1/LAB01WaiverProbe/probe.md
?? .ufo/waves/round-71/w1/LAB01WaiverProbe/probe_extra.py
?? .ufo/waves/round-71/w1/LAB01WaiverProbe/probe_harness.py
?? .ufo/waves/round-71/w1/SCR02SourceRow/receipts/census-after.out
?? .ufo/waves/round-71/w1/SCR02SourceRow/receipts/census-before.out
?? .ufo/waves/round-71/w1/SCR02SourceRow/receipts/census-mirror3.out
?? .ufo/waves/round-71/w1/SCR02SourceRow/receipts/ids_intersection.txt
?? .ufo/waves/round-71/w1/SCR02SourceRow/receipts/ids_lane.txt
?? .ufo/waves/round-71/w1/SCR02SourceRow/receipts/ids_merge.txt
?? .ufo/waves/round-71/w1/SCR02SourceRow/receipts/ids_merge_only.txt
?? .ufo/waves/round-71/w1/SCR02SourceRow/receipts/ids_union.txt
?? .ufo/waves/round-71/w1/SCR02SourceRow/source/git-status.html
?? .ufo/waves/round-71/w1/SCR02SourceRow/source/git-status.html.sha256
?? .ufo/waves/round-71/w1/SCR02SourceRow/source/pytest-exit-codes.html
?? .ufo/waves/round-71/w1/SCT01HostCensus/census-raw.out
?? .ufo/waves/round-71/w1/SCT01HostCensus/pipe-checkout.out
?? .ufo/waves/round-71/w1/SCT01HostCensus/pipe-test.sh
?? .ufo/waves/round-71/w1/SCT01HostCensus/probe.sh
?? .ufo/waves/round-71/w1/swarm-registry.json
?? .ufo/waves/round-71/w1/validate.err
?? .ufo/waves/round-71/w1/w1-dispatch.json
?? tools/pre-report-gate.py
```

Classification (allowed set: `.ufo/waves/round-71/`, `tools/`, `plans/`, `corpus/`, `registry/`, `SKILL.md`,
`SCORECARD.md`, `LOG.md`, `PROVINCE.md`):

| Path | Class | Note |
|---|---|---|
| `PROVINCE.md` | lane-expected | +20/−0 append-only (C3 corrections block) |
| `SCORECARD.md` | lane-expected | +1/−1 in-place rewrite of the calibration row (see F1) |
| `corpus/SOURCES.md` | lane-expected | +2/−1 (S-row for the new source) |
| `corpus/lessons/round-70.md` | lane-expected | +22/−0 append-only (KQ7 respected) |
| 31 untracked paths under `.ufo/waves/round-71/` | lane-expected | wave artifacts, seat reports, receipts |
| `tools/pre-report-gate.py` | lane-expected | 755, 21192 B, untracked; C1 instrument landing |

**Out-of-scope paths: 0.** At audit close (2026-11-03T21:40:35) status counted 73 entries — 4 modified
(`PROVINCE.md`, `SCORECARD.md`, `corpus/SOURCES.md`, `corpus/lessons/round-70.md`), 67 untracked paths under
`.ufo/waves/round-71/`, and 2 untracked tools (`tools/pre-report-gate.py`, `tools/round71-province-host-claims.py`);
one ignored `__pycache__/` under `RVW01C2Attack/shims` accounts for the file-count/status-count difference. Every
path stays inside the allowed prefixes. No writes to the fleet root, sibling lanes, `.ufo/state`,
`.ufo/watchdog.log`, `MANIFEST.json`, fleet `scripts/`/`templates/`, `~/.config`, `~/.omp`, PATH dirs, or
systemd. `git diff --cached --name-only` is empty (nothing staged). The landed census and all
`.ufo/waves/round-70` bytes are unmodified (`git status --porcelain -uall -- .ufo/waves/round-70` empty).

---

## 4. Service / consumer boundary

Wave dir, all files, three greps (2026-11-03T21:40 -03:00):

```
$ grep -rnE 'systemctl|launchctl|net[[:space:]]+start|sc[[:space:]]+start|service[[:space:]]+[A-Za-z0-9_.@-]+[[:space:]]+(start|stop|restart|enable|disable)' .ufo/waves/round-71/
(no output) EXIT=1

$ grep -rnE 'http\.server|socketserver|serve_forever|\.listen\(|\.bind\(' .ufo/waves/round-71/
(no output) EXIT=1

$ grep -rnE '8080|34113|11434' .ufo/waves/round-71/
.ufo/waves/round-71/w1-spec.json:11
.ufo/waves/round-71/w1-spec.json:114
.ufo/waves/round-71/w1/w1-dispatch.json:161
.ufo/waves/round-71/w1/w1-dispatch.json:216
```

The four port hits are inside the seat constraint sentence
`never contact 8080/34113/11434; no credential, token, cookie or session material anywhere` (a prohibition,
carried verbatim in the dispatch payload) and the audit item text. **Requests to those ports: 0.**

Network calls: `requests.` / `urllib.request` / `http.client` / `socket.create_connection` / `curl` / `wget` —
0 hits in code. The only `https://` strings are inside the two captured upstream documentation pages
(`SCR02SourceRow/source/git-status.html:3253-3254` jQuery CDN `<script src>`, `pytest-exit-codes.html` Sphinx/Furo
links); no lane tool reads those HTML files (`grep -rn 'pytest-exit-codes\|SCR02SourceRow\|git-status\.html'
tools/` → no output, EXIT=1). They are data, not fetch instructions.

Process starts (local, no service): `subprocess.run` in
`.ufo/waves/round-71/controls/census-shim-control.py:47,59` (python on two local fixture drivers; writes only
`--scratch`) and `pre-report-shortcut.py:64-66,77,82` (git clone/checkout/update-ref/status **in the scratch
clone**, `repo = scratch/fixture`, so no lane ref is moved; then the four instruments in the clone).
`LAB01WaiverProbe/probe_harness.py:16-18` and `probe_extra.py:12-14` import a scratch copy of the census
in-process (no spawn). `SCT01HostCensus/probe.sh:92-93` runs `command -v systemctl` — a PATH lookup, not a
unit action. No `kill`/`pkill`, no `nohup`, no daemon, no listening socket.

**Conclusion 4:** 0 unit actions, 0 serving constructs, 0 requests to 8080/34113/11434. The only process
starts are local fixture drivers under scratch with argv containing no endpoint.

---

## 5. Freeze C2 predicate vs the landed boundary tool

Freeze sentence (`plans/round-71-claims.md`, §C2):

> **Predicate:** `python3 tools/census-waiver-boundary.py --census tools/round65-host-census.py` prints
> `BOUNDARY cases=7 killed=5 survivors=0` and exits 0; it exits 1 if any named shim survives, if a
> waiver covers an evaluated failing member (that fixture must exit nonzero), or if the landed census bytes are
> killed by mistake.

Landed state at audit close:

```
$ ls -la tools/census-waiver-boundary.py
ls: cannot access 'tools/census-waiver-boundary.py': No such file or directory
$ ls tools/ | grep -E 'census|pre-report|province|round71'
error-verdict-census.py
hexrun-census.py
round65-host-census.py
round65-province-host-audit.py
```

The tool is **absent**; seat `EX02CensusBoundary` (executor, operability) is live and had written nothing to
`tools/` during the audit. No tool has ever emitted a `BOUNDARY` verdict line: every `BOUNDARY cases=` string in
the tree is prose — the freeze text, the dispatch prompts, this audit, and the two labrat notes that say the
line was *not* executed (`w1/LAB01WaiverProbe.md:141`, `w1/LAB01WaiverProbe/probe.md:176`).
`git grep -n 'BOUNDARY cases=' -- tools/` → no output (EXIT=1).

What *is* verifiable is the census-side semantics the sentence rests on (§1.3): exact-name membership,
waiver consumed only by `record_ne`, `failed` never reduced by a waiver, exit `failed==0 and not unwaived_ne`.
The five named shims the tool must kill are the five round-70 holes in the frozen control table
(`.ufo/waves/round-71/measured/before/shim-control-table.out`: `s4-refusal-as-fail`, `s5t-hardcoded-total`,
`s6w-waiver-swallows-failure`, `s8r-second-call-silent`, `s10d-refusal-branch-deleted`; all `PASS (hole)`),
and the nine shims exist at `/fast/scratch/hyaku/kama-r71/l1/shims` (9 `.py` files) matching
`census-shim-control.py`'s `SHIMS` list of 5.

**Conclusion 5:** the landed boundary **tool** does not exist, so the freeze's after-target
(`BOUNDARY cases=7 killed=5 survivors=0`, exit 0) is unproven at this timestamp; the sentence is not
contradicted by the census, which enforces the waiver half of it. The shim-kill half is exactly what the missing
tool must demonstrate. No disagreement with the freeze — a missing landing, not a changed rule.

---

## Findings

**F1 — MEDIUM (credibility/fabricated readiness, calibration row).** `SCORECARD.md` (uncommitted, +1/−1) claims
the C1 after-state before it can exist:

```
$ git diff -- SCORECARD.md
+| calibration | **7** | … run `python3 tools/pre-report-gate.py --repo . --round 71 --tip master` → `PRE_REPORT round=71 arms=5 failed=0 uncommitted=0` (exit 0); …
```

At 21:39:22 the row was already present (`git status -sb` → ` M SCORECARD.md`, 26-entry status) and
`tools/pre-report-gate.py` was not in the worktree (`ls tools/ | grep -E 'census|pre-report|province|round71'`
listed only the four pre-existing tools); the file landed untracked at `2026-11-03 21:39:28` (21192 B, mode 755).
The gate's own arm 5 counts uncommitted paths under `.ufo/waves/round-71` (`pre-report-gate.py:174-178`), and
31 wave paths were uncommitted at the 21:39:50 snapshot (67 at audit close), so no run at this worktree state can
print `uncommitted=0`. Least fix: re-derive that line with a receipt at the evidence commit (or drop it until
then) — the row must not cite an unexecuted run.

**F2 — MEDIUM (unproven claim, expected in-flight).** C2's `tools/census-waiver-boundary.py` is absent, so
`cases=7 killed=5 survivors=0` has no receipt and the five named shims still read `PASS (hole)` in the only
committed control table. No action by me; the executor owns the landing and the kill evidence.

**F3 — LOW (seat-spec defect).** `git grep -n -- '--waive' bs` exits 128: no `bs` path exists in the lane. The
intent is covered by the `:!.ufo` grep plus the three additional greps in §1.1.

**F4 — LOW (landing hazard, calibration).** The lane is on a **detached** HEAD at `b43e71a8`
(`HEAD detached from 9307b15e`; `master` also `b43e71a8`; `git symbolic-ref -q HEAD` exit 1). A wave commit made
here advances HEAD only, leaving `master` at the freeze commit — while C1's counter and the SCORECARD row use
`--tip master`, which would then grade the wrong tip. L1 should commit onto `master` (or move it) for the
evidence commit.

**F5 — INFO.** The wave now carries 126 KB of captured upstream HTML
(`SCR02SourceRow/source/git-status.html` 100062 B, `pytest-exit-codes.html` 25787 B) containing external
`<script src>`/`<a href>` URLs. No tool consumes them, so no request is issued; a future renderer of these files
would fetch third-party resources — keep them as quoted source data only.

**F6 — INFO.** Secret scan: 0 real hits in 101 scoped files (75 round-71 + 26 round-70 at 21:40:32); 4 matches are
the audit prompt's own pattern list inside `w1-spec.json`/`w1-dispatch.json`, and 8 more are this audit file
quoting that list — no credential material.
