VERDICT: n/a — read-only overlap scan: souji confirms no kama claim and contests no artifact; four of its conventions are reusable for C1/C2, and one file is an uncommitted third-party edit kama must not stage.

# ConnectSouji — souji/kama overlap scan (round 17 build wave)

Seat: read-only connector. Scope read: `souji-shokunin/SKILL.md`, `souji-shokunin/PROVINCE.md`, `souji-shokunin/corpus/QUALITY.md`; compared against kama C1/C2, `kama-shokunin/PROVINCE.md`, `kama-shokunin/corpus/QUALITY.md`, `kama-shokunin/SKILL.md`, and the lane's committed/worktree state. No gate, no measurement command, no write outside this file.

## Axes named

- A1 **calibration** (C1: does the detector's verdict name what it actually grades, and is the before/after count byte-addressed).
- A2 **operability** (C2: fail-capable live lifecycle checks and a receipt that survives internal faults).
- A3 **ownership integrity** (no lane absorbs another lane's artifact; no silent staging of third-party changes).
- A4 **evidence verifiability** (a verdict names the bytes it measured and resolves at the measured revision).

Proposed move below improves A1, A3, A4 and leaves A2 untouched.

## 1. Contested scope

### 1a. `.ufo/state/` gitignore line — contested, and it is live right now

- souji never touches it: `souji-shokunin/corpus/QUALITY.md:38` — "Operator-tooling runtime (`.tower/**`, driver and comms logs, `.ufo/state/`) is report-only"; `SKILL.md:69` — "Operator config (`~/.config/**`), the driver (`scripts/`), `.ufo/state/`,".
- kama also never writes it: `kama-shokunin/PROVINCE.md:45` — "kama never writes to `~/.config`, `~/.omp`, or systemd".
- Current lane state: the worktree `.gitignore:2` contains `.ufo/state/`, but `git show master:.gitignore` has only `.ufo/interactive-sessions/`. `git status --porcelain` reports `M .gitignore`, `M AGENTS.md`, `?? .ufo/waves/round-17/`. So the `.ufo/state/` ignore is an **uncommitted third-party edit**, not a landed convention.
- Consequence for C1/C2: any landing commit that stages broadly sweeps a change kama did not author. souji's rule is the reusable one — `souji-shokunin/corpus/QUALITY.md:31` (Q7) — "(b) stages only named paths (`commit -- <paths>`), never `add -A` or `.`".
- It also feeds the kama jj risk: `.ufo/waves/hyaku/jj-w1/reports/JjAuditKama.md:154` — "Under jj, `@` is perpetually ahead of `HEAD` until the helper commits and moves the bookmark"; the round-13 live gate reads `worktree_matches_head` and returns exit 1 `documentation_mismatch` on a divergent worktree. [INFERENCE] The same divergence makes "the current check.py" ambiguous for the C1 mutant count unless the count names bytes (see §3).

### 1b. `registry/history/.lock` — not contested; the round-17 premise is stale

- `registry/history/.gitignore:3` is `.lock`, committed in round 2 (`git log -- registry/history/.gitignore` → `83bee7f round-2`). `git check-ignore -v registry/history/.lock` → `registry/history/.gitignore:3:.lock`.
- souji has no endpoint-registry concept at all: its only "registry" is the gate registry, `souji-shokunin/SKILL.md:126` — "## Gate registry". No handoff exists for `registry/endpoint-consumers.tsv` or `registry/history/`.
- Action: do not cite "`registry/history/.lock` not gitignored" as a round-17 frontier fact without re-running `git check-ignore`; at tip `cff9e62` it is ignored. The `.ufo/state/` half of that same statement is true only of the **committed** blob (`JjAuditKama.md:167` — "`.gitignore` contains only `.ufo/interactive-sessions/`"), not the worktree.

### 1c. Round-17 wave artifacts — no overlap

- souji refuses live lane work: `PROVINCE.md:36` — "Live lane work products (current-round drafts, uncommitted reports)." and `PROVINCE.md:34` — "Any artifact whose owning lane has dirty or unpushed work touching it."
- souji's stale class cannot match these files anyway: `SKILL.md:37` — "scratch type as the tool classifies: `.scratch/`, `*.out`, `*.log`, `launch-*.json`, `*-draft.*`". `frozen/*.py`, `c1/mutants.py`, `c2/*`, `*.json` receipts, and the nine matrix files are outside it.
- Practical rule for C1/C2: never let a count exist only as `*.log`/`*.out`. Write counting output as JSON under `.ufo/waves/round-17/{c1,c2}/` (the contract's own path), where no receipt class reaches it.

### 1d. `~/.config` pins and the retired `qwen-coder` unit — nobody absorbs

souji never touches operator config (`PROVINCE.md:32`), and kama's write boundary refuses it (`kama-shokunin/PROVINCE.md:45`). These are operator-owned, not a handoff to souji. kama's "report, never absorb" already matches souji's arbitration sentence: `SKILL.md:2` — "contested artifact ownership is reported to the integrator, never silently absorbed."

## 2. What kama must hand off rather than absorb

1. **`.ufo/state/` and its ignore line.** Report-only for souji (`QUALITY.md:38`), out of kama's write boundary. L1/operator decides whether the uncommitted `.gitignore` edit lands; kama must not fold it into a C1/C2 commit. Same for `M AGENTS.md`.
2. **Nothing else in kama's registry.** `registry/` is kama's alone; souji's `pushed`/`moved-to-obsidian`/`stale` receipts (`SKILL.md:32-39`) never apply to a `.tsv`/`.json` snapshot. Do not route registry snapshots to souji.
3. **Do not vendor `souji-landing-gate.py` as kama's own gate.** It is souji-owned (`SKILL.md:152`), keyed to `--root LANE`; a kama count that shells into a sibling repo makes calibration depend on a repo kama does not own. Adopt the convention, not the executable. [INFERENCE]
4. **A future souji sweep is not a disposal route for round-15/16 receipts.** souji would require a receipt class and a dry-run table (`SKILL.md:39` — "No receipt → no removal."), and live lane history fails its own pre-removal checklist (`SKILL.md:48`). Keep them; they are C1's before-arm provenance.

## 3. Reusable conventions (concrete)

- **V1 — a verdict names the bytes it measured.** `souji-shokunin/corpus/QUALITY.md:30` (Q6): "names the sha256 of the bytes it measured, and that digest equals the installed file". Ground truth for C1: `.ufo/waves/round-17/frozen/manifest.json` pins `tests/probe-verdicts/check.py` at sha256 `b853576e…` from `source_commit` `cff9e62…`, and the worktree file today hashes to the same `b853576e…`. Round-16 `measure.py` pins only the matrix set digest (`:280-281` — "# Matrix breadth pin", `EXPECTED_MATRIX_SHA256 = "bf9068d8…"`), not the detector's own bytes. [INFERENCE] That is the exact gap a "before/after survivor count" inherits under a dirty worktree.
- **V2 — split pin equality from measured correspondence.** `QUALITY.md:64` (Q25(b)): "every frozen pin must equal its file's committed bytes, and a record's `measured_commit` must hold the bytes the record pins", with separate finding ids `LG-FROZEN-PIN` / `LG-FROZEN-MEASURED` (`SKILL.md:152`). Apply to C1's two arms: frozen-check.py-vs-manifest, and current-check.py-recorded-digest.
- **V3 — consistency is not behaviour.** `QUALITY.md:64`: "A gate pass is consistency, not behavior: a parsing script can still be wrong". This is C1's own thesis; the new fault controls are the behavioural half.
- **V4 — integrity is not safety.** `QUALITY.md:42` (Q18): "Certification integrity and tool safety are separate verdicts." Directly binds C2: `check-receipt.py`'s `VALID` (`kama-shokunin/SKILL.md:536` — "Live receipt gate") proves receipt consistency, not that the harness could fail. `tests/llamacpp-live/controls.py` is the separate behavioural verdict; a `VALID` receipt must never be cited as C2 improvement.
- **V5 — probe vs gate and the 0/1/2 map.** `SKILL.md:128` — "Gate map: 0 clean · 1 failed · 2 could-not-evaluate." and `SKILL.md:129` — "The four legacy receipt/action tools are **probes**, not". kama already uses the map (`kama-shokunin/SKILL.md:533`). C2's "receipt always written on internal faults, exit 2" is exactly `2 could-not-evaluate`; say so in the row rather than inventing a third vocabulary.
- **V6 — supersede, never rewrite.** `QUALITY.md:12-13`: "a criterion is superseded by a new row that names the row it replaces, never rewritten." kama's corpus already states the same (`kama-shokunin/corpus/QUALITY.md:4-5` — "supersession names the old criterion instead of erasing it"). Consequence: the overclaiming registry row `kama-shokunin/SKILL.md:533` ("grades verdict, reason, exit and drift") must gain a superseding row naming it — an in-place rewrite would erase the only record that the old detector passed 5/5 weakened mutants.
- **V7 — optional, flagged.** souji's fixture scratch rule (`QUALITY.md` Q4, "runs only under `/var/tmp`") is not kama-grounded: kama's contract allows `/tmp` seat scratch, and `tools/kama-llamacpp-live.py:891` uses an unqualified `mkstemp` for the child log but unlinks it at `:708` (observed `/tmp` residue: 0). [INFERENCE] Adopt `/var/tmp` for the new wrapper probes only if a kama lesson grounds it; otherwise leave it.

## 4. Proposed move (one, bounded)

**Byte-addressed dual-arm counting with a superseding registry row.** In `mutants.py` (C1) and `controls.py` (C2), have each arm print, next to its behavioural count: (i) the sha256 of the exact detector/tool bytes it executed — frozen arm read from `.ufo/waves/round-17/frozen/manifest.json`, current arm recorded (not pinned); (ii) the matrix set digest `bf9068d8…`; and report pin equality and behaviour as separate findings (`LG-FROZEN-PIN`-style), never a single "pass". Then register the repair by appending a SKILL row that supersedes `SKILL.md:533`, and stage only the named files — never the dirty `.gitignore`/`AGENTS.md`.

This is souji's Q6 + Q25(b) + Q7(b) convention applied at the one place kama is about to count: its own detector. It improves calibration (the before/after number is attached to a digest, not to a mutable path), and ownership (no third-party change is swept into the landing commit). It does not touch operability, the nine matrix files, or any souji artifact.

## 5. Risks

- A digest block can masquerade as the behavioural verdict — that is exactly V3's failure. The output must keep "pins match" and "N mutants survive" as distinct findings; a pin match is not a calibration result.
- `manifest.json` already pins the frozen check.py; re-hardcoding the digest in `mutants.py` creates a second source of truth. Read the manifest, or state both and fail on disagreement.
- The after-arm digest necessarily changes while check.py is being repaired; pin it only at the final measured bytes. The current worktree equals `master` for `check.py` **today** (`b853576e…` both), so the before arm is unambiguous now but will not stay so.
- Reading another lane's convention is not authority: no finding here may be cited as a souji gate result. [INFERENCE]

## 6. Verification (for L1, not run here)

- `git -C kama-shokunin check-ignore -v registry/history/.lock .ufo/state/x` — expected: `registry/history/.gitignore:3:.lock`; `.ufo/state` only under the worktree edit.
- `sha256sum .ufo/waves/round-17/frozen/tests_probe-verdicts_check.py tests/probe-verdicts/check.py` — expected equal to manifest `b853576e…` before repair.
- `git diff --stat master -- tests/probe-verdicts/*.json` — expected empty (hard constraint), plus the `bf9068d8…` set digest recomputation inside the count.
- `python3 .ufo/waves/round-17/c1/mutants.py` (L1-owned) — expected output: before/after survivor counts, both detector digests, matrix set digest, and separate pin findings.
- Commit hygiene: `git show --stat --format= <landing>` lists only the C1/C2 files; `.gitignore` and `AGENTS.md` absent.

## Limitations

Read-only; no gate, matrix, mutant run, or live server was executed. Souji sources were limited to the three files the item names. The `registry/history/.lock` refutation is against `master` = `cff9e62f05aa7cfb9059444f62eb787100719713` and the current worktree; `AGENTS.md`'s uncommitted diff was not read (not mine to inspect). Marked inferences are the dirty-worktree/V1 link, the cross-lane dependency concern, and the `/var/tmp` transplant.

## Installs

None.
