# CritTradeoffHarm — do the round-23 declared tradeoffs harm a real kama workflow?

Seat: CloseKama22.CritTradeoffHarm-2 (critic, leaf). Base `245a37f69628c2c6bb29bbf17897d8fb5946c857`
(clone `/tmp/kama-r23w2/CritTradeoffHarm`, `rev-parse HEAD` = base). Host git 2.56.0 (`which -a git` → `/usr/bin/git` only).
Arms: frozen = blob `4fe9339f:tools/report-landing-audit.py` (sha256 `09ecd63b…3b3f`); current = blob `245a37f6:tools/report-landing-audit.py` (sha256 `f228f174…28a7`).

## Verdict: PARTIALLY FALSIFIED

- **Git ≥ 2.45 floor: holds.** No real workflow runs below it (one git binary on the host, 2.56.0), and the floor fails closed with exit 2 (OldGitFloor).
- **Shallow refusal: holds.** No recorded workflow produces a shallow lane or fleet. Where shallow depth is too small, the refusal replaces a false `failed` verdict.
- **Partial-clone refusal: falsified twice.**
  - **H1:** the refusal fires on a complete repository. As of 12:50:16 -0300 the real fleet is refused, which blocks recipe steps [5]/[6] and the SKILL.md round-report checklist.
  - **H2:** the refusal is bypassed by the `git clone --shared` seat recipe, which gives a false verdict.

## H1 — HARM, real workflow, live now: stray `.promisor` markers in the REAL fleet make the current audit refuse it

Evidence:
- `ls -la /home/vgpnk/Projects/shokunin/.git/objects/pack` shows 4 empty files, all with mtime `2026-10-21 12:50:16 -0300`:
  - `pack-22727cb1….promisor`
  - `pack-3cd47c8a….promisor`
  - `pack-e193a790….promisor`
  - `pack-deadbeef.promisor` (a fixture name)
  - All 4 have sha256 `e3b0c442…` (empty). The same check at ~12:47 -0300 returned 0 promisor files.
- The fleet has no promisor config. `git config --get-regexp 'promisor|partial'` exits 1, and the local config holds only the `remote.origin.url/fetch` and `branch.master.*` keys.
- The fleet is complete. `git --no-lazy-fetch rev-list --objects --all --missing=print | grep -c '^?'` → `0`, and `--is-shallow-repository` → `false`.
- Recipe `round-23/recipe.json` steps [5] and [6] (`--rounds 10-22 --fleet-repo /home/vgpnk/Projects/shokunin --json [--no-errata]`), run from my clone, both give `rc=2 could-not-evaluate: /home/vgpnk/Projects/shokunin: partial clone (promisor pack)`. The declared expected exits are 0 and 1.
- `run.out` cell R0 (real lane + real fleet): frozen `rc=0 … defects=9 corrected=9 … status=clean`; current `rc=2 … partial clone (promisor pack)`.
- The refusal propagates to every non-shared seat copy of the fleet:
  - R1 (`--no-hardlinks` lane + real fleet): rc 2.
  - R3 (`--bare` lane + `--mirror` fleet, the round-21 LessonPointers recipe): rc 2.
  - R4b/R4c (`--no-hardlinks` fleet clone): rc 2.
  - The frozen arm is clean (rc 0) in all of these cells.
- Cause: `tools/report-landing-audit.py:442-444` refuses as soon as any `*.promisor` file exists in `objects/pack`. It does not check whether a promisor remote exists or whether any object is missing.

Writer: not identified. It is not me: I only ran read-only git in the fleet (`rev-parse`, `config --get/--list`, `rev-list`, `ls-tree`, and the audit). No committed round-23 file contains `deadbeef`. The nearest falsify artifact by time is `falsify/out/CritDefensiveOnly/` (directory created 12:50:10); its current `probe.py` only *reads* `.promisor`, so that is [INFERENCE] at most. I reported this to `CloseKama22` as a blocker and did not modify the fleet.

Impacted axes:
- **Operability:** the real fleet gate cannot be evaluated.
- **Calibration of the no-harm evidence:** every rerun of the declared "rounds 10-22 byte-identical" claim against the real fleet is invalid while the markers exist.
- **Identity:** the same object store is accepted through `--shared` (R2 rc 0) and refused directly (R1 rc 2).

Smallest safe correction:
1. **Operator/L1:** remove the four foreign zero-byte markers after re-confirming that the config has no promisor key and the repo has 0 missing objects. Then find the seat that wrote into the fleet; that is a contract breach.
2. **Tool (optional, a tradeoff decision):** keep the refusal fail-closed, but name the marker path in the refusal message, and document it in the SKILL.md registry row (see H3). Refusing a complete repository is a refusal, not a verdict, so calibration is not broken; the cost is operability only.

## H2 — COUNTEREXAMPLE to "partial-clone … repositories … are refused" (docstring `:51`): the `--shared` seat recipe bypasses it

`git clone --shared` is the recorded seat recipe in rounds 20–22. Examples: `round-21/build/advice/AuditHexWordFP.md:6` and `round-22/build/advice/MatrixMutation.md:63`, plus the round-21 C1/C2 probes.

Fixture `out/CritTradeoffHarm/shared-of-partial.sh` (output `shared-of-partial.out`): a `blob:none` file:// partial fleet P, with S = `git clone --shared --no-checkout P`.
- S has `promisor_cfg=none`, `packs=0`, and an `alternates` file pointing at `P/.git/objects`.
- The report cites blob `c2981a99…`, which exists in the source (`cat-file -t` → `blob`) but is not local in P.

