# X10Probe — round-55 probe regression at the freeze commit 9c60eae6f7ed84f7da93d219a406aadc30958c6c

**Verdict: PASS on the probe regression itself (`check` exit 2, `consumers` exit 0, the three DEAD rows, byte-identical to base) — but the item's own stated check command is unsatisfiable as literally written: `git diff BASE FREEZE --stat -- tools/kama-probe.sh registry/` is NOT empty, because C2's `superseded` row lands in `registry/cited-path-corrections.tsv`; the probe-relevant registry surfaces (`tools/kama-probe.sh`, `registry/endpoint-consumers.tsv`, `registry/history/`) ARE unchanged. One spec-text defect, proposed fix in the out dir.**

Axis: operability. Seat: X10Probe (executor). Lane commit under test: `9c60eae6f7ed84f7da93d219a406aadc30958c6c` (round-55 w0 freeze). Base: `3a600d2f729828419aaea34cc402c8b0d20fb720` (round-54 tip).

## 1. The probe regression — PASS

### 1.1 In the lane worktree (read-only run)

```
$ cd /home/vgpnk/Projects/shokunin/kama-shokunin
$ bash tools/kama-probe.sh check        # EXIT=2
$ bash tools/kama-probe.sh consumers    # EXIT=0
```

`check` output (verbatim, saved as `out/X10Probe/probe-check.out`):

```
id                    | consumer                              | declared                                   | verdict | reason             | served_model | evidence
omp-llama-cpp-default | ~/.local/bin/omp                      | http://127.0.0.1:8080                      | DEAD    | connection-refused | -            | file=inherited via raw @8080; rc=7 Failed to connect to 127.0.0.1:8080 after 0 ms: Could not connect to server; GET /v1/models -> 000
ufo-fsd-thetick        | $UFO_SRC/config/the-tick.machine.json | http://127.0.0.1:34113/v1/chat/completions | DEAD    | connection-refused | -            | file=yes via url @34113; rc=7 Failed to connect to 127.0.0.1:34113 after 0 ms: Could not connect to server; GET /v1/models -> 000
ufo-fsd-local-helper  | $UFO_SRC/scripts/local-helper.mjs     | http://127.0.0.1:34113                     | DEAD    | connection-refused | -            | file=yes via url @34113; rc=7 Failed to connect to 127.0.0.1:34113 after 0 ms: Could not connect to server; GET /v1/models -> 000
registry_rows_evaluated=3 model_ok=0 drift=3 exit=2
```

`consumers` output (verbatim, saved as `out/X10Probe/probe-consumers.out`):

```
id                    | consumer                              | declared                                   | resolved_from_file                         | file_match | resolver_kind | endpoint                                   | port  | verdict | served_model
omp-llama-cpp-default | ~/.local/bin/omp                      | http://127.0.0.1:8080                      | LLAMA_CPP_BASE_URL                         | inherited  | raw           | http://127.0.0.1:8080                      | 8080  | DEAD    | -
ufo-fsd-thetick        | $UFO_SRC/config/the-tick.machine.json | http://127.0.0.1:34113/v1/chat/completions | http://127.0.0.1:34113/v1/chat/completions | yes        | url           | http://127.0.0.1:34113/v1/chat/completions | 34113 | DEAD    | -
ufo-fsd-local-helper  | $UFO_SRC/scripts/local-helper.mjs     | http://127.0.0.1:34113                     | http://127.0.0.1:34113                     | yes        | url           | http://127.0.0.1:34113                     | 34113 | DEAD    | -
consumer_rows_evaluated=3 exit=0
```

Expected by the item: exit 2 for `check`, exit 0 for `consumers`, three DEAD rows — **both observed, exactly**. Exit codes match the probe's documented contract (`tools/kama-probe.sh:42-43`: "0 every declared consumer reconciles | 2 at least one drift | 1 probe error").

### 1.2 At the freeze commit itself (own shared clone — the lane worktree HEAD is the later build commit `8abadfedf89f35372645b1e5d6ce4a2109186f90`)

