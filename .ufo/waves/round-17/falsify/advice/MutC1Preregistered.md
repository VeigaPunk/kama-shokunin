VERDICT: partial — H1–H3 survive both bounded detectors; H4 already describes the landed implementation and is not a new mutant.

# Scope and axes

Seat: `KamaR17.MutC1Preregistered`. Attacked C1's detector coverage at commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3`, not C2, a runtime, or round admission. This is scoped advice for L1, not an integration decision.

Axes named before mutation: **calibration** (which independently specified weakenings the detector notices), **coverage** (case, whitespace, and HTTP-method distinctions), and **isolation/restoration** (pinned scratch bytes, identical detector before/after, exact restoration and teardown). H1–H3 were written manually by this seat, not generated from the C1 authors' mutant recipes. Independent detector invocations ran concurrently, with a barrier between pristine, mutation, and restoration phases.

Claim anchor: `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md:161-165`, quote: “current/pair 1 of 10, current/full **10 of 10**.” Also `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:680`, quote: “current 10 of 10”. The observations below do **not** contradict the count for that enumerated author-written set. They identify additional surviving, applicable mutants and therefore bound any generalization from it.

# Results

`fault-controls.py` was unchanged and ran **all F0–F8**, including F7 and all six F8 variants. The pair means the round-16 frozen probe versus the current probe, over all 72 rows in each arm.

| Candidate | Fault-controls result on candidate bytes | Pair versus pristine | Deciding fault / verdict |
|---|---|---|---|
| H1 — case-insensitive reason comparison | exit 0; F0 healthy; detected 8, accepted 0 | no differences; 55/17 then 72/0 | **SURVIVED**; no deciding fault; F1 remains detected |
| H2 — strip verdict before comparison | exit 0; F0 healthy; detected 8, accepted 0 | no differences; 55/17 then 72/0 | **SURVIVED**; no deciding fault; F4 remains detected |
| H3 — route match ignores method | exit 0; F0 healthy; detected 8, accepted 0 | no differences; 55/17 then 72/0 | **SURVIVED**; no deciding fault; all four F6 runs remain detected |
| H4 — derive served-model expectation from reported verdict | unchanged identity replicate; exit 0; detected 8, accepted 0 | no differences; 55/17 then 72/0 | **N/A as mutation**: this behavior already exists at the assigned commit |

Thus **0/3 applicable new mutants killed**, **3/3 survived**, **0 inconclusive**. H4 is excluded from the mutation denominator; it is not a fourth survivor or a killed mutant.

## H1: F1 distinguishes a forged suffix, not case-only corruption

Source: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:475`, quote: `and record["reason"] == expected["reason"]`.

The only mutation was:

```python
and record["reason"].casefold() == expected["reason"].casefold()
```

Expected detector: the unchanged F0–F8 suite plus the pair. Before injection, I predicted survival because F1 changes more than case. Detector source: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/fault-controls.py:283-284`, quote: `row["reason"] = str(row.get("reason")) + "-forged"`.

Actual F1 stdout excerpt on H1:

```json
{"id":"F1","check_exit":1,"detected":true,"target":"reason"}
```

Its actual diagnostic was: “check exited 1 with JSON; all 3 faulted rows failed the 'reason' conjunct”. Both pair arms retained every normalized record field, not merely the totals. The suite had no observable response to H1. **Coverage finding:** case-sensitive reason exactness is not distinguished by these detectors. [INFERENCE] A case-only change to a nonempty correct reason would distinguish this mutation; that additional fault was not run or added.

## H2: F4 distinguishes lowercasing, not whitespace normalization

Source: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:474`, quote: `record["verdict"] == expected["verdict"]`.

The only mutation was:

```python
record["verdict"].strip() == expected["verdict"].strip()
```

Expected detector: unchanged F0–F8 plus pair; predicted survival because F4 lowercases instead of adding whitespace. Detector source: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/fault-controls.py:285-289`, quote: `row["verdict"] = v.lower()`.

Actual F4 stdout excerpt on H2:

```json
{"id":"F4","check_exit":1,"detected":true,"target":"verdict"}
```

Its actual conjunct notes were `expect-exact-id:drift,verdict expect-different-id:verdict canonical-alias:verdict`. There was no detector delta. **Coverage finding:** whitespace-exact verdict comparison is not distinguished. This mutation does not remove the separate raw-verdict drift or served-model guards. [INFERENCE] A whitespace-padded `MODEL_LOADING` verdict with otherwise correct fields is a suitable distinguishing input; padded `MODEL_OK` can instead trip those other guards. No additional fault was run or added.

