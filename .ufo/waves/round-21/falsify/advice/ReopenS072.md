VERDICT: partial - quote, location and committer-rewrite claim verify; URL unpinned (likely v0.46.0 now), so the anchor and the due on-release recheck are stale; author-time half unanchored.

# ReopenS072 — re-open of row S072 (jj metaedit committer rewrite)
Scope: row `corpus/SOURCES.md:84`; Gate row `corpus/lessons/round-21.md:48`; contract v1 (`CORPUS.md`, SOURCES section). Re-opened 2026-10-21. Lane not modified: clone at a6617149 in scratch; worktree and committed blobs compared with cmp (exit 0). Commands, exits and outputs: `out/ReopenS072/evidence.txt` (E1–E14).

## Quote (round-21.md:48)
- Verbatim: yes. Raw page line 10463 contains "the committer name, email, and timestamp are also updated for all rebased commits." (E2). Same text at v0.45.1 snapshot line 2071 and v0.46.0 snapshot line 2133 (E6).
- Location: `## jj metaedit` description ¶1 — yes (E1, E6).
- Length: 13 words, within 25.
- Nit: installed help wraps the sentence between "for all" and "rebased commits." (E8). Verbatim only after joining the wrap.
- Nit: access date stated once at Gate-section level, not per row (contract Rule 1 asks per row).

## Field verdicts (row S072)
| field | verdict | basis |
|---|---|---|
| id | agree | next after S071; no duplicate; NF=13 (E12) |
| source | agree | title and canonical URL match the page's canonical meta (E1) |
| kind | agree | official docs page |
| tier A | agree, with caveat | page says it is experimental, "does not match the `jj help` output exactly", and calls `jj help` "more authoritative" (E2); A rests on the same sentence in the 0.45.1 help and source |
| scope | agree, narrow | "matches installed jj 0.45.1 help" holds for metaedit ¶1 and the author/committer option texts I compared (wording identical, wraps only); the page as a whole is declared non-exact |
| anchor | disagree (partial) | heading, ¶1 and binary version/commit correct (E3, E6, E8); the URL carries no revision or date, so the only revision given is the binary's |
| teaches (a) committer re-stamped on rebase | agree | page ¶1; probe E10 |
| teaches (b) committer cutoff can move a commit across a boundary | [INFERENCE] | follows from (a) and lane tool l.25–26 (E14); not a page statement |
| teaches (c) author time does not move | agree on fact, unanchored | probe E10: author 2020-01-01 +00:00 unchanged across rebase. Page author text covers explicit flags only and never mentions rebase; the row cites none of it |
| status mined | agree | used-by cites it (E13); census mined=60 matches the Context's post-round count (rows 74) (E12) |
| opened 2026-10-21 | agree | equals re-open date |
| recheck on-release | disagree (due now) | v0.46.0 released 2026-10-07 (E5), 14 days before the row's opened date; row still pins 0.45.1 |
| used-by corpus/lessons/round-21.md | agree | file exists; only corpus file citing S072 (E13) |

## Version drift
- Pin holds: binary `jj 0.45.1-7c41cdeb…` (E8) and tag v0.45.1 → 7c41cdeb… (E3).
- Newest release is v0.46.0 (Latest badge, E5). The sentence persists in its docs (line 2133) and source (lines 36–37) (E6), so the claim is not refuted; the pin is one release behind.
- [INFERENCE] `latest` now serves v0.46.0 docs: it lists `jj file edit`, `jj file delete`, `jj workspace remove` (E9), which 0.45.1 help lacks (E8) and the v0.46.0 notes add (E5); its ¶1 sits at the same grep line (2194) as v0.46.0's versioned page (E7).

## Proposed actions (L1 decides; nothing applied)
1. Leave S072's anchor and teaches alone (append-only, Rule 2). Either log this re-open in the round-21 Gate, or add a row whose teaches opens `supersedes S072 —` and pins `cli/tests/cli-reference@.md.snap` @ v0.45.1 (7c41cdeb…) line 2071 and/or `https://docs.jj-vcs.dev/v0.46.0/cli-reference/` (¶1 at line 2194 in grep rendering). Carry the tier caveat.
2. Cite the author-time half to a lane-owned file, e.g. `.ufo/waves/round-21/falsify/out/ReopenS072/probe.sh` plus `probe.log` (E10), or to the page's `--update-author-timestamp` paragraph.
3. `recheck` may change in place (Rule 2), logged old→new in the round lesson: `on-release` is already satisfied by v0.46.0.
4. Scout advice (`build/advice/SrcJjRebaseTimestamps.md` l.8) gives ¶1 as "line 2200"; I get 2194 (grep rendering) and 2071 in the 0.45.1 snapshot. No row cites a line; nit only.

## Not executed / [INFERENCE]
- `latest` = v0.46.0 is inferred from E7 and E9; I did not read the docs build.
- Lane tool's rebase behaviour (l.25–26) is its docstring; I did not run `jj-lane.sh`.
- GitHub API `releases/latest` returned HTTP 403 (E5); used the releases redirect instead.
- Provenance of `~/.local/bin/jj` (sha256 cd5efc3e…) not established by me.

## Installs/updates
None. Used the existing `~/.local/bin/jj` 0.45.1. pacman not used.

## Hygiene
Lane untouched. No subagents, no servers, no model downloads. Raw page (407 KB) kept only in scratch and removed with it. Artifacts: `out/ReopenS072/{evidence.txt, probe.sh, probe.log, help-metaedit-0.45.1.txt, help-file-0.45.1.txt, help-workspace-0.45.1.txt}`.
