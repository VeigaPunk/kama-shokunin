VERDICT: confirm — The sole round-17 SOURCES transition exits 0; b8e485c→ccc4bb3 exits 1 naming S041 anchor and teaches.

# Scope and axes

Reviewer: `KamaR17.AppendOnlyPairwise`. This is scoped advice to L1, not admission of round 17 or a judgment of C1/C2.

Attacked KQ22 compliance at commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3`: completeness of the SOURCES-changing commit census, checking every round transition rather than hiding intermediate edits in a base-to-tip comparison, and failure on the specified historical S041 control.

Review axes: history completeness, reproducible append-only results, fail-capable negative-control detection, and lane isolation. Independent history, blob-identity, positive-control and negative-control queries were run concurrently in an isolated clone.

# Severity-ordered findings

## No actionable current-round defect in this slice

At the pinned revision, `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md:123` requires checks “over every consecutive commit pair touching `corpus/SOURCES.md` in the round”.

The exhaustive path history has exactly one in-round SOURCES-changing commit:

| Order | Commit | Parent | Subject |
|---|---|---|---|
| 1 | `54a29268e2083caa2b1e0d54ee1e7d90961302f3` | `cff9e62f05aa7cfb9059444f62eb787100719713` | round-17: graded check.py fields with fault controls and mutant grid; live receipt v2 with fail-capable checks and controls; SOURCES append-only guard; S042-S046, KQ20-KQ22; jj lane hygiene |

Evidence: both the original path-limited log and the subsequent `--full-history --reverse` log returned that single record. `git rev-list --count cff9e62..54a2926` returned `1` for the entire commit range, not merely the path history. Including `cff9e62` in the path-history query added no SOURCES-changing record; the path-limited show of that baseline was empty.

Consequently there is one transition to grade, with the baseline retained as the left endpoint:

| From | To | Guard exit | Result |
|---|---|---:|---|
| `cff9e62f05aa7cfb9059444f62eb787100719713` | `54a29268e2083caa2b1e0d54ee1e7d90961302f3` | **0** | S042–S046 added; no append-only violations |

This is also the direct parent→commit edge. It is not a shortcut across multiple commits, nor an empty/vacuous sweep omitting the new commit. No intermediate commit exists in the assigned range in which an addition could have been edited or reverted.

Observed blob identities:

- SOURCES at `cff9e62`: `6721ec1006f86f48b48845c3fd05ab3c3e52ccaf`.
- SOURCES at `54a29268^`: `6721ec1006f86f48b48845c3fd05ab3c3e52ccaf`.
- SOURCES at `54a29268`: `d2c4fa40868321797be6dc407bc6de7cd4ce3e08`.
- Last pre-round SOURCES-changing commit: `ccc4bb31267f061c1d3cc4099eb9fb46ed48d004`.

The scoped Git diff reports SOURCES as 20 insertions and zero deletions. The newly appended registry rows are at `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:54-58` in the pinned revision. The guard's plain output was:

```text
added S042 (allowed)
added S043 (allowed)
added S044 (allowed)
added S045 (allowed)
added S046 (allowed)
no append-only violations
EXIT:0
```

Its JSON run independently reported `violations: []`, exactly those five added IDs, and `ok: true`, exit **0**.

## Informational — specified historical defect is detected, not silently accepted

`b8e485cc6b201c8e4604a20808e58babbfe08e34`→`ccc4bb31267f061c1d3cc4099eb9fb46ed48d004` exited **1**. Selected output (the intervening old/new values are omitted here):

```text
VIOLATION S041: cell `anchor` changed in place
VIOLATION S041: cell `teaches` changed in place
1 append-only violation(s)
EXIT:1
```

The JSON run also exited **1**, reporting exactly one affected row (`S041`), kind `cell-changed`, with two detail cells: `anchor` and `teaches`; `added` was empty and `ok` false. The summary is one violating row, not one changed cell.

Evidence location: `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:53` at `ccc4bb3` and the pinned round commit. The historical anchor changed from the 13:49:38 capture on port 32845 to the 14:06:27 capture on port 37527 with a tool digest; the teaches cell gained the loading-envelope observation. This is the expected, pre-round control, not a newly discovered round-17 rewrite.

The result follows the executed implementation, not a prose-only assertion: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/sources-append-only.py:164-190` compares immutable cells for retained IDs, and `:245-257` prints the changed cell names and returns 1 when violations exist.

