# X15NoHarm2 — round-50 regression battery at the build tip

**Verdict: the battery is stable at `97c864bead3ee4a2f629574e77263d33834ec98a` — the ten lane instruments, the four selftests and the three frozen counters reproduce every round-49 value that is not definition-bound, and the seven red/behaviour deltas are all attributable: three reconciler reds are carried in from the round-49 closure commit (the round-50 base `26ecba64`), one is the build's own `SOURCES.md` row-parsing defect (fixed at `3d42897b`), one is the disclosed unregistered-counter bill, and two are the intended v5 definition change (one of which turns the frozen round-49 v4 counter's lane leg red at every post-v5 tip). No instrument, selftest or counter broke silently; no receipt differs from the build's own receipts except the ephemeral live-selftest ports.**

Measured on my own clone: `git clone --shared <lane> $S/lane`, `git checkout --detach 97c864be`, every command run with cwd inside that clone, `TMPDIR` inside my scratch. Drivers (in this directory, reproducible): `battery-v5-tools.sh <clone> <tip> <scratch>` (sha256 `6fe304e0558eeca02d857ea0eebc74f904651e6b0e7cd28c2e7f0c8d0ffff988`) and `battery-v4-counters.sh <clone> <tip> <scratch>` (sha256 `3e6bc0403f658fa2cce460c6a18908da97617c13496de7f7ddd92f282f8ff99a`). Receipts: this directory (`<name>.out`), cited round-49 receipts in `round49-measured/`, cited build receipts in `build-receipts/`, `MANIFEST.sha256` for the whole set.

## 1. Measured values, my run vs `.ufo/waves/round-49/measured/` (measured commit `24e906f0`)

| leg | round-49 measured | mine at `97c864be` | verdict |
|---|---|---|---|
| gate | `registered 44 unregistered 0 defective 0` exit 0 | `registered 44 unregistered 2 defective 0` exit 1 | **red** — known integration item (2 round-50 counters not in `SKILL.md`) |
| capability census | `listed 11 observed 11 missing 0 unsubstantiated 0 met True` exit 0 | identical, exit 0 | stable |
| round-41 head counter | `mismatches=0 met=True` exit 0 | `run_bad=1 mismatches=1 met=False` exit 1 | **red** — base-carried, F1 |
| round-42 selfdesc | `mismatches=0 maxN=49 met=True` exit 0 | `r41=1 mismatches=1 maxN=49 met=False` exit 1 | **red** — inherits F1 |
| round-43 registry | `unreg=0 … selftest=0 … spot=0 pop=44 registered=44 mismatches=0 met=True` exit 0 | `unreg=2 … selftest=1 … spot=1 pop=46 registered=44 mismatches=4 met=False` exit 1 | **red** — F1 (spot) + known item (unreg) + F5 (selftest coupling) |
| planned-pointer | `pointer: ok … met=True` exit 0 | identical, exit 0 | stable |
| digest-ledger | `tokens=130 blob=114 external_ok=9 external_absent=1 unverifiable=5 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0` exit 0 | identical, exit 0 | stable |
| hexrun-census | `tokens=1845 distinct=299 lane_oid=193 … unknown=0` exit 0 | `tokens=1858 distinct=305 lane_oid=198 … unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=1` exit 1 | **red** — base-carried, F2 |
| sources-append-only (`--from 26ecba64 --to TIP`) | (r49: `--from 438127bc` → `added S494 (allowed) / added S495 (allowed) / no append-only violations` exit 0) | `error: 97c864be…:corpus/SOURCES.md:251: unterminated table row (no closing pipe)` exit 2 | **red at this tip** — F3, fixed at `3d42897b`; verified green at `3b79eadd` |
| append-only-audit | `events=5 … ungraded_lines=82` exit 0 | `events=5 restored=5 … ungraded_lines=89` exit 0 | exit 0 as required; count is the intended v5 change, F6 |
| selftest AOA | `AOA_SELFTEST pass=36 fail=0` | identical | stable |
| selftest KLR | `KLR_SELFTEST pass=23 fail=0` | identical | stable |
| selftest live tool | `selftest: ok` (ports vary) | `selftest: ok; closed tcp6 listeners ::1:34455, ::ffff:127.0.0.1:36051` | stable |
| selftest check-receipt | `16 VALID and 1 NOT-EVALUATED receipts accepted; 107 mutations + unreadable case rejected` | identical | stable |
| round-48 C2 counter | `receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True` exit 0 | identical, exit 0 | stable |
| round-49 C1 counter | `witness=1 cap=1 newrow=1 witnessed=3/3 met=True` exit 0 | identical, exit 0 (`cap`: `sparse-1e15` exit 2 `provenance-member-sparse` executed=False; control `server-exited-early-rc3` executed=True) | stable |
| round-49 C2 counter | `fixture=1 lane=1 scenarios=8/8 met=True` exit 0 | `fixture=1 lane=0 scenarios=8/8 met=False` exit 1 | **red** — intended v5 supersession, F4 |

