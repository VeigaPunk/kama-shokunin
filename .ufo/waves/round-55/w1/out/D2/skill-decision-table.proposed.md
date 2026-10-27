# Proposed SKILL.md addition (append at end of file, after line 1600)

Insertion point: `SKILL.md:1600` (end of the round-54 instrument registry). Appended,
never inserted — KQ7/KQ14 (no existing line moves). Owner: kama.

```markdown
## Round-55 decision table — counter-hardening legs (owner: kama)

Grounded in `corpus/knowledge/counter-hardening-legs.md` (S506, S507, S508 rejected,
S500-S502, S509, S510, S511), the round-53 seat reports under
`.ufo/waves/round-53/w1/out/` and the round-55 battery under
`.ufo/waves/round-55/c1/battery/`. Scope: a counter whose claim is about the code a
replay's server executes, or about the cited paths of the lane's self-assessment. It
does not restate KQ94/KQ95's predicates; it says what must be true of a *leg* before
the leg may carry a claim.

| Symptom | First check | Verdict | Action |
|---|---|---|---|
| A root-owned host library appears in the server's mappings that the honest build did not have (14 where 13 was honest), or a library constructor has run | The counter's `envnames` leg (environment **names**) and `hostlibs` leg (frozen basename set) | Code identity unearned: a root-owned mapping is not evidence of benign provenance | Require `LD_PRELOAD`/`DYLD_INSERT_LIBRARIES` to fail the leg and every host basename to be in the frozen set. Never treat `uid 0` as trust (K1Cheat). |
| An executable mapping has no pathname (`rwxp … 00:00 0`) or is an executable memfd that is not the sealed image | The `anon` leg's classification of each maps row | Code from nowhere: the predicate's "executable file mappings" quantifier would have skipped it | Fail the leg. A JIT exception needs an explicit, declared address range (K1Cheat). |
| The counter verifies its archive by path after hashing it, and its scratch sits beside the replay's `TMPDIR` | Whether members are compared against bytes read once (`Archive` at `tools/round54-replay-code-audit.py:448-453`) | The reference is writable by the code under audit; the leg can pass on attacker bytes (Sen1Mem F1) | Read once, hash those bytes, parse those bytes; a path re-open voids the leg. |
| The verdict changes when the measured file is rewritten while the server is held, or after the counter's read | `twopass` (two byte-identical passes) and `rehash` (post-exit re-stat/re-hash), and the declared interval in the recipe | Otherwise the verdict is one point sample, and a flip-and-restore is invisible (J7Late) | Add both legs or state the interval as a limit; a pre-flip receipt digest is not evidence of later state. |
| A fixture's commits land in a repository it was not pointed at (commit count moves), or a hook marker appears outside scratch | Whether every git call runs with `clean_env()` (`tools/round54-cited-path-check.py:198`) and an `--absolute-git-dir` guard | Inherited `GIT_DIR` beats `-C`; `GIT_CONFIG_COUNT` reaches `core.hooksPath` (Sen4Fixture; S510/S511) | Strip every `GIT_*` at both entry points; never run a frozen counter under untrusted git environment. |
| A token cited at base is gone at tip and the counter still prints `dropped=0` | Which surfaces the drop leg reads (`SURFACES`, `:159`; loop `:645-656`) vs where the token was hidden | Hiding passes wherever the leg does not look; a fence, quotes and a `./x/` prefix are the same edit to the parser (J12Hide) | Guard drops on every self-assessment surface; exempt only rowed `fixed`/`externalized`/`superseded`. |
| An `upstream` row passes at a tag, a branch, a fork or a mistyped prefix sha, or serves bytes other than the surface's pin | The URL's ref form and `sha256(body)` against the surface-stated digest (`:421-423`, `UPSTREAM_COMMIT`) | Reachability is not pinned identity; 200 says a file exists, not which (J11BadFixed) | Require a full 40-hex commit, the frozen owner/repo, and digest equality; tag/branch = bad row. |
| A `fixed`/`superseded` replacement resolves, but is an unrelated file or sits on another line | Whether the replacement extends the original stem to its ellipsis and is cited at the base line; whether `superseded`'s original was *live* at base | The row launders a citation instead of correcting it (J11BadFixed F2, M15) | Require stem extension and same-line citation; `superseded` requires a resolving base citation and a resolving replacement. |
| The base/do-nothing control prints `met=True` at the base tip | Whether the base horizon contains the change the claim credits (`BASE`, `tools/round54-cited-path-check.py:156`) | The claim is vacuous: with a same-tip base the counter compares the tree with itself (round-55 pre-freeze check, `dropped=1` only after reverting BASE) | Re-freeze BASE to a tip before the credited change; the base control must print `met=False` before data. |
| A leg has no mutant receipt, or its "mutant" prints `met=True` at the hardened counter | The battery's own classification: a `kill` must exit 1 with its named leg in the `detail:` lines; a void vector is labelled `vector` | A leg no control exercises is vacuous, and a passing mutant is not a kill (round-55 `m-ldaudit-foreign`) | Exclude the vector from the kill rule and name it; a kill rule is stated over the driver's classification, never over an unclassified receipt list. |
```

Note for integration: the round-55 preregistration's C1 target lists
`m-ldaudit-writable` and `m-ldaudit-foreign` among mutants expected to print
`met=False`, while the committed battery receipts print `met=True` and the driver
(`run-battery.py:57-67`) marks them `kind="vector"`. The row above is written to the
driver's classification; the preregistration's own wording is a finding for the outside
closure, not something this table can repair.
