# ConnClosureLearning — kama r20–r22 closure routes into round 23

Seat: `CloseKama22.ConnClosureLearning` (leaf; no dispatch, no REA devices, no installs).
Lane base: `kama-shokunin@4fe9339f8fc3a4a4a479d9c938a850da12f1124d`.
Manifest pin: `/home/vgpnk/Projects/shokunin/MANIFEST.json`, sha256
`3f65273c8071d2def0f2f778d60d5fa777864149ff22f202bc781d7cd5c26747`, 812094 bytes,
421 round entries; access date 2026-10-21 (read-only).

Entries read and identity-asserted: `rounds[397]` (r20), `rounds[406]` (r21),
`rounds[418]` (r22) — all `lane=="kama"`, `type=="closure"`, `admitted=true`.
No kama round-23 closure entry exists yet (all 421 entries scanned for
`round==23` with `kama`; none).

Complete route table: `out/ConnClosureLearning/closure-routes.json` (34 items;
every quote assert-checked as a verbatim substring of the named field by
`out/ConnClosureLearning/extract-closure-routes.py`). The appendix below lists
every item with its exact JSON field path.

## 1. The one route r23 must address

**`rounds[406].notes`** — r21 routed D4: “late C1EnvSentinel identifies
unintegrated repository-local Git-config/history trust hardening and
UTF-8/error/top-level handling; do not use audit on untrusted repos until
hardened”.

This is the declared r23 C1, and r22 did not discharge it: r22 only narrowed
use — fleet `.ufo/reports/round-22/kama.md:24-27` says it “explicitly restricted
the audit to trusted repositories rather than claiming D4 hardening”, and `:201`
still lists “D4 report-audit hardening” under remaining frontier. The committed
blob at 4fe9339 has no isolation flags at all (`git show
HEAD:tools/report-landing-audit.py | grep -n "no-replace-objects\|no-lazy-fetch"`
returned no matches).

Premise, verified in the frozen blob: `tools/report-landing-audit.py:80-81`
claims “neither the audited repos nor the selftest fixtures can be redirected”,
while `:89-90` runs git with `text=True` and `:97` returns stdout. A
`UnicodeDecodeError` raised at `:89-90` is a `ValueError`, not `EvalError` or
`OSError`, so it escapes the top-level handler (`:835-843`) as a traceback
exit 1 — an error becomes a verdict. The round must therefore (a) fix only the
measured channels, (b) present D4 as narrowed, not closed, and (c) keep “do not
use on untrusted repos” for every unmeasured channel.

## 2. Must be explicitly carried (open)

- **R21-SELFTEST-DEBT** — `rounds[406].notes`: “Late C1SelftestReview's vacuous
  uncommitted-now fallback and crash-only GIT_DIR assertion remain test debt,not
  failure of committed11-report result.” The weak forms are still at
  `tools/report-landing-audit.py:779-780` (asserts only `rc==0` and
  `not report_committed`) and `:804-805` (asserts only that the decoy bare
  object list is unchanged). r23 edits this exact `selftest()`/`git_env()`
  surface and adds cases, so it must fix or explicitly carry both. Counts are
  round-specific: r21 recorded `selftest:36` at 7054dba1
  (`rounds[406].verification.rechecks`); the r22 base 4fe9339 is 50
  (`advice/SimplifyWrapper.md:46-47`, re-verified below: `cases=50 failed=0`
  for frozen and worktree copies). If the post-change count stays 50, say that
  no selftest case was added; otherwise report `50+N/0`. “Unchanged 50/50” may
  describe only the frozen baseline.
- **R21-DEBT** — `rounds[406].notes`: “Remaining prelaunch-snapshot race,41-hop
  gate bound,JSON duplicate-key/Unicode edge cases and overbroad any-str-map
  injectivity docstring are routed debt outside static flat-tree count; no
  execution-authentication claim admitted.” Strict decoding must not be
  presented as closing the JSON/Unicode item.
- **R20-LIMITS** — `rounds[397].notes`: “Honest limits, not scope shrink:
  v3-all-scalars 12 test.* values not individually compared …; full 42-run R18
  survivor measure not rerun …; timeout reason precision unclaimed (2
  diagnostic mutation survivors, class boundary intact).”
- **R20-L0 / R21-L0** — `rounds[397].notes` “L0 kama|round-17 llama archive
  question still open.”; `rounds[406].notes` “Existing round16
  fixture-ratification and round17 retained-archive L0 remain operator-owned.”
