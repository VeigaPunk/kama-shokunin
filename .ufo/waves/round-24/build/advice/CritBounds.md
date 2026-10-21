# CritBounds — round 24 (static command review; deadlines and suppressed side effects)

Verdict: **the AuditRepair approach is safe on the bounds axes if it follows nine conditions (C1–C9 below).**
Removing the r23 blanket refusal makes `--no-lazy-fetch` the only barrier against fetching. On git 2.45 that
barrier only holds for the commands the auditor runs today. Three of the conditions are fixable defects
that would otherwise cause a regression or false provenance: C1 (closure roots), C4 (Python reads) and
C6 (pinned refusal reasons). The other conditions are constraints the candidate must keep, plus one
tradeoff: C2 (how much of the closure to require).

Scope: the base tool `tools/report-landing-audit.py` at 0df800e. That file is unchanged at lane HEAD d1b9d95.
I also read the r23 grid `tests/report-audit/repo-state-grid.py` and the assignment text in
`.ufo/waves/round-24/build/spec.json`. No candidate existed when I reviewed:
`/fast/scratch/hyaku/kama-r24/AuditRepair`, `git diff` was empty. I ran no auditor, grid or test.
Everything about candidate behaviour is therefore **unverified**.

## What I observed (read-only)

- `report-landing-audit.py:93-96`: `GIT_ISOLATION` = `--no-replace-objects --no-lazy-fetch` plus log encoding, follow, showRoot, showSignature and mailmap overrides.
- `:108` and `:116-125`: `GIT_TIMEOUT = 20` is set per call. A timeout raises `EvalError`. Every git call goes through `git()`.
- `:450-465`: the blanket refusal, which is the code being removed. It raises "partial clone (promisor pack)" or "partial clone ({key})".
- `:514-517`: `check_history_repo` runs **before** `resolve_branch` pins the lane tip. Fleet HEAD is verified at `:517` but the result is thrown away. Later fleet reads use symbolic `HEAD`: `:310` `show HEAD:rel`, `:216` `log` (implicitly HEAD) and `:429` `ls-tree HEAD`.
- `:404-407`: errata corrections go through `lookup()`, so `missing` becomes `errata_invalid` and exit 1.
- Grid `repo-state-grid.py:696-707` pins refusal reasons: F06 "partial clone", F23 "promisor pack", F30 "timed out after". `:674` F27 (filter-only promisor) expects exit 1. `:727-736` the grid timeout is 30 s and the harness kills the whole process group.
- Repository sizes, from `git count-objects -v` and `rev-list --count HEAD`:
  - lane: 743 loose + 5857 packed objects, 102 commits;
  - fleet `/home/vgpnk/Projects/shokunin`: 2688 loose + 6947 packed objects, 1068 commits.
  - A full `--objects` walk is therefore far below the 20 s budget. That is **[INFERENCE]**; I did not time it.
- Official git source was fetched over HTTPS from raw.githubusercontent.com/git/git. Copies and hashes are in `out/CritBounds/git-v2.45.0/` and `out/CritBounds/git-v2.56.0/`, each with a `SHA256SUMS` file. The local git is 2.56.0.
  - v2.56.0 `promisor-remote.c:34`: `fetch_objects()` returns -1 when `GIT_NO_LAZY_FETCH` is set. The same guard is present in v2.46.0 through v2.50.0 (`grep -c` = 1).
  - **v2.45.0 `promisor-remote.c` has no such guard.** On 2.45 lazy fetch is blocked only by `fetch_if_missing`: `environment.c:211`, `git.c:191-192`, and `object-file.c:1619` in the object-read path. Callers that ask the promisor remote directly bypass it: `diff.c:6960` (called at `:6988` when the diff output needs blob data or pickaxe is used) and `diffcore-rename.c:125` and `:897` (called at `:988` and `:1574` for inexact renames).
  - v2.56.0 `builtin/rev-list.c:539-541`: `--missing=print` sets `fetch_if_missing=0` on its own. `:215-237`: `allow-promisor` and `allow-any` skip missing objects silently. `:1028-1040`: missing objects are printed as `?<oid>` after the walk, after all present objects. `:774-783`: `--missing-only` exists in 2.56.0, but `grep -c missing-only` on v2.45.0 `builtin/rev-list.c` returns **0**.
  - v2.45.0 `rev-list-options.txt:1026`: a missing tip is reported as missing, not as an error.

