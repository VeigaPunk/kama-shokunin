# Round 64 · wave b · CR03DoNothing · C1 do-nothing control

Seat: CR03DoNothing (leaf, operability, milestone: do-nothing control). Lane base 0c1eff3, freeze f6a4ea9.
Instrument scored: tools/round64-c1-counter.py at the freeze commit, unmutated, run from the freeze checkout
with `--repo <clone> --tip <candidate> --work <scratch>`. No counter or lane source was edited. Candidates were
committed only in my scratch clone (`/fast/scratch/hyaku/kama-r64/b/CR03DoNothing/clone`); no lane commit.
Tools installed: none (python3 3.14 stdlib, git, the counter itself).

## 1. Sanity: the frozen instrument at its own tip

```
tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
```

Base tip 0c1eff3 (the do-nothing control, freeze says met=False): reproduced, met=False.

```
tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 ... errors=1 met=False families[]
error: live: ["bind_claim", "inconsistent:missing-checks", "listener_holders_pinned", "schema"]
```

## 2. Candidates (each a commit in the scratch clone, each scored by the unmutated counter)

| id | commit | what the tool does differently from v3 | live | met |
|---|---|---|---|---|
| K1 | 5165dac1 | v2 file; schema string -> v3; hand-written `holders = [{pid: proc.pid, exe: server, exe_sha256: server_sha}]` + `receipt['listener_holders']` + check | 1/1 | **False** (forge anchor, see 3.2) |
| K1c | 61cfb6c9 | K1 + one comment line containing the text `holders = _proc_holders(port)` | 1/1 | **True** |
| K2 | d23a7d31 | v3; `listener_holders_pinned` check argument replaced by `True` | 1/1 | **True** |
| K3 | 99a34427 | v3; `holders = _proc_holders(port)` replaced by the hand-written child-only list (procfs function left dead; comment keeps anchor) | 1/1 | **True** |
| K4 | a31aa0e2 | v3; right after hold.json is written, a second process is spawned holding a `pidfd_getfd` dup of the child's run-port listener; killed at teardown | 0/1 | **False** (KILLED) |
| K5 | 7d0b092d | K4 but the second holder is spawned only after `hold_released` (after the counter's release) and killed before the tool's port check | 1/1 | **True** |
| K6 | 0df194bf | v2 file with only the schema string changed | 0/1 | False |
| base | 0c1eff3 | the real base (v2) | 0/1 | False |

Exact met lines for the passing and killed candidates (all reproduced once more, see section 5):

```
K1c   (61cfb6c9): tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
K2    (d23a7d31): tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[...same 76/76 table...]
K3    (99a34427): tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[...same 76/76 table...]
K5    (7d0b092d): tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[...same 76/76 table...]
K4    (a31aa0e2): tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 missing_families=[...] eval_selftest=0/3 errors=1 met=False families[]
error: live: ["bind_argv", "bind_claim", "bind_exe", "bind_holders", "bind_maps"]
K1    (5165dac1): tool_present=1 live_ok=1/1 controls_targeted=74/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[... forge=1/3 ...]
error: forge forgeA2: patch did not apply to the tip tool
error: forge forgeB2: patch did not apply to the tip tool
```

(The `families[...]` tails are the identical 76/76 table shown in section 1; full lines are in out/runs/.)

## 3. Findings

### 3.1 The counter accepts a schema-relabelled v2 tool with a hand-written block (K1c, K2, K3)

- K1c is the freeze's own kill-rule case ("a v2-schema or schema-relabelled tool accepted"). It prints met=True,
  76/76 controls, 3/3 evaluator self-test, errors=0. Reproduced twice (61cfb6c9 both runs).
- Why it passes: the live binding is computed by the counter from procfs of the real child, which is in fact the
  pinned llama-server answering the request. The base v2 tool already runs that process. The tool's
  `listener_holders` block is checked only for agreement with the counter's own procfs snapshot (`bind_claim`).
  A block that is true by hand (the child is the only holder) agrees, so `bind_claim` passes.
- The 76 controls still reject, because every control either mutates a receipt field the counter re-derives
  (tamper, shape, timing, ...) or is a live forger whose holder set is observed by procfs (`bind_*`, `forge`,
  `canned`, `proxy`, `detach`, `pathcopy`, `preload`, `stalehold`). None of them asks *how* the tool obtained its
  block. No family exercises the tool's own enumeration code.
- K2 shows the same at the check level: the tool's `listener_holders_pinned` check can be a constant `True`.
  The counter never reads the tool's check value except through `inconsistent:` (stored vs recomputed), and
  recomputation uses the block, which is honest here. So the tool-side check is ungraded.
- K3 shows the enumeration can be replaced by the child-only literal (the procfs function is left in the file,
  dead). Same result.

### 3.2 K1 fails only by text coupling, not by the live check (counter artifact)

- K1 (identical to K1c minus the comment) has live_ok=1/1 and then prints met=False, because
  `forge_variants()` builds forgeA2 and forgeB2 by string-replacing `'holders = _proc_holders(port)'` in the tool
  text. The base-style tool has no such text, so those two forgers are not built, the `forge` family is 1/3,
  and the counter's error message says "patch did not apply to the tip tool" (the message is wrong: the anchor is
  missing, the patch applied). The `relabel` control is likewise keyed on the literal
  `receipt['listener_holders'] = holders` and `check('listener_holders_pinned',`.
