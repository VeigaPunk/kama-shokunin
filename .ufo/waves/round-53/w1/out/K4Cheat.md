# K4Cheat — round 53, seat K4Cheat: C2 shortcut attack on the frozen cited-path counter

Verdict: **the frozen counter `tools/round53-cited-path-check.py` at the build commit c22602bd can be satisfied at `met=True` by eight distinct cheap changes under which the self-assessment still points at evidence that is not there; none requires touching the counter, two are genuine counter defects (not pre-registered limits), and one (the ref-set dependence) makes the build's own receipt non-reproducible from a dirty clone.** The round-53 build itself is honest: all 14 of its ledger rows re-derive from the lane/fleet history I checked, and its measured receipt reproduces cleanly (`cited=682 unresolved=14 disclosed=14 bad=0 stale=0 dropped=0 met=True`, exit 0, receipt `K4Cheat/e0-build-baseline.out`).

Frozen-counter integrity: `sha256sum tools/round53-cited-path-check.py` = `1afb8b9d32fd0706d0625a4ea70270890039f93fc32635c28b12fa71b13e3080`, equal to the preregistration's `counter_sha256`. I never edited the counter, the lane, the fleet, or the controls; every attack ran on fixture branches/commits inside my own `git clone --shared` scratch clones with the fixture identity (`-c user.name=fx -c user.email=fx@invalid`, toplevel asserted before every commit), exactly as the shared-resources contract prescribes.

## Environment note (evidence for the instability finding)