- Residual of **R21-D4** — the audit is still not authorized on untrusted
  repositories outside the finite measured grid (replace refs, promisor lazy
  fetch, `i18n.logOutputEncoding`, `log.follow`, strict decode). Channels with
  r23 scout assignments (showSignature/`gpg.program`, mailmap, includeIf,
  fsmonitor/hooks, safe.directory, notes, object-format) are unverified until
  those seats report; the claim must not imply they are hardened.

## 3. Invariants the r23 measurement must reproduce

- **R20-CENSUS** `rounds[397].verification.rechecks`: error census
  `frozen exit1 cells15 frozen_misclassified6 …; --arm current exit0
  current_misclassified0 unrun[]`. r23's no-harm recipe includes the error
  census, so current must stay 0/15 with unrun[].
- **R21-LEDGER** `rounds[406].verification.rechecks`: no-errata run
  `--rounds10-20 … exit1:11 reports,9 defects (8 omissions+1 unresolved full
  hash),42 required/4 post-report commits`; errata run `exit0
  corrected9/uncorrected0, invalid0/unmatched0`. Both are expected states.
  “Clean ledger” means errata mode; no-errata exit 1 is not a failure.
- **R22-LEDGER** `rounds[418].verification.rechecks`: `--rounds 10-21 --report
  22=<fleet report> --fleet-repo <fleet> --json exit0, stderr empty: status
  clean, 13 reports, defects9/corrected9, uncorrected0, errata
  invalid/unmatched0, required54, post-report5; round22 0 defects, required5,
  source_url_hashes [704366d7]`. At r23 the shape becomes `--rounds 10-22
  --report 23=…` = 14 reports; `required`/`post-report` and the new
  `source_url_hashes` list must be re-derived, not copied.
- **R21-SOURCES / R22-SOURCES**: SOURCES stays append-only (`appended,0
  violations`), `sources-census validate kama` exit 0 with W04 duplicate-URL
  warnings only, `missing0`. Row/tier/status counts grow each round (74 at r21,
  88 at r22) and are not invariants.
- **R22-NOHARM** `rounds[418].verification.axis_harm`: the full recipe — links
  grid, receipt gate/mutations, legacy receipts, GGUF, citation, error census,
  snapshot, prelaunch refusal, historical audit ledger, sources-unchanged — all
  at expected exits, plus an honest frontier disclosure. r22 recorded “frontier
  rows unchanged (0 advanced) as disclosed”; r23 may deepen D4 without claiming
  a row advance (r22 report `:198` and `:201`).
- **R22-CONFORMANCE** `rounds[418].verification.conformance`: report sections in
  order — Work performed, Landed changes, Before→after, Sources & frontier,
  Trend verdicts, SHONEN, Swarm/limits, Final report audit; cited commits
  ancestors of HEAD; report commit an ancestor of fleet HEAD; lane HEAD equals
  origin/master for the measured state.
- **R22-PORCELAIN** `rounds[418].verification.conformance`: “Lane HEAD =
  origin/master = 4fe9339f after fetch; lane porcelain empty.” At this seat's
  read the worktree is no longer clean (see contradiction 2); the measured
  “current” must be a committed, pinned state.
- **R21-CATFILE** `rounds[406].verification.spotcheck`: `cat-file -e` is
  rejected as the missing/error distinction; `--batch-check` stays the oracle.
  `--no-lazy-fetch` is documented as the probing companion, but `-e` must not
  replace the batch distinction.
- **R22-SPOTCHECK** `rounds[418].verification.spotcheck`: Python `OSError`
  language for open failures is agreed; a decode failure is
  `UnicodeDecodeError` (a `ValueError`, not `OSError`). Keep the prose distinct.
- **R22-VERDICTS / R22-DISCERNMENT**: operability is 8 and unchanged; r23's
  claim is calibration at 7. `discernment` improved narrowly in r22 and must not
  regress by admitting unmeasured channels as hardened.
- **R22-SCALAR / R22-SCALAR-AFTER / R22-COMPONENTS**
  `rounds[418].claims.C1`: `scalar_before=7`, `scalar_after=7`, and the
  component shape `{before:0, after:18, of:18}`. State both scalars and a
  before/after/of component table; “improved” never implies a raised scalar.
- **R20-RECEIPTS / R21-RECEIPTS**: committed command receipts reconcile
  (stdout sha256, stderr hashes, `.exit` files, expected exits) — 21/21 at r20,
  33/33 at r21.
- **R22-SWARM / R22-TOOLS**: report original deaths, resumes and retained
  reports separately (r21 routed a stale “still-running” description as a
  defect); record any install/update (r22 recorded none).

