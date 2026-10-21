# CritSeparability — is decode-refusal + replace isolation + lazy-fetch suppression one claim?

Seat: CloseKama22.CritSeparability (critic). Base master=4fe9339f8fc3a4a4a479d9c938a850da12f1124d, git 2.56.0, Python 3.14.
Date: 2026-10-21. No installs.

## Verdict

The three fixes are **causally separable**: they are independent mechanisms, no fault needs two of them, and no fix changes another fix's fault cell. As bundled, they **move different axes**, and the bundle **hides one harmed cell**: the lazy-fetch fix turns a legitimate blob-filtered partial-clone lane from `clean` (exit 0) into a refusal (exit 2). Under the current oracle ("crash/flip/execute → typed refusal or correct verdict"), the bundle also passes while three same-class faults stay open (grafts, shallow, `log.showSignature`+`gpg.program`). That fits a narrow claim, but only if the claim names exactly the mechanisms it closes.

**Smallest safe correction:** keep it as ONE calibration claim only if all of the following hold:

1. Each fault gets a pinned expected outcome: the exact exit code plus the exact defect set. "Refusal or correct verdict" is not enough.
2. f1 (log encoding) is fixed by `-c i18n.logOutputEncoding=UTF-8` and must yield the correct verdict, not a refusal.
3. The lazy-fetch fix is scored on its own two axes: whether a command executes (marker file) and object identity. The partial-clone refusal is declared as an accepted tradeoff, or the claim is split.
4. The scope text says "replace refs", not "history identity". Grafts, shallow and `gpg.program` are listed as explicitly NOT covered.
5. `log.follow=false` is kept only with a fixture that actually flips. L1's f6 does not flip; f6b below does.

## Method

- Scratch clone `/tmp/kama-r23/CritSeparability` with a variant toggle in `git()` (`out/CritSeparability/variant-toggle.diff`), selected by `KAMA_VARIANT` letters:
  - `D`: `UnicodeDecodeError` → `EvalError` (strict decode refusal)
  - `E`: `-c i18n.logOutputEncoding=UTF-8`
  - `R`: `--no-replace-objects`
  - `L`: `--no-lazy-fetch`
  - `F`: `-c log.follow=false`
- Grid harness: `out/CritSeparability/grid.sh`, run with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`. Each fault × variant cell is a fresh temp repo. Remotes are only `example.invalid` or local `file://`.
- Command: `bash grid.sh` → run dir `/tmp/kama-r23/CritSeparability-work/run.zznf`.

Cell format below: `exit[TB=traceback][X=marker file created]/status:defect-kinds`.

```
fault               none           D             E       DE      R              L              RL             DERL           DERLF
control             0/c:           0/c:          0/c:    0/c:    0/c:           0/c:           0/c:           0/c:           0/c:
f1-logenc           1TB/-          2/-           0/c:    0/c:    1TB/-          1TB/-          1TB/-          0/c:           0/c:
f2-reportbytes      1TB/-          2/-           1TB/-   2/-     1TB/-          1TB/-          1TB/-          2/-            2/-
f3-replace-omit     0/c:           0/c:          0/c:    0/c:    1/f:omit       0/c:           1/f:omit       1/f:omit       1/f:omit
f4-replace-fake     0/c:           0/c:          0/c:    0/c:    1/f:hash,unre  0/c:           1/f:hash,unre  1/f:hash,unre  1/f:hash,unre
f4b-replace-report  0/c:           0/c:          0/c:    0/c:    1/f:hash,unre  0/c:           1/f:hash,unre  1/f:hash,unre  1/f:hash,unre
f5-lazy-exec        1X/f:hash,unre 1X/f:..       1X/f:.. 1X/f:.. 1X/f:..        1/f:hash,unre  1/f:hash,unre  1/f:hash,unre  1/f:hash,unre
f5b-lazy-supplies   0/c:           0/c:          0/c:    0/c:    0/c:           1/f:hash,unre  1/f:hash,unre  1/f:hash,unre  1/f:hash,unre
g1-grafts           0/c:   (all variants 0/c: — false clean survives every fix)
g2-shallow          0/c:   (all variants 0/c: — false clean survives every fix)
g3-legit-partial    0/c:           0/c:          0/c:    0/c:    0/c:           2/-            2/-            2/-            2/-
g4-showsig-exec     0X/c:  (all variants 0X/c: — repo-configured gpg.program executes under every fix)
g5-foreign-latin1   1TB/-          2/-           1TB/-   2/-     1TB/-          1TB/-          1TB/-          2/-            2/-
```

Fault fixtures I added beyond L1's probe:

