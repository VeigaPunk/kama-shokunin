# Rev3 — round-54 routed defects vs the round-55 tree (kama, r55)

**Verdict:** items 1 and 3 are closed; item 4's receipts landed but its frozen C1 kill-battery target is contradicted by a committed receipt (`m-ldaudit-writable` met=True) — a calibration defect, not an admission; item 2 is open (in-flight wave seats, nothing committed at the freeze); item 5 is open (no LOG.md round-55 entry); item 6 remains operator-owned and was not re-forwarded this round.

Snapshot: lane HEAD when read `8abadfedf89f35372645b1e5d6ce4a2109186f90` (freeze `9c60eae6f7ed84f7da93d219a406aadc30958c6c`, its parent in the w1 sequence); reviewed the `9c60eae6` tree as instructed and the w1 commit that followed it. Worktree was clean except `?? .ufo/waves/round-55/w1.ready.partial`. Read-only throughout: one `git clone --shared` at `9c60eae6` under `/fast/scratch/hyaku/kama-r55/w1/Rev3/lane`; no lane writes, no counter edits, no services.

Freeze order (commit vs data): `preregistration.json` frozen_at `2026-10-27T13:20:12Z`; freeze commit `9c60eae6` `2026-10-27T10:24:22-03:00`; measured runs `10:24:37`/`10:25:00`; battery receipts `10:30:19`–`10:44:09`; w1 commit `8abadfed` `10:52:56-03:00`.

## Item 1 — round-54 lesson written + S510 used-by fixed (census exit 0?) — CLOSED

- Successor lesson is committed in the freeze tree: `corpus/lessons/round-55.md` (present in `git ls-tree 9c60eae6`). It states no round-54 lesson exists and none is backdated (`corpus/lessons/round-55.md:7-9`); the routed item allowed "the round-54 lesson (or its successor)" (`corpus/lessons/round-54-verifier-spotcheck.md:78`).
- S510's dangling `used-by` is re-pointed: `corpus/SOURCES.md:263` ends `... | 2026-10-27 | 360d | corpus/lessons/round-55.md |` (old value `corpus/lessons/round-54.md` is gone; `grep -c 'round-54.md'` on that file → 0).
- Census, reproduced against the exact freeze tree (clone checked out at `9c60eae6`):
  - `scripts/sources-census.sh validate --file <clone>/corpus/SOURCES.md` → **exit 0**; last line `file	ok	<clone>/corpus/SOURCES.md`; the only error-class line is absent; one new warning `file W04 S511 duplicate url git-scm.com/docs/git-config` (`census-validate-9c60.out`).
  - The lesson's own command `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → **exit 0**, 99 warning lines, no `E11` (`census-validate-fleet-kama.out`).
- Round-start red is honestly receipted: `.ufo/waves/round-55/census/start.out` (committed at `9c60eae6`) contains `kama	E11	S510 missing used-by corpus/lessons/round-54.md` and `census_start_exit=1`.
- **Receipt gap (minor, D2):** `corpus/lessons/round-55.md:95` and `:101` cite `.ufo/waves/round-55/census/end.out` as the round-end receipt, but that path exists neither in the `9c60eae6`/`HEAD` trees nor on disk (`ls .ufo/waves/round-55/census/` → `start.out` only). The census result is verifiable by rerun, but the cited receipt does not resolve — the same "quoted output, no committed receipt" class the round-54 closure routed (defect 2).

## Item 2 — X5 sabotage re-verification + C2 fixture receipts committed — OPEN (in flight)

