# R05C1Exit — Audit of the three C1 receipts: `exit=<rc>` fidelity

Seat: R05C1Exit (leaf; no subagents). Scope: confirm each C1 receipt's `exit=` equals the
actual child command return code. All commands run in scratch `/fast/scratch/hyaku/kama-r56/R05C1Exit/`
(TMPDIR set to its `tmp/`), against byte-identical copies of the lane tools; the lane was never written.

## Identity checks (preconditions)

- Lane HEAD = `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7` (freeze tip). `git status --porcelain`:
  `tools/` and `.ufo/waves/round-56/controls/` clean; `.ufo/waves/round-56/measured/` untracked.
- Frozen counter digest verified: `sha256sum tools/round56-replay-code-audit.py` →
  `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f` = preregistration value.
- Mutant construction reproduced exactly as the battery does: anchor
  `BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES", "LD_AUDIT")` occurs exactly once in the
  round-56 counter; replacement changes exactly one line (unified diff: 1 del + 1 add, no other lines).

## How `exit=` is produced (by construction)

`tools/round56-env-leg-battery.py::run()` (committed, clean at freeze):
`p = subprocess.run(["python3", TEST, "--counter", C, "--expect", E], capture_output=True)`,
then writes `p.stdout + p.stderr + f"exit={p.returncode}\n"`. So `exit=` is `p.returncode` of the
child `round56-env-leg-test.py` process. The driver itself returns `0 if result == expect else 1`.

## Reproduction (same commands as the battery, in scratch)

Driver: `python3 round56-env-leg-test.py --counter <copy> --expect <E>` (cwd=scratch, TMPDIR set):

| leg | counter | `--expect` | observed | child rc |
|---|---|---|---|---|
| base-old-counter | round54-replay-code-audit.py | missed | `ld_audit=missed` | 0 |
| round56-counter | round56-replay-code-audit.py | detected | `ld_audit=detected` (problems `env: server environment carries LD_AUDIT`) | 0 |
| m-drop-ldaudit | 1-line mutant | missed | `ld_audit=missed` | 0 |
| probe: mutant | 1-line mutant | detected | `ld_audit=missed` | **1** |

stderr in every leg: `ERROR: ld.so: object '/usr/lib/libexpat.so.1' cannot be loaded as audit
interface: undefined symbol: la_version; ignored.` (the sleep child's ld.so refusal; harmless).

## Receipt-by-receipt audit

Receipt digests (as found on disk, untracked):
`base-c1.out ece98c2fd69fdd7dab5cc0f05025cf69fc487d589db7120e2c1b6615816a00e8`,
`build-c1.out 1aea0d276711e33190962338192054db3f221a8ae8f42a53217dec578c124991`,
`m-drop-ldaudit.out 93813bd7b61d95c3ff631fb5da073f3f25ce9980678ef1c3cadc6b146e9241c7`,
`controls/base-c1.out 48a6f7457a8d015ed52c0a1f9877fa8548d393b8f87f442f7d4c08687eabacec`.

1. `measured/base-c1.out` — receipt `ld_audit=missed … exit=0`; repro rc=0; **byte-equal after
   `pid=\d+` normalization**. `exit=0` is the actual child rc. PASS.
2. `measured/build-c1.out` — receipt `ld_audit=detected … exit=0`; repro rc=0; byte-equal after
   pid normalization. `exit=0` is the actual child rc. PASS.
3. `measured/m-drop-ldaudit.out` — receipt `ld_audit=missed … exit=0`; repro rc=0 for the command
   the battery actually ran (`--expect missed`); byte-equal after pid normalization. `exit=0` is
   the actual child rc **of that invocation**. PASS as recorded — but see Finding 1.
4. `controls/base-c1.out` — `exit=0` equals the repro rc=0, but line order differs (stderr line
   first) → not written by the battery's `capture_output` path; content-equal otherwise. See Finding 2.

The probe leg demonstrates the receipt format carries genuine failures: mutant + `--expect detected`
→ rc=1, so `exit=` is not a constant and PASS receipts are real matches.

## Findings

**F1 — MEDIUM (evidence gap vs preregistered target, no falsification).**
`preregistration.json` C1 `target` and `controls.C1_kill_battery.mutants` say the mutant "must miss
LD_AUDIT **and fail the battery expected-detected condition**". The committed battery runs the kill
leg as `run("m-drop-ldaudit", mutant, "missed", …)` (`tools/round56-env-leg-battery.py`, main) —
i.e. under the expectation the mutant satisfies — so the battery's `ok` for that leg is True and it
contributes to battery exit 0. **No receipt anywhere records the failing exit (1) that the target
sentence asserts as observable.** The mutant's kill is real (probe: `--expect detected` →
`ld_audit=missed`, rc=1, reproduced in scratch), and the C1 *kill rule* is still satisfied ("the
single-line mutant still detects it" did not happen). But the recorded receipts alone do not
evidence the target's third clause. Proposed fix (advisory, one line): add a leg
`run("m-drop-ldaudit-vs-detected", mutant, "detected", OUT / "m-drop-ldaudit-detected.out")` and
require its rc=1, so the expected-detected failure is itself receipted; keep the roster's
`expected: missed` for the observed outcome. Not changed by this seat (frozen after scoring start).

**F2 — LOW (provenance of `controls/base-c1.out`).**
Battery-written receipts always order stdout before stderr (`p.stdout + p.stderr`); this receipt has
the ld.so ERROR line first → it was captured with combined redirection (e.g. `> f 2>&1`, where the
grandchild's stderr wins the race against the block-buffered stdout). Its `exit=0` still equals the
true child rc (reproduced), so the audit passes; only the capture mode is undocumented. Fix: produce
control receipts via the battery (or document the combined-redirect capture) for uniform ordering.

**F3 — LOW (uncommitted measured receipts).**
The three C1 receipts live only on disk: `git status --porcelain` → `?? .ufo/waves/round-56/measured/`
at the freeze tip; `git show efc6b3ec:.ufo/waves/round-56/measured/base-c1.out` fails ("exists on
disk, but not in …"). A lane clean/checkout loses the C1 evidence. Fix: commit `measured/` (and
record the four digests above in the wave notes), or store receipts under the wave out/ tree that is
collected.

**F4 — INFO (lane-tree side effect, pre-existing).**
`tools/__pycache__/` exists in the lane with 10 `round5*` entries (gitignored): importing the
counters by path (as the battery/driver do) writes bytecode caches into the lane tree. No git-visible
change (status clean; hashes of the four tools match the freeze-tip bytes). This seat ran only scratch
copies; its own pycache stayed in scratch.

## Verdict

All recorded C1 `exit=` values (three battery receipts plus the base control receipt) equal the
actual return codes of the child commands actually executed — confirmed by construction (battery
source) and by reproduction (byte-equal outputs modulo pid, equal rc, plus a demonstrated rc=1 probe).
C1's kill rule holds on the recorded bytes. One evidence gap (F1) and three low/informational items
reported; nothing here falsifies C1.

Evidence copies: `.ufo/waves/round-56/w1/out/R05C1Exit/` (repro receipts `repro-*.out`, including
`repro-mutant-detected.out` with `exit=1`, plus `SHA256S.txt`).
