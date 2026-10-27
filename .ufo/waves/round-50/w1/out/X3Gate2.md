# X3Gate2 — gate registry prerequisites for the two round-50 counters

**Verdict: both counters need exactly one five-column registry row each, in a new `## Round-50 instrument registry` section; with those two rows applied on a scratch copy of the lane-master tree the gate prints `registered 46 unregistered 0 defective 0` and exits 0, and without them it prints `registered 44 unregistered 2 defective 0` and exits 1. No defect found in either counter. Two gate-shape hazards are documented below and both are cheap to trip at integration.**

Build measured: `97c864bead3ee4a2f629574e77263d33834ec98a`; lane `master` at measurement time `3b79eaddf38246c637cc7ba1a94ab363422876b6` (SKILL.md unchanged between the two: `git diff 97c864be master -- SKILL.md` is empty). Base `26ecba64ad6fb571d09074b07202d1618a46ecd1`. All work on my own `git clone --shared` plus fixture repos under `/fast/scratch/hyaku/kama-r50/X3Gate2`; no lane file was written, no counter edited.

## 1. Baseline at the build (clone, read-only)

```
$ python3 kama-shokunin/tools/gate-registry-check.py --repo "$S/lane" --rev 97c864bead3ee4a2f629574e77263d33834ec98a
unregistered tools/round50-append-audit-v5-check.py
unregistered tools/round50-replay-bind-audit.py
registered 44 unregistered 2 defective 0
exit=1
```
(`gate-01-build-rev.out`.) Same result at lane `master` `3b79eadd`: `registered 44 unregistered 2 defective 0`, exit 1 — the population is 46 counters, 44 registered, exactly these two missing.

Independent corroboration: the build battery's own receipt `.ufo/waves/round-50/measured/gate-build.out` (copied to `build-battery-gate-build.out`) records
`unregistered tools/round50-append-audit-v5-check.py` / `unregistered tools/round50-replay-bind-audit.py` / `registered 44 unregistered 2 defective 0` / `exit=1` — byte-identical to my clone run, so the clone is not a mangled view.

## 2. What the gate requires of a row (read from the tool, not guessed)

`tools/gate-registry-check.py` (sha256 `20bdb9f0…566e89f`):

- Population: `COUNTER_RE` (`:66-68`) — `.ufo/waves/round-*/count-*.py` one level down, or `tools/round<N>-*.py`. Both round-50 counters are of the second form.
- A path is **registered** only if it occurs in a cell of a row of a table recognised by `registry_rows` (`:148-175`). Prose does not register.
- Recognised table (`:164-170`): a contiguous block of `|` lines, at least two lines, whose first row splits into **exactly five cells** with `hdr[0] == "name"`, `hdr[1]` containing `kind` or `entry`, `hdr[2]` containing `exit`, `hdr[3]` containing `self-test`/`selftest`, `hdr[4]` containing `write`, and whose separator row's cells use only `:`, `-`, space. So the column set is exactly `| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |`, and the rows must sit directly under that header — a blank line ends the block.
  - Consequence: the older ten/twelve-cell tables in this file (`Verdict map`, `Pinned values`, `Owner`, e.g. lines 396, 430, 470, 495, 533, 570) are **not** registry rows for this gate; the round-43…49 sections use the five-column shape and so must round 50.
- Meaning, per matched row (`:196-216`):
  - `thin-row`: fewer than two non-empty cells (`:201`);
  - `empty-entry`: `row[1]` empty; `empty-exit-map`: `row[2]` empty (`:205-208`);
  - `missing-path:PATH`: every path-like token (at least one `/` plus one of `.md .py .sh .json … .gguf .so`) in `row[1]`, `row[3]`, `row[4]` must exist at the evaluated revision (`RE_PATH` `:69-72`, `path_exists` `:141-146`). The counter's own path is exempt; bare filenames, `<placeholders>` and `~`-paths are not paths. In `--rev` mode existence is `git cat-file -e <rev>:<path>`, i.e. the cited file must be **committed at that rev**; without `--rev` it is filesystem existence.
  - Matching is `any(path in c for c in r)` over **all** cells (`:196`), substring, so a row that cites another counter's path also matches that other counter.
- Exit: 0 iff `unregistered == 0 and defective == 0`; 1 otherwise; 2 could not evaluate (`:63-65`, `:236-237`).