Every receipt in this directory is byte-identical to the matching `.ufo/waves/round-50/measured/*-build.out` except `live-selftest.out` (ephemeral ports only; `diff` of the 14 shared legs: `same` for all others).

## 2. Findings

### F1 — base-carried (calibration): the lane's own calibration fact has been false since the round-50 base

* Site: `SCORECARD.md:18` (calibration row) — the re-derivable run states `… print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` → `35`.
* Tree at `97c864be` and at the base `26ecba64` holds **36** such files: `corpus/lessons/round-49-verifier-spotcheck.md` was added by `26ecba64` (`git log --diff-filter=A -- 'corpus/lessons/*verifier-spotcheck.md'` → `26ecba64 round-49 verifier spot-check (integrator, hyaku): non-author admit/reject`), and that commit did not bump the row.
* Show it: `python3 tools/round41-scorecard-reconcile.py` → `run_bad=1 … met=False` exit 1; detail: ``calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '35' (exit 0)``. `round42` inherits it (`r41=1`), `round43` reports `spot: calibration row states 35, tree holds 36`.
* Attribution (measured, not inferred): identical red at the base — `base-r41.out`, `base-r42.out`, `base-r43.out` (run with the clone checked out at `26ecba64`): `run_bad=1`, `r41=1`, `spot=1` respectively. At `24e906f0` the count was 35 and the row said 35 (both `git ls-tree` and `git show 24e906f0:SCORECARD.md`), so the closure commit introduced the red.
* Proposed fix (lane, at integration, not mine to apply): set the row's run fact to `36` and the “outside closures on record” figure accordingly in `SCORECARD.md:18`; that single edit greens `r41`, `r42` and `r43`'s `spot`.

### F2 — base-carried (calibration): the round-49 closure lesson cites a commit that does not exist in the lane

* Site: `corpus/lessons/round-49-verifier-spotcheck.md:21` — `| Report committed by the lane identity | … → one commit: kama-shokunin <kama@shokunin.local> | f8cdb853aaff29393faeb0b6d4c2a2296778b698 2026-10-26 21:00:10 -0300 round-49: kama report | pass |`.
* Show it: `git cat-file -t f8cdb853aaff29393faeb0b6d4c2a2296778b698` → `fatal: git cat-file: could not get object info`; `git rev-list --all | grep -c '^f8cdb853'` → `0`; `git log --all --format='%H %ci %s' | grep -i 'kama report'` → no line; the file it claims, `.ufo/reports/round-49/kama.md`, is in no tree (`git log --all -- .ufo/reports/round-49/kama.md` empty; the only tracked report is `.ufo/reports/round-5/kama.md`). The lane is jj-colocated (`/home/vgpnk/Projects/shokunin/kama-shokunin/.jj` exists) and carries hundreds of `refs/jj/keep/*`, so a rewritten/abandoned commit id is the plausible mechanism — the cited evidence is unrecoverable either way.
* Effect: `hexrun-census` classifies the run `unknown` (`tools/hexrun-census.py:264`; exit rule at `:434`) → `tokens=1858 … unknown=1` exit 1. Full detail line: `detail: f8cdb853aaff29393faeb0b6d4c2a2296778b698 len=40 occurrences=1 class=unknown`. The other `+13` tokens / `+6` distinct / `+5` lane_oid over round-49 are this lesson file as a whole (the build adds no new hex run: the same receipt reproduces at `--rev 26ecba64`).
* Attribution: identical at the base (`base-hexrun.out`: `tokens=1858 … unknown=1` exit 1); absent at `24e906f0` (`git grep f8cdb853 24e906f0` → nothing).
* Proposed fix: either cite the real landing commit of the round-49 report, or add one `registry/hexrun-ledger.tsv` row in the shape the ledger already uses for this class — `f8cdb853aaff29393faeb0b6d4c2a2296778b698	unverifiable				2026-10-27	commit id cited by corpus/lessons/round-49-verifier-spotcheck.md:21 as the round-49 report commit; no such object in the lane store (git cat-file -t fails, rev-list --all 0 hits) and .ufo/reports/round-49/kama.md is in no tree; jj-colocated history, evidence unrecoverable`. Copying the row verbatim needs a tab-separated 7-column write; the header is `token class repo evidence correct verified-at note`.

