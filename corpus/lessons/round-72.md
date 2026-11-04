# Round 72 lesson — kama (2026-11-03)

Carry-in: the round-71 non-author closure (`corpus/lessons/round-71-verifier-spotcheck.md`) ruled round 71
**admitted** and routed five status-neutral defects; its §8 item 4 (a receipt described as "at the report
tip" whose own header names an earlier revision) is C2's motivating evidence, and the round-71 lesson's
routed items are the class C1 kills. Round 72's freeze is `plans/round-72-claims.md`, whose plan states
base revision `d30a8696`; the freeze commit is `090a0b25` and the pre-score amendment commit `a3cc39f0`
(`.ufo/waves/round-72/controls/freeze.txt` carries `base=090a0b25`, the commit whose bytes froze the
claims, while the control receipts measure `base_rev=d30a8696`). Its claims are C1 calibration
(`tools/round72-round-scope.py`, the gate's arm 6) and C2 operability
(`tools/round72-receipt-tip-binding.py`).

Two freeze amendments landed **before any seat returned a score** and are mined below as mistakes 1 and 2:
C1's case A anchor moved from the fleet prompt to the lane-owned plan (the prompt path does not exist at a
lane tip), and C2's exit map gained the zero-citation refusal (`cited=0` → exit 2).

This lesson is written before the report tip. `## Gate` and `## Mistakes` cite the base bytes, the wave's
receipts and the scribe's own selftest runs; the L1 appends its integration addendum after the wave lands.

## Gate

| Row / candidate | Located quote (≤25 words) | Verdict |
|---|---|---|
| `git-check-ignore` (new row **S543**, appended by SCR01SourceRow this round: `SOURCES.md:295`, rows 282 → 283, `used-by` `corpus/knowledge/receipt-tip-binding.md`; the id came from the wave's collision check) `https://git-scm.com/docs/git-check-ignore` | "0 One or more of the provided paths is ignored. 1 None of the provided paths are ignored." (18 words; §EXIT STATUS, anchor `#_exit_status`; page footer "git-check-ignore last updated in 2.52.0"; fetched 2026-11-04T01:42:25Z = 2026-11-03 local, `curl` exit 0; retained bytes sha256 `bdee84a9b7207a7c5920d3e0967c36bb07c941efa5ce56abe8f3a9b15c373927` at `.ufo/waves/round-72/w1/SCR01SourceRow/source/git-check-ignore.html`, `fetch.out` and `quote.txt` beside it) | **admit** — C1's case C needs a *verdict* on whether a path under the wave dir is ignored, and this page gives exit 0/1 as that verdict. The page's third status ("128 A fatal error was encountered", read in the same retained bytes) is a tool error, which C1's exit 2 carries, so the row's two-status quote is the load-bearing half, not the whole page |
| S175 re-opened this round (`https://git-scm.com/docs/git-merge-base`) | "Check if the first <commit> is an ancestor of the second <commit>, and exit with status 0 if true, or with status 1 if not." (25 words; §OPTIONS `--is-ancestor`; re-fetched live 2026-11-03, `curl` exit 0; retained bytes sha256 `46d106b777754f7ec3072813ace57d2c5385d110181b8db1c56b7136cfb49644` at `.ufo/waves/round-72/w1/SCR01SourceRow/source/git-merge-base.html`; footer "git-merge-base last updated in 2.43.0", unchanged from the row's anchor) | **holds** — the row's `teaches` sentence is still the page's sentence; the following sentence separates errors (a nonzero status that is not 1) from a false verdict, which is exactly the distinction C2's ancestor test and exit map rest on. S175 records no byte sha, so no byte comparison is possible: the re-open is a text re-read, not a byte-identity pass |
| S542 re-opened this round (`https://git-scm.com/docs/git-status`) | "is guaranteed not to change in a backwards-incompatible way between Git versions or based on user configuration" (17 words; §OUTPUT → "Porcelain Format Version 1", anchor `#_porcelain_format_version_1`; live re-fetch 2026-11-03, `curl` exit 0; retained bytes sha256 `22ff28ff73f83696c4a503e9c92e7a15f4ded2f91d96cc5668ee79db0a1b0180`) | **holds, byte-identical** — the fetched sha256 equals the sha256 recorded in S542's anchor cell from the round-71 fetch, so no cell changes and no re-read of the quote is needed beyond confirming the bytes; the page still reports "git-status last updated in 2.53.0" and "2.54.0 → 2.56.0 no changes" |
| own-work receipts — `.ufo/waves/round-72/measured/before/round-scope-control-old.out`, `.../receipt-tip-control-old.out`, `.ufo/waves/round-72/controls/freeze.txt`, `plans/round-72-claims.md` | `SCOPE_CONTROL base_rev=d30a8696 cases=3 base_green=3 killed=0` (exit 1); `BINDING_CONTROL cited=3 accepted=3 rejected=0` (exit 1) | **no row** — these are the round's own controls and freeze bytes, i.e. evidence a counter reads (D2 discipline), not learnable sources opened this round |
| `shoukuknow/merge/kama/` package | not re-opened this round; the freeze carries the round-71 decision forward | **Assimilation: none** — the round is sized to two instrument claims, so nothing was re-grounded; the id-collision check ran anyway (receipt `w1/SCR01SourceRow/collisions`) |

Id collision check (wave receipt `w1/SCR01SourceRow/{reg-ids,staged-ids,collisions}`): lane ids 282, staged
ids 142, **collisions 9** (S330, S333, S334, S335, S346, S347, S352, S353, S363), union max **S542**, next
unused **S543**. No staged row is adopted, so no renumber map is needed, and the collision set is why a
bulk append here would have been wrong.

## Mistakes

Class · evidence pointer · captured-by · fix.

1. **an anchor chosen outside the repository the counter can read** · C1's case A was first frozen on the
   fleet prompt `.ufo/prompts/kama-round-72.md`; at the lane tip that path does not exist —
   `git cat-file -e master:.ufo/prompts/kama-round-72.md` → `fatal: path ... does not exist in 'master'`,
   exit 128 (re-run at the base this round), so the frozen predicate was unexecutable as written ·
   captured-by the plan's own freeze-amendment block (`plans/round-72-claims.md:43-48`) · fix: the anchor
   moved to the lane-owned `plans/round-<N>-claims.md`, nothing else changed, and the before-control was
   re-taken against the amended fixture set. The class: a predicate may only anchor on bytes the measured
   revision can serve.
2. **an empty population satisfies an all-quantified sentence** · C2's first exit map had no refusal for
   `cited=0`, so a self-record that cites no receipt at all would have been vacuously green ("every cited
   receipt …" is true of the empty set), the exact class C1 kills for the cleanliness arm · captured-by
   reading the frozen sentence's quantifier before scoring (`plans/round-72-claims.md:106-110`, freeze
   amendment 2) · fix: `cited=0` is exit 2 and the selftest carries an arm for it.
3. **a record's depth anchor quoted a content sha that was never re-derived** · `LOG.md:2728` (§Round 71)
   records `SKILL.md` `0b61e118…` (1724 lines, 48 sections) while `SCORECARD.md:16` and the file itself
   are `7ff94d67…`; re-derived this round: `sha256sum SKILL.md` →
   `7ff94d6743b6bc04860371030123532cecc2a82eb966d664444fa7d908e6485f`, `wc -l` → 1724,
   `grep -c '^## '` → 48 · captured-by the round-71 verifier spot-check §8 item 3
   (`corpus/lessons/round-71-verifier-spotcheck.md:129-131`) · fix: the correction is appended in
   `LOG.md` §Round 72 naming `7ff94d67…`; the intermediate sha stays readable as what it was.
4. **a selftest tally copied between records instead of re-run** · `SKILL.md:310` said
   `BOUNDARY_SELFTEST pass=19 fail=0`; the round-71 receipt says `pass=18 fail=0`, and the re-run this
   round prints the same — `python3 tools/census-waiver-boundary.py --selftest` →
   `BOUNDARY_SELFTEST pass=18 fail=0`, exit 0 · captured-by round-71 spot-check §8 item 1 and the
   re-run · fix: the registry row now carries the re-derived 18 and names the defect; a tally is a run
   fact, so it is re-executed, never copied.
5. **a registry row that does not move with its instrument** · at the base, `SKILL.md:309` described a
   five-arm gate while the round's frozen claim makes the verdict `arms=6` with arm 6 `round-scope`, and
   `SKILL.md:310` mapped `0`/`1` only while `tools/census-waiver-boundary.py` documents exit 2
   ("census unreadable/unloadable, landed census absent, shim corpus missing", docstring lines 11-12;
   `_cnd` prints `BOUNDARY could-not-evaluate`) · captured-by reading the registry rows against the
   tools' own docstrings · fix: both rows are amended in the same landing as the instruments (six arms
   and `arms=6`; the exit map gains `2 could-not-evaluate`), and the five-arm string is kept as the
   round-71 measurement rather than deleted.
6. **a module's selftest was red on the bytes that landed first, and only the row's own run saw it** · the
   first `python3 tools/round72-receipt-tip-binding.py --selftest` on the 22:46 bytes died with
   `TypeError: '<' not supported between instances of 'NoneType' and 'int'` at the `cli-misuse` arm, which
   calls the CLI without `--round` (the module then did `args.round_no < 1` before the missing-argument
   check); the seat's own fixture receipts were green because they all pass `--round 72` · captured-by the
   registry-row run (`.ufo/waves/round-72/w1/SCR03RegistryLog/selftests.out`, first block) · fix: the module guards with
   `ap.error`; the first green re-run at sha256 `94ae3b4a…` printed `pass=14`, and the settled bytes `a9a4e8d3…` print `RECEIPT_TIP_BINDING_SELFTEST pass=16 fail=0`;
   the class: a selftest's own harness is an input, so a fixture suite that only exercises the declared
   argument shape cannot see a missing-argument path.
