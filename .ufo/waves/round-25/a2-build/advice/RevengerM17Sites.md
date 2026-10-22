Verdict: same element, yes for M17 (its lookup() literal is the round-23 refusal; only the variable name changed) and yes for M33 (the bare_objects() refusal is the same refusal at its second call site). Named narrowing: since round 24 (commit 92063cf) no caller in the audit can fire the lookup() refusal, so the registered M17 survives the grid and the round-23 kill now rests on M33.

# 1. Pins and what I read

- Lane tip 1fc41e346853afd98cbd7010af5db4e54dc877f7 (committer 2026-10-22 06:28:54 -0300).
- e0f0434 e0f04346fea0690228f3d3be539559316da4f703 (2026-10-21 12:30:28 -0300) added the refusal and the M17 entry.
- Round 23 auditor e876b953e9da28d2dffd29c923052bc626148c27 (2026-10-21 13:56:35 -0300).
- Round 24: ed1cc3a342bd801fe2d0f54f7ba2eb4ca42d5f05 (2026-10-21 15:44:52 -0300) and 92063cfc60e217fa7e2098c568578119b16a1b95 (2026-10-21 21:50:33 -0300).
- Auditor blob ids (`git rev-parse <rev>:tools/report-landing-audit.py`): e876b95 cf706c52233139920da60f8b55d06f031286c4f9; ed1cc3a 91518a9d661c1f97670fc588e724ce5f97c972ac; 92063cf, efe58e9 and tip all c05c1775989f75f98390dbe33d801199b98eb3af. `git diff 92063cf 1fc41e3 -- tools/report-landing-audit.py` printed nothing, so the auditor did not change after 92063cf.
- Registry blob ids (`tests/report-audit/isolation-mutants.py`): e876b95 bf4eb3b9c60f754c9b83742ef8a08a9da73390df; ed1cc3a 39df197ec9e3b1df88c95ddb8e3f7456372a06e1; 92063cf and efe58e9 a16e7e993b98298d426c34cee639eafe870d69ff; tip a49871e5911dc460d4207fd82a39f727d70b87c4.
- `git hash-object` (no -w) on the lane working copy, exit 0, gave the same two tip blob ids, so the working copy matches the tip for both files.
- Every file I compared was read from git objects with `git show <full rev>:<path>`, not from the working copy.

# 2. Round 23: one call site

- e876b95 tools/report-landing-audit.py:170-172, inside `def lookup(repos, tokens, peel="")` (def at line 139):
  - 170: `if not peel and not parts[0].startswith(token):`
  - 171: `# git resolved a same-named ref before the object prefix`
  - 172: `raise EvalError(f"{repo}: citation {token} names a ref")`
- `git blame -L 166,173 -s -n e876b95 -- tools/report-landing-audit.py` (exit 0, `blame-r23-172.txt`) gives e0f0434 for lines 170-172. e876b95 did not touch them.
- `git log -S "names a ref"` (exit 0, `pickaxe-names-a-ref.txt`) lists two commits, newest first: 92063cf (the second call site) and e0f0434 (the earliest). So the refusal did not exist before round 23.
- e876b95 tests/report-audit/isolation-mutants.py:52-53: `("M17-ref-shadow", 'raise EvalError(f"{repo}: citation {token} names a ref")', 'pass')`. Blame (`blame-mutants-M17-r23.txt`) gives e0f0434.
- Round-23 peel path: e876b95 lines 148-149 `if peel: bare = lookup(repos, tokens)`. The recursive call runs the line-172 check, so peel calls (lines 336-337 and 404) also reach it.
- Round-23 registry on the round-23 auditor: `python3 check_m17_sites.py` (exit 0), `check_m17_sites.out` line 2: `registered=31 stale=0`. Anchor count at line 172: `check_m17_sites.out` line 30 (`count=1 lines=[172]`).
- Round-23 kill: in my clone at e876b95, `python3 tests/report-audit/isolation-mutants.py --only M17-ref-shadow --json` gave exit 0. Pristine passed. M17 killed (grid exit 1), failed row F13-ref-named-abbreviation (`r23-M17-run.json`).

# 3. Round 24 and the repair: how the site moved

