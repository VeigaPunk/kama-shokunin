# Simp2Tool — YAGNI review of `tools/kama-live-replay.py` and `tools/append-only-audit.py`

**Verdict:** 4 deletions proposed (net −2 lines: 9 removed, 7 added; `yagni.diff`, applies cleanly at `3a09a1d9`), covering one dead regex detail, one never-overridden parameter, one option with no caller and one output field with no reader. **No selftest case is deleted:** a one-guard-at-a-time broken-copy matrix shows every case in both runs is the unique killer of at least one guard. The "options nobody needs" hypothesis is **falsified** for `--files`, `--threshold` and `--timeout` — all three have live in-wave callers (below). Every proposed change is behaviour-preserving against both `--selftest` runs, the lane measure at `3a09a1d9`, and the frozen C1 counter (`met=True` before and after). Judged axis: operability.

Scope: read-only on the lane. All runs used a scratch clone `/fast/scratch/hyaku/kama-r47/Simp2Tool/lane` (`git clone --shared`) and scratch copies of the two tools. No lane file, index or jj state was touched (`git -C kama-shokunin status --porcelain -- tools` is empty at the start of the seat; the one `M tests/llamacpp-live/check-receipt.py` is not mine — my only writes under the lane are this report and `out/Simp2Tool/`).

**Tree drift during this seat (not mine, and it does not change what is measured).** Between 18:33 and 18:34 the lane working tree gained in-place edits to `tools/append-only-audit.py`, `tools/kama-live-replay.py`, `tools/gguf-identity.py` and `corpus/SOURCES.md` (an integrating seat adding `vanished`/`unmatched_patterns`/`binary_changes`, NUL-delimited paths, a CRLF-contract refusal, and `notes`/`live-exit:` reporting to the replay). Those files were clean when I read them and the review is against the **committed** build at `3a09a1d9` (`git show 3a09a1d9:tools/…`, blob `9442eb8c` / `3773e62d`), which is what the frozen C1 counter measures (`git show <tip>:tools/append-only-audit.py`). Every line number in this report is a `3a09a1d9` line. All four deletion targets still exist in the drifted tree, at `tools/append-only-audit.py:74,155-156` (`HUNK` and the two `m.group` uses) and `tools/kama-live-replay.py:14,58,167,271` (`Usage`, `fetch`, `live_exit`, `--live`); `yagni.diff` therefore needs a context rebase before it is applied on top of the integration, and D4 must not disturb the integrator's new `live-exit:` mismatch, which is a separate field.

## Axes and what I called a win

| axis | direction | move |
|---|---|---|
| operability | surface a reader must hold | drop the two hunk captures nothing reads, the download parameter nothing overrides, the CLI option nothing invokes and the J field nothing reads |
| operability | evidence integrity | `--live` let a run substitute the tool under test while still reporting `match=True`; the shipped CLI can now only use the live tool beside it (the selftest keeps the function-level seam it actually uses) |
| coverage | must not fall | 0 selftest cases removed, both counters' contracts untouched (`AOA_SELFTEST pass=15`, `KLR_SELFTEST pass=10`, C1 requires `n >= 10`) |
| clarity | — | the retained options now each have a named caller in this round's own seat list |

## Proposed deletions (`yagni.diff`, 4 hunks)