Hazard A (pipe in a cell): `cells()` (`:144-145`) is `line.strip().strip("|").split("|")` — it does not honour `\|`. A raw pipe inside a cell (the round-47…49 rows use `0\|1` in exit maps) produces more than five cells, so `row[3]`/`row[4]` — the self-test and write-scope cells the path test reads — are no longer the real cells, and the empty-cell tests read a fragment. Those rows pass only because `row[1]` and `row[2]` stay non-empty after truncation. My drafted rows avoid `|` inside cells entirely (exits are described as `0` / `1` / `2` in words), so all five cells are real.

Hazard B (citation cross-attribution): because of the substring match at `:196`, citing `tools/round49-append-audit-v4-check.py` in the round-50 C2 row's self-test cell makes the round-49 counter *also* matched by that row — and any defect in that row is then reported against the round-49 counter too. Demonstrated in §5.

## 3. The two drafted rows (proposed, not applied)

Full proposed text: `proposed-round50-registry-section.md` (sha256 `0b1bb557…0da84e`), as a unified diff against the build SKILL.md: `proposed-round50-registry.diff` (sha256 `79df4dde…8e29254`). Insertion point: end of file, after the round-49 bullet at SKILL.md:1504 (`- Record-time bounds: …`), i.e. a new `## Round-50 instrument registry (replay bind audit, append-only v5 calibration)` section with an intro sentence and a `### Re-running round-50 evidence` subsection. SKILL.md is identical at `97c864be` and `3b79eadd`, so the diff applies unchanged at either rev.

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Round-50 C1 replay bind audit | measurement: `python3 tools/round50-replay-bind-audit.py --repo <clone> --tip <full-commit> [--scratch <dir>] [--out <receipt>]` (`--repo` and `--tip` required) | 0 met, prints `tip=<full>` then one summary line with `bind`, `teardown` and `newrow` each 0 or 1, `bound=N/3` and `met=True`, then one `detail:` line per leg; 1 not met, the same summary with `met=False` and a `detail:` line naming each failed leg; 2 could not evaluate, `could-not-evaluate: …` when the tip does not resolve or the tree cannot be archived (a later git or `/proc` failure is an uncaught traceback, not exit 2); with `--out` the same text is also written to the receipt | measured at `97c864be`: exit 0 in 16.5 s with `bind=1 teardown=1 newrow=1 bound=3/3 met=True`; three frozen v5 receipts `.ufo/waves/round-48/c2/live/receipt-1.json` … `-3.json`, server sha256 `35ac50fb…d8d7ff0`, model sha256 `270cba1b…6d3bd256d` from the pinned huggingface revision, base `26ecba64`; no `--selftest` option exists; legs are exe digest, listener ownership, nonce round-trip against the counter's own vocabulary, descent from the replay, environment canaries, mapped file dev/inode/sha256 joined to the rerun receipt's `child_pid`, and SIGKILL-of-invoker teardown within 30 s; needs https to github.com and huggingface.co, Linux `/proc`, and a pids-capable host; starts and stops one `llama-server` per receipt plus one for the teardown leg, loopback only | read-only on `--repo`; a temporary tree, downloads, server logs and receipts under `--scratch` (default `TMPDIR`), removed on exit |
| Round-50 C2 append-audit v5 check | measurement: `python3 tools/round50-append-audit-v5-check.py --repo <clone> --tip <full-commit> [--scratch <dir>] [--out <receipt>]` (`--repo` and `--tip` required) | 0 met, prints `tip=<full>` then one summary line with `fixture` and `lane` each 0 or 1, `scenarios=N/12` and `met=True`, then one `detail:` line per scenario and per lane leg; 1 not met, the same summary with `met=False`; 2 could not evaluate, `could-not-evaluate: …` on stdout for a git failure or a fixture whose `git rev-parse --show-toplevel` is not its own directory; with `--out` the same text is also written to the receipt | measured at `97c864be`: exit 0 in 6.5 s with `fixture=1 lane=1 scenarios=12/12 met=True`, lane `events 5 bad_declarations 0 ungraded_lines 89` and `event dd9f5dc6c0e6 ungraded 17 <= v5 natively exempt 23`; the 12 scenarios are launder, native-head, dated-loss, substring, word-token, negated, wildcard-self, wildcard-named, order-a, order-b, fence and crlf-launder, each requiring `graded + ungraded == deleted`; the tool under test is `tools/append-only-audit.py` at the tip (v5 definitions: birth-based origin, CommonMark fence-aware sections, CR-stripped keys, deleted-line accounting) and the round-49 predecessor whose eight scenarios must stay as written is `tools/round49-append-audit-v4-check.py` | read-only on `--repo`; the extracted tip tree and the twelve fixture repositories under `--scratch` (default `TMPDIR`), removed on exit |

