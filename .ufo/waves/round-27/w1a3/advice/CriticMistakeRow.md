VERDICT: partial — The reported disk-exhaustion incident and missing attempt-2 file-size rule are supported, but the exact self-write mechanism, historical scope of the fix, and universal process-stop interpretation are not.

# CriticMistakeRow — mined-mistake attack

Target: `corpus/lessons/round-27.md:92`, reviewed as the 92-line lesson with SHA-256 `a0b3c748ad4b638320c66449304869f489f8a7fa1ab9266cc56d0d27acb273f7`.

Axes: **calibration** (observation versus causal attribution; bounded claims), **depth** (what the retained source actually writes), **operability** (file-size enforcement versus process termination). This is evidence for the later reviewer, not a round/claim judgment. C1 was not scored; X1 was not judged.

## Per-cell findings

| Cell | Review verdict | Evidence and smallest safe correction |
|---|---|---|
| **class** | **partial** | The removal note reports a 262,699,483,136-byte `sitecustomize.py` and a full `/fast`; the retained prefix repeats source statements. That supports uncontrolled repeated fixture growth, not the specific assertion that the MARKER hook copied its own fixture. The hook writes a formatted `sitecustomize hit pid=… argv=…` record, not its two source lines (`a3/mistake-runaway/sitecustomize.py.head4k:1-4`). [INFERENCE] A source-copying or source-generating writer could explain the prefix; neither writer identity nor MARKER alias is established. Use **“unbounded fixture growth / disk exhaustion; exact writer and self-reference mechanism unestablished.”** |
| **evidence pointer** | **partial** | The directory resolves and contains the stated 4096-byte prefix and Main's removal note. The original size, ENOSPC impact, and whole-file repetition are **reported by the note**, not independently measured from the retained prefix. The note says MARKER **“evidently”** pointed back; it supplies no writer command, MARKER value, or seat-specific original path (`REMOVED-RUNAWAY.txt:1`). The attempt-2 spec identifies the ReviewA3Diff assignment (`w1-controls/spec.json:177-179`), but does not identify the writer. Keep the attribution as reported, distinguish the observed prefix from the original-file report, and label the alias hypothesis [INFERENCE]. |
| **captured-by** | **holds, narrowly scoped** | A full-string sweep of the attempt-2 spec, including all 37 items and ReviewA3Diff, found no `ulimit`, `RLIMIT_FSIZE`, file-size, size-cap, or MARKER rule. Its context names process, memory and wall-time bounds only (`w1-controls/spec.json:4`). This supports **“none: no explicit file-output cap or input/output-alias rule in the attempt-2 dispatch.”** It does not establish that the host's inherited limit was unlimited, or that every historical context was checked. Do not retroactively call the new attempt-3 rule an existing catcher. |
| **fix** | **partial; useful file-bound effect demonstrated** | The current attempt-3 context does require a cap, timeout and disjoint import/input destinations (`w1a3/spec.json:4`). The newly retained ExecFixtureBoundDemo receipt shows the cap bounds growth, including an identical-timeout control. However, **“every round-27 wave context”** is false literally: the preserved attempt-2 context is a counterexample. Narrow this to the attempt-3/new dispatch context. Also say **“bounds each file; timeout stops a writer that continues after EFBIG”**, not that the cap necessarily terminates the writer. The receipt's E2 and D3 are concrete counterexamples to that stronger reading. Link the actual `ExecFixtureBoundDemo/receipt.json` rather than the currently absent lesson §Fix receipt. The numeric demo is evidence of cap effectiveness, not reconstruction of the incident or, by itself, the protocol's non-clean red-before detector proof; details below. |

## Strongest counterexamples and retained evidence

All short paths in this section are under `.ufo/waves/round-27/` unless stated otherwise.

### 1. The retained hook does not emit the repeated source

`a3/mistake-runaway/sitecustomize.py.head4k:1-4`:

```text
import os, sys
open(os.environ["MARKER"], "a").write("sitecustomize hit pid=%d argv=%r\n" % (os.getpid(), sys.argv[:2]))
import os, sys
open(os.environ["MARKER"], "a").write("sitecustomize hit pid=%d argv=%r\n" % (os.getpid(), sys.argv[:2]))
```

An invocation of line 2 emits the formatted message, not `import os, sys` and not another `open(...).write(...)` statement. Thus pointing MARKER at this file is not a demonstrated explanation of its repeated-source prefix. It could coexist with another writer, but that additional writer is not retained here. [INFERENCE] Repeated source is consistent with fixture construction/copying gone wrong; the exact mechanism remains unknown. No banned dead-seat directory was opened to try to reconstruct it.

### 2. A file cap is not a universal termination or nonzero-exit guarantee