- At the freeze tree `9c60eae6`, `git ls-tree -r --name-only 9c60eae6 -- .ufo/waves/round-55` lists exactly: `census/start.out`, `controls/base.c1.out`, `controls/base.c2.out`, `preregistration.json`, `sources/git-docs-git-config.html`. At `HEAD` (`8abadfed`) likewise none: no X5 and no C2-smoke receipt is committed anywhere in the lane (`git grep -l 'X5\|48/48\|smoke' HEAD -- .ufo/waves/round-55` hits only `build_spec.py`, `preregistration.json`, `dispatch.json`, `spec.json`, `swarm-registry.json` — i.e. the seat/spec text, not receipts).
- The round-55 spec assigns both receipts to this wave: `build_spec.py:139-140` (`X5ReplaySelftest`: `--selftest` expecting `KLR_SELFTEST pass=48 fail=0`, then two sabotage mutants each FAILing) and `build_spec.py:142` (`X6C2Smoke`: frozen C2 counter `--out .../X6C2Smoke/c2-smoke.out`, `fixture=1 ... scenarios=15/15 ... met=True`).
- At snapshot (10:57 local), both seat dirs had produced uncommitted files:
  - `w1/out/X5ReplaySelftest/selftest-replay-base-9c60eae.log` → `KLR_SELFTEST pass=48 fail=0`, `exit=0`; `selftest-llamacpp-base-9c60eae.log` → `selftest: ok`, `exit=0`. The two sabotage-mutant FAIL demonstrations were not yet present.
  - `w1/out/X6C2Smoke/c2-smoke.out:2` → `fixture=1 lane=1 scenarios=15/15 ... dropped=0 met=True`; `c2-smoke-fixture-scenarios.out` holds the 15 extracted scenario lines.
- Partial supersession: the committed build receipt `.ufo/waves/round-55/measured/c2-build.out:2` (added by `8abadfed`) already prints `fixture=1 lane=1 scenarios=15/15 ... met=True`, so a committed C2 fixture receipt does exist — but it is the build measurement, and it is 15 scenarios, not the round-54 `14/14` count (the `superseded` scenario was added this round, so the old 14/14 artifact is not reproducible and is not what was asked).
- Disposition: **open**. Nothing was committed at the freeze; dedicated receipts are landing in this wave and are not committed at `HEAD`.

## Item 3 — preregistration + base controls committed — CLOSED

- All three artifacts are in the `9c60eae6` tree: `.ufo/waves/round-55/preregistration.json`, `.ufo/waves/round-55/controls/base.c1.out`, `.ufo/waves/round-55/controls/base.c2.out`.
- Counter hashes match the frozen bytes at `9c60eae6`:
  - `git show 9c60eae6:tools/round54-replay-code-audit.py | sha256sum` → `c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af` = `preregistration.json:16`.
  - `git show 9c60eae6:tools/round54-cited-path-check.py | sha256sum` → `d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c` = `preregistration.json:27`.
- Base controls are red exactly as frozen (`controls/base_do_nothing`, `preregistration.json:37-41`):
  - `base.c1.out:2` → `... newrow=0 ... met=False`; `base.c1.out:1` `tip=3a600d2f...`; last detail `newrow: 0 rows new since base`.
  - `base.c2.out:2` → `fixture=1 lane=0 scenarios=15/15 ... dropped=1 met=False`; `base.c2.out:1` `tip=3a600d2f...`; last detail names the dropped citation `SCORECARD.md: corpus/lessons/round-52-verifier-spotcheck.md`.
  - C2's drop horizon is the round-53 tip as frozen: `tools/round54-cited-path-check.py:158` `BASE = "0b75a84c..."`; C1's BASE is the round-54 tip: `tools/round54-replay-code-audit.py:130` `BASE = "3a600d2f..."`.
- Freeze-before-data holds by commit time: `9c60eae6` at `10:24:22-03` precedes the measured receipts (`10:24:37`, `10:25:00`) and every battery receipt (`10:30`+).
- Provenance note (not a proven edit): `preregistration.json`'s mtime is `10:38:10`, later than its commit (`10:24:22`) and later than the first data run, but `git status --porcelain` and `git diff HEAD` are empty and the bytes match the committed blob — a touch/rewrite of identical content, so no semantic difference is provable.

## Item 4 — C1 end-to-end + kill-battery receipts — RECEIPTS CLOSED; FROZEN BATTERY TARGET CONTRADICTED (defect D1)