- So the counter's verdict for K1 depends on whether certain strings appear in the file. A single comment carrying
  the anchor text (K1c) restores met=True. Both forgery builders are text-keyed; that is an operability defect of
  the instrument regardless of the do-nothing question.

### 3.3 A second holder spawned after raw_a is KILLED (K4)

- K4 spawns a process holding a dup of the child's listener (`pidfd_getfd`, the same socket inode) right after
  hold.json is written. The counter's snapshots catch it: live fails `bind_holders`, `bind_exe`, `bind_argv`,
  `bind_maps`, `bind_claim`. Killed, as the counter should. (Whether raw_a or raw_b saw it depends on timing;
  either is a kill. Both snapshots are downstream of the spawn.)

### 3.4 A second holder spawned after release passes (K5) - not observed by the predicate

- K5 spawns the same second holder only after `hold_released` and kills it before the tool's own port check. I
  traced one run with a scratch driver (copy: out/CR03DoNothing/runs/K5-trace-drive.py, spawn.log): the holder was spawned 55 ms after the counter's release
  (`spawn child=2314131 port=41725 holder=2314740`), the receipt was REQUEST_OK, `port_closed: true`.
- The counter takes raw_a and raw_b strictly before release and checks teardown only as "the recorded holders are
  gone and the port closes". A holder that exists only after release and dies before the port check is therefore
  invisible. Under the frozen predicate the hold window ends at release, so this is a gap in coverage of the
  teardown phase, not a violation of an observed field. I report it as a pass; it is the counter's coverage
  boundary, not a pure bypass.
- A holder hidden between hold.json and raw_b (the probe window) would need timing I could not make deterministic
  (the counter's raw_a→probes→raw_b gap is not measured here; [INFERENCE] it is short, milliseconds). Not built.

### 3.5 What this means under the frozen rules (for the L1 to rule on; not a verdict on C1)

- Kill rule clause "a v2-schema or schema-relabelled tool accepted": K1c is exactly that (a v2 file with the schema string
  relabelled and a hand-written block) and it is accepted with met=True. K3 is a v3-schema tool with a child-only literal
  enumeration; it is accepted too, but it is not a relabel.
  K2 is a v3 tool whose own check is inert and is accepted. K5 is accepted with a holder that exists only in teardown.
- The do-nothing target as frozen is reachable by a change that is observationally identical to the base tool's
  behaviour on the genuine run (the child really is the sole holder at base). The base already has the process
  property the claim names; what the counter discriminates is only the self-description (schema string and
  block), and self-description is graded for agreement, not provenance.
- Possible repairs the L1 may weigh (advisory, untested):
  (a) restate C1 so the claimed work is the process property (already true at base) and drop the v3 block as
      a graded artifact, or grade the block by a planted-canary test in the run path (not available: the tool
      chooses its own port unless `--port` is given, and the counter cannot inject a holder before the tool's
      own enumeration without tool cooperation);
  (b) key the forge and relabel builders on structure (e.g. parse the AST for the holder call and the check
      name) rather than on literal strings, so a comment cannot satisfy them;
  (c) add a control that replaces the tool's enumeration input (for example by running the tool under a
      procfs-view perturbation) - not built, feasibility unknown.

