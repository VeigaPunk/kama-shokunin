VERDICT: partial — neither counting command reads a file the other claim owns, but separability depends on unowned shared inputs staying byte-identical, on serial runs, and on C2's guard certifying C1's SOURCES rows.

Seat: KamaR18.RevSeparability-2 (reviewer, read-only). Lane tip `git rev-parse master` = `e75cf680b53484a61709ee1b2787d8dbc6419f74` (B below). At review time `git status --porcelain` showed no changes under `tools tests registry corpus SKILL.md`.

## Scope and method

- **Read:**
  - lane-tip code (the same bytes as the frozen copies);
  - the build spec items `C1LiveTool`, `C1Gate`, `C1Controls`, `C1Measure`, `C2FaultControls`, `C2CheckPyRobust`, `C2Survivors`, `C2AppendOnly` and `C2Provenance` in `.ufo/waves/round-18/build/spec.json`;
  - the four deliveries in `build/out/` (`KamaR18.C1LiveTool-2`, `C1Gate-2`, `KamaR18.C2CheckPyRobust-2`, `C2Provenance-2`);
  - the in-progress C1Measure draft at `/tmp/kama-r18-C1Measure/.ufo/waves/round-18/c1/measure.py` (a seat clone, not yet delivered);
  - `build/drafts/skill-round18.md` and `build/drafts/sources-kernel.md`.
- **Not yet delivered, so judged from the spec only:**
  - `c2/survivors.py`;
  - the final `controls.py`, `fault-controls.py` and `sources-append-only.py`.
- **No LSP device in this seat.** Every cross-reference below comes from a literal grep or a code read. It is necessary but not sufficient, and it is not semantic proof.
- **Nothing was run.** Measurements belong to L1. No scratch files were created, and nothing was installed.

## 1. File sets and shared dependencies

The declared file sets do not intersect:

- **C1 owns:**
  - `tools/kama-llamacpp-live.py`
  - `tests/llamacpp-live/check-receipt.py`
  - `tests/llamacpp-live/controls.py`
  - `.ufo/waves/round-18/c1/*` (measure.py)
- **C2 owns:**
  - `tests/probe-verdicts/check.py`
  - `tests/probe-verdicts/fault-controls.py`
  - `tools/sources-append-only.py`
  - `.ufo/waves/round-18/dispatch-provenance.py`
  - `.ufo/waves/round-18/c2/*` (survivors.py)

Inputs that neither claim owns:

| Input | Read by C1 | Read by C2 | Pin at B (computed by this seat) |
|---|---|---|---|
| `tools/kama-probe.sh` | The tool, `tools/kama-llamacpp-live.py:54` `DEFAULT_PROBE = LANE / 'tools' / 'kama-probe.sh'`. Also `controls.py:84` and the measure draft's `:34` "the same probe serves both sides." | `check.py:49` `DEFAULT_PROBE = LANE / "tools" / "kama-probe.sh"`; `fault-controls.py:64` | sha256 `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3` |
| `registry/endpoint-consumers.tsv` | The tool at `tools/kama-llamacpp-live.py:53`. Controls stages it at `controls.py:386-387`: "if REGISTRY_SRC.is_file(): shutil.copyfile(REGISTRY_SRC, registry_dir / 'endpoint-consumers.tsv')" | Not read. In port mode the probe never reads the registry: `tools/kama-probe.sh:841` `if [ -n "$OPT_PORT" ]; then`, and `read_registry` sits only in the `else` branch at `:857`. | sha256 `bf343625188d9f486a6f6d13c60c946e23c21d05ee1bef881204dfa14c62bc6c` |
| `tests/probe-verdicts/*.json` (9 files) | Not read (no reference in any C1 file) | Loaded at `check.py:152-154` `def load_matrix(directory=CHECK_DIR)`. `fault-controls.py:621` takes `--matrix-dir`. `:71-72` pins the round-16 digest. | set digest `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32` (round-16 formula; equals `round-17-verifier-spotcheck.md:79`) |
| `.ufo/waves/round-18/frozen/` | frozen tool and gate (the "before" side) | frozen check, fault-controls, append-only and provenance | `SHA256SUMS`, but **untracked** (F-2) |
| Round-17 history: falsify advice, `round-17/build/refused-result-1.json`, `attempts.json` | advice only | survivors families (a)–(d), per the `C2Survivors` spec | committed and immutable |
| `corpus/SOURCES.md` | the C1 "Sourced" rows (draft S048–S050) | only as the guard's real-input subject, through `git show`. Survivors family (c) uses the in-memory selftest. | 47 rows |
| SKILL.md, SCORECARD, lesson, QUALITY.md | docs | docs | read by neither counting command (grep of all owned files: no hit) |
| Host: Python 3.14.8, loopback ephemeral ports, CPU | yes | yes | not pinned (F-1) |