```
$ S=/fast/scratch/hyaku/kama-r55/w1/X10Probe; export TMPDIR="$S"
$ git clone --shared -q /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
$ git -C "$S/lane" rev-parse --show-toplevel   # -> /fast/scratch/hyaku/kama-r55/w1/X10Probe/lane
$ git -C "$S/lane" checkout -q 9c60eae6f7ed84f7da93d219a406aadc30958c6c
$ (cd "$S/lane" && bash tools/kama-probe.sh check)      # CHECK_EXIT=2
$ (cd "$S/lane" && bash tools/kama-probe.sh consumers)  # CONSUMERS_EXIT=0
```

Both clone outputs are **byte-identical** to the lane-worktree run:

```
$ diff out/X10Probe/probe-check.out      out/X10Probe/clone-check.out       # IDENTICAL
$ diff out/X10Probe/probe-consumers.out  out/X10Probe/clone-consumers.out   # IDENTICAL
sha256  fbf8e7b9eb328cca0c6c104cb35fa4adaed261238366991b0f8d625b14ff6c86  probe-check.out
sha256  cc8b8aa8ece9b414d4d801310a6dca480c92e881fe5b41fb409d872acf8137b0  probe-consumers.out
```

### 1.3 Base-vs-freeze equality — the freeze changed probe behaviour by zero

Ran the same two subcommands in the same clone at the base tip:

```
$ git -C "$S/lane" checkout -q 3a600d2f729828419aaea34cc402c8b0d20fb720
$ (cd "$S/lane" && bash tools/kama-probe.sh check)      # BASE_CHECK_EXIT=2
$ (cd "$S/lane" && bash tools/kama-probe.sh consumers)  # BASE_CONSUMERS_EXIT=0
$ diff "$S/base-check.out"      "$S/clone-check.out"      # IDENTICAL
$ diff "$S/base-consumers.out"  "$S/clone-consumers.out"  # IDENTICAL
```

Same sha256 as the freeze run for both files (`fbf8e7b9…`, `cc8b8aa8…`). The freeze commit does not move the probe one byte of behaviour.

### 1.4 The three DEAD rows are the standing baseline, not new drift

`registry/history/latest.tsv` (committed baseline, snapshot `20261014T124232Z`) vs the live run:

| id | live verdict/reason | baseline verdict/reason | match | baseline file_match |
|---|---|---|---|---|
| omp-llama-cpp-default | DEAD / connection-refused | DEAD / connection-refused | yes | inherited |
| ufo-fsd-thetick | DEAD / connection-refused | DEAD / connection-refused | yes | yes |
| ufo-fsd-local-helper | DEAD / connection-refused | DEAD / connection-refused | yes | yes |

Cause is environmental, not code: `ss -ltn 'sport = :8080 or sport = :34113'` returns **no rows** (neither registered port has a listener), and the evidence column shows `rc=7 … Could not connect to server`. The hosts that *do* serve models are on other loopback ports (`listeners` output: 8787/8788/8789/8791/8793/8795/8796 = `MODEL_OK`, 7 model endpoints) — none of them is a registered consumer.

### 1.5 Extra probes beyond the item (all green)

* `bash tools/kama-probe.sh listeners` — EXIT=0, 19 listeners probed, `model_endpoints=7 foreign_service=8 unauthorized_service=1 dead=2 not_http=1 model_loading=0`. Saved `out/X10Probe/probe-listeners.out`.
* `bash tools/kama-probe.sh snapshot --history <clone>/registry/history` — EXIT=2, `rows=3 model_ok=0 drift=3 transitions=0`, and the **regenerated `latest.tsv` is byte-identical to the committed one** (`sha256 f9f8f3b5bb1bfa61e6737a7fe95f7d7e0d0b53e287eb9c7fbe25d6cd0b7c2a2e` in both the clone and the lane). `DELTA.md` recorded **zero transitions**. Saved `out/X10Probe/probe-snapshot-clone.out`.
* `python3 tests/probe-verdicts/check.py` (the verdict-matrix harness, run in the clone at the freeze commit) — **EXIT=0, `tests=72 passes=72 failures=0`**. Saved `out/X10Probe/probe-verdicts-matrix.out`.
* Determinism: a second consecutive `check`/`consumers` pair in the clone produced identical bytes (`diff` clean).
* Read-only proof: after all runs, `git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain -- registry/ tools/ tests/` is **empty** — the probe wrote nothing into the lane (`registry/history/` still holds only the two committed dated JSONs, `DELTA.md`, `latest.tsv`, `.gitignore`, `.lock`). The clone's snapshot artifacts (`20261027T135830Z.json`, `.lock`) are gitignored by `registry/history/.gitignore`.