### F3 — build-caused at the assigned tip (calibration): `sources-append-only` cannot parse the `S498` row

* Site: `corpus/SOURCES.md:251` (the `S498` CommonMark row) at `97c864be`. The row *does* end in `|`, but its cell quotes a lone backtick and a lone tilde (`… at least three consecutive backtick characters (`) or tildes (~).`); the row parser's code-span stripping pairs that backtick with a later one and swallows the closing pipe.
* Show it: `python3 tools/sources-append-only.py --from 26ecba64ad6fb571d09074b07202d1618a46ecd1 --to 97c864bead3ee4a2f629574e77263d33834ec98a` → `error: 97c864be…:corpus/SOURCES.md:251: unterminated table row (no closing pipe)`, exit 2.
* Already known at build time (`.ufo/waves/round-50/measured/sao-build.out` records the same exit 2) and fixed one commit later: `3d42897b round-50: build-fix - S498 row markdown tick parity so sources-append-only row parser accepts it` removes the two lone backticks. Verified green after the fix: `python3 tools/sources-append-only.py --from 26ecba64… --to 3b79eadd` → `added S496 (allowed) / added S497 (allowed) / added S498 (allowed) / no append-only violations`, exit 0 (`sao-at-head.out`).
* Consequence for integration: the battery must be run at `3b79eadd` (or later), not at `97c864be`; round-50's measured receipts must not quote a `sao` line from the build commit.

### F4 — intended v5 supersession (calibration): the frozen round-49 v4 counter's lane leg is red at every post-v5 tip

* Receipt: `r49c2.out` — `fixture=1 lane=0 scenarios=8/8 met=False` exit 1, single failing detail:
  `lane: event 0718b6abbda6 SCORECARD.md ungraded 72 > natively exempt 65`.
* Mechanism: the round-49 counter bounds the tool's self-reported `ungraded` by *its own* frozen v4 recompute (`tools/round49-append-audit-v4-check.py:353-357`: `native = sum(... psec[pos-1] in ex and org.get(text, set()) & ex)`; fail at `:357`). The v5 tool ungrades the seven `## Capabilities` mirror rows of `0718b6abbda6`, so 65 → 72, which v4's own rule cannot account for. The round-50 C2 counter carries the matching v5 bound (`tools/round50-append-audit-v5-check.py:493`).
* Attribution (measured): `met=True`, `ungraded_lines 82`, `0718b6abbda6 … 65 <= 65` at the freeze `601c8889` (`base-r49c2-freeze.out`) and at the base `26ecba64` (`base-r49c2.out`); `met=False`, `89`, `72 > 65` at the build (`r49c2.out`) and at the integration head `3b79eadd` (`base-r49c2-head.out`). So the red is caused by the v5 build, not by lane-history drift, and it persists at HEAD.
* Proposed handling: record `r49c2` in the round-50 measured receipts as *superseded by round-50 C2 for the lane leg only* — its fixture leg stays green (8/8 at both tips) and it stays a valid historical control at v4 tips (≤ `26ecba64`); do not gate round 50 on `r49c2 met=True`, and do not “fix” the counter (it is frozen and did exactly what it was built to do).

### F5 — instrument caveat (operability): the direct gate selftest's lane-tip arm measures the clone's `master`, not the tip under test

* `tools/gate-registry-check.py:333-349` resolves `master` in the *lane root it is embedded in* and grades that commit (`rev-parse --verify master` → `evaluate(lane_root, tip)`). In my clone (HEAD detached at `97c864be`, `master` = `3b79eadd`) the printed arm was `FAIL lane-tip 3b79eaddf382: exit=1 line='registered 44 unregistered 2 defective 0'` — i.e. it graded `3b79eadd`, not the measured tip. `round43-registry-audit.py:172-190` avoids this by cloning and forcing `branch -f master <tip>` before running `--selftest`, so r43's own verdict is about the tip.
* Consequence: `gate.out` (`GATE_SELFTEST pass=5 fail=1`, exit 1) and r43's `selftest=1` (`documented 'GATE_SELFTEST pass=6 fail=0', run printed 'GATE_SELFTEST pass=5 fail=1'`) are both the *same* bill as the disclosed unregistered counters (`SKILL.md:1330` documents `pass=6 fail=0`). Registering `tools/round50-replay-bind-audit.py` and `tools/round50-append-audit-v5-check.py` in `SKILL.md`'s registry turns both green; no separate fix is needed. At `97c864be` the two counters are equally unregistered, so the tip-vs-master subtlety does not change any verdict here.