**Helper modules:** no Python helper module is shared across claims. The harnesses call the shared probe; its header says `tools/kama-probe.sh:25-26` “Deps: python3 stdlib only, plus whatever the probed server and `bash tools/kama-probe.sh` (curl, ss) need.”

- Controls' K6 imports only the staged tool (`controls.py:268` `spec_from_file_location('kama_live_under_test', tool)`, launched with `-B` at `:503`).
- Fault-controls runs check.py as a subprocess (`fault-controls.py:351`).

**Literal cross-reference sweep** (owned files at the lane tip, plus every delivery and the measure draft):

- No C1 file names `probe-verdicts`, `fault-controls`, `sources-append`, `dispatch-provenance` or `round-18/c2`.
- No C2 file names `llamacpp-live`, `check-receipt`, `controls.py` or `round-18/c1`. The C2 files here are the lane-tip files, delivered check.py and delivered provenance.
- Every seat clone holding a working-tree change touches only its own claim's file. For example, `/tmp/kama-r18-C2AppendOnly-2` shows ` M tools/sources-append-only.py`. None touches the probe, the registry or the matrix.

## 2. Can a counting command change if only the other claim lands?

- **C1 `measure.py`: not through files.**
  - Its spec inputs are `--controls`, `--frozen-tool`, `--frozen-gate`, `--tool`, `--gate` and `--probe`.
  - The draft hashes exactly measure, controls, the frozen tool and gate, the tool, the gate and the probe (draft `:722-728`), plus the registry (`:670-674` `doc['inputs']['registry'] = file_record('registry', reg)`).
  - None of these is a C2 file.
- **C2 `survivors.py`: not through files, by spec.** Its inputs are C2 files, frozen C2 copies, the matrix, the probe, and round-17 history that cannot change.
  - Family (c) cannot be moved by C1's SOURCES rows. Its detector is `--selftest`, and `tools/sources-append-only.py:33-34` says it runs "on in-memory tables only; it never runs git and is fixture self-consistency, never corpus evidence."
  - Family (d) reads the round-17 refused-attempt files. It uses `--attempt-result`/`--label` mode, which does not run `node`: the delivered provenance takes `--attempt-result` at `:960` and calls the wave script at `:632` only for `--spec`.
- **Yes, through the runtime environment, when both run at the same time** (F-1).
- **Yes, for verifying C1's Sourced sub-claim** (F-3). This does not affect `measure.py`.

## 3. Findings (by severity)

### Medium

**F-1 — Both counts can move when the commands run at the same time, through shared ports, CPU and timeouts.**

- Both harnesses release a loopback port and assume it stays free:
  - `tools/kama-llamacpp-live.py:284-285`: "Default: bind 127.0.0.1:0, take the offered port, release; retry when refused. The release/rebind race is documented in the receipt."
  - `tests/probe-verdicts/check.py:262-263`: `def bind_closed_port(): """Bind then release a loopback port; the probe must see refusal."""`
  - So a check.py stub can take the tool's port, and a fake or llama-server can take check.py's "closed" port.
- A timeout can turn into a kill:
  - `fault-controls.py:348-350`: "killed wholesale after CHECK_RUN_TIMEOUT and reported with rc=124 so it classifies as accepted, never an own fault."
  - The `C2Survivors` spec scores "killed iff accepted>0 or exit!=0".
  - So a mutant run slowed by load past the 150 s cap (`fault-controls.py:69`) scores as a kill. This is a false kill. [INFERENCE: the mechanism is in the code; its frequency is unmeasured.]
- Precedent: `round-17-verifier-spotcheck.md:18-19` records "the 1/60 false failure under 32x CPU load observed **zero** 503s".
- Host now: `/proc/loadavg` read `144.32 114.28 62.02` with `nproc` 32 at 2026-10-20T18:19:45-03:00. There were 21 TCP listeners, so seat scratch numbers taken now ran under contention.
- `round-18/frozen/round-17_c1_mutants.py:105` has `MAX_WORKERS = 6` (a thread pool at `:1001-1002`). [INFERENCE] If survivors.py copies that pattern, it loads the host by itself.
- **Fix:** see §4 step 2. Run serially on an idle host, repeat the both-landed run, and record `loadavg` and the listener count per run.

**F-2 — Separability holds only if the unowned inputs stay byte-identical. Not every instrument records them, and the baseline directory is untracked.**