## 2. The freeze-commit diff over `registry/` — the item's check command is wrong as written

The item asks to "confirm the freeze commit changed nothing in the probe/registry surfaces (`git diff {BASE} {FREEZE} --stat -- tools/kama-probe.sh registry/` should be empty)".

```
$ git diff 3a600d2f729828419aaea34cc402c8b0d20fb720 9c60eae6f7ed84f7da93d219a406aadc30958c6c \
      --stat -- tools/kama-probe.sh registry/
 registry/cited-path-corrections.tsv | 6 ++++++
 1 file changed, 6 insertions(+)
```

**Not empty** (saved `out/X10Probe/freeze-diff-registry-stat.out`). The 6 added lines are the comment block plus the `superseded` row that the C2 claim lands in the correction ledger — `registry/cited-path-corrections.tsv:41-46`:

```
# Round-55 row: the round-54 re-anchor moved the calibration row's "latest outside
# closure" pointer from the round-52 spotcheck to the round-53 spotcheck ...
SCORECARD.md	corpus/lessons/round-52-verifier-spotcheck.md	superseded	corpus/lessons/round-53-verifier-spotcheck.md	the round-54 re-anchor's closure pointer; the replacement is cited in SCORECARD.md at tip and resolves
```

This is **not** a probe surface and **not** a regression:
* `tools/kama-probe.sh` reads exactly two registry paths — `REGISTRY_DEFAULT="$REPO_ROOT/registry/endpoint-consumers.tsv"` (`tools/kama-probe.sh:68`) and `OPT_HISTORY="$REPO_ROOT/registry/history"` (`tools/kama-probe.sh:77`). `registry/cited-path-corrections.tsv` is never read by the probe (grep over `tools/kama-probe.sh` for `registry/` yields only lines 49, 68, 77, 110, 111).
* The changed file is a **C2 surface**, named as such in the frozen preregistration (`.ufo/waves/round-55/preregistration.json:9`, "separability": "C2 touches `tools/round54-cited-path-check.py` and `registry/cited-path-corrections.tsv` (the superseded row)"), and read by the C2 counter at `tools/round54-cited-path-check.py:160` (`LEDGER = "registry/cited-path-corrections.tsv"`).

### 2.1 The probe-relevant surfaces ARE unchanged (empty diff)

```
$ git diff 3a600d2f729828419aaea34cc402c8b0d20fb720 9c60eae6f7ed84f7da93d219a406aadc30958c6c \
      --stat -- tools/kama-probe.sh registry/endpoint-consumers.tsv registry/history/
                                    # (no output — empty)
```

Blob-level equality at both commits:

```
$ git rev-parse 3a600d2:tools/kama-probe.sh            9c60eae:tools/kama-probe.sh
29b02c744b2fc2e6ea7601d31ead68266362f7ad            29b02c744b2fc2e6ea7601d31ead68266362f7ad   (mode 100755 both)
$ git rev-parse 3a600d2:registry/endpoint-consumers.tsv 9c60eae:registry/endpoint-consumers.tsv
c79b7140b3cf8b6a2e75e58fc7c3e9546b25524f            c79b7140b3cf8b6a2e75e58fc7c3e9546b25524f

$ git show 3a600d2:tools/kama-probe.sh            | sha256sum
4393ab819d6a741646237ef0268cc0836988a9711bab6b06c46cbfea382964f4   # identical at 9c60eae
$ git show 3a600d2:registry/endpoint-consumers.tsv | sha256sum
bf343625188d9f486a6f6d13c60c946e23c21d05ee1bef881204dfa14c62bc6c   # identical at 9c60eae
```

