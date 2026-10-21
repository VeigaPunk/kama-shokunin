# MatrixMutation — round 22, design only

Seat: `KamaR22.MatrixMutation`. State: **DESIGNED / NOT RUN**. This is advisory detector design, not a round verdict or executed mutation result. No subject bytes changed; no build, test, selftest, smoke run, service launch, REA device, or runtime orchestration invoked.

## Axes

- **Calibration (C1):** distinguish a returned incomplete identity, a typed refusal, and inability to evaluate; no crash-as-kill.
- **Operability (assigned lowest axis7, held at 8 in tasking):** exact bounded, reproducible probe commands and restoration evidence.
- **Coverage / compatibility:** independently remove each I/O refusal; retain exact successful regular-file map/digest and intentional symlink/nonregular exclusion. No endpoint-health/authentication claim.

## Static evidence and detector contract

Observed, not behaviorally exercised: `git show 10271460cc575fc2280aa831e442726385fc2319:tools/kama-llamacpp-live.py` exited 0. Frozen `install_tree` at lines 178–202 returns `(tree, None)` on listdir failure; its lstat and member-hash handlers `continue`, then return the digest of the remaining map. `sha256_file` reads through `open(..., 'rb')` at lines 171–176. A listdir escape is therefore a **null identity**, not a comparable partial digest; the other two handlers can yield comparable partial digests.

`KamaR22.Matrix` supplied the following planned IDs (design contract, not yet inspected implementation):

- `listdir:permission`, `listdir:oserror`: **2** rows.
- `lstat:{server|library}:{permission|missing|oserror}`: **6** rows.
- `read:{server|library}:{permission|missing|isdir|oserror}`: **8** rows.
- `control:complete-map-digest`, `control:ignored-symlink-directory`: **2** controls.

Fault success requires the loaded producer's `SetupError` with `.code == 'install-tree-unpinnable'`. Any returned identity, including `(tree, None)` or an empty map, is `ESCAPED`. Unexpected exceptions are errors, not evidence of the intended refusal. Both controls must return the independently pinned two-regular-member map and exact combined digest, not merely agree between frozen/current arms. The second control adds a symlink and subdirectory without changing that expected identity.

## Four independent single-point probes — final integrated phase only

Select the statement structurally **inside `install_tree`**, by the operation protected by its enclosing handler. Do not replace all matching raises, mutate `SetupError`, change the detector, or touch `install_links`. These recipes target ApiFix's declared three-handler fail-closed design; resolve the final source selector after integration rather than using stale line numbers. Replace the entire selected raise statement, including `from exc` if present. Each trial starts from pristine integrated bytes.

All following outcomes are **[INFERENCE] predictions**, not observed outputs.

| Probe | Single behavior-bearing change in sandbox producer | Expected semantic detector result |
|---|---|---|
| `M-listdir-refusal` | In the handler protecting `sorted(os.listdir(directory))`, replace only `raise SetupError('install-tree-unpinnable')` with `return tree, None` (the frozen recovery). | Both named listdir rows return `({}, None)` and are `ESCAPED`; the other 14 fault rows remain typed refusals; both controls pass. Current-arm exit 1. Counting only non-null digest escapes would miss this mutant. |
| `M-lstat-refusal` | In the handler protecting `os.lstat(full)`, replace only the refusal raise with `continue`. | All 6 lstat rows are `ESCAPED`. The returned map is the pinned map minus the targeted server/library; the returned digest is the canonical digest of that smaller map. Other 10 faults remain refusals; both controls pass. Exit 1. |
| `M-read-refusal` | In the handler protecting `tree[name] = sha256_file(full)`, replace only the refusal raise with `continue`. | All 8 read rows are `ESCAPED`, again with the targeted member absent and the smaller-map digest returned. Other 8 faults remain refusals; both controls pass. Exit 1. |
| `M-always-raise` | Insert exactly `raise SetupError('install-tree-unpinnable')` immediately after the `install_tree` docstring, before any I/O. This is a control, not an I/O-recovery deletion. | Both unpatched named controls must report an evaluated mismatch: refusal where the exact tuple is required. The detector must not be green merely because every fault invocation also raises. Those fault injections have zero target hits and earn **no** refusal credit. Expected property-failure exit 1; an unavailable/error-only result is not a killed mutant. |