```diff
--- a/tools/append-only-audit.py
+++ b/tools/append-only-audit.py
@@ -63,7 +63,7 @@
 CONTRACT = "registry/append-only-contract.tsv"
 HEADER = "path\trule\tdeclared_at\tnote"
 RULES = ("A", "A-row", "A-corr")
-HUNK = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
+HUNK = re.compile(rb"^@@ -\d+(?:,(\d+))? \+\d+(?:,(\d+))? @@")
 
 
 class AuditError(Exception):
@@ -123,8 +123,8 @@
         i += 1
         if not m:
             continue
-        nd = int(m.group(2)) if m.group(2) is not None else 1
-        na = int(m.group(4)) if m.group(4) is not None else 1
+        nd = int(m.group(1)) if m.group(1) is not None else 1
+        na = int(m.group(2)) if m.group(2) is not None else 1
         gd = ga = 0
         while i < len(lines) and (gd < nd or ga < na):
             ln = lines[i]
--- a/tools/kama-live-replay.py
+++ b/tools/kama-live-replay.py
@@ -11,7 +11,7 @@
 same ``passed`` value, and the server and model sha256 must be equal.
 
 Usage:
-  kama-live-replay.py --receipt R --work DIR --out J [--live TOOL] [--timeout S]
+  kama-live-replay.py --receipt R --work DIR --out J [--timeout S]
   kama-live-replay.py --selftest [--scratch DIR]
 Writes J: {"schema": "kama-live-replay/v1", "receipt", "work", "rerun_receipt",
 "match", "refused", "mismatches": [...], "inputs": {...}}.
@@ -54,13 +54,13 @@
     return h.hexdigest()
 
 
-def fetch(url, dest, timeout=120):
+def fetch(url, dest):
     """Download url to dest (https or file://; file:// only for the selftest)."""
     if not (url.startswith("https://") or url.startswith("file://")):
         raise Refused(f"url-scheme:{url}")
     tmp = dest + ".part"
     req = urllib.request.Request(url, headers={"User-Agent": "kama-live-replay/1"})
-    with urllib.request.urlopen(req, timeout=timeout) as r, open(tmp, "wb") as fh:
+    with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as fh:
         shutil.copyfileobj(r, fh, CHUNK)
     os.replace(tmp, dest)
 
@@ -155,7 +155,6 @@
                 "--server-asset-sha256", need["server.asset_sha256"], "--server-member", need["server.member"],
                 "--model-url", need["model.url"], "--out", rerun]
         p = subprocess.run(argv, capture_output=True, text=True, env=env, timeout=timeout)
-        res["live_exit"] = p.returncode
         if not os.path.isfile(rerun):
             raise Refused(f"no-rerun-receipt:exit={p.returncode}:{p.stderr[-300:]}")
         res["rerun_receipt"] = rerun
@@ -247,7 +246,6 @@
     ap.add_argument("--receipt")
     ap.add_argument("--work")
     ap.add_argument("--out")
-    ap.add_argument("--live", default=DEFAULT_LIVE, help="kama-llamacpp-live.py path")
     ap.add_argument("--timeout", type=float, default=600.0)
     ap.add_argument("--selftest", action="store_true")
     ap.add_argument("--scratch", help="selftest root (default TMPDIR)")
@@ -256,7 +254,7 @@
         return _selftest(a.scratch or tempfile.gettempdir())
     if not (a.receipt and a.work and a.out):
         ap.error("--receipt, --work and --out are required")
-    res, code = replay(a.receipt, a.work, a.live, a.timeout)
+    res, code = replay(a.receipt, a.work, timeout=a.timeout)
     with open(a.out, "w") as fh:
         json.dump(res, fh, indent=1)
     print(f"replay match={res['match']} refused={res['refused']} mismatches={len(res['mismatches'])} exit={code}")
```

The same patch, byte-for-byte, is `out/Simp2Tool/yagni.diff` (generated with `diff -ruN a b`; that file additionally carries the `diff -r` line and mtimes). Apply from the lane root with `patch -p1` or `git apply -p1`; dry run there: `checking file tools/append-only-audit.py`, `checking file tools/kama-live-replay.py`, `APPLY_DRYRUN_OK`.

### D1 — `append-only-audit.py:66,126-127`: two hunk captures nothing reads
`grep -n "m.group" tools/append-only-audit.py` returns exactly two lines, `m.group(2)` and `m.group(4)`. Groups 1 (old start line) and 3 (new start line) are captured at `:66` and referenced nowhere; only the two *counts* are used (`nd` at `:126`, `na` at `:127`). Keeping them invites the reading that the start offsets matter to the multiset measure, which they do not. Rewriting them as non-capturing keeps the header match requirement (`@@ -\d+ ... @@` also matches the single-line form `@@ -1 +1 @@` and the `-0,0` form) and renumbers the two survivors.

### D2 — `kama-live-replay.py:57,63`: `fetch(..., timeout=120)` is never overridden
Both call sites (`:141`, `:142`) pass two arguments. The parameter and the `timeout=timeout` it feeds are a knob with no turn: the budget that *does* have an option is the inference run, `--timeout`, applied at `subprocess.run` (`:157`); the download budget is fixed. Inlining 120 removes the false suggestion that a caller tunes the download.

