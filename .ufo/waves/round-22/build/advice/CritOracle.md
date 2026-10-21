# CritOracle — C1 attack: frozen-source authenticity, fixed denominator, oracle independence

Seat `KamaR22.CritOracle` (critic, read-only). Base observed: `master` = `HEAD` =
`10271460cc575fc2280aa831e442726385fc2319`. No sandbox existed under
`build/sandboxes/` at read time, so this attacks the frozen source, the shared
interface, and the existing consumers, not a Matrix/ApiFix draft. No verification
was run, nothing was installed, and no REA devices were used. The only commands run
were read-only: `git rev-parse`, `git show | sha256sum`, `git log`, `git diff`, and
`git for-each-ref refs/replace`, plus stdlib `inspect` on `posixpath`/`genericpath`.

Axes: calibration 7 (primary); operability 8 (must not regress).

## Observed facts

| Fact | Value / location |
|---|---|
| Frozen producer blob id | `git rev-parse 10271460…:tools/kama-llamacpp-live.py` = `f030e6f116d507392f188105241b302334233df0` |
| Frozen producer bytes sha256 | `cec679495591cf2410334dfe08c648e310f23825181dcbae7d13b911c980e023` |
| Lane working tree today | identical bytes (same sha256). Until L1 integrates, "current" equals "frozen" in the lane and in every fresh clone. |
| Other "frozen" copies | `.ufo/waves/round-17/frozen/…` `b8c5e8d4…` and `round-18/frozen/…` `0efd1723…` are different bytes. `install-links-grid.py:49` pins `FROZEN_REV = 7a6bc911…`, not the round-22 base. |
| `refs/replace` | none today (`for-each-ref` empty). `install-links-grid.py:69-76` loads with plain `git show`, with no env scrub, no `--no-replace-objects`, and no byte pin, and decodes in text mode (`encoding="utf-8"`). |
| Frozen `install_tree` | `:178-202`. A listdir failure returns `({}, None)` (null digest, **not** comparable). An lstat or member-read failure `continue`s and still returns a str digest (comparable partial). |
| Producer cross-check at frozen | `:1414-1419` calls `install_links(server_real, tree)`. `:258` `name not in tree → not-hashed`, `:260` `lstat → name:strerror`, and `:233` `listdir:` all raise `SetupError('install-tree-unpinnable:…')`. |
| Producer catch-all | `:1607-1608`: any non-SetupError exception becomes `internal:<Type>`, setup-error, exit 2. |
| Server hashed before tree | `:1413` `server_sha = sha256_file(server_real)` runs before `install_tree`. |
| Python 3.14.8 | `posixpath.realpath` calls `os.lstat` and `genericpath.isfile` calls `os.stat` (inspected). `install_links` uses both. |

## Counterexample 1 — false provenance: "red-before" does not exist at the producer

The C1 statement says "before, install_tree silently skips errors; after, all
consumers must refuse." I traced every matrix fault class through the frozen
producer `main` path. The trace is from source and was not executed
[INFERENCE: traced, not run].

- **lstat fault on a member.** Patching `os.lstat` path-filtered also hits `install_links:245`. The result is `install-tree-unpinnable:<name>:<strerror>`, exit 2, and nothing is launched.
- **sha256_file / read fault on a library.** `install_tree` drops the member, then `install_links:258` reports it as `not-hashed`. The result is `install-tree-unpinnable:…:not-hashed`, exit 2.
- **sha256_file fault on `llama-server`.** It fires first at `:1413`, outside `install_tree`. The result is `internal:OSError`, exit 2. The fault fires, but at the wrong call site.
- **listdir fault.** `install_links:233` reports it. The result is `install-tree-unpinnable:listdir:…`, exit 2.

So at the producer consumer, frozen already refuses every non-race cell, and its
token even starts with `install-tree-unpinnable:`. The only frozen escapes are API
callers that use `install_tree` without `install_links(tree)`:

- the frozen arm of `install-links-grid.py identity(with_links=False)` (`:178-186`), and
- historical runners that derive pins from `install_tree` (e.g. `round-18/runs/run.py:58`). That runner checks only `_tree_sha is None`, so a partial str digest would become its own `--expect-install-tree-sha256` pin.

Because of the catch-all at `:1607`, a producer-level oracle that expects exit 2 also
cannot tell ApiFix's explicit `SetupError` apart from an accidentally propagated raw
`OSError`.

**Impacted axis:** calibration (overclaim of a consumer-level before/after delta).

## Counterexample 2 — denominator mixes two properties

The frozen listdir cells return a **null** digest, not a comparable partial one.
The consumers that exist today treat null as failure: `round-18 run.py:59-60` raises,
and the producer refuses via `install_links`. If the listdir cells are counted under
"comparable partial digest escaped", the headline red count is inflated by 2 cells
(listdir PermissionError and listdir OSError).

The lstat-`FileNotFoundError` cells are a different case again. Under mock, the
member still exists, so the oracle's "complete map" is a state the kernel cannot
produce. That cell measures refusal of an inconsistent enumeration. It does not show
that a real member was lost.

## Counterexample 3 — the oracle can be self-referential or vacuous

1. **Expected outcomes taken from running frozen.** If the frozen arm's observed results become the expected table, red-before is true by construction and cannot fail.
2. **Positive control computed by `install_tree`.** If the success digest is computed by `install_tree` (either arm) and then compared with itself, the "preserved bytes" claim is a tautology.
3. **Lookup-site drift.** Suppose ApiFix switches to `os.scandir`/`DirEntry.stat` or inlines `open`. An `os.lstat`/`module.sha256_file` patch then never fires, and the current arm returns a complete map. That reads as "no escape" or a confusing "violated" result, never as "fault not delivered". SrcMock reports the same failure mode.
4. **Attribution.** A global `os.lstat` patch also fires inside `posixpath.realpath` and in `tempfile` cleanup. A server-path read fault fires at `:1413`. A whole-run fire counter can therefore be greater than 0 even though the `install_tree` site was never faulted.
5. **Refusal predicate too wide.** `except Exception`, or `except OSError` on a raw propagation, would score a crash, an `AttributeError` from a bad mock, or a missing handler as "refused". Each exec'd module also defines its **own** `SetupError` class, so `isinstance` has to use the arm's own class.

