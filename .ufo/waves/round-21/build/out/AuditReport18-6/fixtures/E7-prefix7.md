# kama — round 18 (recovery attempt 2)

## Work performed

Declared claims (unchanged from attempt 1, both landed and measured here):

- **C1 — operability, 8 → 8 (delta 0):** receipt v3 separates a missing
  loading observation from an observed failure; schema floor, exact argv,
  loading transitions, IPv6 listener ownership and internal-fault receipts.
  Counting command `python3 .ufo/waves/round-18/c1/measure.py …` (argv in
  `runs/commands.json` `c1-measure`).
- **C2 — calibration, 7 → 7 (delta 0; lowest assigned axis):** a
  statement→mutant→detector ledger for the named round-17 survivors and fault
  paths. Counting command `python3 .ufo/waves/round-18/c2/survivors.py --json`
  (JSON document retained as `runs/c2-survivors.stdout`).

Recovery context: attempt 1 ended on provider quota with
`lane-dead-no-report` (fleet `.ufo/watchdog.log:536`) after spawning the 75-seat
build and 76-seat falsify waves and pushing checkpoint `101f3991…`. This
attempt ran no 64–100 wave (≤49 seats left of the 200-seat round cap): it
integrated the existing outputs, re-verified what it reused, and used one
ordinary `task` call of 7 reviewer/critic seats for residual checks.

Work items, each with an evidence pointer:

- **Reused after re-verification:** implementation commits `c6dc46f` /
  `1c325b2`, both wave specs/registries/advice, the live receipts (restored to
  their checkpoint bytes), the frozen manifest, the strict-canonicalisation and
  probe-matrix tooling, and the corpus text already integrated at the
  checkpoint (S047/S051/S054/S056, README precision paragraph, knowledge
  entries). **Discarded / not respawned:** the 20 never-assigned build members
  (declared in `build/advice/swarm-registry.json`; `dispatch-95.json` is the
  refused payload), the 10 falsify seats that left no report, and the
  pre-repair counter artifact (kept as evidence at
  `runs/pre-repair/c2-survivors.json`).
- **Falsify wave disposition** (`.ufo/waves/round-18/falsify/advice/`, count
  command in `corpus/lessons/round-18.md` §Falsify wave): 66 reports —
  28 confirm, 34 partial, 1 refute (`PrivacyScope`), 3 format-nonconformant
  (their bodies carry partial/confirm verdicts). Fixes landed from it:
  `child_env_keys` values never reach gate diagnostics (+ raw-token and
  non-string cases); `/health` 503 loading envelope cannot stay
  NOT-EVALUATED (H1); a fifth `--expect-server-impl-sha256` pin plus a
  field↔`install_tree` cross-check (consistent swaps now rejected); C1 counter
  row/count under-report, declared-exclusion and arm seams, including the
  bucket-gap hole found by the residual call; guarded finalizer
  signal-handler restore (`ToolFaultPaths` P2, unit-tested); C2 docstring,
  42-run count and empty-arm guard. Corpus appends: ownership honest-limit and
  endianness wording; lifecycle window-exclusion evidence (receipt
  `returncode 0` is the deciding evidence) and the five-pin residual; lessons
  M8/M9 and dispositions. Evidence pointers:
  `tests/llamacpp-live/check-receipt.py`, `tools/kama-llamacpp-live.py`,
  `.ufo/waves/round-18/{c1/measure.py,c2/survivors.py,runs/run.py}`,
  `corpus/knowledge/*.md`, `corpus/lessons/round-18.md`.
- **Residual call** (7 seats, one ordinary `task` call; no GRANT needed under
  the ≤8 allowance): `ResidPrivacy` confirm, `ResidHealth` confirm,
  `ResidImplPin` confirm, `ResidCounterC2` confirm, `ResidCounterC1` partial,
  `ResidCorpus` partial, `ResidClaims` partial. Their fixes are the own-case
  additions above plus: live receipts restored after the recovery run
  overwrote them in place, recovery receipts moved to `live-recovery/`, a
  clean-tree refusal in `run.py`, and removal of a duplicated ownership
  correction. Residuals are named, not closed: one of 51 install-tree members
  pinned; `/health` 503 with a truncated/non-JSON body stays NOT-EVALUATED;
  `gate_flip_arms=0` passes; C2's selftest arm has no full-enumeration check;
  FC-target's retained tail truncates the matched problem; `counts.after.total`
  folds inconclusive; detector-self mutant (b) is outside C2's 15.
- **Official measurement pass:** `python3 .ufo/waves/round-18/runs/run.py` on
  the clean tree `eb78788b…`: 32 commands, every declared exit met, harness
  exit 0, including three live v3 runs with five-pin `VALID` gates, five legacy
  pairs, the wrong-probe-pin negative control, both clone measures and the
  probe-matrix identity over all ten inputs. Raw streams/exits:
  `runs/commands.json`, `runs/*.stdout|.stderr|.exit`.

## Landed changes

- `0c75c611474cfc9f3c549e056fb0b736b20b854f` — code and corpus: gate privacy
  and H1 fixes, impl pin, C1/C2 counter seams, finalizer restore, tool/gate
  selftests, ownership/lifecycle lesson appends and dispositions.
- `888cd384a9cd06dd93d3fe6b05a9d829b9972122` — residual falsification reports,
  pre-repair counter artifact, source censuses.
- `eb78788b35b832d08887d4c366d1d0c1df3a6c19` — harness clean-tree guard and
  non-clobbering C2 capture; the measured tree.
