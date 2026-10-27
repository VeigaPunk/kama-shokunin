# Sc5Skill — round-55 instrument-registry addition (lane kama)

**Verdict:** The paste-ready `## Round-55 instrument registry` section is delivered with four 5-cell rows (both frozen counters with role + full sha256, the kill-battery harness, the lesson), anchored to `SKILL.md:1592` / appended after `SKILL.md:1600`, and it re-checks clean against the frozen C2 counter (`lane=1 … dropped=0 met=True`, rc 0) — with two frozen-contract inconsistencies recorded, not adjudicated: the C1 kill rule fires on the battery's own vector receipt, and the freeze's mutant list names a mutant the landed runner does not carry.

Seat Sc5Skill, round-55 w1, leaf (no dispatch, no subagents). No lane file, lane index or jj state was touched; the only git mutations were fixture commits inside my own scratch clone (toplevel asserted).

## 1. Row shape and anchor (observed)

```
$ wc -l SKILL.md                       → 1600
$ grep -n '^## ' SKILL.md | tail -2     → 1592:## Round-54 instrument registry (hardened code-identity and cited-path counters, seat-report immutability)
                                            (no later header)
$ sed -n '1596p;1600p' SKILL.md        → 1596: | Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
                                        1600: | Seat-report immutability | measurement: ...
$ sed -n '1593,1595p' SKILL.md         → blank, `Rows for the round-54 counters …`, blank
$ tail -c1 SKILL.md | od -An -c        → \n   (file ends with a newline)
```

Five columns, escaped `\|` inside cells, one row per surface — the shape used by the round-53 (`SKILL.md:1565`) and round-54 (`SKILL.md:1596`) registries. The proposed section is appended after line 1600 with one blank separator line; the header it follows is `SKILL.md:1592`. There is no existing `## Round-55` header in SKILL.md (`grep -n 'Round-55' SKILL.md` → no match) and none in SCORECARD.md.

Deliverable: `.ufo/waves/round-55/w1/out/Sc5Skill/registry-round55.md`, 36 lines, sha256 `a4b682db6747b422d0e61db5497a238a71ea201d1a42a532bcf89e0db0bcf825`; the exact application is `.ufo/waves/round-55/w1/out/Sc5Skill/proposed-skill-append.diff` (`@@ -1598,3 +1598,40 @@`).

## 2. Frozen identities verified (commands and outputs)

```
$ git show 9c60eae6f7ed84f7da93d219a406aadc30958c6c:tools/round54-replay-code-audit.py | sha256sum
c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af
$ git show 9c60eae6:tools/round54-cited-path-check.py | sha256sum
d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c
$ sha256sum tools/round54-replay-code-audit.py tools/round54-cited-path-check.py   (worktree, at the later measurement commit)
c81fe971…0579af  c81fe971…
d70a17291…510c    d70a1729…
$ git show 9c60eae6:corpus/lessons/round-55.md | sha256sum   → db45006dc5b5f632961fad96cf74811a5118eee4ea9ba7c3a088c28309d398bc
$ git show 8abadfed:.ufo/waves/round-55/c1/battery/run-battery.py | sha256sum → 49a57a155cd6b31034d9c0a35ef8cdbd99c701d110c7fd662f222e0bdcda2945
```

Both values equal `.ufo/waves/round-55/preregistration.json` `claims.C1.counter_sha256` (`:16`) and `claims.C2.counter_sha256` (`:27`). The counters did not change between the freeze `9c60eae6` and the measurement commit `8abadfed`; the battery harness exists only from `8abadfed` (`git show 9c60eae6:.ufo/waves/round-55/c1/battery/run-battery.py` → "exists on disk, but not in" 9c60eae6).

Commit history used (`git log --oneline 3a600d2f..HEAD`): `9c60eae6` freeze, `8abadfed` measurements + battery + wave spec.

## 3. The four rows (what each claims, and where it is pinned)

1. **Round-55 C1 replay-code audit** — operability 8→8; frozen role is claim C1; exit map 0 met / 1 not met / 2 could not evaluate (git failure), from the docstring `tools/round54-replay-code-audit.py:97` and the returns at `:895`/`:966`; printed keys `bind sealed code teardown newrow bound sealedruns coderuns envnames hostlibs anon twopass rehash met`; `anon`/`rehash` are failing-leg counts (`:943`, `:954`), 0 in a met run; pinned to the round-48 v5 receipts, the server/archive/model digests, the 13-name host set, base `3a600d2f`, the two committed controls.
2. **Round-55 C2 cited-path check** — calibration 7→7; frozen role is claim C2; exit map 0/1/2 from `tools/round54-cited-path-check.py:140` and `:843`/`:856`; 15 scenarios (`SCENARIOS = 15`, `:168`); the row separates the **internal BASE `0b75a84c`** (`:28`) from the **do-nothing control's `--tip 3a600d2f`** (`receipts/base.c2.out` line 1: `tip=3a600d2f…`), because conflating them is exactly the pre-freeze defect the lesson records; ledger row `registry/cited-path-corrections.tsv:46` (`superseded`).
3. **Round-55 C1 kill battery** — control harness, not a gate; constants at `run-battery.py:13-17`, `MUTANTS` at `:23`, per-receipt summary printed to stdout at `:146`, exit `0 if all(...) else 1` at `:148`, `return 2` on clone/reset/anchor/commit failure (`:101`, `:124`, `:127`, `:134`); receipts are counter `--out` files in `.ufo/waves/round-55/c1/battery/`.
4. **Round-55 lesson** — `corpus/lessons/round-55.md`, kind data/reference, no exit; sha256 `db45006d…d398bc`; the row names the section-level facts (S511 at `corpus/SOURCES.md:264`, S510 `used-by` re-pointed at `:263`, census start exit 1 `E11 S510 missing used-by corpus/lessons/round-54.md` at `.ufo/waves/round-55/census/start.out`, KQ97).