### F6 — definition change, not a regression (calibration): `ungraded_lines` 82 → 89

`aoa.out`: `summary commits=327 files=94 events=5 restored=5 partial=0 unrestored=0 ungraded=0 ungraded_lines=89 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=0`, exit 0. The +7 is exactly `event 0718b6abbda6 SCORECARD.md ungraded=72` (v4: 65) — the seven `## Capabilities` mirror rows the round-50 spec says v5 now correctly ungrades (F6 resolved); `event dd9f5dc6c0e6 SCORECARD.md ungraded=17 <= v5 natively exempt 23` is unchanged, and `LOG/QUALITY/README` stay 0. The tool reports `"definition": "v5"` (`tools/append-only-audit.py:573`) with the schema unchanged (`append-only-audit/v3`), as pre-registered.

## 3. Exact commands (all from inside the clone, exit codes as recorded in the receipts)

```bash
S=/fast/scratch/hyaku/kama-r50/X15NoHarm2; export TMPDIR="$S"
git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
git -C "$S/lane" checkout -q --detach 97c864bead3ee4a2f629574e77263d33834ec98a
cd "$S/lane"
python3 tools/gate-registry-check.py --rev 97c864be…            # 1  unregistered 2
python3 tools/capability-repertoire-audit.py                    # 0
python3 tools/round41-scorecard-reconcile.py                    # 1  run_bad=1
python3 tools/round42-selfdesc-reconcile.py                     # 1  r41=1
python3 tools/round43-registry-audit.py                         # 1  mismatches=4
python3 tools/planned-pointer-check.py SCORECARD.md             # 0  met=True
python3 tools/digest-ledger.py scan --repo . --rev 97c864be…    # 0  unknown=0
python3 tools/hexrun-census.py scan --repo . --rev 97c864be…    # 1  unknown=1 (F2)
python3 tools/sources-append-only.py --from 26ecba64… --to 97c864be…   # 2 (F3)
python3 tools/append-only-audit.py --repo . --to 97c864be…      # 0  ungraded_lines=89
python3 tools/append-only-audit.py --selftest --scratch "$S"    # 0  pass=36 fail=0
python3 tools/kama-live-replay.py --selftest --scratch "$S"     # 0  pass=23 fail=0
python3 tools/kama-llamacpp-live.py --selftest                  # 0  selftest: ok
python3 tests/llamacpp-live/check-receipt.py --selftest         # 0  16 VALID / 107 rejected
python3 tools/round48-live-replay-v5-audit.py --repo . --tip 97c864be… --scratch "$S/r48"     # 0 met=True
python3 tools/round49-replay-witness-audit.py --repo . --tip 97c864be… --scratch "$S/r49c1"   # 0 met=True
python3 tools/round49-append-audit-v4-check.py --repo . --tip 97c864be… --scratch "$S/r49c2"  # 1 (F4)
```

Attribution runs (same clone, `git checkout --detach` between, restored to `97c864be` afterwards): `round41/42/43` and `hexrun-census` at `26ecba64` (`base-*.out`); `round49-append-audit-v4-check.py --tip` at `601c8889`, `26ecba64`, `3b79eadd` (`base-r49c2-freeze.out`, `base-r49c2.out`, `base-r49c2-head.out`); `sources-append-only --to 3b79eadd` (`sao-at-head.out`).

## 4. Host / hygiene

* No tool installs or upgrades were needed or performed (python3, git, curl, `ss`, `flock` already present); no pacman transaction.
* No lane write, no git/jj mutation in the lane, no fixture repo created, no subagent. My only writes: this file, the evidence directory beside it.
* Servers: my three counter legs started and tore down their own loopback llama-servers; `pgrep -af llama-server | grep -c X15NoHarm2` → `0`, `ss -ltnp | grep -c X15NoHarm2` → `0`. Nine llama-server processes from *other* seats' scratch dirs are alive on the host right now (`J2NoPdeathsig` pids 2987107/2990076, `Sen3Teardown` 3124696/3127949/3130587/3133900, `X11ModelSwap` 3775851/3778577, `J4Decoy` 3781476 — one of them `J4Decoy`'s host-copy `/home/vgpnk/.local/opt/llama-b11909/llama-server` on port 59043); they are not mine and I did not touch them, but L1 should not read a bare `pgrep llama-server` at integration as a lane artifact.
* Scratch `rm -rf`'d; every receipt cited here is in this directory.