- `1b85a24eca4d1fe81ef8d9ddf513fda1aad93e0e` — measured pass evidence,
  `live-recovery/` receipts, SCORECARD measured rows and LOG entry.
- LOG entries: `LOG.md` §round-18 (attempt 1: build and measurement) and
  §round-18 recovery attempt 2 (this work). Every change above is recorded
  there; the lane tip contains all four commits.
- `c6dc46f` — prefix control: 7-hex cite of a pre-report commit.

## Before → after measurements

Measured tree `eb78788b35b832d08887d4c366d1d0c1df3a6c19`
(`runs/commands.json` `measured_commit`); evidence commit `1b85a24`.

| Claim | Before → after | Counting command | Result |
|---|---|---|---|
| C1 | accepted_bad 5 → 0; good_rejected 1 → 0; misclassified 1 → 0; uncontrolled 0 → 0; gate_flip_arms 16 → 17 | `python3 .ufo/waves/round-18/c1/measure.py --controls tests/llamacpp-live/controls.py --frozen-tool .ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py --frozen-gate .ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py --tool tools/kama-llamacpp-live.py --gate tests/llamacpp-live/check-receipt.py --probe tools/kama-probe.sh --json` | exit 0, `current_clean true`, faults `[]`, frozen pins verified (`runs/c1-measure.json`) |
| C2 | 15 named: before survived 11 / miscount 1 / accepted 3 → after killed 11 / correct 1 / handled 3 | `python3 .ufo/waves/round-18/c2/survivors.py --json` | exit 0, inconclusive 0/0, witnesses 15/15 matched (`runs/c2-survivors.stdout`) |

No axis is harmed: legacy v1/v2 receipts replay byte-identically on both gates,
the five-pin flag is optional for historical receipts, and the extra gate
mutations (72) and counter cases (C1 45/45, C2 60/60) all pass.

## Sources & frontier

Census command:
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama`
→ **47 → 56 rows**, both exits 0 (`sources/census-before.txt`,
`sources/census-after.txt`). Tiers: A 44 → 53, C 3 → 3 (all 9 additions tier A).
Status: mined 37 → 45, queued 5 → 5, rejected 5 → 6. `validate` exits 0 with
three expected W04 duplicate-URL warnings (S031, S043, S056).

Rows added: S048–S056 (kernel tcp6 printer and in6.h, proc_net_tcp docs,
RFC 4291, Python 3.14 built-in exceptions, pytest exit codes, Automake
numbering as a rejected convention precedent, llama.cpp arg parsing, own-work
v3 live receipts, S056 superseding S054's duplicate-option wording). Rows
touched old→new: S047/S049/S050 `used-by` additions (logged in the lesson);
S051 clarification appended (`SOURCES.md:209-213`); S054 unchanged, superseded
by S056. Frontier rows advanced: S048–S050 (new
`corpus/knowledge/loopback-listener-ownership.md`) and S052/S054/S055/S056
(`llamacpp-loading-lifecycle.md` §Round 18). No `status`/`recheck` cell was
rewritten in place.

## Trend verdicts

- **expansion — improved.** 9 new curated source rows, a new knowledge entry
  and a new lifecycle section; census 47 → 56 with exit 0 before and after.
- **quality — improved.** The falsify refute and H1 are closed with fail-capable
  cases, the impl-boundary gap now has a pin, both counters exit 0 on genuine
  inputs, and the finalizer receipt escape is fixed and unit-tested. Named
  residuals remain and are listed above rather than absorbed.
- **discernment — unchanged.** Round 17's outside spot-check (`improved`) still
  stands; round 18's outside non-author admit/reject sample is still owed. The
  falsify and residual seats are lane-dispatched advice, not that outside
  judgment.

## SHONEN

- [~] SKILL decision tables / error patterns / checklist — author assertion;
  pointers `SKILL.md` §§Decision table, Error signatures, Checklist; no named
  non-author verifier this round.
- [~] End-to-end domain task executed and logged — `LOG.md` §§round 1–17 plus
  `round-18` recovery entry; round-18 receipts `live-recovery/receipt-{1,2,3}`
  (11/11 checks, five-pin gate `VALID`) and the five legacy replays.
- [~] Instructions executable without oral context — author assertion;
  `SKILL.md` §Checklist, `corpus/knowledge/*`; independent execution review
  still open.
- [~] No cross-domain bleed — `PROVINCE.md` §Write boundary remains accurate;
  service repair, routing, credentials and the llama archive question stay
  operator-owned.

## Extras

- **Waves/seats:** build 75 spawned/75 completed (one 95-seat call wholly
  refused, refit to 75 and not split; roles executor 13, scout 19, reviewer 16,
  scribe 8, critic 6, connector 4, mutation-tester 4, sentinel 2, revenger 2,
  simplifier 1; planner = L1); falsify 76 spawned, 66 reports, 10 dead (not
  respawned); residual 7 seats (6 reviewer, 1 critic; no GRANT). Round total
  158 spawned of ≤200; zero seat respawns.
- **Stale-lane:** respawn-per-round driver; no other kama mission open. This
  recovery attempt was operator-authorized and reused the pushed checkpoint.
- **Tool installs:** none. No host, package, service or compositor action.
- **Open L0:** the round-17 question about the retained llama-b11755 archive
  (`kama | round-17` in `.ufo/l0-questions.md`) is still unanswered; it does
  not block this round and no new question was filed.
