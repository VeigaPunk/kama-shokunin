# CounterDeterminism — round-29 w2 (attempt 2): property probe of `count-c1.py`

Seat: `CounterDeterminism` — kama lane, round 29, attempt 2, wave 2 (leaf; no delegation).
Item: 3 runs with different `--out` paths must be byte-identical except the out path; a
mid-table-row truncation of `SCORECARD.md` must exit nonzero with an error (never silently
pass); `--tip` naming a nonexistent ref must produce a clean nonzero usage error. Report exit codes.

Counter under test: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py`
sha256 `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` — re-hashed after the
probe, unchanged. Lane `HEAD` = `513eba3ba51a142c9936553e3a85918345eb5c4c` (detached); base
`2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`.

Scratch: `/tmp/cd-kama-w2-CounterDeterminism/` — `rc` (clone, detached at 513eba3),
`rc2` (second independent clone), `shallow` (depth-1 clone), `out/` (receipts, stdout/stderr).
All mutants are throwaway branches inside `rc`; the lane was never written.

Everything below is an actual command's output; nothing is inferred except where marked
`[INFERENCE]`.

## Method

```sh
python3 .ufo/waves/round-29/count-c1.py --repo <clone> --tip <rev> --out <file>
```

The counter reads committed objects only (`git cat-file`/`blame`/`grep`, docstring: "Reads
committed objects only"), so the corruption probes were **committed** on throwaway branches
in the scratch clone. A working-tree-only corruption probe is included to demonstrate that
property (probe 9).

## 1. Determinism — three runs, different `--out` paths

| run | `--out` | exit | receipt sha256 |
|---|---|---|---|
| 1 | `$S/out/run1.json` | 0 | `f3c7a43907d44a4780593e4a12d07b71950e7fd32debb27f144c7dc0069dd504` |
| 2 | `$S/out/run2.json` | 0 | `f3c7a43907d44a4780593e4a12d07b71950e7fd32debb27f144c7dc0069dd504` |
| 3 | `$S/out/run3.json` | 0 | `f3c7a43907d44a4780593e4a12d07b71950e7fd32debb27f144c7dc0069dd504` |

`cmp` run1↔run2 and run1↔run3: equal. stdout identical across the three
(`cmp` clean), stderr empty. The receipt has **no** `out` key at all, so "identical except
out path" is met as **fully byte-identical**.

stdout (each run):

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 513eba3ba51a
```

This reproduces the fresh-clone receipt quoted in the task (`statements 69 mismatched_at_base 11
append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True`).

Additional determinism probes, all **byte-identical** to `run1.json` (exit 0 each):

- second independent clone (`rc2`, same detached tip) — `clone2.json`;
- hostile environment and foreign cwd:
  `cd /tmp && env TZ=Asia/Tokyo LANG=C LC_ALL=C GIT_DIR=/nonexistent GIT_WORK_TREE=/nonexistent
  GIT_AUTHOR_NAME=decoy …` — `env.json`;
- active replacement ref: `git replace 2aa46e2 <commit with empty tree>`. Plain git then reads
  `git cat-file -p 2aa46e2` → `tree 4b825dc642cb6eb9a060e54bf8d69288fbee4904` (empty tree), yet
  the counter's receipt is unchanged — `-C … --no-replace-objects` + `GIT_NO_REPLACE_OBJECTS=1`
  work — `repl.json`.

**Verdict: PASS.** Deterministic at a pinned tip, across clones, locale/TZ, cwd, decoy
`GIT_*`, and replacement refs (see §4 for the one unbound input).

## 2. Corrupt `SCORECARD.md` — mid-table-row truncation

All corruption commits are in the scratch clone only. Receipt fields quoted from the written
JSON; stdout quoted verbatim.

