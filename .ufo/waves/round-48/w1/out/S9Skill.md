# S9Skill — round 48, kama lane: SKILL.md round-48 instrument registry rows and the v5 how-to

**Verdict:** rows drafted for the two round-48 counters and for the v3 / v5 / `--compare` instrument changes, plus the v5 re-running how-to; on a `git clone --shared` whose tree is `380bcdff` with only my 24 appended `SKILL.md` lines, `python3 tools/gate-registry-check.py` reports `registered 42 unregistered 0 defective 0` (exit 0) and `python3 tools/gate-registry-check.py --selftest` reports `GATE_SELFTEST pass=6 fail=0` (exit 0). The L1 has since written its own round-48 section into the lane working tree (uncommitted, `SKILL.md:1464-1482`); that draft also measures clean under the same gate (recorded below). Both drafts register the same two counters — the L1 must pick one, not both.

Axis: operability. Milestone: r48 attack and frontier.

## 1. What I read (contract, not rerun)

- `tools/round48-append-audit-v3-check.py:1-140` — C1 legs (selftest / contract / lane / fixture / stable), output line, exit map, `PREDICATE`.
- `tools/round48-live-replay-v5-audit.py:1-140` — C2 legs (receipts / recordcheck / replay / compare / tamper / urlswap / newrow), output line, exit map, `PREDICATE`, and `main()` (`could-not-evaluate` → exit 2 from `git rev-parse`/`git archive`).
- `tools/append-only-audit.py:1-90` (v3 definitions), `render()` and `exit_code()` (event line, `summary` keys, exit 1 on partial/unrestored/regressed/vanished/bad_declarations).
- `tools/kama-llamacpp-live.py:1-44` (v4/v5 receipt docstring), `1450-1480` (provenance argument validation), `1550-1570` (record-time verification, `schema` upgrade).
- `tools/kama-live-replay.py:1-42` (stable projection, `--compare`), `84-131` (refusal vocabulary), `204-272` (replay flow, `Refused` → exit 2).
- `tools/gate-registry-check.py:1-43` (row meaning: thin-row, empty-entry, empty-exit-map, missing-path), `180-216` (`evaluate`, `RE_PATH` scan), `REGISTRY_HEADER`, `main`.
- `registry/append-only-contract.tsv` — 9 rows; `SKILL.md` itself is not a declared append-only file (only `corpus/SOURCES.md` cites `SKILL.md:578` as `declared_at`), so editing the how-to is not an append-only event.
- `.ufo/waves/round-48/controls/base.c1.out`, `base.c2.out`, `.ufo/waves/round-48/c2/live/install.txt`, `.ufo/waves/round-48/c2/live/receipt-{1,2,3}.json`.

## 2. Measurements this seat ran (all on a clone, never the lane)

Scratch: `S=/fast/scratch/hyaku/kama-r48/S9Skill`; `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`; `git -C $S/lane checkout -q --detach 380bcdff9c8af06997c482f6eb03db926a794a2b`; `git -C $S/lane rev-parse --show-toplevel` = `/fast/scratch/.../S9Skill/lane` (asserted before every commit).

| Command | Output | Exit |
|---|---|---|
| `cd $S/lane && python3 tools/gate-registry-check.py --repo .` (baseline, untouched 380bcdff) | `unregistered tools/round48-append-audit-v3-check.py`, `unregistered tools/round48-live-replay-v5-audit.py`, `registered 40 unregistered 2 defective 0` | 1 |
| `python3 tools/round48-append-audit-v3-check.py --repo $S/lane --tip 380bcdff9c8af06997c482f6eb03db926a794a2b --scratch $S/measure/c1 --out $S/measure/c1.out` (5.3 s) | `selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True`; `tip=380bcdff9c8af06997c482f6eb03db926a794a2b`; no `detail:` lines | 0 |
| `python3 tools/round48-live-replay-v5-audit.py --repo $S/lane --tip 380bcdff9c8af06997c482f6eb03db926a794a2b --scratch $S/measure/c2 --out $S/measure/c2.out` (15.8 s, ~70 MB github.com + ~4 MB huggingface.co) | `receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True`; `tip=380bcdff… started=2026-10-26T22:35:13.593031+00:00`; no `detail:` lines | 0 |
| `python3 tools/append-only-audit.py --selftest --scratch $S/measure/st-a` | `AOA_SELFTEST pass=27 fail=0` | 0 |
| `python3 tools/kama-live-replay.py --selftest --scratch $S/measure/st-r` (dir must already exist) | `KLR_SELFTEST pass=21 fail=0` | 0 |
| `python3 tools/kama-llamacpp-live.py --selftest` | `selftest: ok; closed tcp6 listeners …` | 0 |
| receipt inspection (`json`, all three) | `schema kama-llamacpp-live/v5`, `outcome pass`, 11 checks all `evaluated`, `provenance.model.commit 499bc882…`, `provenance.verified.at record`, `teardown.log_path null`, 3 inlined log lines, `server.sha256 35ac50fb…`, `model.sha256 270cba1b…` | — |

