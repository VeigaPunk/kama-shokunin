# CritOverclaim — round 23 wording-risk critique (findings only)

Seat: CloseKama22.CritOverclaim (critic, leaf). Date 2026-10-21. Git 2.56.0.
Inputs: `corpus/QUALITY.md:165` (KQ32), fleet `.ufo/reports/round-22/kama.md:261-263`
(Limits), `corpus/lessons/round-22.md:116-123,337,357`, `SKILL.md:732-738,771`,
`SCORECARD.md:1107-1108,1121,1149-1150`, the L1's uncommitted
`tools/report-landing-audit.py` (working-tree sha256 `b6064767…`, frozen
4fe9339f blob `09ecd63b…`), and the round-23 drafts under `build/out/`.

## Bottom line

The grid can honestly support this claim: "for N named repository-local channels,
the auditor now refuses (exit 2) or returns the correct verdict where frozen
4fe9339f crashed, flipped or executed." Running the auditor with these
repository-local settings still yields **command execution** in one case and a
**false clean** in two others, in BOTH arms (counterexamples 1–3). So any
wording that drops KQ32's trusted-repository restriction, says "untrusted-repo
safe", or says "no repository-configured command runs" would be false. KQ32 is
not satisfied by this round. It stays in force.

## Counterexamples outside the grid (executed, scratch only)

Fixtures: `build/out/CritOverclaim/beyond-grid.sh` (sha256 `e89abc63…`) and
`beyond-grid-2.sh` (`7db5c6ed…`), each run once. Both run frozen and current
copies from `/tmp/kama-r23-crit-overclaim/` with
`GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`. Commands:
`bash beyond-grid.sh` (run dir `run.b2Ve`) and `bash beyond-grid-2.sh` (`run2.9bOT`).

| # | Repo-local state (lane) | Frozen | Current (L1 working tree) | Kind |
|---|---|---|---|---|
| 1 | `log.showSignature=true` + `gpg.program=<script>`, one round commit with a `gpgsig` header | exit1, `landed-omitted` token `"[GNUPG:] GOODSIG 0 x\n2b5e8fda…"`; marker: `gpg.program ran: --keyid-format=long --status-fd=1 --verify /tmp/.git_vtag_tmp… -` | **identical**: exit1, same garbage token; marker written | executes a configured program, AND corrupts output that is parsed into a verdict (not EvalError) |
| 1b | same keys, smuggled through `include.path=<file>` | exit0 clean, marker written | **identical** | executes |
| 2 | `.git/shallow` naming a later commit, so the omitted `round-1:` commit is hidden | exit0 clean, `required 0` | **identical** | false clean |
| 3 | `objects/info/alternates` → attacker store holding the "fabricated" cited commit | exit0 clean | **identical** | false clean (scope already calls alternates legitimate) |
| 4 | `.git/info/grafts` | `git log` lists 1 of 3 commits with default, `--no-replace-objects`, and `GIT_NO_REPLACE_OBJECTS=1` | not run through the auditor; [INFERENCE] same false-clean shape as #2 | not closed by `--no-replace-objects` |
| — | `.mailmap` / `mailmap.file` | no effect: `%an` is not mailmapped; omission still reported | same | no-effect |
| — | `core.fsmonitor` (set only after all fixture writes) | no marker | no marker (also `--report` draft path) | no-effect |

Correction to my own first run: its fsmonitor marker came from my fixture's
`git add`, not from the auditor. The clean rerun (`beyond-grid-2.sh`) shows no
marker.

Smallest closure for #1, checked directly with plain git in that fixture:
GIT_ISOLATION as shipped → marker PRESENT. Adding `-c log.showSignature=false` →
absent. `--no-show-signature` → absent. Separately, `round_commits` checks only
that field 2 is numeric (`tools/report-landing-audit.py:174`). A non-40-hex
`%H` field is accepted as a SHA. That is how injected stdout became a `failed`
verdict.

Real repos (targeted `git config --local --get` only, no fixtures): lane and fleet
have `log.showSignature`, `gpg.program`, `include.path` and
`extensions.partialClone` unset. `shallow`, `info/grafts` and `alternates` are absent.
So the trusted-repo verdicts are unaffected today. This is a fact about current
state, not a guarantee.

## Wording risks, by artifact

1. **`tools/report-landing-audit.py:45` "Errors are never verdicts."** It is still
   unqualified at the module level, next to the new GIT_ISOLATION. Counterexample
   1 turns corrupted git output into a verdict without any exception. Correction:
   qualify it, e.g. "Exceptions raised while evaluating map to exit 2. Repository
   state outside the named isolation set can still change the answer; supported
   only on the trusted lane/fleet repos (KQ32)." Alternatively, close #1 and add
   a 40-hex `%H` check, with grid cases for both.
