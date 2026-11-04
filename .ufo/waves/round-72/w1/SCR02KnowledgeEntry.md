# SCR02KnowledgeEntry — round-72 wave 1 report

Seat: knowledge entry + coverage-map row + one quality criterion (expansion axis). Leaf member: no
subagent dispatch, no lane commit, no gate run of my own.

## What I built

1. `corpus/knowledge/receipt-tip-binding.md` — new entry, 120 lines (limit 120). Provenance trio
   first (S175, S543, the frozen C2 contract and the lane instrument), then: the frozen predicate
   blockquote (byte-identical to `plans/round-72-claims.md` §C2, 7 lines), four conjuncts it
   establishes, four things it does not, the frozen kill-rule quote with the three classes,
   record-path vs instrument-input (5 vs 7, with the counting command), the commit order a clean
   binding requires, and five limits.
2. `corpus/README.md` — appended `## Coverage map — round 72 addition (2026-11-03)`: one row for
   the new entry and one for the round-71 `knowledge/pre-report-gate.md` omission (round-71
   spot-check §8 item 5). Earlier sections untouched.
3. `corpus/QUALITY.md` — appended `## Criterion added — round 72` with exactly one row, KQ119;
   KQ118's bytes untouched.
4. This report: `.ufo/waves/round-72/w1/SCR02KnowledgeEntry.md`.

## Commands run and observed output

| # | Command | Observed |
|---|---|---|
| 1 | `git log --oneline -4` | `a3cc39f0 round-72: amend C1 case-A anchor … and dispatch wave 1`; `090a0b25 round-72: freeze two claims …`; `d30a8696 round-71 verifier spot-check…`; `7fb6cb4e round-71: lesson final-receipts block…` |
| 2 | `git status --porcelain -uall` | round-72 dirty set: `M plans/round-72-claims.md`, `M tools/pre-report-gate.py`, `M corpus/SOURCES.md`, `M corpus/README.md`, `M corpus/QUALITY.md`; untracked `corpus/knowledge/receipt-tip-binding.md`, `corpus/lessons/round-72.md`, `tools/round72-*.py`, wave files |
| 3 | `git cat-file -e a3cc39f0:tools/round72-receipt-tip-binding.py` | `fatal: path 'tools/round72-receipt-tip-binding.py' does not exist in 'a3cc39f0'`, exit `128` |
| 4 | `sha256sum plans/round-72-claims.md` | `c656e66b2bc3b97164366babb125ffa1cc4ce7c409c8a2943235d92f1be889a1` (worktree, includes uncommitted amendment 2) |
| 5 | `git show a3cc39f0:plans/round-72-claims.md \| sha256sum` | `39f4ddbcd084c05213dd389decaa997e7128a7d1f8a7aebe325fe1dfdc6ad933` (matches `controls/freeze.txt`) |
| 6 | `sha256sum .ufo/waves/round-72/measured/before/receipt-tip-control-old.out` | `6a59487dfdc6bdfe13347d4cbe62198c3d2eee439b9e181d35432d23e87b719c` (matches `controls/freeze.txt`) |
| 7 | `cat .ufo/waves/round-72/measured/before/receipt-tip-control-old.out` | three `BINDING_FIXTURE <unbound\|shifted\|stale> shortcut=accepted cited=1 …` lines; `BINDING_CONTROL cited=3 accepted=3 rejected=0` |
| 8 | record/instrument count one-liner (`python3 -c` over `plans/round-72-claims.md` §C2, pasted in the entry) | `[5, 7]` |
| 9 | `grep -o '# tip=<40-hex>\|# rev=<40-hex>' plans/round-72-claims.md \| sort -u \| wc -l` | `2` |
| 10 | `grep -c 'git-check-ignore' corpus/SOURCES.md` (before S543 landed) | `0`, exit 1 |
| 11 | `grep -n '^| S543' corpus/SOURCES.md` (after SCR01 landed it) | row at `corpus/SOURCES.md:295`; cells: `docs`, `A`, `status mined`, `2026-11-03`, `on-release`, `used-by corpus/knowledge/receipt-tip-binding.md` |
| 12 | `ls corpus/knowledge/*.md \| wc -l`; map-row parse over `corpus/README.md` (before my append) | `42` files; `37` row lines naming `34` distinct entries; unmentioned `completion-request-plane.md`, `ollama-live-amendment-r61.md`, `pre-report-gate.md`, `process-bound-listener.md` |
| 13 | per-entry row check after my append | `pre-report-gate` row=1, `receipt-tip-binding` row=1; the three named gaps row=0 |
| 14 | `wc -l corpus/knowledge/receipt-tip-binding.md` | `120` |
| 15 | quote check (python): extract the `>` blockquotes from `plans/round-72-claims.md` §C2 and the entry | predicate blockquote identical `True` (7 lines); kill-rule quote exact substring `True` |
| 16 | `sha256sum tools/round72-receipt-tip-binding.py` | `789c05593d0af3eb114ee517496877ced5893bf4c6e575f7371fb7183f2fade4` (uncommitted worktree bytes) |
| 17 | read `tools/round72-receipt-tip-binding.py` head/`HEADER_RE`/`_evaluate`; `grep -n ARM_SPECS tools/pre-report-gate.py` | `PREDICATE` byte-equal to the plan; `HEADER_WINDOW = 5`; non-ancestor → `shifted` (`_evaluate` line 414); arm-6 spec passes no `--allow` |
| 18 | read `corpus/lessons/round-72.md` (SCR03 skeleton) | exists; `## Gate` quotes S175 live re-open (sha256 `46d106b7…`) and S543; no `## C2` heading |