- **f4b**: a replace ref on the fleet report commit changes the *report bytes* that `git show HEAD:<rel>` reads. A report citing a fabricated hash then audits clean.
- **f5b**: a promisor remote (`file://`) holds a commit that exists nowhere locally. A citation of it resolves through lazy fetch, giving a false clean.
- **g1**: `.git/info/grafts` reparents past an omitted `round-1:` commit.
- **g2**: `.git/shallow` truncates lane history.
- **g3**: a legitimate `clone --filter=blob:none` lane whose committed `corpus/SOURCES.md` has a Registry URL containing a 40-hex token.
- **g4**: `log.showSignature=true`, `gpg.program=<script>`, and a lane commit carrying a `gpgsig` header.
- **g5**: a foreign-author commit whose message is raw latin-1 with no `encoding` header.

## Findings

### 1. Causal separability holds, but each fix moves a different axis

Each fault column changes only under its own letter:

- `R`: f3, f4, f4b
- `L`: f5, f5b, and the harmed cell g3
- `D` and/or `E`: f1, f2, g5
- `F`: f6b (finding 6)

No interaction was observed: `RL`, `DERL` and `DERLF` equal the union of the single-letter effects.

The improved axes differ by fix:

- `D`/`E` improve the **exit contract**. An error stops masquerading as exit 1 `failed`.
- `R` improves **verdict correctness**. A false clean becomes `failed`.
- `L` improves **side-effect freedom** (f5: the verdict is `failed` in both arms, and only the marker changes) and **object identity** (f5b: a false clean becomes `failed`).

Impact: the verdict-based metric alone cannot register f5's improvement. f5 must be scored on the marker, or it contributes zero to calibration.

### 2. Hidden harm in the lazy-fetch fix: legitimate partial clones flip `clean` → exit 2

g3 with no fix gives exit 0, `clean`, `source_url_hashes=['1234567890abcdef1234567890abcdef12345678']`. With `L`:

```
could-not-evaluate: git cat-file blob 14b6516f… in …/g3-legit-partial.L/lane: rc=128 fatal: git cat-file 14b6516f…: bad file
```

Source: `load_source_urls` (`tools/report-landing-audit.py:222`) needs the SOURCES.md blob, which a blob-filtered clone lacks. `git show HEAD:<rel>` (line 266) has the same exposure on a partial-clone fleet.

This is an operability regression on a configuration the context does not list as illegitimate. The context only blesses alternates and `clone --shared`. The real lane and fleet are **not** partial clones (no `extensions.partialClone`, `promisor` or `filter` keys in `git config --local --list`), so the historical ledger stays unchanged.

Impacted axis: operability (8), which is otherwise not under test. Correction: declare it in the claim as an accepted refusal (a typed exit 2 that never becomes a verdict), or split `L` into its own claim. Do not leave it out of the controls.

### 3. f1 and f2 are different causes; a refusal for f1 is the weaker outcome

f1 is repo-local *config* (`i18n.logOutputEncoding`) re-encoding an irrelevant foreign commit:

- `D` alone gives exit 2 (`could-not-evaluate: git log --format=… master … not UTF-8: … byte 0xe9`).
- `E` gives the **correct** verdict, exit 0 `clean`.

f2 and g5 are *content* (invalid UTF-8 bytes stored in objects). Only `D` changes them, to exit 2, and `E` cannot. A candidate that ships `D` without `E` passes "typed refusal or correct verdict" on f1 while refusing a repo it could have judged.

Correction: pin f1's expectation to exit 0 `clean`, and f2/g5 to exit 2.

Tradeoff to record, not a defect: g5 shows that one foreign non-UTF-8 commit message *anywhere* on the lane's `master` makes the audit refuse permanently (`round_commits` decodes every record, line 148). That is honest, but a verdict was achievable there (only ASCII prefixes are matched). Real histories contain 0/96 (lane) and 0/1025 (fleet) non-UTF-8 commit messages, measured with `git log --format='%H%x00%B%x01' master` plus a Python strict decode, so there is no current harm.

### 4. "Replace isolation" is narrower than the identity class it sits in

The strongest counterexamples:

- **g1 grafts**: false clean under every variant, including `R`. With grafts removed, the same fixture gives exit 1, and `git --no-replace-objects log` still shows the grafted history (`bc45b42 later` → `db796f8 round-1: work`, skipping `4312b0a round-1: more`). git 2.56 still honors grafts and prints only a deprecation hint. `GIT_GRAFT_FILE=/nonexistent` restores the true history, but `git_env` strips all `GIT_*` variables, so this would have to be set explicitly.
- **g2 shallow**: false clean under every variant. With `.git/shallow` removed, the audit reports 2× `landed-omitted`, exit 1. `git rev-parse --is-shallow-repository` returns `true` for g2 and `false` for g1, which makes it a cheap refusal predicate.

