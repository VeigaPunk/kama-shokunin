VERDICT: confirm — at 54a29268 the R1 fix does exactly what the lessons claim: pristine worktree 0/clean, harmless uncommitted append 4/worktree_not_at_measured_revision, real content or prefix failure still 1, unreadable input 3, selftest 13/13; the pre-round copy reproduces the old exit 1 on the identical state.

# What I attacked

The jj-migration R1 fix landed in `.ufo/waves/round-13/measure.py` at lane commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3` (round-17 lessons, R1 bullet, `corpus/lessons/round-17.md:131-136`), plus its three new selftest sandbox cases and the frozen pre-round copy. Everything below ran in a throwaway `git clone` of the lane checked out at that commit; the lane itself was only read (`git rev-parse`, `git cat-file`, `sha256sum`), never executed in, never written except this report.

# Confirmations (direct execution)

**1. Selftest is 13/13, exit 0.** `--selftest` printed `"passed": 13, "failed": 0, "finding": "clean", "verdict_exit": 0`; the three live-sandbox cases observed 4/`worktree_not_at_measured_revision`, 0/`clean`, 1/`documentation_mismatch`, matching the claim at `corpus/lessons/round-17.md:134`: "Selftest 13/13 (three new sandbox cases)". The sandbox creates its own git repo inside `TemporaryDirectory` and repins a copy's `BEFORE_REVISION`; nothing was written in the clone (`git status --porcelain` empty after the run).

**2. Clean committed state at the lane commit exits 0.** `rolling` at `54a29268` (clean checkout, `worktree_matches_head` true) returned `finding: clean`, `verdict_exit: 0`, `measured_revision: 54a29268e2083caa2b1e0d54ee1e7d90961302f3`, `resolved_before_oid: 941bb32c3f591bc63cbf7579b2b6c552228307cd`, `historical_prefix_preserved: true`, `before_missing_assertions: 2`, `after_missing_assertions: 0`. This is the code path `measure.py:480` (`elif clean: finding = 'clean'`) after the predicate at `measure.py:466-474`.

**3. One harmless uncommitted line → exit 4, exactly one observation.** Appending `<!-- KamaR17.R13GateSandbox harmless uncommitted probe line -->` to `corpus/QUALITY.md` gave exit **4**, `finding: worktree_not_at_measured_revision`, `observations: ['worktree_not_at_measured_revision']`, `content_clean: true`, `worktree_matches_head: false`, `final_sha256 != head_quality_sha256`. The branch at `measure.py:475-488` is the only producer of code 4, and `FINDINGS[...] = 4` is at `measure.py:126`; the docstring promise at `measure.py:42-43` — "verdict is worktree_not_at_measured_revision (exit 4) whenever every other check is clean" — held.

**4. Why this was exit 4 and NOT the exit-1 alternative in my ticket.** The canonical before-pin *does* still match: the worktree QUALITY.md begins with the exact historical blob bytes (8619 bytes, `prefix_preserved: true`), the resolved before oid equals the hard-coded `BEFORE_REVISION`, and the before assessment still misses exactly the fixed denominator of 2. A content failure (exit 1) requires a genuine check failure, which I produced deliberately:
- corrupting `source_mismatch=1` → `=9` inside the appended KQ16 admit cell: exit **1**, `documentation_mismatch`, divergence kept as observation (`measure.py:142`: "only while divergence is the sole failure, and any other check failure still reports documentation_mismatch");
- rewriting the file's first byte (true prefix violation): exit **1**, observations `prefix_violation`, `worktree_not_at_measured_revision`;
- appending a second KQ16 row: exit **1** (multiple-row/content failure), missing 0;
- rewriting the historical KQ15 row: exit **1**, `prefix_violation` + `kq15_lines_preserved: false`;
- clean worktree but `--before-revision cff9e62` (a rev that is not the pinned start): exit **1**, observations `before_revision_not_pinned_start`, `before_missing_assertions_not_denominator`.

So "the before-pin no longer matches" would exit 1, not 4; at this commit it matches, hence 4.

**5. Causality: the pre-fix bytes reproduce R1's false failure on the identical state.** Running the frozen pre-round copy (`sha256 2399d64d…`, byte-identical to `git show cff9e62:.ufo/waves/round-13/measure.py`, 39463 bytes) against the same divergent worktree gave exit **1** `documentation_mismatch` with observation `worktree_not_at_measured_revision`; the fixed script gave **4** on the same bytes. That matches the audit's finding, `.ufo/waves/hyaku/jj-w1/reports/JjAuditKama.md:154`: "Under jj, `@` is perpetually ahead of `HEAD` until the helper commits and moves the bookmark".

**6. Frozen manifest mode is unchanged by worktree divergence.** `--manifest .ufo/waves/round-13/frozen/expected.json` with the dirty worktree returned `mode: frozen-pinned`, `finding: clean`, exit **0** — the R1 fix is live-mode only, as the docstring says.

**7. Probe-error precedence survives.** `--quality /nonexistent/QUALITY.md` → exit **3** `probe_error`; `--quality corpus` (a directory) → exit **3**. A failed git read also stays 3 (see risk 4).

**8. Identities line up.** Lane `HEAD` is detached at `54a29268e2083caa2b1e0d54ee1e7d90961302f3` and `refs/heads/master` is the same oid; lane `.ufo/waves/round-13/measure.py` sha256 `38b8123920d3963f22de7164f33e88ac4117827272300bd4a2c07fb0b18c736b` equals the HEAD blob sha, and lane `corpus/QUALITY.md` sha256 `7dd1a3003b418dbf5207c6250fe001fcb5b7592b861c69a02931b973497328f4` equals its HEAD blob sha — so the clone tests ran on the lane's bytes. `AGENTS.md:6` states the ordering: "Run the round-13 live gate only after the helper commit (an uncommitted QUALITY.md now exits 4, could-not-evaluate)."

# Risks / limits (advisory, none falsifies the declared claim)

- **R1-1 byte-only divergence.** `chmod +x corpus/QUALITY.md` (git sees `M`) left `worktree_matches_head: true` and the gate exited **0 clean**: the comparison is `final == head_quality`, i.e. bytes. The code is internally accurate (`measure.py:38` "When the --quality bytes differ from the measured HEAD blob"), but `AGENTS.md:6`'s unqualified "an uncommitted QUALITY.md now exits 4" overstates it for mode-only edits. Suggest wording "uncommitted QUALITY.md bytes".
- **R1-2 exit 4 is not an anti-tamper property.** Committing the appended line moved HEAD, and the gate then exited **0 clean** with `measured_revision: f2d0c4d…`; this is the documented LIMITS entry (`measure.py:142`) that live mode only grades the measured HEAD's wording. The jj audit's model (`JjAuditKama.md:173`: "HEAD at any instant is the last *helper-committed* tree") makes helper-commit-then-gate the intended order, not a defect.
- **R1-3 `checks.kq15_lines_preserved` cannot fail independently in live mode.** It is subset containment (`measure.py:272`: `all(line in final_lines for line in lines)`) and is absent from the `clean` predicate (`measure.py:466-474`); appending a duplicate KQ15 row left it `true` (observed `kq15_row_count: 1`). It is evidence only when `prefix_preserved` already went false; do not read it as a duplicate-row guard.
- **R1-4 the archived copy is not runnable in place.** `.ufo/waves/round-17/frozen/round-13_measure.py` derives `LANE = Path(__file__).parent.parents[2]`, which resolves to `.ufo` at that path; run in place with `--quality corpus/QUALITY.md` it exits **3** `probe_error` (`git rev-parse exited 128: fatal: not a git repository …`, because `GIT_CEILING_DIRECTORIES = LANE.parent` blocks ascent to the repo root). Its manifest claim is digest-only and intact (sha256 `2399d64d…` matches manifest and `cff9e62` blob), and my pre-fix replay worked by placing the copy at `<clone>/.ufo/waves/round-13/measure_frozen.py` so `LANE` resolves to the repo root. Any future "rerun the frozen baseline in place" expectation will see 3, not 0/1/4.

# Exact commands and exit codes (all in `/tmp/KamaR17.R13GateSandbox-clone`, `PYTHONDONTWRITEBYTECODE=1`, lane untouched)

```
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.R13GateSandbox-clone
git -C … checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3        # exit 0; rev-parse → 54a29268…
python3 .ufo/waves/round-13/measure.py --selftest                     # exit 0; passed 13, failed 0
python3 .ufo/waves/round-13/measure.py --quality corpus/QUALITY.md    # exit 0; clean, measured 54a29268, matches True
printf '\n<!-- harmless uncommitted probe -->\n' >> corpus/QUALITY.md
python3 .ufo/waves/round-13/measure.py --quality corpus/QUALITY.md    # exit 4; worktree_not_at_measured_revision
python3 .ufo/waves/round-13/measure.py --quality corpus/QUALITY.md    # exit 4 again after clone reset (deterministic)
# divergent + content failure: exit-map literal 1→9 in Q16 cell     # exit 1
# prefix rewrite: first byte → 'Z'                                  # exit 1; prefix_violation
# duplicate KQ16 row appended                                       # exit 1
# KQ15 row rewritten                                                # exit 1; kq15_lines_preserved False
python3 .ufo/waves/round-13/measure.py --quality corpus/QUALITY.md --before-revision cff9e62   # exit 1; before_revision_not_pinned_start
cp .ufo/waves/round-17/frozen/round-13_measure.py .ufo/waves/round-13/measure_frozen.py
python3 .ufo/waves/round-13/measure_frozen.py --quality corpus/QUALITY.md   # exit 1; pre-fix false failure
python3 .ufo/waves/round-13/measure.py --manifest .ufo/waves/round-13/frozen/expected.json     # exit 0; frozen-pinned clean
python3 .ufo/waves/round-13/measure.py --quality /nonexistent/QUALITY.md    # exit 3
python3 .ufo/waves/round-13/measure.py --quality corpus                     # exit 3
git commit -am 'probe: committed divergence' && python3 .ufo/waves/round-13/measure.py --quality corpus/QUALITY.md   # exit 0; clean at f2d0c4d…
python3 .ufo/waves/round-17/frozen/round-13_measure.py --quality corpus/QUALITY.md   # exit 3; not a git repository
sha256sum .ufo/waves/round-17/frozen/round-13_measure.py; git show cff9e62:.ufo/waves/round-13/measure.py | sha256sum  # both 2399d64d…, 39463 B
```

Lane read-only checks: `git rev-parse HEAD` → `54a29268…`; `git symbolic-ref -q HEAD` → exit 1 (detached); `git rev-parse refs/heads/master` → `54a29268…`; sha256 of lane `measure.py`/`QUALITY.md` equal their HEAD blobs; `git status --porcelain` in the lane showed only untracked `.ufo/waves/round-17/falsify/` (not mine).

# Limitations

- All execution happened in the `/tmp` clone, per the lane contract; I did not run the gate in the lane directory, so the lane's own live invocation is unexercised (clone bytes verified identical to lane worktree and HEAD for both files).
- I ran no `jj` command anywhere (prohibited for this seat); the jj timing model cited is from the in-repo audit's measured findings, not re-measured here [INFERENCE where extended beyond those lines].
- Tests are one-shot states, not fuzz; selftest's live sandbox covers before/after/divergent-failure, so an unrelated third-commit divergence is structurally the same `final == head_quality` comparison.
- Scratch (`/tmp/KamaR17.R13GateSandbox-clone` and `/tmp/KamaR17.R13GateSandbox-*.json/.bak/.md`) removed before finishing.

# Installs

None. No pacman/uv/npx/binary installs; pacman pause untouched. No ports bound or contacted; no llama-server or fake started.