- Round 17 stated the condition: `round-17.md:48-50` "C1 never touches the live tool, its gate or the probe; C2 never touches check.py or the matrix; `tools/kama-probe.sh` is byte-identical".
- Round 18 adds two more inputs to that condition: the registry (C1) and the matrix (C2).
- Controls' own JSON records only `'tool_sha256': sha256_text(args.tool), 'gate_sha256': sha256_text(args.gate),` (`tests/llamacpp-live/controls.py:649-650`). It records no probe or registry digest, which `CritCountingCommands.md:36` also notes.
- The measure draft does record the probe and registry. The `C2Survivors` spec says only "record sha256 of every input". Whether that covers the matrix and the probe is unverified.
- `git ls-files --error-unmatch .ufo/waves/round-18/frozen/SHA256SUMS` returns "did not match any file(s) known to git". A clone-based revert test therefore has no "before" baseline unless L1 commits or copies `frozen/`.
- **Fix:** §4 step 0, preconditions with the pins from §1.

**F-3 — C1's Sourced rows are certified by a C2 instrument that is changing semantics.**

- C1 is "operability (sourced)". Its new rows are drafted as `build/drafts/sources-kernel.md:7` "## Registry rows (append after S047)", with S048–S050 at `:11-13`.
- L1 certifies the append with `tools/sources-append-only.py`, which "Reads both blobs with `git -C REPO show REV:PATH`" (`:10`). That file is C2's.
- The `C2AppendOnly` spec changes real-input behaviour, not only the selftests: "a row lost by parsing must be reported, never silently ignored."
  - Today the guard skips non-row lines (`:120-121` `if not ROW_RE.match(line): continue`).
  - It also tolerates non-id pipe lines (`:145-146` "non-id pipe lines inside the registry section are not rows; tolerate them").
- So the verdict on C1's rows can depend on whether C2 has landed. If C1's rows are well formed, both guards agree. A malformed row would pass the frozen guard silently and fail the new one.
- The frontier's "new SOURCES rows S048+" draw on the same S-row ID range as C1's Sourced rows.
- **Fix:**
  - Certify with both guards (§4 step 4).
  - State in the lesson which S-rows are C1 evidence and which are frontier-only.
  - The `used-by` cell is mutable (`sources-append-only.py:43`), so it can name the tool each row supports.

**F-4 — The SKILL draft contradicts the declared split, and lane SKILL rows already use C1/C2 with the opposite meaning.**

- `build/drafts/skill-round18.md:3` reads "(C1: live lifecycle tool and receipt gate; C2: probe, fault, source and provenance detectors)". It omits controls.py from C1, and its "probe" is ambiguous with the unowned `tools/kama-probe.sh`.
- Row `:24` reads "| C2 live controls v3 | measurement: `python3 tests/llamacpp-live/controls.py". The context assigns controls.py to C1.
- The same section names `:25` "C1 counting command v3", `:27` "C2 fault controls" and `:28` "C2 mutant survivors". The label "C2" therefore covers controls.py and survivors.py at once.
- Lane `SKILL.md:571` "| C1 fault controls |" and `:575` "| C2 live controls |" use round-17 numbering, which is the reverse of round 18's.
- An outside closure that reverts "C2" by reading SKILL would revert controls.py along with C2.
- **Fix:**
  - Drop claim numbers from SKILL row names, or relabel `:24` as C1.
  - Make `:3` read "C1: live tool, receipt gate, live controls; C2: probe-verdict harness, fault controls, SOURCES guard, provenance".

### Low

**F-5 — R7 credit is split across the claims and needs a per-claim ledger.**

- The context gives C1 "the controls.py part of R7" and C2 "Routed R7 (detectors of detectors)".
- The `C1Measure` spec's `--self-mutants` mode covers "drop the gate-flip arm, loosen K0's exit predicate, accept any nonzero for K6".
- The survivors families (a)–(e) do not include controls.py. That is correct.
- `CritC2AxisFit.md:119-120` adds: "[INFERENCE] The `controls.py` self-check arms routed to C1 (`MutControlsSelf`) are likewise instrument-on-instrument evidence — calibration-shaped inside an operability claim."
- **Fix:**
  - The lesson gets one R7 row per sub-item, naming the counting command that settles it.
  - Neither claim cites the other claim's kills.
  - The seven dead round-17 falsify seats (`round-17-verifier-spotcheck.md:255-258`) belong to neither claim.

**F-6 — Frozen copies resolve the lane from their own path, so both "before" columns depend on how inputs are staged.**