| # | corruption (committed) | commit | exit | receipt highlights | stdout |
|---|---|---|---|---|---|
| 2a | truncate inside a row of the *corrections* table (`SCORECARD.md` 107505 → 106401 bytes; cut 70 B into `SA29:…Q:0ccd533544:0`, ASCII) | `91966c5` | **0** | `append_only True`, `correction_rows 6`, `valid_corrections 5`, `false_corrections 1`, `unresolved 7`, `met False` | `statements 69 mismatched_at_base 11 append_only True valid_corrections 5 false_corrections 1 unresolved 7 met False tip 91966c5ee06d` |
| 2b | truncate 30 B into the **final** correction row (107311+30 = 107341 B, ASCII) | `aaa8664` | **0** | `append_only True`, `correction_rows 11`, `valid 10`, `false 1`, `unresolved 2`, `met False` | `… append_only True valid_corrections 10 false_corrections 1 unresolved 2 met False tip aaa8664bdadd` |
| 2c | truncate 25 B into a **base** table header row (`\| Capability \| What it can now do \| …`, 9513 → 9538 B, ASCII) | `146ec24` | **0** | `append_only False`, `correction_rows 0`, `unresolved 69`, `met False` | `statements 69 mismatched_at_base 11 append_only False valid_corrections 0 false_corrections 0 unresolved 69 met False tip 146ec2443238` |
| 2d | truncate to 60000 B inside the base narrative | `60afc68` | **0** | `append_only False`, `unresolved 69`, `met False` | `… append_only False … unresolved 69 met False tip 60afc689c165` |
| 2e | truncate at the **second byte of `→`** in base row 17 (836 B) | `db99e16` | **2** | `error: "'utf-8' codec can't decode byte 0xe2 in position 835: unexpected end of data"` | `could-not-evaluate: 'utf-8' codec can't decode byte 0xe2 in position 835: unexpected end of data` |
| 2f | append 2 invalid bytes **after** all rows (`… \| p:absent \|\n\xff\xfe`) | `f15854f` | **2** | decode error at position 107505 | `could-not-evaluate: 'utf-8' codec can't decode byte 0xff in position 107505: invalid start byte` |
| 2g | drop **only the final newline** | `a612897` | **0** | `append_only True`, `unresolved 0`, **`met True`** | `statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip a6128973c6c9` |

Exact false-correction record for 2a:

```json
{"observed": "required=3", "sid": "SCORECARD.md:Q:0ccd533544:0", "why": "wrong-observed"}
```

**Interpretation.** The counter's exit-2 path is keyed to **decodability**, not to semantic
integrity: an ASCII-boundary truncation that still parses is "evaluable" and exits **0** (its
documented contract: "Exit 0 ran (whatever the count), 2 could not evaluate"); a cut that
splits a UTF-8 codepoint or appends invalid bytes exits **2**. For every truncation that loses
statement or correction bytes the *receipt* flips to `met False` with `unresolved > 0` and a
`false_corrections`/`unresolved_ids` record — **no silent pass of the C1 target was observed**.
The only `met True` truncations (2g; or cutting a row at the end of its observed cell) remove
no statement/correction content — a byte-level but semantically empty loss.