Every measured value in those cells is mine, run at `97c864be` on the clone (`c1-replay-bind-audit.out`, `c2-append-audit-v5-check.out`):

```
$ python3 tools/round50-replay-bind-audit.py --repo "$S/lane" --tip 97c864be… --scratch "$S" --out "$S/c1.out"
tip=97c864bead3ee4a2f629574e77263d33834ec98a
bind=1 teardown=1 newrow=1 bound=3/3 met=True
detail: counter vocabulary: 512 tokens from its own download
detail: bind b1: pid 2555718 port 36273 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1753876713 recorded, nonce 'kama witness c97a5ed35f5f65b3' round-tripped
detail: bind b2: pid 2570175 port 38075 … nonce 'kama witness 2a61f1177b076988' round-tripped
detail: bind b3: pid 2585970 port 36805 … nonce 'kama witness 792b1fb968045ccb' round-tripped
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 3 rows new since base; 1 name proc_pid_maps(5): ['| S496 |']
exit=0     (real 16.5 s — the L1 dry run's 46 s is not reproducible as a fixed cost)
```

```
$ python3 tools/round50-append-audit-v5-check.py --repo "$S/lane" --tip 97c864be… --scratch "$S" --out "$S/c2.out"
tip=97c864bead3ee4a2f629574e77263d33834ec98a
fixture=1 lane=1 scenarios=12/12 met=True
detail: scenario launder … order-a … crlf-launder: ok (one line each)
detail: lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 89
detail: lane: event dd9f5dc6c0e6 SCORECARD.md ungraded 17 <= v5 natively exempt 23
detail: lane: event 0718b6abbda6 SCORECARD.md ungraded 72 <= v5 natively exempt 72
exit=0     (real 6.5 s)
```

Both were run inside my scratch with `--scratch "$S"`; both remove their own trees. `pgrep -af llama-server` afterwards shows only other seats' processes (J4Decoy, X11ModelSwap); nothing under `X3Gate2` survived, and no `llama-server` of mine was left on a port.

## 4. Demonstration on a scratch copy with the rows applied

Fixture `$S/fix.dN4Ape` = `git archive 97c864be | tar -x` + `git init` (toplevel asserted), branch renamed `master`; commit `c9799b52` is the bare build tree, commit `7b9f83d9` adds the rows. Second fixture `$S/tip.CVaTLH` = the same for lane `master` `3b79eadd` (commit `bcd6fc8a`), rows commit `fc6965f0`, whose SKILL.md is byte-identical to the first fixture's (`diff` empty).

```
$ python3 tools/gate-registry-check.py --repo "$D" --rev c9799b52        # fixture, before the rows
unregistered tools/round50-append-audit-v5-check.py
unregistered tools/round50-replay-bind-audit.py
registered 44 unregistered 2 defective 0
exit=1

$ python3 tools/gate-registry-check.py --repo "$D"                        # fixture working tree, rows applied
registered 46 unregistered 0 defective 0
exit=0

$ python3 tools/gate-registry-check.py --repo "$D" --rev HEAD             # fixture at the rows commit 7b9f83d9
registered 46 unregistered 0 defective 0
exit=0

$ python3 tools/gate-registry-check.py --repo "$E" --rev bcd6fc8a         # lane master tree, before the rows
unregistered tools/round50-append-audit-v5-check.py
unregistered tools/round50-replay-bind-audit.py
registered 44 unregistered 2 defective 0
exit=1

$ python3 tools/gate-registry-check.py --repo "$E" --rev HEAD             # lane master tree + rows (fc6965f0)
registered 46 unregistered 0 defective 0
exit=0
```
(`gate-02…gate-04`, `gate-09`, `gate-07`.)