## 4. Closed in r22 — do not reopen

- **R20-D1/D2** (`rounds[397].notes`): the spliced 0957ce61 hash and the four
  omitted r20 commits. Corrected by five rows of
  `registry/report-landing-errata.tsv` (9 data rows total; 5 round-20 rows,
  3 round-18 rows, 1 round-10 row).
- **R21-D1/D2/D3** (`rounds[406].notes`): SCORECARD measured-record lag,
  CORPUS correction rows, two-death/66-falsify accounting. r22 appended the
  SCORECARD correction at `SCORECARD.md:1056` and reports nine correction rows
  (`/home/vgpnk/Projects/shokunin/.ufo/reports/round-22/kama.md:24-27`).
- **R21-C2-CLOSED** (`rounds[406].notes`): the digest sentinel was against an
  older commit; final code covers it. No r23 action.

## 5. Contradictions and disagreements (stated, not smoothed)

1. **D4 “addressed” vs carried.** r21 says “do not use audit on untrusted repos
   until hardened”; r22 only limited use to trusted repositories; r23's Context
   says its own change is “NOT general untrusted-repository hardening”. A report
   that says “D4 fixed” would contradict `rounds[406].notes`,
   `rounds[418].verification.rechecks` and the round's own scope statement.
2. **“Current” is not a clone of base.** The lane HEAD blob is the frozen
   version (`git rev-parse HEAD:tools/report-landing-audit.py` =
   `fcc255ce5115a749dfbd09cf992ba9851a2dc90a`), while the checked-out worktree
   file is `b2844396fb44a8cb600396c23f91dea61fa634cb` with
   `git --no-optional-locks diff --stat` = “1 file changed, 26 insertions(+),
   9 deletions(-)”. A `git clone --no-hardlinks` of the lane at 4fe9339 yields
   the frozen blob. Any seat told to clone base cannot measure “current”; the
   measured current must name its commit/blob. (A longer self-identifying grid
   output is the cheapest fix; the probe transcript below does not pin `AUDIT`.)
3. **Two in-round variants disagree.** SimplifyWrapper's patch post-image is
   `adba7a60d68c978ebe71eaf393310643baa68343` (applied to a frozen copy in
   `/tmp`); the lane worktree is `b2844396…`. Differences:
   (i) the patch keeps the false `git_env` docstring (patch:17-18) — the exact
   overclaim C1 cites — while the worktree corrects it (worktree:89-91);
   (ii) the patch adds env `GIT_NO_REPLACE_OBJECTS`/`GIT_NO_LAZY_FETCH`
   (patch:21-22), the worktree relies on argv only;
   (iii) the patch returns raw `decode("utf-8")` (patch:44), the worktree
   restores universal newlines (worktree:114);
   (iv) the worktree encodes any non-None stdin (worktree:102), so a bytes
   caller would raise an uncaught `AttributeError`; the patch guards with
   `isinstance(stdin, str)` (patch:27-28).
4. **Parity claim vs evidence.** `advice/SimplifyWrapper.md:10` says “Valid
   UTF-8 control paths unchanged”; dropping `text=True` drops line-ending
   conversion. Python documents: “For stdout and stderr, all line endings in the
   output will be converted to `'\n'`.”
   (https://docs.python.org/3/library/subprocess.html, page “subprocess —
   Subprocess management — Python 3.15.1 documentation”, accessed 2026-10-21).
   My CRLF control probe found **no verdict change** (section 7), so this is a
   latent/unverified parity gap, not a demonstrated fault: narrow the wording or
   restore normalization.
5. **Selftest count semantics.** r21 recorded 36; r22 base is 50; r23 adds
   cases. “Existing selftest 50/50 unchanged” is true only of the frozen
   baseline; a current count must be stated separately.
6. **Ledger has two legitimate modes.** No-errata exit 1 with 9 defects and
   errata exit 0 with corrected9 are both correct (`rounds[406]` vs
   `rounds[418]`). r23 must not “fix” history by editing reports (append-only)
   or by changing the expected historical count.
7. **“Improved” ≠ scalar.** r20/r21 were “improved” at 7→7; r22 made
   `scalar_before/after` explicit. r23 must state 7→7 unless a scalar is
   actually earned.
8. **Frontier.** r22 report `:198` says 0 rows advanced and `:201` lists D4 as
   remaining frontier. r23's narrow D4 movement should be disclosed as
   deepening/correction with 0 row advances unless a named row is added.

## 6. One bounded move (godspeed)

**Union the two `git()` variants and make the isolation docstring true.**

