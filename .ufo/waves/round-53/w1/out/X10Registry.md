# X10Registry — round-53 SKILL.md instrument registry draft (lane kama)

Verdict: the two round-53 counter rows register both instruments and make `tools/gate-registry-check.py` clean (`registered 52 unregistered 0 defective 0`, exit 0 at fixture HEAD) and reduce `tools/round43-registry-audit.py` from 4 mismatches to 1, the remaining one a pre-existing `SCORECARD.md:18` calibration-count defect that predates this wave; the draft adds 6 resolving citations and no new C2 miss (`cited=688 unresolved=14 disclosed=14 met=True`).

Base `4229ea1b9a789148dded1f159c20967d9a01373f`; build `c22602bd8d83ab26349d1087e916ca537ee4f9d1`; freeze `d01b2b6d48a54ffe0e475000737d3e302c62e28e`. Scratch clone: `git clone --shared <lane> $S/lane`, detached at the build, SKILL.md section appended, fixture commit `2f5ee1dc3b08cc1be8ada7ab86e52aa76e8e5788` (one parent, the build). No lane file was touched; no tool installed.

## Draft

`skill-round53-registry-draft.md` (5,853 bytes) is a new `## Round-53 instrument registry (memory-read code identity, cited-path corrections)` section in the round-52 shape: a one-paragraph header, a five-column table with one row per counter, and a `### Reading the code identity and the citation ledger (round 53)` subsection. Its rows carry, per the round-52 pattern:

