# Round 63 — MT19C2HostBusy: host-busy attack on the C2 counter

Seat: MT19C2HostBusy (mutation-tester, leaf). Item: attack the host-busy declared outcome of
`tools/round63-c2-counter.py` at tip `03a6a1d850902a66a13dfad33f89cf3a8b759a09`.
Scope: advisory findings only. No commit to the lane, no lane edit, no verdict on the claims.
Evidence: `.ufo/waves/round-63/w1/out/MT19C2HostBusy/` (run logs, patches, receipts, fixtures).
Scratch `/fast/scratch/hyaku/kama-r63/w/MT19C2HostBusy` removed after receipts were copied.

## 1. Bottom line

- **(a) accept host-busy for every row — KILLED.** Only the `hostbusy` family notices. Its named
  failure (`hostbusy-not-declared`) disappears, so the family escapes and the counter prints met=False.
- **(b) drop the pgrep before/after requirement — SURVIVED.** met=True, 12/12 families credited.
  No family probes the pgrep cross-check.
- **(c) refusal with a different message counts — SURVIVED.** met=True, 12/12 families credited.
  No family probes the refusal text.
- **Registry that marks every row host-busy reaching met=True:** not in any mutant tested. Under (a)
  it fails because two families (`verdict`, `hostbusy`) become no-ops on an all-host-busy registry,
  not because host-busy is checked. Under (b) and (c) it fails on 11× `hostbusy-not-declared`.
- **Fake pgrep with NO foreign llama-server, unmutated counter: ACCEPTED (met=True).** The environment
  allowlist does **not** block it (PATH is on the allowlist; the counter's own cross-check does not use
  the allowlist at all).
- **Two further calibration holes found while attacking:**
  - H1: the conditional row's *recorded verdict* is never compared to the live outcome. A registry that
    records `host-busy` on an idle host, with its observed text updated, reaches met=True.
  - H2: the counter is not re-runnable on the same `--work` directory (live-ollama-lifecycle flips to FAIL).
- **Pre-existing at this tip, unchanged by my fixtures:** `selfdesc_mismatches=8` (freeze says this is
  intentional before L1 re-derivation). Baseline `met=False` is for that reason only (section 3).

## 2. Method and disclosed fixtures

Every run used a clone of the lane at the tip (`git clone --shared`, `checkout --detach`, one committed
variant per clone, `T=HEAD`). Every mutated counter ran from its clone path against its committed tip.
Each run used its own `--work` dir (`checkout_tip` reuses an existing `work/tip`, so sharing one would
mix variants). No lane file was edited, nothing was committed in the lane, and the lane was read only.

Two disclosed fixtures, applied identically to every variant:

- **ISO (isolation):** `selfdesc = 0` in `main()` (counter.py:525). This removes the known
  `selfdesc_mismatches=8` gate so that `met` reflects the host-busy gates. Every variant except the
  unmutated baseline carries it. The unmutated tip run without ISO is reported as the base line.
- **Tool fixtures** (committed in the clone, scored by the counter as tip content):
  - *Fixture A:* the idle gate in `kama-context-capacity.py:794` is forced to `if True:`. The tool
    refuses `host-not-idle-before-K1` (exit 2) regardless of its pgrep probe.
  - *Fixture B:* as A, and the refusal text becomes `no-free-port-in-range-for-K1` (a real message the
    tool can emit).

Mutants (clone commits; patches in `out/.../patches/`):

- **M_a** (`ma-real` e013aa2…): `score()` drops the `hostbusy-not-declared` gate (counter:310-312),
  sets `declared={'true','host-busy'}` and `ok = outcome in declared`, so any row may be host-busy.
- **M_b** (`mb-ns-A` 281e7a8…): `run_bound` changes `if before and after:` to `if True:` (counter:365).
- **M_c** (`mc-real-B` 2001843…): the refusal branch accepts any rc==2 refusal with a non-empty last
  output line, which becomes the observed/sensitivity pattern (counter:363-370).