### D3 — `kama-live-replay.py:250`: `--live` has no caller, and it is an evidence knob
`grep -rn -- "--live"` over the lane, excluding the tool itself and the `out/K2Cheat` fork copies, yields only: a byte-code string of the tool, `out/K2Fresh/transcript.md:65` (a seat quoting the option list) and `out/V2Replay.md:20`, where another seat independently names it a hazard: *"any `--live` tool that exits non-zero while writing a pass-shaped receipt substitutes as 'match'."* C2's replay leg (`tools/round47-live-replay-audit.py:184-189`) invokes `--receipt/--work/--out` only, and runs the tool from a `git archive` tree where `DEFAULT_LIVE` resolves correctly. The selftest never routes through argparse: `_selftest` calls `replay(..., live=fake_live)` at `:220`, so the **function** parameter (the real seam) stays; only the CLI surface goes.

### D4 — `kama-live-replay.py:158`: `res["live_exit"]` is written and read by nothing
The J is documented at `:16-17` as `{schema, receipt, work, rerun_receipt, match, refused, mismatches, inputs}` — `live_exit` is not in it. C2's contract reads `schema`, `rerun_receipt`, `match`, `refused` (`round47-live-replay-audit.py:265-269`). No report in the lane narrates it (`grep live_exit` hits only JSON artifacts and the tool). When it would matter (the live tool wrote no receipt) the value is already inside the refusal string at `:160` (`no-rerun-receipt:exit=<code>`); when the live tool wrote a failing receipt, `outcome`/`mismatches` carry the fact. Removing it removes a documented-shape (`:16-17`) contradiction rather than a diagnostic.

## Rejected deletions, with the caller that rejects them

These are the candidates "dead weight" review usually proposes here. Do not apply them.

| candidate | why it stays | evidence |
|---|---|---|
| `--threshold` (`append-only-audit.py:469`) | two seats of this wave run it at 1 | seat **L1Lowthr**: `append-only-audit.py --repo <clone> --to 3a09a1d9… --contract …/append-only-contract.tsv --threshold 1 --json`; seat **R1Sample** the same command; measured here: 91 events, exit 1 (`lane/thr1-after.json`) |
| `--files` (`:471`) | used to run the same measure on lanes with no contract | seat **N3Fleet**: `--repo <lane> --to <tip> --files SCORECARD.md,LOG.md,corpus/QUALITY.md,corpus/README.md,corpus/SOURCES.md --json`; measured here: byte-identical output before/after (`lane/files-*.json`) |
| `--timeout` (`kama-live-replay.py:251`) | a failure-mode seat needs a 1 s budget | seat **X2Offline** "(d) a `--timeout` of 1 second" |
| `--json`, `--scratch` | frozen counter + KQ67 | `round47-append-audit-v2-check.py:337,371`; `corpus/QUALITY.md:387` |
| `inputs` block in J | quoted as evidence by a seat | `out/K2Fresh.md:32` quotes `archive_sha256`; also `C2` runs inside `--scratch` and the block is the only place the *observed* digests are stated |
| `extract()` (`:98`) | one call site, but it is the seam a reviewer points at for the `filter="data"` claim | `:144`; Sen2Replay's item is about exactly that filter |
| `parse_contract` returning the `note` cell | `note` is unread in `audit()`, but dropping the 4th cell changes the parser's stated return shape (`:85`) and the contract's own 4-cell validation | `:93-96` |
| `files = sorted(set(files))` (`:185`) | redundant after `expand()` (`:107`) but required for the comma list `--files` | N3Fleet path above |
| `os.path.basename(url.split("?")[0])` twice (`:139-140`) | two occurrences, each with a different fallback; a helper would add a name and delete no decision | — |
| the two hunk parsers | **intentionally separate — never merge** | see below |

## Duplicated logic: what is deliberate

- **The two hunk parsers** — `deleted_lines()` (`append-only-audit.py:117-137`) and the counter's own (`round47-append-audit-v2-check.py:162-188`) — are the same algorithm over `git diff -U0`, and that is the point: the counter's `lane` leg requires that the tool *cannot* load the counter's recomputation — "the tool's source at `--tip` must not contain the string `round47`, so it cannot load this counter's recomputation" (`round47-append-audit-v2-check.py:70-72`). A shared module would make the C1 claim circular. Keep both, keep them independent. (The counter's copy carries the same two unused captures at `:168`; that is its business, not this lane's tool, and it is frozen.)
- **`numstat()` vs the hunk count** (`append-only-audit.py:165` vs `:126-127`) is not duplication: `numstat` is the ground truth the hunk count must equal (`:203` raises when they differ), i.e. the cross-check the whole v2 definition rests on.
- **`sha256_file` in the replay tool** re-implements a hash the live tool also computes — again the point: the verifier must not call the tool it verifies, and C2 runs the replay tool from `git archive` with no import path to the lane.
- **`provenance()`'s member check (`:84`) vs the post-extraction realpath check (`:146`)** look like one guard twice; they are two different guards. `:84` refuses `../x` before 23 MB is downloaded (and is the only reason the refusal reads `unsafe-member`), `:146` refuses an archive member that is a symlink escaping the tree, which `:84` cannot see. Mutant R4 (below) kills `unsafe-member` when `:84` is removed, which is exactly the message contract.