| arm | fleet = S (shared) | fleet = P (partial) |
|---|---|---|
| current | **exit 1**, `unresolved-full-hash c2981a9931` (false verdict) | exit 2, `partial clone (promisor pack)` |
| frozen | exit 1, same false defect | exit 0 (lazy-fetched; blob local afterwards) |

`check_history_repo` (`:438-448`) inspects only the repository's own `objects/pack` and config. Promisor packs reached through `objects/info/alternates` are never checked. The frozen arm has the same flip, so this is not a regression. It does show that the T01 refusal claim is incomplete on a real recipe path. It is also distinct from open item O01 (alternates make objects resolve *as local*): here, alternates hide *promisor status*, so a promised object becomes a `missing` defect.

Impacted axes: calibration (a verdict where the docstring promises a refusal) and identity (H1's R1/R2 split has the same cause).

Smallest safe correction: in `check_history_repo`, also scan `<alt>/pack/*.promisor` for each path in `git rev-parse --git-path objects/info/alternates`, recursively, and refuse on any match. Add a grid row "shared clone of a partial clone → exit 2". Alternatively, narrow the docstring to "a partial clone's own object store".

## H3 — Documentation: the operator-facing contract does not mention the tradeoffs

Round 23 did not touch SKILL.md, QUALITY.md or README (`git diff --stat 4fe9339f..245a37f` lists 11 files, none of them these).
- **SKILL.md:683** is the registry row for the checklist at `:687-690`. Its exit-2 map lists "missing/irregular report, unusable git, malformed ledger, empty round set, output failure". It omits shallow, grafted, partial-clone, non-sha1 and non-top-level refusals, as well as the git ≥ 2.45 floor.
- **SKILL.md:771** still says "D4 local-Git-config/history and UTF-8 hardening remains frontier."
- **`corpus/lessons/round-23.md:64`** cites KQ34 as the fix, but `rg 'KQ3[2-5]' corpus/QUALITY.md` finds only KQ32 and KQ33.

An operator who hits H1 has no registry text to act on. The fix is limited to documentation: add the refusals and the floor to the `:683` verdict map, and either register KQ34 or drop the reference.

## Real-workflow survey (what the tradeoffs would have to hit)

- **No recipe creates shallow or partial clones of audited repos.** I ran `rg -uu` for `clone…(--depth|--filter|--shallow|--bare|--mirror|--reference|--shared|--single-branch)` and `fetch-depth` over fleet `.ufo/prompts`, `scripts` and the lane. Results:
  - `--depth`/`--filter` appear only on upstream llama.cpp, ollama and git.git clones, which are not audited.
  - `--bare` appears in `scripts/hyaku/jj-lane-selftest.sh:68` (a test remote).
  - The lane-side clones use `--mirror`, `--shared` and `--no-hardlinks`.
  - There is no `.github` CI in the fleet or the lane.
- **Lanes must be real clones.** `scripts/hyaku/jj-lane.sh:75-79` refuses worktrees and anything without a `.git` directory. Neither real repo is shallow or partial: `--is-shallow-repository false`, no promisor/partial config, no grafts or alternates (checked before H1 appeared).
- **The real jj-colocated lane passes the current checks.** Real lane + `--shared` fleet: frozen and current both rc 0 with `defects=9 corrected=9 … clean`. The lane config holds `lane.branch` and `lane.id` and no refused keys.
- **Shallow (`run.out` R6/R7, plus extra runs):**

  | case | frozen | current |
  |---|---|---|
  | `--depth 1` fleet | rc 1, 14 defects / 5 uncorrected (false failure) | rc 2 |
  | `--depth 60` lane | rc 1, 25 uncorrected (false failure) | rc 2 |
  | `--depth 90` lane (98/99 commits) | rc 0 clean | rc 2 |
  | `--shared` clone of a shallow lane | same as its source | rc 2 (the shallow state propagates) |
  | `--depth 400` via file:// | not shallow (full history), so not a shallow test | — |

  The tradeoff costs only when depth happens to be sufficient, and no workflow produces that.
- **Defaults:**
  - R5, a seat clone with the default `--fleet-repo` (the parent directory): both arms rc 2 ("filesystem boundary"). This is unchanged.
  - R4, a tower-style git worktree nested under a fleet clone: frozen rc 2 "has no fleet commit"; current rc 2 "not a repository top level". Both refuse, with a clearer reason in the current arm, so this is not a regression.

## Not verified

- The identity of the agent that wrote the fleet markers, and whether they have been removed since 12:54:55 -0300 (still present then).
- Git below 2.45 on any other host or sandbox. OldGitFloor's matrix was not re-run.
- `tree:0` or ssh/https promisors through `--shared`. A `jj workspace add` layout.
- The full repo-state grid or mutants, which belong to other seats.
- Whether an "operator" ever runs on a non-Arch host.

## Installs

None.

## Files written

- `.ufo/waves/round-23/falsify/advice/CritTradeoffHarm.md` (this report)
- `.ufo/waves/round-23/falsify/out/CritTradeoffHarm/run.sh`, `run.out` (layout matrix R0–R9)
- `.ufo/waves/round-23/falsify/out/CritTradeoffHarm/shared-of-partial.sh`, `shared-of-partial.out` (H2)
- Scratch: `/tmp/kama-r23w2/CritTradeoffHarm` (clone), `/tmp/kama-r23w2/CritTradeoffHarm-fx/` (arms, fixtures `w/`, `sop.*`, recipe `.err` files)
- Peer message: `agent://CloseKama22` (H1 blocker). No lane-tracked, `.git`/`.jj`, fleet or global writes; no commits.