Namespace: an empty PID namespace is built with
`sudo -n unshare -p -f --mount-proc setpriv --reuid=1000 --regid=1000 --clear-groups env HOME=… PATH=…`.
Inside it `pgrep -x llama-server` returns rc=1 and `/proc` shows three processes. `unshare -U`
(user namespace) also works, but it breaks the live-receipt-replay selftest (see section 6), so I did
not use it for evidence.

Host state during the wave: foreign llama-servers were live (operator ports 1234 and 45669 plus other
seats), so every real-host run reads `host_busy=1` from genuine foreign processes. I did not touch them.

## 3. Verbatim counter lines

Baseline, unmutated counter, lane tip (`out/.../runs/base/out.txt`):
```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False
```
Unmutated + ISO, real host (`runs/iso-real`) — the honest isolated baseline:
```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=0 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=True
```

### 3a. Mutant (a): accept host-busy for every row

| run | registry | counter line (verbatim, `runs/<name>/out.txt`) | escaped families | verdict |
|---|---|---|---|---|
| ma-real | tip | `… host_busy=1 mismatches=0 … controls_rejected=11/12 errors=0 met=False` | `hostbusy` (stderr: `control-escape: hostbusy {'met': True, 'hit': False, 'tags': []}`) | KILLED |
| ma-allhb-real | every row host-busy | `… host_busy=1 mismatches=0 … controls_rejected=10/12 errors=0 met=False` | `verdict`, `hostbusy` | KILLED, but see below |

On the all-host-busy registry the two escapes are vacuous. `verdict` replaces the first `\ttrue\t` and
there is none; `hostbusy` replaces the first `\ttrue\t` and there is none. So met=False comes from two
no-op families, not from a host-busy check. The no-op applies only to an all-host-busy registry:
with any `true` row, `verdict` and `hostbusy` do flip a row, so the escape is specific to that input.

### 3b. Mutant (b): drop the pgrep before/after requirement — SURVIVED

| run | fixture | counter line (verbatim) | verdict |
|---|---|---|---|
| mb-ns-A (namespace, no foreign servers, Fixture A) | M_b + ISO | `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=0 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=True` | SURVIVED |
| unm-ns-A (same fixture, unmutated counter) | ISO | `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=11/12 dead=0 host_busy=0 mismatches=1 canonical=63 selfdesc_mismatches=0 sens_selftest=4/4 controls_rejected=0/12 errors=0 met=False` | pair: the unmutated counter rejects the same tool output |

Expected catch: none of the 12 families. All 12 credit. The pgrep cross-check (the only
independent evidence that a host is busy) has no control.

On the real host M_b cannot be told apart from the unmutated counter, because both the tool's refusal
and the counter's pgrep see genuine foreign servers. It is only exposed when the tool refuses with no
foreign server visible to the counter, which is what the namespace fixture reproduces.

### 3c. Mutant (c): refusal with a different message counts — SURVIVED

| run | fixture | counter line (verbatim) | verdict |
|---|---|---|---|
| mc-real-B (real host, Fixture B: refusal `no-free-port-in-range-for-K1`) | M_c + ISO | `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=0 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=True` | SURVIVED |
| unm-real-B (same fixture, unmutated counter) | ISO | `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=11/12 dead=0 host_busy=0 mismatches=1 canonical=63 selfdesc_mismatches=0 sens_selftest=4/4 controls_rejected=0/12 errors=0 met=False` | pair: the unmutated counter rejects it |

Expected catch: none of the 12 families. No family puts a different message in the tool output.

### 3d. The all-host-busy registry under each mutant