No tool was installed or upgraded this seat; no network fetch was made by me (the S543 fetch and its
sha256 are SCR01's receipt, cited as such).

## Gates and checks

- Quote integrity: predicate blockquote byte-identical; kill-rule quote exact (commands 15).
- Length: entry 120 lines (limit 120).
- Every numeric claim in the entry carries a command: record/instrument `[5, 7]` (8), header forms
  `2` (9), line window and class facts cite the tool's own constants and sha256 (16/17).
- I did **not** run `tools/round72-receipt-tip-binding.py`, the corpus census, any lane gate, or any
  selftest; those belong to EX02/EX03/SCR01 and the L1. No green lane receipt is claimed here.

## Touched surfaces (only these)

- `corpus/knowledge/receipt-tip-binding.md` (new)
- `corpus/README.md` (appended section only)
- `corpus/QUALITY.md` (appended heading + KQ119 only)
- `.ufo/waves/round-72/w1/SCR02KnowledgeEntry.md` (this report)

Not touched: `plans/**`, `corpus/SOURCES.md`, `SKILL.md`, `SCORECARD.md`, `LOG.md`, `tools/**`,
`.ufo/state/`, `.ufo/watchdog.log`, the fleet repo, sibling lanes.

## Out of scope / deliberately not done

- No lane commit/push; the integrator commits (my entry is untracked at this tip).
- No fix of the three remaining map gaps (they need their own rows, not prose).
- No run of the binding counter against the in-progress round: it would grade a half-built tree and
  its exit would not be evidence for C2.
- No edit of the frozen claims after reading the amendments: disagreements below are reported, not
  patched.

## Findings for the canonical judge (verbatim conflicts, no freeze edit)

1. **`<rev>` placeholder reuse in the frozen predicate.** `--tip <rev>` names the tip, then "exists
   at `<rev>`" and "an ancestor of `<rev>`" use it for the tip, while "every commit in
   `<rev>..<tip>`" can only mean the receipt's header revision (otherwise the range is empty). The
   kill rule ("a revision whose delta touches `tools/`") fixes the intended reading. Recorded in
   the entry's §Limits; the freeze is unchanged.
2. **Class-mapping divergence between the executor brief and the freeze.** The EX02 seat brief
   (`.ufo/waves/round-72/w1-spec.json`) says a non-ancestor header → `stale`; the frozen kill rule
   says `shifted`; EX02 confirmed in IRC that the tool follows the freeze, and the tool's docstring
   footnote (lines 57-61) plus `_evaluate` (line 414) implement `shifted` with detail "not an
   ancestor of <tip>". The entry states `shifted`.
3. **Freeze amendment 2 is uncommitted at my read.** Worktree `plans/round-72-claims.md` sha256
   `c656e66b…` vs committed `a3cc39f0` `39f4ddbc…`; `controls/freeze.txt` still records
   `39f4ddbc…`. The amended text (empty population `cited=0` → exit 2) is what the entry cites, and
   its `verified-at` names both digests.
4. **C1 arm 6 and C2 impose one order, not two.** C2 refuses a delta commit touching an instrument
   input; C1's arm 6 grades whole-repository porcelain and the gate's arm-6 invocation passes no
   `--allow`, so it requires a clean worktree. Consequence (labelled `[INFERENCE]` in the entry):
   land every instrument input, take receipts naming that revision, then commit only record paths.
5. **The entry's tool-level statements are a read of uncommitted bytes.** The tool exists only in
   the worktree (sha256 `789c0559…`, absent at `a3cc39f0`); the entry claims no lane run of it.

## Artifact paths

- `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/receipt-tip-binding.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/README.md` (`## Coverage map — round 72 addition`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md` (KQ119)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-72/w1/SCR02KnowledgeEntry.md`
- read-only evidence: `plans/round-72-claims.md`, `.ufo/waves/round-72/controls/freeze.txt`,
  `.ufo/waves/round-72/measured/before/receipt-tip-control-old.out`,
  `corpus/lessons/round-72.md`, `corpus/SOURCES.md:295`, `tools/round72-receipt-tip-binding.py`
  (worktree)