- C1 `tools/round53-replay-code-audit.py`: entry `--repo <clone> --tip <full-commit> [--scratch <dir>] [--out <receipt>]`; exit map `bind=0|1 sealed=0|1 code=0|1 teardown=0|1 newrow=0|1 bound=N/3 sealedruns=N/3 coderuns=N/3`; the `code` leg described (every executable mapping read out of `/proc/<pid>/mem` and compared with the counter's own archive member at the mapping's file offset, zero past the end; or a root-owned, same-inode, unwritable host file with dev not compared; the four required `libllama-server-impl.so` / `libggml-base.so*` / `libggml.so*` / `libggml-cpu-*.so` names; receipt `code_mappings` and replay `own_code.verified` cross-checks; `newrow` on `corpus/SOURCES.md` S506); pins the three round-48 v5 receipts, server/archive/model sha256 (`35ac50fb…7ff0`, `bf94332a…695b`, `270cba1b…256d`), the base control and build figures, and counter sha256 `1a7a144204ba8b7e`; write scope `--scratch`/`--out`, read-only `--repo`, loopback server children, network to github.com and huggingface.co.
- C2 `tools/round53-cited-path-check.py`: entry adds `[--fleet <fleet-repo>] [--fleet-rev <rev>]`; exit map `fleet=<rev>` then `fixture=0|1 lane=0|1 scenarios=N/8 cited=N unresolved=N disclosed=N undisclosed=N bad=N stale=N dropped=N met=True`; the parser, the eight fixture scenarios and the ledger classes are described; pins 15 ledger rows (14 disclose the build's 14 unresolved citations, one `fixed` row), base `cited=679 unresolved=16 disclosed=0 met=False`, build `cited=682 unresolved=14 disclosed=14 met=True`, counter sha256 `1afb8b9d32fd0706`; write scope `--scratch`/`--out`, read-only `--repo`/`--fleet`, 5 raw.githubusercontent.com URLs.

Both entry cells name only flags the counters declare (`add_argument` at `tools/round53-replay-code-audit.py:710-713`, `tools/round53-cited-path-check.py:462-467`), which the audit's `flags` fact requires.

## Evidence (all commands from the fleet root; `S=/fast/scratch/hyaku/kama-r53/X10Registry`)

1. Fixture: `git -C $S/lane rev-parse --show-toplevel` → `$S/lane`; `git -C $S/lane rev-parse HEAD` → `2f5ee1dc3b08cc1be8ada7ab86e52aa76e8e5788`; `git -C $S/lane diff --stat c22602bd HEAD` → `SKILL.md | 14 ++++++++++++++` (`fixture-skill-diff.patch`, 22 lines: 3 context, 1 blank + 13 section lines inserted after the round-52 subsection). `tail -c 5853 $S/lane/SKILL.md | sha256sum` equals `sha256sum skill-round53-registry-draft.md` → `76b6d8fa…d8ad6c` (append is byte-identical to the draft: the draft was revised twice before the final fixture — the receipts pointer in the header and the `fleet=<rev>` line in the C2 exit map — and the fixture was rebuilt and re-measured each time).

2. Gate on the fixture:

   `python3 tools/gate-registry-check.py --repo $S/lane --rev HEAD` → `registered 52 unregistered 0 defective 0`, exit 0 (`gate-fixture.out`).

   Baseline in the same clone without the draft, `--rev c22602bd` → `unregistered tools/round53-cited-path-check.py`, `unregistered tools/round53-replay-code-audit.py`, `registered 50 unregistered 2 defective 0`, exit 1 (`gate-baseline.out`). The draft closes exactly those two misses and adds no `missing-path`/`thin-row`/`empty-*` defect.

3. Audit on the fixture:

   `python3 tools/round43-registry-audit.py --repo $S/lane --tip HEAD` → `unreg=0 defect=0 flags=0 pins=0 selftest=0 dc=0 spot=1 hidden=0 pop=52 registered=52 mismatches=1 met=False`, exit 1; the single `detail:` is `spot: calibration row states 38, tree holds 39` (`r43-fixture.out`).

   Baseline at the build (`--tip c22602bd`) → `unreg=2 … selftest=1 … spot=1 … mismatches=4 met=False`, exit 1 (`r43-baseline.out`). The draft fixes `unreg` (2→0) and `selftest` (1→0): with the two counters unregistered, the gate's lane-tip arm fails (`detail: selftest: documented 'GATE_SELFTEST pass=6 fail=0', run printed 'GATE_SELFTEST pass=5 fail=1' exit 1`); with the draft, the audit's own throwaway clone prints the documented line.

4. Gate selftest directly, cwd `$S/lane`, `master` forced to the fixture tip: six PASS lines including `PASS lane-tip 2f5ee1dc3b08: exit=0 line='registered 52 unregistered 0 defective 0'`, then `GATE_SELFTEST pass=6 fail=0` (`gate-selftest-fixture.out`). Note the arm resolves branch `master` (`tools/gate-registry-check.py:365-372`), so it is only meaningful once the tip carries the section — the L1 should re-run it after integration.

5. C2 counter at the fixture (the section adds citations to SKILL.md, so this checks the draft itself):

   `python3 tools/round53-cited-path-check.py --repo $S/lane --tip HEAD --scratch $S` → `fixture=1 lane=1 scenarios=8/8 cited=688 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True`, exit 0 (`c2-fixture.out`; `fleet=ccc6ce8931980b994e8ce8c99ba7799eed4050b0` at this run, versus `ee9f7341…` in the L1 build receipt — the fleet tip moves). The draft raises `cited` from the build's 682 to 688: six new distinct citation tokens, all resolving — measured by importing the counter's own `citations()` on `c22602bd:SKILL.md` and on the fixture `SKILL.md` (`|tip|−|base| = 206−200`): `.ufo/waves/round-53/controls/`, `SHONEN.md`, `SKILL.md`, `registry/cited-path-corrections.tsv`, `scripts/` and `templates/` (the last two resolve in the fleet tree); `unresolved=14`, `disclosed=14` unchanged. The pinned `cited=682` in the row is the build's value and remains attributable to `c22602bd`.

No C1 run by this seat: the row's measured values are the L1's build receipt (`code` 3/3, 8 archive files over 8 executable ranges byte-equal, 13 root-owned host files) and the frozen base control (`bind=1 sealed=1 code=0 teardown=1 newrow=0 met=False`); this seat did not reproduce the 25 s network measurement, and no receipt here claims otherwise.

## Defect found (pre-existing at the build; being fixed in the live working tree)

At the build, `SCORECARD.md:18` (`| calibration | **7** | …`) states `→ `38` (outside closures on record)` and `latest outside closure `corpus/lessons/round-51-verifier-spotcheck.md``, while the tree has held 39 `corpus/lessons/*verifier-spotcheck.md` blobs since the base: the base commit `4229ea1b` adds `corpus/lessons/round-52-verifier-spotcheck.md` (single-file commit, `git show --stat 4229ea1b` → `1 file changed, 153 insertions(+)`) without updating the row. That is why the fixture (build bytes + this section) reports `spot=1 met=False`: the fixture's SCORECARD is the build's. Command: the audit runs above; independently `git ls-tree -r --name-only c22602bd corpus/lessons | grep -c verifier-spotcheck` → `39` (same at `4229ea1b`), and `git show 4229ea1b:SCORECARD.md | sed -n 18p` → the same `38`. Only the number is graded (`tools/round43-registry-audit.py:202-211`).

The live lane working tree already carries the fix, uncommitted during this seat's run (`git diff HEAD -- SCORECARD.md`): count `39`, latest closure `corpus/lessons/round-52-verifier-spotcheck.md` (admitted; re-anchored round 53), and the depth row re-pinned to `SKILL.md` sha256 `cdc061ba…217e` (1576 lines, `grep -c '^## '` → 41). So at the integrated tip the audit's spot leg should clear; the proposal kept for the record is `spot-fix-proposal.diff`, generated against the build's `SCORECARD.md` (`38`→`39` and the re-anchor), which matches what the live tree did; on a fresh copy of the build file `patch -p1 --dry-run < spot-fix-proposal.diff` prints `checking file SCORECARD.md`, exit 0.

## Limit in the two registry instruments (observed, not introduced here)

Both registry tools split a table row on every `|`, so the escaped pipes the registry rows put in the exit map (`bind=0\|1 …`) shift every later cell. `tools/gate-registry-check.py:144` (`cells()`), `:200` (row loop) and `:210` (`for c in (row[1], row[3], row[4])`) then check the entry cell (index 1) and, as index 3/4, fragments of the exit map — the Self-test and Write-scope cells are never path-checked in any row of the round-51/52/53 shape. `tools/round43-registry-audit.py:143,164,165` has the same split, so its `flags`/`pins` facts read fragments as cells 2/3 for such rows; a round-53 row added to `NEWSET` could never satisfy the pins fact (its sha256 sits in cell 5, not 3).

Probe (fixture repo `$S/probe`, `tools/round99-probe.py`, two rows — one plain exit map, one with `\|`, both citing `nowhere/receipt.json` and `missing/dir/file.out`): `python3 tools/gate-registry-check.py --repo $S/probe --rev HEAD` → `defective tools/round99-probe.py: missing-path:missing/dir/file.out`, `defective …: missing-path:nowhere/receipt.json`, `registered 1 unregistered 0 defective 2` — the first row's two bad paths are reported, the second row's two are not. Proposed hardening for `cells()` (both tools): strip the outer pipes, then split with `re.split(r"(?<!\\)\|", body)` and unescape `\|` in each cell, so every cell index is stable. This does not change any verdict here: this seat's rows cite only paths that exist at the fixture tip, and both tools already return `flags=0 pins=0`.

## Risks / hand-off notes

- Integration should land the section verbatim (or re-measured) after `### Reading the sealed server and the restored lines (round 52)`; the file is 1,559 lines at the build and the section was appended at the end in the fixture. If the L1 rewords it, re-run steps 2, 3 and 5.
- After integration the C2 `cited` count at the new tip is 688, not the build's 682; the row's pinned `682` names `c22602bd` explicitly, so a later re-measure should keep the build figure or restate it.
- `spot=1` is the build's `SCORECARD.md:18` count, and the live working tree already fixes it (count `39`, round-52 closure) together with the depth row's `SKILL.md` pin; that is the only reason the fixture audit is not clean with this draft. If the section is appended on top of the live 1,576-line `SKILL.md`, the depth row's pin must be re-measured again (the section adds 14 lines and one `##` heading, so 1,590 lines and 42 headings); the fixture values on the build are `SKILL.md` sha256 `8120a5778a6bc9f17f6f31db06ea7993ca7b62baa9564e6aed40c263b7e16be8`, 1,573 lines, `grep -c '^## '` → 41.
- This seat started no `llama-server` and ran no counter's C1 legs; the pre-existing `llama-server` processes in `pgrep -af llama-server` belong to sibling seats' scratch trees.
- No tool install or upgrade was needed; pacman was not invoked.

## Files written (absolute)

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X10Registry.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X10Registry/skill-round53-registry-draft.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X10Registry/fixture-skill-diff.patch
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X10Registry/gate-fixture.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X10Registry/gate-baseline.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X10Registry/gate-selftest-fixture.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X10Registry/r43-fixture.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X10Registry/r43-baseline.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X10Registry/c2-fixture.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X10Registry/spot-fix-proposal.diff
