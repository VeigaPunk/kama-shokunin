# ConnSiblingTools — sibling-overlap sweep

Seat: connector `CloseKama22.ConnSiblingTools-2`. Base: kama `245a37f69628c2c6bb29bbf17897d8fb5946c857`
(clone `/tmp/kama-r23w2/ConnSiblingTools`, `rev-parse HEAD` = that value). Fleet-root files cited by path
are **not** at that revision (different repo); they were read read-only at the fleet checkout.
No installs. No external URLs used — every quote below is a local file/repo read.

## Verdict: **partially**

The exposure named in C1 (`git` without `--no-replace-objects` / strict decode) is fixed in
`tools/report-landing-audit.py` only. Of kama's 20 distinct registered gate scripts, 10 invoke git; two
of them give **end-to-end false passes** (exit 1 → exit 0 on the same repo after one local
`git update-ref`), one **executes the substituted bytes** it reads (demonstrated), one flips a
capability status, and the fleet's `closure-check` gate shares the same channels (primitives
demonstrated at its exact commands; gate-level flip `[INFERENCE]`). C1 as declared (about its own
instrument) is not falsified; any *generalization* of C1 to "the audit surface" is.

The non-obvious part: the isolation convention C1 asks for **already exists twice in this lane**
(`.ufo/waves/round-12/fidelity.py:80-98` and `.ufo/waves/round-13/measure.py:281-295` pass
`--no-replace-objects` *and* set `GIT_NO_REPLACE_OBJECTS=1`/`GIT_NO_LAZY_FETCH=1`), and two more gates
pin the frozen blob's SHA-256. The gates that grade kama's own records simply never adopted either
pattern.

## 1. Inventory — kama tools (`tools/*`)

Kama has nine tools. Only four touch git; five never do (`tools/kama-probe.sh`,
`tools/test-snapshot.sh`, `tools/gguf-identity.py`, `tools/kama-llamacpp-live.py`,
`tools/kama-ollama-evidence.py`: grep for `"git"`/`git -C` returns only a comment at
`kama-probe.sh:661` and a URL at `kama-llamacpp-live.py:57`).

| # | call site (base `245a37f6`) | git command | `--no-replace-objects` | `--no-lazy-fetch` | env cleared | decode of git bytes | verdict role |
|---|---|---|---|---|---|---|---|
| 1 | `tools/report-landing-audit.py:93-94`, `:99-106`, `:108-126` | all | **yes** | **yes** | **yes** (`git_env`) | strict → `EvalError` (`:123`) | gate, `SKILL.md:683` — **fixed** |
| 2 | `tools/sources-append-only.py:288` | `show REV:PATH` | no | no | no (env inherited) | strict → `ParseError` → exit 2 (control run) | gate, `SKILL.md:576`, `:612` |
| 3 | `tools/citation-provenance.py:42` | `cat-file blob REV:PATH` | no | no | no (env inherited) | raw bytes (no decode) | gate, `SKILL.md:652` |
| 4 | `tools/citation-provenance.py:72` | `rev-parse --git-dir` | no | n/a | no | n/a | same gate |
| 5 | `tools/citation-provenance.py:106` | `merge-base --is-ancestor` | no | n/a | no | n/a | same gate (`off_ref`) |
| 6 | `tools/error-verdict-census.py:143` | `show FROZEN_REV:PATH` | no | no | partial: `env_for` (`:68-72`) sets `GIT_CONFIG_NOSYSTEM`/`GIT_CONFIG_GLOBAL` and drops inherited env, no isolation flags | bytes hashed against `FROZEN_SOURCE_SHA256` (`:151-152`) | measurement gate, `SKILL.md:655` |

## 1b. Kama-owned registered gates outside `tools/*`