## H3: F6 tests the wrong path, not the wrong method on the right path

Source: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:374-376`, quote: `return any(r.get("method") == "GET"`.

The only mutation removed the method conjunct, retaining exactly:

```python
return any(r.get("path", "").split("?", 1)[0] == "/v1/models"
           for r in requests)
```

Expected detector: unchanged F0–F8 plus pair; predicted survival because F6 requests `/health`, not `/v1/models` with another method. Detector source: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/fault-controls.py:242-243`, quote: `hit("/health")`.

Actual F6 stdout excerpt on H3:

```json
{"id":"F6","check_exit":[1,1,1,1],"detected":true,"target":"route"}
```

Each of `expect-exact-id`, `expect-different-id`, `canonical-alias`, and `openmetrics-text` failed the `route` conjunct. The pair also remained unchanged. **Coverage finding:** the GET requirement is not independently distinguished from path presence. [INFERENCE] A cached correct replay accompanied only by a non-GET request to `/v1/models` would distinguish this mutation. That additional fault was not run or added.

## H4: the preregistered change has no behavior-bearing site to change

Source: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:468-469`, quote: `test, record["verdict"])`. The comment at lines 350-352 explicitly says: “So, keyed on the OBSERVED verdict”. These are already the assigned revision's bytes, before any mutation.

I did not fabricate an expected-verdict baseline, inject a cosmetic no-op, or reverse the assigned mutation. Instead, an unchanged `H4-as-landed` copy received the same three-phase controls and pair measurements. Its hash stayed identical throughout. It cannot establish a mutation kill or survival. Nor does this observation alone establish a false acceptance: the independent verdict equality still rejects a reported verdict that differs from the matrix expectation.

# Pristine / candidate / restored evidence

For **each** of the four isolated copies, the same three subprocess commands ran on pristine bytes, candidate bytes, and restored bytes. All outputs parsed; every F0 positive control passed. Each phase's orchestration exited 0. The intentionally negative frozen-probe arm's exit 1 and 17 failures are the expected pair baseline, not an unexpected baseline failure being counted as a kill.

| Copy | Pristine: controls; frozen/current pair | Candidate: controls; frozen/current pair | Restored: controls; frozen/current pair |
|---|---|---|---|
| H1 | 8/0, rc0; 55/17 rc1 / 72/0 rc0 | 8/0, rc0; 55/17 rc1 / 72/0 rc0 | 8/0, rc0; 55/17 rc1 / 72/0 rc0 |
| H2 | 8/0, rc0; 55/17 rc1 / 72/0 rc0 | 8/0, rc0; 55/17 rc1 / 72/0 rc0 | 8/0, rc0; 55/17 rc1 / 72/0 rc0 |
| H3 | 8/0, rc0; 55/17 rc1 / 72/0 rc0 | 8/0, rc0; 55/17 rc1 / 72/0 rc0 | 8/0, rc0; 55/17 rc1 / 72/0 rc0 |
| H4 identity | 8/0, rc0; 55/17 rc1 / 72/0 rc0 | 8/0, rc0; 55/17 rc1 / 72/0 rc0 | 8/0, rc0; 55/17 rc1 / 72/0 rc0 |

Controls' common actual JSON fields in every cell:

```json
{
  "detected": 8,
  "accepted": 0,
  "positive_control": {"check_exit": 0, "detected": true},
  "fault_exits": {
    "F1": 1, "F2": 1, "F3": 1, "F4": 1, "F5": 1,
    "F6": [1,1,1,1], "F7": 1, "F8": [1,1,1,1,1,1]
  }
}
```

Here `fault_exits` is the seat's lossless extraction of each fault's `check_exit`, not a field claimed to exist in the original document. Every F1–F8 `detected` value was true. The comparison output contained `"differences": []` for all 12 candidate-versus-pristine comparisons and all 12 restored-versus-pristine comparisons. Controls comparison included its complete `positive_control` and `faults` values as well as accepted/detected counts. Pair comparison reused the existing detector's `diff_observations`, including its method/path-set normalization and record vector, rather than reducing it to totals. Source: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/c1/mutants.py:113-128,809-846`, quote: “List of observable differences between baseline and mutant runs.” No author-written mutant generation or grid run was invoked.

## Hashes and exact restoration

All pristine and restored copies had SHA-256:

`ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099`

| Copy | Candidate SHA-256 | Restored SHA-256 |
|---|---|---|
| H1 | `036f2103aef304fb545ca65b2a0f206335b3c7c4e84fdd0626ead74eb04c3bd5` | `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099` |
| H2 | `e78796341f17d274de93ed0df556c47265f8f615d81365afc9c698a7042ec6e6` | `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099` |
| H3 | `7f67387a3958e138fe77bab39b77fe6280d54a1e4b8abb880dd0a41f6fd4692d` | `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099` |
| H4 identity | `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099` | `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099` |