2. **GIT_ISOLATION comment (working tree lines 79-82):** "Repository-local state
   that changed or crashed verdicts in the round-23 fault grid: … log.follow". The
   L1's own probe (`.ufo/waves/round-23/probe/probe-4fe9339f.stdout`, and every
   `/tmp/kama-r23-probe/run.*/f6-follow.out`) shows `f6-follow` equal to the
   control: cutoff 2000, required 1, no defects. Unless FollowFixture lands a
   fixture where frozen actually flips, `log.follow=false` is a *preventive*
   override. It must be worded that way and must earn no "fault fixed" credit in the
   before→after count.
3. **The lazy-fetch override's "may run repo-configured commands" text, and any report
   phrase like "no repo-configured command executes" or "command-execution safe".**
   Counterexample 1/1b shows `gpg.program` still runs under the shipped
   isolation. Command-execution wording must be confined to "promisor lazy fetch
   during `cat-file --batch-check`". Fault (e) is execution suppression on that
   one path, and frozen's verdict there was already correct (probe f5: correct
   `unresolved-full-hash`/`landed-unresolved`, exit 1, marker created).
4. **`out/ScribeLessonDraft/round-23-draft.md:10` title "fails closed under
   repository-local git state".** This is unqualified and false by counterexamples
   1–3. Use "…for the named grid channels". Its boundary lines 20 and 38-39 are
   fine.
5. **`out/ScribeQualityRule/KQ34.md:12` lists "`refs/replace` and grafts" as
   isolated channels.** Grafts survive `--no-replace-objects` (#4). Drop grafts
   from the isolated list or add a real closure plus a case. Its own anchors line 20-25
   correctly say it does not lift KQ32. Keep that.
6. **`out/ScribeKnowledgeEntry/error-is-not-a-verdict.appended.md`:**
   - "Not probed: `log.showSignature` … expected to fail as `EvalError` (exit 2),
     not as a clean verdict." This prediction is **falsified** by #1 (exit 1 false
     `failed`) and #1b (exit 0 clean plus execution).
   - Boundary: "Treat a clean verdict from an untrusted repository as clean only
     for the channels listed as isolated." This invites running on untrusted repos,
     which contradicts `SKILL.md:737-738` ("Never point it at an untrusted
     repository"). Running it is exactly what triggers #1b's execution. Replace it
     with "Do not run it on untrusted repositories; a clean verdict there carries no
     guarantee."
   - The table's channel 2-3 (grafts, shallow) and channel 4 (alternates) "still
     open" findings agree with mine. Channel 1 (tag shadowing `master`) I did not
     reproduce.
7. **SKILL.md / SCORECARD / round-23 report.** Any update to `SKILL.md:732-738`
   must *append* the narrowed channel list. It must not delete or soften "supported
   only on this trusted lane and fleet repository" or "Never point it at an
   untrusted repository". The round-23 report's Limits must carry round-22's
   "trusted-repo-only audit" (`kama.md:263`) forward verbatim in meaning, and add
   showSignature/gpg.program, shallow, grafts, alternates and resource exhaustion
   (SentinelResourceDoS) as named open channels. Frontier text should read "D4
   partially narrowed (N channels)", not "D4 advanced/closed". KQ32's lifting
   condition is "hardening is demonstrated separately". A finite grid with known
   open execution and false-clean channels does not meet it, so no KQ32 supersession
   row is justified.
8. **Scoring/trend wording.** Calling this "untrusted-repository hardening" or
   "security" in trends would import round-22's explicit non-claims in reverse
   (`SCORECARD.md:1121,1149-1150`; lesson `:337,:357`). It stays calibration-narrow:
   error/verdict separation and named-channel isolation on trusted repos.

## Impacted axes

Calibration (main risk: the claim reads broader than the measured grid).
Discernment (KQ32 would be silently weakened if the trust restriction is dropped).
Operability is not directly harmed: real repos lack these keys.

## Smallest safe correction

Treat wording as required and code as optional:

- Qualify line 45.
- Mark `log.follow` as preventive unless a flip is observed.
- Confine execution wording to the lazy-fetch path.
- Keep KQ32 and SKILL "never untrusted" text unchanged, appending only.
- List the open channels from counterexamples 1–4 and resource exhaustion as Limits.
- Fix the three drafts per items 4–6.

If the L1 wants #1 inside C1, the closure is `-c log.showSignature=false` plus a
40-hex check on the `%H` field, each with a grid fault case, a control, and a mutant.
Otherwise name it as an open channel.

## Not verified

- I did not run the grid, the selftest (50/50), the witness, or the historical ledger.
- I did not run grafts or tag-shadowing through the auditor.
- I did not check credential helpers, `uploadpack`, hooks, `core.sshCommand` outside
  lazy fetch, or old-git behaviour of `--no-lazy-fetch`.
- No real network host was contacted.
- No installs.

## Files written

- `.ufo/waves/round-23/build/advice/CritOverclaim.md` (this report)
- `.ufo/waves/round-23/build/out/CritOverclaim/beyond-grid.sh`
- `.ufo/waves/round-23/build/out/CritOverclaim/beyond-grid-2.sh`
- Scratch only: `/tmp/kama-r23-crit-overclaim/` (frozen.py, current.py copies, run dirs)