## Selftest distinctness: none is duplicated (evidence, `static/mutants.txt`)

Method: break one guard in a scratch copy, run that copy's `--selftest`, record which cases fail.

| mutant (one-line) | selftest | failed cases |
|---|---|---|
| threshold hard-coded `if ns[f] < 20:` | `pass=14 fail=1` | `threshold-flag` |
| boundary inclusive `if ns[f] <= threshold:` | `pass=13 fail=2` | `exact-threshold-unrestored`, `threshold-flag` |
| v1 `---`-prefix rule restored in the hunk loop | `pass=14 fail=1` | `dashdash-lines` |
| model digest unchecked | `pass=9 fail=1` | `model-digest-wrong` |
| archive digest unchecked | `pass=9 fail=1` | `asset-digest-wrong` |
| provenance schema gate removed | `pass=9 fail=1` | `v3-receipt` |
| pre-download member check removed | `pass=9 fail=1` | `unsafe-member` |

Every case is the unique killer of at least one guard. The two pairs that looked redundant on inspection survive the test: `asset-digest-wrong`/`model-digest-wrong` kill different `acquire()` calls (first vs second input), and `threshold-flag` is the *only* case that kills a hard-coded threshold, so it earns its place even though `exact-threshold-unrestored` covers the `==` boundary. `AOA_SELFTEST` stays at 15 and `KLR_SELFTEST` at 10, so C1's `n >= 10` requirement is untouched.

## Behaviour preserved — commands and results

All in scratch; `S=/fast/scratch/hyaku/kama-r47/Simp2Tool`.

1. **Selftests before/after** — outputs byte-identical, both tools, both runs:
   ```
   python3 $S/base/append-only-audit.py    --selftest --scratch $S   # rc=0, AOA_SELFTEST pass=15 fail=0
   python3 $S/patched/append-only-audit.py --selftest --scratch $S   # rc=0, AOA_SELFTEST pass=15 fail=0
   diff …   → AOA_SELFTEST_OUTPUT_IDENTICAL
   python3 $S/base/kama-live-replay.py    --selftest --scratch $S   # rc=0, KLR_SELFTEST pass=10 fail=0
   python3 $S/patched/kama-live-replay.py --selftest --scratch $S   # rc=0, KLR_SELFTEST pass=10 fail=0
   diff …   → KLR_SELFTEST_OUTPUT_IDENTICAL
   ```
   (`selftest/*.out`)
2. **The lane measure** — `--repo <clone> --to 3a09a1d9… --contract registry/append-only-contract.tsv`, exit 1 both times, **JSON byte-identical** (`cmp` → `LANE_JSON_BYTE_IDENTICAL`), text output identical: 85 files, 303 commits, 5 events — `dd9f5dc6` SCORECARD 31/24 partial; `0718b6ab` LOG 2292 restored, SCORECARD 2421/2420 partial, QUALITY 375 restored, README 663 restored. (`lane/lane-*.json`, `lane/lane-*.txt`) This is the same set the lane reports at `3a09a1d9`.
3. **Every option path that stays** — `--files …` → byte-identical, exit 1; `--threshold 1` → byte-identical, 91 events, exit 1 (`lane/files-*.json`, `lane/thr1-*.json`).
4. **The frozen C1 counter**, run against my clone (`met=True` in both, only the `tip=` line differs):
   ```
   --tip 3a09a1d9…    → selftest=1 contract=1 lane=1 fixture=1 stable=1 files=85 lane_events=5 lane_mismatch=0 fixture_mismatch=0 met=True  rc=0
   --tip 02bd2c86…    → selftest=1 contract=1 lane=1 fixture=1 stable=1 files=85 lane_events=5 lane_mismatch=0 fixture_mismatch=0 met=True  rc=0
   ```
   `02bd2c86` is the patch committed with the fixture identity on top of `3a09a1d9` **inside my scratch clone only**. (`c1/*.out`)