- The tool computes `LANE = SCRIPT.parent.parent` (`tools/kama-llamacpp-live.py:52`). From `frozen/` that resolves to `.ufo/waves/round-18`.
  - Controls neutralises this: it stages under `wd/lane/tools` and copies the registry (`controls.py:378-387`).
- Check.py loads from `load_matrix(directory=CHECK_DIR)` (`check.py:152`), and fault-controls sets `MATRIX_DIR = SELF.parent` (`fault-controls.py:61`).
  - Frozen C2 copies run in place therefore find no matrix files.
  - Survivors must pass `--matrix-dir` and `--probe` (`fault-controls.py:618-621`) from the same bytes as the current side.
- Survivors' "lane defaults" resolve to its own clone. Run against another tree without explicit `--check`, `--fault-controls`, `--append-only` and `--provenance`, it silently measures its own tree. [INFERENCE from the spec; not delivered.]
- `frozen/__pycache__/tools_kama-llamacpp-live.cpython-314.pyc` (16:56) is newer than `SHA256SUMS` (16:46). K6 uses `-B` (`controls.py:503`), so something else imported the frozen tool in place [INFERENCE]. The sums still verify. Run with `PYTHONDONTWRITEBYTECODE=1`.


## 4. Revert test L1 must run

This is a 2×2 over {C1 at B, C1 at I} × {C2 at B, C2 at I}, for each counting command. It is stronger than "each claim with the other reverted": it also proves each count moves with its own claim.

```bash
L=/home/vgpnk/Projects/shokunin/kama-shokunin
B=e75cf680b53484a61709ee1b2787d8dbc6419f74
I=<L1 integration commit>
F1='tools/kama-llamacpp-live.py tests/llamacpp-live/check-receipt.py tests/llamacpp-live/controls.py'
F2='tests/probe-verdicts/check.py tests/probe-verdicts/fault-controls.py tools/sources-append-only.py'
R=/tmp/kama-r18-L1-revert
FZ=$L/.ufo/waves/round-18/frozen
export PYTHONDONTWRITEBYTECODE=1

# 0. Preconditions (any failure: stop; separability unproven)
git -C $L diff --name-only $B $I   # each code path in F1+c1/ OR F2+dispatch-provenance.py+c2/, never both
git -C $L diff --quiet $B $I -- tools/kama-probe.sh registry/endpoint-consumers.tsv 'tests/probe-verdicts/*.json'
(cd $FZ && sha256sum -c --quiet SHA256SUMS)
# Pins expected at I: probe 36b64978…, registry bf343625…, matrix set (round-16 formula) bf9068d8…

# 1. Four trees (git writes only inside /tmp clones)
for x in X0 X1 X2 X12; do
  git clone -q $L $R/$x && git -C $R/$x checkout -q --detach $I
done
git -C $R/X1 checkout -q $B -- $F2
rm -rf $R/X1/.ufo/waves/round-18/c2 $R/X1/.ufo/waves/round-18/dispatch-provenance.py
git -C $R/X2 checkout -q $B -- $F1
rm -rf $R/X2/.ufo/waves/round-18/c1
git -C $R/X0 checkout -q $B -- $F1 $F2
rm -rf $R/X0/.ufo/waves/round-18/{c1,c2,dispatch-provenance.py}
M=$R/X12/.ufo/waves/round-18/c1/measure.py     # instrument from I
S=$R/X12/.ufo/waves/round-18/c2/survivors.py   # instrument from I
# subjects come from tree $t, always passed explicitly (F-6)

# 2. Serial runs only. Before each run, record `cat /proc/loadavg` and `ss -ltnH | wc -l`.
#    Require 1-minute load below nproc/4 and no other seat running.
#    Order: measure X12, X12 (again), X1, X0, X2; then survivors X12, X12, X2, X0, X1.
m() { t=$R/$1; python3 $M --controls $t/tests/llamacpp-live/controls.py \
      --frozen-tool $FZ/tools_kama-llamacpp-live.py --frozen-gate $FZ/tests_llamacpp-live_check-receipt.py \
      --tool $t/tools/kama-llamacpp-live.py --gate $t/tests/llamacpp-live/check-receipt.py \
      --probe $t/tools/kama-probe.sh --json --out $R/m-$1-$2.json; echo "m $1 $2 exit=$?"; }
s() { t=$R/$1; p=$t/.ufo/waves/round-18/dispatch-provenance.py
      [ -f "$p" ] || p=$t/.ufo/waves/round-17/dispatch-provenance.py
      python3 $S --json --out $R/s-$1-$2.json --check $t/tests/probe-verdicts/check.py \
      --fault-controls $t/tests/probe-verdicts/fault-controls.py \
      --append-only $t/tools/sources-append-only.py --provenance "$p"; echo "s $1 $2 exit=$?"; }

# 3. Hidden-read check: one extra, uncounted run of each under strace (installed at /usr/bin/strace)
strace -f -qq -e trace=openat,execve -o $R/m.trace <same command line as m X12>
strace -f -qq -e trace=openat,execve -o $R/s.trace <same command line as s X12>
grep -E 'probe-verdicts/(check|fault-controls)\.py|sources-append-only|dispatch-provenance|round-18/c2|tests_probe-verdicts|round-17_dispatch' $R/m.trace   # must be empty
grep -E 'llamacpp-live|kama-llamacpp|round-18/c1' $R/s.trace                                                           # must be empty

# 4. No-harm arms
#   X1 (C1 alone): run the gate on round-16 receipt.json and receipt-frozen-probe.json, and on
#     round-17 receipt-{1,2,3}.json, with the same pins; the exit and verdict lines must equal
#     the frozen gate's. Then run the tool, gate and controls --selftest.
#   X2 (C2 alone): check.py --selftest; check.py --json 72/72 against tools/kama-probe.sh;
#     .ufo/waves/round-16/measure.py PASS (it runs tests/probe-verdicts/check.py, measure.py:11,42);
#     fault-controls, append-only and provenance --selftest; append-only --from B --to B exit 0
#     and --from b8e485c --to ccc4bb3 exit 1 on S041.
#   All four trees: `bash tools/test-snapshot.sh` gives an identical RESULT line (probe and registry only).
#   I only: round-13 gate after commit (exit 4 means the worktree is ahead). Then both guards
#     on the SOURCES diff (F-3); each must exit 0 with the same added-id list:
python3 $FZ/tools_sources-append-only.py --repo $L --from $B --to $I
python3 $R/X12/tools/sources-append-only.py --repo $L --from $B --to $I
```