The gate's own fail-capable matrix still passes on the trees that carry the rows, including arm 6, which evaluates the tree it lives in at its `master`:

```
$ python3 "$E/tools/gate-registry-check.py" --selftest
PASS valid-row … PASS thin-row … PASS empty-exit-map … PASS missing-path … PASS prose-only …
PASS lane-tip fc6965f0f251: exit=0 line='registered 46 unregistered 0 defective 0'
GATE_SELFTEST pass=6 fail=0
exit=0
```
(`gate-08`; the `97c864` fixture gives the same 6/6 in `gate-05`.)

The proposed diff applies to the lane-master SKILL.md without fuzz and only appends:

```
$ git -C "$S/lane" show master:SKILL.md > SKILL.md && git apply --check proposed-round50-registry.diff && git apply proposed-round50-registry.diff
APPLY_CHECK_OK_AT_MASTER
$ sha256sum SKILL.md
accb3c26b65456fa320838a050b55989b04b15ddb8b0104b4c78ee23fbe09514  SKILL.md
# diff of lines 1-1504 against master:SKILL.md is empty (ONLY_APPENDED)
```
so after integration the SKILL.md blob for the master tree `3b79eadd` should hash to `accb3c26…fbe09514`, and that tree then evaluates `registered 46 unregistered 0 defective 0`.

## 5. Negative control that proves the rows are actually being read

Fixture `$S/neg.j52QSO` = the rows fixture with one extra citation added to the C2 row's self-test cell — `routed by \`corpus/lessons/round-50.md\``, the file the integration scribe lands later:

```
$ python3 tools/gate-registry-check.py --repo "$D2" --rev HEAD
defective tools/round49-append-audit-v4-check.py: missing-path:corpus/lessons/round-50.md
defective tools/round50-append-audit-v5-check.py: missing-path:corpus/lessons/round-50.md
registered 46 unregistered 0 defective 2
exit=1
```
(`gate-06`.) This is Hazard B in the open: the round-49 counter acquires the row's defect because its path is cited inside it. So the rows are parsed and path-checked (not silently skipped), and one careless citation flips the gate from 0 to 1 at integration.

## 6. Integration notes for the L1

1. Apply `proposed-round50-registry.diff` (or append `proposed-round50-registry-section.md`) to SKILL.md at the integration commit; SKILL.md is unchanged from `97c864be` to `3b79eadd`, so it applies at either. Expected gate line afterwards: `registered 46 unregistered 0 defective 0`, exit 0 — and the build battery's own `gate` step (`python3 tools/gate-registry-check.py --rev "$TIP"`, `.ufo/waves/round-50/measured/measure.sh:22`) then passes.
2. Land `corpus/lessons/round-50.md` in the same commit or later, and **do not cite it inside the two rows** until it exists: the `--rev` mode checks `git cat-file -e <rev>:<path>` and a not-yet-landed citation turns both rows (and any counter they cite) defective — §5. The same applies to any `.ufo/waves/round-50/w1/out/…` seat artifact cited in a row: seats' out files land before integration, but anything cited must be committed at the evaluated rev.
3. Keep the rows in a five-column table with the exact header; a sixth `Owner`-style column (the shape of the round-12…19 tables) leaves both counters unregistered.
4. The two rows deliberately contain no raw `|` characters (Hazard A). If a later edit reintroduces `0\|1`-style exit maps, the path checks silently read the wrong cells.
5. The counters stay frozen; the row for C1 states its own limit (only tip-resolution/archive failures return 2; a later `/proc` or git failure surfaces as an uncaught traceback), which the docstring does not say explicitly.

## 7. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X3Gate2.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X3Gate2/proposed-round50-registry-section.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X3Gate2/proposed-round50-registry.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X3Gate2/gate-01-build-rev.out` … `gate-09-master-prerows.out` (nine gate invocations with exit codes)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X3Gate2/c1-replay-bind-audit.out`, `c2-append-audit-v5-check.out` (my counter receipts at the build)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X3Gate2/build-battery-gate-build.out` (the build battery's gate receipt, for cross-check)

No tool installed or upgraded (no pacman, no uv/npx, no binary install). Scratch `/fast/scratch/hyaku/kama-r50/X3Gate2` removed after the artifacts were copied out.