5. **CLI through the changed `main()`** — a harness with the tool and a fake `kama-llamacpp-live.py` side by side (exactly how `DEFAULT_LIVE` resolves after D3), a v4 receipt over `file://` inputs, and a v3 refusal:
   ```
   base    --receipt r.json    → match=True  refused=None mismatches=0 exit=0   (live_exit 0 present)
   patched --receipt r.json    → match=True  refused=None mismatches=0 exit=0   (keys: inputs, match, mismatches, receipt, refused, rerun_receipt, schema, work)
   base/patched v3 receipt     → refused=not-a-v4-receipt:kama-llamacpp-live/v3 exit=2
   ```
   J diff between base and patched, after allowing the two different `--work` roots: only `live_exit` disappears; `rerun_receipt` contents are **byte-equal**; `inputs.archive_sha256`/`model_sha256` equal; the v3 refusal J is equal apart from `work`. (`cli/*.json`)
6. **Static**: `vulture --min-confidence 60|100` and `uvx pyflakes` on both tools — no output, rc 0, so no named dead code exists; the four deletions are structural.

## Findings (not applied — the counters and preregistration are frozen; both tools are the build, so these are proposals)

- **F1 — `append-only-audit.py:442-448`, `threshold-flag`'s name oversells its coverage.** The case is called `t_threshold_flag` but calls `audit(..., threshold=5, files=F)` directly (`:447`), never `main()`, so it does not test the `--threshold` flag it is named for; it tests that the *parameter* is honoured (which is worth keeping — it is the only killer of a hard-coded 20). Proposed fix: rename to `t_threshold_param` and let the flag itself be covered where it is used (L1Lowthr/R1Sample/`lane/thr1-*.json`), or add one `main(["--threshold","5",...])` case. Line: `append-only-audit.py:456` (`for name, fn in [...]` list entry `("threshold-flag", t_threshold_flag)`).
- **F2 — doc consequence of D3/D4, for the L1 to route.** `kama-live-replay.py:14` is the only in-tool record of `--live`; outside it, `out/K2Fresh/transcript.md:65` and `out/V2Replay.md:20` quote the old option list (historical artifacts, leave them). The **SKILL.md `## Round-47 instrument registry` row for `kama-live-replay.py`** that seat S9Skill is drafting from this docstring must record `--receipt/--work/--out/--timeout/--selftest/--scratch` and the J without `live_exit` if D3/D4 land. `SKILL.md:1442` (round-46 append-only row) needs no change: `--threshold` and `--files` are retained.
- **F3 — `append-only-audit.py:66` has the same unused captures in the frozen counter** (`round47-append-audit-v2-check.py:168`). Not a defect and not mine to fix; noted so a later reviewer does not "unify" the two parsers to fix it.

## Tradeoff

D3 costs one thing: a human who copies `kama-live-replay.py` into a scratch tree can no longer point it at a live tool elsewhere, because `DEFAULT_LIVE` follows `__file__` (`:40`). The counter, the two replay seats and this review all either run the tool in place or use the function seam, and the option's only caller-free use was the substitution hazard V2Replay named. If that debugging path is judged worth more than the hazard, drop D3 and keep D1/D2/D4 — they are independent hunks. D4 costs the `live_exit` field that `out/X2Replica/replay-2.json:16` happens to carry; the information survives in `refused`/`outcome`.

## Tooling record

No installs, upgrades or pacman transactions. `vulture` was already present (`≥60`/`100` confidence runs); `uvx pyflakes` ran ephemerally from the uv cache, nothing written to a PATH directory.

## Files written

- `.ufo/waves/round-47/w1/out/Simp2Tool.md` (this report)
- `.ufo/waves/round-47/w1/out/Simp2Tool/yagni.diff`
- `.ufo/waves/round-47/w1/out/Simp2Tool/selftest/{aoa,klr}-{before,after}.out`
- `.ufo/waves/round-47/w1/out/Simp2Tool/lane/{lane-before,lane-after}.{json,txt}`, `lane/{files,thr1}-{before,after}.json`
- `.ufo/waves/round-47/w1/out/Simp2Tool/c1/c1-{before,after}.out`
- `.ufo/waves/round-47/w1/out/Simp2Tool/cli/{cli,cli-v3}-{base,patched}.json`
- `.ufo/waves/round-47/w1/out/Simp2Tool/static/{mutants.txt,static.txt}`