**Verdict on the item's literal expectation ("must exit nonzero with an error"): NOT MET —
mutant survived on the exit-code leg.** The stated safety property ("never silently pass /
fails closed") **holds at the receipt level** but not at the exit-code level. Consequence for
any acceptance gate: a consumer that keys on exit status alone accepts a corrupted tip
(exit 0); it must parse `met`/`unresolved`.

## 3. `--tip` naming a nonexistent ref

| invocation | exit | stdout / receipt |
|---|---|---|
| `--tip refs/heads/does-not-exist --out c1.json` | **2** | `could-not-evaluate: tip refs/heads/does-not-exist unresolved`; receipt keys exactly `['base','counter','counter_sha256','error']` — no counts, no `met` |
| `--tip deadbeef --out c2.json` | **2** | `could-not-evaluate: tip deadbeef unresolved` |
| `--tip "" --out emptytip.json` | **2** | `could-not-evaluate: tip  unresolved` |
| `--repo …/not-a-repo --tip HEAD` | **2** | `could-not-evaluate: tip HEAD unresolved` |
| fresh clone, **no `--tip`** (default `refs/heads/master`; clone is detached, no local `refs/heads/master`) | **2** | `could-not-evaluate: tip refs/heads/master unresolved` |
| `--tip 49f849f292c3…` = lane **master** (513eba3 + one `considerthese` commit; `git diff --stat` = 1 file, +35) | **0** | `statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 49f849f292c3` |

**Verdict: PASS.** Nonexistent/empty tip and a bad `--repo` all exit 2 with a clean
`could-not-evaluate: <reason>` line on stdout and an error-only receipt (no partial counts).
Note: the receipt embeds `tip`, so receipts at different tips are not byte-comparable without
normalizing that field, and the default tip is repo-state dependent — the quoted fresh-clone
receipt is only reproducible with an explicit `--tip` (or a local `refs/heads/master`).

## 4. Unbound input: repository config changes the receipt

`W` comes from `git blame --line-porcelain`, which honors `blame.ignoreRevsFile` — a value
the counter does not neutralize (no `--no-ignore-revs-file`, no `-c blame.ignoreRevsFile=`,
not stripped from the environment).

| probe | exit | receipt |
|---|---|---|
| baseline (no config) | 0 | `mismatched_at_base 11 … unresolved 0 met True` (`f3c7a439…`) |
| `git config blame.ignoreRevsFile .git-blame-ignore-revs`, file lists `ea72c3eae4…` | **0** | `mismatched_at_base 15`, `valid_corrections 11`, `unresolved 4`, **`met False`** (`a915bc76…`); W changed for 2 of the 11 mismatched statements |
| `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=blame.ignoreRevsFile GIT_CONFIG_VALUE_0=/abs/file`, run from `/tmp` | **0** | identical to the previous row (`a915bc76…`) — the env sanitizer strips `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_REPLACE_REF_BASE` but **not `GIT_CONFIG_*`** |
| same config pointing at a missing file | **2** | `could-not-evaluate: git blame …: fatal: could not open object name list: ./missing-ignore-file` |

Direction is fail-closed (more mismatches, never fewer), but identical bytes + identical
command can yield different receipts in a differently configured repo. Host global, system and
lane-local `blame.ignoreRevsFile` are currently **unset** (`git config --{global,system} --get`
and `-C kama-shokunin config --local --get` all empty), so the hazard is latent, not active.
**Verdict: survived (medium)** — determinism holds only for a fixed repo config; config is an
unbound input to `W`.

## 5. Receipt-write and history edges

| probe | exit | observed |
|---|---|---|
| `--out` pointing at an existing receipt | **2** | stderr `refusing to overwrite /tmp/…/run1.json`; existing file sha unchanged (`f3c7a439…`) — no clobbering |
| `--out /nonexistent-dir-xyz/r.json` | **1** | uncaught `FileNotFoundError` traceback (write loop is outside the `try`); nothing printed to stdout, **receipt lost** |
| clone `--depth 1` (base object absent) | **2** | `could-not-evaluate: base SCORECARD.md missing` — fails closed instead of boundary-blame miscount |

## 6. File-scope observations

- Working-tree-only mid-row truncation (tip `513eba3`, uncommitted `SCORECARD.md` 107505 →
  9538 B): exit 0, receipt **byte-identical** to baseline (`b3.json` == `run1.json`). The
  counter genuinely reads committed objects only; "corrupt the clone's file" has no effect
  until committed.
- `SHONEN.md` at the tin: text is never read — truncating it 1855 → 800 B (`ef1cf58`) changes
  only the receipt's `tip` field; every count and `met True` are identical (verified by
  comparing the receipts with `tip` removed). Not a pass-of-target issue (corrections live in
  `SCORECARD.md` by contract), but a corruption there is invisible.

## Findings for the L1 (reported, not fixed)

1. **Exit code is not a corruption signal (medium).** Every ASCII-safe, parseable corruption of
   the tip `SCORECARD.md` exports **0**; exit 2 fires only on decode failure or missing objects.
   The item's expected "nonzero on mid-row truncation" is contradicted by the counter's own
   contract line. If a nonzero-on-corrupt-tip behavior is wanted, that is a contract change to
   be preregistered, not a property this counter has. Any automated gate must read `met`.
