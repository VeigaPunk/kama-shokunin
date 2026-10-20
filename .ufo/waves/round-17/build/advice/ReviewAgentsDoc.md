VERDICT: partial — no current lane rule orders a git write, but the only VCS rule names a citable hash line the helper it cites never prints, omits exit-3/no-op semantics, and five historical verifier protocols still assume `@{u}`/HEAD.

# ReviewAgentsDoc — VCS instructions for a jj-colocated lane

Read-only review seat (`KamaR17.ReviewAgentsDoc-2`). No subagent, no `jj` invocation, no git write, no
lane gate/measure/controls run. Sole write: this file. Snapshot taken 2026-10-20: git 2.56.0;
`master == origin/master == cff9e62f05aa7cfb9059444f62eb787100719713`; `jj-lane.sh state` →
`branch=master ... ahead=0 behind=0 head=detached`.

## 1. Method (only read-only commands)

- `grep -n -E 'git |jj |@\{u\}|abbrev-ref|show-current|\bHEAD\b|commit\b' AGENTS.md SKILL.md PROVINCE.md README.md SHONEN.md MINT.md corpus/QUALITY.md`
- `grep -rn -E "@\{u\}|rev-parse HEAD|rev-list --count|merge-base --is-ancestor[^|]*HEAD" corpus/lessons/` (with `--exclude-dir=interactive-sessions --exclude-dir=.git --exclude-dir=.jj` on every recursive sweep)
- `grep -rn -E 'git +(add|commit|stash|checkout|switch|reset|restore|push|pull|rebase)' tools tests .ufo/waves/round-13 .ufo/waves/round-16 .ufo/waves/round-17 --exclude-dir=frozen`
- detached-HEAD matrix, executed in the lane: `git symbolic-ref -q --short HEAD` → rc 1;
  `git rev-parse --abbrev-ref HEAD` → `HEAD` rc 0; `git branch --show-current` → empty rc 0;
  `git rev-parse '@{u}'` → `fatal: HEAD does not point to a branch` rc 128;
  `git rev-parse master` / `refs/heads/master` / `origin/master` → `cff9e62…`;
  `git rev-list --count origin/master..master` → `0`.
- Read (not executed): `scripts/hyaku/jj-lane.sh`, `scripts/hyaku/jj-lane.sh.new`,
  `scripts/hyaku/lane-addendum.md`, `scripts/hyaku/closure-prompt.md`,
  `.ufo/waves/hyaku/jj-w1/reports/JjAuditKama.md`.

## 2. Complete inventory — instructions that order git writes or lean on attached HEAD/`@{u}`

### 2a. Current lane instruction docs (what an agent reads before working)

| file:line | instruction (≤25-word quote) | class | status |
|---|---|---|---|
| `AGENTS.md:6` | "Commits land only through `/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh commit <lane>`" | jj route, no git write | correct route, under-specified (F1–F7) |
| `AGENTS.md:6` | "cite only the hash it prints as `landed`/`pushed`" | citable-hash rule | **`landed` never printed by the named helper; `committed` not excluded** (F1) |
| `AGENTS.md:6` | "never a mutating `jj` command here" | jj prohibition | self-contradictory as written (F3) |
| `AGENTS.md:6` | "Git HEAD is detached after a helper commit" | HEAD claim | cause wrong, behavior imprecise (F5) |
| `AGENTS.md:6` | "never `@{u}`, `--abbrev-ref HEAD` or `branch --show-current`" | HEAD prohibition | correct, keep |
| `AGENTS.md:6` | "Gates that need git writes run in a `/tmp` clone." | git write, isolated | correct, keep |
| `AGENTS.md:6` | "jj ignores git hooks and `.gitattributes` eol/filters" | write expectation | correct per `JjAuditKama` F5–F6 |
| `SKILL.md` | none — exact verb grep (`git commit|add|push|pull|checkout|switch|reset|stash|restore|rebase`, `jj commit`, `@{u}`, `--abbrev-ref`, `show-current`) exits 1, no match | — | clean |
| `SKILL.md:409` | "revision and does not track mutable `HEAD`." | read-only provenance | compliant |
| `SKILL.md:417-418` | "Capture via `git show` … `git cat-file blob`" (both pinned-revision) | read-only provenance | compliant |
| `SKILL.md:534` | "= blob of `20e392e:tools/kama-probe.sh`" | read-only provenance | compliant |
| `PROVINCE.md`, `README.md`, `SHONEN.md`, `MINT.md` | no `git`/`jj`/`commit` match at all | — | clean |
| `corpus/QUALITY.md:49,61` | KQ15/KQ16 require `git show <pinned>:<path>` capture and `git cat-file blob` comparison | read-only provenance | compliant |
| `scripts/hyaku/jj-lane.sh:38-43` | usage lists `commit <lane-dir> … -- <path>...`; exit map only | helper docs | no agent instruction; omits citable-line rule (F1/D3) |