| Commit (committer time) | Effect on the refusal | Effect on M17 |
|---|---|---|
| e0f0434 (2026-10-21 12:30:28 -0300) | Creates the lookup() refusal, round-23 lines 170-172 | Registers M17 with the `{repo}` text |
| e876b95 (2026-10-21 13:56:35 -0300) | No change to those lines | No change |
| ed1cc3a (2026-10-21 15:44:52 -0300) | Message becomes `{store.path}` (blame: line 235 at ed1cc3a). Peel path becomes `bare = lookup(stores, tokens) if peel else None` (line 204), still a recursive call into the lookup() refusal | M17 text becomes `{store.path}`; anchor count 1 (line 235) |
| 92063cf (2026-10-21 21:50:33 -0300) | Adds `def bare_objects` (line 190) with the same refusal (lines 212-214, blame 92063cf). Peel path now calls `here = bare_objects(store, tokens) if peel else None` (line 246, blame 92063cf). lookup() refusal stays at line 277 | Registry not updated. Anchor now matches twice (lines 214 and 277), so M17 is stale |
| 1fc41e3 (2026-10-22 06:28:54 -0300) | Auditor unchanged (same blob). Only tests/report-audit/isolation-mutants.py changed (`show-stat-tip.txt`: 30 insertions, 3 deletions) | M17 anchor becomes the three-line guarded block (line 275, count 1). M33 added for the bare_objects() site (line 212, count 1) |

Other details I confirmed:
- `git blame` of tip lines 275-277 gives e0f0434 for the guard and comment and ed1cc3a for the raise line (`blame-tip-277.txt`).
- Blame of ed1cc3a lines 233-235 gives the same split (`blame-ed-235.txt`).
- The 92063cf change to the registry is only a new empty-selection check in `main()`. No MUTANTS literal changed at 92063cf (`diff-mut-ed-92063cf.txt`, one hunk, in `main`).

# 4. Same element? Site by site

## 4.1 lookup() site: round 23 against tip

- e876b95:170-172 against 1fc41e3:275-277: the only changed line is the raise, `{repo}` against `{store.path}`. The guard and the comment are identical, and both sit in `def lookup`. Verdict: YES, the same element.
- ed1cc3a:233-235 is identical to 1fc41e3:275-277 (difflib, no differences), so the text change happened at ed1cc3a and nothing after it touched the block.

## 4.2 bare_objects() site: the second site

- 1fc41e3:212-214 against 1fc41e3:275-277: the only difference is the guard, `if not parts[0].startswith(token):` against `if not peel and not parts[0].startswith(token):`.
- `bare_objects(store, tokens)` (line 190) takes bare names only, so the dropped `not peel` is always true. Same predicate, same message, same git call (`cat-file --batch-check` on bare names: lines 194-195). Verdict: YES, M33 weakens the same refusal at the second site.
- The two sites never both run for one call. The bare check runs only when peel is set (line 246), and the lookup() check runs only when peel is empty (guard at line 275).

# 5. The literals cannot match each other's site

- M17 literal (tip registry lines 81-87): count 1, at line 275. Count 0 at line 212 (`check_m17_sites.out` lines 41-46).
- M33 literal (tip registry lines 117-123): count 1, at line 212. Count 0 at line 275 (`check_m17_sites.out` lines 47-52).
- The first line is what tells them apart (`if not peel and` against `if not parts[0]`).
- Registered counting command on the exported tip blobs (`check_m17_sites.out` line 26): `registered=28 stale=0`.
- The pre-repair M17 literal (efe58e9 registry lines 68-69, text `{store.path}` with no guard) matched twice at tip (lines 214 and 277), which is why the old count was stale.

# 6. Named narrowing

## N1. The lookup() refusal lost every production trigger at 92063cf

- Round 23 and ed1cc3a: a peel call ran the bare recursion (line 149 at round 23, line 204 at ed1cc3a), so the lookup() refusal ran for every abbreviated citation. That is the path the grid's F13 row used to kill M17.
- From 92063cf: a peel call runs bare_objects() (1fc41e3:246). The lookup() refusal runs only for non-peel calls.
- The only non-peel production call is 1fc41e3:538, `full = lookup(stores, full_tokens)`. Its tokens come from `FULL` (line 90, exactly 40 lowercase hex) through `classify_full_hashes` (lines 463-481).
- Git's own source says a 40-hex name is the object it spells. Pinned source `git v2.56.0 object-name.c` lines 688-700: the full-length hex branch returns the parsed id at line 700. The ref lookup at line 692 only issues a warning. So for those tokens `not parts[0].startswith(token)` is false and the refusal cannot fire.
- The only other non-peel call that can carry an abbreviation is the self-test at 1170. Its `short` is a four-character prefix shared by two blobs (lines 1162-1167), so `lookup` answers `ambiguous` and never reaches the predicate. Lines 1173-1174 use full-length ids.
- The self-test creates no refs with hex names. A grep for update-ref, tag and refs/ finds only tag `v-hole` at line 1423.
- Result [INFERENCE from the caller list and the git source; the grid run in section 7 agrees]: no caller in the audit can make the lookup() refusal fire.
- git probe, `python3 probe_git_shadow.py` (exit 0, `probe_git_shadow.out`), on git 2.56.0: a tag named `deadbee1` pointing at commit C makes both `deadbee1` and `deadbee1^{commit}` print C's id, so the predicate fires. A tag named with C's full hex pointing at D makes the full hex print C, so the predicate does not fire.