These are **peer-run observations read from retained evidence**, not experiments executed by this critic. Exact commands are in `w1a3/out/ExecFixtureBoundDemo/receipt.json:55,89,107,135` and `run-extra.sh:31`; each uses that seat's generic fixture, not the incident file.

| Retained run | Command, before its per-run stdout/stderr redirects | Observed exit / final fixture size |
|---|---|---|
| A0 | `( ulimit -f 2048; export PROGRESS_LOG=A0.log A3_SIG_DFL=0; exec timeout 60 python3 fixture.py )` | **1**, EFBIG / **2,097,152 B** (`receipt.log:18-28`) |
| B1 | `( ulimit -f 20480; export PROGRESS_LOG=B1.log A3_SIG_DFL=1; exec timeout 5 python3 fixture.py )` | **153** / **20,971,520 B**; `size<=2097152=NO` (`receipt.log:44-56`) |
| C0 | `( ulimit -f 2048; export PROGRESS_LOG=C0.log A3_SIG_DFL=1; exec timeout 5 python3 fixture.py )` | **153** / **2,097,152 B**; `size<=2097152=YES` (`receipt.log:58-69`) |
| E2 | `( ulimit -f 2048; export PROGRESS_LOG=E2.log A3_SIG_DFL=0 A3_SWALLOW=1; exec timeout 3 python3 fixture.py )` | **124**, still looping until timeout / **2,097,152 B**; `swallowed errno=27 count=889000 size=2097152` (`receipt.log:123-131`) |

C0/B1 hold the timeout at five seconds and retain the same writer/signal setting. The 60-versus-5-second difference in the original assignment is therefore **not an outstanding confound**. Their sizes provide positive, discriminating evidence for the smaller cap. A0 also shows why exit 153 cannot be required for every writer: this captured environment inherited ignored SIGXFSZ (`receipt.log:9-16`), while `fixture.template.py:106-107` restores SIG_DFL only for selected runs.

The strongest exit-only counterexample uses the same unclosed `open(...).write(...)` idiom as the incident prefix: `probe-efbig-site.log:13-19` records EFBIG as `Exception ignored while finalizing file`, **`open_write_no_close_exit=0`**, and unchanged **2,097,152 B**. Therefore neither “all cap hits exit 153” nor “all cap hits exit nonzero” is supported. File size stayed bounded; process/verdict behavior is a separate proposition.

The shell-loop counterexample is independent of Python exception handling: D3 records **exit 124**, **2,097,152 B**, and 6,919 `File too large` errors (`receipt.log:145-152`; command at `receipt.json:166`). Timeout, not the cap, owns the eventual loop stop.

### 3. Printed red is not yet the protocol's non-clean red-before detector

The canonical `CORPUS.md:166-171` defines captured-by and requires the same command to exit non-clean for the named reason, with the fix the only delta. The retained `run-demo.sh:42-43` detector only echoes YES or NO; both branches return the successful `echo` status. B1 prints NO, but the overall demo records **`RUN_DEMO_EXIT=0`** (`receipt.log:112`). C0 and B1's writer exits are both 153.

Consequently, the cap's **numeric effectiveness is demonstrated**, while a separately claimed, machine-observed non-clean red-before **size detector** is not present in this receipt. Smallest correction: do not equate a printed NO with that formal proof. If the author credits strict red-before conformance, retain a detector that returns nonzero specifically for `size > 2 MiB`, exercised on the same finite, cap-only-delta pair, and preserve its actual failure output. There is no reason to run an uncapped disk-filling arm.

## Better captured-by rule

Separate two questions rather than giving “none” unlimited scope:

1. **Prevention at incident time:** none found in the bounded attempt-2 spec sweep. The proposed prevention is real but prospective: the **attempt-3 Disk safety rule, `w1a3/spec.json:4`**. It requires a finite inherited file cap, timeout, and destinations separate from imported/input files. “Separate” should mean a different underlying file, including symlink/hardlink aliases, not merely a different pathname. [INFERENCE] A per-file cap is not an aggregate `/fast` quota; many allowed files can consume the shared volume.
2. **Truthfulness of the mined causal explanation:** existing **KQ23**, `corpus/QUALITY.md:132`, is a better catcher than “none”: it requires the trigger, handler/state/outcome chain and names the limits of a termination guarantee. It should reject the unsupported MARKER-to-self causal assertion and any universal process-stop claim. KQ14 (`:41`) likewise keeps content correspondence separate from pointer/shape validity. Neither is an existing disk-output prevention rule.