2. **`blame.ignoreRevsFile` / `GIT_CONFIG_*` are unbound inputs (medium).** A repo or env
   config turns `11 / met True` into `15 / met False` with identical committed bytes. Fresh
   clones and this host are unaffected today (config unset), and the direction is fail-closed.
3. **Bad `--out` directory loses the receipt (low).** `open(o.out, "w")` sits outside the
   `try/except`; `FileNotFoundError`/`PermissionError` gives exit 1 with a traceback and no
   receipt text anywhere.
4. **Undetected harmless shapes (informational).** Dropping the final newline (or a row's
   trailing delimiter) still reports `met True`; tip `SHONEN.md` and any uncommitted working-tree
   edit are never read.
5. **Default tip is repo-state dependent (informational).** In a clone of this detached-HEAD
   lane there is no local `refs/heads/master`, so the default invocation exits 2; the lane's
   `master` (`49f849f`, one commit past `513eba3`) still reads `met True`. Pin `--tip` in
   receipts; normalize `tip` when comparing receipts.

## Exit-code summary

```
baseline x3, cross-clone, hostile env, replace-ref .......... 0 (identical receipts)
corrupt: corrections row / last row / base table row /
         base narrative (ASCII-safe truncations) ............ 0 (met False, unresolved > 0)
corrupt: UTF-8-split cut / trailing invalid bytes ........... 2 (could-not-evaluate: decode)
corrupt: final newline dropped .............................. 0 (met True, content intact)
corrupt: SHONEN tip truncated ............................... 0 (identical except tip)
corrupt: working tree only, uncommitted ..................... 0 (identical receipt)
nonexistent / empty --tip, bad --repo, default tip absent ... 2 (clean could-not-evaluate)
blame.ignoreRevsFile (config or GIT_CONFIG_* injected) ...... 0 (different receipt, met False)
missing ignore file ......................................... 2
--out exists ................................................ 2 (refuses, file unchanged)
--out dir missing ........................................... 1 (traceback, receipt lost)
shallow depth-1 clone ....................................... 2 (base missing)
```

## Restoration evidence

- Lane counter sha256 `fe11d599…b647383` **before and after** — unchanged.
- Lane `git status --porcelain` set identical before and after (pre-probe: `M LOG.md`,
  `M SCORECARD.md`, `M SHONEN.md`, `M corpus/QUALITY.md`, `M corpus/SOURCES.md`,
  `M tools/prereg-time-check.py`, plus the 7 already-untracked round-29 paths; identical after,
  sorted-listing md5 `e05e0af80f36e16c7a6c3beeaf159480`). No `git add/commit/checkout/reset`,
  no jj operation in the lane.
- Lane file mtimes are 09:04–09:15 −0300; the scratch clone was created 15:32 −0300, so no lane
  file was touched by this seat.
- All mutants are local to `/tmp/cd-kama-w2-CounterDeterminism/rc`, branches
  `corrupt-row 91966c5`, `corrupt-base-row aaa8664`, `corrupt-base-table-row 146ec24`,
  `corrupt-base 60afc68`, `utf8-cut db99e16`, `tail-garbage f15854f`, `clean-a3 a612897`,
  `shonen-trunc ef1cf58`, plus `wt-only`/`corrupt-shonen`/`clean-a2` at `513eba3`. Scratch
  retained for inspection; nothing outside it was deleted.
- Tooling installed: **none** (python3 stdlib + git only; no pacman, uv, npx or binaries).

Evidence files (receipts + stdout/stderr) are in
`/tmp/cd-kama-w2-CounterDeterminism/out/` (`run1..3`, `clone2`, `env`, `repl`, `b1`, `b2`,
`b2v2`, `b2v3`, `utf8`, `garbage`, `nl2`, `sh3`, `ignore`, `envcfg`, `c1`, `c2`, `deftip`,
`tip-master`, `b3`, `ow`, `badout`, `norepo`, `emptytip`, `shallow`).