## 3. My draft and its gate evidence

Applied in the clone: `git show 380bcdff:SKILL.md > SKILL.md` then append `…/out/S9Skill/skill.md`; commit `7b8bf454315e8d4e11612c2cf990814f8c2a0318` ("registry: round-48 rows (S9Skill draft)"); `git diff --stat 380bcdff -- SKILL.md` = `1 file changed, 24 insertions(+)`.

- `python3 tools/gate-registry-check.py --repo .` → `registered 42 unregistered 0 defective 0`, **exit 0** (`gate-s9draft.out`).
- `python3 tools/gate-registry-check.py --selftest` → six arms PASS, including `PASS lane-tip 7b8bf454315e: exit=0 line='registered 42 unregistered 0 defective 0'`; `GATE_SELFTEST pass=6 fail=0`, **exit 0** (`gate-selftest-s9draft.out`).
- Fail-capability control: in the clone, one cited path in the *pinned-values* cell changed to `.ufo/waves/round-48/c2/live/install-absent.txt` → `defective tools/round48-live-replay-v5-audit.py: missing-path:.ufo/waves/round-48/c2/live/install-absent.txt`, `registered 42 unregistered 0 defective 1`, **exit 1** (`gate-failcap.out`); tree restored from `skill.md` and re-committed.
- Row shape: each row is exactly 5 cells with no literal `|` inside a cell (`selftest=0/1`, `--contract <tsv> or --files …`), so the gate's fixed column indices and the rendered table agree (measured: cells = 5, 21–2333 bytes per row).

The five rows: `Round-48 C1 append-only v3 calibration audit`, `Round-48 C2 live receipts v5 operability audit (sourced)`, `Round-48 append-only audit v3`, `Round-48 live lifecycle receipt v5`, `Round-48 live receipt replay, stable projection and --compare`; then `### Re-running live evidence (v5, round 48)` with record (archive + pinned `/resolve/<40-hex>/` model URL, `--server-archive`), replay (`--server-archive` passed for v5, stable projection), offline `--compare`, and the graded counter invocation.

Pins in the draft, all from §2 or from files I read: base control `base.c1.out` = `selftest=0 contract=0 lane=0 fixture=0 stable=0 … lane_failures=NA … fixture_fail=11 met=False` with `contract: header is not the v3 header`; base control `base.c2.out` = `receipts=0 … replayed=0/3 met=False`; measured tip values as in §2 (5.3 s / 15.8 s, `rows=9 files=89 lane_events=5 ungraded_lines=89`, `replayed=3/3`); `AOA_SELFTEST pass=27 fail=0`; `KLR_SELFTEST pass=21 fail=0` with the eight v5 arms named; the 13-token refusal vocabulary of `kama-live-replay.py` plus `could-not-run:<exc>`.

## 4. The L1's draft (already in the lane working tree)

`SKILL.md:1464-1482` (uncommitted, `M SKILL.md` in `git status`) holds `## Round-48 instrument registry (append-only v3 regions, live receipts v5)` with five rows and `### Re-running live evidence (v5, round 48)`. Copied verbatim into a clone commit (`721dbbc7bbae`) and gated:

- `python3 tools/gate-registry-check.py --repo .` → `registered 42 unregistered 0 defective 0`, exit 0 (`gate-l1draft.out`).
- `python3 tools/gate-registry-check.py --selftest` → `PASS lane-tip 721dbbc7bbae: exit=0 …`, `GATE_SELFTEST pass=6 fail=0`, exit 0 (`gate-selftest-l1draft.out`).

