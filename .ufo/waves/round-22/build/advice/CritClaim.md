# CritClaim — C1: calibration vs operability; distinct improvement or cleanup?

Verdict: **cleanup / contract hardening at the function level. It is not a distinct
calibration improvement at the receipt level**, unless the matrix shows a frozen
escape through the producer's real pre-launch path. As drafted in the lane, it also
loses some operator diagnostics, so it does not satisfy "improve any axis, harm none".
Sources are base `10271460`, lesson `corpus/lessons/round-21.md`, and the round-21
falsify advice. Nothing was run except read-only `git status`/`diff`/`ls`.

## Axes
- A1 calibration: does the claimed red-before exist where a consumer can see it?
- A2 operability: reason detail and how many faults one run reports.
- A3 consumer completeness: do "all consumers" refuse incomplete identity?
- A4 contract: lane checkout integrity.

## F1 (A1, decisive): the frozen producer already refuses all three fault families
At base, the producer never uses `install_tree` alone. It runs
`install_tree` → `install_links(server_real, tree)` → `if link_problems: raise SetupError('install-tree-unpinnable:'…)`
(`tools/kama-llamacpp-live.py:1414-1419`, base blob). At base each fault that
`install_tree` skips is caught again in `install_links` (lines 230-261):

| Injected fault (in `install_tree`) | What frozen `install_links(…, tree)` sees | Frozen receipt |
|---|---|---|
| `listdir` OSError | its own `listdir` fails, giving `listdir:<strerror>`; or, if transient, `tree={}`, so every regular file (at least `llama-server`) is `not-hashed` | refused, exit 2 |
| `lstat` OSError on a regular member | `<name>:<strerror>` if it is persistent; if transient, `<name>:not-hashed` | refused |
| `sha256_file` OSError | `<name>:unreadable` (mode check), otherwise `<name>:not-hashed` | refused |
| `lstat` fails on a symlink or directory | that entry type is not a member anyway, so identity is unchanged | n/a |

Round 21 already recorded this: "the producer refuses … unreadable members and regular
members `install_tree` failed to hash" (`round-21.md:134-136`). The selftest pins it at
`:1189-1190` (`libllama.so.0.7.1:not-hashed`). I found no source path where a partial,
comparable `install_tree_sha256` reaches a receipt at base. The only callers that
publish `install_tree` output alone are test harnesses: the frozen arm of
`install-links-grid.py:identity(with_links=False)` and the selftest.

This repeats round 21's C2ClaimCritic pattern ("0/N → N/N is detection by construction",
`round-21.md:151-153`): a red-before measured on `install_tree()` in isolation is red
because of how the test is built.

**Falsifiable rejection condition.** Let the Matrix's frozen arm evaluate every fault
cell through the composite `install_tree` → `install_links(server, tree)` → problems
gate, or through the producer CLI, and count escapes: no `SetupError`, plus a
non-null `install_tree_sha256` over a map missing a regular member, or a null digest
with exit ≠ 2.
- If frozen escapes = 0 on every cell, which source reading predicts, C1 MUST be worded
  as "function-level fail-closed contract; the producer receipt already refused at
  base". It moves no score.
- C1 counts as a distinct calibration move only if at least one frozen composite or CLI
  cell escapes and the current build refuses that same cell.

A matrix that only reports `install_tree()` red/green cannot tell these two cases apart.

**Minimum remedy.** Matrix adds a `composite` column, frozen and current, beside the
function-level column, and pins both counts. Claim wording follows the composite count.
The real distinct value is that the function's own contract becomes self-sufficient for
callers that pass no `tree`, such as `install_links(server)` or future callers. Name it
that way.

## F2 (A2 harm): the lane draft is a net operability loss on two points
The current lane `install_tree` (uncommitted, lines 178-203) raises
`install-tree-unpinnable:listdir`, `:lstat:<name>` and `:read:<name>`.

| Case | Frozen setup_error | Lane draft |
|---|---|---|
| unlistable directory (EACCES) | `install-tree-unpinnable:listdir:Permission denied` | `install-tree-unpinnable:listdir` (errno lost) |
| member `lstat` fails | `…:<name>:<strerror>` | `…:lstat:<name>` (errno lost, phase gained) |
| member read fails | `…:<name>:not-hashed` / `:unreadable` | `…:read:<name>` (phase gained) |
| `glibc-hwcaps/` plus an unreadable lib | `…:glibc-hwcaps:loader-searched-subdirectory;libX:unreadable` (up to 8 problems, `:1418-1419`) | `…:read:libX` only, because the first error short-circuits before `install_links` runs |