The registry-consumers blob `c79b7140…` / sha256 `bf343625…` is the same pin the round-18 separability review already froze (`.ufo/waves/round-18/build/advice/RevSeparability.md:164`: `git -C $L diff --quiet $B $I -- tools/kama-probe.sh registry/endpoint-consumers.tsv 'tests/probe-verdicts/*.json'`, with "registry bf343625…" expected). `tests/probe-verdicts/*.json` is also unchanged base→freeze (empty diff) and the 72-case matrix passes.

### 2.2 Defect (spec text, not lane code)

**File/line:** `.ufo/waves/round-55/build_spec.py:148` (the X10Probe item; the same wording is already materialised in `.ufo/waves/round-55/w1/spec.json:453`, `w1/dispatch.json:512,930`, `w1/out/swarm-registry.json:494`, `w1/validate.out`).

**Command that shows it:**
```
$ git diff 3a600d2f729828419aaea34cc402c8b0d20fb720 9c60eae6f7ed84f7da93d219a406aadc30958c6c \
      --stat -- tools/kama-probe.sh registry/
 registry/cited-path-corrections.tsv | 6 ++++++
```

**Why it is a defect, not a finding against the freeze:** the item's assertion is falsified by the freeze commit's own preregistered C2 surface, so an operator following the item literally would have to report either (a) a false "probe/registry surfaces changed" regression, or (b) a false "registry/ was empty" fact. Both are wrong; the probe surfaces are provably unchanged (§2.1) and the ledger change is a preregistered C2 artifact (§2 above). The wider `registry/` path also contains 21 further files (census/ledger/verdict ledgers) that have changed in past rounds for unrelated reasons, so `registry/` was never a probe-surface selector.

**Proposed fix** (unified diff, saved verbatim at `out/X10Probe/proposed-fix.diff`; NOT applied — the lane is read-only for this seat):

```diff
--- a/.ufo/waves/round-55/build_spec.py
+++ b/.ufo/waves/round-55/build_spec.py
@@ -145,7 +145,7 @@
 add("X9Separation", "executor", ["operability", "calibration"],
     f"Causal-separability measurements (supports {PR}'s separability paragraph): in your own clone at {FREEZE}, (a) revert ONLY the superseded ledger row (git show {BASE}:{LEDGER} > {LEDGER}, commit) and run the frozen C1 counter - expect still green; run the frozen C2 counter - expect red (dropped=1); (b) revert ONLY the S511 row (remove it from corpus/SOURCES.md, commit) and run the frozen C2 counter - expect green; run the frozen C1 counter - expect red (newrow=0). Report all four receipts. Output {OUT}/X9Separation/.")
 add("X10Probe", "executor", ["operability"],
-    f"Probe regression at {FREEZE}: `bash tools/kama-probe.sh check` and `bash tools/kama-probe.sh consumers` (read-only; expect exit 2 and exit 0 respectively with the three DEAD rows) - save outputs. This is the standing registered-endpoint regression; confirm the freeze commit changed nothing in the probe/registry surfaces (git diff {BASE} {FREEZE} --stat -- tools/kama-probe.sh registry/ should be empty). Output {OUT}/X10Probe/.")
+    f"Probe regression at {FREEZE}: `bash tools/kama-probe.sh check` and `bash tools/kama-probe.sh consumers` (read-only; expect exit 2 and exit 0 respectively with the three DEAD rows) - save outputs. This is the standing registered-endpoint regression; confirm the freeze commit changed nothing in the probe/registry surfaces (git diff {BASE} {FREEZE} --stat -- tools/kama-probe.sh registry/endpoint-consumers.tsv registry/history/ should be empty -- registry/ as a whole is NOT expected to be empty: C2's `superseded` row lands in registry/cited-path-corrections.tsv, which is a C2 surface, not a probe surface). Output {OUT}/X10Probe/.")
 add("S5Shokuknow", "scout", ["adjacency"],
     f"Assimilation status scan: read /home/vgpnk/Projects/shokuknow/merge/kama/MERGE-REPORT.md and the lane's absent-defect-register slice (the register at /home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md, kama rows; read-only). Confirm whether the register slice has any unchecked rows (the lane's earlier quarantine-first round verdicted them) and whether merge/kama has any NEW rows since the lane's last assimilation pass. Report 'Assimilation: none' supporting facts for the round report. Output {OUT}/S5Shokuknow/.")
 add("S6Considerthese", "scout", ["calibration"],
```