So the known integration item "gate-registry-check lists the two round-48 counters unregistered" is already resolved by the L1's working tree as of this run. My rows add: the exit-2 token `could-not-evaluate:` and the base-control pins for both counters, the full refusal vocabulary for the replay tool, the `compare could-not-read` exit-2 line, and pipe-free cells (§5 F1/F2).

## 5. Findings (frozen tools; reported, not edited)

**F1 — the gate never checks path tokens in the Exit map cell.** `tools/gate-registry-check.py:206` scans `for c in (row[1], row[3], row[4])`. Demonstrated: mutating a path that occurs only in an exit-map cell (`.ufo/waves/round-48/controls/base.c2.out` → `base-c2-absent.out`) left the gate at `registered 42 unregistered 0 defective 0`, exit 0, while the same mutation in a pinned-values cell produced `defective … missing-path:…`, exit 1 (`gate-failcap.out`). Proposed fix: `for c in (row[1], row[2], row[3], row[4])` (the `RE_PATH` filter already drops non-path tokens, so `<path>:<line>` placeholders stay exempt).

**F2 — literal `|` inside a cell shifts the gate's column indices.** Round-47 rows leave `selftest=0|1`, `receipts=0|1 …` unescaped (`SKILL.md:1450`, `:1451`, `:1453`), so `cells()` returns more than five cells and `row[2]`/`row[4]` are fragments; paths cited only in those rows' write-scope cells are unchecked. My rows avoid the character entirely (`0/1`, `or`), measured as 5 cells each. Proposed fix: normalise those three cells (or have `cells()` honour `\|`).

**F3 — the C2 counter's docstring overstates the record-time flag rule.** `tools/round48-live-replay-v5-audit.py:33-36`: "given any provenance flag, the live tool requires all of `--server-asset-url`, `--server-asset-sha256`, `--server-member`, `--model-url` and `--server-archive`". The tool requires only the four v4 flags together (`tools/kama-llamacpp-live.py:1462-1466`) and `--server-archive` merely selects v5; the pinned-`/resolve/<40-hex>/` check runs only with the archive (`:1474-1478`). Consequence, observable without changing anything: the four flags with no archive still record a **v4** receipt with an unpinned (`main`) model URL, i.e. the D6 pin is enforced only on the v5 path. The counter's `recordcheck` leg is consistent with the code (it tests a partial flag set), so this is prose, not a grading defect. Proposed fix: reword that docstring sentence to "the four v4 flags must come together; `--server-archive` additionally requires the pinned model URL and the archive/member digests".

**F4 — two seat drafts now exist.** The L1 draft (§4) and mine (§3) both register the same two counters and both gate clean; applying both would duplicate rows (the gate would not complain). Recommendation: take one — if the L1 draft is kept, port §3's base-control pins and the exit-map `could-not-evaluate:` token and drop the pipe-free rewriting needs (F2) from the older rows instead.

Not findings (already known, per the assignment, and not re-reported): the round-41/42/43 counters' spot-check count 33 vs 34; the hexrun-census unknown `d0012618`.

## 6. Touched surfaces and limits

- Wrote only: `kama-shokunin/.ufo/waves/round-48/w1/out/S9Skill/skill.md`, `…/out/S9Skill.md`, and the ten evidence files under `…/out/S9Skill/`. Nothing in the lane, fleet root, `~/.local/bin`, or the jj/Git index of the lane was written; the clone at `$S/lane` is scratch and was removed.
- No tools installed or upgraded (nothing was needed); no service started, stopped, or left running; the `llama-server` in the C2 replay legs belonged to the counter and is torn down by it.
- Out of scope for this seat: `SCORECARD.md` §Round-48 measured results, the round-48 closure, the frozen counters / preregistration / controls, `tools/gate-registry-check.py` itself, and the C1/C2 claims' verdicts.
- I did not re-run the counters to decorate the report; every number above comes from a run listed in §2 or from a file I read, and the two C2 network legs ran once each.

## 7. Artifacts written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Skill.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Skill/skill.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Skill/gate-s9draft.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Skill/gate-selftest-s9draft.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Skill/gate-failcap.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Skill/gate-l1draft.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Skill/gate-selftest-l1draft.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Skill/c1-counter-380bcdff.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Skill/c2-counter-380bcdff.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Skill/aoa-selftest.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Skill/klr-selftest.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Skill/live-selftest.out`