The mixed-fault directory is a strict harm: the operator now fixes faults one rerun at
a time. SimplifyAPI's bare `SetupError('install-tree-unpinnable')` (`advice/SimplifyAPI.md:9`)
is worse still. It drops every detail, and it fails the existing
`unpinnable-e2e.py:92` predicate `startswith("install-tree-unpinnable:")`.

**Rejection condition.** C1 harms A2 if, for any matrix cell, the current reason carries
fewer facts than the frozen composite reason: no errno, or fewer of the frozen problem
entries.

**Minimum remedy, two options; the L1 picks one:**
- (a) `install_tree` collects its failures and raises once after the loop. Entries use
  `phase:{name!r}:{strerror}`, are joined with `;` and capped at 8 like `:1419`. This
  keeps the errno and any multiple `install_tree` faults. Separately, declare in Limits
  that link problems are no longer reported in the same run.
- (b) When `install_tree` raises, the producer appends
  `install_links(server_real)[2][:8]` to the reason.

Either way, the matrix pins the exact reason strings for both arms, so the A2 change is
measured, not asserted.

## F3 (A3): the "all consumers refuse" claim is false at the gate
`tests/llamacpp-live/check-receipt.py:407-411` still has
`check_digest(..., install_tree_sha256, allow_none=True)`, commented "null only when the
producer could not list the directory". After C1, `install_tree` can never return
`None`, so the comment is false and the leniency is a dead permission. With a non-empty
`install_tree` and a null digest, the recomputation at `:412` is skipped, and the gate
says VALID unless `--expect-install-tree-sha256` is pinned. This was already measured:
`.ufo/waves/round-21/falsify/out/C2SetupErrorGrading/complete-null-tree-digest.json`
gave VALID, exit 0 (`advice/C2SetupErrorGrading.md` F3, open since round 16, `b8e485c`).
The selftest covers only the pinned case (`tree-sha-absent-expect`, `:1975-1977`). No
round-22 seat owns `check-receipt.py`.

No committed receipt outside `.ufo/` carries `"install_tree_sha256": null`; `git grep`
found none. So tightening the gate regrades only wave scratch fixtures.

**Rejection condition.** If C1's text says "all consumers" while
`complete-null-tree-digest.json` still grades VALID at the integrated commit, C1
overclaims.

**Minimum remedy, one of:**
- Narrow the wording to "the producer and its in-repo callers", and record gate F3 as
  named debt in Limits.
- Remove `allow_none=True` at `:411`, rewrite the `:407-408` comment, and add a selftest
  mutation "tree-sha-null-unpinned", expecting INVALID with no expect pin.

## F4 (A4, contract and mistake mining): round-21 M4 has recurred
The lane checkout `/home/vgpnk/Projects/shokunin/kama-shokunin` has uncommitted
modifications (git status ` M`) to `tools/kama-llamacpp-live.py` (+10/-9, the fail-closed
`install_tree`) and `tests/llamacpp-live/install-links-grid.py` (+7/-1, the `SetupError`
catch in `identity`). `.ufo/waves/round-22/build/sandboxes/` contains only `Matrix/`. So
the producer and caller writers edited the lane instead of their own clones; this is
`[INFERENCE]` from the missing sandboxes, and I did not identify the writer.

This also contaminates F1: if Matrix's "current" arm loads the lane path, it measures an
unreviewed stray write.

**Remedy.**
- The L1 restores both files from `master` before integration, using round 21's
  `git status --porcelain` gate.
- Matrix loads "current" from the integrated commit, never from the lane working tree.
- Record this as a Mistakes row (class: repeat of M4, with the lane checkout written
  despite the contract).

## Preserve (no harm found)
- The success path is unchanged in the lane draft: the digest expression at `:201-203`
  and the regular-only `S_ISREG` skip are the same.
- Keep `install_links`' `not-hashed` check. After C1 it is reachable only through a
  membership change between the two scans or an explicitly passed partial map
  (selftest `:1189`). It is still the race detector, not dead code.

## Checks for the L1 (not run here)
- Matrix `--arm both --json` with a composite column (F1).
- Reason-string pins per cell (F2).
- `check-receipt.py` against `complete-null-tree-digest.json` (F3).
- `git status --porcelain -- tools tests` before commit (F4).

No tools installed or updated. Owned and written path:
`.ufo/waves/round-22/build/advice/CritClaim.md`.

Report: .ufo/waves/round-22/build/advice/CritClaim.md