## Counterexample 4 — frozen source authenticity

The `install-links-grid` loader pattern (plain `git show`, text decode, no byte pin)
would execute whatever the object store hands back. That includes a `refs/replace`
substitution, a `GIT_DIR`/`GIT_REPLACE_REF_BASE` environment override, the wrong rev
reused from `FROZEN_REV = 7a6bc911…`, or a `.ufo/waves/*/frozen/` copy with different
bytes.

Today the lane's working tree has the same bytes as frozen. An arm that loads
"current" from the working tree before integration therefore measures frozen twice,
and nothing in the output would show it unless the arm's bytes are recorded.

## Falsifiable rejection conditions (L1/judge rejects C1 if any holds)

- **R1 — authenticity.** The frozen arm's executed bytes are not checked equal to sha256 `cec679495591cf2410334dfe08c648e310f23825181dcbae7d13b911c980e023` (blob `f030e6f1…`, rev `10271460…`) before `exec`. Or the loader does not use a scrubbed git env (as round-21 did) with `--no-replace-objects`. Or a mismatch does not exit 2.
- **R2 — current provenance.** `--json` does not record the current arm's sha256 and the lane commit it was measured at. Or the current sha256 equals `cec67949…` while the report claims green-after.
- **R3 — fixed denominator.** The population is not a pinned literal: a cell-id list plus count, with a digest over the sorted ids, together with per-cell, per-arm expected outcomes written as constants. Or a run whose executed cell set differs from the literal still exits 0.
- **R4 — fault delivery.** Any cell reports green or red without a fire count greater than 0 that is attributed to the `install_tree` call frame of that arm only (for example, a side effect armed only for the duration of the `install_tree` call and filtered to the target path). An unfired cell must exit 2.
- **R5 — refusal predicate.** "Refused" accepts anything other than `isinstance(exc, arm_module.SetupError)` with `exc.code` equal to the agreed token (or the agreed prefix). Raw `OSError` propagation must be its own outcome and is not counted as green.
- **R6 — property split.** The report counts the null-digest listdir cells as "comparable partial digest escaped". The headline must give separate counts for comparable-partial (str digest ≠ independent full digest), null/empty identity returned without an exception, and refused.
- **R7 — independent positive control.** The success digest is not checked against three things: (a) a hashlib-only recomputation from the literal bytes the matrix wrote, using the `'{n} {sha}\n'` sorted formula; (b) a pinned hex literal; and (c) frozen's output on the same unfaulted tree. In addition, the control tree must include a live symlink, a dangling symlink, a symlink to a directory, a subdirectory, and a FIFO, all expected to be skipped with no exception in **both** arms. Without these, the "existing symlink semantics" claim is unguarded; an `os.stat` rewrite would refuse a dangling link.
- **R8 — consumer scope.** The report claims any consumer-level red-before (producer exit or launch) without an executed frozen cell in which the producer accepted a partial tree. Per Counterexample 1 the expected producer-level red count is 0 for non-race cells. C1 must be worded as **API-contract** hardening (direct `install_tree` callers), with the producer's refusal at frozen stated as already present via `install_links`.
- **R9 — matrix self-test.** `--selftest` does not show the oracle can fail. It must run against synthetic producer stubs: one that escapes with a partial digest (exit 1), one that refuses with the wrong exception class or token (not green), one whose lookup site is unpatched so the fault never fires (exit 2), and one that changes the success digest (exit 1).

## Smallest safe correction (advice, not an implementation)

- **Matrix:** load the frozen arm via scrubbed `git --no-replace-objects show 10271460…:tools/kama-llamacpp-live.py` as bytes, compare against the sha256 literal, then decode. Record the current arm's sha256 and HEAD in the JSON. Pin `CELLS` (ids, count, sorted-id digest) and an `EXPECTED[arm][cell]` literal table. Arm the faults only around the `install_tree` call, path-filtered, with a fire counter per cell. Classify outcomes as `refused | raw-oserror | partial-digest | null-identity | complete | unfired`, using the arm's own `SetupError`. Use a three-way positive control over a fixed-bytes tree that includes the non-regular entries listed in R7. Add stub-producer selftests for R9.
- **ApiFix:** keep the `os.listdir`/`os.lstat`/`sha256_file` lookup sites. Matrix fault delivery depends on them; if they change, Matrix must move its injection points in the same round.
- **CallerRepair:** `unpinnable-e2e.py:91-92` requires the `install-tree-unpinnable:` prefix *with a colon*. A bare-token SetupError from `install_tree` would only arrive on the pristine scan at `:73`, where it is uncaught (`:105` catches only OSError/RuntimeError/ValueError) and would exit with a traceback status instead of 2. Make it map to 2, could-not-evaluate.
- **Recipe:** keep tree pins as literals (`6c216313…` per `round-21/recipe-final.json:166-167`). Never derive a pin by calling `install_tree` in `run.py`.
- **L1 report:** split the calibration counts per R6 and word the claim per R8.

## Owned paths

- Written: `.ufo/waves/round-22/build/advice/CritOracle.md` (this file only; append-only from here on).
- No tools installed or updated.

Report: .ufo/waves/round-22/build/advice/CritOracle.md
