VERDICT: partial — no untracked fleet-root file names kama round 17, but round-17-named empty residue and a legacy cross-lane error-path file remain at the fleet root.

# Seat: MisrootSweep (round-17 FALSIFY, scout)

Read-only placement sweep of the fleet root and the lane root at lane HEAD
`54a29268e2083caa2b1e0d54ee1e7d90961302f3`. No lane tool, gate, measurement,
mutant or server was run (no clone needed), no git/jj write, no port bound or
contacted, no install. Only this Report was written.

## 1. The asked question: untracked fleet-root files naming kama round 17

`git -C /home/vgpnk/Projects/shokunin status --porcelain` (exit 0) yields exactly
two kinds of untracked fleet-root entries:

| Path | State | Content check |
|---|---|---|
| `.ufo/reports/round-19/mado.md` | untracked | `grep -c -i kama` → 0 (exit 1); `round-17` appears 2×, at `mado.md:82` (`.ufo/waves/round-17/measure.py` counting command) and `mado.md:106` ("round-17 hardening reads 32/33"). No kama. |
| `.ufo/state/{kaidoku,kake,kama,mado,mori,souji,tabi,tameshi,tsukuroi}.report-baseline` | untracked | Contents NOT read, per contract. `kama.report-baseline` names kama but not round 17. |

**No untracked fleet-root file's content names kama round 17.** The only
fleet-root file whose content names it is tracked and modified:
`.ufo/watchdog.log:484` — `2026-10-20T11:52:26-03:00 launch kama round=17
pgid=3049098 driver=hyaku-inline attempt=1`; `git diff --numstat` = `27 0`.
Tracked `.ufo/prompts/kama-round-17.md` also names it by path (not untracked).

## 2. Round-17-named fleet-root artifacts (residue, no content)

- `.ufo/waves/round-17/` mtime `2026-10-20 12:26:28`, containing only `w1/`
  mtime `2026-10-20 12:27:49`; `find -type f` → 0 files; `git ls-files` → 0.
  Empty directories are invisible to `git status`, so porcelain cannot report
  this. Ownership is unattributable from empty content; its timing follows the
  round-17 build commit (11:50) and is consistent with the relative-path
  misroot class, but other lanes also ran round 17 concurrently. [INFERENCE]
- `.ufo/reports/round-17/` holds 10 **tracked** per-lane reports (`kagi.md`,
  `kaidoku.md`, `kake.md`, `kasegi.md`, `kotoba.md`, `kotodama.md`,
  `kumitate.md`, `mado.md`, `tabi.md`, `tsukuroi.md`) and **no `kama.md`**
  (`ls | grep -i kama` exit 1). This is the fleet's normal report drop, not a
  misroot.

## 3. Documented transient misroots during the round-17 build

`.ufo/waves/round-17/build/advice/ScoutR16SummaryBug.md:64`:
"`RevengerS041Edit.md` … sits at the fleet root, the same relative-path misroot
class reported in round 16." `:65` records the seat's own misplaced
`ScoutR16SummaryBug.md` copy was deleted. Both paths are now absent from the
fleet root (`test -f` fails), so the class recurred in the build wave and was
cleaned; nothing content-bearing from it remains.

## 4. Legacy error-path misroot (not kama, not round 17)

`/home/vgpnk/Projects/shokunin/bash: /home/vgpnk/Projects/shokunin/
souji-shokunin/tests/tools/souji-verify.sh: No such file or directory` is a
directory tree whose leaf name is a shell error string, holding one 10139-byte
JSON seat receipt: `"seat": "S54"`, `"round": 4`, `"lane": "souji-shokunin"`.
`grep -c -i kama` → 0 (exit 1). Created 2026-10-18 14:01, before the round-17
start (`cff9e62`), ignored by fleet `.gitignore:1` (`*-shokunin/`). Not touched.

## 5. Untracked / ignored files inside the lane

`git -C …/kama-shokunin status --porcelain -uall` (exit 0): 12 untracked files,
all under `.ufo/waves/round-17/falsify/` — this wave's runtime artifacts
(`spec.json`, `dispatch.json`, `dispatch.stderr`, `spawn-result.json`,
`task-result-27.json`, `assignments.json`, `attempts.json`, `validation.json`,
`provenance-ledger.json`, `record.stdout`, `make_spec.py`,
`advice/swarm-registry.json`). No path carries an absolute path, `bash: `, or an
error-string name.

Ignored top-level names (`--ignored`): `.jj/`, `.ufo/interactive-sessions/`,
plus files `registry/history/.lock`, `registry/history/20261014T124232Z.json`,
`registry/history/20261014T124525Z.json` (attributed by
`registry/history/.gitignore:2 *.json` and `:3 .lock`). Lane `.gitignore`
lines 1-3 are `.ufo/interactive-sessions/`, `.ufo/state/`, `__pycache__/`;
`.ufo/state` does not exist in the lane. `.jj/` is reported ignored by status
but `git check-ignore` attributes no rule [INFERENCE: jj-internal ignore].

## 6. Did a misroot land in the commit?

`git show --name-status 54a2926`: 187 files, `+47386/-177`, 166 additions under
`.ufo/waves/round-17/`, 0 deletions. Path scan for `kama-shokunin/`,
`bash: `, `: No such`, `/home/vgpnk`, `~`, `|` → no match (grep exit 1).
Lane HEAD equals the attacked commit; parent is the round start `cff9e62`.
No misrooted path is in the commit.

## Commands run (all read-only, exact)

- `git -C /home/vgpnk/Projects/shokunin status --porcelain` → 0
- `git -C /home/vgpnk/Projects/shokunin status --porcelain --ignored` → 0
- `git -C /home/vgpnk/Projects/shokunin status --porcelain -uall` → 0
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain --ignored` → 0
- `git -C …/kama-shokunin status --porcelain -uall` → 0
- `git -C …/kama-shokunin log -1 54a2926`; `git show --name-status/--numstat 54a2926` → 0
- `git -C …/kama-shokunin rev-parse --short HEAD` → `54a2926` (0)
- `git check-ignore -v registry/history/.lock …` → 0 (two rules printed)
- `git -C /home/vgpnk/Projects/shokunin ls-files .ufo/waves/round-17 .ufo/reports/round-17` → 10 (reports only)
- `grep -c -i kama .ufo/reports/round-19/mado.md` → 0 matches, exit 1
- `grep -rIl -i kama .ufo/waves/**-scratch` → 0 (exit 0, no files)
- `grep -c -i kama <bash: error-path file>` → 0, exit 1
- `stat/find` on `.ufo/waves/round-17` and `.ufo/reports/round-17` → 0
- `ss -ltnp | grep -E ':(8080|34113)\b'` → exit 1 (no listener)
- `sha256sum` in falsify: `spawn-result.json` `1e9c9736…`, `task-result-27.json`
  `10618fe6…` (distinct, both this wave's scheduler output)

## Limitations

- `.ufo/state/` contents deliberately unread (9 untracked baselines, including
  `kama.report-baseline`); `.tower/`, `.ufo/interactive-sessions/` and sibling
  lane repos were not descended. The `bash: /` artifact belongs to souji and was
  only read, not moved.
- No lane tool was executed, so no `PYTHONDONTWRITEBYTECODE`/clone clause was
  needed. No `/tmp/KamaR17.MisrootSweep-*` scratch was created; pre-existing
  `/tmp/misroot*` and `/tmp/tameshi-r16-Misroot-demo` are not mine and were not
  touched.