| mutant | counter line (verbatim) | why it is not met |
|---|---|---|
| unmutated (`unm-allhb-real`) | `… covered=1/12 bound=1 … controls_rejected=0/12 errors=11 met=False` | 11× `hostbusy-not-declared` (correct) |
| M_a (`ma-allhb-real`) | `… controls_rejected=10/12 errors=0 met=False` | `verdict`, `hostbusy` no-op escapes (section 3a) |
| M_b (`mb-allhb-ns-A`) | `… covered=1/12 bound=1 … errors=11 met=False` | 11× `hostbusy-not-declared` (gate untouched) |
| M_c (`mc-allhb-real-B`) | `… covered=1/12 bound=1 … errors=11 met=False` | 11× `hostbusy-not-declared` (gate untouched) |

No all-host-busy registry reached met=True in any mutant tested.

## 4. Attack: unmutated counter accepts host-busy with NO foreign llama-server

Setup: the **unmutated** counter (ISO only) and the **unmodified** tip capacity tool, run in the empty PID
namespace (section 2), with `$S/fakebin` first on PATH. The fake `pgrep` answers any `llama-server` query
with `1` and delegates everything else to `/usr/bin/pgrep`. PID 1 exists in the namespace, so the tool's
`/proc/<pid>/stat` check passes.

Result (`runs/iso-ns-fake/out.txt`):
```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=0 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=True
```

Evidence that no foreign server runs:
- Inside the namespace, `/usr/bin/pgrep -c -x llama-server` gives count 0 with rc 1, and `/proc` lists 3 processes.
- The tool's own receipt (`receipts/iso-ns-fake-cc.json`): `error = host-not-idle-before-K1`, `exit_code = 2`,
  `host_idle = {ok: false, other_pids_seen: [1], waited_s: 20.018}`. The refusal came from the forged pid.

Control run (`runs/iso-ns`, no fake pgrep, same empty namespace): `host_busy=0 mismatches=1 … met=False`.
The tool sees an idle host and passes. The mismatch is the row's recorded `observed` text (`host-not-idle-…`)
against the live `all_ports_closed` pattern; see H1 below.

**Does the environment allowlist block it? No.**
- `ENV_KEYS = ('PATH','HOME','LANG','LC_ALL')` (counter.py:42), plus `TMPDIR`, includes **PATH**. The bound
  run inherits the fake `pgrep` through PATH.
- `pgrep_foreign()` (counter.py:336-339) calls bare `pgrep` with the caller's full `os.environ`. It is not
  restricted to the allowlist at all, so the cross-check uses the same forged PATH.
- The lane tool resolves `pgrep` by bare name (`kama-context-capacity.py:220`) and trusts any pid it
  returns that is not a zombie (`:231-237`). It does not check `comm` or `exe`.
- Nothing in the 12 families depends on the pgrep provenance, so the forged pid passes all of them.

Even with real foreign servers present (the real host), the counter trusts pgrep output. The forgery only
shows when no foreign server exists, which is why the namespace run matters.

## 5. Calibration holes beyond the three mutants

**H1 — recorded verdict is never compared on the conditional row (SURVIVED, unmutated counter).**
`score()` line 320-321: `ok = outcome in declared and (outcome == rec or 'alt' in tpl)`. For
context-capacity-receipt `alt` is set, so any recorded verdict is accepted. Two runs, both unmutated:
- `unm-ctxtrue-real`: recorded verdict `true` while the live tool refuses on the busy host.
  `… host_busy=1 mismatches=0 … controls_rejected=12/12 errors=0 met=True`.
- `hb-idle-lie` (`reg_ctxidle.tsv`): recorded verdict `host-busy` and observed `"all_ports_closed": true`,
  run on the idle namespace where the tool exits 0. `… host_busy=0 mismatches=0 … controls_rejected=12/12 errors=0 met=True`.

The `observed` field is checked (`mismatch` fires in `iso-ns`), but the verdict column is not. A row can
therefore disagree with the live host and still be credited. The spec's wording ("equals the recorded
verdict or is one of the row's two declared outcomes") allows this, because for this row both outcomes are
declared. That is a gap in what the spec demands, not only in the code.