## 4. Mutant table (per the seat instruction: KILLED / SURVIVED, one-line output pasted)

| mutant | output (abridged to met and first error) | status |
|---|---|---|
| K1 v2+schema+hand block, no anchor | met=False, errors=1 "forge forgeA2/forgeB2 patch did not apply" | KILLED by an artifact, not by the live check (live_ok=1/1) |
| K1c same + anchor comment | met=True | **SURVIVED** (pass = counter or target wrong) |
| K2 v3, listener check = True | met=True | **SURVIVED** |
| K3 v3, child-only literal holders | met=True | **SURVIVED** |
| K4 second holder after hold.json | met=False, `error: live: ["bind_argv","bind_claim","bind_exe","bind_holders","bind_maps"]` | KILLED |
| K5 second holder after release | met=True | **SURVIVED** (coverage boundary, see 3.4) |
| K6 v2 + schema string only | met=False, `error: live: ["bind_claim","inconsistent:missing-checks","listener_holders_pinned"]` | KILLED |

## 5. Reproducibility

- K1c: 61cfb6c9, two runs, met=True both. K5: 7d0b092d, two runs, met=True both (plus the trace). K3: 99a34427, two
  runs, met=True both. K1: 5165dac1, two runs, met=False both (same artifact). Freeze tip f6a4ea9: met=True once.
- Base 0c1eff3: met=False once (matches c1-base.txt in the freeze).
- Note on file names: out/runs/out-K5-third-run-mislabelled-BASE0c1eff.txt is a K5 run (tip 7d0b092d, met=True)
  that I initially labelled BASE; out/runs/out-BASE.txt is the real base run (tip 0c1eff3, met=False).

## 6. Evidence and files

- Report: this file. Evidence: `.ufo/waves/round-64/b/out/CR03DoNothing/`
  - `candidates/` the committed tool file for each candidate (K1, K1c, K2–K6) and a diff against the freeze or base.
  - `runs/` each counter output and stderr, the freeze run, the K5 trace (drive script, spawn.log, receipt.json),
    the run scripts, and the witness receipts (`runs/receipts/`).
- Scratch `/fast/scratch/hyaku/kama-r64/b/CR03DoNothing/` removed after receipts were copied.
- Reproduce a candidate: `git -C <clone> show <sha>:tools/kama-completion-live.py` into a clone whose tools/
  is the freeze's, then `python3 tools/round64-c1-counter.py --repo <clone> --tip <sha> --work <w>`.

## 7. Counter lines (one line per scored candidate, final)

```
freeze f6a4ea9: tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True
K1c 61cfb6c9:   tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True
K2  d23a7d31:   tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True
K3  99a34427:   tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True
K5  7d0b092d:   tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True
K4  a31aa0e2:   tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 missing_families=[...] eval_selftest=0/3 errors=1 met=False
K1  5165dac1:   tool_present=1 live_ok=1/1 controls_targeted=74/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False
K6  0df194bf:   tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 missing_families=[...] eval_selftest=0/3 errors=1 met=False
base 0c1eff3:   tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 missing_families=[...] eval_selftest=0/3 errors=1 met=False
```