All four `cmp -s` checks against the pinned clone's original succeeded after restoration. Restored detectors then reproduced the pristine observations exactly under the bounded comparison.

Other pins:

- Current probe: `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`.
- Frozen round-16 probe: `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64`.
- Unchanged fault-controls: `d3eaadeb8a061b4e322868d569df77afbd7331089d06b06c86a2063fdc31b312`.
- Existing comparison-helper module: `498d1f7fa7f248d7c794db95ac6208a59c13297305226774e6aa4dc6ff88ac1e`.
- Nine-file, 72-row matrix digest, checked by both detector paths: `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32`.

# Commands and exits

All executed lane code lived in the pinned `/tmp` clone. Every child inherited `PYTHONDONTWRITEBYTECODE=1` and `TMPDIR=/tmp/KamaR17.MutC1Preregistered-clone/preregistered/tmp`. Each detector subprocess had a 300-second outer bound and its own process session; the unchanged controls additionally retain their 150-second check bound. No bound expired in any detector run.

## Setup and phase invocations

The following commands actually ran; each exited **0** unless otherwise stated.

```sh
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.MutC1Preregistered-clone && git -C /tmp/KamaR17.MutC1Preregistered-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3
mkdir -p /tmp/KamaR17.MutC1Preregistered-clone/preregistered/tmp && cp -a /tmp/KamaR17.MutC1Preregistered-clone/tests/probe-verdicts /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H1 && cp -a /tmp/KamaR17.MutC1Preregistered-clone/tests/probe-verdicts /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H2 && cp -a /tmp/KamaR17.MutC1Preregistered-clone/tests/probe-verdicts /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H3 && cp -a /tmp/KamaR17.MutC1Preregistered-clone/tests/probe-verdicts /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H4-as-landed
ss -ltnp && python3 --version
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/KamaR17.MutC1Preregistered-clone/preregistered/tmp python3 /tmp/KamaR17.MutC1Preregistered-clone/probe-preregistered.py pristine
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/KamaR17.MutC1Preregistered-clone/preregistered/tmp python3 /tmp/KamaR17.MutC1Preregistered-clone/probe-preregistered.py mutated
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/KamaR17.MutC1Preregistered-clone/preregistered/tmp python3 /tmp/KamaR17.MutC1Preregistered-clone/probe-preregistered.py restored
```

The driver only orchestrated unchanged detectors and stored observations; mutations and their inverses were separate surgical edits shown above. It submitted the following **12 exact child argv commands once per phase**, concurrently, for 36 child invocations in total. Each command's cwd was its corresponding absolute candidate directory. Frozen-probe commands exited **1**, all controls/current-probe commands **0**, in every phase. These child commands plus the exact single-site replacements above allow reproduction without the removed orchestration script.

```sh
/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered-clone/tests/probe-verdicts/fault-controls.py --check /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H1/check.py --probe /tmp/KamaR17.MutC1Preregistered-clone/tools/kama-probe.sh --matrix-dir /tmp/KamaR17.MutC1Preregistered-clone/tests/probe-verdicts --json
/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H1/check.py --probe /tmp/KamaR17.MutC1Preregistered-clone/.ufo/waves/round-16/frozen/kama-probe-before.sh --json
/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H1/check.py --probe /tmp/KamaR17.MutC1Preregistered-clone/tools/kama-probe.sh --json
/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered-clone/tests/probe-verdicts/fault-controls.py --check /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H2/check.py --probe /tmp/KamaR17.MutC1Preregistered-clone/tools/kama-probe.sh --matrix-dir /tmp/KamaR17.MutC1Preregistered-clone/tests/probe-verdicts --json
/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H2/check.py --probe /tmp/KamaR17.MutC1Preregistered-clone/.ufo/waves/round-16/frozen/kama-probe-before.sh --json
/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H2/check.py --probe /tmp/KamaR17.MutC1Preregistered-clone/tools/kama-probe.sh --json
/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered-clone/tests/probe-verdicts/fault-controls.py --check /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H3/check.py --probe /tmp/KamaR17.MutC1Preregistered-clone/tools/kama-probe.sh --matrix-dir /tmp/KamaR17.MutC1Preregistered-clone/tests/probe-verdicts --json
/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H3/check.py --probe /tmp/KamaR17.MutC1Preregistered-clone/.ufo/waves/round-16/frozen/kama-probe-before.sh --json
/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H3/check.py --probe /tmp/KamaR17.MutC1Preregistered-clone/tools/kama-probe.sh --json
/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered-clone/tests/probe-verdicts/fault-controls.py --check /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H4-as-landed/check.py --probe /tmp/KamaR17.MutC1Preregistered-clone/tools/kama-probe.sh --matrix-dir /tmp/KamaR17.MutC1Preregistered-clone/tests/probe-verdicts --json
/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H4-as-landed/check.py --probe /tmp/KamaR17.MutC1Preregistered-clone/.ufo/waves/round-16/frozen/kama-probe-before.sh --json
/usr/bin/python3 /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H4-as-landed/check.py --probe /tmp/KamaR17.MutC1Preregistered-clone/tools/kama-probe.sh --json
```