- Counter runs read the fleet at its **live HEAD** (`--fleet-rev` default `HEAD`, counter line 438-439): the build receipt pinned `fleet=ee9f7341…`; my baseline run hours later saw `fleet=33540c6e`, then `ccc6ce89`, then `305a7cac` (my fleet clone) — the fleet repo receives commits from other lanes continuously.
- Counter history legs use `git log --all` on the measured clone (counter line 133 `history_paths`, line 274 `moved`'s `git log --all -1 -- e`), so the verdict at a fixed lane commit also depends on the clone's ref set (demonstrated below, attack X).

## Attacks (all receipts in `.ufo/waves/round-53/w1/out/K4Cheat/`; driver `reproduce.sh` regenerates every one)

### a1 — empty files at every dead path (the seat's idea #1) — PASSES
From the base `4229ea1b`, create a 0-byte file at each of the 16 dead lane expansions (15 paths incl. both `{base,after}.out` members and a file under each dead directory; the `tests/report-audit/…` token needs a literal `…` file) plus the same one-line in-place fleet-path edit the real build used (`SKILL.md` line 113 → `~/Projects/ufo-fsd-alpha/scripts/local-helper.mjs`). No ledger rows, no real corrections.
Command: `attack1-stub.sh` → tip `ea441679ffd5f0e42f3e0056e0312ff97a24f9d5`; counter exit 0:
`fixture=1 lane=1 scenarios=8/8 cited=678 unresolved=0 disclosed=0 undisclosed=0 bad=0 stale=0 dropped=0 met=True` (`a1-stub-receipt.out`). Every stub is blob `e69de29` (0 bytes). The SCORECARD/SKILL/SHONEN sentences still describe receipts, llama.cpp sources and seat reports; the files are empty. **Cheapest full-meet alternative to the real build: one commit, zero ledger.**
Mechanism: `resolve()` (counter lines 203-214) is pure path existence via `matches()`; content is never read except for line counts. This exact limit ("a citation resolves when its path exists; the counter does not check that the cited file says what the citing sentence claims") is pre-registered in the preregistration `limits` — so a1 is a **disclosed limit, demonstrated, not a new defect**.

### a2 — cite dead paths in prose, without backticks (idea #3) — PASSES  **[genuine gap]**
On the build tree, append to `SCORECARD.md` (outside fences): "…the calibration evidence … is further documented in .ufo/waves/round-53/w1/out/K4CheatGhost/evidence.txt, tools/kama-no-such-tool.py, corpus/lessons/round-53-ghost.md lines 40-60, tests/no-such-fixture.py and registry/no-such-ledger.tsv; per those sources the scores above are fully supported." — no backticks anywhere.
Tip `459d8a7bfc8dcc6e047f7305a969914a89bbfe16`; counter exit 0: `cited=682 … undisclosed=0 bad=0 stale=0 dropped=0 met=True` (`a2-prose-receipt.out`; cited count identical to baseline — the prose is invisible).
Mechanism: the frozen parser only scans backtick spans (line 156 `re.findall(r"`([^`\n]+)`", line)`); a root-path-shaped prose token is not a citation. The C2 *claim* says "every repository path that SCORECARD.md, SHONEN.md and SKILL.md cite as evidence", with no backtick qualifier; the counter measures a strictly narrower relation. This coverage gap is **not** among the preregistered limits (those cover only *other files* being out of scope). Zero files, one paragraph — the cheapest kill available.

### a3 — `moved` row to an unrelated empty file (idea #2) — PASSES
Fixture branch: commit empty `tools/k4cheat-a3-gone.py` and empty `tools/k4cheat-a3-innocent.py`, delete `gone.py`, cite `` `tools/k4cheat-a3-gone.py` ``, ledger row `moved tools/k4cheat-a3-innocent.py` (row appended to the build's ledger, not replacing it).
Tip `81f55b85d774a27e454d209efbf2f320dabe4ace`; counter exit 0: `cited=683 unresolved=15 disclosed=15 … met=True` (`a3-moved-receipt.out`).
Mechanism: `moved` re-derivation (lines 270-282) only checks `old.stdout == new.stdout` — the **blob id**. All empty files share blob `e69de29…`, so the row "the evidence moved to `tools/k4cheat-a3-innocent.py`" re-derives against a file with no content relationship to the claim. Per-spec as frozen, but gameable to arbitrary degrees of emptiness.

### a4a — `untracked` row: disclosure is a file merely existing on disk under the fleet root (idea #5) — PASSES
Branch cites `` `scripts/driver.log` `` with ledger row `untracked -`; in a full shared clone of the fleet I created `scripts/driver.log` on disk only (never committed, not in any tree).
Tip `252b958dc938e21c947dfb60e2345b3ba37e1c44`; counter exit 0 with `--fleet <clone>`: `cited=683 unresolved=15 disclosed=15 … met=True` (`a4a-untracked-receipt.out`).
Mechanism: `untracked` check (lines 312-318) is `v=="missing" and e.startswith(scripts/|templates/|.ufo/) and e not in fleet.tree and os.path.exists(fleet.path/e)`. No commit, no content, no provenance — anyone who can write under the fleet root manufactures disclosure. I did not touch the real fleet (read-only); the demonstration uses a scratch clone, which is the honest way to run it. (On the real host, this class is exactly what the build legitimately used for `.ufo/watchdog.log` — file verified present on disk, 156988 bytes.)

### a4b — commit an empty stub into the FLEET tree; every lane citation of it resolves (idea #4) — PASSES
In the fleet scratch clone, commit empty `scripts/k4cheat-stub.sh`; on a lane branch off the build, cite `` `scripts/k4cheat-stub.sh` `` with **no ledger row**.
Tip `a09f324d5c90ae10e4acc25b242cee2ffe26f649`; counter exit 0 with `--fleet <clone>`: `cited=683 unresolved=14 disclosed=14 … met=True` (`a4b-fleetstub-receipt.out`).
Mechanism: `resolve()` checks lane tree, then `fleet.tree` at live HEAD — fleet contents are trusted without any base-comparison. A single fleet commit resolves the citation for the lane and for every other lane. Requires fleet write access, so it is outside the lane threat model, but it is the fleet-side mirror of a1 and worth recording because C2's "fleet tree" leg has no pinning at all.

### a5a — drop a citation from SHONEN.md: invisible (asymmetry finding) — PASSES  **[coverage gap, claim-side]**
Branch `66629e33323fa58ef4821892887542cef6f82400` removes the backticks around `.ufo/waves/round-16/live/receipt.json` on SHONEN.md line 8 (the claim text "10/10 checks on the pinned llama.cpp b11755 build" remains, now with no evidence pointer). Counter exit 0: `cited=681 … dropped=0 met=True` (`a5a-shonen-drop-receipt.out`). The `dropped` leg only compares **SCORECARD.md** token sets (counter lines 365-369: `show(base_lane.path, base_lane.rev, "SCORECARD.md")`), so claims can silently shed SHONEN.md/SKILL.md evidence pointers. This matches the claim wording ("no SCORECARD.md citation dropped"), so it is a claim-scope gap rather than a counter defect — but a calibration instrument that guards one of three self-assessment surfaces should be reported as such.

### a5b — drop a citation from SCORECARD.md: caught (contrast) — FAILS as expected
Branch `0acfa5e88b41a58d38d3d6d2cccbffdac5464a33` turns `` `.ufo/l0-questions.md` `` into prose. Counter exit 1: `dropped=1 met=False` with `detail: dropped SCORECARD.md citation '.ufo/l0-questions.md'` (`a5b-scard-drop-receipt.out`). Confirms the dropped leg works exactly where the docstring says it does.

### a6 — `eof` row naming the attacker's own commit (idea #6) — PASSES
Branch: commit `corpus/k4cheat-a6-x.md` with 500 lines (`8d07ca5620b0a13007a5f25f33756678a653b0fb`), then truncate to 2 lines, cite `` `corpus/k4cheat-a6-x.md:400` ``, ledger row `eof 8d07ca56…` (the same branch's parent — my own fixture commit, not history anyone else filed).
Tip `d26f8a47fededba44061532be3f66ae67b444656`; counter exit 0: `cited=683 unresolved=15 disclosed=15 … met=True` (`a6-eof-receipt.out`). The self-assessment cites line 400 of a 2-line file; the counter reports the citation disclosed.
Mechanism: `eof` (lines 284-296) only needs *some* commit in the lane or fleet object store where the path had ≥ N lines; `cat-file -e` (line 289) accepts any object present — the commit need not be an ancestor of tip, need not predate the citation, and the anchor never needed to be valid at base. A commit of *another* repo would fail `cat-file` in both repos (I checked the code path), but the attacker's-own-commit version is strictly cheaper. The class's stated intent ("the anchor named an older version") is per-spec, so this is a frozen-tradeoff demonstration, not a defect.

### X — ref-set instability: the build's own ledger goes bad in a dirty clone  **[genuine defect, demonstrated]**
While my a1 fixture branch still existed in the lane clone, I re-ran the counter at the unchanged build commit. Result (this run's terminal output, also reproducible via `reproduce.sh`'s final step): `fixture=1 lane=0 … undisclosed=7 bad=7 … met=False` — the seven `never` rows flipped to `bad: … was a path in some commit`, because `never` re-derivation (line 265-268) uses `lane.hist()` = `git log --all --name-only` (line 133) over **all refs of the measured clone**, and a1's commits create exactly those paths. After `git branch -D k4cheat-a1-stubs`, the same command at the same tip returns `met=True` again (verified twice). Consequences: (i) C2 is not a pure function of the lane commit — two honest seats measuring with different clone ref sets can disagree, one of them flunking a past build; (ii) any future lane ref (an integration branch, a recovered object) that adds a path named by a `never` row turns the build's frozen receipt from `met=True` into `met=False` — a maintenance landmine the frozen counter cannot re-derive its way out of (the row goes *bad*, not merely *stale*; either fails the run). The `moved` leg (line 274) has the same `--all` shape. The lane is jj-colocated with a rich ref set, so this is not theoretical.

## Classification (what the canonical judge should do with each)

- **Pre-registered, accepted limits (demonstrated, do not re-open):** a1 empty-stub resolution and a6 anchor-line-count (both are verbatim the preregistration `limits` entries for C2). The build relied on the counter's frozen semantics and met them honestly.
- **Frozen-counter defects to fix in a future instrument round (cannot fix in place now):** (1) a2 prose-citation blindness — claim/counter relation mismatch, not in `limits`; (2) X ref-set dependence of `never`/`moved` on `git log --all`, plus the live `--fleet-rev HEAD` and live upstream fetches making receipts drift with the environment.
- **Claim-scope gaps (fix the claim or extend the counter next round):** a5a dropped-leg asymmetry across the three surfaces.
- **Out-of-threat-model but recorded:** a4b fleet-tree trust without pinning.
- Proposed corrections (advisory only — counters are frozen): `K4Cheat/proposed-round54-cited-path-check.patch` — scope history legs to commits reachable from `BASE` or `tip` (with a no-BASE fallback for fixture repos), extend the dropped leg to all three surfaces as a separate `dropped2` advisory count, and flag prose-shaped lane/fleet-root tokens as advisory `detail:` lines so a2-style evidence claims at least surface in the receipt.

## Build legitimacy spot-checks (the real build is fine)

- `deleted` row evidence `9874e455…`: commit exists; `.ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp` present at `9874e455^`, absent at `9874e455` — re-derives.
- `untracked` row `.ufo/watchdog.log`: present on disk at the real fleet root (156988 bytes, uncommitted) — re-derives.
- `never` rows: with a lane-canonical ref set, `git log --all` shows none of the seven tokens as a path (the a1 experiment is precisely the existence proof of the flip side).
- Baseline at the build reproduced `met=True` twice on independent fleet HEADs (33540c6e, ccc6ce89) — modulo the X-instability, the build receipt stands.

## Hygiene

- No lane/fleet files written; all attacks in `$S/lane` / `$S/fleetfx` scratch clones; fixture identity only inside scratch; no pacman/installs needed (python3 stdlib only); no services started; no llama-server processes started (C2 is pure git+HTTP); counters never wrapped; no subagents; no `agent://all` messages.
- Scratch `/fast/scratch/hyaku/kama-r53/K4Cheat` removed at end of seat (receipts preserved under this directory; `reproduce.sh` regenerates them).

## Files written (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/K4Cheat.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/K4Cheat/reproduce.sh`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/K4Cheat/attack1-stub.sh`, `attack2-5.sh`, `attack3-4-6.sh` (the as-run drivers; attack3-4-6.sh's a4a/a4b sections were superseded by the inline corrected reruns captured in `reproduce.sh`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/K4Cheat/{e0-build-baseline,a1-stub,a2-prose,a3-moved,a4a-untracked,a4b-fleetstub,a5a-shonen-drop,a5b-scard-drop,a6-eof}-receipt.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/K4Cheat/proposed-round54-cited-path-check.patch`