Supplemental fixture-only check: `--selftest` exited **0**, printing `14/14 selftest cases passed`. This is not counted as corpus-history evidence.

# Exact executed commands and exits

All guard executions used the checked-out round-commit implementation in `/tmp/AppendOnlyPairwise-clone`, with `PYTHONDONTWRITEBYTECODE=1` and explicit `--repo /tmp/AppendOnlyPairwise-clone`. The explicit repository argument matters because the tool's default otherwise names the live lane. No lane gate or lane Python tool was executed in the lane directory.

For composite commands, the wrapper exit is distinguished from printed inner gate exits. Where a pipeline did not capture constituent exits, only its final/composite exit is reported; those unprinted individual exits are not asserted.

## Clone and history discovery

1. Exit **0** (all three `&&`-linked commands succeeded):

```sh
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/AppendOnlyPairwise-clone && git -C /tmp/AppendOnlyPairwise-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3 && git -C /tmp/AppendOnlyPairwise-clone log --oneline -1
```

2. Exit **0**; returned the single listed SOURCES-changing commit:

```sh
git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --format='%H %s' cff9e62..54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- corpus/SOURCES.md
```

3. Composite exit **0**; returned the same path history, no baseline path change, two existing commit objects and their subjects, and total range count 1:

```sh
cd /tmp/AppendOnlyPairwise-clone && echo '== range incl cff9e62 ==' && git log --format='%H %s' cff9e62^..54a2926 -- corpus/SOURCES.md; echo '== cff9e62 touches? ==' && git show --stat --format='%H %s' cff9e62 -- corpus/SOURCES.md | head -20; echo '== object types ==' && git cat-file -t b8e485c 2>&1; git cat-file -t ccc4bb3 2>&1; echo '== their subjects ==' && git log -1 --format='%H %s' b8e485c 2>&1; git log -1 --format='%H %s' ccc4bb3 2>&1; echo '== full range commit count ==' && git rev-list --count cff9e62..54a2926
```

4. Exit **0**; full-history enumeration independently returned the same single commit and its baseline parent:

```sh
git -C /tmp/AppendOnlyPairwise-clone log --full-history --reverse --format='%H %P %s' cff9e62..54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- corpus/SOURCES.md
```

5. Composite exit **0**; printed the parent, blob IDs and last pre-round SOURCES-changing commit recorded above:

```sh
cd /tmp/AppendOnlyPairwise-clone && echo parent=$(git rev-parse 54a29268e2083caa2b1e0d54ee1e7d90961302f3^) && echo blob_cff9e62=$(git rev-parse cff9e62:corpus/SOURCES.md) && echo blob_parent=$(git rev-parse 54a29268e2083caa2b1e0d54ee1e7d90961302f3^:corpus/SOURCES.md) && echo blob_tip=$(git rev-parse 54a29268e2083caa2b1e0d54ee1e7d90961302f3:corpus/SOURCES.md) && echo last_pre_round=$(git log --format='%H %s' -1 cff9e62 -- corpus/SOURCES.md)
```

6. Exit **0**; scoped diff showed 20 SOURCES insertions and 14 QUALITY insertions, no deletions:

```sh
git -C /tmp/AppendOnlyPairwise-clone diff --no-ext-diff cff9e62 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- corpus/SOURCES.md corpus/QUALITY.md
```

## Assigned transition and historical negative control

7. Guard exit **0**, wrapper exit **0**:

```sh
cd /tmp/AppendOnlyPairwise-clone && PYTHONDONTWRITEBYTECODE=1 python3 tools/sources-append-only.py --from cff9e62 --to 54a29268e2083caa2b1e0d54ee1e7d90961302f3 --repo /tmp/AppendOnlyPairwise-clone; echo EXIT:$?
```