## Counterexamples and corrections

**C1 — Closure roots must be the pinned shas (fixable defect).**
- Counterexample: the candidate runs the closure check inside `check_history_repo`, as it is called at `:514-515`, using `HEAD`. Two failures follow.
  - A bare or worktree lane whose HEAD is unborn, or on another branch, while `--branch master` exists. The `rev-list HEAD` call fails, so an evaluable repo exits 2. That is an operability regression.
  - The objects that are checked are not the ones audited, so the claim of checked closure is false provenance.
- The fleet HEAD is a live repository that other agents commit to. Between the closure check and the reads at `:310`, `:216` and `:429` it can advance.
- Smallest fix:
  - Run the closure check after `resolve_branch` (`:516`), with the lane `tip` sha.
  - Keep the sha from `:517` as `fleet_tip` and pass it to `audit_round`, `report_cutoff` (as `log <fleet_tip> --diff-filter=A ...`) and `show {fleet_tip}:rel`.
  - Never use `--all`, a branch name or symbolic `HEAD` as a closure root. `--all` would also pull in stash, notes and unrelated refs, and a dangling one would cause a spurious exit 2.

**C2 — How much of the closure to require (tradeoff for L1 to decide).**
- A full `--objects --missing=print` walk treats every historical blob as required.
- The audit actually needs:
  - lane: the commits (for `log` with `%an/%at/%s`), the tip tree, the `corpus/SOURCES.md` blob and the errata blob;
  - fleet: the commits, the trees along `.ufo/reports/round-N/` and the report blob at HEAD.
- Each of those blobs is read by a command that already fails when the object is missing under `--no-lazy-fetch`: `:268 cat-file blob`, `:310 show`, `:383 show`. A missing commit makes `log` die when it reads the commit buffer **[INFERENCE from git source, not run]**.
- Consequence: a real `--filter=blob:none` clone with more than one commit touching the same file exits 2, even though every required object is present.
- Smallest bounded option: `git rev-list --objects --filter=blob:none --missing=print --no-object-names <pinned-sha>` per repo.
  - With a filter, blobs are dropped before `show_object` and `finish_object` (`list-objects.c` `process_blob`), so only commits and trees are required.
  - The explicitly read blobs stay protected by their own failing reads.
- Both variants meet every row in the preregistration. The full walk is strictly more refusing. Report the choice; the OracleMissingNonrequired lane is the one that decides it.

**C3 — Rev-list flags and output parsing (constraint).**
- Never use `--missing=allow-promisor`, `--missing=allow-any` or `--exclude-promisor-objects`. They hide exactly the evidence being checked, and the last one is incompatible with `--missing`.
- **Never use `--missing-only`**: v2.45.0 lacks it, so every audit on the documented git 2.45 floor would exit 2.
- Parse strictly, with `errors="strict"`:
  - each line must be `^[0-9a-f]{40}$` or `^\?[0-9a-f]{40}$`;
  - any `?` line raises `EvalError` naming the object id;
  - any other line raises `EvalError`.
- Use `--no-object-names` so paths never reach the parser.

**C4 — Python-side file reads have no deadline (fixable defect if introduced).**
- `GIT_TIMEOUT` only bounds git subprocesses. `grafts_effective` (`:468-479`) is safe because it checks `lstat` / `S_ISREG` before reading.
- Counterexample: the candidate adds a Python `open()` of `objects/info/alternates`, a `.promisor` file or `.git/config` to detect promisor state. A FIFO there blocks forever, and the grid kills the case at 30 s.
- Reading `.git/config` in Python also skips `include.path`, so promisor keys set in an include are missed. That bypasses detection and turns an unknown citation into a false exit 1.
- Fix:
  - Keep detection on `git config --null --list` (`:458`), which follows includes and runs under the timeout.
  - Keep pack markers to a directory listing plus `exists()`, without opening files.
  - Any new file read must check `lstat` / `S_ISREG` first.

**C5 — Detection is part of the side-effect bound (constraint).**
- Once the refusal is gone, the detection result only selects between exit 2 and a verdict. It must cover:
  - `extensions.partialclone` with any value;
  - `remote.*.promisor` when the git boolean is true (`:482-486`);
  - `remote.*.partialclonefilter` with any value. The grid's F27 fixture (`:482-497`) shows this key alone triggers a fetch, and base `:462-465` does not detect it;
  - paired `*.promisor` and `*.pack` markers (`:454-457`).
