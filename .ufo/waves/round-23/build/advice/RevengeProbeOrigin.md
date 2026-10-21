# RevengeProbeOrigin — why KQ32 was written instead of a fix

Seat: CloseKama22.RevengeProbeOrigin (revenger, leaf). Date 2026-10-21. No tools installed. No fixtures executed by this seat; every executed observation below is cited to its seat/artifact. All paths relative to the lane `/home/vgpnk/Projects/shokunin/kama-shokunin` unless prefixed `fleet:` (= `/home/vgpnk/Projects/shokunin`).

## 1. The causal chain (reconstructed, with evidence)

**R21 shipped a scrub and over-claimed it.** Wave-1 integration adopted "scrubbed git environment and config for every git call" (`corpus/lessons/round-21.md:71-72`). The frozen auditor's `git_env` docstring promises: "No inherited GIT_* variables and no user/system config, so neither the audited repos nor the selftest fixtures can be redirected." (`tools/report-landing-audit.py@4fe9339f:80-81`, verified via `git show 4fe9339f…:tools/report-landing-audit.py`; module docstring "Errors are never verdicts." at `:45`). The promise is structurally false: the scrub covers only `GIT_*` env vars plus user/global/system config — repository-local config, refs and object state are untouched.

**The seat built to falsify that promise died before integration.** Round-21 falsify dispatched C1EnvSentinel to "Re-attack environment isolation … git config, `safe.directory`, hooks, gpgsign, `core.fsmonitor`" (`round-21/falsify/dispatch.json:511-514`). It is in `no_report` (`round-21/falsify/completion-summary.json:7-10`, report/verdict/dead all null). Its late advice did reconstruct the full fault surface — repo-local `log.showSignature`+`gpg.program` operator code execution, `refs/replace`/alternates/`shallow`/grafts false-clean, repo-local `i18n.logOutputEncoding` exit-2, UTF-8 crash-as-`failed`, selftest GIT_DIR blind spot (`round-21/falsify/advice/C1EnvSentinel.md:6-30`) — and even produced a 58-line `remediation.patch`, but scratch-only, unapplied, and never measured through an official recipe (`C1EnvSentinel.md:23-26`). So round 21 closed with the defect known and unfixed.