1. Keep the centralized argv prefix `_GIT_PREFIX` (patch:9-13) and add the env
   `GIT_NO_REPLACE_OBJECTS=1` / `GIT_NO_LAZY_FETCH=1` (patch:21-22). Local git
   2.56.0 documents `--no-lazy-fetch`: “Do not fetch missing objects from the
   promisor remote on demand.” and “It is equivalent to setting the
   `GIT_NO_LAZY_FETCH` environment variable to `1`.”
   (`/usr/share/man/man1/git.1.gz`, accessed 2026-10-21; `--no-replace-objects`
   is likewise equivalent to `GIT_NO_REPLACE_OBJECTS`).
2. Replace the frozen `git_env` docstring (`tools/report-landing-audit.py:80-81`)
   with the worktree wording (worktree:89-91). This is the claim's own cited
   overclaim; the simplify patch leaves it in place, so integrating that patch
   alone cannot support “docstring corrected”.
3. Guard stdin with `isinstance(stdin, str)` before encoding (patch:27-28) so a
   bytes caller cannot raise an uncaught `AttributeError` (another
   error-as-verdict path).
4. Restore text-mode line-ending conversion in the strict-decode return:
   `return out.replace("\r\n", "\n").replace("\r", "\n")` (worktree:114), which
   matches the documented `text=True` behavior.
5. Optional: carry the `git show` error-context change (worktree:285-286). No
   selftest asserts the old text (`grep` found none), but it is not required by
   the claim.

Axis effects (declare honestly):

- **Calibration (7):** improves — the isolation docstring becomes true, and
  “valid UTF-8 controls unchanged” becomes true by construction rather than
  unverified. Scalar stays 7 unless separately earned.
- **Operability (8):** no harm — same exit-2 typing; stdin guard removes a
  traceback path; selftest 50/50 verified on both variants.
- **Simplicity:** +3 lines over the simplify patch; still one wrapper.
- **Verification:** resolves the two-variant contradiction only if the
  integrated state is committed and pinned.

Risks:

- The worktree variant's provenance is unobserved; L1 must author/commit the
  union through the normal integration path, not adopt an anonymous worktree.
- One extra copy of git stdout for `.replace` (bounded).
- My probes did not produce a CRLF verdict flip. If clause 4 is rejected, narrow
  the report wording to “valid UTF-8 controls without CR/CRLF”; do not claim
  universal parity.
- If the simplify patch is integrated alone, the report cannot claim the
  `git_env` docstring overclaim is corrected.

## 7. Verification this seat ran (observed)

- `python3 extract-closure-routes.py closure-routes.json` →
  `wrote … items=34 counts={'address-now': 1, 'carry-explicitly': 2, …}`;
  every quote passed an in-script verbatim-substring assertion.
- Selftest, frozen and worktree copies in
  `/tmp/kama-r23/ConnClosureLearning/` with `GIT_CONFIG_GLOBAL=/dev/null
  GIT_CONFIG_NOSYSTEM=1`: both printed `selftest cases=50 failed=0`, exit 0.
- Blob pins: frozen `fcc255ce5115a749dfbd09cf992ba9851a2dc90a`; patch
  post-image `adba7a60d68c978ebe71eaf393310643baa68343`; worktree
  `b2844396fb44a8cb600396c23f91dea61fa634cb`.
- CRLF control probe (fresh `/tmp` lane+fleet repos, CRLF-committed report):
  clean citation → frozen and worktree both exit 0, `defects []`; fabricated
  40-hex citation → both exit 1 with identical `[('unresolved-full-hash',
  'aaaaaaaaaa'), ('landed-unresolved', 'aaaaaaaaaa')]`. LF variants behaved
  identically. No verdict flip observed.
- Docs/evidence quotes above (Python subprocess page; git 2.56.0 man page),
  accessed 2026-10-21.

Not a pass: `probe-4fe9339f.exit` contains `exit=0` from the script's trailing
`echo`, not a fault outcome; `probe.sh` reads `AUDIT` from the environment and
records no blob identity, so its transcript does not pin the frozen arm (its
stdout is consistent with frozen: f1/f2 traceback exit 1, f3/f4 exit 0 false
clean, f5 marker created).

## 8. Not verified by this seat

- The five-fault grid (a–e) against either candidate; GridHarness / DecodeFix /
  ReplaceFix / LazyFetchFix own it.
- The historical ledger against the real lane/fleet repos (fixtures stay in
  `/tmp`; HistoricalNoHarm owns it).