Receipt second lines quoted into the rows (copies in `out/Sc5Skill/receipts/`):

```
controls/base.c1.out   : newrow=0 … anon=0 twopass=3/3 rehash=0 met=False
measured/c1-build.out  : bind=1 sealed=1 code=1 teardown=1 newrow=1 … anon=0 twopass=3/3 rehash=0 met=True
controls/base.c2.out   : fixture=1 lane=0 scenarios=15/15 … dropped=1 met=False   (+ detail: dropped citation `SCORECARD.md: corpus/lessons/round-52-verifier-spotcheck.md`)
measured/c2-build.out  : fixture=1 lane=1 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True
battery/control.out    : … newrow=1 … met=True
battery/m-ldpreload.out: … envnames=0/3 … met=False        (+ detail: envnames b1: env: server environment carries LD_PRELOAD)
battery/m-text-flip.out: bind=0 … code=0 … met=False       (+ detail: code b1: … != archive digest; rehash b1: … changed after the observation)
battery/m-member-flip.out: … rehash=3 met=False            (+ detail: rehash b1: …libggml-cpu-zen4.so changed after the observation)
battery/m-ldaudit-foreign.out: … hostlibs=3/3 … met=True   (kind `vector`, expected)
```

Exit codes are **not** in any receipt: they are the frozen target's declarations (`preregistration.json:19`, `:31`) and the counters' own returns. My row states them as exit maps, not as re-observed values.

## 4. Addition re-check (new verification, fixture only)

```
$ git clone --shared <lane> $S/lane; git -C $S/lane rev-parse --show-toplevel   → $S/lane
$ cp <section-append> $S/lane/SKILL.md
$ git -C $S/lane -c user.name=fx -c user.email=fx@invalid commit -q -m "fixture: …"   → dd03f2b6a8de7e8b0f0310c272574907ff944e98
$ python3 tools/round54-cited-path-check.py --repo $S/lane --tip dd03f2b6… --scratch $S/c2check3 \
      --out out/Sc5Skill/receipts/c2-addition-check.out
tip=dd03f2b6a8de7e8b0f0310c272574907ff944e98 fleet=666bc1efcddd4b711173f23def3278cfe54a418f
fixture=1 lane=1 scenarios=15/15 cited=710 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True
rc=0
```

`cited` 693 → 710 (17 distinct new tokens in the section), nothing unresolved, undisclosed, bad, stale or dropped: the section is citation-clean under the frozen C2 parser. Receipt sha256 `b9dbec9dc83ad1fd19e34593613e58bf9fe58194fcedd8fe15d5c8d6cf009f15`.

## 5. Findings (conflicts quoted verbatim; frozen files not edited)

**F1 — the frozen C1 kill rule fires on the battery's own vector receipt.**
`preregistration.json:20` (verbatim): "the claim is falsified if the base/do-nothing control prints met=True, if any battery mutant prints met=True, if the build measurement prints met=False, or if the counter bytes at measurement differ from counter_sha256".
The harness labels `m-ldaudit-foreign` a `vector` whose expected outcome is `met=True` (`run-battery.py:59`: `# expect met=True: the LD_AUDIT vector is void on this glibc; the`, and `:137-138`: `if kind == "vector": ok = rc == 0 and met`), and its receipt is `hostlibs=3/3 … met=True`. Shown by:

```
$ sed -n '20p' .ufo/waves/round-55/preregistration.json
$ sed -n '2p'  .ufo/waves/round-55/c1/battery/m-ldaudit-foreign.out
$ sed -n '59p;137,138p' .ufo/waves/round-55/c1/battery/run-battery.py
```

Read literally, "any battery mutant prints met=True" falsifies C1 on this receipt (and on `m-ldaudit-writable.out`, F2). Proposed fix (freeze-safe, disclosure only; full text is the paragraph after the table in `registry-round55.md`): state the vector receipt and the rule's literal reading in SKILL.md and let the L1 resolve the claim; do not edit the frozen preregistration. Any edit to the prereg's kill rule after data would be a post-hoc predicate change.

**F2 — the freeze's mutant list and the landed runner differ.**
`preregistration.json:44`: `"mutants": ["m-ldpreload (envnames leg)", "m-ldaudit-writable (code leg)", "m-ldaudit-foreign (hostlibs leg)", "m-member-flip (rehash leg)"]`.
`run-battery.py:23` `MUTANTS` keys, extracted with

