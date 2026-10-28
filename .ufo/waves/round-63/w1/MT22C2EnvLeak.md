# MT22C2EnvLeak — C2 environment-allowlist mutation probe (round 63)

Seat: MT22C2EnvLeak (mutation-tester, leaf). Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09`.
Scope: attack item only (C2 env allowlist of `tools/round63-c2-counter.py`). No verdict on the claims.
Receipts: `.ufo/waves/round-63/w1/out/MT22C2EnvLeak/` (runs, marks, poison sources, drivers, mutant patch).

## 0. Lane incident (disclosed)

One `_edit` header I wrote used a relative path (`kama-shokunin/tools/...`) that resolved to the **lane**
file, not my clone. It changed lane line 504 of `tools/round63-c2-counter.py` for roughly one minute.
Repair: a second `_edit` restored line 504 to the exact HEAD bytes. Verified after repair:
`sha256(git show HEAD:tools/round63-c2-counter.py) == sha256(working file)`, and
`git diff --stat -- tools/round63-c2-counter.py` is empty. No git command was run against the lane.
The unmutated baseline (`U-clean`) was launched before the mistaken edit, and Python loads the script
at process start, so that run used the original bytes. Lane `git status` now shows only other seats'
paths. All later edits used absolute clone paths.

## 1. Mutant

- Clone: `/fast/scratch/hyaku/kama-r63/w/MT22C2EnvLeak/clone` (`git clone --shared`; top-level asserted).
- Commit `58ba80d086cdb703eeac8c970c9a36c2c1e3c7b9` in the clone only (patch in `out/.../mutant-commit.patch`).
- One line changed, `round63-c2-counter.py:504`:
  - before: `env = {k: v for k, v in os.environ.items() if k in ENV_KEYS}`
  - after:  `env = dict(os.environ)  # MT22C2EnvLeak mutant: no allowlist`
  - `TMPDIR` override kept. The same `env` also goes to `selfdesc_mismatches()` (reconciler).
- Mutant run as `$CLONE/tools/round63-c2-counter.py --repo $CLONE --tip 58ba80d0 --work ...`.
  Unmutated run as `$LANE/tools/round63-c2-counter.py --repo $LANE --tip 03a6a1d8 --work ...`.

## 2. Plants (caller environment; all live, loopback-only tools, no registered port touched)

| plant | caller env additions | what it does |
|---|---|---|
| P1 | `PYTHONPATH=poison/json-shadow`, `HTTP_PROXY=http://127.0.0.1:9`, `LD_PRELOAD=mark.so`, `POISON_MARK=…` | `json.py` on PYTHONPATH logs an import then raises `ImportError`; `mark.so` constructor logs each process |
| P0 | `KAMA_PROBE_LEAK=1`, `LD_PRELOAD=mark.so`, `POISON_MARK=…` | benign: nothing in the lane reads `KAMA_PROBE_LEAK` |
| J | P1 minus HTTP_PROXY | json shadow only (attribution) |
| X | `HTTP_PROXY=http://127.0.0.1:9` + `LD_PRELOAD` only | proxy only (attribution) |
| P2 | `PYTHONPATH=poison/forge` | `sitecustomize.py`: every python start prints the 11 bound patterns and `os._exit(0)` (forgery) |