- git < 2.56 behavior (OldGitFloor owns the floor); only local 2.56.0 docs read.
- Who/what produced the uncommitted lane worktree change, or whether it is a jj
  working-copy commit; only git-observed blob state is reported.
- Other seats' results. Channel names in section 2 come from the assignment
  roster, not from completed reports.
- No REA devices, no installs, no network beyond the Python docs page.

## Appendix — every extracted route (exact JSON field path)

| ID | manifest path | disposition | r23 action |
|---|---|---|---|
| R20-D1 | `rounds[397].notes` | closed-in-r22 | errata row; keep corrected9 |
| R20-D2 | `rounds[397].notes` | closed-in-r22 | 4 errata rows; don't reopen |
| R20-LIMITS | `rounds[397].notes` | carry-explicitly | restate unclaimed |
| R20-L0 | `rounds[397].notes` | carry-operator-owned | operator-owned |
| R20-CENSUS | `rounds[397].verification.rechecks` | invariant | current misclassified0/15 |
| R20-SCOPE | `rounds[397].notes` | scope-precedent | finite cells; 7->7 |
| R20-RECEIPTS | `rounds[397].verification.rechecks` | invariant | reconcile 21/21 receipts |
| R21-D4 | `rounds[406].notes` | address-now | r23 C1; narrow |
| R21-D1 | `rounds[406].notes` | closed-in-r22 | SCORECARD append fixed |
| R21-D2 | `rounds[406].notes` | closed-in-r22 | 9 correction rows; preserve |
| R21-D3 | `rounds[406].notes` | closed-in-r22 | death accounting accurate |
| R21-SELFTEST-DEBT | `rounds[406].notes` | open-test-debt | fix or carry; report counts |
| R21-C2-CLOSED | `rounds[406].notes` | closed | no action |
| R21-DEBT | `rounds[406].notes` | carry-explicitly | carry; no exec-auth |
| R21-L0 | `rounds[406].notes` | carry-operator-owned | operator-owned |
| R21-LEDGER | `rounds[406].verification.rechecks` | invariant | both modes at r23 head |
| R21-NOHARM | `rounds[406].verification.rechecks` | invariant | census/witness unchanged |
| R21-SOURCES | `rounds[406].verification.rechecks` | invariant | append-only; missing0 |
| R21-RECEIPTS | `rounds[406].verification.rechecks` | invariant | receipt reconciliation |
| R21-CATFILE | `rounds[406].verification.spotcheck` | invariant-knowledge | batch-check stays |
| R22-SCOPE | `rounds[418].claims.C1.scope` | scope-precedent | mirror narrow scope |
| R22-SCALAR | `rounds[418].claims.C1.scalar_before` | invariant | state 7 |
| R22-SCALAR-AFTER | `rounds[418].claims.C1.scalar_after` | invariant | state 7 |
| R22-COMPONENTS | `rounds[418].claims.C1.components.helper_explicit_refusals` | scope-precedent | before/after/of table |
| R22-LEDGER | `rounds[418].verification.rechecks` | invariant | 14 reports; recount |
| R22-SOURCES | `rounds[418].verification.rechecks` | invariant | missing0; re-derive rows |
| R22-NOHARM | `rounds[418].verification.axis_harm` | invariant | full recipe; frontier 0 |
| R22-CONFORMANCE | `rounds[418].verification.conformance` | invariant | sections/ancestry |
| R22-PORCELAIN | `rounds[418].verification.conformance` | invariant-conformance | pin current commit |
| R22-SPOTCHECK | `rounds[418].verification.spotcheck` | invariant-knowledge | OSError != UnicodeDecodeError |
| R22-DISCERNMENT | `rounds[418].trends.discernment` | invariant | no unmeasured channel admitted |
| R22-VERDICTS | `rounds[418].verdicts` | invariant-axis-budget | operability 8 unchanged |
| R22-SWARM | `rounds[418].verification.swarm` | operational-precedent | death accounting accurate |
| R22-TOOLS | `rounds[418].verification.tools_installed` | operational | record installs |

## Files written

- `.ufo/waves/round-23/build/advice/ConnClosureLearning.md` (this file).
- `.ufo/waves/round-23/build/out/ConnClosureLearning/closure-routes.json`.
- `.ufo/waves/round-23/build/out/ConnClosureLearning/extract-closure-routes.py`.

Scratch only (not repo deliverables): `/tmp/kama-r23/ConnClosureLearning/`
(`frozen.py`, `worktree.py`, selftest outputs, `patchcheck/`, probe case repos).

## Installs / updates

None.