- A failed config read stays `EvalError`, never "not promisor".
- Detection state is computed once per repo per run and passed explicitly to `lookup()`, not cached globally.

**C6 — Keep the r23 refusal reasons stable (fixable defect against the frozen historical grid).**
- F06 and F23 still exit 2 under the new rule, but only because of the unknown-citation rule. If the new message drops the substrings "partial clone" and "promisor pack", both rows fail their `REASONS` pins. That creates undocumented policy-row churn.
- Smallest fix: build the unknown-citation `EvalError` text from the detection label the base already uses, e.g. `f"{repo}: citation {t} absent locally; partial clone ({source})"` with `source` = `promisor pack` or the config key.
- F27's expected exit moves from 1 to 2. That is a documented policy-row change: add a `REASONS` pin for it.
- F30's "timed out after" holds only if no catch-and-continue is added. Otherwise a second hang makes the total exceed the grid's 30 s.

**C7 — All three lookup sites need the unknown rule (fixable defect if missed).**
- The sites are `:325` (full hashes), `:336` (landed citations, peeled) and `:404` (errata corrections).
- Counterexample: an errata correction absent from every repo while one repo is promisor-backed. Today that gives `errata_invalid` and exit 1, which is a guessed absence. It must be exit 2.

**C8 — Wrong-type citations versus an unknown peel target (constraint).**
- A peeled lookup of a present blob or tree prints `missing`. Only a bare `batch-check` type of blob or tree makes that a definite wrong-type `landed-unresolved`.
- A **present annotated tag whose target commit is a missing promisor object** also peels to `missing`, but its absence is unknown. In a promisor repo that must be exit 2, not wrong-type.

**C9 — Deadlines and side effects are preserved only within the current command set (constraint; update the docs).**
- Keep `GIT_ISOLATION` and `GIT_TIMEOUT = 20` unchanged. Make every new call through `git()`. Add no `fetch`, `backfill`, `fsck` or hydration step: `fsck` also checks unreachable objects, which is out of scope and slower.
- On git 2.45.x, a command that reaches `diff.c:6960` or `diffcore-rename.c:125/897` would still fetch, and could run `core.sshCommand`. This includes `-p`, `--stat`, `-S`/`-G`, inexact renames over a multi-path pathspec, `checkout`, `grep` and `blame`.
- Such a fetch would also start a git grandchild that keeps the output pipe open. `subprocess.run(timeout=)` kills only the direct child, so the 20 s deadline would be overrun.
- The current commands avoid these paths. **[INFERENCE]** `log --format=%at --diff-filter=A -- <one path>` has no blob-data output and no rename candidates.
- Docstring `:47-55` currently says partial clones are refused. Rewrite it to say:
  - promisor repositories are audited with lazy fetch disabled;
  - `--no-lazy-fetch` is the only fetch barrier;
  - on git 2.45 that holds only for the documented command set; the `fetch_objects` guard exists from git 2.46.

## Axes affected

| Axis | Conditions |
|---|---|
| Operability (no exit 2 on evaluable repos) | C1, C2, C3 (`--missing-only`) |
| Correctness (no guessed absence) | C4 (include bypass), C5, C7, C8 |
| Deadline | C4, C6 (F30), C9 |
| Suppressed side effects | C3, C9 |
| Provenance of the closure claim | C1 |
| Historical-grid parity | C6 |

Not claimed: alternates that borrow from a partial-clone store. Their `.promisor` packs are not under `git-path objects/pack`, so they are not detected. Docstring `:52-54` already leaves alternates unclaimed.

## Installs

None.

## Files

- This report.
- `out/CritBounds/git-v2.45.0/`: `builtin_rev-list.c`, `promisor-remote.c`, `rev-list-options.txt`, `git.c`, `object-file.c`, `environment.c`, `diff.c`, `diffcore-rename.c`, plus `SHA256SUMS`.
- `out/CritBounds/git-v2.56.0/`: `promisor-remote.c`, `builtin_rev-list.c`, `list-objects.c`, `diffcore-rename.c`, `git.c`, `object-file.c`, `environment.c`, `diff.c`, `Documentation_rev-list-options.adoc`, plus `SHA256SUMS`.
  - `SHA256SUMS.final` in each directory hashes every downloaded file: 8 files in v2.45.0, 9 in v2.56.0. The earlier `SHA256SUMS` files are partial and are left as they were.