**Comparison.** Use `canon` = JSON with a volatile-key list **fixed before the first run** and written into the lesson. The list covers timestamps, seconds and durations, ports, pids, argv, and `/tmp`/clone paths. Keep every `sha256`, count, classification, failed-check list, kill status, `site_missing`, the refused count and every exit code.

```bash
canon() { python3 -c 'import json,sys;V=set(sys.argv[2].split(","));f=lambda o:{k:f(v) for k,v in sorted(o.items()) if k not in V} if isinstance(o,dict) else [f(x) for x in o] if isinstance(o,list) else o;print(json.dumps(f(json.load(open(sys.argv[1]))),sort_keys=True))' "$1" "$VOLATILE"; }
```

**Pass criteria (all required):**

- **P1:** canon(m-X1) = canon(m-X12), with equal exits. C2 landing does not move C1's count.
- **P2:** canon(s-X2) = canon(s-X12), with equal exits. C1 landing does not move C2's count.
- **P3:** canon(m-X0) = canon(m-X2), and canon(s-X0) = canon(s-X1). This closes the 2×2.
- **P4** (the test can fail):
  - m-X0 differs from m-X12 in at least one of accepted_bad, good_rejected, misclassified or uncontrolled_checks.
  - m-X0 has `identical_pairs` true (draft `:740-743`), with before = after.
  - s-X0 differs from s-X12 in at least one survivor status.
  - If P4 fails, P1–P3 pass vacuously.
- **P5:** the two X12 runs agree. Any field that differs between them is flaky; report it as inconclusive and do not count it toward P1 or P2.
- **P6:** both strace greps are empty.
- **P7:**
  - The `inputs` recorded by measure contain no C2 path, and those recorded by survivors contain no C1 path.
  - The recorded probe, registry and matrix digests equal the pins from §1.
  - If survivors records no matrix or probe digest, step 0 is the only proof.

**If P1 or P2 fails:** the differing field names the channel. Do not average and do not re-run until it is green. Either find the shared input (F-1/F-2), or admit the two claims as one causal change.

## 5. Residual risk and verification gaps

- **Undelivered pieces.** `survivors.py` is not delivered, and `measure.py` is an unfinished draft. The final `controls.py`, `fault-controls.py` and `sources-append-only.py` are pending. Statements about them come from the spec. [INFERENCE]
- **Runs.** No counting command was run and no strace trace exists. §4 is a design for L1, not evidence.
- **Coverage of round-17 `SeparabilityNoHarm`:**
  - covered here: the revert test, probe identity, and the round-16 and round-13 gates as arms;
  - not covered: axis-harm rulings for freshness, depth, coverage and adjacency.
- **Saturation.** "0 uncontrolled checks" and "every named survivor killed" are counts over finite named lists. They are not completeness claims.

Installs: none. Scratch: none.