Every `gate:`-style row of `SKILL.md` was parsed to its entry script: **20 distinct scripts**; 10 invoke
git, 10 do not (`round-11/measure.py`, `round-18/c2/survivors.py`, `check-receipt.py` (4 rows),
`install-tree-grid.py`, `ollama-corpus-guard/check.py`, `probe-verdicts/check.py` (2 rows),
`probe-verdicts/fault-controls.py`, `gguf-identity.py`, `kama-ollama-evidence.py`, `kama-probe.sh`
(2 rows) — grep for `["git"`, `'git'`, `git_run(`, `git_read(`).

| row(s) | script:line | isolation | status |
|---|---|---|---|
| `396` | `.ufo/waves/round-12/fidelity.py:80-98` | argv `--no-pager --no-replace-objects`; env drops `GIT_*`, sets `GIT_NO_REPLACE_OBJECTS=1`, `GIT_NO_LAZY_FETCH=1`, `GIT_OPTIONAL_LOCKS=0`, `GIT_TERMINAL_PROMPT=0`, `GIT_CEILING_DIRECTORIES` | **already isolated** |
| `430,577` | `.ufo/waves/round-13/measure.py:281-295` | same shape (`GIT_NO_REPLACE_OBJECTS=1`, `GIT_NO_LAZY_FETCH=1`, argv `--no-replace-objects`) | **already isolated** |
| `723` | `tests/llamacpp-live/install-io-grid.py:207-215` | env `GIT_NO_REPLACE_OBJECTS=1`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`; **no** `GIT_NO_LAZY_FETCH`; SHA-256 pinned (`FROZEN_SHA:24`) | replace fail-closed; lazy fetch open |
| `767` | `.ufo/waves/round-22/.../red-green-witness.py:22-24`, `:48-53` | `GIT_ENV` has `GIT_NO_REPLACE_OBJECTS=1`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`; **no** `GIT_NO_LAZY_FETCH`; blob oid+SHA-256 pinned | replace fail-closed; lazy fetch open |
| `685` | `tests/llamacpp-live/install-links-grid.py:68-78` | **none**: `git -C LANE show FROZEN_REV:PRODUCER`, `encoding="utf-8"` (strict), no digest pin, bytes handed to `exec` (`:61-66`) | **exec + verdict control shown (P2)** |
| `576` | `tools/sources-append-only.py:288` | none | **false pass shown (P3)** |
| `652` | `tools/citation-provenance.py:42` | none | **false pass shown (P4)** |
| `659` | `.ufo/waves/round-20/c2/measure.py:565-583` | `ls-tree` with no `--no-replace-objects`; env is `PATH` + `GIT_CONFIG_NOSYSTEM` only; decode safe (`errors="replace"`) | **status flip shown (P5)** |
| `655` | `tools/error-verdict-census.py:143` | see §1 row 6 | digest fail-closed |
| `683` | `tools/report-landing-audit.py:93-126` | full isolation | **fixed** |

## 2. Fleet gates (registry home `SCORECARD.md:177`)

Registered fleet gates: `closure-check` (`SCORECARD.md:194`), `root-ledgers` (`SCORECARD.md:195`).

| call site | git command | flags | env | decode |
|---|---|---|---|---|
| `.ufo/waves/round-15/closure-check.py:208-214` (`run_git`) | all | none | inherited | `text=True` at `:211`, uncaught |
| `closure-check.py:742`, `:756` via `:1372-1379` | `log --since`, `log -1 --format=%an -- PATH` | none | inherited | `text=True` |
| `closure-check.py:783` | `show -s --format=%an` | none | inherited | `text=True` |
| `closure-check.py:875`, `:886-891`, `:906` | `cat-file --batch-check`, `merge-base --is-ancestor` | none | inherited | `text=True` at `:890` |
| `closure-check.py:958`, `:980` | `show COMMIT:MANIFEST.json`, `merge-base --is-ancestor` | none | inherited | `text=True` |
| `closure-check.py:1040`, `:1043`, `:1123` | `rev-parse --show-toplevel`, `ls-files` | none | inherited | `text=True` |
| `.ufo/gates/root-ledgers.py:103-106` | `show REV:NAME` | none | inherited | `decode_ledger` `:112-116` → exit 2 |
| `root-ledgers.py:255-259` | `rev-parse --short HEAD`, `status --porcelain -- LEDGERS` | none | inherited | `text=True` |