Impact: if the claim text says "audited repos cannot redirect history/object identity", these are open counterexamples, i.e. premature saturation. If it says "replace refs", the claim is accurate.

Correction: either name only replace refs and list grafts and shallow as residual, or add `GIT_GRAFT_FILE=<nonexistent>` plus a shallow refusal as two more pre-registered faults. Neither belongs inside `R` silently.

### 5. "Lazy-fetch suppression" does not equal "no repo-configured command executes"

g4: a marker file is created under **every** variant, including `DERLF`. I re-ran it with the marker deleted first, and the audit alone recreated it, exit 0 `clean`. `git -c log.showSignature=false log …` does not create it.

So `--no-lazy-fetch` closes one execution path (`core.sshCommand` through promisor fetch), not the class. If the claim or the `git_env` docstring is worded as an execution guarantee, g4 falsifies it.

Correction: scope the claim to "promisor lazy fetch". Adding `-c log.showSignature=false` would be a fourth separable mechanism with its own fault. Note that `ScoutShowSignature` owns the detailed analysis of this path.

### 6. `log.follow=false` was bundled without a flipping fixture

L1's f6 is clean both before and after, so it measures nothing: `run.xpxV/f6-follow.out` is `status: clean`. My f6b flips:

- Setup: the report is first added at `old/k.md` at time 2000, then renamed into `.ufo/reports/round-1/kama.md` at 3000. A `round-1:` lane commit is authored at 2500. The fleet has `log.follow=true`.
- With no fix: `cutoff 2000 required 1 post 1`, exit 0. That is a false clean, because the docstring says the cutoff is the commit that first added the report path.
- With `F` or `DERLF`: `cutoff 3000 required 2 post 0`, exit 1, the same as with the config removed (exit 1).

`F` is separable and real, but it needs f6b (or an equivalent) in the frozen grid. Otherwise it is an unmeasured rider.

### 7. Fixture fragility that can fake a pass for `R`

`/tmp/kama-r23-probe/probe.sh:42` runs `git commit-tree` with no identity variables while `GIT_CONFIG_GLOBAL=/dev/null` is set. In my environment this fails:

```
fatal: unable to auto-detect email address (got 'vgpnk@plazir27.(none)')
```

When it fails, no replace ref is created, and the "fault" silently becomes a plain omission that is correctly `failed` in **both** arms. My first grid run did exactly this: f3 showed `1/f:omit` under no fix. A frozen-vs-current comparison would then credit `R` for a fault that never existed.

Correction: export `GIT_{AUTHOR,COMMITTER}_{NAME,EMAIL}` in the probe, and assert the precondition (for example, a frozen-arm f3 result of exit 0 `clean` and a non-empty `refs/replace`) before scoring. Relevant to `RevProbeScript`.

### 8. Controls and no-harm under the full bundle (observed)

- The control cell is `0/c:` in all nine variants.
- `--selftest` reports `selftest cases=50 failed=0` with no fix and with `DERLF`.
- Real ledger: running the scratch script with `--lane-repo <lane> --fleet-repo <fleet>` (rounds 10-, committed errata) gives rc=0 under both, and the JSON documents are **identical** (`identical_docs True`). Summary: 13 reports, 9 defects, 9 corrected, 54 required commits, status clean.

## Not verified

- Signed commits under `log.showSignature` with a *real* gpg (g4 used a fake `gpgsig` header and a script).
- Partial clones with `tree:0` filters, and partial-clone fleets: `show HEAD:<rel>` exposure is inferred from code, not run.
- Promisor lazy fetch over ssh/https actually supplying objects. f5b used a `file://` remote only.
- Whether `-c i18n.logOutputEncoding=UTF-8` still re-encodes when a commit has a bogus `encoding` header. Not tested.
- Other repo-local state (`core.fsmonitor`, `include.path`/`includeIf`, mailmap, notes, object-format). Sibling scouts own these.
- Python versions other than 3.14 and git versions other than 2.56.0 (`--no-lazy-fetch` needs git ≥ 2.44 [INFERENCE from release notes, not checked here]).

## Files written

- `.ufo/waves/round-23/build/advice/CritSeparability.md` (this report)
- `.ufo/waves/round-23/build/out/CritSeparability/grid.sh` (fault × variant harness)
- `.ufo/waves/round-23/build/out/CritSeparability/variant-toggle.diff` (scratch-only `KAMA_VARIANT` toggle in `git()`; not a proposed patch)
- Scratch only: `/tmp/kama-r23/CritSeparability` (clone, toggle applied) and `/tmp/kama-r23/CritSeparability-work/` (grid runs `run.zznf`, `run6.*`, `real.*.json`)
