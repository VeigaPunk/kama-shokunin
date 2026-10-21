# RowF15Sha256Lane — falsify report (row F15-sha256-lane, fault)

Auditor under test: `tools/report-landing-audit.py` @ 245a37f6; frozen arm = blob `4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py` (extracted to `/tmp/kama-r23w2/CloseKama22.RowF15Sha256Lane-2/frozen-audit.py`). All fixtures hand-built under `/tmp/kama-r23w2/CloseKama22.RowF15Sha256Lane-2/` with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1` and grid-equivalent argv (`--lane-repo --fleet-repo --json --rounds 1 --no-errata`, env scrubbed of `GIT_*`, cwd outside the repos). git 2.56.0, python 3.14.8. No installs.

## Verdict

**Row F15 itself holds — the grid is right.** The fault premise is real (frozen emits a *wrong verdict*, not a crash), the expected outcome (exit 2 + "object format") is the correct one, and the current auditor meets it on a by-hand fixture.

**But the same channel has a live hole that falsifies the broader C1 claim "must not crash, flip, hang or run programs":** a repository-local `include.path` (or a `.git/config` that is itself a FIFO) hangs **every** git invocation the auditor makes — the object-format refusal never runs. Both arms, frozen and current, hang; it is an inherited gap, not a regression, but it is a hang caused by repo-local git state inside the audited repos.

## (1) Fault premise — real, observed in frozen

Hand-built fixture `fix/`: `git init --object-format=sha256` lane with one commit `round-1: work` by `kama-shokunin` @1000 (64-hex HEAD `a8ed7535…bee5cd`, verified `rev-parse --show-object-format` = sha256); sha1 fleet with committed `.ufo/reports/round-1/kama.md` citing the 64-hex hash under `## Landed changes`.

Frozen arm output:

    EXIT 1
    defects: [{"kind":"landed-omitted","token":"a8ed7535…bee5cd","cited_elsewhere":false}]
    summary.status = "failed"

The premise is a genuine wrong-verdict defect, stronger than a crash: the report *does* cite the commit (full 64-hex), yet frozen reports `landed-omitted` because `ABBREV = (?<![0-9A-Za-z])[0-9a-f]{7,40}(?![0-9A-Za-z])` (frozen:67) cannot match >40 hex, so `cited` is empty while `round_commits` happily consumes the 64-hex `%H` (frozen:148-160 never validates sha width). A "clean" lane report gets a fabricated failure verdict — exactly the class of fault the row models.

## (2) Expected outcome — correct, and current meets it

Current on the same fixture:

    EXIT 2
    stderr: could-not-evaluate: /tmp/…/fix/lane: object format 'sha256', not sha1

`check_history_repo` (245a37f6:431-433) runs `rev-parse --show-object-format` first for **both** repos (475-476) before any history read, so the 40-hex scanners can never emit a sha1 verdict over sha256 names. Refusal (could-not-evaluate, exit 2) is the honest outcome — the auditor's defect taxonomy is sha1-shaped and cannot truthfully evaluate a sha256 lane; passing it would require a different audit, not a relaxation. The pinned reason string "object format" (REASONS, grid:585) is present. Confirmed refusal precedents also hold: sha256 *fleet* (v1) → `object format 'sha256'`; bare sha256 lane (v7) → same; linked worktree of a sha256 repo (v8) → same; uppercase `objectformat = SHA256` (v6) → git itself rejects the config, clean exit-2; sha256 objects with the extension stripped (v4) → safe exit-2 via `rev-parse --verify` failure (broken ref), never a verdict.

## (3) Near variants of the channel the current auditor still gets wrong

### F15-A (hang, live): repo-local config include / config FIFO — HIGH

    mkfifo v3inc/lane/.git/included.cfg
    printf '[include]\n\tpath = included.cfg\n' >> v3inc/lane/.git/config

- `timeout 5 git -C v3inc/lane rev-parse --show-object-format` → rc=124 (hangs).
- **Current auditor: TIMED_OUT after 8s — no stdout, no stderr, no traceback.**
- **Frozen auditor: TIMED_OUT after 8s** — identical.
- Variant `.git/config` *itself* a FIFO (v5): same — `rev-parse` rc=124, auditor hangs 8s+.

`git()` (245a37f6:108-127) has **no subprocess timeout**, and `GIT_ISOLATION` cannot mask includes — git reads the repo config on every command before any flag matters. `GIT_CONFIG_NOSYSTEM`/`GLOBAL=/dev/null` only cover host-level files. This is a *different repo-local read* than the `.mailmap` FIFO the grid models (F14 blocks on `git log` only with `log.mailmap` enabled); the include FIFO blocks the very first `rev-parse`, before the object-format gate, the shallow gate, everything. Under the grid harness this scores `timed_out → met=False` — a fault the committed auditor still commits: repo-local git state **hangs** it. Not fixed, only ungridded. (Sibling F21 builder `f_nested_subdir` touches the same config-parse surface but not this FIFO; grid has no include.path row.)

### F15-B (semantic, live): >40-hex tokens are invisible to every scanner — MEDIUM

    report cites real 40-hex sha1 commit AND fabricated 64-hex token
    (v2mine, pure sha1 lane+fleet):

    EXIT 0, defects: [], summary.status = "clean"

A fabricated 40-hex token yields `unresolved-full-hash` (grid C03 proves it); a fabricated **64-hex** token — a sha256-shaped citation inside a sha1 world — yields *nothing*: `FULL`/`ABBREV` cap at 40 hex (76-77), `checkable_abbrev` never sees it (173-177). The auditor silently ignores a citation it cannot evaluate instead of refusing or flagging — the mirror image of the F15 hole: F15 makes sha256 *repos* unevaluable; >40-hex *tokens* in sha1 repos remain unevaluable-and-undetected. Frozen behaves identically (same regexes), so inherited, but it is a missed-detection defect in the same object-format/hash-width channel. Every hex token ≥41 chars is a dead zone.

## What I did NOT verify

- Whether the auditor's sibling tools (`tools/report-*.py` others) share the FIFO/width holes — declared "unisolated" out of scope by the build wave.
- git versions < 2.45 (declared floor; mine is 2.56.0). `--show-object-format` needs ≥2.29; fine on the declared floor.
- `includeIf gitdir:/onbranch:/hasconfig:` variants of the include FIFO — same code path as `include.path`; expect identical hangs but not separately run.
- Whether V3/V5's hang is unbounded (verified ≥8s at auditor level, ≥5s raw git; FIFO has no writer so open(2) blocks indefinitely).
- Reftable/`compatObjectFormat` (git-WIP interop) — not exercised.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/advice/RowF15Sha256Lane.md` (this report)
- `/tmp/kama-r23w2/CloseKama22.RowF15Sha256Lane-2/` — `frozen-audit.py`, `run_case.py`, `build-f15.sh`, fixtures `fix/` `v1/` `v2mine/` `v3inc/` `v4/` `v5/` `v6mine/` `v7/` `v8/` (scratch; no lane writes)

## Note to L1

F15 row: keep as-is (passes). But the C1 axis score "no hang" is falsifiable via F15-A: any repo-local FIFO in the config-read path hangs the auditor before its refusals. Cheapest grid-shaped fix would be a `timeout=` in `git()` plus a refuse-on-timeout EvalError; a new grid row for `include.path`→FIFO would pin it. F15-B is a detection gap, defensible only if the auditors' contract explicitly scopes citations to 40-hex (it does not appear to).