8. Guard exit **1**, wrapper exit **0** because the final command echoes the captured grade:

```sh
cd /tmp/AppendOnlyPairwise-clone && PYTHONDONTWRITEBYTECODE=1 python3 tools/sources-append-only.py --from b8e485c --to ccc4bb3 --repo /tmp/AppendOnlyPairwise-clone; echo EXIT:$?
```

9. Selftest exit **0**; round-pair JSON exit **0**; negative-control JSON exit **1**; overall wrapper exit **0**:

```sh
cd /tmp/AppendOnlyPairwise-clone && PYTHONDONTWRITEBYTECODE=1 python3 tools/sources-append-only.py --selftest; echo SELFTEST_EXIT:$?; echo '=== JSON round pair ==='; PYTHONDONTWRITEBYTECODE=1 python3 tools/sources-append-only.py --from cff9e62 --to 54a29268e2083caa2b1e0d54ee1e7d90961302f3 --repo /tmp/AppendOnlyPairwise-clone --json; echo EXIT:$?; echo '=== JSON negative control ==='; PYTHONDONTWRITEBYTECODE=1 python3 tools/sources-append-only.py --from b8e485c --to ccc4bb3 --repo /tmp/AppendOnlyPairwise-clone --json; echo EXIT:$?
```

## Other exploratory commands

10. Exit **0**; printed 433 lines:

```sh
wc -l /tmp/AppendOnlyPairwise-clone/tools/sources-append-only.py
```

11. Composite exit **0**; literal discovery only, not semantic caller evidence:

```sh
cd /tmp/AppendOnlyPairwise-clone && grep -n 'KQ22' corpus/QUALITY.md | head -5; echo '---'; grep -n 'S041' corpus/SOURCES.md | head -5; echo '---'; grep -n 'anchor\|teaches' corpus/SOURCES.md | head -10
```

12. Composite exit **0**; literal discovery only, not the evidence for commit completeness or the guard results:

```sh
cd /tmp/AppendOnlyPairwise-clone && grep -n 'KQ22\|append-only' corpus/lessons/round-17.md | head -10; echo '---'; grep -rn 'sources-append-only' tools/ tests/ .ufo/waves/round-17/ --include='*.md' --include='*.py' 2>/dev/null | grep -v 'sources-append-only.py:' | head -10
```

## Cleanup

13. Exit **0**, observed `SCRATCH_REMOVED exit=0`:

```sh
rm -rf -- /tmp/AppendOnlyPairwise-clone && test ! -e /tmp/AppendOnlyPairwise-clone && printf '%s\n' 'SCRATCH_REMOVED exit=0'
```

# Residual risk, verification gaps, and method limits

- The result is limited to the pinned round range and the explicitly requested historical control. It is not a full-history append-only certification, a general adversarial proof of the parser, or proof about uncommitted or later work.
- This round contains only one commit. The parent-edge check is exhaustive here; the run does not demonstrate traversal of a future multi-commit round.
- Semantic tooling was unavailable: reading `xd://lsp` returned `No such tool: xd://lsp` and listed mounted devices without an LSP device. Therefore status/references/definition/diagnostics could not be obtained. Literal search results are not represented as semantic proof.
- Method deviations are disclosed: the initial shell literal lookups preceded LSP discovery and used shell grep/head rather than the specialized devices. The recursive exploratory lookup in command 12 omitted the mandated exclusion flags; its explicit roots were confined to the scratch clone's tools, tests and round-17 wave directory. It is not used to establish acceptance. Subsequent exact criterion and implementation citations were read through the file-read device.
- C1/C2 grading, live-server behavior, runtime routing/saturation, and resume preflight mutation guarantees were outside this assigned slice and were not exercised. No server was started or contacted; no listener or background process was created by this review.
- No code, corpus, state, fleet configuration, VCS index/ref, or sibling-lane edits were made. The sole lane write is this requested report. Scratch was removed before the report was written. No subagents were dispatched.
- Installs/updates: **none**. No pacman transaction or service restart was performed.