```
$ python3 -c "import re;s=open('.ufo/waves/round-55/c1/battery/run-battery.py').read();print(sorted(re.findall(r'\"(m-[a-z-]+)\": \(', s)))"
['m-ldaudit-foreign', 'm-ldpreload', 'm-member-flip', 'm-text-flip']
```

So `m-ldaudit-writable` is named by the freeze and absent from the runner, replaced by `m-text-flip` (code leg); a receipt `m-ldaudit-writable.out` nevertheless exists in the battery directory with `met=True` (24 lines, `tip=23dc15da…`, `envnames` detail: 6 names). `m-extra-in-tree.out` (`met=True`) is likewise a receipt the harness never produces. Proposed fix: disclosure (already in the section's prose), since re-running a changed battery would invalidate the committed receipts.

**F3 — the battery's per-receipt exit codes are not captured anywhere.**
`preregistration.json:19` targets "each named mutant receipt prints met=False (exit 1)"; the receipts are the counter's `--out` files and contain no exit code (`grep -c 'exit=' .ufo/waves/round-55/c1/battery/*.out` → 0 for every file), while the harness prints `exit=<rc>` only to stdout (`run-battery.py:146`) and no run log is committed (`git show --stat 8abadfed` lists no `battery/*.log`/summary file). Proposed fix, future rounds only (validated with `patch -p1 --dry-run` rc 0 against the committed harness, not applied): `.ufo/waves/round-55/w1/out/Sc5Skill/proposed-harness-summary.diff` tees the summary to `.ufo/waves/round-55/c1/battery/summary.out`.

**F4 — the C2 build receipt is not reproducible at the default fleet revision.**
`measured/c2-build.out` line 1: `fleet=6c4aba34c2a22519152d8c6f32e1039eecb1381b`; the counter's `--fleet-rev` defaults to `HEAD` (`tools/round54-cited-path-check.py:823`), and the fleet repo's HEAD today is `666bc1efcddd4b711173f23def3278cfe54a418f` (my run, §4). Reproducing the build receipt requires `--fleet-rev 6c4aba34…`. Recorded as a limit in the section's prose; no fix proposed (the default is the counter's frozen behaviour).

**F5 — limit, not a defect: `m-text-flip` is not leg-isolated.** Its receipt fails `bind=0` and `code=0` because the replay refuses to start with a flipped rpc library; the harness's expectation is satisfied because a `detail: code b1:` line carries the named leg (`run-battery.py:140-142` matches `"code "` in `detail:` lines). A reader should not read the "code leg" attribution as a single-fault isolation.

No defect found in either frozen counter's own predicate statements: both sha256s match the freeze, their exit maps match their returns, and the C2 base control is genuinely red at the base tree with the dropped citation named.

## 6. Scope and limits of this seat

- I ran no counter against the base or build tip (the receipts already exist; rerunning would only decorate). The one counter invocation here is the C2 addition re-check against a fixture commit — new work on my own deliverable, not a re-run of the round-55 measurement.
- I did not run the C1 counter or the battery: both download the ~30 MB b11909 archive, start loopback servers, and would add no evidence beyond the committed receipts.
- Exit codes for counters/controls are the frozen declarations plus source returns; receipts carry none (F3).
- `corpus/lessons/round-55.md` Gate requires a census end receipt (exit 0) that does not exist yet: `.ufo/waves/round-55/census/` holds only `start.out` (exit 1, `E11 S510 missing used-by corpus/lessons/round-54.md`). The lesson row therefore records the before-state only; the census end is another seat's / the L1's item. I deliberately did not cite that receipt path in the section (an unresolved SKILL.md citation would turn the C2 lane leg red).
- SCORECARD.md carries no round-55 text yet (`grep -n 'round-55' SCORECARD.md` → no match); scoring is out of this seat.
- No tool was installed or upgraded (no pacman, no uv, no npx, no `~/.local/bin` change); nothing in `~/.local/bin` or any PATH directory was created or modified.
- Scratch `/fast/scratch/hyaku/kama-r55/w1/Sc5Skill` was removed; the only llama-server processes left on the host belong to peer `J5EnvNames` (`/fast/scratch/hyaku/kama-r55/w1/J5EnvNames/...`), none to me.
- Read-only git only on the lane (`show`, `log`, `status`, `rev-parse`, `clone --shared` into my scratch); fixture commits only in `$S/lane` with `-c user.name=fx -c user.email=fx@invalid` after `git -C $S/lane rev-parse --show-toplevel` printed `$S/lane`.

## 7. Paths written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sc5Skill.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sc5Skill/registry-round55.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sc5Skill/proposed-skill-append.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sc5Skill/proposed-harness-summary.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sc5Skill/README.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sc5Skill/receipts/` (preregistration.json, base.c1.out, base.c2.out, c1-build.out, c2-build.out, control.out, m-ldpreload.out, m-text-flip.out, m-member-flip.out, m-ldaudit-foreign.out, m-ldaudit-writable.out, m-extra-in-tree.out, c2-addition-check.out)