- Receipts are committed, in `8abadfed` (not in the `9c60eae6` freeze commit):
  - `measured/c1-build.out:2` → `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=True`; last detail `newrow: 2 rows new since base; 1 name the git environment doc: ['| S511 |']`.
  - `measured/c2-build.out:2` → `fixture=1 lane=1 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True`.
  - `.ufo/waves/round-55/c1/battery/`: `control.out` met=True; `m-ldpreload.out` met=False (`envnames=0/3`); `m-text-flip.out` met=False (`bind=0 ... coderuns=0/3`); `m-member-flip.out` met=False (`rehash=3`); `m-ldaudit-foreign.out` met=True; `m-ldaudit-writable.out` met=True; `m-extra-in-tree.out` met=True (`battery-verdicts.txt`).
- **D1 — the executed battery is not the frozen battery, and a frozen mutant passed.** The frozen preregistration names four mutants, `preregistration.json:44`:
  `["m-ldpreload (envnames leg)", "m-ldaudit-writable (code leg)", "m-ldaudit-foreign (hostlibs leg)", "m-member-flip (rehash leg)"]`,
  and its target requires "kill battery: **each named mutant receipt prints met=False** (exit 1) with its named leg failing" (`preregistration.json:19`), with kill rule "the claim is falsified if ... **any battery mutant prints met=True**" (`preregistration.json:20`). The committed receipt `.ufo/waves/round-55/c1/battery/m-ldaudit-writable.out:2` prints `... met=True` (the mutant only added `LD_AUDIT`; the counter's `BAD_ENV` is `("LD_PRELOAD", "DYLD_INSERT_LIBRARIES")` at `tools/round54-replay-code-audit.py:146`, so `envnames` stays 3/3 and `code`/`hostlibs` stay 1/1). The committed driver `.ufo/waves/round-55/c1/battery/run-battery.py:23-85` no longer contains `m-ldaudit-writable` at all; it runs `m-text-flip` (not in the frozen list) and labels `m-ldaudit-foreign` a `"vector"` whose `met=True` is expected (line 57-62, 137-138) — an exception the frozen kill rule does not state. `m-extra-in-tree.out` is likewise a committed battery receipt with no mutant in the driver. No committed document discloses the post-freeze substitution (`grep -rln 'm-ldaudit-writable' corpus .ufo/waves/round-55 --include='*.md' --include='*.json'` matches only `preregistration.json` among committed files; the spec's `M1C1Mut` seat names `m-text-flip` as a mutation target, not as a replacement for the frozen code-leg mutant). Concurrent w1 drafts independently reach the same conflict — `.ufo/waves/round-55/w1/out/Sc2Scoring/proposed-errata.md:22-28` ("the frozen rule fires and C1 is not admitted on it"), `.ufo/waves/round-55/w1/out/Sc3Report/proposed-fixes.md:132-150`, and `Sc4Quality` — all uncommitted at snapshot.
  Consequence: on the frozen documents' own terms the C1 battery leg is not satisfied — a named mutant receipt prints `met=True`, which the kill rule names a falsifier. The lane's own build commit message ("3 live kills + 1 vector analysis") describes the *executed* set, not the frozen set. This is a calibration finding (the exact class the lesson claims to have mined at `corpus/lessons/round-55.md:60-76`, whose closing claim "each battery mutant receipt names the leg it kills" is also contradicted by the three surviving receipts).
- **D3 — receipts under-record their exits and two are unreproducible.** No battery receipt carries the process exit code; the only exit-code record is `run-battery.py`'s stdout summary (`run-battery.py:146-148`), which is not committed. `m-extra-in-tree.out` and `m-ldaudit-writable.out` cannot be regenerated from the committed driver, and their fixture tips (`tip=312530a9...`, `tip=23dc15da...`) are not lane commits, so no committed mutant definition reaches them.

## Item 5 — LOG.md round-55 entry — OPEN