The 2/6/8 predictions apply to the declared rows above, not an open-ended I/O population. A handler deletion need only produce its named semantic escape to establish sensitivity; errors or unrelated failures cannot substitute for that witness.

## Lookup, activation, and output rules

- Use the module objects actually loaded by the detector. Existing loaders create exec-loaded modules; string patch targets can fail import resolution or patch another module. `SrcMock.md:35–59` documents the lookup sites and source reopening.
- Patch `producer.os.listdir`, `producer.os.lstat`, or `producer.sha256_file` with `patch.object`. Capture each original callable **before** patching. Delegate non-target paths; raise only at the exact install directory/member. Create fixtures before the patch and clean up after its context exits. `producer.os` is the shared stdlib module, so an unconditional process-wide failure can break the detector itself.
- Count actual **targeted raises**, not just calls to a delegating wrapper. Require a reached target for every claimed I/O refusal/escape; otherwise the I/O cell is unavailable. For the always-raise control, a no-fault golden mismatch is already a known violation; missing fault activation must not be mislabeled successful refusal. If unavailable cells mask it into exit 2, report that classification limitation, not a kill.
- `PermissionError`, `FileNotFoundError`, `IsADirectoryError`, and `OSError` are suitable for their declared cells because frozen handlers catch `OSError`. Arbitrary `RuntimeError` is not a red-before substitute.
- Retain actual JSON, stderr, process exit, target-hit counts, exception class/code, returned map/digest, and named failed rows. A changed source-hash field, different stdout, nonzero exit, traceback, timeout, or wrong exception **alone** never establishes a kill.

## Exact future surface and restoration protocol

Owned **now**, and the only artifact written by this seat:

`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-22/build/advice/MatrixMutation.md`

Reserved **proposed**, not created or exercised:

- Scratch `S=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-22/build/sandboxes/MatrixMutation`.
- Sole mutation target `$S/tools/kama-llamacpp-live.py`.
- Read-only detector `$S/tests/llamacpp-live/install-io-grid.py` (Matrix-owned implementation; not owned for editing here).
- Evidence root `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-22/build/out/MatrixMutation/<probe-id>/` with distinct pristine/mutated/restored stdout, stderr, exit records; source preimage and three SHA-256 values; detector SHA-256; hit/row evidence. Do not overwrite prior report bytes.

After L1 integration, obtain the candidate using the required unique clone command, **not a sibling sandbox**:

```sh
git clone --shared --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-22/build/sandboxes/MatrixMutation
```

Confirm through retained source evidence that the scratch contains the integrated fix and detector. Retain frozen reference `10271460cc575fc2280aa831e442726385fc2319`; do not mutate that arm. Create `$S/.probe-tmp` inside the scratch. The **same** bounded behavioral invocation is used on pristine, mutated, and restored source bytes for each probe:

```sh
timeout 30s env PYTHONDONTWRITEBYTECODE=1 TMPDIR="$S/.probe-tmp" python3 "$S/tests/llamacpp-live/install-io-grid.py" --arm current --json
```

`S` is the literal scratch path defined above. Capture output outside the command into the evidence root. Do not use `--arm frozen`/`both` as the mutation baseline: they include intentionally violating frozen behavior. Do not run the producer's broad `--selftest`, launch a server, or invoke a separate orchestration runtime for these probes.

For each probe: save exact subject bytes and SHA-256 plus detector SHA-256; pristine detector must exit 0. Apply just the one mutation and record the new hash. Run the same invocation. In a `finally`-equivalent restoration, restore the saved bytes without git reset/checkout/index operations, even after detector failure; require byte equality and restored SHA-256 equal to pristine, then rerun the identical invocation and require exit 0. The detector hash must remain unchanged throughout.

**Verdict protocol:** killed only with pristine 0 → mutant 1 containing its named `ESCAPED`/golden-control mismatch → restored 0, activated I/O witness where applicable, and exact restoration. Mutant 0 is survived (coverage finding). Baseline/restored failure, error-only output, timeout/signal, unavailable result, wrong mutant scope, missing activation evidence, or restoration mismatch is inconclusive; never credit a crash or baseline failure as a kill.

## Actual result / restoration / tooling

