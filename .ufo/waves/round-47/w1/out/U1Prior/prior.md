# U1Prior - prior art for C1 (append-only audit v2), round 47

Verdict: **No surveyed project defines a "restored line". The prior art is (a) per-edge enforcement, (b) a file-level or line-count tripwire, or (c) structural avoidance. v2's multiset-over-window `held(x)` has no precedent, and its closest git primitives (`-S`, `--color-moved=plain`) share its blind spot: they cannot tell a move from a restoration.** Two techniques close real, measured blind spots in v2. A strict byte-prefix check finds 56 mid-file insertions that no deleted-line audit sees. Per-edge/ancestry enforcement is the only technique that catches a history rewrite. Neither changes the C1 result (7->7, met=True at 3a09a1d): the counter scores numstat equality, the fixture and the contract, not these properties.

Sources are fetched 2026-10-26 from the raw upstream files (git/git master `Documentation/`) and the pages named. Quotes are verbatim and <=25 words. Line numbers are in the raw `.adoc`/`.md` file.

## 1. Primary sources

**S1. Git: what a "deleted line" is, and what git itself uses it for.**
- `git diff --numstat` https://git-scm.com/docs/git-diff (git/git `Documentation/diff-options.adoc:231-235`): "shows number of added and deleted lines in decimal notation and pathname without abbreviation, to make it more machine friendly". Also: "For binary files, outputs two `-` instead of saying `0 0`." v2's contract (|D| == numstat deletions; binary skipped) is exactly this definition.
- `--diff-filter` (`diff-options.adoc:632-636`): "Select only files that are Added (`A`), Copied (`C`), Deleted (`D`), Modified (`M`), Renamed (`R`)..." It selects whole-file status, not lines, so it cannot express "no line deleted". A `git log --diff-filter=D` check catches only whole-file deletion. v2 handles that case as an event (the V1Tool `fx_delrecreate` run).
- The pickaxe is the one git primitive built on occurrence counts, the same shape as v2's multiset. https://git-scm.com/docs/gitdiffcore (`gitdiffcore.adoc:251-253`): "`-S<block-of-text>` detects filepairs whose preimage and postimage have different number of occurrences of the specified block of text." Then: "By definition, it will not detect in-file moves."
- Moved-line detection is the nearest git has to "restored". `--color-moved=plain` (`diff-options.adoc:376-381`): "Any line that is added in one location and was removed in another location". Its own docs warn: "it is not very useful in a review to determine if a block of code was moved without permutation".

**S2. Changelog guards in the wild check file status, not deleted lines.** dangoslen/changelog-enforcer, README `changeLogPath` https://github.com/dangoslen/changelog-enforcer: "The file being checked for updates must be either an add (`A`) or modified (`M`) status to `git` to qualify as updated." Its purpose is that every PR touches the changelog. Rewriting or deleting old entries satisfies it (`M`). It is a presence check, the opposite polarity of an append-only audit. The other mainstream approach avoids the problem by structure. towncrier README https://github.com/twisted/towncrier: "Rather than reading the Git history, or having one single file which developers all write to and produce merge conflicts". Entries become one file each, so "append-only" reduces to "fragment files are not deleted or edited". Git's `merge=union` driver (https://git-scm.com/docs/gitattributes, `gitattributes.adoc:1127-1129`) serves the same file-per-writer wish at merge time: "take lines from both versions, instead of leaving conflict markers". It does not guard deletion.

**S3. Enforcement rather than audit: refuse the push, or make the medium append-only.**
- Git hooks https://git-scm.com/docs/githooks (`githooks.adoc:323-326`): the `update` hook "can be used to prevent 'forced' update on certain refs", to "enforce a "fast-forward only" policy". Server side, `receive.denyNonFastForwards` (`config/receive.adoc:105-108`): "deny a ref update which is not a fast-forward". GitHub's branch protection https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches (source `about-protected-branches.md:35`): "each branch protection rule disables force pushes to the matching branches and prevents the matching branches from being deleted". I found no GitHub-published "protect"/append-only-file action (my search only surfaced generated snippets, which I did not use). The shipped primitive is history immutability, not content immutability.
- OS level, chattr(1) https://man7.org/linux/man-pages/man1/chattr.1.html: "A file with the 'a' attribute set can only be opened in append mode for writing."
- Cryptographic level, RFC 6962 §2.1.2 https://www.rfc-editor.org/rfc/rfc6962.txt: "Merkle consistency proofs prove the append-only property of the tree." Auditors keep the previous signed head and ask for a proof that the new head extends it.