- `git show 9c60eae6:LOG.md` has 2443 lines; `grep -nE 'round-5[45]|Round 5[45]'` returns nothing; the last entry is `- Lesson: corpus/lessons/round-53.md.` at line 2443 (`LOG.md:2440-2443` are the round-53 block). The live file is identical (`git status --porcelain LOG.md` empty; `grep -n 'round-55' LOG.md` → no hit).
- The wave intends it: `build_spec.py:100` assigns `Sc2Scoring` to draft a `## Round 55` SCORECARD section **and** a `LOG.md` round-55 entry paragraph, citing committed receipts. Nothing has landed at `HEAD`; the seat had produced no output at snapshot.
- Routed defect 5 remains open at the freeze (`corpus/lessons/round-54-verifier-spotcheck.md:79`); the SHONEN box-2 dependency named at `build_spec.py:154` is likewise still absent.

## Item 6 — ed135b3c ruling — OPERATOR-OWNED (unchanged, not re-forwarded)

- The lane has no `.ufo/l0-questions.md` (`find . -maxdepth 3 -name 'l0-questions*'` → empty); the filing lives in the fleet repo, read-only: `/home/vgpnk/Projects/shokunin/.ufo/l0-questions.md:184-187` carries the kama round-52 corrections and the round-54 forward ("Forwarding the still-open ruling from rounds 52/53: ... keep, remove, or keep with retraction?").
- No round-55 kama line exists in that file (`grep -n 'round-55' ...l0-questions.md` returns only a `kotoba` line), and the fleet git log shows the last kama L0 forward in `e2e2d10f round-54: kama honest-stop report + ed135b3c L0 forward`. Round 55 neither answers nor re-forwards it.
- Disposition: **operator-owned**, still open; not a lane defect. (The routed item said the same.)

## Defects and proposed fixes

Exact commands above; proposals are in `out/Rev3/fix-proposal.md` (unified diffs / full text). Summary:

1. **D1 (calibration, blocking an admission):** `preregistration.json:44` vs `c1/battery/run-battery.py:23-85` and `m-ldaudit-writable.out:2`. Command: `grep -n 'm-ldaudit-writable\|m-text-flip' .ufo/waves/round-55/preregistration.json .ufo/waves/round-55/c1/battery/run-battery.py` plus `sed -n 2p .ufo/waves/round-55/c1/battery/m-ldaudit-writable.out`. Fix (either, recorded in the round-55 report/errata): (a) declare C1 falsified by its own frozen kill rule and score no claim; or (b) if the frozen mutant list is adjudged a freeze drafting error, file an errata naming the post-freeze substitution and the two void vectors, and re-freeze a corrected prereg (new attempt) whose counter either adds `LD_AUDIT` to `BAD_ENV` (new counter sha, new claim) or whose kill rule names the exempt vectors before data.
2. **D2 (minor):** `corpus/lessons/round-55.md:95,101` cite a non-existent `.ufo/waves/round-55/census/end.out`. Fix: produce and commit it (`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama > .ufo/waves/round-55/census/end.out 2>&1; echo "exit=$?" >> .../end.out`) or strike the citation from the lesson errata.
3. **D3 (minor):** battery receipts carry no exit codes and two lack a committed mutant definition. Fix: commit `run-battery.py`'s summary as `battery/summary.out`, and either add the two mutants to the driver or relabel/delete those receipts.

## Method and limits

- Reverse-engineering only: committed blobs, `git ls-tree`/`git show`/`git grep`, one read-only shared clone at the freeze commit, and two read-only census invocations (the only runs I performed). I did **not** rerun the C1/C2 counters or the battery; the base/build exit codes are taken from the frozen receipts/assignment, and I verified their committed `met=` lines, not their process exits. No `llama-server` was started; no tracer; no pacman; no tool installs; no subagents.
- Arrows: `[INFERENCE]` marks the only interpretive claim — that `m-ldaudit-writable` surviving is a genuine counter limitation rather than a void vector is not adjudicated here; the factual defect is the frozen-list/executed-list divergence and the `met=True` receipt, both observed.

## Written paths (absolute)

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Rev3.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Rev3/census-validate-9c60.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Rev3/census-validate-fleet-kama.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Rev3/battery-verdicts.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Rev3/preregistration.frozen.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Rev3/control.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Rev3/m-ldaudit-writable.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Rev3/m-text-flip.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Rev3/m-extra-in-tree.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Rev3/status.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Rev3/fix-proposal.md