**Result: zero current lane instruction tells an agent to run a git write or to read `@{u}`/`HEAD`.**
The only current VCS rule is `AGENTS.md:6`, and its defects are specification gaps, not git-write licence.

### 2b. Historical lane instruction residue (dated records — never edit; add forward pointer)

| file:line | command text (≤25-word quote) | fails today |
|---|---|---|
| `corpus/lessons/round-11-verifier-spotcheck.md:43` | "`git -C <lane> merge-base --is-ancestor <hash> HEAD`" | tests working-copy `HEAD`, not branch tip |
| `corpus/lessons/round-11-verifier-spotcheck.md:44` | "`git -C <lane> rev-list --count @{u}..HEAD`; `git -C <lane> rev-parse HEAD`" | `@{u}` exits 128 |
| `corpus/lessons/round-12-verifier-spotcheck.md:30-31` | "`rev-parse HEAD`" / "`rev-list --count @{u}..HEAD`" | 128 on `@{u}` |
| `corpus/lessons/round-12-verifier-spotcheck.md:32-34` | "`merge-base --is-ancestor <hash> HEAD`" | wrong revision when detached |
| `corpus/lessons/round-13-verifier-spotcheck.md:39,55` | "`rev-list --count '@{u}..HEAD'`" / "`merge-base --is-ancestor HASH HEAD`" | 128 on `@{u}` |
| `corpus/lessons/round-14-verifier-spotcheck.md:32,38` | "`rev-list --count '@{u}..HEAD'`" / "`merge-base --is-ancestor HASH HEAD`" | 128 on `@{u}` |
| `corpus/lessons/round-15-verifier-spotcheck.md:33,39` | "`rev-list --count '@{u}..HEAD'`" / "`merge-base --is-ancestor HASH HEAD`" | 128 on `@{u}` |
| `.ufo/round-6/SEAT-PROTOCOL.md:18` (same in 7–9) | "Do not commit. Do not run `git commit`. The L1 owns the round commit." | prohibitions only; no jj route |
| `.ufo/round-6/SEAT-PROTOCOL.md:23` (same in 7–9) | "Commit hashes: `git cat-file -e <hash>`." | read-only; safe |

These are the only historical lane texts containing copyable `@{u}`/bare-`HEAD` commands. The fleet closure
prompt is already jj-correct (`closure-prompt.md:52-54`), so the risk is a future verifier copying the
round-11…15 lesson blocks rather than reading today's order.

Whole-lane recursive sweep (`--exclude-dir=interactive-sessions --exclude-dir=.git --exclude-dir=.jj`)
found no other instruction surface: the remaining hits are dated narrative only — `LOG.md`,
`SCORECARD.md`, `plans/wwkd-round-5-interactive-freshness.md:5` ("Start HEAD `c390918…`"), and prior
`.ufo/waves/round-*/build/advice/*` seat artifacts. None is a current instruction, and none was edited.

## 3. Findings (severity order)

