# Capability — round 22 C1: existing capability hardened, or new repertoire?

Seat: KamaR22.Capability (connector, read-only). Owned path, the only file written:
`.ufo/waves/round-22/build/advice/Capability.md`. No production edits. No builds, tests,
selftests or fault runs. No installs or updates. Coordination messages went to
KamaR22.ScoreDraft and KamaR22.CallerRepair.

## Verdict

**Reliability hardening of the existing capability `live-llamacpp-lifecycle`
(first working round 16, `SCORECARD.md:628`). It is not new repertoire. Add no
capabilities row.** The fault matrix is a calibration instrument. It needs a SKILL.md
instrument-registry row. It must not get a SCORECARD capabilities row.

## Axes

| Axis | Effect of this ruling |
|---|---|
| calibration 7 (lowest, the claim's axis) | improved-bounded at most. The claim is scoped to statements that are actually false at base (below). |
| operability 8 | held. No new "can now do", and no producer behavior regression. |
| expansion trend | unchanged. No capability or knowledge surface is added. |
| quality trend | improved-bounded. The API now matches its docstring. |
| row count | unchanged. This avoids inflation. |

## Evidence

1. **Rule.** `../AXES.md:57-64`: the axes measure quality, and the capabilities table
   records what the shokunin "can now *do*". Rows enter only by demonstrating a
   capability running.
2. **Lane precedent: install-pin hardening never added a row.**
   - R17 `SCORECARD.md:664-669`: "no new capability row (the round-16 row is hardened, not new)".
   - R18 `:749-751` and `:794-796`: "hardened, not newly acquired".
   - R19 `:827-838`: the tree-sha pin, 8→8, no row.
   - R21 `:1024-1026`: "C2 hardens the existing live-receipt capability's install pin". This is the R21 CapabilityRuleReader ruling (`round-21/build/advice/CapabilityRuleReader.md:30-38`).
   - Expansion: "a source row alone is not new repertoire" (`LOG.md:1184`).
3. **R21 already planned this as hardening.** `SCORECARD.md:1031-1033` lists the frontier
   item "unreadable-member fail-closed rule for `install_tree` consumers *outside the live
   producer*".
4. **No nudge pressure.** The last row entered in round 20 (`SCORECARD.md:909-918`).
   Round 21 was 1 of 4 (`:1027`), so round 22 is **2 of 4**. Calibration 7 is below
   saturation 8 (`:132`). The lowest-axis obligation therefore binds, and the nudge cannot
   be used to justify a row.

## Second-order finding: where "red-before" actually is

At frozen `10271460` the **live producer already fails closed** on these faults. Only
`install_tree()` itself silently returns a partial result.

- The producer calls `install_links(server_real, tree)` immediately after `install_tree`
  (`tools/kama-llamacpp-live.py@10271460:1414-1419`). Any `link_problems` raise
  `SetupError('install-tree-unpinnable:…')`.
- `install_links` records a problem for each of these:
  - its own `listdir` failure (`:232-234`);
  - a per-entry `lstat` OSError (`:260-261`);
  - `os.access` unreadable (`:256-257`);
  - a regular member missing from the supplied tree, "not-hashed" (`:258-259`).
- SKILL.md states this at `:703-704`: "the producer now refuses … unhashed members". The
  producer selftest pins the partial-map case at `:1189-1191`.

Static per-cell consequence. I reasoned this from source and did not run it:

| Fault | Frozen `install_tree()` API | Frozen producer end-to-end |
|---|---|---|
| listdir | returns `({}, None)` | `{}`: every regular member is not-hashed, or install_links' own listdir fails → refused |
| lstat | member silently dropped (partial digest) | install_links lstat fails, or the member is not-hashed → refused |
| sha256_file on a library | member silently dropped (partial digest) | not-hashed → refused |
| sha256_file on the server | — | `sha256_file(server_real)` at `:1413` runs *before* `install_tree`. Its OSError lands in `except BaseException → _record_internal` (`:1607-1608`). That is an internal fault in both arms, not an install-tree refusal and not a partial digest. |

**Proposed move.** State the C1 red-before at the **`install_tree()` API arm** (the
frozen blob is loaded in-process): "returns a comparable partial map/digest or `None`".
Add **one producer-level arm as a no-harm control**, expected to refuse in both arms.
Do **not** claim that the live producer or its receipts ever recorded a partial identity.
That claim would be false at base and would be a calibration overclaim inside a
calibration claim.

**Mistake mined.** The base docstring "{basename: sha256} for every regular file"
(`:179-181`) was false under OSError. That statement-versus-behavior mismatch is the
honest calibration target, together with the R21 frontier wording. Neither is a gap in
the capability.

## Synthesis across proposals

There is a contradiction between proposals:

- `SimplifyAPI.md:9` recommends the bare token `SetupError('install-tree-unpinnable')`.
- The shared interface text says the same.
- `tests/llamacpp-live/unpinnable-e2e.py:91-92` requires `setup.startswith("install-tree-unpinnable:")`, with a colon.

Colon-qualified codes such as `install-tree-unpinnable:listdir`, `…:lstat:NAME` and
`…:read:NAME` keep the existing predicate and SKILL.md:694-695's wording valid, with zero
edits in that consumer. They also keep reason detail without a subtype. A bare token would
force a caller edit that serves no purpose. Recommend the colon form.

There is one residual hazard. A member name containing a control character would be
embedded in the setup_error. `install_links` already flags such names (`:237-240`), but
under the new order `install_tree` raises first. This is cosmetic: it still refuses.

## Observed contract hazard (reported, not judged)

The **lane checkout** `/home/vgpnk/Projects/shokunin/kama-shokunin` has uncommitted edits.
`git status` shows `M tools/kama-llamacpp-live.py` and `M tests/llamacpp-live/install-links-grid.py`.
The edits are 17 insertions and 10 deletions, implementing the colon-qualified
fail-closed `install_tree` and a `SetupError` catch in `identity()`. Meanwhile
`.ufo/waves/round-22/build/sandboxes/` did not exist when I looked.

The contract says seats never mutate the lane checkout, and only L1 integrates. L1 should
confirm who wrote these edits before integrating. If they did not come from L1, measure
from sandbox clones and not from this working tree. I did not touch them.

## Risks

- **A row is added anyway**, for example "fail-closed install identity" or
  "install-io-grid". That would inflate the repertoire and reset the stagnation window on
  hardening, which contradicts R17–R21.
- **Producer-arm "red" is reported as frozen**. That would fabricate a before-state. The
  matrix should report producer cells as *refused at base*.
- **Server-read cell**: the server read is classified as an internal fault, not an
  install-tree refusal, so the Matrix/ApiFix expected classes must say so. If the claim
  wants a refusal there, that is a separate producer change outside the C1 scope.
  [INFERENCE: I have not seen Matrix's report.]

## Proposed checks (for L1 after integration; not run here)

- `python3 tests/llamacpp-live/install-io-grid.py --arm both --json`. Expected: API arm
  frozen exits 1, current exits 0. Producer-control cells are refused in both arms.
- `python3 tests/llamacpp-live/install-io-grid.py --selftest`
- `python3 tools/kama-llamacpp-live.py --selftest`. This checks that the
  `install_tree`/`install_links` digests are byte-identical on success.
- `python3 tests/llamacpp-live/install-links-grid.py --arm both --json`. Expected: exit 1
  from frozen by design. `back_compat_install_tree_sha256_equal=true`, and the
  `regular-unreadable` cell is still detected.
- `python3 tests/llamacpp-live/unpinnable-e2e.py`. Expected: exit 0, with no edit to its
  colon predicate.
- In the SCORECARD round-22 text, search for any `capabilities` append. Expected: none.
  The "window 2 of 4" line should be present.

Report: .ufo/waves/round-22/build/advice/Capability.md

## Appended correction: line anchors

The `@10271460` anchors in the second-order section came from the modified working tree,
whose `install_tree` docstring is one line longer. The verdict and findings are unchanged.
Frozen-blob anchors, from `git show 10271460:tools/kama-llamacpp-live.py`:

| What | Frozen-blob line(s) |
|---|---|
| producer `sha256_file(server_real)` | 1413 |
| `install_tree` call | 1414 |
| `install_links` call | 1415 |
| `if link_problems` | 1417 |
| `SetupError('install-tree-unpinnable:'` | 1418 |
| `install_links` listdir except | 233 |
| control-character problem | 239 |
| unreadable | 257 |
| not-hashed | 259 |
| per-entry OSError | 260 |
| selftest partial map | 1188-1189 |
| producer `except SetupError` | 1602 |
| producer `except BaseException → _record_internal` | 1606-1607 |
| docstring "for every regular file" | 179 |

## Appended note: coordination messages not processed

Both peer notes were delivered, but neither recipient processed them, because each
recipient's wake turn failed.

- KamaR22.ScoreDraft: the wake turn failed with HTTP 429 `rate_limit_error`, with retry-after-ms=6396000 (about 107 minutes).
- KamaR22.CallerRepair: the wake turn failed with "Codex is at capacity" after it exhausted its retry budget.

I did not resend: a resend would hit the same limits. L1 should relay two points to those
seats or their successors:

- to the SCORECARD drafter: no capabilities row, and the window is 2 of 4;
- to the caller-adaptation seat: keep the colon-qualified codes, so the
  `unpinnable-e2e.py:91-92` predicate needs no edit.

Report: .ufo/waves/round-22/build/advice/Capability.md