The narrowed selector `tools/kama-probe.sh registry/endpoint-consumers.tsv registry/history/` matches the probe's actual inputs and the round-18 separability pin, and its diff **is** empty.

## 3. Scope and hygiene

* Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`: read-only. `git status --porcelain -- registry/ tools/ tests/` empty after every run; no `git add/commit/checkout/stash/reset` in the lane; no jj mutation.
* One live clone only: `/fast/scratch/hyaku/kama-r55/w1/X10Probe/lane` (`git clone --shared`); `git -C "$S/lane" rev-parse --show-toplevel` verified to print the clone path before the first checkout. No commits were made in it (checkout only).
* Fleet repo `/home/vgpnk/Projects/shokunin` and `/home/vgpnk/Projects/shokuknow`: read-only, not written, no campaign tool run there. No fleet-root file written.
* No service started or stopped by this seat. No llama-server was launched (the probe and the verdict-matrix harness own their own loopback stubs and tear them down). `pgrep -af llama-server` shows no process attributable to this seat; the two live `llama-server` processes on the host belong to the concurrently running `J5EnvNames` and `Rev1` seats (ports 40863 etc.), and the two `stub.py` processes under `/fast/scratch/hyaku/kama-r49/` predate this wave — none were started or stopped here.
* No tracer (`strace`/`ltrace`) wrapped around any counter or the probe. No counter was edited. The preregistration, controls and measured receipts were read only.
* Tooling: no package was installed or upgraded by this seat (none needed); `ss`, `curl`, `flock`, `python3` were already present. `/home/vgpnk/.omp/agent/RULES.md` was read before any tool use.
* Scratch `/fast/scratch/hyaku/kama-r55/w1/X10Probe` was removed after copying all cited artifacts into the out dir.

## 4. Files written by this seat

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X10Probe.md` (this report)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X10Probe/probe-check.out`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X10Probe/probe-consumers.out`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X10Probe/probe-check-base-3a600d2.out`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X10Probe/probe-consumers-base-3a600d2.out`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X10Probe/probe-listeners.out`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X10Probe/probe-snapshot-clone.out`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X10Probe/probe-verdicts-matrix.out`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X10Probe/freeze-diff-registry-stat.out`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X10Probe/freeze-diff-probe-surfaces-stat.out` (empty by construction — the narrowed diff)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X10Probe/proposed-fix.diff`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/X10Probe/SHA256SUMS.txt`

## 5. Blockers / risks

* None for the probe regression.
* Residual risk for the round report: the standing registered-endpoint state is three DEAD rows because no listener exists on 8080/34113 on this host at this instant. That is an environment fact, not a lane fact; the committed baseline (`registry/history/latest.tsv`) shows the same three DEAD rows, so the standing regression is unchanged.
* The spec-text defect in §2.2 is confined to the X10Probe item wording (already frozen into `w1/spec.json`, `w1/dispatch.json`, `w1/validate.out`, `w1/out/swarm-registry.json`); correcting it in `build_spec.py` only helps a future round. No claim measurement depends on it — C1 and C2 do not touch `tools/kama-probe.sh`, `registry/endpoint-consumers.tsv` or `registry/history/` (freeze diff: only the two counters, `corpus/SOURCES.md`, `corpus/lessons/round-55.md`, `registry/cited-path-corrections.tsv`, and the `.ufo/waves/round-55/` preregistration/controls/sources artifacts).