## N2. The registered mutant run confirms the survivor

- Tip clone (checked out at 1fc41e3): `TMPDIR=<scratch> python3 tests/report-audit/isolation-mutants.py --only M17-ref-shadow --only M33-ref-shadow-bare-objects --json`, exit 0, wall time 99.3 s, `tip-M17-M33-run.json`.
  - Pristine: passed.
  - M17-ref-shadow: grid exit 0, no failed rows. Survived. The run's own `surviving` list is `["M17-ref-shadow"]`.
  - M33-ref-shadow-bare-objects: grid exit 1, failed row F13-ref-named-abbreviation. Killed.
- F13 is the grid row at tip `repo-state-grid.py:661`, with expected text `names a ref` at line 702 and fixture `f_ref_abbrev` at lines 374-381. It publishes a report whose Landed-changes section (lines 99-101) lists `deadbee1`, which the audit checks on the peel path (`cited = set(ABBREV.findall(section))`, line 549; lookup at lines 550-551).
- Causal check, `python3 causal_ed1cc3a_tip_m17.py` (exit 0, run in clone-r23 checked out at ed1cc3a): the tip M17 anchor and replacement, applied to the ed1cc3a auditor where the anchor matches once (line 233), give grid exit 1 with failed row F13. Killed (`ed1cc3a-tipM17-causal.json`). So the survival comes from the round-24 routing change, not from the guarded anchor.
- Round-24 registry at ed1cc3a, `--only M17-ref-shadow --json`, exit 0: pristine passed, M17 killed by F13 (`ed1cc3a-M17-run.json`).
- Round-23 registry at e876b95, same command, exit 0: M17 killed by F13 (`r23-M17-run.json`).

## N3. Registry-level rules

- No id is retired or reused. M33 is new. The denominator at the tip is 28 (`registered=28 stale=0`).
- Both call sites are registered, so no call site is silently dropped.
- M17 is registered and matches once, but on the current callers its refusal can never fire, so the full registry run will list `M17-ref-shadow` among the survivors. The claim's own rule says a survivor is reported, not hidden. I did not run the full registry (out of my scope).
- Identity answer: M17 keeps the round-23 element. The narrowing is in what kills it, not in which statement it removes.

# 7. Side observations (outside M17 and M33, not assessed)

- M11's pre-repair literal (efe58e9 registry lines 56-57) matched once at e876b95 (line 430) and at ed1cc3a (line 608), and matched zero times at 92063cf. The repaired M11 matches once (tip line 682). I did not assess M11's element.
- The id M08 never appears in the registry file's history (`git log -S M08` exit 0 with no output; count of `M08` in e876b95, ed1cc3a, 92063cf and 1fc41e3 is 0). It is a gap in numbering, not a removed id. Recorded for completeness.
- `git log -L` on bare_objects also lists commits before 92063cf (`log-L-bare_objects-tip.txt`). The pickaxe result (`pickaxe-bare-objects.txt`) and blame (`blame-tip-214.txt`) show the function and its refusal arrived in 92063cf. I relied on pickaxe and blame. The `log-L` run for bare-objects with a hyphen, `log-L-bare-objects-tip.txt`, is an earlier attempt that failed on regex escaping (exit 128) and is not used.
- The M17 and M33 anchors are three lines and include the comment line. An edit to that comment would make the anchor stale (count 0) rather than weaken the refusal. This is a fragility, not a current defect [INFERENCE].

# 8. Confidence and what I did not run

- High: identity of the lookup() statement across e0f0434, e876b95, ed1cc3a and 1fc41e3 (blob-level difflib, blame, pickaxe).
- High: the registry counts and the grid exit codes listed in section 7.
- Medium-high: the git 40-hex rule. It comes from the v2.56.0 source and the probe on git 2.56.0 (the host version).
- Not run: the full registry, the audit's own `--selftest`, and any grid row other than the ones named above. The claim that the self-test cannot reach the predicate rests on reading lines 1162-1174.
- No llama-server child was started. No subagent was dispatched.

