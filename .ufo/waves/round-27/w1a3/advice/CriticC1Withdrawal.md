VERDICT: partial — committed evidence supports a pre-data withdrawal with unchanged A3 rules, but “neither meets nor misses” introduces a disposition exemption not present in the retained landed-tip kill rule.

## Scope and axes

Review of C1 disposition only, at `324d5d62e61276af312c8eb42f678004aec245d1`; not a C1/X1 judgment or admission decision. Axes implicated: **depth** (C1's claimed request-validation surface) and **calibration** (accurate chronology, version identity, and self-assessment). No axis scores assigned.

**Direct answers:**

- No C1 data-seat dispatch is present in the committed interval `a720399e..324d5d62`. The recorded 37-seat wave is controls, reconnaissance, tooling, repairs and review—not a data wave. The earlier recorded dispatch timestamp belongs to the earlier control evidence. [INFERENCE] The committed history supports the stated pre-data stop; it cannot prove that an unrecorded dispatch never occurred.
- The entire preregistration and counter are byte-identical between `0ec32cac` and `324d5d62`. Therefore predicate, target **15**, pins, and kill rule are unchanged over that interval. “Unchanged” must mean **A3 unchanged since that revision**, not unchanged throughout round 27: A0→A1→A2→A3 modifications are explicitly committed.
- No committed C1 claim-judgment artifact precedes withdrawal in the inspected history. Earlier **control scores** and author **pilot/base receipts** do exist; “before data” must not be rewritten as “before any scoring.” No numerical re-scale or post-data target reduction was found.
- The unresolved defect is the new categorical **“neither meets nor misses”** outcome. Its compatibility with the original kill rule is for the canonical judge, not this seat or the proposal author.

## Strongest counterexample: unchanged rule, new exemption

The same retained `.ufo/waves/round-27/preregistration.json:16-17` says:

> target: counted >= 15 at the landed lane tip
>
> counted < 15 at the landed tip is a miss: reported as a miss, never amended, never re-scaled.

It does **not** provide a pre-data-withdrawal exception. The new `corpus/lessons/round-27.md:19-21` nevertheless says the claim “neither meets nor misses” because it is not pursued. Round prompt `/home/vgpnk/Projects/shokunin/.ufo/prompts/kama-round-27.md:351,357-360` says not to narrow after landing and to judge the declared counter, kill rule and predicate. The prompt's admission clause at `:37-40` also reserves the ruling to the operator.

**Counterexample:** a reviewer can accept every factual chronology and hash below and still reject the implication “no data seat ⇒ the landed-tip miss rule is inapplicable.” That implication is not in the frozen rule. Changing outcome eligibility in prose is not made safe merely by leaving `TARGET = 15` untouched. [INFERENCE] If the canonical judge does not recognize pre-data withdrawal as a permitted disposition, the lesson's exemption would function as a post-freeze relaxation of the kill rule, even though there was no post-data numerical re-scale.

This is **not** a counter run or a C1 miss verdict. I did not run `count-c1.py`, compute a current-tip C1 result, or turn historical pilot/base receipts into claim data.

**Smallest safe correction:** replace the self-awarded “so it neither meets nor misses” with “C1 is withdrawn and not scored here; its A3 target and kill rule remain unchanged, and final disposition is reserved to the canonical judge.” Qualify “unchanged” as “since A3 / `0ec32cac`.” If the canonical judge rejects withdrawal under §9, that is a contract constraint, not something repairable by editing the target, resetting the freeze, or retrospectively calling old controls data. Do not transfer C1's promised depth credit to X1.

## Evidence: chronology and dispatch

Commands below were read-only and exited **0**. `$R` in explanatory text means `/home/vgpnk/Projects/shokunin/kama-shokunin`; commands show the actual absolute argument. Output excerpts are explicitly trimmed.

### 1. Complete commit interval

```sh
timeout 45s git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --reverse --format='%h author=%aI committer=%cI %s' a720399e..324d5d62
```

Output (subjects trimmed; all six commits retained):

```text
530eaa9 author=2026-10-23T01:21:10-03:00 committer=2026-10-23T01:54:08-03:00 round-27: C1 freeze A0
6020243 author=2026-10-23T02:12:38-03:00 committer=2026-10-23T02:12:38-03:00 round-27: C1 pre-data amendment A1
 a712902 author=2026-10-23T02:19:58-03:00 committer=2026-10-23T02:19:58-03:00 round-27: C1 pre-data amendment A2
1471f67 author=2026-10-23T02:37:01-03:00 committer=2026-10-23T02:37:01-03:00 round-27: C1 pre-data amendment A3
0ec32ca author=2026-10-23T02:41:50-03:00 committer=2026-10-23T02:41:50-03:00 round-27: wave 1 (pre-data control wave + repairs + recon)
324d5d6 author=2026-10-23T03:54:42-03:00 committer=2026-10-23T03:54:43-03:00 round-27: attempt 3 — C1 withdrawn before data
```

```sh
timeout 45s git -C /home/vgpnk/Projects/shokunin/kama-shokunin show -s --format='%H%nparents=%P' 324d5d62
```

```text
324d5d62e61276af312c8eb42f678004aec245d1
parents=0ec32cac09b58a213450ff9f67c319100f21ac27
```

The withdrawal is the direct child of the control-dispatch commit, not a rewrite of that commit.

### 2. Historical dispatch-path changes, including additions/deletions

```sh
timeout 45s git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --reverse --format='%H %s' --name-status a720399e..324d5d62 -- '.ufo/waves/round-27/*dispatch*' '.ufo/waves/round-27/**/dispatch*' '.ufo/waves/round-27/**/spec.json' '.ufo/waves/round-27/**/spawn-result.txt' '.ufo/waves/round-27/**/plan.json'
```

Output (commit subjects omitted here; path rows complete):

```text
6020243e74a470507b9d6d89cd7904b8a878d39b
A .ufo/waves/round-27/controls-dispatched-at.txt
0ec32cac09b58a213450ff9f67c319100f21ac27
A .ufo/waves/round-27/w1-controls/dispatch.json
A .ufo/waves/round-27/w1-controls/dispatched-payload.json
A .ufo/waves/round-27/w1-controls/spawn-result.txt
A .ufo/waves/round-27/w1-controls/spec.json
324d5d62e61276af312c8eb42f678004aec245d1
A .ufo/waves/round-27/a3/plan.json
```

A second history query covered all wave paths, not just dispatch filenames:

```sh
timeout 45s git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --reverse --format='%H %s' --name-status a720399e..324d5d62 -- '.ufo/waves/round-27/w*' '.ufo/waves/round-27/*plan*' '.ufo/waves/round-27/*final*'
```

Output: only the six `w1-controls/` files added at `0ec32cac` (`dispatch.json`, `dispatched-payload.json`, `solution-spaces.json`, `spawn-result.txt`, `spec.json`, `validate.err`) and `a3/plan.json` added at `324d5d62`; no deletion or other wave/final path.

### 3. Actual launch acknowledgment and assignment contents

- `.ufo/waves/round-27/controls-dispatched-at.txt:1`: `2026-10-23T04:55:48Z`.
- `.ufo/waves/round-27/w1-controls/spawn-result.txt:1`: `2026-10-23T05:41:33.096709Z`.
- The serialized acknowledgment on `spawn-result.txt:2` was parsed with Python `ast.literal_eval`, as data, from the committed blob obtained by:

```sh
timeout 40s git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 324d5d62:.ufo/waves/round-27/w1-controls/spawn-result.txt
```

Decoded analysis output:

```text
Committed spawn acknowledgment: 2026-10-23T05:41:33.096709Z Spawned 37 background agents using critic, mutation-tester, scout, scribe, executor, reviewer, sentinel, connector.
Spawned-name count: 37
```

The committed dispatched payload, not merely the proposed spec, classifies those 37 tasks as:

| count | declared service |
|---:|---|
| 19 | C1 pre-data controls / mutations |
| 5 | C1 static reconnaissance, no server or registry rows |
| 1 | C1 probe tooling for future wave-2 data executors, not data |
| 7 | routed repairs, not claims |
| 1 | A3 counter correctness review |
| 1 | A3 measurement-integrity review |
| 1 | frontier SOURCES census/recheck |
| 1 | frontier mistake mining |
| 1 | sibling pre-data control scan |

Pointers: `w1-controls/spec.json:4` and `w1-controls/dispatched-payload.json:2` expressly say no data seat runs in the wave. `spec.json:104,109,114,119,124` marks reconnaissance as static/no registry rows. `spec.json:162-164` / `dispatched-payload.json:191-193` identifies the potentially misleading executor name **ExecProbeTool**: it tests the existing pilot rows and one junk row, not a new C1 data set. The context also expressly forbids copying control rows into the claim registry.

This establishes the scope of the recorded dispatch, not faithful execution of every dead seat's assignment. The earlier timestamp-only record is less complete than the A3 payload; the associated committed reports identify control work (`controls/KamaR27CtlDoNothing/REPORT.md:1-15`; `controls/KamaR27CtlLabelKeyed/REPORT.md:1-24`).

### 4. Complete committed artifact and JSON-receipt inventory

Read-only Eval/Python invoked:

```sh
timeout 40s git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree -r --name-only 324d5d62 -- .ufo/waves/round-27/
timeout 40s git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree -rz 324d5d62 -- .ufo/waves/round-27/
timeout 40s git -C /home/vgpnk/Projects/shokunin/kama-shokunin cat-file --batch
```

For `cat-file --batch`, stdin was every `*.json` blob ID from that NUL-delimited `ls-tree`, one ID per line, in tree order. The Eval parser consumed each length-delimited blob, decoded JSON, and selected objects with `schema == "kama-r27-c1-receipt/v1"`; it did not execute any file. Each subprocess exited **0**, with 45-second subprocess deadlines, 512-MiB address-space and 30-second CPU limits.

Analysis output:

```text
tracked_round27_paths: 1485
control_wave_output_paths: 0
other_wave_paths: []
final_paths: []
JSON blobs inspected: 530
Invalid JSON: []
C1 receipt blobs: 258
A3 receipt paths:
.ufo/waves/round-27/before/c1-base-A3-receipt.json
.ufo/waves/round-27/pilot/pilot-A3-receipt.json
```

All 252 C1 receipt JSONs under the committed `controls/` subtree use other hashes; none uses the frozen A3 hash. The only A3 receipts are the author base/pilot receipts above—not non-author shortcut-control receipts and not a dispatched data seat. This supports the missing-control-receipt reason in `a3/plan.json:8` and `corpus/lessons/round-27.md:14-19`. The requirement that data wait for committed control receipts is independently present at `corpus/lessons/round-26-verifier-spotcheck.md:234`.

## Evidence: unchanged rule and unlanded C1 surface

### 5. Identity since `0ec32cac`

```sh
timeout 45s git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --exit-code 0ec32cac 324d5d62 -- .ufo/waves/round-27/preregistration.json .ufo/waves/round-27/count-c1.py
```

Output: **empty**, exit **0**.

`git ls-tree` was run at each revision on the two paths. Both revisions returned:

```text
100755 blob 7c40aed9415f23034cdaa088197b63bcede15e8b .ufo/waves/round-27/count-c1.py
100644 blob e1f03b14aeab837094fa5310165f723db0d14cf9 .ufo/waves/round-27/preregistration.json
```

Exact hashing commands, each exit **0**:

```sh
timeout 45s git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 0ec32cac:.ufo/waves/round-27/count-c1.py | sha256sum
timeout 45s git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 324d5d62:.ufo/waves/round-27/count-c1.py | sha256sum
```

Both outputs:

```text
49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765  -
```

```sh
timeout 45s git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 0ec32cac:.ufo/waves/round-27/preregistration.json | sha256sum
timeout 45s git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 324d5d62:.ufo/waves/round-27/preregistration.json | sha256sum
```

Both outputs:

```text
a0b3889a87fcd78470a248b760733a0c2f1bba05c4e3896e7db73b4e177fa6c9  -
```

Relevant lines: `preregistration.json:12-18` (predicate, label, command, target, kill rule, hash); `count-c1.py:65,88-90` (claim threshold, base, `TARGET = 15`, `MIN_BYTES = 20`).

### 6. Do not overclaim historical immutability or absence of scoring

```sh
timeout 45s git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --reverse --format='%H %s' --name-status a720399e..324d5d62 -- .ufo/waves/round-27/preregistration.json .ufo/waves/round-27/count-c1.py
```

Output: both files added at `530eaa99`; both modified at `6020243e`, `a712902c`, and `1471f676`; no later modification in the interval. Exit **0**.

`preregistration.json:41,44,49` explicitly retains the amendment history, including earlier control scores and redesigns. `controls/KamaR27CtlLabelKeyed/REPORT.md:6-14` records A0 `21/15` and A1 `20/15` control results. These are historical control reports, not new runs by this seat and not C1 data. The round prompt's “after any seat has scored” sentence must therefore not be paraphrased as “there were no earlier scores.” Whether its pre-freeze-redesign provision licenses the earlier amendments is separate from the **unchanged-since-0ec** withdrawal question.

### 7. No C1 surface landed in this interval

```sh
timeout 45s git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --reverse --format='%H %s' --name-status a720399e..324d5d62 -- SKILL.md registry/error-signatures-r27.json
```

Output: **empty**, exit **0**.

```sh
timeout 45s git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree 324d5d62 -- SKILL.md registry/error-signatures-r27.json .ufo/waves/round-27/w1-controls/advice/ .ufo/waves/round-27/w1-controls/out/ .ufo/waves/round-27/final/
```

Output:

```text
100644 blob 186906468b36f94193a67878059840a3ec6c5075 SKILL.md
```

Exit **0**. No round-27 claim registry, control-wave output/advice, or final directory is committed at this tip. This corroborates missing landed data; it is not a C1 measurement.

## Provenance limits and small timestamp discrepancy

A read-only `git diff --exit-code 324d5d62 --` over the inspected preregistration, counter, plan, control spec/payload/dispatch/spawn files, control timestamp, two cited control reports, and lesson returned empty output, exit **0**. Their local path:line pointers therefore matched the committed tip when inspected.

`a3/plan.json:4` says `written_utc = 2026-10-23T06:57Z` while the landing commit's committer date is `06:54:43Z`. This small discrepancy does not establish post-judgment editing, but the prose time should not be used as a precise chronology witness; use commit topology and recorded dispatch bytes. Smallest correction: use the actual landing time or omit the hand-written time.

No untrusted scratch directories were read or cited. No runtime history absent from committed bytes is asserted. No server, model runtime, counter main, canonical judge, tests/build, or nested seat was invoked. Python Eval was used only for data parsing and read-only Git subprocesses. No tools were installed or updated. All subprocesses completed; no service/process tree was left running. Only this report was written; lane/index/history and claim artifacts were not modified.