Host note: `PYTHONUNBUFFERED` and `NO_COLOR` are the only related host vars; no proxy vars are set on the host.
Host llama-servers (ports 1234, 45669, plus other seats' children) make `context-capacity-receipt` host-busy
in some runs. Those are foreign; I did not touch them.

## 3. Real counter output (verbatim lines, `--work` under my scratch)

    U-clean    population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False
    U-P1       (identical to U-clean)
    U-P0       (identical to U-clean)
    U-forge    (identical to U-clean)
    M-clean    (mutant, minimal env PATH/HOME: identical to U-clean)
    M-P0       (mutant, benign plant: identical to U-clean)
    M-P1       population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=3/12 dead=0 host_busy=0 mismatches=17 canonical=63 selfdesc_mismatches=14 sens_selftest=4/4 controls_rejected=0/12 errors=0 met=False
    M-forge    population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=0 mismatches=1 canonical=63 selfdesc_mismatches=10 sens_selftest=4/4 controls_rejected=0/12 errors=0 met=False

Notes on these lines:
- Every line is `met=False`, including the unmutated baseline. That is the freeze's own state at this tip:
  `selfdesc_mismatches=8` is expected until the L1 re-derives SCORECARD after measurement. So `met` alone
  cannot separate mutant from unmutated here.
- `controls_rejected=0/12` on the M-P1 and M-forge lines is "control credit withheld, baseline not met";
  it is not evidence about the controls.
- `host_busy` tracks foreign llama-server state and the row's own crash. M-P1 host_busy=0 comes from the
  context row erroring under the json shadow, not from the host going idle.

## 4. Per-row outcomes (same scorer, driver `driver/rowdiff.py`, every row executed live)

Columns: **A** unmutated + allowlist, clean caller. **B** unmutated + allowlist + P1. **C** mutant (full env) + P1.
**D** mutant + J (json only). **E** mutant + X (proxy only). **F** mutant + P0 (benign). **G** mutant + P2 (forge).
**H** unmutated + allowlist + P2. **I** mutant + P2 with forgery-consistent record (driver-only patch: the
context-capacity record set to `true` / `"all_ports_closed": true`, not committed).

| row | A | B | C | D | E | F | G | H | I |
|---|---|---|---|---|---|---|---|---|---|
| append-only-audit | true | true | **false** | **false** | true | true | true | true | true |
| context-capacity-receipt | host-busy | host-busy | **false** | **false** | host-busy | host-busy | true | host-busy | true |
| digest-ledger | true | true | true | true | true | true | true | true | true |
| gguf-declared-identity-replay | true | true | **false** | **false** | true | true | true | true | true |
| hexrun-census | true | true | true | true | true | true | true | true | true |
| instrument-agreement | true | true | **false** | **false** | true | true | true | true | true |
| live-llamacpp-lifecycle | true | true | **false** | **false** | true | true | true | true | true |
| live-ollama-lifecycle | true | true | **false** | **false** | true | true | true | true | true |
| live-receipt-replay | true | true | **false** | **false** | true | true | true | true | true |
| ollama-offline-evidence-replay | true | true | **false** | **false** | true | true | true | true | true |
| pin-watch | true | true | true | true | true | true | true | true | true |
| sources-registry | true | true | **false** | **false** | true | true | true | true | true |
| **row mismatches (driver)** | 0 | 0 | 17 | 17 | 0 | 0 | 1 | 0 | 0 |
| **sensitive** | 12/12 | 12/12 | 3/12 | 3/12 | 12/12 | 12/12 | 12/12 | 12/12 | 12/12 |

Per-row reading:
- C and D match: the json shadow alone accounts for the 9 changed rows. D-full-json writes 9 json-shadow
  import markers, the same count as the 9 failing rows. That count match is the only attribution I have.
  [INFERENCE: one import per failing row.]
- E (proxy only) and F (benign) change no row. The live tools that touch HTTP use proxy-free openers
  (`kama-llamacpp-live.py:979` `ProxyHandler({})`, `kama-context-capacity.py:99`), and ollama-live uses http.client.
- G: all 12 rows true, sensitivity 12/12. The one mismatch is context-capacity, whose registry record is
  `host-busy` and whose forged output is `true`.
- I (forgery-consistent record): mismatches 0 across all 12 rows. Its unmutated twin, allow-mode with the same
  record and the same forge caller env, gives context-capacity `host-busy` against the recorded `true`,
  mismatches=1. So the row-level check distinguishes forged from genuine only if the record was written
  honestly.

## 5. Findings

1. **The allowlist is load-bearing against variables a bound tool reads.** `PYTHONPATH` alone changes 9/12
   row outcomes and moves every aggregate field that depends on rows (sensitive 3/12, mismatches 17,
   host_busy 0, selfdesc 14). The unmutated counter is unaffected by the same caller env (U-P1, U-P0, U-forge
   all identical to U-clean). The allowlist works as written.

2. **The allowlist is decorative against benign or unread variables, and no control sees it.** Under the
   benign plant P0 the mutant's printed line is byte-identical to the unmutated line. The counter has no
   field that can tell the two apart at this tip. The 12 control families and the 4-plant sensitivity
   self-test all operate on registries and verdict text, never on the environment, so the predicate clause
   "executed in an allowlisted environment (PATH, HOME, LANG, LC_ALL, TMPDIR only)" is enforced by nothing
   but the one line itself.

3. **A caller environment can forge a bound row's verdict, and the sensitivity test does not notice.** Under
   P2 the mutant turns all 12 rows true with sensitivity 12/12. The verdict function and the flip test see
   only output text and exit code, not provenance. Detection is therefore only the recorded-versus-observed
   mismatch: with an honest record it fires (G: mismatches=1, row context-capacity); with a record written to
   match the forgery it does not (I: mismatches=0). The aggregate moves under G only as a side effect
   (mismatches 1, host_busy 0, selfdesc 10).

4. **Side channel the allowlist does not cover: the lane's own reconciler inherits the full environment.**
   `tools/round42-selfdesc-reconcile.py` runs the r41 check commands (`bash tools/test-snapshot.sh`,
   `python3 tools/instrument-agreement.py --selftest`, and others) through `subprocess.run` with inherited
   env. Run directly, its count moves: clean `mismatches=8`, under P2 `mismatches=10`, under P1 `mismatches=14`.
   The counter passes its allowlisted env to the reconciler, so the unmutated path is protected. The
   reconciler itself is not hardened.

5. **Not tested.** `git()` in the counter strips only `GIT_*` from the full environment, and I did not probe
   git-level poison. `HTTP_PROXY` against a tool that does use default `urllib` was not isolated beyond the
   run in E. `kama-live-replay.py` was not separately inspected; it is true under E, so the proxy plant had
   no visible effect on it.

## 6. Mutation tally (recipe rule)

| mutant | pair result | verdict |
|---|---|---|
| M-P1 (json + proxy + LD_PRELOAD) | differs: sensitive 3/12, mismatches 17, host_busy 0, selfdesc 14 | KILLED, but by row side effects; no control rejected it (credit withheld) |
| M-P0 (benign plant) | identical line; both `met=False` | **SURVIVED** (defect present, no field moves). The recipe's literal "prints met=False" would count this as killed; that kill is spurious, because `met=False` comes from selfdesc=8. |
| M-forge (P2, honest record) | differs: mismatches 1, host_busy 0, selfdesc 10 | KILLED only as a side effect (one row mismatch) |
| M-forge (P2, forgery-consistent record; driver I) | row mismatches 0 | **SURVIVED** at row level |
| M-proxy (X, driver E) | rows identical to A | **SURVIVED** (real counter aggregate not run for this plant) |
| M-clean (PATH/HOME only) | identical to U-clean | control run; not a leak test |

**Defect of the counter/control set, for the L1 (advisory, not a verdict):** no control family or
self-test plants an environment variable or inspects the environment the rows receive. Either M-P0 or
M-forge-consistent survives the frozen suite. A candidate fix is a 13th family that plants a sentinel
variable in the caller env and requires the row environment, the reconciler environment, or both to lack
it (or asserts the built env keys are a subset of ENV_KEYS + TMPDIR). Adding a family changes
`EXPECT_FAMILIES`; that decision belongs to the L1.

## 7. Tools, installs, cleanup

- Installs: none. Used the existing `/usr/bin/gcc` to build the planted `mark.so`, and existing python3 3.14.8.
  Nothing written to `~/.local/bin` or any PATH directory. No pacman.
- Live processes: the counters and their live rows launched unregistered-port children only. I killed nothing;
  I did not touch foreign llama-servers.
- Scratch: `/fast/scratch/hyaku/kama-r63/w/MT22C2EnvLeak` removed after receipts were copied.

Tally line (baseline counter at tip, the value the mutants are compared against):

    population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False