**The non-author closure converted the debt into a routing note, not a fix.** Fleet `MANIFEST.json` `rounds[406]` (r21 closure, `closed_at 2026-10-21T12:51:28Z`): "(D4)late C1EnvSentinel identifies unintegrated repository-local Git-config/history trust hardening and UTF-8/error/top-level handling; do not use audit on untrusted repos until hardened." Same notes: the closure parent "read current code and checked both actual repos: shallow/alternates/grafts absent, replacement refs empty, no local showSignature/gpg/hooks/fsmonitor/i18n config" — i.e., admission was made safe by a *written restriction plus a current-state fact*, explicitly "not a guarantee". A fix was not available to admit: the only candidate (C1EnvSentinel's patch) was late, unintegrated and unmeasured.

**R22 chose restriction-over-fix for two stated reasons.**
1. *One claim per axis / causal separation*: R22's C1 was the llamacpp-live install-helper I/O refusal; "report-audit Git-config/history trust and UTF-8/error-handling debt is not a hardening claim this round … Broader hardening remains explicit frontier because it is causally separate from C1" (`corpus/lessons/round-22.md:115-123`). The M4 conformance repair that round was itself only admitted by being "coalesced with C1 under the one-claim-per-axis rule" (`lessons/round-22.md` Final-report conformance section; `fleet:.ufo/reports/round-22/kama.md`).
2. *No measurement existed*: the closure explicitly refused to let the helper repair launder the debt — "Broader hardening, prelaunch races, gate chain bound and JSON edge cases remain frontier rather than quietly certified by the narrow helper repair" (`LOG.md:1289-1292`). KQ32's own lifting condition is "until … demonstrated separately" (`corpus/QUALITY.md:165`); in R21/R22 no fault grid, recipe or red-green witness for repo-local state existed, so a fix would have been an unmeasured claim.

**The restriction artifacts written instead:** KQ32 row (`corpus/QUALITY.md:165`, anchors "lessons/round-22.md D4; CloseKama21 rounds[406] and late C1EnvSentinel debt"); the SKILL operational rule "Never point it at an untrusted repository under the current guarantee (KQ32; round-22 lesson D4)" plus "D4 local-Git-config/history and UTF-8 hardening remains frontier" (`SKILL.md:732-738,771`); fleet report frontier/limits lines "Remaining frontier: … and D4 report-audit hardening" and "…trusted-repo-only audit" (`fleet:.ufo/reports/round-22/kama.md:198,263`); and the round-22 non-claims "Source URL classification is neither source truth/provenance validation nor D4 untrusted-repository hardening" / "No upstream validity or untrusted-repository security guarantee is inferred from URL classification" (`lessons/round-22.md:337,357`).

**Bottom line:** KQ32 was written because (a) the R21 fix candidate arrived dead-late and unmeasured, (b) the closure could verify the *real* repos were currently clean, making an honest scope restriction sufficient for admission, and (c) R22's declared claim was causally separate and the round discipline forbids absorbing an unmeasured second repair. It was deferral with named debt, not oversight — and the debt was explicitly routed forward ("do not use audit on untrusted repos until hardened"), which is exactly the grid this round measures.

## 2. D4 items deferred in R21/R22

From `rounds[406]` notes D4, `lessons/round-22.md:115-123`, `SKILL.md:735-737`, `LOG.md:1289-1292`:

1. Repository-local **Git-config** trust (config keys that redirect or crash verdicts).
2. **History-integrity** trust (replace refs; grafts named by C1EnvSentinel and KQ34 drafts).
3. **UTF-8** handling (decoding git stdout and committed report bytes).
4. **Error/top-level** handling (uncaught exceptions becoming `failed` verdicts; no catch-all in `main()`).
5. Late **selftest fallback/GIT_DIR assertion debt** ("vacuous uncommitted-now fallback and crash-only GIT_DIR assertion remain test debt" — `rounds[406]`; `lessons/round-22.md:121-123`).
6. **Prelaunch(-snapshot) races** — adjacent routed debt, C2 side (`rounds[406]`; `LOG.md:1291`).
7. **Gate chain bound** (41-hop) — adjacent routed debt, C2 side.
8. **JSON duplicate-key/Unicode edge cases** — adjacent routed debt, C2 side.

Items 6–8 were named in the same D4 sentence but belong to the llamacpp/helper claim; `SKILL.md:771` keeps only "local-Git-config/history and UTF-8" as the auditor frontier.

## 3. Which of those this round's grid covers

Frozen-arm ground truth: `.ufo/waves/round-23/probe/probe-4fe9339f.stdout` / `.exit` (exit=0; probe source `/tmp/kama-r23-probe/probe.sh`, read by this seat, not executed). Declared route: "Address only the measured channels (replace refs, promisor lazy fetch, i18n.logOutputEncoding, log.follow, strict decode)" (`.ufo/waves/round-23/build/out/ConnClosureLearning/closure-routes.json:98`).

| Probe | Channel (deferred item) | Frozen 4fe9339f observed | Grid covers |
|---|---|---|---|
| f1-logenc | repo `i18n.logOutputEncoding=ISO-8859-1` + non-ASCII subject (1,3,4) | exit1, `UnicodeDecodeError … 0xe9` traceback → error became `failed` | yes — crash→typed refusal (strict decode / bytes-mode git) |
| f2-report-bytes | invalid UTF-8 in committed fleet report (3,4) | exit1, `UnicodeDecodeError … 0xff` | yes — strict decode → EvalError exit2 |
| f3-replace-omit | `git replace` hides an omitted round commit (2) | exit0, `defects []` — false clean | yes — global `--no-replace-objects` → correct verdict |
| f4-replace-fake | `refs/replace/<fabricated 40-hex>` resolves a fabricated citation (2) | exit0, `defects []` — false clean | yes — same override |
| f5-lazyfetch | promisor remote + `core.sshCommand`; lazy fetch during `cat-file --batch-check` (1) | verdict already correct (exit1 `unresolved-full-hash`) **but marker created: repo-configured command executed** | yes — `--no-lazy-fetch` execution suppression on this one path (not a verdict flip; CritOverclaim risk #3) |
| f6-follow | fleet `log.follow=true` (1) | equals control (exit0, required 1, cutoff 2000 — no flip) | preventive override only; earns no before→after "fault fixed" credit (CritOverclaim risk #2) |

So the grid covers: config channels `i18n.logOutputEncoding` (+ preventive `log.follow`), the UTF-8 half of items 3–4, and the replace-refs half of item 2, plus lazy-fetch execution suppression.

## 4. What the grid does NOT cover (must stay deferred; KQ32 stays in force)

- `log.showSignature=true` + `gpg.program` / `include.path`: still executes and corrupts a parsed verdict in **both** frozen and current arms (`build/advice/CritOverclaim.md` counterexamples 1/1b; first demonstrated R21 at a6617149, `C1EnvSentinel.md:11-14`).
- `.git/shallow` false clean (CritOverclaim #2), `objects/info/alternates` false clean (#3 — alternates/`clone --shared` remain legitimate by scope), `.git/info/grafts` (#4 — survives `--no-replace-objects`).
- Top-level catch-all (item 4 half), selftest GIT_DIR debt (5), prelaunch races (6), gate chain bound (7), JSON duplicate-key/Unicode limits (8) — all untouched this round.
- KQ32's trust restriction itself: a finite grid with known open execution and false-clean channels does not meet "demonstrated separately"; no supersession row is justified (CritOverclaim #7).

Notable: the round-23 grid is **narrower than the fault surface already reconstructed on 2026-10-21 by C1EnvSentinel** (showSignature exec, shallow/alternates/grafts false-clean). That is the declared design (one finite measured grid per claim), not a new discovery — but any round-23 wording claiming "D4 advanced/closed" or "untrusted-repo safe" would be false against that older evidence.

## Not verified by this seat

- I did not run `probe.sh`, `beyond-grid*.sh`, or any auditor invocation; frozen-arm outcomes are cited from the L1's committed probe artifacts and CritOverclaim's executed fixtures, not re-executed here.
- I did not verify the current (fixed) arm's behavior — the frozen-vs-current grid runs are the L1's measurement, still pending official integration.
- I read `rounds[406]` (the r21 closure) but not any r22 closure manifest entry; the r22 lesson says independent non-author admission "remains pending" (`lessons/round-22.md` end).
- Git-version floor claims (e.g. `--no-lazy-fetch` availability) were not checked against installed git 2.56.0 behavior by me.

## Files written

- `.ufo/waves/round-23/build/advice/RevengeProbeOrigin.md` (this report). No other files; no lane/checkout/tracked-file writes.