# 9. Sources

- https://raw.githubusercontent.com/git/git/v2.56.0/object-name.c, accessed 2026-10-22 with curl (exit 0). Local copy: `/fast/scratch/hyaku/kama-r25a2/RevengerM17Sites/src/git-v2.56.0-object-name.c`, 1901 lines, sha256 6dc003f31ebf2b5982196a01daf265ab12bab02d1585c54324451f550f3f5625.
- Located quotes:
  - line 672: "Git normally never creates a ref that ends with 40 hex characters" (12 words).
  - line 688: `if (len == r->hash_algo->hexsz && !get_oid_hex(str, oid)) {`
  - line 700: `return 0;`
  - line 747: `refs_found = repo_dwim_ref(r, str, len, oid, &real_ref, !fatal);`
  - lines 1131 and 1140: `ret = get_oid_basic(r, name, len, oid, lookup_flags);` then `return get_short_oid(r, name, len, oid, lookup_flags);`

# 10. Tools

- No tool was installed or upgraded by this seat. I used the host's git 2.56.0 (`git --version`, exit 0) and curl.

# 11. Files written

- Advice report: `.ufo/waves/round-25/a2-build/advice/RevengerM17Sites.md` (this file).
- Under `.ufo/waves/round-25/a2-build/out/RevengerM17Sites/`:
  - Scripts: `check_m17_sites.py`, `probe_git_shadow.py`, `causal_ed1cc3a_tip_m17.py`.
  - Script outputs: `check_m17_sites.out` and `.err`, `probe_git_shadow.out` and `.err`.
  - Mutant run records: `tip-M17-M33-run.json` and `.err`, `r23-M17-run.json` and `.err`, `ed1cc3a-M17-run.json` and `.err`, `ed1cc3a-tipM17-causal.json`.
  - Blob ids: `blob-r23.txt`, `blob-ed1cc3a.txt`, `blob-92063cf.txt`, `blob-efe58e9.txt`, `blob-tip.txt`, `blobm-r23.txt`, `blobm-ed1cc3a.txt`, `blobm-92063cf.txt`, `blobm-efe58e9.txt`, `blobm-tip.txt`.
  - History queries: `pickaxe-names-a-ref.txt`, `grep-names-a-ref.txt`, `pickaxe-bare-objects.txt`, `pickaxe-def-lookup.txt`, `pickaxe-peel-guard.txt`, `pickaxe-mutants-history.txt`, `log-audit-history.txt`, `log-L-lookup-tip.txt`, `log-L-bare_objects-tip.txt`, `log-L-bare-objects-tip.txt` (failed attempt, exit 128).
  - Blame: `blame-r23-172.txt`, `blame-ed-235.txt`, `blame-tip-277.txt`, `blame-tip-214.txt`, `blame-mutants-M17-r23.txt`, `blame-mutants-M17-ed1cc3a.txt`, `blame-mutants-M17-92063cf.txt`, `blame-mutants-M17-tip.txt`.
  - Diffs and commit stats: `diff-r23-ed.txt`, `diff-ed-92063cf.txt`, `diff-92063cf-tip.txt`, `diff-92063cf-tip-audit-full.txt`, `diff-r23-ed-audit-full.txt`, `diff-ed-92063cf-audit-full.txt`, `diff-mut-efe-tip.txt`, `diff-mut-ed-92063cf.txt`, `diff-mut-r23-ed.txt`, `show-stat-tip.txt`, `show-stat-92063cf.txt`, `show-stat-ed1cc3a.txt`, `show-stat-r23.txt`.
- Scratch, outside the lane, under `/fast/scratch/hyaku/kama-r25a2/RevengerM17Sites/`: exported blobs (`r23-audit.py`, `ed1cc3a-audit.py`, `92063cf-audit.py`, `efe58e9-audit.py`, `tip-audit.py`, `*-mutants.py`, `tip-grid.py`, `r23-grid.py`), the git source copy under `src/`, the probe repo `gittest/`, two clones (`clone/` at 1fc41e3, `clone-r23/` last checked out at ed1cc3a), and the grid temporary directories `tmp/` and `tmp2/`.
- Lane writes: none. Every lane command was read-only (log, show, blame, diff, rev-parse, hash-object without -w, and clone as a read). The two clones and the probe repo are in scratch.