### F1 — HIGH — the one citable token the lane orders does not exist in the helper the lane names
`AGENTS.md:6`: "cite only the hash it prints as `landed`/`pushed`". The named helper prints
`committed <hash>` (`jj-lane.sh:235`, quote: `echo "committed $hash"`), and `pushed <hash>`
(`jj-lane.sh:111`, quote: `echo "pushed $(jj_ids "heads(${BRANCH}@origin)" commit_id | head -1)"`); `grep -c landed
/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh` → `0`. The only emitter of `landed <hash>` is `jj-lane.sh.new:243,249` (mtime 12:01; [INFERENCE] a
successor in progress — nothing in the lane or fleet names or installs it), documented at `jj-lane.sh.new:58`: "only citable line is
`landed <hash>`" — and no lane doc names it. The fleet addendum resolves the ambiguity
(`lane-addendum.md:126-127`: "an older helper prints `pushed <hash>` … never a `committed <hash>`
line"); the lane doc does not. A seat waiting literally for `landed` gets no such line, and the
`committed` line it does get is the one hash that must never be cited.

### F2 — HIGH — exit 3 and no-op exit 0 are undocumented; both are reachable "successful-looking" outputs
`jj-lane.sh:239`: `do_push || exit 3`; `jj-lane.sh:199`: `echo "nothing to commit (no such paths)"; exit 0`.
`AGENTS.md:6` says neither. Consequences: a mistyped path prints `nothing to commit (no such paths)`,
exits 0, and lands nothing; an empty diff (`:219`) prints `nothing to commit` with no hash for that run;
a failed push exits 3 after printing
only `committed <hash>`. The fleet addendum states both rules (`lane-addendum.md:128-129`: "Exit 3 =
committed but not pushed → rerun … `nothing to commit` lands nothing"). The lane rule must carry them
or a seat can cite a local-only hash or report a no-op as landed.

### F3 — MEDIUM — "never a mutating `jj` command here" contradicts the route it just prescribed
`AGENTS.md:6`: "never a mutating `jj` command here". The prescribed `jj-lane.sh commit` internally runs
`jj commit`, `bookmark set`, and (on recovery) `rebase` (`jj-lane.sh:229-239`). Read literally, the rule
forbids the only sanctioned path. The addendum's wording is unambiguous
(`lane-addendum.md:135-136`: "never run a mutating jj command yourself … the helper is the only writer").

### F4 — MEDIUM — git-write verb list is narrower than the enforced round contract
`AGENTS.md:6` forbids "`git add`/`commit`/`stash`/`checkout`/`switch`/`reset`/`pull`/`push`" — omitting
`restore` and `rebase`, both named in this round's seat contract and in the fleet order
(`lane-addendum.md:131-136`). A seat reverting a file with `git restore <path>` breaks the jj working-copy
invariant without violating the lane doc as written; the addendum's prescribed revert is
`git show <branch>:<path> > <path>` (`lane-addendum.md:141-142`).

### F5 — MEDIUM — detachment cause and the two silent-failure commands are described imprecisely
`AGENTS.md:6`: "Git HEAD is detached after a helper commit". `JjAuditKama.md:3` measured the lane at
audit start with "tip at audit start `726f737…` (attached, `master...origin/master` in sync" — so
detachment is a jj working-copy state, not a guaranteed post-commit effect (attached at `726f737` at audit
start; detached at `cff9e62` now). The parenthetical "(both print junk with exit 0 when detached)"
(`AGENTS.md:6`) attaches to a three-command list and is wrong for `@{u}`, which exits 128 with a fatal
line; `branch --show-current` prints the empty string, not junk. Measured matrix in §1.

### F6 — LOW — `<lane>` is not a directory; a literal copy fails
`AGENTS.md:6` writes `jj-lane.sh commit <lane>`, while the helper's own usage says `<lane-dir>`
(`jj-lane.sh:40`) and `cmd_commit` rejects anything without `.jj` (`jj-lane.sh:186`:
`[ -d "$dir/.jj" ] || { err "not jj-colocated ...`). A seat substituting the lane id `kama` exits 1.
Use the absolute lane path.

### F7 — LOW — path, directory, and size rules are absent (prospective)
`AGENTS.md:6` omits: paths are repo-relative, no `..`, no glob characters, `.ufo/state/*` and
`.ufo/watchdog.log` refused (`jj-lane.sh:181-184`); a named directory commits only files jj can track,
and new files over jj's 1 MiB cap are skipped unless named as files (`jj-lane.sh:201-214`; addendum
`lane-addendum.md:129-131`: "new files over 1 MiB inside it are skipped with a warning"). No current
round-17 file exceeds 1 MiB (`find .ufo/waves/round-17 -type f -size +1M` → empty), so latent only.

### F8 — INFO — the jj audit's gitignore half is stale; no action
Root `.gitignore` now contains `.ufo/state/` (line 2) and `registry/history/.gitignore:3` contains
`.lock`, so `JjAuditKama` §4/R1's "not gitignored" observation no longer holds. Verified, not inferred.

### F9 — INFO — helper replacement changes the legal path surface
`jj-lane.sh.new:28` states "`.ufo`, `.ufo/state`, `.git` and `.jj` are never committable" and enforces it
at `:485`; the installed helper allows `.ufo/waves/...` (only `.ufo/state/*` and `.ufo/watchdog.log`
are refused). If the replacement is installed mid-round, every lane evidence commit under `.ufo/waves/`
would be refused. [INFERENCE] uninstalled today; flag for the fleet owner, not a lane-doc defect now.

## 4. Exact replacement wording

### 4a. `AGENTS.md:6` — paste-ready replacement (one bullet)
```markdown
- VCS (round 17, 2026-10-20): this repo is jj-colocated (git stays the backend and remote). Land work only through
  `/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh commit /home/vgpnk/Projects/shokunin/kama-shokunin --as kama -m "<what>" -- <repo-relative paths>`
  — the first argument is the lane directory; paths are repo-relative, no `..`, no glob characters; `.ufo/state/*` and
  `.ufo/watchdog.log` are refused, and a missing path is skipped: exit 0 with `nothing to commit` landed nothing.
  Cite ONLY the remote-verified hash line the helper prints — `pushed <hash>` on the installed helper, or
  `landed <hash>` if the helper prints that — and NEVER the `committed <hash>` line: a push-recovery rebase rewrites it. Exit 3 =
  committed but not pushed: rerun `jj-lane.sh push /home/vgpnk/Projects/shokunin/kama-shokunin`, never force.
  Read-only git (log, show, diff, status, ls-files, rev-parse, merge-base) is fine; never any git write — `add`,
  `commit`, `stash`, `checkout`, `switch`, `reset`, `restore`, `rebase`, `merge`, `pull`, `push`, `rm`, `mv`, `clean`,
  `update-index` — and never run `jj` yourself (`commit`, `new`, `describe`, `squash`, `rebase`, `abandon`, `bookmark`,
  `undo`, `op restore`/`revert`, `git push`/`fetch`): the helper is the only writer. Git HEAD may be attached or
  detached (jj's working-copy commit): read the lane tip with `git rev-parse master` or
  `jj-lane.sh state /home/vgpnk/Projects/shokunin/kama-shokunin` (`local=`, `ahead=`, `head=`), never `@{u}` (exit
  128), `--abbrev-ref HEAD` (prints `HEAD`, exit 0) or `branch --show-current` (prints empty, exit 0). Record
  measured/pinned revisions as the branch tip, never bare `HEAD`; revert a tracked file with
  `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show master:<path> > <path>`, never `git checkout`/`git restore`.
  Gates that need git writes run in a throwaway `/tmp` clone (`git clone /home/vgpnk/Projects/shokunin/kama-shokunin
  /tmp/<name>`; committed refs only), deleted afterwards. jj ignores git hooks and `.gitattributes` eol/filters: add
  neither expecting them to fire.
```

### 4b. Forward pointer for the historical verifier blocks (append to `AGENTS.md`, do not edit the lessons)
```markdown
- Historical verifier lessons (`corpus/lessons/round-11…15-verifier-spotcheck.md`) quote `@{u}..HEAD` and bare `HEAD`.
  Those commands predate jj colocation: use `git -C <lane> rev-list --count origin/master..master`,
  `git -C <lane> rev-parse master`, and `git -C <lane> merge-base --is-ancestor HASH master`.
```

### 4c. Verifier command substitutions (exact; the first three were run in this lane)
- `git -C <lane> rev-list --count @{u}..HEAD` → `git -C <lane> rev-list --count origin/master..master` (returns `0` now).
- `git -C <lane> rev-parse HEAD` → `git -C <lane> rev-parse master` (`cff9e62…`).
- `git -C <lane> merge-base --is-ancestor HASH HEAD` → `git -C <lane> merge-base --is-ancestor HASH master`.
- Pushed confirmation: `git -C <lane> ls-remote origin refs/heads/master` must equal `git -C <lane> rev-parse master`,
  and `jj-lane.sh state <lane>` must show `ahead=0 behind=0`.
- Keep `git -C <lane> status --porcelain` (read-only; works detached), but an empty worktree is not required while
  sibling seats write — currently 2 tracked + 1 untracked entry.

### 4d. Fleet-owned (outside this lane; for the helper owner, not L1's lane commit)
Add to `jj-lane.sh` usage after the exit line (line 43, before `EOF` at line 44):
```
output: `pushed <hash>` (or `landed <hash>` after the helper upgrade) is the only citable line;
        `committed <hash>` is pre-push and never citable; exit 3 = rerun `jj-lane.sh push <lane-dir>`.
```

## 5. What is already correct — do not churn
- `AGENTS.md:6` already forbids the git writes, names the helper, and names the two silent-HEAD commands; only its
  citation/exit/no-op clauses need the §4a text.
- `SKILL.md` is already jj-correct: every git reference is a read at a pinned revision (`:396,406,409,417-418,534`);
  exact verb grep for writes/`@{u}` returns no match.
- The helper itself is jj-safe for reads: `print_state` uses `refs/heads/$branch` and `refs/remotes/origin/$branch`,
  not `HEAD` (`jj-lane.sh:70-81`), and `detect_branch` prefers a symref then `origin/HEAD` (`:50-65`).

## 6. Limitations and verification gaps
- The helper was read, never executed (any `commit` writes the lane); `.new` likewise. Exit-3 behaviour is read from
  `jj-lane.sh:239`, not exercised.
- `AGENTS.md` is an uncommitted worktree change at review time (`git status` → ` M AGENTS.md`); every `AGENTS.md:6`
  quote and the §4a replacement describe that working-tree text, not `master:cff9e62:AGENTS.md`.
- Lane state is a timestamped snapshot; sibling seats write concurrently (`git status` showed 3 entries).
- The `landed`-vs-`pushed` comparison relies on file bytes at 11:08 (`jj-lane.sh`) and 12:01 (`jj-lane.sh.new`); a fleet
  swap during integration would invalidate the "installed helper" attribution.
- Historical lessons were read, not modified; no claim is made that any verifier actually re-ran their commands after
  colocation.
- Tool installs: none. No package, binary, config or service was installed or changed.

## 7. Residual risk
- `jj-lane.sh.new`'s `.ufo` refusal (F9) plus the token change means a mid-round helper swap can silently break both
  evidence commits and the citation rule; the §4a wording is written to survive the token change but cannot survive
  the `.ufo` refusal.
- [INFERENCE] `jj` may leave `HEAD` attached at the bookmark tip after some operations and detached after others; no
  lane rule should ever read `HEAD`, which §4a now states explicitly.