**H2 — the counter is not re-runnable on the same `--work` (operability; affects calibration).**
Re-running the unchanged iso-real variant on its existing work directory (`runs/iso-real-rerun`) gives:
```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=11/12 dead=0 host_busy=1 mismatches=2 canonical=63 selfdesc_mismatches=0 sens_selftest=4/4 controls_rejected=0/12 errors=0 met=False
```
Cause, probed directly: `kama-ollama-live.py --work <dir> --nonce ctrun0001` returns `"verdict": "FAIL"` when
`<dir>` already exists (from an earlier probe) and `MODEL_OK` on a fresh directory. The bound command
(counter.py:115-116) passes `%S/ollama`, so the row depends on scratch state. The L1 must use a fresh
`--work` for every counter run, or the row must be made idempotent.

**H3 — the lane tool's pgrep probe accepts any live pid (lane tool, not the counter).**
`kama-context-capacity.py:218-238` counts any non-zombie pid returned by `pgrep -x llama-server`, without
checking `comm` or `exe`. The real tool therefore accepts the fake pgrep of section 4 without
complaint. It is a weakness of the tool that the counter inherits.

## 6. Environment notes (not counter defects, recorded for reproducibility)

- A user namespace (`unshare -Urp`) makes `live-receipt-replay` fail one selftest case
  (`code-no-archive-library`, KLR 47/48) and mis-maps the archive's uid. A PID-only namespace through
  `sudo -n unshare -p` with uid 1000 passes 48/48. Only the PID-only namespace is used for evidence.
- `sudo` resets `HOME` to `/root`, which changes `expanduser` in the pinned model path and fails the
  `run:` check for `live-llamacpp-lifecycle`. Fixed by passing `HOME` and `PATH` through `env` after `setpriv`.
- In a probe (`fixtures/probe.py`, output `probe-host.txt` and `probe-nspid.txt`) `live-ollama-lifecycle` fails
  on re-use of the scratch dir (H2). A fresh dir passes; the probe outputs are from the re-run and show this.

## 7. Recommendations (for the L1; not a verdict on the claims)

1. Resolve `pgrep` by absolute path or drop PATH from the allowlist, and cross-check each pid's
   `/proc/<pid>/comm` and `exe` against the pinned llama-server, in both the counter and the tool.
2. For rows with `alt`, require `outcome == rec` (or require the recorded `observed` to match the live
   output for the recorded verdict). A row must not be credited while its verdict disagrees with its own
   observed field.
3. Add control families the current 12 cannot express: (i) pgrep cross-check removed (must be rejected),
   (ii) refusal with a different message (must be rejected), (iii) recorded verdict flipped on the alt row
   (must be rejected). Each should be scored by the same rule as the existing families.
4. Make the `hostbusy` and `verdict` families mutate the row's own content instead of replacing the
   first `\ttrue\t`, so they cannot be no-ops on an all-host-busy registry.
5. Use a fresh `--work` for every counter run, and make the ollama row idempotent.

## 8. Tools and installs

None installed or upgraded. Used existing system tools: `git`, `pgrep`, `unshare`, `setpriv`, and passwordless
`sudo -n` (directive-permitted) for the PID namespace only. No file under `~/.local/bin` or any PATH directory
was touched. The fake `pgrep` lives only in my scratch.

## 9. Tally

Attack (a) KILLED by `hostbusy`; attack (b) SURVIVED; attack (c) SURVIVED; unmutated fake-pgrep forgery
ACCEPTED (met=True, 0 foreign llama-server). All-host-busy registry reaching met=True: 0 of 3 mutants.
Counter-line tally for the C2 mutants (verbatim):
`mb-ns-A: … controls_rejected=12/12 errors=0 met=True`; `mc-real-B: … controls_rejected=12/12 errors=0 met=True`;
`ma-real: … controls_rejected=11/12 errors=0 met=False`.