## 2. How the sources define "restored", and v2's difference

| Technique | Notion of what changed | "Restored"? |
|---|---|---|
| numstat / diff-filter guards | per-edge line counts, or file status | none; any deletion is a violation |
| pre-receive/update, chattr, RFC 6962 | per-edge or cryptographic prefix | none; a restoration later does not excuse an earlier deletion |
| `git log -S` | occurrence count changed between two blobs | not defined; "will not detect in-file moves" |
| `--color-moved` | line added somewhere and removed somewhere in one diff | a move, not a restoration; zebra/blocks add permutation or adjacency conditions |
| **v2** | multiset `held(x)` of deleted lines present again, maximised over the event's window | **yes, content-level and cross-commit, with no precedent** |

What v2 does differently, and where it is weaker:
1. **Audit after the fact, not enforcement.** Every source above rejects the edge or reports presence. v2 reports and then credits restoration. That credit is the lane's own design (the round-46 D2 repair), and nothing I found competes with it. It also makes `restored_max` forgiving: V1Tool's `fx_delrecreate` keeps `restored_max=40` after a later trim.
2. **Count basis.** v2's deleted count is byte-exact numstat and checked against numstat, as in S1, and fixes the `--`-prefix drop. Git itself is not byte-pure here. At 5 of the 91 threshold-1 events (LOG.md 83bee7fa, 33b167ec, 84a81304; SCORECARD.md 84a81304; corpus/README.md 1e41928a) the new blob is a strict byte-extension of the old one, yet numstat and v2 report `deleted=1`. The cause is a missing newline at EOF on the old blob (`old_ends_nl=False`). v2 grades them `restored`, correctly, but they sit in the event list. An audit built on `startswith` would not list them.
3. **Multiset equals `-S` semantics, so it inherits "no in-file moves".** `held(x)` has no order. See finding F1.

## 3. Measured on the lane (3a09a1d, 303 commits, 85 files, first-parent edges)

Script `prefix_scan.py`, output `prefix_scan.out`. For each (parent, commit, file), a strict byte-prefix test (`new.startswith(old)`) was set against `git diff --numstat`:

| class | edges |
|---|---|
| pure append (old is a byte prefix of new) | 267 |
| numstat deleted >= 20 (v2's 5 events) | 5 |
| numstat deleted 1-19 (not prefix) | 81 |
| **numstat deleted = 0 but not a prefix (insertion at top or middle)** | **56** |

(81 + 5 + 5 EOF-newline cases = the 91 events at `--threshold 1`; L1Lowthr counted 86 sub-20 events. The 5 EOF cases are in its 86 but byte-prefix in mine.) The 56 mid-file insertions break down as follows (`mid_breakdown.py`, `mid_breakdown.out`): SOURCES.md 32, SCORECARD.md 8, corpus/lessons 10, LOG.md 3, README.md 2, QUALITY.md 1. 52 are mid-file and 4 are at the top. v2 and every deleted-line audit are blind to them by construction, yet the lane declares append-only with "appended so no existing line moves" (corpus/QUALITY.md:24, and corpus/README.md:86 "Appended rather than inserted, so no existing line moves"). An insertion moves every later line. Some are legitimate: SOURCES.md is `A-row`, and the SCORECARD head is declared re-derived (SCORECARD.md:6). The class still lacks any instrument.

## 4. Findings relative to the round's critics

**F1 (new, not reported by a critic): v2 grades a pure reorder as `restored`.** Fixture `fixture_move.sh` (output `fixture_move.out`): 40-line LOG.md, last 25 lines moved to the top, one commit. numstat `15 15 LOG.md`; byte-prefix False; v2 at `--threshold 10`: `event ... LOG.md deleted=15 restored_max=15 status=restored restored_best=<same commit> restored_by=<same commit>`. A move is indistinguishable from a restoration, and an in-commit move is credited with `restored_by == event commit`. On the lane, `dd9f5dc6 SCORECARD.md` (restored_best = its own commit, 24 of 31) is the same shape, which K1Design/K1Regions explain as a head re-anchor, an in-place rewrite. S1's `-S` carries the same limit ("will not detect in-file moves"), so v2 is no worse than git here, and it is worse than a prefix check. A reorder is an edit to filed history. Confidence: high (reproduced; fixture one commit, output archived). Whether the lane intends moves to count as restoration is undeclared, so I rate this a definitional gap, not a defect.

**F2 (blind spot v2 cannot see, measured): 56 zero-deletion non-append edits in the contracted files.** Technique: strict byte-prefix per edge, as in the pre-receive pattern, or equivalently `new == old + suffix`. It needs no line model, so it avoids the `---` bug class (D1) and the 5 EOF-newline artefacts. It would flag all 142 non-append edges (56 + 81 + 5), out of 409 changed file-edges, where v2 reports 5 at threshold 20. Cost: it is strict, so it needs an allow-list for the declared in-place regions (SCORECARD head, SOURCES `status`/`recheck`/`used-by` cells, knowledge §Errata). That is the K1Design region gap, so the check needs the region scoping that K1Design recommended before it can be made a gate. Confidence: high for the counts, medium for the proposal's value.

**F3 (K1Design/K1Regions region gap): the prior art offers a structural fix, not a tool fix.** None of the surveyed guards scopes a region of a file (S2 is file-level). towncrier's answer is to move the mutable part out: here, the SCORECARD head that SCORECARD.md:6 says is re-derived, and the knowledge §Errata, would sit in separate non-contracted files, so the contract stays whole-file and no `partial` is "expected". This matches K1Regions' F2 (append superseded head rows under Historical head sections) in effect, at lower cost to `restored_max`. Confidence: medium (design inference; I did not build it).

**F4 (L1Lowthr, sub-20 deletions): the 20-line threshold has no counterpart in the sources.** Every surveyed mechanism is zero-tolerance per edge. v2 at `--threshold 1` is already zero-tolerance (91 events, `t1.json` reproduced: 5 + 86). The sources' answer to legitimate exceptions is an allow-list or a label (changelog-enforcer `skipLabels`), recorded per event, not a size cut. Confidence: high.

**F5 (history rewrite, no critic reported it): v2 audits the rev-list of `--to` only.** If history is replaced, the rewritten history shows no events. The sources S3 handle this by ancestry: refuse non-fast-forward (githooks `update`, `receive.denyNonFastForwards`) or prove consistency with the previous head (RFC 6962 §2.1.2). The cheap analogue for v2 is a recorded audit tip plus `git merge-base --is-ancestor <previous-audited-tip> <to>`, exit 2 or 1 when it fails. It would also address the round-46 D2 (tip moves) at its root. Confidence: medium; I did not test it, and the lane's jj/colocated flow may rewrite non-published commits on purpose.

## 5. Recommendations (proposed, not applied)

1. Keep v2's multiset window as the lane's own contribution. Document that it is move-blind (F1).
2. Add an optional per-edge `prefix` mode to the audit (or a sibling check) that reports `non-append` for zero-deletion edits (F2), once region scoping exists (F3).
3. Record the audited `--to` in receipts and verify ancestry against the previous receipt (F5).
4. Prefer separating re-derived regions into non-contracted files over carve-outs in a note column (F3).

No technique here would have changed the five events or the C1 outcome, so the 7->7 claim stands as the counter scores it (the counter's own concerns are K1Cheat's).

## 6. Tooling and hygiene

No tools installed; python3, git 2.56.0 and curl only. All work in scratch `/fast/scratch/hyaku/kama-r47/U1Prior` (a `git clone --shared` of the lane checked at 3a09a1d, plus a one-commit fixture whose toplevel I asserted); scratch removed before finishing. The lane, fleet repo and controls were not written.

Files in this directory: `prior.md`, `prefix_scan.py`/`.out`, `mid_breakdown.py`/`.out`, `fixture_move.sh`/`.out`.