## Hash, byte-comparison and cleanup commands

All three `sha256sum` commands exited **0**, yielding the pins/restoration table above.

```sh
sha256sum /tmp/KamaR17.MutC1Preregistered-clone/tests/probe-verdicts/check.py /tmp/KamaR17.MutC1Preregistered-clone/tests/probe-verdicts/fault-controls.py /tmp/KamaR17.MutC1Preregistered-clone/.ufo/waves/round-17/c1/mutants.py /tmp/KamaR17.MutC1Preregistered-clone/tools/kama-probe.sh /tmp/KamaR17.MutC1Preregistered-clone/.ufo/waves/round-16/frozen/kama-probe-before.sh
sha256sum /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H1/check.py /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H2/check.py /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H3/check.py /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H4-as-landed/check.py
sha256sum /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H1/check.py /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H2/check.py /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H3/check.py /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H4-as-landed/check.py
```

The second hash command was on candidate bytes, the third on restored bytes. This exact byte-comparison/listener command exited **0**:

```sh
cmp -s /tmp/KamaR17.MutC1Preregistered-clone/tests/probe-verdicts/check.py /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H1/check.py && cmp -s /tmp/KamaR17.MutC1Preregistered-clone/tests/probe-verdicts/check.py /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H2/check.py && cmp -s /tmp/KamaR17.MutC1Preregistered-clone/tests/probe-verdicts/check.py /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H3/check.py && cmp -s /tmp/KamaR17.MutC1Preregistered-clone/tests/probe-verdicts/check.py /tmp/KamaR17.MutC1Preregistered-clone/preregistered/H4-as-landed/check.py && ss -ltnp
```

Subsequent cleanup observations:

```sh
ps -p 3556689,3555182,3554730,3523912 -o pid=,ppid=,args=
# exit 1, no output: these PIDs from the earlier ss snapshot had already exited; no attribution inferred.
pgrep -af '/tmp/KamaR17[.]MutC1Preregistered-clone'
# exit 1, no output: no process matching this seat's clone path.
rm -rf /tmp/KamaR17.MutC1Preregistered-clone && ss -ltnp
# exit 0.
```

The final `ss -ltnp` still showed host/concurrent-wave listeners, not an empty host; none was stopped or modified. Every seat detector process had returned before removal. A final specialized glob for `/tmp/KamaR17.MutC1Preregistered-*` returned **“No files found matching pattern”**. All scratch, raw streams, the preregistration JSON and the driver were removed; the retained evidence is this report's observed outputs, exact commands, edits, and hashes. No lane source, sibling file, fleet file, VCS state, or runtime service was written by this seat; the only lane write is this report.

# Limitations and tooling

- H4's requested before→after distinction is absent in the pinned implementation. Its identity measurements are explicitly not a mutation experiment.
- These are coverage findings, not permission to normalize fields or weaken the GET contract. No detector, matrix, production checker, lesson or scorecard was changed.
- No supplementary discriminating faults, general mutant grid, live-model run, or broader verification suite was run. Proposed additional discriminating inputs are marked [INFERENCE].
- The recorded pair rows' port aggregation printed `rows=1728`, `unique_ports=1598`, `protected_ports_observed=[]` for `{8080,34113}`. The existing checker binds loopback ephemeral ports. The controls' summary does not retain all individual port assignments, so this is not a complete historical bind audit for controls.
- The first attempt to launch the pristine orchestration asynchronously was refused by the tool with “Background job limit reached (100).” No detector launched in that attempt; the synchronous retry completed with exit 0. A later metadata-only Eval extraction reported its 30-second cell timeout after printing the command inventory and output excerpts. This did not run a detector or change any source; all detector outcomes above come from the three completed, exit-0 orchestration runs.
- Installs/updates: **none**. Existing `python3 --version` printed **Python 3.14.8**. No pacman transaction or other package/runtime installation occurred.