- Mutant applied: **none**. Expected detector: specified above. Actual detector output: **none; prohibited during this build wave**.
- Verdict: **NOT RUN**, not killed/survived. Execution-stage inconclusive classification is not a substitute for this explicit unrun state.
- Before/mutated/restored SHA-256: **not measured**; no mutation or restoration occurred. No scratch clone or probe artifacts created. Source reference is the statically opened frozen commit above.
- Production/lane sources, sibling sandboxes, Git index, `.jj`, fleet root, config, services, and secrets were not written or inspected for values.
- Tool installs/updates: **none**. Static tool execution was the read-only `git show` above; all behavioral runs are deferred to L1's final integrated phase.

## Append-only clarification

Supersedes the parenthetical in the Operability axis bullet: **C1 is calibration, the tasking's lowest score 7; operability is 8 and preserved.** This seat does not measure or award any score change.

Matrix subsequently reported (implementation-owner communication, not independently executed here) that refusal credit requires `injected_calls == 1` and `raised == 1`. Unreached injections produce `observed:error` / `injection-not-reached`; the always-raise mutant's controls retain their named IDs with `matches_pinned_map_and_digest:false`, and the current-arm invocation returns 1, not 2. This supplies the expected output shape for `M-always-raise`: its kill witness must be those evaluated control mismatches, never the fault-row errors. All execution and hash evidence remains **NOT RUN**.

## Append-only control-oracle update

Matrix's subsequent DirectoryControl-driven change supersedes every earlier occurrence of `control:ignored-symlink-directory` with **`control:subdir-member-skipped`**. This positive cell contains a populated non-`glibc-hwcaps` subdirectory and retains a regular-file symlink. It must return its pinned **full three-regular-member map and exact digest**, excluding both the subdirectory's contents and the symlink as members. This detects over-broad nonregular refusal and unintended recursive hashing.

The other control remains `control:complete-map-digest`; each control is checked against its own pinned complete fixture identity, not an assumed shared two-member map. Thus `M-always-raise` must fail these two current IDs. Fault IDs and the 2/6/8 branch-deletion predictions remain unchanged. This update is an implementation-owner design communication only: no probe was applied or run, and no hashes/restoration evidence were newly measured.

## Append-only final control split

Matrix and DirectoryControl subsequently isolated directory and symlink behavior for single-variable attribution. This supersedes all prior two-control/combined-control descriptions above. The current design has **16 fault rows plus 3 distinct positive controls**:

- `control:complete-map-digest`: unmodified complete fixture.
- `control:subdir-member-skipped`: populated non-hwcaps directory only; no added symlink.
- `control:symlink-member-skipped`: symlink only; no added directory.

Each arm must return the **same pinned full regular-member map and exact combined digest** on all three controls. Consequently the listdir/lstat/read deletion predictions are respectively **2/6/8 escapes, 14/10/8 remaining refusals, and 3 passing controls**. `M-always-raise` must produce named golden-control mismatches for **all 3** IDs, with no credit for unreached I/O injections. All outcomes remain predictions; no mutation, detector run, hash measurement, or restoration occurred.

## Append-only static source alignment

CallerRepair requested confirmation of bare-code versus suffixed-reason handling. Current draft source was opened statically, with **no execution**:

- `build/sandboxes/ApiFix/tools/kama-llamacpp-live.py:157–160`: `SetupError(code, detail=None)` preserves bare `.code`, stores `.detail` separately, and includes detail only in exception text.
- The same draft at `:190,197,204` raises `SetupError('install-tree-unpinnable', detail)` for the three I/O handlers. For the deletion probes, replace that **whole two-argument raise statement** with the specified return/continue; leave the detail assignment alone. The one-argument always-raise insertion remains valid.
- The same draft at `:1660–1662` serializes optional detail into the receipt's `setup_error` text. Suffixed receipt text is therefore compatible with a bare exception `.code`; these are different interfaces.
- `build/sandboxes/Matrix/tests/llamacpp-live/install-io-grid.py:168–176` checks the loaded module's `SetupError` and exact bare `.code == 'install-tree-unpinnable'`. This is statically aligned with ApiFix, without broadening the oracle. Its `:44–67` confirms the 16 fault IDs and final 3 control IDs. The earlier reason-format warning concerns a different draft, not this inspected bare-code comparison.

Paths in this section are relative to `.ufo/waves/round-22/` under the lane root. These are moving draft observations, not integrated-revision or behavioral verification. Mutants, detector outputs, and before/mutated/restored hashes remain **NOT RUN / unmeasured**.