`closure-check` reads **lane repos** (`lane_repo(inp, lane)` at `:772`, `:1372`, `:1379`), not only the
fleet root; `root-ledgers` reads the fleet root.

Fleet **landing drivers** (no verdict map; operator-run, adjacency only): `scripts/hyaku/inline.sh:111`
(`status`/`log -1` on the fleet repo), `:126` (lane `status`), `:127` (`rev-list`), `:132` (`log`);
`scripts/hyaku/fleet-commit.sh:40,44,49,50,53,54,60,63,64`; `scripts/hyaku/append-closure.py:61-64`
(`text=True`); `scripts/hyaku/jj-lane.sh:103,120,167-179,211,231,239,285-288,405-406`;
`scripts/shokunin-watchdog.sh:292,296`.

## 3. Ranked by verdict impact

| rank | site | impact class | what flips | basis |
|---|---|---|---|---|
| P1 | `closure-check.py` (fleet gate #1) | **false clean + false failed** | A lane-planted `refs/replace` changes the bytes `show <commit>:MANIFEST.json` returns (`:958`), the author `show -s --format=%an` reports (`:783`), and which commits `log --since` counts as lane activity (`:742`); `cat-file --batch-check` object *type* flips commit↔blob, changing `_classify` (`:875-906`). Repo-local `i18n.logOutputEncoding` makes `run_git`'s `text=True` (`:211`) raise `UnicodeDecodeError`; top level catches only `BrokenPipeError` (`:2059-2061`) → traceback → exit 1 = *failed*. | D4-D8 |
| P2 | `install-links-grid.py:68-78` (gate `SKILL.md:685`) | **code execution + false pass** (frozen/both arms) | The gate `exec`s the bytes of `git show FROZEN_REV:tools/kama-llamacpp-live.py`, with no isolation and **no digest pin**. One repo-local replace ref makes the gate execute attacker-chosen Python and compute both arms' verdicts from it; a non-UTF-8 substitute also raises an uncaught `UnicodeDecodeError` (strict `encoding="utf-8"`) → traceback → exit 1. Default `--arm current` does not touch the frozen path (`:376-377`); `--arm frozen|both` does. | D16 |
| P3 | `sources-append-only.py:288` | **false clean, end-to-end** | The gate's one job is to catch an in-place rewrite of `corpus/SOURCES.md`; one local `update-ref refs/replace/<from>` makes the *from* blob equal the *to* blob, so the rewrite reports `ok: true`, exit 0. | D1 |
| P4 | `citation-provenance.py:42` | **false clean, end-to-end (official invocation)** | Replace redirects `cat-file blob REV:PATH` to another commit's blob, so the token's SHA-256 matches a file that does not exist at `REV` — the exact round-18 pointer-drift defect (`SKILL.md:652`). `merge-base` is *not* replace-affected (D3), so `off_ref` survives; the digest check does not. | D2, D3 |
| P5 | `round-20/c2/measure.py:565-583` (gate `SKILL.md:659`) | **false failed** | `git ls-tree -r --name-only <rev> -- <path>` honours replace; a replacement commit whose tree gains the path turns `frozen_before.status` from `capability_absent` to `capability_present` (`:586-587`) → `mismatches` vs pinned `expected_status` → defect/exit 1 where the true state was clean (the reverse can hide presence). | D15 |
| P6 | `root-ledgers.py` (fleet gate #2) | **fail-closed; execution-only leak** | `show REV:NAME` honours replace, but frozen replays pin every blob's SHA-256 (`root-ledgers.py:318-325`) → `snapshot_tampered`, exit 2, never a false clean. Live mode runs `git status --porcelain` (`:257`), which executes repo-local `core.fsmonitor` (D9). Fleet-root repo, operator-owned. | D9, code read |
| P7 | `red-green-witness.py` (`SKILL.md:767`) | **evaluation denial** | Pinned blob oid+SHA-256 (`:48-53`) makes replace → `SnapshotError`; `GIT_ENV` lacks `GIT_NO_LAZY_FETCH` (`:22-24`), so a promisor-configured lane makes `git show` spawn `git fetch` from a repo-configured URL (D10) → hang → could-not-evaluate. | D10, code read |
| P8 | `install-io-grid.py:207-215` (`SKILL.md:723`) | **evaluation denial** | `FROZEN_SHA` pin (`:24`, `:213-214`) makes replace → `frozen_source_unavailable_or_tampered`; no `GIT_NO_LAZY_FETCH` in its env (`:208-210`) → lazy fetch reachable. | D10, code read |
| P9 | `error-verdict-census.py:143` | **evaluation denial** | Frozen instrument bytes digest-pinned (`:151-152`), so replace → `CensusFault` exit 2, not a flip; no `--no-lazy-fetch`. | D10, code read |
| P10 | landing drivers | **no scored verdict** | `status --porcelain` (`inline.sh:111,126`, `root-ledgers.py:257`) executes `core.fsmonitor`; `append-closure.py:61-64` decodes git output with `text=True`; replace/lazy-fetch reachable on the fleet repo. Output is printed `OK/WARN`, not a 0/1 gate verdict. | D9, code read |

Already isolated, no finding: `fidelity.py`, `round-13/measure.py` (§1b).

Precision (do **not** overclaim): `merge-base --is-ancestor` ignores replace in git 2.56.0 — a
discriminating fixture (side commit X not an ancestor of `HEAD`; X replaced by an ancestor) returns rc 1
both with and without `--no-replace-objects`. So `off_ref`, `history_pin_orphan` and `_classify`'s
ancestry leg are **not** replace-forgeable; only content reads (`show REV:PATH`, `ls-tree`), metadata
display (`show -s`, `log`) and object type are. `log.mailmap=true` does not rewrite `%an` (no
`--use-mailmap`), so the grid's `.mailmap` channel does not reach `closure-check`.

## 4. Evidence (exact commands, observed output)

Fixtures live in fresh `/tmp` repos with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1` and explicit
identity; one `file://` promisor remote, no network.

- **D1 sources-append-only false pass (end-to-end).** Repo with `S001+S002` at `R1`, `S001` at `R2`:
  `python3 tools/sources-append-only.py --repo … --from 1c03e718… --to a924dc67… --path corpus/SOURCES.md --json`
  → exit **1**, `"violations":[{"id":"S002","kind":"removed"}], "ok":false`.
  Then `git commit-tree <R2-tree>` + `git update-ref refs/replace/1c03e718… <repl>`; same command →
  exit **0**, `"violations":[], "ok":true`. One local ref; no commit, no worktree change.
- **D2 citation-provenance false pass (official invocation, no `--allow-off-ref`).**
  `origin/master=HEAD=C2`; registry cites `C2:evidence.txt` with the SHA-256 of `C1`'s blob.
  Before: exit **1**, `verified=0 mismatch=1`. `git update-ref refs/replace/<C2> <C1>`; after: exit **0**,
  `verified=1 mismatch=0 off_ref=0`. With `--allow-off-ref` the same flip occurs.
- **D3 ancestry unaffected.** `git merge-base --is-ancestor X HEAD` → rc **1** default and rc **1** with
  `--no-replace-objects` (X replaced by an ancestor).
- **D4 identity substitution.** `git show -s --format=%an|%aI <X>` → `mallory|2026-10-20T00:00:00Z`
  default vs `alice|2000-01-01T00:00:00Z` with `--no-replace-objects` (true state).
- **D5 activity-window stuffing.** `git log --since=2025-01-01 --format='%h %an %cI'` → `[]` with
  `--no-replace-objects` vs `0c60e1a mallory 2026-10-20T00:00:00Z` default.
- **D6 object-type flip.** `git cat-file --batch-check` on a commit → `… commit 146` before,
  `… blob 7` after `refs/replace/<commit> → <blob>`; on a blob → `blob 7` before, `commit 194` after.
  `_resolve_hashes` reads `parts[1]` (`closure-check.py:881-883`).
- **D7 history-pin anchor primitive at `closure-check.py:958`.** `git show M1:MANIFEST.json` →
  `{"rounds":[1,2,4]}` (forged) vs `{"rounds":[1,2,3]}` with `--no-replace-objects` (true); canonical
  digest of the seen prefix equals the forged pin (`True`) and differs from the true pin (`False`).
  `[INFERENCE]` this suppresses `history_pin_unanchored`; the gate was not executed.
- **D8 strict decode → traceback → exit 1.** Repo-local `i18n.logOutputEncoding=ISO-8859-1`, author
  `café`: raw bytes `260e266\tcaf\xe9\t…`; `subprocess.run([... 'log','--format=%h\t%an\t%cI'], text=True)`
  raises `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 11`. `run_git` catches
  only `(OSError, subprocess.SubprocessError)` (`:212`).
- **D9 repo-config program execution.** `git config core.fsmonitor <hook>`; hook touches a marker;
  `git status --porcelain -- SCORECARD.md LOG.md` → rc 0 and **marker exists**. Reached by
  `root-ledgers.py:257`, `inline.sh:111`, `inline.sh:126`.
- **D10 lazy fetch, and its env suppression.** Promisor-configured repo (`remote.origin.promisor=true`,
  `file://` URL) with a missing blob: `GIT_TRACE=1 git cat-file blob HEAD:evidence.txt` spawns
  `git fetch origin --no-tags --no-write-fetch-head --recurse-submodules=no --filter=blob:none --stdin`
  (rc 128 in the fixture once the local filter was refused; the fetch ran). With
  `GIT_NO_LAZY_FETCH=1` the same command spawns **no** fetch (trace has no `fetch origin`).
- **D11 decode controls (siblings already handle these).** Non-UTF-8 `SOURCES.md` blob →
  `sources-append-only.py` exit **2**, no traceback. Non-UTF-8 registry and doc →
  `citation-provenance.py` exit **2**, no traceback. The shared defect is missing isolation, not decode.
- **D12 mailmap.** `log.mailmap=true` + `.mailmap` mapping `alice → kama-shokunin`:
  `git log --format=%an` still prints `alice`; `closure-check` uses no `--use-mailmap`.
- **D13 ambient `GIT_DIR`.** With `GIT_DIR=<decoy repo>`, `sources-append-only.py` → exit 2
  (`git show … failed (rc=128)`); `citation-provenance.py` → exit 1 `mismatch=1` (reads the decoy odb).
  A false *failed*, not a false clean, but neither gate clears the child env.
- **D14 live fleet-root state (time-stamped; not created by this seat).**
  `/home/vgpnk/Projects/shokunin/.git/objects/pack/` now holds four zero-byte `*.promisor` markers,
  including a synthetic `pack-deadbeef.promisor` with no matching pack, all mtime
  `2026-10-21 12:50:16 -0300`; no `promisor`/`partialclone` config key exists and the repo is not
  shallow (`git rev-parse --is-shallow-repository` → `false`).
  `report-landing-audit.check_history_repo("/home/vgpnk/Projects/shokunin")` → `EvalError …: partial
  clone (promisor pack)`; the kama lane is accepted. Consequence: **a re-run of the C1 no-harm audit
  against the fleet root right now exits 2**, not 0/1, until those markers are removed (the refusal at
  `report-landing-audit.py:442-444` keys on the marker file, not on config).
- **D15 `ls-tree` status flip at `round-20/c2/measure.py:570`.** Commit `C1` (file `f` only), `C2`
  (files `f`,`g`): `git ls-tree -r --name-only C1 -- g` → rc 0, empty; after
  `git update-ref refs/replace/C1 C2` → `g`; with `--no-replace-objects` → empty.
- **D16 exec of a substituted frozen source at `install-links-grid.py:69`.** Fixture lane whose
  `prod.py` is `TOKEN='real'` at `C1` and `TOKEN='forged'` at `C2`.
  `install-links-grid.frozen_producer(lane)` after pointing `FROZEN_REV` at `C1` →
  `install_links()` returns `real`; after `git update-ref refs/replace/<C1> <C2>` → returns `forged`.
  The module is built by `exec(compile(source…))` in `load_source` (`:61-66`), with no digest check.

## 5. Contradictions (stated, not scored away)

1. `report-landing-audit.py:55` says "Audit trusted repositories only". That precondition cannot be
   inherited by `sources-append-only.py`: its threat model **is** the untrusted lane repository
   (`SKILL.md:576`; KQ22 runs over the lane's own consecutive commit pairs), and the same actor who
   rewrites `SOURCES.md` in place can `git update-ref refs/replace/…` in that repo without leaving a
   worktree diff. For that gate the trust clause is empty.
2. C1's measured claim is about one instrument; the "now-fixed exposure" is a *class*. Two registered
   kama gates still fail the same fault-grid cell (replace substitution) the fixed tool now passes, and
   one executes the substituted bytes. Treating C1 as evidence that "gates are repo-state proof" would
   be a category error.
3. The fixed tool refuses promisor packs; the siblings neither refuse nor disable lazy fetch, and the
   **fleet root itself** now carries promisor markers (D14) — the audit refuses a repo the other gates
   would happily read.

## 6. Proposed move (one, bounded)

**Propagate the two in-lane patterns — flag/env isolation and a pinned frozen-blob digest — to the four
kama gate scripts that lack them; route the fleet gates instead of editing them.**

- `tools/sources-append-only.py:288`: argv `["git", "--no-replace-objects", "--no-lazy-fetch", "-C", …]`
  plus `fidelity.py`'s env shape (`GIT_NO_REPLACE_OBJECTS=1`, `GIT_NO_LAZY_FETCH=1`, `GIT_*` stripped,
  `GIT_OPTIONAL_LOCKS=0`, `GIT_TERMINAL_PROMPT=0`) — ≈10 lines, no new abstraction.
- `tools/citation-provenance.py:42,72,106`: same argv/env; `git_blob`'s failure path already returns a
  reason → exit 2.
- `tests/llamacpp-live/install-links-grid.py:68-78`: add the two flags, run under the same env, and pin
  `sha256(proc.stdout)` the way `install-io-grid.py:207-215` already does (`FROZEN_SHA`); a mismatch is
  `EvalError`, never a loaded module. This closes the exec channel at its source.
- `.ufo/waves/round-20/c2/measure.py:565-583`: add `--no-replace-objects` to the `ls-tree` argv (one
  token); its decode is already safe.
- Registry rows `SKILL.md:576`, `:652`, `:685`: record that these gates read with replace/lazy-fetch
  neutralized and inherit the **git ≥ 2.45** floor already declared for the audit tool (host 2.56.0).
- Add one new cell file `tests/report-audit/sibling-git-state.py` carrying D1/D2/D3/D11/D15/D16 as
  regression cells. **Do not touch `tests/report-audit/repo-state-grid.py`** — its blob `4fe9339f…` is
  cited evidence in this round's claim.
- Route, do not edit: `closure-check.py` (`:211`, `:742`, `:756`, `:783`, `:875`, `:958`),
  `red-green-witness.py:22-24` and `install-io-grid.py:208-210` (missing `GIT_NO_LAZY_FETCH`), and the
  `root-ledgers.py:257` / `inline.sh:111,126` `fsmonitor` execution are fleet-root or historical
  artifacts outside this lane's write scope.

Why flags/pins and not "refuse replace refs": they match the instrument already measured in round 23 and
the convention already implemented three times in-lane, cannot mint a false red on a repo that
legitimately uses replace refs, and leave ancestry checks (which replace cannot forge, D3) untouched.

**Axes.** A1 coverage (four registered gates join a convention six siblings already implement) and A3
verdict soundness (two demonstrated false passes and one false red close; the exec path closes; the fleet
gate's crash-as-failed is documented for routing) improve. A2 exposure completeness improves at those
sites (lazy fetch + ambient env). A4 precision is preserved by declaring what is *not* fixed (ancestry,
mailmap, gitfile/alternates). No axis harmed: all 21 lane repos plus the fleet root carry zero replace
refs (`git replace -l` = 0 in 22 checked repos) and the kama lane zero promisor markers, so the change is a no-op on today's inputs;
`error-verdict-census.py` pins only the **frozen** citation bytes (`FROZEN_SOURCE_SHA256`, rev `37bd4c5`),
so editing the worktree copy changes no pinned digest, and its current-arm classes on the fixture repos
stay identical (those fixtures carry no replace refs and are non-promisor).

**Risks.** The git ≥ 2.45 floor now spans four more gates (T01 already accepts it for the audit); a
partial-clone lane audited by these gates will exit 2 instead of fetching (correct class, new behavior);
`install-links-grid.py`'s frozen arm needs its pinned SHA populated from a trusted checkout, so the
change must record that hash in the same commit; the fleet gate stays exposed until the protocol lane
acts; D14 means the no-harm re-run must clear the stale markers or record exit 2 deliberately.

**Verification.** (1) New cells after the change: D1 → exit 1 with `S002 removed`; D2 → exit 1
`mismatch=1`; D15 → `capability_absent` for the true tree; D16 → `frozen_source_unavailable_or_tampered`
on a replaced blob; D3/D11 unchanged. (2) Existing selftests unchanged:
`python3 tools/sources-append-only.py --selftest` (42 cases), `python3 tools/citation-provenance.py
--selftest`, `python3 tests/llamacpp-live/install-links-grid.py --selftest`. (3) No-harm: run both kama
gates over the round's real windows (e.g. `--from <r22 tip> --to 245a37f6`) and require byte-identical
stdout/exit to the pre-change run (guaranteed by zero replace refs). (4) `git --version` ≥ 2.45.

## 7. What I did NOT verify

- I did not run `report-landing-audit.py`'s grid or selftest, nor re-run the L1's no-harm numbers; C1's
  own arm is the L1's evidence, not mine. D14 is a live-state check, not a re-run.
- I did not execute `closure-check.py`, `round-20/c2/measure.py`, `red-green-witness.py`,
  `install-io-grid.py`, `install-links-grid.py`'s CLI or `error-verdict-census.py` end-to-end; D4-D8 and
  D15-D16 are their primitives/functions at their exact commands and the gate-level effect is
  `[INFERENCE]` except where a function was called directly (D16).
- No signed-commit fixture, so GPG/`log.showSignature` program execution is untested; no `ext::`
  transport test; no `.git` gitfile redirect or `objects/info/alternates` test for the siblings (both
  declared residuals of the fixed tool too); no network fetch (`example.invalid` never exercised; D10
  used `file://`).
- Historical wave experiment scripts outside the registered-gate list (e.g.
  `.ufo/waves/round-16/measure.py`, `round-18/**`, `round-20/build/out/**`, `round-21/**` probes) were
  found by repo-wide grep but were **not** swept cell-by-cell; they are not registered gates.
- I did not determine which process wrote the four fleet-root `.promisor` markers at 12:50:16.

## 8. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/advice/ConnSiblingTools.md`
  (this file). Nothing else; fixtures live only under `/tmp/kama-r23w2/`. No commits, pushes, jj
  commands, installs, or writes to any tracked file, index, or sibling lane.