If the prevention remains captured-by none, canonical `LEARNING.md:19-21` calls for a grounded QUALITY criterion, not only another wave-context instruction. The reviewed 219-line QUALITY file has KQ37 for decoded echoes, but no file-output-budget criterion. Smallest prospective addition: a **lane experiment fixture/log safety criterion**, citing this lesson, requiring finite inherited soft/hard file-size limits plus timeout, no output alias to an input/imported fixture, and retained discriminating evidence for exactly the claimed property. Distinguish file boundedness, write failure, command exit and process termination; do not claim all four from one observation. This is a recommendation, not an added criterion or a second admission authority.

These are fixable provenance/scope/proof defects, not a necessary trade between calibration and operability: retain the useful cap and timeout, narrow the causal and historical language, and name what the evidence actually establishes. No round verdict or admission is made here.

## Commands executed by this critic

Working directory for every command below: `/home/vgpnk/Projects/shokunin/kama-shokunin`. Commands were read-only, under ten-second timeouts; no fixture, Python, counter, server, clone, build or test was run by this seat.

### Full historical-spec rule sweep

```sh
timeout 10s jq -r '{attempt2_items: (.items | length), explicit_bound_mentions: ([paths(strings) as $p | {path: $p, text: getpath($p)} | select(.text | test("ulimit|RLIMIT_FSIZE|file[- ]?size|size cap|MARKER"; "i"))] | map(.path)), reviewer_prompt_found: ([.items[] | select(.name == "ReviewA3Diff")] | length)}' .ufo/waves/round-27/w1-controls/spec.json && printf 'EXIT=0\n'
```

Observed output, exit 0:

```json
{"attempt2_items":37,"explicit_bound_mentions":[],"reviewer_prompt_found":1}
```

The full decoded context and ReviewA3Diff prompt were also read, rather than relying on a clipped grep excerpt. The context says: `Cap processes, memory and wall time with timeout; no unbounded recursive test runs` (`w1-controls/spec.json:4`). No claim about an unobserved host limit follows from this textual sweep.

### Reviewed corpus extent

```sh
timeout 10s wc -lc corpus/lessons/round-27.md corpus/QUALITY.md && printf 'EXIT=0\n'
```

Observed output, exit 0:

```text
   92  6346 corpus/lessons/round-27.md
  219 45169 corpus/QUALITY.md
  311 51515 total
EXIT=0
```

The lesson ended at the Mistakes row; no §Fix receipt existed in those reviewed bytes.

### Input fingerprints

```sh
timeout 10s sha256sum .ufo/waves/round-27/a3/mistake-runaway/sitecustomize.py.head4k .ufo/waves/round-27/a3/mistake-runaway/REMOVED-RUNAWAY.txt .ufo/waves/round-27/w1-controls/spec.json .ufo/waves/round-27/w1a3/spec.json corpus/lessons/round-27.md corpus/QUALITY.md && printf 'EXIT=0\n'
```

Observed SHA-256 values in that order, exit 0:

```text
63ec95fe426aeaabcc09a556eb4250518a5ef16f7e5f18c60bca08ab0db5dc13
774e473a83355ff4df78397a4701911f228b835ad1f717266ffc5c06dd737e94
22ea69c6689dab3b887a5f3e9e8bd83d2a770631015bec63d24ed6631c656c9a
241cd2fd9a43867affe61418375f79807f413ac3b60c4270a7dc5693d3e7e21e
a0b3c748ad4b638320c66449304869f489f8a7fa1ab9266cc56d0d27acb273f7
9083d8b3c2c67496c69059f2ec4f0f27c2b1664a4c20948fcd0fc6454a4e0e57
EXIT=0
```

```sh
timeout 10s sha256sum .ufo/waves/round-27/w1a3/out/ExecFixtureBoundDemo/receipt.json .ufo/waves/round-27/w1a3/out/ExecFixtureBoundDemo/receipt.log .ufo/waves/round-27/w1a3/out/ExecFixtureBoundDemo/fixture.template.py .ufo/waves/round-27/w1a3/out/ExecFixtureBoundDemo/probe-efbig-site.log && printf 'EXIT=0\n'
```

Observed SHA-256 values in that order, exit 0:

```text
b972f2ea9a2d424a67804eb817fcdfca6db062045ce93c50ed2ca5fb3e7cd33f
655a2ca3020add97df7d7d246fa435d1282d2871189f690b9d3dfb6134abe3b1
93af186904dbcb0e030b6a41789c5a4ba97da245a191b648be1b4cb72a3df8e4
a218d11ef6b6ef854906cea5e3b38ac68f682ad9c37b3f0e55f5d72e455509a7
EXIT=0
```

The Bash `help ulimit` read also completed with exit 0: `-f` limits the maximum size of files written by the shell and its children; this Bash uses 1024-byte increments, or 512 in POSIX mode. No tool was installed or updated. No processes were left running by this seat. Only this report was written.
